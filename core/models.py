from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.deletion import ProtectedError

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
    
    
class Usuario(models.Model):
    user = models.OneToOneField(UsuarioBase, on_delete=models.CASCADE, primary_key=True)
    curso = models.CharField(max_length=100)

    def __str__(self):
        return f"Usuário: {self.user.nome}"
