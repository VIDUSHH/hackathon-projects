import pandas as pd

def calculate_safety_stock(sales_std, lead_time_std, lead_time_mean, service_factor=1.65):
    return (service_factor * sales_std * (lead_time_mean ** 0.5)) + (service_factor * lead_time_std * sales_std)

def optimize_inventory(df: pd.DataFrame) -> list:
    """Generates stock recommendations and alerts."""
    recommendations = []
    
    # Calculate for each product
    for product_id, group in df.groupby('Product_ID'):
        recent_avg = group['Sales'].tail(30).mean()
        std_dev = group['Sales'].tail(30).std()
        
        # Simulated metrics
        lead_time = 7
        safety_stock = int(calculate_safety_stock(std_dev if pd.notna(std_dev) else 0, 1, lead_time))
        optimal_stock = int((recent_avg * lead_time) + safety_stock)
        predicted_demand = int(recent_avg * lead_time)
        
        current_stock = int(recent_avg * 5)
        
        # Alert thresholds
        alert = "OK"
        if predicted_demand > current_stock:
            alert = "LOW"
        elif current_stock > optimal_stock * 1.5:
            alert = "OVERSTOCK"
            
        recommendations.append({
            "product_id": product_id,
            "predicted_demand": predicted_demand,
            "safety_stock": safety_stock,
            "optimal_stock": optimal_stock,
            "current_run_rate": round(recent_avg, 2),
            "alert": alert
        })
        
    return recommendations
