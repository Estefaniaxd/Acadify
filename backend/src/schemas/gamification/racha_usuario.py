from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import date

class RachaUsuarioBase(BaseModel):
    usuario_id: UUID
    racha_actual: int = 0
    mejor_racha: int = 0
    fecha_ultimo_dia: Optional[date] = None 
    
class RachaUsuarioCreate(RachaUsuarioBase):
    pass

class RachaUsuarioUpdate(BaseModel):
    racha_actual: int
    mejor_racha: int
    fecha_ultimo_dia: Optional[date] = None
    
class RachaUsuarioInDBBase(RachaUsuarioBase):
    usuario_id: UUID
    
    class Config:
        from_attributes = True
    
class RachaUsuario(RachaUsuarioInDBBase):
    pass