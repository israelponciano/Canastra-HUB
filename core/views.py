from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from core.models import *
from empresa.models import *
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from datetime import datetime

from treinamento.models import Treinamento
from vagas.models import Vagas
from eventos.models import Evento


def _parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def home(request):
    # Buscar notícias ativas que devem aparecer na home
    noticias_home = NoticiaHub.objects.filter(
        noticia__isActive=True,
        noticia__isHome=True
    ).select_related('noticia', 'hub').order_by('-noticia__id')[:5]  # Limitando a 10 notícias
    
    return render(request, 'home.html', {
        'noticias_home': noticias_home
    })

def parceiros(request):

    return render(request, 'parceiros.html')

def hubs(request):
    """View para a central de hubs"""
    hubs = Hub.objects.filter(isActive=True)
    return render(request, 'hubs.html', {'hubs': hubs})

def hub_detalhe(request, nome_hub):
    """View dinâmica para cada hub"""
    hub = get_object_or_404(Hub, nome_hub=nome_hub, isActive=True)
    
    # Buscar notícias relacionadas ao hub
    noticias = NoticiaHub.objects.filter(
        hub=hub, 
        noticia__isActive=True
    ).select_related('noticia')

    eventos = Evento.objects.filter(
        hub=hub
    ).order_by('-id')

    vagas = Vagas.objects.filter(
        hub=hub
    ).order_by('-data_publicacao')

    #Treinamento  vinculado ao hub (novo app)
    treinamentos  = Treinamento.objects.filter(hub=hub).prefetch_related('sessoes').order_by('-id')

    #Empresas parceiras vinculadas ao hub
    empresas_hub = EmpresaHub.objects.filter(hub=hub).select_related('empresa__user')

    context = {
        'hub': hub,
        'noticias': noticias,
        'treinamentos': treinamentos,
        'vagas': vagas,
        'eventos': eventos,
        'empresas_hub': empresas_hub
    }
    return render(request, 'hub.html', context)


def sobre(request):

    return render(request, 'sobre.html')

def espacos_hub(request):

    return render(request, 'espacos_hub.html')

def cadastro(request):

    return render(request, 'cadastro.html')

    # 4. Prepara o contexto
    contexto = {
        'eventos': eventos,
        'termo_busca': termo_busca,  # Passa o termo de volta para o input na tela
    }

    # 5. Renderiza o template de busca
    return render(request, 'tela_busca_eventos.html', contexto)

def render_cadastro_usuario(request):
    estados = Estado.objects.all().order_by('nome_estado')
    return render(request, 'cadastro_usuario.html', {'estados': estados})


