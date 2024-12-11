# GRAPHQL-SUBSCRIPTIONS

Ce backend utilise Django, Strawberry-GraphQL et Django-Channels pour implémenter une API GraphQL avec subscriptions, en exploitant les WebSockets pour des mises à jour en temps réel. ASGI et Daphne permettent de garantir une gestion optimale des requêtes asynchrones et des protocoles modernes.

## Bibliothèques nécessaires

Nous devons nous assurer d'installer les bibliothèques suivantes :

```bash
pip install django strawberry-graphql django-channels daphne
```

### Description des bibliothèques

Django : Framework principal pour la gestion des données et des vues.
Strawberry-GraphQL : Fournit un schéma GraphQL simple à configurer.
Django-Channels : Ajoute la prise en charge d'ASGI pour des protocoles asynchrones comme les WebSockets.
Daphne : Serveur ASGI utilisé pour exécuter l'application.


## Configuration dans settings.py

Ajoutez ou modifiez les configurations suivantes pour activer l'ASGI et les WebSockets :

```bash 
# Ajout des applications nécessaires
INSTALLED_APPS = [
    ...,
    'channels',              # Nécessaire pour la prise en charge ASGI
    'strawberry.django',     # Intégration de Strawberry avec Django
]

# Configuration des Channels pour ASGI
ASGI_APPLICATION = 'nom_du_projet.asgi.application'

# Configuration optionnelle pour Redis (si nécessaire)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

```