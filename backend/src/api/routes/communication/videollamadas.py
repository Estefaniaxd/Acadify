"""API Routes refactorizados para videollamadas con service layer y enums.

Este módulo implementa endpoints REST para gestión de videollamadas usando:
- Service Layer (VideollamadaService) para lógica de negocio
- Python Enums para type-safety
- SOLID principles
- Proper error handling con HTTPExceptions

Arquitectura de 3 capas:
    Routes (API) → Service → CRUD → Database

Principios SOLID:
- Single Responsibility: Cada endpoint una responsabilidad
- Open/Closed: Extensible sin modificar existentes
- Liskov Substitution: Responses intercambiables
- Interface Segregation: Endpoints específicos
- Dependency Inversion: Depende de abstracciones (Service)

Author: Backend Team
Date: 2025-11-01
"""

from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

# Dependencies
from src.api.dependencies import get_current_user, get_db

# Enums
from src.enums.communication.videollamada_enums import (
    CalidadConexion,
)
from src.models.users.usuario import Usuario

# Pydantic Schemas
from src.schemas.communication.videollamada_schemas import (
    # Grabacion schemas
    GrabacionCreate,
    GrabacionResponse,
    # Generic response
    MessageResponse,
    # Participante schemas
    ParticipanteResponse,
    VideollamadaCreate,
    VideollamadaListResponse,
    VideollamadaResponse,
)

# Service Layer
from src.services.communication.videollamada_service import (
    ParticipanteError,
    VideollamadaNotFoundError,
    VideollamadaServiceError,
    VideollamadaStateError,
    videollamada_service,
)


# ===============================
# Router Configuration
# ===============================

router = APIRouter(prefix="/videollamadas", tags=["Videollamadas"])


# ===============================
# Helper Functions
# ===============================


def _handle_service_error(error: Exception) -> HTTPException:
    """Convierte errores del service layer a HTTPExceptions apropiadas.

    Args:
        error: Excepción del service layer

    Returns:
        HTTPException con status code y mensaje apropiados
    """
    if isinstance(error, VideollamadaNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, (VideollamadaStateError, ParticipanteError)):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    if isinstance(error, VideollamadaServiceError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error interno del servidor",
    )


def _verificar_permisos_moderador(
    videollamada: VideollamadaResponse, usuario_id: UUID
) -> None:
    """Verifica que el usuario tenga permisos de moderador.

    Args:
        videollamada: Response de videollamada
        usuario_id: ID del usuario

    Raises:
        HTTPException: 403 si no tiene permisos
    """
    # El iniciador siempre es moderador
    if videollamada.iniciador_id == usuario_id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos de moderador en esta videollamada",
    )


# ===============================
# Rutas Estáticas (DEBEN IR PRIMERO)
# ===============================


@router.get(
    "/health",
    response_model=MessageResponse,
    summary="Health check",
    description="Verifica que el módulo de videollamadas está operativo",
)
async def health_check() -> MessageResponse:
    """Health check endpoint."""
    return MessageResponse(
        success=True,
        message="Módulo de videollamadas operativo con service layer y enums",
    )


