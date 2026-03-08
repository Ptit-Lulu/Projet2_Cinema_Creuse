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



df_final = pd.read_csv("df_final_art_acteur_traduit.csv")

# --- LIRE ET ENCODER L'IMAGE DE FOND ---
with open("Fond_ecran_app_cinema.png", "rb") as f:
    img_bytes = f.read()
encoded = base64.b64encode(img_bytes).decode()

# --- APPLIQUER L'IMAGE DE FOND AVEC UN FILTRE BLANC SEMI-TRANSPARENT ---
st.markdown(f"""
<style>

[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.8)),
        url("data:image/png;base64,{encoded}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}

</style>
""", unsafe_allow_html=True)



st.set_page_config(
    page_title="EDEN - Recommandation de films",
    layout="wide",
    initial_sidebar_state="expanded",

)




#__________________________________________________________________________________________________

#**********************************************
#--- SIDEBAR---
#**********************************************
st.markdown("""
<style>
[data-testid="stSidebar"] * {
    font-family: 'Playfair Display', serif;   /* Police */
    font-size: 20px;                           /* Taille du texte */
}
</style>
""", unsafe_allow_html=True)


st.title("Section Grand Public")


st.markdown("""
             <p 
            style="font-size: 25px;
            font-family: 'Playfair Display', serif;"
            line-height: 1.5;
            margin-top: 10px;>
        Dites nous ce que vos clients aiment et nous vous recommanderons des films à programmer !<br>
        </p>
             """, unsafe_allow_html=True)

st.sidebar.markdown("# Films Grand Public 🎬")

st.sidebar.markdown("""
             <p 
            style="font-size: 18px; 
            font-family: 'Playfair Display', serif;">
        Entrez le titre du film que vous souhaitez.<br>
Notre algorithme vous sélectionnera des films similaires !
        </p>
             """, unsafe_allow_html=True)

st.sidebar.write("---")

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

# Récupérer la valeur poster_path
    poster_path = film_filtre["poster_path"].iloc[0]

    # Vérifier si l'image est valide
    if not film_filtre.empty and poster_path and poster_path not in ["", "None", 0]:
        st.sidebar.image(poster_path, width=300)
        st.sidebar.caption(f"Réalisateur : {film_filtre['primaryName'].iloc[0]} ({film_filtre['startYear'].iloc[0]})", text_alignment="center")
        if st.sidebar.button("Voir les recommandations pour ce film", key="btn_reco", width=300):
            film_dict = film_filtre.reset_index().iloc[0].to_dict()
            st.session_state.selected_film = film_dict

#__________________________________________________________________________________________________

#**********************************************
#--- PAGE PRINCIPAL RECHERCHE FILM---
#**********************************************

# --- MISE EN PAGES DES FILTRES --- 

#---------Bloc réalisateur ---------#
st.divider()

with st.container():
    st.markdown("""
        <span style="
            font-weight:bold;
            font-family: 'Playfair Display', serif;
            font-size: 22px
        ">
        Sélectionnez un réalisateur que vous aimez :
        </span>
        """, unsafe_allow_html=True)
# Filtre par réalisateur
realisateurs = df_final['primaryName'].dropna().unique()
realisateur_choisi = st.selectbox(
    " ",
      ["Tous"] + list(realisateurs)
)


st.divider()

#---------Bloc Acteur principal ---------#

with st.container():
        st.markdown("""
        <span style="
            font-weight:bold;
            font-family: 'Playfair Display', serif;
            font-size: 22px
        ">
        Sélectionnez l'acteur principal :
        </span>
        """, unsafe_allow_html=True)

# Filtre par réalisateur
acteur = df_final['acteur_principal_'].dropna().unique()
acteur_choisi = st.selectbox(
    " ",
      ["Tous"] + list(acteur)
)

st.divider()

#---------Bloc Genre ---------#
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

# Filtre par genre
col1, col2, col3, col4 = st.columns(4,vertical_alignment="center")

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

#---------Bloc année de sortie ---------#

# Filtre par année de sortie
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
    value=(int(1980), int(1990)))

#__________________________________________________________________________________________________

#**********************************************
#--- PAGE PRINCIPAL RECHERCHE FILM---
#**********************************************

# Initialisation de l'état
if "selected_film" not in st.session_state:
    st.session_state.selected_film = None


# Filtrer les films par année de sortie
df_filtre = df_final[
    (df_final["startYear"] >= date_range[0]) &
    (df_final["startYear"] <= date_range[1])
]

# Filtre par réalisateur

if realisateur_choisi != "Tous":
    df_filtre = df_filtre[df_filtre["primaryName"] == realisateur_choisi]


