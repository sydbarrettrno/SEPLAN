# Agente WhatsApp SEPLAN

Backend FastAPI para simular atendimento inicial via WhatsApp da SEPLAN/Prefeitura de Itapoá.

A versão atual recebe mensagens, identifica a intenção, consulta as bases inteligentes em `data/base_inteligente/` e devolve uma resposta curta, segura, rastreável e mais útil para atendimento público. Esta versão ainda não integra WhatsApp real, não usa LLM, não usa embeddings e não chama APIs externas.

## V03 — Atendimento profissional SEPLAN

A V03 melhora a qualidade da resposta do agente. Quando a base não sustenta uma resposta segura, ou quando o atendimento precisa de confirmação, o agente informa **como** falar com a SEPLAN e quais dados ajudam na análise.

Contatos usados pelo agente:

- WhatsApp: (47) 98841-6225
- Telefone: (47) 3443-8826
- E-mail: atendimento.seplan@itapoa.sc.gov.br
- Atendimento: 07h30 às 13h30

O agente também orienta dados úteis conforme a intenção, sem inventar exigências:

- Habite-se: número do atendimento, alvará de construção, balneário, quadra, lote e cadastro/inscrição imobiliária.
- Alvará de construção: balneário, quadra, lote, cadastro/inscrição imobiliária, tipo de obra e documentos do imóvel.
- Declaração de Não Oposição: balneário, quadra, lote, cadastro/inscrição imobiliária e comprovação de vínculo/dominialidade.
- Guia rebaixada: endereço, finalidade do acesso, fotos do local e dados do imóvel.
- Drenagem: endereço, descrição do problema, ponto de referência e fotos/vídeos quando houver.
- Denúncia de obra irregular: endereço, descrição do ocorrido e fotos quando houver.

## V02 — Integração das Bases Inteligentes

O endpoint `/agent/message` consulta as bases em `data/base_inteligente/` antes de responder:

- `base_normativa_seplan_v01.jsonl`: base normativa quando houver regra clara.
- `base_auxiliar_checklists_seplan_v01.jsonl`: checklists operacionais da SEPLAN.
- `base_atendimento_seplan_estatistica_v01.jsonl`: padrões históricos de protocolos e últimos trâmites.
- `respostas_corrigidas_99_100_v02.jsonl`: respostas operacionais corrigidas.
- `perguntas_respostas_seplan_v02.jsonl`: perguntas e respostas curadas para atendimento direto.

O agente usa a base histórica para padrões e rastreabilidade, mas não responde como consulta individual de protocolo. Protocolos fonte aparecem apenas em `source_protocols`.

## Rodar localmente

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn main:app --reload
```

Edite o `SECRET_KEY` no `.env` antes de usar fora de ambiente local.

Links úteis:

- API: http://127.0.0.1:8000
- Interface do agente: http://127.0.0.1:8000/app/
- Docs: http://127.0.0.1:8000/docs
- Health geral: http://127.0.0.1:8000/health
- Health do agente: http://127.0.0.1:8000/agent/health
- Health da memória de protocolos: http://127.0.0.1:8000/protocolos/health

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
  "version": "v02"
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

Resposta com base inteligente:

```json
{
  "channel": "whatsapp",
  "phone_number": "+5547999999999",
  "detected_intent": "HABITE_SE",
  "response_text": "Resposta curta baseada na base inteligente, com orientação prática quando aplicável...",
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

Fallback profissional quando não houver base suficiente:

```json
{
  "detected_intent": "DESCONHECIDA",
  "response_text": "Não encontrei base suficiente para responder com segurança.\n\nPara evitar orientação errada, confirme com a SEPLAN:\nWhatsApp: (47) 98841-6225\nTelefone: (47) 3443-8826\nE-mail: atendimento.seplan@itapoa.sc.gov.br\nAtendimento: 07h30 às 13h30.\n\nSe possível, envie também: descrição do pedido, endereço, balneário, quadra, lote e fotos quando houver.",
  "confidence_score": 0.2,
  "source_patterns": [],
  "source_protocols": [],
  "source_checklists": [],
  "source_normative": [],
  "answer_source": "fallback",
  "needs_human_review": true,
  "fallback_contact": true,
  "contact_instruction": "Fale com a SEPLAN:\nWhatsApp: (47) 98841-6225\nTelefone: (47) 3443-8826\nE-mail: atendimento.seplan@itapoa.sc.gov.br\nAtendimento: 07h30 às 13h30.",
  "knowledge_base_used": false
}
```

Todo atendimento recebido em `/agent/message` é registrado no banco.

### Interface web

Com a API rodando, acesse:

```text
http://127.0.0.1:8000/app/
```

A tela permite conversar com o agente, testar assuntos prontos e visualizar intenção detectada, fonte principal, confiança, checklists, normas e protocolos usados apenas como rastreabilidade.

## Memória interna de protocolos

O módulo `/protocolos` é uma ferramenta interna do agente para importar e consultar registros normalizados. Ele continua disponível para carga, auditoria e testes da base.

### Buscar protocolos

```http
POST /protocolos/search
Content-Type: application/json

{
  "query": "texto livre",
  "limit": 5
}
```

### Consultar protocolo por número

```http
GET /protocolos/12345
```

Retorna o registro encontrado ou `404` com JSON claro.

## Importar protocolos

O importador aceita CSV ou XLSX normalizado. Campos ausentes são tratados como vazios quando possível.

```bash
python scripts/import_protocolos.py caminho\para\protocolos.csv
```

Também é possível informar outro banco:

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

## Fluxo de autenticação existente

1. `POST /auth/register` com `email`, `name`, `password`.
2. `POST /auth/login` para obter `access_token`.
3. `GET /me` com `Authorization: Bearer <token>`.
4. `POST /analyze` com Bearer token e corpo `{ "text": "..." }`.
