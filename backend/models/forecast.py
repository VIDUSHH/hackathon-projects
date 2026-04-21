import pandas as pd
from prophet import Prophet

def generate_forecast(df: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
    """Trains a Prophet model and generates a forecast."""
    prophet_df = df.rename(columns={'Date': 'ds', 'Sales': 'y'})
    
    # Improve accuracy via hyperparameters
    m = Prophet(
        daily_seasonality=True, 
        yearly_seasonality=True,
        weekly_seasonality=True,
        seasonality_mode='multiplicative',
        changepoint_prior_scale=0.15,
        seasonality_prior_scale=10.0
    )
    m.fit(prophet_df)
    
    future = m.make_future_dataframe(periods=periods)
    forecast = m.predict(future)
    
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
