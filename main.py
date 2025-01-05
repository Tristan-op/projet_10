import streamlit as st
from azure.storage.blob import BlobServiceClient
from utils.load_data import load_blob_data, get_embeddings, get_user_clicks
from utils.recommend_logic import generate_recommendations
from utils.user_data import mark_article_as_read

# Configuration de connexion au Blob Storage
BLOB_CONNECTION_STRING = st.secrets["BLOB_CONNECTION_STRING"]
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)

# Titre de l'application
st.title("Vérification des Fichiers et Fonctions dans Azure Blob")

# Liste des fichiers nécessaires
required_files = [
    "articles_embeddings.pickle",
    "articles_metadata.csv",
    "clicks_sample.csv"
]

# Vérifier l'accès aux fichiers
@st.cache_data
def check_file_access(file_name):
    try:
        container_client = blob_service_client.get_container_client("recommendation-data")
        blob_client = container_client.get_blob_client(file_name)
        if blob_client.exists():
            return "✅"
        else:
            return "❌"
    except Exception as e:
        return f"❌ (Erreur : {str(e)})"

# Vérifier l'accès aux fonctions
@st.cache_data
def check_function_access():
    results = {}
    try:
        # Test de chargement des embeddings
        embedding_matrix, article_ids = get_embeddings()
        if embedding_matrix is not None and article_ids is not None:
            results["Chargement des embeddings"] = "✅"
        else:
            results["Chargement des embeddings"] = "❌"
    except Exception as e:
        results["Chargement des embeddings"] = f"❌ (Erreur : {str(e)})"

    try:
        # Test de chargement des clics utilisateurs
        clicks = get_user_clicks()
        if clicks is not None:
            results["Chargement des clics utilisateurs"] = "✅"
        else:
            results["Chargement des clics utilisateurs"] = "❌"
    except Exception as e:
        results["Chargement des clics utilisateurs"] = f"❌ (Erreur : {str(e)})"

    try:
        # Test de génération de recommandations
        recommendations = generate_recommendations(user_id=1)
        if recommendations:
            results["Génération de recommandations"] = "✅"
        else:
            results["Génération de recommandations"] = "❌ (Aucune recommandation générée)"
    except Exception as e:
        results["Génération de recommandations"] = f"❌ (Erreur : {str(e)})"

    try:
        # Test de marquage d'un article comme lu
        success = mark_article_as_read(user_id=1, article_id=12345)
        if success:
            results["Marquage d'un article comme lu"] = "✅"
        else:
            results["Marquage d'un article comme lu"] = "❌"
    except Exception as e:
        results["Marquage d'un article comme lu"] = f"❌ (Erreur : {str(e)})"

    return results

# Affichage des résultats
st.subheader("Statut des Fichiers")
file_results = {file_name: check_file_access(file_name) for file_name in required_files}

for file_name, status in file_results.items():
    st.write(f"**{file_name}** : {status}")

st.subheader("Statut des Fonctions")
function_results = check_function_access()

for function_name, status in function_results.items():
    st.write(f"**{function_name}** : {status}")
