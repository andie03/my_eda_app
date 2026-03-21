# app.py — Entry point

import streamlit as st

from services.data_loader import load_data
from services.preprocessing import missing_values_summary, duplicate_count, low_variance_columns
from services.analysis import descriptive_stats
from utils.helpers import get_numeric_columns
from utils.export import dataframe_to_csv_bytes, build_pdf_report
from ui.overview import show_overview
from ui.numeric import analyze_numeric
from ui.categorical import analyze_categorical

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="EDA Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #1a1f2e; }
    [data-testid="stSidebar"] * { color: #e0e4f0 !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #a8b4d8 !important; }
    /* Push content below Streamlit's top toolbar (~60px) */
    .block-container { padding-top: 4rem !important; }
    header[data-testid="stHeader"] { height: 3.5rem; }
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #f0f2f8;
        border-radius: 8px;
        padding: 4px;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 28px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: white;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }
    div[data-testid="stDownloadButton"] button {
        width: 100%;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## EDA Explorer")
    st.markdown("---")
    st.markdown("**Charger un fichier CSV**")
    uploaded_file = st.file_uploader(" ", type=["csv"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### Exports")

    if "df" in st.session_state:
        df_s = st.session_state["df"]
        filename = st.session_state.get("filename", "dataset")

        st.download_button(
            label="Dataset (CSV)",
            data=dataframe_to_csv_bytes(df_s),
            file_name=f"{filename.replace('.csv', '')}_export.csv",
            mime="text/csv",
            use_container_width=True,
        )

        num_cols = get_numeric_columns(df_s)
        try:
            pdf_bytes = build_pdf_report(
                df_s,
                stats=descriptive_stats(df_s, num_cols) if num_cols else None,
                missing=missing_values_summary(df_s),
                duplicates=duplicate_count(df_s),
                low_var_cols=low_variance_columns(df_s),
            )
            st.download_button(
                label="Rapport (PDF)",
                data=pdf_bytes,
                file_name=f"{filename.replace('.csv', '')}_rapport.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception:
            st.caption("PDF indisponible (fpdf2 requis)")

        st.markdown("---")
        st.markdown(f"**{filename}**")
        st.markdown(f"{df_s.shape[0]:,} lignes · {df_s.shape[1]} colonnes")
    else:
        st.caption("Chargez un fichier pour activer les exports.")

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        st.session_state["df"] = df
        st.session_state["filename"] = uploaded_file.name
    except ValueError as e:
        st.error(str(e))
        st.stop()

if "df" not in st.session_state:
    st.markdown("# EDA Explorer")
    st.markdown("Chargez un fichier CSV dans la barre laterale pour commencer l'analyse.")
    st.stop()

df = st.session_state["df"]

# ---------------------------------------------------------------------------
# Tabs at the top
# ---------------------------------------------------------------------------
tab_overview, tab_numeric, tab_categorical = st.tabs([
    "  Overview  ",
    "  Numerique  ",
    "  Categoriel  ",
])

with tab_overview:
    show_overview(df)

with tab_numeric:
    analyze_numeric(df)

with tab_categorical:
    analyze_categorical(df)
