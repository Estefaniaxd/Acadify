import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Preloader({ show }: { show: boolean }) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/90 dark:bg-[#18181b]/90"
          initial={{ opacity: 1 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            className="flex flex-col items-center gap-4"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Mascota animada o logo */}
            <motion.div
              className="w-24 h-24 rounded-full bg-gradient-to-br from-primary to-purple-700 flex items-center justify-center shadow-2xl border-4 border-black dark:border-white/10"
              animate={{ rotate: [0, 360] }}
              transition={{ repeat: Infinity, duration: 1.6, ease: 'linear' }}
            >
              <span className="text-3xl font-black text-primary">A</span>
            </motion.div>
            <motion.div
              className="text-lg font-bold text-white mt-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.7 }}
            >
              Cargando Acadify...
            </motion.div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
