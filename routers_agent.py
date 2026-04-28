from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from schemas import AgentMessageRequest, AgentMessageResponse
from services_agent import PRODUCT_NAME, handle_agent_message


router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/health")
def agent_health():
    return {
        "status": "ok",
        "module": "agent",
        "product": PRODUCT_NAME,
        "version": "v01",
    }


@router.post("/message", response_model=AgentMessageResponse)
def message(payload: AgentMessageRequest, session: Session = Depends(get_session)):
    return handle_agent_message(session=session, payload=payload)
