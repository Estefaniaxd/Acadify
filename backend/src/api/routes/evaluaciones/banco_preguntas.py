"""
API routes para gestión del banco de preguntas
Incluye búsqueda, creación, edición y gestión de preguntas reutilizables
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, UploadFile, File
from sqlalchemy.orm import Session
import json

from src.api.deps import get_current_user, get_db
from src.crud.evaluaciones import banco_pregunta
from src.schemas.evaluaciones import (
    BancoPreguntaCreate, BancoPreguntaUpdate, BancoPreguntaResponse, FiltrosBancoPreguntas
)
from src.models.evaluaciones import TipoPregunta, DificultadPregunta
from src.models.users.usuario import Usuario

router = APIRouter()


@router.post("/", response_model=BancoPreguntaResponse, status_code=status.HTTP_201_CREATED)
def crear_pregunta_banco(
    *,
    db: Session = Depends(get_db),
    pregunta_in: BancoPreguntaCreate,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear una nueva pregunta en el banco.
    Solo profesores, coordinadores y administradores pueden crear preguntas.
    """
    # Verificar permisos
    if current_user.role not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear preguntas en el banco"
        )
    
    # Asegurar que el creador es el usuario actual
    pregunta_in.creado_por = current_user.user_id
    
    # Si el usuario no es admin, obtener su institución
    if current_user.role != "administrador":
        # TODO: Obtener institución del usuario
        pregunta_in.institucion_id = getattr(current_user, 'institucion_id', None)
    
    created_pregunta = banco_pregunta.create(db=db, obj_in=pregunta_in)
    return created_pregunta


@router.get("/", response_model=List[BancoPreguntaResponse])
def listar_preguntas_banco(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(50, ge=1, le=200, description="Límite de registros"),
    # Filtros de búsqueda
    tipo_pregunta: Optional[TipoPregunta] = Query(None, description="Filtrar por tipo de pregunta"),
    dificultad: Optional[DificultadPregunta] = Query(None, description="Filtrar por dificultad"),
    materia: Optional[str] = Query(None, description="Filtrar por materia"),
    tema: Optional[str] = Query(None, description="Filtrar por tema"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    nivel_educativo: Optional[str] = Query(None, description="Filtrar por nivel educativo"),
    es_publica: Optional[bool] = Query(None, description="Filtrar por visibilidad"),
    texto_busqueda: Optional[str] = Query(None, description="Búsqueda por texto"),
    solo_propias: bool = Query(False, description="Solo mostrar preguntas propias")
):
    """
    Listar preguntas del banco con filtros.
    Cada usuario ve sus propias preguntas, las públicas y las de su institución.
    """
    # Verificar permisos
    if current_user.role not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder al banco de preguntas"
        )
    
    # Construir filtros
    filtros = FiltrosBancoPreguntas(
        tipo_pregunta=tipo_pregunta,
        dificultad=dificultad,
        materia=materia,
        tema=tema,
        categoria=categoria,
        nivel_educativo=nivel_educativo,
        es_publica=es_publica,
        texto_busqueda=texto_busqueda,
        limite=limit,
        offset=skip
    )
    
    if solo_propias:
        filtros.creado_por = current_user.user_id
    
    # Obtener institución del usuario
    institucion_id = getattr(current_user, 'institucion_id', None)
    
    preguntas = banco_pregunta.buscar_con_filtros(
        db=db, 
        filtros=filtros,
        usuario_id=current_user.user_id,
        institucion_id=institucion_id
    )
    
    return preguntas


