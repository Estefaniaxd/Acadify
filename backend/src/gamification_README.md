# 🎮 Sistema de Gamificación Acadify

Sistema completo de gamificación educativa con puntos, rachas, badges y tienda virtual.

---

## 🚀 Quick Start

### 1. Instalar Dependencias

```bash
# Ya incluidas en requirements.txt del proyecto
pip install fastapi sqlalchemy alembic pydantic asyncpg
```

### 2. Ejecutar Migraciones

```bash
# Aplicar migraciones de gamificación
alembic upgrade head
```

### 3. Usar APIs

```python
# Ejemplo: Calificar tarea con gamificación automática
POST /api/v1/cursos/tareas/entregas/{entrega_id}/calificar
{
  "calificacion": 85,
  "comentarios": "Buen trabajo!"
}

# Respuesta incluye:
# - Calificación registrada
# - Puntos otorgados (con bonos)
# - Racha actualizada
# - Milestones alcanzados
```

---

## 📁 Estructura

```
src/
├── enums/gamification/          # Enums del sistema
│   ├── tienda_enums.py          # CategoriaItem, RarezaItem
│   ├── etiqueta_enums.py        # CategoriaEtiqueta, RarezaEtiqueta
│   └── racha_enums.py           # TipoEventoRacha, TipoMilestone
│
├── models/gamification/         # Modelos SQLAlchemy
│   ├── tienda_item.py           # Items de tienda
│   ├── inventario_usuario.py   # Inventario
│   ├── transaccion_tienda.py   # Transacciones
│   ├── etiqueta_perfil.py       # Badges
│   ├── usuario_etiqueta.py      # Badges del usuario
│   ├── historial_racha.py       # Log de rachas
│   ├── recompensa_racha.py      # Milestones
│   └── racha_usuario.py         # Racha actual (expandido)
│
├── services/gamification/       # Lógica de negocio
│   ├── puntos_service.py        # Gestión de puntos
│   ├── tienda_service.py        # Tienda virtual
│   ├── etiquetas_service.py     # Sistema de badges
│   └── racha_service.py         # Rachas Duolingo-style
│
├── schemas/gamification/        # Validación Pydantic
│   ├── tienda.py                # Schemas de tienda
│   ├── etiquetas.py             # Schemas de badges
│   └── rachas.py                # Schemas de rachas
│
└── api/v1/endpoints/gamification/  # REST APIs
    ├── tienda.py                # 11 endpoints de tienda
    ├── etiquetas.py             # 12 endpoints de badges
    └── rachas.py                # 10 endpoints de rachas
```

---

## 🎯 Funcionalidades

### 💰 Sistema de Puntos
- ✅ Múltiples fuentes (tareas, exámenes, rachas, participación)
- ✅ Bonos por calidad y rapidez
- ✅ Penalizaciones configurables
- ✅ Historial completo
- ✅ Economía balanceada

### 🏪 Tienda Virtual
- ✅ Items de ropa para avatares
- ✅ Badges comprables
- ✅ Items funcionales (congeladores, recuperadores)
- ✅ Sistema de rareza (Común, Raro, Épico, Legendario)
- ✅ Inventario con cantidades
- ✅ Equipamiento único por categoría
- ✅ Transacciones auditables

### 🏅 Sistema de Badges
- ✅ 22 categorías (académicas, habilidades, logros)
- ✅ 4 niveles de rareza
- ✅ Sistema de evolución (cadena de 3 niveles)
- ✅ Equipamiento máximo 5 badges
- ✅ Requisitos personalizados (JSON)
- ✅ Progreso trackeable

### 🔥 Rachas (Estilo Duolingo)
- ✅ Verificación diaria automática
- ✅ Recompensas semanales progresivas (10-50 pts/día)
- ✅ Milestones (7, 30, 100, 365 días)
- ✅ Sistema de protección (congeladores)
- ✅ Recuperación de rachas
- ✅ Ranking global
- ✅ Historial completo

---

## 📊 APIs Disponibles

### Tienda

```bash
GET    /api/v1/tienda/items                  # Catálogo
GET    /api/v1/tienda/items/{id}             # Detalle
POST   /api/v1/tienda/comprar                # Comprar
GET    /api/v1/tienda/inventario             # Ver inventario
POST   /api/v1/tienda/equipar                # Equipar item
POST   /api/v1/tienda/desequipar/{id}        # Desequipar
POST   /api/v1/tienda/usar                   # Usar consumible
GET    /api/v1/tienda/transacciones          # Historial
GET    /api/v1/tienda/estadisticas           # Stats
```

