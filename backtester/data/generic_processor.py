import pandas as pd

def sierra_txt_file_to_pq(path: str, out_file: str) -> pd.DataFrame:
    """
    Basic processing of raw Sierra Chart data and optionally save to parquet
    """
    df = pd.read_csv(path)
    initial_cols = df.columns.values
    df = df.rename(columns={c: c.lower().strip().replace(' ', '_') for c in initial_cols})
    
    # Convert to pandas datetime first, then to Python datetime
    df['datetime'] = pd.to_datetime(df['date'] + df['time']).apply(lambda x: x.to_pydatetime())
    
    df.to_parquet(out_file)
    
    return df