@router.get(
    "/room-name/generate",
    response_model=dict,
    summary="Generar room name único",
    description="""
    Genera un room name único para Jitsi Meet.

    Basado en un nombre base, agrega sufijo numérico si ya existe.

    **Permisos**: Usuario autenticado

    **Ejemplo Response**:
    ```json
    {
        "room_name": "sala-matematicas-2"
    }
    ```
    """,
)
async def generar_room_name(
    base_name: str = Query(..., description="Nombre base para la sala"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    """Genera room name único para Jitsi."""
    try:
        room_name = videollamada_service.obtener_room_name_disponible(
            db=db, base_name=base_name
        )
        return {"room_name": room_name}
    except VideollamadaServiceError as e:
        raise _handle_service_error(e) from e


# ===============================
# Endpoints de Videollamadas
# ===============================


@router.post(
    "/",
    response_model=VideollamadaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva videollamada",
    description="""
    Crea una nueva videollamada.

    - El usuario actual se convierte automáticamente en iniciador y moderador
    - Se genera un room_name único si no se especifica
    - Estado inicial: ACTIVA

    **Permisos**: Usuario autenticado

    **Ejemplo Request**:
    ```json
    {
        "sala_chat_id": "uuid",
        "tipo_llamada": "video",
        "titulo": "Reunión de equipo",
        "descripcion": "Planificación sprint"
    }
    ```
    """,
)
async def crear_videollamada(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    videollamada_in: VideollamadaCreate,
) -> VideollamadaResponse:
    """Crea nueva videollamada con el usuario actual como iniciador."""
    try:
        return videollamada_service.crear_videollamada(
            db=db, videollamada_in=videollamada_in, iniciador_id=current_user.id
        )
    except VideollamadaServiceError as e:
        raise _handle_service_error(e) from e


@router.get(
    "/{videollamada_id}",
    response_model=VideollamadaResponse,
    summary="Obtener videollamada por ID",
    description="""
    Obtiene información de una videollamada específica.

    **Permisos**: Usuario autenticado
    """,
)
async def obtener_videollamada(
    videollamada_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    incluir_participantes: bool = Query(
        False, description="Incluir lista de participantes"
    ),
) -> VideollamadaResponse:
    """Obtiene videollamada por ID."""
    try:
        return videollamada_service.obtener_videollamada(
            db=db,
            videollamada_id=videollamada_id,
            incluir_participantes=incluir_participantes,
        )
    except VideollamadaNotFoundError as e:
        raise _handle_service_error(e) from e


@router.get(
    "/",
    response_model=VideollamadaListResponse,
    summary="Listar videollamadas",
    description="""
    Lista videollamadas con paginación.

    Filtros opcionales:
    - sala_chat_id: Filtrar por sala de chat
    - solo_activas: Solo videollamadas en estado ACTIVA

    **Permisos**: Usuario autenticado
    """,
)
async def listar_videollamadas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    sala_chat_id: UUID | None = Query(None, description="Filtrar por sala"),
    solo_activas: bool = Query(True, description="Solo videollamadas activas"),
    skip: int = Query(0, ge=0, description="Items a saltar"),
    limit: int = Query(50, ge=1, le=100, description="Items por página"),
) -> VideollamadaListResponse:
    """Lista videollamadas con filtros."""
    try:
        if solo_activas:
            videollamadas = videollamada_service.listar_videollamadas_activas(
                db=db, skip=skip, limit=limit
            )
        elif sala_chat_id:
            videollamadas = videollamada_service.listar_videollamadas_por_sala_chat(
                db=db,
                sala_chat_id=sala_chat_id,
                incluir_finalizadas=not solo_activas,
                skip=skip,
                limit=limit,
            )
        else:
            # Por defecto, listar activas
            videollamadas = videollamada_service.listar_videollamadas_activas(
                db=db, skip=skip, limit=limit
            )

        return VideollamadaListResponse(
            items=videollamadas,
            total=len(videollamadas),
            skip=skip,
            limit=limit,
            has_more=len(videollamadas) == limit,
        )
    except VideollamadaServiceError as e:
        raise _handle_service_error(e) from e


# ===============================
# Endpoints de Participantes
# ===============================


@router.post(
    "/{videollamada_id}/join",
    response_model=ParticipanteResponse,
    summary="Unirse a videollamada",
    description="""
    Permite a un usuario unirse a una videollamada existente.

    Validaciones automáticas:
    - Videollamada debe estar en estado ACTIVA
    - No puede unirse si ya es participante activo
    - Respeta límite máximo de participantes

    **Permisos**: Usuario autenticado

    **Ejemplo Request**:
    ```json
    {
        "es_moderador": false
    }
    ```
    """,
)
async def unirse_a_videollamada(
    videollamada_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    es_moderador: bool = Body(False, embed=True),
) -> ParticipanteResponse:
    """Usuario se une a videollamada existente."""
    try:
        return videollamada_service.unirse_a_videollamada(
            db=db,
            videollamada_id=videollamada_id,
            usuario_id=current_user.id,
            es_moderador=es_moderador,
        )
    except (VideollamadaNotFoundError, VideollamadaStateError, ParticipanteError) as e:
        raise _handle_service_error(e) from None


@router.post(
    "/{videollamada_id}/leave",
    response_model=MessageResponse,
    summary="Salir de videollamada",
    description="""
    Marca salida del usuario de una videollamada.

    - Registra fecha_salida
    - Calcula duración automáticamente

    **Permisos**: Usuario autenticado participante
    """,
)
async def salir_de_videollamada(
    videollamada_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> MessageResponse:
    """Usuario sale de videollamada."""
    try:
        videollamada_service.salir_de_videollamada(
            db=db, videollamada_id=videollamada_id, usuario_id=current_user.id
        )
        return MessageResponse(
            success=True, message="Has salido de la videollamada exitosamente"
        )
    except (VideollamadaNotFoundError, ParticipanteError) as e:
        raise _handle_service_error(e) from None


@router.get(
    "/{videollamada_id}/participants",
    response_model=list[ParticipanteResponse],
    summary="Listar participantes activos",
    description="""
    Obtiene lista de participantes actualmente conectados.

    **Permisos**: Usuario autenticado
    """,
)
async def obtener_participantes_activos(
    videollamada_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[ParticipanteResponse]:
    """Lista participantes activos de videollamada."""
    try:
        return videollamada_service.obtener_participantes_activos(
            db=db, videollamada_id=videollamada_id
        )
    except VideollamadaNotFoundError as e:
        raise _handle_service_error(e) from e


@router.patch(
    "/participants/{participante_id}/quality",
    response_model=ParticipanteResponse,
    summary="Actualizar calidad de conexión",
    description="""
    Actualiza calidad de conexión de un participante.

    Puede especificar:
    - calidad directamente (EXCELENTE, BUENA, REGULAR, MALA)
    - O métricas (latencia_ms, perdida_paquetes_pct) para cálculo automático

    **Permisos**: Usuario autenticado (propio participante)

    **Ejemplo Request con métricas**:
    ```json
    {
        "latencia_ms": 45,
        "perdida_paquetes_pct": 0.8
    }
    ```

    **Ejemplo Request con calidad directa**:
    ```json
    {
        "calidad": "buena"
    }
    ```
    """,
)
async def actualizar_calidad_conexion(
    participante_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    calidad: CalidadConexion | None = Body(None),
    latencia_ms: int | None = Body(None),
    perdida_paquetes_pct: float | None = Body(None),
) -> ParticipanteResponse:
    """Actualiza calidad de conexión con cálculo automático desde métricas."""
    try:
        return videollamada_service.actualizar_calidad_conexion(
            db=db,
            participante_id=participante_id,
            calidad=calidad,
            latencia_ms=latencia_ms,
            perdida_paquetes_pct=perdida_paquetes_pct,
        )
    except ParticipanteError as e:
        raise _handle_service_error(e) from e


# ===============================
# Endpoints de Control
# ===============================


@router.post(
    "/{videollamada_id}/finalize",
    response_model=VideollamadaResponse,
    summary="Finalizar videollamada",
    description="""
    Finaliza una videollamada activa.

    Validaciones:
    - Solo puede finalizar desde estado ACTIVA o PROGRAMADA
    - Usa método puede_transicionar_a() del enum
    - Solo moderador puede finalizar

    **Permisos**: Usuario autenticado moderador

    **Ejemplo Request**:
    ```json
    {
        "resumen_ia": "Reunión sobre planificación Q4..."
    }
    ```
    """,
)
async def finalizar_videollamada(
    videollamada_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    resumen_ia: str | None = Body(None, embed=True),
) -> VideollamadaResponse:
    """Finaliza videollamada validando transición de estado."""
    try:
        # Verificar permisos
        videollamada_actual = videollamada_service.obtener_videollamada(
            db=db, videollamada_id=videollamada_id
        )
        _verificar_permisos_moderador(videollamada_actual, current_user.id)

        # Finalizar
        return videollamada_service.finalizar_videollamada(
            db=db, videollamada_id=videollamada_id, resumen_ia=resumen_ia
        )
    except (VideollamadaNotFoundError, VideollamadaStateError) as e:
        raise _handle_service_error(e) from None


@router.post(
    "/{videollamada_id}/cancel",
    response_model=VideollamadaResponse,
    summary="Cancelar videollamada",
    description="""
    Cancela una videollamada programada o activa.

    Validaciones:
    - Usa método puede_transicionar_a() del enum
    - Solo moderador puede cancelar
    - Desconecta todos los participantes activos

    **Permisos**: Usuario autenticado moderador
    """,
)
async def cancelar_videollamada(
    videollamada_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> VideollamadaResponse:
    """Cancela videollamada validando transición de estado."""
    try:
        # Verificar permisos
        videollamada_actual = videollamada_service.obtener_videollamada(
            db=db, videollamada_id=videollamada_id
        )
        _verificar_permisos_moderador(videollamada_actual, current_user.id)

        # Cancelar
        return videollamada_service.cancelar_videollamada(
            db=db, videollamada_id=videollamada_id
        )
    except (VideollamadaNotFoundError, VideollamadaStateError) as e:
        raise _handle_service_error(e) from None


# ===============================
# Endpoints de Grabaciones
# ===============================


@router.post(
    "/{videollamada_id}/recordings",
    response_model=GrabacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar grabación",
    description="""
    Registra nueva grabación de videollamada.

    La primera grabación agregada se marca automáticamente como primaria.

    **Permisos**: Usuario autenticado moderador

    **Ejemplo Request**:
    ```json
    {
        "archivo_url": "https://cdn.example.com/rec_123.mp4",
        "formato": "mp4",
        "calidad": "FHD",
        "duracion_segundos": 3600,
        "tamano_bytes": 524288000
    }
    ```
    """,
)
async def agregar_grabacion(
    videollamada_id: UUID,
    grabacion_in: GrabacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> GrabacionResponse:
    """Agrega grabación a videollamada."""
    try:
        # Verificar permisos
        videollamada = videollamada_service.obtener_videollamada(
            db=db, videollamada_id=videollamada_id
        )
        _verificar_permisos_moderador(videollamada, current_user.id)

        # Agregar grabación
        return videollamada_service.agregar_grabacion(
            db=db, videollamada_id=videollamada_id, grabacion_in=grabacion_in
        )
    except VideollamadaNotFoundError as e:
        raise _handle_service_error(e) from e


@router.get(
    "/{videollamada_id}/recordings",
    response_model=list[GrabacionResponse],
    summary="Listar grabaciones",
    description="""
    Obtiene todas las grabaciones de una videollamada.

    Incluye información de formato, calidad y estado de procesamiento.

    **Permisos**: Usuario autenticado
    """,
)
async def obtener_grabaciones(
    videollamada_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[GrabacionResponse]:
    """Lista grabaciones de videollamada."""
    try:
        return videollamada_service.obtener_grabaciones(
            db=db, videollamada_id=videollamada_id
        )
    except VideollamadaNotFoundError as e:
        raise _handle_service_error(e) from e


# ===============================
# Endpoints de Transcripción
# ===============================


@router.patch(
    "/{videollamada_id}/transcription",
    response_model=VideollamadaResponse,
    summary="Actualizar transcripción",
    description="""
    Actualiza o agrega transcripción de videollamada.

    Usado por sistemas de transcripción AI.

    **Permisos**: Usuario autenticado moderador

    **Ejemplo Request**:
    ```json
    {
        "transcripcion": "John Doe: Buenos días a todos..."
    }
    ```
    """,
)
async def actualizar_transcripcion(
    videollamada_id: UUID,
    transcripcion: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> VideollamadaResponse:
    """Actualiza transcripción de videollamada."""
    try:
        # Verificar permisos
        videollamada_actual = videollamada_service.obtener_videollamada(
            db=db, videollamada_id=videollamada_id
        )
        _verificar_permisos_moderador(videollamada_actual, current_user.id)

        # Actualizar transcripción
        return videollamada_service.actualizar_transcripcion(
            db=db, videollamada_id=videollamada_id, transcripcion=transcripcion
        )
    except VideollamadaNotFoundError as e:
        raise _handle_service_error(e) from e


# ===============================
# Utilidades con parámetros
# ===============================


@router.post(
    "/{videollamada_id}/validate-join",
    response_model=dict,
    summary="Validar si puede unirse",
    description="""
    Valida si un usuario puede unirse a una videollamada.

    Verifica:
    - Estado de la videollamada
    - Límite de participantes
    - Si ya está unido

    **Permisos**: Usuario autenticado

    **Ejemplo Response**:
    ```json
    {
        "can_join": true,
        "reason": null,
        "current_participants": 5,
        "max_participants": 50
    }
    ```
    """,
)
async def validar_puede_unirse(
    videollamada_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    """Valida si usuario puede unirse a videollamada."""
    try:
        return videollamada_service.validar_puede_unirse(
            db=db, videollamada_id=videollamada_id, usuario_id=current_user.id
        )
    except VideollamadaNotFoundError as e:
        raise _handle_service_error(e) from e


# ===============================
# Exports
# ===============================

__all__ = ["router"]
