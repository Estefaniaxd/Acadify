"""
CRUD operations para el sistema de comunicación y chat
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc

from crud.base import CRUDBase
from models.communication.chat import (
    SalaChat, ParticipanteSala, Mensaje, LecturaMensaje, 
    Notificacion, ConfiguracionNotificaciones,
    TipoSala, TipoMensaje, EstadoMensaje
)
from schemas.communication.chat_schemas import (
    SalaChatCreate, SalaChatUpdate, SalaChatResponse,
    ParticipanteSalaCreate, ParticipanteSalaUpdate,
    MensajeCreate, MensajeUpdate, MensajeResponse,
    NotificacionCreate, NotificacionResponse,
    ConfiguracionNotificacionesUpdate,
    FiltrosSalas, FiltrosMensajes, FiltrosNotificaciones
)


# ==================== CRUD SALAS DE CHAT ====================

class CRUDSalaChat(CRUDBase[SalaChat, SalaChatCreate, SalaChatUpdate]):
    """CRUD para salas de chat"""
    
    def create_with_creator(
        self, db: Session, *, obj_in: SalaChatCreate, creador_id: str
    ) -> SalaChat:
        """Crear sala con creador"""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, creador_id=creador_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Agregar al creador como administrador
        participante = ParticipanteSala(
            sala_id=db_obj.id,
            usuario_id=creador_id,
            es_admin=True,
            puede_escribir=True,
            notificaciones_activadas=True
        )
        db.add(participante)
        db.commit()
        
        return db_obj
    
    def get_salas_usuario(
        self, db: Session, *, usuario_id: str, filtros: FiltrosSalas
    ) -> List[SalaChat]:
        """Obtener salas donde participa un usuario"""
        query = (
            db.query(self.model)
            .join(ParticipanteSala)
            .filter(
                ParticipanteSala.usuario_id == usuario_id,
                ParticipanteSala.esta_activo == True
            )
        )
        
        # Aplicar filtros
        if filtros.tipo_sala:
            query = query.filter(self.model.tipo_sala == filtros.tipo_sala)
        
        if filtros.es_publica is not None:
            query = query.filter(self.model.es_publica == filtros.es_publica)
        
        if filtros.curso_id:
            query = query.filter(self.model.curso_id == filtros.curso_id)
        
        if filtros.grupo_id:
            query = query.filter(self.model.grupo_id == filtros.grupo_id)
        
        if filtros.buscar:
            busqueda = f"%{filtros.buscar}%"
            query = query.filter(
                or_(
                    self.model.nombre.ilike(busqueda),
                    self.model.descripcion.ilike(busqueda),
                    self.model.tags.ilike(busqueda)
                )
            )
        
        # Ordenamiento
        if filtros.ordenar_por == "nombre":
            order_func = desc if filtros.orden_desc else asc
            query = query.order_by(order_func(self.model.nombre))
        elif filtros.ordenar_por == "fecha_creacion":
            order_func = desc if filtros.orden_desc else asc
            query = query.order_by(order_func(self.model.fecha_creacion))
        else:  # ultimo_mensaje_fecha
            order_func = desc if filtros.orden_desc else asc
            query = query.order_by(order_func(self.model.ultimo_mensaje_fecha))
        
        return query.offset(filtros.offset).limit(filtros.limite).all()
    
    def get_sala_detallada(
        self, db: Session, *, sala_id: str, usuario_id: str
    ) -> Optional[SalaChat]:
        """Obtener sala con detalles completos"""
        # Verificar que el usuario participe en la sala
        participante = (
            db.query(ParticipanteSala)
            .filter(
                ParticipanteSala.sala_id == sala_id,
                ParticipanteSala.usuario_id == usuario_id,
                ParticipanteSala.esta_activo == True
            )
            .first()
        )
        
        if not participante:
            return None
        
        return (
            db.query(self.model)
            .options(
                joinedload(self.model.participantes),
                joinedload(self.model.mensajes).limit(20)
            )
            .filter(self.model.id == sala_id)
            .first()
        )
    
    def actualizar_ultimo_mensaje(
        self, db: Session, *, sala_id: str, fecha: datetime
    ) -> None:
        """Actualizar fecha del último mensaje"""
        db.query(self.model).filter(self.model.id == sala_id).update(
            {"ultimo_mensaje_fecha": fecha}
        )
        db.commit()
    
    def get_estadisticas_sala(
        self, db: Session, *, sala_id: str
    ) -> Dict[str, Any]:
        """Obtener estadísticas de una sala"""
        hoy = datetime.now().date()
        semana_pasada = hoy - timedelta(days=7)
        
        # Total de mensajes
        total_mensajes = (
            db.query(func.count(Mensaje.id))
            .filter(Mensaje.sala_id == sala_id)
            .scalar()
        ) or 0
        
        # Mensajes hoy
        mensajes_hoy = (
            db.query(func.count(Mensaje.id))
            .filter(
                Mensaje.sala_id == sala_id,
                func.date(Mensaje.fecha_creacion) == hoy
            )
            .scalar()
        ) or 0
        
        # Mensajes esta semana
        mensajes_semana = (
            db.query(func.count(Mensaje.id))
            .filter(
                Mensaje.sala_id == sala_id,
                func.date(Mensaje.fecha_creacion) >= semana_pasada
            )
            .scalar()
        ) or 0
        
        # Total participantes activos
        total_participantes = (
            db.query(func.count(ParticipanteSala.id))
            .filter(
                ParticipanteSala.sala_id == sala_id,
                ParticipanteSala.esta_activo == True
            )
            .scalar()
        ) or 0
        
        return {
            "total_mensajes": total_mensajes,
            "mensajes_hoy": mensajes_hoy,
            "mensajes_semana": mensajes_semana,
            "total_participantes": total_participantes,
            "participantes_activos": total_participantes  # Simplificado por ahora
        }


# ==================== CRUD PARTICIPANTES ====================

class CRUDParticipanteSala(CRUDBase[ParticipanteSala, ParticipanteSalaCreate, ParticipanteSalaUpdate]):
    """CRUD para participantes de sala"""
    
    def get_participantes_sala(
        self, db: Session, *, sala_id: str, incluir_inactivos: bool = False
    ) -> List[ParticipanteSala]:
        """Obtener participantes de una sala"""
        query = db.query(self.model).filter(self.model.sala_id == sala_id)
        
        if not incluir_inactivos:
            query = query.filter(self.model.esta_activo == True)
        
        return query.all()
    
    def es_participante(
        self, db: Session, *, sala_id: str, usuario_id: str
    ) -> bool:
        """Verificar si un usuario participa en una sala"""
        return (
            db.query(self.model)
            .filter(
                self.model.sala_id == sala_id,
                self.model.usuario_id == usuario_id,
                self.model.esta_activo == True
            )
            .first()
        ) is not None
    
    def get_participante(
        self, db: Session, *, sala_id: str, usuario_id: str
    ) -> Optional[ParticipanteSala]:
        """Obtener participante específico"""
        return (
            db.query(self.model)
            .filter(
                self.model.sala_id == sala_id,
                self.model.usuario_id == usuario_id
            )
            .first()
        )
    
    def actualizar_ultima_lectura(
        self, db: Session, *, sala_id: str, usuario_id: str
    ) -> None:
        """Actualizar última lectura del participante"""
        db.query(self.model).filter(
            self.model.sala_id == sala_id,
            self.model.usuario_id == usuario_id
        ).update({"fecha_ultima_lectura": datetime.now()})
        db.commit()


# ==================== CRUD MENSAJES ====================

class CRUDMensaje(CRUDBase[Mensaje, MensajeCreate, MensajeUpdate]):
    """CRUD para mensajes"""
    
    def create_mensaje(
        self, db: Session, *, obj_in: MensajeCreate, usuario_id: str
    ) -> Mensaje:
        """Crear mensaje y actualizar sala"""
        # Procesar contenido para detectar menciones automáticamente
        contenido_procesado = self._procesar_menciones(obj_in.contenido)
        
        obj_in_data = obj_in.dict()
        obj_in_data.update({
            "usuario_id": usuario_id,
            "contenido_html": contenido_procesado["html"],
            "menciones_usuarios": contenido_procesado["menciones_usuarios"],
            "menciones_ia": contenido_procesado["menciones_ia"],
            "menciones_todos": contenido_procesado["menciones_todos"]
        })
        
        # Crear mensaje
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Actualizar contador de respuestas si es hijo
        if obj_in.mensaje_padre_id:
            self._actualizar_contador_respuestas(db, obj_in.mensaje_padre_id)
        
        # Actualizar último mensaje de la sala
        crud_sala = CRUDSalaChat(SalaChat)
        crud_sala.actualizar_ultimo_mensaje(
            db, sala_id=obj_in.sala_id, fecha=db_obj.fecha_creacion
        )
        
        # Crear notificaciones para menciones
        if contenido_procesado["menciones_usuarios"] or contenido_procesado["menciones_todos"]:
            self._crear_notificaciones_menciones(db, db_obj, contenido_procesado)
        
        return db_obj
    
    def get_mensajes_sala(
        self, db: Session, *, sala_id: str, usuario_id: str, filtros: FiltrosMensajes
    ) -> List[Mensaje]:
        """Obtener mensajes de una sala con filtros"""
        # Verificar que el usuario participe en la sala
        crud_participante = CRUDParticipanteSala(ParticipanteSala)
        if not crud_participante.es_participante(db, sala_id=sala_id, usuario_id=usuario_id):
            return []
        
        query = db.query(self.model).filter(self.model.sala_id == sala_id)
        
        # Aplicar filtros
        if filtros.usuario_id:
            query = query.filter(self.model.usuario_id == filtros.usuario_id)
        
        if filtros.tipo_mensaje:
            query = query.filter(self.model.tipo_mensaje == filtros.tipo_mensaje)
        
        if filtros.solo_importantes:
            query = query.filter(self.model.es_importante == True)
        
        if filtros.solo_anuncios:
            query = query.filter(self.model.es_anuncio == True)
        
        if filtros.con_archivos:
            query = query.filter(self.model.archivos_urls.isnot(None))
        
        if filtros.menciona_usuario:
            query = query.filter(
                self.model.menciones_usuarios.contains([str(filtros.menciona_usuario)])
            )
        
        if filtros.menciona_ia:
            query = query.filter(self.model.menciona_ia == True)
        
        if filtros.fecha_desde:
            query = query.filter(self.model.fecha_creacion >= filtros.fecha_desde)
        
        if filtros.fecha_hasta:
            query = query.filter(self.model.fecha_creacion <= filtros.fecha_hasta)
        
        if filtros.buscar:
            busqueda = f"%{filtros.buscar}%"
            query = query.filter(self.model.contenido.ilike(busqueda))
        
        if not filtros.incluir_hilos:
            query = query.filter(self.model.mensaje_padre_id.is_(None))
        
        # Ordenamiento
        order_func = desc if filtros.orden_desc else asc
        if filtros.ordenar_por == "fecha_creacion":
            query = query.order_by(order_func(self.model.fecha_creacion))
        
        return query.offset(filtros.offset).limit(filtros.limite).all()
    
    def get_mensaje_con_hilo(
        self, db: Session, *, mensaje_id: str, usuario_id: str
    ) -> Optional[Mensaje]:
        """Obtener mensaje con sus respuestas (hilo)"""
        mensaje = (
            db.query(self.model)
            .options(joinedload(self.model.respuestas))
            .filter(self.model.id == mensaje_id)
            .first()
        )
        
        if not mensaje:
            return None
        
        # Verificar acceso a la sala
        crud_participante = CRUDParticipanteSala(ParticipanteSala)
        if not crud_participante.es_participante(
            db, sala_id=str(mensaje.sala_id), usuario_id=usuario_id
        ):
            return None
        
        return mensaje
    
    def agregar_reaccion(
        self, db: Session, *, mensaje_id: str, usuario_id: str, emoji: str
    ) -> bool:
        """Agregar reacción a un mensaje"""
        mensaje = db.query(self.model).filter(self.model.id == mensaje_id).first()
        if not mensaje:
            return False
        
        reacciones = mensaje.reacciones or {}
        
        # Remover reacciones anteriores del usuario
        for key, usuarios in reacciones.items():
            if usuario_id in usuarios:
                usuarios.remove(usuario_id)
                if not usuarios:
                    del reacciones[key]
        
        # Agregar nueva reacción
        if emoji not in reacciones:
            reacciones[emoji] = []
        
        if usuario_id not in reacciones[emoji]:
            reacciones[emoji].append(usuario_id)
        
        mensaje.reacciones = reacciones
        db.commit()
        return True
    
    def _procesar_menciones(self, contenido: str) -> Dict[str, Any]:
        """Procesar menciones en el contenido del mensaje"""
        import re
        
        menciones_usuarios = []
        menciones_ia = False
        menciones_todos = False
        contenido_html = contenido
        
        # Buscar menciones de usuarios @username
        patron_usuario = r'@(\w+)'
        usuarios_mencionados = re.findall(patron_usuario, contenido)
        
        for usuario in usuarios_mencionados:
            if usuario.lower() == 'rutilio':
                menciones_ia = True
                contenido_html = re.sub(
                    f'@{usuario}', 
                    f'<span class="mencion-ia">@{usuario}</span>', 
                    contenido_html, 
                    flags=re.IGNORECASE
                )
            elif usuario.lower() == 'todos' or usuario.lower() == 'everyone':
                menciones_todos = True
                contenido_html = re.sub(
                    f'@{usuario}', 
                    f'<span class="mencion-todos">@{usuario}</span>', 
                    contenido_html, 
                    flags=re.IGNORECASE
                )
            else:
                # TODO: Verificar que el usuario existe y está en la sala
                contenido_html = re.sub(
                    f'@{usuario}', 
                    f'<span class="mencion-usuario" data-usuario="{usuario}">@{usuario}</span>', 
                    contenido_html, 
                    flags=re.IGNORECASE
                )
                menciones_usuarios.append(usuario)
        
        return {
            "html": contenido_html,
            "menciones_usuarios": menciones_usuarios,
            "menciones_ia": menciones_ia,
            "menciones_todos": menciones_todos
        }
    
    def _actualizar_contador_respuestas(self, db: Session, mensaje_padre_id: str) -> None:
        """Actualizar contador de respuestas del mensaje padre"""
        mensaje_padre = db.query(self.model).filter(self.model.id == mensaje_padre_id).first()
        if mensaje_padre:
            mensaje_padre.tiene_respuestas = True
            mensaje_padre.numero_respuestas = (
                db.query(func.count(self.model.id))
                .filter(self.model.mensaje_padre_id == mensaje_padre_id)
                .scalar()
            ) or 0
            db.commit()
    
    def _crear_notificaciones_menciones(
        self, db: Session, mensaje: Mensaje, contenido_procesado: Dict[str, Any]
    ) -> None:
        """Crear notificaciones para usuarios mencionados"""
        # TODO: Implementar creación de notificaciones
        pass


# ==================== CRUD LECTURAS ====================

class CRUDLecturaMensaje(CRUDBase[LecturaMensaje, None, None]):
    """CRUD para lecturas de mensajes"""
    
    def marcar_como_leido(
        self, db: Session, *, mensaje_id: str, usuario_id: str
    ) -> LecturaMensaje:
        """Marcar mensaje como leído por usuario"""
        # Verificar si ya está marcado como leído
        lectura_existente = (
            db.query(self.model)
            .filter(
                self.model.mensaje_id == mensaje_id,
                self.model.usuario_id == usuario_id
            )
            .first()
        )
        
        if lectura_existente:
            return lectura_existente
        
        # Crear nueva lectura
        lectura = self.model(
            mensaje_id=mensaje_id,
            usuario_id=usuario_id,
            fecha_lectura=datetime.now()
        )
        db.add(lectura)
        db.commit()
        db.refresh(lectura)
        
        return lectura
    
    def marcar_mensajes_sala_leidos(
        self, db: Session, *, sala_id: str, usuario_id: str, hasta_fecha: datetime = None
    ) -> int:
        """Marcar todos los mensajes de una sala como leídos"""
        if hasta_fecha is None:
            hasta_fecha = datetime.now()
        
        # Obtener mensajes no leídos
        mensajes_no_leidos = (
            db.query(Mensaje.id)
            .filter(
                Mensaje.sala_id == sala_id,
                Mensaje.usuario_id != usuario_id,  # No marcar propios mensajes
                Mensaje.fecha_creacion <= hasta_fecha
            )
            .outerjoin(
                LecturaMensaje,
                and_(
                    LecturaMensaje.mensaje_id == Mensaje.id,
                    LecturaMensaje.usuario_id == usuario_id
                )
            )
            .filter(LecturaMensaje.id.is_(None))
            .all()
        )
        
        # Crear lecturas masivamente
        lecturas = [
            LecturaMensaje(
                mensaje_id=mensaje_id[0],
                usuario_id=usuario_id,
                fecha_lectura=hasta_fecha
            )
            for mensaje_id in mensajes_no_leidos
        ]
        
        if lecturas:
            db.add_all(lecturas)
            db.commit()
        
        return len(lecturas)


# ==================== CRUD NOTIFICACIONES ====================

class CRUDNotificacion(CRUDBase[Notificacion, NotificacionCreate, None]):
    """CRUD para notificaciones"""
    
    def get_notificaciones_usuario(
        self, db: Session, *, usuario_id: str, filtros: FiltrosNotificaciones
    ) -> List[Notificacion]:
        """Obtener notificaciones de un usuario"""
        query = db.query(self.model).filter(self.model.usuario_id == usuario_id)
        
        # Aplicar filtros
        if filtros.tipo_notificacion:
            query = query.filter(self.model.tipo_notificacion == filtros.tipo_notificacion)
        
        if filtros.solo_no_leidas:
            query = query.filter(self.model.leida == False)
        
        if filtros.fecha_desde:
            query = query.filter(self.model.fecha_creacion >= filtros.fecha_desde)
        
        if filtros.fecha_hasta:
            query = query.filter(self.model.fecha_creacion <= filtros.fecha_hasta)
        
        # Ordenamiento
        order_func = desc if filtros.orden_desc else asc
        query = query.order_by(order_func(self.model.fecha_creacion))
        
        return query.offset(filtros.offset).limit(filtros.limite).all()
    
    def marcar_como_leida(
        self, db: Session, *, notificacion_id: str, usuario_id: str
    ) -> bool:
        """Marcar notificación como leída"""
        resultado = (
            db.query(self.model)
            .filter(
                self.model.id == notificacion_id,
                self.model.usuario_id == usuario_id
            )
            .update({
                "leida": True,
                "fecha_lectura": datetime.now()
            })
        )
        db.commit()
        return resultado > 0
    
    def marcar_todas_leidas(
        self, db: Session, *, usuario_id: str, tipo_notificacion: str = None
    ) -> int:
        """Marcar todas las notificaciones como leídas"""
        query = db.query(self.model).filter(
            self.model.usuario_id == usuario_id,
            self.model.leida == False
        )
        
        if tipo_notificacion:
            query = query.filter(self.model.tipo_notificacion == tipo_notificacion)
        
        resultado = query.update({
            "leida": True,
            "fecha_lectura": datetime.now()
        })
        db.commit()
        return resultado
    
    def get_count_no_leidas(self, db: Session, *, usuario_id: str) -> int:
        """Obtener cantidad de notificaciones no leídas"""
        return (
            db.query(func.count(self.model.id))
            .filter(
                self.model.usuario_id == usuario_id,
                self.model.leida == False
            )
            .scalar()
        ) or 0


# ==================== CRUD CONFIGURACIÓN NOTIFICACIONES ====================

class CRUDConfiguracionNotificaciones(CRUDBase[ConfiguracionNotificaciones, ConfiguracionNotificacionesUpdate, ConfiguracionNotificacionesUpdate]):
    """CRUD para configuración de notificaciones"""
    
    def get_by_usuario(
        self, db: Session, *, usuario_id: str
    ) -> ConfiguracionNotificaciones:
        """Obtener configuración de usuario (crear si no existe)"""
        config = (
            db.query(self.model)
            .filter(self.model.usuario_id == usuario_id)
            .first()
        )
        
        if not config:
            # Crear configuración por defecto
            config = self.model(usuario_id=usuario_id)
            db.add(config)
            db.commit()
            db.refresh(config)
        
        return config
    
    def update_by_usuario(
        self, db: Session, *, usuario_id: str, obj_in: ConfiguracionNotificacionesUpdate
    ) -> ConfiguracionNotificaciones:
        """Actualizar configuración de usuario"""
        config = self.get_by_usuario(db, usuario_id=usuario_id)
        
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(config, field, value)
        
        config.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(config)
        
        return config


# Instancias de CRUD
crud_sala_chat = CRUDSalaChat(SalaChat)
crud_participante_sala = CRUDParticipanteSala(ParticipanteSala)
crud_mensaje = CRUDMensaje(Mensaje)
crud_lectura_mensaje = CRUDLecturaMensaje(LecturaMensaje)
crud_notificacion = CRUDNotificacion(Notificacion)
crud_config_notificaciones = CRUDConfiguracionNotificaciones(ConfiguracionNotificaciones)