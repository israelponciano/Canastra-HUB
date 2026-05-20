from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
from .models import Reserva
# Se houver a importação de services, mantenha-a abaixo:
# from .services import GoogleAgendaService

@login_required
def realizar_reserva(request):
    if request.method == "POST":
        sala = request.POST.get('sala')
        inicio_str = request.POST.get('inicio')
        fim_str = request.POST.get('fim')

        # 1. Converte as strings para objetos datetime
        inicio = parse_datetime(inicio_str)
        fim = parse_datetime(fim_str)

        if not inicio or not fim:
            messages.error(request, "Por favor, insira datas e horários válidos.")
            return redirect('realizar_reserva')

        # Validação básica: o término não pode ser antes do início
        if fim <= inicio:
            messages.error(request, "A hora de término deve ser após a hora de início.")
            return redirect('realizar_reserva')

        # 2. MOTOR DE SEGURANÇA: Verificação de conflito de horário
        conflito = Reserva.objects.filter(
            sala=sala,
            status='confirmada',
            inicio__lt=fim,  # início da reserva existente é antes do fim da nova
            fim__gt=inicio   # fim da reserva existente é depois do início da nova
        ).exists()

        if conflito:
            messages.error(request, "Esta sala já está reservada para este horário.")
            return redirect('realizar_reserva')

        # 3. SALVAR A RESERVA (Se não houver conflito)
        nova_reserva = Reserva(
            usuario=request.user,  # Ou como estiver relacionado no seu Model
            sala=sala,
            inicio=inicio,
            fim=fim,
            status='confirmada'
        )
        nova_reserva.save()

        messages.success(request, "Agendamento realizado com sucesso!")
        return redirect('realizar_reserva') # ou para a página de 'minhas_reservas'

    # Se o método for GET (quando apenas carrega a página), renderiza o formulário limpo
    return render(request, 'agendamento/agendar.html')


@login_required
def minhas_reservas(request):
    # Coleta todas as reservas confirmadas para exibir no painel
    reservas = Reserva.objects.filter(status='confirmada').order_by('inicio')
    
    return render(request, 'agendamento/minhas_reservas.html', {'reservas': reservas})