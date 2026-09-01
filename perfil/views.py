"""
App perfil — toda a lógica de exibição e atualização de perfil
extraída de core/views.py.

Imports de models são feitos diretamente de seus apps de origem;
este módulo não define nenhum model próprio.
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from core.models import (
    Cidade,
    Estado,
    Usuario,
    ExperienciaProfissional,
    CursoExtraCurricular,
    Idioma,
    Hub,
    InteresseCompra,
)
from empresa.models import Empresa, EmpresaHub


# ══════════════════════════════════════════
# EXIBIÇÃO DO PERFIL
# ══════════════════════════════════════════

@login_required
def perfil(request):
    """
    Exibe o perfil do usuário logado.
    Detecta o tipo (admin, empresa, usuario) e carrega os dados correspondentes.
    """
    user = request.user
    tipo_perfil = request.session.get('perfil', 'admin')

    estados = Estado.objects.all().order_by('nome_estado')

    contexto = {
        'user': user,
        'estados': estados,
        'cidades': Cidade.objects.none(),
    }

    if tipo_perfil == 'empresa':
        try:
            empresa = Empresa.objects.select_related('cidade', 'estado').get(user=user)
            if empresa.estado:
                contexto['cidades'] = Cidade.objects.filter(
                    estado_cidade=empresa.estado
                ).order_by('nome_cidade')

            hubs = Hub.objects.all().order_by('nome_hub')
            hubs_vinculados = list(
                EmpresaHub.objects.filter(empresa=empresa).values_list('hub_id', flat=True)
            )

            contexto.update({
                'empresa': empresa,
                'hubs': hubs,
                'hubs_vinculados': hubs_vinculados,
            })
        except Empresa.DoesNotExist:
            messages.error(request, 'Perfil de empresa não encontrado.')
            return redirect('core:home')

    elif tipo_perfil == 'usuario':
        try:
            usuario = Usuario.objects.select_related('cidade', 'estado').get(user=user)
            experiencias = ExperienciaProfissional.objects.filter(usuario=usuario)
            cursos_extras = CursoExtraCurricular.objects.filter(usuario=usuario)
            idiomas = Idioma.objects.filter(usuario=usuario)
            interesses_compra = list(
                InteresseCompra.objects
                .filter(usuario=usuario, isActive=True)
                .order_by('criado_em')[:3]
            )
            interesses_compra.extend([None] * (3 - len(interesses_compra)))

            if usuario.estado:
                contexto['cidades'] = Cidade.objects.filter(
                    estado_cidade=usuario.estado
                ).order_by('nome_cidade')

            contexto.update({
                'usuario': usuario,
                'experiencias': experiencias,
                'cursos_extras': cursos_extras,
                'idiomas': idiomas,
                'interesses_compra': interesses_compra,
            })
        except Usuario.DoesNotExist:
            messages.error(request, 'Perfil de usuário não encontrado.')
            return redirect('core:home')

    # Admin usa apenas dados do user — sem dados extras

    return render(request, 'perfil/perfil.html', contexto)


# ══════════════════════════════════════════
# ATUALIZAÇÃO DO PERFIL
# ══════════════════════════════════════════

@login_required
def atualizar_perfil(request):
    """
    Processa o formulário POST de atualização de perfil.
    Despacha para o helper específico por tipo de perfil.
    """
    if request.method != 'POST':
        return redirect('perfil:perfil')

    user = request.user
    tipo_perfil = request.session.get('perfil', 'admin')
    apenas_foto = request.POST.get('apenas_foto') == '1'

    try:
        # Foto — comum a todos
        if 'foto' in request.FILES:
            foto = request.FILES['foto']
            ext = foto.name.split('.')[-1].lower()
            if ext in ('jpg', 'jpeg', 'png'):
                user.foto = foto
                user.save()
                if apenas_foto:
                    messages.success(request, 'Foto atualizada com sucesso!')
                    return redirect('perfil:perfil')

        # Nome — comum a todos
        if request.POST.get('nome'):
            user.nome = request.POST.get('nome')
        user.save()

        if tipo_perfil == 'admin':
            messages.success(request, 'Perfil atualizado com sucesso!')

        elif tipo_perfil == 'empresa':
            _atualizar_empresa(request, user)
            messages.success(request, 'Perfil da empresa atualizado com sucesso!')

        elif tipo_perfil == 'usuario':
            _atualizar_usuario(request, user)
            messages.success(request, 'Perfil atualizado com sucesso!')

    except Exception as e:
        messages.error(request, f'Erro ao atualizar perfil: {str(e)}')

    return redirect('perfil:perfil')


# ══════════════════════════════════════════
# API AJAX — cidades por estado
# ══════════════════════════════════════════

def buscar_cidades(request):
    """
    Retorna JSON com cidades filtradas por estado_id.
    Usada nos selects de perfil via AJAX.
    """
    estado_id = request.GET.get('estado_id')
    if not estado_id:
        return JsonResponse({'cidades': []})
    try:
        cidades = Cidade.objects.filter(
            estado_cidade_id=estado_id
        ).order_by('nome_cidade')
        return JsonResponse({
            'cidades': [{'id': c.id, 'nome': c.nome_cidade} for c in cidades]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ══════════════════════════════════════════
# HELPERS PRIVADOS — empresa
# ══════════════════════════════════════════

def _atualizar_empresa(request, user):
    empresa = Empresa.objects.get(user=user)

    empresa.nomefantasia = request.POST.get('nomefantasia', empresa.nomefantasia)
    empresa.razao_social = request.POST.get('razao_social', empresa.razao_social)
    empresa.cnpj = request.POST.get('cnpj', empresa.cnpj)
    empresa.tipo_empresa = request.POST.get('tipo_empresa', empresa.tipo_empresa)
    empresa.segmento = request.POST.get('segmento', empresa.segmento)
    empresa.telefone = request.POST.get('telefone', empresa.telefone)
    empresa.cep = request.POST.get('cep', empresa.cep)
    empresa.rua = request.POST.get('rua', empresa.rua)
    empresa.numero = request.POST.get('numero', empresa.numero) or 0
    empresa.complemento = request.POST.get('complemento', empresa.complemento)

    estado_id = request.POST.get('estado')
    cidade_id = request.POST.get('cidade')
    if estado_id:
        empresa.estado = Estado.objects.get(id=estado_id)
    if cidade_id:
        empresa.cidade = Cidade.objects.get(id=cidade_id)

    empresa.save()
    _atualizar_hubs_empresa(request, empresa)


def _atualizar_hubs_empresa(request, empresa):
    hubs_selecionados = request.POST.getlist('hubs')
    hubs_ids = [int(h) for h in hubs_selecionados if h]
    EmpresaHub.objects.filter(empresa=empresa).delete()
    for hub_id in hubs_ids:
        try:
            EmpresaHub.objects.create(empresa=empresa, hub=Hub.objects.get(id=hub_id))
        except Hub.DoesNotExist:
            pass


# ══════════════════════════════════════════
# HELPERS PRIVADOS — usuário
# ══════════════════════════════════════════

def _atualizar_usuario(request, user):
    usuario = Usuario.objects.get(user=user)

    # Dados pessoais
    usuario.nome_social = request.POST.get('nome_social') or None
    usuario.data_nascimento = _parse_date(request.POST.get('data_nascimento')) or usuario.data_nascimento
    usuario.genero = request.POST.get('genero', usuario.genero)
    usuario.estado_civil = request.POST.get('estado_civil', usuario.estado_civil)
    usuario.nacionalidade = request.POST.get('nacionalidade', usuario.nacionalidade)
    usuario.telefone = request.POST.get('telefone', usuario.telefone)

    # Endereço
    usuario.cep = request.POST.get('cep', usuario.cep)
    usuario.rua = request.POST.get('rua', usuario.rua)
    usuario.bairro = request.POST.get('bairro', usuario.bairro)
    usuario.numero = request.POST.get('numero', usuario.numero)
    usuario.complemento = request.POST.get('complemento') or None

    estado_id = request.POST.get('estado')
    cidade_id = request.POST.get('cidade')
    if estado_id:
        usuario.estado = Estado.objects.get(id=estado_id)
    if cidade_id:
        usuario.cidade = Cidade.objects.get(id=cidade_id)

    # Objetivo profissional
    usuario.cargo_pretendido = request.POST.get('cargo_pretendido') or None
    usuario.area_interesse = request.POST.get('area_interesse') or None
    usuario.pretensao_salarial = _parse_decimal(request.POST.get('pretensao_salarial'))
    usuario.disponibilidade = request.POST.get('disponibilidade') or None
    usuario.remoto = request.POST.get('remoto') == 'on'

    # Redes sociais
    usuario.linkedin = request.POST.get('linkedin') or None
    usuario.github = request.POST.get('github') or None
    usuario.instagram = request.POST.get('instagram') or None
    usuario.facebook = request.POST.get('facebook') or None
    usuario.site_pessoal = request.POST.get('site_pessoal') or None

    # Formação acadêmica (3 blocos)
    for n in ('1', '2', '3'):
        setattr(usuario, f'instituicao_nome{n}', request.POST.get(f'instituicao_nome{n}') or None)
        setattr(usuario, f'grau_escolaridade{n}', request.POST.get(f'grau_escolaridade{n}') or None)
        setattr(usuario, f'curso_graduacao{n}', request.POST.get(f'curso_graduacao{n}') or None)
        setattr(usuario, f'situacao_academica{n}', request.POST.get(f'situacao_academica{n}') or None)
        setattr(usuario, f'data_acad_inicio{n}', _parse_date(request.POST.get(f'data_acad_inicio{n}')))
        setattr(usuario, f'data_acad_fim{n}', _parse_date(request.POST.get(f'data_acad_fim{n}')))

    # Competências (3 blocos)
    for n in ('1', '2', '3'):
        setattr(usuario, f'competencias_tecnicas{n}', request.POST.get(f'competencias_tecnicas{n}') or None)
        setattr(usuario, f'competencias_comportamentais{n}', request.POST.get(f'competencias_comportamentais{n}') or None)

    # Inclusão e acessibilidade
    usuario.pessoa_com_deficiencia = request.POST.get('pessoa_com_deficiencia') == 'on'
    usuario.tipo_deficiencia = request.POST.get('tipo_deficiencia') or None
    usuario.necessidade_adaptacao = request.POST.get('necessidade_adaptacao') or None

    # Informações adicionais
    usuario.interesses_hobbies = request.POST.get('interesses_hobbies') or None

    # Interesses de compra usados no matching de produtos e hubs.
    # Cada slot do formulário carrega o id do registro que edita (campo oculto
    # interesse_idN), então desativar um interesse não faz os demais slots
    # passarem a editar o registro errado.
    interesses_por_id = {
        interesse.pk: interesse
        for interesse in InteresseCompra.objects.filter(usuario=usuario)
    }
    for indice in range(1, 4):
        categoria = (request.POST.get(f'categoria_interesse{indice}') or '').strip()
        descricao = (request.POST.get(f'descricao_interesse{indice}') or '').strip()
        preco_maximo = _parse_decimal(request.POST.get(f'preco_maximo{indice}'))

        interesse_id = _parse_int(request.POST.get(f'interesse_id{indice}'))
        # Só aceita ids que pertencem ao próprio usuário
        interesse = interesses_por_id.get(interesse_id) if interesse_id else None

        if categoria or descricao or preco_maximo is not None:
            if interesse is None:
                interesse = InteresseCompra(usuario=usuario)
            interesse.categoria_interesse = categoria
            interesse.descricao_interesse = descricao
            interesse.preco_maximo = preco_maximo
            interesse.isActive = True
            interesse.save()
        elif interesse is not None and interesse.isActive:
            interesse.isActive = False
            interesse.save()

    # Anexos
    if 'curriculo_pdf' in request.FILES:
        usuario.curriculo_pdf = request.FILES['curriculo_pdf']
    if 'carta_apresentacao' in request.FILES:
        usuario.carta_apresentacao = request.FILES['carta_apresentacao']

    usuario.save()

    _atualizar_experiencias(request, usuario)
    _atualizar_cursos(request, usuario)
    _atualizar_idiomas(request, usuario)


def _atualizar_experiencias(request, usuario):
    exp, _ = ExperienciaProfissional.objects.get_or_create(usuario=usuario)
    for n in ('1', '2', '3'):
        setattr(exp, f'nome_empresa{n}', request.POST.get(f'nome_empresa{n}') or None)
        setattr(exp, f'cargo{n}', request.POST.get(f'cargo{n}') or None)
        setattr(exp, f'data_inicio{n}', _parse_date(request.POST.get(f'data_inicio{n}')))
        setattr(exp, f'data_fim{n}', _parse_date(request.POST.get(f'data_fim{n}')))
    exp.save()


def _atualizar_cursos(request, usuario):
    curso, _ = CursoExtraCurricular.objects.get_or_create(usuario=usuario)
    for n in ('1', '2', '3'):
        setattr(curso, f'nome_curso{n}', request.POST.get(f'nome_curso{n}') or None)
        setattr(curso, f'instituicao{n}', request.POST.get(f'instituicao{n}') or None)
        setattr(curso, f'carga_horaria{n}', _parse_int(request.POST.get(f'carga_horaria{n}')))
        setattr(curso, f'data_conclusao{n}', _parse_date(request.POST.get(f'data_conclusao{n}')))
        setattr(curso, f'link_certificado{n}', request.POST.get(f'link_certificado{n}') or None)
    curso.save()


def _atualizar_idiomas(request, usuario):
    idioma, _ = Idioma.objects.get_or_create(usuario=usuario)
    for n in ('1', '2', '3'):
        setattr(idioma, f'idioma{n}', request.POST.get(f'idioma{n}') or None)
        setattr(idioma, f'nivel_fluencia{n}', request.POST.get(f'nivel_fluencia{n}') or None)
    idioma.save()


# ══════════════════════════════════════════
# HELPERS DE PARSING
# ══════════════════════════════════════════

def _parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None


def _parse_decimal(value_str):
    if not value_str:
        return None
    try:
        return Decimal(value_str)
    except (InvalidOperation, ValueError):
        return None


def _parse_int(value_str):
    if not value_str:
        return None
    try:
        return int(value_str)
    except ValueError:
        return None