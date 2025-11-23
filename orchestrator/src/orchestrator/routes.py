import logging
from fastapi import APIRouter, HTTPException
from datetime import datetime

from .models import IncomingMessageRequest
from .services.message_service import MessageService

logger = logging.getLogger(__name__)
router = APIRouter()

message_service = MessageService()


@router.get("/health")
async def health_check():
    """Verifica saúde da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "Orquestrador de Mensagens"
    }


@router.post("/process-message")
async def receive_message(request: IncomingMessageRequest):
    """
    Recebe mensagem e adiciona ao buffer
    
    NÃO processa imediatamente!
    Aguarda timeout ou mais mensagens.
    """
    logger.info(f"📨 POST /process-message de {request.user_id}")
    
    result = await message_service.receive_message(
        user_id=request.user_id,
        chatId=request.chatId,
        message_type=request.message_type,
        message=request.message
    )
    
    return result


@router.get("/buffer-status/{user_id}")
async def get_buffer_status(user_id: str):
    """Obtém status do buffer de um usuário"""
    return message_service.buffer_service.get_buffer_status(user_id)


@router.post("/process-now/{user_id}")
async def process_buffer_now(user_id: str):
    """
    Força processamento do buffer imediatamente
    (útil para testes)
    """
    buffer = message_service.buffer_service.get_or_create_buffer(user_id)
    
    if not buffer.messages:
        raise HTTPException(status_code=400, detail="Buffer vazio")
    
    messages = buffer.get_messages()
    await message_service._process_buffered_messages(user_id, messages)
    
    return {
        "status": "processed",
        "messages_count": len(messages),
        "user_id": user_id
    }


@router.post("/update-user-profile")
async def update_user_profile(user_id: str, name: str = None, age: int = None, location: str = None):
    """Atualiza perfil do usuário"""
    user_service = message_service.user_service
    await user_service.update_user_profile(
        user_id=user_id,
        name=name,
        age=age,
        location=location
    )
    return {"status": "updated"}


@router.get("/user/{user_id}")
async def get_user_profile(user_id: str):
    """Obtém perfil do usuário"""
    user_service = message_service.user_service
    user = await user_service.get_or_create_user(user_id)
    return user.to_dict()