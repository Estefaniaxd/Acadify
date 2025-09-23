# 🧪 Guía Completa de Pruebas - Sistema de Avatares

## ✅ Problemas Resueltos

### 1. **Avatar no se guardaba** ❌ → ✅
- **Problema**: Conflicto entre dos routers de avatar
- **Solución**: Desactivado router conflictivo en `main.py`
- **Fix aplicado**: Solo usar `avatar_service_complete.py`

### 2. **Avatar no aparecía en navegación** ❌ → ✅
- **Problema**: URL relativa vs URL completa
- **Solución**: Backend ahora devuelve URL completa `http://localhost:8000/static/avatars/...`
- **Fix aplicado**: Sistema de eventos para actualización en tiempo real

### 3. **Ojos se superponían mal** ❌ → ✅
- **Problema**: Base siempre tenía ojos, causando duplicación
- **Solución**: Lógica automática de selección de base:
  - 🚫 **Ojos personalizados**: Usa `base_ayes.png` (sin ojos)
  - ✅ **Sin ojos personalizados**: Usa `base.png` (con ojos)

### 4. **Editor no cargaba avatar guardado** ❌ → ✅
- **Problema**: Editor siempre empezaba vacío
- **Solución**: Auto-carga del avatar activo del usuario al abrir editor
- **Fix aplicado**: `loadUserSavedAvatar()` en `useEffect`

## 🔄 Flujo de Prueba Completo

### **Paso 1: Preparación**
```bash
# Terminal 1: Backend
cd /home/esteban/Acadify/backend
python3 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend  
cd /home/esteban/Acadify/frontend
npm run dev
```

### **Paso 2: Crear Avatar**
1. 🌐 **Abrir navegador**: `http://localhost:5173`
2. 🔐 **Hacer login** con tu usuario
3. 📍 **Ir al editor**: `/avatar`
4. 🎨 **Crear avatar**:
   - Seleccionar género (male/female)
   - Agregar pelo, ropa, zapatos, etc.
   - ⚠️ **PROBAR OJOS**: 
     - Sin ojos → Base debe tener ojos
     - Con ojos → Base debe estar sin ojos

### **Paso 3: Guardar Avatar**
1. ✏️ **Poner nombre**: `Mi Avatar Test`
2. 💾 **Hacer clic en "Guardar"**
3. 📊 **Verificar en consola** (F12):
   ```
   ✅ Avatar saved successfully: {...}
   🔍 Nav: Avatar update event received: {...}
   ```

### **Paso 4: Verificar en Navegación**
1. 👀 **Comprobar navegación principal**: Avatar debe aparecer (esquina superior derecha)
2. 📱 **Abrir sidebar derecho**: Avatar debe aparecer con detalles
3. ⚡ **Debe ser en tiempo real** (sin refrescar página)

### **Paso 5: Verificar en Perfil**
1. 📍 **Ir a perfil**: `/perfil` o `/profile`
2. 👤 **Verificar avatar**: Debe aparecer el mismo avatar guardado
3. ⚡ **Debe mostrar en tiempo real**

### **Paso 6: Verificar Persistencia**
1. 🔄 **Volver al editor**: `/avatar`
2. ✅ **Debe cargar automáticamente**: El avatar creado debe aparecer
3. 📝 **Verificar datos**:
   - Nombre correcto
   - Género correcto  
   - Todas las capas aplicadas
   - Preview correcto

## 🎯 Puntos Críticos a Verificar

### **Ojos (Problema Principal)**
- ❌ **MAL**: Ojos duplicados (base + capa de ojos)
- ✅ **BIEN**: 
  - Sin capa de ojos → Base con ojos
  - Con capa de ojos → Base sin ojos

### **Navegación**
- ❌ **MAL**: Robot/avatar por defecto después de guardar
- ✅ **BIEN**: Avatar personalizado inmediatamente visible

### **Persistencia**
- ❌ **MAL**: Editor siempre vacío al abrir
- ✅ **BIEN**: Editor carga el avatar activo automáticamente

## 🐛 Debugging

### **Consola del Navegador (F12)**
```javascript
// Verificar eventos de avatar
window.addEventListener('avatar-updated', (e) => {
  console.log('Avatar updated:', e.detail);
});

// Probar API manualmente
avatarAPI.getMyAvatars().then(console.log);
```

### **Logs del Backend**
```
🎨 Composing avatar with layers: {...}
👁️ Has custom eyes: true/false
🎨 Using base WITHOUT/WITH eyes: base/.../...base.png
✅ Avatar saved successfully: ...
```

### **Verificar Archivos**
```bash
# Ver avatares guardados
ls -la /home/esteban/Acadify/backend/static/avatars/

# Ver logs del backend
tail -f /home/esteban/Acadify/backend/api_debug.log
```

## 📁 Estructura de Assets (Verificar)
```
backend/static/assets/base/
├── male/
│   ├── male_base.png      # CON ojos (para cuando NO hay ojos personalizados)
│   └── male_base_ayes.png # SIN ojos (para cuando SÍ hay ojos personalizados)
└── female/
    ├── female_base.png      # CON ojos
    └── female_base_ayes.png # SIN ojos
```

## ✅ Resultado Esperado

Al final de todas las pruebas:

1. ✅ **Avatar se guarda** correctamente en BD y archivos
2. ✅ **Navegación muestra avatar** inmediatamente después de guardar
3. ✅ **Perfil muestra avatar** correctamente
4. ✅ **Editor carga avatar** al volver a abrirlo
5. ✅ **Ojos no se duplican** (lógica de base automática)
6. ✅ **Sistema funciona en tiempo real** (sin recargas manuales)

---

**¡Todo debería funcionar perfecto ahora! 🎉**