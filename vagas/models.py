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
    curso = models.CharField(max_length=100, blank=True, null=True)
    tipo_vaga = models.CharField(max_length=255, blank=True, null=True)
    nivel_educacional = models.Charfield(max_length=255, blank=True, null=True)
    faixa_salarial = models.CharField(max_length=100, blank=True, null=True)
    beneficios = models.TextField(blank=True, null=True)
    carga_horaria = models.CharField(max_length=100, blank=True, null=True)
    modalidade = models.CharField(max_length=100, blank=True, null=True)
    
    data_publicacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='vagas')

    empresa_estado = models.ForeignKey(Estado, on_delete=models.PROTECT, blank=True, null=True)
    empresa_cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f"Vaga: {self.cargo_vaga}, {self.tipo_vaga}, {self.modalidade}"
    
class UsuarioVaga(models.Model):
    vaga = models.ForeignKey(Vagas, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_candidatura = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.usuario.username} -> {self.vaga.cargo_vaga}"

