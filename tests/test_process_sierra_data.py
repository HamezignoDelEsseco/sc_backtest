from tabulate import tabulate
from backtester.data.bar_data import BarData
from backtester.data.data_loader import load_pq_with_bar_data
from backtester.data.generic_processor import sierra_txt_file_to_pq


def test_process_and_save():
    load_path = "C:\\backtests\\openVVA\\datasets\\raw\\NQZ25_DV50.txt"
    out_file_name = "C:\\backtests\\openVVA\\datasets\\processed\\NQZ25_DV50.pq"

    df = sierra_txt_file_to_pq(load_path, out_file_name)
    print(f"\n✓ Processed {len(df)} rows")
    print(f"✓ Saved to {out_file_name}")
    print(f"✓ Datetime type: {type(df['datetime'].iloc[0])}")


def test_load_with_bar_data():
    parquet_path = "C:\\backtests\\openVVA\\datasets\\processed\\NQZ25_DV50.pq"
    df = load_pq_with_bar_data(parquet_path)
    
    print("\n=== LOADED DATAFRAME ===")
    print(f"Columns: {list(df.columns)}")
    print(f"Rows: {len(df)}")
    
    print("\n=== FIRST BAR DATA OBJECT ===")
    bar_data = df['bar_data'].iloc[0]
    print(f"Type: {type(bar_data)}")
    print(f"open: {bar_data.open}")
    print(f"high: {bar_data.high}")
    print(f"low: {bar_data.low}")
    print(f"last: {bar_data.last}")
    print(f"datetime: {bar_data.datetime} (type: {type(bar_data.datetime)})")
    
    assert 'bar_data' in df.columns
    assert isinstance(df['bar_data'].iloc[0], BarData)
    assert isinstance(df['bar_data'].iloc[0].datetime, type(bar_data.datetime))
    
    print("\n✓ Test passed: BarData objects created successfully.")
