# 🧪 Guía de Testing Manual - Módulo Instituciones

## 📋 Información del Test

- **URL Base:** http://localhost:5174/admin/instituciones
- **Servidor:** Corriendo en puerto 5174
- **Fecha:** 31 de octubre de 2025
- **Tester:** Manual

---

## ✅ Checklist de Testing

### 1. Acceso a la Página Principal

- [ ] **Navegar a** `http://localhost:5174/admin/instituciones`
- [ ] Verificar que se muestra el título "Instituciones"
- [ ] Verificar que aparece el botón "Nueva Institución"
- [ ] Verificar que hay barra de búsqueda
- [ ] Verificar que hay botón de "Filtros"

**Resultado esperado:** Página carga correctamente con todos los elementos UI

---

### 2. Testing de Lista Vacía

- [ ] **Si no hay instituciones:**
  - Verificar empty state con mensaje
  - Verificar ícono de edificio
  - Mensaje: "No hay instituciones"
  - Submensaje: "Comienza creando tu primera institución"

**Resultado esperado:** Empty state se muestra correctamente

---

### 3. Crear Nueva Institución

#### 3.1 Navegación
- [ ] Click en botón "Nueva Institución"
- [ ] Verificar redirección a `/admin/instituciones/crear`
- [ ] Verificar que se muestra formulario vacío
- [ ] Verificar título "Nueva Institución"

#### 3.2 Validación de Campos
- [ ] **Nombre (requerido):**
  - Dejar vacío y submit → Error: "El nombre es requerido"
  - Escribir "Un" → Error: "El nombre debe tener al menos 3 caracteres"
  - Escribir "Universidad Nacional" → ✅ OK

- [ ] **Email:**
  - Escribir "email-invalido" → Error: "Email inválido"
  - Escribir "contacto@universidad.edu" → ✅ OK

- [ ] **Teléfono:**
  - Escribir "abcd" → Error: "Teléfono inválido"
  - Escribir "+57 123 456 7890" → ✅ OK

- [ ] **Sitio Web:**
  - Escribir "www.universidad.edu" → Error: "URL inválida"
  - Escribir "https://universidad.edu" → ✅ OK

#### 3.3 Upload de Logo
- [ ] Click en "Subir Logo"
- [ ] Seleccionar imagen PNG (< 5MB) → Ver preview
- [ ] Intentar subir archivo > 5MB → Error
- [ ] Intentar subir PDF → Error: "El archivo debe ser una imagen"

