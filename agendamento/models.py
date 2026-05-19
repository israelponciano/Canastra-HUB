from django.db import models
from django.conf import settings

class Reserva(models.Model):
    SALA_CHOICES = [
        ('A', 'Sala A'),
        ('B', 'Sala B'),
    ]
    
    STATUS_CHOICES = [
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuário")
    sala = models.CharField(max_length=1, choices=SALA_CHOICES, verbose_name="Sala")
    inicio = models.DateTimeField(verbose_name="Data/Hora de Início")
    fim = models.DateTimeField(verbose_name="Data/Hora de Término")
    
    # Este campo guarda o ID que o Google vai nos devolver. 
    # Sem ele, não conseguiremos editar ou cancelar no futuro.
    google_event_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID do Evento no Google")
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='confirmada')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        # Garante que não haja duplicidade exata no mesmo milissegundo por segurança
        ordering = ['-inicio']

    def __str__(self):
        return f"{self.usuario.email} - Sala {self.sala} ({self.inicio.strftime('%d/%m/%Y %H:%M')})"