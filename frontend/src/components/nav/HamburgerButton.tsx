import { motion } from 'framer-motion';

export default function HamburgerButton({ onClick }: { onClick: () => void }) {
  return (
    <motion.button
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
  className="fixed top-6 left-4 z-[110] p-2 rounded-lg transition-colors duration-200 focus:outline-none"
      aria-label="Abrir menú"
      onClick={onClick}
    >
      <motion.svg
        className="w-6 h-6 text-purple-700 dark:text-gray-200 drop-shadow"
        fill="none"
        stroke="currentColor"
        strokeWidth={2}
        viewBox="0 0 24 24"
      >
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
      </motion.svg>
    </motion.button>
  );
}
