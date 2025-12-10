# 🎨 Sistema de Categorías Jerárquicas - Avatar System

> **Fecha**: 14 de noviembre de 2025  
> **Versión**: 2.0.0  
> **Estado**: En Diseño

---

## 📋 Tabla de Contenidos

- [Resumen Ejecutivo](#resumen-ejecutivo)
- [Problema Actual](#problema-actual)
- [Solución Propuesta](#solución-propuesta)
- [Arquitectura de Categorías](#arquitectura-de-categorías)
- [Reglas de Compatibilidad de Género](#reglas-de-compatibilidad-de-género)
- [Esquema de Base de Datos](#esquema-de-base-de-datos)
- [Cambios Backend](#cambios-backend)
- [Cambios Frontend](#cambios-frontend)
- [Plan de Migración](#plan-de-migración)
- [Testing](#testing)

---

## 🎯 Resumen Ejecutivo

**Objetivo**: Crear un sistema de categorías jerárquicas y granulares para avatares con reglas de compatibilidad de género, permitiendo:

1. **Categorías principales** (Clothes, Hair, Accessories, etc.)
2. **Subcategorías específicas** (Shirts, Pants dentro de Clothes)
3. **Filtrado inteligente** basado en género base del avatar
4. **Escalabilidad** para agregar nuevas categorías fácilmente
5. **Type-safety** usando ENUMs en PostgreSQL y TypeScript

---

## ❌ Problema Actual

### **Limitaciones**

1. **Categorías planas**: Solo un nivel (hair, eyes, mouth, shirt, pants, etc.)
2. **Sin jerarquía**: No hay agrupación lógica (todas las ropas al mismo nivel)
3. **Compatibilidad manual**: No hay validación de género en backend
4. **Duplicados**: Assets en carpetas `male/` y `unisex/` causaban duplicación en UI
5. **Escalabilidad**: Difícil agregar nuevas categorías sin modificar código

### **Ejemplo de Problema**

```typescript
// ❌ Actual: Lista plana sin organización
categories: {
  hair: [...],
  eyes: [...],
  mouth: [...],
  shirt: [...],
  pants: [...],
  skirt: [...],
  shoes: [...],
  socks: [...],
  jacket: [...],
  accessories: [...]  // Mezcla ojos, manos, boca, cabeza
}
```

---

## ✅ Solución Propuesta

### **Jerarquía de 3 Niveles**

```
CATEGORY (Principal)
  ├── SUBCATEGORY (Específica)
  │     ├── ITEM (Asset individual)
  │     └── ITEM
  └── SUBCATEGORY
        ├── ITEM
        └── ITEM
```

### **Ejemplo Concreto**

```typescript
// ✅ Nuevo: Estructura jerárquica organizada
categories: {
  clothes: {
    shirts: [
      { filename: 'shirt_casual_1.png', target_gender: 'unisex' },
      { filename: 'shirt_formal_1.png', target_gender: 'male' }
    ],
    pants: [
      { filename: 'pants_jeans_1.png', target_gender: 'unisex' },
      { filename: 'pants_formal_1.png', target_gender: 'male' }
    ],
    skirts: [
      { filename: 'skirt_short_1.png', target_gender: 'female' }
    ],
    jackets: [...],
    shoes: [...],
    socks: [...]
  },
  hair: {
    short: [...],
    long: [...],
    curly: [...],
    straight: [...],
    braided: [...]
  },
  accessories: {
    eyes: [...],      // Gafas, lentes de contacto
    hands: [...],     // Guantes, relojes, pulseras
    mouth: [...],     // Piercings, mascarillas
    head: [...],      // Gorras, diademas, sombreros
    neck: [...],      // Collares, bufandas
    ears: [...]       // Aretes, audífonos
  },
  facial: {
    eyes: [...],      // Forma de ojos
    eyebrows: [...],  // Cejas
    nose: [...],      // Nariz
    mouth: [...],     // Boca/labios
    makeup: [...]     // Maquillaje
  },
  base: {
    body: [
      { filename: 'base/male/body_1.png', target_gender: 'male' },
      { filename: 'base/female/body_1.png', target_gender: 'female' }
    ]
  },
  backgrounds: {
    indoor: [...],
    outdoor: [...],
    abstract: [...]
  }
}
```

---

## 🏗️ Arquitectura de Categorías

### **Categorías Principales (Category)**

| Category | Descripción | Subcategorías |
|----------|-------------|---------------|
| `base` | Cuerpo base del avatar | `body` |
| `hair` | Peinados y cabello | `short`, `long`, `curly`, `straight`, `braided`, `bald` |
| `facial` | Rasgos faciales | `eyes`, `eyebrows`, `nose`, `mouth`, `makeup` |
| `clothes` | Vestimenta completa | `shirts`, `pants`, `skirts`, `jackets`, `dresses`, `shoes`, `socks` |
| `accessories` | Accesorios corporales | `eyes`, `hands`, `mouth`, `head`, `neck`, `ears` |
| `backgrounds` | Fondos y escenarios | `indoor`, `outdoor`, `abstract`, `solid` |

### **ENUM CategoryType (PostgreSQL)**

```sql
CREATE TYPE category_type AS ENUM (
  'base',
  'hair',
  'facial',
  'clothes',
  'accessories',
  'backgrounds'
);
```

### **ENUM SubcategoryType (PostgreSQL)**

```sql
CREATE TYPE subcategory_type AS ENUM (
  -- Hair
  'hair_short', 'hair_long', 'hair_curly', 'hair_straight', 'hair_braided', 'hair_bald',
  
  -- Facial
  'facial_eyes', 'facial_eyebrows', 'facial_nose', 'facial_mouth', 'facial_makeup',
  
  -- Clothes
  'clothes_shirts', 'clothes_pants', 'clothes_skirts', 'clothes_jackets', 
  'clothes_dresses', 'clothes_shoes', 'clothes_socks',
  
  -- Accessories
  'accessories_eyes', 'accessories_hands', 'accessories_mouth', 
  'accessories_head', 'accessories_neck', 'accessories_ears',
  
  -- Backgrounds
  'backgrounds_indoor', 'backgrounds_outdoor', 'backgrounds_abstract', 'backgrounds_solid',
  
  -- Base
  'base_body'
);
```

### **ENUM GenderType (PostgreSQL)**

```sql
CREATE TYPE gender_type AS ENUM (
  'male',
  'female',
  'unisex'
);
```

---

## 👔 Reglas de Compatibilidad de Género

### **Principio Base**

> **"Los avatares femeninos pueden usar ropa masculina (más grande), pero los masculinos NO pueden usar ropa femenina (más pequeña)"**

### **Tabla de Compatibilidad**

| Base Avatar | Puede Usar Items de Género |
|-------------|----------------------------|
| **Female** | `female` + `male` + `unisex` |
| **Male** | `male` + `unisex` |

### **Implementación Backend**

```python
# backend/src/services/avatar_service.py

def can_wear_item(base_gender: str, item_gender: str) -> bool:
    """
    Determina si un avatar puede usar un item según género.
    
    Args:
        base_gender: Género base del avatar ('male' o 'female')
        item_gender: Género del item ('male', 'female' o 'unisex')
        
    Returns:
        True si el avatar puede usar el item, False otherwise
        
    Rules:
        - Unisex: Todos pueden usar
        - Female base: Puede usar male, female, unisex
        - Male base: Solo puede usar male, unisex (NO female)
    """
    if item_gender == "unisex":
        return True
    
    if base_gender == "female":
        return True  # Female puede usar todo
    
    if base_gender == "male":
        return item_gender != "female"  # Male NO puede usar female
    
    return False
```

### **Implementación Frontend**

```typescript
// frontend/src/hooks/useGenderCompatibility.ts

export function canSelectItem(
  baseGender: 'male' | 'female',
  itemGender: 'male' | 'female' | 'unisex'
): boolean {
  if (itemGender === 'unisex') return true;
  if (baseGender === 'female') return true; // Female can wear everything
  if (baseGender === 'male') return itemGender !== 'female'; // Male cannot wear female items
  return false;
}

export function getIncompatibilityReason(
  baseGender: 'male' | 'female',
  itemGender: 'male' | 'female' | 'unisex'
): string | null {
  if (canSelectItem(baseGender, itemGender)) return null;
  
  return `Este item es exclusivo para avatares femeninos. Tu avatar masculino no puede usarlo porque es de talla más pequeña.`;
}
```

---

## 💾 Esquema de Base de Datos

### **Cambios en `avatar_asset`**

```sql
-- Migración Alembic: add_subcategory_and_enums

-- 1. Crear ENUMs
CREATE TYPE gender_type AS ENUM ('male', 'female', 'unisex');
CREATE TYPE category_type AS ENUM ('base', 'hair', 'facial', 'clothes', 'accessories', 'backgrounds');
CREATE TYPE subcategory_type AS ENUM (
  'hair_short', 'hair_long', 'hair_curly', 'hair_straight', 'hair_braided', 'hair_bald',
  'facial_eyes', 'facial_eyebrows', 'facial_nose', 'facial_mouth', 'facial_makeup',
  'clothes_shirts', 'clothes_pants', 'clothes_skirts', 'clothes_jackets', 'clothes_dresses', 'clothes_shoes', 'clothes_socks',
  'accessories_eyes', 'accessories_hands', 'accessories_mouth', 'accessories_head', 'accessories_neck', 'accessories_ears',
  'backgrounds_indoor', 'backgrounds_outdoor', 'backgrounds_abstract', 'backgrounds_solid',
  'base_body'
);

-- 2. Agregar columna subcategory
ALTER TABLE avatar_asset 
ADD COLUMN subcategory subcategory_type;

-- 3. Convertir target_gender a ENUM (requiere recrear columna)
ALTER TABLE avatar_asset 
ALTER COLUMN target_gender TYPE gender_type 
USING target_gender::gender_type;

-- 4. Convertir category a ENUM
ALTER TABLE avatar_asset
ALTER COLUMN category TYPE category_type
USING category::category_type;

-- 5. Crear índice compuesto para queries optimizadas
CREATE INDEX idx_avatar_asset_category_subcategory_gender 
ON avatar_asset(category, subcategory, target_gender) 
WHERE is_active = 'Y';
```

### **Modelo SQLAlchemy Actualizado**

```python
# backend/src/models/avatar_asset.py

from enum import Enum as PyEnum
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

class GenderType(str, PyEnum):
    """Enum para tipos de género de assets"""
    MALE = "male"
    FEMALE = "female"
    UNISEX = "unisex"

class CategoryType(str, PyEnum):
    """Enum para categorías principales"""
    BASE = "base"
    HAIR = "hair"
    FACIAL = "facial"
    CLOTHES = "clothes"
    ACCESSORIES = "accessories"
    BACKGROUNDS = "backgrounds"

class SubcategoryType(str, PyEnum):
    """Enum para subcategorías"""
    # Hair
    HAIR_SHORT = "hair_short"
    HAIR_LONG = "hair_long"
    HAIR_CURLY = "hair_curly"
    HAIR_STRAIGHT = "hair_straight"
    HAIR_BRAIDED = "hair_braided"
    HAIR_BALD = "hair_bald"
    
    # Facial
    FACIAL_EYES = "facial_eyes"
    FACIAL_EYEBROWS = "facial_eyebrows"
    FACIAL_NOSE = "facial_nose"
    FACIAL_MOUTH = "facial_mouth"
    FACIAL_MAKEUP = "facial_makeup"
    
    # Clothes
    CLOTHES_SHIRTS = "clothes_shirts"
    CLOTHES_PANTS = "clothes_pants"
    CLOTHES_SKIRTS = "clothes_skirts"
    CLOTHES_JACKETS = "clothes_jackets"
    CLOTHES_DRESSES = "clothes_dresses"
    CLOTHES_SHOES = "clothes_shoes"
    CLOTHES_SOCKS = "clothes_socks"
    
    # Accessories
    ACCESSORIES_EYES = "accessories_eyes"
    ACCESSORIES_HANDS = "accessories_hands"
    ACCESSORIES_MOUTH = "accessories_mouth"
    ACCESSORIES_HEAD = "accessories_head"
    ACCESSORIES_NECK = "accessories_neck"
    ACCESSORIES_EARS = "accessories_ears"
    
    # Backgrounds
    BACKGROUNDS_INDOOR = "backgrounds_indoor"
    BACKGROUNDS_OUTDOOR = "backgrounds_outdoor"
    BACKGROUNDS_ABSTRACT = "backgrounds_abstract"
    BACKGROUNDS_SOLID = "backgrounds_solid"
    
    # Base
    BASE_BODY = "base_body"

class AvatarAsset(Base):
    __tablename__ = "avatar_asset"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    category: Mapped[CategoryType] = mapped_column(Enum(CategoryType, name="category_type"))
    subcategory: Mapped[SubcategoryType | None] = mapped_column(
        Enum(SubcategoryType, name="subcategory_type"), 
        nullable=True
    )
    target_gender: Mapped[GenderType] = mapped_column(Enum(GenderType, name="gender_type"))
    width: Mapped[int]
    height: Mapped[int]
    file_size: Mapped[int]
    sha256: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[str] = mapped_column(String(1), default="Y")
    canonical_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_normalized: Mapped[bool] = mapped_column(default=False)
    meta_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )
```

---

## 🔧 Cambios Backend

### **1. Schemas Pydantic**

```python
# backend/src/schemas/avatar.py

from typing import Literal
from pydantic import BaseModel, Field

GenderType = Literal["male", "female", "unisex"]
CategoryType = Literal["base", "hair", "facial", "clothes", "accessories", "backgrounds"]

class AssetResponse(BaseModel):
    """Schema para asset individual en manifest"""
    filename: str
    url: str
    category: CategoryType
    subcategory: str | None = None
    target_gender: GenderType
    width: int = 512
    height: int = 512
    
    model_config = ConfigDict(from_attributes=True)

class ManifestResponseHierarchical(BaseModel):
    """Schema para manifest jerárquico"""
    categories: dict[CategoryType, dict[str, list[AssetResponse]]]  # {clothes: {shirts: [...], pants: [...]}}
    resolution: str = "512x512"
    total_assets: int
    base_gender: GenderType | None = None  # Género base del avatar actual
    
class ManifestResponseFlat(BaseModel):
    """Schema para manifest plano (backward compatibility)"""
    categories: dict[str, list[AssetResponse]]  # {hair: [...], eyes: [...]}
    resolution: str = "512x512"
    total_assets: int
```

### **2. CRUD Methods**

```python
# backend/src/crud/avatar/avatar_asset_crud.py

class CRUDAvatarAsset(CRUDBase[AvatarAsset, AvatarAssetCreate, AvatarAssetUpdate]):
    
    async def get_by_category_and_subcategory(
        self,
        category: CategoryType,
        subcategory: SubcategoryType | None = None,
        gender: GenderType | None = None,
        active_only: bool = True
    ) -> list[AvatarAsset]:
        """Obtener assets filtrados por category, subcategory y género"""
        query = select(AvatarAsset).where(AvatarAsset.category == category)
        
        if subcategory:
            query = query.where(AvatarAsset.subcategory == subcategory)
        
        if gender:
            # Incluir gender específico + unisex
            query = query.where(
                or_(
                    AvatarAsset.target_gender == gender,
                    AvatarAsset.target_gender == GenderType.UNISEX
                )
            )
        
        if active_only:
            query = query.where(AvatarAsset.is_active == "Y")
        
        result = await self.db.execute(query.order_by(AvatarAsset.filename))
        return list(result.scalars().all())
    
    async def get_compatible_items(
        self,
        base_gender: GenderType,
        category: CategoryType | None = None,
        subcategory: SubcategoryType | None = None
    ) -> list[AvatarAsset]:
        """Obtener items compatibles con base_gender del avatar"""
        query = select(AvatarAsset).where(AvatarAsset.is_active == "Y")
        
        # Aplicar reglas de compatibilidad
        if base_gender == GenderType.MALE:
            # Male solo puede usar male + unisex (NO female)
            query = query.where(AvatarAsset.target_gender != GenderType.FEMALE)
        # Female puede usar todos (no filter needed)
        
        if category:
            query = query.where(AvatarAsset.category == category)
        
        if subcategory:
            query = query.where(AvatarAsset.subcategory == subcategory)
        
        result = await self.db.execute(query.order_by(AvatarAsset.filename))
        return list(result.scalars().all())
```

### **3. Service Methods**

```python
# backend/src/services/avatar_service.py

class AvatarService:
    
    async def get_manifest_hierarchical(
        self,
        base_gender: GenderType | None = None
    ) -> ManifestResponseHierarchical:
        """
        Obtener manifest jerárquico organizado por category -> subcategory -> items
        
        Args:
            base_gender: Si se provee, filtrar por compatibilidad
        """
        crud = CRUDAvatarAsset(self.db)
        
        # Obtener todos los assets activos
        if base_gender:
            assets = await crud.get_compatible_items(base_gender)
        else:
            query = select(AvatarAsset).where(AvatarAsset.is_active == "Y")
            result = await self.db.execute(query)
            assets = list(result.scalars().all())
        
        # Organizar jerárquicamente
        hierarchical_categories: dict[CategoryType, dict[str, list[AssetResponse]]] = {}
        
        for asset in assets:
            category = asset.category
            subcategory = asset.subcategory or "default"
            
            if category not in hierarchical_categories:
                hierarchical_categories[category] = {}
            
            if subcategory not in hierarchical_categories[category]:
                hierarchical_categories[category][subcategory] = []
            
            asset_response = AssetResponse(
                filename=asset.filename,
                url=f"{self.base_url}/static/assets/{asset.filename}",
                category=asset.category,
                subcategory=asset.subcategory,
                target_gender=asset.target_gender,
                width=asset.width,
                height=asset.height
            )
            
            hierarchical_categories[category][subcategory].append(asset_response)
        
        return ManifestResponseHierarchical(
            categories=hierarchical_categories,
            resolution="512x512",
            total_assets=len(assets),
            base_gender=base_gender
        )
    
    def can_wear_item(self, base_gender: GenderType, item_gender: GenderType) -> bool:
        """Validar compatibilidad de género"""
        if item_gender == GenderType.UNISEX:
            return True
        if base_gender == GenderType.FEMALE:
            return True  # Female puede usar todo
        if base_gender == GenderType.MALE:
            return item_gender != GenderType.FEMALE  # Male NO puede usar female
        return False
    
    async def validate_avatar_layers(
        self,
        base_gender: GenderType,
        layers: list[LayerItem]
    ) -> tuple[bool, list[str]]:
        """
        Validar que todas las capas sean compatibles con base_gender
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        for layer in layers:
            # Obtener asset de BD
            crud = CRUDAvatarAsset(self.db)
            result = await self.db.execute(
                select(AvatarAsset).where(AvatarAsset.filename == layer.filename)
            )
            asset = result.scalar_one_or_none()
            
            if not asset:
                errors.append(f"Asset no encontrado: {layer.filename}")
                continue
            
            if not self.can_wear_item(base_gender, asset.target_gender):
                errors.append(
                    f"Avatar {base_gender} no puede usar item {asset.target_gender}: {layer.filename}"
                )
        
        return len(errors) == 0, errors
```

### **4. API Endpoints**

```python
# backend/src/api/routes/avatar.py

@router.get("/assets", response_model=ManifestResponseHierarchical)
async def get_assets_manifest_hierarchical(
    base_gender: GenderType | None = Query(None, description="Filtrar por compatibilidad con género base"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener manifest de assets jerárquico
    
    - Si base_gender se provee, retorna solo items compatibles
    - Organizado por category -> subcategory -> items
    """
    service = AvatarService(db)
    return await service.get_manifest_hierarchical(base_gender)

@router.get("/assets/flat", response_model=ManifestResponseFlat)
async def get_assets_manifest_flat(
    gender: GenderType | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener manifest plano (backward compatibility)
    """
    service = AvatarService(db)
    return await service.get_manifest_for_gender(gender)
```

---

## 🎨 Cambios Frontend

### **1. Types TypeScript**

```typescript
// frontend/src/types/avatar.ts

export type GenderType = 'male' | 'female' | 'unisex';

export type CategoryType = 
  | 'base' 
  | 'hair' 
  | 'facial' 
  | 'clothes' 
  | 'accessories' 
  | 'backgrounds';

export interface AssetInfo {
  filename: string;
  url: string;
  category: CategoryType;
  subcategory?: string;
  target_gender: GenderType;
  width: number;
  height: number;
}

export interface ManifestHierarchical {
  categories: Record<CategoryType, Record<string, AssetInfo[]>>;
  resolution: string;
  total_assets: number;
  base_gender?: GenderType;
}

export interface CategoryConfig {
  key: CategoryType;
  label: string;
  icon: React.ComponentType;
  color: string;
  description: string;
  subcategories: SubcategoryConfig[];
}

export interface SubcategoryConfig {
  key: string;
  label: string;
  description?: string;
}
```

### **2. API Client**

```typescript
// frontend/src/services/avatarAPI.ts

export const avatarAPI = {
  async getAssetsManifestHierarchical(
    baseGender?: GenderType
  ): Promise<ManifestHierarchical> {
    const params = baseGender ? `?base_gender=${baseGender}` : '';
    const response = await apiClient.get<ManifestHierarchical>(
      `/api/avatar/assets${params}`
    );
    return response.data;
  },
  
  async getAssetsManifestFlat(
    gender?: GenderType
  ): Promise<ManifestResponse> {
    const params = gender ? `?gender=${gender}` : '';
    const response = await apiClient.get<ManifestResponse>(
      `/api/avatar/assets/flat${params}`
    );
    return response.data;
  }
};
```

### **3. Custom Hooks**

```typescript
// frontend/src/hooks/useGenderCompatibility.ts

export function canSelectItem(
  baseGender: GenderType,
  itemGender: GenderType
): boolean {
  if (itemGender === 'unisex') return true;
  if (baseGender === 'female') return true; // Female can wear everything
  if (baseGender === 'male') return itemGender !== 'female'; // Male cannot wear female
  return false;
}

export function getIncompatibilityReason(
  baseGender: GenderType,
  itemGender: GenderType
): string | null {
  if (canSelectItem(baseGender, itemGender)) return null;
  
  return `Este item es exclusivo para avatares femeninos. Tu avatar masculino no puede usarlo porque es de talla más pequeña.`;
}

export function useGenderCompatibility(baseGender: GenderType) {
  const canSelect = useCallback(
    (itemGender: GenderType) => canSelectItem(baseGender, itemGender),
    [baseGender]
  );
  
  const getIncompatibilityMessage = useCallback(
    (itemGender: GenderType) => getIncompatibilityReason(baseGender, itemGender),
    [baseGender]
  );
  
  return { canSelect, getIncompatibilityMessage };
}
```

### **4. UI Component**

```typescript
// frontend/src/components/avatar/AvatarStudioV3.tsx

export function AvatarStudioV3() {
  const [selectedCategory, setSelectedCategory] = useState<CategoryType>('hair');
  const [selectedSubcategory, setSelectedSubcategory] = useState<string>('short');
  const [baseGender, setBaseGender] = useState<GenderType>('male');
  
  const { data: manifest, isLoading } = useQuery({
    queryKey: ['avatar-manifest', baseGender],
    queryFn: () => avatarAPI.getAssetsManifestHierarchical(baseGender)
  });
  
  const { canSelect, getIncompatibilityMessage } = useGenderCompatibility(baseGender);
  
  const subcategories = manifest?.categories[selectedCategory] || {};
  const items = subcategories[selectedSubcategory] || [];
  
  return (
    <div>
      {/* Tabs de categorías principales */}
      <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
        {CATEGORY_CONFIGS.map(category => (
          <TabsTrigger key={category.key} value={category.key}>
            <category.icon />
            {category.label}
          </TabsTrigger>
        ))}
      </Tabs>
      
      {/* Pills de subcategorías */}
      <div className="flex gap-2 mt-4">
        {Object.keys(subcategories).map(subcat => (
          <button
            key={subcat}
            onClick={() => setSelectedSubcategory(subcat)}
            className={cn(
              "px-4 py-2 rounded-full",
              selectedSubcategory === subcat
                ? "bg-purple-600 text-white"
                : "bg-gray-200"
            )}
          >
            {subcat}
          </button>
        ))}
      </div>
      
      {/* Grid de items */}
      <div className="grid grid-cols-3 gap-4 mt-6">
        {items.map(item => {
          const isCompatible = canSelect(item.target_gender);
          const incompatibilityReason = getIncompatibilityMessage(item.target_gender);
          
          return (
            <Tooltip key={item.filename}>
              <TooltipTrigger>
                <button
                  disabled={!isCompatible}
                  className={cn(
                    "aspect-square rounded-lg border-2",
                    isCompatible
                      ? "hover:border-purple-500"
                      : "opacity-50 cursor-not-allowed"
                  )}
                >
                  <img src={item.url} alt={item.filename} />
                </button>
              </TooltipTrigger>
              {incompatibilityReason && (
                <TooltipContent>
                  {incompatibilityReason}
                </TooltipContent>
              )}
            </Tooltip>
          );
        })}
      </div>
    </div>
  );
}
```

---

## 🔄 Plan de Migración

### **Fase 1: Preparación (Día 1)**

1. ✅ **Limpiar duplicados** (Completado)
   - Desactivar assets duplicados en BD
   - Verificar dimensiones físicas (512x512)

2. **Crear ENUMs en PostgreSQL**
   ```sql
   CREATE TYPE gender_type AS ENUM ('male', 'female', 'unisex');
   CREATE TYPE category_type AS ENUM ('base', 'hair', 'facial', 'clothes', 'accessories', 'backgrounds');
   CREATE TYPE subcategory_type AS ENUM (...);
   ```

3. **Agregar columna subcategory**
   ```sql
   ALTER TABLE avatar_asset ADD COLUMN subcategory subcategory_type;
   ```

### **Fase 2: Migración de Datos (Día 1-2)**

1. **Script de clasificación automática**
   - Analizar filenames actuales
   - Asignar subcategories basado en patrones
   - Generar reporte de assets sin clasificar

2. **Clasificación manual**
   - Revisar assets sin subcategory
   - Asignar manualmente categorías faltantes

3. **Convertir columnas a ENUM**
   ```sql
   ALTER TABLE avatar_asset 
   ALTER COLUMN target_gender TYPE gender_type 
   USING target_gender::gender_type;
   
   ALTER TABLE avatar_asset 
   ALTER COLUMN category TYPE category_type 
   USING category::category_type;
   ```

### **Fase 3: Backend (Día 2-3)**

1. **Actualizar modelos SQLAlchemy**
   - Agregar ENUMs Python
   - Actualizar AvatarAsset model

2. **Actualizar schemas Pydantic**
   - GenderType, CategoryType literals
   - ManifestResponseHierarchical

3. **Implementar lógica de compatibilidad**
   - can_wear_item()
   - validate_avatar_layers()

4. **Actualizar CRUD methods**
   - get_by_category_and_subcategory()
   - get_compatible_items()

5. **Actualizar service methods**
   - get_manifest_hierarchical()

6. **Actualizar endpoints**
   - GET /assets (hierarchical)
   - GET /assets/flat (backward compat)

### **Fase 4: Frontend (Día 3-4)**

1. **Actualizar types TypeScript**
   - GenderType, CategoryType
   - ManifestHierarchical

2. **Actualizar avatarAPI**
   - getAssetsManifestHierarchical()

3. **Crear hooks**
   - useGenderCompatibility()

4. **Actualizar UI**
   - AvatarStudioV3 con tabs + subcategorías
   - Disabled states para items incompatibles

### **Fase 5: Testing (Día 4-5)**

1. **Backend tests**
   - Test can_wear_item() logic
   - Test manifest hierarchical
   - Test validation

2. **Frontend tests**
   - Test canSelectItem()
   - Test UI rendering
   - Test disabled states

3. **E2E tests**
   - Crear avatar female, seleccionar male items
   - Crear avatar male, verificar restricciones

### **Fase 6: Deploy (Día 5)**

1. **Backup completo**
2. **Migración BD en producción**
3. **Deploy backend**
4. **Deploy frontend**
5. **Monitoreo**

---

## 🧪 Testing

### **Backend Tests**

```python
# tests/services/test_avatar_service.py

@pytest.mark.parametrize("base_gender,item_gender,expected", [
    ("male", "male", True),
    ("male", "female", False),  # Male NO puede usar female
    ("male", "unisex", True),
    ("female", "male", True),  # Female SÍ puede usar male
    ("female", "female", True),
    ("female", "unisex", True),
])
def test_can_wear_item(base_gender, item_gender, expected):
    service = AvatarService(None)
    assert service.can_wear_item(base_gender, item_gender) == expected

async def test_validate_avatar_layers_incompatible(db: AsyncSession):
    service = AvatarService(db)
    
    # Male avatar con female item
    layers = [
        LayerItem(category="base", filename="base/male/body_1.png"),
        LayerItem(category="skirt", filename="clothes/female/skirt_1.png")  # ❌ Incompatible
    ]
    
    is_valid, errors = await service.validate_avatar_layers("male", layers)
    
    assert not is_valid
    assert len(errors) > 0
    assert "no puede usar" in errors[0].lower()
```

### **Frontend Tests**

```typescript
// src/hooks/useGenderCompatibility.test.ts

describe('canSelectItem', () => {
  it('should allow male to select male items', () => {
    expect(canSelectItem('male', 'male')).toBe(true);
  });
  
  it('should NOT allow male to select female items', () => {
    expect(canSelectItem('male', 'female')).toBe(false);
  });
  
  it('should allow female to select male items', () => {
    expect(canSelectItem('female', 'male')).toBe(true);
  });
  
  it('should allow everyone to select unisex items', () => {
    expect(canSelectItem('male', 'unisex')).toBe(true);
    expect(canSelectItem('female', 'unisex')).toBe(true);
  });
});
```

---

## 📚 Referencias

- **PostgreSQL ENUM**: https://www.postgresql.org/docs/current/datatype-enum.html
- **SQLAlchemy Enum**: https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.Enum
- **Pydantic Literal**: https://docs.pydantic.dev/latest/api/types/#pydantic.types.Literal
- **TypeScript Literal Types**: https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#literal-types

---

**Fecha de Última Actualización**: 14 de noviembre de 2025  
**Autor**: Copilot + Equipo Acadify
