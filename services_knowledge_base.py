import json
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


BASE_DIR = Path(__file__).resolve().parent / "data" / "base_inteligente"
HISTORICAL_BASE_PATH = BASE_DIR / "base_atendimento_seplan_estatistica_v01.jsonl"
CHECKLIST_BASE_PATH = BASE_DIR / "base_auxiliar_checklists_seplan_v01.jsonl"
NORMATIVE_BASE_PATH = BASE_DIR / "base_normativa_seplan_v01.jsonl"
CORRECTED_RESPONSES_PATH = BASE_DIR / "respostas_corrigidas_99_100_v02.jsonl"
QA_BASE_PATH = BASE_DIR / "perguntas_respostas_seplan_v02.jsonl"

MIN_CONFIDENCE_SCORE = 0.30
MIN_TOKEN_OVERLAP = 0.10
MIN_CORRECTED_SCORE = 0.25

SOURCE_BONUS = {
    "corrected": 0.20,
    "qa": 0.16,
    "checklist": 0.08,
    "historical": 0.04,
    "normative": 0.02,
}


@lru_cache(maxsize=1)
def load_knowledge_base() -> List[Dict[str, Any]]:
    return _load_jsonl(HISTORICAL_BASE_PATH)


@lru_cache(maxsize=1)
def load_checklist_base() -> List[Dict[str, Any]]:
    return _load_jsonl(CHECKLIST_BASE_PATH)


@lru_cache(maxsize=1)
def load_normative_base() -> List[Dict[str, Any]]:
    return _load_jsonl(NORMATIVE_BASE_PATH)


@lru_cache(maxsize=1)
def load_corrected_responses() -> List[Dict[str, Any]]:
    return _load_jsonl(CORRECTED_RESPONSES_PATH)


@lru_cache(maxsize=1)
def load_qa_base() -> List[Dict[str, Any]]:
    return _load_jsonl(QA_BASE_PATH)


def load_intelligent_bases() -> Dict[str, List[Dict[str, Any]]]:
    return {
        "normative": load_normative_base(),
        "checklist": load_checklist_base(),
        "historical": load_knowledge_base(),
        "corrected": load_corrected_responses(),
        "qa": load_qa_base(),
    }


def normalize_semantic_text(text: str) -> str:
    if not text:
        return ""

    normalized = unicodedata.normalize("NFKD", str(text).casefold().strip())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    normalized = "".join(char if char.isalnum() else " " for char in normalized)
    return " ".join(normalized.split())


def score_knowledge_item(message: str, item: dict) -> float:
    message_text = normalize_semantic_text(message)
    message_tokens = _tokenize(message_text)
    if not message_tokens:
        return 0.0

    weighted_parts = (
        (_item_intent_text(item), 0.14),
        (item.get("pergunta_padrao"), 0.13),
        (item.get("grupo_pergunta"), 0.12),
        (item.get("grupo"), 0.10),
        (item.get("item"), 0.10),
        (item.get("pergunta"), 0.13),
        (" ".join(_as_text_list(item.get("variacoes_usuario"))), 0.15),
        (" ".join(_as_text_list(item.get("termos_associados"))), 0.10),
        (" ".join(_as_text_list(item.get("gatilhos_usuario"))), 0.18),
        (" ".join(_as_text_list(item.get("subassuntos_fonte"))), 0.06),
        (item.get("resposta_consolidada"), 0.04),
        (item.get("resposta_whatsapp"), 0.08),
        (item.get("resposta_base_whatsapp"), 0.07),
        (item.get("resposta_corrigida"), 0.10),
        (item.get("regra_operacional"), 0.07),
        (item.get("tema"), 0.07),
        (item.get("texto_base_resumido"), 0.04),
        (item.get("interpretacao_tecnica"), 0.04),
        (" ".join(_as_text_list(item.get("quando_usar"))), 0.07),
        (" ".join(_as_text_list(item.get("tags"))), 0.10),
    )

    semantic_score = 0.0
    for value, weight in weighted_parts:
        semantic_score += _token_overlap_score(message_tokens, normalize_semantic_text(str(value or ""))) * weight

    phrase_bonus = _phrase_bonus(message_text, item)
    if semantic_score <= 0 and phrase_bonus <= 0:
        return 0.0

    confidence = _item_confidence(item)
    frequency = min(_safe_float(item.get("frequencia"), default=0.0) / 1000.0, 1.0)

    final_score = (semantic_score * 0.70) + (phrase_bonus * 0.18) + (confidence * 0.08) + (frequency * 0.04)
    return round(min(final_score, 1.0), 4)


