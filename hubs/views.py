"""
App hubs — views extraídas do core/views.py.
Hub, Noticia e NoticiaHub permanecem em core/models.py durante a
transição; este app apenas concentra as views e URLs.
"""

from django.shortcuts import render, get_object_or_404

from hubs.models import *
from empresa.models import EmpresaHub
from treinamento.models import Treinamento
from eventos.models import Evento


def listar_hubs(request):
    """Central de Hubs — lista todos os hubs ativos."""
    hubs = Hub.objects.filter(isActive=True)
    return render(request, 'hubs/listar.html', {'hubs': hubs})


def hub_detalhe(request, nome_hub):
    """Página dinâmica de cada hub com notícias, treinamentos, eventos e empresas."""
    hub = get_object_or_404(Hub, nome_hub=nome_hub, isActive=True)

    noticias = NoticiaHub.objects.filter(
        hub=hub,
        noticia__isActive=True,
    ).select_related('noticia')

    treinamentos = (
        Treinamento.objects
        .filter(hub=hub)
        .prefetch_related('sessoes')
        .order_by('-id')
    )

    eventos = (
        Evento.objects
        .filter(hub=hub)
        .order_by('-data_evento_inicio')[:5]
    )

    empresas_hub = EmpresaHub.objects.filter(hub=hub).select_related('empresa__user')

    return render(request, 'hubs/hub.html', {
        'hub': hub,
        'noticias': noticias,
        'treinamentos': treinamentos,
        'eventos': eventos,
        'empresas_hub': empresas_hub,
    })