# uv run streamlit run Accueil.py

# Bibliothèque à importer

import streamlit as st

import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit.components.v1 as components

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import base64
import random

df_final = pd.read_csv("df_final_art_acteur_traduit.csv")


#**********************************************
#--- MISE EN PAGE---
#**********************************************

# --- Config page  ---
st.set_page_config(
    page_title="Cinéma EDEN",
    layout="wide",
    initial_sidebar_state= "expanded"  
)



#--- PERSONALISATION DE LA SIDEBAR---
st.markdown("""
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

button.stButton>button {
    font-size: 20px !important;   /* harmoniser taille des boutons */
}
</style>
""", unsafe_allow_html=True)

# Filtrer les films récents (par exemple sorties depuis 2020)
films_recents = df_final[df_final["startYear"] >= 2024]

# Choisir un film aléatoire
film_aleatoire = films_recents.sample(1).iloc[0]

# Affichage dans la sidebar
st.sidebar.markdown("## **Sortie récente 🎬**")

if film_aleatoire["poster_path"] not in ["", "None", None, 0]:
    st.sidebar.image(film_aleatoire["poster_path"], width=200)

st.sidebar.markdown(f"**{film_aleatoire['title']} ({film_aleatoire['startYear']})**")
# Réalisateur
st.sidebar.markdown(f"Réalisateur : {film_aleatoire['primaryName']}")

# --- LIRE ET ENCODER L'IMAGE DE FOND ---
with open("photo_eden_noir_blanc.png", "rb") as f:
    img_bytes = f.read()
encoded_bg = base64.b64encode(img_bytes).decode()

# --- CSS ---
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.8)),
        url("data:image/png;base64,{encoded_bg}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}

/* Bloc principal (inchangé) */
.custom-block {{
    padding: 30px;
    margin-bottom: 25px;
    border-radius: 20px;
    background-color: rgba(255,255,255,0.35);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 2px solid #884513;
    text-align: center;
}}

/* Trois blocs moins épais */
.custom-block-small {{
    padding: 5px 10px;  /* réduit verticalement pour moins d'épaisseur */
    margin-bottom: 15px;
    border-radius: 15px;
    background-color: rgba(255,255,255,0.35);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid #884513;
    text-align: left;
}}

h1, h2, h3 {{
    font-family: 'Playfair Display', serif;
    color: #2c2c2c;
}}

h1 {{
    font-size: 70px;
}}

h2 {{
    font-size: 32px;
}}

h3 {{
    font-size: 24px;
}}

/* Texte principal (st.write) */
p {{
    font-family: 'Playfair Display', serif;
    font-size: 50px;
    font-weight:bold;
    text-align: justify;
    line-height: 2.0;
    color: #000000;
}}

button.stButton>button {{
    width: 70%;
    padding: 8px;
    font-size: 14px;
    border-radius: 10px;
    background-color: #884513;
    color: white;
    margin-top: 5px;
}}
</style>
""", unsafe_allow_html=True)

# --- Bloc principal ---
st.markdown("""
<div class="custom-block">
    <h1 style="font-size:70px;">Bienvenue au Cinéma EDEN !</h1>
    <p style="font-size:22px; font-style: italic; text-align: center;">
        Trouvez les films qui sauront attirer votre audience.<br>
        Analysez les similarités avec les films ayant déjà rencontré du succès et planifiez votre prochaine programmation en toute confiance.
    </p>
</div>
""", unsafe_allow_html=True)

st.write("\n")  # Espacement entre les blocs
st.divider()  # Ligne de séparation entre les blocs


# --- Trois blocs en colonnes ---
col1, col2, col3 = st.columns(3, gap="large")  # crée 3 colonnes avec un espacement large

# --- Colonne 1 : Recommandations Grand Public ---
with col1:
    st.markdown("""
    <div class="custom-block-small" style="height: 250px; display:flex; flex-direction:column; justify-content:space-between;">
        <h2 style="margin:0; padding:0; line-height:1.2; text-align:center;">🎬 Recommandations</h2>
        <p style="font-size:14px; text-align:center; flex-grow:1; margin-top:10px;">
             Découvrez des films similaires à votre sélection, recommandés selon leurs genres, thèmes, acteurs et autres caractéristiques avancées. 
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Découvrir les recommandations Grand Public générées ici", key="btn_reco_col"):
        st.switch_page("pages/01_Films_Grand_Public.py")

# --- Colonne 2 : Art & Essai ---
with col2:
    st.markdown("""
    <div class="custom-block-small" style="height: 250px; display:flex; flex-direction:column; justify-content:space-between;">
        <h2 style="margin:0; padding:0; line-height:1.2; text-align:center;">🎨 Art & Essai</h2>
        <p style="font-size:14px; text-align:center; flex-grow:1; margin-top:10px;">
            Explorez les films Art & Essai et utilisez la puissance de notre modèle pour cibler uniquement des œuvres labellisées. 
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Voir les recommandations de films Art & Essai générées ici", key="btn_art_col"):
        st.switch_page("pages/02_Films_Art_Essais.py")

# --- Colonne 3 : Chiffres clés ---
with col3:
    st.markdown("""
    <div class="custom-block-small" style="height: 250px; display:flex; flex-direction:column; justify-content:space-between;">
        <h2 style="margin:0; padding:0; line-height:1.2; text-align:center;">📊 Chiffres clés</h2>
        <p style="font-size:14px; text-align:center; flex-grow:1; margin-top:10px;">
            Consultez les indicateurs clés pour analyser le succès des films et tendances du cinéma.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Consulter les chiffres et indicateurs clés des films", key="btn_ind_col"):
        st.switch_page("pages/03_Chiffres_clés.py")



# --- Expander pour détails ---
with st.expander("A propos"):
    st.write("""
    Cette application permet d’explorer des données cinématographiques et de découvrir de nouveaux films grâce à un système de recommandation basé sur l’analyse de similarités entre œuvres. 
             Elle propose également des visualisations et des indicateurs clés afin de mieux comprendre certaines tendances du cinéma. 
             L’interface interactive a été développée avec Streamlit pour offrir une exploration simple et intuitive des données.
    """)

# --- Footer ---
st.markdown("""
<div style="text-align:center; margin-top:50px; font-size:16px; color:#555;">
    &copy; 2026 Cinéma EDEN. Tous droits réservés.
</div>
""", unsafe_allow_html=True)