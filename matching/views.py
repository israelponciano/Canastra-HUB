# matching/views.py
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .service import get_matcher

logger = logging.getLogger(__name__)


@require_GET
def candidatos_para_vaga(request, vaga_id):
    top_k = _parse_int(request.GET.get('top'), default=5, min_val=1, max_val=50)
    min_score = _parse_float(request.GET.get('min_score'), default=0.0)

    if top_k is None or min_score is None:
        return JsonResponse({"erro": "Parâmetros inválidos."}, status=400)

    try:
        resultados = get_matcher().match_resumes_for_job(
            job_id=str(vaga_id), top_k=top_k, min_score=min_score
        )
    except ValueError as e:
        return JsonResponse({"erro": str(e)}, status=404)
    except Exception:
        logger.exception("Erro no matching para vaga %s", vaga_id)
        return JsonResponse({"erro": "Erro interno."}, status=500)

    return JsonResponse({
        "resultados": [
            {"id": r.entity_id, "nome": r.name, "score": r.score}
            for r in resultados
        ]
    })


@require_GET
def vagas_para_usuario(request, usuario_pk):
    top_k = _parse_int(request.GET.get('top'), default=5, min_val=1, max_val=50)
    min_score = _parse_float(request.GET.get('min_score'), default=0.0)

    if top_k is None or min_score is None:
        return JsonResponse({"erro": "Parâmetros inválidos."}, status=400)

    try:
        resultados = get_matcher().match_jobs_for_resume(
            candidate_id=str(usuario_pk), top_k=top_k, min_score=min_score
        )
    except ValueError as e:
        return JsonResponse({"erro": str(e)}, status=404)
    except Exception:
        logger.exception("Erro no matching para candidato %s", usuario_pk)
        return JsonResponse({"erro": "Erro interno."}, status=500)

    return JsonResponse({
        "resultados": [
            {"id": r.entity_id, "cargo": r.name, "empresa": r.company, "score": r.score}
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
