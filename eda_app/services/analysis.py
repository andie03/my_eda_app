# services/analysis.py — Statistical computations

import pandas as pd
import numpy as np
from config import STRONG_CORR_THRESHOLD


def descriptive_stats(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Return extended descriptive statistics for selected numeric columns.
    Includes mean, median, std, min, max, skewness, kurtosis.
    """
    subset = df[columns].select_dtypes(include="number")
    stats = subset.agg(["mean", "median", "std", "min", "max", "skew", "kurt"]).T
    stats.columns = ["Mean", "Median", "Std", "Min", "Max", "Skewness", "Kurtosis"]
    return stats.round(4)


def detect_outliers_iqr(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Detect outliers in a numeric column using the IQR method.
    Returns the rows that contain outlier values.
    """
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return df[(df[column] < lower) | (df[column] > upper)][[column]]


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return the Pearson correlation matrix for numeric columns."""
    return df.select_dtypes(include="number").corr()


def strong_correlations(corr: pd.DataFrame, threshold: float = STRONG_CORR_THRESHOLD) -> pd.DataFrame:
    """
    Extract pairs of variables with |correlation| >= threshold,
    excluding self-correlations.
    """
    mask = np.triu(np.ones(corr.shape, dtype=bool), k=1)
    pairs = (
        corr.where(mask)
        .stack()
        .reset_index()
    )
    pairs.columns = ["Variable A", "Variable B", "Correlation"]
    strong = pairs[pairs["Correlation"].abs() >= threshold].sort_values(
        "Correlation", key=abs, ascending=False
    )
    return strong.reset_index(drop=True)


def value_counts_table(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return value counts and percentages for a categorical column."""
    vc = df[column].value_counts(dropna=False)
    pct = (vc / len(df) * 100).round(2)
    return pd.DataFrame({"Effectif": vc, "Pourcentage (%)": pct})


def contingency_table(df: pd.DataFrame, col_a: str, col_b: str) -> pd.DataFrame:
    """Return a contingency table (cross-tabulation) between two categorical columns."""
    return pd.crosstab(df[col_a], df[col_b])
