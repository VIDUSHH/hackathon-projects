import pandas as pd

def calculate_safety_stock(sales_std, lead_time_std, lead_time_mean, service_factor=1.65):
    return (service_factor * sales_std * (lead_time_mean ** 0.5)) + (service_factor * lead_time_std * sales_std)

def optimize_inventory(df_sales: pd.DataFrame, df_products: pd.DataFrame) -> list:
    """Generates stock recommendations and alerts category-wise."""
    recommendations = []
    
    # Calculate for each product
    for product_id, group in df_sales.groupby('Product_ID'):
        product_info = df_products[df_products['product_id'] == product_id].iloc[0]
        category = product_info['category']
        current_stock = product_info['current_stock']
        product_name = product_info['product_name']
        
        recent_avg = group['Sales'].tail(30).mean()
        std_dev = group['Sales'].tail(30).std()
        
     
        if category == 'Electronics':
            lead_time = 14  
            service_factor = 2.0  
        elif category == 'Grocery':
            lead_time = 3   
            service_factor = 1.2  
        else:
            lead_time = 7
            service_factor = 1.65
            
        safety_stock = int(calculate_safety_stock(std_dev if pd.notna(std_dev) else 0, 1, lead_time, service_factor=service_factor))
        predicted_demand = int(recent_avg * lead_time)
        optimal_stock = predicted_demand + safety_stock
        
        # Alert thresholds based on logic
        alert = "OK"
        if predicted_demand + safety_stock > current_stock:
            alert = "LOW"
        elif current_stock > optimal_stock * 1.5:
            alert = "OVERSTOCK"
            
        recommendations.append({
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "predicted_demand": predicted_demand,
            "safety_stock": safety_stock,
            "optimal_stock": optimal_stock,
            "current_stock": int(current_stock),
            "current_run_rate": round(recent_avg, 2),
            "alert": alert
        })
        
    return recommendations
