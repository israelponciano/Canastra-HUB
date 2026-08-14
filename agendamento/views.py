import datetime
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
from django.utils import timezone
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

        # Correção segura para chamar o nome do usuário
        nome_usuario = getattr(request.user, 'nome',
                               request.user.nome or request.user.email)
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
    tipo_perfil = request.session.get('perfil')

    if tipo_perfil == 'admin':
        reservas = Reserva.objects.filter(
            status='confirmada').order_by('inicio')
    else:
        reservas = Reserva.objects.filter(
            status='confirmada', usuario=request.user).order_by('inicio')

    return render(request, 'agendamento/minhas_reservas.html', {'reservas': reservas})


@login_required
def api_reservas_calendario(request):
    reservas = Reserva.objects.filter(status='confirmada')
    eventos_json = []

    for r in reservas:
        nome_usuario = getattr(
            r.usuario, 'nome', r.usuario.nome or r.usuario.email)
        eventos_json.append({
            'id': r.id,
            'title': f"{r.get_sala_display()}",
            'start': r.inicio.isoformat(),
            'end': r.fim.isoformat(),
            'backgroundColor': '#22c55e',
            'borderColor': '#22c55e',
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

        nome_usuario = getattr(
            reserva.usuario, 'nome', reserva.usuario.nome or reserva.usuario.email)
        titulo_evento = f"Sala {sala} - {nome_usuario} (Atualizado)"

        dados_extras = {
            "empresa_projeto": reserva.empresa_projeto,
            "quantidade_pessoas": reserva.quantidade_pessoas,
            "finalidade": reserva.finalidade,
            "equipamentos": reserva.equipamentos,
            "observacoes": reserva.observacoes,
            "status_checkin": reserva.status_checkin
        }

        try:
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

        reserva.sala = sala
        reserva.inicio = inicio
        reserva.fim = fim
        reserva.save()

        messages.success(
            request, "Agendamento modificado com sucesso!")
        return redirect('minhas_reservas')

    context = {
        'reserva': reserva,
        'data_atual': reserva.inicio.strftime('%Y-%m-%d'),
        'bloco_atual': f"{reserva.inicio.strftime('%H:%M')}-{reserva.fim.strftime('%H:%M')}"
    }
    return render(request, 'agendamento/editar_reserva.html', context)


@login_required
def excluir_reserva(request, reserva_id):
    tipo_perfil = request.session.get('perfil')
    if tipo_perfil != 'admin':
        messages.error(
            request, "Acesso negado. Apenas administradores podem cancelar agendamentos.")
        return redirect('minhas_reservas')

    reserva = get_object_or_404(Reserva, id=reserva_id)

    reserva.status = 'cancelada'
    reserva.save()

    if reserva.linha_planilha:
        GoogleAgendaService.atualizar_checkin_google(
            linha_planilha=reserva.linha_planilha,
            status_checkin="CANCELADA",
            hora_checkin=""
        )

    messages.success(request, "Agendamento cancelado com sucesso!")
    return redirect('minhas_reservas')


@login_required
def gerador_qrcodes(request):
    """
    Gera uma página pronta para impressão contendo os QR Codes das 4 salas
    apontando dinamicamente para o IP/Host atual da máquina.
    """
    # host_atual = request.get_host()
    host_atual = "10.41.35.121"
    protocolo = 'https' if request.is_secure() else 'http'

    salas = [
        {'chave': 'treinamentos', 'nome': 'Espaço de Treinamentos'},
        {'chave': 'reunioes', 'nome': 'Sala de Reuniões'},
        {'chave': 'laboratorio', 'nome': 'Laboratório de Práticas Gerais'},
        {'chave': 'fast', 'nome': 'FAST - Fábrica de Soluções Tecnológicas'},
    ]

    for sala in salas:
        url_checkin = f"{protocolo}://{host_atual}/checkin/{sala['chave']}/"
        sala['qrcode_url'] = f"https://quickchart.io/qr?text={url_checkin}&size=300"
        sala['full_url'] = url_checkin

    return render(request, 'agendamento/qrcodes.html', {'salas': salas})


@login_required
def checkin_qrcode(request, sala_chave):
    """
    Processa a leitura do QR Code da sala:
    1. Se houver reserva confirmada do usuário no horário atual -> Faz o Check-in.
    2. Se a sala estiver ocupada por outra pessoa -> Bloqueia.
    3. Se a sala estiver totalmente vaga -> Cria reserva automática de Uso Direto (1 hora).
    """
    agora = timezone.now()

    # Busca agendamento ativo para a sala no horário corrente
    reserva_atual = Reserva.objects.filter(
        sala=sala_chave,
        status='confirmada',
        inicio__lte=agora,
        fim__gte=agora
    ).first()

    if reserva_atual:
        # CENÁRIO 1: O usuário logado é o titular do agendamento
        if reserva_atual.usuario == request.user:
            reserva_atual.status_checkin = 'CONFIRMADO'
            reserva_atual.hora_checkin = agora
            reserva_atual.save()

            if reserva_atual.linha_planilha:
                GoogleAgendaService.atualizar_checkin_google(
                    linha_planilha=reserva_atual.linha_planilha,
                    status_checkin='CONFIRMADO',
                    hora_checkin=agora.strftime('%H:%M:%S')
                )

            contexto = {
                'status': 'sucesso',
                'titulo': 'Check-in Confirmado! 🟢',
                'mensagem': f'Seu check-in na sala {reserva_atual.get_sala_display()} foi registrado com sucesso.',
                'cor': 'success',
                'reserva': reserva_atual
            }
            return render(request, 'agendamento/checkin_resultado.html', contexto)

        # CENÁRIO 2: A sala está ocupada por outro usuário
        else:
            nome_ocupante = getattr(
                reserva_atual.usuario, 'nome',
                reserva_atual.usuario.nome or reserva_atual.usuario.email
            )
            contexto = {
                'status': 'ocupada',
                'titulo': 'Sala Ocupada 🔴',
                'mensagem': f'Esta sala está atualmente em uso por {nome_ocupante}.',
                'cor': 'danger',
                'reserva': reserva_atual
            }
            return render(request, 'agendamento/checkin_resultado.html', contexto)

    # CENÁRIO 3: Sala VAGA -> Uso Direto (1 Hora)
    else:
        inicio = agora
        fim = agora + timedelta(hours=1)

        nova_reserva = Reserva(
            usuario=request.user,
            sala=sala_chave,
            inicio=inicio,
            fim=fim,
            empresa_projeto="Uso Presencial Espontâneo",
            quantidade_pessoas=1,
            finalidade="Uso Direto via QR Code",
            equipamentos="Uso geral do espaço",
            observacoes="Iniciado via leitura presencial de QR Code.",
            status='confirmada',
            status_checkin='USO DIRETO',
            hora_checkin=agora
        )

        nome_usuario = getattr(
            request.user, 'nome', request.user.nome or request.user.email
        )
        nome_amigavel = nova_reserva.get_sala_display()
        titulo_evento = f"{nome_amigavel} - {nome_usuario} (Uso Direto)"

        dados_extras = {
            "empresa_projeto": nova_reserva.empresa_projeto,
            "quantidade_pessoas": 1,
            "finalidade": nova_reserva.finalidade,
            "equipamentos": nova_reserva.equipamentos,
            "observacoes": nova_reserva.observacoes,
            "status_checkin": "USO DIRETO"
        }

        try:
            google_id, linha_planilha = GoogleAgendaService.enviar_para_google(
                nome_sala=sala_chave,
                titulo=titulo_evento,
                data_inicio=inicio,
                data_fim=fim,
                email_cliente=request.user.email,
                dados_extras=dados_extras
            )
            nova_reserva.google_event_id = google_id
            nova_reserva.linha_planilha = linha_planilha
        except Exception as e:
            print(f"Erro ao registrar uso direto no Google: {e}")

        nova_reserva.save()

        if nova_reserva.linha_planilha:
            GoogleAgendaService.atualizar_checkin_google(
                linha_planilha=nova_reserva.linha_planilha,
                status_checkin='USO DIRETO',
                hora_checkin=agora.strftime('%H:%M:%S')
            )

        contexto = {
            'status': 'uso_direto',
            'titulo': 'Uso Direto Iniciado 🟡',
            'mensagem': f'Espaço livre! Você iniciou uma alocação de 1 hora no espaço {nome_amigavel} (válido até {fim.strftime("%H:%M")}).',
            'cor': 'warning',
            'reserva': nova_reserva
        }
        return render(request, 'agendamento/checkin_resultado.html', contexto)
