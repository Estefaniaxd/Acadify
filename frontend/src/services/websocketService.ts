/**
 * WebSocket Service
 * =================
 * Servicio singleton para gestionar conexiones WebSocket en tiempo real.
 * 
 * Características:
 * - Auto-reconnect con exponential backoff
 * - Event emitter pattern para suscripciones
 * - Type-safe messages
 * - Connection state management
 * - Queue de mensajes offline
 * - Heartbeat/ping para mantener conexión viva
 * 
 * Principios SOLID:
 * - Single Responsibility: Solo gestiona WebSocket
 * - Open/Closed: Extensible para nuevos eventos
 * - Dependency Inversion: Depende de abstracciones (EventEmitter)
 * 
 * @author Acadify Team
 * @version 1.0.0
 */

import { EventEmitter } from 'events';

/**
 * Estado de la conexión WebSocket
 */
export enum WebSocketState {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTING = 'disconnecting',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

/**
 * Tipos de eventos WebSocket
 */
export enum WebSocketEventType {
  // Conexión
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  ERROR = 'error',
  RECONNECTING = 'reconnecting',
  
  // Mensajes
  MESSAGE_NEW = 'message.new',
  MESSAGE_EDIT = 'message.edit',
  MESSAGE_DELETE = 'message.delete',
  MESSAGE_REACTION = 'message.reaction',
  MESSAGE_SENT = 'message.sent',
  MESSAGE_EDITED = 'message.edited',
  MESSAGE_DELETED = 'message.deleted',
  
  // Typing indicators
  TYPING_UPDATE = 'typing.update',
  TYPING_STOP = 'typing.stop',
  TYPING_USERS = 'typing.users',
  
  // Read receipts
  READ_RECEIPT = 'read.receipt',
  MESSAGES_READ = 'messages.read',
  
  // Usuarios online
  USER_CONNECTED = 'user.connected',
  USER_DISCONNECTED = 'user.disconnected',
  USER_JOINED = 'user_joined',
  USER_LEFT = 'user_left',
  ONLINE_USERS = 'online.users',
  
  // Reacciones
  REACTION_ADDED = 'reaction.added'
}

/**
 * Opciones de configuración del WebSocket
 */
export interface WebSocketOptions {
  /** URL base del servidor WebSocket */
  baseUrl: string;
  /** Token JWT para autenticación */
  token: string;
  /** Tiempo máximo de espera para reconexión (ms) */
  maxReconnectDelay?: number;
  /** Número máximo de intentos de reconexión */
  maxReconnectAttempts?: number;
  /** Intervalo de heartbeat (ms) */
  heartbeatInterval?: number;
  /** Habilitar logs de debug */
  debug?: boolean;
}

/**
 * Mensaje WebSocket genérico
 */
export interface WebSocketMessage<T = any> {
  type: string;
  data?: T;
  timestamp?: string;
  [key: string]: any;
}

/**
 * Servicio singleton de WebSocket
 */
export class WebSocketService {
  private static instance: WebSocketService | null = null;
  
  private ws: WebSocket | null = null;
  private eventEmitter: EventEmitter;
  private state: WebSocketState = WebSocketState.DISCONNECTED;
  private options: Required<WebSocketOptions>;
  
  // Reconnection
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  
  // Heartbeat
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private lastPongTime: number = 0;
  
  // Message queue para mensajes offline
  private messageQueue: WebSocketMessage[] = [];
  
  // Metadata
  private salaId: string | null = null;
  
  /**
   * Constructor privado (Singleton)
   */
  private constructor(options: WebSocketOptions) {
    this.options = {
      baseUrl: options.baseUrl,
      token: options.token,
      maxReconnectDelay: options.maxReconnectDelay ?? 30000,
      maxReconnectAttempts: options.maxReconnectAttempts ?? 10,
      heartbeatInterval: options.heartbeatInterval ?? 30000,
      debug: options.debug ?? false
    };
    
    this.eventEmitter = new EventEmitter();
    this.eventEmitter.setMaxListeners(50); // Permitir muchos listeners
    
    this.log('WebSocketService inicializado', this.options);
  }
  
  /**
   * Obtiene la instancia singleton
   */
  public static getInstance(options?: WebSocketOptions): WebSocketService {
    if (!WebSocketService.instance) {
      if (!options) {
        throw new Error('WebSocketService: opciones requeridas en la primera llamada');
      }
      WebSocketService.instance = new WebSocketService(options);
    }
    return WebSocketService.instance;
  }
  
