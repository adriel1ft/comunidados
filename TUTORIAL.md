# Tutorial: Como Executar o Projeto Devs de Impacto

### Visão Geral

Este tutorial guiará você na execução de todos os microsserviços que compõem a plataforma Devs de Impacto. A arquitetura consiste em vários serviços que se comunicam entre si. Seguiremos a ordem de inicialização das dependências e, em seguida, dos serviços principais.

### Pré-requisitos

Antes de começar, certifique-se de que você possui os seguintes softwares instalados em sua máquina:

- **Python 3.10+**
- **Node.js 18+** e **npm**
- **Docker**
- **[uv](https://github.com/astral-sh/uv)**: Um gerenciador de pacotes Python rápido. Instale com:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **[LocalStack](https://docs.localstack.cloud/aws/getting-started/installation/)**: Para simular serviços da AWS localmente.
- **Chave de API da OpenAI**: Necessária para os serviços de IA e áudio. Obtenha em [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
- **Um número de WhatsApp** para testes.

---

### Passo 1: Iniciar Dependências de Infraestrutura

Primeiro, vamos iniciar os serviços de base como o MongoDB e o LocalStack usando o Docker.

1.  **Iniciar LocalStack**:
    Este serviço simula o S3 da AWS para a `api-audio-processing`.

    ```bash
    localstack start -d
    ```

    Aguarde a mensagem `Ready.` nos logs para continuar.

2.  **Iniciar MongoDB**:
    Este banco de dados é usado pelo `orchestrator` para gerenciar usuários e sessões.
    ```bash
    docker run -d \
      --name mongodb \
      -p 27017:27017 \
      mongo:latest
    ```

---

### Passo 2: Configurar e Rodar os Serviços de Suporte

Agora, vamos iniciar as APIs que fornecem dados e funcionalidades específicas para os serviços principais.

#### A. API de Dados Legislativos (`api-mcp-projetos-lei`)

Esta API é uma dependência da `api-agents-whatsapp`.

1.  **Navegue até o diretório e configure o ambiente**:

    ```bash
    # A partir da raiz do projeto
    cd api-mcp-projetos-lei
    uv venv
    source .venv/bin/activate
    ```

2.  **Instale as dependências**:

    ```bash
    uv pip install -e .
    ```

3.  **Inicie o servidor (Terminal 1)**:
    ```bash
    mcp-projetos-lei
    ```
    > 🖥️ Este serviço estará rodando em `http://localhost:8000`. Mantenha este terminal aberto.

#### B. API de Processamento de Áudio (`api-audio-processing`)

1.  **Navegue até o diretório e configure o ambiente**:

    ```bash
    # A partir da raiz do projeto
    cd api-audio-processing
    uv venv
    source .venv/bin/activate
    ```

2.  **Instale as dependências**:

    ```bash
    uv pip install -e .
    ```

3.  **Configure as variáveis de ambiente**:
    Copie o arquivo de exemplo e adicione sua chave da OpenAI.

    ```bash
    cp .env.example .env
    ```

    Edite o arquivo `.env` e preencha a variável `OPENAI_API_KEY`.

4.  **Inicie o servidor (Terminal 2)**:
    O orquestrador espera que este serviço rode na porta `5001`.
    ```bash
    uvicorn api_audio_processing.main:app --host 0.0.0.0 --port 5001 --reload
    ```
    > 🖥️ Este serviço estará rodando em `http://localhost:5001`. Mantenha este terminal aberto.

---

### Passo 3: Configurar e Rodar os Serviços Principais

#### A. API de Agentes (`api-agents-whatsapp`)

1.  **Navegue até o diretório e configure o ambiente**:

    ```bash
    # A partir da raiz do projeto
    cd api-agents-whatsapp
    uv venv
    source .venv/bin/activate
    ```

2.  **Instale as dependências**:

    ```bash
    uv pip install -e .
    ```

3.  **Configure as variáveis de ambiente**:

    ```bash
    cp .env.example .env
    ```

    Edite o arquivo `.env` e adicione sua `OPENAI_API_KEY`.

4.  **Inicie o servidor (Terminal 3)**:
    ```bash
    api-agents
    ```
    > 🖥️ Este serviço estará rodando em `http://localhost:5000`. Mantenha este terminal aberto.

#### B. Orquestrador (`orchestrator`)

1.  **Navegue até o diretório e configure o ambiente**:

    ```bash
    # A partir da raiz do projeto
    cd orchestrator
    uv venv
    source .venv/bin/activate
    ```

2.  **Instale as dependências**:

    ```bash
    uv pip install -e .
    ```

3.  **Configure as variáveis de ambiente**:

    ```bash
    cp .env.example .env
    ```

    Verifique se as URLs no arquivo `.env` correspondem às portas dos serviços que você iniciou:

    - `AGENT_API_URL=http://localhost:5000`
    - `AUDIO_API_URL=http://localhost:5001`
    - `WHATSAPP_SERVICE_URL=http://localhost:5002`

4.  **Inicie o servidor (Terminal 4)**:
    ```bash
    orchestrator --reload
    ```
    > 🖥️ Este serviço estará rodando em `http://localhost:3000`. Mantenha este terminal aberto.

#### C. Serviço do WhatsApp (`whatsapp-service`)

1.  **Navegue até o diretório e instale as dependências**:

    ```bash
    # A partir da raiz do projeto
    cd whatsapp-service
    npm install
    ```

2.  **Configure as variáveis de ambiente**:

    ```bash
    cp .env.example .env
    ```

    Edite o arquivo `.env` e certifique-se de que a `ORCHESTRATOR_URL` aponta para o serviço correto:

    - `ORCHESTRATOR_URL=http://localhost:3000/receive-message`

3.  **Inicie o serviço e autentique (Terminal 5)**:
    ```bash
    npm start
    ```
    - Na primeira execução, um **QR Code** será exibido no terminal.
    - Abra o WhatsApp no seu celular, vá para **Aparelhos conectados** e escaneie o QR Code.
    - Aguarde a mensagem `[✅] WhatsApp conectado!`. A sessão será salva para futuras execuções.

---

### Resumo dos Terminais

Ao final, você terá 5 terminais executando cada um dos serviços:

- **Terminal 1**: `api-mcp-projetos-lei` (Porta 8000)
- **Terminal 2**: `api-audio-processing` (Porta 5001)
- **Terminal 3**: `api-agents-whatsapp` (Porta 5000)
- **Terminal 4**: `orchestrator` (Porta 3000)
- **Terminal 5**: `whatsapp-service` (Porta 5002 para webhook)

Com todos os serviços rodando, você pode enviar uma mensagem para o número de WhatsApp conectado e o fluxo completo do projeto será executado.
