# 🧪 Guía de Pruebas - Sistema de Proctoring

## 🚀 Inicio Rápido

### Paso 1: Acceder a la Página de Pruebas
```
URL: http://localhost:5175/evaluaciones/proctoring-test
```

### Paso 2: Iniciar Monitoreo
1. Clic en botón **"▶️ Iniciar Monitoreo"**
2. Navegador solicitará permisos:
   - ✅ **Permitir acceso a cámara**
   - ✅ **Permitir acceso a micrófono**
3. Esperar a que aparezcan los widgets de cámara y audio

---

## ✅ Checklist de Pruebas

### 📹 Prueba 1: Cámara Básica
- [ ] Widget de cámara visible en esquina inferior derecha
- [ ] Preview de video funcionando
- [ ] Contador "1 rostro detectado" visible
- [ ] Indicador verde de estado activo
- [ ] Botón de minimizar/expandir funciona

**Estado Esperado**: 🟢 Verde con "1 rostro detectado"

---

### 🎤 Prueba 2: Micrófono Básico
- [ ] Widget de audio visible debajo de la cámara
- [ ] Ecualizador de 8 barras moviéndose
- [ ] Porcentaje de nivel de audio actualizado
- [ ] Barra de nivel con color (verde < 40%, naranja 40-70%, rojo > 70%)

**Acción**: Habla cerca del micrófono  
**Estado Esperado**: Barras suben, porcentaje aumenta

---

### 🚨 Prueba 3: Alerta Sin Rostro
**Objetivo**: Probar detección cuando no hay rostro

**Pasos**:
1. Cubrir la cámara con la mano por 3 segundos
2. Observar cambios

**Resultado Esperado**:
- [ ] Widget cambia a color rojo 🔴
- [ ] Texto "Sin rostro detectado"
- [ ] Sonido de alerta (659 Hz)
- [ ] Toast rojo en esquina superior derecha
- [ ] Panel de alertas muestra contador actualizado
- [ ] Nueva alerta en timeline

---

### 👥 Prueba 4: Alerta Múltiples Rostros
**Objetivo**: Probar detección de más de un rostro

**Pasos**:
1. Tener a otra persona junto a ti frente a la cámara
2. Esperar 2 segundos

**Resultado Esperado**:
- [ ] Widget cambia a color naranja 🟠
- [ ] Texto "2 rostros detectados"
- [ ] Sonido de alerta crítica (880 Hz)
- [ ] Toast rojo con mensaje "Múltiples rostros"
- [ ] Contador de alertas críticas +1

---

### 🔊 Prueba 5: Audio Alto
**Objetivo**: Probar detección de audio sospechoso

**Pasos**:
1. Hablar muy fuerte cerca del micrófono
2. Mantener volumen alto por 5 segundos

**Resultado Esperado**:
- [ ] Barra de nivel > 70% (roja)
- [ ] Ecualizador con barras altas
- [ ] Alerta "Audio sospechoso" después de 5 seg
- [ ] Sonido de alerta (659 Hz)

---

### 📸 Prueba 6: Snapshots Automáticos
**Objetivo**: Verificar captura de imágenes

**Pasos**:
1. Esperar 30 segundos con monitoreo activo
2. Scroll hasta sección "Últimos Snapshots"

**Resultado Esperado**:
- [ ] Thumbnail de imagen visible
- [ ] Timestamp mostrado
- [ ] Metadata: ancho, alto, calidad
- [ ] Nuevos snapshots cada 30 segundos

---

### 📊 Prueba 7: Panel de Alertas
**Objetivo**: Verificar sistema de gestión de alertas

**Pasos**:
1. Generar algunas alertas (cubrir cámara varias veces)
2. Clic en botón flotante con número rojo (ej: "5")
3. Observar panel lateral

**Resultado Esperado**:
- [ ] Panel se desliza desde la derecha
- [ ] Contador por severidad actualizado:
  - 🔵 Baja
  - 🟡 Media
  - 🟠 Alta
  - 🔴 Crítica
- [ ] Indicador de riesgo global con color
- [ ] Timeline con últimas 10 alertas
- [ ] Cada alerta muestra: icono, mensaje, timestamp, badge de severidad

---

### 🎵 Prueba 8: Sonidos de Alerta
**Objetivo**: Verificar notificaciones auditivas

**Pasos**:
1. Asegurar que audio del sistema está activo
2. Generar alertas de diferentes severidades
3. Observar botón de campana en panel

**Resultado Esperado**:
- [ ] Alerta baja: 440 Hz (tono medio)
- [ ] Alerta media: 523 Hz (tono medio-alto)
- [ ] Alerta alta: 659 Hz (tono alto)
- [ ] Alerta crítica: 880 Hz (tono muy alto)
- [ ] Botón de campana alterna entre 🔔/🔕

---

### ⚠️ Prueba 9: Alertas Críticas (3+)
**Objetivo**: Verificar sistema de finalizaciónautomática

**Pasos**:
1. Clic en "Agregar Alerta de Prueba" 3 veces
2. Seleccionar severidad "Crítica" cada vez
3. Observar console log

**Resultado Esperado**:
- [ ] Contador de críticas llega a 3
- [ ] Console log: "⚠️ ALERTA CRÍTICA: Se han detectado 3 alertas críticas"
- [ ] En examen real: finalizaría automáticamente

---

### 🌙 Prueba 10: Dark Mode
**Objetivo**: Verificar compatibilidad con tema oscuro

**Pasos**:
1. Activar dark mode en sistema operativo
2. Recargar página
3. Observar todos los componentes

