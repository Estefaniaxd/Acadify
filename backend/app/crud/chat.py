from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, or_
from uuid import UUID
from datetime import datetime, timedelta

from .base import CRUDBase
from ..models.chat import GroupChat, Message, ChatFile, BotMessage, ChatBot, FAQBot
from ..models.user import User
from ..models.group import Group, StudentGroup
from ..schemas.chat import (
    GroupChatCreate, GroupChatUpdate,
    MessageCreate, MessageUpdate,
    ChatFileCreate,
    BotMessageCreate,
    ChatBotCreate, ChatBotUpdate,
    FAQBotCreate, FAQBotUpdate,
    ChatSearchFilters
)

# -----------------------------
# CRUD de Chats de Grupo
# -----------------------------
class CRUDGroupChat(CRUDBase[GroupChat, GroupChatCreate, GroupChatUpdate]):

    def get_by_group(self, db: Session, *, group_id: UUID) -> Optional[GroupChat]:
        return db.query(self.model).filter_by(group_id=group_id).first()
    
    def get_user_chats(self, db: Session, *, user_id: UUID) -> List[GroupChat]:
        return (
            db.query(self.model)
            .join(Group)
            .join(StudentGroup, Group.id == StudentGroup.group_id)
            .filter(StudentGroup.student_id == user_id)
            .options(joinedload(GroupChat.group))
            .all()
        )
    
    def get_recent_activity(self, db: Session, *, user_id: UUID, hours: int = 24) -> List[GroupChat]:
        since = datetime.utcnow() - timedelta(hours=hours)
        return (
            db.query(self.model)
            .join(Group)
            .join(StudentGroup, Group.id == StudentGroup.group_id)
            .join(Message)
            .filter(StudentGroup.student_id == user_id, Message.created_at >= since)
            .distinct()
            .options(joinedload(GroupChat.group))
            .all()
        )

