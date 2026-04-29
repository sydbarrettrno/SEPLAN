from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from schemas import AgentMessageRequest, AgentMessageResponse
from services_agent import PRODUCT_NAME, handle_agent_message
from services_knowledge_base import load_intelligent_bases


router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/health")
def agent_health():
    return {
        "status": "ok",
        "module": "agent",
        "product": PRODUCT_NAME,
        "version": "v02",
    }


@router.post("/message", response_model=AgentMessageResponse)
def message(payload: AgentMessageRequest, session: Session = Depends(get_session)):
    return handle_agent_message(session=session, payload=payload)


@router.get("/knowledge")
def knowledge_health():
    bases = load_intelligent_bases()
    return {
        "status": "ok",
        "module": "knowledge_base",
        "version": "v02",
        "sources": {name: len(items) for name, items in bases.items()},
        "priority": ["corrected", "qa", "checklist", "historical", "normative", "fallback"],
    }
