import streamlit as st
from azure.storage.blob import BlobServiceClient
from utils.load_data import get_embeddings, get_user_clicks
from utils.recommend_logic import (
    generate_recommendations,
    recommend_collaborative,
    recommend_content_based
)
from utils.user_data import mark_article_as_read
import os

# Configuration de connexion au Blob Storage
BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
if not BLOB_CONNECTION_STRING:
    raise ValueError("La chaîne de connexion BLOB_CONNECTION_STRING est introuvable.")
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)

# Chargement des données globales
embedding_matrix, article_ids = get_embeddings()
clicks_sample = get_user_clicks()

# Configuration des pages
st.set_page_config(
    page_title="CLARA",
    page_icon="📚",
    layout="wide"
)

# Sidebar Navigation
pages = ["Home", "Data", "Recommendations", "Logs"]
page = st.sidebar.selectbox("Navigation", pages)

if page == "Home":
    st.title("Bienvenue sur CLARA")
    st.write("\nCLARA est votre assistante pour la recommandation d'articles personnalisés. Explorez les données, obtenez des recommandations et surveillez les performances de l'application.")

elif page == "Data":
    st.title("Données")
    if embedding_matrix is not None and clicks_sample is not None:
        st.write(f"**Nombre d'articles :** {len(article_ids)}")
        st.write(f"**Nombre d'utilisateurs :** {clicks_sample['user_id'].nunique()}")
    else:
        st.error("Les données ne sont pas disponibles. Vérifiez les connexions.")

elif page == "Recommendations":
    st.title("Recommandations d'articles")
    try:
        # Sélection de l'utilisateur
        user_ids = clicks_sample["user_id"].unique()
        selected_user = st.selectbox("Sélectionnez un ID utilisateur", user_ids)

        if st.button("Obtenir des recommandations"):
            # Content-Based Recommendations
            content_recs = recommend_content_based(
                user_id=selected_user,
                embeddings=embedding_matrix,
                article_ids=article_ids,
                user_clicks=clicks_sample,
                top_n=5
            )
            st.write("### Articles proposés d'après vos choix :")
            for article in content_recs:
                st.write(f"- Article ID : {article}")

            # Collaborative Recommendations
            collaborative_recs = recommend_collaborative(
                user_id=selected_user,
                user_clicks=clicks_sample,
                top_n=5
            )
            st.write("### Articles à la mode :")
            for article in collaborative_recs:
                st.write(f"- Article ID : {article}")

            # Combined Recommendations
            combined_recs = generate_recommendations(
                user_id=selected_user,
                embeddings=embedding_matrix,
                article_ids=article_ids,
                user_clicks=clicks_sample,
                top_n=5
            )
            st.write("### Recommandations combinées :")
            for article in combined_recs:
                st.write(f"- Article ID : {article}")
                if st.button(f"Lire l'article {article}", key=f"read_{article}"):
                    mark_article_as_read(user_id=selected_user, article_id=article)
                    st.success(f"Article {article} marqué comme lu.")
    except Exception as e:
        st.error(f"Erreur lors de la génération des recommandations : {str(e)}")

elif page == "Logs":
    st.title("Logs et Tests")

    # Liste des fichiers nécessaires
    required_files = [
        "articles_embeddings.pickle",
        "articles_metadata.csv",
        "clicks_sample.csv"
    ]

    # Vérifier l'accès aux fichiers
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
    def check_function_access():
        results = {}
        try:
            if embedding_matrix is not None and article_ids is not None:
                results["Chargement des embeddings"] = "✅"
            else:
                results["Chargement des embeddings"] = "❌"
        except Exception as e:
            results["Chargement des embeddings"] = f"❌ (Erreur : {str(e)})"

        try:
            if clicks_sample is not None:
                results["Chargement des clics utilisateurs"] = "✅"
            else:
                results["Chargement des clics utilisateurs"] = "❌"
        except Exception as e:
            results["Chargement des clics utilisateurs"] = f"❌ (Erreur : {str(e)})"

        return results

    st.subheader("Statut des Fichiers")
    file_results = {file_name: check_file_access(file_name) for file_name in required_files}
    for file_name, status in file_results.items():
        st.write(f"**{file_name}** : {status}")

    st.subheader("Statut des Fonctions")
    function_results = check_function_access()
    for function_name, status in function_results.items():
        st.write(f"**{function_name}** : {status}")