def search_knowledge_base(message: str, limit: int = 3) -> List[Dict[str, Any]]:
    scored_items: List[Dict[str, Any]] = []
    for source_type, items in _source_items():
        for item in items:
            score = score_knowledge_item(message, item)
            if score <= 0:
                continue
            scored_items.append(_enrich_item(item=item, source_type=source_type, score=score))

    scored_items.sort(key=_sort_key, reverse=True)
    return scored_items[:limit]


def select_best_pattern(message: str) -> Optional[Dict[str, Any]]:
    results = search_knowledge_base(message, limit=1000)
    if not results:
        return None

    message_tokens = _tokenize(normalize_semantic_text(message))
    for result in results:
        if result.get("_source_type") != "corrected":
            continue
        if _is_safe_candidate(result, message_tokens, MIN_CORRECTED_SCORE):
            return result

    for result in results:
        if _is_safe_candidate(result, message_tokens, MIN_CONFIDENCE_SCORE):
            return result

    return None


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    items: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            clean_line = line.strip()
            if not clean_line:
                continue
            items.append(json.loads(clean_line))

    return items


def _source_items() -> List[tuple[str, List[Dict[str, Any]]]]:
    return [
        ("corrected", load_corrected_responses()),
        ("qa", load_qa_base()),
        ("checklist", load_checklist_base()),
        ("historical", load_knowledge_base()),
        ("normative", load_normative_base()),
    ]


def _enrich_item(item: dict, source_type: str, score: float) -> Dict[str, Any]:
    enriched = dict(item)
    intent = _item_intent(enriched)
    enriched["_source_type"] = source_type
    enriched["_score"] = score
    enriched["_confidence"] = _item_confidence(enriched)
    enriched["_response_text"] = _response_text(enriched, source_type)
    enriched["_source_patterns"] = _source_patterns(enriched, source_type)
    enriched["_source_protocols"] = _source_protocols(enriched, source_type)
    enriched["_source_checklists"] = _source_checklists(enriched, source_type)
    enriched["_source_normative"] = _source_normative(enriched, source_type, intent)
    enriched["_intent"] = intent
    return enriched


def _sort_key(item: Dict[str, Any]) -> tuple[float, float, float, float]:
    score = _safe_float(item.get("_score"), default=0.0)
    source_type = str(item.get("_source_type") or "")
    bonus = SOURCE_BONUS.get(source_type, 0.0)
    if source_type == "normative" and score >= 0.65:
        bonus = 0.25

    return (
        score + bonus,
        score,
        _safe_float(item.get("_confidence"), default=0.0),
        _safe_float(item.get("frequencia"), default=0.0),
    )


def _is_safe_candidate(item: Dict[str, Any], message_tokens: Set[str], min_score: float) -> bool:
    item_tokens = _knowledge_item_tokens(item)
    overlap = len(message_tokens.intersection(item_tokens)) / max(len(message_tokens), 1)
    confidence = _safe_float(item.get("_confidence"), default=0.0)

    if item.get("_score", 0.0) < min_score:
        return False
    if confidence < 0.5:
        return False
    if overlap < MIN_TOKEN_OVERLAP:
        return False
    return True


def _response_text(item: dict, source_type: str) -> str:
    if source_type == "qa":
        return str(item.get("resposta_whatsapp") or "")
    if source_type == "corrected":
        return str(item.get("resposta_corrigida") or "")
    if source_type == "checklist":
        return str(item.get("resposta_base_whatsapp") or item.get("regra_operacional") or "")
    if source_type == "normative":
        return str(item.get("resposta_whatsapp_sugerida") or item.get("interpretacao_tecnica") or "")
    return str(item.get("resposta_consolidada") or "")


def _source_patterns(item: dict, source_type: str) -> List[str]:
    if source_type in {"qa", "corrected"}:
        values = [item.get("pergunta")]
        if source_type == "qa":
            values = [item.get("pergunta_padrao"), *_as_text_list(item.get("variacoes_usuario"))[:2]]
    elif source_type == "checklist":
        values = [item.get("grupo"), item.get("item")]
    elif source_type == "normative":
        values = [item.get("tema"), item.get("fonte_normativa")]
    else:
        values = [item.get("grupo_pergunta"), item.get("pergunta_padrao")]

    return _clean_list(values)


def _source_protocols(item: dict, source_type: str) -> List[str]:
    if source_type == "qa":
        return _clean_list(_as_text_list(item.get("source_protocols")))
    if source_type != "historical":
        return []
    return _clean_list(_as_text_list(item.get("protocolos_fonte")))


def _source_checklists(item: dict, source_type: str) -> List[str]:
    if source_type == "qa":
        return _clean_list(_as_text_list(item.get("source_checklists")))
    if source_type != "checklist":
        return []
    label = " - ".join(_clean_list([item.get("id"), item.get("item")]))
    return [label] if label else []


