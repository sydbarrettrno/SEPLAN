from datetime import datetime
from typing import List, Mapping, Optional, Sequence, Tuple, Union
import unicodedata

from sqlalchemy import func
from sqlmodel import Session, select

from models import ProtocolRecord


SEARCH_FIELDS: Sequence[str] = (
    "protocolo",
    "numero_ano",
    "requerente",
    "obs_abertura",
    "ultimo_tramite_obs",
    "subassunto",
    "situacao",
    "responsavel",
    "texto_busca",
)


def normalize_text(value: object) -> str:
    if value is None:
        return ""

    text = str(value).casefold().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def build_texto_busca(source: Union[ProtocolRecord, Mapping[str, object]]) -> str:
    parts: List[str] = []
    for field_name in SEARCH_FIELDS:
        if isinstance(source, ProtocolRecord):
            value = getattr(source, field_name, None)
        else:
            value = source.get(field_name)

        if value is not None and str(value).strip():
            parts.append(str(value).strip())

    return " | ".join(parts)


def count_protocols(session: Session) -> int:
    return session.exec(select(func.count(ProtocolRecord.id))).one()


def get_protocol_by_number(session: Session, protocolo: str) -> Optional[ProtocolRecord]:
    value = protocolo.strip()
    if not value:
        return None

    record = session.exec(
        select(ProtocolRecord).where(ProtocolRecord.protocolo == value)
    ).first()
    if record:
        return record

    return session.exec(
        select(ProtocolRecord).where(ProtocolRecord.numero_ano == value)
    ).first()


def search_protocols(session: Session, query: str, limit: int = 5) -> List[ProtocolRecord]:
    normalized_query = normalize_text(query)
    if not normalized_query:
        return []

    tokens = normalized_query.split()
    records = session.exec(select(ProtocolRecord)).all()
    scored: List[Tuple[int, ProtocolRecord]] = []

    for record in records:
        score = _score_record(record, normalized_query, tokens)
        if score > 0:
            scored.append((score, record))

    scored.sort(key=_sort_key, reverse=True)
    return [record for _, record in scored[:limit]]


def _score_record(record: ProtocolRecord, normalized_query: str, tokens: Sequence[str]) -> int:
    search_text = normalize_text(build_texto_busca(record))
    if not search_text:
        return 0

    score = 0
    if normalized_query in search_text:
        score += 20

    for field_name in ("protocolo", "numero_ano"):
        field_text = normalize_text(getattr(record, field_name, None))
        if field_text == normalized_query:
            score += 60
        elif field_text.startswith(normalized_query):
            score += 30

    for token in tokens:
        if token in search_text:
            score += 3

    return score


def _sort_key(item: Tuple[int, ProtocolRecord]) -> Tuple[int, datetime, int]:
    score, record = item
    reference_date = record.ultimo_tramite_data or record.updated_at or datetime.min
    return score, reference_date, record.id or 0
