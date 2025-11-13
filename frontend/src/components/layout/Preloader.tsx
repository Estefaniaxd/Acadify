import { motion, AnimatePresence } from 'framer-motion';

interface PreloaderProps {
  show: boolean;
}

export default function Preloader({ show }: PreloaderProps) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className="fixed inset-0 z-[9999] flex items-center justify-center bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-neutral-950 dark:via-violet-950/20 dark:to-neutral-900"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4 }}
        >
          {/* Fondo con patrón sutil */}
          <div className="absolute inset-0 opacity-30">
            <div 
              className="absolute inset-0" 
              style={{
                backgroundImage: `radial-gradient(circle at 1px 1px, rgb(139 92 246 / 0.1) 1px, transparent 0)`,
                backgroundSize: '32px 32px'
              }}
            />
          </div>

          {/* Contenedor principal */}
          <motion.div
            className="relative flex flex-col items-center gap-6"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {/* Logo animado */}
            <div className="relative">
              {/* Anillo giratorio */}
              <motion.div
                className="absolute inset-0 w-20 h-20 rounded-full border-3 border-transparent border-t-violet-500 border-r-purple-500"
                animate={{ rotate: 360 }}
                transition={{ duration: 1.2, repeat: Infinity, ease: "linear" }}
              />
              
              {/* Logo central */}
              <motion.div
                className="relative w-20 h-20 rounded-2xl bg-gradient-to-br from-violet-500 via-purple-600 to-indigo-600 flex items-center justify-center shadow-xl"
                animate={{ 
                  scale: [1, 1.05, 1],
                  boxShadow: [
                    "0 10px 40px rgba(139, 92, 246, 0.3)",
                    "0 10px 60px rgba(139, 92, 246, 0.5)", 
                    "0 10px 40px rgba(139, 92, 246, 0.3)"
                  ]
                }}
                transition={{ 
                  duration: 1.5, 
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <motion.span 
                  className="text-3xl font-black text-white"
                  animate={{ opacity: [0.9, 1, 0.9] }}
                  transition={{ duration: 1.2, repeat: Infinity }}
                >
                  A
                </motion.span>
              </motion.div>
            </div>

            {/* Texto */}
            <motion.div
              className="text-center space-y-2"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 dark:from-violet-400 dark:via-purple-400 dark:to-indigo-400 bg-clip-text text-transparent">
                Acadify
              </h1>
              <motion.p 
                className="text-sm text-neutral-600 dark:text-neutral-400"
                animate={{ opacity: [0.7, 1, 0.7] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                Cargando...
              </motion.p>
            </motion.div>

            {/* Puntos de carga */}
            <div className="flex gap-1.5">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-2 h-2 rounded-full bg-gradient-to-r from-violet-500 to-purple-500"
                  animate={{
                    scale: [1, 1.3, 1],
                    opacity: [0.4, 1, 0.4],
                  }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    delay: i * 0.15,
                    ease: "easeInOut",
                  }}
                />
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
