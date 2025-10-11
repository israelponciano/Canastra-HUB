from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from empresa.models import *
from core.models import *
from vagas.models import * 
from django.contrib import messages
from django.http import JsonResponse

import re

def limpar_numeros(valor):
    # Remove tudo que não for dígito
    return re.sub(r'\D', '', valor)


def cadastro_vagas(request):
    estados = Estado.objects.all().order_by('nome_estado')
    return render(request, 'cadastro_vagas.html', {'estados': estados})

def criar_vagas(request):
    
    if request.method == 'POST':
        nomeEmpresa = request.POST.get('txtNomeEmpresa')
        cnpjEmpresa = limpar_numeros(request.POST.get('txtCnpjEmpresa'))
        cargo_vaga = request.POST.get('txtCargoVaga')
        descricao_vaga = request.POST.get('txtDescricao')
        cidade_id = request.POST.get('cidade')
        estado_id = request.POST.get('estado')
        requisito_vaga =request.POST.get('txtRequisito')
        curso = request.POST.get('txtCurso')

        # Validar se estado e cidade existem
        if not Estado.objects.filter(id=estado_id).exists():
            messages.error(request, 'Estado inválido.')
            estados = Estado.objects.all().order_by('nome_estado')
            return render(request, 'cadastro_vagas.html', {'estados': estados})

        if not Cidade.objects.filter(id=cidade_id).exists():
            messages.error(request, 'Cidade inválida.')
            estados = Estado.objects.all().order_by('nome_estado')
            return render(request, 'cadastro_vagas.html', {'estados': estados})

        # Buscar os objetos Estado e Cidade no banco
        estado = Estado.objects.get(id=estado_id)
        cidade = Cidade.objects.get(id=cidade_id)
        
        empresa = Empresa.objects.filter(nomefantasia=nomeEmpresa, cnpj=cnpjEmpresa).first()
        
        if not empresa:
            messages.error(request, f'Empresa "{nomeEmpresa}" com CNPJ {cnpjEmpresa} não encontrada.')
            estados = Estado.objects.all().order_by('nome_estado')
            return render(request, 'cadastro_vagas.html', {'estados': estados})
        
        # Criar empresa
        vagas = Vagas.objects.create(
            cargo_vaga=cargo_vaga,
            descricao_vaga=descricao_vaga,
            requisito_vaga=requisito_vaga,
            curso=curso,
            empresa=empresa, 
        )
        messages.success(request, 'Vaga cadastrada com sucesso!')
        return redirect('core:home')

    # GET request - carregar página com dados do banco
    estados = Estado.objects.all().order_by('nome_estado')
    empresas = Empresa.objects.all().order_by('nome_empresa')
    return render(request, 'cadastro_vagas.html', {
            'estados': estados,
            'empresas': empresas})

@require_http_methods(["GET"])
def get_cidades(request):
    """View para retornar cidades via AJAX baseado no estado selecionado"""
    estado_id = request.GET.get('estado_id')
    
    print(f"DEBUG: estado_id recebido = {estado_id}")

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

    # ✅ ForeignKey é 'estado_cidade'
    cidades = Cidade.objects.filter(estado_cidade_id=estado_id).order_by('nome_cidade')
    
    print(f"DEBUG: {cidades.count()} cidades encontradas")

    cidades_data = [
        {'id': cidade.id, 'nome': cidade.nome_cidade}
        for cidade in cidades
    ]

    return JsonResponse({
        'cidades': cidades_data,
        'total': len(cidades_data)
    })
