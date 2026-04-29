# Agente WhatsApp SEPLAN

Backend FastAPI para simular um atendimento inicial via WhatsApp da SEPLAN/Prefeitura de Itapoa.

A V02 recebe mensagens, identifica a intencao, consulta a Base Inteligente de Atendimento SEPLAN e devolve uma resposta curta, segura e rastreavel. Esta versao nao integra WhatsApp real, nao usa LLM, nao usa embeddings e nao chama APIs externas.

## Plano tecnico

O plano da V01 esta em [`docs/PLANO_AGENT_WHATSAPP_V01.md`](docs/PLANO_AGENT_WHATSAPP_V01.md).

## V02 — Integração das Bases Inteligentes

O endpoint `/agent/message` consulta as bases em `data/base_inteligente/` antes de responder:

- `base_normativa_seplan_v01.jsonl`: base normativa quando houver regra clara.
- `base_auxiliar_checklists_seplan_v01.jsonl`: checklists operacionais da SEPLAN.
- `base_atendimento_seplan_estatistica_v01.jsonl`: padrões históricos de protocolos e últimos trâmites.
- `respostas_corrigidas_99_100_v02.jsonl`: respostas operacionais corrigidas.
- `perguntas_respostas_seplan_v02.jsonl`: perguntas e respostas curadas para atendimento direto.

O agente usa a base histórica para padrões e rastreabilidade, mas não responde como consulta individual de protocolo. Protocolos fonte aparecem apenas em `source_protocols`.

Se a base não tiver confiança suficiente, o agente responde com fallback orientando contato com a SEPLAN.

## Rodar localmente

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn main:app --reload
```

Edite o `SECRET_KEY` no `.env` antes de usar fora de ambiente local.

Links uteis:

- API: http://127.0.0.1:8000
- Interface do agente: http://127.0.0.1:8000/app/
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
  "detected_intent": "HABITE_SE",
  "response_text": "Resposta curta baseada na base inteligente...",
  "confidence_score": 0.95,
  "source_patterns": ["Habite-se", "Como solicitar Habite-se?"],
  "source_protocols": ["30690/2025", "30604/2025"],
  "source_checklists": [],
  "source_normative": ["LCM_49_2016_CODIGO_OBRAS"],
  "answer_source": "historical",
  "needs_human_review": false,
  "fallback_contact": false,
  "contact_instruction": null,
  "knowledge_base_used": true
}
```

Fallback quando nao houver base suficiente:

```json
{
  "detected_intent": "DESCONHECIDA",
  "response_text": "Não encontrei base suficiente para responder com segurança. Em caso de dúvida, entre em contato com a SEPLAN.",
  "confidence_score": 0.2,
  "source_patterns": [],
  "source_protocols": [],
  "source_checklists": [],
  "source_normative": [],
  "answer_source": "fallback",
  "needs_human_review": true,
  "fallback_contact": true,
  "contact_instruction": "Em caso de dúvida, entre em contato com a SEPLAN.",
  "knowledge_base_used": false
}
```

Todo atendimento recebido em `/agent/message` e registrado no banco.

### Interface web

Com a API rodando, acesse:

```text
http://127.0.0.1:8000/app/
```

A tela permite conversar com o agente, testar assuntos prontos e visualizar a intencao detectada, fonte principal, confianca, checklists, normas e protocolos usados apenas como rastreabilidade.

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
python -m pytest
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