def cadastro_usuario(request):
    if request.user.is_authenticated:
        messages.warning(
            request, 'Você já está logado, não é possível realizar outro cadastro.')
        return redirect('core:home')

    estados = Estado.objects.all().order_by('nome_estado')

    if request.method == 'POST':
        nome_user = request.POST.get('txtNome')

        if not nome_user or not nome_user.strip():
            messages.error(request, 'O nome é obrigatório.')
            return render(request, 'cadastro_usuario.html', {'estados': estados})

        if len(nome_user.strip()) < 3:
            messages.error(request, 'O nome deve possuir no mínimo 3 caracteres.')
            return render(request, 'cadastro_usuario.html', {'estados': estados})

        senha = request.POST.get('txtSenha')
        confirmacao_senha = request.POST.get('confirmar_Senha')
        if senha != confirmacao_senha:
            messages.error(request, 'As senhas devem ser iguais.')
            return render(request, 'cadastro_usuario.html', {'estados': estados})

        nome_social = request.POST.get('txtNomeSocial')
        data_nasc = _parse_date(request.POST.get('txtDataNasc'))
        genero = request.POST.get('txtGenero') or ''
        estado_civil = request.POST.get('txtEstadoCivil') or ''
        nacionalidade = request.POST.get('txtNacionalidade') or ''
        email = request.POST.get('txtEmail')
        telefone = request.POST.get('txtTelefone') or ''
        foto_user = request.FILES.get('fileFoto')
        cep = request.POST.get('txtCep') or ''
        rua = request.POST.get('txtRua') or ''
        numero = request.POST.get('txtNumero') or ''
        bairro = request.POST.get('txtBairro') or ''
        complemento = request.POST.get('txtComplemento') or ''

        cidade_id = request.POST.get('cidade')
        estado_id = request.POST.get('estado')
        if not cidade_id:
            messages.error(request, 'Selecione uma cidade.')
            return render(request, 'cadastro_usuario.html', {'estados': estados})

        if not estado_id:
            messages.error(request, 'Selecione um estado.')
            return render(request, 'cadastro_usuario.html', {'estados': estados})

        if not Estado.objects.filter(id=estado_id).exists():
            messages.error(request, 'Estado inválido.')
            return render(request, 'cadastro_usuario.html', {'estados': estados})

        if not Cidade.objects.filter(id=cidade_id).exists():
            messages.error(request, 'Cidade inválida.')
            return render(request, 'cadastro_usuario.html', {'estados': estados})

        estado = Estado.objects.get(id=estado_id)
        cidade = Cidade.objects.get(id=cidade_id)

        if not data_nasc:
            messages.error(request, 'Informe a data de nascimento.')
            return render(request, 'cadastro_usuario.html', {'estados': estados})

        user = UsuarioBase.objects.create_user(
            email=email,
            password=senha,
            nome=nome_user,
            tipo='usuario'
        )
        if foto_user:
            user.foto = foto_user
            user.save()

        endereco = Endereco.objects.create(
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            complemento=complemento,
            cidade=cidade,
            estado=estado,
        )

        usuario = Usuario.objects.create(
            user=user,
            nome_social=nome_social or None,
            data_nascimento=data_nasc,
            genero=genero,
            estado_civil=estado_civil,
            nacionalidade=nacionalidade,
            telefone=telefone,
            endereco=endereco,
        )
        request.session['usuario_email'] = usuario.user.email

        messages.success(request, 'Cadastro inicial realizado! Complete seu perfil profissional!')
        return redirect('core:login')

    return render(request, 'cadastro_usuario.html', {'estados': estados})

