# utils/export.py — Export utilities (CSV, PNG, PDF)

import io
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Return a CSV-encoded byte string from a DataFrame (no index)."""
    return df.to_csv(index=False).encode("utf-8")


# ---------------------------------------------------------------------------
# PNG
# ---------------------------------------------------------------------------

def figure_to_png_bytes(fig: plt.Figure, dpi: int = 150) -> bytes:
    """Return PNG-encoded bytes from a matplotlib Figure."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    buf.seek(0)
    return buf.read()


# ---------------------------------------------------------------------------
# PDF (simplified report)
# ---------------------------------------------------------------------------

class _ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Rapport EDA — Resume analytique", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(230, 235, 245)
        self.cell(0, 8, title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text: str):
        self.set_font("Helvetica", size=9)
        self.multi_cell(0, 6, text)
        self.ln(1)

    def dataframe_table(self, df: pd.DataFrame, max_rows: int = 30):
        """Render a DataFrame as a simple PDF table."""
        self.set_font("Helvetica", "B", 8)
        col_w = min(40, int(180 / max(len(df.columns), 1)))
        cols = ["Index"] + list(df.columns)
        effective_w = min(40, int(180 / max(len(cols), 1)))

        # Header
        for col in cols:
            self.cell(effective_w, 6, str(col)[:18], border=1)
        self.ln()

        # Rows
        self.set_font("Helvetica", size=7)
        for i, (idx, row) in enumerate(df.head(max_rows).iterrows()):
            self.cell(effective_w, 5, str(idx)[:18], border=1)
            for val in row:
                self.cell(effective_w, 5, str(val)[:18], border=1)
            self.ln()
        self.ln(2)


def build_pdf_report(
    df: pd.DataFrame,
    stats: pd.DataFrame | None = None,
    missing: pd.DataFrame | None = None,
    duplicates: int = 0,
    low_var_cols: list[str] | None = None,
) -> bytes:
    """
    Build and return a simplified PDF report.
    Includes dataset overview, missing values, duplicates, and descriptive stats.
    """
    pdf = _ReportPDF()
    pdf.add_page()

    # --- Dataset overview ---
    pdf.section_title("1. Apercu du dataset")
    pdf.body_text(
        f"Dimensions : {df.shape[0]} lignes x {df.shape[1]} colonnes\n"
        f"Doublons detectes : {duplicates}\n"
        f"Colonnes numeriques : {len(df.select_dtypes(include='number').columns)}\n"
        f"Colonnes categorielles : {len(df.select_dtypes(include=['object','category','bool']).columns)}"
    )

    # --- Missing values ---
    pdf.section_title("2. Valeurs manquantes")
    if missing is not None and not missing.empty:
        pdf.dataframe_table(missing)
    else:
        pdf.body_text("Aucune valeur manquante detectee.")

    # --- Low variance ---
    pdf.section_title("3. Colonnes a faible variance")
    if low_var_cols:
        pdf.body_text("Colonnes candidates a la suppression :\n" + ", ".join(low_var_cols))
    else:
        pdf.body_text("Aucune colonne a faible variance detectee.")

    # --- Descriptive stats ---
    if stats is not None and not stats.empty:
        pdf.section_title("4. Statistiques descriptives (colonnes numeriques)")
        pdf.dataframe_table(stats)

    return bytes(pdf.output())
