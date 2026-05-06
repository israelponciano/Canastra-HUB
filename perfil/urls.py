from django.urls import path
from . import views

app_name = 'perfil'

urlpatterns = [
    path('', views.perfil, name='perfil'),
    path('atualizar/', views.atualizar_perfil, name='atualizar_perfil'),
    path('api/cidades/', views.buscar_cidades, name='buscar_cidades'),
]