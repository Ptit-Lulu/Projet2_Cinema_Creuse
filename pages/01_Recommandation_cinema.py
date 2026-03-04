# Bibliothèque à importer

import base64
from datetime import date
from pathlib import Path

import streamlit as st

import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import numpy as np

@st.cache_resource
def load_all():
    knn = joblib.load("knn_model.joblib")          # Le modèle NearestNeighbors
    pipeline = joblib.load("pipeline.joblib")  # Pour transformer les données
    X_features = joblib.load("X_features.joblib")  # Matrice déjà transformée
    return knn, pipeline, X_features

knn, pipeline, X_features = load_all()

def recommander_films_par_id(film_id, knn, X_features, df, n=5):
    vecteur = X_features[film_id].reshape(1, -1)
    distances, indices = knn.kneighbors(vecteur, n_neighbors=n+1)
    indices = indices[0][1:]

    resultats = df.iloc[indices][["title", "poster_path", "primaryName", "startYear"]]
    return resultats.to_dict(orient="records")



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

st.sidebar.markdown("""
             <p 
            style="font-size: 18px; 
            font-family: 'Playfair Display', serif;">
        Vous connaissez un film que vous avez aimé ? <br>
                    Nous allons vous recommander des films similaires !
        </p>
             """, unsafe_allow_html=True)



# --- AFFICHAGE DE L'AFFICHE DU FILM DANS LA SIDEBAR---


titre_choisi = st.sidebar.selectbox(
    "Choisissez un titre :",
    df_final["title"].tolist(),
    index=None,
    placeholder="Commencez à taper un titre..."
)

# On ne fait rien tant qu'aucun film n'est sélectionné
if titre_choisi is not None:

    film_filtre = df_final[df_final["title"] == titre_choisi]

    if not film_filtre.empty and film_filtre["poster_path"].notna().iloc[0]:

        base_url = "https://image.tmdb.org/t/p/w500"
        poster_path = film_filtre["poster_path"].iloc[0]
        poster_url = base_url + poster_path

        st.sidebar.image(poster_url)
        st.caption(f"Réalisateur : {df_final['primaryName']} ({df_final['startYear']})", width=200, text_alignment="center")

    else:
        st.sidebar.image("Image_non_disponible.jpg")



#--- PAGE RECHERCHE FILM---

st.divider()

with st.container():
    st.markdown("""
        <span style="
            font-weight:bold;
            font-family: 'Playfair Display', serif;
            font-size: 22px
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

with st.container():
    st.markdown("""
        <span style="
            font-weight:bold;
            font-family: 'Playfair Display', serif;
            font-size: 22px
        ">
        Sélectionnez la date de sortie du film :
        </span>
        """, unsafe_allow_html=True)


date_range = st.slider(
    "",
    min_value=int(df_final["startYear"].min()),
    max_value=int(df_final["startYear"].max()),
    value=(int(df_final["startYear"].min()), int(df_final["startYear"].max())))

# Initialisation de l'état
if "selected_film" not in st.session_state:
    st.session_state.selected_film = None


# Filtrer les films par année (et éventuellement genres)
df_filtre = df_final[
    (df_final["startYear"] >= date_range[0]) &
    (df_final["startYear"] <= date_range[1])
]


# Ajouter ici le filtrage par genre si besoin
# Liste des genres cochés
genres_choisis = []
if Action:
    genres_choisis.append("Action")
if Aventure:
    genres_choisis.append("Aventure")
if Animation:
    genres_choisis.append("Animation")
if Comédie:
    genres_choisis.append("Comédie")
if Crime:
    genres_choisis.append("Crime")
if Documentaire:
    genres_choisis.append("Documentaire")
if Drame:
    genres_choisis.append("Drame")
if Famille:
    genres_choisis.append("Famille")
if Fantastique:
    genres_choisis.append("Fantastique")
if Histoire:
    genres_choisis.append("Histoire")
if Guerre:
    genres_choisis.append("Guerre")
if Musique:
    genres_choisis.append("Musique")
if Romance:
    genres_choisis.append("Romance")
if Science_Fiction:
    genres_choisis.append("Science-Fiction")
if Thriller:
    genres_choisis.append("Thriller")
if Western:
    genres_choisis.append("Western")

# --- FILTRAGE PAR GENRES ---
# Construire la liste des genres cochés
genres_choisis = []
if Action:
    genres_choisis.append("Action")
if Aventure:
    genres_choisis.append("Aventure")
# … répéter pour tous les genres …

# Appliquer le filtre ET logique
if genres_choisis:
    df_filtre = df_filtre[
        df_filtre.apply(
            lambda x: all(g in [x['genre_1'], x['genre_2'], x['genre_3']] for g in genres_choisis),
            axis=1
        )
    ]


films = df_filtre
films = films.reset_index()  # ajoute une colonne "index" avec l'ID réel du film dans df_final
films_records = films.to_dict(orient="records")

# Page principale : grille de films
if st.session_state.selected_film is None:

    if not films_records:
        st.write("Aucun film trouvé pour cette plage d'années.")
    else:
        n_cols = 5
        for i in range(0, len(films_records), n_cols):
            cols = st.columns(n_cols)
            for j, film in enumerate(films_records[i:i+n_cols]):
                with cols[j]:

                    # bouton cliquable stocke TOUT le film dans session_state
                    if st.button(film["title"], key=f"btn_{i+j}", width=200):
                        st.session_state.selected_film = film

                    poster_path = film.get("poster_path")
                    if poster_path:
                        st.image("https://image.tmdb.org/t/p/w500" + poster_path, width=200)
                    else:
                        st.image("Image_non_disponible.jpg", width=200)

                    st.caption(f"Réalisateur : {film['primaryName']} ({film['startYear']})", width=200, text_alignment="center")

# Page détaillée du film
else:
    film = st.session_state.selected_film
    st.header(film["title"])
    poster_path = film.get("poster_path")
    if poster_path:
        st.image("https://image.tmdb.org/t/p/w500" + poster_path, width=300)
    else:
        st.image("Image_non_disponible.jpg", width=300)

    
    # Ici tu peux mettre toutes les infos personnalisées
    st.write("Résumé, acteurs, notes, etc...")

    if st.button("Retour aux films"):
        st.session_state.selected_film = None