/**
 * Message Service
 * Handles all messaging and chat-related API calls
 * 
 * @module services/message
 * @implements Repository Pattern
 * @follows Single Responsibility Principle
 */

import { apiClient } from '@/utils/api';
import { AxiosResponse } from 'axios';

// ==================== TYPES ====================

/**
 * Conversation data
 */
export interface Conversation {
  id: string;
  tipo: 'individual' | 'grupo';
  nombre?: string;
  avatar_url?: string;
  ultimo_mensaje?: Message;
  no_leidos: number;
  participantes: ConversationParticipant[];
  created_at: string;
  updated_at: string;
}

/**
 * Conversation participant
 */
export interface ConversationParticipant {
  usuario_id: string;
  nombre: string;
  avatar_url?: string;
  es_admin: boolean;
  estado_online: boolean;
  ultima_conexion?: string;
}

/**
 * Message data
 */
export interface Message {
  id: string;
  conversacion_id: string;
  remitente_id: string;
  remitente_nombre: string;
  remitente_avatar?: string;
  contenido: string;
  tipo: 'texto' | 'imagen' | 'archivo' | 'audio';
  archivo_url?: string;
  archivo_nombre?: string;
  archivo_tamano?: number;
  es_leido: boolean;
  editado: boolean;
  respondiendo_a?: {
    mensaje_id: string;
    contenido: string;
    remitente_nombre: string;
  };
  created_at: string;
  updated_at: string;
}

/**
 * Send message request
 */
export interface SendMessageRequest {
  conversacion_id: string;
  contenido: string;
  tipo?: 'texto' | 'imagen' | 'archivo' | 'audio';
  respondiendo_a_id?: string;
}

/**
 * Create conversation request
 */
export interface CreateConversationRequest {
  tipo: 'individual' | 'grupo';
  participantes_ids: string[];
  nombre?: string;
}

/**
 * Update conversation request
 */
export interface UpdateConversationRequest {
  nombre?: string;
  avatar_url?: string;
}

/**
 * Typing indicator
 */
export interface TypingIndicator {
  conversacion_id: string;
  usuario_id: string;
  usuario_nombre: string;
  is_typing: boolean;
}

/**
 * Paginated messages
 */
