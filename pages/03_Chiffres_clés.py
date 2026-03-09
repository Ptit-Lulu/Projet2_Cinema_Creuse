
import os
import math
import base64
from html import escape

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# =====================================================
# FONCTIONS
# =====================================================
def b64_png(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def fmt_usd(n: float) -> str:
    n = float(n)
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000_000:
        return f"{sign}${n/1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"{sign}${n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"{sign}${n/1_000:.0f}K"
    return f"{sign}${n:.0f}"

def read_csv_robust(path: str) -> pd.DataFrame:
    essais = [
        {"sep": ";", "engine": "python"},
        {"sep": ",", "engine": "python"},
        {"sep": None, "engine": "python"},
    ]

    best_df = None
    best_cols = -1

    for params in essais:
        try:
            df_try = pd.read_csv(path, **params)
            if df_try.shape[1] > best_cols:
                best_df = df_try.copy()
                best_cols = df_try.shape[1]
        except Exception:
            pass

    if best_df is None:
        raise ValueError(f"Impossible de lire le fichier : {path}")

    return best_df

def stars_html_from_rating10(rating10: float) -> str:
    if pd.isna(rating10):
        return ""

    x = float(rating10) / 2.0
    x = max(0.0, min(5.0, x))
    x = round(x * 2) / 2

    full = int(math.floor(x))
    half = 1 if (x - full) >= 0.5 else 0
    empty = 5 - full - half

    full_stars = "★" * full
    empty_stars = "☆" * empty
    half_star = '<span class="half-star">★</span>' if half == 1 else ""

    return f'<span class="stars">{full_stars}{half_star}{empty_stars}</span>'

def rating_table_html(df: pd.DataFrame, title_col: str, rating_col: str) -> str:
    rows = []

    for _, r in df.iterrows():
        film = escape(str(r[title_col]))
        note = float(r[rating_col]) if not pd.isna(r[rating_col]) else None
        note_txt = f"{note:.1f}".replace(".", ",") if note is not None else ""
        stars = stars_html_from_rating10(note) if note is not None else ""

        rows.append(
            "<tr>"
            f'<td class="col-film" title="{film}">{film}</td>'
            f'<td class="col-stars">{stars}</td>'
            f'<td class="col-note">{note_txt}</td>'
            "</tr>"
        )

    html = (
        '<div class="rating-wrap">'
        '<div class="rating-head">'
        '<div class="rh-film">Film</div>'
        '<div class="rh-stars"></div>'
        '<div class="rh-note">Note</div>'
        "</div>"
        '<div class="rating-body">'
        '<table class="rating-table"><tbody>'
        + "".join(rows) +
        "</tbody></table>"
        "</div>"
        "</div>"
    )
    return html

def render_plotly_card(fig, height: int, extra_bottom_px: int = 0):
    fig.update_layout(autosize=True)

    plot_html = pio.to_html(
        fig,
        include_plotlyjs="cdn",
        full_html=False,
        config={
            "displayModeBar": False,
            "responsive": True
        }
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                background: transparent;
                overflow: hidden;
            }}

            * {{
                box-sizing: border-box;
            }}

            .outer {{
                width: 100%;
                padding: 4px 4px 8px 4px;
                background: transparent;
            }}

            .card {{
                width: 100%;
                background: #ffffff;
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: 18px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05);
                overflow: hidden;
            }}

            .inner {{
                width: 100%;
                padding: 12px 12px 16px 12px;
                background: #ffffff;
                border-radius: 18px;
                overflow: hidden;
            }}

            .plotly, .js-plotly-plot, .plot-container, .plotly-graph-div {{
                width: 100% !important;
            }}
        </style>
    </head>
    <body>
        <div class="outer">
            <div class="card">
                <div class="inner">
                    {plot_html}
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    components.html(
        html,
        height=height + 44 + int(extra_bottom_px),
        scrolling=False
    )

def style_barh_inside_names(fig, bar_color, height=460, left_margin=60):
    fig.update_traces(
        marker_color=bar_color,
        cliponaxis=False,
        textposition="inside",
        insidetextanchor="start",
        textfont=dict(color="rgba(245,245,245,0.95)", size=16, family="Arial Black"),
        texttemplate="<b>%{text}</b>",
    )

    fig.update_layout(
        height=height,
        margin=dict(l=left_margin, r=60, t=10, b=16),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color="rgba(58, 36, 21, 0.98)", size=15),
        xaxis=dict(
            title=None,
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            ticks="",
        ),
        yaxis=dict(
            title=None,
            showgrid=False,
            showticklabels=False,
        ),
    )
    return fig

def add_value_annotations(fig, y_vals, x_vals, labels):
    ann = []

    for y, x, lab in zip(y_vals, x_vals, labels):
        ann.append(
            dict(
                x=x,
                y=y,
                xref="x",
                yref="y",
                text=f"<b>{lab}</b>",
                showarrow=False,
                xanchor="left",
                xshift=8,
                font=dict(color="#111111", size=15),
            )
        )

    fig.update_layout(annotations=ann)
    return fig

def build_top10_bar(df_top: pd.DataFrame, value_is_money: bool, bar_color: str, height: int = 460):
    if df_top.empty:
        return None

    dfp = df_top.sort_values("Valeur", ascending=True).copy()
    fig = px.bar(dfp, x="Valeur", y="Nom", orientation="h", text="Nom")
    fig = style_barh_inside_names(fig, bar_color=bar_color, height=height, left_margin=60)

    if value_is_money:
        labels = [fmt_usd(v) for v in dfp["Valeur"].tolist()]
    else:
        labels = [str(int(v)) for v in dfp["Valeur"].tolist()]

    fig = add_value_annotations(
        fig,
        y_vals=dfp["Nom"].tolist(),
        x_vals=dfp["Valeur"].tolist(),
        labels=labels,
    )

    return fig

