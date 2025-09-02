from typing import List
from uuid import UUID
import json

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, UploadFile, File
from sqlalchemy.orm import Session

# Core
from ...database import get_db
from ...core.security import get_current_user, get_user_from_token

# CRUD
from ...crud import chat as crud_chat

# Models & Schemas
from ...models.user import User, UserRole, Student
from ...models.group import StudentGroup
from ...schemas.chat import (
    WebSocketMessage, GroupChat, GroupChatCreate, GroupChatWithMessages,
    Message, MessageCreate, ChatFile, ChatFileCreate
)

# Services
from ...services.file_service import FileService
# Utils
from ...utils.websocket_utils import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


# ---------------------------
# Dependencias y utilidades
# ---------------------------
async def validate_chat_access(group_chat_id: UUID, current_user: User, db: Session) -> GroupChat:
    chat = crud_chat.group_chat.get(db=db, id=group_chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")
        membership = db.query(StudentGroup).filter(
            StudentGroup.student_id == student.id,
            StudentGroup.group_id == chat.group_id
        ).first()
        if not membership:
            raise HTTPException(status_code=403, detail="Access denied to this chat")
    return chat


async def enrich_messages(messages: List[Message]) -> List[Message]:
    return [
        Message(
            **msg.__dict__,
            sender_name=f"{msg.sender.first_names} {msg.sender.last_names}" if msg.sender else None,
            sender_role=msg.sender.role.value if msg.sender else None
        ) for msg in reversed(messages)
    ]


async def enrich_files(files: List[ChatFile]) -> List[ChatFile]:
    return [
        ChatFile(
            **file.__dict__,
            uploader_name=f"{file.user.first_names} {file.user.last_names}" if file.user else None
        ) for file in files
    ]


# ---------------------------
# WebSocket Endpoint
# ---------------------------
@router.websocket("/ws/{group_chat_id}")
async def websocket_endpoint(websocket: WebSocket, group_chat_id: UUID, token: str, db: Session = Depends(get_db)):
    current_user = await get_user_from_token(token, db)
    if not current_user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    _ = await validate_chat_access(group_chat_id, current_user, db)
    await websocket.accept()
    await manager.connect(websocket, group_chat_id, str(current_user.id))

    # Notify join
    join_msg = WebSocketMessage(
        type="user_joined",
        data={"user_id": str(current_user.id), "user_name": f"{current_user.first_names} {current_user.last_names}"},
        sender_id=current_user.id,
        group_chat_id=group_chat_id
    )
    await manager.broadcast_to_group(group_chat_id, join_msg.dict())

    try:
        while True:
            data = json.loads(await websocket.receive_text())

            if data.get("type") == "message":
                message_create = MessageCreate(
                    group_chat_id=group_chat_id,
                    message_type=data.get("message_type", "text"),
                    content=data.get("content")
                )
                new_message = crud_chat.message.create_with_sender(db=db, obj_in=message_create, sender_id=current_user.id)

                ws_message = WebSocketMessage(
                    type="new_message",
                    data={
                        "id": str(new_message.id),
                        "content": new_message.content,
                        "message_type": new_message.message_type.value,
                        "sender_id": str(current_user.id),
                        "sender_name": f"{current_user.first_names} {current_user.last_names}"
                    },
                    sender_id=current_user.id,
                    group_chat_id=group_chat_id
                )
                await manager.broadcast_to_group(group_chat_id, ws_message.dict())

            elif data.get("type") == "typing":
                typing_msg = WebSocketMessage(
                    type="user_typing",
                    data={
                        "user_id": str(current_user.id),
                        "user_name": f"{current_user.first_names} {current_user.last_names}",
                        "is_typing": data.get("is_typing", True)
                    },
                    sender_id=current_user.id,
                    group_chat_id=group_chat_id
                )
                await manager.broadcast_to_group(group_chat_id, typing_msg.dict(), exclude_user=str(current_user.id))

    except WebSocketDisconnect:
        manager.disconnect(group_chat_id, str(current_user.id))
        leave_msg = WebSocketMessage(
            type="user_left",
            data={"user_id": str(current_user.id), "user_name": f"{current_user.first_names} {current_user.last_names}"},
            sender_id=current_user.id,
            group_chat_id=group_chat_id
        )
        await manager.broadcast_to_group(group_chat_id, leave_msg.dict())

    except Exception:
        manager.disconnect(group_chat_id, str(current_user.id))
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


# ---------------------------
# REST Endpoints
# ---------------------------
@router.post("/", response_model=GroupChat, status_code=status.HTTP_201_CREATED)
async def create_group_chat(chat_in: GroupChatCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")
        membership = db.query(StudentGroup).filter(
            StudentGroup.student_id == student.id,
            StudentGroup.group_id == chat_in.group_id
        ).first()
        if not membership:
            raise HTTPException(status_code=403, detail="Access denied to this group")
    return crud_chat.group_chat.create(db=db, obj_in=chat_in)


@router.get("/", response_model=List[GroupChat])
async def get_user_chats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")
        return crud_chat.group_chat.get_user_chats(db=db, user_id=student.id)
    return crud_chat.group_chat.get_multi(db=db)


@router.get("/{group_chat_id}", response_model=GroupChatWithMessages)
async def get_chat_detail(group_chat_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat = await validate_chat_access(group_chat_id, current_user, db)
    messages = await enrich_messages(crud_chat.message.get_by_chat(db=db, group_chat_id=group_chat_id, limit=50))
    files = await enrich_files(crud_chat.chat_file.get_by_chat(db=db, group_chat_id=group_chat_id, limit=20))
    online_users = manager.get_connected_users(group_chat_id)

    return GroupChatWithMessages(
        **chat.__dict__,
        messages=messages,
        files=files,
        online_users=online_users,
        total_messages=len(messages)
    )


@router.post("/{group_chat_id}/messages", response_model=Message)
async def send_message(group_chat_id: UUID, message_in: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    await validate_chat_access(group_chat_id, current_user, db)
    message_in.group_chat_id = group_chat_id
    new_message = crud_chat.message.create_with_sender(db=db, obj_in=message_in, sender_id=current_user.id)

    ws_message = WebSocketMessage(
        type="new_message",
        data={
            "id": str(new_message.id),
            "content": new_message.content,
            "message_type": new_message.message_type.value,
            "sender_id": str(current_user.id),
            "sender_name": f"{current_user.first_names} {current_user.last_names}",
            "created_at": new_message.created_at.isoformat()
        },
        sender_id=current_user.id,
        group_chat_id=group_chat_id
    )
    await manager.broadcast_to_group(group_chat_id, ws_message.dict())
    return Message(**new_message.__dict__, sender_name=f"{current_user.first_names} {current_user.last_names}", sender_role=current_user.role.value)


@router.post("/{group_chat_id}/files", response_model=ChatFile)
async def upload_chat_file(group_chat_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat = await validate_chat_access(group_chat_id, current_user, db)
    if not chat.allows_files:
        raise HTTPException(status_code=400, detail="File uploads not allowed in this chat")

    current_usage = crud_chat.chat_file.get_chat_storage_usage(db=db, group_chat_id=group_chat_id)
    if current_usage >= chat.storage_capacity:
        raise HTTPException(status_code=400, detail="Chat storage capacity exceeded")

    file_url = await FileService.upload_chat_file(file, current_user.id, group_chat_id)
    chat_file_create = ChatFileCreate(group_chat_id=group_chat_id, file_name=file.filename, file_url=file_url, file_type=file.content_type)
    new_file = crud_chat.chat_file.create_with_user(db=db, obj_in=chat_file_create, user_id=current_user.id)

    # Broadcast archivo
    file_message = MessageCreate(group_chat_id=group_chat_id, message_type="file", content=f"📎 {file.filename}")
    file_msg = crud_chat.message.create_with_sender(db=db, obj_in=file_message, sender_id=current_user.id)
    ws_message = WebSocketMessage(
        type="file_shared",
        data={
            "file_id": str(new_file.id),
            "file_name": new_file.file_name,
            "file_url": new_file.file_url,
            "file_type": new_file.file_type,
            "sender_id": str(current_user.id),
            "sender_name": f"{current_user.first_names} {current_user.last_names}",
            "message_id": str(file_msg.id)
        },
        sender_id=current_user.id,
        group_chat_id=group_chat_id
    )
    await manager.broadcast_to_group(group_chat_id, ws_message.dict())
    return ChatFile(**new_file.__dict__, uploader_name=f"{current_user.first_names} {current_user.last_names}")
