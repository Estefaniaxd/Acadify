# 🎛️ PANEL DE ADMINISTRADOR - GUÍA COMPLETA
## Sistema de Gamificación Acadify

---

## 📋 ÍNDICE

1. [Sistema de Precios](#sistema-de-precios)
2. [Panel de Administrador](#panel-de-administrador)
3. [Gestión de Items de Tienda](#gestión-de-items-de-tienda)
4. [Gestión de Badges](#gestión-de-badges)
5. [Gestión de Milestones](#gestión-de-milestones)
6. [Estadísticas y Analytics](#estadísticas-y-analytics)
7. [Casos de Uso](#casos-de-uso)
8. [Best Practices](#best-practices)

---

## 💰 SISTEMA DE PRECIOS

### ¿Precio Automático o Manual?

El sistema soporta **AMBOS** métodos:

#### 1️⃣ Precio Automático (Basado en Rareza)

**Ventajas:**
- ✅ Consistencia: Todos los items de misma rareza cuestan similar
- ✅ Fácil de mantener: No hay que pensar en cada precio
- ✅ Balanceado: Basado en la economía diseñada

**Precios por Rareza:**

| Rareza | Precio Base | Rango Recomendado |
|--------|-------------|-------------------|
| **COMUN** | 100 pts | 50-150 pts |
| **RARO** | 300 pts | 200-500 pts |
| **EPICO** | 1,000 pts | 800-1,500 pts |
| **LEGENDARIO** | 3,000 pts | 2,000-5,000 pts |

**Uso:**
```json
{
  "nombre": "Cabello Fuego",
  "categoria": "CABELLO",
  "rareza": "EPICO",
  "usar_precio_automatico": true  // ← Sistema calcula 1,000 pts
}
```

#### 2️⃣ Precio Manual (Personalizado)

**Ventajas:**
- ✅ Flexibilidad total: Ajustar según demanda
- ✅ Promociones: Ofrecer descuentos temporales
- ✅ Items especiales: Eventos, colaboraciones, ediciones limitadas

**Uso:**
```json
{
  "nombre": "Avatar Halloween 2025",
  "categoria": "ROPA",
  "rareza": "LEGENDARIO",
  "precio_puntos": 1500  // ← Precio manual (en lugar de 3,000)
}
```

#### 3️⃣ Sistema Híbrido (Recomendado) ⭐

**Estrategia:**
- Items regulares → Precio automático
- Items especiales → Precio manual
- Promociones → Precio manual temporal

**Ejemplo:**
```python
# Items de Halloween (promoción)
cabello_halloween = {
    "rareza": "EPICO",
    "precio_puntos": 500  # Descuento! (normal: 1,000)
}

# Items regulares
cabello_normal = {
    "rareza": "EPICO",
    "usar_precio_automatico": true  # 1,000 pts
}
```

### Ajustes Dinámicos de Precios

El admin puede **cambiar precios en cualquier momento**:

```python
PUT /admin/tienda/items/{item_id}
{
  "precio_puntos": 150  # Nuevo precio
}
```

**Casos de uso:**
- 📈 **Aumentar precio** si item es muy popular (economía)
- 📉 **Reducir precio** si nadie lo compra
- 🎉 **Promociones** temporales (eventos, días festivos)
- ⚖️ **Balanceo** tras analizar estadísticas

---

## 🎛️ PANEL DE ADMINISTRADOR

### Permisos

**Roles con acceso:**
- ✅ `admin` - Acceso completo
- ✅ `coordinador` - Acceso completo
- ❌ `docente` - Sin acceso
- ❌ `estudiante` - Sin acceso

### Endpoints Disponibles

```
📦 TIENDA
POST   /admin/tienda/items          # Crear item
GET    /admin/tienda/items          # Listar todos (incluye inactivos)
GET    /admin/tienda/items/{id}     # Ver detalle
PUT    /admin/tienda/items/{id}     # Actualizar
DELETE /admin/tienda/items/{id}     # Eliminar
GET    /admin/tienda/estadisticas   # Stats de ventas

🏅 BADGES (En desarrollo)
POST   /admin/etiquetas/badges      # Crear badge
GET    /admin/etiquetas/badges      # Listar
PUT    /admin/etiquetas/badges/{id} # Actualizar
DELETE /admin/etiquetas/badges/{id} # Eliminar

🔥 RACHAS (En desarrollo)
POST   /admin/rachas/milestones     # Crear milestone
GET    /admin/rachas/milestones     # Listar
PUT    /admin/rachas/milestones/{id}# Actualizar
DELETE /admin/rachas/milestones/{id}# Eliminar
```

---

## 🛍️ GESTIÓN DE ITEMS DE TIENDA

### Crear Item Nuevo

**Endpoint:** `POST /admin/tienda/items`

**Request Completo:**
```json
{
  "nombre": "Cabello Galaxia",
  "descripcion": "Cabello con efecto de galaxia animada, perfecto para destacar",
  "categoria": "CABELLO",
  "rareza": "EPICO",
  
  // PRECIO (elige uno)
  "usar_precio_automatico": true,  // Opción 1: Auto (1,000 pts)
  // "precio_puntos": 1200,        // Opción 2: Manual
  
  // REQUISITOS
  "nivel_minimo_requerido": 15,
  
  // STOCK
  "stock_limitado": true,
  "stock_disponible": 50,
  
  // CONSUMIBLE (si aplica)
  "es_consumible": false,
  "usos_maximos": null,
  
  // DISPONIBILIDAD TEMPORAL (opcional)
  "disponible_desde": "2025-11-01T00:00:00Z",
  "disponible_hasta": "2025-11-30T23:59:59Z",
  
  // ESTADO
  "activo": true,
  
  // APARIENCIA
  "imagen_url": "https://cdn.acadify.com/items/cabello_galaxia.png",
  "preview_url": "https://cdn.acadify.com/previews/cabello_galaxia.glb",
  "color_hex": "#4B0082"
}
```

**Response:**
```json
{
  "item_id": "a1b2c3d4-...",
  "nombre": "Cabello Galaxia",
  "categoria": "CABELLO",
  "rareza": "EPICO",
  "precio_puntos": 1000,
  "nivel_minimo_requerido": 15,
  "stock_limitado": true,
  "stock_disponible": 50,
  "activo": true,
  "total_vendidos": 0,
  "fecha_creacion": "2025-10-31T..."
}
```

### Categorías Disponibles

#### 👤 Personalización de Avatar

| Categoría | Descripción | Ejemplos |
|-----------|-------------|----------|
| **CABELLO** | Peinados, colores | Trenzas, Afro, Galaxia |
| **ROPA** | Camisetas, vestidos | Hoodie SENA, Traje |
| **OJOS** | Color, forma | Ojos Azules, Ojos Gato |
| **BOCA** | Expresiones | Sonrisa, Serio |
| **NARIZ** | Forma | Pequeña, Grande |
| **CEJAS** | Forma, grosor | Arqueadas, Rectas |

#### 💍 Accesorios

| Categoría | Descripción | Ejemplos |
|-----------|-------------|----------|
| **ACCESORIO_CABEZA** | Sombreros, diademas | Corona, Gorra SENA |
| **ACCESORIO_CUELLO** | Collares, bufandas | Bufanda, Corbata |
| **ACCESORIO_MANOS** | Guantes, anillos | Guantes, Brazalete |

#### 🎨 Efectos Visuales

| Categoría | Descripción | Ejemplos |
|-----------|-------------|----------|
| **FONDO** | Fondos de perfil | Galaxia, Playa, Montañas |
| **MARCO** | Marcos de avatar | Dorado, Brillante |
| **EFECTO** | Efectos animados | Partículas, Brillo |

#### ⚙️ Items Funcionales

| Categoría | Descripción | Ejemplos |
|-----------|-------------|----------|
| **FUNCIONAL** | Items usables | Congelador Racha, Recuperador |

### Editar Item Existente

**Endpoint:** `PUT /admin/tienda/items/{item_id}`

**Request (solo campos a cambiar):**
```json
{
  "precio_puntos": 800,  // Reducir precio (promoción)
  "activo": true
}
```

### Desactivar vs Eliminar

#### ⏸️ Desactivar (Recomendado)

**Ventajas:**
- ✅ Mantiene historial de transacciones
- ✅ Se puede reactivar después
- ✅ Datos estadísticos íntegros

```json
PUT /admin/tienda/items/{item_id}
{
  "activo": false
}
```

#### ❌ Eliminar (Solo si es necesario)

**Cuándo usar:**
- Item creado por error
- Item sin ventas
- Limpieza de BD

```bash
DELETE /admin/tienda/items/{item_id}?forzar=false

# Con ventas (cuidado!):
DELETE /admin/tienda/items/{item_id}?forzar=true
```

### Gestión de Stock

#### Items con Stock Limitado

**Uso:** Crear escasez artificial, items exclusivos

```json
{
  "nombre": "Avatar Edición Halloween",
  "stock_limitado": true,
  "stock_disponible": 100,  // Solo 100 unidades
  "rareza": "LEGENDARIO"
}
```

**Comportamiento:**
- Sistema reduce stock automáticamente al vender
- Cuando stock=0 → Item no se puede comprar
- Admin puede agregar más stock:

```json
PUT /admin/tienda/items/{item_id}
{
  "stock_disponible": 200  // Agregar 100 más
}
```

#### Items Sin Límite

```json
{
  "stock_limitado": false,
  "stock_disponible": null  // Infinito
}
```

### Items Temporales (Eventos)

**Ejemplo: Item de Halloween**

```json
{
  "nombre": "Máscara Halloween 2025",
  "categoria": "ACCESORIO_CABEZA",
  "rareza": "EPICO",
  "precio_puntos": 666,  // Precio temático
  "disponible_desde": "2025-10-25T00:00:00Z",
  "disponible_hasta": "2025-11-01T23:59:59Z",
  "stock_limitado": true,
  "stock_disponible": 500,
  "activo": true
}
```

**Comportamiento:**
- Antes del 25 oct → No visible en tienda
- Del 25 oct al 1 nov → Visible y comprable
- Después del 1 nov → No se puede comprar
- Los que ya lo compraron → Lo mantienen para siempre

---

## 🏅 GESTIÓN DE BADGES (Próximamente)

### Crear Badge

```json
POST /admin/etiquetas/badges
{
  "nombre": "Matemático",
  "descripcion": "Completa 10 tareas de matemáticas con excelencia",
  "categoria": "MATEMATICAS",
  "rareza": "RARO",
  "precio_puntos": 300,
  
  // REQUISITOS (JSON personalizado)
  "requisitos": {
    "tareas_completadas": {
      "materia": "Matemáticas",
      "cantidad": 10,
      "calificacion_minima": 4.5
    }
  },
  
  // EVOLUCIÓN (opcional)
  "evolucion_a_id": "uuid-badge-matematico-experto",
  "requisito_evolucion": {
    "tareas_completadas": {
      "materia": "Matemáticas",
      "cantidad": 30,
      "calificacion_minima": 4.7
    }
  },
  
  "imagen_url": "https://cdn.acadify.com/badges/matematico.png",
  "activo": true
}
```

### Cadenas de Evolución

```
Matemático Novato (COMUN)
    ↓ 10 tareas
Matemático (RARO)
    ↓ 30 tareas
Matemático Experto (EPICO)
    ↓ 100 tareas
Maestro Matemático (LEGENDARIO)
```

---

## 🔥 GESTIÓN DE MILESTONES (Próximamente)

### Crear Milestone de Racha

```json
POST /admin/rachas/milestones
{
  "tipo_milestone": "DIAS_CONSECUTIVOS",
  "dias_requeridos": 7,
  "nombre": "Primera Semana",
  "descripcion": "7 días consecutivos de actividad",
  "puntos_recompensa": 50,
  "insignia_id": "uuid-badge-constante",
  "activo": true,
  "icon": "🔥",
  "color_hex": "#FF6600"
}
```

### Milestones Recomendados

| Días | Nombre | Puntos | Badge |
|------|--------|--------|-------|
| 3 | Primer Paso | 20 | Iniciado |
| 7 | Primera Semana | 50 | Constante |
| 14 | Dos Semanas | 100 | Persistente |
| 30 | Primer Mes | 200 | Dedicado |
| 60 | Dos Meses | 500 | Comprometido |
| 100 | Maestría | 1,000 | Maestro |
| 365 | Un Año | 5,000 | Leyenda |

---

## 📊 ESTADÍSTICAS Y ANALYTICS

### Dashboard de Ventas

**Endpoint:** `GET /admin/tienda/estadisticas`

**Response:**
```json
{
  "total_transacciones": 1543,
  "transacciones_exitosas": 1521,
  "transacciones_fallidas": 22,
  "total_puntos_gastados": 456789,
  
  "items_mas_vendidos": [
    {
      "item_id": "...",
      "nombre": "Cabello Afro",
      "total_vendidos": 234,
      "puntos_generados": 23400
    },
    // ... top 10
  ],
  
  "ventas_por_categoria": {
    "CABELLO": 456,
    "ROPA": 389,
    "OJOS": 234,
    // ...
  },
  
  "ventas_por_rareza": {
    "COMUN": 789,
    "RARO": 456,
    "EPICO": 234,
    "LEGENDARIO": 42
  },
  
  "ingresos_ultimos_7_dias": [
    {"fecha": "2025-10-31", "puntos": 12345, "ventas": 67},
    {"fecha": "2025-10-30", "puntos": 10234, "ventas": 54},
    // ...
  ]
}
```

### Métricas Clave

**Balanceo de Economía:**
```
Puntos Otorgados (entrada) vs Puntos Gastados (salida)

Ideal: 70-80% de puntos otorgados se gastan
- < 50%: Deflación (subir precios o crear items más atractivos)
- > 90%: Inflación (reducir otorgamiento o subir precios)
```

---

## 💼 CASOS DE USO

### Caso 1: Lanzamiento de Nueva Colección

**Objetivo:** Lanzar colección de avatares "Profesiones"

**Pasos:**

1. **Crear items:**
```bash
POST /admin/tienda/items
# Crear 10 items (Doctor, Ingeniero, Chef, etc.)
```

2. **Configurar precios:**
```json
{
  "rareza": "RARO",
  "usar_precio_automatico": true  // 300 pts cada uno
}
```

3. **Promoción de lanzamiento:**
```json
{
  "disponible_desde": "2025-11-01T00:00:00Z",
  "disponible_hasta": "2025-11-07T23:59:59Z",
  "precio_puntos": 200  // Descuento 33% primera semana
}
```

4. **Después de la semana:**
```bash
PUT /admin/tienda/items/{item_id}
{
  "precio_puntos": 300,
  "disponible_hasta": null  // Disponible siempre
}
```

### Caso 2: Evento de Halloween

1. **Crear items temáticos:**
```json
{
  "nombre": "Máscara Calabaza",
  "categoria": "ACCESORIO_CABEZA",
  "rareza": "EPICO",
  "precio_puntos": 666,
  "stock_limitado": true,
  "stock_disponible": 300,
  "disponible_desde": "2025-10-20",
  "disponible_hasta": "2025-11-02"
}
```

2. **Crear badge especial:**
```json
{
  "nombre": "Espíritu Halloween",
  "requisitos": {
    "comprar_items": ["mascara_calabaza", "fondo_cementerio"]
  }
}
```

3. **Después del evento:**
```bash
# Items se ocultan automáticamente (disponible_hasta)
# Usuarios que los compraron los mantienen
```

### Caso 3: Balanceo de Economía

**Problema:** Demasiados puntos en circulación, inflación

**Solución:**

1. **Analizar estadísticas:**
```bash
GET /admin/tienda/estadisticas
# Ver puntos gastados vs otorgados
```

2. **Ajustar precios:**
```bash
# Subir precios de items populares
PUT /admin/tienda/items/{item_id}
{
  "precio_puntos": 400  # Antes: 300
}
```

3. **Crear items caros:**
```json
{
  "nombre": "Avatar Legendario",
  "rareza": "LEGENDARIO",
  "precio_puntos": 10000  # Sumidero de puntos
}
```

### Caso 4: Promoción de Actividad

**Objetivo:** Incentivar completar rachas

1. **Crear descuentos para usuarios con racha:**
```json
// En el futuro: Descuentos basados en logros
{
  "nombre": "Avatar Exclusivo",
  "requisitos_compra": {
    "racha_minima": 30
  },
  "precio_puntos": 500  // Precio especial
}
```

---

## ✅ BEST PRACTICES

### Precios

1. **Empezar con precios automáticos** 
   - Más fácil de mantener
   - Consistencia garantizada

2. **Ajustar basado en datos**
   - Monitorear estadísticas semanalmente
   - Items muy populares → Subir precio
   - Items sin ventas → Bajar precio

3. **Promociones temporales**
   - Generar urgencia (FOMO)
   - Aumentar engagement

4. **Precios psicológicos**
   - 299 en lugar de 300
   - 999 en lugar de 1000

### Categorización

1. **Ser consistente**
   - Items similares en misma categoría
   - Rareza refleja valor real

2. **Rarezas balanceadas**
   ```
   COMUN: 60% de items
   RARO: 25%
   EPICO: 12%
   LEGENDARIO: 3%
   ```

3. **Evolución lógica**
   - Solo items que hacen sentido
   - Requisitos alcanzables

### Stock

1. **Stock limitado para:**
   - Items de eventos
   - Colaboraciones
   - Ediciones especiales

2. **Stock ilimitado para:**
   - Items básicos
   - Items permanentes

### Comunicación

1. **Anunciar cambios de precio**
   - Notificar a usuarios
   - Explicar razón

2. **Promocionar nuevos items**
   - Newsletter
   - Banner en plataforma

3. **Transparencia en economía**
   - Mostrar stats públicas
   - Explicar sistema de precios

---

## 🔧 CONFIGURACIÓN TÉCNICA

### Variables de Entorno

```bash
# Precios automáticos (puedes personalizar)
PRECIO_COMUN=100
PRECIO_RARO=300
PRECIO_EPICO=1000
PRECIO_LEGENDARIO=3000

# Límites
MAX_ITEMS_POR_USUARIO=1000
MAX_STOCK_POR_ITEM=10000
```

### Permisos en BD

```sql
-- Crear rol admin
CREATE ROLE admin;

-- Permisos completos en tablas de gamificación
GRANT ALL ON tienda_items TO admin;
GRANT ALL ON etiquetas_perfil TO admin;
GRANT ALL ON recompensas_racha TO admin;
```

---

## 📞 SOPORTE

**Problemas comunes:**

1. **"No puedo crear items"**
   - Verificar rol (admin/coordinador)
   - Verificar token JWT válido

2. **"Items no aparecen en tienda"**
   - Verificar `activo = true`
   - Verificar `disponible_desde` y `disponible_hasta`

3. **"Precios no se calculan automáticamente"**
   - Verificar `usar_precio_automatico = true`
   - Si tiene `precio_puntos`, ese tiene prioridad

**Contacto:**
- 📧 dev@acadify.com
- 💬 Slack: #admin-gamificacion

---

**🎛️ Panel de Administrador v1.0**  
*Sistema de Gamificación Acadify*  
*Última actualización: 31 de octubre de 2025*
