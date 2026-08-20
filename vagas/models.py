from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.db.models.deletion import ProtectedError
from core.models import *
from empresa.models import *

# Create your models here.
class Vagas(models.Model):
    cargo_vaga = models.CharField(max_length=100,  blank=True, null=True)
    descricao_vaga = models.TextField(blank=True, null=True)
    requisito_vaga = models.TextField(blank=True, null=True)
    
    local = models.CharField(max_length=255, blank=True, null=True)
    data_publicacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, blank=True, null=True, default='ativa')
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='vagas')
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE, related_name='vagas', null=True, blank=True)

    def __str__(self):
        return f"Vaga: {self.cargo_vaga}, {self.descricao_vaga}"
    
class UsuarioVaga(models.Model):
    STATUS_CANDIDATADO = 'candidatado'
    STATUS_CONTRATADO = 'contratado'
    STATUS_REJEITADO = 'rejeitado'
    STATUS_CHOICES = [
        (STATUS_CANDIDATADO, 'Candidatado'),
        (STATUS_CONTRATADO, 'Contratado'),
        (STATUS_REJEITADO, 'Rejeitado'),
    ]

    vaga = models.ForeignKey(Vagas, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_candidatura = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_CANDIDATADO)
    data_status = models.DateTimeField(null=True, blank=True)
    ifmg_no_momento_contratacao = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.usuario.nome_social} -> {self.vaga.cargo_vaga}"

class CursoVaga(models.Model):
    vaga = models.ForeignKey(Vagas, on_delete=models.CASCADE)
    curso = models.CharField(max_length=100, blank=True, null=True)
    