# agendamento/constants.py
from datetime import datetime, timedelta
from django.utils import timezone

# Slots de 1h20min (Sala de Reuniões e Sala Fast)
SLOTS_80_MINUTOS = [
    ("07:00", "08:20", "07:00 às 08:20"),
    ("08:30", "09:50", "08:30 às 09:50"),
    ("10:00", "11:20", "10:00 às 11:20"),
    ("11:30", "12:50", "11:30 às 12:50"),
    ("13:00", "14:20", "13:00 às 14:20"),
    ("14:30", "15:50", "14:30 às 15:50"),
    ("16:00", "17:20", "16:00 às 17:20"),
    ("17:30", "18:50", "17:30 às 18:50"),
    ("19:00", "20:20", "19:00 às 20:20"),
]

# Slots de 50min (Demais salas / Treinamento)
SLOTS_50_MINUTOS = [
    ("07:00", "07:50", "07:00 às 07:50"),
    ("08:00", "08:50", "08:00 às 08:50"),
    ("09:00", "09:50", "09:00 às 09:50"),
    ("10:00", "10:50", "10:00 às 10:50"),
    ("11:00", "11:50", "11:00 às 11:50"),
    ("12:00", "12:50", "12:00 às 12:50"),
    ("13:00", "13:50", "13:00 às 13:50"),
    ("14:00", "14:50", "14:00 às 14:50"),
    ("15:00", "15:50", "15:00 às 15:50"),
    ("16:00", "16:50", "16:00 às 16:50"),
    ("17:00", "17:50", "17:00 às 17:50"),
    ("18:00", "18:50", "18:00 às 18:50"),
    ("19:00", "19:50", "19:00 às 19:50"),
    ("20:00", "20:50", "20:00 às 20:50"),
]


def obter_slots_por_sala(nome_sala):
    nome_normalizado = nome_sala.lower()
    if 'reunioes' in nome_normalizado or 'fast' in nome_normalizado:
        return SLOTS_80_MINUTOS
    return SLOTS_50_MINUTOS


def obter_duracao_padrao_sala(nome_sala):
    nome_normalizado = nome_sala.lower()
    if any(termo in nome_normalizado for termo in ['reuniao', 'reunioes', 'fast']):
        return 80
    return 50


def calcular_horario_fim_uso_direto(nome_sala, agora=None):
    if agora is None:
        agora = timezone.localtime()

    slots = obter_slots_por_sala(nome_sala)

    for inicio_str, fim_str, _ in slots:
        h_fim = datetime.strptime(fim_str, "%H:%M").time()
        dt_fim = datetime.combine(agora.date(), h_fim)

        # Converte dt_fim para timezone-aware igual a agora
        if timezone.is_aware(agora):
            dt_fim = timezone.make_aware(
                dt_fim, timezone.get_current_timezone())

        if agora < dt_fim:
            minutos_restantes = int((dt_fim - agora).total_seconds() // 60)
            return dt_fim, minutos_restantes

    # Caso esteja fora da grade normal de horários
    duracao_padrao = obter_duracao_padrao_sala(nome_sala)
    dt_fim = agora + timedelta(minutes=duracao_padrao)
    return dt_fim, duracao_padrao
