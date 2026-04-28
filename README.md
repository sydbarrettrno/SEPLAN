# Agente WhatsApp SEPLAN

Backend FastAPI para simular um atendimento inicial via WhatsApp da SEPLAN/Prefeitura de Itapoa.

A V01 recebe mensagens, identifica uma intencao por regras simples, consulta a base local de protocolos como memoria interna e devolve uma resposta curta, segura e rastreavel. Esta versao nao integra WhatsApp real, nao usa LLM, nao usa embeddings e nao chama APIs externas.

## Plano tecnico

O plano da V01 esta em [`docs/PLANO_AGENT_WHATSAPP_V01.md`](docs/PLANO_AGENT_WHATSAPP_V01.md).

## Rodar localmente

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload
```

Edite o `SECRET_KEY` no `.env` antes de usar fora de ambiente local.

Links uteis:

- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs
- Health geral: http://127.0.0.1:8000/health
- Health do agente: http://127.0.0.1:8000/agent/health
- Health da memoria de protocolos: http://127.0.0.1:8000/protocolos/health

## Agente WhatsApp

### Health

```http
GET /agent/health
```

Resposta:

```json
{
  "status": "ok",
  "module": "agent",
  "product": "Agente WhatsApp SEPLAN",
  "version": "v01"
}
```

### Simular mensagem

```http
POST /agent/message
Content-Type: application/json

{
  "channel": "whatsapp",
  "phone_number": "+5547999999999",
  "message": "quero saber como pedir habite-se"
}
```

Resposta:

```json
{
  "channel": "whatsapp",
  "phone_number": "+5547999999999",
  "detected_intent": "habite_se",
  "response_text": "Mensagem curta em estilo WhatsApp...",
  "confidence_score": 0.0,
  "source_protocols": [],
  "needs_human_review": true
}
```

Intencoes da V01:

- `habite_se`
- `alvara_construcao`
- `certidao_uso_ocupacao`
- `declaracao_nao_oposicao`
- `guia_rebaixada`
- `drenagem`
- `denuncia`
- `desconhecida`

Todo atendimento recebido em `/agent/message` e registrado no banco.

## Memoria interna de protocolos

O modulo `/protocolos` e uma ferramenta interna do agente para importar e consultar registros normalizados. Ele continua disponivel para carga, auditoria e testes da base.

### Buscar protocolos

```http
POST /protocolos/search
Content-Type: application/json

{
  "query": "texto livre",
  "limit": 5
}
```

Resposta:

```json
{
  "query": "texto livre",
  "count": 0,
  "results": []
}
```

### Consultar protocolo por numero

```http
GET /protocolos/12345
```

Retorna o registro encontrado ou `404` com JSON claro.

## Importar protocolos

O importador aceita CSV ou XLSX normalizado. Campos ausentes sao tratados como vazios quando possivel.

```bash
python scripts/import_protocolos.py caminho\para\protocolos.csv
```

Tambem e possivel informar outro banco:

```bash
python scripts/import_protocolos.py caminho\para\protocolos.xlsx --database-url sqlite:///./app.db
```

Ao final, o script imprime um resumo JSON com `imported`, `updated`, `skipped` e `total_rows`.

## Testes

```bash
pytest
```

## Docker Compose

```bash
copy .env.example .env
docker compose up --build -d
```

## Fluxo de autenticacao existente

1. `POST /auth/register` com `email`, `name`, `password`.
2. `POST /auth/login` para obter `access_token`.
3. `GET /me` com `Authorization: Bearer <token>`.
4. `POST /analyze` com Bearer token e corpo `{ "text": "..." }`.