#### 3.4 Personalización de Colores
- [ ] Click en color picker primario
- [ ] Seleccionar azul (#3B82F6) → Verificar preview
- [ ] Editar hex manualmente → Verificar actualización
- [ ] Repetir para color secundario

#### 3.5 Envío del Formulario
- [ ] Completar todos los campos obligatorios
- [ ] Click en "Crear Institución"
- [ ] Verificar mensaje de éxito (alert)
- [ ] Verificar redirección a `/admin/instituciones`
- [ ] Verificar que nueva institución aparece en la lista

**Resultado esperado:** Institución creada y visible en lista

---

### 4. Testing de Lista con Datos

#### 4.1 Visualización de Cards
Para cada institución en la lista:

- [ ] **Header de Card:**
  - Logo se muestra (o ícono por defecto)
  - Fondo con degradado azul-morado
  - Badge de estado (Activo/Inactivo)

- [ ] **Contenido de Card:**
  - Nombre de la institución
  - Descripción (si existe)
  - Estadísticas:
    - X cursos (con ícono de libro)
    - Y estudiantes (con ícono de usuarios)

- [ ] **Botones de Acción:**
  - Botón "Ver" (azul)
  - Botón "Editar" (morado)
  - Botón de menú (tres puntos verticales)

#### 4.2 Grid Responsivo
- [ ] **Desktop (>1024px):** 3 columnas
- [ ] **Tablet (768-1024px):** 2 columnas  
- [ ] **Mobile (<768px):** 1 columna

---

### 5. Testing de Búsqueda

- [ ] Escribir en barra de búsqueda: "Universidad"
- [ ] Verificar que se filtra en tiempo real (debounce ~300ms)
- [ ] Limpiar búsqueda
- [ ] Verificar que vuelven todos los resultados
- [ ] Buscar término que no existe → Empty state
- [ ] Verificar mensaje: "No hay instituciones"

**Resultado esperado:** Búsqueda funciona correctamente

---

### 6. Testing de Filtros

#### 6.1 Abrir/Cerrar Panel
- [ ] Click en botón "Filtros"
- [ ] Verificar que se abre panel con 3 selectores
- [ ] Click nuevamente → Panel se cierra

#### 6.2 Filtro por Estado
- [ ] Seleccionar "Activos" → Solo instituciones activas
- [ ] Seleccionar "Inactivos" → Solo instituciones inactivas
- [ ] Seleccionar "Todos" → Todas las instituciones

#### 6.3 Filtro por Ordenamiento
- [ ] **Ordenar por:**
  - "Nombre" + "Ascendente" → A-Z
  - "Nombre" + "Descendente" → Z-A
  - "Fecha" + "Descendente" → Más recientes primero
  - "Estudiantes" + "Descendente" → Más estudiantes primero

**Resultado esperado:** Filtros aplican correctamente

---

### 7. Testing de Paginación

**(Solo si hay > 10 instituciones)**

- [ ] Verificar info: "Mostrando 1-10 de X instituciones"
- [ ] Verificar botón "Anterior" deshabilitado en página 1
- [ ] Click en "Siguiente" → Página 2
- [ ] Verificar que cambian las instituciones mostradas
- [ ] Verificar info: "Mostrando 11-20 de X instituciones"
- [ ] Click en "Anterior" → Volver a página 1
- [ ] En última página, "Siguiente" debe estar deshabilitado

**Resultado esperado:** Paginación funciona correctamente

---

### 8. Testing de Edición

#### 8.1 Navegación a Edición
- [ ] Click en botón "Editar" de una institución
- [ ] Verificar redirección a `/admin/instituciones/{id}/editar`
- [ ] Verificar que formulario carga con datos existentes
- [ ] Verificar título "Editar Institución"

#### 8.2 Edición de Datos
- [ ] Modificar nombre
- [ ] Modificar descripción
- [ ] Cambiar colores
- [ ] Upload nuevo logo → Ver nuevo preview
- [ ] Click en "Guardar Cambios"
- [ ] Verificar mensaje de éxito
- [ ] Verificar redirección a `/admin/instituciones/{id}` (o lista)
- [ ] Volver a lista → Verificar cambios aplicados

**Resultado esperado:** Edición guarda correctamente

---

### 9. Testing de Menú de Opciones

#### 9.1 Abrir Menú
- [ ] Click en botón de tres puntos (⋮)
- [ ] Verificar que se abre dropdown con opciones
- [ ] Click fuera → Menú se cierra

#### 9.2 Activar/Desactivar
- [ ] **Si institución está activa:**
  - Click en "Desactivar"
  - Verificar cambio de badge: "Activo" → "Inactivo"
  - Sin recarga de página

- [ ] **Si institución está inactiva:**
  - Click en "Activar"
  - Verificar cambio de badge: "Inactivo" → "Activo"
  - Sin recarga de página

#### 9.3 Eliminar Institución
- [ ] Click en "Eliminar" (texto rojo)
- [ ] Verificar modal de confirmación
- [ ] Mensaje: "¿Estás seguro de eliminar esta institución? Esta acción no se puede deshacer."
- [ ] Click en "Cancelar" → No se elimina
- [ ] Intentar de nuevo
- [ ] Click en "Confirmar" → Se elimina
- [ ] Verificar mensaje de éxito
- [ ] Verificar que desaparece de la lista
- [ ] Sin recarga de página

**Resultado esperado:** Operaciones funcionan sin errores

---

### 10. Testing de Estados de Carga

#### 10.1 Loading Inicial
- [ ] Recargar página (F5)
- [ ] Verificar skeletons animados mientras carga
- [ ] Verificar que desaparecen al cargar datos

#### 10.2 Loading en Mutaciones
- [ ] Crear institución:
  - Verificar spinner en botón
  - Botón deshabilitado
  - Texto "Creando..."
  
- [ ] Actualizar institución:
  - Verificar spinner en botón
  - Texto "Guardando..."

**Resultado esperado:** Feedback visual claro

---

### 11. Testing de Manejo de Errores

#### 11.1 Error de Red
- [ ] **Simular:** Detener backend o desconectar internet
- [ ] Intentar cargar instituciones
- [ ] Verificar mensaje de error rojo
- [ ] Verificar botón "Reintentar"
- [ ] Click en "Reintentar" → Vuelve a intentar

#### 11.2 Error 401 (No Autorizado)
- [ ] **Simular:** Borrar localStorage token
- [ ] Intentar cualquier operación
- [ ] Verificar redirección automática a `/login`
- [ ] Mensaje: "Sesión expirada"

#### 11.3 Error de Validación
- [ ] Intentar crear con nombre duplicado
- [ ] Verificar mensaje específico del servidor
- [ ] Mensaje permanece visible
- [ ] Formulario no se limpia

**Resultado esperado:** Errores manejados apropiadamente

---

### 12. Testing de Dark Mode

- [ ] Activar modo oscuro (si existe toggle)
- [ ] Verificar que todos los colores se ajustan:
  - Fondo oscuro
  - Texto claro
  - Cards con fondo gris oscuro
  - Bordes visibles
  - Botones legibles

**Resultado esperado:** UI legible en ambos modos

---

### 13. Testing de Accesibilidad

#### 13.1 Navegación con Teclado
- [ ] Tab → Avanza entre elementos
- [ ] Shift+Tab → Retrocede
- [ ] Enter → Activa botones
- [ ] Escape → Cierra modales/dropdowns

#### 13.2 Focus Visible
- [ ] Todos los elementos interactivos muestran focus
- [ ] Outline visible y claro

#### 13.3 ARIA Labels
- [ ] Inspeccionar botones sin texto
- [ ] Verificar aria-label presente
- [ ] Screen readers podrían leer correctamente

**Resultado esperado:** Navegación accesible

---

## 📊 Resumen de Resultados

### Checklist General

- [ ] Página principal carga ✅/❌
- [ ] Crear institución ✅/❌
- [ ] Editar institución ✅/❌
- [ ] Eliminar institución ✅/❌
- [ ] Búsqueda ✅/❌
- [ ] Filtros ✅/❌
- [ ] Paginación ✅/❌
- [ ] Loading states ✅/❌
- [ ] Error handling ✅/❌
- [ ] Responsive design ✅/❌
- [ ] Dark mode ✅/❌
- [ ] Accesibilidad ✅/❌

### Bugs Encontrados

**#** | **Descripción** | **Severidad** | **Pasos para Reproducir**
------|-----------------|---------------|---------------------------
1 | | | 
2 | | |
3 | | |

### Notas Adicionales



---

## ✅ Aprobación Final

- [ ] **Testing completado**
- [ ] **Sin bugs críticos**
- [ ] **Performance aceptable**
- [ ] **UI/UX intuitiva**

**Firma:** ________________  
**Fecha:** 31/10/2025

---

**¿Continuamos con Fase 2 (Módulo Programas)?** ✅/❌
