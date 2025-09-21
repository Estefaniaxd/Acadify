from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from src.crud.classes import asistencia
from src.api.deps import get_db
from src.schemas.classes.asistencia import (
    Asistencia,
    AsistenciaCreate,
    AsistenciaUpdate
)
from src.enums.classes.asistencia_enums import EstadoAsistencia

router = APIRouter()

ASISTENCIA_NOT_FOUND = "Asistencia no encontrada"


# Crear asistencia
@router.post("/", response_model=Asistencia, status_code=201)
def create_asistencia(
    *,
    db: Session = Depends(get_db),
    asistencia_in: AsistenciaCreate,
):
    """
    Crear una nueva asistencia.
    """
    # Verificar si ya existe una asistencia para ese estudiante en esa clase
    existing = asistencia.get_by_clase_and_estudiante(
        db=db,
        clase_id=asistencia_in.clase_id,
        estudiante_id=asistencia_in.estudiante_id,
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una asistencia registrada para este estudiante en esta clase",
        )

    return asistencia.create(db=db, obj_in=asistencia_in)


# Obtener asistencia específica
@router.get("/{asistencia_id}", response_model=Asistencia)
def read_asistencia(
    asistencia_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Obtener asistencia por ID.
    """
    db_asistencia = asistencia.get(db=db, asistencia_id=asistencia_id)
    if not db_asistencia:
        raise HTTPException(status_code=404, detail=ASISTENCIA_NOT_FOUND)
    return db_asistencia


# Obtener múltiples asistencias con paginación
@router.get("/", response_model=List[Asistencia])
def read_asistencias(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(
        100, ge=1, le=1000, description="Máximo número de registros a retornar"
    ),
    db: Session = Depends(get_db),
):
    """
    Obtener lista de asistencias con paginación.
    """
    asistencias = asistencia.get_multi(db=db, skip=skip, limit=limit)
    return asistencias


# Obtener asistencias por clase
@router.get("/clase/{clase_id}", response_model=List[Asistencia])
def read_asistencias_by_clase(
    clase_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Obtener todas las asistencias de una clase específica.
    """
    asistencias = asistencia.get_by_clase(db=db, clase_id=clase_id)
    return asistencias


# Obtener asistencias por estudiante
@router.get("/estudiante/{estudiante_id}", response_model=List[Asistencia])
def read_asistencias_by_estudiante(
    estudiante_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Obtener todas las asistencias de un estudiante específico.
    """
    asistencias = asistencia.get_by_estudiante(db=db, estudiante_id=estudiante_id)
    return asistencias


# Obtener asistencias por estado
@router.get("/estado/{estado}", response_model=List[Asistencia])
def read_asistencias_by_estado(
    estado: EstadoAsistencia,
    db: Session = Depends(get_db),
):
    """
    Obtener asistencias filtradas por estado.
    """
    asistencias = asistencia.get_by_estado(db=db, estado=estado)
    return asistencias


# Obtener asistencia específica de estudiante en clase
@router.get(
    "/clase/{clase_id}/estudiante/{estudiante_id}", response_model=Asistencia
)
def read_asistencia_by_clase_and_estudiante(
    clase_id: UUID,
    estudiante_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Obtener la asistencia de un estudiante específico en una clase específica.
    """
    db_asistencia = asistencia.get_by_clase_and_estudiante(
        db=db, clase_id=clase_id, estudiante_id=estudiante_id
    )
    if not db_asistencia:
        raise HTTPException(
            status_code=404,
            detail="No se encontró asistencia para este estudiante en esta clase",
        )
    return db_asistencia


# Actualizar asistencia
@router.put("/{asistencia_id}", response_model=Asistencia)
def update_asistencia(
    asistencia_id: UUID,
    asistencia_in: AsistenciaUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualizar una asistencia existente.
    """
    db_asistencia = asistencia.get(db=db, asistencia_id=asistencia_id)
    if not db_asistencia:
        raise HTTPException(status_code=404, detail=ASISTENCIA_NOT_FOUND)

    return asistencia.update(db=db, db_obj=db_asistencia, obj_in=asistencia_in)


# Actualizar estado de asistencia (endpoint específico)
@router.patch("/{asistencia_id}/estado", response_model=Asistencia)
def update_estado_asistencia(
    asistencia_id: UUID,
    estado: EstadoAsistencia,
    db: Session = Depends(get_db),
):
    """
    Actualizar solo el estado de una asistencia.
    """
    db_asistencia = asistencia.get(db=db, asistencia_id=asistencia_id)
    if not db_asistencia:
        raise HTTPException(status_code=404, detail=ASISTENCIA_NOT_FOUND)

    asistencia_update = AsistenciaUpdate(estado=estado)
    return asistencia.update(db=db, db_obj=db_asistencia, obj_in=asistencia_update)


# Eliminar asistencia
@router.delete("/{asistencia_id}", status_code=204)
def delete_asistencia(
    asistencia_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Eliminar una asistencia.
    """
    db_asistencia = asistencia.remove(db=db, asistencia_id=asistencia_id)
    if not db_asistencia:
        raise HTTPException(status_code=404, detail=ASISTENCIA_NOT_FOUND)


# Endpoint para registrar asistencia masiva (útil para tomar asistencia de toda una clase)
@router.post("/clase/{clase_id}/masiva", response_model=List[Asistencia])
def create_asistencia_masiva(
    clase_id: UUID,
    asistencias_data: List[
        dict
    ],  # [{"estudiante_id": UUID, "estado": EstadoAsistencia}]
    db: Session = Depends(get_db),
):
    """
    Crear múltiples asistencias para una clase específica.
    Formato esperado: [{"estudiante_id": "uuid", "estado": "PRESENTE|AUSENTE|TARDANZA"}]
    """
    created_asistencias = []

    for item in asistencias_data:
        try:
            # Verificar si ya existe
            existing = asistencia.get_by_clase_and_estudiante(
                db=db, clase_id=clase_id, estudiante_id=UUID(item["estudiante_id"])
            )

            if existing:
                # Actualizar si ya existe
                asistencia_update = AsistenciaUpdate(estado=item["estado"])
                updated = asistencia.update(
                    db=db, db_obj=existing, obj_in=asistencia_update
                )
                created_asistencias.append(updated)
            else:
                # Crear nuevo si no existe
                asistencia_create = AsistenciaCreate(
                    clase_id=clase_id,
                    estudiante_id=UUID(item["estudiante_id"]),
                    estado=EstadoAsistencia(item["estado"]),
                )
                new_asistencia = asistencia.create(db=db, obj_in=asistencia_create)
                created_asistencias.append(new_asistencia)

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error procesando estudiante {item.get('estudiante_id')}: {str(e)}",
            )

    return created_asistencias
