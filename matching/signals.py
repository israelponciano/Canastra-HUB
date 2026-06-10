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


@receiver(post_save, sender=Vagas, dispatch_uid="matching.sync_vaga")
def sync_vaga(sender, instance, **kwargs):
    try:
        get_matcher().update_job(
            JobModel(
                text=build_job_text(instance),
                job_title=instance.cargo_vaga or "",
                company=instance.empresa.nomefantasia or "",
                job_id=str(instance.id),
            )
        )
    except Exception:
        logger.exception("Erro ao sincronizar vaga %s com o JobMatcher", instance.id)
