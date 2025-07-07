from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.db.models.deletion import ProtectedError
from core.models import UsuarioBase
# Create your models here.
class Empresa(models.Model):
    user = models.OneToOneField(UsuarioBase, on_delete=models.CASCADE, primary_key=True)
    segmento = models.CharField(max_length=100)

    def __str__(self):
        return f"Empresa: {self.user.nome}"
    
# class Estado(models.Model):
#     nome_estado = models.CharField(max_length=100)
#     sigla_estado = models.CharField(max_length=2)

#     def __str__(self):
#         return self.sigla_estado


# class Cidade(models.Model):
#     nome_cidade = models.CharField(max_length=100)

#     def __str__(self):
#         return self.nome_cidade


# class Segmento(models.Model):
#     nome_segmento = models.CharField(max_length=100)

#     def __str__(self):
#         return self.nome_segmento


# class Empresa(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_empresa')
    
#     cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT)
#     estado = models.ForeignKey(Estado, on_delete=models.PROTECT)

#     CEP = models.CharField(max_length=10)
#     rua = models.CharField(max_length=255)
#     numero = models.IntegerField()
#     complemento = models.CharField(max_length=25)
#     tipo_empresa = models.CharField(max_length=100)
#     #nome_empresa = models.CharField(max_length=255, unique=True)
#     razao_social = models.CharField(max_length=255)
#     cnpj = models.CharField(max_length=20, unique=True)
#     #email_empresa = models.CharField(max_length=255, unique=True)
#     telefone_empresa = models.CharField(max_length=20)
    

#     segmentos = models.ManyToManyField(Segmento, through='EmpresaSegmento')

#     def __str__(self):
#         return self.nome_empresa


# class EmpresaSegmento(models.Model):
#     empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
#     segmento = models.ForeignKey(Segmento, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.empresa.nome_empresa} - {self.segmento.nome_segmento}"
