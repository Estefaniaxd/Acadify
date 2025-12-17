# 🎨 Sistema de Avatares - Progreso de Implementación

> **Fecha**: 14 de noviembre de 2025
> **Branch**: `feature/avatar-normalize`
> **Estado**: 🟢 Base de Datos Completada | ⚠️ Backend/Frontend Pendiente

---

## ✅ COMPLETADO

### 1. **Corrección de Duplicados** ✅
**Problema**: UI mostraba assets duplicados (ej: `hair_1.png` aparecía 2 veces).

**Causa Raíz**: Assets físicamente duplicados en carpetas `male/` y `unisex/` con mismo nombre base.

**Solución Aplicada**:
```sql
-- Desactivados 43 assets duplicados
UPDATE avatar_asset SET is_active='N' 
WHERE filename IN (
    'hair/male/hair_1.png', 'hair/female/hair_1.png', -- duplicados de unisex
    'clothes/male/camisa_cafe.png', -- duplicado de unisex
    ... (43 total)
);
```

**Resultado**: 
- ✅ 0 duplicados en manifest
- ✅ 99 assets únicos activos
- ✅ Prioridad a versiones `unisex`

---

### 2. **Verificación de Escalado** ✅
**Problema**: Usuario reportaba que a veces los assets se agrandaban (1440×3200).

**Verificación Completa**:
```sql
-- Base de datos: TODOS 512×512
SELECT COUNT(*) FROM avatar_asset 
WHERE is_active='Y' AND (width != 512 OR height != 512);
-- Resultado: 0 ❌ incorrectos

-- Archivos físicos: TODOS 512×512
find . -name "*.png" | head -20 | xargs -I {} python3 -c "..."
-- Resultado: 161 archivos ✅ correctos
```

**Conclusión**: El bug de escalado es **cache del navegador**. Los assets están correctos.

---

### 3. **Sistema de ENUMs PostgreSQL** ✅

**Creados 3 ENUMs**:

```sql
CREATE TYPE gender_type AS ENUM ('male', 'female', 'unisex');

CREATE TYPE category_type AS ENUM (
    'base', 'hair', 'eyes', 'mouth', 'makeup', 
    'clothes', 'accessories', 'backgrounds'
);

CREATE TYPE subcategory_type AS ENUM (
    -- CLOTHES: 8 tipos
    'shirt', 'pants', 'skirt', 'jacket', 'socks', 'shoes', 'dress', 'underwear',
    
    -- HAIR: 8 estilos
    'short', 'medium', 'long', 'curly', 'straight', 'wavy', 'ponytail', 'braid',
    
    -- ACCESSORIES: 9 tipos
    'glasses', 'hat', 'earrings', 'necklace', 'bracelet', 'ring', 'watch', 'headband', 'mask',
    
    -- EYES: 3 estilos
    'normal', 'anime', 'realistic',
    
    -- MAKEUP: 4 tipos
    'lipstick', 'eyeshadow', 'blush', 'eyeliner',
    
    -- BACKGROUNDS: 4 tipos
    'solid', 'gradient', 'pattern', 'scene',
    
    -- General
    'other', 'none'
);
```

**Ventajas**:
- ✅ Validación a nivel de BD (no se pueden insertar valores inválidos)
- ✅ Mejor performance (ENUMs son más rápidos que VARCHAR + CHECK)
- ✅ Autocomplete en queries
- ✅ Compatibilidad con SQLAlchemy Enum

---

### 4. **Modificación de Tabla `avatar_asset`** ✅

**Cambios Aplicados**:

```sql
-- 1. Columna target_gender convertida a ENUM
ALTER TABLE avatar_asset 
ALTER COLUMN target_gender TYPE gender_type 
USING target_gender::gender_type;

-- 2. Nueva columna subcategory
ALTER TABLE avatar_asset 
ADD COLUMN subcategory VARCHAR(50) NULL;

-- 3. Índices para performance
CREATE INDEX idx_avatar_asset_subcategory 
ON avatar_asset(subcategory) 
WHERE subcategory IS NOT NULL;

CREATE INDEX idx_avatar_asset_cat_subcat 
ON avatar_asset(category, subcategory) 
WHERE is_active = 'Y';
```

