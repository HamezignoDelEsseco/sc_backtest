import pandas as pd
from backtester.data.bar_data import BarData


def load_pq_with_bar_data(file_path: str) -> pd.DataFrame:
    """
    Load processed parquet data and create BarData objects from flat records
    """
    df = pd.read_parquet(file_path)
    
    # Create BarData objects from flat records
    df['bar_data'] = df.apply(
        lambda row: BarData.from_dict(row.to_dict()),
        axis=1
    )
    
    return df
