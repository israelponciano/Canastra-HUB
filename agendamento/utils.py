from django.utils import timezone
from .models import Reserva


def processar_noshow_banco():
    agora = timezone.now()

    qtd_atualizadas = Reserva.objects.filter(
        fim__lte=agora,
        status='confirmada',
        status_checkin='Pendente'  # Alinhado com o campo da sua tabela
    ).update(status='nao_compareceu')

    return qtd_atualizadas
