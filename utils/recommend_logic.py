import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils.load_data import get_embeddings, get_user_clicks, get_trending_articles
from utils.user_data import get_articles_read

def generate_recommendations(user_id, total_n=5, personalized_n=4):
    """
    Génère une liste d'articles recommandés pour un utilisateur.
    """
    embedding_matrix, article_ids = get_embeddings()
    if embedding_matrix is None or article_ids is None:
        return []

    articles_read = get_articles_read(user_id)
    user_clicks = get_user_clicks()
    if user_clicks is None or user_id not in user_clicks["user_id"].values:
        return []

    clicked_articles = user_clicks[user_clicks["user_id"] == user_id]["click_article_id"].tolist()
    clicked_embeddings = [embedding_matrix[article_ids.index(a)] for a in clicked_articles if a in article_ids]
    if not clicked_embeddings:
        return []

    user_profile = np.mean(clicked_embeddings, axis=0).reshape(1, -1)
    similarities = cosine_similarity(user_profile, embedding_matrix)[0]

    recommendations = [
        article_ids[i] for i in similarities.argsort()[::-1] if article_ids[i] not in articles_read
    ][:personalized_n]

    trending_articles = get_trending_articles()
    trending_article = next((a for a in trending_articles if a not in articles_read), None)

    return recommendations + ([trending_article] if trending_article else [])
