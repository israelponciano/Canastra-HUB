from django.db import models

# ------------------ USUÁRIO ------------------
class TblUsuario(models.Model):
    intIdUsuario = models.AutoField(primary_key=True)
    txtNomeCompleto = models.CharField(max_length=255)
    txtNomeSocial = models.CharField(max_length=255, blank=True, null=True)
    datNascimento = models.DateField()

    txtGenero = models.CharField(max_length=20, choices=[
        ('Masculino', 'Masculino'),
        ('Feminino', 'Feminino'),
        ('Outro', 'Outro'),
        ('Prefiro não dizer', 'Prefiro não dizer')
    ])

    txtEstadoCivil = models.CharField(max_length=20, choices=[
        ('Solteiro', 'Solteiro'),
        ('Casado', 'Casado'),
        ('Divorciado', 'Divorciado'),
        ('Viúvo', 'Viúvo'),
        ('Outro', 'Outro')
    ])

    txtNacionalidade = models.CharField(max_length=100)
    txtTelefonePrincipal = models.CharField(max_length=20)
    txtTelefoneSecundario = models.CharField(max_length=20, blank=True, null=True)

    txtCEP = models.CharField(max_length=10)
    txtRua = models.CharField(max_length=255)
    txtNumero = models.CharField(max_length=10)
    txtComplemento = models.CharField(max_length=25, blank=True, null=True)

    txtCidade = models.CharField(max_length=100, null=True, blank=True)
    txtEstado = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.txtNomeCompleto


# ------------------ CURRÍCULO ------------------
class TblCurriculo(models.Model):
    DISPONIBILIDADE_CHOICES = [
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('integral', 'Integral'),
        ('noturno', 'Noturno'),
        ('fim_de_semana', 'Fins de semana'),
    ]

    intIdCurriculo = models.AutoField(primary_key=True)
    intIdUsuario = models.OneToOneField(TblUsuario, on_delete=models.CASCADE, related_name='curriculo')

    txtCargoPretendido = models.CharField(max_length=100)
    txtAreaInteresse = models.CharField(max_length=100)
    decPretensaoSalarial = models.DecimalField(max_digits=10, decimal_places=2)
    txtDisponibilidade = models.CharField(max_length=20, choices=DISPONIBILIDADE_CHOICES)
    txtCurriculoPdf = models.FileField(upload_to='curriculos/')
    txtCartaApresentacao = models.FileField(upload_to='cartas/', blank=True, null=True)
    bolDisponibilidadeRemoto = models.BooleanField()

    def __str__(self):
        return f"{self.intIdUsuario.txtNomeCompleto} - {self.txtCargoPretendido}"


# ------------------ SKILLS ------------------
class TblSkill(models.Model):
    intIdSkill = models.AutoField(primary_key=True)
    intIdCurriculo = models.ForeignKey(TblCurriculo, on_delete=models.CASCADE, related_name='skills')
    txtSkill = models.CharField(max_length=100)

    def __str__(self):
        return self.txtSkill


# ------------------ ACESSIBILIDADE ------------------
class TblAcessibilidade(models.Model):
    intIdAcessibilidade = models.AutoField(primary_key=True)
    intIdCurriculo = models.OneToOneField(TblCurriculo, on_delete=models.CASCADE, related_name='acessibilidade')
    bolPCD = models.BooleanField()
    txtTipoDeficiencia = models.CharField(max_length=255, blank=True, null=True)
    txtNecessidadeAdaptacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"PCD: {self.bolPCD}"


# ------------------ REDES SOCIAIS ------------------
class TblRedesSociais(models.Model):
    intIdRedesSociais = models.AutoField(primary_key=True)
    intIdCurriculo = models.OneToOneField(TblCurriculo, on_delete=models.CASCADE, related_name='redes')

    txtLinkedin = models.CharField(max_length=255, blank=True, null=True)
    txtGithub = models.CharField(max_length=255, blank=True, null=True)
    txtSitePessoal = models.CharField(max_length=255, blank=True, null=True)
    txtInstagram = models.CharField(max_length=255, blank=True, null=True)
    txtFacebook = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.txtLinkedin or "Redes Sociais"


# ------------------ EXPERIÊNCIA PROFISSIONAL ------------------
class TblExperienciaProfissional(models.Model):
    intIdExperiencia = models.AutoField(primary_key=True)
    intIdCurriculo = models.ForeignKey(TblCurriculo, on_delete=models.CASCADE, related_name='experiencias')

    txtNomeEmpresa = models.CharField(max_length=255)
    txtCargo = models.CharField(max_length=100)
    txtTipoContrato = models.CharField(max_length=20, choices=[
        ('CLT', 'CLT'),
        ('PJ', 'PJ'),
        ('Freelancer', 'Freelancer'),
        ('Estágio', 'Estágio'),
        ('Temporário', 'Temporário'),
        ('Outro', 'Outro')
    ])
    txtLocal = models.CharField(max_length=255)
    txtDescricao = models.TextField()
    datPeriodoInicio = models.DateField()
    datPeriodoFim = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.txtCargo} em {self.txtNomeEmpresa}"


# ------------------ CURSOS ------------------
class TblCurso(models.Model):
    intIdCurso = models.AutoField(primary_key=True)
    intIdCurriculo = models.ForeignKey(TblCurriculo, on_delete=models.CASCADE, related_name='cursos')

    txtNomeCurso = models.CharField(max_length=255)
    txtInstituicao = models.CharField(max_length=255)
    intCargaHoraria = models.IntegerField()
    datConclusao = models.DateField()

    def __str__(self):
        return self.txtNomeCurso


# ------------------ IDIOMAS ------------------
class TblIdioma(models.Model):
    intIdIdioma = models.AutoField(primary_key=True)
    intIdCurriculo = models.ForeignKey(TblCurriculo, on_delete=models.CASCADE, related_name='idiomas')

    txtIdioma = models.CharField(max_length=100)
    txtNivelFluencia = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.txtIdioma} ({self.txtNivelFluencia})"


# ------------------ FORMAÇÃO ACADÊMICA ------------------
class TblFormacaoAcademica(models.Model):
    intIdFormacao = models.AutoField(primary_key=True)
    intIdCurriculo = models.ForeignKey(TblCurriculo, on_delete=models.CASCADE, related_name='formacoes')

    txtNomeInstituicao = models.CharField(max_length=255)
    txtGrau = models.CharField(max_length=100)
    txtCurso = models.CharField(max_length=255)
    txtSituacao = models.CharField(max_length=20, choices=[
        ('Cursando', 'Cursando'),
        ('Concluído', 'Concluído'),
        ('Trancado', 'Trancado'),
        ('Abandonado', 'Abandonado')
    ])
    datInicio = models.DateField()
    datConclusao = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.txtCurso} - {self.txtSituacao}"
