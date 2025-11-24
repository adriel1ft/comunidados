# Arquitetura do Sistema ZapCidadão

## Visão Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                          USUÁRIO FINAL                          │
│                         (WhatsApp App)                          │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ Mensagens (texto/áudio)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      WHATSAPP SERVICE                           │
│                      (wwebjs) :5002                             │
│  • Conexão com WhatsApp Web                                     │
│  • Recebe mensagens de usuários                                 │
│  • Envia respostas (texto/áudio)                                │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ HTTP POST
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ORCHESTRATOR :3000                        │
│  • Gerencia fluxo de mensagens                                  │
│  • Mantém sessões e contexto                                    │
│  • Coordena chamadas entre serviços                             │
│  • Gerencia preferências de usuários (MongoDB)                  │
└─────┬──────────┬──────────┬──────────┬─────────────────────────┘
      │          │          │          │
      │          │          │          └──────────┐
      │          │          │                     │
      ▼          ▼          ▼                     ▼
┌─────────┐ ┌─────────┐ ┌─────────┐       ┌─────────────┐
│ Backend │ │ Agents  │ │  Audio  │       │   MongoDB   │
│  :4000  │ │  :5000  │ │  :5001  │       │   :27017    │
└─────────┘ └─────────┘ └─────────┘       └─────────────┘
     │           │           │
     │           │           └─────────┐
     │           │                     │
     │           └────────┐            │
     │                    │            │
     ▼                    ▼            ▼
┌──────────┐       ┌─────────────────────────┐
│   MCP    │       │      S3 (LocalStack)    │
│  :8000   │       │         :4566           │
└──────────┘       └─────────────────────────┘
```

## Fluxo de Mensagem Detalhado

### 1. Mensagem de Texto

```
Usuário
  │
  │ 1. Envia: "Qual o status do PL 1234/2023?"
  ▼
WhatsApp Service
  │
  │ 2. POST /receive-message
  ▼
Orchestrator
  │
  │ 3. Identifica tipo: texto
  │ 4. POST /api/chat
  ▼
Backend (RAG Service)
  │
  │ 5. Query Claude + MCP
  ▼
MCP Projetos Lei
  │
  │ 6. Busca documentos sobre PL 1234/2023
  │ 7. Retorna dados estruturados
  ▼
Backend
  │
  │ 8. Formata resposta com fontes
  │ 9. POST /synthesize (se audioEnabled=true)
  ▼
Audio Processing
  │
  │ 10. Gera áudio com TTS
  │ 11. Salva no S3
  │ 12. Retorna base64/URL
  ▼
Backend
  │
  │ 13. Retorna resposta completa
  ▼
Orchestrator
  │
  │ 14. Envia para WhatsApp Service
  ▼
WhatsApp Service
  │
  │ 15. Envia resposta ao usuário
  ▼
Usuário
```

### 2. Mensagem de Áudio

```
Usuário
  │
  │ 1. Envia: 🎤 "Qual o PL sobre educação?"
  ▼
WhatsApp Service
  │
  │ 2. POST /receive-message (com audio_base64)
  ▼
Orchestrator
  │
  │ 3. Identifica tipo: áudio
  │ 4. POST /transcribe
  ▼
Audio Processing
  │
  │ 5. Whisper transcreve
  │ 6. Retorna: "Qual o PL sobre educação?"
  ▼
Orchestrator
  │
  │ 7. POST /api/chat (audioEnabled=true)
  ▼
Backend (RAG Service)
  │
  │ 8-12. [Processo RAG igual ao texto]
  ▼
Audio Processing
  │
  │ 13. TTS gera áudio da resposta
  ▼
Orchestrator
  │
  │ 14. Envia áudio + texto
  ▼
WhatsApp Service
  │
  │ 15. Envia 🔊 resposta em áudio
  ▼
