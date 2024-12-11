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
# Dans notre cas le projet est nommer graphql_demo

# (si nécessaire)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

```

## Création du fichier asgi.py

Ce fichier permet de définir la structure de l'application ASGI avec Django Channels :

```bash
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nom_du_projet.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Requêtes HTTP classiques
    "websocket": AuthMiddlewareStack(
        URLRouter(
            []  # Ajoutez vos routes WebSocket ici si nécessaire
        )
    ),
})

```

Pour la configuration AGSI de notre backend de ce projet, nous avons défini la structure de l'application ASGI comme suite:


```bash

graphql_app = GraphQL(schema)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
           
            path("graphql/", graphql_app),
        ])
    ),
})

```
Les WebSockets sont généralement utilisés pour implémenter les subscriptions.

Un WebSocket est un protocole de communication bidirectionnel qui permet une interaction en temps réel entre un client (comme un navigateur web) et un serveur.les WebSockets établissent une connexion persistante, permettant à l'un ou l'autre côté d'envoyer des données à tout moment.

#### Structure de base d'un WebSocket :
Client : Établit une connexion avec un serveur via WebSocket.
Serveur : Écoute les connexions entrantes et communique avec le client.

Dans notre cas comme nous utilisons GraphQL avec Django Channels, donc nous devons configurer asgi.py pour inclure un routeur WebSocket et nous allons utiliser le django admin comme client HTTP:

<img src= "picture/img1.png"><img/>

## Création du schéma GraphQL avec une subscription

Dans notre projet nous avons defini un schéma qui contient les query ainsi que un subsription pour le test du backend:

```bash

import asyncio
from typing import List, AsyncGenerator
from asgiref.sync import async_to_sync
import strawberry
from strawberry.types import Info
from strawberry.django import type as strawberry_django_type
from strawberry.django.views import GraphQLView
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL
from strawberry.asgi import GraphQL

from django.db.models.signals import post_save
from django.dispatch import receiver

import django.apps

Category_maladie = django.apps.apps.get_model('app_test', 'Category_maladie')
Patient = django.apps.apps.get_model('app_test', 'Patient')



# Types pour les modèles Django
@strawberry.django.type(Category_maladie)
class CategoryMaladieType:
    id: strawberry.ID
    name: str
    patients: List["PatientType"]


@strawberry.django.type(Patient)
class PatientType:
    id: strawberry.ID
    name: str
    name_maladie: str
    category_maladie: CategoryMaladieType



# Résolveurs pour les abonnements
@strawberry.type
class Subscription:
    @strawberry.subscription
    async def new_patient(self) -> AsyncGenerator[str, None]:
        """
        Notifie en temps réel lorsqu'un nouveau patient est ajouté.
        """
        print("Un client s'est abonné à 'new_patient'")

        queue = asyncio.Queue()

        @receiver(post_save, sender=Patient)
        def patient_signal_handler(sender, instance, created, **kwargs):
            if created:
                # Placer le message dans la file d'attente en mode synchrone
                async_to_sync(queue.put)(f"Nouveau patient ajouté : {instance.name}")

        # Gestion des abonnements
        #try:
        while True:
            message = await queue.get()
            yield message
       # finally:
            # Déconnecter le signal lorsque l'abonnement est terminé
            #post_save.disconnect(patient_signal_handler, sender=Patient)




# Résolveurs pour les mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_patient(
        self,
        info: Info,
        name: str,
        name_maladie: str,
        category_id: strawberry.ID,
    ) -> PatientType:
        """
        Ajoute un nouveau patient et retourne ses détails.
        """
        category = Category_maladie.objects.get(id=category_id)
        patient = Patient.objects.create(
            name=name, name_maladie=name_maladie, category_maladie=category
        )
        return patient



# Résolveurs pour les requêtes
@strawberry.type
class Query:
    @strawberry.field
    def all_categories(self, info: Info) -> List[CategoryMaladieType]:
        """
        Retourne toutes les catégories de maladies.
        """
        return Category_maladie.objects.all()

    @strawberry.field
    def all_patients(self, info: Info) -> List[PatientType]:
        """
        Retourne tous les patients.
        """
        return Patient.objects.all()

    @strawberry.field
    def patients_by_category(self, info: Info, category_id: strawberry.ID) -> List[PatientType]:
        """
        Retourne les patients appartenant à une catégorie spécifique.
        """
        return Patient.objects.filter(category_maladie_id=category_id)


# Schéma et configuration GraphQL
schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)

graphql_app = GraphQL(schema, subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL])


```

Le code du subscription coté serveur  permet de notifier le client quand un patient est ajouter.
