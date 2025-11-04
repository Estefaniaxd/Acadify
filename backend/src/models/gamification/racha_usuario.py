from ...db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, Integer, Boolean, TIME
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, ARRAY
from sqlalchemy.sql import func


class RachaUsuario(Base):
    """
    Modelo de Racha de Usuario (Gamificación)
    
    Gestiona las rachas de actividad de los usuarios:
    - Racha actual y máxima
    - Sistema de congelación de rachas
    - Notificaciones y recordatorios
    - Milestones y logros
    - Estadísticas históricas
    """
    __tablename__ = "racha_usuario"

    # ============================================
    # IDENTIFICACIÓN
    # ============================================
    racha_id = Column(UUID(as_uuid=True), primary_key=True)
    usuario_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"), 
        nullable=False
    )
    tipo = Column(String(13), nullable=False)  # diaria, semanal, etc.
    
    # ============================================
    # RACHA ACTUAL
    # ============================================
    racha_actual = Column(Integer, nullable=False, default=0)
    racha_maxima = Column(Integer, nullable=False, default=0)
    fecha_inicio_racha = Column(TIMESTAMP(timezone=True), nullable=True)
    ultima_actividad = Column(TIMESTAMP(timezone=True), nullable=True)
    proxima_actividad_requerida = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # ============================================
    # ESTADO Y CONGELACIÓN
    # ============================================
    esta_activa = Column(Boolean, nullable=False, default=True)
    esta_congelada = Column(Boolean, nullable=False, default=False)
    fecha_congelacion = Column(TIMESTAMP(timezone=True), nullable=True)
    dias_congelacion_restantes = Column(Integer, nullable=False, default=0)
    
    # ============================================
    # NOTIFICACIONES
    # ============================================
    notificacion_enviada = Column(Boolean, nullable=False, default=False)
    hora_notificacion_preferida = Column(TIME, nullable=True)
    
    # ============================================
    # ESTADÍSTICAS Y CONTADORES
    # ============================================
    total_activaciones = Column(Integer, nullable=False, default=0)
    total_congelaciones_usadas = Column(Integer, nullable=False, default=0)
    total_rachas_perdidas = Column(Integer, nullable=False, default=0)
    
    # ============================================
    # MILESTONES Y LOGROS
    # ============================================
    milestones_alcanzados = Column(ARRAY(Integer), nullable=True)  # [7, 30, 100, etc.]
    ultimo_milestone = Column(Integer, nullable=True)
    fecha_ultimo_milestone = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # ============================================
    # AUDITORÍA
    # ============================================
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