def chart_block(title_html: str, df_top: pd.DataFrame, value_is_money: bool, bar_color: str):
    st.markdown(f'<div class="chart-title-out">{title_html}</div>', unsafe_allow_html=True)

    fig = build_top10_bar(df_top, value_is_money=value_is_money, bar_color=bar_color, height=460)

    if fig is None:
        st.info("Aucune donnée disponible pour ce filtre.")
    else:
        render_plotly_card(fig, height=460, extra_bottom_px=8)

def rating_block(title_html: str, df_top: pd.DataFrame):
    st.markdown(f'<div class="chart-title-out">{title_html}</div>', unsafe_allow_html=True)

    if df_top.empty:
        st.info("Aucune donnée disponible pour ce filtre.")
    else:
        st.markdown(rating_table_html(df_top, "Film", "Note"), unsafe_allow_html=True)

def render_kpi_card(bg_b64: str, title: str, value: str, zoom: float, y: int, tx: int = 0, extra_class: str = ""):
    return f"""
    <div class="kpi-cell">
        <div class="kpi-stage">
            <div class="kpi-card {extra_class}" style="
                background-image:url('data:image/png;base64,{bg_b64}');
                --zoom:{zoom};
                --y:{y}px;">
                <div class="kpi-overlay" style="--tx:{tx}px;">
                    <div class="kpi-title">{title}</div>
                    <div class="kpi-value">{value}</div>
                </div>
            </div>
        </div>
    </div>
    """

def compute_positive_tickvals(max_value: float, nb_ticks: int = 6) -> list:
    if max_value is None or pd.isna(max_value) or max_value <= 0:
        return []

    raw_step = float(max_value) / max(nb_ticks, 1)
    power = 10 ** math.floor(math.log10(raw_step)) if raw_step > 0 else 1
    ratio = raw_step / power

    if ratio <= 1:
        nice = 1
    elif ratio <= 2:
        nice = 2
    elif ratio <= 5:
        nice = 5
    else:
        nice = 10

    step = int(nice * power)
    if step <= 0:
        step = 1

    top = int(math.ceil(max_value / step) * step)
    return list(range(step, top + step, step))

def first_valid_string(series: pd.Series) -> str:
    for v in series:
        if pd.notna(v):
            s = str(v).strip()
            if s and s.lower() not in ("nan", "none", "null"):
                return s
    return ""

def is_valid_actor_image_url(url: str) -> bool:
    if pd.isna(url):
        return False
    s = str(url).strip()
    if not s:
        return False
    s_low = s.lower()

    if "image_non_disponible" in s_low:
        return False
    if "raw.githubusercontent.com" in s_low and "image_non_disponible" in s_low:
        return False

    return s_low.startswith("https://image.tmdb.org/") or s_low.startswith("http://image.tmdb.org/")

def render_actor_card(name: str, note: float, image_url: str) -> str:
    name_html = escape(str(name))
    note_txt = f"{float(note):.1f}".replace(".", ",")
    stars = stars_html_from_rating10(float(note))

    img_html = f'<img src="{escape(image_url.strip())}" alt="{name_html}" class="actor-img"/>'

    return f"""
    <div class="actor-card-wrap">
        <div class="actor-card">
            <div class="actor-image-zone">
                {img_html}
            </div>
            <div class="actor-info-zone">
                <div class="actor-name" title="{name_html}">{name_html}</div>
                <div class="actor-rating-row">
                    <div class="actor-note">{note_txt}/10</div>
                    <div class="actor-stars">{stars}</div>
                </div>
            </div>
        </div>
    </div>
    """

