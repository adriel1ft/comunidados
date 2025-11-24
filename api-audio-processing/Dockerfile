# Dockerfile para api-audio-processing
FROM dev-politica-bot-base:latest

WORKDIR /app

# Copia arquivos do projeto
COPY . /app

# Instala dependências
RUN uv venv && \
    uv pip install -e .

# Porta padrão (5001 para não conflitar)
EXPOSE 5001

# Entrypoint
CMD [".venv/bin/api-audio-processing"]
