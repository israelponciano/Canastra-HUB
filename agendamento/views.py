import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
from django.http import JsonResponse
from .models import Reserva
from .services import GoogleAgendaService


@login_required
def realizar_reserva(request):
    if request.method == "POST":
        sala = request.POST.get('sala')
        data_str = request.POST.get('data_reserva')
        bloco_str = request.POST.get('bloco_horario')

        # Captura os novos campos vindos do formulário HTML
        empresa_projeto = request.POST.get('empresa_projeto', 'Não informado')
        quantidade_pessoas = request.POST.get('quantidade_pessoas', 0)
        finalidade = request.POST.get('finalidade', 'Não informado')
        equipamentos = request.POST.get('equipamentos', 'Não informado')
        observacoes = request.POST.get('observacoes', 'Não informado')

        if not data_str or not bloco_str:
            messages.error(
                request, "Por favor, preencha todos os campos do formulário.")
            return redirect('realizar_reserva')

        try:
            hora_inicio_str, hora_fim_str = bloco_str.split('-')
            inicio_comb = f"{data_str} {hora_inicio_str}:00"
            fim_comb = f"{data_str} {hora_fim_str}:00"
            inicio = parse_datetime(inicio_comb)
            fim = parse_datetime(fim_comb)
        except Exception:
            messages.error(
                request, "Erro ao processar o bloco de horário selecionado.")
            return redirect('realizar_reserva')

        conflito = Reserva.objects.filter(
            sala=sala, status='confirmada', inicio__lt=fim, fim__gt=inicio).exists()
        if conflito:
            messages.error(
                request, "Esta sala já se encontra reservada para o período selecionado.")
            return redirect('realizar_reserva')

        # Criação na memória com os novos dados locais salvos
        nova_reserva = Reserva(
            usuario=request.user,
            sala=sala,
            inicio=inicio,
            fim=fim,
            empresa_projeto=empresa_projeto,
            quantidade_pessoas=int(
                quantidade_pessoas) if quantidade_pessoas else 0,
            finalidade=finalidade,
            equipamentos=equipamentos,
            observacoes=observacoes,
            status='confirmada'
        )

        nome_amigavel_sala = nova_reserva.get_sala_display()

        # Correção segura para chamar o nome do usuário (trata caso 'nome' não exista no User)
        nome_usuario = getattr(request.user, 'nome',
                               request.user.first_name or request.user.email)
        titulo_evento = f"{nome_amigavel_sala} - {nome_usuario}"

        # Dicionário auxiliar para carregar os dados extras ao Service
        dados_extras = {
            "empresa_projeto": empresa_projeto,
            "quantidade_pessoas": quantidade_pessoas,
            "finalidade": finalidade,
            "equipamentos": equipamentos,
            "observacoes": observacoes,
            "status_checkin": "Pendente"
        }

        google_id = None
        linha_planilha = None
        try:
            # Descompacta a tupla retornada (event_id, linha_planilha)
            google_id, linha_planilha = GoogleAgendaService.enviar_para_google(
                nome_sala=sala,
                titulo=titulo_evento,
                data_inicio=inicio,
                data_fim=fim,
                email_cliente=request.user.email,
                dados_extras=dados_extras
            )
        except Exception as e:
            print(f"Erro de comunicação capturado na View: {e}")
            google_id, linha_planilha = None, None

        if not google_id:
            messages.error(
                request, "Não foi possível concluir o agendamento devido a uma falha na integração com o Google Calendar.")
            return redirect('realizar_reserva')

        # Salva as chaves de integração
        nova_reserva.google_event_id = google_id
        nova_reserva.linha_planilha = linha_planilha
        nova_reserva.save()

        messages.success(
            request, "Agendamento realizado e sincronizado com o Google com sucesso!")
        return redirect('minhas_reservas')

    return render(request, 'agendamento/agendar.html')


@login_required
def minhas_reservas(request):
    # 1. Verifica se o perfil ativo na sessão é administrador
    tipo_perfil = request.session.get('perfil')

    if tipo_perfil == 'admin':
        # Se for admin, lista todos os agendamentos confirmados do sistema
        reservas = Reserva.objects.filter(
            status='confirmada').order_by('inicio')
    else:
        # Se for usuário comum, filtra trazendo apenas as reservas criadas por ele mesmo
        reservas = Reserva.objects.filter(
            status='confirmada', usuario=request.user).order_by('inicio')

    return render(request, 'agendamento/minhas_reservas.html', {'reservas': reservas})


@login_required
def api_reservas_calendario(request):
    reservas = Reserva.objects.filter(status='confirmada')
    eventos_json = []

    for r in reservas:
        nome_usuario = getattr(
            r.usuario, 'nome', r.usuario.first_name or r.usuario.email)
        eventos_json.append({
            'id': r.id,
            'title': f"{r.get_sala_display()}",
            'start': r.inicio.isoformat(),
            'end': r.fim.isoformat(),
            'backgroundColor': '#22c55e',
            'borderColor': '#22c55e',
            # PASSAMOS OS DADOS EXTRA AQUI DENTRO:
            'extendedProps': {
                'sala': r.get_sala_display(),
                'usuario_nome': nome_usuario,
                'usuario_email': r.usuario.email,
                'horario_str': f"{r.inicio.strftime('%H:%M')} às {r.fim.strftime('%H:%M')}"
            }
        })

    return JsonResponse(eventos_json, safe=False)


