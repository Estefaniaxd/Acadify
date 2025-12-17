# 🗺️ ROADMAP - PRÓXIMOS PASOS POST-FASE 4

> **Documento**: Post-implementación
> **Horizonte**: 1-2 semanas
> **Prioridades**: Ordenadas por impacto

---

## 📌 RESUMEN EJECUTIVO

**Fase 4 completó**: Sistema completo de tareas + IA con mock endpoints
**Próximo**: Integración real de IA + optimizaciones + producción

---

## 🚀 SEMANA 1: INTEGRACIÓN REAL

### 1.1 Integración OpenAI Real (2 días)

**Qué hacer**:
```python
# backend/src/services/ia_service.py (NUEVO)
from openai import AsyncOpenAI

class IAService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generar_retroalimentacion(self, contenido: str, modelo: str):
        response = await self.client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": contenido}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
```

**Archivos a crear**:
- `backend/src/services/ia_service.py` - Lógica IA
- `backend/src/schemas/ia.py` - Schemas para respuestas
- Tests: `backend/tests/test_ia_service.py`

**Endpoints a actualizar**:
- `POST /api/ia/retroalimentacion-tareas` - Usar OpenAI real
- `POST /api/ia/retroalimentacion-masiva` - Background task con OpenAI
- `POST /api/ia/calificacion-automatica` - Usar OpenAI para evaluar

**Testing**:
```bash
# Crear archivo .env.test con OPENAI_API_KEY válida
pytest backend/tests/test_ia_service.py -v

# Test manual
curl -X POST http://localhost:8000/api/ia/retroalimentacion-tareas \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"contenido_tarea": "Mi respuesta"}'
```

**Estimado**: 2-3 horas

---

### 1.2 Sistema de Quotas/Limiting (1 día)

**Qué hacer**:
```python
# backend/src/services/quota_service.py (NUEVO)
class QuotaService:
    async def verificar_cuota_usuario(self, usuario_id: int) -> QuotaInfo:
        # Obtener cuota del usuario en BD
        # Validar no haya excedido límite
        # Retornar tokens_restantes, reset_date, etc
        pass
    
    async def consumir_tokens(self, usuario_id: int, tokens: int):
        # Restar tokens de cuota del usuario
        # Registrar en audit log
        pass
```

**Archivos a crear**:
- `backend/src/models/usuario_quota.py` - Modelo para quotas
- `backend/src/services/quota_service.py` - Lógica de quotas
- Migración Alembic

**Funcionalidad**:
```
Admin dashboard:
- Ver cuota de usuario
- Editar límites
- Reset de cuota
- Audit log de consumo

Response de IA incluirá:
{
  "retroalimentacion": "...",
  "tokens_usados": 1250,
  "tokens_restantes": 3750,
  "reset_date": "2024-12-25"
}
```

**Estimado**: 1-2 horas

---

### 1.3 Caching de Respuestas IA (1 día)

**Qué hacer**:
```python
# backend/src/services/ia_cache_service.py (NUEVO)
class IACacheService:
    async def obtener_o_generar(
        self,
        contenido_hash: str,
        tipo_tarea: str,
        modelo: str
    ):
        # Buscar en Redis
        cached = await redis.get(f"ia:{contenido_hash}")
        if cached:
            return json.loads(cached)
        
        # Si no está, generar y cachear
        resultado = await ia_service.generar(...)
        await redis.setex(
            f"ia:{contenido_hash}",
            86400,  # 24 horas
            json.dumps(resultado)
        )
        return resultado
```

**Beneficios**:
- ⚡ Respuestas instantáneas para contenido visto antes
- 💰 Ahorro de tokens OpenAI
- 📊 Métricas: hit rate, cache efficiency

**Estimado**: 1 hora

---

## 🛠️ SEMANA 2: OPTIMIZACIONES & POLISH

### 2.1 UI/UX Enhancements (2 días)

**BulkIAFeedbackModal Mejorado**:
```typescript
// Agregar:
- Pausar/Reanudar procesamiento ✅ (ya está)
- Cancelar individual de tarea
- Retry automático en error
- Export resultados a CSV
- Resumen final con estadísticas
- Notificación push cuando complete
```

**CalificacionTarea Mejorado**:
```typescript
// Agregar:
- Preview de retroalimentación antes de guardar
- Historial de cambios (undo/redo)
- Sugerencias de puntos por criterio
- Comparación con calificaciones anteriores
- Plantillas de comentarios rápidos
```

