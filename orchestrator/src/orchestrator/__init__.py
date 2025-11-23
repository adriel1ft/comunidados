"""
Orquestrador de Mensagens WhatsApp

Módulo principal que integra:
- WhatsApp Service
- API de Áudio (Speech-to-Text, Text-to-Speech)
- API de Agentes (LLM + MCPs)
- Gerenciamento de Usuários e Sessões
"""

__version__ = "0.1.0"
__author__ = "DevsImpacto"
__description__ = "Orquestrador de mensagens WhatsApp com suporte a áudio e agentes IA"

# Exportar componentes principais
from .config import settings
from .services.message_service import MessageService
from .services.user_service import UserService
from .services.audio_service import AudioService
from .services.agent_service import AgentService

__all__ = [
    "settings",
    "MessageService",
    "UserService",
    "AudioService",
    "AgentService",
]