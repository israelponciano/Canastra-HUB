from __future__ import annotations

import math
from datetime import date

import numpy as np

# ── Mapeamento ordinal de grau de escolaridade ────────────────────────────────
# Escala alinhada com ESCOLARIDADE em vagas/models.py (0–10):
# 0=Fund.Incompleto 1=Fund.Completo 2=Médio Incompleto 3=Médio Completo
# 4=Técnico 5=Superior Incompleto 6=Superior Completo 7=Pós/MBA 8=Mestrado 9=Doutorado 10=Pós-Doutorado
_EDUCATION_LEVELS: dict[str, int] = {
    "fundamental incompleto": 0,
    "fundamental completo": 1,
    "médio incompleto": 2, "medio incompleto": 2,
    "médio completo": 3, "medio completo": 3, "ensino médio": 3, "ensino medio": 3,
    "técnico": 4, "tecnico": 4, "técnica": 4, "tecnica": 4,
    "superior incompleto": 5,
    "tecnólogo": 6, "tecnologo": 6, "tecnóloga": 6, "tecnologa": 6,
    "tecnológico": 6, "tecnologico": 6,
    "bacharelado": 6, "graduação": 6, "graduacao": 6,
    "licenciatura": 6, "superior completo": 6, "superior": 6,
    "pós-graduação": 7, "pos-graduacao": 7, "pós graduação": 7,
    "especialização": 7, "especializacao": 7, "mba": 7,
    "mestrado": 8, "mestre": 8,
    "doutorado": 9, "doutor": 9, "phd": 9, "ph.d": 9,
    "pós-doutorado": 10, "pos-doutorado": 10,
}

# λ: meia-vida de 36 meses (3 anos) → λ = ln(2)/36
_LAMBDA: float = math.log(2) / 36.0

WEIGHTS: dict[str, float] = {
    "experiencia": 0.45,
    "formacao": 0.30,
    "tecnico": 0.20,
    "hobbies": 0.05,
}

# Score neutro para campos não preenchidos (experiência/formação não são obrigatórios)
_SCORE_SEM_DADOS: float = 0.5


# ── helpers ───────────────────────────────────────────────────────────────────

def _education_to_ordinal(grau: str | None) -> int:
    if not grau:
        return 0
    g = grau.lower().strip()
    for keyword, level in _EDUCATION_LEVELS.items():
        if keyword in g:
            return level
    return 0


def _months_between(start: date, end: date) -> float:
    return max(0.0, (end.year - start.year) * 12.0 + (end.month - start.month))


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    norm_a, norm_b = np.linalg.norm(a), np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def _unit_range(sim: float) -> float:
    """Clamp cosine similarity to [0, 1] — sentence-transformer scores are already non-negative in practice."""
    return max(0.0, min(1.0, sim))


def _job_area_embedding(vaga, model) -> np.ndarray | None:
    """
    Embedding compacto da área da vaga: cargo + requisitos.
    Usado para medir relevância de área em experiência e formação.
    """
    text = " ".join(filter(None, [vaga.cargo_vaga or "", vaga.requisito_vaga or ""]))
    if not text.strip():
        return None
    return model.encode([text], show_progress_bar=False)[0]


# ── componentes de pontuação ──────────────────────────────────────────────────

def score_formacao(usuario, vaga, model, _job_emb: np.ndarray | None = None) -> float:
    """
    Codificação Ordinal Hierárquica com Penalização Unidirecional,
    ponderada pela relevância da área de formação à área da vaga.

    Para cada registro de formação:
      score = relevância × ordinal + (1 − relevância) × neutro(0.5)

    A relevância é o cosseno entre o embedding do curso e o da área da vaga.
    Se a vaga não exige nível → 1.0.
    Se candidato sem dados de formação → 0.5 (neutro).
    """
    n_vaga = int(getattr(vaga, "nivel_formacao_req", 0) or 0)
    if n_vaga <= 0:
        return 1.0

    if _job_emb is None:
        _job_emb = _job_area_embedding(vaga, model)

    best: float | None = None

    for n in ("1", "2", "3"):
        grau = getattr(usuario, f"grau_escolaridade{n}") or ""
        curso = getattr(usuario, f"curso_graduacao{n}") or ""
        if not grau and not curso:
            continue

        n_cand = _education_to_ordinal(grau)
        if n_cand == 0:
            ordinal = 0.0
        elif n_cand >= n_vaga:
            ordinal = 1.0
        else:
            ordinal = 1.0 - (n_vaga - n_cand) / n_vaga

        # Relevância da área de formação à área da vaga
        if _job_emb is not None:
            form_text = " ".join(filter(None, [grau, curso]))
            form_emb = model.encode([form_text], show_progress_bar=False)[0]
            relevance = max(0.0, _cosine(_job_emb, form_emb))
        else:
            relevance = 0.5

        weighted = relevance * ordinal + (1.0 - relevance) * _SCORE_SEM_DADOS
        best = weighted if best is None else max(best, weighted)

    return best if best is not None else _SCORE_SEM_DADOS


