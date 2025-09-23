# 📁 Estructura Completa de Assets para Sistema de Avatars

## 🎯 Ubicación Principal
```
backend/static/assets/
```

## 📂 Estructura de Carpetas Completa

### **Assets Base (OBLIGATORIOS)**
```
backend/static/assets/base/
├── male/              # Avatar base masculino
│   └── male_base.png      # (512x512)
├── female/            # Avatar base femenino  
│   └── female_base.png    # (512x512)
└── unisex/            # Bases que pueden usar ambos géneros
    └── ...
```

### **Peinados (Hair)**
```
backend/static/assets/hair/
├── male/              # Peinados específicos masculinos
│   ├── short_black.png
│   ├── buzz_cut.png
│   ├── slicked_back.png
│   └── ...
├── female/            # Peinados específicos femeninos
│   ├── long_blonde.png
│   ├── curly_red.png
│   ├── pixie_cut.png
│   └── ...
└── unisex/            # Peinados que pueden usar ambos géneros
    ├── bald.png
    ├── cap.png
    └── ...
```

### **Camisas y Tops (Shirt)**
```
backend/static/assets/shirt/
├── male/              # Camisas específicas masculinas
│   ├── shirt_formal_white.png
│   ├── shirt_casual_blue.png
│   ├── polo_red.png
│   └── ...
├── female/            # Blusas específicas femeninas
│   ├── blouse_elegant_red.png
│   ├── top_casual_pink.png
│   ├── camisole_black.png
│   └── ...
└── unisex/            # Camisas que pueden usar ambos géneros
    ├── tshirt_basic_white.png
    ├── tshirt_sport_blue.png
    ├── hoodie_casual_gray.png
    └── ...
```

### **Pantalones y Faldas (Pants)**
```
backend/static/assets/pants/
├── male/              # Pantalones específicos masculinos
│   ├── pants_formal_black.png
│   ├── jeans_casual_blue.png
│   ├── shorts_sport_red.png
│   └── ...
├── female/            # Faldas y pantalones específicos femeninos
│   ├── skirt_elegant_black.png
│   ├── pants_office_gray.png
│   ├── shorts_summer_white.png
│   └── ...
└── unisex/            # Pantalones que pueden usar ambos géneros
    ├── jeans_classic_blue.png
    ├── shorts_sport_black.png
    ├── leggings_sport_gray.png
    └── ...
```

### **Zapatos (Shoes)**
```
backend/static/assets/shoes/
├── male/              # Zapatos específicos masculinos
│   ├── shoes_formal_black.png
│   ├── sneakers_sport_white.png
│   ├── boots_winter_brown.png
│   └── ...
├── female/            # Zapatos específicos femeninos
│   ├── heels_elegant_red.png
│   ├── flats_casual_brown.png
│   ├── boots_fashion_black.png
│   └── ...
└── unisex/            # Zapatos que pueden usar ambos géneros
    ├── sneakers_casual_white.png
    ├── boots_winter_brown.png
    ├── sandals_summer_tan.png
    └── ...
```

### **Chaquetas y Abrigos (Jacket)**
```
backend/static/assets/jacket/
├── male/              # Chaquetas específicas masculinas
│   ├── blazer_formal_navy.png
│   ├── jacket_casual_brown.png
│   ├── coat_winter_black.png
│   └── ...
├── female/            # Chaquetas específicas femeninas
│   ├── blazer_office_black.png
│   ├── cardigan_casual_pink.png
│   ├── coat_elegant_red.png
│   └── ...
└── unisex/            # Chaquetas que pueden usar ambos géneros
    ├── hoodie_casual_gray.png
    ├── jacket_winter_blue.png
    ├── windbreaker_sport_green.png
    └── ...
```

### **Ojos (Eyes)**
```
backend/static/assets/eyes/
├── male/              # Ojos específicos masculinos (opcional)
│   ├── eyes_masculine_brown.png
│   └── ...
├── female/            # Ojos específicos femeninos (opcional)
│   ├── eyes_feminine_blue.png
│   └── ...
└── unisex/            # Ojos que pueden usar ambos géneros
    ├── brown_eyes.png
    ├── blue_eyes.png
    ├── green_eyes.png
    ├── hazel_eyes.png
    └── ...
```

### **Bocas (Mouth) - NUEVA**
```
backend/static/assets/mouth/
├── male/              # Bocas específicas masculinas
│   ├── mouth_serious.png
│   ├── mouth_smile_masculine.png
│   └── ...
├── female/            # Bocas específicas femeninas
│   ├── mouth_smile_feminine.png
│   ├── mouth_lipstick_red.png
│   └── ...
└── unisex/            # Bocas que pueden usar ambos géneros
    ├── mouth_neutral.png
    ├── mouth_smile.png
    ├── mouth_surprised.png
    └── ...
```

### **Maquillaje (Makeup) - NUEVA**
```
backend/static/assets/makeup/
├── male/              # Maquillaje específico masculino
│   ├── beard_full.png
│   ├── mustache.png
│   ├── eyebrows_thick.png
│   └── ...
├── female/            # Maquillaje específico femenino
│   ├── eyeliner_black.png
│   ├── eyeshadow_blue.png
│   ├── blush_pink.png
│   ├── foundation_light.png
│   └── ...
└── unisex/            # Maquillaje que pueden usar ambos géneros
    ├── eyebrows_natural.png
    ├── freckles.png
    └── ...
```

