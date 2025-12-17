from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods 
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from core.models import *
from empresa.models import *
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from datetime import datetime

def home(request):

    return render(request, 'home.html')

def hubs(request):

    return render(request, 'hubs.html')

def parceiros(request):

    return render(request, 'parceiros.html')

def agro(request):

    return render(request, 'agro.html')

def queijo(request):

    return render(request, 'queijo.html')

def apicultura(request):

    return render(request, 'apicultura.html')

def calcados(request):
    return render(request, 'calcados.html')


def milho(request):
    return render(request, 'milho.html')

def graos(request):

    return render(request, 'graos.html')

def sobre(request):

    return render(request, 'sobre.html')

def espacos_hub(request):

    return render(request, 'espacos_hub.html')

def cadastro(request):

    return render(request, 'cadastro.html')

def cadastro_eventos(request):
    
    return render(request,'cadastro_eventos.html')

def criar_eventos(request):
    usuario_email = request.session.get('email_atual')

    if request.method == 'POST':
        nome_evento = request.POST.get('txtNomeEvento')
        data_evento_inicio = request.POST.get('dteInicioEvento') 
        data_evento_fim = request.POST.get('dteFimEvento') 
        horario_evento = request.POST.get('hrEvento') 
        local_evento = request.POST.get('txtLocalEvento') 
        publico_evento = request.POST.get('txtPublicoAlvoEvento') 
        descricao_evento = request.POST.get('txtDescricaoEvento') 
        
        usuario = UsuarioBase.objects.get(email=usuario_email)
    
        evento = Eventos.objects.create(
            nome_evento = nome_evento,
            data_evento_inicio = data_evento_inicio,
            data_evento_fim = data_evento_fim,
            horario_evento = horario_evento,
            local_evento = local_evento,
            publico_evento = publico_evento, 
            descricao_evento = descricao_evento        
        )   

        UsuarioEventos.objects.create(
            evento = evento,
            usuario = usuario
        )
        messages.success(request, 'Evento cadastrado com sucesso')
        return redirect('core:home')

    return render(request, 'cadastro_evento.html')

def buscar_eventos(request):
    '''
    Lista todas os eventos ativos, com opção de filtrar por termo de busca.
    '''
    # 1. Receber o termo de busca (query) da URL (ex: /vagas/?q=Desenvolvedor)
    termo_busca = request.GET.get('q', '').strip()

    eventos= Eventos.objects.order_by('-data_evento_inicio')

    # 3. Se houver um termo de busca, aplica o filtro
    if termo_busca:
        # Filtra as vagas onde o termo de busca aparece:
        # - No cargo da vaga (cargo_vaga__icontains)
        # - Na descrição da vaga (descricao_vaga__icontains)
        # - Ou no requisito (requisito_vaga__icontains)
        eventos = eventos.filter(
            models.Q(nome_evento__icontains=termo_busca) |
            models.Q(descricao_evento__icontains=termo_busca) |
            models.Q(local_evento__icontains=termo_busca)
            # Usa .distinct() para evitar duplicatas, se a busca for mais complexa
        ).distinct()

    # 4. Prepara o contexto
    contexto = {
        'eventos': eventos,
        'termo_busca': termo_busca,  # Passa o termo de volta para o input na tela
    }

    # 5. Renderiza o template de busca
    return render(request, 'tela_busca_eventos.html', contexto)

def cadastro_treinamentos(request):

    return render(request, 'cadastro_treinamentos.html')


def criar_treinamentos(request):
    usuario_email = request.session.get('email_atual')

    if request.method == 'POST':
        nome_treinamentos = request.POST.get('txtNomeTreinamento')
        data_treinamento_inicio = request.POST.get('dteInicioTreinamento') 
        data_treinamento_fim = request.POST.get('dteFimTreinamento') 
        horario_treinamento = request.POST.get('hrTreinamento') 
        local_treinamento = request.POST.get('txtLocalTreinamento') 
        publico_treinamento = request.POST.get('txtPublicoAlvo') 
        descricao_treinamento = request.POST.get('txtDescricaoTreinamento') 
        
        usuario = UsuarioBase.objects.get(email=usuario_email)
    
        treinamento = Treinamentos.objects.create(
            nome_treinamentos = nome_treinamentos,
            data_treinamento_inicio = data_treinamento_inicio,
            data_treinamento_fim = data_treinamento_fim,
            horario_treinamento = horario_treinamento,
            local_treinamento = local_treinamento,
            publico_treinamento = publico_treinamento, 
            descricao_treinamento = descricao_treinamento        
        )   

        UsuarioTreinamentos.objects.create(
            treinamento = treinamento,
            usuario = usuario
        )
        messages.success(request, 'Treinamento cadastrado com sucesso')
        return redirect('core:home')
    
    return render(request,'cadastro_treinamentos.html')

