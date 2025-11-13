"""add complete gamification system with raw SQL

Revision ID: 004_gamification_sql
Revises: 736229add923
Create Date: 2025-11-02 20:35:00.000000

Crea el sistema completo de gamificación usando SQL directo para evitar conflictos con SQLAlchemy
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '004_gamification_sql'
down_revision = '736229add923'
branch_labels = None
depends_on = None


def upgrade():
    """Crea sistema completo de gamificación con SQL puro"""
    
    print("\n🎮 ===============================================")
    print("   SISTEMA DE GAMIFICACIÓN - INSTALACIÓN")
    print("===============================================\n")
    
    # ========== PASO 1: CREAR ENUMS ==========
    print("🎨 Paso 1/9: Creando enums...")
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE categoria_etiqueta_enum AS ENUM (
                'matematicas', 'ciencias', 'programacion', 'idiomas',
                'literatura', 'historia', 'arte', 'musica',
                'lectura', 'escritura', 'investigacion', 'pensamiento_critico',
                'creatividad', 'liderazgo',
                'logro_tareas', 'logro_examenes', 'participacion', 'colaboracion',
                'racha', 'ranking', 'evento', 'especial'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE rareza_enum AS ENUM ('comun', 'raro', 'epico', 'legendario');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE categoria_item_enum AS ENUM (
                'avatar_cabeza', 'avatar_torso', 'avatar_piernas', 'avatar_zapatos',
                'avatar_accesorios', 'avatar_conjunto',
                'foto_perfil', 'foto_portada', 'marco_perfil', 'efecto_perfil',
                'tema_chat', 'sticker', 'emoji_personalizado',
                'multiplicador_puntos', 'proteccion_racha', 'desbloquear_contenido',
                'boost_experiencia', 'evento', 'limitado', 'exclusivo'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE tipo_item_enum AS ENUM ('avatar', 'cosmetic', 'consumible', 'permanente', 'temporal');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE tipo_racha_enum AS ENUM ('diaria', 'semanal', 'mensual', 'personalizada');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    print("   ✅ 5 enums creados\n")
    
    # ========== PASO 2: TABLA ETIQUETAS_PERFIL ==========
    print("📋 Paso 2/9: Tabla etiquetas_perfil...")
    op.execute("""
        CREATE TABLE IF NOT EXISTS etiquetas_perfil (
            etiqueta_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            nombre VARCHAR(100) NOT NULL UNIQUE,
            descripcion VARCHAR(500),
            categoria categoria_etiqueta_enum NOT NULL,
            rareza rareza_enum NOT NULL,
            icono_url VARCHAR(500),
            color_hex VARCHAR(7),
            animacion_url VARCHAR(500),
            precio_puntos INTEGER,
            es_comprable BOOLEAN NOT NULL DEFAULT true,
            requisito_logro JSON,
            etiqueta_evolucion_id UUID REFERENCES etiquetas_perfil(etiqueta_id) ON DELETE SET NULL,
            requisito_evolucion JSON,
            es_activa BOOLEAN NOT NULL DEFAULT true,
            orden INTEGER NOT NULL DEFAULT 0,
            fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT check_etiqueta_precio_positivo CHECK (precio_puntos IS NULL OR precio_puntos >= 0),
            CONSTRAINT check_etiqueta_comprable_tiene_precio CHECK (NOT (es_comprable = true AND precio_puntos IS NULL))
        );
        CREATE INDEX IF NOT EXISTS idx_etiqueta_categoria ON etiquetas_perfil(categoria);
        CREATE INDEX IF NOT EXISTS idx_etiqueta_rareza ON etiquetas_perfil(rareza);
        CREATE INDEX IF NOT EXISTS idx_etiqueta_activa ON etiquetas_perfil(es_activa);
        CREATE INDEX IF NOT EXISTS idx_etiqueta_comprable ON etiquetas_perfil(es_comprable);
    """)
    print("   ✅ Tabla + 4 índices\n")
    
    # ========== PASO 3: TABLA USUARIO_ETIQUETA ==========
    print("👤 Paso 3/9: Tabla usuario_etiqueta...")
    op.execute("""
        CREATE TABLE IF NOT EXISTS usuario_etiqueta (
            usuario_etiqueta_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            usuario_id UUID NOT NULL REFERENCES "Usuario"(usuario_id) ON DELETE CASCADE,
            etiqueta_id UUID NOT NULL REFERENCES etiquetas_perfil(etiqueta_id) ON DELETE CASCADE,
            fecha_obtencion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            metodo_obtencion VARCHAR(50) NOT NULL DEFAULT 'compra',
            puntos_gastados INTEGER,
            esta_equipada BOOLEAN NOT NULL DEFAULT false,
            orden_visualizacion INTEGER,
            fecha_equipamiento TIMESTAMP WITH TIME ZONE,
            progreso_evolucion JSON,
            puede_evolucionar BOOLEAN NOT NULL DEFAULT false,
            veces_equipada INTEGER NOT NULL DEFAULT 0,
            fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT uq_usuario_etiqueta UNIQUE (usuario_id, etiqueta_id),
            CONSTRAINT check_orden_visualizacion_valido CHECK (orden_visualizacion IS NULL OR (orden_visualizacion >= 1 AND orden_visualizacion <= 5)),
            CONSTRAINT check_equipada_tiene_orden CHECK (NOT (esta_equipada = true AND orden_visualizacion IS NULL)),
            CONSTRAINT check_puntos_gastados_positivo CHECK (puntos_gastados IS NULL OR puntos_gastados >= 0)
        );
        CREATE INDEX IF NOT EXISTS idx_usuario_etiqueta_usuario ON usuario_etiqueta(usuario_id);
        CREATE INDEX IF NOT EXISTS idx_usuario_etiqueta_etiqueta ON usuario_etiqueta(etiqueta_id);
        CREATE INDEX IF NOT EXISTS idx_usuario_etiqueta_equipada ON usuario_etiqueta(usuario_id, esta_equipada);
    """)
    print("   ✅ Tabla + 3 índices\n")
    
    # ========== PASO 4: TABLA TIENDA_ITEM ==========
    print("🛍️  Paso 4/9: Tabla tienda_item...")
    op.execute("""
        CREATE TABLE IF NOT EXISTS tienda_item (
            item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            nombre VARCHAR(100) NOT NULL UNIQUE,
            descripcion VARCHAR(500),
            categoria categoria_item_enum NOT NULL,
            tipo tipo_item_enum NOT NULL,
            rareza rareza_enum NOT NULL,
            imagen_url VARCHAR(500),
            imagen_preview_url VARCHAR(500),
            icono_url VARCHAR(500),
            color_hex VARCHAR(7),
            precio_puntos INTEGER NOT NULL,
            precio_original INTEGER,
            descuento_porcentaje INTEGER,
            es_disponible BOOLEAN NOT NULL DEFAULT true,
            stock_limitado BOOLEAN NOT NULL DEFAULT false,
            stock_actual INTEGER,
            max_por_usuario INTEGER,
            es_limitado BOOLEAN NOT NULL DEFAULT false,
            fecha_inicio TIMESTAMP WITH TIME ZONE,
            fecha_fin TIMESTAMP WITH TIME ZONE,
            nivel_minimo INTEGER,
            requisito_logro JSON,
            avatar_asset_id UUID REFERENCES avatar_asset(id) ON DELETE SET NULL,
            recompensa_id UUID REFERENCES "Recompensa"(recompensa_id) ON DELETE SET NULL,
            duracion_dias INTEGER,
            efecto_json JSON,
            veces_comprado INTEGER NOT NULL DEFAULT 0,
            popularidad INTEGER NOT NULL DEFAULT 0,
            orden INTEGER NOT NULL DEFAULT 0,
            es_destacado BOOLEAN NOT NULL DEFAULT false,
            es_nuevo BOOLEAN NOT NULL DEFAULT false,
            fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT check_item_precio_positivo CHECK (precio_puntos >= 0),
            CONSTRAINT check_item_precio_original_mayor CHECK (precio_original IS NULL OR precio_original >= precio_puntos),
            CONSTRAINT check_item_descuento_valido CHECK (descuento_porcentaje IS NULL OR (descuento_porcentaje >= 0 AND descuento_porcentaje <= 100)),
            CONSTRAINT check_item_stock_positivo CHECK (stock_actual IS NULL OR stock_actual >= 0),
            CONSTRAINT check_item_max_usuario_positivo CHECK (max_por_usuario IS NULL OR max_por_usuario > 0),
            CONSTRAINT check_item_duracion_positiva CHECK (duracion_dias IS NULL OR duracion_dias > 0)
        );
        CREATE INDEX IF NOT EXISTS idx_tienda_item_categoria ON tienda_item(categoria);
        CREATE INDEX IF NOT EXISTS idx_tienda_item_tipo ON tienda_item(tipo);
        CREATE INDEX IF NOT EXISTS idx_tienda_item_rareza ON tienda_item(rareza);
        CREATE INDEX IF NOT EXISTS idx_tienda_item_disponible ON tienda_item(es_disponible);
        CREATE INDEX IF NOT EXISTS idx_tienda_item_destacado ON tienda_item(es_destacado);
    """)
    print("   ✅ Tabla + 5 índices\n")
    
    # ========== PASO 5: TABLA TRANSACCION_TIENDA ==========
    print("💰 Paso 5/9: Tabla transaccion_tienda...")
    op.execute("""
        CREATE TABLE IF NOT EXISTS transaccion_tienda (
            transaccion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            usuario_id UUID NOT NULL REFERENCES "Usuario"(usuario_id) ON DELETE CASCADE,
            item_id UUID NOT NULL REFERENCES tienda_item(item_id) ON DELETE CASCADE,
            tipo_transaccion VARCHAR(20) NOT NULL DEFAULT 'compra',
            cantidad INTEGER NOT NULL DEFAULT 1,
            puntos_gastados INTEGER NOT NULL,
            puntos_antes INTEGER NOT NULL,
            puntos_despues INTEGER NOT NULL,
            destinatario_id UUID REFERENCES "Usuario"(usuario_id) ON DELETE SET NULL,
            mensaje_regalo VARCHAR(500),
            estado VARCHAR(20) NOT NULL DEFAULT 'completada',
            fecha_transaccion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            metadata_json JSON,
            ip_address VARCHAR(45),
            CONSTRAINT check_transaccion_cantidad_positiva CHECK (cantidad > 0),
            CONSTRAINT check_transaccion_puntos_positivo CHECK (puntos_gastados >= 0),
            CONSTRAINT check_transaccion_puntos_antes_positivo CHECK (puntos_antes >= 0),
            CONSTRAINT check_transaccion_puntos_despues_positivo CHECK (puntos_despues >= 0)
        );
        CREATE INDEX IF NOT EXISTS idx_transaccion_usuario ON transaccion_tienda(usuario_id);
        CREATE INDEX IF NOT EXISTS idx_transaccion_item ON transaccion_tienda(item_id);
        CREATE INDEX IF NOT EXISTS idx_transaccion_fecha ON transaccion_tienda(fecha_transaccion);
    """)
    print("   ✅ Tabla + 3 índices\n")
    
    # ========== PASO 6: TABLA INVENTARIO_USUARIO ==========
    print("🎒 Paso 6/9: Tabla inventario_usuario...")
    op.execute("""
        CREATE TABLE IF NOT EXISTS inventario_usuario (
            inventario_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            usuario_id UUID NOT NULL REFERENCES "Usuario"(usuario_id) ON DELETE CASCADE,
            item_id UUID NOT NULL REFERENCES tienda_item(item_id) ON DELETE CASCADE,
            fecha_compra TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            puntos_gastados INTEGER NOT NULL,
            transaccion_id UUID REFERENCES transaccion_tienda(transaccion_id) ON DELETE SET NULL,
            esta_equipado BOOLEAN NOT NULL DEFAULT false,
            fecha_equipamiento TIMESTAMP WITH TIME ZONE,
            cantidad INTEGER NOT NULL DEFAULT 1,
            esta_consumido BOOLEAN NOT NULL DEFAULT false,
            fecha_consumo TIMESTAMP WITH TIME ZONE,
            fecha_expiracion TIMESTAMP WITH TIME ZONE,
            esta_expirado BOOLEAN NOT NULL DEFAULT false,
            veces_usado INTEGER NOT NULL DEFAULT 0,
            fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT check_inventario_cantidad_positiva CHECK (cantidad > 0),
            CONSTRAINT check_inventario_puntos_positivo CHECK (puntos_gastados >= 0),
            CONSTRAINT check_inventario_usos_positivo CHECK (veces_usado >= 0)
        );
        CREATE INDEX IF NOT EXISTS idx_inventario_usuario ON inventario_usuario(usuario_id);
        CREATE INDEX IF NOT EXISTS idx_inventario_item ON inventario_usuario(item_id);
        CREATE INDEX IF NOT EXISTS idx_inventario_equipado ON inventario_usuario(usuario_id, esta_equipado);
    """)
    print("   ✅ Tabla + 3 índices\n")
    
    # ========== PASO 7: TABLA RACHA_USUARIO ==========
    print("🔥 Paso 7/9: Tabla racha_usuario...")
    op.execute("""
        CREATE TABLE IF NOT EXISTS racha_usuario (
            racha_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            usuario_id UUID NOT NULL REFERENCES "Usuario"(usuario_id) ON DELETE CASCADE,
            tipo tipo_racha_enum NOT NULL DEFAULT 'diaria',
            racha_actual INTEGER NOT NULL DEFAULT 0,
            racha_maxima INTEGER NOT NULL DEFAULT 0,
            fecha_inicio_racha TIMESTAMP WITH TIME ZONE,
            ultima_actividad TIMESTAMP WITH TIME ZONE,
            proxima_actividad_requerida TIMESTAMP WITH TIME ZONE,
            esta_activa BOOLEAN NOT NULL DEFAULT true,
            esta_congelada BOOLEAN NOT NULL DEFAULT false,
            fecha_congelacion TIMESTAMP WITH TIME ZONE,
            dias_congelacion_restantes INTEGER NOT NULL DEFAULT 0,
            notificacion_enviada BOOLEAN NOT NULL DEFAULT false,
            hora_notificacion_preferida TIME,
            total_activaciones INTEGER NOT NULL DEFAULT 0,
            total_congelaciones_usadas INTEGER NOT NULL DEFAULT 0,
            total_rachas_perdidas INTEGER NOT NULL DEFAULT 0,
            milestones_alcanzados INTEGER[],
            ultimo_milestone INTEGER,
            fecha_ultimo_milestone TIMESTAMP WITH TIME ZONE,
            fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT uq_racha_usuario_tipo UNIQUE (usuario_id, tipo),
            CONSTRAINT check_racha_actual_positiva CHECK (racha_actual >= 0),
            CONSTRAINT check_racha_maxima_positiva CHECK (racha_maxima >= 0),
            CONSTRAINT check_racha_actual_menor_maxima CHECK (racha_actual <= racha_maxima),
            CONSTRAINT check_dias_congelacion_positivo CHECK (dias_congelacion_restantes >= 0)
        );
        CREATE INDEX IF NOT EXISTS idx_racha_usuario ON racha_usuario(usuario_id);
        CREATE INDEX IF NOT EXISTS idx_racha_tipo ON racha_usuario(tipo);
        CREATE INDEX IF NOT EXISTS idx_racha_activa ON racha_usuario(esta_activa);
        CREATE INDEX IF NOT EXISTS idx_racha_proxima_actividad ON racha_usuario(proxima_actividad_requerida);
    """)
    print("   ✅ Tabla + 4 índices\n")
    
    # ========== PASO 8: TABLA RECOMPENSA_RACHA ==========
    print("🎁 Paso 8/9: Tabla recompensa_racha...")
    op.execute("""
        CREATE TABLE IF NOT EXISTS recompensa_racha (
            recompensa_racha_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            milestone_dias INTEGER NOT NULL,
            tipo_racha tipo_racha_enum NOT NULL DEFAULT 'diaria',
            nombre VARCHAR(100) NOT NULL,
            descripcion VARCHAR(500),
            icono_url VARCHAR(500),
            imagen_url VARCHAR(500),
            puntos_otorgados INTEGER NOT NULL DEFAULT 0,
            dias_congelacion INTEGER NOT NULL DEFAULT 0,
            insignia_id UUID REFERENCES "Insignia"(insignia_id) ON DELETE SET NULL,
            item_tienda_id UUID REFERENCES tienda_item(item_id) ON DELETE SET NULL,
            etiqueta_id UUID REFERENCES etiquetas_perfil(etiqueta_id) ON DELETE SET NULL,
            multiplica_puntos_porcentaje INTEGER,
            duracion_multiplicador_dias INTEGER,
            es_activa BOOLEAN NOT NULL DEFAULT true,
            orden INTEGER NOT NULL DEFAULT 0,
            veces_otorgada INTEGER NOT NULL DEFAULT 0,
            fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT uq_recompensa_milestone UNIQUE (milestone_dias, tipo_racha),
            CONSTRAINT check_milestone_positivo CHECK (milestone_dias > 0),
            CONSTRAINT check_puntos_otorgados_positivo CHECK (puntos_otorgados >= 0),
            CONSTRAINT check_dias_congelacion_recompensa_positivo CHECK (dias_congelacion >= 0)
        );
        CREATE INDEX IF NOT EXISTS idx_recompensa_racha_milestone ON recompensa_racha(milestone_dias);
        CREATE INDEX IF NOT EXISTS idx_recompensa_racha_tipo ON recompensa_racha(tipo_racha);
        CREATE INDEX IF NOT EXISTS idx_recompensa_racha_activa ON recompensa_racha(es_activa);
    """)
    print("   ✅ Tabla + 3 índices\n")
    
    # ========== PASO 9: TABLA HISTORIAL_RACHA ==========
    print("📊 Paso 9/9: Tabla historial_racha...")
    op.execute("""
        CREATE TABLE IF NOT EXISTS historial_racha (
            historial_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            racha_id UUID NOT NULL REFERENCES racha_usuario(racha_id) ON DELETE CASCADE,
            usuario_id UUID NOT NULL REFERENCES "Usuario"(usuario_id) ON DELETE CASCADE,
            tipo_evento VARCHAR(50) NOT NULL,
            fecha_evento TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            racha_antes INTEGER NOT NULL,
            racha_despues INTEGER NOT NULL,
            milestone_alcanzado INTEGER,
            puntos_ganados INTEGER,
            recompensa_id UUID REFERENCES recompensa_racha(recompensa_racha_id) ON DELETE SET NULL,
            metadata_json JSON,
            ip_address VARCHAR(45),
            CONSTRAINT check_hist_racha_antes_positiva CHECK (racha_antes >= 0),
            CONSTRAINT check_hist_racha_despues_positiva CHECK (racha_despues >= 0),
            CONSTRAINT check_hist_puntos_positivo CHECK (puntos_ganados IS NULL OR puntos_ganados >= 0)
        );
        CREATE INDEX IF NOT EXISTS idx_historial_racha ON historial_racha(racha_id);
        CREATE INDEX IF NOT EXISTS idx_historial_usuario ON historial_racha(usuario_id);
        CREATE INDEX IF NOT EXISTS idx_historial_fecha ON historial_racha(fecha_evento);
    """)
    print("   ✅ Tabla + 3 índices\n")
    
    # ========== DATOS INICIALES ==========
    print("🌱 Insertando datos iniciales...")
    op.execute("""
        INSERT INTO recompensa_racha (milestone_dias, tipo_racha, nombre, descripcion, puntos_otorgados, dias_congelacion, orden)
        VALUES
            (3, 'diaria', '3 Días Seguidos', 'Mantuviste tu racha por 3 días consecutivos', 50, 1, 1),
            (7, 'diaria', '¡1 Semana!', 'Una semana completa de actividad', 150, 2, 2),
            (14, 'diaria', '2 Semanas Imparable', 'Dos semanas de dedicación continua', 350, 3, 3),
            (30, 'diaria', '¡Un Mes!', 'Un mes entero manteniendo tu racha', 1000, 5, 4),
            (60, 'diaria', '2 Meses Maestro', 'Dos meses de constancia increíble', 2500, 7, 5),
            (100, 'diaria', '¡100 Días!', 'Alcanzaste el hito de 100 días consecutivos', 5000, 10, 6),
            (365, 'diaria', '¡Un Año Completo!', 'Has mantenido tu racha por un año entero', 20000, 30, 7)
        ON CONFLICT DO NOTHING;
    """)
    print("   ✅ 7 recompensas de milestone\n")
    
    print("=" * 50)
    print("✨ SISTEMA DE GAMIFICACIÓN INSTALADO EXITOSAMENTE!")
    print("=" * 50)
    print("\n📊 Resumen:")
    print("   • 5 enums creados")
    print("   • 8 tablas creadas:")
    print("     - etiquetas_perfil + usuario_etiqueta")
    print("     - tienda_item + transaccion_tienda + inventario_usuario")
    print("     - racha_usuario + historial_racha + recompensa_racha")
    print("   • 28 índices para optimización")
    print("   • 7 recompensas de milestone predefinidas")
    print("\n🎮 ¡Listo para usar!\n")


def downgrade():
    """Elimina el sistema completo de gamificación"""
    
    print("\n🗑️  ELIMINANDO SISTEMA DE GAMIFICACIÓN...\n")
    
    op.execute("""
        DROP TABLE IF EXISTS historial_racha CASCADE;
        DROP TABLE IF EXISTS recompensa_racha CASCADE;
        DROP TABLE IF EXISTS racha_usuario CASCADE;
        DROP TABLE IF EXISTS inventario_usuario CASCADE;
        DROP TABLE IF EXISTS transaccion_tienda CASCADE;
        DROP TABLE IF EXISTS tienda_item CASCADE;
        DROP TABLE IF EXISTS usuario_etiqueta CASCADE;
        DROP TABLE IF EXISTS etiquetas_perfil CASCADE;
        
        DROP TYPE IF EXISTS tipo_racha_enum CASCADE;
        DROP TYPE IF EXISTS tipo_item_enum CASCADE;
        DROP TYPE IF EXISTS categoria_item_enum CASCADE;
        DROP TYPE IF EXISTS rareza_enum CASCADE;
        DROP TYPE IF EXISTS categoria_etiqueta_enum CASCADE;
    """)
    
    print("✅ Sistema de gamificación eliminado\n")
