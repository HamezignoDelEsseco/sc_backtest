from tabulate import tabulate
from backtester.data.generic_processor import basic_process
from backtester.data.nested_df_builder import build_nested_dataframe

def test_load_data():
    # Load sample dataset
    load_path = "C:\\backtests\\openVVA\\datasets\\raw\\NQZ25_DV50.txt"
    df = basic_process(load_path)
    print(tabulate(df.head(), headers="keys", tablefmt="psql"))
    print(df.dtypes)


def test_nested_structure():
    load_path = "C:\\backtests\\openVVA\\datasets\\raw\\NQZ25_DV50.txt"
    out_file_name = "C:\\backtests\\openVVA\\datasets\\processed\\NQZ25_DV50.pq"
    df = basic_process(load_path)
    nested_cols = ["open", "high", "low", "last", "datetime"]

    # Build nested DataFrame
    df_nested = build_nested_dataframe(
        df,
        nested_cols=nested_cols,
        col_name="bar",
        passthrough=True,
        write_to_parquet=True,
        out_file_name=out_file_name
    )

    # --- Visualization/Debug Output ---
    print("\n=== NESTED DATAFRAME SAMPLE ===")
    print(df_nested.head())

    print("\n=== FIRST NESTED OBJECT ===")
    print(df_nested["bar"].iloc[0])
    print("Fields in nested object:", df_nested["bar"].iloc[0].__dict__)

    # --- Simple correctness checks ---
    assert "bar" in df_nested.columns
    assert hasattr(df_nested["bar"].iloc[0], nested_cols[0].lower()) or \
           hasattr(df_nested["bar"].iloc[0], nested_cols[0])

    # ensure all nested columns are bundled
    nested_obj = df_nested["bar"].iloc[0]
    for col in nested_cols:
        # Allow lower-case attributes too, depending on your naming policy
        assert (hasattr(nested_obj, col)
                or hasattr(nested_obj, col.lower())), f"Missing attribute: {col}"

    print("\nTest passed: nested structure created successfully.")