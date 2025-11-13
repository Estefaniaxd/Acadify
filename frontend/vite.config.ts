import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  // Eliminar console.logs en producción
  esbuild: {
    drop: mode === 'production' ? ['console', 'debugger'] : [],
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  build: {
    // Optimizaciones de bundle
    rollupOptions: {
      output: {
        // Manual chunking para mejor cache y lazy loading
        manualChunks: (id) => {
          // Vendor chunks (librerías grandes)
          if (id.includes('node_modules')) {
            // React core bundle (estable, buen cache)
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router')) {
              return 'react-vendor';
            }
            // Framer Motion bundle separado (grande)
            if (id.includes('framer-motion')) {
              return 'framer-motion';
            }
            // React Query bundle
            if (id.includes('@tanstack/react-query')) {
              return 'react-query';
            }
            // React Icons bundle separado (muy grande)
            if (id.includes('react-icons')) {
              return 'icons';
            }
            // Otros vendors
            return 'vendor';
          }
          
          // Feature chunks (code splitting por módulo)
          // UI Components bundle (reutilizables)
          if (id.includes('/src/components/ui/')) {
            return 'ui-components';
          }
          // Layout components (Nav, Footer, etc)
          if (id.includes('/src/components/layout/')) {
            return 'layout';
          }
          // Navigation components (Sidebars, etc)
          if (id.includes('/src/components/nav/')) {
            return 'navigation';
          }
          // Auth pages bundle
          if (id.includes('/src/pages/auth/')) {
            return 'auth';
          }
          // Dashboard bundle
          if (id.includes('/src/pages/dashboard/') || id.includes('/src/modules/dashboard/')) {
            return 'dashboard';
          }
          // Avatar/Editor bundle (pesado)
          if (id.includes('/src/modules/avatar/') || id.includes('/src/pages/avatar/') || id.includes('/src/components/avatar/')) {
            return 'avatar';
          }
          // Comunicación bundle
          if (id.includes('/src/modules/comunicacion/') || id.includes('/src/components/comunicacion/')) {
            return 'comunicacion';
          }
          // Gamificación bundle
          if (id.includes('/src/modules/logros/') || id.includes('/src/modules/puntos/') || id.includes('/src/modules/niveles/') || id.includes('/src/modules/tienda/')) {
            return 'gamificacion';
          }
          // Hooks compartidos
          if (id.includes('/src/hooks/')) {
            return 'hooks';
          }
          // Utils y helpers
          if (id.includes('/src/utils/')) {
            return 'utils';
          }
        },
        // Nombres de archivo con hash para cache-busting
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    // Aumentar límite de advertencia para chunks grandes conocidos
    chunkSizeWarningLimit: 600,
    // Minificación con esbuild (más rápido que terser)
    minify: 'esbuild',
    // Source maps deshabilitados para producción
    sourcemap: false,
    // CSS code splitting
    cssCodeSplit: true,
  },
  // Optimizaciones de desarrollo
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'], // Pre-bundle critical deps
    exclude: ['@tanstack/react-query-devtools'], // Excluir devtools
  },
  server: {
    port: 5173,
    proxy: {
      '/auth': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
      '/static': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
}))
