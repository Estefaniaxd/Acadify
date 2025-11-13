"""
Modelo para rachas de usuarios.

Este modelo registra la racha actual y mejor racha del usuario,
así como información para el sistema de rachas estilo Duolingo.

Author: GitHub Copilot & Team
Date: 31 de octubre de 2025
Version: 2.0.0 - Expandido con funcionalidades Duolingo-style
"""

from sqlalchemy import Column, ForeignKey, text, CheckConstraint, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID, INTEGER, DATE
from sqlalchemy.orm import relationship

from src.db.base_class import Base


class RachaUsuario(Base):
    """
    Modelo para rachas de usuarios.
    
    Registra la racha actual, mejor racha, y funcionalidades avanzadas
    como congelación de racha, recuperaciones y notificaciones.
    
    Attributes:
        usuario_id: ID del usuario (PK)
        racha_actual: Días consecutivos de actividad actuales
        mejor_racha: Mejor racha histórica del usuario
        fecha_ultimo_dia: Última fecha de actividad
        racha_congelada_hasta: Fecha hasta la que está protegida la racha
        recuperaciones_disponibles: Cantidad de recuperaciones disponibles
        notificacion_enviada: Si se envió notificación de racha en peligro
        ultima_recompensa_dia: Último día de ciclo semanal que recibió recompensa (1-7)
    
    Relationships:
        usuario: Usuario propietario de la racha
        historial: Historial de cambios en la racha
    
    Example:
        >>> # Racha básica
        >>> racha = RachaUsuario(
        ...     usuario_id=usuario_id,
        ...     racha_actual=5,
        ...     mejor_racha=10,
        ...     fecha_ultimo_dia=date.today()
        ... )
        
        >>> # Racha con protección
        >>> racha = RachaUsuario(
        ...     usuario_id=usuario_id,
        ...     racha_actual=15,
        ...     mejor_racha=15,
        ...     fecha_ultimo_dia=date.today(),
        ...     racha_congelada_hasta=date.today() + timedelta(days=1),
        ...     recuperaciones_disponibles=2
        ... )
    """
    
    __tablename__ = "RachaUsuario"
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "racha_actual >= 0",
            name="check_racha_actual_positiva"
        ),
        CheckConstraint(
            "mejor_racha >= 0",
            name="check_mejor_racha_positiva"
        ),
        CheckConstraint(
            "mejor_racha >= racha_actual",
            name="check_mejor_racha_mayor_o_igual"
        ),
        CheckConstraint(
            "recuperaciones_disponibles >= 0",
            name="check_recuperaciones_positivas"
        ),
        CheckConstraint(
            "ultima_recompensa_dia >= 0 AND ultima_recompensa_dia <= 7",
            name="check_recompensa_dia_valido"
        ),
        # Índices
        Index("idx_racha_usuario_fecha", "fecha_ultimo_dia"),
        Index("idx_racha_congelada", "racha_congelada_hasta"),
        Index("idx_racha_notificacion", "notificacion_enviada"),
    )
    
    # Primary Key
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        primary_key=True,
        doc="ID del usuario"
    )
    
    # Racha básica
    racha_actual = Column(
        INTEGER,
        nullable=False,
        default=0,
        server_default=text("0"),
        doc="Días consecutivos de actividad actuales"
    )
    
    mejor_racha = Column(
        INTEGER,
        nullable=False,
        default=0,
        server_default=text("0"),
        doc="Mejor racha histórica del usuario"
    )
    
    fecha_ultimo_dia = Column(
        DATE,
        nullable=True,
        index=True,
        doc="Última fecha en que hubo actividad"
    )
    
    # Funcionalidades Duolingo-style (NUEVO)
    racha_congelada_hasta = Column(
        DATE,
        nullable=True,
        index=True,
        doc="Fecha hasta la que la racha está protegida (item congelador)"
    )
    
    recuperaciones_disponibles = Column(
        INTEGER,
        nullable=False,
        default=0,
        server_default=text("0"),
        doc="Cantidad de recuperaciones de racha disponibles"
    )
    
    notificacion_enviada = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
        doc="Si se envió notificación de racha en peligro hoy"
    )
    
    ultima_recompensa_dia = Column(
        INTEGER,
        nullable=False,
        default=0,
        server_default=text("0"),
        doc="Último día del ciclo semanal (1-7) que recibió recompensa"
    )
    
    # Relaciones
    usuario = relationship(
        "Usuario",
        backref="racha"
    )
    
    def __repr__(self):
        return (
            f"<RachaUsuario("
            f"usuario_id={self.usuario_id}, "
            f"actual={self.racha_actual}, "
            f"mejor={self.mejor_racha}"
            f")>"
        )
    
    @property
    def esta_protegida(self) -> bool:
        """
        Verifica si la racha está actualmente protegida por congelador.
        
        Returns:
            True si está congelada hasta hoy o después
        """
        if not self.racha_congelada_hasta:
            return False
        
        from datetime import date
        return date.today() <= self.racha_congelada_hasta
    
    @property
    def puede_recuperar(self) -> bool:
        """
        Verifica si el usuario puede recuperar una racha perdida.
        
        Returns:
            True si tiene recuperaciones disponibles
        """
        return self.recuperaciones_disponibles > 0
    
    @property
    def dia_ciclo_semanal(self) -> int:
        """
        Calcula el día actual del ciclo semanal de recompensas (1-7).
        
        Returns:
            Día del ciclo (1-7)
        """
        if self.racha_actual == 0:
            return 0
        return ((self.racha_actual - 1) % 7) + 1
    
    def incrementar_racha(self):
        """Incrementa la racha en 1 día."""
        self.racha_actual += 1
        if self.racha_actual > self.mejor_racha:
            self.mejor_racha = self.racha_actual
        
        from datetime import date
        self.fecha_ultimo_dia = date.today()
        self.notificacion_enviada = False
    
    def resetear_racha(self):
        """Resetea la racha a 0."""
        self.racha_actual = 0
        self.ultima_recompensa_dia = 0
        self.notificacion_enviada = False
    
    def usar_recuperacion(self):
        """
        Usa una recuperación para restaurar la racha.
        
        Returns:
            True si se usó correctamente
        """
        if not self.puede_recuperar:
            return False
        
        self.recuperaciones_disponibles -= 1
        # La racha se mantiene, solo actualizamos la fecha
        from datetime import date
        self.fecha_ultimo_dia = date.today()
        return True
    
    def activar_congelador(self, dias: int = 1):
        """
        Activa protección de racha por días.
        
        Args:
            dias: Cantidad de días de protección
        """
        from datetime import date, timedelta
        
        if self.racha_congelada_hasta and self.racha_congelada_hasta >= date.today():
            # Ya está protegida, extender
            self.racha_congelada_hasta += timedelta(days=dias)
        else:
            # Nueva protección
            self.racha_congelada_hasta = date.today() + timedelta(days=dias)
    
    def to_dict(self) -> dict:
        """
        Convierte la racha a diccionario para API.
        
        Returns:
            Diccionario con información de la racha
        """
        return {
            "usuario_id": str(self.usuario_id),
            "racha_actual": self.racha_actual,
            "mejor_racha": self.mejor_racha,
            "fecha_ultimo_dia": self.fecha_ultimo_dia.isoformat() if self.fecha_ultimo_dia else None,
            "esta_protegida": self.esta_protegida,
            "racha_congelada_hasta": self.racha_congelada_hasta.isoformat() if self.racha_congelada_hasta else None,
            "recuperaciones_disponibles": self.recuperaciones_disponibles,
            "puede_recuperar": self.puede_recuperar,
            "dia_ciclo_semanal": self.dia_ciclo_semanal,
            "ultima_recompensa_dia": self.ultima_recompensa_dia,
        }
