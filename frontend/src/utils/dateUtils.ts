/**
 * Date Utilities
 * Funciones centralizadas para formateo de fechas
 * 
 * Benefits:
 * - Single import of date-fns locale (saves ~10KB)
 * - Consistent date formatting across the app
 * - Easy to customize formats
 */

import { formatDistanceToNow, format as formatFn, isToday, isYesterday, isThisWeek, isThisYear } from 'date-fns';
import { es } from 'date-fns/locale';

// Singleton locale instance
const locale = es;

/**
 * Formats a date as relative time (e.g., "hace 5 minutos")
 * 
 * @example
 * formatRelativeTime(new Date()) // "menos de un minuto"
 * formatRelativeTime('2024-01-01') // "hace 10 meses"
 */
export function formatRelativeTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  return formatDistanceToNow(dateObj, {
    addSuffix: true,
    locale,
  });
}

/**
 * Formats a date as short date (e.g., "15 ene")
 * 
 * @example
 * formatShortDate(new Date()) // "01 nov"
 */
export function formatShortDate(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  return formatFn(dateObj, 'dd MMM', { locale });
}

/**
 * Formats a date as full date (e.g., "15 de enero de 2024")
 * 
 * @example
 * formatFullDate(new Date()) // "01 de noviembre de 2025"
 */
export function formatFullDate(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  return formatFn(dateObj, "dd 'de' MMMM 'de' yyyy", { locale });
}

/**
 * Formats a date as date and time (e.g., "15 ene, 14:30")
 * 
 * @example
 * formatDateTime(new Date()) // "01 nov, 10:30"
 */
export function formatDateTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  return formatFn(dateObj, 'dd MMM, HH:mm', { locale });
}

/**
 * Formats a date as time only (e.g., "14:30")
 * 
 * @example
 * formatTime(new Date()) // "10:30"
 */
export function formatTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  return formatFn(dateObj, 'HH:mm', { locale });
}

/**
 * Formats a date intelligently based on how recent it is
 * - Today: "14:30"
 * - Yesterday: "Ayer, 14:30"
 * - This week: "Lunes, 14:30"
 * - This year: "15 ene, 14:30"
 * - Older: "15 ene 2023"
 * 
 * @example
 * formatSmartDate(new Date()) // "10:30"
 * formatSmartDate(yesterday) // "Ayer, 10:30"
 */
export function formatSmartDate(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isToday(dateObj)) {
    return formatTime(dateObj);
  }
  
  if (isYesterday(dateObj)) {
    return `Ayer, ${formatTime(dateObj)}`;
  }
  
  if (isThisWeek(dateObj)) {
    return formatFn(dateObj, "EEEE, HH:mm", { locale });
  }
  
  if (isThisYear(dateObj)) {
    return formatDateTime(dateObj);
  }
  
  return formatFn(dateObj, 'dd MMM yyyy', { locale });
}

/**
 * Formats a date for chat messages
 * - Today: "14:30"
 * - Yesterday: "Ayer"
 * - This week: "Lunes"
 * - Older: "15 ene"
 * 
 * @example
 * formatChatDate(new Date()) // "10:30"
 * formatChatDate(yesterday) // "Ayer"
 */
export function formatChatDate(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isToday(dateObj)) {
    return formatTime(dateObj);
  }
  
  if (isYesterday(dateObj)) {
    return 'Ayer';
  }
  
  if (isThisWeek(dateObj)) {
    return formatFn(dateObj, 'EEEE', { locale });
  }
  
  return formatShortDate(dateObj);
}

/**
 * Parses a date string safely
 * Returns null if invalid
 * 
 * @example
 * parseDate('2024-01-01') // Date object
 * parseDate('invalid') // null
 */
export function parseDate(dateString: string): Date | null {
  try {
    const date = new Date(dateString);
    return isNaN(date.getTime()) ? null : date;
  } catch {
    return null;
  }
}

/**
 * Checks if a date is valid
 * 
 * @example
 * isValidDate(new Date()) // true
 * isValidDate(new Date('invalid')) // false
 */
export function isValidDate(date: Date | string): boolean {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return !isNaN(dateObj.getTime());
}

/**
 * Gets a human-readable time ago (simplified)
 * - "Ahora" (< 1 min)
 * - "Hace 5 min" (< 1 hour)
 * - "Hace 2 horas" (< 1 day)
 * - "Hace 3 días" (< 1 week)
 * - "15 ene" (older)
 * 
 * @example
 * getTimeAgo(new Date()) // "Ahora"
 */
export function getTimeAgo(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - dateObj.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 1) return 'Ahora';
  if (diffMins < 60) return `Hace ${diffMins} min`;
  if (diffHours < 24) return `Hace ${diffHours} ${diffHours === 1 ? 'hora' : 'horas'}`;
  if (diffDays < 7) return `Hace ${diffDays} ${diffDays === 1 ? 'día' : 'días'}`;
  
  return formatShortDate(dateObj);
}