# =====================================================
# CSS SIDEBAR TYPO
# =====================================================
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] * {
        font-family: 'Playfair Display', serif !important;
        font-size: 20px !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: 'Playfair Display', serif !important;
        font-size: 20px !important;
        font-weight: normal;
    }

    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] .st-bq {
        font-family: 'Playfair Display', serif !important;
        font-size: 20px !important;
    }

    button.stButton > button {
        font-size: 20px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =====================================================
# IMAGE DE FOND APP
# =====================================================
bg_encoded = b64_png("Fond_ecran_app_cinema.png")

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background:
            linear-gradient(rgba(255,255,255,0.75), rgba(255,255,255,0.75)),
            url("data:image/png;base64,{bg_encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =====================================================
# SIDEBAR COULEUR
# =====================================================
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] > div:first-child { background: #e0bf7f; }
    [data-testid="stSidebar"] * { color: #2b1c10 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =====================================================
# IMAGES KPI
# =====================================================
kpi_bg_total = b64_png("bobine.png")
kpi_bg_art = b64_png("piece_or.png")
kpi_bg_no = b64_png("interdit.png")
kpi_bg_pct = b64_png("diagram.png")

# =====================================================
# CSS GLOBAL
# =====================================================
st.markdown(
    """
    <style>
    .block-container{
        max-width: 100% !important;
        padding-top: 0.8rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    h1{
        font-size: 46px !important;
        margin-bottom: 1.2rem !important;
        color: #3a2415 !important;
    }

    [data-testid="stHorizontalBlock"] .stMarkdown{
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ================= TITRE PAGE ================= */
    .page-title-row{
        display:flex;
        align-items:center;
        gap:14px;
        margin: 6px 0 18px 0;
    }

    .page-title-text{
        font-size: 46px;
        font-weight: 900;
        line-height: 1.05;
        color: #2f1d11;
        text-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }

    .page-title-stars{
        display:flex;
        align-items:center;
        gap:3px;
        margin-left: 4px;
    }

    .page-title-stars span{
        font-size: 22px;
        color: #f2b01e;
        text-shadow:
            0 2px 6px rgba(0,0,0,0.14),
            0 0 6px rgba(255,224,130,0.35);
        line-height: 1;
    }

    /* ================= KPI ================= */
    .kpi-cell{
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .kpi-stage{
        width: 360px;
        height: 168px;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: visible;
    }

    .kpi-card{
        position: relative;
        width: 360px;
        aspect-ratio: 3 / 2;
        height: auto;
        background-repeat: no-repeat !important;
        background-size: contain !important;
        background-position: center center !important;
        transform: translateY(var(--y, 0px)) scale(var(--zoom, 1.00));
        transform-origin: center center;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        background-color: transparent !important;
        overflow: visible !important;
    }

    .kpi-overlay{
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding-left: 160px;
        padding-right: 18px;
        padding-top: 2px;
        transform: translateX(var(--tx, 0px));
    }

    .kpi-title{
        font-size: 19px;
        font-weight: 900;
        color: rgba(35, 25, 16, 0.92);
        text-shadow: 0 2px 12px rgba(0,0,0,0.12);
        line-height: 1.05;
        margin-bottom: 8px;
        white-space: nowrap;
    }

    .kpi-value{
        font-size: 44px;
        font-weight: 900;
        color: #1f1f1f;
        text-shadow: 0 2px 16px rgba(0,0,0,0.14);
        letter-spacing: 0.2px;
        line-height: 1.0;
    }

    .kpi-orange .kpi-value{
        color: #2b1c10;
        text-shadow: 0 2px 18px rgba(0,0,0,0.18);
    }

    .kpi-green .kpi-value{
        color: #15803d;
    }

    @media (max-width: 1400px){
        .kpi-stage{ width: 330px; height: 156px; }
        .kpi-card{ width: 330px; }
        .kpi-overlay{ padding-left: 150px; }
    }

    @media (max-width: 1200px){
        .kpi-stage{ width: 300px; height: 144px; }
        .kpi-card{ width: 300px; }
        .kpi-title{ font-size: 18px; }
        .kpi-value{ font-size: 40px; }
        .kpi-overlay{ padding-left: 140px; }
    }

    /* ================= TITRES BLOCS ================= */
    .chart-title-out{
        font-size: 20px;
        font-weight: 900;
        font-style: italic;
        color: #4b2e1f;
        text-shadow: 0 2px 12px rgba(0,0,0,0.08);
        margin: 10px 0 14px 0;
    }

    /* ================= TABLES NOTES ================= */
    .rating-wrap{
        width: 100%;
        background: rgba(255,255,255,0.97);
        border-radius: 18px;
        padding: 10px 10px 6px 10px;
        border: 1px solid rgba(0,0,0,0.08);
        box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05);
    }

    .rating-head{
        display:grid;
        grid-template-columns: 1fr 105px 48px;
        gap:10px;
        align-items:center;
        padding: 6px 6px 10px 6px;
        border-bottom: 1px solid rgba(43, 28, 16, 0.18);
    }

    .rh-film,.rh-note{
        font-weight:900;
        color: #4b2e1f;
    }

    .rh-note{
        text-align:right;
    }

    .rating-body{
        padding-top: 6px;
    }

    .rating-table{
        width:100%;
        border-collapse:collapse;
        table-layout: fixed;
    }

    .rating-table tr{
        border-bottom: 1px dashed rgba(43, 28, 16, 0.16);
    }

    .rating-table td{
        padding: 8px 6px;
        vertical-align: middle;
    }

    .col-film{
        font-weight: 800;
        color: rgba(35, 25, 16, 0.92);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .col-stars{
        width: 105px;
        text-align: left;
        white-space: nowrap;
    }

    .col-note{
        width: 48px;
        text-align: right;
        font-weight: 900;
        color: rgba(35, 25, 16, 0.95);
    }

    .stars{
        font-size: 16px;
        letter-spacing: 1px;
        color: #f59e0b;
        text-shadow: 0 1px 6px rgba(0,0,0,0.12);
        display: inline-block;
        width: 105px;
    }

    .half-star{
        position: relative;
        display: inline-block;
        color: rgba(245, 158, 11, 0.25);
    }

    .half-star::after{
        content:"★";
        position:absolute;
        left:0;
        top:0;
        width:50%;
        overflow:hidden;
        color:#f59e0b;
    }

    /* ================= CARTES ACTEURS ================= */
    .actor-card-wrap{
        width:100%;
        margin-bottom: 18px;
    }

    .actor-card{
        width:100%;
        background: rgba(255,255,255,0.98);
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(0,0,0,0.08);
        box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05);
    }

    .actor-image-zone{
        width:100%;
        aspect-ratio: 3 / 4;
        background: linear-gradient(180deg, #f7f1e5 0%, #ece3d0 100%);
        overflow:hidden;
    }

    .actor-img{
        width:100%;
        height:100%;
        object-fit: cover;
        display:block;
    }

    .actor-info-zone{
        background:#ffffff;
        padding: 12px 12px 14px 12px;
        min-height: 86px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        gap: 8px;
    }

    .actor-name{
        font-size: 18px;
        font-weight: 900;
        color:#1f1f1f;
        line-height:1.15;
        min-height: 40px;
        display:-webkit-box;
        -webkit-line-clamp:2;
        -webkit-box-orient: vertical;
        overflow:hidden;
    }

    .actor-rating-row{
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:10px;
    }

    .actor-note{
        font-size:16px;
        font-weight:900;
        color:#4b2e1f;
        white-space:nowrap;
    }

    .actor-stars .stars{
        width:auto;
        font-size:15px;
        letter-spacing:0.5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =====================================================
# CHARGEMENT DATA
# =====================================================
possible_files = [
    "df_final_art_acteur_traduit.csv",
    "df_final_art_acteur.csv",
]

csv_path = None
for f in possible_files:
    if os.path.exists(f):
        csv_path = f
        break

if csv_path is None:
    st.error("Fichier CSV principal introuvable.")
    st.stop()

try:
    df_final = read_csv_robust(csv_path)
except Exception as e:
    st.error(f"Impossible de lire le CSV principal : {e}")
    st.stop()

df_final.columns = [str(c).replace("\ufeff", "").strip() for c in df_final.columns]

required_cols = [
    "tconst",
    "title",
    "startYear",
    "runtimeMinutes",
    "primaryName",
    "primaryProfession",
    "averageRating",
    "budget",
    "revenue",
    "genre_1",
    "Art_Essai",
    "acteur_principal_",
]

missing_cols = [c for c in required_cols if c not in df_final.columns]
if missing_cols:
    st.error(f"Colonnes manquantes dans le CSV principal : {missing_cols}")
    st.stop()

# =====================================================
# CHARGEMENT DF IMAGES ACTEURS
# =====================================================
possible_files_web = [
    "df_final_web_acteur.csv",
]

web_actor_path = None
for f in possible_files_web:
    if os.path.exists(f):
        web_actor_path = f
        break

if web_actor_path is not None:
    try:
        df_web_acteur = read_csv_robust(web_actor_path)
        df_web_acteur.columns = [str(c).replace("\ufeff", "").strip() for c in df_web_acteur.columns]
    except Exception:
        df_web_acteur = pd.DataFrame(columns=["tconst", "acteur_principal_", "actor_image_url"])
else:
    df_web_acteur = pd.DataFrame(columns=["tconst", "acteur_principal_", "actor_image_url"])

for c in ["tconst", "acteur_principal_", "actor_image_url"]:
    if c not in df_web_acteur.columns:
        df_web_acteur[c] = ""

# =====================================================
# CHARGEMENT DF TRADUCTION GENRES
# =====================================================
possible_files_genre = [
    "df_final_genre.csv",
]

genre_path = None
for f in possible_files_genre:
    if os.path.exists(f):
        genre_path = f
        break

if genre_path is not None:
    try:
        df_genre_ref = read_csv_robust(genre_path)
        df_genre_ref.columns = [str(c).replace("\ufeff", "").strip() for c in df_genre_ref.columns]
    except Exception:
        df_genre_ref = pd.DataFrame(columns=["genre_1", "Genre_fr"])
else:
    df_genre_ref = pd.DataFrame(columns=["genre_1", "Genre_fr"])

for c in ["genre_1", "Genre_fr"]:
    if c not in df_genre_ref.columns:
        df_genre_ref[c] = ""

# =====================================================
# TYPES
# =====================================================
df_final["startYear"] = pd.to_numeric(df_final["startYear"], errors="coerce")
df_final["runtimeMinutes"] = pd.to_numeric(df_final["runtimeMinutes"], errors="coerce")
df_final["budget"] = pd.to_numeric(df_final["budget"], errors="coerce").fillna(0)
df_final["revenue"] = pd.to_numeric(df_final["revenue"], errors="coerce").fillna(0)
df_final["averageRating"] = pd.to_numeric(df_final["averageRating"], errors="coerce")
df_final["Art_Essai"] = df_final["Art_Essai"].fillna("").astype(str)

df_web_acteur["acteur_principal_"] = df_web_acteur["acteur_principal_"].fillna("").astype(str)
df_web_acteur["actor_image_url"] = df_web_acteur["actor_image_url"].fillna("").astype(str)

df_genre_ref["genre_1"] = df_genre_ref["genre_1"].fillna("").astype(str)
df_genre_ref["Genre_fr"] = df_genre_ref["Genre_fr"].fillna("").astype(str)

# =====================================================
# MAPPING GENRES EN -> FR
# =====================================================
df_genre_ref = df_genre_ref[df_genre_ref["genre_1"].str.strip().ne("")]
df_genre_ref = df_genre_ref.drop_duplicates(subset=["genre_1"], keep="first").copy()

genre_en_to_fr = {}
for _, row in df_genre_ref.iterrows():
    k = str(row["genre_1"]).strip()
    v = str(row["Genre_fr"]).strip()
    genre_en_to_fr[k] = v if v else k

genres_en = (
    df_final["genre_1"]
    .dropna()
    .astype(str)
    .str.strip()
)
genres_en = genres_en[genres_en.ne("")]
genres_en = sorted(genres_en.unique().tolist())

genre_pairs = []
for g_en in genres_en:
    g_fr = genre_en_to_fr.get(g_en, g_en)
    genre_pairs.append((g_fr, g_en))

genre_pairs = sorted(genre_pairs, key=lambda x: x[0].lower())
genre_display_labels = ["Tous"] + [fr for fr, _ in genre_pairs]
genre_display_to_en = {"Tous": "Tous"}
for fr, en in genre_pairs:
    genre_display_to_en[fr] = en

# =====================================================
# MAP IMAGES ACTEURS 
# =====================================================
df_actor_img_map = df_web_acteur.copy()
df_actor_img_map = df_actor_img_map[df_actor_img_map["acteur_principal_"].str.strip().ne("")]
df_actor_img_map = df_actor_img_map[df_actor_img_map["actor_image_url"].apply(is_valid_actor_image_url)].copy()

df_actor_img_map = (
    df_actor_img_map.groupby("acteur_principal_")["actor_image_url"]
    .agg(first_valid_string)
    .reset_index()
)

df_actor_img_map = df_actor_img_map[df_actor_img_map["actor_image_url"].apply(is_valid_actor_image_url)].copy()
actor_to_image = dict(zip(df_actor_img_map["acteur_principal_"], df_actor_img_map["actor_image_url"]))

# =====================================================
# PRÉPARATION FILTRES
# =====================================================
years = df_final["startYear"].dropna().astype(int).sort_values().unique().tolist()
if not years:
    years = [2000]

art_options = ["Tous", "Art & Essai", "Non Art & Essai"]

note_values = sorted(df_final["averageRating"].dropna().round(1).unique().tolist())
if not note_values:
    note_values = [0.0]

runtime_values = sorted(
    df_final.loc[df_final["runtimeMinutes"].notna() & (df_final["runtimeMinutes"] > 0), "runtimeMinutes"]
    .round()
    .astype(int)
    .unique()
    .tolist()
)
if not runtime_values:
    runtime_values = [0]

note_min_global = float(note_values[0])
note_max_global = float(note_values[-1])
runtime_min_global = int(runtime_values[0])
runtime_max_global = int(runtime_values[-1])

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] [data-baseweb="select"] > div{
        background-color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05) !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] *{
        color: #2b1c10 !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] h1{
        font-size: 30px !important;
        font-weight: 900 !important;
        margin-bottom: 12px !important;
        color: #4b2e1f !important;
    }

    .sb-label{
        font-size: 15px;
        font-weight: 900;
        font-style: italic;
        color: #4b2e1f;
        margin: 6px 0 4px 0;
    }

    div[data-baseweb="popover"]{
        background: #ffffff !important;
    }

    div[data-baseweb="popover"] > div{
        background: #ffffff !important;
        border-radius: 16px !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05) !important;
    }

    div[data-baseweb="popover"] ul{
        background: #ffffff !important;
    }

    div[data-baseweb="popover"] li{
        background: #ffffff !important;
        color: #2b1c10 !important;
        font-weight: 700 !important;
    }

    div[data-baseweb="popover"] li:hover{
        background: #f7f1e5 !important;
    }

    div[data-baseweb="popover"] li[aria-selected="true"]{
        background: #f0e2c3 !important;
        color: #2b1c10 !important;
    }

    div[data-baseweb="popover"] [role="listbox"]{
        background: #ffffff !important;
    }

    div[data-baseweb="popover"] [role="option"]{
        background: #ffffff !important;
        color: #2b1c10 !important;
        font-weight: 700 !important;
    }

    div[data-baseweb="popover"] [role="option"]:hover{
        background: #f7f1e5 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("# Navigation")

st.sidebar.markdown('<div class="sb-label">Genre</div>', unsafe_allow_html=True)
genre_sel_display = st.sidebar.selectbox("", genre_display_labels, index=0, label_visibility="collapsed")
genre_sel = genre_display_to_en.get(genre_sel_display, "Tous")

st.sidebar.markdown('<div class="sb-label">Type de films</div>', unsafe_allow_html=True)
art_sel = st.sidebar.selectbox("", art_options, index=0, label_visibility="collapsed")

c_y1, c_y2 = st.sidebar.columns(2)
with c_y1:
    st.markdown('<div class="sb-label">Année début</div>', unsafe_allow_html=True)
    year_start = st.selectbox("", years, index=0, label_visibility="collapsed")

with c_y2:
    st.markdown('<div class="sb-label">Année fin</div>', unsafe_allow_html=True)
    year_end = st.selectbox("", years, index=len(years) - 1, label_visibility="collapsed")

c_n1, c_n2 = st.sidebar.columns(2)
with c_n1:
    st.markdown('<div class="sb-label">Note min</div>', unsafe_allow_html=True)
    note_min_sel = st.selectbox(
        "",
        note_values,
        index=0,
        format_func=lambda x: f"{float(x):.1f}".replace(".", ","),
        label_visibility="collapsed",
    )

with c_n2:
    st.markdown('<div class="sb-label">Note max</div>', unsafe_allow_html=True)
    note_max_sel = st.selectbox(
        "",
        note_values,
        index=len(note_values) - 1,
        format_func=lambda x: f"{float(x):.1f}".replace(".", ","),
        label_visibility="collapsed",
    )

c_d1, c_d2 = st.sidebar.columns(2)
with c_d1:
    st.markdown('<div class="sb-label">Durée min</div>', unsafe_allow_html=True)
    duration_min_sel = st.selectbox(
        "",
        runtime_values,
        index=0,
        format_func=lambda x: f"{int(x)}",
        label_visibility="collapsed",
    )

with c_d2:
    st.markdown('<div class="sb-label">Durée max</div>', unsafe_allow_html=True)
    duration_max_sel = st.selectbox(
        "",
        runtime_values,
        index=len(runtime_values) - 1,
        format_func=lambda x: f"{int(x)}",
        label_visibility="collapsed",
    )

if year_start > year_end:
    year_start, year_end = year_end, year_start

if note_min_sel > note_max_sel:
    note_min_sel, note_max_sel = note_max_sel, note_min_sel

if duration_min_sel > duration_max_sel:
    duration_min_sel, duration_max_sel = duration_max_sel, duration_min_sel

# =====================================================
# TITRE PAGE
# =====================================================
st.markdown(
    """
    <div class="page-title-row">
        <div class="page-title-text">Indicateurs clés</div>
        <div class="page-title-stars">
            <span>★</span>
            <span>★</span>
            <span>★</span>
            <span>★</span>
            <span>★</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =====================================================
# FILTRAGE GLOBAL UNIQUE
# =====================================================
df_filtres = df_final.copy()

if genre_sel != "Tous":
    df_filtres = df_filtres[df_filtres["genre_1"].astype(str) == genre_sel]

df_filtres = df_filtres[
    (df_filtres["startYear"] >= year_start) &
    (df_filtres["startYear"] <= year_end)
]

if art_sel == "Art & Essai":
    df_filtres = df_filtres[df_filtres["Art_Essai"] == "Yes"]
elif art_sel == "Non Art & Essai":
    df_filtres = df_filtres[df_filtres["Art_Essai"] == "No"]

note_filter_active = (float(note_min_sel) > note_min_global) or (float(note_max_sel) < note_max_global)
if note_filter_active:
    df_filtres = df_filtres[
        df_filtres["averageRating"].notna() &
        (df_filtres["averageRating"] >= float(note_min_sel)) &
        (df_filtres["averageRating"] <= float(note_max_sel))
    ]

duration_filter_active = (int(duration_min_sel) > runtime_min_global) or (int(duration_max_sel) < runtime_max_global)
if duration_filter_active:
    df_filtres = df_filtres[
        df_filtres["runtimeMinutes"].notna() &
        (df_filtres["runtimeMinutes"] >= int(duration_min_sel)) &
        (df_filtres["runtimeMinutes"] <= int(duration_max_sel))
    ]

# =====================================================
# KPI LIÉS AUX FILTRES
# =====================================================
df_kpi = df_filtres.drop_duplicates(subset=["tconst"]).copy()

total_films = df_kpi["tconst"].nunique()
films_art = df_kpi.loc[df_kpi["Art_Essai"] == "Yes", "tconst"].nunique()
pct_art = (films_art / total_films) * 100 if total_films else 0

df_runtime = df_kpi.copy()
df_runtime = df_runtime[df_runtime["runtimeMinutes"].notna()]
df_runtime = df_runtime[df_runtime["runtimeMinutes"] > 0]
runtime_mean = df_runtime["runtimeMinutes"].mean() if not df_runtime.empty else None

total_films_f = f"{total_films:,}".replace(",", " ")
films_art_f = f"{films_art:,}".replace(",", " ")
pct_art_f = f"{pct_art:.2f}".replace(".", ",") + " %"
runtime_mean_f = f"{int(round(runtime_mean))} min" if runtime_mean is not None and not pd.isna(runtime_mean) else "—"

# =====================================================
# KPI CARDS
# =====================================================
col1, col2, col3, col4 = st.columns(4, gap="small")

with col1:
    st.markdown(
        render_kpi_card(
            bg_b64=kpi_bg_total,
            title="# Total de Films",
            value=total_films_f,
            zoom=1.06,
            y=0,
            tx=-10,
            extra_class=""
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        render_kpi_card(
            bg_b64=kpi_bg_art,
            title="Films Art & Essai",
            value=films_art_f,
            zoom=1.02,
            y=2,
            tx=10,
            extra_class="kpi-orange"
        ),
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        render_kpi_card(
            bg_b64=kpi_bg_no,
            title="Durée moyenne",
            value=runtime_mean_f,
            zoom=1.08,
            y=1,
            tx=0,
            extra_class=""
        ),
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        render_kpi_card(
            bg_b64=kpi_bg_pct,
            title="% Art & Essai",
            value=pct_art_f,
            zoom=1.14,
            y=-3,
            tx=0,
            extra_class="kpi-green"
        ),
        unsafe_allow_html=True,
    )

# =====================================================
# PRÉPARATION DONNÉES VISUELS
# =====================================================
df_actor = df_filtres.copy()
df_actor["acteur_principal_"] = df_actor["acteur_principal_"].fillna("").astype(str)
df_actor = df_actor[df_actor["acteur_principal_"].str.strip().ne("")]
df_actor = df_actor[df_actor["acteur_principal_"].str.lower().ne("inconnu")]

df_director = df_filtres.copy()
df_director["primaryName"] = df_director["primaryName"].fillna("").astype(str)
df_director["primaryProfession"] = df_director["primaryProfession"].fillna("").astype(str)
df_director = df_director[df_director["primaryName"].str.strip().ne("")]
df_director = df_director[df_director["primaryName"].str.lower().ne("inconnu")]
df_director = df_director[df_director["primaryProfession"].str.lower().str.contains("director", na=False)]

df_movies = df_filtres.copy()
df_movies["title"] = df_movies["title"].fillna("").astype(str)
df_movies = df_movies[df_movies["title"].str.strip().ne("")]

# =====================================================
# TOP 10 ACTEURS / DIRECTEURS / FILMS
# =====================================================
top10_count = (
    df_actor.groupby("acteur_principal_")["tconst"]
    .nunique()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .rename(columns={"acteur_principal_": "Nom", "tconst": "Valeur"})
)

top10_rev = (
    df_actor.groupby("acteur_principal_")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .rename(columns={"acteur_principal_": "Nom", "revenue": "Valeur"})
)

top10_dir_count = (
    df_director.groupby("primaryName")["tconst"]
    .nunique()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .rename(columns={"primaryName": "Nom", "tconst": "Valeur"})
)

top10_dir_rev = (
    df_director.groupby("primaryName")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .rename(columns={"primaryName": "Nom", "revenue": "Valeur"})
)

top10_budget = (
    df_movies[["title", "budget"]]
    .sort_values("budget", ascending=False)
    .head(10)
    .rename(columns={"title": "Nom", "budget": "Valeur"})
    .reset_index(drop=True)
)

top10_movie_rev = (
    df_movies[["title", "revenue"]]
    .sort_values("revenue", ascending=False)
    .head(10)
    .rename(columns={"title": "Nom", "revenue": "Valeur"})
    .reset_index(drop=True)
)

# =====================================================
# STYLE PLOTLY
# =====================================================
BAR_ACTEURS = "#d97706"
BAR_DIRECTEURS = "#0f766e"
BAR_FILMS = "#c2410c"

# =====================================================
# AFFICHAGE 3 LIGNES x 2 CADRES
# =====================================================
g1, g2 = st.columns(2, gap="large")
with g1:
    chart_block("TOP 10 ACTEURS — nombre de films distincts", top10_count, False, BAR_ACTEURS)
with g2:
    chart_block("TOP 10 ACTEURS — plus gros revenu cumulé", top10_rev, True, BAR_ACTEURS)

g3, g4 = st.columns(2, gap="large")
with g3:
    chart_block("TOP 10 DIRECTEURS — nombre de films distincts", top10_dir_count, False, BAR_DIRECTEURS)
with g4:
    chart_block("TOP 10 DIRECTEURS — plus gros revenu cumulé", top10_dir_rev, True, BAR_DIRECTEURS)

g5, g6 = st.columns(2, gap="large")
with g5:
    chart_block("TOP 10 FILMS — plus gros budget", top10_budget, True, BAR_FILMS)
with g6:
    chart_block("TOP 10 FILMS — plus gros revenu", top10_movie_rev, True, BAR_FILMS)

# =====================================================
# 3 VISUELS : NOTES + ÉTOILES
# =====================================================
df_rate = df_movies.copy()
df_rate = df_rate.dropna(subset=["tconst"]).drop_duplicates(subset=["tconst"], keep="first")
df_rate_art = df_rate[df_rate["Art_Essai"] == "Yes"].copy()

top10_best = (
    df_rate.dropna(subset=["averageRating"])
    .sort_values("averageRating", ascending=False)
    .head(10)[["title", "averageRating"]]
    .rename(columns={"title": "Film", "averageRating": "Note"})
)

top10_worst = (
    df_rate.dropna(subset=["averageRating"])
    .sort_values("averageRating", ascending=True)
    .head(10)[["title", "averageRating"]]
    .rename(columns={"title": "Film", "averageRating": "Note"})
)

top10_best_art = (
    df_rate_art.dropna(subset=["averageRating"])
    .sort_values("averageRating", ascending=False)
    .head(10)[["title", "averageRating"]]
    .rename(columns={"title": "Film", "averageRating": "Note"})
)

c1, c2, c3 = st.columns(3, gap="large")
with c1:
    rating_block("TOP 10 FILMS LES MIEUX NOTÉS", top10_best)
with c2:
    rating_block("TOP 10 FILMS LES MOINS BIEN NOTÉS", top10_worst)
with c3:
    rating_block("TOP 10 FILMS LES MIEUX NOTÉS (Art & Essai)", top10_best_art)

# =====================================================
# CAMEMBERT TOP 5 GENRES (AFFICHAGE FR)
# =====================================================
df_gen = df_filtres.copy()
df_gen["genre_1"] = df_gen["genre_1"].fillna("Inconnu").astype(str)
df_gen["genre_affiche"] = df_gen["genre_1"].map(genre_en_to_fr).fillna(df_gen["genre_1"])

gen_counts = (
    df_gen.groupby("genre_affiche")["tconst"]
    .nunique()
    .sort_values(ascending=False)
)

top5 = gen_counts.head(5)
others = gen_counts.iloc[5:].sum() if len(gen_counts) > 5 else 0

labels = top5.index.tolist()
values = top5.values.tolist()

if others > 0:
    labels.append("Autres")
    values.append(int(others))

labels_with_counts = [f"{lab}  {val:,}".replace(",", " ") for lab, val in zip(labels, values)]
df_pie = pd.DataFrame({"Label": labels_with_counts, "Value": values})

pie_colors = [
    "#0f766e", "#d97706", "#c2410c", "#7c2d12", "#b45309",
    "#14532d", "#0ea5a5", "#a16207", "#9a3412", "#64748b", "#3f3f46"
]

fig_pie = px.pie(
    df_pie,
    names="Label",
    values="Value",
    hole=0.62
)
fig_pie.update_traces(
    sort=False,
    marker=dict(colors=pie_colors[:len(df_pie)]),
    textinfo="none"
)
fig_pie.update_layout(
    height=360,
    margin=dict(l=10, r=10, t=10, b=10),
    showlegend=True,
    legend=dict(
        orientation="v",
        x=1.02,
        y=0.5,
        xanchor="left",
        yanchor="middle",
        font=dict(size=13, color="#4b2e1f")
    ),
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0)",
    font=dict(color="#4b2e1f")
)

# =====================================================
# BARRES PAR DÉCENNIE
# =====================================================
df_dec = df_filtres.copy()
df_dec = df_dec.dropna(subset=["startYear"])
df_dec["startYear"] = df_dec["startYear"].astype(int)
df_dec["Decennie"] = (df_dec["startYear"] // 10) * 10

dec_min = (int(year_start) // 10) * 10
dec_max = (int(year_end) // 10) * 10
all_decades = list(range(dec_min, dec_max + 10, 10))

dec_counts = (
    df_dec.groupby("Decennie")["tconst"]
    .nunique()
    .reindex(all_decades, fill_value=0)
    .reset_index()
    .rename(columns={"index": "Decennie", "tconst": "tconst"})
)

dec_counts["Decennie_lbl"] = dec_counts["Decennie"].astype(str) + "s"
dec_counts["Decennie_lbl"] = pd.Categorical(
    dec_counts["Decennie_lbl"],
    categories=[str(d) + "s" for d in all_decades],
    ordered=True
)

fig_dec = px.bar(
    dec_counts,
    x="Decennie_lbl",
    y="tconst",
    text="tconst"
)
fig_dec.update_traces(
    marker_color="#0f766e",
    texttemplate="<b>%{text}</b>",
    textposition="outside",
    cliponaxis=False
)
fig_dec.update_layout(
    height=360,
    margin=dict(l=10, r=10, t=10, b=60),
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0)",
    font=dict(color="#4b2e1f"),
    xaxis=dict(
        title=None,
        showgrid=False,
        tickfont=dict(size=15, color="#4b2e1f"),
        tickangle=0,
        categoryorder="array",
        categoryarray=[str(d) + "s" for d in all_decades],
        automargin=True
    ),
    yaxis=dict(
        title=None,
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        ticks=""
    )
)

# =====================================================
# COURBE : NOMBRE DE FILMS PAR DURÉE
# =====================================================
df_runtime_curve = df_filtres.copy()
df_runtime_curve = df_runtime_curve.dropna(subset=["tconst"]).drop_duplicates(subset=["tconst"], keep="first")
df_runtime_curve = df_runtime_curve[df_runtime_curve["runtimeMinutes"].notna()]
df_runtime_curve = df_runtime_curve[df_runtime_curve["runtimeMinutes"] > 0]

if not df_runtime_curve.empty:
    df_runtime_curve["runtimeMinutes"] = df_runtime_curve["runtimeMinutes"].round().astype(int)

runtime_dist = (
    df_runtime_curve.groupby("runtimeMinutes")["tconst"]
    .nunique()
    .reset_index()
    .rename(columns={"runtimeMinutes": "Duree", "tconst": "Nombre"})
    .sort_values("Duree")
)

fig_runtime = go.Figure()

if not runtime_dist.empty:
    fig_runtime.add_trace(
        go.Scatter(
            x=runtime_dist["Duree"],
            y=runtime_dist["Nombre"],
            mode="lines",
            line=dict(color="#0f766e", width=3, shape="spline", smoothing=1.0),
            fill="tozeroy",
            fillcolor="rgba(15,118,110,0.18)",
            hovertemplate="Durée : %{x} min<br>Nombre de films : %{y}<extra></extra>",
            showlegend=False
        )
    )

runtime_tickvals = compute_positive_tickvals(
    runtime_dist["Nombre"].max() if not runtime_dist.empty else 0,
    nb_ticks=6
)

fig_runtime.update_layout(
    height=390,
    margin=dict(l=18, r=18, t=8, b=52),
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0)",
    font=dict(color="#4b2e1f"),
    hovermode="x",
    showlegend=False,
    xaxis=dict(
        title="Durée ",
        showgrid=False,
        zeroline=False,
        tickfont=dict(size=14, color="#4b2e1f"),
        title_font=dict(size=15, color="#4b2e1f"),
        automargin=True
    ),
    yaxis=dict(
        title=None,
        showgrid=False,
        zeroline=False,
        tickmode="array",
        tickvals=runtime_tickvals,
        ticktext=[str(v) for v in runtime_tickvals],
        tickfont=dict(size=14, color="#4b2e1f"),
        automargin=True
    )
)

# =====================================================
# AFFICHAGE BAS
# =====================================================
left, right = st.columns([1, 2], gap="large")

with left:
    st.markdown('<div class="chart-title-out">Top 5 Genres</div>', unsafe_allow_html=True)
    if df_pie.empty or df_pie["Value"].sum() == 0:
        st.info("Aucune donnée disponible pour ce filtre.")
    else:
        render_plotly_card(fig_pie, height=360)

with right:
    st.markdown('<div class="chart-title-out">Nombre de films par décennie</div>', unsafe_allow_html=True)
    if dec_counts.empty:
        st.info("Aucune donnée disponible pour ce filtre.")
    else:
        render_plotly_card(fig_dec, height=360, extra_bottom_px=20)

# =====================================================
# VISUEL BAS PLEINE LARGEUR
# =====================================================
st.markdown('<div class="chart-title-out">Nombre de films par durée (minutes)</div>', unsafe_allow_html=True)
if runtime_dist.empty:
    st.info("Aucune donnée disponible pour ce filtre.")
else:
    render_plotly_card(fig_runtime, height=390, extra_bottom_px=12)

# =====================================================
# TOP 10 ACTEURS LES MIEUX NOTÉS 
# =====================================================
df_top_actor_rate = df_filtres.copy()
df_top_actor_rate["acteur_principal_"] = df_top_actor_rate["acteur_principal_"].fillna("").astype(str)
df_top_actor_rate = df_top_actor_rate[df_top_actor_rate["acteur_principal_"].str.strip().ne("")]
df_top_actor_rate = df_top_actor_rate[df_top_actor_rate["acteur_principal_"].str.lower().ne("inconnu")]
df_top_actor_rate = df_top_actor_rate[df_top_actor_rate["averageRating"].notna()]
df_top_actor_rate = df_top_actor_rate.drop_duplicates(subset=["tconst", "acteur_principal_"], keep="first")

top_actor_all = (
    df_top_actor_rate.groupby("acteur_principal_")
    .agg(
        Note=("averageRating", "mean"),
        Nb_films=("tconst", "nunique"),
    )
    .reset_index()
)

top_actor_all["actor_image_url"] = top_actor_all["acteur_principal_"].map(actor_to_image).fillna("")
top_actor_all = top_actor_all[top_actor_all["actor_image_url"].apply(is_valid_actor_image_url)].copy()

top10_actor_best = (
    top_actor_all
    .sort_values(["Note", "Nb_films", "acteur_principal_"], ascending=[False, False, True])
    .head(10)
    .copy()
)

st.markdown('<div class="chart-title-out">Top 10 des acteurs les mieux notés</div>', unsafe_allow_html=True)

if top10_actor_best.empty:
    st.info("Aucune donnée disponible pour ce filtre.")
else:
    actor_records = top10_actor_best.to_dict(orient="records")

    for i in range(0, len(actor_records), 5):
        row_records = actor_records[i:i+5]
        cols = st.columns(5, gap="large")

        for j in range(5):
            with cols[j]:
                if j < len(row_records):
                    r = row_records[j]
                    st.markdown(
                        render_actor_card(
                            name=r["acteur_principal_"],
                            note=r["Note"],
                            image_url=r["actor_image_url"],
                        ),
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown("", unsafe_allow_html=True)