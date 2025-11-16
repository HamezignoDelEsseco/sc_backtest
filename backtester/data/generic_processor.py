import pandas as pd

def basic_process(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    initial_cols = df.columns.values
    df = df.rename(columns={c: c.lower().strip().replace(' ', '_') for c in initial_cols})
    df['datetime'] = pd.to_datetime(df['date'] + df['time'])
    return df
