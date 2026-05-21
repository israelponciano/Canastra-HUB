# matching/text_builders.py
from __future__ import annotations

from core.models import Usuario, ExperienciaProfissional
from vagas.models import Vagas, CursoVaga


def build_resume_text(usuario: Usuario) -> str:
    parts = []

    if usuario.cargo_pretendido:
        parts.append(f"objetivo: {usuario.cargo_pretendido}")
    if usuario.area_interesse:
        parts.append(f"área de interesse: {usuario.area_interesse}")
    if usuario.disponibilidade:
        parts.append(f"disponibilidade: {usuario.disponibilidade}")
    if usuario.remoto:
        parts.append("disponível para trabalho remoto")
    if usuario.curso:
        parts.append(f"curso: {usuario.curso}")

    for n in ('1', '2', '3'):
        instituicao = getattr(usuario, f'instituicao_nome{n}')
        grau = getattr(usuario, f'grau_escolaridade{n}')
        curso = getattr(usuario, f'curso_graduacao{n}')
        situacao = getattr(usuario, f'situacao_academica{n}')
        if any([instituicao, grau, curso]):
            linha = " ".join(filter(None, [grau, curso, "em", instituicao, situacao]))
            parts.append(f"formação: {linha}")

    for n in ('1', '2', '3'):
        tec = getattr(usuario, f'competencias_tecnicas{n}')
        comp = getattr(usuario, f'competencias_comportamentais{n}')
        if tec:
            parts.append(f"competências técnicas: {tec}")
        if comp:
            parts.append(f"competências comportamentais: {comp}")

    try:
        exp = ExperienciaProfissional.objects.get(usuario=usuario)
        for n in ('1', '2', '3'):
            cargo = getattr(exp, f'cargo{n}')
            empresa = getattr(exp, f'nome_empresa{n}')
            if cargo or empresa:
                parts.append(f"experiência: {cargo or ''} em {empresa or ''}")
    except ExperienciaProfissional.DoesNotExist:
        pass

    if usuario.interesses_hobbies:
        parts.append(f"interesses: {usuario.interesses_hobbies}")

    return "\n".join(parts)


def build_job_text(vaga: Vagas) -> str:
    parts = []

    if vaga.cargo_vaga:
        parts.append(f"cargo: {vaga.cargo_vaga}")
    if vaga.descricao_vaga:
        parts.append(f"descrição: {vaga.descricao_vaga}")
    if vaga.requisito_vaga:
        parts.append(f"requisitos: {vaga.requisito_vaga}")
    if vaga.local:
        parts.append(f"local: {vaga.local}")

    cursos = CursoVaga.objects.filter(vaga=vaga).values_list('curso', flat=True)
    if cursos:
        parts.append(f"cursos desejados: {', '.join(filter(None, cursos))}")

    try:
        parts.append(f"empresa: {vaga.empresa.nomefantasia}")
        if vaga.empresa.segmento:
            parts.append(f"segmento: {vaga.empresa.segmento}")
    except Exception:
        pass

    return "\n".join(parts)
