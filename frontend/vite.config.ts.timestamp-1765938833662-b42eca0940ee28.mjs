// vite.config.ts
import { defineConfig } from "file:///run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/frontend/node_modules/.pnpm/vite@5.1.5_@types+node@24.9.1/node_modules/vite/dist/node/index.js";
import react from "file:///run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/frontend/node_modules/.pnpm/@vitejs+plugin-react@5.0.4_vite@5.1.5_@types+node@24.9.1_/node_modules/@vitejs/plugin-react/dist/index.js";
var vite_config_default = defineConfig(({ mode }) => ({
  plugins: [react()],
  // Eliminar console.logs en producción
  esbuild: {
    drop: mode === "production" ? ["console", "debugger"] : []
  },
  resolve: {
    alias: {
      "@": "/src"
    }
  },
  build: {
    // Optimizaciones de bundle
    rollupOptions: {
      output: {
        // Manual chunking para mejor cache y lazy loading
        manualChunks: (id) => {
          if (id.includes("node_modules")) {
            if (id.includes("react") || id.includes("react-dom") || id.includes("react-router")) {
              return "react-vendor";
            }
            if (id.includes("framer-motion")) {
              return "framer-motion";
            }
            if (id.includes("@tanstack/react-query")) {
              return "react-query";
            }
            if (id.includes("react-icons")) {
              return "icons";
            }
            return "vendor";
          }
          if (id.includes("/src/components/ui/")) {
            return "ui-components";
          }
          if (id.includes("/src/components/layout/")) {
            return "layout";
          }
          if (id.includes("/src/components/nav/")) {
            return "navigation";
          }
          if (id.includes("/src/pages/auth/")) {
            return "auth";
          }
          if (id.includes("/src/pages/dashboard/") || id.includes("/src/modules/dashboard/")) {
            return "dashboard";
          }
          if (id.includes("/src/modules/avatar/") || id.includes("/src/pages/avatar/") || id.includes("/src/components/avatar/")) {
            return "avatar";
          }
          if (id.includes("/src/modules/comunicacion/") || id.includes("/src/components/comunicacion/")) {
            return "comunicacion";
          }
          if (id.includes("/src/modules/logros/") || id.includes("/src/modules/puntos/") || id.includes("/src/modules/niveles/") || id.includes("/src/modules/tienda/")) {
            return "gamificacion";
          }
          if (id.includes("/src/hooks/")) {
            return "hooks";
          }
          if (id.includes("/src/utils/")) {
            return "utils";
          }
        },
        // Nombres de archivo con hash para cache-busting
        chunkFileNames: "assets/[name]-[hash].js",
        entryFileNames: "assets/[name]-[hash].js",
        assetFileNames: "assets/[name]-[hash].[ext]"
      }
    },
    // Aumentar límite de advertencia para chunks grandes conocidos
    chunkSizeWarningLimit: 600,
    // Minificación con esbuild (más rápido que terser)
    minify: "esbuild",
    // Source maps deshabilitados para producción
    sourcemap: false,
    // CSS code splitting
    cssCodeSplit: true
  },
  // Optimizaciones de desarrollo
  optimizeDeps: {
    include: ["react", "react-dom", "react-router-dom"],
    // Pre-bundle critical deps
    exclude: ["@tanstack/react-query-devtools"]
    // Excluir devtools
  },
  server: {
    port: 5173,
    proxy: {
      "/auth": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
        // Excluir rutas de OAuth callback para que las maneje React Router
        bypass: (req) => {
          if (req.url?.startsWith("/auth/google/callback")) {
            return req.url;
          }
        }
      },
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false
      },
      "/static": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false
      },
      "/invitaciones": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false
      },
      "/uploads": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false
      }
    }
  }
}));
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvcnVuL21lZGlhL2FyY2gvU3RvcmFnZS9TRU5BL1Byb3llY3RvLUZvcm1hdGl2by9BY2FkaWZ5L2Zyb250ZW5kXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCIvcnVuL21lZGlhL2FyY2gvU3RvcmFnZS9TRU5BL1Byb3llY3RvLUZvcm1hdGl2by9BY2FkaWZ5L2Zyb250ZW5kL3ZpdGUuY29uZmlnLnRzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9ydW4vbWVkaWEvYXJjaC9TdG9yYWdlL1NFTkEvUHJveWVjdG8tRm9ybWF0aXZvL0FjYWRpZnkvZnJvbnRlbmQvdml0ZS5jb25maWcudHNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlJ1xuaW1wb3J0IHJlYWN0IGZyb20gJ0B2aXRlanMvcGx1Z2luLXJlYWN0J1xuXG5leHBvcnQgZGVmYXVsdCBkZWZpbmVDb25maWcoKHsgbW9kZSB9KSA9PiAoe1xuICBwbHVnaW5zOiBbcmVhY3QoKV0sXG4gIC8vIEVsaW1pbmFyIGNvbnNvbGUubG9ncyBlbiBwcm9kdWNjaVx1MDBGM25cbiAgZXNidWlsZDoge1xuICAgIGRyb3A6IG1vZGUgPT09ICdwcm9kdWN0aW9uJyA/IFsnY29uc29sZScsICdkZWJ1Z2dlciddIDogW10sXG4gIH0sXG4gIHJlc29sdmU6IHtcbiAgICBhbGlhczoge1xuICAgICAgJ0AnOiAnL3NyYycsXG4gICAgfSxcbiAgfSxcbiAgYnVpbGQ6IHtcbiAgICAvLyBPcHRpbWl6YWNpb25lcyBkZSBidW5kbGVcbiAgICByb2xsdXBPcHRpb25zOiB7XG4gICAgICBvdXRwdXQ6IHtcbiAgICAgICAgLy8gTWFudWFsIGNodW5raW5nIHBhcmEgbWVqb3IgY2FjaGUgeSBsYXp5IGxvYWRpbmdcbiAgICAgICAgbWFudWFsQ2h1bmtzOiAoaWQpID0+IHtcbiAgICAgICAgICAvLyBWZW5kb3IgY2h1bmtzIChsaWJyZXJcdTAwRURhcyBncmFuZGVzKVxuICAgICAgICAgIGlmIChpZC5pbmNsdWRlcygnbm9kZV9tb2R1bGVzJykpIHtcbiAgICAgICAgICAgIC8vIFJlYWN0IGNvcmUgYnVuZGxlIChlc3RhYmxlLCBidWVuIGNhY2hlKVxuICAgICAgICAgICAgaWYgKGlkLmluY2x1ZGVzKCdyZWFjdCcpIHx8IGlkLmluY2x1ZGVzKCdyZWFjdC1kb20nKSB8fCBpZC5pbmNsdWRlcygncmVhY3Qtcm91dGVyJykpIHtcbiAgICAgICAgICAgICAgcmV0dXJuICdyZWFjdC12ZW5kb3InO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgLy8gRnJhbWVyIE1vdGlvbiBidW5kbGUgc2VwYXJhZG8gKGdyYW5kZSlcbiAgICAgICAgICAgIGlmIChpZC5pbmNsdWRlcygnZnJhbWVyLW1vdGlvbicpKSB7XG4gICAgICAgICAgICAgIHJldHVybiAnZnJhbWVyLW1vdGlvbic7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgICAvLyBSZWFjdCBRdWVyeSBidW5kbGVcbiAgICAgICAgICAgIGlmIChpZC5pbmNsdWRlcygnQHRhbnN0YWNrL3JlYWN0LXF1ZXJ5JykpIHtcbiAgICAgICAgICAgICAgcmV0dXJuICdyZWFjdC1xdWVyeSc7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgICAvLyBSZWFjdCBJY29ucyBidW5kbGUgc2VwYXJhZG8gKG11eSBncmFuZGUpXG4gICAgICAgICAgICBpZiAoaWQuaW5jbHVkZXMoJ3JlYWN0LWljb25zJykpIHtcbiAgICAgICAgICAgICAgcmV0dXJuICdpY29ucyc7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgICAvLyBPdHJvcyB2ZW5kb3JzXG4gICAgICAgICAgICByZXR1cm4gJ3ZlbmRvcic7XG4gICAgICAgICAgfVxuXG4gICAgICAgICAgLy8gRmVhdHVyZSBjaHVua3MgKGNvZGUgc3BsaXR0aW5nIHBvciBtXHUwMEYzZHVsbylcbiAgICAgICAgICAvLyBVSSBDb21wb25lbnRzIGJ1bmRsZSAocmV1dGlsaXphYmxlcylcbiAgICAgICAgICBpZiAoaWQuaW5jbHVkZXMoJy9zcmMvY29tcG9uZW50cy91aS8nKSkge1xuICAgICAgICAgICAgcmV0dXJuICd1aS1jb21wb25lbnRzJztcbiAgICAgICAgICB9XG4gICAgICAgICAgLy8gTGF5b3V0IGNvbXBvbmVudHMgKE5hdiwgRm9vdGVyLCBldGMpXG4gICAgICAgICAgaWYgKGlkLmluY2x1ZGVzKCcvc3JjL2NvbXBvbmVudHMvbGF5b3V0LycpKSB7XG4gICAgICAgICAgICByZXR1cm4gJ2xheW91dCc7XG4gICAgICAgICAgfVxuICAgICAgICAgIC8vIE5hdmlnYXRpb24gY29tcG9uZW50cyAoU2lkZWJhcnMsIGV0YylcbiAgICAgICAgICBpZiAoaWQuaW5jbHVkZXMoJy9zcmMvY29tcG9uZW50cy9uYXYvJykpIHtcbiAgICAgICAgICAgIHJldHVybiAnbmF2aWdhdGlvbic7XG4gICAgICAgICAgfVxuICAgICAgICAgIC8vIEF1dGggcGFnZXMgYnVuZGxlXG4gICAgICAgICAgaWYgKGlkLmluY2x1ZGVzKCcvc3JjL3BhZ2VzL2F1dGgvJykpIHtcbiAgICAgICAgICAgIHJldHVybiAnYXV0aCc7XG4gICAgICAgICAgfVxuICAgICAgICAgIC8vIERhc2hib2FyZCBidW5kbGVcbiAgICAgICAgICBpZiAoaWQuaW5jbHVkZXMoJy9zcmMvcGFnZXMvZGFzaGJvYXJkLycpIHx8IGlkLmluY2x1ZGVzKCcvc3JjL21vZHVsZXMvZGFzaGJvYXJkLycpKSB7XG4gICAgICAgICAgICByZXR1cm4gJ2Rhc2hib2FyZCc7XG4gICAgICAgICAgfVxuICAgICAgICAgIC8vIEF2YXRhci9FZGl0b3IgYnVuZGxlIChwZXNhZG8pXG4gICAgICAgICAgaWYgKGlkLmluY2x1ZGVzKCcvc3JjL21vZHVsZXMvYXZhdGFyLycpIHx8IGlkLmluY2x1ZGVzKCcvc3JjL3BhZ2VzL2F2YXRhci8nKSB8fCBpZC5pbmNsdWRlcygnL3NyYy9jb21wb25lbnRzL2F2YXRhci8nKSkge1xuICAgICAgICAgICAgcmV0dXJuICdhdmF0YXInO1xuICAgICAgICAgIH1cbiAgICAgICAgICAvLyBDb211bmljYWNpXHUwMEYzbiBidW5kbGVcbiAgICAgICAgICBpZiAoaWQuaW5jbHVkZXMoJy9zcmMvbW9kdWxlcy9jb211bmljYWNpb24vJykgfHwgaWQuaW5jbHVkZXMoJy9zcmMvY29tcG9uZW50cy9jb211bmljYWNpb24vJykpIHtcbiAgICAgICAgICAgIHJldHVybiAnY29tdW5pY2FjaW9uJztcbiAgICAgICAgICB9XG4gICAgICAgICAgLy8gR2FtaWZpY2FjaVx1MDBGM24gYnVuZGxlXG4gICAgICAgICAgaWYgKGlkLmluY2x1ZGVzKCcvc3JjL21vZHVsZXMvbG9ncm9zLycpIHx8IGlkLmluY2x1ZGVzKCcvc3JjL21vZHVsZXMvcHVudG9zLycpIHx8IGlkLmluY2x1ZGVzKCcvc3JjL21vZHVsZXMvbml2ZWxlcy8nKSB8fCBpZC5pbmNsdWRlcygnL3NyYy9tb2R1bGVzL3RpZW5kYS8nKSkge1xuICAgICAgICAgICAgcmV0dXJuICdnYW1pZmljYWNpb24nO1xuICAgICAgICAgIH1cbiAgICAgICAgICAvLyBIb29rcyBjb21wYXJ0aWRvc1xuICAgICAgICAgIGlmIChpZC5pbmNsdWRlcygnL3NyYy9ob29rcy8nKSkge1xuICAgICAgICAgICAgcmV0dXJuICdob29rcyc7XG4gICAgICAgICAgfVxuICAgICAgICAgIC8vIFV0aWxzIHkgaGVscGVyc1xuICAgICAgICAgIGlmIChpZC5pbmNsdWRlcygnL3NyYy91dGlscy8nKSkge1xuICAgICAgICAgICAgcmV0dXJuICd1dGlscyc7XG4gICAgICAgICAgfVxuICAgICAgICB9LFxuICAgICAgICAvLyBOb21icmVzIGRlIGFyY2hpdm8gY29uIGhhc2ggcGFyYSBjYWNoZS1idXN0aW5nXG4gICAgICAgIGNodW5rRmlsZU5hbWVzOiAnYXNzZXRzL1tuYW1lXS1baGFzaF0uanMnLFxuICAgICAgICBlbnRyeUZpbGVOYW1lczogJ2Fzc2V0cy9bbmFtZV0tW2hhc2hdLmpzJyxcbiAgICAgICAgYXNzZXRGaWxlTmFtZXM6ICdhc3NldHMvW25hbWVdLVtoYXNoXS5bZXh0XSdcbiAgICAgIH1cbiAgICB9LFxuICAgIC8vIEF1bWVudGFyIGxcdTAwRURtaXRlIGRlIGFkdmVydGVuY2lhIHBhcmEgY2h1bmtzIGdyYW5kZXMgY29ub2NpZG9zXG4gICAgY2h1bmtTaXplV2FybmluZ0xpbWl0OiA2MDAsXG4gICAgLy8gTWluaWZpY2FjaVx1MDBGM24gY29uIGVzYnVpbGQgKG1cdTAwRTFzIHJcdTAwRTFwaWRvIHF1ZSB0ZXJzZXIpXG4gICAgbWluaWZ5OiAnZXNidWlsZCcsXG4gICAgLy8gU291cmNlIG1hcHMgZGVzaGFiaWxpdGFkb3MgcGFyYSBwcm9kdWNjaVx1MDBGM25cbiAgICBzb3VyY2VtYXA6IGZhbHNlLFxuICAgIC8vIENTUyBjb2RlIHNwbGl0dGluZ1xuICAgIGNzc0NvZGVTcGxpdDogdHJ1ZSxcbiAgfSxcbiAgLy8gT3B0aW1pemFjaW9uZXMgZGUgZGVzYXJyb2xsb1xuICBvcHRpbWl6ZURlcHM6IHtcbiAgICBpbmNsdWRlOiBbJ3JlYWN0JywgJ3JlYWN0LWRvbScsICdyZWFjdC1yb3V0ZXItZG9tJ10sIC8vIFByZS1idW5kbGUgY3JpdGljYWwgZGVwc1xuICAgIGV4Y2x1ZGU6IFsnQHRhbnN0YWNrL3JlYWN0LXF1ZXJ5LWRldnRvb2xzJ10sIC8vIEV4Y2x1aXIgZGV2dG9vbHNcbiAgfSxcbiAgc2VydmVyOiB7XG4gICAgcG9ydDogNTE3MyxcbiAgICBwcm94eToge1xuICAgICAgJy9hdXRoJzoge1xuICAgICAgICB0YXJnZXQ6ICdodHRwOi8vMTI3LjAuMC4xOjgwMDAnLFxuICAgICAgICBjaGFuZ2VPcmlnaW46IHRydWUsXG4gICAgICAgIHNlY3VyZTogZmFsc2UsXG4gICAgICAgIC8vIEV4Y2x1aXIgcnV0YXMgZGUgT0F1dGggY2FsbGJhY2sgcGFyYSBxdWUgbGFzIG1hbmVqZSBSZWFjdCBSb3V0ZXJcbiAgICAgICAgYnlwYXNzOiAocmVxKSA9PiB7XG4gICAgICAgICAgaWYgKHJlcS51cmw/LnN0YXJ0c1dpdGgoJy9hdXRoL2dvb2dsZS9jYWxsYmFjaycpKSB7XG4gICAgICAgICAgICByZXR1cm4gcmVxLnVybDsgLy8gRGV2b2x2ZXIgbGEgVVJMIHBhcmEgcXVlIFZpdGUgc2lydmEgZWwgSFRNTCBkZSBSZWFjdFxuICAgICAgICAgIH1cbiAgICAgICAgfSxcbiAgICAgIH0sXG4gICAgICAnL2FwaSc6IHtcbiAgICAgICAgdGFyZ2V0OiAnaHR0cDovLzEyNy4wLjAuMTo4MDAwJyxcbiAgICAgICAgY2hhbmdlT3JpZ2luOiB0cnVlLFxuICAgICAgICBzZWN1cmU6IGZhbHNlLFxuICAgICAgfSxcbiAgICAgICcvc3RhdGljJzoge1xuICAgICAgICB0YXJnZXQ6ICdodHRwOi8vMTI3LjAuMC4xOjgwMDAnLFxuICAgICAgICBjaGFuZ2VPcmlnaW46IHRydWUsXG4gICAgICAgIHNlY3VyZTogZmFsc2UsXG4gICAgICB9LFxuICAgICAgJy9pbnZpdGFjaW9uZXMnOiB7XG4gICAgICAgIHRhcmdldDogJ2h0dHA6Ly8xMjcuMC4wLjE6ODAwMCcsXG4gICAgICAgIGNoYW5nZU9yaWdpbjogdHJ1ZSxcbiAgICAgICAgc2VjdXJlOiBmYWxzZSxcbiAgICAgIH0sXG4gICAgICAnL3VwbG9hZHMnOiB7XG4gICAgICAgIHRhcmdldDogJ2h0dHA6Ly8xMjcuMC4wLjE6ODAwMCcsXG4gICAgICAgIGNoYW5nZU9yaWdpbjogdHJ1ZSxcbiAgICAgICAgc2VjdXJlOiBmYWxzZSxcbiAgICAgIH1cbiAgICB9XG4gIH1cbn0pKVxuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUFrWCxTQUFTLG9CQUFvQjtBQUMvWSxPQUFPLFdBQVc7QUFFbEIsSUFBTyxzQkFBUSxhQUFhLENBQUMsRUFBRSxLQUFLLE9BQU87QUFB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
