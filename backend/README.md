# Backend - RAG Service

Backend service que fornece chat com RAG (Retrieval-Augmented Generation) usando Claude 3.5 Sonnet e integração com MCP (Model Context Protocol).

## 🎯 Funcionalidades

- Chat com RAG usando Claude 3.5 Sonnet
- Integração com MCP Server de Projetos de Lei
- Geração de áudio via API de processamento de áudio
- Validação de contexto e fontes
- API REST com Express + TypeScript

## 🏗️ Arquitetura

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│   Cliente   │─────▶│     Backend      │─────▶│  MCP Projetos Lei   │
│  (Frontend) │      │  (RAG Service)   │      │   (Busca docs)      │
└─────────────┘      └──────────────────┘      └─────────────────────┘
                              │
                              │
                              ▼
                     ┌──────────────────┐
                     │  Audio Processing│
                     │   (TTS/Whisper)  │
                     └──────────────────┘
```

## 🚀 Endpoints

### POST `/api/chat`

Processa mensagens de chat com RAG.

**Request:**
```json
{
  "message": "Qual o status do PL 1234/2023?",
  "audioEnabled": true
}
```

**Response:**
```json
{
  "text": "O PL 1234/2023 está em tramitação...",
  "audio": "base64_encoded_audio",
  "sources": [
    {
      "pl_number": "PL 1234/2023",
      "author": "Deputado X",
      "status": "Em tramitação",
      "content": "..."
    }
  ],
  "hasContext": true,
  "debug": {
    "query": "Qual o status do PL 1234/2023?",
    "isPLQuery": true,
    "sourcesFound": 1
  }
}
```

### GET `/health`

Health check do serviço.

**Response:**
```json
{
  "status": "ok",
  "service": "backend",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## 🔧 Variáveis de Ambiente

```bash
# Server
BACKEND_PORT=4000
BACKEND_HOST=0.0.0.0

# Anthropic
ANTHROPIC_API_KEY=sk-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Services
MCP_PROJETOS_LEI_URL=http://api-mcp-projetos-lei:8000
AUDIO_API_URL=http://api-audio-processing:5001

# Debug
DEBUG=false
```

## 📦 Desenvolvimento

### Instalar dependências
```bash
npm install
```

### Rodar em modo dev
```bash
npm run dev
```

### Build
```bash
npm run build
```

### Rodar produção
```bash
npm start
```

## 🐳 Docker

### Build
```bash
docker build -t dev-politica-bot-backend .
```

### Run
```bash
docker run -p 4000:4000 \
  -e ANTHROPIC_API_KEY=sk-... \
  -e MCP_PROJETOS_LEI_URL=http://api-mcp-projetos-lei:8000 \
  dev-politica-bot-backend
```

## 📝 Estrutura de Código

```
backend/
├── src/
│   ├── index.ts              # Entry point e server setup
│   ├── config.ts             # Configurações e variáveis de ambiente
│   ├── controllers/
│   │   └── chat.controller.ts   # Controller de chat
│   └── services/
│       └── rag.service.ts       # Serviço de RAG com Claude
├── Dockerfile
├── package.json
└── tsconfig.json
```

## 🧠 RAG Service

O `RAGService` implementa:

1. **Query com RAG**: Usa Claude + MCP para buscar documentos relevantes
2. **Validação de contexto**: Verifica se há informações reais nos documentos
3. **Extração estruturada**: Parseia respostas JSON do Claude
4. **Formatação para fala**: Prepara texto para TTS

### Regras do RAG

- ✅ SEMPRE usa MCP para buscar documentos
- ✅ NUNCA inventa informações
- ✅ Cita fontes quando disponível
- ✅ Responde apenas com info dos documentos
- ❌ Não alucina dados sobre PLs

## 🔗 Integração com outros serviços

### MCP Projetos Lei
Busca informações sobre projetos de lei brasileiros.

### Audio Processing
Gera áudio a partir do texto da resposta usando OpenAI TTS.

### Orchestrator (opcional)
O backend pode ser usado diretamente ou via orchestrator para fluxos mais complexos.

## 🧪 Testes

Para testar o backend:

```bash
curl -X POST http://localhost:4000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Qual o status do PL 1234/2023?",
    "audioEnabled": true
  }'
```

## 📊 Logs

O backend loga:
- Todas as requisições HTTP
- Queries ao RAG service
- Chamadas ao MCP
- Geração de áudio
- Erros e warnings

## 🐛 Debug

Para debug detalhado:
```bash
DEBUG=true npm run dev
```

## 📚 Documentação Relacionada

- [Claude AI SDK](https://docs.anthropic.com/claude/reference/client-sdks)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Express.js](https://expressjs.com/)
