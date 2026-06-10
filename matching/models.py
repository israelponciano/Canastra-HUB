from django.db import models
from core.models import Usuario
from vagas.models import Vagas


class MatchScore(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='match_scores')
    vaga = models.ForeignKey(Vagas, on_delete=models.CASCADE, related_name='match_scores')
    score = models.FloatField(default=0.0)
    breakdown = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'vaga')

    def __str__(self):
        return f"{self.usuario_id}<->{self.vaga_id}: {self.score}"
