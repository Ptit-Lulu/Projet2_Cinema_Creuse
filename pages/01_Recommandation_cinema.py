# Bibliothèque à importer

import base64
from datetime import date

import streamlit as st

import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


df_final = pd.read_csv("df_final_art_acteur.csv", sep =";")

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

st.set_page_config(
    page_title="Cinéma EDEN-Recommandation",
    layout="wide",
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


st.title("Pas d'idée de film ? ")

st.markdown("""
             <p 
            style="font-size: 25px;
            font-family: 'Playfair Display', serif;">
        Nous avons la solution ! Dites nous ce que vous aimez et nous vous recommanderons des films à voir !<br>
        </p>
             """, unsafe_allow_html=True)

st.sidebar.markdown("# Recommandation films 🎬")

st.sidebar.markdown("Vous connaissez un film que vous avez aimé ? Nous allons vous recommander des films similaires !")
  
recherche = st.sidebar.selectbox("Commencez à taper un titre :", df_final["title"])

st.sidebar.markdown(df_final[df_final["title"].str.contains(recherche, case=False, na=False)])

st.divider()

with st.container():
    st.markdown("""
        <span style="
            text-decoration: underline;
            text-decoration-color: black;
            text-decoration-thickness: 3px;
            font-family: 'Playfair Display', serif;
            font-size: 20px
        ">
        Sélectionnez le(s) genre(s) que vous aimez :
        </span>
        """, unsafe_allow_html=True)

     


    col1, col2, col3, col4 = st.columns(4,vertical_alignment="center", border=True)

    with col1:
        Action = st.checkbox("Action")
        Aventure = st.checkbox("Aventure")
        Animation = st.checkbox("Animation")
        Comédie = st.checkbox("Comédie")
    with col2:
        Crime = st.checkbox("Crime")
        Documentaire = st.checkbox("Documentaire")
        Drame = st.checkbox("Drame")
        Famille = st.checkbox("Famille")

    with col3:
        Fantastique = st.checkbox("Fantastique")
        Histoire = st.checkbox("Histoire")
        Guerre = st.checkbox("Guerre")
        Musique = st.checkbox("Musique")
    
    with col4:
        Romance = st.checkbox("Romance")
        Science_Fiction = st.checkbox("Science-Fiction") 
        Thriller = st.checkbox("Thriller")
        Western = st.checkbox("Western")


st.divider()

st.slider("Sélectionnez la date de sortie :",
           min_value=df_final["startYear"].min(),
           max_value=df_final["startYear"].max(),
           value=(df_final["startYear"].min(), df_final["startYear"].max())
          )

