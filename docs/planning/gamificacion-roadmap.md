# 🎮 Sistema de Gamificación - Estado Actual y Roadmap

**Fecha:** 3 de noviembre de 2025  
**Estado:** Auditoría Completa  
**Objetivo:** Hacer el sistema de gamificación más completo y robusto posible

---

## 📊 Estado Actual del Sistema

### ✅ **Módulos Implementados**

#### 1. **Sistema de Avatares** ⭐ COMPLETO
- ✅ Editor de avatares con capas (cabello, ojos, boca, ropa, accesorios)
- ✅ Sistema de género (masculino/femenino)
- ✅ Personalización de colores
- ✅ Galería de avatares guardados
- ✅ Avatar activo por usuario
- ✅ Privacidad de avatares (públicos/privados)
- ✅ Preview en tiempo real
- ✅ Sistema de assets con manifest.json
- ✅ Backend con Redis cache
- ✅ Frontend completo con React

**Componentes:**
- `AvatarStudio.tsx` - Editor completo
- `SimpleAvatar.tsx` - Visualización
- `AvatarGallery.tsx` - Galería
- `avatar_service.py` - Backend service

#### 2. **Sistema de Puntos** ⭐ COMPLETO (100% tests)
- ✅ Puntos acumulados por usuario
- ✅ Historial de puntos con paginación
- ✅ Sistema de niveles (Bronce I-III, Plata I-III, Oro I-III, Platino I-III)
- ✅ Ranking global paginado
- ✅ Posición en ranking con contexto
- ✅ Otorgar/quitar puntos (admin)
- ✅ Validación de usuarios
- ✅ Info de niveles y umbrales

**Endpoints:**
- `GET /api/gamification/puntos/me` - Mis puntos
- `GET /api/gamification/puntos/ranking` - Ranking global
- `GET /api/gamification/puntos/ranking/me` - Mi posición
- `POST /api/gamification/puntos/otorgar` - Otorgar puntos (admin)
- `GET /api/gamification/puntos/historial` - Historial
- `GET /api/gamification/puntos/nivel/info` - Info niveles

#### 3. **Sistema de Insignias** ⭐ IMPLEMENTADO
- ✅ Modelo `Insignia` con tipos y descripciones
- ✅ Modelo `UsuarioInsignia` con fechas
- ✅ Relación con sistema de puntos
- ✅ Insignias automáticas por umbrales:
  - Novato (100 pts)
  - Estudiante Dedicado (500 pts)
  - Explorador del Conocimiento (1000 pts)
  - Maestro en Progreso (2000 pts)
  - Sabio Digital (5000 pts)

#### 4. **Sistema de Rachas (Streaks)** ⭐ IMPLEMENTADO
- ✅ Modelo `RachaUsuario` con días actuales y máximos
- ✅ Modelo `HistorialRacha` para registro de eventos
- ✅ Modelo `RecompensaRacha` para premios
- ✅ Enum `TipoEventoRacha` (incremento, pérdida, recuperación, milestone)

#### 5. **Sistema de Tienda Virtual** ⭐ IMPLEMENTADO
- ✅ Modelo `TiendaItem` completo con:
  - Categorías de ropa y accesorios
  - Fondos y marcos de perfil
  - Etiquetas personalizadas
  - Items funcionales
  - Sistema de rareza (Común, Raro, Épico, Legendario)
  - Stock limitado
  - Items de temporada
  - Requisitos de nivel/puntos
  - Preview URLs
- ✅ Modelo `TransaccionTienda` para historial
- ✅ Modelo `InventarioUsuario` para items comprados
- ✅ Enums bien definidos (CategoriaItem, RarezaItem, MetodoAdquisicion)

#### 6. **Sistema de Etiquetas de Perfil** ⭐ IMPLEMENTADO
- ✅ Modelo `EtiquetaPerfil` con colores y iconos
- ✅ Modelo `UsuarioEtiqueta` con fechas de asignación
- ✅ Etiquetas para personalización de perfil

