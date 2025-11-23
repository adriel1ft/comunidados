import logging
import httpx
from typing import Optional, Dict

from ..config import settings

logger = logging.getLogger(__name__)


class AgentService:
    """Integração com API de Agentes (API 3)"""
    
    async def process_message(
        self,
        user_message: str,
        user_id: str,
        session_id: str,
        user_preferences: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Processa mensagem do usuário através do agente
        
        Fluxo:
        1. Envia mensagem para API 3
        2. Agente processa com MCPs
        3. Retorna resposta textual e indicação de áudio
        """
        try:
            logger.info(f"🤖 Processando mensagem com agente: {user_message[:50]}...")
            
            payload = {
                "user_message": user_message,
                "user_id": user_id,
                "session_id": session_id,
                "message_type": "text",
                "user_preferences": user_preferences or {}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.agent_api_url}/process-message",
                    json=payload,
                    timeout=30.0
                )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Agente respondeu: {result.get('response_text', '')[:50]}...")
                return result
            else:
                logger.error(f"❌ Erro ao processar com agente: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na integração com agente: {e}")
            return None