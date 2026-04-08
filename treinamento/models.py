from django.db import models
from core.models import UsuarioBase, Hub

class Treinamento(models.Model):
    nome = models.CharField(max_length=100)
    data_inicio = models.DateField(blank=True, null=True)
    data_fim = models.DateField(blank=True, null=True)
    local = models.CharField(max_length=255, blank=True, null=True)
    publico_alvo = models.CharField(max_length=255, blank=True, null=True)
    descricao = models.TextField(max_length=250, blank=True, null=True)
    vagas_disponiveis = models.PositiveIntegerField(default=0)       # novo
    tipo_setc = models.CharField(max_length=100, blank=True, null=True)  # novo
    hub = models.ForeignKey(                                          # novo
        Hub, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='treinamentos'
    )

    def __str__(self):
        return self.nome


class SessaoTreinamento(models.Model):         # novo — múltiplos horários
    treinamento = models.ForeignKey(
        Treinamento, on_delete=models.CASCADE, related_name='sessoes'
    )
    data = models.DateField()
    horario = models.TimeField()

    def __str__(self):
        return f"{self.treinamento.nome} — {self.data} {self.horario}"


class InscricaoTreinamento(models.Model):
    treinamento = models.ForeignKey(Treinamento, on_delete=models.CASCADE)
    usuario = models.ForeignKey(UsuarioBase, on_delete=models.CASCADE)
    data_inscricao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('treinamento', 'usuario')

    def __str__(self):
        return f"{self.usuario.email} → {self.treinamento.nome}"