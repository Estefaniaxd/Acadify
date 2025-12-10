/**
 * Tipos centralizados para el sistema de avatares
 * 
 * IMPORTANTE: Los filtros de género son INFORMATIVOS, NO bloquean la selección.
 * Cualquier avatar (male/female) puede usar cualquier item, solo se sugiere el género objetivo.
 */

// ==========================================
// TIPOS BÁSICOS
// ==========================================

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
  | "shirt"
  | "pants"
  | "skirt"
  | "jacket"
  | "socks"
  | "shoes"
  | "dress"
  | "underwear"
  // HAIR
  | "short"
  | "medium"
  | "long"
  | "curly"
  | "straight"
  | "wavy"
  | "ponytail"
  | "braid"
  // ACCESSORIES
  | "glasses"
  | "hat"
  | "earrings"
  | "necklace"
  | "bracelet"
  | "ring"
  | "watch"
  | "headband"
  | "mask"
  // EYES
  | "normal"
  | "anime"
  | "realistic"
  // MAKEUP
  | "lipstick"
  | "eyeshadow"
  | "blush"
  | "eyeliner"
  // BACKGROUNDS
  | "solid"
  | "gradient"
  | "pattern"
  | "scene"
  // GENERAL
  | "other"
  | "none";

// ==========================================
// INTERFACES
// ==========================================

export interface AssetInfo {
  id: string;
  filename: string;
  displayName: string;
  category: CategoryType;
  subcategory?: SubcategoryType;
  targetGender: GenderType; // Solo informativo, NO bloquea uso
  url: string;
  width: number;
  height: number;
  fileSize: number;
  isNormalized: boolean;
  metaInfo: Record<string, any>;
}

export interface LayerItem {
  category: CategoryType;
  filename: string;
  url: string;
}

export interface ManifestResponse {
  resolution: [number, number];
  categories: Record<CategoryType, AssetInfo[]>; // Flat list
  hierarchical?: Record<CategoryType, Record<SubcategoryType, AssetInfo[]>>; // Grouped by subcategory
  totalAssets: number;
  gender?: GenderType;
}

export interface PreviewRequest {
  baseGender: "male" | "female";
  layers: LayerItem[];
}

export interface PreviewResponse {
  previewUrl: string;
  layersHash: string;
  fromCache: boolean;
}

export interface SaveAvatarRequest {
  name: string;
  baseGender: "male" | "female";
  layers: LayerItem[];
  isActive?: boolean;
  isPublic?: boolean;
}

export interface UserAvatarResponse {
  id: string;
  userId: string;
  name: string;
  baseGender: "male" | "female";
  layers: LayerItem[];
  imageUrl: string;
  layersHash: string;
  isActive: boolean;
  isPublic: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface UserAvatarListResponse {
  avatars: UserAvatarResponse[];
  total: number;
  active?: UserAvatarResponse;
}

// ==========================================
// CONFIGURACIÓN UI
// ==========================================

export interface CategoryConfig {
  key: CategoryType;
  label: string;
  icon: any; // Lucide icon component
  color: string; // Tailwind gradient classes
  description: string;
  subcategories?: SubcategoryConfig[];
}

export interface SubcategoryConfig {
  key: SubcategoryType;
  label: string;
  icon?: any;
  count?: number;
}

export interface GenderFilterOption {
  key: GenderType | "all";
  label: string;
  icon: any;
  description: string;
}

// ==========================================
// METADATA Y HELPERS
// ==========================================

/**
 * Metadata de categorías con configuración UI
 */
export const CATEGORY_METADATA: Record<CategoryType, Omit<CategoryConfig, "key">> = {
  base: {
    label: "Base",
    icon: null, // Set in component
    color: "from-gray-500 to-gray-600",
    description: "Cuerpo base del avatar",
  },
  hair: {
    label: "Cabello",
    icon: null,
    color: "from-amber-500 to-orange-500",
    description: "Estilos de cabello",
  },
  eyes: {
    label: "Ojos",
    icon: null,
    color: "from-blue-500 to-indigo-500",
    description: "Color y forma de ojos",
  },
  mouth: {
    label: "Boca",
    icon: null,
    color: "from-pink-500 to-rose-500",
    description: "Expresiones y labios",
  },
  makeup: {
    label: "Maquillaje",
    icon: null,
    color: "from-purple-500 to-violet-500",
    description: "Maquillaje y detalles",
  },
  clothes: {
    label: "Ropa",
    icon: null,
    color: "from-green-500 to-emerald-500",
    description: "Camisas, pantalones, faldas",
  },
  accessories: {
    label: "Accesorios",
    icon: null,
    color: "from-yellow-500 to-amber-500",
    description: "Complementos y joyas",
  },
  backgrounds: {
    label: "Fondos",
    icon: null,
    color: "from-teal-500 to-cyan-500",
    description: "Fondos y escenarios",
  },
};

/**
 * Metadata de subcategorías
 */
export const SUBCATEGORY_LABELS: Record<SubcategoryType, string> = {
  // CLOTHES
  shirt: "Camisas",
  pants: "Pantalones",
  skirt: "Faldas",
  jacket: "Chaquetas",
  socks: "Medias",
  shoes: "Zapatos",
  dress: "Vestidos",
  underwear: "Ropa Interior",
  // HAIR
  short: "Corto",
  medium: "Medio",
  long: "Largo",
  curly: "Rizado",
  straight: "Lacio",
  wavy: "Ondulado",
  ponytail: "Coleta",
  braid: "Trenza",
  // ACCESSORIES
  glasses: "Gafas",
  hat: "Sombreros",
  earrings: "Aretes",
  necklace: "Collares",
  bracelet: "Pulseras",
  ring: "Anillos",
  watch: "Relojes",
  headband: "Diademas",
  mask: "Máscaras",
  // EYES
  normal: "Normal",
  anime: "Anime",
  realistic: "Realista",
  // MAKEUP
  lipstick: "Labial",
  eyeshadow: "Sombra de Ojos",
  blush: "Rubor",
  eyeliner: "Delineador",
  // BACKGROUNDS
  solid: "Sólido",
  gradient: "Degradado",
  pattern: "Patrón",
  scene: "Escena",
  // GENERAL
  other: "Otros",
  none: "Ninguno",
};

/**
 * Iconos de género para badges
 */
export const GENDER_ICONS: Record<GenderType, string> = {
  male: "♂",
  female: "♀",
  unisex: "⚲",
};

/**
 * Colores de género para badges
 */
export const GENDER_COLORS: Record<GenderType, string> = {
  male: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
  female: "bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-300",
  unisex: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300",
};

/**
 * Obtiene el label de una subcategoría
 */
export function getSubcategoryLabel(subcategory: SubcategoryType): string {
  return SUBCATEGORY_LABELS[subcategory] || subcategory;
}

/**
 * Obtiene el ícono de género
 */
export function getGenderIcon(gender: GenderType): string {
  return GENDER_ICONS[gender] || "?";
}

/**
 * Obtiene las clases de color de género
 */
export function getGenderColorClasses(gender: GenderType): string {
  return GENDER_COLORS[gender] || "bg-gray-100 text-gray-700";
}
