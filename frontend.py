import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

# Titre de l'application
st.write('''
         # App pour le reporting des outputs des modèles data
         Cette application permet de faire des reportings graphiques sur les données immobilières.
         ''')

# Récupération des données depuis l'API
try:
    req = requests.get("http://127.0.0.1:5000/index")
    req.raise_for_status()  # Lève une exception si la requête a échoué (statut HTTP != 200)
    
    # Vérifie si la réponse contient du JSON valide
    if req.headers['Content-Type'] == 'application/json':
        resultat = req.json()
    else:
        st.error("La réponse de l'API n'est pas au format JSON.")
        st.stop()
except requests.exceptions.RequestException as e:
    st.error(f"Erreur lors de la récupération des données depuis l'API : {e}")
    st.stop()

# Création du DataFrame
try:
    data = pd.DataFrame(resultat, columns=["id", "type_bien", "type_transaction", "week", "month", "year", "predicted_price"])
    data["predicted_price"] = data["predicted_price"].astype(float)
    data["week"] = data["week"].astype(int)
    data["month"] = data["month"].astype(int)
    data["year"] = data["year"].astype(int)
except Exception as e:
    st.error(f"Erreur lors de la création du DataFrame : {e}")
    st.stop()

# Configuration de la page Streamlit
st.title("Reporting des Prix Prédits Immobiliers")

# Option pour sélectionner le type de visualisation
visualization_type = st.sidebar.selectbox("Choisissez le type de visualisation", ("Histogramme", "Courbe", "Camembert"))

# Sélection du filtre : Semaine, Mois ou Type de bien
filter_by = st.sidebar.radio("Filtrer par", ("Semaine", "Mois", "Type de bien"))

# Sous-filtres pour la sélection de plages de semaines ou de mois
if filter_by == "Semaine":
    min_week, max_week = st.sidebar.select_slider(
        "Sélectionnez la plage de semaines",
        options=sorted(data["week"].unique()),
        value=(min(data["week"]), max(data["week"]))
    )
    filtered_df = data[(data["week"] >= min_week) & (data["week"] <= max_week)]
    numeric_df = filtered_df.select_dtypes(include=['number'])
    group_data = numeric_df.groupby("week").mean().reset_index()
elif filter_by == "Mois":
    min_month, max_month = st.sidebar.select_slider(
        "Sélectionnez la plage de mois",
        options=sorted(data["month"].unique()),
        value=(min(data["month"]), max(data["month"]))
    )
    filtered_df = data[(data["month"] >= min_month) & (data["month"] <= max_month)]
    numeric_df = filtered_df.select_dtypes(include=['number'])
    group_data = numeric_df.groupby("month").mean().reset_index()
else:
    # Grouper par type de bien et calculer la moyenne uniquement sur les colonnes numériques
    numeric_df = data.select_dtypes(include=['number'])
    group_data = numeric_df.groupby(data["type_bien"]).mean().reset_index()

# Visualisation des données
if visualization_type == "Histogramme":
    st.header(f"Histogramme des prix prédits par {filter_by.lower()}")
    fig, ax = plt.subplots()
    
    # Utiliser le bon nom de colonne pour l'axe des x
    x_column = "week" if filter_by == "Semaine" else "month" if filter_by == "Mois" else "type_bien"
    
    sns.barplot(x=x_column, y='predicted_price', data=group_data, ax=ax, label='Prix Prédit')
    ax.set_ylabel('Prix Prédit Moyen')
    st.pyplot(fig)

elif visualization_type == "Courbe":
    st.header(f"Courbe des prix prédits par {filter_by.lower()}")
    fig, ax = plt.subplots()
    
    # Utiliser le bon nom de colonne pour l'axe des x
    x_column = "week" if filter_by == "Semaine" else "month" if filter_by == "Mois" else "type_bien"
    
    sns.lineplot(x=x_column, y='predicted_price', data=group_data, ax=ax, label='Prix Prédit')
    ax.set_ylabel('Prix Prédit Moyen')
    st.pyplot(fig)

elif visualization_type == "Camembert":
    st.header("Répartition des prix prédits par type de bien")
    fig, ax = plt.subplots()
    
    # Sélectionner uniquement les colonnes numériques
    numeric_df = data.select_dtypes(include=['number'])
    
    # Grouper par type de bien et calculer la moyenne uniquement sur les colonnes numériques
    group_data = numeric_df.groupby(data["type_bien"]).mean().reset_index()
    
    # Afficher le camembert
    group_data.set_index('type_bien')['predicted_price'].plot.pie(autopct='%1.1f%%', ax=ax, label='Prix Prédit Moyen')
    st.pyplot(fig)

# Afficher le tableau de données
st.header("Tableau des données")
st.dataframe(data)

# Filtres supplémentaires
st.sidebar.header("Filtres supplémentaires")
selected_type_bien = st.sidebar.multiselect(
    "Sélectionnez le type de bien",
    options=data["type_bien"].unique(),
    default=data["type_bien"].unique()
)
selected_type_transaction = st.sidebar.multiselect(
    "Sélectionnez le type de transaction",
    options=data["type_transaction"].unique(),
    default=data["type_transaction"].unique()
)

# Appliquer les filtres supplémentaires
filtered_df = data[
    (data["type_bien"].isin(selected_type_bien)) &
    (data["type_transaction"].isin(selected_type_transaction))
]

# Afficher les données filtrées
st.header("Données filtrées")
st.dataframe(filtered_df)

# Autres options de reporting
st.header("Autres Analyses")
st.write("Sélectionnez différentes options dans la barre latérale pour explorer les données sous divers angles.")