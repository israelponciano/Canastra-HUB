from django.urls import path
from . import views

urlpatterns = [
    path('reservar/', views.realizar_reserva, name='realizar_reserva'),
    path('minhas-reservas/', views.minhas_reservas, name='minhas_reservas'),
    path('api/reservas/', views.api_reservas_calendario, name='api_reservas'),
    
    # NOVAS ROTAS ADMINISTRATIVAS
    path('reservas/<int:reserva_id>/editar/', views.editar_reserva, name='editar_reserva'),
    path('reservas/<int:reserva_id>/excluir/', views.excluir_reserva, name='excluir_reserva'),
]