@login_required
def editar_reserva(request, reserva_id):
    # SEGURANÇA POR SESSÃO: Bloqueia perfis que não sejam administradores
    tipo_perfil = request.session.get('perfil')
    if tipo_perfil != 'admin':
        messages.error(
            request, "Acesso negado. Apenas administradores podem editar agendamentos.")
        return redirect('minhas_reservas')

    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == "POST":
        sala = request.POST.get('sala')
        data_str = request.POST.get('data_reserva')
        bloco_str = request.POST.get('bloco_horario')

        if not data_str or not bloco_str:
            messages.error(
                request, "Por favor, preencha todos os campos obrigatórios.")
            return redirect('editar_reserva', reserva_id=reserva.id)

        try:
            hora_inicio_str, hora_fim_str = bloco_str.split('-')
            inicio_comb = f"{data_str} {hora_inicio_str}:00"
            fim_comb = f"{data_str} {hora_fim_str}:00"

            inicio = parse_datetime(inicio_comb)
            fim = parse_datetime(fim_comb)
        except Exception:
            messages.error(
                request, "Erro na leitura dos horários selecionados.")
            return redirect('editar_reserva', reserva_id=reserva.id)

        # MOTOR DE SEGURANÇA: Bloqueia conflitos desconsiderando o id da própria reserva em edição
        conflito = Reserva.objects.filter(
            sala=sala,
            status='confirmada',
            inicio__lt=fim,
            fim__gt=inicio
        ).exclude(id=reserva.id).exists()

        if conflito:
            messages.error(
                request, "Esta sala já está preenchida para este horário por outro utilizador.")
            return redirect('editar_reserva', reserva_id=reserva.id)

        # ATUALIZAÇÃO GOOGLE AGENDA
        nome_usuario = getattr(
            reserva.usuario, 'nome', reserva.usuario.first_name or reserva.usuario.email)
        titulo_evento = f"Sala {sala} - {nome_usuario} (Atualizado)"

        # Mantém os dados extras atuais durante a edição
        dados_extras = {
            "empresa_projeto": reserva.empresa_projeto,
            "quantidade_pessoas": reserva.quantidade_pessoas,
            "finalidade": reserva.finalidade,
            "equipamentos": reserva.equipamentos,
            "observacoes": reserva.observacoes,
            "status_checkin": reserva.status_checkin
        }

        try:
            # Descompacta a tupla retornada e corrige o parâmetro 'nome_sala'
            novo_google_id, nova_linha = GoogleAgendaService.enviar_para_google(
                nome_sala=sala,
                titulo=titulo_evento,
                data_inicio=inicio,
                data_fim=fim,
                email_cliente=reserva.usuario.email,
                dados_extras=dados_extras
            )
            if novo_google_id:
                reserva.google_event_id = novo_google_id
                reserva.linha_planilha = nova_linha
        except Exception:
            messages.warning(
                request, "Alterações salvas localmente, mas falhou a atualização no Google Calendar.")

        # Guarda as alterações definitivas no banco de dados
        reserva.sala = sala
        reserva.inicio = inicio
        reserva.fim = fim
        reserva.save()

        # REDIRECIONAMENTO INTELIGENTE: Devolve o admin à central de gerenciamento
        messages.success(
            request, f"Agendamento modificado com sucesso!")
        return redirect('minhas_reservas')

    # Método GET
    context = {
        'reserva': reserva,
        'data_atual': reserva.inicio.strftime('%Y-%m-%d'),
        'bloco_atual': f"{reserva.inicio.strftime('%H:%M')}-{reserva.fim.strftime('%H:%M')}"
    }
    return render(request, 'agendamento/editar_reserva.html', context)


@login_required
def excluir_reserva(request, reserva_id):
    # SEGURANÇA POR SESSÃO: Bloqueia perfis que não sejam administradores
    tipo_perfil = request.session.get('perfil')
    if tipo_perfil != 'admin':
        messages.error(
            request, "Acesso negado. Apenas administradores podem cancelar agendamentos.")
        return redirect('minhas_reservas')

    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Executa a exclusão lógica alterando o status para cancelada
    reserva.status = 'cancelada'
    reserva.save()

    # Se a reserva já estiver na planilha, atualiza a cor/status lá também
    if reserva.linha_planilha:
        GoogleAgendaService.atualizar_checkin_google(
            linha_planilha=reserva.linha_planilha,
            status_checkin="CANCELADA",
            hora_checkin=""
        )

    # REDIRECIONAMENTO INTELIGENTE: Atualiza a lista removendo o item imediatamente
    messages.success(request, "Agendamento cancelado com sucesso!")
    return redirect('minhas_reservas')
