import sys
import os
sys.path.append('.')
from app import predict, PredictRequest

try:
    req = PredictRequest(product_id='PROD-ELEC-01', periods=30)
    res = predict(req)
    print("KEYS:", res.keys())
    print("HIST LEN:", len(res.get('historical', [])))
    print("PROPHET LEN:", len(res.get('forecast', [])))
    print("LSTM LEN:", len(res.get('lstm_forecast', [])))
except Exception as e:
    import traceback
    traceback.print_exc()
