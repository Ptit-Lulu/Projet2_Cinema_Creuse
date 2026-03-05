import streamlit as st

import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import base64



# --- LIRE ET ENCODER L'IMAGE DE FOND ---
with open("Fond_ecran_app_cinema.png", "rb") as f:
    img_bytes = f.read()
encoded = base64.b64encode(img_bytes).decode()


# --- APPLIQUER L'IMAGE DE FOND AVEC UN FILTRE BLANC SEMI-TRANSPARENT ---
st.markdown(f"""
<style>

[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)),
        url("data:image/png;base64,{encoded}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}

</style>
""", unsafe_allow_html=True)



#--- PERSONALISATION DE LA SIDEBAR---
st.markdown("""
<style>
[data-testid="stSidebar"] * {
    font-family: 'Playfair Display', serif;   /* Police */
    font-size: 20px;                           /* Taille du texte */
}
</style>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import base64
import plotly.express as px
import plotly.io as pio
import streamlit.components.v1 as components
import math

# =====================================================
# DEBUT
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

def stars_html_from_rating10(rating10: float) -> str:
    # 1 étoile 
    if pd.isna(rating10):
        return ""
    x = float(rating10) / 2.0
    x = max(0.0, min(5.0, x))
    x = round(x * 2) / 2  # pas de 0.5

    full = int(math.floor(x))
    half = 1 if (x - full) >= 0.5 else 0
    empty = 5 - full - half

    full_stars = "★" * full
    empty_stars = "☆" * empty
    half_star = '<span class="half-star">★</span>' if half == 1 else ""

    return f'<span class="stars">{full_stars}{half_star}{empty_stars}</span>'

def rating_table_html(df: pd.DataFrame, title_col: str, rating_col: str) -> str:
    # IMPORTANT
    rows = []
    for _, r in df.iterrows():
        film = str(r[title_col])
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
        '</div>'
        '<div class="rating-body">'
        '<table class="rating-table"><tbody>'
        + "".join(rows) +
        '</tbody></table>'
        '</div>'
        '</div>'
    )
    return html

def plotly_card_like_notes(fig, height: int, extra_bottom_px: int = 0):
    # Fond blanc 
    html = pio.to_html(fig, include_plotlyjs="cdn", full_html=False)
    card_style = (
        "width:100%;"
        "background:rgba(255,255,255,0.94);"
        "border-radius:10px;"
        "padding:12px;"
        "box-shadow:0 10px 24px rgba(107, 75, 43, 0.12);"
    )
    inner = f'<div style="{card_style}">{html}</div>'
    components.html(inner, height=height + 40 + int(extra_bottom_px), scrolling=False)

# =====================================================
# IMAGE DE FOND APP
# =====================================================
bg_encoded = b64_png("Fond_ecran_app_cinema.png")

st.markdown(f"""
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
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
st.markdown("""
<style>
[data-testid="stSidebar"] > div:first-child { background: #e0bf7f; }
[data-testid="stSidebar"] * { color: #2b1c10 !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# IMAGES KPI (base64)
# =====================================================
kpi_bg_total = b64_png("bobine.png")
kpi_bg_art   = b64_png("piece_or.png")
kpi_bg_no    = b64_png("interdit.png")
kpi_bg_pct   = b64_png("diagram.png")

# =====================================================
# CSS GLOBAL : KPI + TITRES AU-DESSUS + TABLES NOTATION
# =====================================================
st.markdown("""
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
}
[data-testid="stHorizontalBlock"] .stMarkdown{
    margin: 0 !important;
    padding: 0 !important;
}

/* ================= KPI ================= */
.kpi-cell{
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: flex-start;
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
.kpi-green  .kpi-value{ color: #15803d; }

@media (max-width: 1400px){
    .kpi-card{ width: 330px; }
    .kpi-overlay{ padding-left: 150px; }
}
@media (max-width: 1200px){
    .kpi-card{ width: 300px; }
    .kpi-title{ font-size: 18px; }
    .kpi-value{ font-size: 40px; }
    .kpi-overlay{ padding-left: 140px; }
}

/* ================= Titres au-dessus des cadres ================= */
.chart-title-out{
    font-size: 20px;
    font-weight: 900;
    font-style: italic;
    color: rgba(35, 25, 16, 0.95);
    text-shadow: 0 2px 12px rgba(0,0,0,0.10);
    margin: 10px 0 14px 0;
}

/* ================= Tables notes + étoiles ================= */
.rating-wrap{
    width: 100%;
    background: rgba(255,255,255,0.94);
    border-radius: 10px;
    padding: 10px 10px 6px 10px;
    box-shadow: 0 10px 24px rgba(107, 75, 43, 0.12);
}
.rating-head{
    display:grid;
    grid-template-columns: 1fr 105px 48px;
    gap:10px;
    align-items:center;
    padding: 6px 6px 10px 6px;
    border-bottom: 1px solid rgba(43, 28, 16, 0.18);
}
.rh-film,.rh-note{ font-weight:900; color: rgba(35, 25, 16, 0.95); }
.rh-note{ text-align:right; }
.rating-body{ padding-top: 6px; }
.rating-table{
    width:100%;
    border-collapse:collapse;
    table-layout: fixed;
}
.rating-table tr{ border-bottom: 1px dashed rgba(43, 28, 16, 0.16); }
.rating-table td{ padding: 8px 6px; vertical-align: middle; }

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
</style>
""", unsafe_allow_html=True)

# =====================================================
# TITRE
# =====================================================
st.markdown("# Indicateurs clés ")

# =====================================================
# DATA
# =====================================================
df_final = pd.read_csv("df_final_art_acteur.csv", sep=";")
df_final["startYear"] = pd.to_numeric(df_final["startYear"], errors="coerce")

genres = df_final["genre_1"].dropna().astype(str).sort_values().unique().tolist()
genres = ["Tous"] + genres

years = df_final["startYear"].dropna().astype(int).sort_values().unique().tolist()
if not years:
    years = [2000]

# =====================================================
# SIDEBAR : Navigation
# =====================================================
st.markdown("""
<style>
[data-testid="stSidebar"] [data-baseweb="select"] > div{
    background-color: #ffffff !important;
    border-radius: 8px !important;
    border: 1px solid rgba(43, 28, 16, 0.35) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] *{
    color: #2b1c10 !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] h1{
    font-size: 30px !important;
    font-weight: 900 !important;
    margin-bottom: 12px !important;
}
.sb-label{
    font-size: 15px;
    font-weight: 900;
    font-style: italic;
    color: #2b1c10;
    margin: 6px 0 4px 0;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("# Navigation")

st.sidebar.markdown('<div class="sb-label">Genre</div>', unsafe_allow_html=True)
genre_sel = st.sidebar.selectbox("", genres, index=0, label_visibility="collapsed")

c_y1, c_y2 = st.sidebar.columns(2)
with c_y1:
    st.markdown('<div class="sb-label">Année début</div>', unsafe_allow_html=True)
    year_start = st.selectbox("", years, index=0, label_visibility="collapsed")
with c_y2:
    st.markdown('<div class="sb-label">Année fin</div>', unsafe_allow_html=True)
    year_end = st.selectbox("", years, index=len(years)-1, label_visibility="collapsed")

if year_start > year_end:
    year_start, year_end = year_end, year_start

# =====================================================
# FILTRAGE 
# =====================================================
df_f = df_final.copy()
if genre_sel != "Tous":
    df_f = df_f[df_f["genre_1"].astype(str) == genre_sel]
df_f = df_f[(df_f["startYear"] >= year_start) & (df_f["startYear"] <= year_end)]

# =====================================================
# KPI LIES AU FILTRE
# =====================================================
total_films = df_f["tconst"].nunique()
films_art = (df_f["Art_Essai"] == "Yes").sum()
films_non_art = (df_f["Art_Essai"] == "No").sum()
pct_art = (films_art / total_films) * 100 if total_films else 0

total_films_f = f"{total_films:,}".replace(",", " ")
films_art_f = f"{films_art:,}".replace(",", " ")
films_non_art_f = f"{films_non_art:,}".replace(",", " ")
pct_art_f = f"{pct_art:.2f}".replace(".", ",") + " %"

# =====================================================
# KPI CARDS
# =====================================================
col1, col2, col3, col4 = st.columns(4, gap="small")

with col1:
    st.markdown(f"""
    <div class="kpi-cell">
        <div class="kpi-card" style="
            background-image:url('data:image/png;base64,{kpi_bg_total}');
            --zoom: 1.06; --y: 0px;">
            <div class="kpi-overlay" style="--tx: -10px;">
                <div class="kpi-title"># Total de Films</div>
                <div class="kpi-value">{total_films_f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-cell">
        <div class="kpi-card kpi-orange" style="
            background-image:url('data:image/png;base64,{kpi_bg_art}');
            --zoom: 0.95; --y: 0px;">
            <div class="kpi-overlay" style="--tx: +10px;">
                <div class="kpi-title">Films Art & Essai</div>
                <div class="kpi-value">{films_art_f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-cell">
        <div class="kpi-card" style="
            background-image:url('data:image/png;base64,{kpi_bg_no}');
            --zoom: 1.01; --y: 6px;">
            <div class="kpi-overlay" style="--tx: 0px;">
                <div class="kpi-title">Films Non Art & Essai</div>
                <div class="kpi-value">{films_non_art_f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-cell">
        <div class="kpi-card kpi-green" style="
            background-image:url('data:image/png;base64,{kpi_bg_pct}');
            --zoom: 1.11; --y: -6px;">
            <div class="kpi-overlay" style="--tx: 0px;">
                <div class="kpi-title">% Art & Essai</div>
                <div class="kpi-value">{pct_art_f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# PREP DONNEES VISUELS
# =====================================================
df_f["acteur_principal_"] = df_f["acteur_principal_"].fillna("").astype(str)
df_f = df_f[df_f["acteur_principal_"].str.strip().ne("")]
df_f = df_f[df_f["acteur_principal_"].str.lower().ne("inconnu")]

df_d = df_f.copy()
df_d["primaryName"] = df_d["primaryName"].fillna("").astype(str)
df_d["primaryProfession"] = df_d["primaryProfession"].fillna("").astype(str)
df_d = df_d[df_d["primaryName"].str.strip().ne("")]
df_d = df_d[df_d["primaryName"].str.lower().ne("inconnu")]
df_d = df_d[df_d["primaryProfession"].str.lower().str.contains("director", na=False)]

df_f["revenue"] = pd.to_numeric(df_f["revenue"], errors="coerce").fillna(0)
df_f["budget"] = pd.to_numeric(df_f["budget"], errors="coerce").fillna(0)

# =====================================================
# TOP 10 ACTEURS DIRECTEURS / FILMS
# =====================================================
top10_count = (
    df_f.groupby("acteur_principal_")["tconst"]
    .nunique()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .rename(columns={"acteur_principal_": "Nom", "tconst": "Valeur"})
)

top10_rev = (
    df_f.groupby("acteur_principal_")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .rename(columns={"acteur_principal_": "Nom", "revenue": "Valeur"})
)

top10_dir_count = (
    df_d.groupby("primaryName")["tconst"]
    .nunique()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .rename(columns={"primaryName": "Nom", "tconst": "Valeur"})
)

top10_dir_rev = (
    df_d.groupby("primaryName")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .rename(columns={"primaryName": "Nom", "revenue": "Valeur"})
)

df_movies = df_f.copy()
df_movies["title"] = df_movies["title"].fillna("").astype(str)
df_movies = df_movies[df_movies["title"].str.strip().ne("")]

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
FONT = "rgba(35, 25, 16, 0.95)"
BLACK = "#111111"
GRID = "rgba(43, 28, 16, 0.12)"
INBAR = "rgba(245,245,245,0.95)"

BAR_ACTEURS = "#d97706"
BAR_DIRECTEURS = "#0f766e"
BAR_FILMS = "#c2410c"

def style_barh_inside_names(fig, bar_color, height=460, left_margin=60):
    fig.update_traces(
        marker_color=bar_color,
        cliponaxis=False,
        textposition="inside",
        insidetextanchor="start",
        textfont=dict(color=INBAR, size=16, family="Arial Black"),
        texttemplate="<b>%{text}</b>",
    )
    fig.update_layout(
        height=height,
        margin=dict(l=left_margin, r=60, t=10, b=10),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color=FONT, size=15),
        xaxis=dict(
            title=None,
            showgrid=True,
            gridcolor=GRID,
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
        ann.append(dict(
            x=x,
            y=y,
            xref="x",
            yref="y",
            text=f"<b>{lab}</b>",
            showarrow=False,
            xanchor="left",
            xshift=8,
            font=dict(color=BLACK, size=13),
        ))
    fig.update_layout(annotations=ann)
    return fig

def draw_top10_bar(df_top: pd.DataFrame, value_is_money: bool, bar_color: str, height: int = 460):
    if df_top.empty:
        st.info("Aucune donnée disponible pour ce filtre.")
        return

    dfp = df_top.sort_values("Valeur", ascending=True).copy()
    fig = px.bar(dfp, x="Valeur", y="Nom", orientation="h", text="Nom")
    fig = style_barh_inside_names(fig, bar_color=bar_color, height=height, left_margin=60)

    if value_is_money:
        labels = [fmt_usd(v) for v in dfp["Valeur"].tolist()]
    else:
        labels = [str(int(v)) for v in dfp["Valeur"].tolist()]

    fig = add_value_annotations(fig, y_vals=dfp["Nom"].tolist(), x_vals=dfp["Valeur"].tolist(), labels=labels)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def chart_block(title_html: str, df_top: pd.DataFrame, value_is_money: bool, bar_color: str):
    st.markdown(f'<div class="chart-title-out">{title_html}</div>', unsafe_allow_html=True)
    with st.container(border=True):
        draw_top10_bar(df_top, value_is_money=value_is_money, bar_color=bar_color, height=460)

# =====================================================
# AFFICHAGE 3 LIGNES x 2 CADRES (6 GRAPHES)
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
df_rate["averageRating"] = pd.to_numeric(df_rate["averageRating"], errors="coerce")
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

def rating_block(title_html: str, df_top: pd.DataFrame):
    st.markdown(f'<div class="chart-title-out">{title_html}</div>', unsafe_allow_html=True)
    if df_top.empty:
        st.info("Aucune donnée disponible pour ce filtre.")
    else:
        st.markdown(rating_table_html(df_top, "Film", "Note"), unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="large")
with c1:
    rating_block("TOP 10 FILMS LES MIEUX NOTÉS", top10_best)
with c2:
    rating_block("TOP 10 FILMS LES MOINS BIEN NOTÉS", top10_worst)
with c3:
    rating_block("TOP 10 FILMS LES MIEUX NOTÉS (Art & Essai)", top10_best_art)

# =====================================================
# NOUVEAUX VISUELS SOUS LES CARTES NOTES 
# - Camembert 
# - Barres : #tconst par décennie 
# + Fond blanc 
# + Décennies 
# + Barres 
# =====================================================

# -------- Camember
df_gen = df_f.copy()
df_gen["genre_1"] = df_gen["genre_1"].fillna("Inconnu").astype(str)
gen_counts = (
    df_gen.groupby("genre_1")["tconst"]
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
        font=dict(size=13, color="rgba(35, 25, 16, 0.95)")
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(35, 25, 16, 0.95)")
)

# -------- Bars par décennie 
df_dec = df_f.copy()
df_dec["startYear"] = pd.to_numeric(df_dec["startYear"], errors="coerce")
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
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(35, 25, 16, 0.95)"),
    xaxis=dict(
        title=None,
        showgrid=False,
        tickfont=dict(size=15, color="rgba(35, 25, 16, 0.95)"),
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

# -------- test
left, right = st.columns([1, 2], gap="large")

with left:
    st.markdown('<div class="chart-title-out">Top 5 Genres</div>', unsafe_allow_html=True)
    plotly_card_like_notes(fig_pie, height=360)

with right:
    st.markdown('<div class="chart-title-out">Nombre de films par décennie</div>', unsafe_allow_html=True)
    plotly_card_like_notes(fig_dec, height=360, extra_bottom_px=20)