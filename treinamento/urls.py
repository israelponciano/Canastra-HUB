from django.urls import path
from . import views

app_name = 'treinamento'

urlpatterns = [
    path('', views.listar_treinamentos, name='listar_treinamentos'),
    path('criar/', views.criar_treinamento, name='cadastro_treinamentos'),
    path('<int:treinamento_id>/editar/', views.editar_treinamento, name='editar_treinamento'),
    path('<int:treinamento_id>/remover/', views.remover_treinamento, name='remover_treinamento'),
    path('<int:treinamento_id>/inscrever/', views.inscrever, name='inscrever'),
    path('<int:treinamento_id>/cancelar/', views.cancelar_inscricao, name='cancelar'),
]