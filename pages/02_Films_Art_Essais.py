# Bibliothèque à importer

import base64
import streamlit as st
import pandas as pd
import joblib
import numpy as np
from sklearn.neighbors import NearestNeighbors

# -------------------------
# Charger le DataFrame et modèles
# -------------------------
@st.cache_resource
def load_all():
    knn = joblib.load("knn_model.joblib")          # modèle NearestNeighbors spécifique
    pipeline = joblib.load("pipeline.joblib")      # pipeline spécifique
    X_features = joblib.load("X_features.joblib")  # matrice features spécifique
    return knn, pipeline, X_features

knn, pipeline, X_features = load_all()

df_final = pd.read_csv("df_final_art_acteur_traduit.csv")
df_art_essai = df_final[df_final["Art_Essai"] == "Yes"].copy()
# -------------------------
# Fonction recommandation
# -------------------------
def recommander_films_par_id(film_id, knn, X_features, df, n=5):

    vecteur = X_features[film_id].reshape(1, -1)
    distances, indices = knn.kneighbors(vecteur, n_neighbors=50)

    indices = indices[0][1:]

    # garder seulement les Art & Essai
    indices = [i for i in indices if df.iloc[i]["Art_Essai"] == "Yes"]

    indices = indices[:n]

    resultats = df.iloc[indices][["title","poster_path","primaryName","startYear"]]

    return resultats.to_dict(orient="records")

# -------------------------
# Image de fond
# -------------------------
with open("Fond_ecran_art_essai.png", "rb") as f:
    img_bytes = f.read()
encoded = base64.b64encode(img_bytes).decode()

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

[data-testid="stSidebar"] * {{
    font-family: 'Playfair Display', serif;
    font-size: 20px;
}}

