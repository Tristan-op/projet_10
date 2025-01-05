import logging
import azure.functions as func
from utils.recommend_logic import generate_recommendations
from utils.user_data import mark_article_as_read
from utils.load_data import initialize_global_data

# Initialisation globale des ressources
logging.info("Initialisation des ressources globales...")
data_loaded = initialize_global_data()
if not data_loaded:
    logging.error("Échec du chargement des données initiales.")
else:
    logging.info("Données initiales chargées avec succès.")

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function principale pour gérer les recommandations d'articles.
    Deux endpoints gérés :
    1. /recommendations : Retourne des recommandations personnalisées.
    2. /select_article : Marque un article comme "lu" pour un utilisateur.
    """
    try:
        # Identifier l'endpoint demandé
        route = req.route_params.get("route")

        # Endpoint : Recommandations
        if route == "recommendations":
            user_id = req.params.get("user_id")
            if not user_id:
                return func.HttpResponse("Missing user_id parameter.", status_code=400)

            # Générer des recommandations personnalisées
            recommendations = generate_recommendations(int(user_id))
            if not recommendations:
                return func.HttpResponse(
                    "No recommendations available for the user.",
                    status_code=404
                )

            return func.HttpResponse(
                func.Json.dumps({
                    "user_id": user_id,
                    "recommendations": recommendations
                }),
                mimetype="application/json",
                status_code=200
            )

        # Endpoint : Sélection d'un article
        elif route == "select_article":
            user_id = req.params.get("user_id")
            article_id = req.params.get("article_id")
            if not user_id or not article_id:
                return func.HttpResponse("Missing user_id or article_id parameter.", status_code=400)

            # Marquer l'article comme "lu"
            success = mark_article_as_read(int(user_id), int(article_id))
            if success:
                return func.HttpResponse(f"Article {article_id} marked as read for user {user_id}.", status_code=200)
            else:
                return func.HttpResponse("Failed to mark article as read.", status_code=500)

        # Route non reconnue
        else:
            return func.HttpResponse("Invalid endpoint.", status_code=404)

    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        return func.HttpResponse(f"Invalid input: {ve}", status_code=400)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)