### Etiquetas (Badges)

```bash
GET    /api/v1/etiquetas/disponibles         # Catálogo
GET    /api/v1/etiquetas/disponibles/{id}    # Detalle
GET    /api/v1/etiquetas/mis-etiquetas       # Mis badges
POST   /api/v1/etiquetas/comprar             # Comprar
POST   /api/v1/etiquetas/equipar             # Equipar (max 5)
POST   /api/v1/etiquetas/desequipar/{id}     # Desequipar
GET    /api/v1/etiquetas/progreso/{id}       # Ver progreso
POST   /api/v1/etiquetas/evolucionar         # Evolucionar
GET    /api/v1/etiquetas/top-usuarios/{id}   # Ranking
```

### Rachas

```bash
GET    /api/v1/rachas/mi-racha               # Ver racha
POST   /api/v1/rachas/verificar              # Verificar diaria
POST   /api/v1/rachas/recuperar              # Recuperar
POST   /api/v1/rachas/congelar               # Activar protección
GET    /api/v1/rachas/historial              # Historial
GET    /api/v1/rachas/milestones             # Milestones
GET    /api/v1/rachas/estadisticas           # Stats
GET    /api/v1/rachas/ranking-global         # Leaderboard
```

---

## 💡 Ejemplos de Uso

### Calificar Tarea (Integración Automática)

```python
from src.services.academic.tarea_service import TareaService

# El docente solo califica normalmente
resultado = await TareaService.calificar_entrega(
    db=db,
    entrega_id="a1b2c3d4...",
    calificacion=85,
    retroalimentacion="Excelente trabajo!",
    usuario=docente
)

# El sistema automáticamente:
# 1. Calcula puntos (base + bonos)
# 2. Otorga puntos al estudiante
# 3. Verifica racha diaria
# 4. Detecta milestones
# 5. Retorna respuesta completa

print(resultado['data']['puntos']['puntos_totales'])  # 70
print(resultado['data']['racha']['racha_actual'])     # 7 días
print(resultado['data']['racha']['milestone_alcanzado'])  # "7_dias"
```

### Comprar Item de Tienda

```python
from src.services.gamification.tienda_service import TiendaService

tienda_service = TiendaService(db)

# Estudiante compra un avatar
compra = await tienda_service.comprar_item(
    usuario_id=estudiante_id,
    item_id=item_id,
    cantidad=1
)

# Sistema verifica puntos, stock, requisitos
# Deduce puntos, agrega a inventario, registra transacción
```

### Equipar Badges

```python
from src.services.gamification.etiquetas_service import EtiquetasService

etiquetas_service = EtiquetasService(db)

# Equipar hasta 5 badges (con orden)
resultado = await etiquetas_service.equipar_etiquetas(
    usuario_id=estudiante_id,
    usuario_etiquetas_ids=[id1, id2, id3, id4, id5]
)

# Sistema valida máximo 5, no duplicados
```

### Verificar Racha

```python
from src.services.gamification.racha_service import RachaService

racha_service = RachaService(db)

# Verificar racha diaria (automático al calificar)
resultado = await racha_service.verificar_racha_diaria(
    usuario_id=estudiante_id,
    tipo_actividad="TAREA_COMPLETADA",
    actividad_id=entrega_id
)

# Sistema:
# 1. Verifica si es día consecutivo
# 2. Incrementa o resetea racha
# 3. Otorga puntos del día (10-50)
# 4. Detecta milestones
# 5. Otorga recompensas de milestone
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Tests unitarios de modelos y enums
pytest tests/gamification/test_gamification_models.py
pytest tests/gamification/test_gamification_enums.py
pytest tests/gamification/test_racha_usuario_expanded.py

# Test de integración completo
python scripts/test_gamification_integration.py
```

### Tests Disponibles

- ✅ **test_gamification_enums.py** - Validación de 11 enums
- ✅ **test_gamification_models.py** - Validación de 7 modelos
- ✅ **test_racha_usuario_expanded.py** - Validación de expansión de racha
- ✅ **test_gamification_integration.py** - Flujo completo de calificación

---

## 📚 Documentación

### Documentos Principales

1. **GAMIFICACION_SYSTEM_DESIGN.md**
   - Arquitectura completa
   - Reglas de negocio
   - Diseño de base de datos

