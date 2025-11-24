# 🎼 Orquestrador de Mensagens WhatsApp

Servidor FastAPI que coordena o fluxo completo de mensagens do WhatsApp, integrando processamento de áudio, agentes de IA e gerenciamento de usuários.

## 🎯 Visão Geral

O Orquestrador é o **coração da comunicação** do projeto DevsImpacto. Ele:

- ✅ Recebe mensagens do [WhatsApp Service](../whatsapp-service)
- ✅ Agrupa mensagens em **buffers inteligentes** (com timeout)
- ✅ Transcreve áudio via [API de Áudio](../api-audio-processing)
- ✅ Processa com **agentes de IA** via [API de Agentes](../api-agents-whatsapp)
- ✅ Gerencia **usuários e sessões** (MongoDB)
- ✅ Decide formato de resposta (texto/áudio)
- ✅ Envia resposta ao WhatsApp

## 📊 Arquitetura

```
┌─────────────────────────────────────────────┐
│         WhatsApp Web (usuário)              │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      WhatsApp Service (Node.js)             │
│   (recebe e envia mensagens)                │
└──────────────┬──────────────────────────────┘
               │
               │ POST /receive-message
               ▼
┌─────────────────────────────────────────────────────────┐
│  Orquestrador (esta aplicação - FastAPI)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐                                   │
│  │ Message Buffer   │◄─── Agrupa mensagens             │
│  │ Service          │     (timeout inteligente)        │
│  └────────┬─────────┘                                   │
│           │                                             │
│           ├─────────────────┬──────────────┐            │
│           ▼                 ▼              ▼            │
│    ┌────────────┐    ┌────────────┐  ┌────────────┐    │
│    │Audio API   │    │Agent API   │  │User Service│    │
│    │(transcrição│    │(LLM + MCP) │  │(MongoDB)   │    │
│    │e síntese)  │    │            │  │            │    │
│    └────────────┘    └────────────┘  └────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
               │
               │ POST /send-message
               ▼
┌─────────────────────────────────────────────┐
│      WhatsApp Service (resposta)            │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│    WhatsApp Web (resposta ao usuário)       │
└─────────────────────────────────────────────┘
```

## ⚡ Fluxo de Processamento (com Batching)

```
Usuário envia Msg 1 (10:00:00)
     │
     ├─► [Buffer] + Timer: 30s
     │
     ▼
Usuário envia Msg 2 (10:00:05) ◄─── Menos de 15s!
     │
     ├─► [Buffer: 2 msgs] + Reset Timer
     │
     ▼
Usuário envia Msg 3 (10:00:12) ◄─── Menos de 15s!
     │
     ├─► [Buffer: 3 msgs] + Reset Timer
     │
     ▼
Usuário PARA (nenhuma mensagem por 15s)
     │
     ├─► 🎯 PROCESSA BUFFER
     │
     ├─► 1️⃣  Transcrever áudios (se houver)
     │
     ├─► 2️⃣  Combinar mensagens
     │
     ├─► 3️⃣  Chamar agente LLM
     │
     ├─► 4️⃣  Decidir se envia áudio
     │
     ├─► 5️⃣  Gerar áudio (se necessário)
     │
     ├─► 6️⃣  Enviar resposta ao WhatsApp
     │
     └─► ✅ SALVAR NA SESSION

     Result: UMA resposta única para 3 mensagens!
```

## 🚀 Quick Start

### Pré-requisitos