**NotificacionesPanel Mejorado**:
```typescript
// Agregar:
- Audio/sonido para notificaciones nuevas
- Vibración en móvil
- Agrupar por tarea/curso
- Búsqueda y filtrado avanzado
- Notificaciones push del navegador
- Snooze (recordar después)
```

**Estimado**: 2-3 horas

---

### 2.2 Performance & Optimization (1 día)

**Frontend**:
```typescript
// Lazy loading
const CalificacionTarea = lazy(() => import('./CalificacionTarea'));

// Virtualización
import { VirtualList } from 'react-virtualized';

// Memoization
const TareaItem = memo(({ tarea }) => {...});

// React Query optimization
useInfiniteQuery({
  queryKey: ['notificaciones'],
  queryFn: fetchNotificaciones,
  getNextPageParam: (...) => ...
});
```

**Backend**:
```python
# N+1 queries fix
async def obtener_tareas(curso_id: int):
    return await db.execute(
        select(Tarea)
        .options(selectinload(Tarea.entregas))  # Eager load
        .options(selectinload(Tarea.criterios))
        .where(Tarea.curso_id == curso_id)
    )

# Índices en BD
class Notificacion:
    __table_args__ = (
        Index('ix_notificacion_usuario_fecha', 'usuario_id', 'fecha_creacion'),
        Index('ix_notificacion_usuario_leida', 'usuario_id', 'leida'),
    )
```

**Estimado**: 1-2 horas

---

### 2.3 Testing Completo (1 día)

**Frontend Tests**:
```typescript
// frontend/src/components/__tests__/CalificacionTarea.test.tsx
describe('CalificacionTarea', () => {
  it('should generate IA feedback', async () => {
    // Render component
    // Mock iaService
    // Click "Generar IA"
    // Assert feedback appears
  });
});
```

**Backend Tests**:
```python
# backend/tests/test_ia_endpoints.py
@pytest.mark.asyncio
async def test_retroalimentacion_individual():
    response = await client.post(
        "/api/ia/retroalimentacion-tareas",
        json={...},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "retroalimentacion" in response.json()

@pytest.mark.asyncio
async def test_retroalimentacion_masiva():
    # Test bulk processing
    pass

@pytest.mark.asyncio
async def test_quota_enforcement():
    # Test quota limiting
    pass
```

**Coverage Target**: > 80%

**Estimado**: 1-2 horas

---

## 📊 SEMANA 3: MONITOREO & PRODUCCIÓN

### 3.1 Monitoreo y Analytics (1 día)

**Backend Metrics**:
```python
# backend/src/utils/metrics.py (NUEVO)
from prometheus_client import Counter, Histogram

ia_requests = Counter('ia_requests_total', 'Total IA requests')
ia_latency = Histogram('ia_request_duration_seconds', 'IA latency')
ia_tokens_used = Counter('ia_tokens_used', 'Tokens used')
ia_errors = Counter('ia_errors_total', 'IA errors')

# Usar en endpoints
@router.post("/retroalimentacion-tareas")
async def generar_retroalimentacion(data: RetroalimentacionRequest):
    with ia_latency.time():
        try:
            resultado = await ia_service.generar(...)
            ia_requests.labels(status='success').inc()
            ia_tokens_used.add(resultado.tokens_usados)
            return resultado
        except Exception as e:
            ia_errors.labels(tipo=type(e).__name__).inc()
            raise
```

**Sentry Integration**:
```python
# backend/src/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

**Frontend Analytics**:
```typescript
// frontend/src/utils/analytics.ts
export const trackEvent = (event: string, data?: any) => {
  // Sendto Mixpanel/Amplitude/GA4
  console.log(`📊 Event: ${event}`, data);
  mixpanel.track(event, data);
};

// Usar en componentes
useEffect(() => {
  trackEvent('bulk_ia_started', { tareas_count: tareas.length });
}, []);
```

**Estimado**: 1 hora

---

### 3.2 Documentación para Producción (1 día)

**Crear**:
- [ ] `DEPLOYMENT.md` - Guía deploy a producción
- [ ] `OPERATIONS.md` - Guía de operaciones (monitoring, alertas)
- [ ] `TROUBLESHOOTING.md` - Guía de troubleshooting
- [ ] API Docs Swagger (`/docs`)
- [ ] Video tutorial: "Cómo usar retroalimentación IA"

**Estimado**: 1-2 horas

---

### 3.3 Preparar para Producción (1 día)

**Checklist**:
```
Security:
 ☐ Rate limiting en endpoints
 ☐ CORS configurado correctamente
 ☐ Secrets en variables de entorno
 ☐ SQL Injection prevention (ya está con SQLAlchemy)
 ☐ CSRF tokens (ya está con JWT)

