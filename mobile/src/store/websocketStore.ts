/**
 * WebSocket Store
 * Real-time communication management
 * 
 * @module store/websocketStore
 * @follows Single Responsibility Principle
 */

import { create } from 'zustand';

// ==================== TYPES ====================

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface WebSocketMessage {
  type: 'message' | 'typing' | 'read' | 'notification' | 'online_status';
  data: any;
  timestamp: string;
}

export interface WebSocketState {
  // State
  status: ConnectionStatus;
  socket: WebSocket | null;
  reconnectAttempts: number;
  maxReconnectAttempts: number;
  
  // Actions
  connect: (url: string, token: string) => void;
  disconnect: () => void;
  send: (message: WebSocketMessage) => void;
  addMessageHandler: (handler: (message: WebSocketMessage) => void) => () => void;
  
  // Internal
  setStatus: (status: ConnectionStatus) => void;
  handleReconnect: (url: string, token: string) => void;
}

// ==================== STORE ====================

/**
 * WebSocket Store
 * Manages real-time WebSocket connection for chat and notifications
 * 
 * @example
 * ```typescript
 * const { status, connect, send, addMessageHandler } = useWebSocketStore();
 * 
 * // Connect
 * connect('wss://api.acadify.com/ws', accessToken);
 * 
 * // Listen to messages
 * const unsubscribe = addMessageHandler((message) => {
 *   if (message.type === 'message') {
 *     console.log('New message:', message.data);
 *   }
 * });
 * 
 * // Send message
 * send({
 *   type: 'message',
 *   data: { conversacion_id: 'conv-123', contenido: 'Hola!' },
 *   timestamp: new Date().toISOString()
 * });
 * 
 * // Cleanup
 * unsubscribe();
 * disconnect();
 * ```
 */
export const useWebSocketStore = create<WebSocketState>((set, get) => {
  let messageHandlers: Array<(message: WebSocketMessage) => void> = [];
  let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

  return {
    // Initial state
    status: 'disconnected',
    socket: null,
    reconnectAttempts: 0,
    maxReconnectAttempts: 5,

    /**
     * Connect to WebSocket server
     * @param {string} url - WebSocket server URL
     * @param {string} token - Authentication token
     */
    connect: (url, token) => {
      const { socket, status } = get();

      // Don't connect if already connected or connecting
      if (socket && (status === 'connected' || status === 'connecting')) {
        console.log('WebSocket already connected or connecting');
        return;
      }

      try {
        set({ status: 'connecting' });

        // Create WebSocket connection with auth token
        const ws = new WebSocket(`${url}?token=${token}`);

        ws.onopen = () => {
          console.log('✅ WebSocket connected');
          set({ status: 'connected', reconnectAttempts: 0 });

          // Clear reconnect timeout
          if (reconnectTimeout) {
            clearTimeout(reconnectTimeout);
            reconnectTimeout = null;
          }
        };

        ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            
            // Notify all handlers
            messageHandlers.forEach((handler) => {
              try {
                handler(message);
              } catch (error) {
                console.error('Error in message handler:', error);
              }
            });
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          set({ status: 'error' });
        };

        ws.onclose = (event) => {
          console.log('🔌 WebSocket disconnected:', event.code, event.reason);
          set({ status: 'disconnected', socket: null });

          // Attempt reconnection if not a clean close
          if (event.code !== 1000 && event.code !== 1001) {
            get().handleReconnect(url, token);
          }
        };

        set({ socket: ws });
      } catch (error) {
        console.error('Error creating WebSocket:', error);
        set({ status: 'error' });
      }
    },

    /**
     * Disconnect from WebSocket server
     */
    disconnect: () => {
      const { socket } = get();

      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
        reconnectTimeout = null;
      }

      if (socket) {
        socket.close(1000, 'Client disconnect');
        set({ socket: null, status: 'disconnected', reconnectAttempts: 0 });
      }
    },

    /**
     * Send message through WebSocket
     * @param {WebSocketMessage} message - Message to send
     */
    send: (message) => {
      const { socket, status } = get();

      if (!socket || status !== 'connected') {
        console.warn('Cannot send message: WebSocket not connected');
        return;
      }

      try {
        socket.send(JSON.stringify(message));
      } catch (error) {
        console.error('Error sending WebSocket message:', error);
      }
    },

    /**
     * Add message handler
     * @param {Function} handler - Message handler function
     * @returns {Function} Unsubscribe function
     */
    addMessageHandler: (handler) => {
      messageHandlers.push(handler);

      // Return unsubscribe function
      return () => {
        messageHandlers = messageHandlers.filter((h) => h !== handler);
      };
    },

    /**
     * Set connection status
     * @param {ConnectionStatus} status - Connection status
     */
    setStatus: (status) => {
      set({ status });
    },

    /**
     * Handle reconnection with exponential backoff
     * @param {string} url - WebSocket server URL
     * @param {string} token - Authentication token
     */
    handleReconnect: (url, token) => {
      const { reconnectAttempts, maxReconnectAttempts } = get();

      if (reconnectAttempts >= maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
        set({ status: 'error' });
        return;
      }

      // Exponential backoff: 1s, 2s, 4s, 8s, 16s
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 16000);

      console.log(`Reconnecting in ${delay}ms... (attempt ${reconnectAttempts + 1})`);

      reconnectTimeout = setTimeout(() => {
        set((state) => ({ reconnectAttempts: state.reconnectAttempts + 1 }));
        get().connect(url, token);
      }, delay);
    },
  };
});
