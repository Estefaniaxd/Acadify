# Sistema de Proctoring - Documentación

## 📋 Descripción General

Sistema completo de monitoreo por cámara y micrófono para evaluaciones en línea, construido con React, TypeScript y Web APIs siguiendo principios SOLID y Clean Code.

## 🏗️ Arquitectura

### Componentes Principales

```
proctoring/
├── ProctoringCamera.tsx     (420 líneas) - Captura y detección de rostros
├── ProctoringAudio.tsx      (380 líneas) - Análisis de audio en tiempo real
├── AlertasProctoring.tsx    (440 líneas) - Sistema de alertas y notificaciones
├── ProctoringTest.tsx       (310 líneas) - Página de pruebas
└── index.ts                 - Exports limpios
```

### Principios Aplicados

#### ✅ SOLID
- **Single Responsibility**: Cada hook maneja una responsabilidad única
- **Open/Closed**: Componentes extensibles mediante props
- **Liskov Substitution**: Interfaces consistentes y predecibles
- **Interface Segregation**: Props específicas por componente
- **Dependency Inversion**: Lógica desacoplada mediante callbacks

#### ✅ Clean Code
- Nombres descriptivos y consistentes
- Funciones pequeñas con propósito único
- Comentarios JSDoc en lógica compleja
- TypeScript strict mode
- Separation of Concerns

## 📦 Componentes

### 1. ProctoringCamera

**Propósito**: Captura de video y detección de rostros

**Props**:
```typescript
interface ProctoringCameraProps {
  configuracion: ConfiguracionProctoring;
  onAlerta: (alerta: AlertaProctoring) => void;
  onSnapshot: (snapshot: SnapshotProctoring) => void;
  activo: boolean;
  className?: string;
}
```

**Custom Hooks**:
- `useMediaStream`: Gestión de MediaStream con cleanup automático
- `useDeteccionRostros`: Detección de rostros (simulada, lista para MediaPipe)
- `useSnapshots`: Captura periódica de frames

**Características**:
- ✅ Video preview en tiempo real (1280x720)
- ✅ Widget minimizable/expandable
- ✅ Detección de rostros cada 2 segundos
- ✅ Snapshots automáticos configurables
- ✅ Alertas por: sin rostro (alta), múltiples rostros (crítica)
- ✅ Estados visuales por color
- ✅ Full dark mode

**Ejemplo de uso**:
```tsx
<ProctoringCamera
  configuracion={configuracion}
  activo={monitoreoActivo}
  onAlerta={(alerta) => {
    console.log('Alerta:', alerta);
    // Reportar al backend
  }}
  onSnapshot={(snapshot) => {
    console.log('Snapshot:', snapshot);
    // Guardar en servidor
  }}
/>
```

### 2. ProctoringAudio

**Propósito**: Captura y análisis de audio en tiempo real

**Props**:
```typescript
interface ProctoringAudioProps {
  configuracion: ConfiguracionProctoring;
  onAlerta: (alerta: AlertaProctoring) => void;
  onEventoAudio: (evento: EventoAudio) => void;
  activo: boolean;
  className?: string;
}
```

**Custom Hooks**:
- `useAudioStream`: Gestión de audio MediaStream
- `useAudioAnalysis`: Análisis RMS con Web Audio API

**Características**:
- ✅ Captura con cancelación de eco
- ✅ Análisis RMS en tiempo real
- ✅ Ecualizador visual de 8 barras
- ✅ Barra de porcentaje con colores
- ✅ Alertas de audio sospechoso (>70%)
- ✅ Widget minimizable
- ✅ Full dark mode

**Detalles Técnicos**:
- FFT Size: 2048 (balance precisión/CPU)
- Throttling: 5 segundos entre alertas similares
- RMS: `√(Σ(sample²) / length)`

**Ejemplo de uso**:
```tsx
<ProctoringAudio
  configuracion={configuracion}
  activo={monitoreoActivo}
  onAlerta={(alerta) => {
    // Manejar alerta de audio alto
  }}
  onEventoAudio={(evento) => {
    // Registrar nivel de audio
  }}
/>
```

### 3. AlertasProctoring

**Propósito**: Sistema completo de gestión de alertas

