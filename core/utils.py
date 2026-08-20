def obter_ip_cliente(request):
    """Extrai o IP real do cliente, considerando proxies/load balancer."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def registrar_log(request, tipo_acao, descricao=''):
    """Cria um LogAcao a partir da request atual.

    Uso: registrar_log(request, LogAcao.TipoAcao.VAGA_CRIADA, "Vaga X criada")
    """
    from core.models import LogAcao  # import local evita import circular

    usuario = request.user if request.user.is_authenticated else None
    LogAcao.objects.create(
        usuario=usuario,
        tipo_acao=tipo_acao,
        descricao=descricao,
        ip=obter_ip_cliente(request),
    )