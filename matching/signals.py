# matching/signals.py
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Usuario
from vagas.models import Vagas
from matching.matcher import JobModel, ResumeModel
from .service import get_matcher
from .text_builders import build_resume_text, build_job_text

logger = logging.getLogger(__name__)


def _upsert_scores_for_usuario(usuario):
    """Computa composite_score do usuario contra todas as vagas e faz bulk upsert."""
    from .models import MatchScore
    from .scoring import composite_score

    matcher = get_matcher()
    vagas = list(Vagas.objects.all())
    if not vagas:
        return

    records = []
    for vaga in vagas:
        try:
            result = composite_score(usuario, vaga, matcher.model)
            records.append(MatchScore(
                usuario=usuario,
                vaga=vaga,
                score=result['score'],
                breakdown=result['breakdown'],
            ))
        except Exception:
            logger.exception("Erro ao calcular score usuario=%s vaga=%s", usuario.pk, vaga.pk)

    if records:
        MatchScore.objects.bulk_create(
            records,
            update_conflicts=True,
            unique_fields=['usuario', 'vaga'],
            update_fields=['score', 'breakdown', 'updated_at'],
        )


def _upsert_scores_for_vaga(vaga):
    """Computa composite_score de todos os usuarios contra a vaga e faz bulk upsert."""
    from .models import MatchScore
    from .scoring import composite_score

    matcher = get_matcher()
    usuarios = list(Usuario.objects.all())
    if not usuarios:
        return

    records = []
    for usuario in usuarios:
        try:
            result = composite_score(usuario, vaga, matcher.model)
            records.append(MatchScore(
                usuario=usuario,
                vaga=vaga,
                score=result['score'],
                breakdown=result['breakdown'],
            ))
        except Exception:
            logger.exception("Erro ao calcular score usuario=%s vaga=%s", usuario.pk, vaga.pk)

    if records:
        MatchScore.objects.bulk_create(
            records,
            update_conflicts=True,
            unique_fields=['usuario', 'vaga'],
            update_fields=['score', 'breakdown', 'updated_at'],
        )


@receiver(post_save, sender=Usuario, dispatch_uid="matching.sync_usuario")
def sync_usuario(sender, instance, **kwargs):
    try:
        get_matcher().update_resume(
            ResumeModel(
                text=build_resume_text(instance),
                candidate_name=instance.user.nome,
                candidate_id=str(instance.pk),
            )
        )
    except Exception:
        logger.exception("Erro ao sincronizar candidato %s com o JobMatcher", instance.pk)

    try:
        _upsert_scores_for_usuario(instance)
    except Exception:
        logger.exception("Erro ao persistir MatchScore para usuario %s", instance.pk)


@receiver(post_save, sender=Vagas, dispatch_uid="matching.sync_vaga")
def sync_vaga(sender, instance, **kwargs):
    try:
        get_matcher().update_job(
            JobModel(
                text=build_job_text(instance),
                job_title=instance.cargo_vaga or "",
                company=instance.empresa.nomefantasia if instance.empresa else "",
                job_id=str(instance.id),
            )
        )
    except Exception:
        logger.exception("Erro ao sincronizar vaga %s com o JobMatcher", instance.id)

    try:
        _upsert_scores_for_vaga(instance)
    except Exception:
        logger.exception("Erro ao persistir MatchScore para vaga %s", instance.pk)
