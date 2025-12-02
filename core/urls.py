from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    # path("main", views.main, name="main"),
    path("", views.home, name="home"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    
    # cadastros de usuario    
    path("cadastro/", views.cadastro, name="cadastro"),
    path("cadastro_usuario/", views.cadastro_usuario, name="cadastro_usuario"),
    path("cadastro_usuario_completo/", views.cadastro_completo, name="cadastro_completo"),
    path("get_cidades/", views.get_cidades, name="get_cidades"),
    
    # cadastros de eventos    
    path("cadastro_eventos/", views.cadastro_eventos, name="cadastro_eventos"),
    path("criar_eventos/", views.criar_eventos, name="criar_eventos"),
    path('buscar_eventos/', views.buscar_eventos, name='buscar_eventos'),

    # cadastros de treinamento    
    path("cadastro_treinamentos/", views.cadastro_treinamentos, name="cadastro_treinamentos"),
    path("criar_treinamentos/", views.criar_treinamentos, name="criar_treinamentos"),
    path('buscar_treinamentos/', views.buscar_treinamentos, name='buscar_treinamentos'),

    # tela de hubs 
    path("hubs/", views.hubs, name="hubs"),
    path("agro/", views.agro, name="agro"),
    path("apicultura/", views.apicultura, name="apicultura"),
    path("queijo/", views.queijo, name="queijo"),
    path("calcados/", views.calcados, name="calcados"),
    path("milho/", views.milho, name="milho"),
    path("graos/", views.graos, name="graos"),
    path("sobre/", views.sobre, name="sobre"),
    path("espacos_hub/", views.espacos_hub, name="espacos_hub"),
    path("parceiros/", views.parceiros, name="parceiros"),
]
