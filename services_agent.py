import json
import unicodedata
from typing import List, Optional

from sqlmodel import Session

from models import AttendanceMessage
from schemas import AgentMessageRequest, AgentMessageResponse
from services_knowledge_base import search_knowledge_base, select_best_pattern


PRODUCT_NAME = "SEPLAN IA — Apoio Técnico ao Atendimento"
SEPLAN_CONTACT = {
    "whatsapp": "(47) 9 8841-6225",
    "phone": "(47) 3443-8826",
    "email": "atendimento.seplan@itapoa.sc.gov.br",
    "hours": "07h30 às 13h30",
}
FALLBACK_RESPONSE = (
    "Não encontrei base suficiente para responder com segurança.\n\n"
    "Para evitar orientação errada, confirme com a SEPLAN:\n"
    f"WhatsApp: {SEPLAN_CONTACT['whatsapp']}\n"
    f"Telefone: {SEPLAN_CONTACT['phone']}\n"
    f"E-mail: {SEPLAN_CONTACT['email']}\n"
    f"Atendimento: {SEPLAN_CONTACT['hours']}.\n\n"
    "Se possível, envie também: descrição do pedido, endereço, balneário, "
    "quadra, lote e fotos quando houver."
)


CONTACT_INTENTS = {
    "DECLARACAO_NAO_OPOSICAO",
    "DECLARACAO_NAO_OPOSICAO_AGUA",
    "DECLARACAO_NAO_OPOSICAO_LUZ",
    "GUIA_REBAIXADA",
    "DRENAGEM",
    "DENUNCIA",
    "DENUNCIA_OBRA_IRREGULAR",
    "DESCONHECIDA",
}


def handle_agent_message(session: Session, payload: AgentMessageRequest) -> AgentMessageResponse:
    normalized_message = normalize_agent_text(payload.message)
    ranked_patterns = search_knowledge_base(payload.message, limit=8)
    best_pattern = select_best_pattern(payload.message)

    if best_pattern:
        detected_intent = str(best_pattern.get("_intent") or best_pattern.get("intent") or "DESCONHECIDA")
        supporting_patterns = filter_supporting_patterns(best_pattern, ranked_patterns)
        response_text = sanitize_public_response(build_response_text(best_pattern))
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
        knowledge_base_used = True
        needs_human_review = confidence_score < 0.7
        include_contact = should_include_contact(detected_intent, confidence_score, needs_human_review)
        response_text = sanitize_public_response(
            professionalize_response_text(
                response_text=response_text,
                detected_intent=detected_intent,
                include_contact=include_contact,
            )
        )
        contact_instruction = build_contact_block() if include_contact else None
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
        contact_instruction = build_contact_block()
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


def sanitize_public_response(text: str) -> str:
    """Remove termos de bastidor antes de mostrar a resposta ao cidadão."""
    replacements = {
        "dentro do prazo indicado no checklist da SEPLAN": "atualizado para análise da SEPLAN",
        "dentro do prazo indicado no checklist": "atualizado para análise",
        "conforme checklist da SEPLAN": "para análise da SEPLAN",
        "segundo o checklist da SEPLAN": "para análise da SEPLAN",
        "no checklist da SEPLAN": "na análise da SEPLAN",
        "checklist da SEPLAN": "análise da SEPLAN",
        "checklist interno": "análise técnica",
        "checklists internos": "critérios técnicos",
        "checklists técnicos": "critérios técnicos",
        "checklist": "análise técnica",
        "base histórica": "registros da SEPLAN",
        "base inteligente": "sistema da SEPLAN",
        "fonte operacional": "orientação interna",
        "padrões históricos": "registros anteriores da SEPLAN",
        "últimos trâmites": "registros anteriores",
        "ultimos tramites": "registros anteriores",
    }
    clean_text = text
    for old, new in replacements.items():
        clean_text = clean_text.replace(old, new)
        clean_text = clean_text.replace(old.capitalize(), new.capitalize())
        clean_text = clean_text.replace(old.upper(), new.upper())
    return clean_text


def should_include_contact(detected_intent: str, confidence_score: float, needs_human_review: bool) -> bool:
    normalized_intent = str(detected_intent or "").upper()
    return (
        needs_human_review
        or confidence_score < 0.75
        or normalized_intent in CONTACT_INTENTS
    )


def professionalize_response_text(
    response_text: str,
    detected_intent: str,
    include_contact: bool,
) -> str:
    parts = [response_text.strip()]
    info_hint = build_required_info_hint(detected_intent)
    if info_hint and info_hint not in response_text:
        parts.append(info_hint)

    if include_contact:
        contact_block = build_contact_block()
        if contact_block not in response_text:
            parts.append(contact_block)

    return "\n\n".join(part for part in parts if part)


def build_contact_block() -> str:
    return (
        "Fale com a SEPLAN:\n"
        f"WhatsApp: {SEPLAN_CONTACT['whatsapp']}\n"
        f"Telefone: {SEPLAN_CONTACT['phone']}\n"
        f"E-mail: {SEPLAN_CONTACT['email']}\n"
        f"Atendimento: {SEPLAN_CONTACT['hours']}."
    )


def build_required_info_hint(intent: Optional[str]) -> str:
    normalized_intent = str(intent or "").upper()
    hints = {
        "HABITE_SE": (
            "Para agilizar, informe o número do atendimento, se já existir, e os dados do imóvel: "
            "alvará de construção, balneário, quadra, lote e cadastro ou inscrição imobiliária."
        ),
        "ALVARA_CONSTRUCAO": (
            "Para agilizar, tenha em mãos os dados do imóvel: balneário, quadra, lote, "
            "cadastro ou inscrição imobiliária, tipo de obra e documentos do imóvel."
        ),
        "ALVARA_ATENDIMENTO": (
            "Para agilizar, tenha em mãos os dados do imóvel: balneário, quadra, lote, "
            "cadastro ou inscrição imobiliária, tipo de obra e documentos do imóvel."
        ),
        "DECLARACAO_NAO_OPOSICAO": (
            "Para análise, informe balneário, quadra, lote, cadastro ou inscrição imobiliária "
            "e tenha a comprovação de vínculo ou dominialidade do imóvel."
        ),
        "DECLARACAO_NAO_OPOSICAO_AGUA": (
            "Para análise, informe balneário, quadra, lote, cadastro ou inscrição imobiliária "
            "e tenha a comprovação de vínculo ou dominialidade do imóvel."
        ),
        "DECLARACAO_NAO_OPOSICAO_LUZ": (
            "Para análise, informe balneário, quadra, lote, cadastro ou inscrição imobiliária "
            "e tenha a comprovação de vínculo ou dominialidade do imóvel."
        ),
        "GUIA_REBAIXADA": (
            "Para análise, informe o endereço, a finalidade do acesso, fotos do local e os dados do imóvel."
        ),
        "DRENAGEM": (
            "Para análise, descreva o problema, informe o endereço, ponto de referência e envie fotos ou vídeos quando houver."
        ),
        "DENUNCIA": (
            "Para análise, informe o endereço, descreva o ocorrido e envie fotos quando houver."
        ),
        "DENUNCIA_OBRA_IRREGULAR": (
            "Para análise, informe o endereço, descreva o ocorrido e envie fotos quando houver."
        ),
        "DESCONHECIDA": (
            "Se possível, envie também: descrição do pedido, endereço, balneário, quadra, lote e fotos quando houver."
        ),
    }
    return hints.get(normalized_intent, "")


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
