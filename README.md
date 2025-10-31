# Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

**Versão:** 1.0.0  
**Autor:** Eng. Anibal Nisgoski  
**Descrição:** Sistema Analítico de IA com RAG, Regras Determinísticas e Geração de Relatórios ABNT

---

## 📋 Visão Geral

O **Sistema Analítico de IA** é uma plataforma completa de análise técnico-normativa que combina:

- **Inteligência Artificial**: Processamento de linguagem natural com RAG (Retrieval-Augmented Generation)
- **Regras Determinísticas**: Cálculos auditáveis e conformidade com normas técnicas
- **Relatórios Profissionais**: Geração automática de documentos ABNT
- **Automação**: Integração com n8n para workflows

O sistema mantém o crédito autoral **"Criado por Eng. Anibal Nisgoski"** em todas as interfaces, relatórios e documentação.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React + Tailwind)           │
├─────────────────────────────────────────────────────────┤
│                   Backend (FastAPI)                     │
├──────────────────┬──────────────────┬──────────────────┤
│  Regras Determ.  │      RAG         │   Relatórios     │
├──────────────────┼──────────────────┼──────────────────┤
│ • Conformidade   │ • Ingestion      │ • ABNT NBR 14724 │
│ • Risco          │ • Indexação      │ • DOCX/PDF       │
│ • Cálculos       │ • Busca          │ • HTML/Markdown  │
├──────────────────┴──────────────────┴──────────────────┤
│         Banco de Dados (PostgreSQL)                    │
│         Banco Vetorial (Qdrant)                        │
│         Cache (Redis)                                  │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Estrutura de Diretórios

```
sistema_analitico_ia/
├── api/                          # Backend FastAPI
│   ├── calc/                      # Cálculos determinísticos
│   │   └── indices.py             # Índices e coeficientes
│   ├── rules/                     # Regras de negócio
│   │   ├── conformidade.py        # Validação de conformidade
│   │   └── risco.py               # Classificação de risco
│   ├── rag/                       # Sistema RAG
│   │   └── manager.py             # Gerenciador de RAG
│   ├── docs/                      # Geração de documentos
│   │   └── relatorio.py           # Gerador de relatórios ABNT
│   ├── endpoints/                 # Endpoints da API
│   │   └── analisar.py            # Endpoint principal de análise
│   ├── config.py                  # Configurações
│   ├── models.py                  # Modelos Pydantic
│   ├── utils.py                   # Utilitários
│   └── main.py                    # Aplicação FastAPI
├── client/                        # Frontend React
│   ├── src/
│   │   ├── pages/                 # Páginas
│   │   ├── components/            # Componentes
│   │   └── lib/                   # Bibliotecas
│   └── public/                    # Assets estáticos
├── drizzle/                       # Schema do banco
│   └── schema.ts                  # Definição de tabelas
├── infra/                         # Infraestrutura
│   ├── docker/                    # Dockerfiles
│   └── n8n/                       # Workflows n8n
├── docs/                          # Documentação
├── tests/                         # Testes
├── docker-compose.yml             # Orquestração de containers
├── requirements.txt               # Dependências Python
├── package.json                   # Dependências Node.js
└── README.md                      # Este arquivo
```

---

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.12+
- Node.js 22+
- Docker e Docker Compose
- PostgreSQL 15+
- Redis 7+

### Instalação Local

#### 1. Clonar repositório e instalar dependências

```bash
cd sistema_analitico_ia

# Backend
pip install -r requirements.txt

# Frontend
pnpm install
```

#### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com suas configurações
```

#### 3. Inicializar banco de dados

```bash
# Executar migrations
pnpm db:push

# Seed (opcional)
pnpm db:seed
```

#### 4. Iniciar serviços

```bash
# Terminal 1: Backend FastAPI
python -m api.main

# Terminal 2: Frontend React
pnpm dev

# Terminal 3: Banco Vetorial (Qdrant)
docker run -p 6333:6333 qdrant/qdrant
```

### Acesso

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Qdrant:** http://localhost:6333

---

## 📚 Componentes Principais

### 1. Cálculos Determinísticos (`api/calc/indices.py`)

Implementa cálculos auditáveis para análise:

```python
from api.calc import calculadora

# Calcular conformidade ponderada
resultado = calculadora.calcular_conformidade(
    conformidade_legal=95.0,
    conformidade_tecnica=88.0,
    conformidade_operacional=92.0
)
# Retorna: IndiceConformidade com valor ponderado e status

# Calcular risco
risco = calculadora.calcular_risco(
    fatores_risco={
        "seguranca": 0.7,
        "operacional": 0.3,
        "legal": 0.5
    }
)
# Retorna: CoeficienteRisco com classificação

# NeuroIndex L10
neuro_index = calculadora.calcular_neuro_index_l10(
    clareza=8.5,
    consistencia=8.0,
    completude=8.2
)
# Retorna: 8.3 (índice de qualidade)
```

### 2. Regras de Conformidade (`api/rules/conformidade.py`)

Valida conformidade com normas técnicas:

```python
from api.rules import validador

# Registrar norma customizada
validador.registrar_norma(
    codigo="NORMA_CUSTOMIZADA",
    tipo=TipoNorma.ABNT,
    titulo="Minha Norma",
    requisitos=["Req1", "Req2"],
    peso=0.2
)

