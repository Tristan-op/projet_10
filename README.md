# Projet de Recommandation d'Articles

Ce projet utilise des Azure Functions pour générer des recommandations d'articles personnalisées en fonction des interactions utilisateur. 

## Architecture du Projet

### Répertoires Principaux

#### `.github/workflows/`
- Contient les fichiers pour l'intégration et le déploiement continus (CI/CD).
- Exemple : `main_clara.yml` pour automatiser les workflows GitHub Actions.

#### `RecommendArticles/`
- Héberge les fichiers principaux pour l'Azure Function.
  - **`__init__.py`** : Point d'entrée de l'Azure Function.
  - **`function.json`** : Configuration de l'Azure Function (routes, bindings, etc.).

#### `static/`
- Contient les fichiers statiques tels que les styles CSS.
  - **`style.css`** : Fichier de mise en forme des pages HTML.

#### `templates/`
- Répertoire dédié aux templates HTML pour le rendu côté serveur.
  - **`home.html`** : Page d'accueil.
  - **`data.html`** : Affichage des données.
  - **`logs.html`** : Journal des logs.
  - **`recommendations.html`** : Interface pour afficher les recommandations.

#### `utils/`
- Contient des scripts utilitaires pour gérer les fonctionnalités clés du projet :
  - **`load_data.py`** : Chargement des données depuis Azure Blob Storage.
  - **`recommend_logic.py`** : Génération des recommandations.
  - **`user_data.py`** : Gestion des interactions utilisateur.
  - **`test_blob_connection.py`** : Vérification des connexions à Azure Blob Storage.

### Fichiers Racine

- **`main.py`** : Point d'entrée pour tester le projet localement.
- **`requirements.txt`** : Liste des dépendances nécessaires pour exécuter le projet.
- **`README.md`** : Documentation complète du projet.

## Fonctionnalités Principales

1. **Recommandations Personnalisées** :
   - Génération d'une liste de recommandations basées sur les clics utilisateur et un modèle hybride (80% filtrage basé sur le contenu, 20% filtrage collaboratif).
   
2. **Marquage d'Articles** :
   - Permet de marquer un article comme "lu" pour exclure cet article des recommandations futures.

3. **Robustesse Technique** :
   - Vérification des connexions aux services Azure (Blob Storage, API Flask, etc.).
   - Gestion des erreurs avec des logs détaillés.
  
