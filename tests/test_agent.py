from fastapi.testclient import TestClient
from sqlmodel import Session, delete, select

from database import engine, init_db
from main import app
from models import AttendanceMessage, ProtocolRecord
from services_protocolos import build_texto_busca


def seed_agent_protocol() -> None:
    init_db()
    with Session(engine) as session:
        session.exec(delete(AttendanceMessage))
        session.exec(delete(ProtocolRecord))
        record = ProtocolRecord(
            protocolo="777",
            ano=2024,
            numero_ano="777/2024",
            requerente="Joao Souza",
            situacao="Concluido",
            subassunto="Habite-se",
            responsavel="SEPLAN",
        )
        record.texto_busca = build_texto_busca(record)
        session.add(record)
        session.commit()


def test_agent_health():
    with TestClient(app) as client:
        response = client.get("/agent/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "module": "agent",
        "product": "Agente WhatsApp SEPLAN",
        "version": "v01",
    }


def test_agent_message_detects_intent_searches_protocols_and_logs():
    seed_agent_protocol()
    payload = {
        "channel": "whatsapp",
        "phone_number": "+5547999999999",
        "message": "quero saber como pedir habite-se",
    }

    with TestClient(app) as client:
        response = client.post("/agent/message", json=payload)

    body = response.json()
    assert response.status_code == 200
    assert body["channel"] == "whatsapp"
    assert body["phone_number"] == "+5547999999999"
    assert body["detected_intent"] == "habite_se"
    assert body["confidence_score"] >= 0.0
    assert body["source_protocols"][0]["protocolo"] == "777"
    assert body["needs_human_review"] is True

    with Session(engine) as session:
        logs = session.exec(select(AttendanceMessage)).all()

    assert len(logs) == 1