export interface PaginatedMessages {
  data: Message[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// ==================== SERVICE ====================

/**
 * Message Service
 * Provides methods for messaging and chat management
 * 
 * @class MessageService
 * @implements Repository Pattern
 */
class MessageService {
  private readonly baseUrl = '/messages';

  /**
   * Get user's conversations
   * 
   * @param {number} limit - Max conversations to return
   * @param {number} offset - Offset for pagination
   * @returns {Promise<Conversation[]>} List of conversations
   * @throws {AxiosError} If request fails
   * 
   * @example
   * ```typescript
   * const conversations = await messageService.getConversations(20, 0);
   * ```
   */
  async getConversations(limit = 20, offset = 0): Promise<Conversation[]> {
    const response: AxiosResponse<Conversation[]> = await apiClient.get(
      `${this.baseUrl}/conversations`,
      { params: { limit, offset } }
    );
    return response.data;
  }

  /**
   * Get conversation by ID
   * 
   * @param {string} conversationId - Conversation ID
   * @returns {Promise<Conversation>} Conversation details
   * @throws {AxiosError} If conversation not found
   * 
   * @example
   * ```typescript
   * const conversation = await messageService.getConversationById('conv-123');
   * ```
   */
  async getConversationById(conversationId: string): Promise<Conversation> {
    const response: AxiosResponse<Conversation> = await apiClient.get(
      `${this.baseUrl}/conversations/${conversationId}`
    );
    return response.data;
  }

  /**
   * Create new conversation
   * 
   * @param {CreateConversationRequest} data - Conversation data
   * @returns {Promise<Conversation>} Created conversation
   * @throws {AxiosError} If validation fails
   * 
   * @example
   * ```typescript
   * const conversation = await messageService.createConversation({
   *   tipo: 'grupo',
   *   participantes_ids: ['user-1', 'user-2', 'user-3'],
   *   nombre: 'Grupo de estudio'
   * });
   * ```
   */
  async createConversation(data: CreateConversationRequest): Promise<Conversation> {
    const response: AxiosResponse<Conversation> = await apiClient.post(
      `${this.baseUrl}/conversations`,
      data
    );
    return response.data;
  }

  /**
   * Update conversation
   * 
   * @param {string} conversationId - Conversation ID
   * @param {UpdateConversationRequest} data - Update data
   * @returns {Promise<Conversation>} Updated conversation
   * @throws {AxiosError} If not admin or conversation not found
   * 
   * @example
   * ```typescript
   * await messageService.updateConversation('conv-123', {
   *   nombre: 'Nuevo nombre del grupo'
   * });
   * ```
   */
  async updateConversation(
    conversationId: string,
    data: UpdateConversationRequest
  ): Promise<Conversation> {
    const response: AxiosResponse<Conversation> = await apiClient.patch(
      `${this.baseUrl}/conversations/${conversationId}`,
      data
    );
    return response.data;
  }

  /**
   * Delete conversation
   * 
   * @param {string} conversationId - Conversation ID
   * @returns {Promise<{message: string}>} Success message
   * @throws {AxiosError} If not admin or conversation not found
   * 
   * @example
   * ```typescript
   * await messageService.deleteConversation('conv-123');
   * ```
   */
  async deleteConversation(conversationId: string): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.delete(
      `${this.baseUrl}/conversations/${conversationId}`
    );
    return response.data;
  }

  /**
   * Get conversation messages
   * 
   * @param {string} conversationId - Conversation ID
   * @param {number} limit - Max messages to return
   * @param {number} offset - Offset for pagination
   * @returns {Promise<PaginatedMessages>} List of messages
   * @throws {AxiosError} If conversation not found
   * 
   * @example
   * ```typescript
   * const messages = await messageService.getMessages('conv-123', 50, 0);
   * ```
   */
  async getMessages(
    conversationId: string,
    limit = 50,
    offset = 0
  ): Promise<PaginatedMessages> {
    const response: AxiosResponse<PaginatedMessages> = await apiClient.get(
      `${this.baseUrl}/conversations/${conversationId}/messages`,
      { params: { limit, offset } }
    );
    return response.data;
  }

  /**
   * Send message
   * 
   * @param {SendMessageRequest} data - Message data
   * @returns {Promise<Message>} Sent message
   * @throws {AxiosError} If validation fails or not participant
   * 
   * @example
   * ```typescript
   * const message = await messageService.sendMessage({
   *   conversacion_id: 'conv-123',
   *   contenido: 'Hola a todos!',
   *   tipo: 'texto'
   * });
   * ```
   */
  async sendMessage(data: SendMessageRequest): Promise<Message> {
    const response: AxiosResponse<Message> = await apiClient.post(
      `${this.baseUrl}/conversations/${data.conversacion_id}/messages`,
      data
    );
    return response.data;
  }

  /**
   * Upload file and send as message
   * 
   * @param {string} conversationId - Conversation ID
   * @param {File | Blob} file - File to upload
   * @param {string} tipo - File type (imagen, archivo, audio)
   * @returns {Promise<Message>} Sent message with file
   * @throws {AxiosError} If file too large or invalid format
   * 
   * @example
   * ```typescript
   * const message = await messageService.sendFile('conv-123', imageFile, 'imagen');
   * ```
   */
  async sendFile(conversationId: string, file: File | Blob, tipo: string): Promise<Message> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('tipo', tipo);

    const response: AxiosResponse<Message> = await apiClient.post(
      `${this.baseUrl}/conversations/${conversationId}/messages/file`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  /**
   * Edit message
   * 
   * @param {string} conversationId - Conversation ID
   * @param {string} messageId - Message ID
   * @param {string} newContent - New message content
   * @returns {Promise<Message>} Updated message
   * @throws {AxiosError} If not owner or message not found
   * 
   * @example
   * ```typescript
   * await messageService.editMessage('conv-123', 'msg-456', 'Contenido editado');
   * ```
   */
  async editMessage(
    conversationId: string,
    messageId: string,
    newContent: string
  ): Promise<Message> {
    const response: AxiosResponse<Message> = await apiClient.patch(
      `${this.baseUrl}/conversations/${conversationId}/messages/${messageId}`,
      { contenido: newContent }
    );
    return response.data;
  }

  /**
   * Delete message
   * 
   * @param {string} conversationId - Conversation ID
   * @param {string} messageId - Message ID
   * @returns {Promise<{message: string}>} Success message
   * @throws {AxiosError} If not owner or message not found
   * 
   * @example
   * ```typescript
   * await messageService.deleteMessage('conv-123', 'msg-456');
   * ```
   */
  async deleteMessage(conversationId: string, messageId: string): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.delete(
      `${this.baseUrl}/conversations/${conversationId}/messages/${messageId}`
    );
    return response.data;
  }

  /**
   * Mark messages as read
   * 
   * @param {string} conversationId - Conversation ID
   * @returns {Promise<{message: string; marcados: number}>} Success message
   * @throws {AxiosError} If conversation not found
   * 
   * @example
   * ```typescript
   * const result = await messageService.markAsRead('conv-123');
   * console.log('Marcados:', result.marcados);
   * ```
   */
  async markAsRead(conversationId: string): Promise<{ message: string; marcados: number }> {
    const response: AxiosResponse<{ message: string; marcados: number }> = await apiClient.post(
      `${this.baseUrl}/conversations/${conversationId}/read`
    );
    return response.data;
  }

  /**
   * Send typing indicator
   * 
   * @param {string} conversationId - Conversation ID
   * @param {boolean} isTyping - Whether user is typing
   * @returns {Promise<void>}
   * @throws {AxiosError} If conversation not found
   * 
   * @example
   * ```typescript
   * await messageService.sendTypingIndicator('conv-123', true);
   * // ... user typing
   * await messageService.sendTypingIndicator('conv-123', false);
   * ```
   */
  async sendTypingIndicator(conversationId: string, isTyping: boolean): Promise<void> {
    await apiClient.post(`${this.baseUrl}/conversations/${conversationId}/typing`, {
      is_typing: isTyping,
    });
  }

  /**
   * Add participant to conversation
   * 
   * @param {string} conversationId - Conversation ID
   * @param {string} userId - User ID to add
   * @returns {Promise<{message: string}>} Success message
   * @throws {AxiosError} If not admin or user already participant
   * 
   * @example
   * ```typescript
   * await messageService.addParticipant('conv-123', 'user-456');
   * ```
   */
  async addParticipant(conversationId: string, userId: string): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.post(
      `${this.baseUrl}/conversations/${conversationId}/participants`,
      { usuario_id: userId }
    );
    return response.data;
  }

