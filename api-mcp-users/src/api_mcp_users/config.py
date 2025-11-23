"""
Configurações do servidor MCP de Usuários
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API
    api_title: str = "MCP Usuários"
    api_version: str = "0.1.0"
    api_port: int = 8001
    api_host: str = "0.0.0.0"
    debug: bool = False

    # MCP Server
    mcp_server_name: str = "usuarios-mcp"
    mcp_server_version: str = "0.1.0"

    # MongoDB (mesmo banco do orquestrador)
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db: str = "devsimpacto"
    mongodb_users_collection: str = "users"

    # Serviços Externos
    orchestrator_url: str = "http://localhost:3000"

    # Cache
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hora

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# Instância global de configurações
settings = Settings()