# 📋 GUIA COMPLETO DE SOLUÇÕES 100% GRATUITAS
## Sistema Analítico de IA — Criado por Eng. Anibal Nisgoski

---

## 🎯 RESUMO EXECUTIVO

O **Sistema Analítico de IA** foi desenvolvido utilizando **exclusivamente tecnologias 100% gratuitas e open-source**, tanto para execução local quanto em nuvem. Este guia detalha cada componente, sua instalação, configuração e alternativas equivalentes.

**Sem custos com:**
- ✅ Infraestrutura
- ✅ Bancos de dados
- ✅ Cache e indexação
- ✅ IA/ML
- ✅ Deploy
- ✅ Monitoramento
- ✅ Testes e CI/CD

---

## 🚀 STACK TÉCNICO GRATUITO

| Camada | Componente | Licença | Alternativas |
|--------|-----------|---------|--------------|
| **Frontend** | React 18+ | MIT | Vue, Svelte |
| | TypeScript | Apache 2.0 | JavaScript puro |
| | Tailwind CSS | MIT | Bootstrap, Material UI |
| | Shadcn/UI | MIT | Radix UI, Headless UI |
| **Backend** | FastAPI | MIT | Django, Flask, Fastify |
| | Python 3.12 | PSF | Node.js, Go, Rust |
| | Pydantic | MIT | Marshmallow, Cerberus |
| | SQLAlchemy | MIT | Prisma, Sequelize |
| **Dados** | PostgreSQL 15 | PostgreSQL | MySQL, MariaDB, SQLite |
| | Redis 7 | BSD | Memcached, Valkey |
| | Qdrant | AGPL/Elastic | Milvus, Weaviate, Pinecone |
| **IA/ML** | Hugging Face | Apache 2.0 | OpenAI, Anthropic |
| | LangChain | MIT | LlamaIndex, Semantic Kernel |
| | Sentence Transformers | Apache 2.0 | FastText, Word2Vec |
| **Deploy** | Docker | Apache 2.0 | Podman, Containerd |
| | Docker Compose | Apache 2.0 | Kubernetes (k3s) |
| | Nginx | BSD | Apache, Caddy |
| **Automação** | n8n Community | Fair License | Zapier (pago), Make (pago) |
| **Testes** | Pytest | MIT | Jest, Vitest |
| | Cypress | MIT | Playwright, Selenium |
| **CI/CD** | GitHub Actions | Free | GitLab CI, Gitea |

---

## 📦 INSTALAÇÃO LOCAL

### Pré-requisitos
```bash
# Verificar versões
python3 --version          # Python 3.11+
node --version             # Node 18+
docker --version           # Docker 20.10+
docker-compose --version   # Docker Compose 2.0+
git --version              # Git 2.30+
```

### 1. Clonar Repositório
```bash
git clone https://github.com/seu-usuario/sistema_analitico_ia.git
cd sistema_analitico_ia
```

### 2. Instalar Dependências Frontend
```bash
cd client
npm install
# ou
pnpm install
```

### 3. Instalar Dependências Backend
```bash
cd ../api
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
```bash
# Criar arquivo .env na raiz
cat > .env << EOF
# Backend
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
DEBUG=true

# Banco de Dados
DATABASE_URL=postgresql://user:password@localhost:5432/sistema_analitico
REDIS_URL=redis://localhost:6379/0

# Qdrant (Banco Vetorial)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# LLM (OpenAI ou compatível)
LLM_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7

# Segurança
SECRET_KEY=sua-chave-super-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Frontend
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=Sistema Analítico de IA
VITE_APP_LOGO=/logo.svg
EOF
```

### 5. Iniciar com Docker Compose
```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f api
docker-compose logs -f web
```

### 6. Iniciar Desenvolvimento Local (sem Docker)

**Terminal 1 - Backend:**
```bash
cd api
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd client
npm run dev
# Acesso em http://localhost:5173
```

---

## 🗄️ BANCOS DE DADOS GRATUITOS

### PostgreSQL (Banco Principal)
**Instalação Local:**
```bash
# macOS
brew install postgresql@15

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows
# Baixar de https://www.postgresql.org/download/windows/

# Iniciar serviço
sudo systemctl start postgresql

# Criar banco
createdb sistema_analitico
createuser app_user
psql -U postgres -d sistema_analitico -c "ALTER USER app_user WITH PASSWORD 'senha123';"
```

**Alternativas Gratuitas:**
- **SQLite**: Perfeito para desenvolvimento local (sem servidor)
- **MySQL 8.0**: Compatível, mesma performance
- **MariaDB**: Fork open-source do MySQL

### Redis (Cache)
**Instalação Local:**
```bash
# macOS
brew install redis