def _source_normative(item: dict, source_type: str, intent: str) -> List[str]:
    if source_type == "qa":
        return _clean_list(_as_text_list(item.get("source_normative")))
    if source_type == "normative":
        return _clean_list([item.get("id"), item.get("fonte_normativa")])

    explicit_sources = _clean_list(_as_text_list(item.get("base_normativa_relacionada")))
    if explicit_sources:
        return explicit_sources

    related = []
    for normative in load_normative_base():
        intents = {normalize_semantic_text(value) for value in _as_text_list(normative.get("intent_relacionadas"))}
        if normalize_semantic_text(intent) in intents:
            related.extend(_clean_list([normative.get("id")]))

    return related[:3]


def _item_intent(item: dict) -> str:
    if item.get("intent"):
        return str(item.get("intent"))

    related = _as_text_list(item.get("intent_relacionadas"))
    return str(related[0]) if related else "DESCONHECIDA"


def _item_intent_text(item: dict) -> str:
    values = [item.get("intent"), *_as_text_list(item.get("intent_relacionadas"))]
    return " ".join(str(value) for value in values if value)


def _item_confidence(item: dict) -> float:
    for field_name in ("confianca_final", "nivel_confianca", "confianca_estatistica", "confianca_normativa"):
        value = item.get(field_name)
        if value is None:
            continue
        parsed = _safe_float(value, default=-1.0)
        if parsed >= 0:
            return min(parsed, 1.0)

        normalized = normalize_semantic_text(str(value))
        if normalized in {"alta", "alto"}:
            return 0.9
        if normalized in {"media", "medio"}:
            return 0.65
        if normalized in {"baixa", "baixo"}:
            return 0.4

    return 0.6


def _as_text_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if isinstance(value, str) and "|" in value:
        return [part.strip() for part in value.split("|") if part.strip()]
    return [str(value)]


def _clean_list(values: Any) -> List[str]:
    clean_values = []
    for value in _as_text_list(values):
        text = str(value or "").strip()
        if text and text not in clean_values:
            clean_values.append(text)
    return clean_values


def _tokenize(text: str) -> Set[str]:
    ignored = {
        "a",
        "ao",
        "aos",
        "as",
        "com",
        "como",
        "da",
        "das",
        "de",
        "do",
        "dos",
        "e",
        "em",
        "eu",
        "meu",
        "minha",
        "o",
        "os",
        "para",
        "por",
        "preciso",
        "quais",
        "que",
        "quero",
        "saber",
        "um",
        "uma",
    }
    return {token for token in text.split() if len(token) > 2 and token not in ignored}


def _token_overlap_score(message_tokens: Set[str], candidate_text: str) -> float:
    candidate_tokens = _tokenize(candidate_text)
    if not candidate_tokens:
        return 0.0

    intersection = message_tokens.intersection(candidate_tokens)
    return len(intersection) / max(len(message_tokens), 1)


def _phrase_bonus(message_text: str, item: dict) -> float:
    candidates = [
        item.get("grupo_pergunta"),
        item.get("pergunta_padrao"),
        item.get("grupo"),
        item.get("item"),
        item.get("pergunta"),
        item.get("tema"),
        *_as_text_list(item.get("variacoes_usuario")),
        *_as_text_list(item.get("gatilhos_usuario")),
        *_as_text_list(item.get("quando_usar")),
    ]
    for candidate in candidates:
        candidate_text = normalize_semantic_text(str(candidate or ""))
        if candidate_text and (candidate_text in message_text or message_text in candidate_text):
            return 1.0
    return 0.0


def _knowledge_item_tokens(item: dict) -> Set[str]:
    text_parts = [
        _item_intent_text(item),
        item.get("grupo_pergunta"),
        item.get("pergunta_padrao"),
        item.get("grupo"),
        item.get("item"),
        item.get("pergunta"),
        item.get("tema"),
        item.get("resposta_whatsapp"),
        " ".join(_as_text_list(item.get("variacoes_usuario"))),
        " ".join(_as_text_list(item.get("termos_associados"))),
        " ".join(_as_text_list(item.get("gatilhos_usuario"))),
        " ".join(_as_text_list(item.get("tags"))),
        " ".join(_as_text_list(item.get("subassuntos_fonte"))),
        " ".join(_as_text_list(item.get("quando_usar"))),
        item.get("regra_operacional"),
        item.get("resposta_base_whatsapp"),
    ]
    return _tokenize(normalize_semantic_text(" ".join(str(part or "") for part in text_parts)))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
