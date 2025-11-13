"""Utilidades de paginación centralizadas.

Proporciona helpers reutilizables para paginación consistente
en toda la aplicación siguiendo Clean Code y DRY.
"""

from typing import Any, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field


# Type variable para tipado genérico
T = TypeVar("T")


class PaginationParams(BaseModel):
    """Parámetros de paginación estandarizados.

    Uso en rutas:
        pagination: PaginationParams = Depends()
    """

    limit: int = Field(
        default=50, ge=1, le=100, description="Número máximo de resultados por página"
    )
    offset: int = Field(default=0, ge=0, description="Número de resultados a saltar")

    @property
    def page(self) -> int:
        """Calcula el número de página basado en offset y limit."""
        return (self.offset // self.limit) + 1 if self.limit > 0 else 1

    def dict_params(self) -> dict[str, int]:
        """Retorna dict para usar en queries SQL."""
        return {"limit": self.limit, "offset": self.offset}


class PaginatedResponse[T](BaseModel):
    """Respuesta paginada genérica estandarizada.

    Uso en services:
        return PaginatedResponse(
            success=True,
            data=items,
            total=len(items),
            page=pagination.page,
            limit=pagination.limit,
            message="Datos obtenidos exitosamente"
        )
    """

    success: bool = True
    message: str = "Datos obtenidos exitosamente"
    data: list[T]
    total: int = Field(description="Total de items en la página actual")
    page: int | None = Field(default=None, description="Número de página actual")
    limit: int | None = Field(default=None, description="Items por página")
    total_pages: int | None = Field(default=None, description="Total de páginas")
    has_next: bool | None = Field(default=None, description="Hay página siguiente")
    has_prev: bool | None = Field(default=None, description="Hay página anterior")

    def __init__(self, **data) -> None:
        """Calcula campos derivados automáticamente."""
        super().__init__(**data)

        # Calcular total_pages si tenemos limit
        if self.limit and self.limit > 0:
            self.total_pages = (self.total + self.limit - 1) // self.limit

            # Calcular has_next y has_prev si tenemos page
            if self.page:
                self.has_next = (
                    self.page < self.total_pages if self.total_pages else False
                )
                self.has_prev = self.page > 1


def create_pagination_query(limit_default: int = 50, limit_max: int = 100):
    """Factory para crear parámetros de paginación como dependencia.

    Uso en rutas:
        @router.get("/items")
        def get_items(
            limit: int = Query(50, le=100),
            offset: int = Query(0, ge=0)
        ):
            ...

    Equivalente con factory:
        pagination = create_pagination_query()

        @router.get("/items")
        def get_items(pagination: PaginationParams = Depends(pagination)):
            ...
    """

    def get_pagination(
        limit: int = Query(
            default=limit_default,
            ge=1,
            le=limit_max,
            description="Límite de resultados por página",
        ),
        offset: int = Query(
            default=0, ge=0, description="Offset de resultados (para paginación)"
        ),
    ) -> PaginationParams:
        return PaginationParams(limit=limit, offset=offset)

    return get_pagination


def paginate_dict_response(
    data: list[Any],
    total: int,
    limit: int,
    offset: int,
    message: str = "Datos obtenidos exitosamente",
    **extra_fields,
) -> dict[str, Any]:
    """Helper para crear respuestas paginadas como Dict.

    Uso en services que retornan Dict:
        return paginate_dict_response(
            data=items,
            total=len(items),
            limit=limit,
            offset=offset,
            message="Cursos obtenidos",
            source="database"  # campos extra
        )
    """
    pagination = PaginationParams(limit=limit, offset=offset)

    response = {
        "success": True,
        "message": message,
        "data": data,
        "total": total,
        "page": pagination.page,
        "limit": limit,
        "offset": offset,
    }

    # Calcular metadata de paginación
    if limit > 0:
        total_pages = (total + limit - 1) // limit
        response["total_pages"] = total_pages
        response["has_next"] = (
            pagination.page < total_pages if total_pages > 0 else False
        )
        response["has_prev"] = pagination.page > 1

    # Agregar campos extra
    response.update(extra_fields)

    return response


# Constantes de paginación global
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100
DEFAULT_OFFSET = 0


# Helper para queries SQL con paginación
def get_sql_pagination_clause(
    limit: int = DEFAULT_PAGE_SIZE, offset: int = DEFAULT_OFFSET
) -> str:
    """Genera cláusula SQL LIMIT/OFFSET segura.

    Uso:
        query = f"SELECT * FROM tabla {get_sql_pagination_clause(limit, offset)}"
    """
    return f"LIMIT {int(limit)} OFFSET {int(offset)}"


def validate_pagination_params(limit: int, offset: int) -> None:
    """Valida parámetros de paginación.

    Raises:
        ValueError: Si los parámetros no son válidos
    """
    if limit < 1:
        msg = "El límite debe ser al menos 1"
        raise ValueError(msg)

    if limit > MAX_PAGE_SIZE:
        msg = f"El límite no puede exceder {MAX_PAGE_SIZE}"
        raise ValueError(msg)

    if offset < 0:
        msg = "El offset no puede ser negativo"
        raise ValueError(msg)


# Ejemplo de uso en services:
"""
from src.utils.pagination import paginate_dict_response, DEFAULT_PAGE_SIZE

def obtener_items(
    db: Session,
    limit: int = DEFAULT_PAGE_SIZE,
    offset: int = 0
) -> Dict[str, Any]:
    items = db.query(Item).limit(limit).offset(offset).all()
    total = db.query(Item).count()

    return paginate_dict_response(
        data=[item.dict() for item in items],
        total=total,
        limit=limit,
        offset=offset,
        message="Items obtenidos exitosamente"
    )
"""

# Ejemplo de uso en rutas:
"""
from src.utils.pagination import PaginationParams
from fastapi import Depends

@router.get("/items")
def get_items(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(deps.get_db)
):
    return item_service.obtener_items(
        db=db,
        limit=pagination.limit,
        offset=pagination.offset
    )
"""
