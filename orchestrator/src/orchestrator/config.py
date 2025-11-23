from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # API
    api_title: str = "API Orquestrador"
    api_version: str = "0.1.0"
    api_port: int = 3000
    api_host: str = "0.0.0.0"
    debug: bool = False
    
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db: str = "devsimpacto"
    
    # Serviços Externos
    whatsapp_service_url: str = "http://localhost:5002"
    audio_api_url: str = "http://localhost:5001"
    agent_api_url: str = "http://localhost:5000"
    mcp_users_url: str = "http://localhost:8000/mcp"
    
    # Message Batching
    message_batch_timeout_seconds: int = 5  # Timeout total
    message_inter_timeout_seconds: int = 5  # Timeout entre mensagens


settings = Settings()