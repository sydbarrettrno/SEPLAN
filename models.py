from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, UniqueConstraint


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    name: str
    password_hash: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProtocolRecord(SQLModel, table=True):
    __tablename__ = "protocol_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    protocolo: Optional[str] = Field(default=None, index=True)
    ano: Optional[int] = Field(default=None, index=True)
    numero_ano: Optional[str] = Field(default=None, index=True)
    requerente: Optional[str] = Field(default=None, index=True)
    abertura_data: Optional[str] = Field(default=None, index=True)
    obs_abertura: Optional[str] = Field(default=None)
    ultimo_tramite_data: Optional[str] = Field(default=None, index=True)
    situacao: Optional[str] = Field(default=None, index=True)
    assunto: Optional[str] = Field(default=None, index=True)
    subassunto: Optional[str] = Field(default=None, index=True)
    ultimo_tramite_obs: Optional[str] = Field(default=None)
    responsavel: Optional[str] = Field(default=None, index=True)
    tipo_processo_normalizado: Optional[str] = Field(default=None, index=True)
    status_semantico_normalizado: Optional[str] = Field(default=None, index=True)
    confiabilidade_extracao: Optional[float] = Field(default=None)
    status_revisao: Optional[str] = Field(default=None, index=True)
    texto_busca: str = Field(default="", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AttendanceMessage(SQLModel, table=True):
    __tablename__ = "attendance_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    channel: str = Field(default="manual", index=True)
    phone_number: Optional[str] = Field(default=None, index=True)
    inbound_text: str
    normalized_text: str = Field(default="", index=True)
    detected_intent: Optional[str] = Field(default=None, index=True)
    response_text: Optional[str] = Field(default=None)
    confidence_score: Optional[float] = Field(default=None)
    source_protocols: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
