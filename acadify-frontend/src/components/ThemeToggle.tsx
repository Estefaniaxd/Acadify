import React from 'react';
import { motion } from 'framer-motion';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <motion.button
      onClick={toggleTheme}
      className="relative w-16 h-8 bg-gray-200 dark:bg-dark-700 rounded-full p-1 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-neon-purple"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-label={`Cambiar a tema ${theme === 'light' ? 'oscuro' : 'claro'}`}
    >
      {/* Background gradient */}
      <motion.div
        className="absolute inset-0 rounded-full bg-gradient-to-r from-primary-400 to-secondary-400 dark:from-neon-purple dark:to-neon-green opacity-0 dark:opacity-100"
        animate={{ opacity: theme === 'dark' ? 1 : 0 }}
        transition={{ duration: 0.3 }}
      />
      
      {/* Toggle switch */}
      <motion.div
        className="relative w-6 h-6 bg-white dark:bg-dark-800 rounded-full shadow-lg flex items-center justify-center"
        animate={{ 
          x: theme === 'light' ? 0 : 32,
          backgroundColor: theme === 'light' ? '#ffffff' : '#1e293b'
        }}
        transition={{ 
          type: "spring", 
          stiffness: 700, 
          damping: 30 
        }}
      >
        {/* Icons */}
        <motion.div
          animate={{ 
            opacity: theme === 'light' ? 1 : 0,
            rotate: theme === 'light' ? 0 : 180,
            scale: theme === 'light' ? 1 : 0.8
          }}
          transition={{ duration: 0.3 }}
          className="absolute"
        >
          <Sun className="w-4 h-4 text-yellow-500" />
        </motion.div>
        
        <motion.div
          animate={{ 
            opacity: theme === 'dark' ? 1 : 0,
            rotate: theme === 'dark' ? 0 : -180,
            scale: theme === 'dark' ? 1 : 0.8
          }}
          transition={{ duration: 0.3 }}
          className="absolute"
        >
          <Moon className="w-4 h-4 text-neon-purple" />
        </motion.div>
      </motion.div>
      
      {/* Glow effect for dark mode */}
      <motion.div
        className="absolute inset-0 rounded-full"
        animate={{ 
          boxShadow: theme === 'dark' 
            ? '0 0 20px rgba(191, 0, 255, 0.3), 0 0 40px rgba(0, 255, 136, 0.2)' 
            : '0 0 0px rgba(0, 0, 0, 0)'
        }}
        transition={{ duration: 0.3 }}
      />
    </motion.button>
  );
};

export default ThemeToggle;