/* boutons streamlit */
div.stButton > button {{
    background: linear-gradient(45deg,#C9A227,#FFD700);
    color: black;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}}

/* effet hover */
div.stButton > button:hover {{
    background-color: #c39e2f;
    color: black;
}}

/* SELECTBOX (réalisateur, acteur) */
div[data-baseweb="select"] > div {{
    background: linear-gradient(45deg,#C9A227,#FFD700);
    border-radius: 8px;
    color: black;
    font-weight: bold;
}}

/* texte dans le select */
div[data-baseweb="select"] span {{
    color: black;
}}

/* CHECKBOX (genres) - style label reste normal, case seule en doré */
.stCheckbox > label {{
    background: transparent;   /* plus de dégradé sur tout le label */
    padding: 0;                /* plus de padding autour de la case */
    color: black;              /* texte normal */
    font-weight: 500;
    border-radius: 0;
}}

/* carré de la checkbox */
.stCheckbox input[type="checkbox"] {{
    accent-color: #FFD700;    /* case dorée */
    width: 20px;               /* taille case si besoin */
    height: 20px;
}}

</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Art & Essai", layout="wide", initial_sidebar_state="auto")

# -------------------------
# Sidebar
# -------------------------
st.sidebar.markdown("# Films Art & Essai 🎬")
st.sidebar.markdown("""
                     <p 
            style="font-size: 18px; 
            font-family: 'Playfair Display', serif;">
Entrez le titre du film Art & Essai que vous souhaitez.<br>
Notre algorithme vous recommandera des films labellisés similaires !
""", unsafe_allow_html=True)

titre_choisi = st.sidebar.selectbox("Choisissez un titre :", df_art_essai["title"].tolist(), index=None, placeholder="Commencez à taper un titre...")

if titre_choisi:
    film_filtre = df_art_essai[df_art_essai["title"] == titre_choisi]
    poster_path = film_filtre["poster_path"].iloc[0]
    if poster_path and poster_path not in ["", "None", 0]:
        st.sidebar.image(poster_path, width=300)
        st.sidebar.caption(f"Réalisateur : {film_filtre['primaryName'].iloc[0]} ({film_filtre['startYear'].iloc[0]})")
        if st.sidebar.button("Voir recommandations", key="btn_reco_art"):
            st.session_state.selected_film = film_filtre.reset_index().iloc[0].to_dict()

# -------------------------
# Filtres sur la page principale
# -------------------------
st.title("Section Art & Essai")

st.markdown("""
             <p 
            style="font-size: 25px;
            font-family: 'Playfair Display', serif;">
        Recherche par caractéristiques<br>
        </p>
             """, unsafe_allow_html=True)

#---------Bloc réalisateur ---------#
st.divider()

with st.container():
    st.markdown("""
        <span style="
            font-weight:bold;
            font-family: 'Playfair Display', serif;
            font-size: 22px
        ">
        Sélectionnez le réalisateur que vous aimez :
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
        Sélectionnez l'acteur principal que vous aimez :
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


# Mapping français -> anglais
genres_choisis = []
if Action: genres_choisis.append("Action")
if Aventure: genres_choisis.append("Adventure")
if Animation: genres_choisis.append("Animation")
if Comédie: genres_choisis.append("Comedy")
if Crime: genres_choisis.append("Crime")
if Documentaire: genres_choisis.append("Documentary")
if Drame: genres_choisis.append("Drama")
if Famille: genres_choisis.append("Family")
if Fantastique: genres_choisis.append("Fantasy")
if Histoire: genres_choisis.append("History")
if Guerre: genres_choisis.append("War")
if Musique: genres_choisis.append("Music")
if Romance: genres_choisis.append("Romance")
if Science_Fiction: genres_choisis.append("Sci-Fi")
if Thriller: genres_choisis.append("Thriller")
if Western: genres_choisis.append("Western")



# -------------------------
# Filtrage
# -------------------------
if "selected_film" not in st.session_state:
    st.session_state.selected_film = None

df_filtre = df_art_essai[
    (df_art_essai["startYear"] >= date_range[0]) & (df_art_essai["startYear"] <= date_range[1])
]

if realisateur_choisi != "Tous":
    df_filtre = df_filtre[df_filtre["primaryName"] == realisateur_choisi]
if acteur_choisi != "Tous":
    df_filtre = df_filtre[df_filtre["acteur_principal_"] == acteur_choisi]
if genres_choisis:
    df_filtre = df_filtre[df_filtre.apply(lambda x: all(g in [x['genre_1'], x['genre_2'], x['genre_3']] for g in genres_choisis), axis=1)]

films_records = df_filtre.reset_index().to_dict(orient="records")

# -------------------------
# Affichage films / page détaillée
# -------------------------
if st.session_state.selected_film is None:
    if not films_records:
        st.write("Aucun film trouvé pour ces filtres.")
    else:
        n_cols = 5
        for i in range(0, len(films_records), n_cols):
            cols = st.columns(n_cols)
            for j, film in enumerate(films_records[i:i+n_cols]):
                with cols[j]:
                    if st.button(film["title"], key=f"btn_art_{i+j}", width=200):
                        st.session_state.selected_film = film
                    poster_path = film.get("poster_path")
                    if poster_path and poster_path not in ["", "None", 0]:
                        st.image(poster_path, width=200)
                    st.caption(f"{film['primaryName']} ({film['startYear']})")
else:
    film = st.session_state.selected_film
    st.header(film["title"])
    col1, col2 = st.columns([1,2])
    with col1:
        poster_path = film.get("poster_path")
        if poster_path: st.image(poster_path, width=300)
        else: st.image("Image_non_disponible.jpg", width=300)
    with col2:
        tagline = film.get("tagline_fr")
        if tagline and tagline not in ["", "None"]:
            st.markdown(f"### _{tagline}_")
        overview = film.get("overview_fr")
        st.markdown("#### Synopsis")
        if overview and overview not in ["", "None"]:
            st.write(overview)
        else:
            st.write("Synopsis non disponible.")
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
    film_id = film.get("index", None)
    if film_id is not None:
        recommandations = recommander_films_par_id(film_id, knn, X_features, df_final)
    else:
        recommandations = []

    cols = st.columns(5)
    for i, reco in enumerate(recommandations):
        film_match = df_art_essai[df_art_essai["title"] == reco["title"]]
        if not film_match.empty:
            reco_dict = film_match.reset_index().iloc[0].to_dict()
        else:
            reco_dict = None
        with cols[i]:
            if reco_dict and st.button(reco["title"], key=f"reco_art_{i}", width=150):
                st.session_state.selected_film = reco_dict
            poster_path = reco["poster_path"]
            if poster_path:
                st.image(poster_path, width=150)
            else:
                st.image("Image_non_disponible.jpg", width=150)
            st.caption(f"{reco['primaryName']} ({reco['startYear']})")

    if st.button("Retour aux films"):
        st.session_state.selected_film = None

