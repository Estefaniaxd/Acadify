# Sistema de Avatares - Acadify

## Descripción General

El sistema de avatares permite a los usuarios crear y personalizar avatares utilizando un sistema de capas (base, pelo, ojos, ropa, accesorios, fondo). Los usuarios pueden ver un preview inmediato de sus creaciones, guardar avatares finales y gestionar su galería personal.

## Arquitectura

### Backend (FastAPI)

#### Modelos de Base de Datos

1. **AvatarAsset** (`/backend/src/models/avatar_asset.py`)
   - Almacena metadatos de assets PNG
   - Campos: id, filename, category, display_name, width, height, file_size, is_normalized, metadata
   - Validación automática de archivos PNG y normalización a 512x512

2. **UserAvatar** (`/backend/src/models/user_avatar.py`)
   - Almacena avatares compuestos por usuarios
   - Campos: id, user_id, name, layers (JSON), image_url, layers_hash, is_active, is_public
   - Un solo avatar activo por usuario

#### Servicios Principales

1. **AvatarService** (`/backend/src/services/avatar_service.py`)
   - Composición de imágenes con PIL
   - Cache de previews con Redis (TTL: 1 hora)
   - Validación de capas y assets
   - Generación de hashes únicos para composiciones

2. **StorageService** (`/backend/src/services/storage.py`)
   - Abstracción para almacenamiento local/S3
   - Manejo de uploads de assets
   - URLs públicas para acceso a assets

3. **ImageUtils** (`/backend/src/utils/image_utils.py`)
   - Validación de imágenes PNG
   - Normalización a resolución estándar (512x512)
   - Composición de capas ordenadas
   - Optimización de archivos

#### API Endpoints (`/backend/src/api/routes/avatar.py`)

```python
# Assets
GET /api/v1/avatar/assets/manifest    # Obtener manifest de assets
POST /api/v1/avatar/assets           # Subir nuevo asset (admin)
GET /api/v1/avatar/assets/{id}       # Obtener asset específico
PUT /api/v1/avatar/assets/{id}       # Actualizar asset (admin)
DELETE /api/v1/avatar/assets/{id}    # Eliminar asset (admin)

# Previews y composición
GET /api/v1/avatar/preview           # Generar preview de capas
POST /api/v1/avatar/save             # Guardar avatar final

# Gestión de avatares de usuario
GET /api/v1/avatar/my                # Obtener mis avatares
PUT /api/v1/avatar/{id}/active       # Establecer avatar activo
PUT /api/v1/avatar/{id}/privacy      # Cambiar privacidad
DELETE /api/v1/avatar/{id}           # Eliminar avatar
```

### Frontend (React + TypeScript)

#### Componentes Principales

1. **AvatarEditor** (`/frontend/src/components/avatar/AvatarEditor.tsx`)
   - Componente principal del editor
   - Integra PreviewCanvas, LayerPicker y SaveAvatarDialog
   - Manejo de estado global del avatar en construcción

2. **PreviewCanvas** (`/frontend/src/components/avatar/PreviewCanvas.tsx`)
   - Preview en tiempo real del avatar
   - Soporte para renderizado cliente/servidor
   - Estados de carga y error
   - Responsive design

3. **LayerPicker** (`/frontend/src/components/avatar/LayerPicker.tsx`)
   - Selección de assets por categoría
   - Tabs de navegación entre categorías
   - Grid responsive con search
   - Estados de selección visual

4. **SaveAvatarDialog** (`/frontend/src/components/avatar/SaveAvatarDialog.tsx`)
   - Modal para guardar avatar
   - Validación de nombre (2-100 caracteres)
   - Opciones: activar y hacer público
   - Estados de carga durante guardado

5. **AvatarGallery** (`/frontend/src/components/avatar/AvatarGallery.tsx`)
   - Galería de avatares guardados
   - Filtros: todos, activos, públicos, privados
   - Ordenamiento: fecha, nombre, estado activo
   - Búsqueda por nombre
   - Acciones: activar, editar, eliminar

#### Hooks Personalizados

1. **useAvatarEditor** (`/frontend/src/components/avatar/useAvatar.ts`)
   - Estado del editor de avatares
   - Generación automática de previews
   - Guardado de avatares
   - Gestión de capas seleccionadas

2. **useUserAvatars** (`/frontend/src/components/avatar/useAvatar.ts`)
   - Gestión de galería de avatares
   - CRUD de avatares personales
   - Sincronización con backend
   - Estados de carga y error

#### API Client (`/frontend/src/components/avatar/avatarAPI.ts`)

```typescript
// Principales funciones
avatarAPI.getAssetsManifest()           // Obtener assets disponibles
avatarAPI.generatePreview(layers)       // Generar preview
avatarAPI.saveAvatar(name, layers, ...)  // Guardar avatar
avatarAPI.getMyAvatars()                // Obtener mis avatares
avatarAPI.setActiveAvatar(id)           // Activar avatar
avatarAPI.deleteAvatar(id)              // Eliminar avatar
```

## Estructura de Assets

### Directorio de Assets (`/backend/static/assets/`)

