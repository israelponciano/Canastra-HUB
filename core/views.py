from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from core.models import *

# Create your views here.


def home(request):

    return render(request, 'home.html')

def hubs(request):

    return render(request, 'hubs.html')

def cadastro(request):

    return render(request, 'cadastro.html')


def cadastro_usuario(request):
    if request.user.is_authenticated:
        messages.warning(
            request, f'Você ja está logado, não é possivel realizar outro cadastro.')
        return redirect('core:home')
    if request.method == 'POST':
        nomeUser = request.POST.get('txtNome')
        nomeSocial = request.POST.get('txtNomeSocial')
        dataNasc = request.POST.get('txtDataNasc')
        genero = request.POST.get('txtGenero')
        estadoCivil = request.POST.get('txtEstadoCivil')
        nacionalidade = request.POST.get('txtNacionalidade')
        email = request.POST.get('txtEmail')
        telefone = request.POST.get('txtTelefone')
        senha = request.POST.get('txtSenha')
        foto_user = request.FILES.get('fileFoto')
        cep = request.POST.get('txtCep')
        rua = request.POST.get('txtRua')
        numero = request.POST.get('txtNumero')
        bairro = request.POST.get('txtBairro')
        complemento = request.POST.get('txtComplemento')

        cidade_id = request.POST.get('cidade')
        estado_id = request.POST.get('estado')

        if not Estado.objects.filter(id=estado_id).exists():
            messages.error(request, 'Estado inválido.')
            estados = Estado.objects.all().order_by('nome_estado')
            return render(request, 'cadastro_usuario.html', {'estados': estados})

        if not Cidade.objects.filter(id=cidade_id).exists():
            messages.error(request, 'Cidade inválida.')
            estados = Estado.objects.all().order_by('nome_estado')
            return render(request, 'cadastro_usuario.html', {'estados': estados})
        # Buscar os objetos Estado e Cidade no Banco
        estado = Estado.objects.get(id=estado_id)
        cidade = Cidade.objects.get(id=cidade_id)

        # Criar usuário base
        user = UsuarioBase.objects.create_user(
            email=email,
            password=senha,
            nome=nomeUser,
            tipo='usuario'
        )
        user.foto = foto_user
        user.save()
        # Cria usuario com os outros campos faltantes
        usuario = Usuario.objects.create(
            user=user,
            nome_social=nomeSocial,
            data_nascimento=dataNasc,
            genero=genero,
            estado_civil=estadoCivil,
            nacionalidade=nacionalidade,
            telefone=telefone,
            cep=cep,
            rua=rua,
            numero=numero,
            bairro=bairro,
            estado=estado,
            cidade=cidade,
            complemento=complemento
        )
        request.session['usuario_email'] = usuario.user.email

        messages.success(request, 'Cadastro inicial realizado! Complete seu perfil profissional!')
        return redirect('core:login')

    estados = Estado.objects.all().order_by('nome_estado')
    return render(request, 'cadastro_usuario.html', {'estados': estados})