def buscar_treinamentos(request):
    '''
    Lista todas os Treinamentos ativos, com opção de filtrar por termo de busca.
    '''

    termo_busca = request.GET.get('q', '').strip()

    treinamentos = Treinamentos.objects.order_by('-data_treinamento_inicio')

    # 3. Se houver um termo de busca, aplica o filtro
    if termo_busca:
        # filtrar por nome ou descrição 
        treinamentos = treinamentos.filter(
            models.Q(nome_treinamentos__icontains=termo_busca) |
            models.Q(descricao_treinamento__icontains=termo_busca) |
            models.Q(local_treinamento__icontains=termo_busca)
            # Usa .distinct() para evitar duplicatas, se a busca for mais complexa
        ).distinct()

    # 4. Prepara o contexto
    contexto = {
        'treinamentos': treinamentos,
        'termo_busca': termo_busca,
    }

    return render(request, 'tela_busca_treinamentos.html', contexto)


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
    
    
@login_required
def perfil(request):
    """
    View para exibir o perfil do usuário logado.
    Detecta o tipo de usuário (admin, empresa, usuario) e carrega os dados correspondentes.
    """
    user = request.user
    tipo_perfil = request.session.get('perfil', 'admin')
    
    # Carregar estados para os selects
    estados = Estado.objects.all().order_by('nome_estado')
    
    contexto = {
        'user': user,
        'estados': estados,
        'cidades': Cidade.objects.none(),  # Inicialmente vazio, carrega via AJAX
    }
    
    if tipo_perfil == 'empresa':
        try:
            empresa = Empresa.objects.select_related('cidade', 'estado').get(user=user)
            # Carregar cidades do estado selecionado
            if empresa.estado:
                contexto['cidades'] = Cidade.objects.filter(estado_cidade=empresa.estado).order_by('nome_cidade')
            
            # Carregar todos os hubs disponíveis
            hubs = Hub.objects.all().order_by('nome_hub')
            
            # Carregar IDs dos hubs vinculados à empresa
            hubs_vinculados = list(EmpresaHub.objects.filter(empresa=empresa).values_list('hub_id', flat=True))
            
            contexto['empresa'] = empresa
            contexto['hubs'] = hubs
            contexto['hubs_vinculados'] = hubs_vinculados
        except Empresa.DoesNotExist:
            messages.error(request, 'Perfil de empresa não encontrado.')
            return redirect('core:home')
            
    elif tipo_perfil == 'usuario':
        try:
            usuario = Usuario.objects.select_related('cidade', 'estado').get(user=user)
            experiencias = ExperienciaProfissional.objects.filter(usuario=usuario)
            cursos_extras = CursoExtraCurricular.objects.filter(usuario=usuario)
            idiomas = Idioma.objects.filter(usuario=usuario)
            
            # Carregar cidades do estado selecionado
            if usuario.estado:
                contexto['cidades'] = Cidade.objects.filter(estado_cidade=usuario.estado).order_by('nome_cidade')
            
            contexto.update({
                'usuario': usuario,
                'experiencias': experiencias,
                'cursos_extras': cursos_extras,
                'idiomas': idiomas,
            })
        except Usuario.DoesNotExist:
            messages.error(request, 'Perfil de usuário não encontrado.')
            return redirect('core:home')
    
    # Admin não precisa de dados extras (usa apenas user)
    
    return render(request, 'perfil.html', contexto)


