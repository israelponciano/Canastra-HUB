from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models as db_models
from core.models import Hub
from .models import Treinamento, SessaoTreinamento, InscricaoTreinamento


# ──────────────────────────────────────────
# LISTAGEM E BUSCA — todos os usuários
# ──────────────────────────────────────────

def listar_treinamentos(request):
    termo = request.GET.get('q', '').strip()
    treinamentos = Treinamento.objects.prefetch_related('sessoes').order_by('-id')

    if termo:
        treinamentos = treinamentos.filter(
            db_models.Q(nome__icontains=termo) |
            db_models.Q(descricao__icontains=termo) |
            db_models.Q(local__icontains=termo)
        ).distinct()

    # marca quais o usuário logado já está inscrito
    inscritos = set()
    if request.user.is_authenticated:
        inscritos = set(
            InscricaoTreinamento.objects.filter(
                usuario=request.user
            ).values_list('treinamento_id', flat=True)
        )

    return render(request, 'treinamento/listar.html', {
        'treinamentos': treinamentos,
        'termo': termo,
        'inscritos': inscritos,
    })


# ──────────────────────────────────────────
# CADASTRO — empresa e admin
# ──────────────────────────────────────────

@login_required
def criar_treinamento(request):
    perfil = request.session.get('perfil')
    if perfil not in ('empresa', 'admin'):
        messages.error(request, 'Acesso negado.')
        return redirect('treinamento:listar_treinamentos')

    hubs = Hub.objects.filter(isActive=True).order_by('nome_hub')

    if request.method == 'POST':
        nome          = request.POST.get('nome', '').strip()
        data_inicio   = request.POST.get('data_inicio') or None
        data_fim      = request.POST.get('data_fim') or None
        local         = request.POST.get('local', '').strip()
        publico_alvo  = request.POST.get('publico_alvo', '').strip()
        descricao     = request.POST.get('descricao', '').strip()
        vagas         = request.POST.get('vagas_disponiveis') or 0
        tipo_setc     = request.POST.get('tipo_setc', '').strip()
        hub_id        = request.POST.get('hub') or None

        # datas das sessões (listas)
        datas_sessao   = request.POST.getlist('sessao_data')
        horarios_sessao = request.POST.getlist('sessao_horario')

        if not nome:
            messages.error(request, 'O nome do treinamento é obrigatório.')
            return render(request, 'treinamento/form.html', {'hubs': hubs})

        treinamento = Treinamento.objects.create(
            nome=nome,
            data_inicio=data_inicio,
            data_fim=data_fim,
            local=local,
            publico_alvo=publico_alvo,
            descricao=descricao,
            vagas_disponiveis=int(vagas),
            tipo_setc=tipo_setc,
            hub_id=hub_id,
        )

        # salva as sessões enviadas
        for data, horario in zip(datas_sessao, horarios_sessao):
            if data and horario:
                SessaoTreinamento.objects.create(
                    treinamento=treinamento,
                    data=data,
                    horario=horario,
                )

        messages.success(request, 'Treinamento cadastrado com sucesso!')
        return redirect('treinamento:listar_treinamentos')

    return render(request, 'treinamento/form.html', {'hubs': hubs})


# ──────────────────────────────────────────
# EDIÇÃO — empresa e admin
# ──────────────────────────────────────────

@login_required
def editar_treinamento(request, treinamento_id):
    perfil = request.session.get('perfil')
    if perfil not in ('empresa', 'admin'):
        messages.error(request, 'Acesso negado.')
        return redirect('treinamento:listar_treinamentos')

    treinamento = get_object_or_404(Treinamento, id=treinamento_id)
    hubs = Hub.objects.filter(isActive=True).order_by('nome_hub')
    sessoes = treinamento.sessoes.all()

    if request.method == 'POST':
        treinamento.nome           = request.POST.get('nome', '').strip()
        treinamento.data_inicio    = request.POST.get('data_inicio') or None
        treinamento.data_fim       = request.POST.get('data_fim') or None
        treinamento.local          = request.POST.get('local', '').strip()
        treinamento.publico_alvo   = request.POST.get('publico_alvo', '').strip()
        treinamento.descricao      = request.POST.get('descricao', '').strip()
        treinamento.vagas_disponiveis = int(request.POST.get('vagas_disponiveis') or 0)
        treinamento.tipo_setc      = request.POST.get('tipo_setc', '').strip()
        treinamento.hub_id         = request.POST.get('hub') or None

        if not treinamento.nome:
            messages.error(request, 'O nome do treinamento é obrigatório.')
            return render(request, 'treinamento/form.html', {
                'hubs': hubs, 'treinamento': treinamento, 'sessoes': sessoes
            })

        treinamento.save()

        # recria as sessões do zero
        treinamento.sessoes.all().delete()
        datas_sessao    = request.POST.getlist('sessao_data')
        horarios_sessao = request.POST.getlist('sessao_horario')
        for data, horario in zip(datas_sessao, horarios_sessao):
            if data and horario:
                SessaoTreinamento.objects.create(
                    treinamento=treinamento, data=data, horario=horario
                )

        messages.success(request, 'Treinamento atualizado com sucesso!')
        return redirect('treinamento:listar_treinamentos')

    return render(request, 'treinamento/form.html', {
        'hubs': hubs,
        'treinamento': treinamento,
        'sessoes': sessoes,
    })


# ──────────────────────────────────────────
# REMOÇÃO — empresa e admin
# ──────────────────────────────────────────

@login_required
def remover_treinamento(request, treinamento_id):
    perfil = request.session.get('perfil')
    if perfil not in ('empresa', 'admin'):
        messages.error(request, 'Acesso negado.')
        return redirect('treinamento:listar_treinamentos')

    treinamento = get_object_or_404(Treinamento, id=treinamento_id)

    if request.method == 'POST':
        treinamento.delete()
        messages.success(request, 'Treinamento removido com sucesso.')
        return redirect('treinamento:listar_treinamentos')

    return render(request, 'treinamento/confirmar_remocao.html', {
        'treinamento': treinamento
    })


# ──────────────────────────────────────────
# INSCRIÇÃO — usuário comum
# ──────────────────────────────────────────

@login_required
def inscrever(request, treinamento_id):
    treinamento = get_object_or_404(Treinamento, id=treinamento_id)

    if treinamento.vagas_disponiveis <= 0:
        messages.error(request, 'Não há vagas disponíveis neste treinamento.')
        return redirect('treinamento:listar_treinamentos')

    _, criado = InscricaoTreinamento.objects.get_or_create(
        treinamento=treinamento,
        usuario=request.user,
    )

    if criado:
        treinamento.vagas_disponiveis -= 1
        treinamento.save()
        messages.success(request, f'Inscrição em "{treinamento.nome}" realizada!')
    else:
        messages.warning(request, 'Você já está inscrito neste treinamento.')

    return redirect('treinamento:listar_treinamentos')


# ──────────────────────────────────────────
# CANCELAMENTO — usuário comum
# ──────────────────────────────────────────

@login_required
def cancelar_inscricao(request, treinamento_id):
    treinamento = get_object_or_404(Treinamento, id=treinamento_id)

    try:
        inscricao = InscricaoTreinamento.objects.get(
            treinamento=treinamento,
            usuario=request.user,
        )
        inscricao.delete()
        treinamento.vagas_disponiveis += 1
        treinamento.save()
        messages.success(request, 'Inscrição cancelada com sucesso.')
    except InscricaoTreinamento.DoesNotExist:
        messages.error(request, 'Você não está inscrito neste treinamento.')

    return redirect('treinamento:listar_treinamentos')