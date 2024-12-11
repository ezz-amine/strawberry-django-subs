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
