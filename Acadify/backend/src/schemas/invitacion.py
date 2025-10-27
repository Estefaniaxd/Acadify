from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from uuid import UUID
from datetime import datetime

class InvitacionCreate(BaseModel):
    email_destino: EmailStr
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email_destino": "coordinador@universidad.edu"
            }
        }
    }

class InvitacionResponse(BaseModel):
    id: UUID
    codigo: constr(min_length=6, max_length=6)
    email_destino: EmailStr
    institucion_id: UUID
    estado: str
    fecha_creacion: datetime
    fecha_expiracion: datetime
    coordinador_id: Optional[UUID]
    usado_en: Optional[datetime]

    model_config = {
        "from_attributes": True
    }

class InvitacionAceptar(BaseModel):
    codigo: constr(min_length=6, max_length=6)
    password: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "codigo": "123456",
                "password": "MiContraseña123!"
            }
        }
    }
