from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def recommend_content_based(user_id, embeddings, article_ids, user_clicks, top_n=5):
    """
    Recommande des articles similaires à ceux lus par l'utilisateur.
    """
    clicked_articles = user_clicks[user_clicks["user_id"] == user_id]["click_article_id"].tolist()
    user_embeddings = [embeddings[article_ids.index(aid)] for aid in clicked_articles if aid in article_ids]
    
    if not user_embeddings:
        return []  # Aucun article lu par l'utilisateur

    user_profile = np.mean(user_embeddings, axis=0).reshape(1, -1)
    similarities = cosine_similarity(user_profile, embeddings)[0]
    recommended_indices = np.argsort(similarities)[::-1]
    recommended_articles = [
        article_ids[i] for i in recommended_indices if article_ids[i] not in clicked_articles
    ][:top_n]

    return recommended_articles

def recommend_collaborative(user_id, user_clicks, top_n=5):
    """
    Recommande des articles en fonction des utilisateurs similaires.
    """
    user_articles = user_clicks[user_clicks["user_id"] == user_id]["click_article_id"].tolist()
    if not user_articles:
        return []  # Aucun article lu par l'utilisateur

    similar_users = user_clicks[user_clicks["click_article_id"].isin(user_articles)]["user_id"].unique()
    similar_users = [u for u in similar_users if u != user_id]
    recommended_articles = (
        user_clicks[user_clicks["user_id"].isin(similar_users)]
        .groupby("click_article_id")
        .size()
        .sort_values(ascending=False)
        .head(top_n)
        .index
        .tolist()
    )
    recommended_articles = [aid for aid in recommended_articles if aid not in user_articles]
    
    return recommended_articles

def generate_recommendations(user_id, embeddings, article_ids, user_clicks, top_n=5):
    """
    Combine le filtrage par contenu et collaboratif pour générer des recommandations.
    """
    content_recommendations = recommend_content_based(
        user_id, embeddings, article_ids, user_clicks, top_n=10
    )
    collaborative_recommendations = recommend_collaborative(
        user_id, user_clicks, top_n=10
    )
    combined_recommendations = content_recommendations[:int(0.8 * top_n)] + \
                               collaborative_recommendations[:int(0.2 * top_n)]
    combined_recommendations = list(dict.fromkeys(combined_recommendations))[:top_n]
    
    return combined_recommendations
