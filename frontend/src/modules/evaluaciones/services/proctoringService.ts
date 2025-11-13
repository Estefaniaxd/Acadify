/**
 * Servicio de Proctoring API
 * 
 * Cliente HTTP para comunicación con endpoints de proctoring del backend.
 * Maneja registro de eventos, snapshots y obtención de resúmenes.
 * 
 * Características:
 * - Type-safe con TypeScript
 * - Manejo de errores robusto
 * - Retry logic para fallos de red
 * - Queue para requests offline
 * 
 * @module ProctoringService
 */

import type { 
  AlertaProctoring, 
  SnapshotProctoring, 
  EventoAudio,
  TipoEvento 
} from '../types';

/**
 * Configuración del servicio
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const PROCTORING_ENDPOINT = `${API_BASE_URL}/api/v1/evaluaciones/proctoring`;

/**
 * Response de evento registrado
 */
export interface EventoProctoringResponse {
  evento_id: string;
  intento_id: string;
  tipo_evento: string;
  severidad: string;
  detalle: string;
  timestamp: string;
  resuelta: boolean;
  datos_adicionales?: Record<string, unknown>;
}

/**
 * Response de snapshot
 */
export interface SnapshotResponse {
  snapshot_url: string;
  mensaje: string;
  intento_id: string;
  timestamp: string;
}

/**
 * Response de evento de audio
 */
export interface EventoAudioResponse {
  mensaje: string;
  intento_id: string;
  nivel_audio: number;
  es_sospechoso: boolean;
  timestamp: string;
}

/**
 * Resumen de sesión de proctoring
 */
export interface ResumenProctoring {
  intento_id: string;
  total_eventos: number;
  eventos_por_severidad: Record<string, number>;
  eventos_por_tipo: Record<string, number>;
  nivel_riesgo: 'bajo' | 'medio' | 'alto' | 'critico';
  duracion_minutos: number;
  total_snapshots: number;
  total_eventos_audio: number;
  promedio_nivel_audio: number;
  infracciones_criticas: EventoProctoringResponse[];
  ultimo_snapshot: string | null;
  recomendacion: string;
}

/**
 * Error del servicio de proctoring
 */
export class ProctoringServiceError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: unknown
  ) {
    super(message);
    this.name = 'ProctoringServiceError';
  }
}

/**
 * Servicio de Proctoring
 * 
 * Singleton que gestiona la comunicación con el backend de proctoring.
 * 
 * @example
 * ```typescript
 * const service = ProctoringService.getInstance();
 * 
 * // Registrar evento
 * await service.registrarEvento(intentoId, alerta);
 * 
 * // Subir snapshot
 * await service.subirSnapshot(intentoId, snapshot);
 * 
 * // Obtener resumen
 * const resumen = await service.obtenerResumen(intentoId);
 * ```
 */
class ProctoringService {
  private static instance: ProctoringService;
  private token: string | null = null;
  private requestQueue: Array<() => Promise<void>> = [];
  private isProcessingQueue = false;

  /**
   * Constructor privado (Singleton)
   */
  private constructor() {}

  /**
   * Obtiene la instancia única del servicio
   */
  public static getInstance(): ProctoringService {
    if (!ProctoringService.instance) {
      ProctoringService.instance = new ProctoringService();
    }
    return ProctoringService.instance;
  }

  /**
   * Establece el token de autenticación
   */
  public setToken(token: string): void {
    this.token = token;
  }

