"""API Routes para el sistema de comunicación y chat
Endpoints para salas, mensajes, notificaciones y WebSocket.
"""

from uuid import UUID

from src.api.dependencies import get_current_user, get_db
from src.crud.communication.chat import (
    crud_config_notificaciones,
    crud_lectura_mensaje,
    crud_mensaje,
    crud_notificacion,
    crud_participante_sala,
    crud_sala_chat,
)
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, status
from src.models.communication.chat import EstadoMensaje
from src.models.users import Usuario
from src.schemas.communication.chat_schemas import (
    ConfiguracionNotificacionesResponse,
    # Configuración
    ConfiguracionNotificacionesUpdate,
    # Estadísticas
    EstadisticasSala,
    EstadisticasUsuario,
    FiltrosMensajes,
    FiltrosNotificaciones,
    # Filtros
    FiltrosSalas,
    MarcarLectura,
    MarcarNotificacionLeida,
    # Mensajes
    MensajeCreate,
    MensajeDetallado,
    MensajeResponse,
    MensajeUpdate,
    # Notificaciones
    NotificacionResponse,
    # Participantes
    ParticipanteSalaCreate,
    ParticipanteSalaResponse,
    ParticipanteSalaUpdate,
    ReaccionMensaje,
    # Salas
    SalaChatCreate,
    SalaChatDetallada,
    SalaChatResponse,
    SalaChatUpdate,
)
from services.websocket_manager import websocket_endpoint
from sqlalchemy.orm import Session

router = APIRouter(prefix="/communication", tags=["Comunicación"])


# ==================== WEBSOCKET ====================


@router.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    token: str | None = Query(None),
    usuario_id: str | None = Query(None),
    sala_id: str | None = Query(None),
    db: Session = Depends(get_db),
) -> None:
    """Endpoint WebSocket para comunicación en tiempo real."""
    await websocket_endpoint(websocket, usuario_id, sala_id, token, db)


# ==================== SALAS DE CHAT ====================


@router.post("/salas", response_model=SalaChatResponse)
async def crear_sala(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    sala_in: SalaChatCreate,
) -> SalaChatResponse:
    """Crear nueva sala de chat."""
    sala = crud_sala_chat.create_with_creator(
        db=db, obj_in=sala_in, creador_id=str(current_user.id)
    )
    return SalaChatResponse.from_orm(sala)


@router.get("/salas", response_model=list[SalaChatResponse])
async def listar_salas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    tipo_sala: str | None = None,
    es_publica: bool | None = None,
    curso_id: UUID | None = None,
    grupo_id: UUID | None = None,
    buscar: str | None = None,
    solo_participando: bool = True,
    incluir_archivadas: bool = False,
    ordenar_por: str = "ultimo_mensaje_fecha",
    orden_desc: bool = True,
    limite: int = 50,
    offset: int = 0,
) -> list[SalaChatResponse]:
    """Obtener salas donde participa el usuario."""
    filtros = FiltrosSalas(
        tipo_sala=tipo_sala,
        es_publica=es_publica,
        curso_id=curso_id,
        grupo_id=grupo_id,
        buscar=buscar,
        solo_participando=solo_participando,
        incluir_archivadas=incluir_archivadas,
        ordenar_por=ordenar_por,
        orden_desc=orden_desc,
        limite=limite,
        offset=offset,
    )

    salas = crud_sala_chat.get_salas_usuario(
        db=db, usuario_id=str(current_user.id), filtros=filtros
    )

    return [SalaChatResponse.from_orm(sala) for sala in salas]


@router.get("/salas/{sala_id}", response_model=SalaChatDetallada)
async def obtener_sala(
    sala_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> SalaChatDetallada:
    """Obtener detalles completos de una sala."""
    sala = crud_sala_chat.get_sala_detallada(
        db=db, sala_id=str(sala_id), usuario_id=str(current_user.id)
    )

    if not sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala no encontrada o sin acceso",
        )

    return SalaChatDetallada.from_orm(sala)


@router.put("/salas/{sala_id}", response_model=SalaChatResponse)
async def actualizar_sala(
    sala_id: UUID,
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    sala_in: SalaChatUpdate,
) -> SalaChatResponse:
    """Actualizar sala de chat."""
    # Verificar permisos (admin o creador)
    participante = crud_participante_sala.get_participante(
        db=db, sala_id=str(sala_id), usuario_id=str(current_user.id)
    )

    if not participante or not participante.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar esta sala",
        )

    sala = crud_sala_chat.get(db=db, id=str(sala_id))
    if not sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sala no encontrada"
        )

    sala = crud_sala_chat.update(db=db, db_obj=sala, obj_in=sala_in)
    return SalaChatResponse.from_orm(sala)


