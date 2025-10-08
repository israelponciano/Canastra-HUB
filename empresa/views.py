from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from empresa.models import *
from core.models import *
from django.contrib import messages
from django.http import JsonResponse

import re


def limpar_numeros(valor):
    # Remove tudo que não for dígito
    return re.sub(r'\D', '', valor)


def cadastro_empresa(request):
    estados = Estado.objects.all().order_by('nome_estado')
    hubs = Hub.objects.all().order_by('nome_hub')

    return render(request, 'cadastro_empresa.html', {
        'estados': estados,
        'hubs': hubs
    })


def criar_empresa(request):
    if request.user.is_authenticated:
        messages.warning(
            request, f'Você ja está logado, não é possivel realizar outro cadastro.')
        return redirect('core:home')
    if request.method == 'POST':
        nomefantasia = request.POST.get('txtNome')
        email = request.POST.get('txtEmail')
        senha = request.POST.get('txtSenha')
        segmento = request.POST.get('txtSegmento')
        tipo_empresa = request.POST.get('txtTipo')
        telefone = limpar_numeros(request.POST.get('txtTelefone'))
        rua = request.POST.get('txtRua')
        cep = limpar_numeros(request.POST.get('txtCep'))
        numero = request.POST.get('txtNumero')
        complemento = request.POST.get('txtComplemento')
        cidade_id = request.POST.get('cidade')
        estado_id = request.POST.get('estado')

        # CORREÇÃO: Pega a lista de hubs, não apenas um. O nome deve ser 'hubs'
        hubs_selecionados_ids = request.POST.getlist('hubs[]')

        print(f"hubs selecionados {hubs_selecionados_ids}")

        foto_empresa = request.FILES.get('fileFoto')
        cnpj = limpar_numeros(request.POST.get('txtCnpj'))
        razao_social = request.POST.get('txtRazaoSocial')

        # Validar se estado e cidade existem
        if not Estado.objects.filter(id=estado_id).exists():
            messages.error(request, 'Estado inválido.')
            estados = Estado.objects.all().order_by('nome_estado')
            hubs = Hub.objects.all().order_by('nome_hub')
            return render(request, 'cadastro_empresa.html', {'estados': estados, 'hubs': hubs})

        if not Cidade.objects.filter(id=cidade_id).exists():
            messages.error(request, 'Cidade inválida.')
            estados = Estado.objects.all().order_by('nome_estado')
            hubs = Hub.objects.all().order_by('nome_hub')
            return render(request, 'cadastro_empresa.html', {'estados': estados, 'hubs': hubs})

        # Buscar os objetos Estado e Cidade no banco
        estado = Estado.objects.get(id=estado_id)
        cidade = Cidade.objects.get(id=cidade_id)

        # Criar usuário
        user = UsuarioBase.objects.create_user(
            email=email,
            password=senha,
            nome=nomefantasia,
            tipo='empresa'
        )

        user.foto = foto_empresa
        user.save()

        # Criar empresa
        empresa = Empresa.objects.create(
            user=user,
            nomefantasia=nomefantasia,
            tipo_empresa=tipo_empresa,
            razao_social=razao_social,
            cnpj=cnpj,
            telefone=telefone,
            rua=rua,
            cep=cep,
            numero=numero,
            complemento=complemento,
            cidade=cidade,
            estado=estado,
            segmento=segmento
        )

        # CORREÇÃO: Associa todos os hubs de uma só vez usando o método set()
        if hubs_selecionados_ids == '' or hubs_selecionados_ids is None:
            empresa.hubs.set(hubs_selecionados_ids)

        messages.success(request, 'Empresa cadastrada com sucesso!')
        return redirect('core:login')

    # GET request - carregar página com dados do banco
    estados = Estado.objects.all().order_by('nome_estado')
    hubs = Hub.objects.all().order_by('nome_hub')
    return render(request, 'cadastro_empresa.html', {'estados': estados, 'hubs': hubs})


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


@require_http_methods(["GET"])
def get_hubs(request):
    """View para retornar todos os hubs disponíveis"""
    hubs = Hub.objects.all().order_by('nome_hub').values('id', 'nome_hub', 'descricao')

    hubs_data = [
        {
            'id': hub['id'],
            'nome': hub['nome_hub'],
            'descricao': hub['descricao'] if hub['descricao'] else ''
        }
        for hub in hubs
    ]

    return JsonResponse({
        'hubs': hubs_data,
        'total': len(hubs_data)
    })
