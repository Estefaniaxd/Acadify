"""
Chat WebSocket Endpoint
=======================
WebSocket endpoint específico para chat en tiempo real.

Eventos soportados:
- message.new: Nuevo mensaje
- message.edit: Editar mensaje
- message.delete: Eliminar mensaje
- message.reaction: Añadir reacción
- typing.start: Usuario comenzó a escribir
- typing.stop: Usuario dejó de escribir
- read.receipt: Confirmación de lectura

Principios SOLID:
- Single Responsibility: Solo maneja WebSocket de chat
- Open/Closed: Extensible para nuevos eventos
- Liskov Substitution: Implementa contrato de WebSocket
- Interface Segregation: Eventos específicos de chat
- Dependency Inversion: Depende de abstracciones (CRUD, manager)
"""

import json
import logging
from datetime import datetime, UTC
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user_websocket
from src.api.deps import get_db
from src.models.users.usuario import Usuario
from src.models.communication.chat import TipoMensaje
from src.crud.communication.chat import (
    crud_mensaje,
    crud_participante_sala,
    crud_lectura_mensaje,
    crud_sala_chat,
)
from src.schemas.communication.chat_schemas import MensajeCreate, MensajeUpdate
from src.services.websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatWebSocketHandler:
    """
    Manejador específico de eventos WebSocket para chat.
    
    Responsabilidad: Procesar eventos de chat y coordinar con el ConnectionManager.
    """
    
    def __init__(self, db: Session, usuario: Usuario, sala_id: str):
        self.db = db
        self.usuario = usuario
        self.sala_id = sala_id
        
        # Validar acceso a la sala
        self.participante = crud_participante_sala.get_participante(
            self.db,
            sala_id=sala_id,
            usuario_id=str(usuario.id)
        )
        
        if not self.participante:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a esta sala de chat"
            )
    
    async def handle_event(self, event_type: str, data: dict) -> dict:
        """
        Procesa un evento recibido del cliente.
        
        Args:
            event_type: Tipo de evento (message.new, typing.start, etc.)
            data: Datos del evento
            
        Returns:
            Respuesta para el cliente (puede ser None para broadcast only)
        """
        try:
            # Router de eventos
            if event_type == "message.new":
                return await self._handle_new_message(data)
            
            elif event_type == "message.edit":
                return await self._handle_edit_message(data)
            
            elif event_type == "message.delete":
                return await self._handle_delete_message(data)
            
            elif event_type == "message.reaction":
                return await self._handle_reaction(data)
            
            elif event_type == "typing.start":
                return await self._handle_typing_start()
            
            elif event_type == "typing.stop":
                return await self._handle_typing_stop()
            
            elif event_type == "read.receipt":
                return await self._handle_read_receipt(data)
            
            elif event_type == "get.online_users":
                return await self._handle_get_online_users()
            
            elif event_type == "get.typing_users":
                return await self._handle_get_typing_users()
            
            else:
                logger.warning(f"⚠️ Evento no reconocido: {event_type}")
                return {
                    "type": "error",
                    "error": "unknown_event",
                    "message": f"Tipo de evento no reconocido: {event_type}"
                }
        
        except HTTPException as he:
            logger.error(f"❌ HTTP Error en evento {event_type}: {he.detail}")
            return {
                "type": "error",
                "error": "http_error",
                "message": he.detail,
                "status_code": he.status_code
            }
        
        except Exception as e:
            logger.exception(f"❌ Error procesando evento {event_type}: {str(e)}")
            return {
                "type": "error",
                "error": "internal_error",
                "message": f"Error interno procesando {event_type}"
            }
    
    async def _handle_new_message(self, data: dict) -> dict:
        """Maneja el envío de un nuevo mensaje."""
        
        # Validar permisos de escritura
        if not self.participante.puede_escribir:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para escribir en esta sala"
            )
        
        # Crear mensaje
        mensaje_data = MensajeCreate(
            sala_id=self.sala_id,
            contenido=data.get("contenido", ""),
            tipo_mensaje=TipoMensaje(data.get("tipo_mensaje", "texto")),
            mensaje_padre_id=data.get("mensaje_padre_id"),
            archivos_urls=data.get("archivos_urls", []),
            metadatos_archivos=data.get("metadatos_archivos", {}),
            menciones_usuarios=data.get("menciones_usuarios", []),
            menciones_ia=data.get("menciones_ia", False),
            menciones_todos=data.get("menciones_todos", False),
            es_importante=data.get("es_importante", False),
            es_anuncio=data.get("es_anuncio", False),
        )
        
        # Guardar en base de datos
        mensaje = crud_mensaje.create_mensaje(
            self.db,
            obj_in=mensaje_data,
            usuario_id=str(self.usuario.id)
        )
        
        # Preparar mensaje para broadcast
        broadcast_data = {
            "type": "message.new",
            "sala_id": self.sala_id,
            "mensaje": {
                "id": str(mensaje.id),
                "sala_id": str(mensaje.sala_id),
                "usuario_id": str(mensaje.usuario_id),
                "usuario_nombre": self.usuario.nombre,
                "usuario_apellido": self.usuario.apellido,
                "usuario_avatar": getattr(self.usuario, "avatar_url", None),
                "contenido": mensaje.contenido,
                "contenido_html": mensaje.contenido_html,
                "tipo_mensaje": mensaje.tipo_mensaje.value,
                "archivos_urls": mensaje.archivos_urls,
                "metadatos_archivos": mensaje.metadatos_archivos,
                "mensaje_padre_id": str(mensaje.mensaje_padre_id) if mensaje.mensaje_padre_id else None,
                "menciones_usuarios": mensaje.menciones_usuarios,
                "menciones_ia": mensaje.menciona_ia,
                "menciones_todos": mensaje.menciones_todos,
                "es_importante": mensaje.es_importante,
                "es_anuncio": mensaje.es_anuncio,
                "fecha_creacion": mensaje.fecha_creacion.isoformat(),
                "editado": mensaje.editado,
                "eliminado": mensaje.eliminado,
            },
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        # Broadcast a toda la sala
        await manager.broadcast_to_sala(self.sala_id, broadcast_data)
        
        logger.info(
            f"✅ Mensaje enviado: usuario={self.usuario.id}, "
            f"sala={self.sala_id}, mensaje_id={mensaje.id}"
        )
        
        # Procesar menciones de IA si es necesario
        if mensaje.menciona_ia:
            # TODO: Integrar con servicio de IA (Rutilio)
            logger.info(f"🤖 Mención a IA detectada en mensaje {mensaje.id}")
        
        # Retornar confirmación al emisor
        return {
            "type": "message.sent",
            "mensaje_id": str(mensaje.id),
            "timestamp": mensaje.fecha_creacion.isoformat()
        }
    
    async def _handle_edit_message(self, data: dict) -> dict:
        """Maneja la edición de un mensaje existente."""
        
        mensaje_id = data.get("mensaje_id")
        nuevo_contenido = data.get("contenido")
        
        if not mensaje_id or not nuevo_contenido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="mensaje_id y contenido son requeridos"
            )
        
        # Obtener mensaje
        mensaje = crud_mensaje.get(self.db, id=mensaje_id)
        
        if not mensaje:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensaje no encontrado"
            )
        
        # Validar que el usuario sea el autor
        if str(mensaje.usuario_id) != str(self.usuario.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes editar tus propios mensajes"
            )
        
        # Validar que el mensaje no esté eliminado
        if mensaje.eliminado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes editar un mensaje eliminado"
            )
        
        # Actualizar mensaje
        mensaje_update = MensajeUpdate(contenido=nuevo_contenido)
        mensaje_actualizado = crud_mensaje.update(
            self.db,
            db_obj=mensaje,
            obj_in=mensaje_update
        )
        
        # Broadcast actualización
        broadcast_data = {
            "type": "message.edit",
            "sala_id": self.sala_id,
            "mensaje_id": str(mensaje_id),
            "contenido": mensaje_actualizado.contenido,
            "contenido_html": mensaje_actualizado.contenido_html,
            "fecha_edicion": mensaje_actualizado.fecha_edicion.isoformat(),
            "editado": True,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        await manager.broadcast_to_sala(self.sala_id, broadcast_data)
        
        logger.info(f"✏️ Mensaje editado: mensaje_id={mensaje_id}")
        
        return {
            "type": "message.edited",
            "mensaje_id": str(mensaje_id),
            "timestamp": mensaje_actualizado.fecha_edicion.isoformat()
        }
    
    async def _handle_delete_message(self, data: dict) -> dict:
        """Maneja la eliminación (soft delete) de un mensaje."""
        
        mensaje_id = data.get("mensaje_id")
        
        if not mensaje_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="mensaje_id es requerido"
            )
        
        # Obtener mensaje
        mensaje = crud_mensaje.get(self.db, id=mensaje_id)
        
        if not mensaje:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensaje no encontrado"
            )
        
        # Validar permisos (autor o administrador de sala)
        es_autor = str(mensaje.usuario_id) == str(self.usuario.id)
        es_admin = self.participante.es_administrador
        
        if not (es_autor or es_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar este mensaje"
            )
        
        # Soft delete
        mensaje_update = MensajeUpdate(eliminado=True)
        mensaje_eliminado = crud_mensaje.update(
            self.db,
            db_obj=mensaje,
            obj_in=mensaje_update
        )
        
        # Broadcast eliminación
        broadcast_data = {
            "type": "message.delete",
            "sala_id": self.sala_id,
            "mensaje_id": str(mensaje_id),
            "eliminado_por": str(self.usuario.id),
            "es_administrador": es_admin,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        await manager.broadcast_to_sala(self.sala_id, broadcast_data)
        
        logger.info(
            f"🗑️ Mensaje eliminado: mensaje_id={mensaje_id}, "
            f"usuario={self.usuario.id}, es_admin={es_admin}"
        )
        
        return {
            "type": "message.deleted",
            "mensaje_id": str(mensaje_id),
            "timestamp": mensaje_eliminado.fecha_eliminacion.isoformat()
        }
    
    async def _handle_reaction(self, data: dict) -> dict:
        """Maneja añadir/quitar reacción a un mensaje."""
        
        mensaje_id = data.get("mensaje_id")
        emoji = data.get("emoji")
        
        if not mensaje_id or not emoji:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="mensaje_id y emoji son requeridos"
            )
        
        # Agregar reacción
        success = crud_mensaje.agregar_reaccion(
            self.db,
            mensaje_id=mensaje_id,
            usuario_id=str(self.usuario.id),
            emoji=emoji
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensaje no encontrado"
            )
        
        # Obtener mensaje actualizado
        mensaje = crud_mensaje.get(self.db, id=mensaje_id)
        
        # Broadcast reacción
        broadcast_data = {
            "type": "message.reaction",
            "sala_id": self.sala_id,
            "mensaje_id": str(mensaje_id),
            "emoji": emoji,
            "usuario_id": str(self.usuario.id),
            "reacciones": mensaje.reacciones,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        await manager.broadcast_to_sala(self.sala_id, broadcast_data)
        
        logger.info(
            f"👍 Reacción añadida: mensaje_id={mensaje_id}, "
            f"emoji={emoji}, usuario={self.usuario.id}"
        )
        
        return {
            "type": "reaction.added",
            "mensaje_id": str(mensaje_id),
            "emoji": emoji,
            "timestamp": datetime.now(UTC).isoformat()
        }
    
    async def _handle_typing_start(self) -> dict:
        """Maneja cuando el usuario comienza a escribir."""
        
        await manager.set_typing(
            sala_id=self.sala_id,
            usuario_id=str(self.usuario.id),
            is_typing=True
        )
        
        return None  # No response needed, broadcast only
    
    async def _handle_typing_stop(self) -> dict:
        """Maneja cuando el usuario deja de escribir."""
        
        await manager.set_typing(
            sala_id=self.sala_id,
            usuario_id=str(self.usuario.id),
            is_typing=False
        )
        
        return None  # No response needed, broadcast only
    
    async def _handle_read_receipt(self, data: dict) -> dict:
        """Maneja confirmación de lectura de mensajes."""
        
        mensajes_ids = data.get("mensajes_ids", [])
        
        # Marcar mensajes como leídos
        for mensaje_id in mensajes_ids:
            crud_lectura_mensaje.marcar_como_leido(
                self.db,
                mensaje_id=mensaje_id,
                usuario_id=str(self.usuario.id)
            )
        
        # Broadcast confirmación de lectura
        broadcast_data = {
            "type": "read.receipt",
            "sala_id": self.sala_id,
            "usuario_id": str(self.usuario.id),
            "mensajes_ids": mensajes_ids,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        await manager.broadcast_to_sala(self.sala_id, broadcast_data)
        
        logger.debug(
            f"✅ Mensajes marcados como leídos: {len(mensajes_ids)} mensajes, "
            f"usuario={self.usuario.id}"
        )
        
        return {
            "type": "messages.read",
            "count": len(mensajes_ids),
            "timestamp": datetime.now(UTC).isoformat()
        }
    
    async def _handle_get_online_users(self) -> dict:
        """Obtiene lista de usuarios online en la sala."""
        
        online_users = await manager.get_online_users_in_sala(self.sala_id)
        
        return {
            "type": "online.users",
            "sala_id": self.sala_id,
            "usuarios": online_users,
            "count": len(online_users),
            "timestamp": datetime.now(UTC).isoformat()
        }
    
    async def _handle_get_typing_users(self) -> dict:
        """Obtiene lista de usuarios que están escribiendo."""
        
        typing_users = manager.get_typing_users(self.sala_id)
        
        return {
            "type": "typing.users",
            "sala_id": self.sala_id,
            "usuarios": typing_users,
            "count": len(typing_users),
            "timestamp": datetime.now(UTC).isoformat()
        }


@router.websocket("/ws/chat/{sala_id}")
async def chat_websocket_endpoint(
    websocket: WebSocket,
    sala_id: str,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Endpoint WebSocket para chat en tiempo real.
    
    Args:
        websocket: Conexión WebSocket
        sala_id: ID de la sala de chat
        token: Token JWT para autenticación
        db: Sesión de base de datos
        
    Uso desde el cliente:
        const ws = new WebSocket('ws://localhost:8000/api/communication/ws/chat/SALA_ID?token=JWT_TOKEN');
        
        // Enviar mensaje
        ws.send(JSON.stringify({
            type: 'message.new',
            data: {
                contenido: 'Hola mundo',
                tipo_mensaje: 'texto'
            }
        }));
        
        // Indicador de escritura
        ws.send(JSON.stringify({
            type: 'typing.start',
            data: {}
        }));
    """
    
    connection_id = None
    usuario = None
    handler = None
    
    try:
        # Autenticar usuario
        if not token:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Token de autenticación requerido"
            )
            return
        
        try:
            usuario = await get_current_user_websocket(token, db)
        except Exception as e:
            logger.error(f"❌ Error autenticando usuario: {str(e)}")
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Autenticación fallida"
            )
            return
        
        # Validar sala existe
        sala = crud_sala_chat.get(db, id=sala_id)
        if not sala:
            await websocket.close(
                code=status.WS_1003_UNSUPPORTED_DATA,
                reason="Sala no encontrada"
            )
            return
        
        # Crear handler de chat
        try:
            handler = ChatWebSocketHandler(db, usuario, sala_id)
        except HTTPException as he:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=he.detail
            )
            return
        
        # Conectar al manager
        connection_id = f"chat_{sala_id}_{usuario.id}_{datetime.now(UTC).timestamp()}"
        await manager.connect(websocket, str(usuario.id), sala_id, connection_id)
        
        logger.info(
            f"✅ WebSocket chat conectado: usuario={usuario.id}, "
            f"sala={sala_id}, connection={connection_id}"
        )
        
        # Enviar mensaje de bienvenida
        await websocket.send_json({
            "type": "connected",
            "sala_id": sala_id,
            "sala_nombre": sala.nombre,
            "usuario_id": str(usuario.id),
            "connection_id": connection_id,
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        # Enviar usuarios online
        online_users = await manager.get_online_users_in_sala(sala_id)
        await websocket.send_json({
            "type": "online.users",
            "usuarios": online_users,
            "count": len(online_users),
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        # Loop principal: escuchar mensajes del cliente
        while True:
            try:
                # Recibir mensaje
                raw_message = await websocket.receive_text()
                message_data = json.loads(raw_message)
                
                event_type = message_data.get("type")
                event_data = message_data.get("data", {})
                
                if not event_type:
                    await websocket.send_json({
                        "type": "error",
                        "error": "missing_type",
                        "message": "El campo 'type' es requerido"
                    })
                    continue
                
                # Procesar evento
                response = await handler.handle_event(event_type, event_data)
                
                # Enviar respuesta al cliente si hay
                if response:
                    await websocket.send_json(response)
            
            except WebSocketDisconnect:
                logger.info(f"❌ WebSocket desconectado: usuario={usuario.id}, sala={sala_id}")
                break
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "error": "invalid_json",
                    "message": "Formato JSON inválido"
                })
            
            except Exception as e:
                logger.exception(f"❌ Error en loop WebSocket: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "error": "internal_error",
                    "message": "Error interno del servidor"
                })
    
    except Exception as e:
        logger.exception(f"❌ Error fatal en WebSocket: {str(e)}")
    
    finally:
        # Desconectar y limpiar
        if connection_id and usuario:
            await manager.disconnect(connection_id)
            logger.info(
                f"🔌 WebSocket cerrado: usuario={usuario.id}, "
                f"sala={sala_id}, connection={connection_id}"
            )