def cadastro_completo(request):
    usuario_email = request.session.get('usuario_email') or request.session.get('email_atual')
    if not usuario_email:
        messages.error(request, 'Você deve realizar o cadastro inicial primeiro!')
        return redirect('core:cadastro_usuario')

    usuario = Usuario.objects.select_related('user').filter(user__email=usuario_email).first()
    if not usuario:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('core:cadastro_usuario')

    if request.method == 'POST':
        request.session['incompleto'] = False

        nome_social = request.POST.get('nome_social') or request.POST.get('txtNomeSocial') or None
        data_nascimento = _parse_date(request.POST.get('data_nascimento') or request.POST.get('txtDataNasc'))
        genero = request.POST.get('genero') or request.POST.get('txtGenero') or usuario.genero
        estado_civil = request.POST.get('estado_civil') or request.POST.get('txtEstadoCivil') or usuario.estado_civil
        nacionalidade = request.POST.get('nacionalidade') or request.POST.get('txtNacionalidade') or usuario.nacionalidade
        telefone = request.POST.get('telefone') or request.POST.get('txtTelefone') or usuario.telefone

        usuario.nome_social = nome_social
        usuario.data_nascimento = data_nascimento or usuario.data_nascimento
        usuario.genero = genero
        usuario.estado_civil = estado_civil
        usuario.nacionalidade = nacionalidade
        usuario.telefone = telefone
        usuario.save()

        endereco = usuario.endereco or Endereco()
        estado_id = request.POST.get('estado') or request.POST.get('estado_id')
        cidade_id = request.POST.get('cidade') or request.POST.get('cidade_id')
        endereco.cep = request.POST.get('cep') or request.POST.get('txtCep') or (endereco.cep or '')
        endereco.rua = request.POST.get('rua') or request.POST.get('txtRua') or (endereco.rua or '')
        endereco.bairro = request.POST.get('bairro') or request.POST.get('txtBairro') or (endereco.bairro or '')
        endereco.numero = request.POST.get('numero') or request.POST.get('txtNumero') or (endereco.numero or '')
        endereco.complemento = request.POST.get('complemento') or request.POST.get('txtComplemento') or (endereco.complemento or '')

        if estado_id:
            endereco.estado = Estado.objects.get(id=estado_id)
        if cidade_id:
            endereco.cidade = Cidade.objects.get(id=cidade_id)

        if endereco.estado and endereco.cidade:
            endereco.save()
            usuario.endereco = endereco
            usuario.save()

        objetivo = usuario.objetivo_profissional or ProfessionalTarget.objects.create()
        objetivo.cargo_pretendido = request.POST.get('cargo_pretendido') or request.POST.get('txtCargoPretendido') or None
        objetivo.area_interesse = request.POST.get('area_interesse') or request.POST.get('txtAreaInteresse') or None
        objetivo.pretensao_salarial = _parse_decimal(request.POST.get('pretensao_salarial') or request.POST.get('decPretensaoSalarial'))
        objetivo.disponibilidade = request.POST.get('disponibilidade') or request.POST.get('txtDisponibilidade') or None
        objetivo.remoto = request.POST.get('remoto') == 'sim' or request.POST.get('remoto') == 'on'
        objetivo.save()
        usuario.objetivo_profissional = objetivo
        usuario.save()

        formacao = usuario.formacao_academica or AcademyGraduation.objects.create()
        for index in ('1', '2', '3'):
            instituicao = request.POST.get(f'instituicao_nome{index}') or request.POST.get(f'txtNomeInstituicao{index}')
            grau = request.POST.get(f'grau_escolaridade{index}') or request.POST.get(f'escolaridade{index}')
            curso = request.POST.get(f'curso_graduacao{index}') or request.POST.get(f'txtCurso{index}')
            situacao = request.POST.get(f'situacao_academica{index}') or request.POST.get(f'txtSituacao{index}')
            data_inicio = _parse_date(request.POST.get(f'data_acad_inicio{index}') or request.POST.get(f'txtDataAcad{index}'))
            data_fim = _parse_date(request.POST.get(f'data_acad_fim{index}') or request.POST.get(f'txtDataFimAcad{index}'))

            if any([instituicao, grau, curso, situacao, data_inicio, data_fim]):
                formacao.instituicao_nome = instituicao or formacao.instituicao_nome
                formacao.grau_escolaridade = grau or formacao.grau_escolaridade
                formacao.curso_graduacao = curso or formacao.curso_graduacao
                formacao.situacao_academica = situacao or formacao.situacao_academica
                formacao.data_acad_inicio = data_inicio or formacao.data_acad_inicio
                formacao.data_acad_fim = data_fim or formacao.data_acad_fim
                break

        formacao.save()
        usuario.formacao_academica = formacao
        usuario.save()

        social = usuario.social_media or SocialMedia.objects.create()
        social.linkedin = request.POST.get('linkedin') or request.POST.get('txtLinkedin') or None
        social.github = request.POST.get('github') or request.POST.get('txtGithub') or None
        social.instagram = request.POST.get('instagram') or request.POST.get('txtInstagram') or None
        social.facebook = request.POST.get('facebook') or request.POST.get('txtFacebook') or None
        social.site_pessoal = request.POST.get('site_pessoal') or request.POST.get('txtSitePessoal') or None
        social.save()
        usuario.social_media = social
        usuario.save()

        usuario.competencias.clear()
        for raw_value in [request.POST.get('skills'), request.POST.get('competencias')]:
            if raw_value:
                for item in [part.strip() for part in raw_value.split(',') if part.strip()]:
                    competencia, _ = Competencia.objects.get_or_create(
                        nome_competencia=item,
                        defaults={'tipo_competencia': 'tecnica'}
                    )
                    usuario.competencias.add(competencia)

        for index in ('1', '2', '3'):
            tecnica = request.POST.get(f'txtHardSkil{index}') or request.POST.get(f'competencias_tecnicas{index}')
            comportamental = request.POST.get(f'txtSoftSkil{index}') or request.POST.get(f'competencias_comportamentais{index}')
            for raw_value, tipo_competencia in ((tecnica, 'tecnica'), (comportamental, 'comportamental')):
                if raw_value:
                    for item in [part.strip() for part in raw_value.split(',') if part.strip()]:
                        competencia, _ = Competencia.objects.get_or_create(
                            nome_competencia=item,
                            defaults={'tipo_competencia': tipo_competencia}
                        )
                        usuario.competencias.add(competencia)

        usuario.interesses_hobbies.clear()
        for raw_value in [request.POST.get('interesses_hobbies') or request.POST.get('txtHobbie')]:
            if raw_value:
                for item in [part.strip() for part in raw_value.split(',') if part.strip()]:
                    hobby, _ = Hobby.objects.get_or_create(nome_hobby=item)
                    usuario.interesses_hobbies.add(hobby)

        acessibilidade = usuario.acessibilidade or Acessibilidade.objects.create(usuario=usuario)
        acessibilidade.pessoa_com_deficiencia = request.POST.get('pcd') == 'sim' or request.POST.get('pessoa_com_deficiencia') == 'on'
        acessibilidade.tipo_deficiencia = request.POST.get('tipoDeficiencia') or request.POST.get('tipo_deficiencia') or None
        acessibilidade.necessidade_adaptacao = request.POST.get('necessidadeAdaptacao') or request.POST.get('necessidade_adaptacao') or None
        acessibilidade.save()

        if request.FILES.get('curriculoPdf'):
            Attachment.objects.filter(usuario=usuario, description='curriculo').delete()
            Attachment.objects.create(usuario=usuario, file=request.FILES['curriculoPdf'], description='curriculo')
        if request.FILES.get('cartaApresentacao'):
            Attachment.objects.filter(usuario=usuario, description='carta_apresentacao').delete()
            Attachment.objects.create(usuario=usuario, file=request.FILES['cartaApresentacao'], description='carta_apresentacao')

        ExperienciaProfissional.objects.filter(usuario=usuario).delete()
        for index in ('1', '2', '3'):
            nome_empresa = request.POST.get(f'txtNomeEmpresa{index}') or request.POST.get(f'nome_empresa{index}')
            cargo = request.POST.get(f'txtCargo{index}') or request.POST.get(f'cargo{index}')
            data_inicio = _parse_date(request.POST.get(f'txtDataProf{index}') or request.POST.get(f'data_inicio{index}'))
            data_fim = _parse_date(request.POST.get(f'txtDataFimProf{index}') or request.POST.get(f'data_fim{index}'))
            if any([nome_empresa, cargo, data_inicio, data_fim]):
                ExperienciaProfissional.objects.create(
                    usuario=usuario,
                    nome_empresa=nome_empresa or None,
                    cargo=cargo or None,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                )

        CursoExtraCurricular.objects.filter(usuario=usuario).delete()
        for index in ('1', '2', '3'):
            nome_curso = request.POST.get(f'txtNomeCurso{index}') or request.POST.get(f'nome_curso{index}')
            instituicao = request.POST.get(f'txtInstituicao{index}') or request.POST.get(f'instituicao{index}')
            carga_horaria = request.POST.get(f'txtCargaHoras{index}') or request.POST.get(f'carga_horaria{index}')
            data_conclusao = _parse_date(request.POST.get(f'txtDataFimCurso{index}') or request.POST.get(f'data_conclusao{index}'))
            link_certificado = request.POST.get(f'txtLinkCertificado{index}') or request.POST.get(f'link_certificado{index}')
            if any([nome_curso, instituicao, carga_horaria, data_conclusao, link_certificado]):
                CursoExtraCurricular.objects.create(
                    usuario=usuario,
                    nome_curso=nome_curso or None,
                    instituicao=instituicao or None,
                    carga_horaria=int(carga_horaria) if carga_horaria else None,
                    data_conclusao=data_conclusao,
                    link_certificado=link_certificado or None,
                )

        Idioma.objects.filter(usuario=usuario).delete()
        for index in ('1', '2', '3'):
            language = request.POST.get(f'txtIdioma{index}') or request.POST.get(f'idioma{index}')
            fluency = request.POST.get(f'fluencia{index}') or request.POST.get(f'nivel_fluencia{index}')
            if language:
                Idioma.objects.create(usuario=usuario, language=language, fluency=fluency)

        messages.success(request, 'Cadastro realizado com sucesso!')
        return render(request, 'home.html')

    estados = Estado.objects.all().order_by('nome_estado')
    return render(request, 'cadastro_usuario_completo.html', {'estados': estados})



def login(request):
    if request.method == 'POST':
        email = request.POST.get('txtEmail')
        senha = request.POST.get('txtSenha')

        usuario = authenticate(request, username=email, password=senha)
        
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