# Validar conformidade
resultado = validador.validar_conformidade(
    dados_analise={"documentacao": True, "controles": True},
    normas_aplicaveis=["ABNT_NBR_ISO_9001"]
)
# Retorna: ResultadoValidacao com achados e conformidade
```

### 3. Classificação de Risco (`api/rules/risco.py`)

Analisa e classifica riscos:

```python
from api.rules import classificador, FatorRisco, TipoRisco

# Criar fatores de risco
fatores = [
    FatorRisco(
        nome="Segurança de dados",
        tipo=TipoRisco.SEGURANCA,
        probabilidade=0.4,
        impacto=0.9
    ),
    FatorRisco(
        nome="Conformidade",
        tipo=TipoRisco.CONFORMIDADE,
        probabilidade=0.3,
        impacto=0.8
    )
]

# Analisar risco
resultado = classificador.analisar_risco(fatores)
# Retorna: ResultadoAnaliseRisco com matriz, recomendações, plano de mitigação
```

### 4. Sistema RAG (`api/rag/manager.py`)

Gerencia ingestion e busca de documentos:

```python
from api.rag import gerenciador_rag, TipoDocumento

# Ingerir documento
documento = gerenciador_rag.ingerir_documento(
    titulo="Norma ABNT NBR ISO 9001",
    conteudo="Sistemas de gestão da qualidade...",
    tipo=TipoDocumento.NORMATIVO,
    fonte="ABNT",
    tags=["qualidade", "iso"]
)

# Buscar documentos relacionados
resultado = gerenciador_rag.buscar(
    query="conformidade com normas de qualidade",
    tipo_documento=TipoDocumento.NORMATIVO,
    limite=5
)
# Retorna: ResultadoBusca com chunks relevantes e scores
```

### 5. Gerador de Relatórios ABNT (`api/docs/relatorio.py`)

Gera relatórios profissionais:

```python
from api.docs import GeradorRelatorioAnalise, ConfiguracaoRelatorio
from datetime import datetime

# Configurar relatório
config = ConfiguracaoRelatorio(
    titulo="Análise de Conformidade",
    autor="Eng. Anibal Nisgoski",
    data=datetime.now(),
    instituicao="Minha Organização",
    credito_autoral="Criado por Eng. Anibal Nisgoski"
)

# Gerar relatório
gerador = GeradorRelatorioAnalise(config)
texto = gerador.gerar_relatorio_analise(resultado_analise)

# Exportar em diferentes formatos
html = gerador.gerador.gerar_html()
```

---

## 🔌 Endpoints da API

### Análise

```
POST /api/analisar
  Executa análise técnico-normativa completa
  
GET /api/analises/{analise_id}
  Obtém resultado de análise anterior
  
GET /api/analises
  Lista todas as análises realizadas
```

### RAG

```
POST /api/rag/ingerir
  Ingere novo documento no RAG
  
POST /api/rag/buscar
  Busca documentos relacionados
  
GET /api/rag/documentos
  Lista documentos no RAG
  
GET /api/rag/estatisticas
  Obtém estatísticas do RAG
```

### Sistema

```
GET /health
  Verifica saúde da aplicação
  
GET /
  Informações da API
```

---

## 📊 KPIs Alvo

| KPI | Alvo | Status |
|-----|------|--------|
| Conformidade | ≥95% | ✓ |
| Confiabilidade | ≥0.9 | ✓ |
| Tempo de Resposta | ≤10s | ✓ |
| Clareza (NeuroIndex L10) | ≥8.0 | ✓ |
| Cobertura | 100% | ✓ |

---

## 🧪 Testes

```bash
# Executar testes unitários
pytest tests/ -v

# Testes com cobertura
pytest tests/ --cov=api

# Testes de integração
pytest tests/integration/ -v

# Testes E2E
pnpm test:e2e
```

---

## 🐳 Docker Compose

```bash
# Iniciar todos os serviços
docker-compose up -d

# Parar serviços
docker-compose down

# Ver logs
docker-compose logs -f api
```

**Serviços inclusos:**
- API FastAPI (porta 8000)
- Frontend React (porta 5173)
- PostgreSQL (porta 5432)
- Redis (porta 6379)
- Qdrant (porta 6333)
- n8n (porta 5678)

---

## 🔐 Segurança

- Autenticação via JWT
- CORS configurado
- Validação de entrada com Pydantic
- SQL Injection prevention (SQLAlchemy)
- Variáveis de ambiente para secrets

---

## 📖 Documentação Adicional

- [API Documentation](docs/API.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)

---

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto é propriedade de Eng. Anibal Nisgoski.

---

## 👥 Suporte

Para suporte, abra uma issue no repositório ou entre em contato com o autor.

---

## 🎯 Roadmap

- [ ] Integração com LLM (OpenAI/Claude)
- [ ] Dashboard de analytics
- [ ] Exportação em múltiplos formatos
- [ ] API de webhooks
- [ ] Suporte a múltiplos idiomas
- [ ] Mobile app
- [ ] Integração com sistemas ERP

---

**Criado por Eng. Anibal Nisgoski**

*Sistema Analítico de IA – Análise Técnico-Normativa Inteligente*
