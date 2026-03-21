# services/data_loader.py — CSV loading with validation and caching

import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def load_data(file) -> pd.DataFrame:
    """
    Load a CSV file into a DataFrame.
    Raises ValueError for invalid or empty files.
    """
    try:
        df = pd.read_csv(file)
    except Exception as exc:
        raise ValueError(f"Impossible de lire le fichier CSV : {exc}") from exc

    if df.empty:
        raise ValueError("Le dataset est vide.")

    if df.shape[1] < 2:
        raise ValueError("Le dataset doit contenir au moins deux colonnes.")

    return df
