"""
API Orquestrador de Mensagens WhatsApp

Responsável por:
1. Receber mensagens do WhatsApp Service
2. Transcrever áudio (se necessário) via API 2
3. Processar com agentes via API 3
4. Decidir formato de resposta (texto/áudio)
5. Enviar resposta de volta ao WhatsApp
"""
import logging
import uvicorn
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
    description="Orquestrador de mensagens WhatsApp - Integra áudio, agentes e MCPs",
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


@app.on_event("startup")
async def startup():
    logger.info("🚀 Orquestrador iniciando...")
    logger.info(f"📡 WhatsApp Service: {settings.whatsapp_service_url}")
    logger.info(f"🎵 Audio API: {settings.audio_api_url}")
    logger.info(f"🤖 Agent API: {settings.agent_api_url}")


@app.on_event("shutdown")
async def shutdown():
    logger.info("🛑 Orquestrador encerrando...")


def main():
    """Ponto de entrada"""
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )


if __name__ == "__main__":
    main()