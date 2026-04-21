import pandas as pd

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Dynamically unpivots any dataset mapping numerics to Prophet requirements."""
    
    # Ensure columns exist, stripping white spaces
    df.columns = [str(c).strip() for c in df.columns]

    # 1. Identify Date Column
    date_col = None
    date_keywords = ['date', 'time', 'day', 'period', 'month', 'year', 'record', 'timestamp']
    for col in df.columns:
        if any(kw in col.lower() for kw in date_keywords):
            date_col = col
            break
            
    if not date_col:
        # heuristic approach
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col].dropna().head(10))
                    date_col = col
                    break
                except Exception:
                    pass

    if date_col:
        date_series = pd.to_datetime(df[date_col], errors='coerce')
        if date_col != 'Date' and 'Date' in df.columns:
             df = df.drop(columns=['Date'])
        if date_col != 'Date':
            df = df.drop(columns=[date_col])
        df['Date'] = date_series
    else:
        df['Date'] = pd.date_range(end=pd.Timestamp.today(), periods=len(df), freq='D')

    df = df.dropna(subset=['Date'])
    
    # 2. Isolate Groups & Metrics
    categorical_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    if 'Date' in categorical_cols: categorical_cols.remove('Date')
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if 'Date' in numeric_cols: numeric_cols.remove('Date')

    if not numeric_cols:
        df['Count'] = 1
        numeric_cols = ['Count']

    # 3. Concatenate Categories
    if categorical_cols:
        df[categorical_cols] = df[categorical_cols].fillna("Unassigned")
        df['Category_Group'] = df[categorical_cols].astype(str).agg(' - '.join, axis=1)
    else:
        df['Category_Group'] = 'Global'
        
    # 4. Melt / Unpivot
    melted = pd.melt(df, id_vars=['Date', 'Category_Group'], value_vars=numeric_cols, 
                     var_name='Metric', value_name='Sales')
                     
    # 5. Generate Target Identifier
    melted['Product_ID'] = melted.apply(
        lambda row: f"{row['Category_Group']} | {row['Metric']}" if row['Category_Group'] != 'Global' else str(row['Metric']),
        axis=1
    )
    
    # Convert numerical to float securely
    melted['Sales'] = pd.to_numeric(melted['Sales'], errors='coerce').fillna(0)

    clean_df = melted[['Date', 'Product_ID', 'Sales']].copy()

    # 6. Aggregate Duplicates 
    clean_df = clean_df.groupby(['Date', 'Product_ID'], as_index=False)['Sales'].sum()
    clean_df = clean_df.sort_values(by=['Product_ID', 'Date'])
    
    return clean_df
