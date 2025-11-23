"""
Serviço de agentes para processar mensagens
"""
import logging
import os
from typing import Optional
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from agno.tools.mcp import MultiMCPTools
from .config import settings
from .models import AgentRequest, AgentResponse
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentService:
    """Gerenciador de agentes Agno com suporte a múltiplos MCPs"""
    
    def __init__(self):
        self.agent = None
        self.mcp_context = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Inicializa o agente com modelo OpenAI e ferramentas MCP"""
        try:
            logger.info("🚀 Inicializando Agente Agno...")
            
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
    
    async def _setup_mcp_tools(self) -> Optional[MCPTools]:
        """
        Configura conexão com servidor MCP de Projetos de Lei
        
        Returns:
            MCPTools conectado ou None se falhar
        """
        mcp_tools_list = []

        try:
            logger.info(f"🔌 Conectando ao MCP: {settings.mcp_projetos_lei_url}")
            
            mcp_projetos_lei = MCPTools(
                transport="streamable-http",
                url=settings.mcp_projetos_lei_url
            )

            mcp_tools_list.append(mcp_projetos_lei)
            logger.info(f"✅ MCP conectado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao MCP: {e}")
        
        try:
            logger.info(f"🔌 Conectando ao MCP Usuários: {settings.mcp_users_url}")
            mcp_users = MCPTools(
                transport="streamable-http",
                url=settings.mcp_users_url
            )
            mcp_tools_list.append(mcp_users)
            logger.info("✅ MCP Usuários conectado")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar MCP Usuários: {e}")

        if not mcp_tools_list:
            logger.warning("⚠️  Nenhum MCP disponível, agente funcionará sem ferramentas")
            return None
        
        return mcp_tools_list
    
    async def process_message(self, request: AgentRequest) -> AgentResponse:
        """
        Processa uma mensagem do usuário usando o agente Agno
        
        Args:
            request: Requisição do agente
            
        Returns:
            Resposta do agente com metadados
        """
        try:
            logger.info(f"🤖 Processando mensagem de {request.user_id}")
            logger.info(f"   Tipo: {request.message_type}")
            logger.info(f"   Conteúdo: {request.user_message[:100]}...")
            
            # Construir prompt baseado no tipo de mensagem
            prompt = self._build_prompt(request)
            
            # Configurar ferramentas MCP
            mcp_tools_list = await self._setup_mcp_tools()
            
            # Executar agente com context manager se MCP disponível
            if mcp_tools_list:
                agent_with_tools = Agent(
                    model=OpenAIChat(
                        id=settings.agent_model,
                        api_key=settings.openai_api_key,
                    ),
                    tools=[tool for tool in mcp_tools_list],
                    markdown=True
                )
                logger.info("📤 Enviando prompt para agente...")
                response_output = await agent_with_tools.arun(input=prompt)
            else:
                # Fallback: usar agente sem tools
                logger.warning("⚠️  Usando agente sem ferramentas MCP")
                response_output = await self.agent.arun(input=prompt)
            
            # Extrair texto da resposta
            response_text = self._extract_response_text(response_output)
            
            logger.info(f"✅ Resposta recebida: {response_text[:80]}...")
            
            # Determinar se deve enviar áudio
            should_send_audio = self._should_send_audio(request, response_output)
            
            # Criar resposta
            response = AgentResponse(
                session_id=request.session_id,
                user_id=request.user_id,
                response_text=response_text,
                auxiliary_text=self._get_auxiliary_text(should_send_audio),
                should_send_audio=should_send_audio,
                timestamp=datetime.now(),
            )
            
            logger.info(
                f"✅ Resposta gerada para {request.user_id} "
                f"(áudio: {should_send_audio})"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")
            logger.exception("Traceback completo:")
            raise
    
    def _extract_response_text(self, response_output) -> str:
        """
        Extrai o texto da resposta do agente
        
        Args:
            response_output: Output do agente (pode ter vários formatos)
            
        Returns:
            Texto extraído
        """
        # Tentar diferentes atributos comuns
        if hasattr(response_output, 'content'):
            text = response_output.content
        elif hasattr(response_output, 'message'):
            text = response_output.message
        elif hasattr(response_output, 'text'):
            text = response_output.text
        elif isinstance(response_output, dict):
            text = response_output.get('content') or response_output.get('message') or str(response_output)
        elif isinstance(response_output, str):
            text = response_output
        else:
            text = str(response_output)
        
        # Garantir que não retorna None
        return text.strip() if text else "Desculpe, não consegui processar sua mensagem no momento."
    
    def _build_prompt(self, request: AgentRequest) -> str:
        """
        Constrói o prompt para o agente baseado na requisição
        
        Args:
            request: Requisição do agente
            
        Returns:
            Prompt formatado para o agente
        """
        base_prompt = f"""Você é um assistente especializado em legislação brasileira e projetos de lei do Congresso Nacional.

📋 CONTEXTO DA MENSAGEM:
- Tipo: {request.message_type}
- Usuário: {request.user_id}
- Session: {request.session_id}

💬 MENSAGEM DO USUÁRIO:
{request.user_message}

📋 INSTRUÇÕES PARA RESPOSTA:
1. Use as ferramentas MCP disponíveis para buscar informações atualizadas sobre projetos de lei
2. Responda de forma clara, objetiva e acessível (evite jargão técnico excessivo)
3. Estruture a resposta com:
   - Resposta direta à pergunta
   - Contexto e background relevante
   - Links úteis quando apropriado (e-Cidadania, Câmara dos Deputados)
4. Se encontrar múltiplos projetos relevantes, resuma os 3 principais
5. Cite as fontes de informação
6. Mantenha tom profissional mas amigável
7. Se a pergunta não está relacionada a legislação, redirecione gentilmente

⚙️ INFORMAÇÕES DO USUÁRIO:"""
        
        # Adicionar preferências do usuário se disponíveis
        if request.user_preferences:
            if request.user_preferences.get("topics"):
                topics = ", ".join(request.user_preferences["topics"])
                base_prompt += f"\n- Tópicos de interesse: {topics}"
            
            if request.user_preferences.get("prefer_audio"):
                base_prompt += "\n- Preferência: Respostas em áudio (responda concisamente)"
        
        base_prompt += "\n\nAGORA, responda à mensagem do usuário:"
        
        return base_prompt
    
    def _get_auxiliary_text(self, should_send_audio: bool) -> Optional[str]:
        """
        Retorna texto auxiliar para TTS se necessário
        
        Args:
            should_send_audio: Se deve enviar áudio
            
        Returns:
            Texto auxiliar ou None
        """
        if not should_send_audio:
            return None
        
        return (
            "📢 Esta resposta foi gerada pelo assistente de IA do DevsImpacto. "
            "Para mais informações, visite e-Cidadania.camara.leg.br"
        )
    
    def _should_send_audio(self, request: AgentRequest, response_output) -> bool:
        """
        Determina se a resposta deve ser enviada em áudio
        
        Args:
            request: Requisição do agente
            
        Returns:
            True se deve enviar áudio
        """
        if "should_send_audio" in dir(response_output):
            if response_output.should_send_audio:
                return True
        
        if "content" in dir(response_output):
            if "should_send_audio" in response_output.content.lower():
                return True

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