from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.password_utils import get_password_hash, verify_password
from app.models.user import User, UserRole, AccountStatus
from app.schemas.user import UserCreate, UserUpdate
from .base import CRUDBase

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """Operaciones CRUD para usuarios"""

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.institutional_email == email).first()

    def get_by_document(self, db: Session, *, document_number: str) -> Optional[User]:
        return db.query(User).filter(User.document_number == document_number).first()

    def search_users(
        self,
        db: Session,
        *,
        query: str,
        role: Optional[UserRole] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        search_filter = or_(
            User.first_names.ilike(f"%{query}%"),
            User.last_names.ilike(f"%{query}%"),
            User.institutional_email.ilike(f"%{query}%")
        )
        db_query = db.query(User).filter(search_filter)
        if role:
            db_query = db_query.filter(User.role == role)
        return db_query.offset(skip).limit(limit).all()

    def get_by_role(
        self,
        db: Session,
        *,
        role: UserRole,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        create_data = obj_in.dict()
        create_data["password_hash"] = get_password_hash(create_data.pop("password"))
        db_obj = User(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def update_password(self, db: Session, *, user: User, new_password: str) -> User:
        user.password_hash = get_password_hash(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_last_access(self, db: Session, *, user: User) -> User:
        user.last_access = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def change_account_status(self, db: Session, *, user: User, new_status: AccountStatus) -> User:
        user.account_status = new_status
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def is_active(self, user: User) -> bool:
        return user.account_status == AccountStatus.ACTIVE

    def is_superuser(self, user: User) -> bool:
        return user.role == UserRole.ADMINISTRATOR

# Instancia global
user_crud = CRUDUser(User)
