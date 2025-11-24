# Dockerfile para api-mcp-projetos-lei
FROM dev-politica-bot-base:latest

WORKDIR /app

# Copia arquivos do projeto
COPY . /app

# Instala dependências
RUN uv venv && \
    uv pip install -e .

# Porta padrão
EXPOSE 8000

# Entrypoint
CMD [".venv/bin/api-mcp-projetos-lei"]