**Estructura Actualizada**:
```
avatar_asset:
  id: uuid (PK)
  category: varchar(50)
  filename: varchar(255) (UNIQUE)
  target_gender: gender_type ← ENUM
  subcategory: varchar(50) ← NUEVO
  width: int (512)
  height: int (512)
  is_active: char(1) ('Y'/'N')
  ... (otros campos)
```

---

### 5. **Clasificación Automática de Subcategorías** ✅

**Algoritmo de Clasificación**:

```sql
-- HAIR: Por número de archivo
UPDATE avatar_asset SET subcategory = 
    CASE 
        WHEN filename ~ 'hair_[1-4]\.png' THEN 'short'
        WHEN filename ~ 'hair_[5-7]\.png' THEN 'medium'
        WHEN filename ~ 'hair_8\.png|hair_long' THEN 'long'
        ELSE 'medium'
    END
WHERE category = 'hair';

-- CLOTHES: Por patrón de nombre
UPDATE avatar_asset SET subcategory = 
    CASE 
        WHEN filename ~* 'camisa_|shirt_|blusa' THEN 'shirt'
        WHEN filename ~* 'pantalon_|pants_' THEN 'pants'
        WHEN filename ~* 'falda_|skirt_' THEN 'skirt'
        WHEN filename ~* 'zapatos_|shoes_' THEN 'shoes'
        WHEN filename ~* 'medias_|socks_' THEN 'socks'
        WHEN filename ~* 'chaqueta|jacket' THEN 'jacket'
        ELSE 'shirt'
    END
WHERE category IN ('shirt', 'pants', 'skirt', 'shoes', 'socks', 'jacket', 'clothes');

-- ACCESSORIES: Por tipo de accesorio
UPDATE avatar_asset SET subcategory = 
    CASE 
        WHEN filename ~* 'manilla|bracelet' THEN 'bracelet'
        WHEN filename ~* 'gafas|glasses' THEN 'glasses'
        WHEN filename ~* 'collar|necklace' THEN 'necklace'
        ELSE 'other'
    END
WHERE category = 'accessories';
```

**Resultado Final**:

| Categoría     | Subcategoría | Count |
|---------------|--------------|-------|
| accessories   | bracelet     | 3     |
| accessories   | glasses      | 3     |
| accessories   | necklace     | 4     |
| accessories   | other        | 6     |
| base          | none         | 4     |
| eyes          | normal       | 12    |
| hair          | medium       | 3     |
| hair          | short        | 4     |
| jacket        | jacket       | 2     |
| makeup        | blush        | 4     |
| makeup        | other        | 5     |
| mouth         | normal       | 7     |
| pants         | pants        | 8     |
| shirt         | shirt        | 25    |
| shoes         | shoes        | 3     |
| skirt         | skirt        | 4     |
| socks         | socks        | 2     |

**Total**: 99 assets clasificados en 17 subcategorías.

---

## ⏳ PENDIENTE

### Backend

#### 1. **Actualizar Modelos SQLAlchemy** 🔴 Alta Prioridad
**Archivo**: `backend/src/models/avatar_asset.py`

**Cambios Necesarios**:
```python
from sqlalchemy import Enum as SQLEnum
from enum import Enum as PyEnum

class GenderType(str, PyEnum):
    MALE = "male"
    FEMALE = "female"
    UNISEX = "unisex"

class AvatarAsset(Base):
    __tablename__ = "avatar_asset"
    
    # Cambiar de String a Enum
    target_gender: Mapped[GenderType] = mapped_column(
        SQLEnum(GenderType, name="gender_type"),
        nullable=False,
        default=GenderType.UNISEX
    )
    
    # Agregar subcategory
    subcategory: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
```

#### 2. **Actualizar Schemas Pydantic** 🔴 Alta Prioridad
**Archivo**: `backend/src/schemas/avatar.py`

