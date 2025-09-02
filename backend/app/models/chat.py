# backend/app/models/chat.py
from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Text, Boolean, Enum, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel as Base
from datetime import datetime
import enum
import uuid


# ================================
# ENUMS
# ================================
class ChatStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class MessageType(str, enum.Enum):
    text = "text"
    file = "file"
    image = "image"
    video = "video"

class MessageContext(str, enum.Enum):
    general = "general"
    assignment = "assignment"
    notification = "notification"

# ================================
# MODELOS
# ================================

class GroupChat(Base):
    __tablename__ = "group_chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    description = Column(Text, nullable=True)
    profile_image = Column(String, nullable=True)
    allows_files = Column(Boolean, default=True)
    storage_capacity = Column(Integer, default=50*1024*1024)  # 50MB
    status = Column(Enum(ChatStatus), default=ChatStatus.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    group = relationship("Group", back_populates="chat")
    messages = relationship("Message", back_populates="group_chat", cascade="all, delete-orphan")
    files = relationship("ChatFile", back_populates="group_chat", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_chat_id = Column(UUID(as_uuid=True), ForeignKey("group_chats.id"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    message_type = Column(Enum(MessageType), nullable=False)
    content = Column(Text, nullable=False)
    context = Column(Enum(MessageContext), default=MessageContext.general)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    group_chat = relationship("GroupChat", back_populates="messages")
    sender = relationship("User", back_populates="messages_sent")

class ChatFile(Base):
    __tablename__ = "chat_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_chat_id = Column(UUID(as_uuid=True), ForeignKey("group_chats.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    group_chat = relationship("GroupChat", back_populates="files")
    user = relationship("User", back_populates="chat_files")

class ChatBot(Base):
    __tablename__ = "chat_bots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    profile_image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bot_messages = relationship("BotMessage", back_populates="chatbot", cascade="all, delete-orphan")

class BotMessage(Base):
    __tablename__ = "bot_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chatbot_id = Column(UUID(as_uuid=True), ForeignKey("chat_bots.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    group_chat_id = Column(UUID(as_uuid=True), ForeignKey("group_chats.id"), nullable=True)
    content = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    context = Column(Enum(MessageContext), default=MessageContext.general)
    referenced_material_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chatbot = relationship("ChatBot", back_populates="bot_messages")
    user = relationship("User", back_populates="bot_messages")
    group_chat = relationship("GroupChat")

class FAQBot(Base):
    __tablename__ = "faq_bots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
