/**
 * Servicio de Detección de Rostros usando MediaPipe
 * 
 * Este servicio encapsula la lógica de detección de rostros
 * usando la biblioteca MediaPipe Face Detection de Google.
 * 
 * Características:
 * - Detección en tiempo real
 * - Soporte para múltiples rostros
 * - Scoring de confianza
 * - Optimizado para performance
 * 
 * @module FaceDetectionService
 */

// TODO: Descomentar cuando se instale @mediapipe/face_detection
// import { FaceDetection } from '@mediapipe/face_detection';
// import { Camera } from '@mediapipe/camera_utils';

/**
 * Resultado de detección de un rostro individual
 */
export interface DetectedFace {
  /** Score de confianza (0-1) */
  score: number;
  /** Bounding box del rostro */
  boundingBox: {
    xMin: number;
    yMin: number;
    width: number;
    height: number;
  };
  /** Puntos clave faciales (6 puntos) */
  keypoints: Array<{ x: number; y: number }>;
}

/**
 * Resultado completo de la detección
 */
export interface FaceDetectionResult {
  /** Lista de rostros detectados */
  faces: DetectedFace[];
  /** Timestamp de la detección */
  timestamp: number;
  /** Tiempo de procesamiento en ms */
  processingTime: number;
}

/**
 * Configuración del detector
 */
export interface FaceDetectionConfig {
  /** Modelo: 'short' (mejor para cerca) o 'full' (mejor para lejos) */
  modelSelection: 'short' | 'full';
  /** Confianza mínima para considerar un rostro (0-1) */
  minDetectionConfidence: number;
}

/**
 * Servicio de Detección de Rostros
 * 
 * Singleton que gestiona la instancia de MediaPipe Face Detection
 * y proporciona métodos para detectar rostros en imágenes/videos.
 * 
 * @example
 * ```typescript
 * const detector = FaceDetectionService.getInstance();
 * await detector.initialize({
 *   modelSelection: 'short',
 *   minDetectionConfidence: 0.7
 * });
 * 
 * const results = await detector.detectFaces(videoElement);
 * console.log(`Detectados ${results.faces.length} rostros`);
 * ```
 */
class FaceDetectionService {
  private static instance: FaceDetectionService;
  
  // TODO: Descomentar cuando se instale @mediapipe/face_detection
  // private faceDetection: FaceDetection | null = null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private faceDetection: any = null;
  
  private config: FaceDetectionConfig = {
    modelSelection: 'short',
    minDetectionConfidence: 0.7,
  };
  
  private isInitialized = false;
  private isProcessing = false;

  /**
   * Constructor privado (Singleton Pattern)
   */
  private constructor() {}

  /**
   * Obtiene la instancia única del servicio
   */
  public static getInstance(): FaceDetectionService {
    if (!FaceDetectionService.instance) {
      FaceDetectionService.instance = new FaceDetectionService();
    }
    return FaceDetectionService.instance;
  }

  /**
   * Inicializa el detector de rostros
   * 
   * Debe ser llamado antes de usar detectFaces().
   * Carga el modelo de MediaPipe y configura los parámetros.
   * 
   * @param config - Configuración del detector
   * @throws Error si falla la inicialización
   */
  public async initialize(config?: Partial<FaceDetectionConfig>): Promise<void> {
    if (this.isInitialized) {
      console.warn('FaceDetectionService ya está inicializado');
      return;
    }

    // Merge config
    this.config = { ...this.config, ...config };

    try {
      // TODO: Implementar cuando se instale MediaPipe
      // this.faceDetection = new FaceDetection({
      //   locateFile: (file) => {
      //     return `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`;
      //   }
      // });

      // this.faceDetection.setOptions({
      //   model: this.config.modelSelection === 'short' ? 0 : 1,
      //   minDetectionConfidence: this.config.minDetectionConfidence,
      // });

      // await this.faceDetection.initialize();
      
      this.isInitialized = true;
      // eslint-disable-next-line no-console
      console.log('✅ FaceDetectionService inicializado correctamente');
    } catch (error) {
      console.error('❌ Error al inicializar FaceDetectionService:', error);
      throw new Error('No se pudo inicializar el detector de rostros');
    }
  }

