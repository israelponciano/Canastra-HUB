from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

# 1. IMPORTAÇÃO DAS VIEWS DE CHECK-IN / AGENDAMENTO:
# Assumindo que essas views estão em agendamento/views.py
from agendamento.views import (
    realizar_reserva,
    minhas_reservas,
    editar_reserva,
    excluir_reserva,
    api_reservas_calendario,
    gerador_qrcodes,
    checkin_qrcode
)

# NOTA: O 'from . import views' foi removido!

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('core.urls')),
    path('empresa/', include('empresa.urls')),
    path('vagas/', include('vagas.urls')),
    path('administrador/', include('administrador.urls')),
    path('treinamento/', include('treinamento.urls')),
    path('perfil/', include('perfil.urls')),
    path('eventos/', include('eventos.urls')),
    path('agendamento/', include('agendamento.urls')),

    # parte de check-in
    path('agendar/', realizar_reserva, name='realizar_reserva'),
    path('minhas-reservas/', minhas_reservas, name='minhas_reservas'),
    path('editar/<int:reserva_id>/', editar_reserva, name='editar_reserva'),
    path('excluir/<int:reserva_id>/', excluir_reserva, name='excluir_reserva'),
    path('api/reservas/', api_reservas_calendario,
         name='api_reservas_calendario'),


    path('qrcodes/', gerador_qrcodes, name='gerador_qrcodes'),
    # 🎯 ROTA DO QR CODE (Check-in Presencial / Uso Direto)
    path('checkin/<str:sala_chave>/', checkin_qrcode, name='checkin_qrcode'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
