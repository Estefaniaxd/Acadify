/**
 * Custom Hooks for Messages API
 * React Query hooks for messaging with real-time capabilities
 * 
 * @module hooks/useMessages
 */

import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { messageService, type Conversation, type Message, type SendMessageRequest, type CreateConversationRequest, type PaginatedMessages } from '@/services';

// ==================== QUERY KEYS ====================

export const MESSAGE_QUERY_KEYS = {
  conversations: ['conversations'] as const,
  conversationDetail: (id: string) => ['conversations', 'detail', id] as const,
  conversationMessages: (id: string, limit?: number, offset?: number) => 
    ['conversations', id, 'messages', limit, offset] as const,
  unreadCount: ['messages', 'unread-count'] as const,
} as const;

// ==================== CONVERSATIONS ====================

/**
 * Hook para obtener lista de conversaciones
 * 
 * @param {number} limit - Cantidad de conversaciones
 * @param {number} offset - Offset para paginación
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con conversaciones
 * 
 * @example
 * ```typescript
 * const { data: conversations, isLoading } = useConversations();
 * ```
 */
export function useConversations(
  limit = 20,
  offset = 0,
  options?: Omit<UseQueryOptions<Conversation[]>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Conversation[]>({
    queryKey: MESSAGE_QUERY_KEYS.conversations,
    queryFn: () => messageService.getConversations(limit, offset),
    staleTime: 1000 * 30, // 30 seconds - short for real-time feel
    refetchInterval: 1000 * 60, // Refetch every minute
    ...options,
  });
}

/**
 * Hook para obtener detalle de una conversación
 * 
 * @param {string} conversationId - ID de la conversación
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con detalle
 * 
 * @example
 * ```typescript
 * const { data: conversation } = useConversationDetail('conv-123');
 * ```
 */
export function useConversationDetail(
  conversationId: string,
  options?: Omit<UseQueryOptions<Conversation>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Conversation>({
    queryKey: MESSAGE_QUERY_KEYS.conversationDetail(conversationId),
    queryFn: () => messageService.getConversationById(conversationId),
    enabled: !!conversationId,
    staleTime: 1000 * 60, // 1 minute
    ...options,
  });
}

/**
 * Hook para obtener mensajes de una conversación
 * 
 * @param {string} conversationId - ID de la conversación
 * @param {number} limit - Cantidad de mensajes
 * @param {number} offset - Offset para paginación
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con mensajes
 * 
 * @example
 * ```typescript
 * const { data: messages, isLoading } = useConversationMessages('conv-123');
 * ```
 */
export function useConversationMessages(
  conversationId: string,
  limit = 50,
  offset = 0,
  options?: Omit<UseQueryOptions<PaginatedMessages>, 'queryKey' | 'queryFn'>
) {
  return useQuery<PaginatedMessages>({
    queryKey: MESSAGE_QUERY_KEYS.conversationMessages(conversationId, limit, offset),
    queryFn: () => messageService.getMessages(conversationId, limit, offset),
    enabled: !!conversationId,
    staleTime: 1000 * 10, // 10 seconds - very short for chat
    refetchInterval: 1000 * 30, // Refetch every 30 seconds
    ...options,
  });
}

/**
 * Hook para obtener contador de mensajes sin leer
 * 
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con contador
 * 
 * @example
 * ```typescript
 * const { data } = useUnreadMessagesCount();
 * console.log('Sin leer:', data?.count);
 * ```
 */
export function useUnreadMessagesCount(
  options?: Omit<UseQueryOptions<{ count: number }>, 'queryKey' | 'queryFn'>
) {
  return useQuery<{ count: number }>({
    queryKey: MESSAGE_QUERY_KEYS.unreadCount,
    queryFn: () => messageService.getUnreadCount(),
    staleTime: 1000 * 20, // 20 seconds
    refetchInterval: 1000 * 60, // Refetch every minute
    ...options,
  });
}

// ==================== MUTATIONS ====================

/**
 * Hook para crear nueva conversación
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createConversation } = useCreateConversation();
 * createConversation({
 *   tipo: 'grupo',
 *   participantes_ids: ['user-1', 'user-2'],
 *   nombre: 'Mi grupo'
 * });
 * ```
 */
export function useCreateConversation(
  options?: UseMutationOptions<Conversation, Error, CreateConversationRequest>
) {
  const queryClient = useQueryClient();

  return useMutation<Conversation, Error, CreateConversationRequest>({
    mutationFn: (data: CreateConversationRequest) => messageService.createConversation(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MESSAGE_QUERY_KEYS.conversations });
    },
    ...options,
  });
}

/**
 * Hook para enviar mensaje
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: sendMessage, isLoading } = useSendMessage();
 * sendMessage({
 *   conversacion_id: 'conv-123',
 *   contenido: 'Hola!',
 *   tipo: 'texto'
 * });
 * ```
 */
export function useSendMessage(
  options?: UseMutationOptions<Message, Error, SendMessageRequest>
) {
  const queryClient = useQueryClient();

  return useMutation<Message, Error, SendMessageRequest>({
    mutationFn: (data: SendMessageRequest) => messageService.sendMessage(data),
    onSuccess: (_, variables) => {
      // Optimistically update messages list
      queryClient.invalidateQueries({ 
        queryKey: MESSAGE_QUERY_KEYS.conversationMessages(variables.conversacion_id) 
      });
      queryClient.invalidateQueries({ queryKey: MESSAGE_QUERY_KEYS.conversations });
    },
    ...options,
  });
}

