import pandas as pd
from models.forecast import generate_forecast
from models.lstm_model import generate_lstm_forecast

def predict_demand(df: pd.DataFrame, product_id: str, periods: int = 30) -> dict:
    """Filters data for a given product and runs both models."""
    product_df = df[df['Product_ID'] == product_id]
    
    if product_df.empty:
        return {"prophet": [], "lstm": []}
    
    # Run Prophet
    forecast_df_prophet = generate_forecast(product_df, periods)
    forecast_df_prophet['ds'] = forecast_df_prophet['ds'].dt.strftime('%Y-%m-%d')
    prophet_results = forecast_df_prophet.to_dict(orient='records')
    
    # Run LSTM
    try:
        lstm_results = generate_lstm_forecast(product_df, periods)
        # Format date for json
        for res in lstm_results:
            if isinstance(res['ds'], pd.Timestamp):
                res['ds'] = res['ds'].strftime('%Y-%m-%d')
    except Exception as e:
        print(f"LSTM error: {e}")
        lstm_results = []
        
    return {
        "prophet": prophet_results,
        "lstm": lstm_results
    }