Performance:
 ☐ Caché estratégico (Redis)
 ☐ Compresión gzip
 ☐ CDN para assets
 ☐ Database índices optimizados
 ☐ Lazy loading implementado

Monitoring:
 ☐ Sentry para errores
 ☐ Prometheus para métricas
 ☐ Logging centralizado
 ☐ Alertas configuradas
 ☐ Uptime monitoring

Testing:
 ☐ Unit tests: > 80%
 ☐ Integration tests
 ☐ E2E tests básicos
 ☐ Load testing

Deployment:
 ☐ Docker images
 ☐ CI/CD pipeline
 ☐ Rollback strategy
 ☐ Backup strategy
 ☐ Runbooks for incidents
```

**Estimado**: 2-3 horas

---

## 🎯 ROADMAP VISUAL

```
SEMANA 1: INTEGRACIÓN REAL
├─ 1.1 OpenAI Real (2-3h)
├─ 1.2 Quotas & Limiting (1-2h)
└─ 1.3 Caching (1h)

SEMANA 2: OPTIMIZACIONES
├─ 2.1 UI/UX Enhancements (2-3h)
├─ 2.2 Performance (1-2h)
└─ 2.3 Testing (1-2h)

SEMANA 3: PRODUCCIÓN
├─ 3.1 Monitoreo (1h)
├─ 3.2 Documentación (1-2h)
└─ 3.3 Deploy Prep (2-3h)

SEMANA 4: LAUNCH
├─ QA Testing
├─ Deploy Staging
├─ Deploy Producción
└─ Monitoring & Support
```

---

## 🔥 QUICK WINS (Hacer primero)

1. **Integración OpenAI** (2-3 horas)
   - Máximo impacto
   - Core functionality
   - Relativamente simple

2. **Performance Optimization** (1-2 horas)
   - Mejora UX notablemente
   - Relativamente rápido
   - Impacto visible inmediato

3. **Testing Completo** (1-2 horas)
   - Reduce bugs
   - Confianza de deploy
   - Fácil de automatizar

---

## 💡 CONSIDERACIONES

### Seguridad
- Validar input en todos los endpoints
- Rate limiting para IA (evitar abuse)
- Audit logging de acciones

### Escalabilidad
- Usar Celery/RQ para background jobs masivos
- Redis para caching
- Considerar microservicio de IA separado

### Costos
- OpenAI: ~$0.002-0.003 por request
- Estimado por usuario: $5-10/mes si usa mucho
- Implementar quotas para controlar costos

### Experiencia de Usuario
- Feedback visual mientras IA procesa
- Manejo gracioso de errores
- Fallback a feedback manual si IA falla

---

## 📞 MÉTRICAS A TRACKEAR

Una vez en producción, monitorear:

```
Uso:
- Usuarios activos
- Tareas creadas/día
- IA requests/día
- Tokens consumidos/mes

Performance:
- Latencia IA (target: < 5s)
- Latencia API (target: < 500ms)
- Uptime (target: 99.9%)
- Error rate (target: < 0.1%)

Negocio:
- Satisfacción usuario (NPS)
- Adopción feature IA
- Tasa de retención
- ROI de IA
```

---

## 🎓 APRENDIZAJES

Lo completado en Fase 4:
✅ Sistema modular y escalable
✅ Componentes reutilizables
✅ Type-safe con TypeScript
✅ Production-ready patterns
✅ Documentación clara
✅ Testing infrastructure

A continuar:
→ Integración IA real (fácil ahora con mock en lugar)
→ Optimizaciones (incremental)
→ Monitoreo (para observabilidad)
→ Escalabilidad (cuando necesario)

---

## ✅ CONCLUSIÓN

**Fase 4 alcanzó objetivo**: Sistema completo, profesional, producción-ready

**Próxima fase es optimización**: Integrar IA real, performance, monitoreo

**Timeline realista**: 2-3 semanas para estar 100% en prod con todas las bells & whistles

---

## 📋 NEXT ACTIONS

1. **Hoy**: Integración checklist (INTEGRATION_CHECKLIST.md)
2. **Mañana**: Testeo completo de Fase 4
3. **Esta semana**: Integración OpenAI
4. **Próxima semana**: Optimizaciones
5. **Semana posterior**: Producción

---

**¡Listo para la siguiente fase!** 🚀

Diciembre 2024 | Equipo Acadify
