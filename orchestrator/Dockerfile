# Dockerfile para orchestrator
FROM dev-politica-bot-base:latest

WORKDIR /app

# Copia arquivos do projeto
COPY . /app

# Instala dependências
RUN uv venv && \
    uv pip install -e . -p .venv/bin/python


# Porta padrão
EXPOSE 5000

# Entrypoint
CMD [".venv/bin/orchestrator"]