  /**
   * Detecta rostros en una imagen o frame de video
   * 
   * @param source - Elemento de imagen o video (HTMLImageElement | HTMLVideoElement | HTMLCanvasElement)
   * @returns Resultado de la detección con rostros encontrados
   * @throws Error si el servicio no está inicializado
   */
  public async detectFaces(
    source: HTMLImageElement | HTMLVideoElement | HTMLCanvasElement
  ): Promise<FaceDetectionResult> {
    if (!this.isInitialized) {
      throw new Error('FaceDetectionService no está inicializado. Llama a initialize() primero.');
    }

    if (this.isProcessing) {
      // Si ya hay una detección en proceso, retornar resultado vacío
      return {
        faces: [],
        timestamp: Date.now(),
        processingTime: 0,
      };
    }

    this.isProcessing = true;
    const startTime = performance.now();

    try {
      // TODO: Implementar cuando se instale MediaPipe
      // const results = await this.faceDetection.send({ image: source });
      
      // SIMULACIÓN temporal para desarrollo (REMOVER cuando MediaPipe esté instalado)
      const results = await this.simulateDetection(source);
      
      const processingTime = performance.now() - startTime;

      return {
        faces: results,
        timestamp: Date.now(),
        processingTime,
      };
    } catch (error) {
      console.error('Error en detectFaces:', error);
      return {
        faces: [],
        timestamp: Date.now(),
        processingTime: 0,
      };
    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * SIMULACIÓN temporal de detección (REMOVER cuando MediaPipe esté instalado)
   * 
   * Simula la detección de rostros para desarrollo sin MediaPipe.
   * Detecta 0, 1 o 2 rostros aleatoriamente con probabilidades realistas.
   */
  private async simulateDetection(
    _source: HTMLImageElement | HTMLVideoElement | HTMLCanvasElement
  ): Promise<DetectedFace[]> {
    // Simular tiempo de procesamiento real (10-30ms)
    await new Promise(resolve => setTimeout(resolve, 10 + Math.random() * 20));

    const random = Math.random();
    
    // 70% probabilidad: 1 rostro (caso normal)
    // 20% probabilidad: 0 rostros (persona se movió)
    // 10% probabilidad: 2 rostros (alguien se acercó)
    
    if (random < 0.20) {
      // 0 rostros
      return [];
    } else if (random < 0.90) {
      // 1 rostro
      return [{
        score: 0.85 + Math.random() * 0.15, // 0.85-1.0
        boundingBox: {
          xMin: 0.3 + Math.random() * 0.1,
          yMin: 0.2 + Math.random() * 0.1,
          width: 0.3 + Math.random() * 0.1,
          height: 0.4 + Math.random() * 0.1,
        },
        keypoints: this.generateRandomKeypoints(),
      }];
    } else {
      // 2 rostros
      return [
        {
          score: 0.80 + Math.random() * 0.15,
          boundingBox: {
            xMin: 0.2,
            yMin: 0.2,
            width: 0.25,
            height: 0.35,
          },
          keypoints: this.generateRandomKeypoints(),
        },
        {
          score: 0.75 + Math.random() * 0.15,
          boundingBox: {
            xMin: 0.55,
            yMin: 0.25,
            width: 0.23,
            height: 0.33,
          },
          keypoints: this.generateRandomKeypoints(),
        },
      ];
    }
  }

  /**
   * Genera keypoints aleatorios para simulación
   */
  private generateRandomKeypoints(): Array<{ x: number; y: number }> {
    return Array.from({ length: 6 }, () => ({
      x: Math.random(),
      y: Math.random(),
    }));
  }

  /**
   * Detecta rostros en modo continuo desde una cámara
   * 
   * Útil para streaming en tiempo real.
   * 
   * @param videoElement - Elemento de video con stream activo
   * @param onResults - Callback llamado cada vez que hay resultados
   * @param intervalMs - Intervalo entre detecciones (default: 100ms = 10 FPS)
   * @returns Función para detener la detección continua
   */
  public startContinuousDetection(
    videoElement: HTMLVideoElement,
    onResults: (results: FaceDetectionResult) => void,
    intervalMs: number = 100
  ): () => void {
    let isRunning = true;

    const detect = async () => {
      if (!isRunning) return;

      try {
        const results = await this.detectFaces(videoElement);
        onResults(results);
      } catch (error) {
        console.error('Error en detección continua:', error);
      }

      if (isRunning) {
        setTimeout(detect, intervalMs);
      }
    };

    // Iniciar detección
    detect();

    // Retornar función para detener
    return () => {
      isRunning = false;
    };
  }

  /**
   * Actualiza la configuración del detector
   * 
   * Puede ser llamado en cualquier momento para ajustar parámetros.
   * 
   * @param config - Configuración parcial a actualizar
   */
  public updateConfig(config: Partial<FaceDetectionConfig>): void {
    this.config = { ...this.config, ...config };
    
    // TODO: Actualizar MediaPipe cuando esté instalado
    // if (this.faceDetection && this.isInitialized) {
    //   this.faceDetection.setOptions({
    //     model: this.config.modelSelection === 'short' ? 0 : 1,
    //     minDetectionConfidence: this.config.minDetectionConfidence,
    //   });
    // }
  }

  /**
   * Libera recursos del detector
   * 
   * Debe ser llamado cuando ya no se necesite el servicio.
   */
  public async dispose(): Promise<void> {
    if (this.faceDetection) {
      // TODO: Descomentar cuando se instale MediaPipe
      // await this.faceDetection.close();
      this.faceDetection = null;
    }
    this.isInitialized = false;
    // eslint-disable-next-line no-console
    console.log('🗑️ FaceDetectionService disposed');
  }

  /**
   * Verifica si el servicio está listo para usar
   */
  public isReady(): boolean {
    return this.isInitialized;
  }

  /**
   * Obtiene la configuración actual
   */
  public getConfig(): FaceDetectionConfig {
    return { ...this.config };
  }
}

// Exportar instancia única
export const faceDetectionService = FaceDetectionService.getInstance();

// Exportar clase para testing
export { FaceDetectionService };
