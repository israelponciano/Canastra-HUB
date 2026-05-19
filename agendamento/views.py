from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
from .models import Reserva
from .services import GoogleAgendaService

@login_required
def realizar_reserva(request):
    if request.method == "POST":
        sala = request.POST.get('sala')
        inicio_str = request.POST.get('inicio')  # Recebe do input datetime-local (YYYY-MM-DDTHH:MM)
        fim_str = request.POST.get('fim')
        
        # 1. Converte as strings de data/hora do formulário para objetos Python datetime
        inicio = parse_datetime(inicio_str)
        fim = parse_datetime(fim_str)

        if not inicio or not fim:
            messages.error(request, "Por favor, insira datas e horários válidos.")
            return redirect('realizar_reserva')

        # Validação básica: o término não pode ser antes do início
        if fim <= inicio:
            messages.error(request, "A hora de término deve ser após a hora de início.")
            return redirect('realizar_reserva')

        # 2. MOTOR DE SEGURANÇA: Verificação de Conflito de Horário Local
        # (Garante que ninguém pegue a mesma sala no mesmo período)
        conflito = Reserva.objects.filter(
            sala=sala,
            status='confirmada',
            inicio__lt=fim,  # O início da reserva existente é antes do fim da nova
            fim__gt=inicio   # O fim da reserva existente é depois do início da nova
        ).exists()

        if conflito:
            messages.error(request, "Desculpe, este horário já está reservado para esta sala!")
            return redirect('realizar_reserva')

        # 3. Dispara a criação no Google Agenda via Apps Script
        # O título do evento no Google será o nome do usuário logado
        titulo_evento = f"Reserva Sala {sala} - {request.user.get_full_name() or request.user.username}"
        
        resultado = GoogleAgendaService.enviar_para_google(
            sala=sala,
            titulo=titulo_evento,
            data_inicio=inicio.isoformat(),
            data_fim=fim.isoformat(),
            email_cliente=request.user.email
        )

        # 4. Trata o retorno do Google
        if resultado.get('status') == 'sucesso':
            # Salva no banco de dados local com o ID retornado pelo Google
            Reserva.objects.create(
                usuario=request.user,
                sala=sala,
                inicio=inicio,
                fim=fim,
                google_event_id=resultado.get('event_id'),
                status='confirmada'
            )
            messages.success(request, "Reserva realizada com sucesso! O convite foi enviado para o seu e-mail.")
            return redirect('realizar_reserva')  # Mude para a sua página de listagem ou dashboard depois
        else:
            # Se o Google der erro (ex: agenda inválida), avisa o usuário sem salvar no banco
            erro_msg = resultado.get('message', 'Erro desconhecido.')
            messages.error(request, f"Erro ao sincronizar com o Google Agenda: {erro_msg}")

    # Se for um acesso via GET (carregando a página), apenas renderiza o formulário
    return render(request, 'agendamento/criar_reserva.html')