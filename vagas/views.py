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
    usuario_email = request.session.get('email_atual')

    if request.method == 'POST':
        titulo = request.POST.get('txtTitulo')
        descricao_vaga = request.POST.get('txtDescricao')
        local = request.POST.get('txtLocal')
        requisito_vaga = request.POST.get('txtRequisito')
        cursos = request.POST.getlist('txtCursos[]') 

        usuario = UsuarioBase.objects.get(email = usuario_email)  
        empresa = usuario.empresa

        # Criar Vaga
        vaga = Vagas.objects.create(
            cargo_vaga=titulo,
            local = local,
            descricao_vaga=descricao_vaga,
            requisito_vaga=requisito_vaga,

            empresa=empresa,
        )

        for curso in cursos:
                CursoVaga.objects.create(
                    vaga=vaga,
                    curso=curso
                )

        messages.success(request, 'Vaga cadastrada com sucesso!')
        return redirect('core:home')

    estados = Estado.objects.all().order_by('nome_estado')
    empresas = Empresa.objects.all().order_by('nome_empresa')
    return render(request, 'cadastro_vagas.html', {
        'estados': estados,
        # 'empresas': empresas
    })

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
