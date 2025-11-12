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

def parceiros(request):

    return render(request, 'parceiros.html')

def agro(request):

    return render(request, 'agro.html')

def apicultura(request):

    return render(request, 'apicultura.html')

def sobre(request):

    return render(request, 'sobre.html')

def espacos_hub(request):

    return render(request, 'espacos_hub.html')

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

        if(area_interesse != None):
            request.session['incompleto'] = False
            
        #Formacao Academica 1 
        instituicao_nome1= request.POST.get('txtNomeInstituicao1')
        grau_escolaridade1 = request.POST.get('escolaridade1')
        curso_graduacao1 = request.POST.get('txtCurso1')
        situacao_academica1 = request.POST.get('txtSituacao1')
        data_acad_inicio1 = request.POST.get('txtDataAcad1')
        data_acad_fim1= request.POST.get('txtDataFimAcad1')

        #Formacao Academica 2 
        instituicao_nome2 = request.POST.get('txtNomeInstituicao2')
        grau_escolaridade2 = request.POST.get('escolaridade2')
        curso_graduacao2 = request.POST.get('txtCurso2')
        situacao_academica2= request.POST.get('txtSituacao2')
        data_acad_inicio2 = request.POST.get('txtDataAcad2')
        data_acad_fim2 = request.POST.get('txtDataFimAcad2')

        #Formacao Academica 3
        instituicao_nome3 = request.POST.get('txtNomeInstituicao3')
        grau_escolaridade3 = request.POST.get('escolaridade3')
        curso_graduacao3 = request.POST.get('txtCurso3')
        situacao_academica3 = request.POST.get('txtSituacao3')
        data_acad_inicio3= request.POST.get('txtDataAcad3')
        data_acad_fim3 = request.POST.get('txtDataFimAcad3')

        #Experiencia professional 1
        nome_empresa1 = request.POST.get('txtNomeEmpresa1')
        cargo1 = request.POST.get('txtCargo1')
        data_inicio1 = request.POST.get('txtDataProf1')
        data_fim1 = request.POST.get('txtDataFimProf1')
        
        #Experiencia professional 2 
        nome_empresa2 = request.POST.get('txtNomeEmpresa2')
        cargo2 = request.POST.get('txtCargo2')
        data_inicio2 = request.POST.get('txtDataProf2')
        data_fim2 = request.POST.get('txtDataFimProf2')
        
        #Experiencia professional 3 
        nome_empresa3 = request.POST.get('txtNomeEmpresa3')
        cargo3 = request.POST.get('txtCargo3')
        data_inicio3 = request.POST.get('txtDataProf3')
        data_fim3 = request.POST.get('txtDataFimProf3')

        #Rede sociais e links
        linkedin = request.POST.get('txtLinkedin')
        github = request.POST.get('txtGithub')
        instagram = request.POST.get('txtInstagram')
        facebook = request.POST.get('txtFacebook')
        site_pessoal = request.POST.get('txtSitePessoal')

        #Curso Extracurriculares 1
        nome_curso1 = request.POST.get('txtNomeCurso1')
        instituicao1 = request.POST.get('txtInstituicao1')
        carga_horaria1 = request.POST.get('txtCargaHoras1')
        data_conclusao1 = request.POST.get('txtDataFimCurso1')
        link_certificado1 = request.POST.get('txtLinkCertificado1')

        #Curso Extracurriculares 2
        nome_curso2 = request.POST.get('txtNomeCurso2')
        instituicao2 = request.POST.get('txtInstituicao2')
        carga_horaria2 = request.POST.get('txtCargaHoras2')
        data_conclusao2 = request.POST.get('txtDataFimCurso2')
        link_certificado2 = request.POST.get('txtLinkCertificado2')

        #Curso Extracurriculares 3
        nome_curso3 = request.POST.get('txtNomeCurso3')
        instituicao3 = request.POST.get('txtInstituicao3')
        carga_horaria3 = request.POST.get('txtCargaHoras3')
        data_conclusao3 = request.POST.get('txtDataFimCurso3')
        link_certificado3 = request.POST.get('txtLinkCertificado3')
        
        #Idiomas 1
        idioma1 = request.POST.get('txtIdioma1')
        nivel_fluencia1 = request.POST.get('fluencia1')

        #Idiomas 2
        idioma2 = request.POST.get('txtIdioma2')
        nivel_fluencia2 = request.POST.get('fluencia2')

        #Idiomas 
        idioma3 = request.POST.get('txtIdioma3')
        nivel_fluencia3 = request.POST.get('fluencia3')

        #Competencias 1 
        competencias_tecnicas1 = request.POST.get('txtHardSkil1')
        competencias_comportamentais1 = request.POST.get('txtSoftSkil1')

        #Competencias 2 
        competencias_tecnicas2 = request.POST.get('txtHardSkil2')
        competencias_comportamentais2 = request.POST.get('txtSoftSkil2')

        #Competencias 3 
        competencias_tecnicas3 = request.POST.get('txtHardSkil3')
        competencias_comportamentais3 = request.POST.get('txtSoftSkil3')

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

        # SALVANDO NO BANCO  
        # Objetivo Profissional
        usuario.cargo_pretendido = cargo_pretendido
        usuario.area_interesse = area_interesse
        usuario.pretensao_salarial = pretensao_salarial
        usuario.disponibilidade = disponibilidade

        # Formação academica 1         
        usuario.instituicao_nome1 = instituicao_nome1
        usuario.grau_escolaridade1 = grau_escolaridade1
        usuario.curso_graduacao1 = curso_graduacao1
        usuario.situacao_academica1 = situacao_academica1
        usuario.data_acad_inicio1 = data_acad_inicio1
        usuario.data_acad_fim1 = data_acad_fim1
        # 2 
        usuario.instituicao_nome2 = instituicao_nome2
        usuario.grau_escolaridade2 = grau_escolaridade2
        usuario.curso_graduacao2 = curso_graduacao2
        usuario.situacao_academica2 = situacao_academica2
        usuario.data_acad_inicio2 = data_acad_inicio2
        usuario.data_acad_fim2 = data_acad_fim2
        # 3
        usuario.instituicao_nome3 = instituicao_nome3
        usuario.grau_escolaridade3 = grau_escolaridade3
        usuario.curso_graduacao3 = curso_graduacao3
        usuario.situacao_academica3 = situacao_academica3
        usuario.data_acad_inicio3 = data_acad_inicio3
        usuario.data_acad_fim3 = data_acad_fim3
        # end formacao
        # ------------

        # Experiencia profissional  
        usuario.nome_empresa1 = nome_empresa1
        usuario.cargo1 = cargo1
        usuario.data_inicio1 = data_inicio1
        usuario.data_fim1 = data_fim1
        # 2 
        usuario.nome_empresa2 = nome_empresa2
        usuario.cargo2 = cargo2
        usuario.data_inicio2 = data_inicio2
        usuario.data_fim2 = data_fim2
        # 3  
        usuario.nome_empresa3 = nome_empresa3
        usuario.cargo3 = cargo3
        usuario.data_inicio3 = data_inicio3
        usuario.data_fim3 = data_fim3
        # end Experiencia
        #  ------------------

        # Links e sites 
        usuario.linkedin = linkedin
        usuario.github = github
        usuario.instagram = instagram
        usuario.facebook = facebook
        usuario.site_pessoal = site_pessoal
        # end links
        # ----------

        # Curso Extra curricular 
        usuario.nome_curso1 = nome_curso1
        usuario.instituicao1 = instituicao1
        usuario.carga_horaria1 = carga_horaria1
        usuario.data_conclusao1 = data_conclusao1
        usuario.link_certificado1 = link_certificado1
        # 2 
        usuario.nome_curso2 = nome_curso2
        usuario.instituicao2 = instituicao2
        usuario.carga_horaria2 = carga_horaria2
        usuario.data_conclusao2 = data_conclusao2
        usuario.link_certificado2 = link_certificado2
        # 3 
        usuario.nome_curso3 = nome_curso3
        usuario.instituicao3 = instituicao3
        usuario.carga_horaria3 = carga_horaria3
        usuario.data_conclusao3 = data_conclusao3
        usuario.link_certificado3 = link_certificado3
        # end curso
        # -----------

        # Idioma 
        usuario.idioma1 = idioma1
        usuario.nivel_fluencia1 = nivel_fluencia1
        # 2 
        usuario.idioma2 = idioma2
        usuario.nivel_fluencia2 = nivel_fluencia2
        # 3 
        usuario.idioma3 = idioma3
        usuario.nivel_fluencia3 = nivel_fluencia3
        # end idioma 
        # ----------

        # Competencias
        usuario.competencias_tecnicas1 = competencias_tecnicas1
        usuario.competencias_comportamentais1 = competencias_comportamentais1
        # 2
        usuario.competencias_tecnicas2 = competencias_tecnicas2
        usuario.competencias_comportamentais2 = competencias_comportamentais2
        # 3 
        usuario.competencias_tecnicas3 = competencias_tecnicas3
        usuario.competencias_comportamentais3 = competencias_comportamentais3 
        # end Competencias
        # ---------------

        usuario.pessoa_com_deficiencia = pessoa_com_deficiencia
        usuario.tipo_deficiencia = tipo_deficiencia
        usuario.necessidade_adaptacao = necessidade_adaptacao
        
        usuario.remoto = remoto
        usuario.interesses_hobbies = interesses_hobbies
        
        usuario.curriculo_pdf = curriculo_pdf
        usuario.carta_apresentacao = carta_apresentacao

        campos_verif = [
            'data_nascimento', 'data_admissao', 'data_demissao',

            'pretensao_salarial',

            # Formação Acadêmica
            'data_acad_inicio1', 'data_acad_fim1',
            'data_acad_inicio2', 'data_acad_fim2',
            'data_acad_inicio3', 'data_acad_fim3',
            
            # Experiência Profissional
            'data_inicio1', 'data_fim1',
            'data_inicio2', 'data_fim2',
            'data_inicio3', 'data_fim3',
            
            # Cursos Extracurriculares
            'data_conclusao1', 'data_conclusao2', 'data_conclusao3'
        ]

        # Limpa todos os campos de data vazios
        for campo in campos_verif:
            valor = getattr(usuario, campo, None)
            if valor == '' or valor == 'None' or valor is None:
                setattr(usuario, campo, None)
        
        usuario.save()

        # del request.session['usuario_email']
        messages.success(request, 'Cadastro realizado com sucesso!')
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
            if usuario.tipo == "usuario":
                tblusuario = Usuario.objects.get(user = usuario)
                if tblusuario.area_interesse == None:
                    request.session['incompleto'] = True 
                    
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
