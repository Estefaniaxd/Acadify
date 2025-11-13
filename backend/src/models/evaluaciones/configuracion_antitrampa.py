"""Sistema Anti-Trampa para Evaluaciones en Línea.
==============================================

Modelo profesional y completo para configuración de integridad académica.
Sincronizado 100% con la base de datos real (84 campos).

CAPACIDADES DEL SISTEMA:
✓ Grabación: Pantalla + Audio + Teclas (keylogger)
✓ Cámara: Captura periódica con reconocimiento facial
✓ IA: Detección de respuestas generadas por ChatGPT/IA
✓ Plagio: Comparación entre estudiantes, banco de respuestas, internet
✓ Navegación: Control de pestañas, aplicaciones, ventanas
✓ Comportamiento: Análisis de patrones sospechosos
✓ Seguridad: Sesiones múltiples, VPN, dispositivos externos, IPs
✓ Bloqueo: 8 funcionalidades bloqueables (copiar, pegar, F12, etc.)
✓ Tiempo Real: Dashboard con alertas inmediatas
✓ Puntuación: Sistema de riesgo con pesos configurables
✓ Jerarquía: 5 niveles con herencia (Global → Institución → Curso → Examen → Estudiante)

Autor: Sistema Acadify
Fecha: 2025-11-03
Versión: 2.0 - Sincronizado con BD
"""

from datetime import datetime
from typing import Any
import uuid

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from src.db.base_class import Base