**Props**:
```typescript
interface AlertasProctoringProps {
  alertas: AlertaProctoring[];
  onResolverAlerta: (id: string) => void;
  onAlertaCritica?: (contadorCriticas: number) => void;
  className?: string;
}
```

**Sub-componentes**:
- `ContadorInfracciones`: Contador por severidad + riesgo global
- `TarjetaAlerta`: Card individual de alerta

**Custom Hook**:
- `useSonidosAlerta`: Genera tonos con AudioContext

**Características**:
- ✅ Panel lateral deslizante
- ✅ Contador por severidad (baja, media, alta, crítica)
- ✅ Indicador de riesgo global con colores
- ✅ Timeline de eventos con timestamps
- ✅ Sonidos diferenciados (440-880 Hz)
- ✅ Sistema de resolución de alertas
- ✅ Callback de alerta crítica (≥3)
- ✅ Full dark mode

**Frecuencias de sonido**:
- Baja: 440 Hz (A)
- Media: 523 Hz (C)
- Alta: 659 Hz (E)
- Crítica: 880 Hz (A octave)

**Ejemplo de uso**:
```tsx
<AlertasProctoring
  alertas={alertasProctoring}
  onResolverAlerta={(id) => {
    setAlertas(prev => 
      prev.map(a => a.id === id ? { ...a, resuelta: true } : a)
    );
  }}
  onAlertaCritica={(count) => {
    if (count >= 3) {
      // Finalizar examen automáticamente
      finalizarExamen();
    }
  }}
/>
```

## 🔧 Integración en TomadorExamen

### Paso 1: Imports

```tsx
import { ProctoringCamera } from '../proctoring/ProctoringCamera';
import { ProctoringAudio } from '../proctoring/ProctoringAudio';
import { AlertasProctoring } from '../proctoring/AlertasProctoring';
import type { 
  ConfiguracionProctoring, 
  AlertaProctoring, 
  SnapshotProctoring,
  EventoAudio 
} from '../../types';
```

### Paso 2: Estados

```tsx
const [alertasProctoring, setAlertasProctoring] = useState<AlertaProctoring[]>([]);
const [snapshotsCapturados, setSnapshotsCapturados] = useState<SnapshotProctoring[]>([]);
const [eventosAudio, setEventosAudio] = useState<EventoAudio[]>([]);
const [monitoreoActivo, setMonitoreoActivo] = useState(false);
```

### Paso 3: Configuración

```tsx
const configuracionProctoring: ConfiguracionProctoring = {
  habilitarCamera: examen.configuracion_avanzada?.proctoring?.camera ?? false,
  habilitarMicrofono: examen.configuracion_avanzada?.proctoring?.audio ?? false,
  deteccionRostros: true,
  deteccionMultiplesRostros: true,
  deteccionAudio: true,
  grabarVideo: false,
  grabarAudio: false,
  frecuenciaSnapshotsSegundos: 30,
  umbralConfianzaRostro: 0.8,
  alertarSinRostro: true,
  alertarMultiplesRostros: true,
  alertarRostroDesconocido: false,
  alertarMultiplesVoces: true,
};
```

### Paso 4: Callbacks

```tsx
const handleAlertaProctoring = useCallback((alerta: AlertaProctoring) => {
  setAlertasProctoring(prev => [...prev, alerta]);
  
  // Mostrar toast según severidad
  if (alerta.severidad === 'critica' || alerta.severidad === 'alta') {
    showToast({
      type: 'error',
      title: 'Alerta de Seguridad',
      message: alerta.mensaje
    });
  }
  
  // TODO: Reportar al backend
  // await evaluacionesService.reportarEventoAntiTrampa(intento.intento_id, {
  //   tipo_evento: alerta.tipo,
  //   detalle: alerta.mensaje,
  //   timestamp: alerta.timestamp
  // });
}, [showToast]);

const handleSnapshotProctoring = useCallback((snapshot: SnapshotProctoring) => {
  setSnapshotsCapturados(prev => [...prev, snapshot].slice(-20));
  
  // TODO: Enviar al backend
  // await evaluacionesService.enviarSnapshot(intento.intento_id, snapshot);
}, []);

const handleEventoAudio = useCallback((evento: EventoAudio) => {
  setEventosAudio(prev => [...prev, evento].slice(-50));
  
  // TODO: Enviar al backend
  // await evaluacionesService.registrarEventoAudio(intento.intento_id, evento);
}, []);

const handleAlertaCritica = useCallback((contadorCriticas: number) => {
  if (contadorCriticas >= 3) {
    showToast({
      type: 'error',
      title: 'Examen Finalizado',
      message: 'Se detectaron múltiples infracciones de seguridad.'
    });
    
    setTimeout(() => {
      manejarFinalizarExamen();
    }, 3000);
  }
}, [showToast]);
```

