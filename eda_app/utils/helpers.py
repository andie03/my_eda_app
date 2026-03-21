# utils/helpers.py — Generic utility functions

import pandas as pd


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    """Return the list of numeric column names."""
    return df.select_dtypes(include="number").columns.tolist()


def get_categorical_columns(df: pd.DataFrame) -> list[str]:
    """Return the list of categorical (object / boolean) column names."""
    return df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()


def column_type_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a table of column names and their detected Pandas dtypes."""
    return pd.DataFrame({
        "Colonne": df.columns,
        "Type": df.dtypes.values.astype(str),
    })


def safe_sample(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the first n rows (or fewer if the dataset is smaller)."""
    return df.head(min(n, len(df)))