#### 7. **Sistema de Temas** ⭐ IMPLEMENTADO
- ✅ Modelo `Tema` base
- ✅ Modelo `TemaPredefinido` para temas oficiales
- ✅ Modelo `TemaPersonalizado` para temas de usuario
- ✅ Colores primarios, secundarios, fondos, textos

---

## 🚀 Propuestas de Mejora y Expansión

### 🎯 **PRIORIDAD ALTA** - Funcionalidad Crítica

#### 1. **Foto de Perfil y Banner** 🆕
**Estado:** NO IMPLEMENTADO  
**Impacto:** ALTO

**Propuesta:**
```python
# Agregar a modelo Usuario
class Usuario(Base):
    # ... campos existentes ...
    
    # 🆕 NUEVOS CAMPOS
    foto_perfil_url = Column(TEXT, nullable=True)
    foto_perfil_custom = Column(BOOLEAN, default=False)  # True si es custom, False si es avatar
    banner_url = Column(TEXT, nullable=True)
    banner_activo_id = Column(UUID, ForeignKey("tienda_items.item_id"))
    marco_perfil_id = Column(UUID, ForeignKey("tienda_items.item_id"))
    
    # Relaciones
    banner_activo = relationship("TiendaItem", foreign_keys=[banner_activo_id])
    marco_perfil = relationship("TiendaItem", foreign_keys=[marco_perfil_id])
```

**Funcionalidad:**
- ✅ Foto de perfil puede ser:
  - Avatar personalizado (por defecto)
  - Imagen custom subida por usuario
- ✅ Banner de perfil:
  - Colección de banners temáticos en tienda
  - Diferentes rarezas y precios
  - Preview en perfil
- ✅ Marco de avatar:
  - Marcos decorativos alrededor del avatar
  - Diferentes estilos (elegante, gaming, académico)

#### 2. **Sistema de Rachas - Endpoints Faltantes** 🔧
**Estado:** PARCIAL (solo modelos)  
**Impacto:** ALTO

**Endpoints a implementar:**
```python
# src/api/routes/gamification/racha_routes.py

@router.get("/rachas/me")
async def obtener_mi_racha(
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene racha actual del usuario"""
    pass

@router.post("/rachas/registrar-actividad")
async def registrar_actividad(
    current_user: Usuario = Depends(get_current_user)
):
    """Registra actividad diaria para racha"""
    pass

@router.get("/rachas/historial")
async def obtener_historial_racha(
    current_user: Usuario = Depends(get_current_user)
):
    """Historial de rachas del usuario"""
    pass

@router.post("/rachas/recuperar")
async def recuperar_racha(
    item_id: UUID,
    current_user: Usuario = Depends(get_current_user)
):
    """Usa item funcional para recuperar racha"""
    pass
```

**Service necesario:**
```python
# src/services/gamification/racha_service.py

class RachaService:
    async def obtener_racha_usuario(self, usuario_id: UUID)
    async def registrar_actividad_diaria(self, usuario_id: UUID)
    async def verificar_perdida_racha(self, usuario_id: UUID)
    async def recuperar_racha(self, usuario_id: UUID, dias: int)
    async def obtener_recompensas_racha(self, dias_racha: int)
    async def procesar_milestone_racha(self, usuario_id: UUID, dias: int)
```

#### 3. **Sistema de Tienda - Endpoints Completos** 🔧
**Estado:** PARCIAL (solo modelos)  
**Impacto:** ALTO

