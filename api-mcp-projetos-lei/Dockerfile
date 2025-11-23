# Dockerfile para api-mcp-projetos-lei
FROM dev-politica-bot-base:latest

WORKDIR /app

# Copia arquivos do projeto
COPY . /app

# Instala dependências
RUN uv venv && \
    uv pip install -e . -p .venv/bin/python


# Porta padrão
EXPOSE 8000

# Entrypoint
CMD [".venv/bin/python", "-m", "src.api_mcp_projetos_lei.main"]
