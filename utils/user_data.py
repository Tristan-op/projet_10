import json
import os

USER_DATA_PATH = "user_data.json"

def get_articles_read(user_id):
    """
    Retourne la liste des articles lus par un utilisateur.
    """
    if not os.path.exists(USER_DATA_PATH):
        return []

    with open(USER_DATA_PATH, "r") as f:
        data = json.load(f)
    return data.get(str(user_id), [])

def mark_article_as_read(user_id, article_id):
    """
    Ajoute un article à la liste des articles lus d'un utilisateur.
    """
    if not os.path.exists(USER_DATA_PATH):
        data = {}
    else:
        with open(USER_DATA_PATH, "r") as f:
            data = json.load(f)

    user_articles = data.get(str(user_id), [])
    if article_id not in user_articles:
        user_articles.append(article_id)
    data[str(user_id)] = user_articles

    with open(USER_DATA_PATH, "w") as f:
        json.dump(data, f)

    return True
