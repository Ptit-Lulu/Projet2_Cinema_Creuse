# uv run streamlit run Accueil.py

# Bibliothèque à importer

import streamlit as st

import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import base64


#--- CONFIGURATION DE LA PAGE --- 



st.set_page_config(
    page_title="Cinéma EDEN",
    layout="wide",  
    initial_sidebar_state="expanded"
    
)
custom_toggle = """
<style>

/* Cible n'importe quel bouton contenant un SVG (le toggle fait partie de ceux-là) */
header button svg {
    display: none !important;
}

/* Ajoute ton icône avant le bouton toggle */
header button::before {
    content: "☰" !important;
    font-size: 26px !important;
    color: #000000 !important;
    position: relative;
    top: 2px;
}

</style>
"""

st.markdown(custom_toggle, unsafe_allow_html=True)


# --- LIRE ET ENCODER L'IMAGE DE FOND ---
with open("photo_eden_noir_blanc.png", "rb") as f:
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


# --- 1er bloc avec titre ---
st.markdown("""
<div style="
    padding: 50px;
    border-radius: 25px;
    background: rgba(255, 255, 255, 0.30);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 3px solid #884513;   
    text-align: center;
    margin-bottom: 40px;
    font-family: 'Playfair Display', serif;;        
">
    <h1 style="font-size: 70px; font-family: 'Playfair Display', serif;">
        Bienvenue au Cinéma EDEN !
    </h1>
 <p style="font-size: 25px; font-style: italic; font-family: 'Playfair Display', serif;">
        Découvrez le film parfait pour chaque instant !<br>
        Vos soirées cinéma n’ont jamais été aussi faciles à choisir !
    </p>
</div>
""", unsafe_allow_html=True)


# --- bloc personalisé ---
st.markdown("""
<div style="
    padding:20px;
    background-color: rgba(255,255,255,0.6);
    border-radius:15px;
    margin-bottom:20px;
    font-family: 'Georgia', serif;
">
<h3>Section personnalisée</h3>
<p>Contenu stylisé</p>
</div>
""", unsafe_allow_html=True)




st.title("Accueil")

st.text("Retrouvez les recommandations de films, les indicateurs clés et la section Art & Essai dans les onglets à gauche !")



with st.container():
    st.subheader("Bloc 1")
    st.write("Contenu du premier bloc")

with st.container():
    st.subheader("Bloc 2")
    st.write("Contenu du deuxième bloc")

with st.expander("Voir les détails"):
    st.write("Infos supplémentaires ici")










