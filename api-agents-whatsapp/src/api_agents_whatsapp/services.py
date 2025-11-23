"""
Serviço de agentes para processar mensagens
"""
import logging
import os
from typing import Optional
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from .config import settings
from .models import AgentRequest, AgentResponse
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentService:
    """Gerenciador de agentes Agno com suporte a múltiplos MCPs"""
    
    def __init__(self):
        self.mcp_tools_cache = {}
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Inicializa o agente com modelo OpenAI"""
        try:
            self.agent = Agent(
                model=OpenAIChat(
                    id=settings.agent_model,
                    api_key=settings.openai_api_key,
                ),
                markdown=True,
            )
            logger.info("✅ Agente Agno inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar agente: {e}")
            raise
    
    async def _get_mcp_tools(self, mcp_url: str) -> Optional[MCPTools]:
        """
        Obtém e cacheia ferramentas MCP
        
        Args:
            mcp_url: URL do servidor MCP
            
        Returns:
            Instância de MCPTools ou None se falhar
        """
        if mcp_url in self.mcp_tools_cache:
            return self.mcp_tools_cache[mcp_url]
        
        try:
            logger.info(f"🔌 Conectando ao MCP: {mcp_url}")
            mcp_tools = MCPTools(
                transport="streamable-http",
                url=mcp_url
            )
            
            self.mcp_tools_cache[mcp_url] = mcp_tools
            logger.info(f"✅ Conectado ao MCP: {mcp_url}")
            return mcp_tools
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao MCP {mcp_url}: {e}")
            return None
    
    async def process_message(self, request: AgentRequest) -> AgentResponse:
        """
        Processa uma mensagem do usuário usando o agente
        
        Args:
            request: Requisição do agente
            
        Returns:
            Resposta do agente
        """
        try:
            logger.info(f"🤖 Processando mensagem de {request.user_id}")
            logger.info(f"   Tipo: {request.message_type}")
            logger.info(f"   Conteúdo: {request.user_message[:100]}...")
            
            # Conectar ao MCP de projetos de lei (principal)
            mcp_tools = await self._get_mcp_tools(
                settings.mcp_projetos_lei_url
            )
            
            tools = []
            if mcp_tools:
                tools = [mcp_tools]
            else:
                logger.warning("⚠️  MCP indisponível, usando agente sem tools")
            
            # Criar agente com tools dinâmicas
            async with MCPTools(
                transport="streamable-http",
                url=settings.mcp_projetos_lei_url
            ) as mcp_context:
                agent = Agent(
                    model=OpenAIChat(
                        id=settings.agent_model,
                        api_key=settings.openai_api_key,
                    ),
                    tools=[mcp_context] if tools else [],
                    markdown=True,
                )
                
                # Construir prompt baseado no tipo de mensagem
                prompt = self._build_prompt(request)
                
                # Executar agente
                response_output = await agent.arun(input=prompt)

                if hasattr(response_output, 'content'):
                    response_text = response_output.content
                elif hasattr(response_output, 'message'):
                    response_text = response_output.message
                else:
                    response_text = str(response_output)
            
            # Determinar se deve enviar áudio
            should_send_audio = self._should_send_audio(request)
            
            # Criar resposta
            response = AgentResponse(
                session_id=request.session_id,
                user_id=request.user_id,
                response_text=response_text,
                auxiliary_text=None if not should_send_audio else (
                    "📢 Esta resposta foi gerada pelo assistente de IA. "
                    "Para mais informações, acesse o e-Cidadania."
                ),
                should_send_audio=should_send_audio,
                confidence=0.85,
                timestamp=datetime.now(),
            )
            
            logger.info(
                f"✅ Resposta gerada para {request.user_id} "
                f"(áudio: {should_send_audio})"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")
            raise
    
    def _build_prompt(self, request: AgentRequest) -> str:
        """
        Constrói o prompt para o agente baseado na requisição
        
        Args:
            request: Requisição do agente
            
        Returns:
            Prompt formatado
        """
        base_prompt = f"""
Você é um assistente especializado em legislação brasileira e projetos de lei.
A mensagem é do tipo: {request.message_type}

Mensagem do usuário:
{request.user_message}

Instruções:
1. Busque informações relevantes usando as tools disponíveis (se houver)
2. Responda de forma clara, objetiva e acessível
3. Cite as fontes quando apropriado
4. Se relevante, mencione links úteis (e-Cidadania, Câmara dos Deputados)
5. Mantenha tom profissional mas amigável
"""
        
        if request.user_preferences:
            if request.user_preferences.get("topics"):
                base_prompt += (
                    f"\nTópicos de interesse do usuário: "
                    f"{', '.join(request.user_preferences['topics'])}\n"
                )
        
        return base_prompt
    
    def _should_send_audio(self, request: AgentRequest) -> bool:
        """
        Determina se a resposta deve ser enviada em áudio
        
        Args:
            request: Requisição do agente
            
        Returns:
            True se deve enviar áudio
        """
        # Lógica 1: Se a mensagem original foi áudio
        if request.message_type == "audio":
            return True
        
        # Lógica 2: Se o usuário tem preferência de áudio
        if request.user_preferences:
            if request.user_preferences.get("prefer_audio"):
                return True
        
        return False


# Instância global do serviço
agent_service = AgentService()