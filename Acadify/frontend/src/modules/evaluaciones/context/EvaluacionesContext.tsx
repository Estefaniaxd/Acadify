import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import { 
  ConfiguracionEvaluacion, 
  DashboardEstadisticas,
  EventoAntiTrampa 
} from '../types';
import { evaluacionesService } from '../services/evaluacionesService';

// ================================
// TIPOS PARA EL CONTEXTO
// ================================

interface EvaluacionesState {
  configuracion: ConfiguracionEvaluacion | null;
  dashboard: DashboardEstadisticas | null;
  eventosAntiTrampa: EventoAntiTrampa[];
  loading: boolean;
  error: string | null;
}

type EvaluacionesAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_CONFIGURACION'; payload: ConfiguracionEvaluacion }
  | { type: 'SET_DASHBOARD'; payload: DashboardEstadisticas }
  | { type: 'ADD_EVENTO_ANTI_TRAMPA'; payload: EventoAntiTrampa }
  | { type: 'SET_EVENTOS_ANTI_TRAMPA'; payload: EventoAntiTrampa[] }
  | { type: 'RESET_STATE' };

interface EvaluacionesContextType extends EvaluacionesState {
  cargarConfiguracion: () => Promise<void>;
  actualizarConfiguracion: (config: Partial<ConfiguracionEvaluacion>) => Promise<void>;
  cargarDashboard: () => Promise<void>;
  reportarEventoAntiTrampa: (evento: Omit<EventoAntiTrampa, 'timestamp'>) => void;
  limpiarErrores: () => void;
  resetear: () => void;
}

// ================================
// ESTADO INICIAL Y REDUCER
// ================================

const initialState: EvaluacionesState = {
  configuracion: null,
  dashboard: null,
  eventosAntiTrampa: [],
  loading: false,
  error: null,
};

function evaluacionesReducer(state: EvaluacionesState, action: EvaluacionesAction): EvaluacionesState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    
    case 'SET_CONFIGURACION':
      return { ...state, configuracion: action.payload, loading: false };
    
    case 'SET_DASHBOARD':
      return { ...state, dashboard: action.payload, loading: false };
    
    case 'ADD_EVENTO_ANTI_TRAMPA':
      return { 
        ...state, 
        eventosAntiTrampa: [action.payload, ...state.eventosAntiTrampa].slice(0, 100) // Mantener solo los últimos 100
      };
    
    case 'SET_EVENTOS_ANTI_TRAMPA':
      return { ...state, eventosAntiTrampa: action.payload };
    
    case 'RESET_STATE':
      return initialState;
    
    default:
      return state;
  }
}

// ================================
// CONTEXTO
// ================================

const EvaluacionesContext = createContext<EvaluacionesContextType | undefined>(undefined);

// ================================
// PROVIDER COMPONENT
// ================================

interface EvaluacionesProviderProps {
  children: React.ReactNode;
}

