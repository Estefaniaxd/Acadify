"""
CRUD operations para el modelo BancoPregunta
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
from datetime import datetime

from src.crud.base import CRUDBase
from src.models.evaluaciones import BancoPregunta, TipoPregunta, DificultadPregunta
from src.schemas.evaluaciones import BancoPreguntaCreate, BancoPreguntaUpdate, FiltrosBancoPreguntas


class CRUDBancoPregunta(CRUDBase[BancoPregunta, BancoPreguntaCreate, BancoPreguntaUpdate]):
    
    def get_preguntas_por_profesor(
        self, 
        db: Session, 
        profesor_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[BancoPregunta]:
        """Obtener preguntas del banco creadas por un profesor específico"""
        return db.query(BancoPregunta).filter(
            BancoPregunta.creado_por == profesor_id
        ).order_by(desc(BancoPregunta.fecha_creacion)).offset(skip).limit(limit).all()
    
    def get_preguntas_publicas(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[BancoPregunta]:
        """Obtener preguntas públicas disponibles para todos los profesores"""
        return db.query(BancoPregunta).filter(
            BancoPregunta.es_publica == True
        ).order_by(desc(BancoPregunta.veces_utilizada)).offset(skip).limit(limit).all()
    
    def get_preguntas_institucion(
        self, 
        db: Session, 
        institucion_id: str, 
        incluir_publicas: bool = True,
        skip: int = 0, 
        limit: int = 100
    ) -> List[BancoPregunta]:
        """Obtener preguntas disponibles para una institución"""
        query = db.query(BancoPregunta)
        
        if incluir_publicas:
            query = query.filter(
                or_(
                    BancoPregunta.institucion_id == institucion_id,
                    BancoPregunta.es_publica == True
                )
            )
        else:
            query = query.filter(BancoPregunta.institucion_id == institucion_id)
        
        return query.order_by(desc(BancoPregunta.fecha_creacion)).offset(skip).limit(limit).all()
    
    def buscar_con_filtros(
        self, 
        db: Session, 
        filtros: FiltrosBancoPreguntas,
        usuario_id: Optional[str] = None,
        institucion_id: Optional[str] = None
    ) -> List[BancoPregunta]:
        """Buscar preguntas con filtros avanzados"""
        query = db.query(BancoPregunta)
        
        # Filtros de acceso básicos
        if usuario_id and institucion_id:
            query = query.filter(
                or_(
                    BancoPregunta.creado_por == usuario_id,  # Propias
                    BancoPregunta.es_publica == True,        # Públicas
                    BancoPregunta.institucion_id == institucion_id  # De la institución
                )
            )
        elif usuario_id:
            query = query.filter(
                or_(
                    BancoPregunta.creado_por == usuario_id,
                    BancoPregunta.es_publica == True
                )
            )
        
        # Filtro por tipo de pregunta
        if filtros.tipo_pregunta:
            query = query.filter(BancoPregunta.tipo_pregunta == filtros.tipo_pregunta)
        
        # Filtro por dificultad
        if filtros.dificultad:
            query = query.filter(BancoPregunta.dificultad == filtros.dificultad)
        
        # Filtro por materia
        if filtros.materia:
            query = query.filter(BancoPregunta.materia.ilike(f"%{filtros.materia}%"))
        
        # Filtro por tema
        if filtros.tema:
            query = query.filter(BancoPregunta.tema.ilike(f"%{filtros.tema}%"))
        
        # Filtro por categoría
        if filtros.categoria:
            query = query.filter(BancoPregunta.categoria.ilike(f"%{filtros.categoria}%"))
        
        # Filtro por nivel educativo
        if filtros.nivel_educativo:
            query = query.filter(BancoPregunta.nivel_educativo == filtros.nivel_educativo)
        
        # Filtro por tags
        if filtros.tags:
            for tag in filtros.tags:
                query = query.filter(BancoPregunta.tags.contains([tag]))
        
        # Filtro por visibilidad
        if filtros.es_publica is not None:
            query = query.filter(BancoPregunta.es_publica == filtros.es_publica)
        
        # Filtro por creador
        if filtros.creado_por:
            query = query.filter(BancoPregunta.creado_por == filtros.creado_por)
        
        # Búsqueda por texto
        if filtros.texto_busqueda:
            texto = f"%{filtros.texto_busqueda}%"
            query = query.filter(
                or_(
                    BancoPregunta.titulo.ilike(texto),
                    BancoPregunta.descripcion.ilike(texto),
                    BancoPregunta.materia.ilike(texto),
                    BancoPregunta.tema.ilike(texto)
                )
            )
        
        # Ordenar por relevancia/uso
        query = query.order_by(desc(BancoPregunta.veces_utilizada), desc(BancoPregunta.fecha_creacion))
        
        return query.offset(filtros.offset).limit(filtros.limite).all()
    
    def get_materias_disponibles(
        self, 
        db: Session, 
        usuario_id: Optional[str] = None,
        institucion_id: Optional[str] = None
    ) -> List[str]:
        """Obtener lista de materias disponibles"""
        query = db.query(BancoPregunta.materia).distinct()
        
        if usuario_id and institucion_id:
            query = query.filter(
                or_(
                    BancoPregunta.creado_por == usuario_id,
                    BancoPregunta.es_publica == True,
                    BancoPregunta.institucion_id == institucion_id
                )
            )
        
        materias = [m[0] for m in query.all() if m[0] is not None]
        return sorted(materias)
    
    def get_temas_por_materia(
        self, 
        db: Session, 
        materia: str,
        usuario_id: Optional[str] = None,
        institucion_id: Optional[str] = None
    ) -> List[str]:
        """Obtener temas disponibles para una materia específica"""
        query = db.query(BancoPregunta.tema).distinct().filter(
            BancoPregunta.materia == materia
        )
        
        if usuario_id and institucion_id:
            query = query.filter(
                or_(
                    BancoPregunta.creado_por == usuario_id,
                    BancoPregunta.es_publica == True,
                    BancoPregunta.institucion_id == institucion_id
                )
            )
        
        temas = [t[0] for t in query.all() if t[0] is not None]
        return sorted(temas)
    
    def get_tags_populares(
        self, 
        db: Session, 
        limite: int = 50,
        usuario_id: Optional[str] = None,
        institucion_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obtener los tags más populares"""
        query = db.query(BancoPregunta.tags)
        
        if usuario_id and institucion_id:
            query = query.filter(
                or_(
                    BancoPregunta.creado_por == usuario_id,
                    BancoPregunta.es_publica == True,
                    BancoPregunta.institucion_id == institucion_id
                )
            )
        
        # Contar frecuencia de tags
        tag_counts = {}
        for row in query.all():
            if row.tags and isinstance(row.tags, list):
                for tag in row.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Ordenar por frecuencia
        tags_ordenados = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"tag": tag, "count": count} 
            for tag, count in tags_ordenados[:limite]
        ]
    
    def duplicar_pregunta(
        self, 
        db: Session, 
        pregunta_id: str, 
        nuevo_creador_id: str,
        nueva_institucion_id: Optional[str] = None
    ) -> Optional[BancoPregunta]:
        """Duplicar una pregunta del banco para otro usuario/institución"""
        pregunta_original = self.get(db=db, id=pregunta_id)
        if not pregunta_original:
            return None
        
        # Crear nueva pregunta basada en la original
        pregunta_data = BancoPreguntaCreate(
            titulo=f"Copia de: {pregunta_original.titulo}",
            descripcion=pregunta_original.descripcion,
            tipo_pregunta=pregunta_original.tipo_pregunta,
            dificultad=pregunta_original.dificultad,
            materia=pregunta_original.materia,
            tema=pregunta_original.tema,
            subtema=pregunta_original.subtema,
            opciones_respuesta=pregunta_original.opciones_respuesta,
            respuesta_correcta=pregunta_original.respuesta_correcta,
            explicacion=pregunta_original.explicacion,
            imagen_url=pregunta_original.imagen_url,
            audio_url=pregunta_original.audio_url,
            video_url=pregunta_original.video_url,
            archivos_adjuntos=pregunta_original.archivos_adjuntos,
            es_publica=False,  # Las copias empiezan privadas
            tags=pregunta_original.tags.copy() if pregunta_original.tags else None,
            categoria=pregunta_original.categoria,
            nivel_educativo=pregunta_original.nivel_educativo,
            puntuacion_sugerida=pregunta_original.puntuacion_sugerida,
            tiempo_estimado_segundos=pregunta_original.tiempo_estimado_segundos,
            creado_por=nuevo_creador_id,
            institucion_id=nueva_institucion_id
        )
        
        return self.create(db=db, obj_in=pregunta_data)
    
    def marcar_como_publica(
        self, 
        db: Session, 
        pregunta_id: str, 
        usuario_id: str
    ) -> Optional[BancoPregunta]:
        """Marcar una pregunta como pública (solo el creador puede hacerlo)"""
        pregunta = self.get(db=db, id=pregunta_id)
        if not pregunta or pregunta.creado_por != usuario_id:
            return None
        
        pregunta.es_publica = True
        pregunta.fecha_actualizacion = datetime.utcnow()
        
        db.commit()
        db.refresh(pregunta)
        return pregunta
    
    def solicitar_revision(
        self, 
        db: Session, 
        pregunta_id: str, 
        usuario_id: str
    ) -> Optional[BancoPregunta]:
        """Solicitar revisión de una pregunta para hacerla pública"""
        pregunta = self.get(db=db, id=pregunta_id)
        if not pregunta or pregunta.creado_por != usuario_id:
            return None
        
        pregunta.estado_revision = "pendiente"
        pregunta.fecha_actualizacion = datetime.utcnow()
        
        db.commit()
        db.refresh(pregunta)
        return pregunta
    
    def revisar_pregunta(
        self, 
        db: Session, 
        pregunta_id: str, 
        revisor_id: str,
        aprobada: bool,
        comentarios: Optional[str] = None
    ) -> Optional[BancoPregunta]:
        """Revisar una pregunta (admin o coordinador)"""
        pregunta = self.get(db=db, id=pregunta_id)
        if not pregunta:
            return None
        
        pregunta.revisado_por = revisor_id
        pregunta.fecha_revision = datetime.utcnow()
        pregunta.estado_revision = "aprobado" if aprobada else "rechazado"
        pregunta.comentarios_revision = comentarios
        
        if aprobada:
            pregunta.es_publica = True
        
        pregunta.fecha_actualizacion = datetime.utcnow()
        
        db.commit()
        db.refresh(pregunta)
        return pregunta
    
    def get_preguntas_pendientes_revision(
        self, 
        db: Session, 
        institucion_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[BancoPregunta]:
        """Obtener preguntas pendientes de revisión"""
        query = db.query(BancoPregunta).filter(
            BancoPregunta.estado_revision == "pendiente"
        )
        
        if institucion_id:
            query = query.filter(BancoPregunta.institucion_id == institucion_id)
        
        return query.order_by(asc(BancoPregunta.fecha_actualizacion)).offset(skip).limit(limit).all()
    
    def get_estadisticas_banco(
        self, 
        db: Session, 
        usuario_id: Optional[str] = None,
        institucion_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtener estadísticas del banco de preguntas"""
        query_base = db.query(BancoPregunta)
        
        # Filtrar por usuario/institución si se proporciona
        if usuario_id:
            query_usuario = query_base.filter(BancoPregunta.creado_por == usuario_id)
            total_propias = query_usuario.count()
            
            # Estadísticas por tipo de pregunta (propias)
            tipos_propias = db.query(
                BancoPregunta.tipo_pregunta, 
                func.count(BancoPregunta.pregunta_id)
            ).filter(
                BancoPregunta.creado_por == usuario_id
            ).group_by(BancoPregunta.tipo_pregunta).all()
            
            # Estadísticas por dificultad (propias)
            dificultades_propias = db.query(
                BancoPregunta.dificultad, 
                func.count(BancoPregunta.pregunta_id)
            ).filter(
                BancoPregunta.creado_por == usuario_id
            ).group_by(BancoPregunta.dificultad).all()
            
            # Preguntas más utilizadas (propias)
            mas_utilizadas_propias = query_usuario.order_by(
                desc(BancoPregunta.veces_utilizada)
            ).limit(5).all()
            
        else:
            total_propias = 0
            tipos_propias = []
            dificultades_propias = []
            mas_utilizadas_propias = []
        
        # Estadísticas globales
        total_publicas = query_base.filter(BancoPregunta.es_publica == True).count()
        
        if institucion_id:
            total_institucion = query_base.filter(
                BancoPregunta.institucion_id == institucion_id
            ).count()
        else:
            total_institucion = 0
        
        # Distribución por tipos (todas las preguntas accesibles)
        if usuario_id and institucion_id:
            query_accesibles = query_base.filter(
                or_(
                    BancoPregunta.creado_por == usuario_id,
                    BancoPregunta.es_publica == True,
                    BancoPregunta.institucion_id == institucion_id
                )
            )
        elif usuario_id:
            query_accesibles = query_base.filter(
                or_(
                    BancoPregunta.creado_por == usuario_id,
                    BancoPregunta.es_publica == True
                )
            )
        else:
            query_accesibles = query_base
        
        tipos_accesibles = db.query(
            BancoPregunta.tipo_pregunta, 
            func.count(BancoPregunta.pregunta_id)
        ).filter(
            query_accesibles.statement.whereclause
        ).group_by(BancoPregunta.tipo_pregunta).all()
        
        return {
            "total_preguntas_propias": total_propias,
            "total_preguntas_publicas": total_publicas,
            "total_preguntas_institucion": total_institucion,
            "total_preguntas_accesibles": query_accesibles.count(),
            "distribucion_tipos_propias": dict(tipos_propias),
            "distribucion_dificultades_propias": dict(dificultades_propias),
            "distribucion_tipos_accesibles": dict(tipos_accesibles),
            "preguntas_mas_utilizadas_propias": [
                {
                    "pregunta_id": p.pregunta_id,
                    "titulo": p.titulo,
                    "veces_utilizada": p.veces_utilizada,
                    "tipo_pregunta": p.tipo_pregunta.value
                }
                for p in mas_utilizadas_propias
            ]
        }
    
    def actualizar_estadisticas_uso(
        self, 
        db: Session, 
        pregunta_id: str, 
        promedio_aciertos: Optional[float] = None,
        tiempo_promedio: Optional[float] = None
    ) -> Optional[BancoPregunta]:
        """Actualizar estadísticas de uso de una pregunta"""
        pregunta = self.get(db=db, id=pregunta_id)
        if not pregunta:
            return None
        
        if promedio_aciertos is not None:
            pregunta.promedio_aciertos = promedio_aciertos
            # Recalcular dificultad basada en aciertos
            if promedio_aciertos >= 80:
                nueva_dificultad_calc = 1.0  # Muy fácil
            elif promedio_aciertos >= 60:
                nueva_dificultad_calc = 2.0  # Fácil
            elif promedio_aciertos >= 40:
                nueva_dificultad_calc = 3.0  # Medio
            elif promedio_aciertos >= 20:
                nueva_dificultad_calc = 4.0  # Difícil
            else:
                nueva_dificultad_calc = 5.0  # Muy difícil
            
            pregunta.calificacion_dificultad = nueva_dificultad_calc
        
        pregunta.ultima_vez_utilizada = datetime.utcnow()
        pregunta.fecha_actualizacion = datetime.utcnow()
        
        db.commit()
        db.refresh(pregunta)
        return pregunta
    
    def exportar_preguntas(
        self, 
        db: Session, 
        pregunta_ids: List[str],
        formato: str = "json"
    ) -> Dict[str, Any]:
        """Exportar preguntas seleccionadas"""
        preguntas = db.query(BancoPregunta).filter(
            BancoPregunta.pregunta_id.in_(pregunta_ids)
        ).all()
        
        if formato == "json":
            return {
                "formato": "acadify_banco_preguntas_v1",
                "fecha_exportacion": datetime.utcnow().isoformat(),
                "total_preguntas": len(preguntas),
                "preguntas": [
                    {
                        "titulo": p.titulo,
                        "descripcion": p.descripcion,
                        "tipo_pregunta": p.tipo_pregunta.value,
                        "dificultad": p.dificultad.value,
                        "materia": p.materia,
                        "tema": p.tema,
                        "subtema": p.subtema,
                        "opciones_respuesta": p.opciones_respuesta,
                        "respuesta_correcta": p.respuesta_correcta,
                        "explicacion": p.explicacion,
                        "tags": p.tags,
                        "categoria": p.categoria,
                        "nivel_educativo": p.nivel_educativo,
                        "puntuacion_sugerida": p.puntuacion_sugerida,
                        "tiempo_estimado_segundos": p.tiempo_estimado_segundos
                    }
                    for p in preguntas
                ]
            }
        
        return {"error": "Formato no soportado"}
    
    def importar_preguntas(
        self, 
        db: Session, 
        datos_importacion: Dict[str, Any],
        usuario_id: str,
        institucion_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Importar preguntas desde un archivo"""
        if datos_importacion.get("formato") != "acadify_banco_preguntas_v1":
            return {"exito": False, "error": "Formato no reconocido"}
        
        preguntas_importadas = []
        errores = []
        
        for i, pregunta_data in enumerate(datos_importacion.get("preguntas", [])):
            try:
                pregunta_create = BancoPreguntaCreate(
                    titulo=pregunta_data["titulo"],
                    descripcion=pregunta_data.get("descripcion"),
                    tipo_pregunta=TipoPregunta(pregunta_data["tipo_pregunta"]),
                    dificultad=DificultadPregunta(pregunta_data.get("dificultad", "medio")),
                    materia=pregunta_data.get("materia"),
                    tema=pregunta_data.get("tema"),
                    subtema=pregunta_data.get("subtema"),
                    opciones_respuesta=pregunta_data.get("opciones_respuesta"),
                    respuesta_correcta=pregunta_data.get("respuesta_correcta"),
                    explicacion=pregunta_data.get("explicacion"),
                    tags=pregunta_data.get("tags"),
                    categoria=pregunta_data.get("categoria"),
                    nivel_educativo=pregunta_data.get("nivel_educativo"),
                    puntuacion_sugerida=pregunta_data.get("puntuacion_sugerida", 1.0),
                    tiempo_estimado_segundos=pregunta_data.get("tiempo_estimado_segundos"),
                    creado_por=usuario_id,
                    institucion_id=institucion_id,
                    es_publica=False  # Las preguntas importadas empiezan privadas
                )
                
                pregunta_creada = self.create(db=db, obj_in=pregunta_create)
                preguntas_importadas.append(pregunta_creada.pregunta_id)
                
            except Exception as e:
                errores.append(f"Error en pregunta {i+1}: {str(e)}")
        
        return {
            "exito": True,
            "preguntas_importadas": len(preguntas_importadas),
            "preguntas_con_errores": len(errores),
            "errores": errores,
            "ids_creados": preguntas_importadas
        }


# Instancia del CRUD
banco_pregunta = CRUDBancoPregunta(BancoPregunta)