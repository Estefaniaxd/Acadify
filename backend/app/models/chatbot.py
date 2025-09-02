#app/models/chatbot.py
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.chat import MessageContext
from .base import BaseModel

class ChatBot(BaseModel):
    """Modelo de chatbot"""
    __tablename__ = "chatbots"
    
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    profile_image_url = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    bot_messages = relationship("BotMessage", back_populates="chatbot")

class FAQBot(BaseModel):
    """Modelo de preguntas frecuentes del bot"""
    __tablename__ = "faq_bot"
    
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    last_updated = Column(DateTime(timezone=True))

class BotMessage(BaseModel):
    """Modelo de mensaje del bot"""
    __tablename__ = "bot_messages"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    group_chat_id = Column(UUID(as_uuid=True), ForeignKey("group_chats.id"))
    chatbot_id = Column(UUID(as_uuid=True), ForeignKey("chatbots.id"), nullable=False)
    referenced_material_id = Column(UUID(as_uuid=True), ForeignKey("educational_materials.id"))
    content = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    context = Column(SQLEnum(MessageContext), nullable=False)
    
    # Relaciones
    user = relationship("User")
    group_chat = relationship("GroupChat", back_populates="bot_messages")
    chatbot = relationship("ChatBot", back_populates="bot_messages")
    referenced_material = relationship("EducationalMaterial", back_populates="bot_messages")