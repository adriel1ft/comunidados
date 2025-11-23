import logging
import httpx
import base64
import tempfile
from typing import Optional
from fastapi import File

from ..config import settings

logger = logging.getLogger(__name__)


class AudioService:
    """Integração com API de Áudio (API 2)"""
    
    async def transcribe_audio(self, audio_base64: str) -> Optional[str]:
        """
        Transcreve áudio recebido via WhatsApp para texto
        
        Fluxo:
        1. Recebe áudio em base64
        2. Salva como arquivo temporário
        3. Envia para API 2 (speech-to-text)
        4. Retorna texto transcrito
        """
        try:
            logger.info("🎵 Iniciando transcrição de áudio...")
            
            # Salvar arquivo temporário
            audio_data = base64.b64decode(audio_base64)
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            # Enviar para API 2
            async with httpx.AsyncClient() as client:
                with open(tmp_path, "rb") as audio_file:
                    files = {"file": audio_file}
                    response = await client.post(
                        f"{settings.audio_api_url}/speech-to-text",
                        files=files,
                        timeout=30.0
                    )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("text", "")
                logger.info(f"✅ Áudio transcrito: {text[:50]}...")
                return text
            else:
                logger.error(f"❌ Erro ao transcrever: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na transcrição: {e}")
            return None
    
    async def text_to_speech(self, text: str, auxiliary_text: Optional[str] = None) -> Optional[str]:
        """
        Converte texto em áudio
        
        Fluxo:
        1. Envia texto para API 2 (text-to-speech)
        2. Retorna URL do áudio gerado
        """
        try:
            logger.info("🔊 Gerando áudio a partir de texto...")
            
            payload = {
                "text": text,
                "auxiliary_text": auxiliary_text
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.audio_api_url}/text-to-speech",
                    json=payload,
                    timeout=30.0
                )
            
            if response.status_code == 200:
                result = response.json()
                audio_url = result.get("audio_url", "")
                logger.info(f"✅ Áudio gerado: {audio_url}")
                return audio_url
            else:
                logger.error(f"❌ Erro ao gerar áudio: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na síntese: {e}")
            return None