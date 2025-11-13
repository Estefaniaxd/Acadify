/**
 * Development Logger Utility
 * 
 * Conditional logging that only runs in development mode
 * Production builds will tree-shake these away
 */

type LogLevel = 'info' | 'warn' | 'error' | 'debug';

const isDev = import.meta.env.DEV;

export const logger = {
  /**
   * Info logs - only in development
   */
  info: (...args: any[]) => {
    if (isDev) {
      console.log(...args);
    }
  },

  /**
   * Warning logs - only in development
   */
  warn: (...args: any[]) => {
    if (isDev) {
      console.warn(...args);
    }
  },

  /**
   * Error logs - always logged (needed in production for monitoring)
   */
  error: (...args: any[]) => {
    console.error(...args);
  },

  /**
   * Debug logs - only in development
   */
  debug: (...args: any[]) => {
    if (isDev) {
      console.debug(...args);
    }
  },

  /**
   * Group logs - only in development
   */
  group: (label: string, callback: () => void) => {
    if (isDev) {
      console.group(label);
      callback();
      console.groupEnd();
    }
  },

  /**
   * Table logs - only in development
   */
  table: (data: any) => {
    if (isDev) {
      console.table(data);
    }
  },

  /**
   * Time measurement - only in development
   */
  time: (label: string) => {
    if (isDev) {
      console.time(label);
    }
  },

  timeEnd: (label: string) => {
    if (isDev) {
      console.timeEnd(label);
    }
  },
};

/**
 * Conditional logger factory
 * Use this when you need different behavior per component
 */
export const createLogger = (prefix: string, enabled = isDev) => ({
  info: (...args: any[]) => enabled && console.log(`[${prefix}]`, ...args),
  warn: (...args: any[]) => enabled && console.warn(`[${prefix}]`, ...args),
  error: (...args: any[]) => console.error(`[${prefix}]`, ...args),
  debug: (...args: any[]) => enabled && console.debug(`[${prefix}]`, ...args),
});
