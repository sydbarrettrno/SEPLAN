from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AnalyzeRequest(BaseModel):
    text: str


class ProtocolSearchRequest(BaseModel):
    query: str = Field(..., max_length=500)
    limit: int = Field(default=5, ge=1, le=50)


class ProtocolRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    protocolo: str
    ano: Optional[int] = None
    numero_ano: Optional[str] = None
    requerente: Optional[str] = None
    abertura_data: Optional[date] = None
    obs_abertura: Optional[str] = None
    ultimo_tramite_data: Optional[datetime] = None
    situacao: Optional[str] = None
    subassunto: Optional[str] = None
    ultimo_tramite_obs: Optional[str] = None
    responsavel: Optional[str] = None
    tipo_processo_normalizado: Optional[str] = None
    status_semantico_normalizado: Optional[str] = None
    confiabilidade_extracao: Optional[float] = None
    status_revisao: Optional[str] = None
    texto_busca: str
    created_at: datetime
    updated_at: datetime


class ProtocolSearchResponse(BaseModel):
    query: str
    count: int
    results: List[ProtocolRecordResponse]


class AgentMessageRequest(BaseModel):
    channel: str = Field(default="whatsapp", min_length=1, max_length=30)
    phone_number: Optional[str] = Field(default=None, max_length=30)
    message: str = Field(..., min_length=1, max_length=1000)


class AgentMessageResponse(BaseModel):
    channel: str
    phone_number: Optional[str] = None
    detected_intent: str
    response_text: str
    confidence_score: float
    source_patterns: List[str]
    source_protocols: List[str]
    source_checklists: List[str]
    source_normative: List[str]
    answer_source: str
    needs_human_review: bool
    fallback_contact: bool
    contact_instruction: Optional[str] = None
    knowledge_base_used: bool
