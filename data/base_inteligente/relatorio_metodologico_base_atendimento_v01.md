# Relatório metodológico — Base Inteligente de Atendimento SEPLAN V01

## 1. Escopo congelado

Esta base não é consulta individual de protocolo. O objetivo é alimentar o Agente WhatsApp SEPLAN com padrões de atendimento.

Regra central: `ObsAbertura` é tratada como pergunta/pedido real do cidadão; `Último Trâmite - Observação` é tratado como resposta prática/encaminhamento da SEPLAN; protocolo é usado apenas como rastreabilidade.

## 2. Fonte processada

- Arquivo: `BASE 2000-2025(2).xlsx`
- Aba: `BASE LIMPA`
- Registros processados: 2680
- Colunas mapeadas: Número/Ano.1, Número/Ano.2, Requerente - Nome Razão, Último Trâmite - Data/Hora.1, Observação Abertura, Situação, Abertura - Data, Assunto - Descrição, Subassunto - Descrição, Responsável, Último Trâmite - Observação, Prazo Atual, Data Encerramento, Última Atividade, Centro de Custo Atual - Descrição, Centro de Custo Abertura - Descrição, Usuário Atual - Nome

## 3. Método aplicado

1. Leitura da base enviada.
2. Mapeamento dos campos equivalentes à normalização histórica.
3. Classificação por intenção com temperatura semântica baixa.
4. Agrupamento estatístico por intenção e subassunto.
5. Extração de padrões recorrentes do campo `Último Trâmite - Observação`.
6. Consolidação de respostas gerais de atendimento.
7. Inclusão de camada normativa inicial com fontes oficiais/localizadas.
8. Fallback obrigatório para contato com a SEPLAN.

## 4. Frequência por intenção

- ALVARA_CONSTRUCAO: 972 (36.27%)
- HABITE_SE: 498 (18.58%)
- ALVARA_ATENDIMENTO: 471 (17.57%)
- DESDOBRO: 412 (15.37%)
- DESDOBRO_UNIFICACAO_ATENDIMENTO: 211 (7.87%)
- ALVARA_DEMOLICAO: 94 (3.51%)
- UNIFICACAO: 11 (0.41%)
- ALVARA_AMPLIACAO: 5 (0.19%)
- ALVARA_REGULARIZACAO: 4 (0.15%)
- ALVARA_MODIFICATIVO: 2 (0.07%)

## 5. Intenções sem dados nesta base

CERTIDAO_USO_OCUPACAO_SOLO, DECLARACAO_NAO_OPOSICAO_AGUA, DECLARACAO_NAO_OPOSICAO_LUZ, GUIA_REBAIXADA, DRENAGEM, DENUNCIA_OBRA_IRREGULAR, DOCUMENTACAO_EXIGENCIAS, TAXAS, PRAZO_ANDAMENTO, PEDIDO_DESARQUIVAMENTO, OUTROS, DESCONHECIDA

Essas intenções permanecem no dicionário como pendentes para base ampliada ou validação futura.

## 6. Camada normativa inicial

A camada normativa foi criada de forma conservadora. Foram incluídas fontes para Código de Obras, Plano Diretor, Uso/Ocupação do Solo e ligação de água. O agente não deve inventar artigo, documento obrigatório, prazo ou decisão administrativa quando a base normativa não sustentar.

## 7. Regras de segurança

- Não expor dados pessoais.
- Não transformar último trâmite individual em regra universal.
- Não responder decisão administrativa definitiva.
- Encaminhar à SEPLAN quando a confiança for baixa ou houver dúvida normativa.
- Usar temperatura baixa para classificação e consolidação.
- Usar linguagem de WhatsApp apenas na camada final de resposta.

## 8. Saídas geradas

- `base_atendimento_seplan_estatistica_v01.jsonl`
- `base_atendimento_seplan_estatistica_v01.csv`
- `dicionario_intencoes_seplan_v01.json`
- `base_normativa_seplan_v01.jsonl`
- `estatisticas_base_origem_v01.json`

## 9. Limitações

A base enviada contém forte concentração em alvará, habite-se, desdobro/unificação e demolição. Temas como declaração de não oposição, drenagem, denúncia, guia rebaixada e certidão de uso/ocupação não apareceram com volume suficiente nesta planilha específica. Eles foram mantidos no dicionário como intenções pendentes.

## 10. Próxima etapa

Integrar esta base ao backend para que `/agent/message` consulte primeiro `base_atendimento_seplan_estatistica_v01.jsonl` antes de gerar resposta.
