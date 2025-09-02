from fastapi import Depends, HTTPException, status, Query
from typing import Optional, List, Dict
from app.core.security import get_current_active_user
from app.models.user import User, UserRole

# -------------------------------
# Dependencia de rol genérica
# -------------------------------
def get_current_user_with_role(allowed_roles: List[UserRole]):
    """
    Crea una dependencia que verifica que el usuario tenga uno de los roles permitidos
    """
    def check_user_role(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción"
            )
        return current_user
    return check_user_role

# -------------------------------
# Dependencias específicas por rol
# -------------------------------
def get_current_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Requiere rol de administrador"""
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user

def get_current_coordinator(current_user: User = Depends(get_current_active_user)) -> User:
    """Requiere rol de coordinador"""
    if current_user.role != UserRole.COORDINATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de coordinador"
        )
    return current_user

def get_current_teacher(current_user: User = Depends(get_current_active_user)) -> User:
    """Requiere rol de docente"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de docente"
        )
    return current_user

def get_current_student(current_user: User = Depends(get_current_active_user)) -> User:
    """Requiere rol de estudiante"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de estudiante"
        )
    return current_user

# -------------------------------
# Dependencias de paginación
# -------------------------------
def get_pagination_params(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página")
) -> Dict[str, int]:
    skip = (page - 1) * size
    return {"skip": skip, "limit": size, "page": page, "size": size}

# -------------------------------
# Dependencias de búsqueda y orden
# -------------------------------
def get_search_params(
    q: Optional[str] = Query(None, description="Término de búsqueda"),
    sort_by: Optional[str] = Query("created_at", description="Campo por el cual ordenar"),
    sort_order: Optional[str] = Query("desc", pattern="^(asc|desc)$", description="Orden ascendente o descendente")
) -> Dict[str, Optional[str]]:
    return {"search_query": q, "sort_by": sort_by, "sort_order": sort_order}
