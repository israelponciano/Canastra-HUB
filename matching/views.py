# matching/views.py
import math
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core.models import Usuario
from vagas.models import Vagas
from .models import MatchScore

logger = logging.getLogger(__name__)


@require_GET
def candidatos_para_vaga(request, vaga_id):
    page = _parse_int(request.GET.get("page"), default=1, min_val=1, max_val=100_000)
    page_size = _parse_int(request.GET.get("page_size"), default=20, min_val=1, max_val=100)

    if page is None or page_size is None:
        return JsonResponse({"erro": "Parâmetros inválidos."}, status=400)

    if not Vagas.objects.filter(pk=vaga_id).exists():
        return JsonResponse({"erro": "Vaga não encontrada."}, status=404)

    qs = (
        MatchScore.objects
        .filter(vaga_id=vaga_id)
        .order_by('-score')
        .select_related('usuario__user')
    )
    total = qs.count()
    offset = (page - 1) * page_size
    resultados = qs[offset: offset + page_size]

    return JsonResponse({
        "total": total,
        "page": page,
        "pages": math.ceil(total / page_size) if total else 0,
        "resultados": [
            {
                "usuario_id": r.usuario_id,
                "nome": r.usuario.user.nome,
                "score": r.score,
                "breakdown": r.breakdown,
            }
            for r in resultados
        ],
    })


@require_GET
def vagas_para_usuario(request, usuario_pk):
    page = _parse_int(request.GET.get("page"), default=1, min_val=1, max_val=100_000)
    page_size = _parse_int(request.GET.get("page_size"), default=20, min_val=1, max_val=100)

    if page is None or page_size is None:
        return JsonResponse({"erro": "Parâmetros inválidos."}, status=400)

    if not Usuario.objects.filter(pk=usuario_pk).exists():
        return JsonResponse({"erro": "Candidato não encontrado."}, status=404)

    qs = (
        MatchScore.objects
        .filter(usuario_id=usuario_pk)
        .order_by('-score')
        .select_related('vaga__empresa')
    )
    total = qs.count()
    offset = (page - 1) * page_size
    resultados = qs[offset: offset + page_size]

    return JsonResponse({
        "total": total,
        "page": page,
        "pages": math.ceil(total / page_size) if total else 0,
        "resultados": [
            {
                "vaga_id": r.vaga_id,
                "cargo": r.vaga.cargo_vaga,
                "empresa": r.vaga.empresa.nomefantasia if r.vaga.empresa else "",
                "score": r.score,
                "breakdown": r.breakdown,
            }
            for r in resultados
        ],
    })


def _parse_int(value, *, default: int, min_val: int, max_val: int):
    if value is None:
        return default
    try:
        v = int(value)
        return v if min_val <= v <= max_val else None
    except (ValueError, TypeError):
        return None
