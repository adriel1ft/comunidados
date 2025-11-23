# API de Agentes para WhatsApp

Servidor FastAPI que utiliza agentes Agno com integração MCP para gerar respostas inteligentes a mensagens do WhatsApp sobre legislação brasileira.

## Visão Geral

Esta API é o núcleo de processamento de mensagens do projeto DevsImpacto. Ela recebe mensagens de texto ou áudio do usuário via WhatsApp e gera respostas usando:

- **Agno**: Framework para criar agentes de IA com LLMs
- **OpenAI**: Modelo GPT-4 Turbo para processamento de linguagem natural
- **MCP (Model Context Protocol)**: Integração com servidores de contexto para buscar dados legislativos
- **FastAPI**: Framework web assíncrono

## 📋 Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│         Orquestrador de Mensagens WhatsApp              │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ POST /process-message
                       ▼
┌───────────────────────────────────────────────────┐
│      API de Agentes WhatsApp (esta aplicação)     │
├───────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────────┐        ┌──────────────┐         │
│  │  Agente Agno │◄──────►│   OpenAI     │         │
│  │  + Tools MCP │        │   GPT-4      │         │
│  └──────────────┘        └──────────────┘         │
│         │                                         │
│         ├─────────────┬──────────┐                │
│         ▼             ▼          ▼                │
│    ┌────────┐  ┌──────────┐  ┌──────┐             │
│    │  MCP   │  │Construção│  │Cache │             │
│    │Projetos│  │ Prompts  │  │Tools │             │
│    │de Lei  │  │          │  │      │             │
│    └────────┘  └──────────┘  └──────┘             │
│                                                   │
└───────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Pré-requisitos

- **Python 3.10+**
- **[uv](https://github.com/astral-sh/uv)**: Gerenciador de pacotes ultrarrápido
- **Chave de API OpenAI**: Obtenha em https://platform.openai.com/api-keys

### Instalação

```bash
# 1. Clonar o repositório (se necessário)
cd api-agents-whatsapp

# 2. Criar ambiente virtual
uv venv

# 3. Ativar ambiente (Linux/macOS)
source .venv/bin/activate

# 4. Instalar dependências
uv pip install -e .

# 5. Configurar variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua OPENAI_API_KEY
```

### Iniciar a API

**Terminal 1 - API MCP de Projetos de Lei:**

```bash
cd ../api-mcp-projetos-lei
uv venv && source .venv/bin/activate
uv pip install -e .
mcp-projetos-lei
# Servidor MCP rodando em http://localhost:8000
```

**Terminal 2 - API de Agentes:**

```bash
cd ../api-agents-whatsapp
source .venv/bin/activate
api-agents
# API rodando em http://localhost:5000
```

### Testar a API

```bash
# Health check
curl http://localhost:5000/health

# Processar mensagem
curl -X POST "http://localhost:5000/process-message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Quais são os projetos sobre inteligência artificial?",
    "user_id": "5585988123456@c.us",
    "session_id": "sess_001",
    "message_type": "text",
    "user_preferences": {
      "topics": ["tecnologia", "educação"]
    }
  }'
```

**Documentação interativa:** http://localhost:5000/docs

## 📁 Estrutura do Projeto

```
api-agents-whatsapp/
├── .env.example              # Variáveis de ambiente (exemplo)
├── .env                      # Variáveis de ambiente (local)
├── .python-version           # Versão Python recomendada
├── pyproject.toml            # Dependências e configuração
├── README.md                 # Este arquivo
└── src/
    └── api_agents_whatsapp/
        ├── __init__.py       # Package initialization
        ├── main.py           # FastAPI app + entry point
        ├── config.py         # Configurações (BaseSettings)
        ├── models.py         # Modelos Pydantic (request/response)
        ├── routes.py         # Endpoints da API
        └── services.py       # Lógica de negócio (AgentService)
```

## 📚 Como Funciona

### Fluxo de Processamento

```
1. Receber Requisição
   └─ AgentRequest (user_message, user_id, session_id, message_type)

2. Conectar ao MCP
   └─ Estabelecer contexto com servidor MCP (Projetos de Lei)

3. Construir Prompt
   └─ Template dinâmico baseado em:
      - Tipo de mensagem (texto/áudio)
      - Preferências do usuário
      - Tópicos de interesse

4. Executar Agente Agno
   └─ Agent recebe prompt + tools MCP
      └─ LLM (GPT-4) processa com contexto
         └─ Retorna resposta estruturada

5. Pós-processamento
   └─ Detectar se deve enviar em áudio
   └─ Preparar texto auxiliar (se necessário)

6. Retornar AgentResponse
   └─ response_text
   └─ should_send_audio
   └─ auxiliary_text
   └─ confidence score
```

## 📊 Exemplo de Uso Completo

### 1. Requisição de Texto Simples

```bash
curl -X POST "http://localhost:5000/process-message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "O que é o Estatuto da Criança?",
    "user_id": "5585988123456@c.us",
    "session_id": "sess_001",
    "message_type": "text"
  }'
```

**Resposta:**

```json
{
  "session_id": "sess_001",
  "user_id": "5585988123456@c.us",
  "response_text": "O Estatuto da Criança e do Adolescente (ECA) é uma lei...",
  "auxiliary_text": null,
  "should_send_audio": false,
  "confidence": 0.85,
  "timestamp": "2025-11-23T01:45:00"
}
```

### 2. Requisição com Áudio

```bash
curl -X POST "http://localhost:5000/process-message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Quero saber sobre projetos de educação",
    "user_id": "5585988123456@c.us",
    "session_id": "sess_002",
    "message_type": "audio",
    "user_preferences": {
      "prefer_audio": true,
      "topics": ["educação"]
    }
  }'
```

**Resposta (note `should_send_audio: true`):**

```json
{
  "session_id": "sess_002",
  "user_id": "5585988123456@c.us",
  "response_text": "Existem vários projetos sobre educação...",
  "auxiliary_text": "📢 Esta resposta foi gerada pelo assistente de IA. Para mais informações, acesse o e-Cidadania.",
  "should_send_audio": true,
  "confidence": 0.85,
  "timestamp": "2025-11-23T01:46:00"
}
```

## 📚 Recursos Úteis

- [Documentação Agno](https://github.com/phidatahq/agno)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [Model Context Protocol](https://spec.modelcontextprotocol.io/)
