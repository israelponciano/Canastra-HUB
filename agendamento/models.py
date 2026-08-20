from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Reserva(models.Model):
    SALA_CHOICES = [
        ('treinamentos', 'Espaço de Treinamentos'),
        ('reunioes', 'Sala de Reuniões'),
        ('laboratorio', 'Laboratório de Práticas Gerais'),
        ('fast', 'FAST - Fábrica de Soluções Tecnológicas'),
    ]

    STATUS_CHOICES = [
        ('pendente_aprovacao', 'Aguardando Aprovação Noturna'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuário")
    sala = models.CharField(
        max_length=30, choices=SALA_CHOICES, verbose_name="Sala")
    inicio = models.DateTimeField(verbose_name="Data/Hora de Início")
    fim = models.DateTimeField(verbose_name="Data/Hora de Término")

    # Campos exigidos pela planilha
    empresa_projeto = models.CharField(
        max_length=150, blank=True, null=True, default="Não informado", verbose_name="Empresa/Projeto")
    quantidade_pessoas = models.PositiveIntegerField(
        default=0, verbose_name="Quantidade de Pessoas")
    finalidade = models.CharField(
        max_length=255, blank=True, null=True, default="Não informado", verbose_name="Finalidade")
    equipamentos = models.TextField(
        blank=True, null=True, default="Não informado", verbose_name="Equipamentos")
    observacoes = models.TextField(
        blank=True, null=True, default="Não informado", verbose_name="Observações")

    # Status e horário de Check-in
    status_checkin = models.CharField(
        max_length=30, default="Pendente", verbose_name="Status Check-in")
    hora_checkin = models.DateTimeField(
        blank=True, null=True, verbose_name="Hora Check-in")

    # Integração Google Sheets / Calendar
    google_event_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="ID do Evento no Google")
    linha_planilha = models.IntegerField(
        blank=True, null=True, verbose_name="Linha na Planilha Google")

    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='confirmada')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-inicio']

    def clean(self):
        """Validação no modelo para garantir coerência nas datas."""
        if self.inicio and self.fim and self.inicio >= self.fim:
            raise ValidationError(
                "A data/hora de término deve ser posterior à data/hora de início.")

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.email} - {self.get_sala_display()} ({self.inicio.strftime('%d/%m/%Y %H:%M')})"