```
assets/
├── manifest.json          # Índice de todos los assets
├── base/                  # Bases/cuerpos
│   ├── base_001.png
│   └── base_002.png
├── hair/                  # Peinados
│   ├── hair_001.png
│   └── hair_002.png
├── eyes/                  # Ojos
│   ├── eyes_001.png
│   └── eyes_002.png
├── clothing/              # Ropa
│   ├── shirt_001.png
│   └── dress_001.png
├── accessories/           # Accesorios
│   ├── glasses_001.png
│   └── hat_001.png
└── background/            # Fondos
    ├── bg_001.png
    └── bg_002.png
```

### Especificaciones Técnicas

- **Formato**: PNG con transparencia
- **Resolución**: 512x512 pixels (normalización automática)
- **Capas ordenadas**: background → base → clothing → hair → eyes → accessories
- **Naming convention**: `{category}_{number}.png`

## Configuración y Variables de Entorno

### Backend (`/backend/.env`)

```env
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost/acadify

# Redis (cache de previews)
REDIS_URL=redis://localhost:6379/0

# Almacenamiento
AVATAR_STORAGE_TYPE=local  # o 's3'
AVATAR_ASSETS_PATH=/path/to/assets
AWS_S3_BUCKET=your-bucket  # si storage_type=s3
AWS_REGION=us-east-1

# URLs públicas
AVATAR_ASSETS_BASE_URL=http://localhost:8000/static/assets
```

### Frontend (`/frontend/.env`)

```env
# URLs de API
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_ASSETS_BASE_URL=http://localhost:8000/static/assets
```

## Instalación y Configuración

### 1. Backend Setup

```bash
cd backend/

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
alembic upgrade head

# Cargar assets iniciales (opcional)
python scripts/load_initial_assets.py

# Ejecutar servidor
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend/

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev
```

### 3. Assets Setup

1. Crear directorio de assets: `/backend/static/assets/`
2. Organizar assets por categorías según estructura
3. Ejecutar comando de sincronización: `python scripts/sync_assets.py`
4. Verificar manifest en: `GET /api/v1/avatar/assets/manifest`

## Uso del Sistema

### 1. Crear Avatar

```typescript
import { AvatarEditor } from '@/components/avatar';

function MyPage() {
  return (
    <div>
      <h1>Crear Avatar</h1>
      <AvatarEditor />
    </div>
  );
}
```

### 2. Galería de Avatares

```typescript
import { AvatarGallery } from '@/components/avatar';

function ProfilePage() {
  const handleEditAvatar = (avatar) => {
    // Lógica para editar avatar
  };

  return (
    <AvatarGallery 
      onEditAvatar={handleEditAvatar}
      onSelectAvatar={(avatar) => console.log('Selected:', avatar)}
    />
  );
}
```

### 3. Preview Standalone

```typescript
import { PreviewCanvas } from '@/components/avatar';

const layers = [
  { category: 'base', file: 'base_001.png' },
  { category: 'hair', file: 'hair_002.png' }
];

function AvatarPreview() {
  return (
    <PreviewCanvas 
      layers={layers}
      size={200}
      className="rounded-full"
    />
  );
}
```

## Cache y Rendimiento

### Redis Cache
- **Previews**: TTL de 1 hora
- **Manifests**: TTL de 24 horas
- **Keys**: `avatar:preview:{hash}`, `avatar:manifest`

### Optimizaciones Frontend
- Lazy loading de componentes
- Memoización de previews
- Debounce en búsquedas
- Virtual scrolling en galerías grandes

## Seguridad y Validaciones

### Backend
- Autenticación JWT requerida
- Validación de tipos de archivo (solo PNG)
- Sanitización de nombres de archivo
- Rate limiting en endpoints de preview
- Validación de ownership para CRUD operations

### Frontend
- Validación de formularios
- Escape de contenido HTML
- Manejo seguro de URLs
- Estados de error controlados

## Testing

### Backend Tests
```bash
# Ejecutar tests
pytest tests/test_avatar.py -v

# Coverage
pytest --cov=src.services.avatar_service tests/
```

### Frontend Tests
```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e
```

## Troubleshooting

### Problemas Comunes

1. **Preview no se genera**
   - Verificar que Redis esté corriendo
   - Verificar permisos de directorio de assets
   - Revisar logs del servicio de imágenes

2. **Assets no se cargan**
   - Verificar configuración de AVATAR_ASSETS_BASE_URL
   - Verificar estructura de directorios
   - Verificar permisos de lectura

3. **Error al guardar avatar**
   - Verificar autenticación del usuario
   - Verificar límites de tamaño de archivo
   - Revisar logs de base de datos

### Logs Importantes

```bash
# Backend logs
tail -f api_debug.log

# Specific avatar service logs
grep "avatar" api_debug.log

# Database queries
grep "avatar_asset\|user_avatar" api_debug.log
```

## Roadmap y Mejoras Futuras

### Versión 1.1
- [ ] Animaciones de avatar
- [ ] Efectos y filtros
- [ ] Importación de assets personalizados

### Versión 1.2
- [ ] Mercado de assets comunitarios
- [ ] Colaboración en tiempo real
- [ ] API pública para terceros

### Versión 2.0
- [ ] Avatares 3D
- [ ] Realidad aumentada
- [ ] AI-generated assets