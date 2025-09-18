from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.deletion import ProtectedError
from django.core.validators import FileExtensionValidator

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, tipo, password=None):
        if not email:
            raise ValueError('O usuário deve ter um endereço de e-mail')
        user = self.model(email=self.normalize_email(email), nome=nome, tipo=tipo)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, tipo, password=None):
        user = self.create_user(email, nome, tipo, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class UsuarioBase(AbstractBaseUser):
    nome = models.CharField(max_length=300)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    tipo = models.CharField(max_length=10, null=False)

    foto = models.ImageField(upload_to="fotos_perfil/",
                                    validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "jpeg"])],
                                    null=True,
                                    blank=True,
                                    default=None)
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
    
#USUARIO DO SISTEMA, INCOMPLETO    
class Usuario(models.Model):
    user = models.OneToOneField(UsuarioBase, on_delete=models.CASCADE, primary_key=True)
    curso = models.CharField(max_length=100)

    def __str__(self):
        return f"Usuário: {self.user.nome}"
    
    
class Estado(models.Model):
    nome_estado = models.CharField(max_length=100)
    sigla_estado = models.CharField(max_length=2)
    
    def __str__(self):
        return f"{self.nome_estado} ({self.sigla_estado})"
    
    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"


class Cidade(models.Model):
    nome_cidade = models.CharField(max_length=100)
    estado_cidade = models.ForeignKey(Estado, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome_cidade} - {self.estado_cidade.sigla_estado}"
    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"


class Hub(models.Model):
    nome_hub = models.CharField(max_length=100)
    descricao = models.CharField(max_length=250)
    foto = models.ImageField(upload_to="fotos_hub/",
                                    validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "jpeg"])],
                                    null=True,
                                    blank=True,
                                    default=None)

    def __str__(self):
        return f"Usuário: {self.user.nome}"
    