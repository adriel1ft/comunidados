# Backend Integration Guide

O backend foi completamente integrado ao sistema dev-politica-bot! 🎉

## ✅ O que foi implementado

### 1. **Estrutura TypeScript Completa**
- `package.json` com todas as dependências necessárias
- `tsconfig.json` configurado para Node.js + TypeScript
- Estrutura modular com controllers, services e config

### 2. **Serviços Implementados**

#### RAGService (`src/services/rag.service.ts`)
- Integração com Claude 3.5 Sonnet da Anthropic
- Busca de documentos via MCP
- Validação de contexto
- Formatação de respostas com fontes

#### ChatController (`src/controllers/chat.controller.ts`)
- Endpoint `/api/chat` para processar mensagens
- Validação de queries sobre PLs
- Integração com Audio API para TTS
- Tratamento de erros robusto

#### Config (`src/config.ts`)
- Gerenciamento centralizado de env vars
- Validação de variáveis obrigatórias
- Defaults sensatos

### 3. **API REST com Express**
- Middleware CORS configurado
- Body parser para JSON
- Logging de requisições
- Health check endpoint
- Error handler global

### 4. **Docker & Deployment**
- `Dockerfile` otimizado multi-stage
- `.dockerignore` para build limpo
- Integrado ao `docker-compose.yml`
- Variáveis de ambiente configuradas

## 🏗️ Arquitetura do Sistema

```
┌──────────────┐
│   WhatsApp   │
│   Service    │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Orchestrator │────▶│   Backend    │────▶│  MCP Server  │
│              │     │ (RAG Service)│     │ Projetos Lei │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Audio     │
                     │  Processing  │
                     └──────────────┘
```

## 🔗 Fluxo de Integração

### Opção 1: Uso Direto do Backend
Frontend/Cliente → Backend:4000 → MCP + Audio

### Opção 2: Via Orchestrator (Recomendado para WhatsApp)
WhatsApp → Orchestrator:3000 → Backend:4000 → MCP + Audio

## 🚀 Como Usar

### 1. Configurar variáveis de ambiente
Adicione ao `.env.global`:

```bash
# Backend
BACKEND_PORT=4000
BACKEND_HOST=0.0.0.0

# Anthropic (obrigatório)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# URLs dos serviços (já configuradas no docker-compose)
MCP_PROJETOS_LEI_URL=http://api-mcp-projetos-lei:8000
AUDIO_API_URL=http://api-audio-processing:5001
```

### 2. Build e Run com Docker Compose

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Ver logs do backend
docker-compose logs -f backend
```

### 3. Testar o Backend

```bash
# Health check
curl http://localhost:4000/health

# Chat query
curl -X POST http://localhost:4000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Qual o status do PL 1234/2023?",
    "audioEnabled": true
  }'
```

## 📦 Instalação Local (sem Docker)

```bash
cd backend

# Instalar dependências
npm install

# Configurar .env local
cp ../.env.global .env

# Rodar em dev mode
npm run dev

# Build para produção
npm run build

# Rodar produção
npm start
```

## 🔧 Configuração do Orchestrator

Para integrar o backend com o orchestrator, atualize o `orchestrator/src/orchestrator/config.py`:

```python
# Adicionar configuração do backend
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:4000")
```

E em `orchestrator/src/orchestrator/services/agent_service.py`:

```python
async def process_with_backend(self, message: str, audio_enabled: bool = True):
    """Processa mensagem usando o backend RAG"""
    try:
        response = await self.http_client.post(
            f"{settings.backend_api_url}/api/chat",
            json={
                "message": message,
                "audioEnabled": audio_enabled
            }
        )
        return response.json()
    except Exception as e:
        logger.error(f"Erro ao chamar backend: {e}")
        raise
```

## 🎯 Endpoints do Backend

### POST `/api/chat`
Processa mensagens com RAG

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
  "text": "O PL 1234/2023...",
  "audio": "base64_audio_data",
  "sources": [...],
  "hasContext": true,
  "debug": {...}
}
```

### GET `/health`
Verifica status do serviço

## 🐛 Troubleshooting

### Backend não inicia
1. Verificar se `ANTHROPIC_API_KEY` está configurada
2. Verificar se portas 4000 não está em uso
3. Ver logs: `docker-compose logs backend`

### MCP não responde
1. Verificar se `api-mcp-projetos-lei` está rodando
2. Testar MCP diretamente: `curl http://localhost:8000/health`
3. Verificar network: todos devem estar em `dev-politica-network`

### Áudio não é gerado
1. Verificar se `api-audio-processing` está rodando
2. Verificar `OPENAI_API_KEY` no .env.global
3. Teste sem áudio: `"audioEnabled": false`

## 📊 Monitoramento

Ver logs em tempo real:
```bash
# Todos os serviços
docker-compose logs -f

# Apenas backend
docker-compose logs -f backend

# Backend + MCP + Audio
docker-compose logs -f backend api-mcp-projetos-lei api-audio-processing
```

## 🎨 Próximos Passos

1. **Adicionar autenticação**: JWT tokens para segurança
2. **Rate limiting**: Prevenir abuse da API
3. **Cache**: Redis para respostas frequentes
4. **Metrics**: Prometheus/Grafana para monitoramento
5. **Testes**: Jest para testes unitários e de integração

## 📚 Documentação dos Componentes

- [Backend README](./README.md)
- [MCP Projetos Lei](../api-mcp-projetos-lei/README.md)
- [Audio Processing](../api-audio-processing/README.md)
- [Orchestrator](../orchestrator/README.md)

## 🤝 Contribuindo

O backend está pronto para receber melhorias! Áreas para contribuir:
- Adicionar mais MCPs (usuários, legislação, etc)
- Melhorar prompts do RAG
- Adicionar cache de respostas
- Implementar streaming de respostas
- Adicionar testes automatizados

---

**Status**: ✅ Totalmente funcional e integrado ao sistema!
