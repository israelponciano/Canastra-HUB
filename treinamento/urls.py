from django.urls import path
from . import views

app_name = 'treinamento'

urlpatterns = [
    path('', views.listar_treinamentos, name='listar_treinamentos'),
    path('criar/', views.criar_treinamento, name='criar_treinamentos'),
    path('<int:treinamento_id>/inscrever/', views.inscrever, name='inscrever'),
    path('<int:treinamento_id>/cancelar/', views.cancelar_inscricao, name='cancelar'),
]