export function EvaluacionesProvider({ children }: EvaluacionesProviderProps) {
  const [state, dispatch] = useReducer(evaluacionesReducer, initialState);

  // ================================
  // FUNCIONES DEL CONTEXTO
  // ================================

  const cargarConfiguracion = useCallback(async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const config = await evaluacionesService.obtenerConfiguracion();
      dispatch({ type: 'SET_CONFIGURACION', payload: config });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Error al cargar configuración';
      dispatch({ type: 'SET_ERROR', payload: errorMsg });
    }
  }, []);

  const actualizarConfiguracion = useCallback(async (config: Partial<ConfiguracionEvaluacion>) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const configActualizada = await evaluacionesService.actualizarConfiguracion(config);
      dispatch({ type: 'SET_CONFIGURACION', payload: configActualizada });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Error al actualizar configuración';
      dispatch({ type: 'SET_ERROR', payload: errorMsg });
      throw error;
    }
  }, []);

  const cargarDashboard = useCallback(async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const dashboard = await evaluacionesService.obtenerDashboardEstadisticas();
      dispatch({ type: 'SET_DASHBOARD', payload: dashboard });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Error al cargar dashboard';
      dispatch({ type: 'SET_ERROR', payload: errorMsg });
    }
  }, []);

  const reportarEventoAntiTrampa = useCallback((evento: Omit<EventoAntiTrampa, 'timestamp'>) => {
    const eventoCompleto: EventoAntiTrampa = {
      ...evento,
      timestamp: new Date().toISOString(),
    };
    
    dispatch({ type: 'ADD_EVENTO_ANTI_TRAMPA', payload: eventoCompleto });
    
    // Opcional: También reportar al servidor si es necesario
    // En un caso real, podrías querer enviar esto al backend
  }, []);

  const limpiarErrores = useCallback(() => {
    dispatch({ type: 'SET_ERROR', payload: null });
  }, []);

  const resetear = useCallback(() => {
    dispatch({ type: 'RESET_STATE' });
  }, []);

  // ================================
  // EFECTOS
  // ================================

  // Cargar configuración al montar el componente
  useEffect(() => {
    cargarConfiguracion();
    cargarDashboard();
  }, [cargarConfiguracion, cargarDashboard]);

  // Auto-refresh del dashboard cada 5 minutos
  useEffect(() => {
    const interval = setInterval(() => {
      cargarDashboard();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, [cargarDashboard]);

  // ================================
  // VALOR DEL CONTEXTO
  // ================================

  const contextValue: EvaluacionesContextType = {
    ...state,
    cargarConfiguracion,
    actualizarConfiguracion,
    cargarDashboard,
    reportarEventoAntiTrampa,
    limpiarErrores,
    resetear,
  };

  return (
    <EvaluacionesContext.Provider value={contextValue}>
      {children}
    </EvaluacionesContext.Provider>
  );
}

// ================================
// HOOK PERSONALIZADO
// ================================

export function useEvaluacionesContext() {
  const context = useContext(EvaluacionesContext);
  
  if (context === undefined) {
    throw new Error('useEvaluacionesContext debe ser usado dentro de un EvaluacionesProvider');
  }
  
  return context;
}

// ================================
// HOC PARA COMPONENTES QUE NECESITAN EL CONTEXTO
// ================================

export function withEvaluacionesContext<P extends object>(
  Component: React.ComponentType<P>
) {
  return function WrappedComponent(props: P) {
    return (
      <EvaluacionesProvider>
        <Component {...props} />
      </EvaluacionesProvider>
    );
  };
}

// ================================
// HOOK PARA DETECTAR EVENTOS ANTI-TRAMPA
// ================================

export function useAntiTrampaDetection(activo: boolean = false) {
  const { reportarEventoAntiTrampa } = useEvaluacionesContext();

  useEffect(() => {
    if (!activo) return;

    let cambiosPestanaCount = 0;
    let tiempoInicioInactividad: number | null = null;

    // Detectar cambio de pestaña/ventana
    const handleVisibilityChange = () => {
      if (document.hidden) {
        cambiosPestanaCount++;
        tiempoInicioInactividad = Date.now();
        
        reportarEventoAntiTrampa({
          tipo_evento: 'CAMBIO_PESTANA',
          descripcion: `Usuario cambió de pestaña o minimizó ventana (intento #${cambiosPestanaCount})`,
          nivel_sospecha: cambiosPestanaCount > 3 ? 'ALTO' : cambiosPestanaCount > 1 ? 'MEDIO' : 'BAJO',
          datos_adicionales: { cambios_totales: cambiosPestanaCount }
        });
      } else {
        if (tiempoInicioInactividad) {
          const tiempoInactivo = Date.now() - tiempoInicioInactividad;
          reportarEventoAntiTrampa({
            tipo_evento: 'RETORNO_PESTANA',
            descripcion: `Usuario regresó a la pestaña después de ${Math.round(tiempoInactivo / 1000)}s`,
            nivel_sospecha: tiempoInactivo > 30000 ? 'MEDIO' : 'BAJO',
            datos_adicionales: { tiempo_inactivo_ms: tiempoInactivo }
          });
          tiempoInicioInactividad = null;
        }
      }
    };

    // Detectar salida de pantalla completa
    const handleFullscreenChange = () => {
      if (!document.fullscreenElement) {
        reportarEventoAntiTrampa({
          tipo_evento: 'SALIDA_PANTALLA_COMPLETA',
          descripcion: 'Usuario salió del modo pantalla completa',
          nivel_sospecha: 'ALTO',
          datos_adicionales: {}
        });
      }
    };

    // Detectar clic derecho
    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault();
      reportarEventoAntiTrampa({
        tipo_evento: 'CLICK_DERECHO',
        descripcion: 'Usuario intentó abrir menú contextual',
        nivel_sospecha: 'BAJO',
        datos_adicionales: { x: e.clientX, y: e.clientY }
      });
    };

    // Detectar atajos de teclado sospechosos
    const handleKeyDown = (e: KeyboardEvent) => {
      const sospechosos = [
        { keys: ['Control', 'c'], desc: 'Copiar' },
        { keys: ['Control', 'v'], desc: 'Pegar' },
        { keys: ['Control', 'a'], desc: 'Seleccionar todo' },
        { keys: ['Control', 'f'], desc: 'Buscar' },
        { keys: ['F12'], desc: 'DevTools' },
        { keys: ['Control', 'Shift', 'I'], desc: 'DevTools' },
        { keys: ['Control', 'U'], desc: 'Ver código fuente' },
        { keys: ['Alt', 'Tab'], desc: 'Cambiar aplicación' },
        { keys: ['Control', 'Tab'], desc: 'Cambiar pestaña' },
      ];

      for (const sospechoso of sospechosos) {
        if (sospechoso.keys.every(key => 
          key === e.key || 
          (key === 'Control' && e.ctrlKey) || 
          (key === 'Shift' && e.shiftKey) ||
          (key === 'Alt' && e.altKey)
        )) {
          e.preventDefault();
          reportarEventoAntiTrampa({
            tipo_evento: 'ATAJO_SOSPECHOSO',
            descripcion: `Usuario intentó usar atajo: ${sospechoso.desc}`,
            nivel_sospecha: sospechoso.desc.includes('DevTools') ? 'ALTO' : 'MEDIO',
            datos_adicionales: { teclas: sospechoso.keys.join('+') }
          });
          break;
        }
      }
    };

    // Detectar cambio de tamaño de ventana (posible split-screen)
    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      const aspectRatio = width / height;
      
      // Si la relación de aspecto es muy ancha (posible split-screen)
      if (aspectRatio > 2.5 || aspectRatio < 0.8) {
        reportarEventoAntiTrampa({
          tipo_evento: 'CAMBIO_TAMANO_VENTANA',
          descripcion: `Cambio de tamaño de ventana sospechoso: ${width}x${height}`,
          nivel_sospecha: 'MEDIO',
          datos_adicionales: { width, height, aspectRatio }
        });
      }
    };

    // Detectar pérdida de foco prolongada
    let focusTimer: NodeJS.Timeout | null = null;
    const handleBlur = () => {
      focusTimer = setTimeout(() => {
        reportarEventoAntiTrampa({
          tipo_evento: 'PERDIDA_FOCO_PROLONGADA',
          descripcion: 'Ventana perdió el foco por más de 10 segundos',
          nivel_sospecha: 'ALTO',
          datos_adicionales: {}
        });
      }, 10000);
    };

    const handleFocus = () => {
      if (focusTimer) {
        clearTimeout(focusTimer);
        focusTimer = null;
      }
    };

    // Registrar event listeners
    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('keydown', handleKeyDown);
    window.addEventListener('resize', handleResize);
    window.addEventListener('blur', handleBlur);
    window.addEventListener('focus', handleFocus);

    // Cleanup
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('blur', handleBlur);
      window.removeEventListener('focus', handleFocus);
      
      if (focusTimer) {
        clearTimeout(focusTimer);
      }
    };
  }, [activo, reportarEventoAntiTrampa]);

  return {
    reportarEventoAntiTrampa,
  };
}