@router.get("/{pregunta_id}", response_model=BancoPreguntaResponse)
def obtener_pregunta_banco(
    *,
    db: Session = Depends(get_db),
    pregunta_id: str = Path(..., description="ID de la pregunta"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener detalles de una pregunta específica del banco.
    """
    pregunta = banco_pregunta.get(db=db, id=pregunta_id)
    if not pregunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    # Verificar acceso
    institucion_id = getattr(current_user, 'institucion_id', None)
    puede_ver = (
        current_user.role == "administrador" or
        pregunta.creado_por == current_user.user_id or
        pregunta.es_publica or
        (institucion_id and pregunta.institucion_id == institucion_id)
    )
    
    if not puede_ver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver esta pregunta"
        )
    
    return pregunta


@router.put("/{pregunta_id}", response_model=BancoPreguntaResponse)
def actualizar_pregunta_banco(
    *,
    db: Session = Depends(get_db),
    pregunta_id: str = Path(..., description="ID de la pregunta"),
    pregunta_in: BancoPreguntaUpdate,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar una pregunta del banco.
    Solo el creador o un coordinador de la misma institución pueden editar.
    """
    pregunta = banco_pregunta.get(db=db, id=pregunta_id)
    if not pregunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    # Verificar permisos
    institucion_id = getattr(current_user, 'institucion_id', None)
    puede_editar = (
        current_user.role == "administrador" or
        pregunta.creado_por == current_user.user_id or
        (current_user.role == "coordinador" and 
         institucion_id and pregunta.institucion_id == institucion_id)
    )
    
    if not puede_editar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar esta pregunta"
        )
    
    updated_pregunta = banco_pregunta.update(db=db, db_obj=pregunta, obj_in=pregunta_in)
    return updated_pregunta


@router.delete("/{pregunta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pregunta_banco(
    *,
    db: Session = Depends(get_db),
    pregunta_id: str = Path(..., description="ID de la pregunta"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Eliminar una pregunta del banco.
    Solo el creador o un administrador pueden eliminar.
    """
    pregunta = banco_pregunta.get(db=db, id=pregunta_id)
    if not pregunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    # Verificar permisos
    puede_eliminar = (
        current_user.role == "administrador" or
        pregunta.creado_por == current_user.user_id
    )
    
    if not puede_eliminar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar esta pregunta"
        )
    
    # Verificar si está siendo usada
    if pregunta.veces_utilizada > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar una pregunta que está siendo utilizada en exámenes"
        )
    
    banco_pregunta.remove(db=db, id=pregunta_id)


@router.post("/{pregunta_id}/duplicar", response_model=BancoPreguntaResponse)
def duplicar_pregunta_banco(
    *,
    db: Session = Depends(get_db),
    pregunta_id: str = Path(..., description="ID de la pregunta a duplicar"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Duplicar una pregunta del banco para el usuario actual.
    """
    # Verificar permisos
    if current_user.role not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para duplicar preguntas"
        )
    
    institucion_id = getattr(current_user, 'institucion_id', None)
    
    pregunta_duplicada = banco_pregunta.duplicar_pregunta(
        db=db,
        pregunta_id=pregunta_id,
        nuevo_creador_id=current_user.user_id,
        nueva_institucion_id=institucion_id
    )
    
    if not pregunta_duplicada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta a duplicar no encontrada"
        )
    
    return pregunta_duplicada


@router.post("/{pregunta_id}/marcar-publica", response_model=BancoPreguntaResponse)
def marcar_pregunta_publica(
    *,
    db: Session = Depends(get_db),
    pregunta_id: str = Path(..., description="ID de la pregunta"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Marcar una pregunta como pública.
    Solo el creador puede hacer su pregunta pública.
    """
    pregunta_marcada = banco_pregunta.marcar_como_publica(
        db=db, pregunta_id=pregunta_id, usuario_id=current_user.user_id
    )
    
    if not pregunta_marcada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada o no tienes permisos"
        )
    
    return pregunta_marcada


@router.post("/{pregunta_id}/solicitar-revision", response_model=BancoPreguntaResponse)
def solicitar_revision_pregunta(
    *,
    db: Session = Depends(get_db),
    pregunta_id: str = Path(..., description="ID de la pregunta"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Solicitar revisión de una pregunta para hacerla pública.
    """
    pregunta_enviada = banco_pregunta.solicitar_revision(
        db=db, pregunta_id=pregunta_id, usuario_id=current_user.user_id
    )
    
    if not pregunta_enviada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada o no tienes permisos"
        )
    
    return pregunta_enviada


@router.post("/{pregunta_id}/revisar", response_model=BancoPreguntaResponse)
def revisar_pregunta(
    *,
    db: Session = Depends(get_db),
    pregunta_id: str = Path(..., description="ID de la pregunta"),
    aprobada: bool = Body(..., embed=True, description="Si se aprueba la pregunta"),
    comentarios: Optional[str] = Body(None, embed=True, description="Comentarios de la revisión"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Revisar una pregunta pendiente.
    Solo coordinadores y administradores pueden revisar.
    """
    if current_user.role not in ["coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para revisar preguntas"
        )
    
    pregunta_revisada = banco_pregunta.revisar_pregunta(
        db=db,
        pregunta_id=pregunta_id,
        revisor_id=current_user.user_id,
        aprobada=aprobada,
        comentarios=comentarios
    )
    
    if not pregunta_revisada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    return pregunta_revisada


@router.get("/pendientes-revision/", response_model=List[BancoPreguntaResponse])
def obtener_preguntas_pendientes_revision(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200)
):
    """
    Obtener preguntas pendientes de revisión.
    Solo coordinadores y administradores pueden acceder.
    """
    if current_user.role not in ["coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver preguntas pendientes"
        )
    
    institucion_id = None
    if current_user.role == "coordinador":
        institucion_id = getattr(current_user, 'institucion_id', None)
    
    preguntas_pendientes = banco_pregunta.get_preguntas_pendientes_revision(
        db=db, institucion_id=institucion_id, skip=skip, limit=limit
    )
    
    return preguntas_pendientes


@router.get("/materias/", response_model=List[str])
def obtener_materias_disponibles(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener lista de materias disponibles en el banco.
    """
    if current_user.role not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder al banco de preguntas"
        )
    
    institucion_id = getattr(current_user, 'institucion_id', None)
    materias = banco_pregunta.get_materias_disponibles(
        db=db, usuario_id=current_user.user_id, institucion_id=institucion_id
    )
    
    return materias


@router.get("/materias/{materia}/temas", response_model=List[str])
def obtener_temas_por_materia(
    *,
    db: Session = Depends(get_db),
    materia: str = Path(..., description="Nombre de la materia"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener temas disponibles para una materia específica.
    """
    if current_user.role not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder al banco de preguntas"
        )
    
    institucion_id = getattr(current_user, 'institucion_id', None)
    temas = banco_pregunta.get_temas_por_materia(
        db=db, materia=materia, usuario_id=current_user.user_id, institucion_id=institucion_id
    )
    
    return temas


@router.get("/tags/populares", response_model=List[Dict[str, Any]])
def obtener_tags_populares(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    limite: int = Query(50, ge=1, le=100, description="Número máximo de tags")
):
    """
    Obtener los tags más populares del banco.
    """
    if current_user.role not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder al banco de preguntas"
        )
    
    institucion_id = getattr(current_user, 'institucion_id', None)
    tags_populares = banco_pregunta.get_tags_populares(
        db=db, limite=limite, usuario_id=current_user.user_id, institucion_id=institucion_id
    )
    
    return tags_populares


@router.get("/estadisticas/", response_model=Dict[str, Any])
def obtener_estadisticas_banco(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener estadísticas del banco de preguntas.
    """
    if current_user.role not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estas estadísticas"
        )
    
    institucion_id = getattr(current_user, 'institucion_id', None)
    estadisticas = banco_pregunta.get_estadisticas_banco(
        db=db, usuario_id=current_user.user_id, institucion_id=institucion_id
    )
    
    return estadisticas


@router.post("/exportar", response_model=Dict[str, Any])
def exportar_preguntas(
    *,
    db: Session = Depends(get_db),
    pregunta_ids: List[str] = Body(..., description="Lista de IDs de preguntas a exportar"),
    formato: str = Body("json", description="Formato de exportación"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Exportar preguntas seleccionadas.
    """
    if current_user.role not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para exportar preguntas"
        )
    
    if not pregunta_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Debe seleccionar al menos una pregunta"
        )
    
    # Verificar que el usuario puede acceder a todas las preguntas
    for pregunta_id in pregunta_ids:
        pregunta = banco_pregunta.get(db=db, id=pregunta_id)
        if not pregunta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pregunta {pregunta_id} no encontrada"
            )
        
        # Verificar acceso
        institucion_id = getattr(current_user, 'institucion_id', None)
        puede_exportar = (
            current_user.role == "administrador" or
            pregunta.creado_por == current_user.user_id or
            pregunta.es_publica or
            (institucion_id and pregunta.institucion_id == institucion_id)
        )
        
        if not puede_exportar:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos para exportar la pregunta {pregunta_id}"
            )
    
    resultado_exportacion = banco_pregunta.exportar_preguntas(
        db=db, pregunta_ids=pregunta_ids, formato=formato
    )
    
    return resultado_exportacion


@router.post("/importar", response_model=Dict[str, Any])
async def importar_preguntas(
    *,
    db: Session = Depends(get_db),
    archivo: UploadFile = File(..., description="Archivo con preguntas a importar"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Importar preguntas desde un archivo.
    """
    if current_user.role not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para importar preguntas"
        )
    
    # Verificar tipo de archivo
    if not archivo.filename.endswith('.json'):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Solo se admiten archivos JSON"
        )
    
    try:
        # Leer contenido del archivo
        contenido = await archivo.read()
        datos_importacion = json.loads(contenido)
        
        # Obtener institución del usuario
        institucion_id = getattr(current_user, 'institucion_id', None)
        
        # Importar preguntas
        resultado = banco_pregunta.importar_preguntas(
            db=db,
            datos_importacion=datos_importacion,
            usuario_id=current_user.user_id,
            institucion_id=institucion_id
        )
        
        return resultado
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Archivo JSON inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el archivo: {str(e)}"
        )