from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from agendamento.models import Reserva
from agendamento.services import GoogleAgendaService


class Command(BaseCommand):
    help = 'Verifica reservas pendentes que ultrapassaram a tolerância de check-in e marca como NÃO COMPARECEU'

    def handle(self, *args, **options):
        agora = timezone.now()

        # Tolerância: Considera No-Show se já se passaram 20 minutos do horário de início sem check-in
        tempo_limite = agora - timedelta(minutes=20)

        # Busca reservas confirmadas, com check-in pendente, cujo início já ultrapassou o limite
        reservas_noshow = Reserva.objects.filter(
            status='confirmada',
            status_checkin='Pendente',
            inicio__lte=tempo_limite
        )

        total = reservas_noshow.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS(
                'Nenhuma reserva em No-Show encontrada no momento.'))
            return

        self.stdout.write(
            f'Encontradas {total} reservas para processar No-Show...')

        for reserva in reservas_noshow:
            # 1. Atualiza no banco do Django
            reserva.status_checkin = 'NÃO COMPARECEU'
            reserva.save(update_fields=['status_checkin'])

            # 2. Atualiza na Planilha do Google (Pinta a célula de Vermelho)
            if reserva.linha_planilha:
                GoogleAgendaService.atualizar_checkin_google(
                    linha_planilha=reserva.linha_planilha,
                    status_checkin='NÃO COMPARECEU',
                    hora_checkin=""
                )

            self.stdout.write(
                self.style.WARNING(
                    f'🔴 Reserva #{reserva.id} ({reserva.usuario.email}) marcada como NÃO COMPARECEU.')
            )

        self.stdout.write(self.style.SUCCESS(
            f'✅ Processamento concluído: {total} reservas atualizadas.'))
