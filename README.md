# SEPLAN MVP — Backend FastAPI com JWT

Este MVP entrega autenticação (registro/login), proteção de rotas com Bearer JWT, healthcheck e um endpoint `/analyze` (stub determinístico).
Pronto para rodar local com SQLite, ou em Docker.

## 1) Rodar local (sem Docker)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # edite SECRET_KEY (use algo forte)
uvicorn main:app --reload
```
Abra: http://127.0.0.1:8000/docs

## 2) Rodar com Docker Compose
```bash
cp .env.example .env  # ajuste valores
docker compose up --build -d
# Health: http://127.0.0.1:8000/health
# Docs:   http://127.0.0.1:8000/docs
```

## 3) Fluxo de uso (via /docs)
1. POST /auth/register  → informe email, name, password (recebe `access_token`)
2. POST /auth/login     → retorne `access_token` quando necessário
3. GET  /me             → passe `Authorize -> Bearer <token>`
4. POST /analyze        → idem; corpo: `{ "text": "..." }`

## 4) Próximos passos
- Trocar SQLite por Postgres (alterar `DATABASE_URL` para `postgresql+psycopg2://user:pass@host/db`)
- Conectar LLM (OpenAI/Claude) e RAG
- Log/Auditoria (tabelas de trilha)
- Rate limit / Redis
- Testes automatizados (pytest)
