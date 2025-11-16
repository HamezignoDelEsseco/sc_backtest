import pandas as pd
from typing import List
from dataclasses import make_dataclass, asdict


def build_nested_dataframe(
        df: pd.DataFrame,
        nested_cols: List[str],
        col_name="bar_data",
        passthrough=True,
        write_to_parquet: bool = True,
        out_file_name: str = None
) -> pd.DataFrame:
    """
    Convert selected columns from df into a nested object column.

    Parameters
    ----------
    df : pandas.DataFrame
        Source dataframe (OHLCV etc.)
    nested_cols : list[str]
        List of columns to bundle into a single nested object.
    col_name : str
        Name of the resulting nested column.
    passthrough : bool
        If True → keep all other columns.
        If False → only return the single nested column.
        
    write_to_parquet : bool
        If True, writes output to parquet file
        
    out_file_name : str
        File output name

    Returns
    -------
    out
        DataFrame where each row contains `col_name` as a BarData-like object.
    """
    for col in nested_cols:
        if col not in df.columns:
            raise ValueError(f"Column {col} not found in DataFrame.")

    # 2. Dynamically construct a dataclass based on column list
    # Example: nested_cols = ["open", "high", "low", "close", "FVH", "FVL"]
    NestedCls = make_dataclass(
        cls_name="BarData",
        fields=[(col, type(df[col].iloc[0])) for col in nested_cols],
        frozen=True
    )

    # 3. Build the nested object per row
    nested_series = df[nested_cols].apply(
        lambda row: NestedCls(*row.values), axis=1
    )

    # 4. Construct output DataFrame
    if passthrough:
        out = df.copy()
        out[col_name] = nested_series
    else:
        out = pd.DataFrame({col_name: nested_series}, index=df.index)

    if write_to_parquet:
        # Convert dataclass objects to dictionaries for parquet compatibility
        out_for_parquet = out.copy()
        if col_name in out_for_parquet.columns:
            out_for_parquet[col_name] = out_for_parquet[col_name].apply(
                lambda obj: asdict(obj) if hasattr(obj, '__dataclass_fields__') else obj
            )
        out_for_parquet.to_parquet(out_file_name)

    return out
