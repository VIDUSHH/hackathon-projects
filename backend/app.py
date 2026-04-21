from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import io

from services.prediction import predict_demand
from services.optimization import optimize_inventory
from database.queries import get_all_sales, get_product_sales, get_all_products
import io
import sqlite3
from database.db_config import DB_PATH
from api.auth import router as auth_router
from api.agentic_routes import router as agent_router
from genai.explanation import generate_explanation
from services.po_generator import generate_po, generate_discount_letter
from fastapi.responses import Response
from datetime import datetime

app = FastAPI(title="Inventory AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(agent_router, prefix="/api/agent", tags=["NLP Agent"])

# Database Status Endpoint (replacing upload)

@app.get("/db-status")
def get_db_status():
    try:
        sales_df = get_all_sales()
        products_df = get_all_products()
        
        if sales_df.empty:
            return {"status": "empty", "message": "Database has no sales records"}
            
        preview = sales_df.head(10).copy()
        if not preview.empty and 'Date' in preview.columns:
            preview['Date'] = preview['Date'].dt.strftime('%Y-%m-%d')
            
        return {
            "status": "connected",
            "message": "Connected to SQLite Database",
            "sales_count": len(sales_df),
            "products_count": len(products_df),
            "products_list": products_df[['product_id', 'product_name', 'category']].to_dict(orient="records"),
            "preview": preview.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Summary Endpoint

@app.get("/summary")
def get_summary():
    sales = get_all_sales()
    if sales.empty:
        raise HTTPException(status_code=400, detail="No data in DB")

    category_summaries = {}
    categories = sales['Category'].unique().tolist()
    
    for cat in categories:
        cat_sales = sales[sales['Category'] == cat]
        
        pivot = cat_sales.pivot(index='Date', columns='Product_ID', values='Sales').fillna(0)
        pivot.index = pivot.index.strftime('%Y-%m-%d')
        chart_data = pivot.reset_index().to_dict(orient='records')
        
        totals = cat_sales.groupby('Product_ID')['Sales'].sum().sort_values(ascending=False)
        top_selling = totals.index[0] if len(totals) > 0 else "N/A"
        least_selling = totals.index[-1] if len(totals) > 0 else "N/A"
        
        insight_text = (
            f"Top moving product in {cat} is {top_selling}. "
            f"Monitor {least_selling} for possible stagnation. "
            f"Total units mapped: {totals.sum():,.0f}."
        )
        
        products_in_cat = cat_sales['Product_ID'].unique().tolist()
        
        category_summaries[cat] = {
            "products": products_in_cat,
            "chart_data": chart_data,
            "kpis": {
                "top_selling": top_selling,
                "least_selling": least_selling,
                "insight": insight_text
            }
        }

    return {
        "categories": categories,
        "category_data": category_summaries
    }


# Prediction Endpoint

class PredictRequest(BaseModel):
    product_id: str
    periods: int = 30


@app.post("/predict")
def predict(request: PredictRequest):
    df = get_all_sales()
    if df.empty:
        raise HTTPException(status_code=400, detail="No data in DB")

    if request.product_id not in df['Product_ID'].unique():
        raise HTTPException(status_code=400, detail="Product ID not found")

    forecast_outputs = predict_demand(df, request.product_id, request.periods)

    hist = df[df['Product_ID'] == request.product_id].copy()
    hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
    historical_chart = hist[['Date', 'Sales']].to_dict(orient='records')
    
    explanation = generate_explanation(forecast_outputs["prophet"], historical_chart)

    return {
        "product_id": request.product_id,
        "historical": historical_chart,
        "forecast": forecast_outputs["prophet"],
        "lstm_forecast": forecast_outputs["lstm"],
        "explanation": explanation
    }

# Optimization Endpoint

@app.get("/optimize")
def optimize():
    df_sales = get_all_sales()
    df_products = get_all_products()
    if df_sales.empty:
        raise HTTPException(status_code=400, detail="No data in DB")

    recommendations = optimize_inventory(df_sales, df_products)
    return {"recommendations": recommendations}


# PO & Workflow Endpoints
@app.get("/api/po/generate")
def api_generate_po(product_id: str, product_name: str, quantity: int):
    date_str = datetime.now().strftime('%Y-%m-%d')
    po_text = generate_po(product_name, product_id, quantity, date_str)
    return Response(content=po_text, media_type="text/plain", headers={"Content-Disposition": f"attachment; filename=PO_{product_id}.txt"})

@app.get("/api/discount/generate")
def api_generate_discount(product_id: str, product_name: str):
    letter_text = generate_discount_letter(product_name, product_id)
    return Response(content=letter_text, media_type="text/plain", headers={"Content-Disposition": f"attachment; filename=Discount_{product_id}.txt"})

# CRUD Data Management & CSV Endpoints

class ProductCreate(BaseModel):
    product_id: str
    product_name: str
    category: str
    current_stock: int

class SaleCreate(BaseModel):
    date: str
    product_id: str
    sales_quantity: int

@app.post("/api/products")
def create_product(prod: ProductCreate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (product_id, product_name, category, current_stock) VALUES (?, ?, ?, ?)",
                       (prod.product_id, prod.product_name, prod.category, prod.current_stock))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Product ID already exists.")
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    conn.close()
    return {"message": "Product created successfully"}

@app.post("/api/sales")
def create_sale(sale: SaleCreate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO sales (date, product_id, sales_quantity) VALUES (?, ?, ?)",
                       (sale.date, sale.product_id, sale.sales_quantity))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    conn.close()
    return {"message": "Sale created successfully"}

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file format")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Introspect schemas
    cursor.execute("PRAGMA table_info(products)")
    prod_cols = [r[1].lower() for r in cursor.fetchall()]
    
    cursor.execute("PRAGMA table_info(sales)")
    sales_cols = [r[1].lower() for r in cursor.fetchall()]
    
    df.columns = [c.strip().lower() for c in df.columns]
    
    inserted_products = 0
    inserted_sales = 0
    
    prod_matches = [c for c in df.columns if c in prod_cols and c != 'id']
    sales_matches = [c for c in df.columns if c in sales_cols and c != 'id']
    
    target_table = None
    valid_cols = []
    
    if len(prod_matches) >= 1 and len(prod_matches) >= len(sales_matches):
        target_table = "products"
        valid_cols = prod_matches
    elif len(sales_matches) >= 1:
        target_table = "sales"
        valid_cols = sales_matches
    else:
        conn.close()
        raise HTTPException(status_code=400, detail="CSV does not contain any column matching the 'products' or 'sales' database schema.")
        
    for _, row in df.iterrows():
        vals = [row[col] if pd.notna(row[col]) else None for col in valid_cols]
        if all(v is None for v in vals):
            continue
            
        placeholders = ",".join(["?"] * len(valid_cols))
        col_str = ",".join(valid_cols)
        try:
            if target_table == "products":
                cursor.execute(f"INSERT OR IGNORE INTO products ({col_str}) VALUES ({placeholders})", tuple(vals))
                if cursor.rowcount > 0:
                    inserted_products += 1
            else:
                cursor.execute(f"INSERT INTO sales ({col_str}) VALUES ({placeholders})", tuple(vals))
                inserted_sales += 1
        except Exception:
            pass
            
    conn.commit()
    conn.close()
    
    return {"message": f"Successfully parsed CSV with partial schema matching! Inserted {inserted_products} products and {inserted_sales} sales records.", "inserted_products": inserted_products, "inserted_sales": inserted_sales}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)