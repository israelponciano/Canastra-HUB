from django.urls import path
from . import views

app_name = 'agendamento'

urlpatterns = [
    # Painel principal do agendamento (Calendário + Lista)
    path('', views.minhas_reservas, name='minhas_reservas'),

    # api ajax horarios em constants.py
    path('api/horarios-sala/', views.obter_horarios_sala,
         name='obter_horarios_sala'),
    # Formulário de criação de nova reserva
    path('novo/', views.realizar_reserva, name='realizar_reserva'),

    # API para popular o FullCalendar
    path('api/reservas/', views.api_reservas_calendario,
         name='api_reservas_calendario'),

    # Gerenciamento de reservas
    path('editar/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),
    path('excluir/<int:reserva_id>/',
         views.excluir_reserva, name='excluir_reserva'),

    # 🎯 QR CODE & CHECK-IN PRESENCIAL
    path('qrcodes/', views.gerador_qrcodes, name='gerador_qrcodes'),
    path('checkin/<str:sala_chave>/', views.checkin_qrcode, name='checkin_qrcode'),

    # configurações de emails HUB(para disparo de confirmações)
    path('configuracoes/',
         views.gerenciar_configuracoes_hub, name='configuracoes_hub'),
]
