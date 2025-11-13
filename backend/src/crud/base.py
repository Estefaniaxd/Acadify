# src/crud/base.py
from typing import Any, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session


ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase[ModelType, CreateSchemaType: BaseModel, UpdateSchemaType: BaseModel]:
    def __init__(self, model: type[ModelType], id_field: str = "id") -> None:
        """Objeto CRUD con métodos por defecto para Create, Read, Update, Delete (CRUD).

        **Parámetros**
        * `model`: Clase del modelo SQLAlchemy
        """
        self.model = model
        self.id_field = id_field

    def get(self, db: Session, id: Any) -> ModelType | None:
        """Obtener un registro por ID."""
        return (
            db.query(self.model)
            .filter(getattr(self.model, self.id_field) == id)
            .first()
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Obtener múltiples registros con paginación."""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Crear un nuevo registro."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """Actualizar un registro existente."""
        update_data = (
            obj_in
            if isinstance(obj_in, dict)
            else obj_in.model_dump(exclude_unset=True)
        )

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> ModelType | None:
        """Eliminar un registro por ID."""
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


# Stub para evitar error de importación circular
class CRUDMensajeBot(CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]):
    pass