Usuário
```

## Componentes e Responsabilidades

### WhatsApp Service (Node.js)
**Porta:** 5002  
**Tech:** wwebjs, Express

**Responsabilidades:**
- Conexão com WhatsApp Web
- Recepção de mensagens (texto/áudio/mídia)
- Envio de respostas ao usuário
- QR Code para autenticação
- Rate limiting de mensagens

### Orchestrator (Python/FastAPI)
**Porta:** 3000  
**Tech:** FastAPI, MongoDB, httpx

**Responsabilidades:**
- Orquestração central do fluxo
- Gerenciamento de sessões de usuário
- Buffer de mensagens
- Roteamento para serviços corretos
- Persistência de histórico
- Preferências de usuário

### Backend RAG Service (TypeScript) ✨ NOVO
**Porta:** 4000  
**Tech:** Express, Anthropic SDK, TypeScript

**Responsabilidades:**
- Chat com RAG usando Claude 3.5 Sonnet
- Integração com MCP para busca de documentos
- Validação de contexto (anti-alucinação)
- Formatação de respostas com fontes
- Integração com Audio API
- API REST para chat inteligente

**Endpoints:**
- `POST /api/chat` - Processa mensagens
- `GET /health` - Health check

### Agents API (Python/LangGraph)
**Porta:** 5000  
**Tech:** LangGraph, OpenAI

**Responsabilidades:**
- Processamento de linguagem natural
- Geração de respostas contextuais
- Decisão de formato de resposta
- Integração com LLMs

### Audio Processing (Python/FastAPI)
**Porta:** 5001  
**Tech:** FastAPI, OpenAI Whisper/TTS, boto3

**Responsabilidades:**
- **STT:** Transcrição de áudio (Whisper)
- **TTS:** Síntese de voz (OpenAI TTS)
- Upload/download de áudios (S3)
- Processamento de formatos de áudio

**Endpoints:**
- `POST /transcribe` - Áudio → Texto
- `POST /synthesize` - Texto → Áudio

### MCP Projetos Lei (Python/FastMCP)
**Porta:** 8000  
**Tech:** FastMCP, Playwright, httpx

**Responsabilidades:**
- Busca de projetos de lei
- Scraping da Câmara dos Deputados
- Dados estruturados sobre PLs
- Notícias relacionadas
- Links do e-Cidadania

**Tools:**
- `buscar_projetos_recentes`
- `buscar_projetos_mais_votados`
- `obter_detalhes_projeto`
- `buscar_noticias_tema`

### MongoDB
**Porta:** 27017  
**Tech:** MongoDB

**Armazena:**
- Perfis de usuários
- Histórico de conversas
- Preferências (áudio/texto)
- Sessões ativas

### LocalStack (S3)
**Porta:** 4566  
**Tech:** LocalStack

**Armazena:**
- Arquivos de áudio
- Cache de transcrições
- Logs de processamento

## Tecnologias Utilizadas

### Backend
- **TypeScript** - Backend RAG Service
- **Python** - Orchestrator, Agents, Audio, MCP
- **Node.js** - WhatsApp Service

### Frameworks
- **Express** - Backend REST API
- **FastAPI** - APIs Python (Orchestrator, Audio, MCP)
- **FastMCP** - Servidor MCP
- **LangGraph** - Agentes conversacionais

### AI/ML
- **Claude 3.5 Sonnet** (Anthropic) - RAG no Backend
- **GPT-4** (OpenAI) - Agentes
- **Whisper** (OpenAI) - Speech-to-Text
- **TTS** (OpenAI) - Text-to-Speech

### Infrastructure
- **Docker** - Containerização
- **Docker Compose** - Orquestração
- **MongoDB** - Database NoSQL
- **LocalStack** - S3 local

### Integrations
- **wwebjs** - WhatsApp Web
- **Playwright** - Web scraping
- **boto3** - S3 client
- **httpx** - HTTP cliente assíncrono

## Variáveis de Ambiente

Ver `.env.global.example` para lista completa. Principais:

```bash
# AI APIs
OPENAI_API_KEY=sk-...           # Para Agents e Audio
ANTHROPIC_API_KEY=sk-ant-...    # Para Backend RAG

# Service URLs (Docker)
MCP_PROJETOS_LEI_URL=http://api-mcp-projetos-lei:8000
AUDIO_API_URL=http://api-audio-processing:5001
BACKEND_API_URL=http://backend:4000

# Portas
BACKEND_PORT=4000
API_PORT_ORCHESTRATOR=3000
API_PORT_AGENTS=5000
API_PORT_AUDIO=5001
API_PORT_MCP=8000
API_PORT_WHATSAPP=5002

# Database
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB=devsimpacto
```

## Fluxos de Integração

### Opção 1: Frontend → Backend (Direto)
Para aplicações web/mobile que querem usar o RAG diretamente:

```
Frontend
  ↓
Backend:4000 /api/chat
  ↓
MCP + Audio APIs
  ↓
Resposta com texto + áudio + fontes
```

### Opção 2: WhatsApp → Orchestrator → Backend (Completo)
Para usuários do WhatsApp com gerenciamento de sessão:

```
WhatsApp
  ↓
WhatsApp Service:5002
  ↓
Orchestrator:3000
  ↓
Backend:4000 (RAG)
  ↓
MCP:8000 + Audio:5001
  ↓
Resposta orquestrada
  ↓
WhatsApp Service → Usuário
```

### Opção 3: Agents API (Legado)
Para compatibilidade com sistema anterior:

```
Orchestrator
  ↓
Agents API:5000
  ↓
MCP + LLMs
```

## Segurança

- [ ] Rate limiting em todos os endpoints
- [ ] Autenticação JWT
- [ ] Validação de inputs
- [ ] Sanitização de dados
- [ ] CORS configurado
- [ ] Secrets em .env (não commitados)
- [ ] HTTPS em produção

## Monitoramento

Ver logs em tempo real:
```bash
# Todos
docker-compose logs -f

# Backend específico
docker-compose logs -f backend

# Múltiplos
docker-compose logs -f backend orchestrator api-mcp-projetos-lei
```

Health checks:
```bash
curl http://localhost:4000/health  # Backend
curl http://localhost:3000/health  # Orchestrator
curl http://localhost:5001/health  # Audio
curl http://localhost:8000/health  # MCP
```

## Escalabilidade

Para escalar o sistema:

1. **Horizontal:** Replicar containers com load balancer
2. **Cache:** Adicionar Redis para respostas frequentes
3. **Queue:** Adicionar RabbitMQ/Kafka para mensagens assíncronas
4. **CDN:** Para servir áudios estáticos
5. **Database:** MongoDB Atlas para clustering

## Troubleshooting

Ver [backend/INTEGRATION.md](../backend/INTEGRATION.md) para guia completo de troubleshooting.

## Próximos Passos

1. ✅ Backend integrado com RAG
2. 🔄 Testes end-to-end
3. 📊 Dashboard de monitoramento
4. 🔐 Sistema de autenticação
5. 🚀 Deploy em produção
6. 📱 Frontend web/mobile

---

**Documentação atualizada:** Novembro 2025  
**Status:** ✅ Sistema totalmente integrado e funcional
