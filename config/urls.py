from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from . import views

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
    path('agendar/', views.realizar_reserva, name='realizar_reserva'),
    path('minhas-reservas/', views.minhas_reservas, name='minhas_reservas'),
    path('editar/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),
    path('excluir/<int:reserva_id>/',
         views.excluir_reserva, name='excluir_reserva'),
    path('api/reservas/', views.api_reservas_calendario,
         name='api_reservas_calendario'),

    # 🎯 ROTA DO QR CODE (Check-in Presencial / Uso Direto)
    path('checkin/<str:sala_chave>/',
         views.checkin_qrcode, name='checkin_qrcode'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
