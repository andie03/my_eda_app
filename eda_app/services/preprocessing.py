# services/preprocessing.py — Data cleaning and quality checks

import pandas as pd
from config import LOW_VARIANCE_THRESHOLD


def missing_values_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a table of missing value counts and percentages per column."""
    missing = df.isnull().sum()
    pct = (missing / len(df) * 100).round(2)
    summary = pd.DataFrame({"Valeurs manquantes": missing, "Pourcentage (%)": pct})
    return summary[summary["Valeurs manquantes"] > 0].sort_values(
        "Valeurs manquantes", ascending=False
    )


def duplicate_count(df: pd.DataFrame) -> int:
    """Return the number of duplicate rows."""
    return int(df.duplicated().sum())


def low_variance_columns(df: pd.DataFrame) -> list[str]:
    """
    Return a list of numeric columns whose normalised variance is below the threshold.
    Quasi-constant columns are candidates for removal.
    """
    num_df = df.select_dtypes(include="number")
    if num_df.empty:
        return []
    ranges = num_df.max() - num_df.min()
    # Avoid division by zero
    ranges = ranges.replace(0, float("nan"))
    norm_var = num_df.var() / ranges
    return list(norm_var[norm_var < LOW_VARIANCE_THRESHOLD].dropna().index)


def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame with duplicate rows removed."""
    return df.drop_duplicates().reset_index(drop=True)


def fill_missing_median(df: pd.DataFrame) -> pd.DataFrame:
    """Fill numeric NaN with column median (non-destructive copy)."""
    result = df.copy()
    for col in result.select_dtypes(include="number").columns:
        result[col].fillna(result[col].median(), inplace=True)
    return result
