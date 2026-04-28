# Plano Agent WhatsApp V01

## Produto

Agente WhatsApp SEPLAN: backend FastAPI que simula a entrada de mensagens de WhatsApp, identifica a intencao do cidadao, consulta a base local de protocolos como memoria interna e retorna uma resposta curta, segura e rastreavel.

## Arquitetura V01

- `/agent/message` recebe uma mensagem simulada de WhatsApp.
- `services_agent.py` normaliza o texto, classifica a intencao por regras simples e monta a resposta.
- `services_agent.py` consulta `services_protocolos.py` internamente para buscar protocolos semelhantes.
- `AttendanceMessage` registra entrada, intencao, resposta, confianca, fontes usadas e necessidade de revisao humana.
- `/protocolos/search` continua disponivel como ferramenta interna de consulta e validacao da base.

## Escopo desta versao

- Simular atendimento WhatsApp via API.
- Classificar intencoes minimas: `habite_se`, `alvara_construcao`, `certidao_uso_ocupacao`, `declaracao_nao_oposicao`, `guia_rebaixada`, `drenagem`, `denuncia` e `desconhecida`.
- Responder em linguagem curta de atendimento, sem inventar exigencias.
- Registrar todo atendimento no banco.
- Manter importacao e busca textual de protocolos como memoria interna.

## Fora de escopo

- Integracao real com WhatsApp.
- Uso de LLM.
- Embeddings ou busca semantica real.
- APIs externas.
- Frontend especifico.

## Evolucao sugerida

1. Validar as respostas com a equipe da SEPLAN.
2. Ampliar sinonimos e exemplos reais por intencao.
3. Adicionar filtros de protocolo por ano, situacao e responsavel.
4. Integrar WhatsApp real somente depois que a simulacao estiver auditavel.
