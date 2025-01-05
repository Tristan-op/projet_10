import logging
import os
import pandas as pd
import pickle
from azure.storage.blob import BlobServiceClient
import io  # Ajout de l'importation pour remplacer pandas.compat.StringIO

# Charger la chaîne de connexion depuis les variables d'environnement
BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
if not BLOB_CONNECTION_STRING:
    raise ValueError("La chaîne de connexion BLOB_CONNECTION_STRING est introuvable. Vérifiez votre configuration des secrets ou local.settings.json.")

# Initialisation globale du client Blob
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
container_client = blob_service_client.get_container_client("recommendation-data")

def load_blob_data(blob_name):
    """
    Télécharge un fichier Blob depuis Azure Blob Storage.
    
    :param blob_name: Nom du fichier dans le conteneur Blob.
    :return: Contenu du fichier (en mémoire).
    """
    try:
        blob_client = container_client.get_blob_client(blob_name)
        logging.info(f"Téléchargement du fichier {blob_name} depuis le Blob Storage...")
        data = blob_client.download_blob().readall()
        return data
    except Exception as e:
        logging.error(f"Erreur lors du téléchargement du fichier {blob_name} : {e}")
        return None

def get_embeddings():
    """
    Charge la matrice d'embeddings des articles et leurs IDs.
    
    :return: Tuple (embedding_matrix, article_ids).
    """
    embeddings_data = load_blob_data("articles_embeddings.pickle")
    if embeddings_data is None:
        logging.error("Impossible de charger les embeddings.")
        return None, None

    embedding_matrix = pickle.loads(embeddings_data)

    metadata_data = load_blob_data("articles_metadata.csv")
    if metadata_data is None:
        logging.error("Impossible de charger les métadonnées des articles.")
        return None, None

    articles_metadata = pd.read_csv(io.StringIO(metadata_data.decode('utf-8')))  # Utilisation de io.StringIO
    article_ids = articles_metadata["article_id"].tolist()

    return embedding_matrix, article_ids

def get_trending_articles(top_n=10):
    """
    Identifie les articles les plus populaires (en termes de clics).

    :param top_n: Nombre d'articles les plus populaires à retourner.
    :return: Liste des IDs des articles les plus populaires.
    """
    clicks_sample = get_user_clicks()
    if clicks_sample is None:
        logging.error("Impossible de calculer les tendances globales.")
        return []

    trending_articles = clicks_sample["click_article_id"].value_counts().head(top_n).index.tolist()
    return trending_articles


def get_user_clicks():
    """
    Charge les clics utilisateurs depuis les fichiers horaires concaténés.
    
    :return: DataFrame des clics utilisateur.
    """
    clicks_data = load_blob_data("clicks_sample.csv")
    if clicks_data is None:
        logging.error("Impossible de charger les clics utilisateur.")
        return None

    clicks_sample = pd.read_csv(io.StringIO(clicks_data.decode('utf-8')))  # Utilisation de io.StringIO
    return clicks_sample

def initialize_global_data():
    """
    Fonction d'initialisation globale pour charger les données nécessaires au système.
    
    :return: Booléen indiquant si le chargement a réussi.
    """
    try:
        global embedding_matrix, article_ids, clicks_sample

        embedding_matrix, article_ids = get_embeddings()
        if embedding_matrix is None or article_ids is None:
            raise ValueError("Erreur lors du chargement des embeddings.")

        clicks_sample = get_user_clicks()
        if clicks_sample is None:
            raise ValueError("Erreur lors du chargement des clics utilisateur.")

        logging.info("Toutes les données ont été chargées avec succès.")
        return True
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation globale des données : {e}")
        return False

