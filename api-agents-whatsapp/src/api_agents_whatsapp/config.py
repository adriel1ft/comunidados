"""
Configurações da API de Agentes
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # API
    api_title: str = "API Agentes WhatsApp"
    api_version: str = "0.1.0"
    api_port: int = 5000
    api_host: str = "0.0.0.0"
    debug: bool = False
    
    # OpenAI
    openai_api_key: str = ""
    agent_model: str = "gpt-4o-mini"
    agent_temperature: float = 0.7
    
    # MCP Servers
    mcp_projetos_lei_url: str = "http://localhost:8000/mcp"
    mcp_users_url: str = "http://localhost:8001/mcp"
    # mcp_audio_url: str = "http://localhost:8001/mcp"


settings = Settings()