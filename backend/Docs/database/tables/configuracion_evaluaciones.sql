-- =====================================================
-- Tabla: configuracion_evaluaciones
-- =====================================================

CREATE TABLE IF NOT EXISTS configuracion_evaluaciones (
    config_id character varying NOT NULL,
    tiempo_gracia_segundos integer DEFAULT 300,
    maximo_intentos_globales integer DEFAULT 5,
    tiempo_minimo_entre_intentos integer DEFAULT 3600,
    max_cambios_pestana_permitidos integer DEFAULT 5,
    tiempo_max_inactividad_global integer DEFAULT 1800,
    habilitar_deteccion_copia_texto boolean DEFAULT true,
    habilitar_deteccion_pantalla_completa boolean DEFAULT true,
    algoritmo_calificacion_ensayos character varying(100) DEFAULT 'keyword_matching'::character varying,
    umbral_similitud_plagio double precision DEFAULT '0.8'::double precision,
    habilitar_feedback_automatico boolean DEFAULT true,
    notificar_intento_finalizado boolean DEFAULT true,
    notificar_resultado_disponible boolean DEFAULT true,
    notificar_tiempo_restante boolean DEFAULT true,
    tiempo_notificacion_previa_minutos integer DEFAULT 10,
    guardar_progreso_cada_segundos integer DEFAULT 30,
    habilitar_recuperacion_sesion boolean DEFAULT true,
    tiempo_expiracion_backup_horas integer DEFAULT 72,
    institucion_id character varying,
    aplicar_globalmente boolean DEFAULT true,
    creado_por character varying NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone
,
    PRIMARY KEY (config_id)
);

-- Check Constraints de configuracion_evaluaciones
ALTER TABLE configuracion_evaluaciones ADD CONSTRAINT 39558_40867_1_not_null CHECK (config_id IS NOT NULL);
ALTER TABLE configuracion_evaluaciones ADD CONSTRAINT 39558_40867_21_not_null CHECK (creado_por IS NOT NULL);
