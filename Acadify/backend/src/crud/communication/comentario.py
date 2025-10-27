# src/crud/communication/comentario.py

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc, or_

from src.crud.base import CRUDBase
from src.models.communication.comentario import Comentario, TipoComentario
from src.schemas.communication.comentario import ComentarioCreate, ComentarioUpdate


class CRUDComentario(CRUDBase[Comentario, ComentarioCreate, ComentarioUpdate]):
    """
    CRUD operations for Comentario model
    """

    def create_comentario(
        self, 
        db: Session, 
        *, 
        comentario_in: ComentarioCreate, 
        autor_id: UUID
    ) -> Comentario:
        """
        Crear un nuevo comentario en un curso
        """
        db_obj = Comentario(
            curso_id=comentario_in.curso_id,
            autor_id=autor_id,
            contenido=comentario_in.contenido,
            tipo=comentario_in.tipo,
            archivos_adjuntos=comentario_in.archivos_adjuntos,
            comentario_padre_id=comentario_in.comentario_padre_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_comentarios_curso(
        self, 
        db: Session, 
        *, 
        curso_id: UUID,
        skip: int = 0,
        limit: int = 50,
        incluir_eliminados: bool = False,
        tipo_filtro: Optional[TipoComentario] = None
    ) -> List[Comentario]:
        """
        Obtener comentarios de un curso con filtros
        """
        query = db.query(Comentario).filter(
            Comentario.curso_id == curso_id
        )
        
        # Filtrar por eliminados
        if not incluir_eliminados:
            query = query.filter(Comentario.esta_eliminado == False)
            
        # Filtrar por activos
        query = query.filter(Comentario.activo == True)
        
        # Filtrar por tipo si se especifica
        if tipo_filtro:
            query = query.filter(Comentario.tipo == tipo_filtro)
            
        return query.order_by(desc(Comentario.fecha_creacion)).offset(skip).limit(limit).all()

    def get_comentarios_con_respuestas(
        self, 
        db: Session, 
        *, 
        curso_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[Comentario]:
        """
        Obtener comentarios principales con sus respuestas anidadas
        """
        # Obtener comentarios principales (no son respuestas)
        comentarios_principales = db.query(Comentario).filter(
            and_(
                Comentario.curso_id == curso_id,
                Comentario.comentario_padre_id == None,
                Comentario.esta_eliminado == False,
                Comentario.activo == True
            )
        ).order_by(desc(Comentario.fecha_creacion)).offset(skip).limit(limit).all()
        
        return comentarios_principales

    def get_respuestas_comentario(
        self, 
        db: Session, 
        *, 
        comentario_padre_id: UUID
    ) -> List[Comentario]:
        """
        Obtener todas las respuestas de un comentario específico
        """
        return db.query(Comentario).filter(
            and_(
                Comentario.comentario_padre_id == comentario_padre_id,
                Comentario.esta_eliminado == False,
                Comentario.activo == True
            )
        ).order_by(asc(Comentario.fecha_creacion)).all()

    def get_comentarios_usuario(
        self, 
        db: Session, 
        *, 
        autor_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Comentario]:
        """
        Obtener todos los comentarios de un usuario específico
        """
        return db.query(Comentario).filter(
            and_(
                Comentario.autor_id == autor_id,
                Comentario.esta_eliminado == False,
                Comentario.activo == True
            )
        ).order_by(desc(Comentario.fecha_creacion)).offset(skip).limit(limit).all()

    def search_comentarios(
        self, 
        db: Session, 
        *, 
        curso_id: UUID,
        busqueda: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Comentario]:
        """
        Buscar comentarios por contenido en un curso específico
        """
        return db.query(Comentario).filter(
            and_(
                Comentario.curso_id == curso_id,
                Comentario.contenido.ilike(f"%{busqueda}%"),
                Comentario.esta_eliminado == False,
                Comentario.activo == True
            )
        ).order_by(desc(Comentario.fecha_creacion)).offset(skip).limit(limit).all()

    def update_comentario(
        self, 
        db: Session, 
        *, 
        comentario_id: UUID,
        comentario_update: ComentarioUpdate,
        usuario_id: UUID
    ) -> Optional[Comentario]:
        """
        Actualizar un comentario (solo el autor puede editarlo)
        """
        comentario = db.query(Comentario).filter(
            and_(
                Comentario.comentario_id == comentario_id,
                Comentario.autor_id == usuario_id,
                Comentario.esta_eliminado == False
            )
        ).first()
        
        if not comentario:
            return None
            
        # Actualizar campos
        if comentario_update.contenido is not None:
            comentario.contenido = comentario_update.contenido
            comentario.editado = True
            comentario.fecha_actualizacion = datetime.utcnow()
            
        if comentario_update.archivos_adjuntos is not None:
            comentario.archivos_adjuntos = comentario_update.archivos_adjuntos
            
        db.commit()
        db.refresh(comentario)
        return comentario

    def soft_delete_comentario(
        self, 
        db: Session, 
        *, 
        comentario_id: UUID,
        usuario_id: UUID
    ) -> bool:
        """
        Eliminar un comentario (soft delete) - solo el autor puede eliminarlo
        """
        comentario = db.query(Comentario).filter(
            and_(
                Comentario.comentario_id == comentario_id,
                Comentario.autor_id == usuario_id,
                Comentario.esta_eliminado == False
            )
        ).first()
        
        if not comentario:
            return False
            
        comentario.esta_eliminado = True
        comentario.fecha_eliminacion = datetime.utcnow()
        db.commit()
        return True

    def count_comentarios_curso(
        self, 
        db: Session, 
        *, 
        curso_id: UUID,
        tipo_filtro: Optional[TipoComentario] = None
    ) -> int:
        """
        Contar comentarios activos en un curso
        """
        query = db.query(Comentario).filter(
            and_(
                Comentario.curso_id == curso_id,
                Comentario.esta_eliminado == False,
                Comentario.activo == True
            )
        )
        
        if tipo_filtro:
            query = query.filter(Comentario.tipo == tipo_filtro)
            
        return query.count()

    def get_anuncios_curso(
        self, 
        db: Session, 
        *, 
        curso_id: UUID,
        skip: int = 0,
        limit: int = 10
    ) -> List[Comentario]:
        """
        Obtener solo los anuncios de un curso (para profesores)
        """
        return db.query(Comentario).filter(
            and_(
                Comentario.curso_id == curso_id,
                Comentario.tipo == TipoComentario.anuncio,
                Comentario.esta_eliminado == False,
                Comentario.activo == True
            )
        ).order_by(desc(Comentario.fecha_creacion)).offset(skip).limit(limit).all()

    def get_preguntas_sin_respuesta(
        self, 
        db: Session, 
        *, 
        curso_id: UUID,
        skip: int = 0,
        limit: int = 10
    ) -> List[Comentario]:
        """
        Obtener preguntas que no tienen respuestas aún
        """
        # Subconsulta para obtener IDs de comentarios que tienen respuestas
        subquery = db.query(Comentario.comentario_padre_id).filter(
            and_(
                Comentario.curso_id == curso_id,
                Comentario.comentario_padre_id != None,
                Comentario.esta_eliminado == False
            )
        ).distinct()
        
        # Consulta principal para preguntas sin respuestas
        return db.query(Comentario).filter(
            and_(
                Comentario.curso_id == curso_id,
                Comentario.tipo == TipoComentario.pregunta,
                Comentario.comentario_id.notin_(subquery),
                Comentario.esta_eliminado == False,
                Comentario.activo == True
            )
        ).order_by(desc(Comentario.fecha_creacion)).offset(skip).limit(limit).all()


# Instancia del CRUD
comentario = CRUDComentario(Comentario)