### Paso 5: Renderizado

```tsx
{estado === 'en_progreso' && monitoreoActivo && (
  <>
    {configuracionProctoring.habilitarCamera && (
      <ProctoringCamera
        configuracion={configuracionProctoring}
        activo={monitoreoActivo}
        onAlerta={handleAlertaProctoring}
        onSnapshot={handleSnapshotProctoring}
      />
    )}
    
    {configuracionProctoring.habilitarMicrofono && (
      <ProctoringAudio
        configuracion={configuracionProctoring}
        activo={monitoreoActivo}
        onAlerta={handleAlertaProctoring}
        onEventoAudio={handleEventoAudio}
      />
    )}
    
    <AlertasProctoring
      alertas={alertasProctoring}
      onResolverAlerta={(id) => {
        setAlertasProctoring(prev => 
          prev.map(a => a.id === id ? { ...a, resuelta: true } : a)
        );
      }}
      onAlertaCritica={handleAlertaCritica}
    />
  </>
)}
```

## 🧪 Testing

### Página de Pruebas

Accede a la página de pruebas en desarrollo:

```
http://localhost:5173/evaluaciones/proctoring-test
```

### Escenarios de Prueba

#### ✅ Test 1: Permisos
1. Abrir página de pruebas
2. Clic en "Iniciar Monitoreo"
3. **Esperado**: Solicitud de permisos de cámara y micrófono
4. **Validar**: Aceptar ambos permisos

#### ✅ Test 2: Cámara
1. Cubrir la cámara con la mano
2. **Esperado**: Alerta "sin_rostro_detectado" (severidad alta) después de 3 segundos
3. **Validar**: Toast rojo + sonido 659 Hz
4. Descubrir cámara
5. **Esperado**: Estado verde "1 rostro detectado"

#### ✅ Test 3: Múltiples Rostros
1. Tener 2+ personas frente a la cámara
2. **Esperado**: Alerta "multiples_rostros" (severidad crítica)
3. **Validar**: Toast rojo + sonido 880 Hz

#### ✅ Test 4: Audio
1. Hablar en voz alta cerca del micrófono
2. **Esperado**: Nivel de audio >70% visible en widget
3. **Validar**: Barra roja + ecualizador activo
4. **Esperado**: Alerta "audio_sospechoso" después de 5 segundos

#### ✅ Test 5: Snapshots
1. Esperar 30 segundos con monitoreo activo
2. **Esperado**: Snapshot capturado visible en "Últimos Snapshots"
3. **Validar**: Imagen thumbnail + metadata (ancho, alto, calidad)

#### ✅ Test 6: Panel de Alertas
1. Clic en botón flotante con número de alertas
2. **Esperado**: Panel lateral se desliza desde la derecha
3. **Validar**: 
   - Contador por severidad actualizado
   - Timeline con últimas 10 alertas
   - Indicador de riesgo con color correcto
   - Footer con estadísticas

#### ✅ Test 7: Alertas Críticas
1. Generar 3+ alertas críticas (ej: múltiples rostros)
2. **Esperado**: Callback `onAlertaCritica` disparado
3. **Validar**: Console log "⚠️ ALERTA CRÍTICA"

#### ✅ Test 8: Dark Mode
1. Toggle dark mode en ajustes del sistema
2. **Esperado**: Todos los componentes adaptan colores
3. **Validar**: 
   - Widgets con fondo oscuro
   - Panel lateral con colores oscuros
   - Alertas legibles en ambos modos

## 🎨 Personalización

### Configuración de Snapshots

```tsx
const configuracion: ConfiguracionProctoring = {
  // ... otras props
  frecuenciaSnapshotsSegundos: 60, // Cambiar a 1 minuto
};
```

