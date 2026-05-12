from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from empresa.models import *
from core.models import *
from django.contrib import messages
from django.http import JsonResponse

import re

def validar_email(email: str) -> bool:
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None


def limpar_numeros(valor):
    # Remove tudo que não for dígito
    return re.sub(r'\D', '', valor)

def _get_contexto_cadastro():
    """Retorna o contexto padrão para renderizar o formulário de cadastro."""
    return {
        'estados': Estado.objects.all().order_by('nome_estado'),
        'hubs': Hub.objects.all().order_by('nome_hub'),
        'complemento_max_length': Empresa._meta.get_field('complemento').max_length,
    }

def _erro_cadastro(request, mensagens:list | str):
    """Atalho para adicionar erro e retornar o formulário com contexto."""
    
    if isinstance(mensagens,str):
        mensagens = [mensagens]

    for mensagem in mensagens:
        messages.error(request, mensagem)
    
    return render(request, 'cadastro_empresa.html', _get_contexto_cadastro())


def cadastro_empresa(request):
    return render(request, 'cadastro_empresa.html', _get_contexto_cadastro())


def criar_empresa(request):
    
    if request.user.is_authenticated:
        messages.warning(
            request, f'Você ja está logado, não é possivel realizar outro cadastro.')
        return redirect('core:home')
    
    if request.method != 'POST':
        return render(request, 'cadastro_empresa.html', _get_contexto_cadastro())

    nomefantasia = request.POST.get('txtNome', '').strip()
    email = request.POST.get('txtEmail', '').strip()
    senha = request.POST.get('txtSenha', '').strip()
    segmento = request.POST.get('txtSegmento', '').strip()
    tipo_empresa = request.POST.get('txtTipo', '').strip()
    telefone = limpar_numeros(request.POST.get('txtTelefone'))
    rua = request.POST.get('txtRua', '').strip()
    cep = limpar_numeros(request.POST.get('txtCep'))
    numero_raw = request.POST.get('txtNumero', '').strip()
    complemento = request.POST.get('txtComplemento', '').strip()
    cidade_id = request.POST.get('cidade', '').strip()
    estado_id = request.POST.get('estado', '').strip()
    hubs_selecionados = request.POST.getlist('hubs[]')
    foto_empresa = request.FILES.get('fileFoto')
    cnpj = limpar_numeros(request.POST.get('txtCnpj'))
    razao_social = request.POST.get('txtRazaoSocial', '').strip()

    campos_obrigatorios = {
        'Nome fantasia': nomefantasia,
        'E-mail': email,
        'Senha': senha,
        'Segmento': segmento,
        'Tipo de empresa': tipo_empresa,
        'Telefone': telefone,
        'Rua': rua,
        'CEP': cep,
        'Número': numero_raw,
        'Estado': estado_id,
        'Cidade': cidade_id,
        'CNPJ': cnpj,
        'Razão social': razao_social,
    }

    for nome_campo, valor in campos_obrigatorios.items():
        if not valor:
            return _erro_cadastro(request, f'O campo "{nome_campo}" é obrigatório.')

    if not validar_email(email):
        return _erro_cadastro(request, 'Endereço de e-mail inválido.')

    if len(senha) < 8:
        return _erro_cadastro(request, 'A senha deve ter pelo menos 8 caracteres.')

    if len(cnpj) != 14:
        return _erro_cadastro(request, 'CNPJ inválido — informe os 14 dígitos.')

    if len(telefone) < 10 or len(telefone) > 11:
        return _erro_cadastro(request, 'Telefone inválido — informe DDD + número.')

    if len(cep) != 8:
        return _erro_cadastro(request, 'CEP inválido — informe os 8 dígitos.')

    if not numero_raw.isdigit():
        return _erro_cadastro(request, 'O número do endereço deve ser numérico.')

    numero = int(numero_raw)

    complemento_max = Empresa._meta.get_field('complemento').max_length
    if len(complemento) > complemento_max:
        return _erro_cadastro(
            request,
            f'O complemento pode ter no máximo {complemento_max} caracteres.'
        )

    if not estado_id.isdigit() or not cidade_id.isdigit():
        return _erro_cadastro(request, 'Seleção de estado ou cidade inválida.')

    try:
        estado = Estado.objects.get(id=estado_id)
    except Estado.DoesNotExist:
        return _erro_cadastro(request, 'Estado selecionado não encontrado.')

    try:
        cidade = Cidade.objects.get(id=cidade_id, estado_cidade=estado)
    except Cidade.DoesNotExist:
        return _erro_cadastro(request, 'Cidade inválida ou não pertence ao estado selecionado.')

    hubs_validos = []
    if hubs_selecionados:
        ids_numericos = [h for h in hubs_selecionados if str(h).isdigit()]
        hubs_validos = list(Hub.objects.filter(id__in=ids_numericos))
        if len(hubs_validos) != len(ids_numericos):
            return _erro_cadastro(request, 'Um ou mais hubs selecionados são inválidos.')

    if UsuarioBase.objects.filter(email=email).exists():
        return _erro_cadastro(request, 'Já existe uma conta cadastrada com este e-mail.')

    if Empresa.objects.filter(cnpj=cnpj).exists():
        return _erro_cadastro(request, 'Já existe uma empresa cadastrada com este CNPJ.')

    user = UsuarioBase.objects.create_user(
        email=email,
        password=senha,
        nome=nomefantasia,
        tipo='empresa'
    )
    if foto_empresa:
        user.foto = foto_empresa
        user.save()

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
        segmento=segmento,
    )

    if hubs_validos:
        empresa.hubs.set(hubs_validos)

    messages.success(request, 'Empresa cadastrada com sucesso!')
    return redirect('core:login')

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

