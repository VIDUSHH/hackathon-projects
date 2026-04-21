from database.db_config import get_db_connection
import pandas as pd

def get_all_sales():
    conn = get_db_connection()
    query = """
    SELECT s.date as Date, p.product_id as Product_ID, p.category as Category, s.sales_quantity as Sales
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    ORDER BY s.date ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
    
    return df

def get_product_sales(product_id: str):
    conn = get_db_connection()
    query = """
    SELECT s.date as Date, p.product_id as Product_ID, p.category as Category, s.sales_quantity as Sales
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    WHERE p.product_id = ?
    ORDER BY s.date ASC
    """
    df = pd.read_sql_query(query, conn, params=(product_id,))
    conn.close()
    
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        
    return df

def get_all_products():
    conn = get_db_connection()
    query = "SELECT * FROM products"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