### Umbral de Audio

```tsx
// En ProctoringAudio.tsx línea 150
const umbralAudioAlto = 70; // Cambiar a 80 para ser más permisivo
```

### Colores de Alertas

```tsx
// En AlertasProctoring.tsx
const coloresSeveridad = {
  baja: 'bg-blue-50 dark:bg-blue-900/20',     // Cambiar a gris
  media: 'bg-yellow-50 dark:bg-yellow-900/20', // Mantener amarillo
  alta: 'bg-orange-50 dark:bg-orange-900/20',  // Cambiar a naranja oscuro
  critica: 'bg-red-50 dark:bg-red-900/20',     // Mantener rojo
};
```

### Frecuencias de Sonido

```tsx
// En AlertasProctoring.tsx línea 29
const frecuencias = {
  baja: 440,    // A4
  media: 587,   // D5 (cambiar de C5)
  alta: 740,    // F#5 (cambiar de E5)
  critica: 988, // B5 (cambiar de A5)
};
```

## 🔌 APIs Utilizadas

### MediaStream API
```typescript
navigator.mediaDevices.getUserMedia({
  video: { width: 1280, height: 720, facingMode: 'user' },
  audio: { echoCancellation: true, noiseSuppression: true }
});
```

### Web Audio API
```typescript
const audioContext = new AudioContext();
const analyser = audioContext.createAnalyser();
analyser.fftSize = 2048;
analyser.getByteTimeDomainData(dataArray);
```

### Canvas API
```typescript
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
ctx.drawImage(video, 0, 0, width, height);
const imageData = canvas.toDataURL('image/jpeg', 0.7);
```

### Notification API
```typescript
if ('Notification' in window && Notification.permission === 'granted') {
  new Notification(titulo, { body: mensaje, icon: '/logo.png' });
}
```

## 🚀 Próximas Mejoras

### Corto Plazo
- [ ] Integrar MediaPipe para detección real de rostros
- [ ] Endpoints backend para eventos anti-trampa
- [ ] Endpoints backend para snapshots
- [ ] Sistema de reconocimiento facial

### Mediano Plazo
- [ ] Grabación completa de video con WebRTC
- [ ] Análisis de voz para detectar múltiples personas
- [ ] Dashboard de administrador para revisar eventos
- [ ] Reproducción de sesión de examen

### Largo Plazo
- [ ] Machine Learning para detectar comportamientos sospechosos
- [ ] Detección de objetos prohibidos (celulares, libros)
- [ ] Sistema de alertas en tiempo real al profesor
- [ ] Analytics de patrones de trampa

## 📝 Notas Técnicas

### Permisos del Navegador
- **Chrome/Edge**: Requiere HTTPS en producción
- **Firefox**: Permite localhost sin HTTPS
- **Safari**: Requiere permisos explícitos del usuario

### Performance
- **CPU**: ~5-10% en análisis de audio + video
- **Memoria**: ~50-100MB para streams
- **Red**: ~100KB por snapshot (JPEG 70% quality)

### Compatibilidad
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+
- ❌ IE11 (no soportado)

## 🐛 Troubleshooting

### Error: "Permission denied"
**Solución**: Usuario rechazó permisos. Mostrar instrucciones para habilitar en configuración del navegador.

### Error: "NotAllowedError"
**Solución**: Sitio no está en HTTPS. Usar localhost o habilitar HTTPS.

### Error: "No devices found"
**Solución**: No hay cámara/micrófono disponible. Verificar hardware.

### Audio no detecta nivel
**Solución**: Verificar que `echoCancellation: true` no esté bloqueando entrada.

### Snapshots borrosos
**Solución**: Aumentar `calidadSnapshot` de 0.7 a 0.9 (más tamaño).

## 📚 Referencias

- [MediaStream API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_API)
- [Web Audio API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [Canvas API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
- [Notification API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API)
- [MediaPipe Face Detection](https://google.github.io/mediapipe/solutions/face_detection.html)
- [face-api.js](https://github.com/justadudewhohacks/face-api.js/)

---

**Autor**: Sistema de Proctoring - Acadify  
**Versión**: 1.0.0  
**Última actualización**: 8 de noviembre de 2025
