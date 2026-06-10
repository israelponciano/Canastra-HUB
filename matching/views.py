# matching/views.py
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core.models import Usuario
from vagas.models import Vagas
from .service import get_matcher

logger = logging.getLogger(__name__)


@require_GET
def candidatos_para_vaga(request, vaga_id):
    top_k = _parse_int(request.GET.get("top"), default=5, min_val=1, max_val=50)
    min_score = _parse_float(request.GET.get("min_score"), default=0.0)

    if top_k is None or min_score is None:
        return JsonResponse({"erro": "Parâmetros inválidos."}, status=400)

    try:
        vaga = Vagas.objects.select_related("empresa").get(pk=vaga_id)
    except Vagas.DoesNotExist:
        return JsonResponse({"erro": "Vaga não encontrada."}, status=404)

    try:
        resultados = get_matcher().match_structured_resumes_for_job(
            vaga=vaga, top_k=top_k, min_score=min_score
        )
    except Exception:
        logger.exception("Erro no matching para vaga %s", vaga_id)
        return JsonResponse({"erro": "Erro interno."}, status=500)

    return JsonResponse({
        "resultados": [
            {
                "id": r.entity_id,
                "nome": r.name,
                "score": r.score,
                "breakdown": r.breakdown,
            }
            for r in resultados
        ]
    })


@require_GET
def vagas_para_usuario(request, usuario_pk):
    top_k = _parse_int(request.GET.get("top"), default=5, min_val=1, max_val=50)
    min_score = _parse_float(request.GET.get("min_score"), default=0.0)

    if top_k is None or min_score is None:
        return JsonResponse({"erro": "Parâmetros inválidos."}, status=400)

    try:
        usuario = Usuario.objects.select_related("user").get(pk=usuario_pk)
    except Usuario.DoesNotExist:
        return JsonResponse({"erro": "Candidato não encontrado."}, status=404)

    try:
        resultados = get_matcher().match_structured_jobs_for_resume(
            usuario=usuario, top_k=top_k, min_score=min_score
        )
    except Exception:
        logger.exception("Erro no matching para candidato %s", usuario_pk)
        return JsonResponse({"erro": "Erro interno."}, status=500)

    return JsonResponse({
        "resultados": [
            {
                "id": r.entity_id,
                "cargo": r.name,
                "empresa": r.company,
                "score": r.score,
                "breakdown": r.breakdown,
            }
            for r in resultados
        ]
    })


def _parse_int(value, *, default: int, min_val: int, max_val: int):
    if value is None:
        return default
    try:
        v = int(value)
        return v if min_val <= v <= max_val else None
    except (ValueError, TypeError):
        return None


def _parse_float(value, *, default: float):
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
