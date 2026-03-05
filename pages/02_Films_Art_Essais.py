# Bibliothèque à importer

import base64

import streamlit as st

import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import base64

# Lire l'image locale et encoder en base64
with open("Fond_ecran_art_essai.png", "rb") as f:
    img_bytes = f.read()
encoded = base64.b64encode(img_bytes).decode()


#**********************************************
#--- MISE EN PAGE---
#**********************************************

# --- Config page  ---
st.set_page_config(
    page_title="Cinéma EDEN",
    layout="wide",
    initial_sidebar_state="expanded"  
)


 #--- CSS ---
st.markdown(f"""
<style> @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=Lora&display=swap');
/* Fond principal avec filtre semi-transparent */
[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)),
        url("data:image/png;base64,{encoded}");
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

#--- PERSONALISATION DE LA SIDEBAR---
st.markdown("""
<style>
[data-testid="stSidebar"] * {
    font-family: 'Playfair Display', serif;   /* Police */
    font-size: 20px;                           /* Taille du texte */
}
</style>
""", unsafe_allow_html=True)




st.markdown("# Section Art & Essai")
st.sidebar.markdown("# Section Art & Essai")

