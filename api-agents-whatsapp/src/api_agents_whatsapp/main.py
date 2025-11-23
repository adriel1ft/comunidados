"""
API de Agentes para gerar mensagens do WhatsApp
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="API de Agentes Agno para gerar respostas a mensagens do WhatsApp",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(router)


def main():
    """Ponto de entrada"""
    import uvicorn
    
    logger.info(
        f"🚀 Iniciando {settings.api_title} v{settings.api_version} "
        f"na porta {settings.api_port}"
    )
    
    uvicorn.run(
        "api_agents_whatsapp.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()