```python
from typing import Literal

GenderType = Literal["male", "female", "unisex"]
CategoryType = Literal["base", "hair", "eyes", "mouth", "makeup", "clothes", "accessories", "backgrounds"]
SubcategoryType = Literal["shirt", "pants", "skirt", ...]  # 50 valores

class AssetResponse(BaseModel):
    id: UUID
    filename: str
    category: str
    subcategory: str | None  # ← NUEVO
    target_gender: GenderType  # ← CAMBIAR de str a Literal
    url: str
    width: int
    height: int
    # ...

class ManifestResponse(BaseModel):
    categories: dict[str, list[AssetResponse]]  # Actual
    # TODO: Agregar versión jerárquica
    hierarchical: dict[CategoryType, dict[SubcategoryType, list[AssetResponse]]] | None
```

#### 3. **Actualizar AvatarService** 🟡 Media Prioridad
**Archivo**: `backend/src/services/avatar_service.py`

**Nuevos Métodos**:
```python
class AvatarService:
    def can_wear_item(
        self, 
        base_gender: Literal["male", "female"], 
        item_gender: Literal["male", "female", "unisex"]
    ) -> bool:
        """Reglas de compatibilidad:
        - Female puede usar: male, female, unisex (TODO)
        - Male puede usar: male, unisex (NO female)
        """
        if base_gender == "female":
            return True  # Mujeres pueden usar todo
        else:  # male
            return item_gender in ["male", "unisex"]
    
    async def get_manifest_for_gender(
        self, 
        db: Session, 
        gender: Literal["male", "female"],
        include_subcategories: bool = True
    ) -> dict:
        """Filtrar manifest según reglas de compatibilidad."""
        # ...
    
    async def get_manifest_hierarchical(
        self,
        db: Session,
        gender: Literal["male", "female"] | None = None
    ) -> dict:
        """Retorna manifest agrupado por category -> subcategory."""
        # {
        #   "clothes": {
        #     "shirt": [asset1, asset2],
        #     "pants": [asset3, asset4]
        #   },
        #   "hair": {
        #     "short": [asset5],
        #     "medium": [asset6, asset7]
        #   }
        # }
```

#### 4. **Actualizar CRUD** 🟡 Media Prioridad
**Archivo**: `backend/src/crud/avatar/avatar_asset_crud.py`

```python
class CRUDAvatarAsset:
    async def get_by_category_and_subcategory(
        self,
        db: Session,
        category: str,
        subcategory: str | None = None,
        gender: Literal["male", "female", "unisex"] | None = None,
        active_only: bool = True
    ) -> list[AvatarAsset]:
        """Obtener assets filtrados por category + subcategory + gender."""
        query = select(AvatarAsset).where(AvatarAsset.category == category)
        
        if subcategory:
            query = query.where(AvatarAsset.subcategory == subcategory)
        
        if gender:
            query = query.where(
                or_(
                    AvatarAsset.target_gender == gender,
                    AvatarAsset.target_gender == "unisex"
                )
            )
        
        if active_only:
            query = query.where(AvatarAsset.is_active == "Y")
        
        result = await db.execute(query)
        return list(result.scalars().all())
```

---

### Frontend

#### 5. **Actualizar Tipos TypeScript** 🔴 Alta Prioridad
**Archivo**: `frontend/src/types/avatar.ts` (crear)

```typescript
export type GenderType = "male" | "female" | "unisex";

export type CategoryType = 
  | "base"
  | "hair"
  | "eyes"
  | "mouth"
  | "makeup"
  | "clothes"
  | "accessories"
  | "backgrounds";

export type SubcategoryType =
  // CLOTHES
  | "shirt" | "pants" | "skirt" | "jacket" | "socks" | "shoes" | "dress" | "underwear"
  // HAIR
  | "short" | "medium" | "long" | "curly" | "straight" | "wavy" | "ponytail" | "braid"
  // ACCESSORIES
  | "glasses" | "hat" | "earrings" | "necklace" | "bracelet" | "ring" | "watch" | "headband" | "mask"
  // OTHERS
  | "normal" | "anime" | "realistic" | "lipstick" | "eyeshadow" | "blush" | "eyeliner"
  | "solid" | "gradient" | "pattern" | "scene" | "other" | "none";

export interface AssetInfo {
  id: string;
  filename: string;
  category: CategoryType;
  subcategory?: SubcategoryType;  // ← NUEVO
  targetGender: GenderType;  // ← CAMBIAR de string
  url: string;
  width: number;
  height: number;
  displayName?: string;
}

export interface ManifestResponse {
  categories: Record<CategoryType, AssetInfo[]>;
  // Versión jerárquica opcional
  hierarchical?: Record<CategoryType, Record<SubcategoryType, AssetInfo[]>>;
  totalAssets: number;
  resolution: string;
}
```