  /**
   * Remove participant from conversation
   * 
   * @param {string} conversationId - Conversation ID
   * @param {string} userId - User ID to remove
   * @returns {Promise<{message: string}>} Success message
   * @throws {AxiosError} If not admin or user not participant
   * 
   * @example
   * ```typescript
   * await messageService.removeParticipant('conv-123', 'user-456');
   * ```
   */
  async removeParticipant(conversationId: string, userId: string): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.delete(
      `${this.baseUrl}/conversations/${conversationId}/participants/${userId}`
    );
    return response.data;
  }

  /**
   * Leave conversation
   * 
   * @param {string} conversationId - Conversation ID
   * @returns {Promise<{message: string}>} Success message
   * @throws {AxiosError} If not participant
   * 
   * @example
   * ```typescript
   * await messageService.leaveConversation('conv-123');
   * ```
   */
  async leaveConversation(conversationId: string): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.post(
      `${this.baseUrl}/conversations/${conversationId}/leave`
    );
    return response.data;
  }

  /**
   * Search messages
   * 
   * @param {string} conversationId - Conversation ID
   * @param {string} query - Search query
   * @returns {Promise<Message[]>} Matching messages
   * @throws {AxiosError} If conversation not found
   * 
   * @example
   * ```typescript
   * const messages = await messageService.searchMessages('conv-123', 'importante');
   * ```
   */
  async searchMessages(conversationId: string, query: string): Promise<Message[]> {
    const response: AxiosResponse<Message[]> = await apiClient.get(
      `${this.baseUrl}/conversations/${conversationId}/search`,
      { params: { q: query } }
    );
    return response.data;
  }

  /**
   * Get unread conversations count
   * 
   * @returns {Promise<{count: number}>} Unread count
   * @throws {AxiosError} If request fails
   * 
   * @example
   * ```typescript
   * const { count } = await messageService.getUnreadCount();
   * console.log('Mensajes sin leer:', count);
   * ```
   */
  async getUnreadCount(): Promise<{ count: number }> {
    const response: AxiosResponse<{ count: number }> = await apiClient.get(
      `${this.baseUrl}/unread-count`
    );
    return response.data;
  }
}

// Export singleton instance
export const messageService = new MessageService();
export default messageService;
