import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface EmojiPickerProps {
  onEmojiSelect: (emoji: string) => void;
  isOpen: boolean;
  onClose: () => void;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

// Lista de emojis categorizada estilo Discord moderna
const emojiCategories = {
  'Frecuentes': {
    icon: '⭐',
    emojis: ['😀', '😂', '😍', '😭', '😊', '🤔', '😎', '🔥', '👍', '👏', '❤️', '💀', '😢', '🙄', '😤', '😳', '🤪', '😅', '🥺', '👀']
  },
  'Emociones': {
    icon: '😊',
    emojis: [
      '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃',
      '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '�',
      '🥲', '�😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🤫',
      '🤔', '🤐', '🤨', '😐', '😑', '😶', '😏', '😒', '🙄', '😬',
      '🤥', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢', '🤮',
      '🤧', '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '😎', '🤓'
    ]
  },
  'Gestos': {
    icon: '👋',
    emojis: [
      '�', '🤚', '�️', '✋', '�', '�👌', '🤏', '✌️', '🤞', '🤟',
      '🤘', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝️', '�', '👎',
      '👊', '✊', '�', '🤜', '�', '🙌', '�', '🤝', '🙏', '✍️',
      '�', '🤳', '�', '�', '🦿', '🦵', '🦶', '�', '🦻', '�'
    ]
  },
  'Personas': {
    icon: '👥',
    emojis: [
      '👶', '🧒', '👦', '👧', '🧑', '👨', '👩', '🧓', '👴', '👵',
      '👱‍♂️', '👱‍♀️', '🧔', '👨‍🦰', '👨‍🦱', '👨‍🦳', '👨‍🦲', '👩‍🦰', '👩‍🦱', '👩‍🦳',
      '👩‍🦲', '🤵', '👰', '🤰', '🤱', '👼', '🎅', '🤶', '🦸‍♂️', '🦸‍♀️',
      '🦹‍♂️', '🦹‍♀️', '🧙‍♂️', '🧙‍♀️', '🧚‍♂️', '🧚‍♀️', '🧛‍♂️', '🧛‍♀️', '🧜‍♂️', '🧜‍♀️'
    ]
  },
  'Animales': {
    icon: '🐶',
    emojis: [
      '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯',
      '🦁', '🐮', '🐷', '🐽', '🐸', '🐵', '🙈', '🙉', '🙊', '🐒',
      '🦍', '🦘', '🦌', '🐕', '🐩', '🦮', '🐈', '🐓', '🦃', '🦅',
      '🦆', '🦢', '🦉', '🦩', '🦚', '🦜', '�', '�', '🐤', '🐣'
    ]
  },
  'Comida': {
    icon: '🍕',
    emojis: [
      '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍈',
      '🍒', '🍑', '🥭', '🍍', '🥥', '🥝', '🍅', '🍆', '🥑', '🥦',
      '🥬', '🥒', '🌶️', '🫑', '🌽', '🥕', '🫒', '🧄', '🧅', '🥔',
      '🍠', '🥐', '🍞', '🥖', '🥨', '🧀', '🥚', '🍳', '�', '�'
    ]
  },
  'Actividades': {
    icon: '⚽',
    emojis: [
      '⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🥏', '🎱',
      '🪀', '🏓', '🏸', '🏒', '🏑', '🥍', '🏏', '🪃', '🥅', '⛳',
      '🪁', '🏹', '🎣', '🤿', '🥊', '🥋', '🎽', '🛹', '🛼', '🛷'
    ]
  },
  'Objetos': {
    icon: '💎',
    emojis: [
      '⌚', '📱', '📲', '💻', '⌨️', '🖥️', '🖨️', '🖱️', '🖲️', '🕹️',
      '🗜️', '💽', '💾', '💿', '📀', '📼', '📷', '📸', '📹', '🎥',
      '📽️', '🎞️', '📞', '☎️', '📟', '📠', '📺', '📻', '🎙️', '🎚️'
    ]
  },
  'Símbolos': {
    icon: '❤️',
    emojis: [
      '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔',
      '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '☮️',
      '✝️', '☪️', '🕉️', '☸️', '✡️', '🔯', '🕎', '☯️', '☦️', '🛐',
      '🔥', '💯', '💫', '⭐', '🌟', '✨', '⚡', '💥', '💢', '💨'
    ]
  }
};

export const EmojiPicker: React.FC<EmojiPickerProps> = ({
  onEmojiSelect,
  isOpen,
  onClose,
  position = 'bottom',
  className = ''
}) => {
  const [activeCategory, setActiveCategory] = useState('Frecuentes');
  const [searchTerm, setSearchTerm] = useState('');
  const pickerRef = useRef<HTMLDivElement>(null);

  // Cerrar cuando se hace click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  // Filtrar emojis por búsqueda
  const filteredEmojis = searchTerm ? 
    Object.values(emojiCategories).flatMap(cat => cat.emojis).filter(emoji => 
      emoji.includes(searchTerm.toLowerCase())
    ) : 
    emojiCategories[activeCategory as keyof typeof emojiCategories]?.emojis || [];

  const handleEmojiClick = (emoji: string) => {
    onEmojiSelect(emoji);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        ref={pickerRef}
        initial={{ opacity: 0, scale: 0.95, y: position === 'bottom' ? -10 : 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: position === 'bottom' ? -10 : 10 }}
        transition={{ 
          type: "spring",
          stiffness: 300,
          damping: 30,
          duration: 0.2 
        }}
        className={`
          absolute z-50 bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700
          backdrop-blur-sm overflow-hidden
          ${position === 'bottom' ? 'top-full mt-2' : ''}
          ${position === 'top' ? 'bottom-full mb-2' : ''}
          ${position === 'left' ? 'right-full mr-2' : ''}
          ${position === 'right' ? 'left-full ml-2' : ''}
          ${className}
        `}
        style={{ width: '350px', height: '420px' }}
      >
        {/* Header elegante con gradiente */}
        <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-lg">Emojis</h3>
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white transition-colors p-1"
            >
              ✕
            </button>
          </div>
          <input
            type="text"
            placeholder="Buscar emojis..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 text-sm rounded-xl border-0 
                     focus:outline-none focus:ring-2 focus:ring-white/30
                     bg-white/20 backdrop-blur-sm placeholder-white/60 text-white"
          />
        </div>

        <div className="flex h-full">
          {/* Categorías con iconos */}
          {!searchTerm && (
            <div className="w-16 bg-gray-50 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-600 overflow-y-auto">
              {Object.entries(emojiCategories).map(([category, data]) => (
                <motion.button
                  key={category}
                  onClick={() => setActiveCategory(category)}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className={`
                    w-full p-3 text-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200
                    ${activeCategory === category 
                      ? 'bg-blue-100 dark:bg-blue-900 border-r-2 border-blue-500' 
                      : 'text-gray-600 dark:text-gray-400'
                    }
                  `}
                  title={category}
                >
                  {data.icon}
                </motion.button>
              ))}
            </div>
          )}

          {/* Grid de emojis mejorado */}
          <div className="flex-1 p-4 overflow-y-auto bg-gray-50/50 dark:bg-gray-800/50">
            {searchTerm && (
              <div className="mb-3 text-sm text-gray-500 dark:text-gray-400 font-medium">
                {filteredEmojis.length} resultados para "{searchTerm}"
              </div>
            )}
            
            <div className="grid grid-cols-8 gap-2">
              {filteredEmojis.map((emoji, index) => (
                <motion.button
                  key={`${emoji}-${index}`}
                  onClick={() => handleEmojiClick(emoji)}
                  whileHover={{ scale: 1.2, rotate: 5 }}
                  whileTap={{ scale: 0.9 }}
                  className="w-8 h-8 flex items-center justify-center text-xl 
                           hover:bg-white dark:hover:bg-gray-700 rounded-lg
                           transition-all duration-150 cursor-pointer
                           hover:shadow-md active:shadow-sm"
                  title={emoji}
                >
                  {emoji}
                </motion.button>
              ))}
            </div>

            {filteredEmojis.length === 0 && searchTerm && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center py-12 text-gray-500 dark:text-gray-400"
              >
                <div className="text-4xl mb-3">�</div>
                <div className="font-medium">No se encontraron emojis</div>
                <div className="text-sm mt-1">Intenta con otra búsqueda</div>
              </motion.div>
            )}
          </div>
        </div>

        {/* Footer con información */}
        <div className="p-2 bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-600">
          <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
            Haz clic en un emoji para reaccionar
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default EmojiPicker;