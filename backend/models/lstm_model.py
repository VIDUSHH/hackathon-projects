import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
from datetime import timedelta

def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:(i + seq_length)].flatten())
        y.append(data[i + seq_length])
    return np.array(X), np.array(y).flatten()

def generate_lstm_forecast(df: pd.DataFrame, periods: int = 30) -> list:
    """Trains a Deep Learning model and generates predictions."""

    df = df.sort_values('Date').copy()
    sales_data = df['Sales'].values.reshape(-1, 1)
    
    if len(sales_data) < 15:
        return []
        
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(sales_data)
    
    seq_length = 7
    X, y = create_sequences(scaled_data, seq_length)
    
    if len(X) == 0:
        return []

    # Safe DL proxy fallback due to TensorFlow Windows compatibility issues
    model = MLPRegressor(hidden_layer_sizes=(32, 16), max_iter=500, random_state=42)
    model.fit(X, y)
    
    # Generate Historical Fit predictions
    hist_preds = model.predict(X)
    hist_preds_unscaled = scaler.inverse_transform(hist_preds.reshape(-1, 1))
    hist_dates = df['Date'].iloc[seq_length:]
    
    last_sequence = scaled_data[-seq_length:].flatten()
    predictions = []
    current_seq = last_sequence.copy()
    
    for _ in range(periods):
        curr_pred = model.predict([current_seq])[0]
        predictions.append(curr_pred)
        current_seq = np.append(current_seq[1:], curr_pred)
        
    predictions_unscaled = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
    
    last_date = df['Date'].iloc[-1]
    last_date = pd.to_datetime(last_date)
    future_dates = [last_date + timedelta(days=i) for i in range(1, periods + 1)]
    
    results = []
    
    # Append Historical fit curve
    for d, val in zip(hist_dates, hist_preds_unscaled):
        pred = float(val[0])
        results.append({
            "ds": pd.to_datetime(d).strftime('%Y-%m-%d'),
            "yhat": pred if pred > 0 else 0.0
        })
        
    # Append Future extrapolation curve    
    for d, val in zip(future_dates, predictions_unscaled):
        pred = float(val[0])
        results.append({
            "ds": d.strftime('%Y-%m-%d'),
            "yhat": pred if pred > 0 else 0.0
        })
        
    return results
