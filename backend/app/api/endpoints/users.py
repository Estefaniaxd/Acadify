# backend/app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import csv
import io

from backend.app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.core.security import get_current_user
from app.utils.actions import sanitize_email, log_action

router = APIRouter(prefix="/users", tags=["Users"])

# -------------------------------
# Helpers internos
# -------------------------------
def get_user_or_404(db: Session, user_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id, User.is_active).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def check_owner_or_admin(current_user: User, target_user: User):
    if not (current_user.role == "administrator" or current_user.id == target_user.id):
        raise HTTPException(status_code=403, detail="Operation not permitted")

# -------------------------------
# Listar usuarios con filtros y paginación
# -------------------------------
@router.get("/", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = Query(None, description="Buscar por nombre o email"),
    is_active: Optional[bool] = True
):
    query = db.query(User).filter(User.is_active == is_active)
    if search:
        query = query.filter(
            (User.first_names.ilike(f"%{search}%")) |
            (User.last_names.ilike(f"%{search}%")) |
            (User.institutional_email.ilike(f"%{search}%"))
        )
    users = query.offset(skip).limit(limit).all()
    return users

# -------------------------------
# Obtener un usuario por ID
# -------------------------------
@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user_or_404(db, user_id)
    check_owner_or_admin(current_user, user)
    return user

# -------------------------------
# Crear un nuevo usuario
# -------------------------------
@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "administrator":
        raise HTTPException(status_code=403, detail="Only admins can create users")

    sanitized_email = sanitize_email(user_in.institutional_email)
    user_data = user_in.dict()
    user_data["institutional_email"] = sanitized_email
    user_data["id"] = uuid4()
    user_data["created_at"] = datetime.utcnow()
    
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    log_action(current_user.id, f"Created user {user.id}")
    return user

# -------------------------------
# Actualizar un usuario
# -------------------------------
@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: UUID, user_in: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user_or_404(db, user_id)
    check_owner_or_admin(current_user, user)

    for field, value in user_in.dict(exclude_unset=True).items():
        if field == "institutional_email":
            value = sanitize_email(value)
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    log_action(current_user.id, f"Updated user {user.id}")
    return user

# -------------------------------
# Soft delete de usuario
# -------------------------------
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user_or_404(db, user_id)
    if current_user.role != "administrator":
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    user.is_active = False
    user.deleted_at = datetime.utcnow()
    db.commit()
    log_action(current_user.id, f"Soft deleted user {user.id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# -------------------------------
# Bulk-create de usuarios
# -------------------------------
@router.post("/bulk", response_model=List[UserOut])
def bulk_create_users(users_in: List[UserCreate], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "administrator":
        raise HTTPException(status_code=403, detail="Only admins can create users")

    created_users = []
    for user_data in users_in:
        sanitized_email = sanitize_email(user_data.institutional_email)
        data = user_data.dict()
        data["institutional_email"] = sanitized_email
        data["id"] = uuid4()
        data["created_at"] = datetime.utcnow()
        user = User(**data)
        db.add(user)
        created_users.append(user)

    db.commit()
    for user in created_users:
        db.refresh(user)
        log_action(current_user.id, f"Bulk created user {user.id}")
    return created_users

# -------------------------------
# Reset / cambiar contraseña
# -------------------------------
@router.post("/{user_id}/reset-password")
def reset_password(user_id: UUID, new_password: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user_or_404(db, user_id)
    check_owner_or_admin(current_user, user)
    if hasattr(user, "set_password"):
        user.set_password(new_password)
    else:
        user.password = new_password  # fallback simple
    db.commit()
    log_action(current_user.id, f"Password reset for user {user.id}")
    return {"detail": "Password updated successfully"}

# -------------------------------
# Exportar usuarios a CSV
# -------------------------------
@router.get("/export/csv")
def export_users_csv(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "administrator":
        raise HTTPException(status_code=403, detail="Only admins can export users")

    users = db.query(User).filter(User.is_active).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "First Names", "Last Names", "Email", "Created At", "Updated At"])

    for u in users:
        writer.writerow([u.id, u.first_names, u.last_names, u.institutional_email, u.created_at, u.updated_at])

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=users.csv"
    return response
