import json
import unicodedata
from typing import List

from sqlmodel import Session

from models import AttendanceMessage
from schemas import AgentMessageRequest, AgentMessageResponse
from services_knowledge_base import search_knowledge_base, select_best_pattern


PRODUCT_NAME = "Agente WhatsApp SEPLAN"
CONTACT_INSTRUCTION = "Em caso de dúvida, entre em contato com a SEPLAN."
FALLBACK_RESPONSE = (
    "Não encontrei base suficiente para responder com segurança. "
    "Em caso de dúvida, entre em contato com a SEPLAN."
)


def handle_agent_message(session: Session, payload: AgentMessageRequest) -> AgentMessageResponse:
    normalized_message = normalize_agent_text(payload.message)
    ranked_patterns = search_knowledge_base(payload.message, limit=8)
    best_pattern = select_best_pattern(payload.message)

    if best_pattern:
        detected_intent = str(best_pattern.get("_intent") or best_pattern.get("intent") or "DESCONHECIDA")
        supporting_patterns = filter_supporting_patterns(best_pattern, ranked_patterns)
        response_text = build_response_text(best_pattern)
        confidence_score = round(
            float(best_pattern.get("_confidence") or best_pattern.get("_score") or 0.0),
            2,
        )
        source_patterns = merge_source_values(best_pattern, supporting_patterns, "_source_patterns")
        source_protocols = merge_source_values(best_pattern, supporting_patterns, "_source_protocols", limit=6)
        source_checklists = merge_source_values(best_pattern, supporting_patterns, "_source_checklists", limit=6)
        source_normative = merge_source_values(best_pattern, supporting_patterns, "_source_normative", limit=6)
        if source_protocols:
            response_text = remove_individual_protocol_language(response_text)
        answer_source = str(best_pattern.get("_source_type") or "knowledge_base")
        fallback_contact = False
        contact_instruction = None
        knowledge_base_used = True
        needs_human_review = confidence_score < 0.7
    else:
        detected_intent = "DESCONHECIDA"
        response_text = FALLBACK_RESPONSE
        confidence_score = 0.2
        source_patterns = []
        source_protocols = []
        source_checklists = []
        source_normative = []
        answer_source = "fallback"
        fallback_contact = True
        contact_instruction = CONTACT_INSTRUCTION
        knowledge_base_used = False
        needs_human_review = True

    log = AttendanceMessage(
        channel=payload.channel,
        phone_number=payload.phone_number,
        inbound_text=payload.message,
        normalized_text=normalized_message,
        detected_intent=detected_intent,
        response_text=response_text,
        confidence_score=confidence_score,
        source_protocols=json.dumps(source_protocols, ensure_ascii=False),
        needs_human_review=needs_human_review,
        source_checklists=json.dumps(source_checklists, ensure_ascii=False),
        source_normative=json.dumps(source_normative, ensure_ascii=False),
        answer_source=answer_source,
        fallback_contact=fallback_contact,
        knowledge_base_used=knowledge_base_used,
    )
    session.add(log)
    session.commit()

    return AgentMessageResponse(
        channel=payload.channel,
        phone_number=payload.phone_number,
        detected_intent=detected_intent,
        response_text=response_text,
        confidence_score=confidence_score,
        source_patterns=source_patterns,
        source_protocols=source_protocols,
        source_checklists=source_checklists,
        source_normative=source_normative,
        answer_source=answer_source,
        needs_human_review=needs_human_review,
        fallback_contact=fallback_contact,
        contact_instruction=contact_instruction,
        knowledge_base_used=knowledge_base_used,
    )


def normalize_agent_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.casefold().strip())
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = "".join(char if char.isalnum() else " " for char in text)
    return " ".join(text.split())


def build_source_patterns(pattern: dict) -> List[str]:
    values = pattern.get("_source_patterns")
    if values:
        return [str(value) for value in values if value]

    fallback_values = [
        pattern.get("grupo_pergunta"),
        pattern.get("pergunta_padrao"),
        pattern.get("grupo"),
        pattern.get("item"),
        pattern.get("pergunta"),
    ]
    return [str(value) for value in fallback_values if value]


def filter_supporting_patterns(best_pattern: dict, ranked_patterns: List[dict]) -> List[dict]:
    best_intent = normalize_agent_text(str(best_pattern.get("_intent") or best_pattern.get("intent") or ""))
    supporting: List[dict] = []
    for pattern in ranked_patterns:
        if pattern is best_pattern:
            continue

        source_type = str(pattern.get("_source_type") or "")
        pattern_intent = normalize_agent_text(str(pattern.get("_intent") or pattern.get("intent") or ""))
        if pattern_intent == best_intent or source_type == "normative":
            supporting.append(pattern)

    return supporting


def merge_source_values(best_pattern: dict, supporting_patterns: List[dict], key: str, limit: int = 8) -> List[str]:
    values: List[str] = []
    for pattern in [best_pattern, *supporting_patterns]:
        for value in pattern.get(key, []) or []:
            text = str(value).strip()
            if text and text not in values:
                values.append(text)
            if len(values) >= limit:
                return values

    return values


def build_response_text(pattern: dict) -> str:
    text = str(pattern.get("_response_text") or FALLBACK_RESPONSE).strip()
    if not text:
        return FALLBACK_RESPONSE

    return text


def remove_individual_protocol_language(text: str) -> str:
    replacements = {
        "documentação do protocolo": "documentação enviada",
        "documentacao do protocolo": "documentacao enviada",
        "no protocolo": "no atendimento",
        "do protocolo": "do atendimento",
        "protocolo": "atendimento",
    }
    clean_text = text
    for old, new in replacements.items():
        clean_text = clean_text.replace(old, new)
        clean_text = clean_text.replace(old.capitalize(), new.capitalize())
    return clean_text
