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
        messages.success(request, 'Usuario cadastrado com sucesso!')
        return redirect('core:login')

    estados = Estado.objects.all().order_by('nome_estado')
    return render(request, 'cadastro_usuario.html', {'estados': estados})


def cadastro_completo(request):

    return render(request, 'cadastro_usuario_completo.html')


def login(request):
    print("CHEGOU LOGIN")
    if request.method == 'POST':
        print("Chegou POST")
        email = request.POST.get('txtEmail')
        senha = request.POST.get('txtSenha')
        # perfil_id = request.POST.get('slcPerfil')

        print(email, senha)

        usuario = authenticate(request, username=email, password=senha)
        print(usuario)
        # if usuario is not None and perfil_id:
        if usuario is not None:
            # perfis_usuario = usuario.perfis.filter(id=perfil_id)
            # if perfis_usuario.exists():
            # limpa as sessoes do usuario
            request.session.flush()
            # cria a sessao do usuario
            auth_login(request, usuario)

            request.session['is_login'] = False
            if usuario.is_admin:
                request.session['is_admin'] = usuario.is_admin
            # print(request.session['is_admin'])
            request.session['perfil'] = usuario.tipo
            request.session['id_atual'] = usuario.id
            request.session['email_atual'] = usuario.email
            # request.session['perfil_atual'] = perfis_usuario.first().nome
            # request.session['perfis'] = list(usuario.perfis.values_list('nome', flat=True))
            # print(request.session['perfis'])

            # configura sessao para expirar em 4 horas
            request.session.set_expiry(14400)

            messages.success(request, 'Login realizado com sucesso!')

            # no futuro iremos separar em diferentes paginas
            # if request.session.get('perfil_atual') in {'Administrador', 'Funcionario'}:
            return redirect('core:home')

            # else:
            #     messages.error(request, 'Perfil inválido para este usuário.')
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