@login_required
def atualizarPerfil(request):
    """
    View para atualizar o perfil do usuário logado.
    Processa o formulário POST e atualiza os dados no banco.
    """
    if request.method != 'POST':
        return redirect('core:perfil')
    
    user = request.user
    tipo_perfil = request.session.get('perfil', 'admin')
    
    # Verificar se é apenas upload de foto
    apenas_foto = request.POST.get('apenas_foto') == '1'
    
    try:
        # Atualizar foto do perfil (comum a todos)
        if 'foto' in request.FILES:
            foto = request.FILES['foto']
            # Validar extensão
            ext = foto.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png']:
                user.foto = foto
                user.save()
                
                # Se for apenas foto, retorna aqui
                if apenas_foto:
                    messages.success(request, 'Foto atualizada com sucesso!')
                    return redirect('core:perfil')
        
        # Atualizar nome (comum a todos)
        if request.POST.get('nome'):
            user.nome = request.POST.get('nome')
        
        user.save()
        
        # Atualizar dados específicos por tipo de perfil
        if tipo_perfil == 'admin':
            # Admin só atualiza dados básicos
            messages.success(request, 'Perfil atualizado com sucesso!')
            
        elif tipo_perfil == 'empresa':
            _atualizar_empresa(request, user)
            messages.success(request, 'Perfil da empresa atualizado com sucesso!')
            
        elif tipo_perfil == 'usuario':
            _atualizar_usuario(request, user)
            messages.success(request, 'Perfil atualizado com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Erro ao atualizar perfil: {str(e)}')
    
    return redirect('core:perfil')


def _atualizar_empresa(request, user):
    """
    Função auxiliar para atualizar dados da empresa.
    """
    empresa = Empresa.objects.get(user=user)
    
    # Dados da empresa
    empresa.nomefantasia = request.POST.get('nomefantasia', empresa.nomefantasia)
    empresa.razao_social = request.POST.get('razao_social', empresa.razao_social)
    empresa.cnpj = request.POST.get('cnpj', empresa.cnpj)
    empresa.tipo_empresa = request.POST.get('tipo_empresa', empresa.tipo_empresa)
    empresa.segmento = request.POST.get('segmento', empresa.segmento)
    empresa.telefone = request.POST.get('telefone', empresa.telefone)
    
    # Endereço
    empresa.cep = request.POST.get('cep', empresa.cep)
    empresa.rua = request.POST.get('rua', empresa.rua)
    empresa.numero = request.POST.get('numero', empresa.numero) or 0
    empresa.complemento = request.POST.get('complemento', empresa.complemento)
    
    # Cidade e Estado
    estado_id = request.POST.get('estado')
    cidade_id = request.POST.get('cidade')
    
    if estado_id:
        empresa.estado = Estado.objects.get(id=estado_id)
    if cidade_id:
        empresa.cidade = Cidade.objects.get(id=cidade_id)
    
    empresa.save()
    
    # Atualizar hubs vinculados
    _atualizar_hubs_empresa(request, empresa)


def _atualizar_hubs_empresa(request, empresa):
    """
    Atualiza os hubs vinculados à empresa.
    Remove vínculos antigos e cria novos conforme seleção.
    """
    # Pegar os IDs dos hubs selecionados no formulário
    hubs_selecionados = request.POST.getlist('hubs')
    
    # Converter para inteiros
    hubs_selecionados_ids = [int(h) for h in hubs_selecionados if h]
    
    # Remover todos os vínculos atuais
    EmpresaHub.objects.filter(empresa=empresa).delete()
    
    # Criar novos vínculos
    for hub_id in hubs_selecionados_ids:
        try:
            hub = Hub.objects.get(id=hub_id)
            EmpresaHub.objects.create(empresa=empresa, hub=hub)
        except Hub.DoesNotExist:
            pass  # Ignorar hub inválido


