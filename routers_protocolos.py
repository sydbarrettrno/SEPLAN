from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database import get_session
from schemas import ProtocolRecordResponse, ProtocolSearchRequest, ProtocolSearchResponse
from services_protocolos import count_protocols, get_protocol_by_number, search_protocols


router = APIRouter(prefix="/protocolos", tags=["protocolos"])


@router.get("/health")
def protocolos_health(session: Session = Depends(get_session)):
    return {
        "status": "ok",
        "module": "protocolos",
        "version": "v01",
        "records": count_protocols(session),
    }


@router.post("/search", response_model=ProtocolSearchResponse)
def search(payload: ProtocolSearchRequest, session: Session = Depends(get_session)):
    results = search_protocols(session=session, query=payload.query, limit=payload.limit)
    return ProtocolSearchResponse(
        query=payload.query,
        count=len(results),
        results=results,
    )


@router.get("/{protocolo:path}", response_model=ProtocolRecordResponse)
def get_protocol(protocolo: str, session: Session = Depends(get_session)):
    record = get_protocol_by_number(session=session, protocolo=protocolo)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "not_found",
                "message": "Protocolo nao encontrado",
                "protocolo": protocolo,
            },
        )

    return record
