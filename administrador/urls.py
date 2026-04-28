from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from hubs.models import *

app_name = 'administrador'

urlpatterns = [
    path("", views.areaAdm, name="areaAdm"),
    
    # gerencia os hubs
    path("cadastrarHub/", views.cadastrarHub, name="cadastrarHub"),
    path("gerenciarHubs/", views.gerenciarHubs, name="gerenciarHubs"),
    path("alterarHub/", views.alterarHub, name="alterarHub"),
    path("deletaHub/<int:hubs_id>", views.deletaHub, name="deletaHub"),

    # gerencia as noticias
    path("cadastrarNoticias/", views.cadastrarNoticias, name="cadastrarNoticias"),
    path("gerenciarNoticias/", views.gerenciarNoticias, name="gerenciarNoticias"),
    path("alterarNoticias/", views.alterarNoticias, name="alterarNoticias"),
    path("deletaNoticias/<int:hubs_id>", views.deletaNoticias, name="deletaNoticias"),

    #gerencia os usuários
    path("listar_usuarios/", views.listar_usuarios, name="listar_usuarios"),
    path("detalhe_usuario/<int:usuario_id>/", views.detalhe_usuario, name="detalhe_usuario"),
    path("desativar_usuario/<int:usuario_id>/", views.desativar_usuario, name="desativar_usuario"),
]