@router.delete("/salas/{sala_id}")
async def eliminar_sala(
    sala_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Eliminar sala de chat."""
    sala = crud_sala_chat.get(db=db, id=str(sala_id))
    if not sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sala no encontrada"
        )

    # Solo el creador puede eliminar
    if sala.creador_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el creador puede eliminar la sala",
        )

    crud_sala_chat.remove(db=db, id=str(sala_id))
    return {"message": "Sala eliminada exitosamente"}


@router.get("/salas/{sala_id}/estadisticas", response_model=EstadisticasSala)
async def obtener_estadisticas_sala(
    sala_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> EstadisticasSala:
    """Obtener estadísticas de una sala."""
    # Verificar acceso
    participante = crud_participante_sala.get_participante(
        db=db, sala_id=str(sala_id), usuario_id=str(current_user.id)
    )

    if not participante:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta sala"
        )

    estadisticas = crud_sala_chat.get_estadisticas_sala(db=db, sala_id=str(sala_id))
    return EstadisticasSala(**estadisticas)


# ==================== PARTICIPANTES ====================


@router.get(
    "/salas/{sala_id}/participantes", response_model=list[ParticipanteSalaResponse]
)
async def listar_participantes(
    sala_id: UUID,
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[ParticipanteSalaResponse]:
    """Obtener participantes de una sala."""
    # Verificar acceso
    participante = crud_participante_sala.get_participante(
        db=db, sala_id=str(sala_id), usuario_id=str(current_user.id)
    )

    if not participante:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta sala"
        )

    participantes = crud_participante_sala.get_participantes_sala(
        db=db, sala_id=str(sala_id), incluir_inactivos=incluir_inactivos
    )

    return [ParticipanteSalaResponse.from_orm(p) for p in participantes]


@router.post("/salas/{sala_id}/participantes", response_model=ParticipanteSalaResponse)
async def agregar_participante(
    sala_id: UUID,
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    participante_in: ParticipanteSalaCreate,
) -> ParticipanteSalaResponse:
    """Agregar participante a sala."""
    # Verificar permisos (admin o moderador)
    mi_participacion = crud_participante_sala.get_participante(
        db=db, sala_id=str(sala_id), usuario_id=str(current_user.id)
    )

    if not mi_participacion or not (
        mi_participacion.es_admin or mi_participacion.es_moderador
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para agregar participantes",
        )

    participante_in.sala_id = sala_id
    participante = crud_participante_sala.create(db=db, obj_in=participante_in)
    return ParticipanteSalaResponse.from_orm(participante)


@router.put(
    "/salas/{sala_id}/participantes/{usuario_id}",
    response_model=ParticipanteSalaResponse,
)
async def actualizar_participante(
    sala_id: UUID,
    usuario_id: UUID,
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    participante_in: ParticipanteSalaUpdate,
) -> ParticipanteSalaResponse:
    """Actualizar participante de sala."""
    # Verificar permisos
    mi_participacion = crud_participante_sala.get_participante(
        db=db, sala_id=str(sala_id), usuario_id=str(current_user.id)
    )

    if not mi_participacion or not mi_participacion.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar participantes",
        )

    participante = crud_participante_sala.get_participante(
        db=db, sala_id=str(sala_id), usuario_id=str(usuario_id)
    )

    if not participante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participante no encontrado"
        )

    participante = crud_participante_sala.update(
        db=db, db_obj=participante, obj_in=participante_in
    )
    return ParticipanteSalaResponse.from_orm(participante)


@router.delete("/salas/{sala_id}/participantes/{usuario_id}")
async def remover_participante(
    sala_id: UUID,
    usuario_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Remover participante de sala."""
    # Verificar permisos o si es el mismo usuario
    mi_participacion = crud_participante_sala.get_participante(
        db=db, sala_id=str(sala_id), usuario_id=str(current_user.id)
    )

    puede_remover = (mi_participacion and mi_participacion.es_admin) or str(
        current_user.id
    ) == str(usuario_id)

    if not puede_remover:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para remover este participante",
        )

    participante = crud_participante_sala.get_participante(
        db=db, sala_id=str(sala_id), usuario_id=str(usuario_id)
    )

    if not participante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participante no encontrado"
        )

    # Marcar como inactivo en lugar de eliminar
    participante.esta_activo = False
    db.commit()

    return {"message": "Participante removido exitosamente"}


# ==================== MENSAJES ====================