### **Accesorios (Accessories)**
```
backend/static/assets/accessories/
├── male/              # Accesorios específicos masculinos
│   ├── watch_formal.png
│   ├── tie_business.png
│   ├── hat_fedora.png
│   └── ...
├── female/            # Accesorios específicos femeninos
│   ├── earrings_gold.png
│   ├── necklace_pearl.png
│   ├── bracelet_silver.png
│   └── ...
└── unisex/            # Accesorios que pueden usar ambos géneros
    ├── glasses_black.png
    ├── hat_cap.png
    ├── necklace_silver.png
    ├── backpack_casual.png
    └── ...
```

### **Fondos (Backgrounds)**
```
backend/static/assets/backgrounds/
├── male/              # Fondos con temas masculinos (opcional)
│   └── ...
├── female/            # Fondos con temas femeninos (opcional)
│   └── ...
└── unisex/            # Fondos para todos
    ├── simple_white.png
    ├── gradient_blue.png
    ├── office_background.png
    ├── outdoor_park.png
    └── ...
```

## 🎨 Especificaciones Técnicas

### **Formato de Imágenes**
- **Formato:** PNG con transparencia (RGBA)
- **Resolución:** 512x512 píxeles (obligatorio)
- **Tamaño máximo:** 1.5MB por archivo
- **Fondo:** Transparente (para capas que no sean background)

### **Convenciones de Nombres**
- **Sin espacios:** Usar guiones bajos `_`
- **Descriptivo:** `hair_long_blonde.png`, `clothes_dress_red.png`
- **Género en carpeta:** No en nombre de archivo (la carpeta ya indica el género)

## 🔧 Configuración en Base de Datos

Cada imagen se registra automáticamente con:
- **category:** base, hair, clothes, eyes, accessories, backgrounds
- **target_gender:** male, female, unisex (según la carpeta)
- **filename:** ruta relativa desde assets/ (ej: `hair/male/short_black.png`)

## 🚀 Funcionamiento del Sistema

### **Composición de Capas (orden de superposición):**
1. **Backgrounds** (fondo)
2. **Base** (forma del avatar - male_base.png o female_base.png)
3. **Makeup** (maquillaje base, foundation)
4. **Shirt** (camisas, blusas, tops)
5. **Pants** (pantalones, faldas)
6. **Shoes** (zapatos, botas, deportivos)
7. **Hair** (cabello)
8. **Eyes** (ojos)
9. **Mouth** (bocas, labios)
10. **Jacket** (chaquetas, abrigos - encima de camisas)
11. **Accessories** (accesorios al frente)

### **Lógica de Filtrado:**
- **Base:** Siempre específico del género seleccionado
- **Otras categorías:** Muestra específicas del género + unisex
- **Ejemplo:** Usuario masculino ve:
  - shirt/male/* + shirt/unisex/*
  - pants/male/* + pants/unisex/*
  - shoes/male/* + shoes/unisex/*
  - jacket/male/* + jacket/unisex/*
  - makeup/male/* + makeup/unisex/*
  - mouth/male/* + mouth/unisex/*
  - etc.

## 📋 Lista de Verificación para Agregar Imágenes

### ✅ Antes de Agregar:
- [ ] Imagen en formato PNG con transparencia
- [ ] Resolución exacta de 512x512 píxeles
- [ ] Fondo transparente (excepto backgrounds)
- [ ] Tamaño menor a 1.5MB

### ✅ Al Agregar:
- [ ] Colocar en la carpeta correcta según género
- [ ] Nombre descriptivo sin espacios
- [ ] Verificar que se superpone correctamente con bases

### ✅ Después de Agregar:
- [ ] Ejecutar migración de base de datos si es necesario
- [ ] Reiniciar el backend para cargar nuevos assets
- [ ] Probar en el editor de avatars

## 🎯 Ejemplos de Uso

### **Usuario Masculino:**
```json
{
  "base_gender": "male",
  "layers": [
    {"category": "base", "file": "base/male/male_base.png"},
    {"category": "makeup", "file": "makeup/male/beard_full.png"},
    {"category": "hair", "file": "hair/male/short_black.png"},
    {"category": "shirt", "file": "shirt/unisex/tshirt_blue.png"},
    {"category": "pants", "file": "pants/male/jeans_casual_blue.png"},
    {"category": "shoes", "file": "shoes/unisex/sneakers_white.png"},
    {"category": "eyes", "file": "eyes/unisex/brown_eyes.png"},
    {"category": "mouth", "file": "mouth/unisex/mouth_smile.png"},
    {"category": "accessories", "file": "accessories/unisex/glasses_black.png"}
  ]
}
```

### **Usuario Femenino:**
```json
{
  "base_gender": "female",
  "layers": [
    {"category": "base", "file": "base/female/female_base.png"},
    {"category": "makeup", "file": "makeup/female/foundation_light.png"},
    {"category": "hair", "file": "hair/female/long_blonde.png"},
    {"category": "shirt", "file": "shirt/female/blouse_elegant_red.png"},
    {"category": "pants", "file": "pants/female/skirt_elegant_black.png"},
    {"category": "shoes", "file": "shoes/female/heels_elegant_red.png"},
    {"category": "eyes", "file": "eyes/unisex/blue_eyes.png"},
    {"category": "mouth", "file": "mouth/female/mouth_lipstick_red.png"},
    {"category": "accessories", "file": "accessories/female/earrings_gold.png"}
  ]
}
```

---

**¡Listo para agregar tus imágenes!** Solo colócalas en las carpetas correspondientes y el sistema las detectará automáticamente.