def _atualizar_usuario(request, user):
    """
    Função auxiliar para atualizar dados do usuário (candidato).
    """
    usuario = Usuario.objects.get(user=user)
    
    # Informações pessoais
    usuario.nome_social = request.POST.get('nome_social') or None
    usuario.data_nascimento = _parse_date(request.POST.get('data_nascimento')) or usuario.data_nascimento
    usuario.genero = request.POST.get('genero', usuario.genero)
    usuario.estado_civil = request.POST.get('estado_civil', usuario.estado_civil)
    usuario.nacionalidade = request.POST.get('nacionalidade', usuario.nacionalidade)
    usuario.telefone = request.POST.get('telefone', usuario.telefone)
    
    # Endereço
    usuario.cep = request.POST.get('cep', usuario.cep)
    usuario.rua = request.POST.get('rua', usuario.rua)
    usuario.bairro = request.POST.get('bairro', usuario.bairro)
    usuario.numero = request.POST.get('numero', usuario.numero)
    usuario.complemento = request.POST.get('complemento') or None
    
    # Cidade e Estado
    estado_id = request.POST.get('estado')
    cidade_id = request.POST.get('cidade')
    
    if estado_id:
        usuario.estado = Estado.objects.get(id=estado_id)
    if cidade_id:
        usuario.cidade = Cidade.objects.get(id=cidade_id)
    
    # Objetivo profissional
    usuario.cargo_pretendido = request.POST.get('cargo_pretendido') or None
    usuario.area_interesse = request.POST.get('area_interesse') or None
    usuario.pretensao_salarial = _parse_decimal(request.POST.get('pretensao_salarial'))
    usuario.disponibilidade = request.POST.get('disponibilidade') or None
    usuario.remoto = request.POST.get('remoto') == 'on'
    
    # Redes sociais
    usuario.linkedin = request.POST.get('linkedin') or None
    usuario.github = request.POST.get('github') or None
    usuario.instagram = request.POST.get('instagram') or None
    usuario.facebook = request.POST.get('facebook') or None
    usuario.site_pessoal = request.POST.get('site_pessoal') or None
    
    # Formação acadêmica 1
    usuario.instituicao_nome1 = request.POST.get('instituicao_nome1') or None
    usuario.grau_escolaridade1 = request.POST.get('grau_escolaridade1') or None
    usuario.curso_graduacao1 = request.POST.get('curso_graduacao1') or None
    usuario.situacao_academica1 = request.POST.get('situacao_academica1') or None
    usuario.data_acad_inicio1 = _parse_date(request.POST.get('data_acad_inicio1'))
    usuario.data_acad_fim1 = _parse_date(request.POST.get('data_acad_fim1'))
    
    # Formação acadêmica 2
    usuario.instituicao_nome2 = request.POST.get('instituicao_nome2') or None
    usuario.grau_escolaridade2 = request.POST.get('grau_escolaridade2') or None
    usuario.curso_graduacao2 = request.POST.get('curso_graduacao2') or None
    usuario.situacao_academica2 = request.POST.get('situacao_academica2') or None
    usuario.data_acad_inicio2 = _parse_date(request.POST.get('data_acad_inicio2'))
    usuario.data_acad_fim2 = _parse_date(request.POST.get('data_acad_fim2'))
    
    # Formação acadêmica 3
    usuario.instituicao_nome3 = request.POST.get('instituicao_nome3') or None
    usuario.grau_escolaridade3 = request.POST.get('grau_escolaridade3') or None
    usuario.curso_graduacao3 = request.POST.get('curso_graduacao3') or None
    usuario.situacao_academica3 = request.POST.get('situacao_academica3') or None
    usuario.data_acad_inicio3 = _parse_date(request.POST.get('data_acad_inicio3'))
    usuario.data_acad_fim3 = _parse_date(request.POST.get('data_acad_fim3'))
    
    # Competências 1
    usuario.competencias_tecnicas1 = request.POST.get('competencias_tecnicas1') or None
    usuario.competencias_comportamentais1 = request.POST.get('competencias_comportamentais1') or None
    
    # Competências 2
    usuario.competencias_tecnicas2 = request.POST.get('competencias_tecnicas2') or None
    usuario.competencias_comportamentais2 = request.POST.get('competencias_comportamentais2') or None
    
    # Competências 3
    usuario.competencias_tecnicas3 = request.POST.get('competencias_tecnicas3') or None
    usuario.competencias_comportamentais3 = request.POST.get('competencias_comportamentais3') or None
    
    # Inclusão e acessibilidade
    usuario.pessoa_com_deficiencia = request.POST.get('pessoa_com_deficiencia') == 'on'
    usuario.tipo_deficiencia = request.POST.get('tipo_deficiencia') or None
    usuario.necessidade_adaptacao = request.POST.get('necessidade_adaptacao') or None
    
    # Informações adicionais
    usuario.interesses_hobbies = request.POST.get('interesses_hobbies') or None
    
    # Anexos
    if 'curriculo_pdf' in request.FILES:
        usuario.curriculo_pdf = request.FILES['curriculo_pdf']
    if 'carta_apresentacao' in request.FILES:
        usuario.carta_apresentacao = request.FILES['carta_apresentacao']
    
    usuario.save()
    
    # Atualizar experiências profissionais
    _atualizar_experiencias(request, usuario)
    
    # Atualizar cursos extracurriculares
    _atualizar_cursos(request, usuario)
    
    # Atualizar idiomas
    _atualizar_idiomas(request, usuario)


