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
        user = self.model(email=self.normalize_email(
            email), nome=nome, tipo=tipo)
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
                             validators=[FileExtensionValidator(
                                 allowed_extensions=["jpg", "png", "jpeg"])],
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


class Estado(models.Model):
    nome_estado = models.CharField(max_length=100)
    sigla_estado = models.CharField(max_length=2)

    def __str__(self):
        return f"{self.nome_estado} ({self.sigla_estado})"


class Cidade(models.Model):
    nome_cidade = models.CharField(max_length=100)
    estado_cidade = models.ForeignKey(Estado, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome_cidade} - {self.estado_cidade.sigla_estado}"

# USUARIO DO SISTEMA


class Usuario(models.Model):
    user = models.OneToOneField(
        UsuarioBase, on_delete=models.CASCADE, primary_key=True)
    curso = models.CharField(max_length=100, blank=True, null=True, default='')

    # informação pessoal
    nome_social = models.CharField(max_length=255, blank=True, null=True)
    data_nascimento = models.DateField()
    genero = models.CharField(max_length=255)
    estado_civil = models.CharField(max_length=255)
    nacionalidade = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)

    # endereco
    cep = models.CharField(max_length=10)
    rua = models.CharField(max_length=255)
    bairro = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)

    # obejtivo_profissional
    cargo_pretendido = models.CharField(max_length=255, blank=True, null=True )
    area_interesse = models.CharField(max_length=255, blank=True, null=True)
    pretensao_salarial = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    disponibilidade =  models.CharField(max_length=255, blank=True, null=True)

    # formação academica
    instituicao_nome = models.CharField(max_length=255, blank=True, null=True)
    grau_escolaridade = models.CharField(max_length=255, blank=True, null=True)
    curso_graduacao = models.CharField(max_length=255, blank=True, null=True)
    situacao_academica = models.CharField(max_length=255, blank=True, null=True)
    data_acad_inicio = models.DateField(blank=True, null=True)
    data_acad_fim = models.DateField(blank=True, null=True)

    # rede sociais e links
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)  # apenas username
    facebook = models.URLField(blank=True, null=True)
    site_pessoal = models.URLField(blank=True, null=True)

    # competencias
    competencias_tecnicas = models.TextField(blank=True, null=True)
    competencias_comportamentais = models.TextField(blank=True, null=True)

    # inclusao e acessibilidade
    pessoa_com_deficiencia = models.BooleanField(default=False)
    tipo_deficiencia = models.CharField(max_length=255, blank=True, null=True)
    necessidade_adaptacao = models.TextField(blank=True, null=True)

    # informações adicionais
    remoto = models.BooleanField(default=False)
    interesses_hobbies = models.TextField(blank=True, null=True)

    # ANEXOS (considere modelo separado para múltiplos arquivos)
    curriculo_pdf = models.FileField(
        upload_to='curriculos/', blank=True, null=True)
    carta_apresentacao = models.FileField(upload_to='cartas/', blank=True, null=True)

    # METADADOS
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_social

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


# MODELOS SEPARADOS RECOMENDADOS (para melhor normalização)
class ExperienciaProfissional(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='experiencias')
    nome_empresa = models.CharField(max_length=255, blank=True, null=True)
    cargo = models.CharField(max_length=255, blank=True, null=True)

    empresa_cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT, blank=True, null=True)
    empresa_estado = models.ForeignKey(Estado, on_delete=models.PROTECT, blank=True, null=True)
    tipo_contrato = models.CharField(max_length=255, blank=True, null=True)
    descricao_atividades = models.TextField(blank=True, null=True)
    data_inicio = models.DateField(blank=True, null=True)
    data_fim = models.DateField(blank=True, null=True)  
    emprego_atual = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cargo} - {self.nome_empresa}"

    class Meta:
        ordering = ['-data_inicio']


class CursoExtraCurricular(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='cursos_extras')
    nome_curso = models.CharField(max_length=255, blank=True, null=True)
    instituicao = models.CharField(max_length=255, blank=True, null=True)
    carga_horaria = models.PositiveIntegerField(blank=True, null=True)
    data_conclusao = models.DateField(blank=True, null=True)
    link_certificado = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nome_curso


class Idioma(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='idiomas')
    idioma = models.CharField(max_length=100, blank=True, null=True)
    nivel_fluencia = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.idioma}"


class Hub(models.Model):
    nome_hub = models.CharField(max_length=100)
    descricao = models.CharField(max_length=250)
    foto = models.ImageField(upload_to="fotos_hub/",
                             validators=[FileExtensionValidator(
                                 allowed_extensions=["jpg", "png", "jpeg"])],
                             null=True,
                             blank=True,
                             default=None)

    def __str__(self):
        return f"{self.nome_hub}"
