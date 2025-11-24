# Quick Start Guide - Backend Integration

Este guia rápido ajuda você a começar com o backend integrado do ZapCidadão.

## 🚀 Início Rápido (5 minutos)

### 1. Configurar variáveis de ambiente

Copie o arquivo de exemplo:
```bash
cp .env.global.example .env.global
```

Edite `.env.global` e adicione suas API keys:
```bash
# OBRIGATÓRIO - Para o backend RAG
ANTHROPIC_API_KEY=sk-ant-seu-token-aqui

# OBRIGATÓRIO - Para áudio e agents
OPENAI_API_KEY=sk-seu-token-aqui
```

### 2. Build e iniciar todos os serviços

```bash
# Build da imagem base
docker build -f Dockerfile.base -t dev-politica-bot-base:latest .

# Build e iniciar todos os serviços
docker-compose build
docker-compose up -d
```

### 3. Verificar se tudo está rodando

```bash
# Health checks
curl http://localhost:4000/health  # Backend ✨
curl http://localhost:3000/health  # Orchestrator
curl http://localhost:5001/health  # Audio
curl http://localhost:8000/health  # MCP
```

Esperado: `{"status":"ok",...}` em todos.

### 4. Testar o Backend RAG

```bash
curl -X POST http://localhost:4000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quais são os projetos de lei mais votados recentemente?",
    "audioEnabled": false
  }'
```

Resposta esperada:
```json
{
  "text": "Aqui estão os projetos...",
  "audio": null,
  "sources": [
    {
      "pl_number": "PL 1234/2023",
      "author": "Deputado X",
      "status": "Em tramitação",
      "content": "..."
    }
  ],
  "hasContext": true
}
```

## 🧪 Testes Completos

### Teste 1: Chat sem áudio
```bash
curl -X POST http://localhost:4000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Me fale sobre o PL 1234/2023",
    "audioEnabled": false
  }' | jq
```

### Teste 2: Chat com áudio
```bash
curl -X POST http://localhost:4000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quais os PLs sobre educação?",
    "audioEnabled": true
  }' | jq
```

### Teste 3: Via Orchestrator (fluxo completo)
```bash
curl -X POST http://localhost:3000/receive-message \
  -H "Content-Type: application/json" \
  -d '{
    "from": "5511999999999",
    "body": "Qual o status do PL 2024/2023?",
    "type": "text"
  }' | jq
```

### Teste 4: MCP direto
```bash
# Buscar projetos recentes
curl -X POST http://localhost:8000/tools/buscar_projetos_recentes \
  -H "Content-Type: application/json" \
  -d '{"limite": 5}' | jq
```

### Teste 5: Audio Processing
```bash
# Text-to-Speech
curl -X POST http://localhost:5001/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Olá, este é um teste de síntese de voz."
  }' | jq
```

## 📊 Monitoramento

### Ver logs em tempo real

```bash
# Todos os serviços
docker-compose logs -f

# Apenas backend
docker-compose logs -f backend

# Backend + MCP + Audio
docker-compose logs -f backend api-mcp-projetos-lei api-audio-processing

# Orchestrator + WhatsApp
docker-compose logs -f orchestrator whatsapp-service
```

### Status dos containers

```bash
docker-compose ps
```

Esperado: todos com status `Up`.

### Uso de recursos

```bash
docker stats
```

## 🔧 Troubleshooting Rápido

### Backend não inicia

```bash
# Ver logs
docker-compose logs backend

# Problemas comuns:
# 1. ANTHROPIC_API_KEY não configurada
# 2. Porta 4000 já em uso
# 3. Dependências não instaladas

# Solução: rebuild
docker-compose build backend
docker-compose up -d backend
```

### MCP não responde

```bash
# Testar conexão
curl http://localhost:8000/health

# Se falhar, restart
docker-compose restart api-mcp-projetos-lei

# Ver logs
docker-compose logs api-mcp-projetos-lei
```

### Áudio não é gerado

```bash
# Verificar OPENAI_API_KEY
docker-compose logs api-audio-processing

# Testar sem áudio primeiro
curl -X POST http://localhost:4000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "teste", "audioEnabled": false}'
```

### Limpar e reiniciar tudo

```bash
# Parar tudo
docker-compose down

# Remover volumes (CUIDADO: apaga dados)
docker-compose down -v

# Rebuild completo
docker-compose build --no-cache

# Iniciar
docker-compose up -d
```

## 🧰 Comandos Úteis

### Entrar em um container

```bash
# Backend
docker exec -it backend sh

# Orchestrator
docker exec -it orchestrator sh

# MongoDB
docker exec -it mongodb mongosh
```

### Ver variáveis de ambiente de um container

```bash
docker exec backend env | grep -E "(ANTHROPIC|MCP|AUDIO)"
```

### Restart de um serviço específico

```bash
docker-compose restart backend
```

### Rebuild de um serviço específico

```bash
docker-compose build backend
docker-compose up -d backend
```

### Ver rede Docker

```bash
docker network inspect dev-politica-bot_dev-politica-network
```

## 📝 Desenvolvimento Local (sem Docker)

Se preferir rodar o backend localmente:

```bash
cd backend

# Instalar deps
npm install

# Configurar .env
cp ../.env.global .env

# Rodar em dev mode
npm run dev

# Build
npm run build

# Rodar produção
npm start
```

**Nota:** Você ainda precisará dos outros serviços rodando (MCP, Audio, etc).

## 🎯 Próximos Passos

Após verificar que tudo está funcionando:

1. **Frontend Integration**: Integre o backend com seu frontend
2. **WhatsApp Testing**: Teste o fluxo completo via WhatsApp
3. **Custom Prompts**: Ajuste prompts no RAG service
4. **Add More MCPs**: Adicione novos MCPs (usuários, legislação, etc)
5. **Monitoring**: Configure Prometheus/Grafana
6. **Production**: Deploy em cloud provider

## 📚 Documentação Adicional

- [README Principal](./README.md)
- [Arquitetura Completa](./ARCHITECTURE.md)
- [Backend README](./backend/README.md)
- [Backend Integration Guide](./backend/INTEGRATION.md)
- [MCP Projetos Lei](./api-mcp-projetos-lei/README.md)
- [Audio Processing](./api-audio-processing/README.md)
- [Orchestrator](./orchestrator/README.md)

## 🆘 Suporte

Problemas? Verifique:
1. Logs dos containers
2. Health checks
3. Variáveis de ambiente
4. Conectividade de rede Docker
5. API keys válidas

Ainda com problemas? Abra uma issue no repositório!

---

✅ **Tudo funcionando?** Parabéns! O ZapCidadão está pronto para uso! 🎉
