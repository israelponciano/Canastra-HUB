from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'administrador'

urlpatterns = [
    path("", views.areaAdm, name="areaAdm"),
    path("cadastrarHub/", views.cadastrarHub, name="cadastrarHub"),
    path("gerenciarHubs/", views.gerenciarHubs, name="gerenciarHubs"),
    path("alterarHub/", views.alterarHub, name="alterarHub"),
    path("deletaHub/<int:hubs_id>", views.deletaHub, name="deletaHub"),
]
