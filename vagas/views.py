from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import models
from empresa.models import *
from core.models import *
from vagas.models import *
from django.contrib import messages
from django.http import JsonResponse
from .models import Vagas, UsuarioVaga  # Importe UsuarioVaga aqui

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

        usuario = UsuarioBase.objects.get(email=usuario_email)
        empresa = usuario.empresa

        # Criar Vaga
        vaga = Vagas.objects.create(
            cargo_vaga=titulo,
            local=local,
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

    cidades = Cidade.objects.filter(
        estado_cidade_id=estado_id).order_by('nome_cidade')

    print(f"DEBUG: {cidades.count()} cidades encontradas")

    cidades_data = [
        {'id': cidade.id, 'nome': cidade.nome_cidade} for cidade in cidades
    ]

    return JsonResponse({
        'cidades': cidades_data,
        'total': len(cidades_data)
    })

# bucar vagas


def buscar_vagas(request):
    """
    Lista todas as vagas ativas, com opção de filtrar por termo de busca.
    """
    # 1. Receber o termo de busca (query) da URL (ex: /vagas/?q=Desenvolvedor)
    termo_busca = request.GET.get('q', '').strip()

    # 2. Começa com todas as vagas ativas
    vagas = Vagas.objects.filter(status='ativa').order_by('-data_publicacao')

    # checagem de vagas ativas feita -> adiciona vagas candidatadas pelo usuario
    # pegamos os dados do usuário
    if request.user.is_authenticated:
        try:
            usuario_perfil = Usuario.objects.get(user=request.user)
            candidaturas_do_usuario = UsuarioVaga.objects.filter(
                usuario=usuario_perfil).values_list('vaga__id', flat=True)

            for vaga in vagas:
                vaga.ja_candidatada = vaga.id in candidaturas_do_usuario
        except Usuario.DoesNotExist:
            pass

    # 3. Se houver um termo de busca, aplica o filtro
    if termo_busca:
        # Filtra as vagas onde o termo de busca aparece:
        # - No cargo da vaga (cargo_vaga__icontains)
        # - Na descrição da vaga (descricao_vaga__icontains)
        # - Ou no requisito (requisito_vaga__icontains)
        vagas = vagas.filter(
            models.Q(cargo_vaga__icontains=termo_busca) | models.Q(
                descricao_vaga__icontains=termo_busca) | models.Q(requisito_vaga__icontains=termo_busca)
            # Usa .distinct() para evitar duplicatas, se a busca for mais complexa
        ).distinct()

    # 4. Prepara o contexto
    contexto = {
        'vagas': vagas,
        'termo_busca': termo_busca,  # Passa o termo de volta para o input na tela
    }

    # 5. Renderiza o template de busca
    return render(request, 'tela_busca_vagas.html', contexto)

# detalhe da vaga


@login_required
def detalhe_vaga(request, vaga_id):
    # Tenta buscar a vaga
    vaga = get_object_or_404(Vagas, id=vaga_id)

    # Busca os cursos/requisitos relacionados a esta vaga (CursoVaga)
    cursos = CursoVaga.objects.filter(vaga=vaga)

    ja_candidatado = False

    if request.user.is_authenticated:
        # Assumindo que o perfil do usuário se chama 'Usuario'
        try:
            usuario = Usuario.objects.get(user=request.user)
            # Verifica se já existe um registro em UsuarioVaga
            ja_candidatado = UsuarioVaga.objects.filter(
                vaga=vaga, usuario=usuario).exists()
        except Usuario.DoesNotExist:
            pass

    contexto = {
        'vaga': vaga,
        'cursos': cursos,  # Passando os cursos para o template
        'ja_candidatado': ja_candidatado,
    }

    return render(request, 'detalhe_vaga.html', contexto)


@login_required
def mensagembonita(request):

    messages.success(request, f'Inscrição feita com sucesso!')
    return redirect('core:home')

# No seu vagas/views.py
# Assumindo que seu modelo de usuário está em 'usuario.models'
# Função para registrar a candidatura


@login_required
@require_http_methods(["POST"])
def candidatar_vaga(request, vaga_id):
    vaga = get_object_or_404(Vagas, id=vaga_id)

    # CRÍTICO: Obter a instância do seu modelo de perfil Usuario, não o User padrão
    try:
        # Tenta obter o objeto de perfil Usuario associado ao usuário logado
        # Ajuste esta linha se o seu perfil Usuario estiver ligado de forma diferente
        usuario_perfil = Usuario.objects.get(user=request.user)
    except Usuario.DoesNotExist:
        messages.error(request, "Seu perfil de usuário não foi encontrado.")
        return redirect('vagas:detalhe_vaga', vaga_id=vaga.id)

    # Cria o registro apenas se ele não existir
    if UsuarioVaga.objects.filter(vaga=vaga, usuario=usuario_perfil).exists():
        messages.warning(request, "Você já está candidatado a esta vaga.")
    else:
        UsuarioVaga.objects.create(vaga=vaga, usuario=usuario_perfil)
        messages.success(
            request, f"Candidatura à vaga '{vaga.cargo_vaga}' registrada com sucesso!")

    # Redireciona para a página de detalhes da vaga
    return redirect('vagas:detalhe_vaga', vaga_id=vaga.id)


# Função para cancelar a candidatura
@login_required
@require_http_methods(["POST"])
def cancelar_candidatura(request, vaga_id):
    vaga = get_object_or_404(Vagas, id=vaga_id)

    try:
        # Obtém o perfil do usuário
        usuario_perfil = Usuario.objects.get(user=request.user)

        # Tenta encontrar e deletar a candidatura
        candidatura = UsuarioVaga.objects.get(
            vaga=vaga, usuario=usuario_perfil)
        candidatura.delete()
        messages.success(
            request, f"Candidatura à vaga '{vaga.cargo_vaga}' cancelada com sucesso.")
    except UsuarioVaga.DoesNotExist:
        messages.error(request, "Erro: Candidatura não encontrada.")
    except Usuario.DoesNotExist:
        messages.error(request, "Seu perfil de usuário não foi encontrado.")

    # Redireciona para a página de detalhes da vaga
    return redirect('vagas:detalhe_vaga', vaga_id=vaga.id)
