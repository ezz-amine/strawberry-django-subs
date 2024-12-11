from django.urls import path
from django.views.decorators.csrf import csrf_exempt
#from graphene_django.views import GraphQLView
from strawberry.django.views import GraphQLView
from graphql_demo.schema import schema
from . import views



urlpatterns = [
    # ...
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    path('', views.index, name='index'),
]