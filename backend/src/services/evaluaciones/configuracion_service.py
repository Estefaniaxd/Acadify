"""Servicio para gestionar configuraciones del sistema anti-trampa.
Incluye herencia jerárquica, perfiles predefinidos, plantillas, importar/exportar.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.models.evaluaciones.configuracion_antitrampa import (
    ConfiguracionAntiTrampa,
    NivelSeguridad,
    PlantillaConfiguracion,
    TipoConfiguracion,
)
from src.schemas.evaluaciones.configuracion import (
    ConfiguracionAntiTrampaCreate,
    ConfiguracionAntiTrampaUpdate,
    PerfilSeguridadResponse,
)


class ConfiguracionAntiTrampaService:
    """Servicio para gestionar configuraciones del sistema anti-trampa."""

    # ==========================================
    # PERFILES PREDEFINIDOS DEL SISTEMA
    # ==========================================

    PERFILES_SISTEMA = {
        NivelSeguridad.BAJO: {
            "nombre": "Seguridad Baja - Modo Práctico",
            "descripcion": "Para prácticas, simulacros, autoevaluaciones. Monitoreo mínimo.",
            "uso_recomendado": "Quizzes, prácticas, autoevaluación",
            "configuracion": {
                "detectar_cambio_pestana": False,
                "detectar_cambio_aplicacion": False,
                "detectar_salida_pantalla_completa": False,
                "detectar_clic_fuera_ventana": False,
                "detectar_inactividad": True,
                "tiempo_max_inactividad_minutos": 30,
                "detectar_teclas_sospechosas": False,
                "bloquear_copy_paste": False,
                "bloquear_clic_derecho": False,
                "detectar_multiples_sesiones": False,
                "detectar_respuestas_muy_rapidas": False,
                "detectar_ia_respuestas": False,
                "detectar_plagio": False,
                "requerir_webcam": False,
                "monitorear_actividad_red": False,
                "detectar_dispositivos_externos": False,
                "monitoreo_tiempo_real": False,
                "alertas_inmediatas": False,
            },
        },
        NivelSeguridad.MEDIO: {
            "nombre": "Seguridad Media - Modo Estándar",
            "descripcion": "Para evaluaciones regulares. Balance entre seguridad y usabilidad.",
            "uso_recomendado": "Exámenes parciales, tareas calificadas",
            "configuracion": {
                "detectar_cambio_pestana": True,
                "max_cambios_pestana": 5,
                "accion_exceder_cambios_pestana": "alertar",
                "detectar_cambio_aplicacion": True,
                "max_cambios_aplicacion": 3,
                "detectar_salida_pantalla_completa": True,
                "max_salidas_pantalla_completa": 2,
                "detectar_clic_fuera_ventana": True,
                "max_clics_fuera_ventana": 10,
                "detectar_inactividad": True,
                "tiempo_max_inactividad_minutos": 10,
                "accion_inactividad": "alertar",
                "detectar_teclas_sospechosas": True,
                "bloquear_copy_paste": False,
                "bloquear_clic_derecho": False,
                "detectar_multiples_sesiones": True,
                "permitir_cambio_ip": False,
                "detectar_respuestas_muy_rapidas": True,
                "tiempo_minimo_respuesta_segundos": 5,
                "detectar_patron_tiempo_uniforme": True,
                "detectar_ia_respuestas": False,
                "detectar_plagio": False,
                "requerir_webcam": False,
                "monitorear_actividad_red": False,
                "detectar_dispositivos_externos": False,
                "monitoreo_tiempo_real": True,
                "alertas_inmediatas": True,
                "enviar_notificacion_profesor": True,
            },
        },
        NivelSeguridad.ALTO: {
            "nombre": "Seguridad Alta - Modo Supervisado",
            "descripcion": "Para exámenes importantes. Monitoreo estricto con múltiples capas.",
            "uso_recomendado": "Exámenes finales, evaluaciones críticas",
            "configuracion": {
                "detectar_cambio_pestana": True,
                "max_cambios_pestana": 3,
                "accion_exceder_cambios_pestana": "bloquear",
                "detectar_cambio_aplicacion": True,
                "max_cambios_aplicacion": 2,
                "detectar_salida_pantalla_completa": True,
                "max_salidas_pantalla_completa": 1,
                "detectar_clic_fuera_ventana": True,
                "max_clics_fuera_ventana": 5,
                "detectar_inactividad": True,
                "tiempo_max_inactividad_minutos": 5,
                "accion_inactividad": "pausar",
                "detectar_teclas_sospechosas": True,
                "bloquear_copy_paste": True,
                "bloquear_clic_derecho": True,
                "bloquear_imprimir_pantalla": True,
                "detectar_multiples_sesiones": True,
                "permitir_cambio_ip": False,
                "max_cambios_ip": 0,
                "detectar_respuestas_muy_rapidas": True,
                "tiempo_minimo_respuesta_segundos": 10,
                "detectar_patron_tiempo_uniforme": True,
                "detectar_precision_velocidad_anomala": True,
                "detectar_ia_respuestas": True,
                "umbral_probabilidad_ia": 0.7,
                "detectar_plagio": True,
                "umbral_similitud_plagio": 0.75,
                "comparar_con_respuestas_previas": True,
                "comparar_entre_estudiantes_curso": True,
                "requerir_webcam": True,
                "captura_periodica_webcam": True,
                "intervalo_captura_minutos": 10,
                "detectar_multiples_personas": True,
                "detectar_ausencia_persona": True,
                "monitorear_actividad_red": False,
                "detectar_dispositivos_externos": True,
                "alertar_dispositivo_conectado": True,
                "monitoreo_tiempo_real": True,
                "alertas_inmediatas": True,
                "umbral_eventos_criticos": 2,
                "enviar_notificacion_profesor": True,
                "pausar_examen_automaticamente": False,
                "mostrar_estudiantes_en_vivo": True,
            },
        },
        NivelSeguridad.MAXIMO: {
            "nombre": "Seguridad Máxima - Modo Certificación",
            "descripcion": "Máximo nivel de seguridad. Para certificaciones y exámenes críticos.",
            "uso_recomendado": "Certificaciones profesionales, exámenes de estado",
            "configuracion": {
                "detectar_cambio_pestana": True,
                "max_cambios_pestana": 1,
                "accion_exceder_cambios_pestana": "terminar",
                "detectar_cambio_aplicacion": True,
                "max_cambios_aplicacion": 1,
                "detectar_salida_pantalla_completa": True,
                "max_salidas_pantalla_completa": 0,
                "detectar_clic_fuera_ventana": True,
                "max_clics_fuera_ventana": 3,
                "detectar_inactividad": True,
                "tiempo_max_inactividad_minutos": 3,
                "accion_inactividad": "terminar",
                "detectar_teclas_sospechosas": True,
                "bloquear_copy_paste": True,
                "bloquear_clic_derecho": True,
                "bloquear_imprimir_pantalla": True,
                "bloquear_tecla_windows": True,
                "detectar_multiples_sesiones": True,
                "permitir_cambio_ip": False,
                "max_cambios_ip": 0,
                "permitir_cambio_user_agent": False,
                "detectar_respuestas_muy_rapidas": True,
                "tiempo_minimo_respuesta_segundos": 15,
                "detectar_patron_tiempo_uniforme": True,
                "detectar_precision_velocidad_anomala": True,
                "umbral_precision_velocidad": 0.95,
                "detectar_patron_repetitivo": True,
                "detectar_ia_respuestas": True,
                "umbral_probabilidad_ia": 0.6,
                "api_deteccion_ia": "openai",
                "analizar_estilo_escritura": True,
                "comparar_estilo_previo": True,
                "detectar_plagio": True,
                "umbral_similitud_plagio": 0.7,
                "comparar_con_respuestas_previas": True,
                "comparar_entre_estudiantes_curso": True,
                "comparar_con_internet": True,
                "requerir_webcam": True,
                "captura_periodica_webcam": True,
                "intervalo_captura_minutos": 3,
                "verificar_identidad_facial": True,
                "umbral_similitud_facial": 0.9,
                "detectar_multiples_personas": True,
                "detectar_ausencia_persona": True,
                "accion_deteccion_anomalia_webcam": "terminar",
                "almacenar_capturas": True,
                "encriptar_capturas": True,
                "monitorear_actividad_red": True,
                "bloquear_todas_conexiones_externas": True,
                "detectar_dispositivos_externos": True,
                "bloquear_usb": True,
                "bloquear_bluetooth": True,
                "alertar_dispositivo_conectado": True,
                "monitoreo_tiempo_real": True,
                "alertas_inmediatas": True,
                "umbral_eventos_criticos": 1,
                "enviar_notificacion_profesor": True,
                "pausar_examen_automaticamente": True,
                "terminar_examen_automaticamente": False,
                "mostrar_estudiantes_en_vivo": True,
                "actualizar_dashboard_segundos": 5,
                "grabar_pantalla": True,
                "grabar_audio": False,
            },
        },
    }

    # ==========================================
    # CRUD BÁSICO
    # ==========================================

    @staticmethod
    def crear_configuracion(
        db: Session, config_data: ConfiguracionAntiTrampaCreate, creado_por_id: UUID
    ) -> ConfiguracionAntiTrampa:
        """Crea una nueva configuración."""
        config_dict = config_data.dict(exclude_unset=True)
        config = ConfiguracionAntiTrampa(**config_dict, creado_por_id=creado_por_id)
        db.add(config)
        db.commit()
        db.refresh(config)
        return config

    @staticmethod
    def obtener_configuracion(
        db: Session, config_id: UUID
    ) -> ConfiguracionAntiTrampa | None:
        """Obtiene una configuración por ID."""
        return (
            db.query(ConfiguracionAntiTrampa)
            .filter(ConfiguracionAntiTrampa.id == config_id)
            .first()
        )

    @staticmethod
    def actualizar_configuracion(
        db: Session, config_id: UUID, config_update: ConfiguracionAntiTrampaUpdate
    ) -> ConfiguracionAntiTrampa | None:
        """Actualiza una configuración."""
        config = (
            db.query(ConfiguracionAntiTrampa)
            .filter(ConfiguracionAntiTrampa.id == config_id)
            .first()
        )

        if not config:
            return None

        update_data = config_update.dict(exclude_unset=True)
        for campo, valor in update_data.items():
            setattr(config, campo, valor)

        db.commit()
        db.refresh(config)
        return config

    @staticmethod
    def eliminar_configuracion(db: Session, config_id: UUID) -> bool:
        """Elimina una configuración."""
        config = (
            db.query(ConfiguracionAntiTrampa)
            .filter(ConfiguracionAntiTrampa.id == config_id)
            .first()
        )

        if not config:
            return False

        db.delete(config)
        db.commit()
        return True

    # ==========================================
    # JERARQUÍA Y HERENCIA
    # ==========================================

    @staticmethod
    def obtener_configuracion_efectiva(
        db: Session, tipo: TipoConfiguracion, entidad_id: UUID
    ) -> dict[str, Any]:
        """Obtiene la configuración efectiva para una entidad.
        Aplica herencia desde global → institución → curso → examen → estudiante.
        """
        jerarquia = []
        config_actual = None

        # Buscar configuración para la entidad específica
        if tipo == TipoConfiguracion.ESTUDIANTE:
            config_actual = (
                db.query(ConfiguracionAntiTrampa)
                .filter(
                    and_(
                        ConfiguracionAntiTrampa.tipo == TipoConfiguracion.ESTUDIANTE,
                        ConfiguracionAntiTrampa.estudiante_id == entidad_id,
                        ConfiguracionAntiTrampa.es_activa,
                    )
                )
                .first()
            )
        elif tipo == TipoConfiguracion.EXAMEN:
            config_actual = (
                db.query(ConfiguracionAntiTrampa)
                .filter(
                    and_(
                        ConfiguracionAntiTrampa.tipo == TipoConfiguracion.EXAMEN,
                        ConfiguracionAntiTrampa.examen_id == entidad_id,
                        ConfiguracionAntiTrampa.es_activa,
                    )
                )
                .first()
            )
        elif tipo == TipoConfiguracion.CURSO:
            config_actual = (
                db.query(ConfiguracionAntiTrampa)
                .filter(
                    and_(
                        ConfiguracionAntiTrampa.tipo == TipoConfiguracion.CURSO,
                        ConfiguracionAntiTrampa.curso_id == entidad_id,
                        ConfiguracionAntiTrampa.es_activa,
                    )
                )
                .first()
            )
        elif tipo == TipoConfiguracion.INSTITUCION:
            config_actual = (
                db.query(ConfiguracionAntiTrampa)
                .filter(
                    and_(
                        ConfiguracionAntiTrampa.tipo == TipoConfiguracion.INSTITUCION,
                        ConfiguracionAntiTrampa.institucion_id == entidad_id,
                        ConfiguracionAntiTrampa.es_activa,
                    )
                )
                .first()
            )
        elif tipo == TipoConfiguracion.GLOBAL:
            config_actual = (
                db.query(ConfiguracionAntiTrampa)
                .filter(
                    and_(
                        ConfiguracionAntiTrampa.tipo == TipoConfiguracion.GLOBAL,
                        ConfiguracionAntiTrampa.es_activa,
                    )
                )
                .first()
            )

        # Construir jerarquía desde la configuración hasta la raíz
        temp_config = config_actual
        while temp_config:
            jerarquia.insert(
                0,
                {
                    "id": str(temp_config.id),
                    "tipo": temp_config.tipo.value,
                    "nombre": temp_config.nombre,
                    "nivel_seguridad": temp_config.nivel_seguridad.value,
                },
            )
            temp_config = temp_config.padre

        # Si no hay configuración, usar perfil MEDIO por defecto
        if not config_actual:
            perfil_default = ConfiguracionAntiTrampaService.PERFILES_SISTEMA[
                NivelSeguridad.MEDIO
            ]
            return {
                "configuracion": perfil_default["configuracion"],
                "origen_valores": dict.fromkeys(
                    perfil_default["configuracion"].keys(), "default"
                ),
                "configuracion_id": None,
                "jerarquia": [],
            }

        # Aplicar herencia: recorrer jerarquía y consolidar valores
        configuracion_final = {}
        origen_valores = {}

        for nivel_config in jerarquia:
            config_nivel = (
                db.query(ConfiguracionAntiTrampa)
                .filter(ConfiguracionAntiTrampa.id == UUID(nivel_config["id"]))
                .first()
            )

            if config_nivel:
                config_dict = config_nivel.to_dict(incluir_herencia=False)
                for campo, valor in config_dict.items():
                    if valor is not None and campo not in configuracion_final:
                        configuracion_final[campo] = valor
                        if config_nivel.id == config_actual.id:
                            origen_valores[campo] = "propio"
                        else:
                            origen_valores[campo] = (
                                f"heredado_{config_nivel.tipo.value}"
                            )

        return {
            "configuracion": configuracion_final,
            "origen_valores": origen_valores,
            "configuracion_id": str(config_actual.id),
            "jerarquia": jerarquia,
        }

    # ==========================================
    # PERFILES Y PLANTILLAS
    # ==========================================

    @staticmethod
    def obtener_perfiles_sistema() -> list[PerfilSeguridadResponse]:
        """Devuelve los perfiles predefinidos del sistema."""
        perfiles = []
        for nivel, datos in ConfiguracionAntiTrampaService.PERFILES_SISTEMA.items():
            perfiles.append(
                PerfilSeguridadResponse(
                    nivel=nivel,
                    nombre=datos["nombre"],
                    descripcion=datos["descripcion"],
                    uso_recomendado=datos["uso_recomendado"],
                    configuracion_sugerida=datos["configuracion"],
                )
            )
        return perfiles

    @staticmethod
    def aplicar_perfil(
        db: Session,
        nivel: NivelSeguridad,
        tipo: TipoConfiguracion,
        entidad_id: UUID,
        creado_por_id: UUID,
        nombre_config: str | None = None,
    ) -> ConfiguracionAntiTrampa:
        """Aplica un perfil predefinido a una entidad."""
        perfil = ConfiguracionAntiTrampaService.PERFILES_SISTEMA.get(nivel)

        if not perfil:
            msg = f"Perfil {nivel} no encontrado"
            raise ValueError(msg)

        # Crear configuración basada en el perfil
        nombre = nombre_config or f"{perfil['nombre']} - {tipo.value}"

        config_data = ConfiguracionAntiTrampaCreate(
            tipo=tipo,
            nombre=nombre,
            descripcion=perfil["descripcion"],
            nivel_seguridad=nivel,
            **perfil["configuracion"],
        )

        # Asignar IDs según el tipo
        if tipo == TipoConfiguracion.EXAMEN:
            config_data.examen_id = entidad_id
        elif tipo == TipoConfiguracion.CURSO:
            config_data.curso_id = entidad_id
        elif tipo == TipoConfiguracion.INSTITUCION:
            config_data.institucion_id = entidad_id
        elif tipo == TipoConfiguracion.ESTUDIANTE:
            config_data.estudiante_id = entidad_id

        return ConfiguracionAntiTrampaService.crear_configuracion(
            db=db, config_data=config_data, creado_por_id=creado_por_id
        )

    @staticmethod
    def crear_plantilla(
        db: Session,
        nombre: str,
        descripcion: str,
        nivel_seguridad: NivelSeguridad,
        configuracion_base: ConfiguracionAntiTrampaCreate,
        creado_por_id: UUID,
        institucion_id: UUID | None = None,
        es_publica: bool = True,
    ) -> PlantillaConfiguracion:
        """Crea una plantilla reutilizable."""
        # Crear la configuración base
        config = ConfiguracionAntiTrampaService.crear_configuracion(
            db=db, config_data=configuracion_base, creado_por_id=creado_por_id
        )

        # Marcar como plantilla
        config.es_plantilla = True
        db.commit()

        # Crear la plantilla
        plantilla = PlantillaConfiguracion(
            nombre=nombre,
            descripcion=descripcion,
            nivel_seguridad=nivel_seguridad,
            configuracion_id=config.id,
            es_publica=es_publica,
            creado_por_id=creado_por_id,
            institucion_id=institucion_id,
        )

        db.add(plantilla)
        db.commit()
        db.refresh(plantilla)
        return plantilla

    @staticmethod
    def aplicar_plantilla(
        db: Session,
        plantilla_id: UUID,
        tipo: TipoConfiguracion,
        entidad_id: UUID,
        creado_por_id: UUID,
        sobrescribir: bool = False,
    ) -> ConfiguracionAntiTrampa:
        """Aplica una plantilla a una entidad."""
        plantilla = (
            db.query(PlantillaConfiguracion)
            .filter(PlantillaConfiguracion.id == plantilla_id)
            .first()
        )

        if not plantilla:
            msg = "Plantilla no encontrada"
            raise ValueError(msg)

        # Verificar si ya existe configuración
        config_existente = None
        if tipo == TipoConfiguracion.EXAMEN:
            config_existente = (
                db.query(ConfiguracionAntiTrampa)
                .filter(
                    and_(
                        ConfiguracionAntiTrampa.tipo == tipo,
                        ConfiguracionAntiTrampa.examen_id == entidad_id,
                    )
                )
                .first()
            )
        # Similar para otros tipos...

        if config_existente and not sobrescribir:
            msg = "Ya existe configuración. Use sobrescribir=True"
            raise ValueError(msg)

        if config_existente and sobrescribir:
            db.delete(config_existente)
            db.commit()

        # Clonar configuración de la plantilla
        config_base = plantilla.configuracion.to_dict()
        config_base.pop("id", None)
        config_base.pop("creado_por_id", None)
        config_base.pop("fecha_creacion", None)
        config_base.pop("fecha_modificacion", None)

        # Asignar a la entidad
        config_base["tipo"] = tipo
        if tipo == TipoConfiguracion.EXAMEN:
            config_base["examen_id"] = entidad_id
        elif tipo == TipoConfiguracion.CURSO:
            config_base["curso_id"] = entidad_id
        elif tipo == TipoConfiguracion.INSTITUCION:
            config_base["institucion_id"] = entidad_id
        elif tipo == TipoConfiguracion.ESTUDIANTE:
            config_base["estudiante_id"] = entidad_id

        nueva_config = ConfiguracionAntiTrampa(
            **config_base, creado_por_id=creado_por_id
        )
        db.add(nueva_config)

        # Incrementar contador de uso
        plantilla.veces_utilizada += 1

        db.commit()
        db.refresh(nueva_config)
        return nueva_config

    # ==========================================
    # IMPORTAR/EXPORTAR
    # ==========================================

    @staticmethod
    def exportar_configuracion(db: Session, config_id: UUID) -> dict[str, Any]:
        """Exporta una configuración a formato JSON portable."""
        config = ConfiguracionAntiTrampaService.obtener_configuracion(db, config_id)

        if not config:
            msg = "Configuración no encontrada"
            raise ValueError(msg)

        return {
            "version": "1.0",
            "fecha_exportacion": datetime.utcnow().isoformat(),
            "configuracion": config.to_dict(),
            "metadatos": {
                "nombre": config.nombre,
                "descripcion": config.descripcion,
                "nivel_seguridad": config.nivel_seguridad.value,
                "tipo_original": config.tipo.value,
            },
        }

    @staticmethod
    def importar_configuracion(
        db: Session,
        datos_exportados: dict[str, Any],
        tipo_destino: TipoConfiguracion,
        destino_id: UUID | None,
        nombre_config: str,
        creado_por_id: UUID,
    ) -> ConfiguracionAntiTrampa:
        """Importa una configuración desde JSON exportado."""
        if datos_exportados.get("version") != "1.0":
            msg = "Versión de configuración no soportada"
            raise ValueError(msg)

        config_data = datos_exportados["configuracion"]

        # Limpiar campos no transferibles
        config_data.pop("id", None)
        config_data.pop("creado_por_id", None)
        config_data.pop("fecha_creacion", None)
        config_data.pop("fecha_modificacion", None)
        config_data["nombre"] = nombre_config
        config_data["tipo"] = tipo_destino

        # Asignar a destino
        if tipo_destino == TipoConfiguracion.EXAMEN and destino_id:
            config_data["examen_id"] = destino_id
        elif tipo_destino == TipoConfiguracion.CURSO and destino_id:
            config_data["curso_id"] = destino_id
        elif tipo_destino == TipoConfiguracion.INSTITUCION and destino_id:
            config_data["institucion_id"] = destino_id
        elif tipo_destino == TipoConfiguracion.ESTUDIANTE and destino_id:
            config_data["estudiante_id"] = destino_id

        nueva_config = ConfiguracionAntiTrampa(
            **config_data, creado_por_id=creado_por_id
        )
        db.add(nueva_config)
        db.commit()
        db.refresh(nueva_config)

        return nueva_config
