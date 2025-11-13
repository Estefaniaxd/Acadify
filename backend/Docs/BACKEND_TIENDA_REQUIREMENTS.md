# 🏪 Requisitos del Backend - Sistema de Tienda de Puntos

## 📋 Tabla de Contenidos
1. [Visión General](#visión-general)
2. [Modelos de Base de Datos](#modelos-de-base-de-datos)
3. [Endpoints Requeridos](#endpoints-requeridos)
4. [Lógica de Negocio](#lógica-de-negocio)
5. [Validaciones](#validaciones)
6. [Ejemplos de Respuestas](#ejemplos-de-respuestas)

---

## 🎯 Visión General

El sistema de tienda permite a los usuarios canjear sus puntos de gamificación por productos virtuales como temas, ropa para avatares, accesorios y efectos especiales.

### Flujo Principal
1. Usuario navega catálogo de productos
2. Filtra por categoría, rareza, precio
3. Verifica disponibilidad y puntos suficientes
4. Realiza compra (descuenta puntos)
5. Producto se agrega al inventario
6. Usuario puede equipar/desequipar items

---

## 📊 Modelos de Base de Datos

### 1. **Tabla: `productos_tienda`**

```sql
CREATE TABLE productos_tienda (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(50) NOT NULL,  -- 'temas', 'ropa', 'accesorios', 'efectos', 'insignias'
    precio INTEGER NOT NULL CHECK (precio > 0),
    imagen_url VARCHAR(500),
    icono VARCHAR(100),  -- Emoji o código de ícono
    rareza VARCHAR(20) NOT NULL DEFAULT 'común',  -- 'común', 'raro', 'épico', 'legendario'
    stock INTEGER,  -- NULL = stock ilimitado
    stock_ilimitado BOOLEAN DEFAULT true,
    popular BOOLEAN DEFAULT false,
    nuevo BOOLEAN DEFAULT false,
    descuento_porcentaje INTEGER DEFAULT 0 CHECK (descuento_porcentaje BETWEEN 0 AND 100),
    precio_original INTEGER,  -- Para mostrar precio anterior si hay descuento
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_categoria CHECK (categoria IN ('temas', 'ropa', 'accesorios', 'efectos', 'insignias')),
    CONSTRAINT valid_rareza CHECK (rareza IN ('común', 'raro', 'épico', 'legendario'))
);

-- Índices
CREATE INDEX idx_productos_categoria ON productos_tienda(categoria);
CREATE INDEX idx_productos_rareza ON productos_tienda(rareza);
CREATE INDEX idx_productos_precio ON productos_tienda(precio);
CREATE INDEX idx_productos_popular ON productos_tienda(popular) WHERE popular = true;
CREATE INDEX idx_productos_nuevo ON productos_tienda(nuevo) WHERE nuevo = true;
CREATE INDEX idx_productos_activo ON productos_tienda(activo) WHERE activo = true;
```

**Campos importantes:**
- `stock_ilimitado`: Si es `true`, ignora el campo `stock`
- `popular`: Para destacar en sección de populares
- `nuevo`: Para destacar en sección de novedades
- `descuento_porcentaje`: Descuento actual (0-100)
- `activo`: Productos inactivos no se muestran en tienda

---

### 2. **Tabla: `compras_tienda`**

```sql
CREATE TABLE compras_tienda (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES productos_tienda(id) ON DELETE RESTRICT,
    puntos_gastados INTEGER NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 1 CHECK (cantidad > 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'completada',  -- 'completada', 'pendiente', 'cancelada', 'reembolsada'
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_activacion TIMESTAMP,  -- Cuando se usó/activó el producto
    notas TEXT,
    
    CONSTRAINT valid_estado CHECK (estado IN ('completada', 'pendiente', 'cancelada', 'reembolsada'))
);

-- Índices
CREATE INDEX idx_compras_usuario ON compras_tienda(usuario_id);
CREATE INDEX idx_compras_producto ON compras_tienda(producto_id);
CREATE INDEX idx_compras_fecha ON compras_tienda(fecha_compra DESC);
CREATE INDEX idx_compras_estado ON compras_tienda(estado);
```

**Lógica:**
- `puntos_gastados`: Puntos que se descontaron (puede variar por descuentos)
- `cantidad`: Cantidad de unidades compradas
- `estado`: Estado de la compra para auditoría
- `fecha_activacion`: Cuándo se equipó/usó por primera vez

---

### 3. **Tabla: `inventario_usuario`**

```sql
CREATE TABLE inventario_usuario (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES productos_tienda(id) ON DELETE RESTRICT,
    cantidad INTEGER NOT NULL DEFAULT 1 CHECK (cantidad > 0),
    equipado BOOLEAN DEFAULT false,
    fecha_adquisicion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Un usuario no puede tener el mismo producto duplicado
    UNIQUE(usuario_id, producto_id)
);

-- Índices
CREATE INDEX idx_inventario_usuario ON inventario_usuario(usuario_id);
CREATE INDEX idx_inventario_producto ON inventario_usuario(producto_id);
CREATE INDEX idx_inventario_equipado ON inventario_usuario(equipado) WHERE equipado = true;
```

**Lógica:**
- Solo puede haber un registro por `usuario_id + producto_id`
- `cantidad`: Acumula si compra el mismo producto varias veces
- `equipado`: Solo puede haber 1 equipado por categoría (validar en lógica de negocio)

---

## 🔌 Endpoints Requeridos

### **1. Productos**

#### `GET /api/tienda/productos`
Obtiene lista de productos con filtros

**Query Params:**
```typescript
{
  categoria?: 'temas' | 'ropa' | 'accesorios' | 'efectos' | 'insignias'
  rareza?: 'común' | 'raro' | 'épico' | 'legendario'
  precio_min?: number
  precio_max?: number
  busqueda?: string  // Busca en nombre y descripción
  popular?: boolean
  nuevo?: boolean
  solo_disponibles?: boolean  // Solo con stock disponible
  orden_por?: 'precio_asc' | 'precio_desc' | 'nombre' | 'popularidad' | 'fecha_desc'
  pagina?: number (default: 1)
  por_pagina?: number (default: 12)
}
```

**Respuesta:**
```json
{
  "productos": [
    {
      "id": 1,
      "nombre": "Tema Galaxia",
      "descripcion": "Tema oscuro con efectos de galaxia",
      "categoria": "temas",
      "precio": 150,
      "imagen_url": "https://...",
      "icono": "🌌",
      "rareza": "épico",
      "stock": null,
      "stock_ilimitado": true,
      "popular": true,
      "nuevo": false,
      "descuento_porcentaje": 20,
      "precio_original": 150,
      "activo": true,
      "fecha_creacion": "2025-01-01T00:00:00Z",
      "fecha_actualizacion": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 45,
  "pagina": 1,
  "por_pagina": 12,
  "total_paginas": 4
}
```

---

#### `GET /api/tienda/productos/{id}`
Obtiene un producto específico

**Respuesta:** Objeto `ProductoTienda`

---

#### `GET /api/tienda/productos/destacados`
Obtiene productos destacados (populares, nuevos, con descuento)

**Respuesta:**
```json
{
  "populares": [ /* ProductoTienda[] */ ],
  "nuevos": [ /* ProductoTienda[] */ ],
  "descuentos": [ /* ProductoTienda[] */ ]
}
```

---

#### `GET /api/tienda/categorias`
Obtiene lista de categorías con conteo

**Respuesta:**
```json
[
  {
    "categoria": "temas",
    "nombre": "Temas Visuales",
    "total_productos": 15
  },
  {
    "categoria": "ropa",
    "nombre": "Ropa para Avatar",
    "total_productos": 23
  }
]
```

---

### **2. Compras**

#### `POST /api/tienda/comprar`
Realiza una compra

**Request Body:**
```json
{
  "producto_id": 1,
  "cantidad": 1
}
```

**Validaciones:**
1. Producto existe y está activo
2. Hay stock disponible (si no es ilimitado)
3. Usuario tiene puntos suficientes
4. No se puede comprar mismo producto si ya está en inventario (excepto apilables)

**Respuesta:**
```json
{
  "compra": {
    "id": 123,
    "usuario_id": 45,
    "producto_id": 1,
    "producto": { /* ProductoTienda */ },
    "puntos_gastados": 120,
    "cantidad": 1,
    "estado": "completada",
    "fecha_compra": "2025-11-09T10:00:00Z"
  },
  "puntos_restantes": 380,
  "mensaje": "¡Compra realizada con éxito!"
}
```

**Errores:**
- `400`: Puntos insuficientes
- `404`: Producto no encontrado
- `409`: Producto agotado
- `409`: Ya posee este producto

---

#### `GET /api/tienda/compras`
Historial de compras del usuario

**Query Params:**
```typescript
{
  pagina?: number (default: 1)
  por_pagina?: number (default: 20)
}
```

**Respuesta:**
```json
{
  "compras": [ /* CompraUsuario[] */ ],
  "total": 15,
  "pagina": 1,
  "por_pagina": 20,
  "total_paginas": 1
}
```

---

#### `GET /api/tienda/compras/{id}`
Detalle de una compra específica

**Respuesta:** Objeto `CompraUsuario` con producto incluido

---

### **3. Inventario**

#### `GET /api/tienda/inventario`
Obtiene inventario del usuario autenticado

**Respuesta:**
```json
[
  {
    "id": 1,
    "usuario_id": 45,
    "producto_id": 1,
    "producto": { /* ProductoTienda */ },
    "cantidad": 1,
    "equipado": true,
    "fecha_adquisicion": "2025-11-01T10:00:00Z"
  }
]
```

---

#### `GET /api/tienda/inventario/{id}`
Detalle de un item del inventario

**Respuesta:** Objeto `ItemInventario`

---

#### `POST /api/tienda/inventario/{id}/equipar`
Equipa un item del inventario

**Lógica:**
1. Desequipar otros items de la misma categoría
2. Marcar este item como equipado
3. Registrar fecha de activación si es primera vez

**Respuesta:**
```json
{
  "mensaje": "Item equipado exitosamente",
  "item": { /* ItemInventario */ }
}
```

---

#### `POST /api/tienda/inventario/{id}/desequipar`
Desequipa un item

**Respuesta:**
```json
{
  "mensaje": "Item desequipado",
  "item": { /* ItemInventario */ }
}
```

---

### **4. Utilidades**

#### `GET /api/tienda/productos/{id}/disponibilidad`
Verifica si se puede comprar un producto

**Query Params:**
```typescript
{
  cantidad?: number (default: 1)
}
```

**Respuesta:**
```json
{
  "puede_comprar": true,
  "razon": null,
  "puntos_faltantes": 0
}
```

O si no puede:
```json
{
  "puede_comprar": false,
  "razon": "puntos_insuficientes",  // 'puntos_insuficientes', 'sin_stock', 'ya_poseido'
  "puntos_faltantes": 50
}
```

---

#### `GET /api/tienda/estadisticas`
Estadísticas de tienda del usuario

**Respuesta:**
```json
{
  "total_gastado": 1250,
  "total_compras": 8,
  "items_inventario": 8,
  "items_equipados": 3,
  "categoria_favorita": "temas",
  "producto_mas_usado": { /* ProductoTienda */ }
}
```

---

## 🧠 Lógica de Negocio

### **Flujo de Compra**

```python
def realizar_compra(usuario_id: int, producto_id: int, cantidad: int = 1):
    # 1. Obtener producto
    producto = obtener_producto(producto_id)
    if not producto or not producto.activo:
        raise ProductoNoDisponibleError()
    
    # 2. Verificar stock
    if not producto.stock_ilimitado and producto.stock < cantidad:
        raise StockInsuficienteError()
    
    # 3. Calcular precio final (con descuento)
    precio_unitario = producto.precio
    if producto.descuento_porcentaje > 0:
        precio_unitario = producto.precio * (1 - producto.descuento_porcentaje / 100)
    
    precio_total = precio_unitario * cantidad
    
    # 4. Verificar puntos del usuario
    puntos_usuario = obtener_puntos_usuario(usuario_id)
    if puntos_usuario < precio_total:
        raise PuntosInsuficientesError(
            faltantes=precio_total - puntos_usuario
        )
    
    # 5. Iniciar transacción
    with transaction():
        # 5.1 Descontar puntos
        descontar_puntos(usuario_id, precio_total)
        
        # 5.2 Reducir stock (si no es ilimitado)
        if not producto.stock_ilimitado:
            reducir_stock(producto_id, cantidad)
        
        # 5.3 Crear registro de compra
        compra = crear_compra(
            usuario_id=usuario_id,
            producto_id=producto_id,
            puntos_gastados=precio_total,
            cantidad=cantidad,
            estado='completada'
        )
        
        # 5.4 Agregar al inventario o incrementar cantidad
        item = obtener_item_inventario(usuario_id, producto_id)
        if item:
            incrementar_cantidad(item.id, cantidad)
        else:
            crear_item_inventario(
                usuario_id=usuario_id,
                producto_id=producto_id,
                cantidad=cantidad
            )
        
        # 5.5 Registrar evento de gamificación
        registrar_evento('compra_tienda', usuario_id)
    
    return compra
```

---

### **Equipar Items**

```python
def equipar_item(usuario_id: int, item_id: int):
    # 1. Verificar que el item pertenece al usuario
    item = obtener_item_inventario(item_id)
    if item.usuario_id != usuario_id:
        raise PermisoDenegadoError()
    
    # 2. Desequipar otros items de la misma categoría
    categoria = item.producto.categoria
    desequipar_items_categoria(usuario_id, categoria)
    
    # 3. Equipar el item actual
    marcar_equipado(item_id, True)
    
    # 4. Registrar fecha de activación si es primera vez
    if not item.fecha_activacion:
        registrar_activacion(item_id)
    
    return item
```

---

## ✅ Validaciones

### **A Nivel de Base de Datos**
- ✅ Precios deben ser positivos
- ✅ Stock no puede ser negativo
- ✅ Descuentos entre 0-100%
- ✅ Categorías y rarezas válidas
- ✅ No duplicados en inventario (usuario + producto)

### **A Nivel de API**
- ✅ Usuario autenticado
- ✅ Producto activo y disponible
- ✅ Puntos suficientes
- ✅ Stock disponible
- ✅ Cantidad válida (> 0)
- ✅ Permisos sobre inventario propio

---

## 📦 Datos Iniciales Recomendados

### **Productos de Ejemplo**

```sql
-- Temas (6 productos)
INSERT INTO productos_tienda (nombre, categoria, precio, rareza, icono, descripcion, popular, nuevo) VALUES
('Tema Galaxia', 'temas', 150, 'épico', '🌌', 'Tema oscuro con efectos de galaxia', true, false),
('Tema Océano', 'temas', 120, 'raro', '🌊', 'Tema azul con ondas acuáticas', false, true),
('Tema Primavera', 'temas', 100, 'común', '🌸', 'Tema colorido con flores', false, false),
('Tema Nocturno', 'temas', 180, 'épico', '🌙', 'Tema oscuro elegante', true, false),
('Tema Fuego', 'temas', 200, 'legendario', '🔥', 'Tema con efectos de fuego', true, true),
('Tema Naturaleza', 'temas', 90, 'común', '🌿', 'Tema verde natural', false, false);

-- Ropa (8 productos)
INSERT INTO productos_tienda (nombre, categoria, precio, rareza, icono, descripcion, popular) VALUES
('Gorra de Graduación', 'ropa', 80, 'raro', '🎓', 'Gorra académica elegante', true),
('Camiseta Acadify', 'ropa', 50, 'común', '👕', 'Camiseta oficial de Acadify', false),
('Sudadera Premium', 'ropa', 150, 'épico', '🧥', 'Sudadera de edición limitada', true),
('Zapatos Deportivos', 'ropa', 100, 'raro', '👟', 'Zapatos cómodos', false),
('Corbata Elegante', 'ropa', 60, 'común', '👔', 'Corbata para ocasiones especiales', false),
('Chaqueta de Cuero', 'ropa', 250, 'legendario', '🧥', 'Chaqueta de cuero premium', true),
('Pantalones Formales', 'ropa', 80, 'raro', '👖', 'Pantalones elegantes', false),
('Gafas de Sol', 'ropa', 70, 'raro', '🕶️', 'Gafas modernas', false);

-- Y más...
```

---

## 🔒 Seguridad

1. **Autenticación**: Todos los endpoints requieren JWT token
2. **Autorización**: Solo puede comprar/equipar el propio usuario
3. **Validación de entrada**: Sanitizar todos los inputs
4. **Rate limiting**: Limitar compras por minuto
5. **Logs de auditoría**: Registrar todas las transacciones

---

## 📈 Optimizaciones

1. **Caché**: Cachear lista de productos por 5 minutos
2. **Índices**: Ya definidos en los modelos
3. **Paginación**: Siempre paginar resultados
4. **Eager loading**: Incluir relaciones en queries complejas
5. **Transacciones**: Usar transacciones para compras

---

## 🎯 Prioridades de Implementación

**Fase 1 (MVP):**
1. ✅ Modelos de base de datos
2. ✅ Endpoints de productos (GET)
3. ✅ Endpoint de compra (POST)
4. ✅ Endpoint de inventario (GET)

**Fase 2:**
5. Equipar/desequipar items
6. Estadísticas
7. Disponibilidad

**Fase 3:**
8. Filtros avanzados
9. Descuentos dinámicos
10. Sistema de reembolsos

---

**Fecha:** 9 de noviembre de 2025  
**Versión:** 1.0  
**Autor:** Sistema de Gamificación Acadify