- **Python 3.10+**
- **[uv](https://github.com/astral-sh/uv)**: Gerenciador de pacotes ultrarrápido
- **MongoDB**: Local ou Docker
- **APIs em execução**:
  - WhatsApp Service (porta 3001)
  - API de Áudio (porta 5002)
  - API de Agentes (porta 5000)

### 1️⃣ Instalar `uv` (se necessário)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2️⃣ Configurar Ambiente

```bash
# Entrar no diretório
cd orchestrator

# Criar ambiente virtual
uv venv

# Ativar (Linux/macOS)
source .venv/bin/activate

# Ativar (Windows)
# .venv\Scripts\activate
```

### 3️⃣ Instalar Dependências

```bash
uv pip install -e .
```

### 4️⃣ Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
# (ver seção "Variáveis de Ambiente" abaixo)
```

### 5️⃣ Iniciar MongoDB (se usando Docker)

```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  mongo:latest
```

### 6️⃣ Iniciar o Orquestrador

```bash
orchestrator
# Ou com desenvolvimento:
orchestrator --reload
```

✅ API rodando em `http://localhost:3000`
📚 Documentação: `http://localhost:3000/docs`

## 📁 Estrutura do Projeto

```
orchestrator/
├── .env.example                    # Variáveis de ambiente (exemplo)
├── .env                            # Variáveis de ambiente (local)
├── .python-version                 # Versão Python recomendada
├── pyproject.toml                  # Dependências e configuração
├── README.md                       # Este arquivo
└── src/orchestrator/
    ├── __init__.py                 # Exports principais
    ├── main.py                     # FastAPI app + entry point
    ├── config.py                   # Configurações (BaseSettings)
    ├── models.py                   # Modelos Pydantic (request/response)
    ├── models_db.py                # Modelos MongoDB (UserDB, SessionDB)
    ├── routes.py                   # Endpoints da API
    └── services/
        ├── __init__.py
        ├── message_buffer_service.py   # Buffer inteligente de mensagens
        ├── message_service.py          # Orquestração do fluxo completo
        ├── user_service.py             # Gerenciamento de usuários
        ├── audio_service.py            # Integração com API de Áudio
        └── agent_service.py            # Integração com API de Agentes
```

## 🔌 Endpoints da API

### Receber Mensagem

```bash
POST /receive-message
Content-Type: application/json

{
  "user_id": "5585988123456@c.us",
  "chatId": "5585988123456@c.us",
  "message_type": "text",
  "message": "Olá, como funcionam os projetos de lei?",
  "timestamp": "2025-11-23T10:00:00"
}
```

**Resposta (mensagem adicionada ao buffer):**

```json
{
  "status": "buffered",
  "buffer_status": {
    "user_id": "5585988123456@c.us",
    "messages_count": 1,
    "is_processing": false,
    "last_message": "2025-11-23T10:00:00",
    "messages": [
      {
        "type": "text",
        "timestamp": "2025-11-23T10:00:00",
        "preview": "Olá, como funcionam os projetos de lei?"
      }
    ]
  },
  "message": "Mensagem adicionada ao buffer, aguardando mais mensagens ou timeout..."
}
```

### Forçar Processamento

```bash
POST /process-now/{user_id}
```

Força processamento do buffer imediatamente (útil para testes).

```bash
curl -X POST http://localhost:5001/process-now/5585988123456@c.us
```

### Obter Perfil de Usuário

```bash
GET /user/{user_id}
```

### Atualizar Perfil

```bash
POST /update-user-profile?user_id={user_id}&name={name}&age={age}&location={location}
```

## 🧪 Testando a API

### 2️⃣ Enviar Múltiplas Mensagens

**Terminal 1 - Iniciar Orquestrador:**

```bash
orchestrator
```

**Terminal 2 - Enviar mensagens:**

```bash
# Mensagem 1
curl -X POST http://localhost:3000/receive-message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "chatId": "chat123",
    "message_type": "text",
    "message": "Primeira mensagem",
    "timestamp": "2025-11-23T10:00:00"
  }'

# Mensagem 2 (aguarde < 15s)
sleep 5
curl -X POST http://localhost:3000/receive-message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "chatId": "chat123",
    "message_type": "text",
    "message": "Segunda mensagem",
    "timestamp": "2025-11-23T10:00:05"
  }'

# Mensagem 3 (aguarde < 15s)
sleep 5
curl -X POST http://localhost:3000/receive-message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "chatId": "chat123",
    "message_type": "text",
    "message": "Terceira mensagem",
    "timestamp": "2025-11-23T10:00:10"
  }'

# Aguarde 15s... Buffer será processado automaticamente!
```

## 🛠️ Desenvolvimento

### Instalar Dependências de Desenvolvimento

```bash
uv pip install -e ".[dev]"
```

## 📝 Logging

O Orquestrador usa logging estruturado com emojis para facilitar compreensão.

**Níveis de Log:**

```
📨 = Mensagem recebida
🎵 = Áudio detectado
🤖 = Agente processando
🔊 = Síntese de áudio
📝 = Alterações de dados
✅ = Sucesso
❌ = Erro
⚠️  = Aviso
⏱️  = Timeout
```

## 🔗 Integração com Outros Serviços

### WhatsApp Service

**Como envia mensagens para o Orquestrador:**

```javascript
// whatsapp-service/handlers.js
const response = await fetch("http://localhost:5001/receive-message", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    user_id: message.from,
    chatId: message.from,
    message_type: message.type === "ptt" ? "audio" : "text",
    message: message.body || base64Audio,
    timestamp: new Date().toISOString(),
  }),
});
```

### API de Áudio

**Como o Orquestrador a usa:**

```python
# Transcrição
POST http://localhost:5001/transcribe
Files: {audio: <arquivo>}
Response: {"text": "..."}

# Síntese
POST http://localhost:5001/synthesize
JSON: {"text": "...", "auxiliary_text": "..."}
