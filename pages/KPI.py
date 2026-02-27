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
with open("Fond_ecran_app_cinema.png", "rb") as f:
    img_bytes = f.read()
encoded = base64.b64encode(img_bytes).decode()

st.markdown(f"""
<style>
.stApp::before {{
    content:"";
    position: fixed;
    inset: 0;
    background: url("data:image/png;base64,{encoded}") no-repeat center center;
    background-size: cover;
    opacity: 0.4;       /* ajuste la transparence de l'image */
    pointer-events: none;
    z-index: 0;
}}

.stApp > div {{
    position: relative;
    z-index: 1;
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

st.markdown("# Indicateurs clés 📊")
st.sidebar.markdown("# Indicateurs clés 📊")