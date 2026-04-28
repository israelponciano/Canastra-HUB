from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.deletion import ProtectedError
from django.core.validators import FileExtensionValidator

class Hub(models.Model):
    nome_hub = models.CharField(max_length=100, unique=True)
    descricao_hub = models.CharField(max_length=250)
    foto_hub = models.ImageField(upload_to="fotos_hub/",
                             validators=[FileExtensionValidator(
                                 allowed_extensions=["jpg", "png", "jpeg"])],
                             null=True,
                             blank=True,
                             default=None)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome_hub}"
    

class Noticia(models.Model):
    titulo_noticia = models.CharField(max_length=250)
    descricao_noticia = models.CharField(max_length=250)
    fonte = models.CharField(max_length=50)
    url = models.URLField(blank=True, null=True)
    isActive = models.BooleanField(default=True)
    isHome = models.BooleanField(default=True)
    imagem_noticia = models.ImageField(upload_to="fotos_noticia/",
                             validators=[FileExtensionValidator(
                                 allowed_extensions=["jpg", "png", "jpeg"])],
                             null=True,
                             blank=True,
                             default=None, db_column='foto_hub')

class NoticiaHub(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)