2. **GAMIFICATION_COMPLETE_REPORT.md**
   - Reporte de implementación
   - Estadísticas del proyecto
   - Guía de APIs

3. **GAMIFICATION_INTEGRATION_COMPLETE.md**
   - Integración con sistema de tareas
   - Flujos detallados
   - Ejemplos de uso

4. **GAMIFICATION_EXECUTIVE_SUMMARY.md**
   - Resumen ejecutivo
   - Métricas del proyecto
   - Impacto esperado

### Swagger/OpenAPI

```bash
# Documentación interactiva
http://localhost:8000/docs

# Ver todos los endpoints de gamificación:
# - /api/v1/tienda/*
# - /api/v1/etiquetas/*
# - /api/v1/rachas/*
```

---

## 🔧 Configuración

### Variables de Entorno

```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/acadify

# Gamificación
PUNTOS_BASE_TAREA=50
PUNTOS_BONIFICACION_TAREA=20
PUNTOS_RACHA_MIN=10
PUNTOS_RACHA_MAX=50
```

### Personalización

```python
# En src/services/gamification/racha_service.py

RECOMPENSAS_SEMANALES = {
    0: 10,  # Lunes
    1: 20,  # Martes
    2: 30,  # Miércoles
    3: 40,  # Jueves
    4: 50,  # Viernes
    5: 30,  # Sábado
    6: 50,  # Domingo
}

MILESTONES = [
    (7, 50),     # 7 días: +50 pts
    (30, 200),   # 30 días: +200 pts
    (100, 1000), # 100 días: +1000 pts
    (365, 5000), # 365 días: +5000 pts
]
```

---

## 🐛 Troubleshooting

### Error: "Puntos insuficientes"
```python
# Verificar puntos del usuario
query = "SELECT SUM(cantidad) FROM historial_puntos WHERE usuario_id = ?"
```

### Error: "Racha no se incrementa"
```python
# Verificar última actividad
query = "SELECT fecha_ultimo_dia FROM RachaUsuario WHERE usuario_id = ?"
# Debe ser día anterior (no mismo día)
```

### Error: "No puede equipar más badges"
```python
# Máximo 5 badges equipados
query = "SELECT COUNT(*) FROM usuario_etiquetas WHERE usuario_id = ? AND equipada = true"
# Si es >= 5, desequipar primero
```

---

## 📈 Métricas y Monitoreo

### Queries Útiles

```sql
-- Top usuarios por puntos
SELECT u.nombres, SUM(hp.cantidad) as total_puntos
FROM "Usuario" u
JOIN historial_puntos hp ON u.usuario_id = hp.usuario_id
GROUP BY u.usuario_id
ORDER BY total_puntos DESC
LIMIT 10;

-- Top rachas activas
SELECT u.nombres, r.racha_actual, r.mejor_racha
FROM "Usuario" u
JOIN "RachaUsuario" r ON u.usuario_id = r.usuario_id
WHERE r.racha_actual > 0
ORDER BY r.racha_actual DESC
LIMIT 10;

-- Items más comprados
SELECT ti.nombre, COUNT(*) as compras
FROM transacciones_tienda tt
JOIN tienda_items ti ON tt.item_id = ti.item_id
WHERE tt.exitosa = true
GROUP BY ti.item_id
ORDER BY compras DESC
LIMIT 10;
```

---

## 🚀 Roadmap

### Fase 5 (Futuro)

- [ ] Dashboard de analytics para docentes
- [ ] Notificaciones push para milestones
- [ ] Sistema de gifts entre usuarios
- [ ] Desafíos grupales
- [ ] Eventos temporales
- [ ] Niveles de experiencia (XP)
- [ ] Logros ocultos
- [ ] Integración con redes sociales

---

## 🤝 Contribuir

Para contribuir al sistema de gamificación:

1. Fork el repositorio
2. Crear branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m "Agregar nueva funcionalidad"`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

---

## 📄 Licencia

Copyright © 2025 Acadify  
Todos los derechos reservados.

---

## 📞 Soporte

- 📧 Email: dev@acadify.com
- 💬 Slack: #gamificacion
- 🐛 Issues: GitHub Issues
- 📚 Docs: /docs/gamification/

---

**🎮 ¡Aprende Jugando con Acadify! 🚀**

*Sistema de Gamificación v1.0*  
*Última actualización: 31 de octubre de 2025*