# -----------------------------
# CRUD de Mensajes
# -----------------------------
class CRUDMessage(CRUDBase[Message, MessageCreate, MessageUpdate]):

    def get_by_chat(self, db: Session, *, group_chat_id: UUID, skip: int = 0, limit: int = 50) -> List[Message]:
        return (
            db.query(self.model)
            .filter_by(group_chat_id=group_chat_id)
            .options(joinedload(Message.sender))
            .order_by(desc(Message.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_recent(self, db: Session, *, group_chat_id: UUID, minutes: int = 30) -> List[Message]:
        since = datetime.utcnow() - timedelta(minutes=minutes)
        return (
            db.query(self.model)
            .filter_by(group_chat_id=group_chat_id)
            .filter(Message.created_at >= since)
            .options(joinedload(Message.sender))
            .order_by(Message.created_at)
            .all()
        )
    
    def create_with_sender(self, db: Session, *, obj_in: MessageCreate, sender_id: UUID) -> Message:
        db_obj = self.model(sender_id=sender_id, **obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def search(self, db: Session, *, filters: ChatSearchFilters, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Message]:
        query = (
            db.query(self.model)
            .join(GroupChat)
            .join(Group)
            .join(StudentGroup, Group.id == StudentGroup.group_id)
            .filter(StudentGroup.student_id == user_id)
        )
        if filters.query:
            query = query.filter(Message.content.ilike(f"%{filters.query}%"))
        if filters.message_type:
            query = query.filter(Message.message_type == filters.message_type)
        if filters.sender_id:
            query = query.filter(Message.sender_id == filters.sender_id)
        if filters.date_from:
            query = query.filter(Message.created_at >= filters.date_from)
        if filters.date_to:
            query = query.filter(Message.created_at <= filters.date_to)
        return query.options(joinedload(Message.sender)).order_by(desc(Message.created_at)).offset(skip).limit(limit).all()
    
    def count_user_messages(self, db: Session, *, user_id: UUID, days: int = 30) -> int:
        since = datetime.utcnow() - timedelta(days=days)
        return db.query(func.count(Message.id)).filter(Message.sender_id==user_id, Message.created_at>=since).scalar()

# -----------------------------
# CRUD de Archivos de Chat
# -----------------------------
class CRUDChatFile(CRUDBase[ChatFile, ChatFileCreate, dict]):

    def get_by_chat(self, db: Session, *, group_chat_id: UUID, skip: int = 0, limit: int = 50) -> List[ChatFile]:
        return (
            db.query(self.model)
            .filter_by(group_chat_id=group_chat_id)
            .options(joinedload(ChatFile.user))
            .order_by(desc(ChatFile.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def storage_usage(self, db: Session, *, group_chat_id: UUID) -> int:
        count = db.query(func.count(self.model.id)).filter_by(group_chat_id=group_chat_id).scalar()
        return count * 1048576  # 1MB promedio
    
    def create_with_user(self, db: Session, *, obj_in: ChatFileCreate, user_id: UUID) -> ChatFile:
        db_obj = self.model(user_id=user_id, **obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

# -----------------------------
# CRUD ChatBot y BotMessage
# -----------------------------
class CRUDChatBot(CRUDBase[ChatBot, ChatBotCreate, ChatBotUpdate]):
    def get_active(self, db: Session) -> List[ChatBot]:
        return db.query(self.model).filter_by(is_active=True).all()
    
    def get_default(self, db: Session) -> Optional[ChatBot]:
        return db.query(self.model).filter_by(is_active=True).order_by(ChatBot.created_at).first()

class CRUDBotMessage(CRUDBase[BotMessage, BotMessageCreate, dict]):
    def get_by_user(self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 50) -> List[BotMessage]:
        return (
            db.query(self.model)
            .filter_by(user_id=user_id)
            .options(joinedload(BotMessage.chatbot))
            .order_by(desc(BotMessage.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_context(self, db: Session, *, context: str, reference_id: Optional[UUID] = None) -> List[BotMessage]:
        query = db.query(self.model).filter_by(context=context)
        if reference_id:
            query = query.filter(BotMessage.referenced_material_id == reference_id)
        return query.options(joinedload(BotMessage.user), joinedload(BotMessage.chatbot)).order_by(desc(BotMessage.created_at)).all()

# -----------------------------
# CRUD FAQ
# -----------------------------
class CRUDFAQBot(CRUDBase[FAQBot, FAQBotCreate, FAQBotUpdate]):
    def get_by_category(self, db: Session, *, category: str) -> List[FAQBot]:
        return db.query(self.model).filter_by(category=category).all()
    
    def search(self, db: Session, *, query: str) -> List[FAQBot]:
        search_term = f"%{query.lower()}%"
        return db.query(self.model).filter(or_(func.lower(FAQBot.question).like(search_term),
                                               func.lower(FAQBot.answer).like(search_term))).all()
    
    def get_categories(self, db: Session) -> List[str]:
        return [row[0] for row in db.query(FAQBot.category).distinct().all()]

# -----------------------------
# Estadísticas y Analytics
# -----------------------------
class ChatAnalytics:
    
    @staticmethod
    def _since(days: int) -> datetime:
        return datetime.utcnow() - timedelta(days=days)
    
    @staticmethod
    def chat_stats(db: Session, group_chat_id: UUID, days: int = 30) -> Dict[str, Any]:
        since = ChatAnalytics._since(days)
        total_messages = db.query(func.count(Message.id)).filter_by(group_chat_id=group_chat_id).scalar()
        recent_messages = db.query(func.count(Message.id)).filter(Message.group_chat_id==group_chat_id, Message.created_at>=since).scalar()
        files_shared = db.query(func.count(ChatFile.id)).filter_by(group_chat_id=group_chat_id).scalar()
        most_active = db.query(Message.sender_id, func.count(Message.id).label('count'), User.first_names, User.last_names)\
                        .join(User, Message.sender_id==User.id)\
                        .filter(Message.group_chat_id==group_chat_id, Message.created_at>=since)\
                        .group_by(Message.sender_id, User.first_names, User.last_names)\
                        .order_by(desc('count')).first()
        return {
            'total_messages': total_messages,
            'recent_messages': recent_messages,
            'files_shared': files_shared,
            'most_active_user': f"{most_active.first_names} {most_active.last_names}" if most_active else None,
            'period_days': days
        }
    
    @staticmethod
    def user_activity(db: Session, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        since = ChatAnalytics._since(days)
        messages_sent = db.query(func.count(Message.id)).filter(Message.sender_id==user_id, Message.created_at>=since).scalar()
        files_shared = db.query(func.count(ChatFile.id)).filter(ChatFile.user_id==user_id, ChatFile.created_at>=since).scalar()
        active_chats = db.query(func.count(func.distinct(Message.group_chat_id))).filter(Message.sender_id==user_id, Message.created_at>=since).scalar()
        return {
            'messages_sent': messages_sent,
            'files_shared': files_shared,
            'active_chats': active_chats,
            'period_days': days
        }

# -----------------------------
# Instancias de CRUD
# -----------------------------
group_chat = CRUDGroupChat(GroupChat)
message = CRUDMessage(Message)
chat_file = CRUDChatFile(ChatFile)
chat_bot = CRUDChatBot(ChatBot)
bot_message = CRUDBotMessage(BotMessage)
faq_bot = CRUDFAQBot(FAQBot)
