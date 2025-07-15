from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.fncCadastrarCurriculo, name='tela_cadastro'),
]