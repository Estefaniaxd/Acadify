from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, date
from typing import List, Optional
from src.crud.classes import clase
from src.db.session import get_db
from src.schemas.classes.clase import ClaseCreate, ClaseUpdate, Clase as ClaseSchema

router = APIRouter(
    prefix="/clases",
    tags=["clases"]
)

CLASE_NOT_FOUND = "Clase no encontrada"

# ============================================================================
# ENDPOINTS BÁSICOS CRUD
# ============================================================================

@router.post("/", response_model=ClaseSchema, status_code=201)
def create_clase(
    clase_in: ClaseCreate,
    db: Session = Depends(get_db),
):
    """
    Crear una nueva clase.
    """
    return clase.create(db=db, obj_in=clase_in)

@router.get("/{clase_id}", response_model=ClaseSchema)
def read_clase(
    clase_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Obtener una clase específica por ID.
    """
    db_clase = clase.get(db=db, clase_id=clase_id)
    if not db_clase:
        raise HTTPException(status_code=404, detail=CLASE_NOT_FOUND)
    return db_clase

@router.get("/", response_model=List[ClaseSchema])
def read_clases(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo número de registros a retornar"),
    db: Session = Depends(get_db),
):
    """
    Obtener lista de clases con paginación.
    """
    clases = clase.get_multi(db=db, skip=skip, limit=limit)
    return clases

@router.put("/{clase_id}", response_model=ClaseSchema)
def update_clase(
    clase_id: UUID,
    clase_in: ClaseUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualizar una clase existente.
    """
    db_clase = clase.get(db=db, clase_id=clase_id)
    if not db_clase:
        raise HTTPException(status_code=404, detail=CLASE_NOT_FOUND)
    
    return clase.update(db=db, db_obj=db_clase, obj_in=clase_in)

@router.delete("/{clase_id}", status_code=204)
def delete_clase(
    clase_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Eliminar una clase.
    """
    db_clase = clase.remove(db=db, clase_id=clase_id)
    if not db_clase:
        raise HTTPException(status_code=404, detail=CLASE_NOT_FOUND)

# ============================================================================
# ENDPOINTS DE FILTRADO Y CONSULTAS ESPECÍFICAS
# ============================================================================

@router.get("/grupo-curso/{grupo_curso_id}", response_model=List[ClaseSchema])
def read_clases_by_grupo_curso(
    grupo_curso_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Obtener todas las clases de un grupo curso específico.
    """
    clases = clase.get_by_grupo_curso(db=db, grupo_curso_id=grupo_curso_id)
    return clases

@router.get("/plataforma/{plataforma_id}", response_model=List[ClaseSchema])
def read_clases_by_plataforma(
    plataforma_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Obtener todas las clases de una plataforma específica.
    """
    clases = clase.get_by_plataforma(db=db, plataforma_id=plataforma_id)
    return clases

@router.get("/proximas/", response_model=List[ClaseSchema])
def read_upcoming_clases(
    limit: int = Query(10, ge=1, le=50, description="Número máximo de clases próximas a retornar"),
    db: Session = Depends(get_db),
):
    """
    Obtener las próximas clases ordenadas por fecha de inicio.
    """
    clases = clase.get_upcoming_classes(db=db, limit=limit)
    return clases

@router.get("/rango-fechas/", response_model=List[ClaseSchema])
def read_clases_by_date_range(
    fecha_inicio: datetime = Query(..., description="Fecha y hora de inicio del rango (formato: 2024-01-01T10:00:00)"),
    fecha_fin: datetime = Query(..., description="Fecha y hora de fin del rango (formato: 2024-01-31T18:00:00)"),
    db: Session = Depends(get_db),
):
    """
    Obtener clases dentro de un rango de fechas específico.
    Las fechas deben estar en formato ISO 8601: YYYY-MM-DDTHH:MM:SS
    """
    if fecha_inicio >= fecha_fin:
        raise HTTPException(
            status_code=400, 
            detail="La fecha de inicio debe ser anterior a la fecha de fin"
        )
    
    clases = clase.get_by_date_range(
        db=db, 
        start_date=fecha_inicio, 
        end_date=fecha_fin
    )
    return clases

# ============================================================================
# ENDPOINTS DE CONVENIENCIA CON QUERY PARAMETERS
# ============================================================================

@router.get("/buscar/", response_model=List[ClaseSchema])
def search_clases(
    grupo_curso_id: Optional[UUID] = Query(None, description="Filtrar por grupo curso"),
    plataforma_id: Optional[UUID] = Query(None, description="Filtrar por plataforma"),
    fecha_desde: Optional[date] = Query(None, description="Filtrar desde esta fecha (formato: YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Filtrar hasta esta fecha (formato: YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo número de registros a retornar"),
    db: Session = Depends(get_db),
):
    """
    Buscar clases con múltiples filtros opcionales.
    Permite combinar filtros por grupo curso, plataforma y rango de fechas.
    """
    from src.models.classes.clase import Clase
    
    # Construir query base
    query = db.query(Clase)
    
    # Aplicar filtros según los parámetros proporcionados
    if grupo_curso_id:
        query = query.filter(Clase.grupo_curso_id == grupo_curso_id)
    
    if plataforma_id:
        query = query.filter(Clase.plataforma_id == plataforma_id)
    
    if fecha_desde:
        fecha_inicio = datetime.combine(fecha_desde, datetime.min.time())
        query = query.filter(Clase.hora_inicio >= fecha_inicio)
    
    if fecha_hasta:
        fecha_fin = datetime.combine(fecha_hasta, datetime.max.time())
        query = query.filter(Clase.hora_inicio <= fecha_fin)
    
    # Ordenar por fecha de inicio y aplicar paginación
    clases = query.order_by(Clase.hora_inicio).offset(skip).limit(limit).all()
    
    return clases

# ============================================================================
# ENDPOINTS PARA CASOS DE USO ESPECÍFICOS
# ============================================================================

@router.get("/hoy/", response_model=List[ClaseSchema])
def read_clases_today(
    db: Session = Depends(get_db),
):
    """
    Obtener todas las clases programadas para hoy.
    """
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    
    clases = clase.get_by_date_range(
        db=db,
        start_date=start_of_day,
        end_date=end_of_day
    )
    return clases

@router.get("/esta-semana/", response_model=List[ClaseSchema])
def read_clases_this_week(
    db: Session = Depends(get_db),
):
    """
    Obtener todas las clases de esta semana.
    """
    from datetime import timedelta
    
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Lunes
    end_of_week = start_of_week + timedelta(days=6)  # Domingo
    
    start_datetime = datetime.combine(start_of_week, datetime.min.time())
    end_datetime = datetime.combine(end_of_week, datetime.max.time())
    
    clases = clase.get_by_date_range(
        db=db,
        start_date=start_datetime,
        end_date=end_datetime
    )
    return clases

@router.patch("/{clase_id}/link", response_model=ClaseSchema)
def update_clase_link(
    clase_id: UUID,
    nuevo_link: str = Query(..., description="Nuevo enlace de videollamada"),
    db: Session = Depends(get_db),
):
    """
    Actualizar solo el enlace de videollamada de una clase.
    Útil para cambios rápidos del enlace de la reunión.
    """
    db_clase = clase.get(db=db, clase_id=clase_id)
    if not db_clase:
        raise HTTPException(status_code=404, detail=CLASE_NOT_FOUND)
    
    clase_update = ClaseUpdate(link_videollamada=nuevo_link)
    return clase.update(db=db, db_obj=db_clase, obj_in=clase_update)

@router.patch("/{clase_id}/hora", response_model=ClaseSchema)
def update_clase_hora(
    clase_id: UUID,
    nueva_hora: datetime = Query(..., description="Nueva hora de inicio (formato: 2024-01-01T10:00:00)"),
    db: Session = Depends(get_db),
):
    """
    Actualizar solo la hora de inicio de una clase.
    Útil para reprogramar clases rápidamente.
    """
    db_clase = clase.get(db=db, clase_id=clase_id)
    if not db_clase:
        raise HTTPException(status_code=404, detail=CLASE_NOT_FOUND)
    
    # Validar que la nueva hora no sea en el pasado
    if nueva_hora <= datetime.now():
        raise HTTPException(
            status_code=400, 
            detail="La nueva hora debe ser en el futuro"
        )
    
    clase_update = ClaseUpdate(hora_inicio=nueva_hora)
    return clase.update(db=db, db_obj=db_clase, obj_in=clase_update)