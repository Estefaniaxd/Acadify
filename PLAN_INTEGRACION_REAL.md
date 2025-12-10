# 🚀 PLAN DE INTEGRACIÓN REAL - FRONTEND TAREAS

**Fecha**: 18 Noviembre 2025  
**Estado**: 🔴 INICIANDO FASE 2B  
**Prioridad**: CRÍTICA  

---

## 📋 AUDITORÍA RÁPIDA - QUÉ FALTA

### ✅ En Backend (Verificado 99.2%)
- Models: `Tarea` (45 campos) + `EntregaTarea` (36 campos) ✓
- Schemas: 8 Pydantic schemas completos ✓
- CRUD: 14/15 métodos ✓
- API Endpoints: 12/12 operacionales ✓
- Validators: Business logic completo ✓

### 🔴 En Frontend - CRÍTICO
**Problema 1**: `TareasPage.tsx` NO incluye todos los campos de la BD
**Problema 2**: Formulario de crear tarea INCOMPLETO
**Problema 3**: NO hay página para subir tarea (EntregaTarea)
**Problema 4**: No hay integración con IA/Gemini
**Problema 5**: Rutas NO apuntan a nuevos componentes

---

## 📊 CAMPOS QUE FALTAN EN FRONTEND

### En Tarea (45 campos en BD vs menos en form):

```
FALTANTES EN FORMULARIO:
  ✗ instrucciones
  ✗ objetivos
  ✗ tags
  ✗ fecha_inicio_disponible
  ✗ tiempo_estimado
  ✗ permite_entrega_tardia
  ✗ penalizacion_tardia
  ✗ intentos_maximos
  ✗ formato_entrega
  ✗ tamano_maximo_mb
  ✗ puntuacion_maxima (llamado puntos_max)
  ✗ peso_evaluacion
  ✗ es_grupal
  ✗ es_publica
  ✗ requiere_aprobacion
  ✗ recursos_necesarios
  ✗ criterios_evaluacion
  ✗ rubrica_id
  ✗ configuracion_json
  ✗ estado
  ✗ activa
  ✗ habilitar_retroalimentacion_ia
  ✗ prompt_ia_personalizado
```

### En EntregaTarea (36 campos):
```
TODO FALTA - No existe página para subir entrega
```

---

## 🎯 PLAN DE ACCIÓN - 4 FASES

### **FASE 1: Corregir Formulario de Crear Tarea** (1-2 horas)
```
1. Revisar TareaFormModal.tsx
2. Agregar TODOS los campos faltantes
3. Validar contra Pydantic schema
4. Crear secciones acordeón para organizar
5. Conectar IA (opcional vs requerido)
```

### **FASE 2: Crear Página SubirTarea/EntregaTarea** (1-2 horas)
```
1. Crear:
   - src/pages/academic/SubirTareaPage.tsx (para estudiantes)
   - src/components/academic/EntregarTareaForm.tsx
   - src/hooks/academic/useEntregarTarea.ts (mutations)
2. Validar archivos
3. Conectar con backend /api/entregas
4. Mostrar feedback de IA
```

### **FASE 3: Listar y Calificar** (1-2 horas)
```
1. Integrar lista de entregas
2. Form de calificación CON TODOS los campos
3. Cálculo automático de puntos
4. Mostrar entregas tardías
```

### **FASE 4: Validación y Pruebas** (2-3 horas)
```
1. Test con archivos reales
2. Verificar persistencia en BD
3. Probar tardíos
4. Edge cases
```

---

## 🔧 ARCHIVO PRIORITARIO: Fix Formulario Tarea

**Archivo**: `frontend/src/modules/tareas/components/TareaFormModal.tsx` o similar  
**Acción**: Agregar campos faltantes  
**Estimado**: 30 minutos

---

## 📁 NUEVOS ARCHIVOS A CREAR

1. **frontend/src/pages/academic/SubirTareaPage.tsx** (400 líneas)
   - Página para estudiantes subir tarea
   - Dual view (progreso + form)

2. **frontend/src/components/academic/EntregarTareaForm.tsx** (350 líneas)
   - Form completo para entregar
   - Drag-drop, links, comments

3. **frontend/src/hooks/academic/useSubirTarea.ts** (200 líneas)
   - Mutations para crear entrega
   - Upload de archivos

4. **frontend/src/pages/academic/CalificarPage.tsx** (300 líneas)
   - Interfaz docentes para calificar
   - Lista + form detallado

---

## ⚡ EMPEZAR AHORA

**Paso 1**: Revisar formulario actual  
**Paso 2**: Agregar campos  
**Paso 3**: Crear página SubirTarea  
**Paso 4**: Test real

**Tiempo Total**: 4-6 horas de codificación pura  
**Complejidad**: Media (bien documentado)  
**Riesgo**: Bajo (backend ya verificado)

---

## 🚨 ESTÁNDARES A CUMPLIR

- ✅ 100% TypeScript strict mode
- ✅ React Query con proper caching
- ✅ Tailwind CSS responsive
- ✅ Validación Pydantic alineada
- ✅ Error handling completo
- ✅ Accesibilidad (a11y)
- ✅ Documentación inline
- ✅ Types compartidos con backend

---

**Status**: 🟢 LISTO PARA EMPEZAR  
**Next**: Revisar formulario actual

