import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiZap, FiStar, FiHeart } from 'react-icons/fi';

export default function Preloader({ show }: { show: boolean }) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className="fixed inset-0 z-[9999] flex items-center justify-center bg-gradient-to-br from-violet-900 via-purple-900 to-indigo-900 dark:from-gray-900 dark:via-purple-900/50 dark:to-gray-900"
          initial={{ opacity: 1 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Partículas de fondo */}
          <div className="absolute inset-0 overflow-hidden">
            {[...Array(20)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-2 h-2 bg-white/20 rounded-full"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                }}
                animate={{
                  y: [-20, -100],
                  opacity: [0, 1, 0],
                }}
                transition={{
                  duration: 3 + Math.random() * 2,
                  repeat: Infinity,
                  delay: Math.random() * 2,
                  ease: "easeOut",
                }}
              />
            ))}
          </div>

          <motion.div
            className="flex flex-col items-center gap-8 relative z-10"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Logo principal con animaciones avanzadas */}
            <div className="relative">
              {/* Círculo exterior animado */}
              <motion.div
                className="absolute inset-0 w-32 h-32 rounded-full border-4 border-violet-400/30"
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
              />
              
              {/* Círculo medio */}
              <motion.div
                className="absolute inset-2 w-28 h-28 rounded-full border-2 border-purple-400/50"
                animate={{ rotate: -360 }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
              />
              
              {/* Logo central */}
              <motion.div
                className="relative w-32 h-32 rounded-full bg-gradient-to-br from-violet-500 via-purple-600 to-indigo-600 flex items-center justify-center shadow-2xl border-4 border-white/20"
                animate={{ 
                  scale: [1, 1.1, 1],
                  boxShadow: [
                    "0 0 20px rgba(139, 92, 246, 0.5)",
                    "0 0 40px rgba(139, 92, 246, 0.8)", 
                    "0 0 20px rgba(139, 92, 246, 0.5)"
                  ]
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <motion.span 
                  className="text-4xl font-black text-white"
                  animate={{ 
                    textShadow: [
                      "0 0 10px rgba(255, 255, 255, 0.5)",
                      "0 0 20px rgba(255, 255, 255, 0.8)",
                      "0 0 10px rgba(255, 255, 255, 0.5)"
                    ]
                  }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  A
                </motion.span>
              </motion.div>

              {/* Iconos flotantes alrededor */}
              {[
                { icon: FiZap, angle: 0, delay: 0 },
                { icon: FiStar, angle: 120, delay: 0.5 },
                { icon: FiHeart, angle: 240, delay: 1 },
              ].map(({ icon: Icon, angle, delay }, idx) => (
                <motion.div
                  key={idx}
                  className="absolute w-8 h-8 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center shadow-lg"
                  style={{
                    left: `${50 + 35 * Math.cos((angle * Math.PI) / 180)}%`,
                    top: `${50 + 35 * Math.sin((angle * Math.PI) / 180)}%`,
                    transform: 'translate(-50%, -50%)',
                  }}
                  animate={{
                    y: [-5, 5, -5],
                    rotate: [0, 10, 0],
                    scale: [1, 1.2, 1],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    delay,
                    ease: "easeInOut",
                  }}
                >
                  <Icon className="w-4 h-4 text-white" />
                </motion.div>
              ))}
            </div>

            {/* Texto principal */}
            <motion.div
              className="text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.7 }}
            >
              <motion.h1 
                className="text-3xl font-black text-white mb-2"
                animate={{ 
                  textShadow: [
                    "0 0 10px rgba(255, 255, 255, 0.3)",
                    "0 0 20px rgba(255, 255, 255, 0.6)",
                    "0 0 10px rgba(255, 255, 255, 0.3)"
                  ]
                }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                Acadify
              </motion.h1>
              <motion.p 
                className="text-violet-200 text-lg font-medium"
                animate={{ opacity: [0.7, 1, 0.7] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                Preparando tu experiencia de aprendizaje...
              </motion.p>
            </motion.div>

            {/* Barra de progreso animada */}
            <motion.div
              className="w-64 h-2 bg-white/10 rounded-full overflow-hidden"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5, duration: 0.5 }}
            >
              <motion.div
                className="h-full bg-gradient-to-r from-violet-400 via-purple-500 to-indigo-500 rounded-full"
                animate={{
                  x: ['-100%', '100%'],
                  boxShadow: [
                    "0 0 10px rgba(139, 92, 246, 0.5)",
                    "0 0 20px rgba(139, 92, 246, 0.8)",
                    "0 0 10px rgba(139, 92, 246, 0.5)"
                  ]
                }}
                transition={{
                  x: { duration: 1.5, repeat: Infinity, ease: "easeInOut" },
                  boxShadow: { duration: 1, repeat: Infinity }
                }}
              />
            </motion.div>

            {/* Puntos de carga */}
            <motion.div 
              className="flex gap-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7, duration: 0.5 }}
            >
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-3 h-3 bg-violet-400 rounded-full"
                  animate={{
                    scale: [1, 1.5, 1],
                    opacity: [0.5, 1, 0.5],
                  }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    delay: i * 0.2,
                    ease: "easeInOut",
                  }}
                />
              ))}
            </motion.div>

            {/* Mensaje inspiracional */}
            <motion.div
              className="text-center max-w-xs"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1, duration: 0.7 }}
            >
              <motion.p 
                className="text-violet-100 text-sm italic"
                animate={{ opacity: [0.6, 1, 0.6] }}
                transition={{ duration: 3, repeat: Infinity }}
              >
                "El aprendizaje nunca agota la mente"
              </motion.p>
              <motion.p 
                className="text-violet-300 text-xs mt-1"
                animate={{ opacity: [0.4, 0.8, 0.4] }}
                transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
              >
                - Leonardo da Vinci
              </motion.p>
            </motion.div>
          </motion.div>

          {/* Efecto de ondas */}
          <motion.div
            className="absolute inset-0 pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.5 }}
          >
            {[1, 2, 3].map((i) => (
              <motion.div
                key={i}
                className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 border border-violet-400/20 rounded-full"
                animate={{
                  width: [`${20 + i * 10}px`, `${200 + i * 50}px`],
                  height: [`${20 + i * 10}px`, `${200 + i * 50}px`],
                  opacity: [0.8, 0],
                }}
                transition={{
                  duration: 2 + i * 0.5,
                  repeat: Infinity,
                  delay: i * 0.3,
                  ease: "easeOut",
                }}
              />
            ))}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