**Endpoints a implementar:**
```python
# src/api/routes/gamification/tienda_routes.py

@router.get("/tienda/items")
async def listar_items_tienda(
    categoria: Optional[CategoriaItem] = None,
    rareza: Optional[RarezaItem] = None,
    skip: int = 0,
    limit: int = 50
):
    """Lista items disponibles con filtros"""
    pass

@router.get("/tienda/items/{item_id}")
async def obtener_item_detalle(item_id: UUID):
    """Detalle de un item específico"""
    pass

@router.post("/tienda/comprar")
async def comprar_item(
    item_id: UUID,
    current_user: Usuario = Depends(get_current_user)
):
    """Compra un item con puntos"""
    pass

@router.get("/tienda/inventario")
async def obtener_inventario(
    current_user: Usuario = Depends(get_current_user)
):
    """Inventario de items del usuario"""
    pass

@router.post("/tienda/equipar/{item_id}")
async def equipar_item(
    item_id: UUID,
    current_user: Usuario = Depends(get_current_user)
):
    """Equipa un item del inventario"""
    pass

@router.get("/tienda/historial")
async def historial_transacciones(
    current_user: Usuario = Depends(get_current_user)
):
    """Historial de compras"""
    pass
```

#### 4. **Sistema de Logros/Achievements** 🆕
**Estado:** NO IMPLEMENTADO  
**Impacto:** ALTO

**Nuevos Modelos:**
```python
# src/models/gamification/logro.py

class Logro(Base):
    """
    Logros desbloqueables.
    
    Ejemplos:
    - "Primera Tarea Completada"
    - "10 Días de Racha"
    - "Nivel Plata Alcanzado"
    - "100 Puntos en Examen"
    - "Ayudante" (50 comentarios útiles)
    """
    __tablename__ = "logros"
    
    logro_id = Column(UUID, primary_key=True)
    nombre = Column(String(100))
    descripcion = Column(String(500))
    categoria = Column(ENUM(CategoriaLogro))  # académico, social, racha, puntos
    icono_url = Column(String(500))
    puntos_recompensa = Column(Integer)
    rareza = Column(ENUM(RarezaItem))
    es_secreto = Column(Boolean, default=False)  # No se muestra hasta desbloquearlo
    requisitos_json = Column(JSON)  # Condiciones para desbloquear
    orden_visualizacion = Column(Integer)
    es_activo = Column(Boolean, default=True)


class UsuarioLogro(Base):
    """Logros desbloqueados por usuario"""
    __tablename__ = "usuario_logros"
    
    usuario_logro_id = Column(UUID, primary_key=True)
    usuario_id = Column(UUID, ForeignKey("Usuario.usuario_id"))
    logro_id = Column(UUID, ForeignKey("logros.logro_id"))
    fecha_desbloqueo = Column(TIMESTAMP(timezone=True))
    progreso_actual = Column(Integer)  # Para logros con progreso (ej: 5/10)
    esta_completado = Column(Boolean, default=False)
```

### 🎨 **PRIORIDAD MEDIA** - Experiencia de Usuario

#### 5. **Sistema de Títulos/Badges** 🆕
**Propuesta:**
```python
class TituloUsuario(Base):
    """
    Títulos que se muestran junto al nombre.
    
    Ejemplos:
    - "🏆 Leyenda del Aprendizaje"
    - "⚡ Relámpago" (racha 30+ días)
    - "🌟 Estrella Naciente"
    - "📚 Bibliotecario"
    """
    __tablename__ = "titulos_usuario"
    
    titulo_id = Column(UUID, primary_key=True)
    nombre = Column(String(50))
    icono = Column(String(10))  # Emoji
    color = Column(String(7))  # Hex color
    requisito_nivel = Column(String(20))
    requisito_puntos = Column(Integer)
    requisito_logros = Column(Integer)  # X logros desbloqueados
    es_premium = Column(Boolean, default=False)
```

#### 6. **Sistema de Reacciones a Contenido** ✅ IMPLEMENTADO
- Ya existe modelo `Reaccion` para comentarios
- **Mejora:** Expandir a tareas, evaluaciones, avatares

