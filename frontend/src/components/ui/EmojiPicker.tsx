import React, { useState, useRef, useMemo, memo, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
;
import { useClickOutside, useDebounce, useKeyPress } from '../../hooks';
import { X } from 'lucide-react';

/* ==========================================================================
   😀 EMOJI PICKER COMPONENT PROFESIONAL
   ========================================================================== */

export interface EmojiPickerProps {
  onEmojiSelect: (emoji: string) => void;
  isOpen: boolean;
  onClose: () => void;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
  recentEmojis?: string[];
}

interface EmojiCategory {
  icon: string;
  label: string;
  emojis: string[];
}

const EMOJI_CATEGORIES: Record<string, EmojiCategory> = {
  frecuentes: {
    icon: '⭐',
    label: 'Frecuentes',
    emojis: ['😀', '😂', '😍', '😭', '😊', '🤔', '😎', '🔥', '👍', '👏', '❤️', '💀', '😢', '🙄', '😤', '😳', '🤪', '😅', '🥺', '👀']
  },
  emociones: {
    icon: '😊',
    label: 'Emociones',
    emojis: [
      '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃',
      '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '�',
      '🥲', '�😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🤫',
      '🤔', '🤐', '🤨', '😐', '😑', '😶', '😏', '😒', '🙄', '😬',
      '🤥', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢', '🤮',
      '🤧', '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '😎', '🤓'
    ]
  },
  gestos: {
    icon: '👋',
    label: 'Gestos',
    emojis: [
      '�', '🤚', '�️', '✋', '�', '�👌', '🤏', '✌️', '🤞', '🤟',
      '🤘', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝️', '�', '👎',
      '👊', '✊', '�', '🤜', '�', '🙌', '�', '🤝', '🙏', '✍️',
      '�', '🤳', '�', '�', '🦿', '🦵', '🦶', '�', '🦻', '�'
    ]
  },
  personas: {
    icon: '👥',
    label: 'Personas',
    emojis: [
      '👶', '🧒', '👦', '👧', '🧑', '👨', '👩', '🧓', '👴', '👵',
      '👱‍♂️', '👱‍♀️', '🧔', '👨‍🦰', '👨‍🦱', '👨‍🦳', '👨‍🦲', '👩‍🦰', '👩‍🦱', '👩‍🦳',
      '👩‍🦲', '🤵', '👰', '🤰', '🤱', '👼', '🎅', '🤶', '🦸‍♂️', '🦸‍♀️',
      '🦹‍♂️', '🦹‍♀️', '🧙‍♂️', '🧙‍♀️', '🧚‍♂️', '🧚‍♀️', '🧛‍♂️', '🧛‍♀️', '🧜‍♂️', '🧜‍♀️'
    ]
  },
  animales: {
    icon: '🐶',
    label: 'Animales',
    emojis: [
      '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯',
      '🦁', '🐮', '🐷', '🐽', '🐸', '🐵', '🙈', '🙉', '🙊', '🐒',
      '🦍', '🦘', '🦌', '🐕', '🐩', '🦮', '🐈', '🐓', '🦃', '🦅',
      '🦆', '🦢', '🦉', '🦩', '🦚', '🦜', '�', '�', '🐤', '🐣'
    ]
  },
  comida: {
    icon: '🍕',
    label: 'Comida',
    emojis: [
      '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍈',
      '🍒', '🍑', '🥭', '🍍', '🥥', '🥝', '🍅', '🍆', '🥑', '🥦',
      '🥬', '🥒', '🌶️', '🫑', '🌽', '🥕', '🫒', '🧄', '🧅', '🥔',
      '🍠', '🥐', '🍞', '🥖', '🥨', '🧀', '🥚', '🍳', '�', '�'
    ]
  },
  actividades: {
    icon: '⚽',
    label: 'Actividades',
    emojis: [
      '⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🥏', '🎱',
      '🪀', '🏓', '🏸', '🏒', '🏑', '🥍', '🏏', '🪃', '🥅', '⛳',
      '🪁', '🏹', '🎣', '🤿', '🥊', '🥋', '🎽', '🛹', '🛼', '🛷'
    ]
  },
  objetos: {
    icon: '💎',
    label: 'Objetos',
    emojis: [
      '⌚', '📱', '📲', '💻', '⌨️', '🖥️', '🖨️', '🖱️', '🖲️', '🕹️',
      '🗜️', '💽', '💾', '💿', '📀', '📼', '📷', '📸', '📹', '🎥',
      '📽️', '🎞️', '📞', '☎️', '📟', '📠', '📺', '📻', '🎙️', '🎚️'
    ]
  },
  simbolos: {
    icon: '❤️',
    label: 'Símbolos',
    emojis: [
      '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔',
      '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '☮️',
      '✝️', '☪️', '🕉️', '☸️', '✡️', '🔯', '🕎', '☯️', '☦️', '🛐',
      '🔥', '💯', '💫', '⭐', '🌟', '✨', '⚡', '💥', '💢', '💨'
    ]
  }
};

const POSITION_CLASSES = {
  top: 'bottom-full mb-2',
  bottom: 'top-full mt-2',
  left: 'right-full mr-2',
  right: 'left-full ml-2',
};

export const EmojiPicker = memo<EmojiPickerProps>(({
  onEmojiSelect,
  isOpen,
  onClose,
  position = 'bottom',
  className = '',
  recentEmojis,
}) => {
  const [activeCategory, setActiveCategory] = useState('frecuentes');
  const [searchTerm, setSearchTerm] = useState('');
  const pickerRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  useClickOutside(pickerRef, onClose, isOpen);
  useKeyPress('Escape', onClose, { enabled: isOpen });
  
  const debouncedSearch = useDebounce(searchTerm, 200);

  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  const filteredEmojis = useMemo(() => {
    if (debouncedSearch) {
      return Object.values(EMOJI_CATEGORIES)
        .flatMap((cat: EmojiCategory) => cat.emojis)
        .filter((emoji: string) => emoji.includes(debouncedSearch.toLowerCase()));
    }
    
    const category = EMOJI_CATEGORIES[activeCategory];
    if (activeCategory === 'frecuentes' && recentEmojis) {
      return recentEmojis;
    }
    
    return category?.emojis || [];
  }, [debouncedSearch, activeCategory, recentEmojis]);

  const handleEmojiClick = useCallback((emoji: string) => {
    onEmojiSelect(emoji);
    onClose();
  }, [onEmojiSelect, onClose]);

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
        <div className="p-4 bg-gradient-to-r from-primary-600 to-secondary-600 text-white">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-lg">Emojis</h3>
            <button
              onClick={onClose}
              className="p-1 hover:bg-white/20 rounded-lg transition-colors"
              aria-label="Cerrar"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Buscar emojis..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="
              w-full px-4 py-2 text-sm rounded-xl
              bg-white/20 backdrop-blur-sm
              border-0 placeholder-white/70 text-white
              focus:outline-none focus:ring-2 focus:ring-white/40
            "
          />
        </div>

        <div className="flex h-[calc(100%-120px)]">
          {!debouncedSearch && (
            <div className="w-16 bg-neutral-50 dark:bg-neutral-800 border-r border-neutral-200 dark:border-neutral-700 overflow-y-auto scrollbar-thin">
              {Object.entries(EMOJI_CATEGORIES).map(([key, cat]) => (
                <motion.button
                  key={key}
                  onClick={() => setActiveCategory(key)}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className={`
                    w-full p-3 text-xl transition-colors
                    ${activeCategory === key 
                      ? 'bg-primary-100 dark:bg-primary-900/50 border-r-2 border-primary-600' 
                      : 'hover:bg-neutral-100 dark:hover:bg-neutral-700'
                    }
                  `}
                  title={cat.label}
                  aria-label={cat.label}
                >
                  {cat.icon}
                </motion.button>
              ))}
            </div>
          )}

          <div className="flex-1 p-4 overflow-y-auto scrollbar-thin">
            {debouncedSearch && (
              <div className="mb-3 text-sm text-neutral-600 dark:text-neutral-400 font-medium">
                {filteredEmojis.length} resultados
              </div>
            )}
            
            <div className="grid grid-cols-8 gap-2">
              {filteredEmojis.map((emoji: string, index: number) => (
                <motion.button
                  key={`${emoji}-${index}`}
                  onClick={() => handleEmojiClick(emoji)}
                  whileHover={{ scale: 1.3, rotate: 5 }}
                  whileTap={{ scale: 0.9 }}
                  className="
                    w-8 h-8 flex items-center justify-center text-2xl
                    hover:bg-neutral-100 dark:hover:bg-neutral-800 
                    rounded-lg transition-colors
                  "
                  title={emoji}
                  aria-label={`Seleccionar emoji ${emoji}`}
                >
                  {emoji}
                </motion.button>
              ))}
            </div>

            {filteredEmojis.length === 0 && debouncedSearch && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-12 text-neutral-500 dark:text-neutral-400"
              >
                <div className="text-4xl mb-3">😕</div>
                <div className="font-medium">No se encontraron emojis</div>
              </motion.div>
            )}
          </div>
        </div>

        <div className="p-2 bg-neutral-100 dark:bg-neutral-800 border-t border-neutral-200 dark:border-neutral-700">
          <div className="text-xs text-neutral-500 dark:text-neutral-400 text-center">
            Haz clic en un emoji para agregarlo
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
});

EmojiPicker.displayName = 'EmojiPicker';

export default EmojiPicker;