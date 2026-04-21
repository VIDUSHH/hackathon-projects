import pandas as pd
import numpy as np

def generate_explanation(forecast_data: list, historical_data: list) -> str:
    """Analyze predictions vs historicals to provide an exact insight string."""
    
    if not forecast_data or not historical_data:
        return "Insufficient data to generate an explanation."
        
    hist_sales = []
    for x in historical_data:
        if isinstance(x, dict):
            hist_sales.append(x.get('Sales', 0))
            
    pred_sales = []
    for x in forecast_data:
        if isinstance(x, dict):
            pred_sales.append(x.get('yhat', 0))
    
    if not hist_sales or not pred_sales:
         return "Missing series data for reasoning."

    hist_avg = np.mean(hist_sales)
    pred_avg = np.mean(pred_sales)
    
    growth_rate = ((pred_avg - hist_avg) / hist_avg) * 100 if hist_avg > 0 else 0
    std_dev = np.std(hist_sales)
    cv = std_dev / hist_avg if hist_avg > 0 else 0 # Coefficient of variation
    
    trend_text = "a stable trajectory"
    reasoning = "Historically consistent momentum indicates steady continued demand."
    
    recent_avg = np.mean(hist_sales[-14:]) if len(hist_sales) > 14 else hist_avg
    older_avg = np.mean(hist_sales[:-14]) if len(hist_sales) > 14 else hist_avg

    if growth_rate > 5:
        trend_text = "a bullish (upward) trend"
        if recent_avg > older_avg:
            reasoning = "Prophet is reacting bullishly because it detected strong momentum and increased sales volumes over the recent two weeks."
        else:
            reasoning = "The model expects an incoming seasonal or cyclic spike based on historical cyclic overlays, despite recent stagnant volumes."
    elif growth_rate < -5:
        trend_text = "a bearish (downward) trend"
        if recent_avg < older_avg:
            reasoning = "Prophet is projecting a bearish drop-off. The model is reacting to a recent slump in sales volume trailing below historical averages."
        else:
            reasoning = "Although recent momentum is fair, Prophet anticipates an upcoming seasonal bearish drop-off based on historical patterns."
        
    variance_text = "low variance"
    if cv > 0.4:
        variance_text = "high variance"
        
    return f"Demand is experiencing {trend_text} ({growth_rate:.1f}% change) with {variance_text} observed in historical patterns. {reasoning}"