def _atualizar_experiencias(request, usuario):
    """
    Atualiza ou cria experiências profissionais do usuário.
    """
    # Buscar ou criar o registro de experiência
    experiencia, created = ExperienciaProfissional.objects.get_or_create(usuario=usuario)
    
    # Experiência 1
    experiencia.nome_empresa1 = request.POST.get('nome_empresa1') or None
    experiencia.cargo1 = request.POST.get('cargo1') or None
    experiencia.data_inicio1 = _parse_date(request.POST.get('data_inicio1'))
    experiencia.data_fim1 = _parse_date(request.POST.get('data_fim1'))
    
    # Experiência 2
    experiencia.nome_empresa2 = request.POST.get('nome_empresa2') or None
    experiencia.cargo2 = request.POST.get('cargo2') or None
    experiencia.data_inicio2 = _parse_date(request.POST.get('data_inicio2'))
    experiencia.data_fim2 = _parse_date(request.POST.get('data_fim2'))
    
    # Experiência 3
    experiencia.nome_empresa3 = request.POST.get('nome_empresa3') or None
    experiencia.cargo3 = request.POST.get('cargo3') or None
    experiencia.data_inicio3 = _parse_date(request.POST.get('data_inicio3'))
    experiencia.data_fim3 = _parse_date(request.POST.get('data_fim3'))
    
    experiencia.save()


def _atualizar_cursos(request, usuario):
    """
    Atualiza ou cria cursos extracurriculares do usuário.
    """
    curso, created = CursoExtraCurricular.objects.get_or_create(usuario=usuario)
    
    # Curso 1
    curso.nome_curso1 = request.POST.get('nome_curso1') or None
    curso.instituicao1 = request.POST.get('instituicao1') or None
    curso.carga_horaria1 = _parse_int(request.POST.get('carga_horaria1'))
    curso.data_conclusao1 = _parse_date(request.POST.get('data_conclusao1'))
    curso.link_certificado1 = request.POST.get('link_certificado1') or None
    
    # Curso 2
    curso.nome_curso2 = request.POST.get('nome_curso2') or None
    curso.instituicao2 = request.POST.get('instituicao2') or None
    curso.carga_horaria2 = _parse_int(request.POST.get('carga_horaria2'))
    curso.data_conclusao2 = _parse_date(request.POST.get('data_conclusao2'))
    curso.link_certificado2 = request.POST.get('link_certificado2') or None
    
    # Curso 3
    curso.nome_curso3 = request.POST.get('nome_curso3') or None
    curso.instituicao3 = request.POST.get('instituicao3') or None
    curso.carga_horaria3 = _parse_int(request.POST.get('carga_horaria3'))
    curso.data_conclusao3 = _parse_date(request.POST.get('data_conclusao3'))
    curso.link_certificado3 = request.POST.get('link_certificado3') or None
    
    curso.save()


def _atualizar_idiomas(request, usuario):
    """
    Atualiza ou cria idiomas do usuário.
    """
    idioma, created = Idioma.objects.get_or_create(usuario=usuario)
    
    # Idioma 1
    idioma.idioma1 = request.POST.get('idioma1') or None
    idioma.nivel_fluencia1 = request.POST.get('nivel_fluencia1') or None
    
    # Idioma 2
    idioma.idioma2 = request.POST.get('idioma2') or None
    idioma.nivel_fluencia2 = request.POST.get('nivel_fluencia2') or None
    
    # Idioma 3
    idioma.idioma3 = request.POST.get('idioma3') or None
    idioma.nivel_fluencia3 = request.POST.get('nivel_fluencia3') or None
    
    idioma.save()


# =============================================
# FUNÇÕES AUXILIARES DE PARSING
# =============================================

def _parse_date(date_str):
    """
    Converte string de data para objeto date.
    Retorna None se a conversão falhar.
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None


def _parse_decimal(value_str):
    """
    Converte string para Decimal.
    Retorna None se a conversão falhar.
    """
    if not value_str:
        return None
    try:
        return Decimal(value_str)
    except (InvalidOperation, ValueError):
        return None


def _parse_int(value_str):
    """
    Converte string para int.
    Retorna None se a conversão falhar.
    """
    if not value_str:
        return None
    try:
        return int(value_str)
    except ValueError:
        return None


# =============================================
# API AJAX PARA CIDADES
# =============================================

def buscar_cidades(request):
    """
    API para buscar cidades por estado via AJAX.
    Retorna JSON com lista de cidades.
    """
    estado_id = request.GET.get('estado_id')
    
    if not estado_id:
        return JsonResponse({'cidades': []})
    
    try:
        cidades = Cidade.objects.filter(estado_cidade_id=estado_id).order_by('nome_cidade')
        cidades_list = [{'id': c.id, 'nome': c.nome_cidade} for c in cidades]
        return JsonResponse({'cidades': cidades_list})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