def cadastro_completo(request):
    usuario_email = request.session.get('email_atual')
    print(usuario_email)
    if not usuario_email:
        messages.error(request, 'Você deve realizar o cadastro inicial primeiro!')
        return redirect('core:cadastro_usuario')

    usuario = Usuario.objects.select_related('user').filter(user__email=usuario_email).first()
    if not usuario:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('core:cadastro_usuario')

    if request.method == 'POST':
        #Objetivo Profissional
        cargo_pretendido = request.POST.get('txtCargoPretendido')
        area_interesse = request.POST.get('txtAreaInteresse')
        pretensao_salarial = request.POST.get('decPretensaoSalarial')
        disponibilidade = request.POST.get('txtDisponibilidade')

        #Formacao Academica
        instituicao_nome = request.POST.get('txtNomeInstituicao')
        grau_escolaridade = request.POST.get('escolaridade')
        curso_graduacao = request.POST.get('txtCurso')
        situacao_academica = request.POST.get('txtSituacao')
        data_acad_inicio = request.POST.get('txtDataAcad')
        data_acad_fim = request.POST.get('txtDataFimAcad')

        #Experiencia professional
        nome_empresa = request.POST.get('txtNomeEmpresa')
        cargo = request.POST.get('txtCargo')
        tipo_contrato = request.POST.get('tipoContrato')
        empresa_cidade_id = request.POST.get('cidadeEmpresa')
        empresa_estado_id = request.POST.get('estadoEmpresa')
        descricao_atividades = request.POST.get('txtDescricao')
        data_inicio = request.POST.get('txtDataProf')
        data_fim = request.POST.get('txtDataFimProf')

        #Rede sociais e links
        linkedin = request.POST.get('txtLinkedin')
        github = request.POST.get('txtGithub')
        instagram = request.POST.get('txtInstagram')
        facebook = request.POST.get('txtFacebook')
        site_pessoal = request.POST.get('txtSitePessoal')

        #Curso Extracurriculares
        nome_curso = request.POST.get('txtNomeCurso')
        instituicao = request.POST.get('txtInstituicao')
        carga_horaria = request.POST.get('txtCargaHoras')
        data_conclusao = request.POST.get('txtDataFimCurso')
        link_certificado = request.POST.get('txtLinkCertificado')
        
        #Idiomas 
        idioma = request.POST.get('txtIdioma')
        nivel_fluencia = request.POST.get('fluencia')

        #Competencias
        competencias_tecnicas = request.POST.get('txtHardSkil')
        competencias_comportamentais = request.POST.get('txtSoftSkil')

        #Acessibilidade 
        pessoa_com_deficiencia = request.POST.get('pcd') == 'sim'
        tipo_deficiencia = request.POST.get('tipoDeficiencia')
        necessidade_adaptacao = request.POST.get('necessidadeAdaptacao')

        #Informações Adicionais
        remoto = request.POST.get('remoto') == 'sim'
        interesses_hobbies = request.POST.get('txtHobbie')

        #Anexos
        curriculo_pdf = request.FILES.get('curriculoPdf')
        carta_apresentacao = request.FILES.get('cartaApresentacao')

        # Buscando no banco
        empresa_cidade = Cidade.objects.filter(id = empresa_cidade_id).first()
        empresa_estado = Estado.objects.filter(id = empresa_estado_id).first()

        # Salvando no banco
        usuario.cargo_pretendido = cargo_pretendido
        usuario.area_interesse = area_interesse
        usuario.pretensao_salarial = pretensao_salarial
        usuario.disponibilidade = disponibilidade
        
        usuario.instituicao_nome = instituicao_nome
        usuario.grau_escolaridade = grau_escolaridade
        usuario.curso_graduacao = curso_graduacao
        usuario.situacao_academica = situacao_academica
        usuario.data_acad_inicio = data_acad_inicio
        usuario.data_acad_fim = data_acad_fim
        
        usuario.nome_empresa = nome_empresa
        usuario.cargo = cargo
        usuario.tipo_contrato = tipo_contrato
        usuario.empresa_cidade = empresa_cidade
        usuario.empresa_estado = empresa_estado
        usuario.descricao_atividades = descricao_atividades
        usuario.data_inicio = data_inicio
        usuario.data_fim = data_fim
        
        usuario.linkedin = linkedin
        usuario.github = github
        usuario.instagram = instagram
        usuario.facebook = facebook
        usuario.site_pessoal = site_pessoal

        usuario.nome_curso = nome_curso
        usuario.instituicao = instituicao
        usuario.carga_horaria = carga_horaria
        usuario.data_conclusao = data_conclusao
        usuario.link_certificado = link_certificado
        
        usuario.idioma = idioma
        usuario.nivel_fluencia = nivel_fluencia
        
        usuario.competencias_tecnicas = competencias_tecnicas
        usuario.competencias_comportamentais = competencias_comportamentais
        
        usuario.pessoa_com_deficiencia = pessoa_com_deficiencia
        usuario.tipo_deficiencia = tipo_deficiencia
        usuario.necessidade_adaptacao = necessidade_adaptacao
        
        usuario.remoto = remoto
        usuario.interesses_hobbies = interesses_hobbies
        
        usuario.curriculo_pdf = curriculo_pdf
        usuario.carta_apresentacao = carta_apresentacao

        usuario.save()

        # del request.session['usuario_email']
        messages.success(request, 'Deu boa')
        return render(request, 'home.html')

    estados = Estado.objects.all().order_by('nome_estado')
    return render(request, 'cadastro_usuario_completo.html', {'estados': estados})



def login(request):
    if request.method == 'POST':
        email = request.POST.get('txtEmail')
        senha = request.POST.get('txtSenha')

        print(email, senha)

        usuario = authenticate(request, username=email, password=senha)
        print(usuario)
        
        if usuario is not None:
            request.session.flush()
            #cria a sessao do usuario
            auth_login(request, usuario)
                
            request.session['is_login'] = False
            if usuario.foto and hasattr(usuario.foto, "url"):
                foto = usuario.foto.url
            else:
                foto = None
            if usuario.is_admin:
                request.session['is_admin'] = usuario.is_admin
            request.session['nome'] = usuario.nome
            request.session['foto'] = foto
            request.session['perfil'] = usuario.tipo
            request.session['id_atual'] = usuario.id
            request.session['email_atual'] = usuario.email
            
            #configura sessao para expirar em 4 horas
            request.session.set_expiry(14400)
            
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('core:home')
        
        else:
            print("Usuario ou senha invalidos")
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'login.html')


def logout(request):
    # limpa a sessao ao deslogar
    request.session.flush()
    auth_logout(request)

    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('core:home')


@require_http_methods(["GET"])
def get_cidades(request):
    """View para retornar cidades via AJAX baseado no estado selecionado"""
    estado_id = request.GET.get('estado_id')

    # Validação básica do parâmetro
    if not estado_id or not estado_id.isdigit():
        return JsonResponse({
            'cidades': [],
            'error': 'ID do estado inválido'
        })

    # Verificar se o estado existe
    if not Estado.objects.filter(id=estado_id).exists():
        return JsonResponse({
            'cidades': [],
            'error': 'Estado não encontrado'
        })

    # Buscar cidades
    cidades = Cidade.objects.filter(
        estado_cidade_id=estado_id
    ).order_by('nome_cidade').values('id', 'nome_cidade')

    cidades_data = [
        {'id': cidade['id'], 'nome': cidade['nome_cidade']}
        for cidade in cidades
    ]

    return JsonResponse({
        'cidades': cidades_data,
        'total': len(cidades_data)
    })