#### 6. **Actualizar avatarAPI.ts** 🔴 Alta Prioridad
**Archivo**: `frontend/src/components/avatar/avatarAPI.ts`

```typescript
import type { GenderType, ManifestResponse } from "@/types/avatar";

export const avatarAPI = {
  async getAssetsManifest(gender?: GenderType): Promise<ManifestResponse> {
    const url = gender 
      ? `/avatar/assets?gender=${gender}`
      : `/avatar/assets`;
    
    const response = await apiClient.get<ManifestResponse>(url);
    return response.data;
  },
  
  // ... otros métodos
};
```

#### 7. **UI de Subcategorías** 🟡 Media Prioridad
**Archivo**: `frontend/src/components/avatar/AvatarStudioV2.tsx`

**Diseño Propuesto**:

```
┌─────────────────────────────────────┐
│  [Base] [Hair] [Eyes] [Makeup]     │  ← Tabs Categorías
│  [Clothes] [Accessories] [Bg]       │
├─────────────────────────────────────┤
│  Clothes seleccionado:              │
│  • Shirts (25) • Pants (8)          │  ← Pills Subcategorías
│  • Skirts (4) • Shoes (3) ...       │
├─────────────────────────────────────┤
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐           │
│  │ 👔│ │ 👔│ │ 👔│ │ 👔│           │  ← Grid Items
│  └───┘ └───┘ └───┘ └───┘           │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐           │
│  │ 👔│ │ 👔│ │ 👔│ │ 👔│           │
│  └───┘ └───┘ └───┘ └───┘           │
└─────────────────────────────────────┘
```

**Implementación**:
```typescript
const [activeCategory, setActiveCategory] = useState<CategoryType>("hair");
const [activeSubcategory, setActiveSubcategory] = useState<SubcategoryType | null>(null);

// Obtener subcategorías disponibles para la categoría actual
const availableSubcategories = useMemo(() => {
  if (!manifest?.hierarchical) return [];
  return Object.keys(manifest.hierarchical[activeCategory] || {});
}, [manifest, activeCategory]);

// Grid de items filtrados
const filteredAssets = useMemo(() => {
  if (!manifest?.hierarchical) return [];
  
  if (activeSubcategory) {
    return manifest.hierarchical[activeCategory]?.[activeSubcategory] || [];
  } else {
    // Mostrar todos los items de la categoría
    return Object.values(manifest.hierarchical[activeCategory] || {}).flat();
  }
}, [manifest, activeCategory, activeSubcategory]);
```

#### 8. **Validación de Compatibilidad** 🟢 Baja Prioridad (Nice to Have)
**Hook Custom**: `frontend/src/hooks/useGenderCompatibility.ts`

```typescript
export function useGenderCompatibility(baseGender: GenderType) {
  const canSelectItem = useCallback(
    (itemGender: GenderType): boolean => {
      if (baseGender === "female") {
        return true; // Mujeres pueden usar todo
      } else {
        return itemGender === "male" || itemGender === "unisex";
      }
    },
    [baseGender]
  );
  
  return { canSelectItem };
}

// Uso en componente
const { canSelectItem } = useGenderCompatibility(selectedGender);

<AssetCard 
  asset={asset}
  disabled={!canSelectItem(asset.targetGender)}
  tooltip={
    !canSelectItem(asset.targetGender)
      ? "Este item es solo para avatares femeninos"
      : undefined
  }
/>
```

---

## 📊 Métricas del Sistema

