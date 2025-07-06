from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.db.models.deletion import ProtectedError
from core.models import UsuarioBase, Estado, Cidade
# Create your models here.
class Segmento(models.Model):
    nome_segmento = models.CharField(max_length=100)

    def __str__(self):
        return self.nome_segmento

class Empresa(models.Model):
    user = models.OneToOneField(UsuarioBase, on_delete=models.CASCADE, primary_key=True)
    nomefantasia = models.CharField(max_length=100, default=False)
    tipo_empresa = models.CharField(max_length=100, default=False)
    razao_social = models.CharField(max_length=255, default=False)
    cnpj = models.CharField(max_length=20, default=False)
    telefone = models.CharField(max_length=20, default=False)
    rua = models.CharField(max_length=255, default=False)
    cep = models.CharField(max_length=10, default=False)
    numero = models.IntegerField(default=False)
    complemento = models.CharField(max_length=25, default=False)
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)

    segmentos = models.ManyToManyField(Segmento, through='EmpresaSegmento')
    
    def __str__(self):
        return f"Empresa: {self.user.nome}, {self.nomefantasia}, {self.tipo_empresa}"
    

class EmpresaSegmento(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    segmento = models.ForeignKey(Segmento, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.empresa.user.nome} - {self.segmento.nome_segmento}"
