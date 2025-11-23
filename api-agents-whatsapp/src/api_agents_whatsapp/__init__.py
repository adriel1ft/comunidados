"""
API Agentes WhatsApp
"""

__version__ = "0.1.0"

from .main import app
from .services import agent_service

__all__ = ["app", "agent_service", "__version__"]