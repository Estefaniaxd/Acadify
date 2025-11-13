import React, { createContext, useContext, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';

type Variant = 'success' | 'warning' | 'danger' | 'info';

export interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: Variant;
}

interface ToastContextValue {
  toast: (options: Omit<Toast, 'id'>) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within ToastProvider');
  return context;
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = (options: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36);
    const newToast = { ...options, id };
    setToasts(prev => [...prev, newToast]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3000);
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <View style={styles.container}>
        {toasts.map(t => (
          <View key={t.id} style={[styles.toast, t.variant && styles[t.variant]]}>
            <Text style={styles.title}>{t.title}</Text>
            {t.description && <Text style={styles.desc}>{t.description}</Text>}
          </View>
        ))}
      </View>
    </ToastContext.Provider>
  );
};

const styles = StyleSheet.create({
  container: { position: 'absolute', top: 50, left: 0, right: 0, alignItems: 'center' },
  toast: { backgroundColor: '#3b82f6', borderRadius: 12, padding: 16, marginBottom: 8, minWidth: 300, maxWidth: '90%' },
  success: { backgroundColor: '#10b981' },
  warning: { backgroundColor: '#f59e0b' },
  danger: { backgroundColor: '#dc2626' },
  info: { backgroundColor: '#3b82f6' },
  title: { fontSize: 14, fontWeight: '600', color: '#fff' },
  desc: { fontSize: 12, color: '#fff', opacity: 0.9, marginTop: 4 },
});

export default ToastProvider;
