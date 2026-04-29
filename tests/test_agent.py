from fastapi.testclient import TestClient
from sqlmodel import Session, delete, select

from database import engine, init_db
from main import app
from models import AttendanceMessage


def clear_attendance_logs() -> None:
    init_db()
    with Session(engine) as session:
        session.exec(delete(AttendanceMessage))
        session.commit()


def test_agent_health():
    with TestClient(app) as client:
        response = client.get("/agent/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "module": "agent",
        "product": "Agente WhatsApp SEPLAN",
        "version": "v02",
    }


def test_agent_message_uses_knowledge_base_and_returns_source_patterns():
    clear_attendance_logs()
    payload = {
        "channel": "whatsapp",
        "phone_number": "+5547999999999",
        "message": "quero saber como pedir habite-se",
    }

    with TestClient(app) as client:
        response = client.post("/agent/message", json=payload)

    body = response.json()
    assert response.status_code == 200
    assert body["detected_intent"] == "HABITE_SE"
    assert body["knowledge_base_used"] is True
    assert body["fallback_contact"] is False
    assert body["source_patterns"]
    assert "Habite-se" in body["source_patterns"]
    assert body["source_protocols"]
    assert body["source_checklists"] == []
    assert body["source_normative"]
    assert body["answer_source"] in {"historical", "qa"}

    with Session(engine) as session:
        logs = session.exec(select(AttendanceMessage)).all()

    assert len(logs) == 1


def test_agent_message_fallbacks_to_seplan_contact_when_confidence_is_low():
    clear_attendance_logs()
    payload = {
        "channel": "whatsapp",
        "phone_number": "+5547999999999",
        "message": "qual o melhor horario para observar estrelas",
    }

    with TestClient(app) as client:
        response = client.post("/agent/message", json=payload)

    body = response.json()
    assert response.status_code == 200
    assert body["detected_intent"] == "DESCONHECIDA"
    assert body["knowledge_base_used"] is False
    assert body["fallback_contact"] is True
    assert body["needs_human_review"] is True
    assert body["contact_instruction"] == "Em caso de dúvida, entre em contato com a SEPLAN."
    assert body["source_checklists"] == []
    assert body["source_normative"] == []
    assert body["answer_source"] == "fallback"


def test_agent_does_not_answer_as_individual_protocol_lookup():
    clear_attendance_logs()
    payload = {
        "channel": "whatsapp",
        "phone_number": "+5547999999999",
        "message": "preciso de vistoria para habite-se",
    }

    with TestClient(app) as client:
        response = client.post("/agent/message", json=payload)

    body = response.json()
    assert response.status_code == 200
    assert body["source_protocols"]
    assert "protocolo" not in body["response_text"].casefold()
    for source_protocol in body["source_protocols"]:
        assert source_protocol not in body["response_text"]


def test_agent_message_returns_checklist_sources_for_document_question():
    clear_attendance_logs()
    payload = {
        "channel": "whatsapp",
        "phone_number": "+5547999999999",
        "message": "matricula registro de imoveis",
    }

    with TestClient(app) as client:
        response = client.post("/agent/message", json=payload)

    body = response.json()
    assert response.status_code == 200
    assert body["detected_intent"] == "ALVARA_CONSTRUCAO"
    assert body["knowledge_base_used"] is True
    assert body["source_checklists"]
    assert body["source_protocols"] == []
    assert body["answer_source"] in {"checklist", "qa"}


def test_agent_message_uses_corrected_dno_response():
    clear_attendance_logs()
    payload = {
        "channel": "whatsapp",
        "phone_number": "+5547999999999",
        "message": "preciso de declaracao de nao oposicao para agua ou luz",
    }

    with TestClient(app) as client:
        response = client.post("/agent/message", json=payload)

    body = response.json()
    assert response.status_code == 200
    assert body["detected_intent"] == "DECLARACAO_NAO_OPOSICAO"
    assert body["knowledge_base_used"] is True
    assert body["fallback_contact"] is False
    assert "Declaração de Não Oposição" in body["response_text"]
    assert body["answer_source"] == "corrected"


def test_agent_message_answers_alvara_with_qa_and_traceability():
    clear_attendance_logs()
    payload = {
        "channel": "whatsapp",
        "phone_number": "+5547999999999",
        "message": "quais documentos para alvara de construcao",
    }

    with TestClient(app) as client:
        response = client.post("/agent/message", json=payload)

    body = response.json()
    assert response.status_code == 200
    assert body["detected_intent"] == "ALVARA_CONSTRUCAO"
    assert body["answer_source"] == "qa"
    assert body["source_checklists"]
    assert body["source_protocols"]
    assert "protocolo" not in body["response_text"].casefold()


def test_agent_knowledge_endpoint_reports_loaded_bases():
    with TestClient(app) as client:
        response = client.get("/agent/knowledge")

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["sources"]["qa"] > 0
    assert body["sources"]["checklist"] > 0
    assert body["sources"]["historical"] > 0