class ConfiguracionAntiTrampa(Base):
    """Configuración profesional y completa del sistema anti-trampa.

    **Jerarquía de Herencia:**
    Global → Institución → Curso → Examen → Estudiante

    Las configuraciones hijas heredan valores de las padres, permitiendo:
    - Definir políticas globales
    - Personalizar por institución
    - Ajustar por curso
    - Configurar específicamente por examen
    - Excepciones individuales por estudiante

    **Funcionalidades Principales:**

    1. **Grabación Completa:**
       - Pantalla (screen recording)
       - Audio (micrófono)
       - Teclas pulsadas (keylogger)
       - Retención configurable

    2. **Monitoreo de Cámara:**
       - Captura inicial (verificación de identidad)
       - Capturas periódicas (frecuencia configurable)
       - Reconocimiento facial
       - Detección de múltiples personas
       - Detección de ausencia

    3. **Detección de IA:**
       - Análisis de respuestas generadas por IA
       - Umbral de probabilidad configurable
       - Tipos de pregunta específicos
       - Acciones automáticas

    4. **Análisis de Plagio:**
       - Comparación entre estudiantes del mismo curso
       - Comparación con banco de respuestas previas
       - Búsqueda en internet (API externa)
       - Umbral de similitud configurable

    5. **Control de Navegación:**
       - Cambios de pestaña
       - Cambios de aplicación
       - Cambios de ventana
       - Salida de pantalla completa
       - Límites y acciones configurables

    6. **Seguridad Avanzada:**
       - Sesiones múltiples
       - Detección de VPN
       - Dispositivos externos
       - Control de IPs
       - Validación de ubicación

    7. **Sistema de Puntuación:**
       - Pesos configurables por tipo de evento
       - Score de riesgo acumulativo
       - Bloqueo automático por umbral
    """

    __tablename__ = "configuraciones_antitrampa"

    # ============================================
    # 1. IDENTIFICACIÓN Y JERARQUÍA
    # ============================================
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)

    # Tipo en la jerarquía
    tipo = Column(
        String(50), nullable=False
    )  # global, institucion, curso, examen, estudiante
    nivel_seguridad = Column(
        String(50), nullable=False
    )  # bajo, medio, alto, maximo, personalizado

    # Estado
    activa = Column(Boolean, nullable=True, default=True)

    # Relaciones jerárquicas
    padre_id = Column(
        String(36), ForeignKey("configuraciones_antitrampa.id"), nullable=True
    )
    institucion_id = Column(
        String(36), ForeignKey("Institucion.institucion_id"), nullable=True
    )
    curso_id = Column(String(36), ForeignKey("Curso.curso_id"), nullable=True)
    examen_id = Column(String(36), ForeignKey("examenes.examen_id"), nullable=True)
    estudiante_id = Column(String(36), ForeignKey("Usuario.usuario_id"), nullable=True)
    creador_id = Column(String(36), ForeignKey("Usuario.usuario_id"), nullable=False)

    # ============================================
    # 2. DETECCIÓN DE NAVEGACIÓN (4 tipos)
    # ============================================
    detectar_cambio_pestana = Column(Boolean, nullable=True, default=True)
    detectar_cambio_aplicacion = Column(Boolean, nullable=True, default=True)
    detectar_cambio_ventana = Column(Boolean, nullable=True, default=True)
    detectar_salida_pantalla_completa = Column(Boolean, nullable=True, default=True)

    # Configuración de límites
    max_cambios_pestana = Column(Integer, nullable=True, default=5)

    # ============================================
    # 3. ACCIONES AUTOMÁTICAS (4 tipos)
    # ============================================
    accion_cambio_pestana = Column(
        String(50), nullable=True, default="alertar"
    )  # alertar, terminar, bloquear
    accion_inactividad = Column(
        String(50), nullable=True, default="alertar"
    )  # alertar, pausar, terminar
    accion_sesion_duplicada = Column(
        String(50), nullable=True, default="terminar"
    )  # terminar, alertar
    accion_deteccion_ia = Column(
        String(50), nullable=True, default="revisar"
    )  # revisar, invalidar, alertar

    # ============================================
    # 4. DETECCIÓN DE COMPORTAMIENTO (3 tipos)
    # ============================================
    detectar_inactividad = Column(Boolean, nullable=True, default=True)
    detectar_patron_respuesta_rapida = Column(Boolean, nullable=True, default=True)
    detectar_patron_secuencial = Column(Boolean, nullable=True, default=True)

    # Configuración de tiempos
    tiempo_max_inactividad_segundos = Column(
        Integer, nullable=True, default=300
    )  # 5 minutos
    umbral_tiempo_respuesta_segundos = Column(
        Integer, nullable=True, default=5
    )  # Mínimo 5 seg por pregunta

    # ============================================
    # 5. BLOQUEO DE FUNCIONALIDADES (8 tipos)
    # ============================================
    # Clipboard
    bloquear_copiar = Column(Boolean, nullable=True, default=False)
    bloquear_pegar = Column(Boolean, nullable=True, default=False)
    bloquear_cortar = Column(Boolean, nullable=True, default=False)

    # Pantalla
    bloquear_captura_pantalla = Column(Boolean, nullable=True, default=True)
    bloquear_segunda_pantalla = Column(Boolean, nullable=True, default=False)
    bloquear_imprimir = Column(Boolean, nullable=True, default=True)

    # Desarrollo
    bloquear_clic_derecho = Column(Boolean, nullable=True, default=False)
    bloquear_teclas_desarrollador = Column(
        Boolean, nullable=True, default=True
    )  # F12, Ctrl+Shift+I

    # ============================================
    # 6. SEGURIDAD AVANZADA (7 tipos)
    # ============================================
    detectar_multiples_sesiones = Column(Boolean, nullable=True, default=True)
    detectar_vpn = Column(Boolean, nullable=True, default=False)
    detectar_dispositivos_externos = Column(Boolean, nullable=True, default=False)
    detectar_impresoras = Column(Boolean, nullable=True, default=False)

    # Configuración de sesiones
    max_sesiones_simultaneas = Column(Integer, nullable=True, default=1)
    permitir_sesion_recuperacion = Column(Boolean, nullable=True, default=True)
    tiempo_gracia_retorno_segundos = Column(
        Integer, nullable=True, default=120
    )  # 2 minutos

    # ============================================
    # 7. CONTROL DE RED (3 campos)
    # ============================================
    monitorear_actividad_red = Column(Boolean, nullable=True, default=False)
    validar_ubicacion_ip = Column(Boolean, nullable=True, default=False)
    ips_permitidas = Column(ARRAY(String), nullable=True)  # Lista de IPs whitelisted
    rangos_ip_bloqueados = Column(
        ARRAY(String), nullable=True
    )  # Lista de rangos bloqueados

    # ============================================
    # 8. CAPTURA DE CÁMARA (5 campos)
    # ============================================
    requerir_webcam = Column(Boolean, nullable=True, default=False)
    capturar_foto_inicio = Column(Boolean, nullable=True, default=False)
    capturar_fotos_periodicas = Column(Boolean, nullable=True, default=False)
    verificar_identidad_facial = Column(Boolean, nullable=True, default=False)
    incluir_capturas_webcam = Column(Boolean, nullable=True, default=True)
    incluir_log_eventos = Column(
        Boolean, nullable=True, default=True
    )  # Incluir eventos en el log

    # Detección de anomalías en webcam
    detectar_multiples_personas = Column(Boolean, nullable=True, default=True)
    detectar_ausencia_persona = Column(Boolean, nullable=True, default=True)

    # ============================================
    # 9. GRABACIÓN COMPLETA (3 tipos)
    # ============================================
    grabar_pantalla = Column(Boolean, nullable=True, default=False)
    grabar_audio = Column(Boolean, nullable=True, default=False)
    grabar_teclas = Column(Boolean, nullable=True, default=False)  # Keylogger

    # Retención de grabaciones
    tiempo_retencion_grabaciones_dias = Column(Integer, nullable=True, default=30)

    # ============================================
    # 10. DETECCIÓN DE IA (4 campos)
    # ============================================
    detectar_ia_respuestas = Column(Boolean, nullable=True, default=False)
    umbral_deteccion_ia = Column(
        Float, nullable=True, default=0.7
    )  # 0.0-1.0 probabilidad
    tipos_pregunta_analizar_ia = Column(
        ARRAY(String), nullable=True
    )  # ["ensayo", "desarrollo", etc.]

    # ============================================
    # 11. ANÁLISIS DE PLAGIO (4 campos)
    # ============================================
    detectar_plagio = Column(Boolean, nullable=True, default=False)
    detectar_respuestas_identicas = Column(Boolean, nullable=True, default=True)
    umbral_similitud_plagio = Column(
        Float, nullable=True, default=0.8
    )  # 0.0-1.0 (80% similar)

    # Tipos de comparación
    comparar_entre_estudiantes = Column(Boolean, nullable=True, default=True)
    comparar_con_banco_respuestas = Column(Boolean, nullable=True, default=True)
    comparar_con_internet = Column(
        Boolean, nullable=True, default=False
    )  # Requiere API externa

    # ============================================
    # 12. SISTEMA DE PUNTUACIÓN (7 pesos)
    # ============================================
    peso_cambio_pestana = Column(Float, nullable=True, default=3.0)
    peso_inactividad = Column(Float, nullable=True, default=2.0)
    peso_tecla_sospechosa = Column(Float, nullable=True, default=4.0)
    peso_sesion_multiple = Column(Float, nullable=True, default=6.0)
    peso_patron_sospechoso = Column(Float, nullable=True, default=5.0)
    peso_ia_detectada = Column(Float, nullable=True, default=8.0)
    peso_plagio_detectado = Column(Float, nullable=True, default=7.0)

    # Umbral de bloqueo automático
    umbral_bloqueo_automatico = Column(
        Float, nullable=True, default=60.0
    )  # Score para bloqueo

    # ============================================
    # 13. UMBRALES ADICIONALES
    # ============================================
    umbral_confianza_facial = Column(
        Float, nullable=True, default=0.85
    )  # 85% match facial

    # ============================================
    # 14. FRECUENCIAS Y TIMERS (3 campos)
    # ============================================
    frecuencia_actualizacion_segundos = Column(
        Integer, nullable=True, default=10
    )  # Dashboard
    frecuencia_captura_minutos = Column(
        Integer, nullable=True, default=5
    )  # Fotos webcam
    frecuencia_verificacion_minutos = Column(
        Integer, nullable=True, default=2
    )  # Verificaciones

    # ============================================
    # 15. CONFIGURACIÓN AVANZADA (4 campos)
    # ============================================
    forzar_pantalla_completa = Column(Boolean, nullable=True, default=True)
    habilitar_monitoreo_tiempo_real = Column(Boolean, nullable=True, default=True)
    generar_reporte_integridad = Column(Boolean, nullable=True, default=True)
    notificar_eventos_supervisor = Column(Boolean, nullable=True, default=True)

    # ============================================
    # 16. AUDITORÍA
    # ============================================
    fecha_creacion = Column(DateTime, nullable=True, default=datetime.utcnow)
    fecha_modificacion = Column(
        DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # ============================================
    # RELATIONSHIPS
    # ============================================
    padre = relationship("ConfiguracionAntiTrampa", remote_side=[id], backref="hijas")
    creador = relationship("Usuario", foreign_keys=[creador_id])
    institucion = relationship("Institucion", backref="configuraciones_antitrampa")
    curso = relationship("Curso", backref="configuraciones_antitrampa")
    examen = relationship("Examen", backref="configuracion_antitrampa")
    estudiante = relationship(
        "Usuario",
        foreign_keys=[estudiante_id],
        backref="configuraciones_antitrampa_personales",
    )

    # ============================================
    # MÉTODOS ÚTILES
    # ============================================

    def __repr__(self) -> str:
        return f"<ConfiguracionAntiTrampa '{self.nombre}' - {self.tipo} - {self.nivel_seguridad}>"

    def calcular_score_evento(self, tipo_evento: str) -> float:
        """Calcula el peso de un evento para el score de riesgo.

        Args:
            tipo_evento: Tipo de evento detectado

        Returns:
            float: Peso del evento
        """
        pesos = {
            "cambio_pestana": self.peso_cambio_pestana or 0,
            "inactividad": self.peso_inactividad or 0,
            "tecla_sospechosa": self.peso_tecla_sospechosa or 0,
            "sesion_multiple": self.peso_sesion_multiple or 0,
            "patron_sospechoso": self.peso_patron_sospechoso or 0,
            "ia_detectada": self.peso_ia_detectada or 0,
            "plagio_detectado": self.peso_plagio_detectado or 0,
        }
        return pesos.get(tipo_evento, 0)

    def requiere_bloqueo_automatico(self, score_actual: float) -> bool:
        """Determina si el score actual requiere bloqueo automático.

        Args:
            score_actual: Score de riesgo acumulado

        Returns:
            bool: True si debe bloquearse
        """
        return score_actual >= (self.umbral_bloqueo_automatico or 60.0)

    def to_dict(self, incluir_herencia: bool = False) -> dict[str, Any]:
        """Exporta la configuración a diccionario.

        Args:
            incluir_herencia: Si True, aplica herencia del padre

        Returns:
            Dict con todos los campos de configuración
        """
        data = {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "tipo": self.tipo,
            "nivel_seguridad": self.nivel_seguridad,
            "activa": self.activa,
            # Detección navegación
            "detectar_cambio_pestana": self.detectar_cambio_pestana,
            "detectar_cambio_aplicacion": self.detectar_cambio_aplicacion,
            "detectar_cambio_ventana": self.detectar_cambio_ventana,
            "detectar_salida_pantalla_completa": self.detectar_salida_pantalla_completa,
            "max_cambios_pestana": self.max_cambios_pestana,
            # Acciones
            "accion_cambio_pestana": self.accion_cambio_pestana,
            "accion_inactividad": self.accion_inactividad,
            "accion_sesion_duplicada": self.accion_sesion_duplicada,
            "accion_deteccion_ia": self.accion_deteccion_ia,
            # Comportamiento
            "detectar_inactividad": self.detectar_inactividad,
            "detectar_patron_respuesta_rapida": self.detectar_patron_respuesta_rapida,
            "detectar_patron_secuencial": self.detectar_patron_secuencial,
            "tiempo_max_inactividad_segundos": self.tiempo_max_inactividad_segundos,
            "umbral_tiempo_respuesta_segundos": self.umbral_tiempo_respuesta_segundos,
            # Bloqueos
            "bloquear_copiar": self.bloquear_copiar,
            "bloquear_pegar": self.bloquear_pegar,
            "bloquear_cortar": self.bloquear_cortar,
            "bloquear_captura_pantalla": self.bloquear_captura_pantalla,
            "bloquear_segunda_pantalla": self.bloquear_segunda_pantalla,
            "bloquear_imprimir": self.bloquear_imprimir,
            "bloquear_clic_derecho": self.bloquear_clic_derecho,
            "bloquear_teclas_desarrollador": self.bloquear_teclas_desarrollador,
            # Seguridad
            "detectar_multiples_sesiones": self.detectar_multiples_sesiones,
            "detectar_vpn": self.detectar_vpn,
            "detectar_dispositivos_externos": self.detectar_dispositivos_externos,
            "detectar_impresoras": self.detectar_impresoras,
            "max_sesiones_simultaneas": self.max_sesiones_simultaneas,
            "permitir_sesion_recuperacion": self.permitir_sesion_recuperacion,
            "tiempo_gracia_retorno_segundos": self.tiempo_gracia_retorno_segundos,
            # Red
            "monitorear_actividad_red": self.monitorear_actividad_red,
            "validar_ubicacion_ip": self.validar_ubicacion_ip,
            "ips_permitidas": self.ips_permitidas,
            "rangos_ip_bloqueados": self.rangos_ip_bloqueados,
            # Cámara
            "requerir_webcam": self.requerir_webcam,
            "capturar_foto_inicio": self.capturar_foto_inicio,
            "capturar_fotos_periodicas": self.capturar_fotos_periodicas,
            "verificar_identidad_facial": self.verificar_identidad_facial,
            "incluir_capturas_webcam": self.incluir_capturas_webcam,
            "detectar_multiples_personas": self.detectar_multiples_personas,
            "detectar_ausencia_persona": self.detectar_ausencia_persona,
            # Grabación
            "grabar_pantalla": self.grabar_pantalla,
            "grabar_audio": self.grabar_audio,
            "grabar_teclas": self.grabar_teclas,
            "tiempo_retencion_grabaciones_dias": self.tiempo_retencion_grabaciones_dias,
            # IA
            "detectar_ia_respuestas": self.detectar_ia_respuestas,
            "umbral_deteccion_ia": self.umbral_deteccion_ia,
            "tipos_pregunta_analizar_ia": self.tipos_pregunta_analizar_ia,
            # Plagio
            "detectar_plagio": self.detectar_plagio,
            "detectar_respuestas_identicas": self.detectar_respuestas_identicas,
            "umbral_similitud_plagio": self.umbral_similitud_plagio,
            "comparar_entre_estudiantes": self.comparar_entre_estudiantes,
            "comparar_con_banco_respuestas": self.comparar_con_banco_respuestas,
            "comparar_con_internet": self.comparar_con_internet,
            # Puntuación
            "peso_cambio_pestana": self.peso_cambio_pestana,
            "peso_inactividad": self.peso_inactividad,
            "peso_tecla_sospechosa": self.peso_tecla_sospechosa,
            "peso_sesion_multiple": self.peso_sesion_multiple,
            "peso_patron_sospechoso": self.peso_patron_sospechoso,
            "peso_ia_detectada": self.peso_ia_detectada,
            "peso_plagio_detectado": self.peso_plagio_detectado,
            "umbral_bloqueo_automatico": self.umbral_bloqueo_automatico,
            "umbral_confianza_facial": self.umbral_confianza_facial,
            # Frecuencias
            "frecuencia_actualizacion_segundos": self.frecuencia_actualizacion_segundos,
            "frecuencia_captura_minutos": self.frecuencia_captura_minutos,
            "frecuencia_verificacion_minutos": self.frecuencia_verificacion_minutos,
            # Avanzado
            "forzar_pantalla_completa": self.forzar_pantalla_completa,
            "habilitar_monitoreo_tiempo_real": self.habilitar_monitoreo_tiempo_real,
            "generar_reporte_integridad": self.generar_reporte_integridad,
            "notificar_eventos_supervisor": self.notificar_eventos_supervisor,
        }

        # Aplicar herencia si se solicita
        if incluir_herencia and self.padre:
            data_padre = self.padre.to_dict(incluir_herencia=True)
            for key, valor in data_padre.items():
                if key not in data or data[key] is None:
                    data[key] = valor

        return data


class PlantillaConfiguracion(Base):
    """Plantillas predefinidas de configuración anti-trampa.

    Facilita la configuración rápida con niveles de seguridad predefinidos:
    - BAJO: Exámenes de baja criticidad
    - MEDIO: Balance entre supervisión y experiencia de usuario
    - ALTO: Evaluaciones importantes
    - MAXIMO: Certificaciones, exámenes de alto riesgo
    """

    __tablename__ = "plantillas_configuracion"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(200), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    nivel_seguridad = Column(String(50), nullable=False)

    # Referencia a la configuración base
    configuracion_id = Column(String(36), ForeignKey("configuraciones_antitrampa.id"))

    # Metadata
    es_sistema = Column(Boolean, default=False)  # Plantilla del sistema (no editable)
    es_publica = Column(Boolean, default=True)  # Visible para todas las instituciones
    veces_utilizada = Column(Integer, default=0)

    # Auditoría
    creador_id = Column(String(36), ForeignKey("Usuario.usuario_id"))
    institucion_id = Column(
        String(36), ForeignKey("Institucion.institucion_id"), nullable=True
    )
    fecha_creacion = Column(DateTime, nullable=True, default=datetime.utcnow)
    fecha_modificacion = Column(
        DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    configuracion = relationship("ConfiguracionAntiTrampa", backref="plantilla")
    creador = relationship("Usuario")
    institucion = relationship("Institucion", backref="plantillas_configuracion")

    def __repr__(self) -> str:
        return f"<PlantillaConfiguracion '{self.nombre}' - {self.nivel_seguridad}>"