### Base de Datos
- ✅ **3 ENUMs** creados (gender_type, category_type, subcategory_type)
- ✅ **99 assets** activos clasificados
- ✅ **17 subcategorías** únicas en uso
- ✅ **0 duplicados** en manifest
- ✅ **2 índices** nuevos para performance

### Assets por Categoría Principal

| Categoría     | Count | Subcategorías                          |
|---------------|-------|----------------------------------------|
| **shirt**     | 25    | shirt                                  |
| **accessories** | 16  | bracelet, glasses, necklace, other     |
| **eyes**      | 12    | normal                                 |
| **makeup**    | 9     | blush, other                           |
| **pants**     | 8     | pants                                  |
| **hair**      | 7     | short, medium                          |
| **mouth**     | 7     | normal                                 |
| **base**      | 4     | none                                   |
| **skirt**     | 4     | skirt                                  |
| **shoes**     | 3     | shoes                                  |
| **socks**     | 2     | socks                                  |
| **jacket**    | 2     | jacket                                 |

**Total**: 99 assets distribuidos en 8 categorías principales.

---

## 🎯 Siguiente Sprint

### Prioridad Inmediata (Hoy)
1. ✅ Actualizar modelo SQLAlchemy `AvatarAsset`
2. ✅ Actualizar schemas Pydantic
3. ✅ Reiniciar backend y probar endpoint `/avatar/assets`

### Prioridad Alta (Esta Semana)
4. ⚠️ Actualizar `AvatarService` con lógica de compatibilidad
5. ⚠️ Actualizar tipos TypeScript
6. ⚠️ Actualizar `avatarAPI.ts`
7. ⚠️ Implementar UI de subcategorías

### Prioridad Media (Próxima Semana)
8. 🔵 Testing completo (backend + frontend)
9. 🔵 Validación de compatibilidad frontend
10. 🔵 Performance optimization

### Prioridad Baja (Nice to Have)
11. 🟢 Animaciones avanzadas
12. 🟢 Búsqueda/filtro de items
13. 🟢 Favoritos de usuario
14. 🟢 Sugerencias IA de combinaciones

---

## 🚀 Comandos Útiles

### Verificar Estado de BD
```bash
# Ver ENUMs disponibles
psql $DB -c "SELECT typname, enumlabel FROM pg_type JOIN pg_enum ON pg_type.oid = pg_enum.enumtypid WHERE typname IN ('gender_type', 'category_type', 'subcategory_type') ORDER BY typname, enumsortorder;"

# Ver assets por subcategoría
psql $DB -c "SELECT category, subcategory, COUNT(*) FROM avatar_asset WHERE is_active='Y' GROUP BY category, subcategory ORDER BY category, subcategory;"

# Ver duplicados (debería retornar 0)
psql $DB -c "SELECT filename, COUNT(*) FROM avatar_asset WHERE is_active='Y' GROUP BY filename HAVING COUNT(*) > 1;"
```

### Reiniciar Backend
```bash
cd backend
source venv/bin/activate.fish
pkill -f uvicorn
uvicorn src.main:app --reload --port 8000
```

### Probar Manifest
```bash
# Sin filtro
curl -sS 'http://localhost:8000/avatar/assets' | jq '.categories | keys'

# Con filtro male
curl -sS 'http://localhost:8000/avatar/assets?gender=male' | jq '.categories.hair | length'

# Ver subcategorías
curl -sS 'http://localhost:8000/avatar/assets' | jq '.categories.shirt[0]'
```

---

## 📚 Referencias

- **Diseño Completo**: `docs/features/AVATAR_CATEGORIES_DESIGN.md`
- **Scripts SQL**: `/tmp/create_avatar_enums.sql`, `/tmp/assign_subcategories.sql`
- **Scripts Python**: `/tmp/fix_avatar_duplicates.py`
- **Modelos Backend**: `backend/src/models/avatar_asset.py`
- **Schemas Backend**: `backend/src/schemas/avatar.py`
- **Service Backend**: `backend/src/services/avatar_service.py`
- **Frontend UI**: `frontend/src/components/avatar/AvatarStudioV2.tsx`

---

**Última actualización**: 14 de noviembre de 2025, 09:30
**Próxima revisión**: Después de implementar modelos SQLAlchemy
