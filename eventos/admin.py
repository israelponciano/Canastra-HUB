from django.contrib import admin
from .models import Evento, InscricaoEvento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nome_evento', 'hub', 'data_evento_inicio', 'data_evento_fim', 'vagas_disponiveis')
    list_filter = ('hub', 'data_evento_inicio')
    search_fields = ('nome_evento', 'local_evento')


@admin.register(InscricaoEvento)
class InscricaoEventoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'evento', 'data_inscricao', 'presenca')
    list_filter = ('presenca', 'evento')
    search_fields = ('usuario__email', 'evento__nome_evento')