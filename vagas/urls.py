from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'vagas'

urlpatterns = [
    path("cadastro_vagas/", views.cadastro_vagas, name="cadastro_vagas"),
    path("criar_vagas/", views.criar_vagas, name="criar_vagas"),
    path('get_cidades/', views.get_cidades, name='get_cidades'),
]