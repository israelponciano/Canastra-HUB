from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'empresa'

urlpatterns = [
    path("cadastro_empresa/", views.cadastro_empresa, name="cadastro_empresa"),
    path("criar_empresa/", views.criar_empresa, name="criar_empresa"),
    path('get_cidades/', views.get_cidades, name='get_cidades'),
]