  /**
   * Obtiene headers por defecto
   */
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  /**
   * Maneja errores de fetch
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ProctoringServiceError(
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData
      );
    }

    return response.json();
  }

  /**
   * Ejecuta request con retry logic
   */
  private async fetchWithRetry<T>(
    url: string,
    options: RequestInit,
    retries: number = 3
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(url, options);
        return await this.handleResponse<T>(response);
      } catch (error) {
        lastError = error as Error;
        
        // Si es error de autenticación, no reintentar
        if (error instanceof ProctoringServiceError && error.statusCode === 401) {
          throw error;
        }

        // Esperar antes de reintentar (exponential backoff)
        if (i < retries - 1) {
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
        }
      }
    }

    throw lastError || new Error('Request failed after retries');
  }

  /**
   * Registra un evento de proctoring
   * 
   * @param intentoId - ID del intento de examen
   * @param alerta - Alerta generada
   * @returns Promise con la respuesta del servidor
   */
  public async registrarEvento(
    intentoId: string,
    alerta: AlertaProctoring
  ): Promise<EventoProctoringResponse> {
    const url = `${PROCTORING_ENDPOINT}/intentos/${intentoId}/eventos`;

    const body = {
      tipo_evento: alerta.tipo,
      severidad: alerta.severidad,
      detalle: alerta.mensaje,
      datos_adicionales: alerta.datos || {},
    };

    try {
      return await this.fetchWithRetry<EventoProctoringResponse>(url, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(body),
      });
    } catch (error) {
      console.error('Error al registrar evento de proctoring:', error);
      // Agregar a cola para reintento posterior
      this.addToQueue(() => this.registrarEvento(intentoId, alerta));
      throw error;
    }
  }

  /**
   * Sube un snapshot de cámara
   * 
   * @param intentoId - ID del intento de examen
   * @param snapshot - Datos del snapshot
   * @returns Promise con la URL del snapshot almacenado
   */
  public async subirSnapshot(
    intentoId: string,
    snapshot: SnapshotProctoring
  ): Promise<SnapshotResponse> {
    const url = `${PROCTORING_ENDPOINT}/intentos/${intentoId}/snapshots`;

    const body = {
      imagen_base64: snapshot.imagenBase64,
      ancho: snapshot.ancho,
      alto: snapshot.alto,
      calidad: snapshot.calidad,
      rostros_detectados: snapshot.rostrosDetectados,
      metadata: snapshot.metadata || {},
    };

    try {
      return await this.fetchWithRetry<SnapshotResponse>(url, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(body),
      });
    } catch (error) {
      console.error('Error al subir snapshot:', error);
      // Agregar a cola para reintento posterior
      this.addToQueue(() => this.subirSnapshot(intentoId, snapshot));
      throw error;
    }
  }

  /**
   * Registra un evento de audio
   * 
   * @param intentoId - ID del intento de examen
   * @param eventoAudio - Datos del evento de audio
   * @returns Promise con la confirmación del servidor
   */
  public async registrarEventoAudio(
    intentoId: string,
    eventoAudio: EventoAudio
  ): Promise<EventoAudioResponse> {
    const url = `${PROCTORING_ENDPOINT}/intentos/${intentoId}/eventos-audio`;

    const body = {
      nivel_audio: eventoAudio.nivelAudio,
      duracion_ms: eventoAudio.duracionMs,
      frecuencia_dominante: eventoAudio.frecuenciaDominante || null,
      es_sospechoso: eventoAudio.esSospechoso,
      metadata: {
        timestamp: eventoAudio.timestamp.toISOString(),
      },
    };

    try {
      return await this.fetchWithRetry<EventoAudioResponse>(url, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(body),
      });
    } catch (error) {
      console.error('Error al registrar evento de audio:', error);
      // Agregar a cola para reintento posterior
      this.addToQueue(() => this.registrarEventoAudio(intentoId, eventoAudio));
      throw error;
    }
  }

  /**
   * Obtiene el resumen de proctoring de un intento
   * 
   * @param intentoId - ID del intento de examen
   * @returns Promise con el resumen completo
   */
  public async obtenerResumen(intentoId: string): Promise<ResumenProctoring> {
    const url = `${PROCTORING_ENDPOINT}/intentos/${intentoId}/resumen`;

    return await this.fetchWithRetry<ResumenProctoring>(url, {
      method: 'GET',
      headers: this.getHeaders(),
    });
  }

  /**
   * Resuelve un evento de proctoring (solo profesores)
   * 
   * @param eventoId - ID del evento
   * @param notas - Notas de resolución (opcional)
   * @returns Promise con la confirmación
   */
  public async resolverEvento(
    eventoId: string,
    notas?: string
  ): Promise<{ mensaje: string; evento_id: string; timestamp: string }> {
    const url = `${PROCTORING_ENDPOINT}/eventos/${eventoId}/resolver`;

    return await this.fetchWithRetry(url, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify({ notas }),
    });
  }

  /**
   * Agrega un request a la cola para reintento posterior
   */
  private addToQueue(request: () => Promise<void>): void {
    this.requestQueue.push(request);
    
    if (!this.isProcessingQueue) {
      this.processQueue();
    }
  }

  /**
   * Procesa la cola de requests pendientes
   */
  private async processQueue(): Promise<void> {
    if (this.isProcessingQueue || this.requestQueue.length === 0) {
      return;
    }

    this.isProcessingQueue = true;

    while (this.requestQueue.length > 0) {
      const request = this.requestQueue.shift();
      
      if (request) {
        try {
          await request();
        } catch (error) {
          console.error('Error al procesar request de cola:', error);
        }
      }

      // Esperar 1 segundo entre requests
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    this.isProcessingQueue = false;
  }

  /**
   * Limpia la cola de requests pendientes
   */
  public clearQueue(): void {
    this.requestQueue = [];
  }

  /**
   * Obtiene el número de requests en cola
   */
  public getQueueSize(): number {
    return this.requestQueue.length;
  }
}

// Exportar instancia única
export const proctoringService = ProctoringService.getInstance();

// Exportar clase para testing
export { ProctoringService };
