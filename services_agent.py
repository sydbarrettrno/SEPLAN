import json
import unicodedata
from typing import Dict, List, Sequence, Tuple

from sqlmodel import Session

from models import AttendanceMessage, ProtocolRecord
from schemas import AgentMessageRequest, AgentMessageResponse, AgentSourceProtocol
from services_protocolos import search_protocols


PRODUCT_NAME = "Agente WhatsApp SEPLAN"

INTENT_KEYWORDS: Dict[str, Sequence[str]] = {
    "habite_se": ("habite se", "habite-se", "habite", "habitese"),
    "alvara_construcao": ("alvara construcao", "alvara de construcao", "licenca construcao"),
    "certidao_uso_ocupacao": (
        "certidao uso ocupacao",
        "uso ocupacao",
        "uso do solo",
        "zoneamento",
    ),
    "declaracao_nao_oposicao": (
        "declaracao nao oposicao",
        "nao oposicao",
        "sem oposicao",
    ),
    "guia_rebaixada": ("guia rebaixada", "rebaixamento guia", "baixar guia"),
    "drenagem": ("drenagem", "agua pluvial", "aguas pluviais", "escoamento"),
    "denuncia": ("denuncia", "denunciar", "irregular", "obra irregular"),
}

RESPONSE_TEMPLATES: Dict[str, str] = {
    "habite_se": (
        "Para Habite-se, normalmente o atendimento confere dados do imovel, "
        "alvara de construcao e documentos anexados ao protocolo."
    ),
    "alvara_construcao": (
        "Para alvara de construcao, o atendimento costuma conferir os dados do imovel "
        "e as informacoes anexadas ao protocolo."
    ),
    "certidao_uso_ocupacao": (
        "Para certidao de uso e ocupacao, o atendimento verifica os dados do imovel "
        "e o enquadramento informado no protocolo."
    ),
    "declaracao_nao_oposicao": (
        "Para declaracao de nao oposicao, o atendimento confere o pedido e os dados "
        "apresentados no protocolo."
    ),
    "guia_rebaixada": (
        "Sobre guia rebaixada, o atendimento costuma verificar o local informado "
        "e os dados registrados no protocolo."
    ),
    "drenagem": (
        "Sobre drenagem, o atendimento verifica a situacao descrita, o local e os "
        "registros relacionados na base da SEPLAN."
    ),
    "denuncia": (
        "Para denuncia, posso registrar a orientacao inicial, mas a avaliacao precisa "
        "passar pelo atendimento responsavel."
    ),
    "desconhecida": (
        "Nao consegui identificar com seguranca o tipo de pedido. Posso te encaminhar "
        "para o atendimento conferir melhor."
    ),
}


def handle_agent_message(session: Session, payload: AgentMessageRequest) -> AgentMessageResponse:
    normalized_message = normalize_agent_text(payload.message)
    detected_intent, intent_score = detect_intent(normalized_message)
    source_records = find_source_protocols(session, payload.message, detected_intent)
    source_protocols = [to_source_protocol(record) for record in source_records]
    confidence_score = calculate_confidence(intent_score, source_protocols)
    needs_human_review = True
    response_text = build_response_text(detected_intent, source_protocols)

    log = AttendanceMessage(
        channel=payload.channel,
        phone_number=payload.phone_number,
        inbound_text=payload.message,
        normalized_text=normalized_message,
        detected_intent=detected_intent,
        response_text=response_text,
        confidence_score=confidence_score,
        source_protocols=json.dumps(
            [source.model_dump() for source in source_protocols],
            ensure_ascii=False,
        ),
        needs_human_review=needs_human_review,
    )
    session.add(log)
    session.commit()

    return AgentMessageResponse(
        channel=payload.channel,
        phone_number=payload.phone_number,
        detected_intent=detected_intent,
        response_text=response_text,
        confidence_score=confidence_score,
        source_protocols=source_protocols,
        needs_human_review=needs_human_review,
    )


def normalize_agent_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.casefold().strip())
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = "".join(char if char.isalnum() else " " for char in text)
    return " ".join(text.split())


def detect_intent(normalized_message: str) -> Tuple[str, float]:
    best_intent = "desconhecida"
    best_score = 0.0

    for intent, keywords in INTENT_KEYWORDS.items():
        score = 0.0
        for keyword in keywords:
            normalized_keyword = normalize_agent_text(keyword)
            if normalized_keyword and normalized_keyword in normalized_message:
                score += 1.0
        if score > best_score:
            best_intent = intent
            best_score = score

    if best_intent == "desconhecida":
        return best_intent, 0.0

    return best_intent, min(0.65, 0.35 + (best_score * 0.15))


def find_source_protocols(
    session: Session,
    message: str,
    detected_intent: str,
) -> List[ProtocolRecord]:
    if detected_intent == "desconhecida":
        query = message
    else:
        keywords = " ".join(INTENT_KEYWORDS.get(detected_intent, ()))
        query = f"{message} {detected_intent.replace('_', ' ')} {keywords}"

    return search_protocols(session=session, query=query, limit=3)


def to_source_protocol(record: ProtocolRecord) -> AgentSourceProtocol:
    return AgentSourceProtocol(
        protocolo=record.protocolo,
        numero_ano=record.numero_ano,
        situacao=record.situacao,
        subassunto=record.subassunto,
    )


def calculate_confidence(intent_score: float, source_protocols: Sequence[AgentSourceProtocol]) -> float:
    source_bonus = 0.15 if source_protocols else 0.0
    return round(min(0.95, intent_score + source_bonus), 2)


def build_response_text(
    detected_intent: str,
    source_protocols: Sequence[AgentSourceProtocol],
) -> str:
    base_text = RESPONSE_TEMPLATES.get(detected_intent, RESPONSE_TEMPLATES["desconhecida"])

    if detected_intent == "desconhecida":
        return base_text

    if source_protocols:
        return (
            f"{base_text} Encontrei registros semelhantes na base da SEPLAN, "
            "mas a conferencia final precisa ser feita pelo atendimento."
        )

    return (
        f"{base_text} Nao encontrei registros semelhantes agora, entao a conferencia "
        "precisa ser feita pelo atendimento."
    )