@router.post("/mensajes", response_model=MensajeResponse)
async def enviar_mensaje(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    mensaje_in: MensajeCreate,
) -> MensajeResponse:
    """Enviar nuevo mensaje (REST endpoint, también disponible via WebSocket)."""
    # Verificar permisos
    participante = crud_participante_sala.get_participante(
        db=db, sala_id=str(mensaje_in.sala_id), usuario_id=str(current_user.id)
    )

    if not participante or not participante.puede_escribir:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para escribir en esta sala",
        )

    mensaje = crud_mensaje.create_mensaje(
        db=db, obj_in=mensaje_in, usuario_id=str(current_user.id)
    )

    return MensajeResponse.from_orm(mensaje)


@router.get("/salas/{sala_id}/mensajes", response_model=list[MensajeResponse])
async def listar_mensajes(
    sala_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    usuario_id: UUID | None = None,
    tipo_mensaje: str | None = None,
    solo_importantes: bool | None = None,
    solo_anuncios: bool | None = None,
    con_archivos: bool | None = None,
    menciona_usuario: UUID | None = None,
    menciona_ia: bool | None = None,
    buscar: str | None = None,
    solo_no_leidos: bool = False,
    incluir_hilos: bool = True,
    ordenar_por: str = "fecha_creacion",
    orden_desc: bool = True,
    limite: int = 50,
    offset: int = 0,
) -> list[MensajeResponse]:
    """Obtener mensajes de una sala."""
    filtros = FiltrosMensajes(
        usuario_id=usuario_id,
        tipo_mensaje=tipo_mensaje,
        solo_importantes=solo_importantes,
        solo_anuncios=solo_anuncios,
        con_archivos=con_archivos,
        menciona_usuario=menciona_usuario,
        menciona_ia=menciona_ia,
        buscar=buscar,
        solo_no_leidos=solo_no_leidos,
        incluir_hilos=incluir_hilos,
        ordenar_por=ordenar_por,
        orden_desc=orden_desc,
        limite=limite,
        offset=offset,
    )

    mensajes = crud_mensaje.get_mensajes_sala(
        db=db, sala_id=str(sala_id), usuario_id=str(current_user.id), filtros=filtros
    )

    return [MensajeResponse.from_orm(m) for m in mensajes]


@router.get("/mensajes/{mensaje_id}", response_model=MensajeDetallado)
async def obtener_mensaje(
    mensaje_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> MensajeDetallado:
    """Obtener mensaje con hilo de respuestas."""
    mensaje = crud_mensaje.get_mensaje_con_hilo(
        db=db, mensaje_id=str(mensaje_id), usuario_id=str(current_user.id)
    )

    if not mensaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado o sin acceso",
        )

    return MensajeDetallado.from_orm(mensaje)


@router.put("/mensajes/{mensaje_id}", response_model=MensajeResponse)
async def actualizar_mensaje(
    mensaje_id: UUID,
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    mensaje_in: MensajeUpdate,
) -> MensajeResponse:
    """Actualizar mensaje (solo el autor puede editarlo)."""
    mensaje = crud_mensaje.get(db=db, id=str(mensaje_id))

    if not mensaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mensaje no encontrado"
        )

    if mensaje.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes editar tus propios mensajes",
        )

    mensaje = crud_mensaje.update(db=db, db_obj=mensaje, obj_in=mensaje_in)
    return MensajeResponse.from_orm(mensaje)