**Resultado Esperado**:
- [ ] Widgets con fondo oscuro
- [ ] Panel lateral con colores oscuros
- [ ] Alertas legibles
- [ ] Botones con hover oscuro
- [ ] Texto con buen contraste

---

### 🧹 Prueba 11: Limpiar Datos
**Objetivo**: Verificar reset del estado

**Pasos**:
1. Generar varias alertas y snapshots
2. Clic en "🗑️ Limpiar Datos"
3. Observar componentes

**Resultado Esperado**:
- [ ] Alertas borradas
- [ ] Snapshots borrados
- [ ] Eventos de audio borrados
- [ ] Contadores en 0
- [ ] Dashboard de métricas reseteado

---

### ⏸️ Prueba 12: Detener Monitoreo
**Objetivo**: Verificar cleanup de recursos

**Pasos**:
1. Con monitoreo activo
2. Clic en "⏸️ Detener Monitoreo"
3. Observar cambios

**Resultado Esperado**:
- [ ] Widgets desaparecen
- [ ] Cámara se apaga (luz LED se apaga)
- [ ] Micrófono se desactiva
- [ ] Botón cambia a "▶️ Iniciar Monitoreo"

---

## 📊 Dashboard de Métricas

**Ubicación**: Parte superior de la página

**Métricas en Tiempo Real**:
- **Monitoreo Activo**: ✅/❌
- **Total de Alertas**: Número total generado
- **Snapshots Capturados**: Número de imágenes
- **Eventos de Audio**: Número de registros

---

## 🐛 Problemas Comunes

### ❌ No se solicitan permisos
**Causa**: Permisos previamente denegados  
**Solución**: 
1. Clic en ícono de candado/cámara en barra de dirección
2. Permitir cámara y micrófono
3. Recargar página

### ❌ Widget de cámara negro
**Causa**: Cámara en uso por otra aplicación  
**Solución**: Cerrar otras apps que usen cámara (Zoom, Teams, etc.)

### ❌ No detecta audio
**Causa**: Micrófono silenciado  
**Solución**: Verificar que micrófono del sistema no esté muteado

### ❌ No aparecen widgets
**Causa**: Error en navegador  
**Solución**: 
1. Abrir DevTools (F12)
2. Revisar Console por errores
3. Verificar que navegador soporta getUserMedia

---

## 🎯 Resultados Esperados Finales

Al completar todas las pruebas, deberías tener:

- ✅ Cámara funcionando con detección de rostros
- ✅ Micrófono capturando y analizando audio
- ✅ Al menos 10 alertas generadas
- ✅ Al menos 2 snapshots capturados
- ✅ Al menos 20 eventos de audio registrados
- ✅ Panel de alertas con timeline completo
- ✅ Todos los sonidos reproducidos
- ✅ Dark mode verificado
- ✅ Cleanup funcionando correctamente

---

## 📸 Screenshots Esperados

### Vista Principal
```
┌─────────────────────────────────────────┐
│  📊 DASHBOARD                           │
│  Monitoreo: ✅ | Alertas: 12            │
│  Snapshots: 3 | Audio: 45               │
├─────────────────────────────────────────┤
│  [⏸️ Detener] [🚨 Agregar] [🗑️ Limpiar] │
├─────────────────────────────────────────┤
│  📹 CÁMARA          🎤 AUDIO            │
│  ┌─────────┐       ┌─────────┐         │
│  │ Preview │       │ ████████ │         │
│  │  Video  │       │ ██████   │         │
│  │ 1 rostro│       │ ████     │ 65%    │
│  └─────────┘       └─────────┘         │
├─────────────────────────────────────────┤
│  📸 ÚLTIMOS SNAPSHOTS                   │
│  [img] [img] [img]                      │
├─────────────────────────────────────────┤
│  🎤 EVENTOS DE AUDIO                    │
│  12:30:45 - Nivel: 65% ████████         │
│  12:30:43 - Nivel: 45% █████            │
└─────────────────────────────────────────┘
```

### Panel de Alertas
```
                    ┌──────────────────────┐
                    │ 📊 ALERTAS           │
                    │ ✕                    │
                    ├──────────────────────┤
                    │ 🔵 Baja      2       │
                    │ 🟡 Media     5       │
                    │ 🟠 Alta      3       │
                    │ 🔴 Crítica   2       │
                    │                      │
                    │ 🎯 RIESGO: ALTO      │
                    ├──────────────────────┤
                    │ ⏱️ RECIENTES         │
                    │                      │
                    │ 🔴 Sin rostro        │
                    │    12:30:45          │
                    │                      │
                    │ 🟠 Audio alto        │
                    │    12:30:40          │
                    ├──────────────────────┤
                    │ 12 alertas activas   │
                    └──────────────────────┘
```

---

## ✨ Tips de Testing

1. **Usa headphones**: Para evitar feedback del audio
2. **Buena iluminación**: Para mejor detección de rostros
3. **Navegador actualizado**: Chrome 90+, Firefox 88+
4. **Console abierto**: Para ver logs de debugging
5. **Network throttling**: Para simular conexión lenta

---

## 📞 Soporte

Si encuentras algún bug o comportamiento inesperado:

1. Captura screenshot
2. Abre DevTools → Console → Copia errores
3. Reporta con:
   - Navegador y versión
   - Sistema operativo
   - Pasos para reproducir
   - Errores de console

---

**¡Listo para probar!** 🚀

Accede a: http://localhost:5175/evaluaciones/proctoring-test