#### 7. **Perfil Público Mejorado** 🔧
**Elementos a mostrar:**
- ✅ Avatar personalizado
- 🆕 Banner de perfil
- 🆕 Marco decorativo
- ✅ Nivel y puntos
- ✅ Insignias obtenidas
- 🆕 Logros destacados (3 favoritos)
- ✅ Racha actual
- 🆕 Título activo
- ✅ Etiquetas
- 🆕 Estadísticas (tareas completadas, puntuación promedio, etc.)

### 🌟 **PRIORIDAD BAJA** - Features Avanzadas

#### 8. **Sistema de Mascotas/Compañeros Virtuales** 🆕
```python
class MascotaVirtual(Base):
    """Mascota que evoluciona con actividad del usuario"""
    mascota_id = Column(UUID, primary_key=True)
    usuario_id = Column(UUID, ForeignKey("Usuario.usuario_id"))
    tipo_mascota = Column(String(50))  # gato, perro, dragon, etc.
    nombre = Column(String(50))
    nivel = Column(Integer, default=1)
    experiencia = Column(Integer, default=0)
    felicidad = Column(Integer, default=100)
    hambre = Column(Integer, default=0)
    ultima_interaccion = Column(TIMESTAMP(timezone=True))
    
    # Items equipados
    accesorio_1 = Column(UUID, ForeignKey("tienda_items.item_id"))
    accesorio_2 = Column(UUID, ForeignKey("tienda_items.item_id"))
```

#### 9. **Sistema de Eventos Temporales** 🆕
```python
class EventoTemporada(Base):
    """Eventos especiales con recompensas únicas"""
    evento_id = Column(UUID, primary_key=True)
    nombre = Column(String(100))
    descripcion = Column(TEXT)
    fecha_inicio = Column(TIMESTAMP(timezone=True))
    fecha_fin = Column(TIMESTAMP(timezone=True))
    tema = Column(String(50))  # halloween, navidad, etc.
    items_exclusivos = Column(JSON)  # IDs de items solo en este evento
    desafios_json = Column(JSON)  # Desafíos especiales
```

#### 10. **Sistema de Clanes/Equipos** 🆕
```python
class Clan(Base):
    """Grupos de estudiantes que compiten"""
    clan_id = Column(UUID, primary_key=True)
    nombre = Column(String(50))
    descripcion = Column(TEXT)
    escudo_url = Column(String(500))
    lider_id = Column(UUID, ForeignKey("Usuario.usuario_id"))
    puntos_totales = Column(Integer, default=0)
    miembros_max = Column(Integer, default=30)
    es_publico = Column(Boolean, default=True)
    fecha_creacion = Column(TIMESTAMP(timezone=True))
    
class MiembroClan(Base):
    usuario_id = Column(UUID, ForeignKey("Usuario.usuario_id"), primary_key=True)
    clan_id = Column(UUID, ForeignKey("clanes.clan_id"), primary_key=True)
    rol_clan = Column(String(20))  # lider, oficial, miembro
    contribucion_puntos = Column(Integer, default=0)
    fecha_union = Column(TIMESTAMP(timezone=True))
```

---

## 🛠️ Plan de Implementación Sugerido

### **Fase 1: Completar Funcionalidad Core** (1-2 semanas)
1. ✅ Sistema de puntos (COMPLETO)
2. 🔧 Endpoints de rachas (CRÍTICO)
3. 🔧 Endpoints de tienda (CRÍTICO)
4. 🆕 Foto de perfil y banner (ALTA PRIORIDAD)

### **Fase 2: Mejorar Experiencia** (1 semana)
1. 🆕 Sistema de logros
2. 🆕 Títulos de usuario
3. 🔧 Perfil público mejorado

### **Fase 3: Features Avanzadas** (2-3 semanas)
1. 🆕 Mascotas virtuales
2. 🆕 Eventos temporales
3. 🆕 Sistema de clanes

---

## 📋 Checklist de Implementación Inmediata

### Para Completar el Sistema Actual:

