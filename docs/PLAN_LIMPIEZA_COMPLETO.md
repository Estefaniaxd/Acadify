# 🧹 PLAN DE LIMPIEZA Y ORGANIZACIÓN - ACADIFY

## 📊 ANÁLISIS INICIAL

### Archivos encontrados:
- **422+ archivos .md** (muchos duplicados y temporales)
- **88+ archivos .csv** (reportes de Locust - performance testing)
- **54+ archivos .html** (reportes y templates)
- Múltiples archivos de test dispersos
- Documentación sin organizar

---

## 🎯 PLAN DE ACCIÓN

### FASE 1: BACKEND - LIMPIEZA

#### 1.1 CSVs de Locust (88 archivos) ❌ ELIMINAR
**Ubicación**: `backend/*.csv`
**Acción**: ELIMINAR TODOS - Son reportes antiguos de pruebas de carga
**Razón**: Datos históricos obsoletos, ocupan espacio innecesario

#### 1.2 HTMLs de Locust (16 archivos) ❌ ELIMINAR  
**Ubicación**: `backend/locust_*.html`
**Acción**: ELIMINAR TODOS
**Razón**: Reportes visuales antiguos, ya no relevantes

#### 1.3 Markdowns del Backend (50+ archivos) 📁 ORGANIZAR
**Archivos a MANTENER en docs/**:
- README.md → `docs/README.md`
- BACKEND_TIENDA_REQUIREMENTS.md → `docs/features/tienda.md`
- ADMIN_PANEL_GUIDE.md → `docs/guides/admin-panel.md`
- GAMIFICATION_COMPLETE_REPORT.md → `docs/features/gamification.md`
- EXECUTIVE_SUMMARY.md → `docs/project/executive-summary.md`

**Archivos a ELIMINAR (temporales)**:
- FASE0_INVESTIGACION_COMPLETADA.md
- PRUEBA_SISTEMA_PRE_FASE2.md
- PERFORMANCE_TEST_RESULTS_V2.md
- RESUMEN_ESTADO_BACKEND.md
- BUG_REPORT_*.md
- AUDITORIA_*.md
- SESSION_SUMMARY.md

#### 1.4 Templates HTML ✅ MANTENER
**Ubicación**: `backend/src/templates/emails/*.html`
**Acción**: MANTENER TODOS (son funcionales)
**Limpiar**: 
- base_old.html → ELIMINAR
- base_backup_concatenado.html → ELIMINAR

---

### FASE 2: FRONTEND - LIMPIEZA

#### 2.1 Markdowns del Frontend (40+ archivos) 📁 ORGANIZAR
**Archivos a MANTENER**:
- README.md → mantener en raíz
- DESIGN_SYSTEM.md → `docs/frontend/design-system.md`
- MANUAL_TESTING_GUIDE.md → `docs/testing/manual-guide.md`

**Archivos TEMPORALES a ELIMINAR**:
- FASE_1_COMPLETADA.md
- FASE_2_COMPLETADA.md
- SESSION_COMPLETE.md
- SESSION_SUMMARY.md
- PROGRESO_SESION*.md
- OPTIMIZATION_*.md (múltiples)
- TEST_RESULTS*.md (múltiples)
- PERFORMANCE_*.md
- ICON_MIGRATION_RESULTS.md
- REORGANIZATION_REPORT.md
- SPRINT1_*.md
- VERIFICACION_COMPLETA.md

#### 2.2 HTMLs de Testing 🧪 REVISAR
**Archivos**:
- test-connection.html → mover a `dev-tools/`
- public/set-token.html → mover a `dev-tools/`
- public/test-dashboard.html → mover a `dev-tools/`

#### 2.3 Coverage HTML ✅ MANTENER
**Ubicación**: `frontend/coverage/`
**Acción**: MANTENER (generados automáticamente por tests)
**Agregar**: coverage/ al .gitignore

---

### FASE 3: ROOT - LIMPIEZA

#### 3.1 Markdowns del Root (10+ archivos) 📁 ORGANIZAR
**Archivos**:
- TEST_VIDEOLLAMADAS_GUIA.md → `docs/testing/videollamadas.md`
- MOBILE_APP_PLAN.md → `docs/planning/mobile-app.md`
- GIT_WORKFLOW_AUTOMATION.md → `docs/development/git-workflow.md`
- PRUEBA_DE_FUEGO.md → ELIMINAR (temporal)
- PROGRESO_FASE_1.md → ELIMINAR (histórico)
- PLAN_DE_TRABAJO_COMPLETO.md → `docs/planning/work-plan.md`
- ANALISIS_*.md → ELIMINAR (análisis antiguos)
- LINTING_AND_FORMATTING.md → `docs/development/code-quality.md`

---

### FASE 4: MOBILE - ORGANIZACIÓN

#### 4.1 Markdowns de Mobile (10+ archivos) 📁 ORGANIZAR
**Mantener estructura actual en mobile/docs/**:
- README.md → mantener
- ARCHITECTURE.md → mobile/docs/architecture.md
- USAGE_GUIDE.md → mobile/docs/usage-guide.md

**Eliminar archivos de FASE**:
- FASE_1_COMPLETED.md → ELIMINAR
- FASE_2_COMPLETED.md → ELIMINAR
- FASE_3_COMPLETED.md → ELIMINAR
- TEST_REPORT*.md → consolidar en uno solo
- AUTH_AND_NAV_COMPLETED.md → ELIMINAR
- PROBLEMA_COMPILACION_RESUELTO.md → ELIMINAR

---

### FASE 5: AGENTES CLAUDE (.claude/)

#### 5.1 Agentes ✅ MANTENER
**Ubicación**: `.claude/agents/*.md`
**Acción**: MANTENER TODOS (útiles para desarrollo)
**Organizar**: Ya están bien organizados

#### 5.2 Skills ✅ MANTENER
**Ubicación**: `.claude/skills/`
**Acción**: MANTENER

---

## 📂 NUEVA ESTRUCTURA PROPUESTA

```
Acadify/
├── docs/                           # 📚 NUEVA CARPETA
│   ├── README.md                  # Índice general
│   ├── project/                   # Documentación del proyecto
│   │   ├── executive-summary.md
│   │   └── work-plan.md
│   ├── features/                  # Documentación de features
│   │   ├── gamification.md
│   │   ├── tienda.md
│   │   ├── avatares.md
│   │   └── evaluaciones.md
│   ├── guides/                    # Guías de uso
│   │   ├── admin-panel.md
│   │   └── api-usage.md
│   ├── development/               # Desarrollo
│   │   ├── git-workflow.md
│   │   ├── code-quality.md
│   │   └── architecture.md
│   ├── testing/                   # Testing
│   │   ├── manual-guide.md
│   │   └── videollamadas.md
│   └── planning/                  # Planificación
│       └── mobile-app.md
│
├── dev-tools/                     # 🛠️ NUEVA CARPETA
│   ├── test-connection.html
│   ├── set-token.html
│   └── test-dashboard.html
│
├── backend/
│   ├── docs/                      # Docs específicos de backend
│   │   └── migrations/
│   │       └── README.md
│   ├── scripts/                   # Scripts organizados
│   ├── tests/                     # Tests organizados
│   └── migrations/                # Ya existe
│
├── frontend/
│   ├── docs/                      # Docs específicos de frontend
│   │   └── design-system.md
│   ├── tests/                     # Tests
│   └── coverage/                  # En .gitignore
│
├── mobile/
│   └── docs/                      # Ya organizado
│
└── .claude/                       # Mantener como está
```

---

## 🗑️ RESUMEN DE ELIMINACIONES

### Archivos a eliminar:
- ✅ **88 CSVs** de Locust (backend)
- ✅ **16 HTMLs** de reportes Locust (backend)  
- ✅ **60+ MDs temporales** (FASE, PROGRESO, SESSION, TEST_RESULTS, etc.)
- ✅ **3 HTMLs antiguos** de templates (base_old, backup)
- ✅ **Archivos de análisis** obsoletos

### Total estimado: **~170 archivos** a eliminar

---

## ✅ CHECKLIST DE EJECUCIÓN

### Backend:
- [ ] Eliminar todos los .csv de Locust
- [ ] Eliminar todos los .html de reportes Locust
- [ ] Crear carpeta docs/
- [ ] Mover MDs importantes a docs/
- [ ] Eliminar MDs temporales
- [ ] Limpiar templates/emails/

### Frontend:
- [ ] Crear carpeta docs/
- [ ] Mover DESIGN_SYSTEM.md
- [ ] Eliminar MDs de FASE/PROGRESO/SESSION
- [ ] Mover HTMLs de test a dev-tools/
- [ ] Agregar coverage/ a .gitignore

### Root:
- [ ] Crear carpeta docs/ principal
- [ ] Crear carpeta dev-tools/
- [ ] Mover y organizar MDs
- [ ] Eliminar archivos temporales

### Mobile:
- [ ] Organizar mobile/docs/
- [ ] Eliminar archivos de FASE
- [ ] Consolidar test reports

---

## 🎯 BENEFICIOS ESPERADOS

1. **Reducción de ~170 archivos** innecesarios
2. **Documentación centralizada** y organizada
3. **Estructura clara** por categorías
4. **Fácil navegación** para nuevos desarrolladores
5. **Repositorio más limpio** y profesional
6. **Mejor performance** de Git
7. **Índices claros** en cada carpeta docs/

---

## ⚡ SIGUIENTE PASO

¿Comenzamos con la limpieza? Puedo:
1. Empezar por el backend (eliminar CSVs y HTMLs)
2. Crear la estructura de carpetas docs/
3. Mover archivos importantes
4. Eliminar archivos temporales

**¿Por dónde empezamos?**