/**
 * Hook para enviar archivo
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: sendFile } = useSendFile();
 * sendFile({ conversationId: 'conv-123', file: imageFile, tipo: 'imagen' });
 * ```
 */
export function useSendFile(
  options?: UseMutationOptions<Message, Error, { conversationId: string; file: File | Blob; tipo: string }>
) {
  const queryClient = useQueryClient();

  return useMutation<Message, Error, { conversationId: string; file: File | Blob; tipo: string }>({
    mutationFn: ({ conversationId, file, tipo }) => 
      messageService.sendFile(conversationId, file, tipo),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ 
        queryKey: MESSAGE_QUERY_KEYS.conversationMessages(variables.conversationId) 
      });
      queryClient.invalidateQueries({ queryKey: MESSAGE_QUERY_KEYS.conversations });
    },
    ...options,
  });
}

/**
 * Hook para editar mensaje
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: editMessage } = useEditMessage();
 * editMessage({ conversationId: 'conv-123', messageId: 'msg-456', newContent: 'Editado' });
 * ```
 */
export function useEditMessage(
  options?: UseMutationOptions<Message, Error, { conversationId: string; messageId: string; newContent: string }>
) {
  const queryClient = useQueryClient();

  return useMutation<Message, Error, { conversationId: string; messageId: string; newContent: string }>({
    mutationFn: ({ conversationId, messageId, newContent }) => 
      messageService.editMessage(conversationId, messageId, newContent),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ 
        queryKey: MESSAGE_QUERY_KEYS.conversationMessages(variables.conversationId) 
      });
    },
    ...options,
  });
}

/**
 * Hook para eliminar mensaje
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteMessage } = useDeleteMessage();
 * deleteMessage({ conversationId: 'conv-123', messageId: 'msg-456' });
 * ```
 */
export function useDeleteMessage(
  options?: UseMutationOptions<any, Error, { conversationId: string; messageId: string }>
) {
  const queryClient = useQueryClient();

  return useMutation<any, Error, { conversationId: string; messageId: string }>({
    mutationFn: ({ conversationId, messageId }) => 
      messageService.deleteMessage(conversationId, messageId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ 
        queryKey: MESSAGE_QUERY_KEYS.conversationMessages(variables.conversationId) 
      });
    },
    ...options,
  });
}

/**
 * Hook para marcar mensajes como leídos
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: markAsRead } = useMarkMessagesAsRead();
 * markAsRead('conv-123');
 * ```
 */
export function useMarkMessagesAsRead(
  options?: UseMutationOptions<any, Error, string>
) {
  const queryClient = useQueryClient();

  return useMutation<any, Error, string>({
    mutationFn: (conversationId: string) => messageService.markAsRead(conversationId),
    onSuccess: (_, conversationId) => {
      queryClient.invalidateQueries({ queryKey: MESSAGE_QUERY_KEYS.conversations });
      queryClient.invalidateQueries({ 
        queryKey: MESSAGE_QUERY_KEYS.conversationDetail(conversationId) 
      });
      queryClient.invalidateQueries({ queryKey: MESSAGE_QUERY_KEYS.unreadCount });
    },
    ...options,
  });
}

/**
 * Hook para agregar participante
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: addParticipant } = useAddParticipant();
 * addParticipant({ conversationId: 'conv-123', userId: 'user-456' });
 * ```
 */
export function useAddParticipant(
  options?: UseMutationOptions<any, Error, { conversationId: string; userId: string }>
) {
  const queryClient = useQueryClient();

  return useMutation<any, Error, { conversationId: string; userId: string }>({
    mutationFn: ({ conversationId, userId }) => 
      messageService.addParticipant(conversationId, userId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ 
        queryKey: MESSAGE_QUERY_KEYS.conversationDetail(variables.conversationId) 
      });
    },
    ...options,
  });
}

/**
 * Hook para eliminar participante
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: removeParticipant } = useRemoveParticipant();
 * removeParticipant({ conversationId: 'conv-123', userId: 'user-456' });
 * ```
 */
export function useRemoveParticipant(
  options?: UseMutationOptions<any, Error, { conversationId: string; userId: string }>
) {
  const queryClient = useQueryClient();

  return useMutation<any, Error, { conversationId: string; userId: string }>({
    mutationFn: ({ conversationId, userId }) => 
      messageService.removeParticipant(conversationId, userId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ 
        queryKey: MESSAGE_QUERY_KEYS.conversationDetail(variables.conversationId) 
      });
    },
    ...options,
  });
}

/**
 * Hook para salir de conversación
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: leaveConversation } = useLeaveConversation();
 * leaveConversation('conv-123');
 * ```
 */
export function useLeaveConversation(
  options?: UseMutationOptions<any, Error, string>
) {
  const queryClient = useQueryClient();

  return useMutation<any, Error, string>({
    mutationFn: (conversationId: string) => messageService.leaveConversation(conversationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MESSAGE_QUERY_KEYS.conversations });
    },
    ...options,
  });
}