#### **1. Foto de Perfil y Banner** ⏰ 2-3 días
- [ ] Migración para agregar campos a Usuario
- [ ] Endpoint upload foto de perfil
- [ ] Endpoint upload banner
- [ ] Endpoint equipar banner de tienda
- [ ] Endpoint equipar marco de perfil
- [ ] Frontend: Componente PerfilEditor
- [ ] Frontend: Preview de perfil con banner/marco

#### **2. Sistema de Rachas** ⏰ 3-4 días
- [ ] Servicio RachaService completo
- [ ] Endpoints de racha
- [ ] Job automático para verificar rachas perdidas
- [ ] Items funcionales de recuperación
- [ ] Frontend: Componente RachaDisplay
- [ ] Frontend: Historial de rachas
- [ ] Sistema de notificaciones de racha

#### **3. Sistema de Tienda** ⏰ 4-5 días
- [ ] Servicio TiendaService completo
- [ ] Todos los endpoints de tienda
- [ ] Seed inicial de items básicos
- [ ] Frontend: Componente Tienda con categorías
- [ ] Frontend: Modal de detalle de item
- [ ] Frontend: Carrito y compra
- [ ] Frontend: Inventario visual
- [ ] Sistema de equipar items

#### **4. Crear Items Iniciales** ⏰ 1-2 días
- [ ] Script para poblar tienda con:
  - 10 fondos de avatar (común)
  - 10 banners de perfil (común-raro)
  - 10 marcos decorativos (raro-épico)
  - 20 piezas de ropa avatar (todos los niveles)
  - 15 accesorios avatar
  - 5 items funcionales
  - 10 etiquetas personalizadas

#### **5. Sistema de Logros Básico** ⏰ 3-4 días
- [ ] Modelos Logro y UsuarioLogro
- [ ] Migración de base de datos
- [ ] Servicio LogroService
- [ ] Endpoints de logros
- [ ] Seed de logros iniciales (20-30)
- [ ] Sistema de verificación automática
- [ ] Frontend: Panel de logros
- [ ] Frontend: Notificación de logro desbloqueado

---

## 💡 Recomendaciones Técnicas

### **Base de Datos**
- Usar índices en columnas frecuentes (rareza, categoria, es_activo)
- Implementar cache para items de tienda (Redis)
- Archivado automático de transacciones antiguas

### **Backend**
- Servicios independientes para cada módulo
- Jobs programados para:
  - Verificar rachas (diario a medianoche)
  - Procesar recompensas de nivel
  - Limpiar cache
- Validaciones robustas de compras (puntos, requisitos, stock)

### **Frontend**
- Lazy loading de imágenes de items
- Animaciones para desbloqueos y logros
- Sonidos opcionales para eventos importantes
- Cache local de inventario

### **Seguridad**
- Rate limiting en endpoints de compra
- Validación server-side de todas las transacciones
- Logs de todas las operaciones con puntos
- Prevención de duplicación de items

---

## 🎯 Métricas de Éxito

### KPIs del Sistema de Gamificación:
- **Engagement:** % usuarios activos diarios
- **Retention:** Usuarios con racha 7+ días
- **Monetización:** Puntos gastados vs ganados
- **Personalización:** % usuarios con items equipados
- **Logros:** Promedio de logros por usuario
- **Social:** Interacciones en perfiles

---

## 📚 Referencias y Recursos

### Assets Necesarios:
- Iconos de logros (Font Awesome / Custom)
- Banners temáticos (1920x400px)
- Marcos decorativos (SVG)
- Sprites de mascotas (opcional)

### Inspiración:
- Discord (sistema de badges y perfiles)
- Duolingo (rachas y logros)
- League of Legends (tienda y rareza)
- Xbox/PlayStation (sistema de logros)

---

**Última actualización:** 3 de noviembre de 2025  
**Próxima revisión:** Después de implementar Fase 1
