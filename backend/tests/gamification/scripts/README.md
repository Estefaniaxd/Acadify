# 🛠️ Scripts de Diagnóstico y Corrección de Tests

Esta carpeta contiene scripts automatizados para facilitar el diagnóstico, análisis y corrección de problemas en los tests de gamificación.

## 📋 Scripts Disponibles

### 1. `run_diagnostics.py` - Script Maestro
**El más recomendado para empezar**

Ejecuta todos los scripts de diagnóstico en secuencia y genera un reporte completo.

```bash
python tests/gamification/scripts/run_diagnostics.py
```

**¿Qué hace?**
- ✅ Ejecuta todos los tests
- 📊 Analiza errores encontrados
- 🔍 Busca problemas sync/async
- 📝 Genera reportes detallados

---

### 2. `run_all_tests.py` - Ejecutor de Tests con Reportes
Ejecuta todos los tests y genera un reporte visual del progreso.

```bash
# Reporte en consola
python tests/gamification/scripts/run_all_tests.py

# Reporte en consola + HTML
python tests/gamification/scripts/run_all_tests.py --html
```

**Output:**
- Estadísticas de tests (pasando/fallando)
- Barra de progreso visual
- Tiempo de ejecución
- Reporte HTML interactivo (opcional)

---

### 3. `analyze_test_errors.py` - Analizador de Errores
Analiza errores 500 y los categoriza por tipo.

```bash
# Analizar todos los tests
python tests/gamification/scripts/analyze_test_errors.py

# Analizar un archivo específico
python tests/gamification/scripts/analyze_test_errors.py test_puntos_api.py
```

**Genera:**
- `error_report.json` - Reporte detallado en JSON
- Categorización de errores:
  - Campos faltantes en modelos
  - Tablas faltantes en BD
  - Campos con nombres incorrectos
  - Problemas async/sync
  - Otros errores

---

### 4. `debug_500_errors.py` - Debug Detallado
Ejecuta cada test individualmente y captura errores 500 específicos.

```bash
python tests/gamification/scripts/debug_500_errors.py
```

**Útil para:**
- Ver exactamente qué tests fallan
- Obtener el mensaje de error específico de cada test
- Identificar patrones de errores por categoría de tests

---

### 5. `convert_sync_to_async.py` - Detector/Corrector Async
Encuentra y opcionalmente corrige problemas de código síncrono en código asíncrono.

```bash
# Solo análisis (recomendado primero)
python tests/gamification/scripts/convert_sync_to_async.py --dir src/services

# Análisis + ver cambios propuestos
python tests/gamification/scripts/convert_sync_to_async.py --dir src/services --fix --dry-run

# Aplicar correcciones automáticas
python tests/gamification/scripts/convert_sync_to_async.py --dir src/services --fix

# Analizar un archivo específico
python tests/gamification/scripts/convert_sync_to_async.py --file src/services/gamification/puntos_service.py
```

**Detecta:**
- `db.query()` en lugar de `select()`
- Llamadas a CRUD sin `await`
- `Session` en lugar de `AsyncSession`
- Funciones que deberían ser `async def`

---

## 🚀 Workflow Recomendado

### Primera Vez
```bash
# 1. Diagnóstico completo
cd backend
python tests/gamification/scripts/run_diagnostics.py

# 2. Revisar reportes generados
cat tests/gamification/scripts/error_report.json
open tests/gamification/scripts/test_report.html  # Si se generó

# 3. Aplicar correcciones automáticas (si procede)
python tests/gamification/scripts/convert_sync_to_async.py --dir src/services --fix --dry-run
python tests/gamification/scripts/convert_sync_to_async.py --dir src/services --fix

# 4. Ejecutar tests nuevamente
pytest tests/gamification/test_puntos_api.py -v
```

### Desarrollo Continuo
```bash
# Ejecutar tests con reporte
python tests/gamification/scripts/run_all_tests.py

# Si hay errores específicos, debug detallado
python tests/gamification/scripts/debug_500_errors.py

# Para errores complejos
python tests/gamification/scripts/analyze_test_errors.py
```

---

## 📊 Interpretando los Reportes

### Error Report (JSON)
```json
{
  "missing_fields": [
    {
      "model": "UsuarioInsignia",
      "field": "fecha_obtencion",
      "full_error": "..."
    }
  ],
  "missing_tables": [...],
  "invalid_fields": [...],
  "sync_issues": [...]
}
```

**Cómo usarlo:**
- `missing_fields`: Campos que no existen → Verificar modelo real
- `missing_tables`: Tablas no creadas → Agregar a `conftest.py`
- `invalid_fields`: Campos con nombre incorrecto → Buscar y reemplazar
- `sync_issues`: Código síncrono → Convertir a async

### Test Report (HTML)
Reporte visual con:
- 📊 Gráficas de progreso
- ✅ Lista de tests pasando
- ❌ Lista de tests fallando
- 📈 Tendencias (si se ejecuta múltiples veces)

---

## 🎯 Casos de Uso Comunes

### "Tengo muchos tests fallando, ¿por dónde empiezo?"
```bash
python tests/gamification/scripts/run_diagnostics.py
```
Este script te dará una visión completa y priorizará los problemas.

### "Necesito saber qué test específico está fallando"
```bash
python tests/gamification/scripts/debug_500_errors.py
```

### "Creo que tengo problemas de async/await"
```bash
python tests/gamification/scripts/convert_sync_to_async.py --dir src/services
```

### "Quiero un reporte visual para compartir"
```bash
python tests/gamification/scripts/run_all_tests.py --html
```

---

## 🔧 Personalización

Puedes modificar los scripts para:
- Cambiar directorios escaneados
- Agregar nuevos patrones de detección
- Personalizar formato de reportes
- Agregar correcciones automáticas adicionales

---

## 📝 Notas

- **Backup**: Siempre usa `--dry-run` primero antes de aplicar correcciones automáticas
- **Git**: Haz commit antes de ejecutar correcciones automáticas
- **Iterativo**: Es normal ejecutar los scripts varias veces mientras corriges
- **Combinación**: Usa los scripts en conjunto para máxima efectividad

---

## 🆘 Troubleshooting

**"ModuleNotFoundError"**
```bash
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python tests/gamification/scripts/...
```

**"Permission denied"**
```bash
chmod +x tests/gamification/scripts/*.py
```

**"Script tarda mucho"**
- Los tests completos pueden tardar 20-30 segundos
- Usa flags específicos para tests individuales

---

## 📚 Más Información

Para detalles sobre los tests de gamificación, ver:
- `tests/gamification/README.md` - Documentación de tests
- `tests/gamification/conftest.py` - Configuración de fixtures
- `src/services/gamification/` - Servicios implementados

---

**Última actualización:** 3 de noviembre de 2025
**Versión:** 1.0
**Autor:** GitHub Copilot & Team
