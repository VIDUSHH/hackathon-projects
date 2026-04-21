import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from prophet import Prophet
import joblib

DATASETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../datasets'))
SAVED_MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../saved_models'))

def run_pipeline():
    print("Starting Advanced ML Pipeline...")
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    
    # 1. Process Demand Time Series (Electronics/Grocery/etc)
    demand_path = os.path.join(DATASETS_DIR, 'demand_forecasting.csv')
    if os.path.exists(demand_path):
        print(f"Ingesting {demand_path}...")
        df_demand = pd.read_csv(demand_path)
        
        # Preprocessing
        df_demand.fillna(value={'Discount': 0, 'Promotion': 0, 'Epidemic': 0}, inplace=True)
        
        categories = df_demand['Category'].unique()
        for cat in categories:
            print(f"Training Prophet model for Category: {cat}")
            cat_df = df_demand[df_demand['Category'] == cat].copy()
            
            cat_df['ds'] = pd.to_datetime(cat_df['Date'])
            cat_df['y'] = cat_df['Demand']
            
            daily_series = cat_df.groupby('ds')['y'].sum().reset_index()
            
            scaler = MinMaxScaler()
            daily_series['y_scaled'] = scaler.fit_transform(daily_series[['y']])
            
            train_df = daily_series[['ds', 'y_scaled']].rename(columns={'y_scaled': 'y'})
            m = Prophet()
            m.fit(train_df)
            
            joblib.dump(m, os.path.join(SAVED_MODELS_DIR, f'prophet_{cat}_model.pkl'))
            joblib.dump(scaler, os.path.join(SAVED_MODELS_DIR, f'prophet_{cat}_scaler.pkl'))
            print(f"Model saved: prophet_{cat}_model.pkl")

    # 2. Process Fashion Boutique Dataset
    fashion_path = os.path.join(DATASETS_DIR, 'fashion_boutique_dataset.csv')
    if os.path.exists(fashion_path):
        print(f"Ingesting {fashion_path}...")
        df_fashion = pd.read_csv(fashion_path)
        
        # Preprocessing
        df_fashion.fillna(value={'size': 'M'}, inplace=True)
        
        df_fashion['ds'] = pd.to_datetime(df_fashion['purchase_date'])
        df_fashion['y'] = df_fashion['stock_quantity']
        
        print("Training Prophet model for Fashion DB")
        daily_fashion = df_fashion.groupby('ds')['y'].sum().reset_index()
        
        fashion_scaler = MinMaxScaler()
        daily_fashion['y_scaled'] = fashion_scaler.fit_transform(daily_fashion[['y']])
        
        train_fashion = daily_fashion[['ds', 'y_scaled']].rename(columns={'y_scaled': 'y'})
        fm = Prophet()
        fm.fit(train_fashion)
        
        joblib.dump(fm, os.path.join(SAVED_MODELS_DIR, 'prophet_fashion_model.pkl'))
        joblib.dump(fashion_scaler, os.path.join(SAVED_MODELS_DIR, 'prophet_fashion_scaler.pkl'))
        print("Model saved: prophet_fashion_model.pkl")

    print("Pipeline Complete! Models export to /saved_models successfully.")

if __name__ == "__main__":
    run_pipeline()
