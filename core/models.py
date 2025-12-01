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

    # formação academica 1 
    instituicao_nome1 = models.CharField(max_length=255, blank=True, null=True)
    grau_escolaridade1 = models.CharField(max_length=255, blank=True, null=True)
    curso_graduacao1 = models.CharField(max_length=255, blank=True, null=True)
    situacao_academica1 = models.CharField(max_length=255, blank=True, null=True)
    data_acad_inicio1 = models.DateField(blank=True, null=True)
    data_acad_fim1 = models.DateField(blank=True, null=True)

    # formação academica 2 
    instituicao_nome2 = models.CharField(max_length=255, blank=True, null=True)
    grau_escolaridade2 = models.CharField(max_length=255, blank=True, null=True)
    curso_graduacao2 = models.CharField(max_length=255, blank=True, null=True)
    situacao_academica2= models.CharField(max_length=255, blank=True, null=True)
    data_acad_inicio2 = models.DateField(blank=True, null=True)
    data_acad_fim2 = models.DateField(blank=True, null=True)

    # formação academica 3 
    instituicao_nome3 = models.CharField(max_length=255, blank=True, null=True)
    grau_escolaridade3 = models.CharField(max_length=255, blank=True, null=True)
    curso_graduacao3 = models.CharField(max_length=255, blank=True, null=True)
    situacao_academica3 = models.CharField(max_length=255, blank=True, null=True)
    data_acad_inicio3 = models.DateField(blank=True, null=True)
    data_acad_fim3 = models.DateField(blank=True, null=True)

    # rede sociais e links
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)  # apenas username
    facebook = models.URLField(blank=True, null=True)
    site_pessoal = models.URLField(blank=True, null=True)

    # competencias 1 
    competencias_tecnicas1 = models.TextField(blank=True, null=True)
    competencias_comportamentais1 = models.TextField(blank=True, null=True)

    # competencias 2
    competencias_tecnicas2 = models.TextField(blank=True, null=True)
    competencias_comportamentais2 = models.TextField(blank=True, null=True)

    # competencias 3
    competencias_tecnicas3 = models.TextField(blank=True, null=True)
    competencias_comportamentais3 = models.TextField(blank=True, null=True)

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


class ExperienciaProfissional(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='experiencias')
    nome_empresa1 = models.CharField(max_length=255, blank=True, null=True)
    cargo1 = models.CharField(max_length=255, blank=True, null=True)
    data_inicio1 = models.DateField(blank=True, null=True)
    data_fim1 = models.DateField(blank=True, null=True)  

    nome_empresa2 = models.CharField(max_length=255, blank=True, null=True)
    cargo2 = models.CharField(max_length=255, blank=True, null=True)
    data_inicio2 = models.DateField(blank=True, null=True)
    data_fim2= models.DateField(blank=True, null=True)  

    nome_empresa3= models.CharField(max_length=255, blank=True, null=True)
    cargo3 = models.CharField(max_length=255, blank=True, null=True)
    data_inicio3 = models.DateField(blank=True, null=True)
    data_fim3 = models.DateField(blank=True, null=True)  
    
    def __str__(self):
        return f"{self.cargo} - {self.nome_empresa}"
        

class CursoExtraCurricular(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='cursos_extras')
    nome_curso1 = models.CharField(max_length=255, blank=True, null=True)
    instituicao1 = models.CharField(max_length=255, blank=True, null=True)
    carga_horaria1 = models.PositiveIntegerField(blank=True, null=True)
    data_conclusao1 = models.DateField(blank=True, null=True)
    link_certificado1 = models.URLField(blank=True, null=True)

    nome_curso2 = models.CharField(max_length=255, blank=True, null=True)
    instituicao2 = models.CharField(max_length=255, blank=True, null=True)
    carga_horaria2 = models.PositiveIntegerField(blank=True, null=True)
    data_conclusao2 = models.DateField(blank=True, null=True)
    link_certificado2 = models.URLField(blank=True, null=True)

    nome_curso3 = models.CharField(max_length=255, blank=True, null=True)
    instituicao3 = models.CharField(max_length=255, blank=True, null=True)
    carga_horaria3 = models.PositiveIntegerField(blank=True, null=True)
    data_conclusao3 = models.DateField(blank=True, null=True)
    link_certificado3 = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nome_curso


class Idioma(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='idiomas')
    idioma1 = models.CharField(max_length=100, blank=True, null=True)
    nivel_fluencia1 = models.CharField(max_length=100, blank=True, null=True)

    idioma2 = models.CharField(max_length=100, blank=True, null=True)
    nivel_fluencia2 = models.CharField(max_length=100, blank=True, null=True)

    idioma3 = models.CharField(max_length=100, blank=True, null=True)
    nivel_fluencia3 = models.CharField(max_length=100, blank=True, null=True)

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


class Eventos(models.Model):
    nome_evento = models.CharField(max_length=100, blank=True, null=True)
    data_evento_inicio = models.DateField(blank=True, null=True)
    data_evento_fim = models.DateField(blank=True, null=True)
    horario_evento = models.TimeField(blank=True, null=True)
    local_evento = models.CharField(max_length=255, blank=True, null=True)
    publico_evento = models.CharField(max_length=255, blank=True, null=True)
    descricao_evento = models.TextField(max_length=250,blank=True, null=True)

    def __str__(self):
        return f"{self.nome_evento}"

class UsuarioEventos(models.Model):
    evento = models.ForeignKey(Eventos, on_delete=models.CASCADE)
    usuario = models.ForeignKey(UsuarioBase, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario.username} -> {self.evento.nome_evento}"


class Treinamentos(models.Model):
    nome_treinamentos = models.CharField(max_length=100, blank=True, null=True)
    data_treinamento_inicio = models.DateField(blank=True, null=True)
    data_treinamento_fim = models.DateField(blank=True, null=True)
    horario_treinamento = models.TimeField(blank=True, null=True)
    local_treinamento = models.CharField(max_length=255, blank=True, null=True)
    publico_treinamento = models.CharField(max_length=255, blank=True, null=True)
    descricao_treinamento = models.TextField(max_length=250, blank=True, null=True)

    def __str__(self):
        return f"{self.nome_treinamentos}"

class UsuarioTreinamentos(models.Model):
    treinamento = models.ForeignKey(Treinamentos, on_delete=models.CASCADE)
    usuario = models.ForeignKey(UsuarioBase, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario.username} -> {self.evento.nome_treinamentos}"