def score_experiencia(usuario, vaga, model, _job_emb: np.ndarray | None = None) -> float:
    """
    Overlap Temporal com Decaimento Exponencial e Filtro de Área.

    Cada experiência contribui com:
      duração × e^(−λ·t) × relevância_de_área

    onde relevância_de_área é o cosseno entre o cargo exercido e a área da vaga.

    Casos especiais:
      • Vaga não exige experiência (t_req = 0)  → 1.0
      • Vaga exige, sem dados de datas           → 0.5 (neutro)
    """
    from core.models import ExperienciaProfissional

    t_req = float(getattr(vaga, "anos_experiencia_req", 0.0) or 0.0)
    if t_req <= 0:
        return 1.0

    if _job_emb is None:
        _job_emb = _job_area_embedding(vaga, model)

    today = date.today()
    exp = ExperienciaProfissional.objects.filter(usuario=usuario).first()
    if exp is None:
        return _SCORE_SEM_DADOS

    # Coleta slots com data de início preenchida
    entries = []
    for n in ("1", "2", "3"):
        inicio = getattr(exp, f"data_inicio{n}")
        if not inicio:
            continue
        entries.append({
            "inicio": inicio,
            "fim": getattr(exp, f"data_fim{n}"),
            "cargo": getattr(exp, f"cargo{n}") or "",
        })

    if not entries:
        return _SCORE_SEM_DADOS

    # Batch-encode todos os cargos de uma vez para eficiência
    cargo_texts = [e["cargo"] for e in entries]
    if _job_emb is not None and any(cargo_texts):
        cargo_embs = model.encode(cargo_texts, show_progress_bar=False)
    else:
        cargo_embs = None

    decayed_months = 0.0
    for i, entry in enumerate(entries):
        end = entry["fim"] or today
        duration = _months_between(entry["inicio"], end)
        months_since = _months_between(end, today) if entry["fim"] else 0.0
        temporal_decay = math.exp(-_LAMBDA * months_since)

        if cargo_embs is not None and entry["cargo"]:
            relevance = max(0.0, _cosine(_job_emb, cargo_embs[i]))
        else:
            relevance = 0.5  # neutro se cargo não preenchido

        decayed_months += duration * temporal_decay * relevance

    t_cand = decayed_months / 12.0
    return min(1.0, t_cand / t_req)


def score_tecnico(usuario, vaga, model) -> float:
    """
    Embeddings Densos + Similaridade de Cosseno entre as
    competências técnicas do candidato e os requisitos da vaga.
    Retorna 0.5 (neutro) quando um dos lados estiver vazio.
    """
    skills_cand = " ".join(
        filter(None, [getattr(usuario, f"competencias_tecnicas{n}") or "" for n in ("1", "2", "3")])
    ).strip()
    skills_vaga = (vaga.requisito_vaga or "").strip()

    if not skills_cand or not skills_vaga:
        return 0.5

    a, b = model.encode([skills_cand, skills_vaga], show_progress_bar=False)
    return _unit_range(_cosine(a, b))


def score_hobbies(usuario, vaga, model) -> float:
    """
    Busca Semântica Assimétrica: projeção dos hobbies do candidato
    contra a descrição da vaga.

    Garante um piso de 0.20 para não penalizar candidatos cujos hobbies
    não têm correlação com a área da vaga.
    """
    hobbies = (getattr(usuario, "interesses_hobbies", None) or "").strip()
    descricao = (vaga.descricao_vaga or "").strip()

    if not hobbies or not descricao:
        return 0.25  # baseline neutro

    a, b = model.encode([hobbies, descricao], show_progress_bar=False)
    return max(0.20, _unit_range(_cosine(a, b)))


# ── score composto ────────────────────────────────────────────────────────────

def composite_score(usuario, vaga, model) -> dict:
    """
    Combina os 4 critérios com média ponderada:
      45% experiência · 30% formação · 20% técnico · 5% hobbies

    O embedding da área da vaga é pré-computado uma vez e compartilhado
    entre score_experiencia e score_formacao para evitar encoding redundante.
    """
    job_emb = _job_area_embedding(vaga, model)

    s_exp = score_experiencia(usuario, vaga, model, job_emb)
    s_form = score_formacao(usuario, vaga, model, job_emb)
    s_tech = score_tecnico(usuario, vaga, model)
    s_hob = score_hobbies(usuario, vaga, model)

    total = (
        WEIGHTS["experiencia"] * s_exp
        + WEIGHTS["formacao"] * s_form
        + WEIGHTS["tecnico"] * s_tech
        + WEIGHTS["hobbies"] * s_hob
    )

    return {
        "score": round(total, 4),
        "breakdown": {
            "experiencia": round(s_exp, 4),
            "formacao": round(s_form, 4),
            "tecnico": round(s_tech, 4),
            "hobbies": round(s_hob, 4),
        },
    }
