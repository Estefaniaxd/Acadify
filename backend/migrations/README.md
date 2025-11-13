# 🎯 Sistema de Misiones - Migración de Base de Datos

Este directorio contiene los scripts SQL para crear el sistema de misiones en PostgreSQL.

## 📁 Archivos

- **001_sistema_misiones.sql** - Script principal de migración
- **001_sistema_misiones_rollback.sql** - Script para revertir la migración
- **ejecutar_migracion.sh** - Script bash automático
- **README.md** - Este archivo

## 🚀 Ejecución Rápida

### Opción 1: Script Automático (Recomendado)

```bash
cd backend/migrations
chmod +x ejecutar_migracion.sh
./ejecutar_migracion.sh
```

El script lee automáticamente las credenciales desde `backend/.env` y ejecuta la migración.

### Opción 2: Manual con psql

```bash
# Desde el directorio migrations/
psql -h localhost -p 5432 -U tu_usuario -d tu_database -f 001_sistema_misiones.sql
```

### Opción 3: Desde pgAdmin o DBeaver

1. Abre el archivo `001_sistema_misiones.sql`
2. Conéctate a tu base de datos
3. Ejecuta el script completo

### Opción 4: Python con psycopg2

```python
import psycopg2
from pathlib import Path

# Conectar a la base de datos
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="acadify_db",
    user="tu_usuario",
    password="tu_password"
)

# Leer y ejecutar el script
script_path = Path("001_sistema_misiones.sql")
with open(script_path, 'r', encoding='utf-8') as f:
    sql_script = f.read()

with conn.cursor() as cur:
    cur.execute(sql_script)
    conn.commit()

print("✓ Migración completada")
conn.close()
```

## 📋 Lo que crea la migración

### 1. ENUMs (4 tipos)
- `tipo_mision`: participacion, entrega, evaluacion, racha, social, logro, puntos
- `estado_mision`: disponible, en_progreso, completada, reclamada, expirada, bloqueada
- `frecuencia_mision`: diaria, semanal, mensual, unica
- `dificultad_mision`: facil, normal, dificil, epica

### 2. Tablas (2)
- **misiones**: Definición de misiones (17 campos)
- **misiones_usuario**: Relación usuario-misión con progreso (11 campos)

### 3. Índices (12)
- Optimizados para consultas frecuentes
- Índices parciales para estados activos
- Índices compuestos para rendimiento

### 4. Funciones (3)
- `actualizar_fecha_modificacion()`: Trigger automático
- `asignar_misiones_diarias_usuario(UUID)`: Auto-asignar misiones
- `expirar_misiones_vencidas()`: Marcar misiones expiradas

### 5. Vistas (1)
- `vista_estadisticas_misiones_usuario`: Estadísticas agregadas

### 6. Datos Iniciales
- **4 misiones diarias** (asistencia, tareas, participación, racha)
- **4 misiones semanales** (estudiante dedicado, evaluación, social, puntos)
- **3 misiones mensuales** (maestro del mes, racha legendaria, evaluador)
- **4 misiones únicas** (logros especiales)

## ✅ Verificación Post-Migración

```sql
-- Ver todos los ENUMs creados
SELECT typname FROM pg_type WHERE typname LIKE '%mision%';

-- Ver todas las misiones
SELECT nombre, tipo, frecuencia, dificultad, puntos_recompensa 
FROM misiones 
ORDER BY frecuencia, orden_visualizacion;

-- Ver estadísticas de una tabla
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserciones,
    n_tup_upd as actualizaciones
FROM pg_stat_user_tables 
WHERE tablename IN ('misiones', 'misiones_usuario');

-- Probar función de asignación
SELECT asignar_misiones_diarias_usuario('UUID_DEL_USUARIO');
```

## 🔄 Rollback (Revertir Migración)

**⚠️ ADVERTENCIA**: Esto eliminará TODOS los datos de misiones.

```bash
psql -h localhost -p 5432 -U tu_usuario -d tu_database -f 001_sistema_misiones_rollback.sql
```

## 🛠️ Troubleshooting

### Error: "role does not exist"
```bash
# Crear el usuario si no existe
sudo -u postgres psql -c "CREATE USER tu_usuario WITH PASSWORD 'tu_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tu_database TO tu_usuario;"
```

### Error: "database does not exist"
```bash
# Crear la base de datos
sudo -u postgres psql -c "CREATE DATABASE tu_database OWNER tu_usuario;"
```

### Error: "permission denied"
```bash
# Dar permisos al usuario
sudo -u postgres psql tu_database -c "GRANT ALL ON SCHEMA public TO tu_usuario;"
```

### Error: "type already exists"
El script maneja esto automáticamente con `DO $$ BEGIN ... EXCEPTION`. No es un error crítico.

## 📊 Consultas Útiles

```sql
-- Ver todas las misiones agrupadas por frecuencia
SELECT 
    frecuencia,
    COUNT(*) as total,
    AVG(puntos_recompensa) as puntos_promedio
FROM misiones
WHERE es_activa = true
GROUP BY frecuencia;

-- Ver progreso de un usuario
SELECT 
    m.nombre,
    mu.estado,
    mu.progreso_actual,
    m.objetivo,
    ROUND((mu.progreso_actual::DECIMAL / m.objetivo) * 100, 2) as porcentaje
FROM misiones_usuario mu
JOIN misiones m ON mu.mision_id = m.mision_id
WHERE mu.usuario_id = 'UUID_USUARIO'
ORDER BY mu.fecha_asignacion DESC;

-- Estadísticas globales
SELECT * FROM vista_estadisticas_misiones_usuario
WHERE usuario_id = 'UUID_USUARIO';
```

## 🔐 Variables de Entorno

Asegúrate de tener en `backend/.env`:

```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/acadify_db
```

O las variables individuales:

```env
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=acadify_db
```

## 📝 Notas

- El script es **idempotente**: puedes ejecutarlo múltiples veces sin problemas
- Usa `ON CONFLICT DO NOTHING` para datos de ejemplo
- Los ENUMs se crean con bloques `DO $$ BEGIN ... EXCEPTION`
- Todos los UUIDs se generan automáticamente con `gen_random_uuid()`
- Las fechas usan `TIMESTAMP WITH TIME ZONE` para manejar zonas horarias

## 🎓 Comandos de Mantenimiento

```sql
-- Expirar misiones vencidas manualmente
SELECT expirar_misiones_vencidas();

-- Asignar misiones diarias a un usuario
SELECT asignar_misiones_diarias_usuario('uuid-del-usuario');

-- Limpiar misiones antiguas (30+ días)
DELETE FROM misiones_usuario 
WHERE fecha_asignacion < CURRENT_TIMESTAMP - INTERVAL '30 days'
AND estado IN ('expirada', 'reclamada');

-- Ver rendimiento de índices
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
AND tablename IN ('misiones', 'misiones_usuario')
ORDER BY idx_scan DESC;
```

## 🆘 Soporte

Si encuentras problemas:

1. Verifica que PostgreSQL esté corriendo: `sudo systemctl status postgresql`
2. Revisa los logs: `sudo tail -f /var/log/postgresql/postgresql-*.log`
3. Verifica permisos del usuario
4. Asegúrate de tener la extensión `uuid-ossp` o usar `gen_random_uuid()`

---

**Autor**: Sistema de Gamificación Acadify  
**Fecha**: 2025-11-09  
**Versión**: 1.0.0
