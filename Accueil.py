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

# --- Image de fond ---
    initial_sidebar_state="auto",

)


#--- PERSONALISATION DE LA SIDEBAR---
st.markdown("""
<style>
[data-testid="stSidebar"] * {
    font-family: 'Playfair Display', serif;   /* Police */
    font-size: 20px;                           /* Taille du texte */
}
</style>
""", unsafe_allow_html=True)


# --- LIRE ET ENCODER L'IMAGE DE FOND ---
with open("photo_eden_noir_blanc.png", "rb") as f:
    img_bytes = f.read()
encoded_bg = base64.b64encode(img_bytes).decode()

# --- CSS ---
st.markdown(f"""
<style> @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=Lora&display=swap');
/* Fond principal avec filtre semi-transparent */
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
        Découvrez le film parfait pour chaque instant !<br>
        Vos soirées cinéma n’ont jamais été aussi faciles à choisir !
    </p>
</div>
""", unsafe_allow_html=True)

st.write("\n")  # Espacement entre les blocs
st.divider()  # Ligne de séparation entre les blocs


# --- Trois blocs plus fins, empilés verticalement ---
# Bloc 1 : Recommandations
st.markdown("""
<div class="custom-block-small">
    <h2 style="margin:0; padding:0; line-height:1.2;">🎬 Recommandations</h2>
</div>
""", unsafe_allow_html=True)

st.write("\n")  # Espacement
st.write("Cette section présente un modèle de recommandation permettant de suggérer des films similaires à partir d’un film sélectionné par l’utilisateur. Le système repose sur l’analyse de caractéristiques communes entre les films (genres, thèmes, similarités entre œuvres, etc.). L’objectif est d’illustrer l’utilisation de méthodes de recommandation dans le domaine du cinéma afin d’améliorer la découverte de contenus et de proposer une expérience personnalisée.")

st.write("\n")  # Espacement

if st.button("Découvrir les recommandations", key="btn_reco"):
    st.switch_page("pages/01_Recommandation_cinema.py")

st.divider()  # Ligne de séparation entre les blocs


#bloc 2 : Art & Essai
st.markdown("""
<div class="custom-block-small">
    <h2 style="margin:0; padding:0; line-height:1.2;"> 🎨 Art & Essai</h2>
</div>
""", unsafe_allow_html=True)

st.write("\n")  # Espacement 
st.write("Cette partie est consacrée à l’exploration des films classés « Art et Essai ». Elle permet d’identifier certaines caractéristiques propres à ce type de production cinématographique et d’observer les tendances associées. L’analyse met en évidence les spécificités de ces œuvres, souvent reconnues pour leur dimension artistique, culturelle ou expérimentale.")
st.write("\n")  # Espacement 

if st.button("Voir Art & Essai", key="btn_art"):
    st.switch_page("pages\\02_Films_Art_Essais.py")

st.divider()  # Ligne de séparation entre les blocs


#Bloc 3 : Chiffres clés
st.markdown("""
<div class="custom-block-small">
    <h2 style="margin:0; padding:0; line-height:1.2;"> 📊 Chiffres clés</h2>
</div>
""", unsafe_allow_html=True)

st.write("\n")  # Espacement 

st.write("Cette section présente un modèle de recommandation permettant de suggérer des films similaires à partir d’un film sélectionné par l’utilisateur. Le système repose sur l’analyse de caractéristiques communes entre les films (genres, thèmes, similarités entre œuvres, etc.). L’objectif est d’illustrer l’utilisation de méthodes de recommandation dans le domaine du cinéma afin d’améliorer la découverte de contenus et de proposer une expérience personnalisée.")

st.write("\n")  # Espacement 

if st.button("Voir les indicateurs", key="btn_ind"):
    st.switch_page("pages\\03_Chiffres clés.py")
    

st.divider()  # Ligne de séparation entre les blocs



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