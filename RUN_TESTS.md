`test-agno-mcp.py`

```bash
cd api-mcp-projetos-lei
source .venv/bin/activate
mcp-projetos-lei

# Executar teste
cd screening
python test-agno-mcp.py
```

`test-audio-processing-api.py`

```bash
# Inicializar o localstack (simular AWS S3)
localstack start -d

cd api-audio-processing
source .venv/bin/activate
api-audio-processing

# Executar teste
cd screening
python test-audio-processing-api.py
```

`test-whatsapp-service.py`

```bash
# Instalar as dependências do projeto
cd whatsapp-service
npm install
# Autenticar via QR Code, caso não tenha
npm start

# Executar teste
cd screening
python test-whatsapp-service.py
```

`test-agents-api.py`

```bash
# Terminal 1 - MCP de Projetos de Lei
cd api-mcp-projetos-lei
source .venv/bin/activate
mcp-projetos-lei

# Terminal 2 - API de Agentes
cd api-agents-whatsapp
source .venv/bin/activate
api-agents

# Terminal 3 - Executar Teste
cd screening
python test-agents-api.py
```
