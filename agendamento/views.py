import datetime
from django.shortcuts import render, redirect, get_object_or_404  # Garantido o 404 correto aqui
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
        data_str = request.POST.get('data_reserva')   # Ex: "2026-06-02"
        bloco_str = request.POST.get('bloco_horario') # Ex: "08:00-09:30"

        if not data_str or not bloco_str:
            messages.error(request, "Por favor, preencha todos os campos.")
            return redirect('realizar_reserva')

        try:
            # Separa o horário de início e fim do bloco de texto
            hora_inicio_str, hora_fim_str = bloco_str.split('-')
            
            # Constrói as strings completas no formato aceito pelo Django
            inicio_comb = f"{data_str} {hora_inicio_str}:00"
            fim_comb = f"{data_str} {hora_fim_str}:00"
            
            # Converte para datetime nativo
            inicio = parse_datetime(inicio_comb)
            fim = parse_datetime(fim_comb)
        except Exception:
            messages.error(request, "Erro ao processar o horário selecionado.")
            return redirect('realizar_reserva')

        if fim <= inicio:
            messages.error(request, "A hora de término deve ser após a hora de início.")
            return redirect('realizar_reserva')

        # MOTOR DE SEGURANÇA: Verificação de conflito de horário
        conflito = Reserva.objects.filter(
            sala=sala,
            status='confirmada',
            inicio__lt=fim,
            fim__gt=inicio
        ).exists()

        if conflito:
            messages.error(request, "Esta sala já está reservada para este horário.")
            return redirect('realizar_reserva')

        # SALVAR A RESERVA NO BANCO LOCAL
        nova_reserva = Reserva(
            usuario=request.user,
            sala=sala,
            inicio=inicio,
            fim=fim,
            status='confirmada'
        )
        
        # INTEGRAÇÃO GOOGLE AGENDA (Na criação da reserva)
        titulo_evento = f"Sala {sala} - {request.user.username}"
        try:
            google_id = GoogleAgendaService.enviar_para_google(
                sala=sala,
                titulo=titulo_evento,
                data_inicio=inicio.isoformat(),
                data_fim=fim.isoformat(),
                email_cliente=request.user.email
            )
            if google_id:
                nova_reserva.google_event_id = google_id
        except Exception:
            messages.warning(request, "Agendamento feito localmente, mas não sincronizado com o Google.")

        nova_reserva.save()
        messages.success(request, "Agendamento realizado com sucesso!")
        return redirect('minhas_reservas')

    return render(request, 'agendamento/agendar.html')


@login_required
def minhas_reservas(request):
    # Coleta todas as reservas confirmadas para exibir no painel
    reservas = Reserva.objects.filter(status='confirmada').order_by('inicio')
    return render(request, 'agendamento/minhas_reservas.html', {'reservas': reservas})


@login_required
def api_reservas_calendario(request):
    """ Retorna as reservas em formato JSON para alimentar o FullCalendar """
    reservas = Reserva.objects.filter(status='confirmada')
    eventos_json = []
    
    for r in reservas:
        eventos_json.append({
            'id': r.id,
            'title': f"Sala {r.sala} - Ocupado",
            'start': r.inicio.isoformat(),
            'end': r.fim.isoformat(),
            'backgroundColor': '#22c55e',
            'borderColor': '#22c55e'
        })
        
    return JsonResponse(eventos_json, safe=False)


@login_required
def editar_reserva(request, reserva_id):
    # SEGURANÇA PERSONALIZADA: Valida pelo tipo de perfil ativo na sessão
    tipo_perfil = request.session.get('perfil')
    if tipo_perfil != 'admin':
        messages.error(request, "Acesso negado. Apenas administradores podem editar agendamentos.")
        return redirect('minhas_reservas')
        
    # Corrigido aqui: Agora usando a função importada corretamente
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if request.method == "POST":
        sala = request.POST.get('sala')
        data_str = request.POST.get('data_reserva')
        bloco_str = request.POST.get('bloco_horario')
        
        if not data_str or not bloco_str:
            messages.error(request, "Por favor, preencha todos os campos.")
            return redirect('editar_reserva', reserva_id=reserva.id)
            
        try:
            hora_inicio_str, hora_fim_str = bloco_str.split('-')
            inicio_comb = f"{data_str} {hora_inicio_str}:00"
            fim_comb = f"{data_str} {hora_fim_str}:00"
            
            inicio = parse_datetime(inicio_comb)
            fim = parse_datetime(fim_comb)
        except Exception:
            messages.error(request, "Erro ao processar o horário selecionado.")
            return redirect('editar_reserva', reserva_id=reserva.id)

        # MOTOR DE SEGURANÇA: Bloqueia se houver choque de horários com outros usuários
        conflito = Reserva.objects.filter(
            sala=sala,
            status='confirmada',
            inicio__lt=fim,
            fim__gt=inicio
        ).exclude(id=reserva.id).exists()

        if conflito:
            messages.error(request, "Esta sala já está reservada para este horário.")
            return redirect('editar_reserva', reserva_id=reserva.id)

        # SINCRONIZAÇÃO COM O GOOGLE AGENDA (Atualização)
        titulo_evento = f"Sala {sala} - {reserva.usuario.username}"
        try:
            novo_google_id = GoogleAgendaService.enviar_para_google(
                sala=sala,
                titulo=titulo_evento,
                data_inicio=inicio.isoformat(),
                data_fim=fim.isoformat(),
                email_cliente=reserva.usuario.email
            )
            if novo_google_id:
                reserva.google_event_id = novo_google_id
        except Exception:
            messages.warning(request, "O agendamento foi salvo localmente, mas não atualizou o Google Agenda.")

        # Salva as alterações finais no banco de dados local
        reserva.sala = sala
        reserva.inicio = inicio
        reserva.fim = fim
        reserva.save()
        
        messages.success(request, f"Agendamento de {reserva.usuario.username} atualizado com sucesso!")
        return redirect('minhas_reservas')

    # Retorno para o método GET (Carregamento da página)
    context = {
        'reserva': reserva,
        'data_atual': reserva.inicio.strftime('%Y-%m-%d'),
        'bloco_atual': f"{reserva.inicio.strftime('%H:%M')}-{reserva.fim.strftime('%H:%M')}"
    }
    return render(request, 'agendamento/editar_reserva.html', context)


@login_required
def excluir_reserva(request, reserva_id):
    # SEGURANÇA PERSONALIZADA: Valida pelo tipo de perfil ativo na sessão
    tipo_perfil = request.session.get('perfil')
    if tipo_perfil != 'admin':
        messages.error(request, "Acesso negado. Apenas administradores podem remover agendamentos.")
        return redirect('minhas_reservas')
        
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Exclusão lógica mudando o status para cancelada
    reserva.status = 'cancelada'
    reserva.save()
    
    messages.success(request, "Agendamento cancelado com sucesso!")
    return redirect('minhas_reservas')