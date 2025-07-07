from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'empresa'

urlpatterns = [
    path("cadastro_empresa", views.cadastro_empresa, name="cadastro_empresa"),
]