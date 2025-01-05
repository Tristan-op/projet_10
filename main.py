from flask import Flask, render_template, request, jsonify, redirect, url_for
from utils.load_data import get_embeddings, get_user_clicks
from utils.recommend_logic import (
    generate_recommendations,
    recommend_collaborative,
    recommend_content_based
)
from utils.user_data import mark_article_as_read
import os

app = Flask(__name__)

# Configuration de connexion au Blob Storage
BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
if not BLOB_CONNECTION_STRING:
    raise ValueError("La chaîne de connexion BLOB_CONNECTION_STRING est introuvable.")

# Chargement des données globales
embedding_matrix, article_ids = get_embeddings()
clicks_sample = get_user_clicks()

# Routes pour les pages
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/data')
def data():
    if embedding_matrix is not None and clicks_sample is not None:
        num_articles = len(article_ids)
        num_users = clicks_sample['user_id'].nunique()
        return render_template('data.html', num_articles=num_articles, num_users=num_users)
    else:
        return render_template('error.html', message="Les données ne sont pas disponibles. Vérifiez les connexions.")

@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    user_ids = clicks_sample["user_id"].unique()
    selected_user = None
    content_recs, collaborative_recs, combined_recs = [], [], []

    if request.method == 'POST':
        selected_user = int(request.form.get('user_id'))
        # Content-Based Recommendations
        content_recs = recommend_content_based(
            user_id=selected_user,
            embeddings=embedding_matrix,
            article_ids=article_ids,
            user_clicks=clicks_sample,
            top_n=5
        )
        # Collaborative Recommendations
        collaborative_recs = recommend_collaborative(
            user_id=selected_user,
            user_clicks=clicks_sample,
            top_n=5
        )
        # Combined Recommendations
        combined_recs = generate_recommendations(
            user_id=selected_user,
            embeddings=embedding_matrix,
            article_ids=article_ids,
            user_clicks=clicks_sample,
            top_n=5
        )

    return render_template(
        'recommendations.html',
        user_ids=user_ids,
        selected_user=selected_user,
        content_recs=content_recs,
        collaborative_recs=collaborative_recs,
        combined_recs=combined_recs
    )

@app.route('/logs')
def logs():
    required_files = [
        "articles_embeddings.pickle",
        "articles_metadata.csv",
        "clicks_sample.csv"
    ]

    file_status = {}
    for file_name in required_files:
        file_status[file_name] = "✅" if file_exists(file_name) else "❌"

    function_status = {
        "Chargement des embeddings": "✅" if embedding_matrix is not None and article_ids is not None else "❌",
        "Chargement des clics utilisateurs": "✅" if clicks_sample is not None else "❌",
    }

    return render_template('logs.html', file_status=file_status, function_status=function_status)

# Vérifie si un fichier existe dans Azure Blob Storage
def file_exists(file_name):
    try:
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client("recommendation-data")
        blob_client = container_client.get_blob_client(file_name)
        return blob_client.exists()
    except Exception:
        return False

# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True)