@router.delete("/mensajes/{mensaje_id}")
async def eliminar_mensaje(
    mensaje_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Eliminar mensaje (marcar como eliminado)."""
    mensaje = crud_mensaje.get(db=db, id=str(mensaje_id))

    if not mensaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mensaje no encontrado"
        )

    # Verificar permisos (autor o admin de sala)
    puede_eliminar = mensaje.usuario_id == current_user.id

    if not puede_eliminar:
        participante = crud_participante_sala.get_participante(
            db=db, sala_id=str(mensaje.sala_id), usuario_id=str(current_user.id)
        )
        puede_eliminar = participante and participante.es_admin

    if not puede_eliminar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este mensaje",
        )

    # Marcar como eliminado en lugar de eliminar físicamente
    mensaje.estado = EstadoMensaje.ELIMINADO
    mensaje.contenido = "[Mensaje eliminado]"
    mensaje.contenido_html = "<em>[Mensaje eliminado]</em>"
    db.commit()

    return {"message": "Mensaje eliminado exitosamente"}


@router.post("/mensajes/{mensaje_id}/reaccion")
async def agregar_reaccion(
    mensaje_id: UUID,
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    reaccion: ReaccionMensaje,
):
    """Agregar reacción a mensaje."""
    success = crud_mensaje.agregar_reaccion(
        db=db,
        mensaje_id=str(mensaje_id),
        usuario_id=str(current_user.id),
        emoji=reaccion.emoji,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mensaje no encontrado"
        )

    return {"message": "Reacción agregada exitosamente"}


# ==================== LECTURAS ====================


@router.post("/mensajes/marcar-leido")
async def marcar_mensajes_leidos(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    lectura: MarcarLectura,
):
    """Marcar mensajes como leídos."""
    if lectura.sala_id:
        # Marcar toda la sala como leída
        count = crud_lectura_mensaje.marcar_mensajes_sala_leidos(
            db=db, sala_id=str(lectura.sala_id), usuario_id=str(current_user.id)
        )
        return {"message": f"{count} mensajes marcados como leídos"}

    if lectura.mensajes_ids:
        # Marcar mensajes específicos
        count = 0
        for mensaje_id in lectura.mensajes_ids:
            crud_lectura_mensaje.marcar_como_leido(
                db=db, mensaje_id=str(mensaje_id), usuario_id=str(current_user.id)
            )
            count += 1

        return {"message": f"{count} mensajes marcados como leídos"}

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Debe especificar sala_id o mensajes_ids",
    )


# ==================== NOTIFICACIONES ====================


@router.get("/notificaciones", response_model=list[NotificacionResponse])
async def listar_notificaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    tipo_notificacion: str | None = None,
    solo_no_leidas: bool = False,
    ordenar_por: str = "fecha_creacion",
    orden_desc: bool = True,
    limite: int = 20,
    offset: int = 0,
) -> list[NotificacionResponse]:
    """Obtener notificaciones del usuario."""
    filtros = FiltrosNotificaciones(
        tipo_notificacion=tipo_notificacion,
        solo_no_leidas=solo_no_leidas,
        ordenar_por=ordenar_por,
        orden_desc=orden_desc,
        limite=limite,
        offset=offset,
    )

    notificaciones = crud_notificacion.get_notificaciones_usuario(
        db=db, usuario_id=str(current_user.id), filtros=filtros
    )

    return [NotificacionResponse.from_orm(n) for n in notificaciones]


@router.post("/notificaciones/marcar-leidas")
async def marcar_notificaciones_leidas(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    notificaciones: MarcarNotificacionLeida,
):
    """Marcar notificaciones como leídas."""
    count = 0
    for notif_id in notificaciones.notificaciones_ids:
        if crud_notificacion.marcar_como_leida(
            db=db, notificacion_id=str(notif_id), usuario_id=str(current_user.id)
        ):
            count += 1

    return {"message": f"{count} notificaciones marcadas como leídas"}


@router.post("/notificaciones/marcar-todas-leidas")
async def marcar_todas_notificaciones_leidas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    tipo_notificacion: str | None = None,
):
    """Marcar todas las notificaciones como leídas."""
    count = crud_notificacion.marcar_todas_leidas(
        db=db, usuario_id=str(current_user.id), tipo_notificacion=tipo_notificacion
    )

    return {"message": f"{count} notificaciones marcadas como leídas"}


@router.get("/notificaciones/count")
async def contar_notificaciones_no_leidas(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    """Obtener cantidad de notificaciones no leídas."""
    count = crud_notificacion.get_count_no_leidas(
        db=db, usuario_id=str(current_user.id)
    )

    return {"count": count}


# ==================== CONFIGURACIÓN ====================


@router.get(
    "/configuracion/notificaciones", response_model=ConfiguracionNotificacionesResponse
)
async def obtener_configuracion_notificaciones(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
) -> ConfiguracionNotificacionesResponse:
    """Obtener configuración de notificaciones del usuario."""
    config = crud_config_notificaciones.get_by_usuario(
        db=db, usuario_id=str(current_user.id)
    )

    return ConfiguracionNotificacionesResponse.from_orm(config)


@router.put(
    "/configuracion/notificaciones", response_model=ConfiguracionNotificacionesResponse
)
async def actualizar_configuracion_notificaciones(
    *,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    config_in: ConfiguracionNotificacionesUpdate,
) -> ConfiguracionNotificacionesResponse:
    """Actualizar configuración de notificaciones."""
    config = crud_config_notificaciones.update_by_usuario(
        db=db, usuario_id=str(current_user.id), obj_in=config_in
    )

    return ConfiguracionNotificacionesResponse.from_orm(config)


# ==================== ESTADÍSTICAS ====================


@router.get("/estadisticas/usuario", response_model=EstadisticasUsuario)
async def obtener_estadisticas_usuario(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
) -> EstadisticasUsuario:
    """Obtener estadísticas de comunicación del usuario."""
    # TODO: Implementar estadísticas detalladas
    return EstadisticasUsuario(
        mensajes_enviados=0,
        salas_participando=0,
        menciones_recibidas=0,
        reacciones_recibidas=0,
    )
