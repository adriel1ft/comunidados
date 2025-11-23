"""
Rotas da API de Agentes
"""
import logging
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from .models import AgentRequest, AgentResponse, HealthResponse
from .services import agent_service
from .config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check da API
    """
    return HealthResponse(
        status="healthy",
        service="api-agents",
        timestamp=datetime.now(),
        mcp_servers={
            "projetos_lei": settings.mcp_projetos_lei_url,
        },
    )


@router.post(
    "/process-message",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    tags=["Agent"],
    summary="Processar mensagem com agente"
)
async def process_message(request: AgentRequest):
    """
    Processa uma mensagem do usuário através de um agente Agno
    
    O agente irá:
    1. Conectar-se aos servidores MCP disponíveis
    2. Buscar informações relevantes (projetos de lei, notícias, etc)
    3. Gerar uma resposta textual clara e acessível
    4. Determinar se a resposta deve ser em áudio
    5. Retornar a resposta com metadados
    
    **Exemplos de uso:**
    
    - Texto simples:
    ```json
    {
        "user_message": "Quais são os projetos sobre educação?",
        "user_id": "5585988123456@c.us",
        "session_id": "sess_123",
        "message_type": "text"
    }
    ```
    
    - Com preferências:
    ```json
    {
        "user_message": "Fale sobre inteligência artificial",
        "user_id": "5585988123456@c.us",
        "session_id": "sess_123",
        "message_type": "audio",
        "user_preferences": {
            "prefer_audio": true,
            "topics": ["educação", "tecnologia"]
        }
    }
    ```
    """
    try:
        logger.info(f"📨 Recebida requisição de {request.user_id}")
        response = await agent_service.process_message(request)
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", tags=["Info"])
async def root():
    """Informações da API"""
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "process_message": "/process-message",
        },
    }