from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'administrador'

urlpatterns = [
    path("cadastro_hubs/", views.cadastro_hubs, name="cadastro_hubs"),
    # path("gerenciar_hubs/", views.cadastro_hubs, name="cadastro_hubs"),
]