# Ubuntu/Debian
sudo apt-get install redis-server

# Windows (via WSL ou Docker)
docker run -d -p 6379:6379 redis:7

# Iniciar
redis-server
```

**Alternativas Gratuitas:**
- **Valkey**: Fork do Redis (mantido pela Linux Foundation)
- **Memcached**: Mais simples, sem persistência

### Qdrant (Banco Vetorial)
**Instalação Local:**
```bash
# Docker (recomendado)
docker run -p 6333:6333 -p 6334:6334 \
  -v ./qdrant_storage:/qdrant/storage:z \
  qdrant/qdrant

# Acesso: http://localhost:6333/dashboard
```

**Alternativas Gratuitas:**
- **Milvus**: Banco vetorial open-source em C++
- **Weaviate**: Banco vetorial com GraphQL
- **Chroma**: Leve, perfeito para desenvolvimento

---

## 🤖 IA/ML 100% GRATUITA

### Opção 1: LLMs Open-Source Locais

**Ollama (Recomendado)**
```bash
# Instalar de https://ollama.ai

# Baixar modelo
ollama pull mistral  # 7B, rápido
ollama pull neural-chat  # 7B, otimizado
ollama pull llama2  # 7B, versátil

# Iniciar servidor
ollama serve

# Usar em código
curl http://localhost:11434/api/generate \
  -d '{"model":"mistral","prompt":"Olá"}'
```

**Alternativas:**
- **LM Studio**: Interface gráfica para rodar LLMs locais
- **GPT4All**: Modelos quantizados (1-4GB)
- **LocalAI**: Compatível com OpenAI API

### Opção 2: APIs Gratuitas

| Serviço | Limite Gratuito | Modelo |
|---------|-----------------|--------|
| **Hugging Face Inference** | 30k requisições/mês | Mistral, Llama 2, etc |
| **Together AI** | $5/mês crédito | Mistral, Llama 2, etc |
| **Replicate** | $5/mês crédito | Modelos diversos |
| **Groq** | Gratuito (beta) | LLaMA 2, Mixtral |
| **Perplexity** | Gratuito | Claude, GPT-4 |

### Embeddings Gratuitos
```python
from sentence_transformers import SentenceTransformer

# Modelo gratuito
model = SentenceTransformer('all-MiniLM-L6-v2')

# Gerar embeddings
sentences = ["Olá", "Mundo"]
embeddings = model.encode(sentences)
```

---

## 🌐 DEPLOY GRATUITO EM NUVEM

### Opção 1: Railway (Recomendado)
**Características:**
- 500 horas/mês gratuitas
- PostgreSQL incluído
- Redis incluído
- Deploy automático via GitHub

**Passos:**
```bash
# 1. Criar conta em https://railway.app
# 2. Conectar repositório GitHub
# 3. Criar serviços:
#    - Backend (FastAPI)
#    - Frontend (React)
#    - PostgreSQL
#    - Redis
# 4. Configurar variáveis de ambiente
# 5. Deploy automático
```

### Opção 2: Render
**Características:**
- 750 horas/mês gratuitas
- PostgreSQL gratuito
- Deploy via GitHub
- Suporte a Docker

**Passos:**
```bash
# 1. Criar conta em https://render.com
# 2. Criar Web Service
# 3. Conectar repositório
# 4. Configurar build command
# 5. Deploy automático
```

### Opção 3: Heroku (Free Tier Descontinuado)
**Alternativa:** Use Railway ou Render

### Opção 4: VPS Gratuito

| Serviço | Limite | Especificações |
|---------|--------|----------------|
| **Oracle Cloud** | Sempre gratuito | 2 vCPU, 1GB RAM, 20GB SSD |
| **AWS Free Tier** | 12 meses | t2.micro, 1GB RAM, 20GB SSD |
| **Google Cloud** | 12 meses | e2-micro, 0.5GB RAM, 30GB SSD |
| **Azure** | 12 meses | B1S, 1GB RAM, 30GB SSD |

**Deploy em VPS Gratuito:**
```bash
# 1. Criar conta e instância
# 2. SSH na máquina
ssh ubuntu@seu-ip

# 3. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Clonar repositório
git clone seu-repo
cd sistema_analitico_ia

# 5. Iniciar com Docker Compose
docker-compose up -d

