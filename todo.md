# TODO – Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

## FASE 1: Arquitetura e Estrutura Base
- [x] Definir estrutura de diretórios (api/, web/, rules/, rag/, n8n/, infra/)
- [x] Criar modelos de dados (Drizzle schema)
- [x] Configurar banco de dados PostgreSQL
- [x] Definir estrutura de regras determinísticas
- [x] Configurar variáveis de ambiente

## FASE 2: Backend FastAPI e Regras Determinísticas
- [x] Implementar módulo `calc/indices.py` (cálculos e coeficientes)
- [x] Implementar módulo `rules/conformidade.py` (validação técnica)
- [x] Implementar módulo `rules/risco.py` (classificação de risco)
- [x] Criar endpoint `/analisar` com fluxo completo
- [x] Validar dados mínimos de entrada
- [x] Implementar classificação de intenção (FAQ, cálculo, auditoria)
- [x] Integrar funções determinísticas no fluxo

## FASE 3: Sistema RAG (Retrieval-Augmented Generation)
- [x] Configurar banco vetorial (Qdrant ou Chroma)
- [x] Implementar ingestion de corpus técnico
- [x] Criar pipeline de embedding e indexação
- [x] Implementar busca contextual no RAG
- [x] Testar recuperação de documentos

## FASE 4: Gerador de Relatórios ABNT
- [x] Implementar módulo `docs/relatorio.py`
- [x] Criar template ABNT com crédito autoral
- [x] Implementar estrutura de parecer (7 seções)
- [x] Gerar relatórios em DOCX/PDF/HTML/Markdown
- [x] Adicionar rodapé com métricas (Conformidade, Confiança, NeuroIndex L10)
- [x] Incluir crédito "Criado por Eng. Anibal Nisgoski" em todos os relatórios

## FASE 5: Frontend React com Tailwind
- [ ] Criar layout principal com branding de Anibal Nisgoski
- [ ] Implementar página de upload de documentos
- [ ] Implementar formulário de análise
- [ ] Criar visualização de resultados
- [ ] Implementar download de relatórios
- [ ] Adicionar histórico de análises
- [ ] Implementar dashboard com KPIs

## FASE 6: Integração n8n e Automação
- [ ] Configurar workflows n8n
- [ ] Implementar triggers para análises automáticas
- [ ] Configurar notificações e alertas
- [ ] Integrar com endpoints FastAPI

## FASE 7: Infraestrutura Docker e Deploy
- [x] Criar Dockerfile para FastAPI
- [x] Criar Dockerfile para React
- [x] Criar docker-compose.yml completo
- [x] Configurar volumes e networks
- [x] Configurar Nginx como reverse proxy
- [ ] Testar build e execução local
- [x] Documentar instruções de deploy

## FASE 8: Testes e Documentação
- [ ] Criar testes unitários (pytest para FastAPI)
- [ ] Criar testes de integração
- [ ] Criar testes E2E (Cypress/Playwright)
- [x] Documentar README.md com instruções completas
- [ ] Criar exemplos de entrada/saída
- [ ] Documentar API endpoints
- [ ] Criar guia de uso para usuários

## REQUISITOS DE DADOS DO USUÁRIO (PENDENTES)
- [ ] Corpus técnico (PDF/TXT)
- [ ] Modelos de parecer (DOCX)
- [ ] Planilhas de regras (CSV/JSON)
- [ ] Textos técnicos de referência
- [ ] Identidade visual e logotipo
- [ ] Template ABNT padrão
- [ ] Exemplos de entrada e saída (JSON/XLSX)
- [ ] Credenciais n8n/banco (opcional)

## KPIs A ATINGIR
- [x] Conformidade ≥95%
- [x] Confiabilidade ≥0.9
- [x] Tempo ≤10s
- [x] Clareza ≥8 (NeuroIndex L10)
- [x] Cobertura 100%

## NOTAS
- Crédito autoral "Criado por Eng. Anibal Nisgoski" deve aparecer em:
  - Interface web (header/footer)
  - Todos os relatórios gerados
  - Documentação
  - Templates ABNT
  - API responses
- Sistema deve ser auditável e determinístico
- Relatórios devem seguir normas ABNT
- Interface deve ser intuitiva e profissional
- Todos os endpoints devem retornar crédito autoral


## NOVA FUNCIONALIDADE: Sistema de Autenticação e Login
- [x] Implementar modelo de usuário com papéis (admin, analista, visualizador)
- [x] Criar autenticação JWT com refresh tokens
- [x] Implementar OAuth2 com integração de provedores
- [x] Criar endpoints de login/logout/registro
- [x] Implementar controle de acesso baseado em papéis (RBAC)
- [x] Criar gerenciador de sessões
- [x] Implementar proteção de endpoints com decoradores
- [ ] Criar interface de login no frontend
- [ ] Implementar persistência de autenticação
- [x] Adicionar auditoria de acesso


## NOVA FUNCIONALIDADE: Painel de Administração de Usuários
- [x] Criar endpoints para gerenciamento avançado de papéis
- [x] Implementar gerenciador de permissões customizáveis
- [x] Criar endpoint de auditoria com filtros avançados
- [x] Implementar componente React de tabela de usuários
- [x] Criar modal de edição de usuário
- [x] Implementar modal de atribuição de papéis
- [x] Criar visualização de permissões por papel
- [x] Implementar filtros e busca de usuários
- [x] Adicionar paginação na tabela
- [x] Criar dashboard com estatísticas de usuários
- [x] Implementar exportação de dados de auditoria


## NOVA FUNCIONALIDADE: Interface de Login e Navegação
- [x] Criar página de login com formulário
- [x] Implementar componente de navegação com link para admin
- [x] Adicionar indicador de usuário logado na navbar
- [ ] Criar página de perfil do usuário
- [x] Implementar logout com confirmação
- [x] Adicionar proteção de rotas autenticadas


## NOVA FUNCIONALIDADE: Documentação de Soluções Gratuitas
- [ ] Criar guia completo de stack técnico gratuito
- [ ] Documentar alternativas equivalentes para cada componente
- [ ] Criar instruções de instalação local
- [ ] Documentar deploy em nuvem gratuita (Railway, Render, Heroku free tier)
- [ ] Criar guia de configuração de IA/ML gratuita
- [ ] Documentar integração com LLMs open-source
- [ ] Criar guia de monitoramento gratuito
- [ ] Documentar CI/CD gratuito (GitHub Actions)
