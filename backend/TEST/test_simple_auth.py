"""
Endpoint de prueba para comentarios sin Redis
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import logging
import uuid
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from src.db.session import SessionLocal, get_db
from src.core.config import settings
from src.models.users.usuario import Usuario
from src.crud.user.usuario import usuario_crud

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Router de prueba
test_router = APIRouter(prefix="/test")

def get_current_user_simple(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """Autenticación simplificada sin Redis"""
    try:
        token = credentials.credentials
        
        # Decodificar token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        # Verificar tipo
        if payload.get("type") != "access":,
            raise HTTPException(status_code=401, detail="Token tipo inválido")
        
        # Obtener usuario
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token sin usuario")
        
        user = usuario_crud.get(db, id=uuid.UUID(user_id))
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    except Exception as e:
        logger.error(f"Error en autenticación: {e}")
        raise HTTPException(status_code=401, detail="Error de autenticación")

@test_router.get("/comentarios/{curso_id}")
async def test_obtener_comentarios(
    curso_id: str,
    current_user: Usuario = Depends(get_current_user_simple)
):
    """Endpoint de prueba para comentarios"""
    try:
        logger.info(f"[TEST] Obteniendo comentarios del curso {curso_id} para usuario: {current_user.usuario_id}")
        
        db = SessionLocal()
        
        try:
            # Verificar acceso al curso
            acceso_result = db.execute(text("""
                SELECT 1 FROM "EstudianteGrupo" eg
                JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id,
                WHERE gc.curso_id = :curso_id AND eg.estudiante_id = :usuario_id
                
                UNION
                
                SELECT 1 FROM "GrupoCurso" gc
                WHERE gc.curso_id = :curso_id AND gc.docente_id = :usuario_id
            """), {"curso_id": curso_id, "usuario_id": current_user.usuario_id}).fetchone()
            
            if not acceso_result:
                return {"error": "No tienes acceso a este curso", "status": 403}
            
            # Obtener comentarios
            result = db.execute(text("""
                SELECT c.comentario_id, c.contenido, c.tipo, c.fecha_creacion, 
                       u.nombres, u.apellidos
                FROM "Comentario" c
                JOIN "Usuario" u ON c.autor_id = u.usuario_id,
                WHERE c.curso_id = :curso_id
                ORDER BY c.fecha_creacion DESC
                LIMIT 10
            """), {"curso_id": curso_id})
            
            comentarios = []
            for row in result.fetchall():
                comentarios.append({
                    "id": str(row[0]),
                    "contenido": row[1],
                    "tipo": row[2],
                    "fecha": row[3].isoformat(),
                    "autor": f"{row[4]} {row[5]}"
                })
            
            return {
                "success": True,
                "data": comentarios,
                "total": len(comentarios),
                "user_id": str(current_user.usuario_id),
                "user_name": f"{current_user.nombres} {current_user.apellidos}"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[TEST] Error: {e}")
        return {"error": str(e), "status": 500}