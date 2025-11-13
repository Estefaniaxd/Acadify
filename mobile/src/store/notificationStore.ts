/**
 * Notification Store
 * Global notifications management with Zustand
 * 
 * @module store/notificationStore
 * @follows Single Responsibility Principle
 */

import { create } from 'zustand';

// ==================== TYPES ====================

export interface Notification {
  id: string;
  type: 'curso' | 'mensaje' | 'logro' | 'sistema';
  titulo: string;
  descripcion: string;
  leida: boolean;
  url?: string;
  data?: any;
  created_at: string;
}

export interface NotificationState {
  // State
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;

  // Actions
  addNotification: (notification: Omit<Notification, 'id' | 'leida' | 'created_at'>) => void;
  markAsRead: (notificationId: string) => void;
  markAllAsRead: () => void;
  removeNotification: (notificationId: string) => void;
  clearAll: () => void;
  setNotifications: (notifications: Notification[]) => void;
  setLoading: (loading: boolean) => void;
}

// ==================== STORE ====================

/**
 * Notification Store
 * Manages app notifications (push, in-app)
 * 
 * @example
 * ```typescript
 * const { notifications, unreadCount, addNotification, markAsRead } = useNotificationStore();
 * 
 * // Add notification
 * addNotification({
 *   type: 'logro',
 *   titulo: 'Nuevo logro desbloqueado',
 *   descripcion: 'Has completado tu primer curso'
 * });
 * 
 * // Mark as read
 * markAsRead(notificationId);
 * ```
 */
export const useNotificationStore = create<NotificationState>((set, get) => ({
  // Initial state
  notifications: [],
  unreadCount: 0,
  loading: false,

  /**
   * Add new notification
   * @param {Omit<Notification, 'id' | 'leida' | 'created_at'>} notification - Notification data
   */
  addNotification: (notification) => {
    const newNotification: Notification = {
      ...notification,
      id: `notif-${Date.now()}-${Math.random()}`,
      leida: false,
      created_at: new Date().toISOString(),
    };

    set((state) => ({
      notifications: [newNotification, ...state.notifications],
      unreadCount: state.unreadCount + 1,
    }));
  },

  /**
   * Mark notification as read
   * @param {string} notificationId - Notification ID
   */
  markAsRead: (notificationId) => {
    set((state) => ({
      notifications: state.notifications.map((notif) =>
        notif.id === notificationId ? { ...notif, leida: true } : notif
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    }));
  },

  /**
   * Mark all notifications as read
   */
  markAllAsRead: () => {
    set((state) => ({
      notifications: state.notifications.map((notif) => ({ ...notif, leida: true })),
      unreadCount: 0,
    }));
  },

  /**
   * Remove notification
   * @param {string} notificationId - Notification ID
   */
  removeNotification: (notificationId) => {
    set((state) => {
      const notification = state.notifications.find((n) => n.id === notificationId);
      const wasUnread = notification && !notification.leida;

      return {
        notifications: state.notifications.filter((notif) => notif.id !== notificationId),
        unreadCount: wasUnread ? Math.max(0, state.unreadCount - 1) : state.unreadCount,
      };
    });
  },

  /**
   * Clear all notifications
   */
  clearAll: () => {
    set({
      notifications: [],
      unreadCount: 0,
    });
  },

  /**
   * Set notifications from API
   * @param {Notification[]} notifications - Notifications array
   */
  setNotifications: (notifications) => {
    const unreadCount = notifications.filter((n) => !n.leida).length;
    set({ notifications, unreadCount });
  },

  /**
   * Set loading state
   * @param {boolean} loading - Loading state
   */
  setLoading: (loading) => {
    set({ loading });
  },
}));
