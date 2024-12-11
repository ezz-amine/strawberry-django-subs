"""
ASGI config for graphql_demo project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graphql_demo.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from strawberry.asgi import GraphQL
from graphql_demo.schema import schema
from django.urls import path


graphql_app = GraphQL(schema)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # Ajouter les routes pour les WebSockets ici
            path("graphql/", graphql_app),
        ])
    ),
})