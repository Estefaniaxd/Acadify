/**
 * Componente optimizado para toggle de tema
 * Usa el ThemeContext centralizado
 */

import React from 'react';
import { motion } from 'framer-motion';
;
import { useTheme } from '../context/ThemeContext';
import { Moon, Sun } from 'lucide-react';

type Props = {
  // Props opcionales para compatibilidad con código legacy
  readonly theme?: 'light' | 'dark';
  readonly setTheme?: (t: 'light' | 'dark') => void;
}

export default function ThemeToggle({ theme: legacyTheme, setTheme: legacySetTheme }: Readonly<Props>) {
  // Usar el contexto de tema si está disponible, sino usar props legacy
  const contextTheme = useTheme();
  
  const theme = legacyTheme || contextTheme.theme;
  const toggleTheme = legacySetTheme 
    ? () => legacySetTheme(theme === 'dark' ? 'light' : 'dark')
    : contextTheme.toggleTheme;
  
  const isDark = theme === 'dark';

  return (
    <motion.button
      aria-label={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      className="relative p-3 rounded-2xl transition-all duration-300 shadow-md hover:shadow-lg group overflow-hidden"
      style={{
        background: isDark
          ? 'linear-gradient(135deg, rgba(40, 20, 80, 0.6) 0%, rgba(139, 92, 246, 0.4) 100%)'
          : 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.95) 100%)',
        border: isDark ? '1px solid #312e81' : '1px solid #ede9fe',
      }}
      onClick={toggleTheme}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {/* Icono animado */}
      <motion.div
        animate={{ rotate: isDark ? 180 : 0 }}
        transition={{ duration: 0.5, ease: 'easeInOut' }}
        className="relative z-10"
      >
        {isDark ? (
          <Sun className="w-5 h-5 text-yellow-400" />
        ) : (
          <Moon className="w-5 h-5 text-purple-600" />
        )}
      </motion.div>

      {/* Efecto de brillo al hover */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100"
        animate={{
          x: ['-100%', '100%'],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          repeatDelay: 2,
        }}
      />
    </motion.button>
  );
}
