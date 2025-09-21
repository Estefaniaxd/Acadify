/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Paleta principal de Acadify - Tonos Morados y Verdes Súper Llamativos
        primary: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7', // purple principal
          600: '#9333ea',
          700: '#7c2d12',
          800: '#6b21a8',
          900: '#581c87',
          950: '#3b0764',
        },
        secondary: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981', // green principal
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
          950: '#022c22',
        },
        // Colores SÚPER LLAMATIVOS para dark mode
        neon: {
          purple: '#bf00ff',
          green: '#00ff88',
          blue: '#0099ff',
          pink: '#ff0099',
          cyan: '#00ffff',
          yellow: '#ffff00',
          orange: '#ff6600',
        },
        // Colores dark mode específicos
        dark: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
        accent: {
          yellow: '#fbbf24',
          pink: '#ec4899',
          blue: '#3b82f6',
          orange: '#f97316',
        },
        // Colores neutros personalizados
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        }
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #a855f7 0%, #9333ea 100%)',
        'gradient-secondary': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        'gradient-hero': 'linear-gradient(135deg, #a855f7 0%, #10b981 100%)',
        'gradient-hero-dark': 'linear-gradient(135deg, #bf00ff 0%, #00ff88 100%)',
        'gradient-card': 'linear-gradient(135deg, #f5f3ff 0%, #ecfdf5 100%)',
        'gradient-card-dark': 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        'gradient-cta': 'linear-gradient(135deg, #9333ea 0%, #10b981 100%)',
        'gradient-cta-dark': 'linear-gradient(135deg, #bf00ff 0%, #00ff88 100%)',
        'gradient-neon': 'linear-gradient(45deg, #bf00ff, #00ff88, #0099ff, #ff0099)',
        'gradient-radial': 'radial-gradient(ellipse at center, var(--tw-gradient-stops))',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'display': ['Poppins', 'Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'bounce-slow': 'bounce 3s infinite',
        'pulse-slow': 'pulse 4s infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'glow-neon': 'glowNeon 2s ease-in-out infinite alternate',
        'wiggle': 'wiggle 1s ease-in-out infinite',
        'fade-in': 'fadeIn 0.5s ease-in',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'rainbow': 'rainbow 3s linear infinite',
        'neon-pulse': 'neonPulse 1.5s ease-in-out infinite alternate',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glow: {
          '0%': { 'box-shadow': '0 0 5px #a855f7, 0 0 10px #a855f7, 0 0 15px #a855f7' },
          '100%': { 'box-shadow': '0 0 10px #10b981, 0 0 20px #10b981, 0 0 30px #10b981' },
        },
        glowNeon: {
          '0%': { 'box-shadow': '0 0 5px #bf00ff, 0 0 10px #bf00ff, 0 0 20px #bf00ff, 0 0 40px #bf00ff' },
          '100%': { 'box-shadow': '0 0 5px #00ff88, 0 0 10px #00ff88, 0 0 20px #00ff88, 0 0 40px #00ff88' },
        },
        neonPulse: {
          '0%': { 
            'box-shadow': '0 0 5px #bf00ff, 0 0 10px #bf00ff, 0 0 15px #bf00ff',
            'text-shadow': '0 0 5px #bf00ff, 0 0 10px #bf00ff'
          },
          '100%': { 
            'box-shadow': '0 0 10px #00ff88, 0 0 20px #00ff88, 0 0 30px #00ff88',
            'text-shadow': '0 0 10px #00ff88, 0 0 20px #00ff88'
          },
        },
        rainbow: {
          '0%': { 'background-position': '0% 50%' },
          '50%': { 'background-position': '100% 50%' },
          '100%': { 'background-position': '0% 50%' },
        },
        wiggle: {
          '0%, 100%': { transform: 'rotate(-3deg)' },
          '50%': { transform: 'rotate(3deg)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      boxShadow: {
        'glow': '0 0 20px rgba(168, 85, 247, 0.3)',
        'glow-green': '0 0 20px rgba(16, 185, 129, 0.3)',
        'glow-neon': '0 0 20px rgba(191, 0, 255, 0.5)',
        'glow-neon-green': '0 0 20px rgba(0, 255, 136, 0.5)',
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'card-dark': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
        'card-dark-hover': '0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.3)',
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}