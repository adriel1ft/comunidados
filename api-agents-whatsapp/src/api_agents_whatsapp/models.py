"""
Modelos de dados da API
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class AgentRequest(BaseModel):
    """Requisição para processamento por agente"""
    
    user_message: str = Field(..., description="Mensagem do usuário")
    user_id: str = Field(..., description="ID do usuário no WhatsApp")
    session_id: str = Field(..., description="ID da sessão de conversa")
    message_type: Literal["text", "audio"] = Field(
        default="text",
        description="Tipo da mensagem recebida"
    )
    user_preferences: Optional[dict] = Field(
        default=None,
        description="Preferências do usuário (áudio/texto, tópicos)"
    )


class AgentResponse(BaseModel):
    """Resposta do agente"""
    
    session_id: str
    user_id: str
    response_text: str
    auxiliary_text: Optional[str] = None
    should_send_audio: bool = False
    confidence: float = Field(ge=0, le=1)
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str
    service: str
    timestamp: datetime
    mcp_servers: dict