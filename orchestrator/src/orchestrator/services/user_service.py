import logging
from datetime import datetime
from typing import Optional
from pymongo import MongoClient

from ..config import settings
from ..models_db import UserDB

logger = logging.getLogger(__name__)


class UserService:
    """Gerencia usuários e perfis"""
    
    def __init__(self):
        self.client = MongoClient(settings.mongodb_url)
        self.db = self.client[settings.mongodb_db]
        self.users_collection = self.db["users"]
    
    async def get_or_create_user(self, user_id: str) -> UserDB:
        """Obtém usuário existente ou cria novo"""
        user_doc = self.users_collection.find_one({"user_id": user_id})
        
        if user_doc:
            logger.info(f"✅ Usuário encontrado: {user_id}")
            # Converter documento para objeto (simplificado)
            return UserDB(
                user_id=user_doc["user_id"],
                name=user_doc.get("name"),
                age=user_doc.get("age"),
                location=user_doc.get("location"),
                prefer_audio=user_doc.get("prefer_audio", False)
            )
        
        logger.info(f"🆕 Novo usuário: {user_id}")
        new_user = UserDB(user_id=user_id)
        self.users_collection.insert_one(new_user.to_dict())
        return new_user
    
    async def update_user_profile(
        self, 
        user_id: str, 
        name: Optional[str] = None,
        age: Optional[int] = None,
        location: Optional[str] = None,
        topics: Optional[list] = None,
        prefer_audio: Optional[bool] = None
    ) -> UserDB:
        """Atualiza perfil do usuário"""
        update_data = {
            "updated_at": datetime.utcnow()
        }
        
        if name:
            update_data["name"] = name
        if age:
            update_data["age"] = age
        if location:
            update_data["location"] = location
        if topics:
            update_data["topics_of_interest"] = topics
        if prefer_audio is not None:
            update_data["prefer_audio"] = prefer_audio
        
        self.users_collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        logger.info(f"📝 Perfil atualizado: {user_id}")
        return await self.get_or_create_user(user_id)
    
    async def get_user_preference_audio(self, user_id: str) -> bool:
        """Obtém preferência de áudio do usuário"""
        user = await self.get_or_create_user(user_id)
        return user.prefer_audio