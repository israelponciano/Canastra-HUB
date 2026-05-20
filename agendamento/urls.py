from django.urls import path
from . import views

urlpatterns = [
    # O primeiro parâmetro é o link do navegador (ex: mysite.com/agendamento/reservar/)
    # O segundo é a função da views
    # O terceiro é o apelido (name) usado nas tags {% url %} do HTML
    path('reservar/', views.realizar_reserva, name='realizar_reserva'),
]