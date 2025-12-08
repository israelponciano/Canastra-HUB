from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'vagas'

urlpatterns = [
    path("cadastro_vagas/", views.cadastro_vagas, name="cadastro_vagas"),
    path("criar_vagas/", views.criar_vagas, name="criar_vagas"),
    path('get_cidades/', views.get_cidades, name='get_cidades'),
    path('mensagembonita/', views.mensagembonita, name='mensagembonita'),
    path('buscar_vagas/', views.buscar_vagas, name='buscar_vagas'),
    path('vaga/<int:vaga_id>/', views.detalhe_vaga, name='detalhe_vaga'),
    path('vaga/<int:vaga_id>/candidatar/',
         views.candidatar_vaga, name='candidatar_vaga'),
    path('vaga/<int:vaga_id>/cancelar/',
         views.cancelar_candidatura, name='cancelar_candidatura'),
]
