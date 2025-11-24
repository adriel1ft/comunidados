# Dockerfile para orchestrator
FROM dev-politica-bot-base:latest

WORKDIR /app

# Copia arquivos do projeto
COPY . /app

# Instala dependências
RUN uv venv && \
    uv pip install -e .

# Porta padrão (orchestrator usa 3000)
EXPOSE 3000

# Entrypoint
CMD [".venv/bin/orchestrator"]