# 6. Configurar Nginx como reverse proxy
# (ver seção abaixo)
```

---

## 🔒 SEGURANÇA GRATUITA

### SSL/TLS Gratuito
```bash
# Let's Encrypt + Certbot
sudo apt-get install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot certonly --standalone -d seu-dominio.com

# Renovação automática
sudo systemctl enable certbot.timer
```

### Firewall
```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Monitoramento Gratuito
- **Prometheus**: Coleta de métricas
- **Grafana**: Visualização (versão open-source)
- **Sentry**: Rastreamento de erros
- **UptimeRobot**: Monitoramento de uptime

---

## 🧪 TESTES GRATUITOS

### Backend (Pytest)
```bash
# Instalar
pip install pytest pytest-cov

# Executar testes
pytest api/tests/

# Com cobertura
pytest --cov=api api/tests/
```

### Frontend (Vitest)
```bash
# Instalar
npm install -D vitest

# Executar
npm run test

# Com cobertura
npm run test:coverage
```

### E2E (Cypress)
```bash
# Instalar
npm install -D cypress

# Abrir interface
npx cypress open

# Executar headless
npx cypress run
```

---

## 🔄 CI/CD GRATUITO (GitHub Actions)

**Arquivo: `.github/workflows/test.yml`**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r api/requirements.txt
      
      - name: Run tests
        run: |
          pytest api/tests/
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 📊 MONITORAMENTO GRATUITO

### Prometheus + Grafana
```bash
# Docker Compose adicional
docker run -d -p 9090:9090 \
  -v ./prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

docker run -d -p 3000:3000 \
  grafana/grafana
```

### Sentry (Rastreamento de Erros)
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://seu-dsn@sentry.io/projeto-id",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0
)
```

---

## 🛠️ FERRAMENTAS ADICIONAIS GRATUITAS

| Ferramenta | Uso | Alternativa |
|-----------|-----|-----------|
| **Git** | Controle de versão | Mercurial |
| **GitHub** | Repositório | GitLab, Gitea |
| **VS Code** | Editor | Vim, Neovim, Sublime |
| **Postman** | API testing | Insomnia, REST Client |
| **DBeaver** | Database GUI | pgAdmin, MySQL Workbench |
| **Figma** | Design | Penpot, Inkscape |
| **Excalidraw** | Diagramas | Draw.io |

---

## 💰 CUSTO TOTAL ANUAL

| Componente | Custo |
|-----------|------|
| **Infraestrutura** | R$ 0 (VPS gratuito) |
| **Bancos de Dados** | R$ 0 (Inclusos) |
| **IA/ML** | R$ 0 (Open-source) |
| **Deploy** | R$ 0 (Railway/Render) |
| **Domínio** | R$ 30-50 (Namecheap) |
| **SSL** | R$ 0 (Let's Encrypt) |
| **Monitoramento** | R$ 0 (Prometheus/Grafana) |
| **CI/CD** | R$ 0 (GitHub Actions) |
| **TOTAL** | **R$ 30-50/ano** |

---

## 🎓 RECURSOS DE APRENDIZADO GRATUITOS

### Documentação
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Docs](https://docs.docker.com/)

### Cursos
- [FreeCodeCamp](https://www.freecodecamp.org/) - YouTube
- [Coursera](https://www.coursera.org/) - Cursos gratuitos
- [Udemy](https://www.udemy.com/) - Cursos gratuitos frequentes
- [MIT OpenCourseWare](https://ocw.mit.edu/)

### Comunidades
- [Stack Overflow](https://stackoverflow.com/)
- [Dev.to](https://dev.to/)
- [Reddit r/learnprogramming](https://reddit.com/r/learnprogramming/)
- [Discord Communities](https://discord.com/)

---

## 🚀 PRÓXIMOS PASSOS

1. **Clonar e executar localmente** (5 min)
2. **Configurar banco de dados** (10 min)
3. **Testar endpoints** (15 min)
4. **Fazer deploy em Railway** (20 min)
5. **Configurar domínio** (10 min)
6. **Integrar IA open-source** (30 min)

**Tempo total: ~90 minutos para ter um sistema em produção!**

---

## 📞 SUPORTE

- **Issues**: GitHub Issues
- **Discussões**: GitHub Discussions
- **Email**: seu-email@example.com
- **Comunidade**: Discord/Slack

---

## 📄 LICENÇA

Este projeto é 100% open-source e gratuito. Veja `LICENSE` para detalhes.

**Criado por Eng. Anibal Nisgoski**
