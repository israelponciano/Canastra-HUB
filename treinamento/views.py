from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import Treinamento, InscricaoTreinamento


def listar_treinamentos(request):
    termo = request.GET.get('q', '').strip()
    treinamentos = Treinamento.objects.order_by('-data_inicio')

    if termo:
        treinamentos = treinamentos.filter(
            models.Q(nome__icontains=termo) |
            models.Q(descricao__icontains=termo) |
            models.Q(local__icontains=termo)
        ).distinct()

    return render(request, 'treinamento/listar.html', {
        'treinamentos': treinamentos,
        'termo': termo,
    })


@login_required
def criar_treinamento(request):
    if request.method == 'POST':
        # logica de criação - pendente
        pass
    return render(request, 'treinamento/form.html')


@login_required
def inscrever(request, treinamento_id):
    treinamento = get_object_or_404(Treinamento, id=treinamento_id)

    if treinamento.vagas_disponiveis == 0:
        messages.error(request, 'Não há vagas disponíveis.')
        return redirect('treinamento:listar')

    _, criado = InscricaoTreinamento.objects.get_or_create(
        treinamento=treinamento,
        usuario=request.user
    )

    if criado:
        treinamento.vagas_disponiveis -= 1
        treinamento.save()
        messages.success(request, 'Inscrição realizada com sucesso!')
    else:
        messages.warning(request, 'Você já está inscrito neste treinamento.')

    return redirect('treinamento:listar')


@login_required
def cancelar_inscricao(request, treinamento_id):
    treinamento = get_object_or_404(Treinamento, id=treinamento_id)

    try:
        inscricao = InscricaoTreinamento.objects.get(
            treinamento=treinamento, usuario=request.user
        )
        inscricao.delete()
        treinamento.vagas_disponiveis += 1
        treinamento.save()
        messages.success(request, 'Inscrição cancelada com sucesso.')
    except InscricaoTreinamento.DoesNotExist:
        messages.error(request, 'Você não está inscrito neste treinamento.')

    return redirect('treinamento:listar')