# Filtre par acteur principal
if acteur_choisi != "Tous":
    df_filtre = df_filtre[df_filtre["acteur_principal_"] == acteur_choisi]


# Filtre par genres cochés
genres_choisis = []
if Action:
    genres_choisis.append("Action")
if Aventure:
    genres_choisis.append("Adventure")
if Animation:
    genres_choisis.append("Animation")
if Comédie:
    genres_choisis.append("Comedy")
if Crime:
    genres_choisis.append("Crime")
if Documentaire:
    genres_choisis.append("Documentary")
if Drame:
    genres_choisis.append("Drama")
if Famille:
    genres_choisis.append("Family")
if Fantastique:
    genres_choisis.append("Fantasy")
if Histoire:
    genres_choisis.append("History")
if Guerre:
    genres_choisis.append("War")
if Musique:
    genres_choisis.append("Music")
if Romance:
    genres_choisis.append("Romance")
if Science_Fiction:
    genres_choisis.append("Sci-Fi")
if Thriller:
    genres_choisis.append("Thriller")
if Western:
    genres_choisis.append("Western")


# Appliquer le filtre ET logique
if genres_choisis:
    df_filtre = df_filtre[
        df_filtre.apply(
            lambda x: all(g in [x['genre_1'], x['genre_2'], x['genre_3']] for g in genres_choisis),
            axis=1
        )
    ]



# On ajoute l'index réel du DataFrame pour pouvoir retrouver le film dans df_final
films_records = df_filtre.reset_index().to_dict(orient="records")

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
                    
                    # bouton cliquable stocke le dict du film dans session_state
                    if st.button(film["title"], key=f"btn_{i+j}", width=200):
                        st.session_state.selected_film = film  # film est un dict issu de films_records

                    poster_path = film.get("poster_path")
                    if poster_path and poster_path not in ["", "None", 0]:
                        st.image(poster_path, width=200)
                    st.caption(f"Réalisateur : {film['primaryName']} ({film['startYear']})", width=200, text_alignment="center")

# Page détaillée du film
else:
    film = st.session_state.selected_film

    st.header(film["title"])

    col1, col2 = st.columns([1,2])

# -------- Affiche à gauche --------
    with col1:
        poster_path = film.get("poster_path")
        if poster_path:
            st.image(poster_path, width=300)
        else:
            st.image("Image_non_disponible.jpg", width=300)

# -------- Infos film à droite --------
    with col2:

    # Tagline
        tagline = film.get("tagline_fr")
        if tagline and tagline not in ["", "None"]:
            st.markdown(f"### _{tagline}_")

    # Synopsis
        st.markdown("#### Synopsis")
        overview = film.get("overview_fr")
        if overview and overview not in ["", "None"]:
            st.write(overview)
        else:
            st.write("Synopsis non disponible.")

    # Réalisateur | Genres | Date sur la même ligne
        col_r, col_g, col_d = st.columns([1, 2, 1])  # ratios largeur : 1 | 2 | 1

        with col_r:
            st.markdown("#### Réalisateur")
            st.write(film.get("primaryName", "Non renseigné"))

        with col_g:
            st.markdown("#### Genres")
            genres = [film.get(f"genre_{i}", "") for i in range(1,4)]
            genres = [g for g in genres if g not in ["", "None", None, np.nan]]
            st.write(", ".join(genres) if genres else "Non renseigné")

        with col_d:
            st.markdown("#### Date de sortie")
            st.text(film.get("startYear", "Non renseigné"))

    st.subheader("Films recommandés 🎬")

   # film["index"] correspond à l'index original dans df_final grâce au reset_index() plus haut
    film_id = film.get("index", None)
    if film_id is not None:
        recommandations = recommander_films_par_id(
        film_id,
        knn,
        X_features,
        df_final
    )
    else:
        recommandations = []  # sécurité au cas où

    cols = st.columns(5)
    for i, reco in enumerate(recommandations):

    # retrouver l'index du film dans df_final
        film_match = df_final[df_final["title"] == reco["title"]]

        if not film_match.empty:
            reco_dict = film_match.reset_index().iloc[0].to_dict()
        else:
            reco_dict = None

        with cols[i]:

            if reco_dict:
                if st.button(reco["title"], key=f"reco_{i}", width=150):
                    st.session_state.selected_film = reco_dict

            if reco["poster_path"]:
                st.image(reco["poster_path"], width=150)
            else:
                st.image("Image_non_disponible.jpg", width=150)

            st.caption(f"{reco['primaryName']} ({reco['startYear']})")

    if st.button("Retour aux films"):
        st.session_state.selected_film = None