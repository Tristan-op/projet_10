import os
from azure.storage.blob import BlobServiceClient

# Charger la chaîne de connexion depuis les variables d'environnement
BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")

# Liste des fichiers nécessaires dans le Blob Storage
required_files = [
    "articles_embeddings.pickle",
    "articles_metadata.csv",
    "clicks_sample.csv"
]

def test_blob_connection():
    """
    Vérifie la connexion au Blob Storage et l'existence des fichiers nécessaires.
    """
    try:
        # Initialiser le client Blob
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client("recommendation-data")

        # Vérifier l'existence des fichiers
        for file_name in required_files:
            blob_client = container_client.get_blob_client(file_name)
            if blob_client.exists():
                print(f"✅ Fichier présent : {file_name}")
            else:
                print(f"❌ Fichier manquant : {file_name}")
                return False

        print("✅ Connexion Blob Storage réussie et tous les fichiers nécessaires sont présents.")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion au Blob Storage : {str(e)}")
        return False


if __name__ == "__main__":
    if not test_blob_connection():
        exit(1)  # Retourne une erreur si le test échoue
