# backend/app/schemas/chat.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.chat import ChatStatus, MessageType, MessageContext

# ================================
# Esquemas para GroupChat
# ================================
class GroupChatBase(BaseModel):
    description: Optional[str] = None
    profile_image: Optional[str] = None
    allows_files: bool = True
    storage_capacity: int = Field(default=50 * 1024 * 1024, ge=0)  # 50MB
    chat_status: ChatStatus = ChatStatus.active

class GroupChatCreate(GroupChatBase):
    group_id: UUID

class GroupChatUpdate(BaseModel):
    description: Optional[str] = None
    profile_image: Optional[str] = None
    allows_files: Optional[bool] = None
    storage_capacity: Optional[int] = Field(None, ge=0)
    chat_status: Optional[ChatStatus] = None

class GroupChatInDB(GroupChatBase):
    id: UUID
    group_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class GroupChat(GroupChatInDB):
    pass

# ================================
# Esquemas para Message
# ================================
class MessageBase(BaseModel):
    message_type: MessageType
    content: str = Field(..., min_length=1)

class MessageCreate(MessageBase):
    group_chat_id: UUID

class MessageUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)

class MessageInDB(MessageBase):
    id: UUID
    group_chat_id: UUID
    sender_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class Message(MessageInDB):
    sender_name: Optional[str] = None
    sender_role: Optional[str] = None

# ================================
# Esquemas para ChatFile
# ================================
class ChatFileBase(BaseModel):
    file_name: str = Field(..., min_length=1)
    file_url: str = Field(..., min_length=1)
    file_type: Optional[str] = None

class ChatFileCreate(ChatFileBase):
    group_chat_id: UUID

class ChatFileInDB(ChatFileBase):
    id: UUID
    group_chat_id: UUID
    user_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ChatFile(ChatFileInDB):
    uploader_name: Optional[str] = None

# ================================
# Esquemas para BotMessage
# ================================
class BotMessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    response: str = Field(..., min_length=1)
    context: MessageContext

class BotMessageCreate(BotMessageBase):
    user_id: UUID
    group_chat_id: Optional[UUID] = None
    chatbot_id: UUID
    referenced_material_id: Optional[UUID] = None

class BotMessageInDB(BotMessageBase):
    id: UUID
    user_id: UUID
    group_chat_id: Optional[UUID]
    chatbot_id: UUID
    referenced_material_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class BotMessage(BotMessageInDB):
    user_name: Optional[str] = None
    chatbot_name: Optional[str] = None

# ================================
# Esquemas para ChatBot
# ================================
class ChatBotBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    profile_image_url: str = Field(..., min_length=1)
    is_active: bool = True

class ChatBotCreate(ChatBotBase):
    pass

class ChatBotUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    profile_image_url: Optional[str] = Field(None, min_length=1)
    is_active: Optional[bool] = None

class ChatBotInDB(ChatBotBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ChatBot(ChatBotInDB):
    pass

# ================================
# Esquemas para WebSocket
# ================================
class WebSocketMessage(BaseModel):
    type: str  # "message", "notification", etc.
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender_id: Optional[UUID] = None
    group_chat_id: Optional[UUID] = None

class WebSocketNotification(BaseModel):
    type: str  # "new_assignment", "grade_received", etc.
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    priority: str = Field(default="normal")  # "low", "normal", "high", "urgent"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: UUID

class ChatConnection(BaseModel):
    user_id: UUID
    group_chat_id: UUID
    connection_time: datetime = Field(default_factory=datetime.utcnow)

# ================================
# Esquemas para respuestas complejas
# ================================
class GroupChatWithMessages(GroupChat):
    messages: List[Message] = []
    files: List[ChatFile] = []
    online_users: List[UUID] = []
    total_messages: int = 0

class MessageWithReactions(Message):
    reactions: Dict[str, List[UUID]] = {}  # emoji -> list of user_ids
    reply_to: Optional[UUID] = None

class ChatStats(BaseModel):
    total_messages: int
    messages_today: int
    files_shared: int
    active_users: int
    most_active_user: Optional[str] = None

# ================================
# Esquemas para notificaciones
# ================================
class NotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1)
    notification_type: str
    is_read: bool = False
    priority: str = Field(default="normal")
    data: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: UUID

class NotificationInDB(NotificationBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True

class Notification(NotificationInDB):
    pass

# ================================
# Esquemas para FAQ Bot
# ================================
class FAQBotBase(BaseModel):
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1, max_length=50)

class FAQBotCreate(FAQBotBase):
    pass

class FAQBotUpdate(BaseModel):
    question: Optional[str] = Field(None, min_length=1)
    answer: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, min_length=1, max_length=50)

class FAQBotInDB(FAQBotBase):
    id: UUID
    created_at: datetime
    last_updated: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class FAQBot(FAQBotInDB):
    pass

# ================================
# Esquemas para búsqueda y filtros
# ================================
class ChatSearchFilters(BaseModel):
    query: Optional[str] = None
    message_type: Optional[MessageType] = None
    sender_id: Optional[UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    has_files: Optional[bool] = None

class MessageSearchResult(BaseModel):
    message: Message
    chat_name: str
    context_messages: List[Message] = []
