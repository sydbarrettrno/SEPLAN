from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from database import engine, init_db
from main import app
from models import ProtocolRecord
from scripts.import_protocolos import build_record
from services_protocolos import build_texto_busca


def seed_protocol() -> ProtocolRecord:
    init_db()
    with Session(engine) as session:
        session.exec(delete(ProtocolRecord))
        record = ProtocolRecord(
            protocolo="12345",
            ano=2024,
            numero_ano="12345/2024",
            requerente="Maria Silva",
            situacao="Em andamento",
            subassunto="Consulta de viabilidade",
            responsavel="SEPLAN",
        )
        record.texto_busca = build_texto_busca(record)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def test_protocolos_health():
    init_db()
    with TestClient(app) as client:
        response = client.get("/protocolos/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["module"] == "protocolos"


def test_protocolos_search_returns_results():
    seed_protocol()
    with TestClient(app) as client:
        response = client.post("/protocolos/search", json={"query": "Maria viabilidade", "limit": 5})

    body = response.json()
    assert response.status_code == 200
    assert body["query"] == "Maria viabilidade"
    assert body["count"] == 1
    assert body["results"][0]["protocolo"] == "12345"


def test_get_protocol_by_number():
    seed_protocol()
    with TestClient(app) as client:
        response = client.get("/protocolos/12345")

    assert response.status_code == 200
    assert response.json()["numero_ano"] == "12345/2024"


def test_get_protocol_not_found():
    seed_protocol()
    with TestClient(app) as client:
        response = client.get("/protocolos/99999")

    assert response.status_code == 404
    assert response.json()["detail"]["status"] == "not_found"


def test_import_build_record_splits_numero_ano_when_protocol_column_is_missing():
    record = build_record(
        {
            "numero_ano": "12345/2024",
            "requerente": "Maria Silva",
            "subassunto": "Consulta de viabilidade",
        }
    )

    assert record is not None
    assert record.protocolo == "12345"
    assert record.ano == 2024
    assert record.numero_ano == "12345/2024"
    assert "Maria Silva" in record.texto_busca