  /**
   * Destruye la instancia singleton (útil para tests)
   */
  public static destroyInstance(): void {
    if (WebSocketService.instance) {
      WebSocketService.instance.disconnect();
      WebSocketService.instance = null;
    }
  }
  
  /**
   * Conecta al WebSocket de una sala específica
   */
  public connect(salaId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.state === WebSocketState.CONNECTED && this.salaId === salaId) {
        this.log('Ya conectado a la sala', salaId);
        resolve();
        return;
      }
      
      // Desconectar si hay una conexión previa
      if (this.ws) {
        this.disconnect();
      }
      
      this.salaId = salaId;
      this.setState(WebSocketState.CONNECTING);
      
      const wsUrl = `${this.options.baseUrl}/ws/chat/${salaId}?token=${this.options.token}`;
      this.log('Conectando a WebSocket:', wsUrl);
      
      try {
        this.ws = new WebSocket(wsUrl);
        
        // Event: Open
        this.ws.onopen = () => {
          this.log('✅ WebSocket conectado');
          this.setState(WebSocketState.CONNECTED);
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.flushMessageQueue();
          resolve();
        };
        
        // Event: Message
        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            this.error('Error parsing WebSocket message:', error);
          }
        };
        
        // Event: Error
        this.ws.onerror = (event) => {
          this.error('❌ WebSocket error:', event);
          this.setState(WebSocketState.ERROR);
          this.emit(WebSocketEventType.ERROR, event);
          reject(new Error('WebSocket connection error'));
        };
        
