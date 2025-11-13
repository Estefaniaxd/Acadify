/**
 * TypingIndicator Component
 * =========================
 * Componente indicador de usuarios escribiendo.
 * 
 * Responsabilidades:
 * - Mostrar quién está escribiendo
 * - Animación de puntos
 * - Formato según cantidad de usuarios
 * 
 * @author Acadify Team
 */

import React from 'react';
import { motion } from 'framer-motion';

interface TypingIndicatorProps {
  usuarios: string[];
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({ usuarios }) => {
  if (usuarios.length === 0) return null;

  // Formatear texto según cantidad de usuarios
  const getTexto = (): string => {
    if (usuarios.length === 1) {
      return `${usuarios[0]} está escribiendo`;
    } else if (usuarios.length === 2) {
      return `${usuarios[0]} y ${usuarios[1]} están escribiendo`;
    } else {
      return `${usuarios[0]} y ${usuarios.length - 1} más están escribiendo`;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      className="flex items-center space-x-2 mb-2"
    >
      <div className="bg-gray-200 dark:bg-gray-700 rounded-2xl px-4 py-2 flex items-center space-x-2">
        {/* Dots animados */}
        <div className="flex space-x-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-2 h-2 bg-gray-500 dark:bg-gray-400 rounded-full"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.5, 1, 0.5]
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
                delay: i * 0.2
              }}
            />
          ))}
        </div>
        
        {/* Texto */}
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {getTexto()}
        </span>
      </div>
    </motion.div>
  );
};

export default TypingIndicator;
