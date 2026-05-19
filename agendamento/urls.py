from django.urls import path
from . import views

urlpatterns = [
    path('agendar/', views.realizar_reserva, name='realizar_reserva'),
]