        // Event: Close
        this.ws.onclose = (event) => {
          this.log('❌ WebSocket cerrado:', event.code, event.reason);
          this.stopHeartbeat();
          
          if (this.state !== WebSocketState.DISCONNECTING) {
            // Reconexión automática
            this.attemptReconnect();
          } else {
            this.setState(WebSocketState.DISCONNECTED);
          }
        };
        
      } catch (error) {
        this.error('Error creando WebSocket:', error);
        this.setState(WebSocketState.ERROR);
        reject(error);
      }
    });
  }
  
  /**
   * Desconecta del WebSocket
   */
  public disconnect(): void {
    this.log('Desconectando WebSocket...');
    this.setState(WebSocketState.DISCONNECTING);
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    this.setState(WebSocketState.DISCONNECTED);
    this.salaId = null;
    this.emit(WebSocketEventType.DISCONNECTED, {});
  }
  
  /**
   * Envía un mensaje por WebSocket
   */
  public send<T = any>(type: string, data?: T): void {
    const message: WebSocketMessage<T> = {
      type,
      data,
      timestamp: new Date().toISOString()
    };
    
    if (this.state === WebSocketState.CONNECTED && this.ws) {
      try {
        this.ws.send(JSON.stringify(message));
        this.log('📤 Mensaje enviado:', type, data);
      } catch (error) {
        this.error('Error enviando mensaje:', error);
        this.queueMessage(message);
      }
    } else {
      this.log('⚠️ No conectado, mensaje encolado:', type);
      this.queueMessage(message);
    }
  }
  
  /**
   * Suscribe un listener a un evento
   */
  public on(event: WebSocketEventType | string, callback: (...args: any[]) => void): void {
    this.eventEmitter.on(event, callback);
  }
  
  /**
   * Desuscribe un listener de un evento
   */
  public off(event: WebSocketEventType | string, callback: (...args: any[]) => void): void {
    this.eventEmitter.off(event, callback);
  }
  
  /**
   * Suscribe un listener que se ejecuta solo una vez
   */
  public once(event: WebSocketEventType | string, callback: (...args: any[]) => void): void {
    this.eventEmitter.once(event, callback);
  }
  
  /**
   * Obtiene el estado actual de la conexión
   */
  public getState(): WebSocketState {
    return this.state;
  }
  
  /**
   * Verifica si está conectado
   */
  public isConnected(): boolean {
    return this.state === WebSocketState.CONNECTED;
  }
  
  /**
   * Obtiene la sala actual
   */
  public getCurrentSala(): string | null {
    return this.salaId;
  }
  
  // ==================== Métodos Privados ====================
  
  /**
   * Maneja un mensaje recibido del servidor
   */
  private handleMessage(message: WebSocketMessage): void {
    this.log('📥 Mensaje recibido:', message.type, message);
    
    const eventType = message.type as WebSocketEventType;
    
    // Actualizar last pong time si es heartbeat
    if (eventType === 'pong' || eventType === 'connected') {
      this.lastPongTime = Date.now();
    }
    
    // Emitir evento específico
    this.emit(eventType, message);
    
    // Emitir evento genérico de mensaje
    this.emit('message', message);
  }
  
  /**
   * Emite un evento
   */
  private emit(event: string, data: any): void {
    this.eventEmitter.emit(event, data);
  }
  
  /**
   * Cambia el estado de la conexión
   */
  private setState(newState: WebSocketState): void {
    const oldState = this.state;
    this.state = newState;
    
    if (oldState !== newState) {
      this.log(`Estado cambió: ${oldState} -> ${newState}`);
      this.emit('stateChange', { oldState, newState });
    }
  }
  
  /**
   * Intenta reconectar con exponential backoff
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
      this.error('❌ Máximo de intentos de reconexión alcanzado');
      this.setState(WebSocketState.DISCONNECTED);
      this.emit(WebSocketEventType.ERROR, {
        message: 'Max reconnect attempts reached'
      });
      return;
    }
    
    this.reconnectAttempts++;
    this.setState(WebSocketState.RECONNECTING);
    
    // Exponential backoff: 1s, 2s, 4s, 8s, 16s, 30s (max)
    const delay = Math.min(
      1000 * Math.pow(2, this.reconnectAttempts - 1),
      this.options.maxReconnectDelay
    );
    
    this.log(`🔄 Reconectando en ${delay}ms (intento ${this.reconnectAttempts}/${this.options.maxReconnectAttempts})`);
    this.emit(WebSocketEventType.RECONNECTING, {
      attempt: this.reconnectAttempts,
      delay
    });
    
    this.reconnectTimeout = setTimeout(() => {
      if (this.salaId) {
        this.connect(this.salaId).catch((error) => {
          this.error('Error en reconexión:', error);
        });
      }
    }, delay);
  }
  
  /**
   * Inicia heartbeat para mantener conexión viva
   */
  private startHeartbeat(): void {
    this.stopHeartbeat();
    
    this.lastPongTime = Date.now();
    
    this.heartbeatInterval = setInterval(() => {
      // Verificar si el servidor sigue respondiendo
      const timeSinceLastPong = Date.now() - this.lastPongTime;
      
      if (timeSinceLastPong > this.options.heartbeatInterval * 2) {
        this.log('⚠️ Servidor no responde, reconectando...');
        this.ws?.close();
        return;
      }
      
      // Enviar ping
      this.send('ping', {});
    }, this.options.heartbeatInterval);
  }
  
  /**
   * Detiene heartbeat
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
  
  /**
   * Encola un mensaje para enviar cuando se reconecte
   */
  private queueMessage(message: WebSocketMessage): void {
    this.messageQueue.push(message);
    
    // Limitar tamaño de la cola
    if (this.messageQueue.length > 100) {
      this.messageQueue.shift();
    }
  }
  
  /**
   * Envía todos los mensajes encolados
   */
  private flushMessageQueue(): void {
    if (this.messageQueue.length === 0) return;
    
    this.log(`📤 Enviando ${this.messageQueue.length} mensajes encolados`);
    
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message && this.ws) {
        try {
          this.ws.send(JSON.stringify(message));
        } catch (error) {
          this.error('Error enviando mensaje encolado:', error);
          break;
        }
      }
    }
  }
  
  /**
   * Log de debug
   */
  private log(...args: any[]): void {
    if (this.options.debug) {
      console.log('[WebSocketService]', ...args);
    }
  }
  
  /**
   * Log de error
   */
  private error(...args: any[]): void {
    console.error('[WebSocketService]', ...args);
  }
}

/**
 * Hook factory para crear instancia del servicio
 */
export const createWebSocketService = (options: WebSocketOptions): WebSocketService => {
  return WebSocketService.getInstance(options);
};

/**
 * Obtiene la instancia existente del servicio
 */
export const getWebSocketService = (): WebSocketService => {
  return WebSocketService.getInstance();
};

export default WebSocketService;
