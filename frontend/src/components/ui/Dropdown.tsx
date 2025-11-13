/**
 * Dropdown/Menu Component
 * Menú desplegable con submenus, dividers y posicionamiento inteligente
 * Sigue principios SOLID y mejores prácticas de accesibilidad
 */

import React, { useState, useRef, useCallback, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
;
import type { IconType } from 'react-icons';
import { useClickOutside } from '../../hooks/useClickOutside';
import { useKeyPress } from '../../hooks/useKeyPress';
import { Check, ChevronRight } from 'lucide-react';

/* ============================================
   TYPES & INTERFACES
   ============================================ */

export type MenuItemType = 'item' | 'divider' | 'header';
export type MenuPlacement = 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end' | 'right-start' | 'left-start';

export interface MenuItem {
  id: string;
  type?: MenuItemType;
  label?: string;
  icon?: IconType;
  shortcut?: string;
  onClick?: () => void;
  disabled?: boolean;
  danger?: boolean; // Para acciones destructivas (rojo)
  selected?: boolean; // Para mostrar checkmark
  items?: MenuItem[]; // Submenu items
}

export interface DropdownProps {
  trigger: React.ReactNode;
  items: MenuItem[];
  placement?: MenuPlacement;
  className?: string;
  menuClassName?: string;
  closeOnSelect?: boolean;
  disabled?: boolean;
}

/* ============================================
   CONFIGURATION
   ============================================ */

const PLACEMENT_STYLES: Record<MenuPlacement, string> = {
  'bottom-start': 'top-full left-0 mt-2',
  'bottom-end': 'top-full right-0 mt-2',
  'top-start': 'bottom-full left-0 mb-2',
  'top-end': 'bottom-full right-0 mb-2',
  'right-start': 'left-full top-0 ml-2',
  'left-start': 'right-full top-0 mr-2'
};

const ANIMATION_VARIANTS = {
  menu: {
    hidden: { 
      opacity: 0, 
      scale: 0.95,
      y: -10 
    },
    visible: { 
      opacity: 1, 
      scale: 1,
      y: 0,
      transition: {
        duration: 0.15,
        ease: [0.23, 1, 0.32, 1]
      }
    },
    exit: { 
      opacity: 0, 
      scale: 0.95,
      y: -10,
      transition: {
        duration: 0.1
      }
    }
  },
  submenu: {
    hidden: { 
      opacity: 0, 
      x: -10 
    },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: {
        duration: 0.15
      }
    },
    exit: { 
      opacity: 0, 
      x: -10,
      transition: {
        duration: 0.1
      }
    }
  }
};

/* ============================================
   SUB-COMPONENTS
   ============================================ */

interface MenuItemComponentProps {
  item: MenuItem;
  onClose: () => void;
  closeOnSelect: boolean;
  level?: number;
}

const MenuItemComponent = memo<MenuItemComponentProps>(({ 
  item, 
  onClose, 
  closeOnSelect,
  level = 0 
}) => {
  const [showSubmenu, setShowSubmenu] = useState(false);
  const hasSubmenu = item.items && item.items.length > 0;

  const handleClick = useCallback(() => {
    if (item.disabled) return;
    
    if (hasSubmenu) {
      setShowSubmenu(!showSubmenu);
    } else {
      item.onClick?.();
      if (closeOnSelect) {
        onClose();
      }
    }
  }, [item, hasSubmenu, showSubmenu, closeOnSelect, onClose]);

  if (item.type === 'divider') {
    return (
      <div className="my-1 h-px bg-neutral-200 dark:bg-neutral-700" role="separator" />
    );
  }

  if (item.type === 'header') {
    return (
      <div className="px-3 py-2 text-xs font-semibold text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
        {item.label}
      </div>
    );
  }

  const Icon = item.icon;

  return (
    <div className="relative">
      <motion.button
        onClick={handleClick}
        onMouseEnter={() => hasSubmenu && setShowSubmenu(true)}
        onMouseLeave={() => hasSubmenu && setShowSubmenu(false)}
        disabled={item.disabled}
        whileHover={!item.disabled ? { x: 2 } : {}}
        className={`
          w-full flex items-center gap-3 px-3 py-2 rounded-lg
          text-sm font-medium text-left
          transition-all duration-150
          ${item.disabled
            ? 'opacity-50 cursor-not-allowed'
            : item.danger
              ? 'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30'
              : 'text-neutral-700 dark:text-neutral-300 hover:bg-violet-50 dark:hover:bg-violet-950/30 hover:text-violet-600 dark:hover:text-violet-400'
          }
          focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-900
        `}
      >
        {/* Icon */}
        {Icon && (
          <Icon className="w-4 h-4 flex-shrink-0" />
        )}

        {/* Selected Check */}
        {item.selected && (
          <Check className="w-4 h-4 flex-shrink-0 text-violet-600 dark:text-violet-400" />
        )}

        {/* Label */}
        <span className="flex-1">{item.label}</span>

        {/* Shortcut */}
        {item.shortcut && (
          <kbd className="px-2 py-0.5 text-xs rounded bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 font-mono">
            {item.shortcut}
          </kbd>
        )}

        {/* Submenu Indicator */}
        {hasSubmenu && (
          <ChevronRight className="w-4 h-4 flex-shrink-0" />
        )}
      </motion.button>

      {/* Submenu */}
      {hasSubmenu && (
        <AnimatePresence>
          {showSubmenu && (
            <motion.div
              variants={ANIMATION_VARIANTS.submenu}
              initial="hidden"
              animate="visible"
              exit="exit"
              className="absolute left-full top-0 ml-1 min-w-[200px] z-50"
              onMouseEnter={() => setShowSubmenu(true)}
              onMouseLeave={() => setShowSubmenu(false)}
            >
              <div className="p-1 rounded-xl shadow-xl border-2 border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 backdrop-blur-xl">
                {item.items!.map((subItem) => (
                  <MenuItemComponent
                    key={subItem.id}
                    item={subItem}
                    onClose={onClose}
                    closeOnSelect={closeOnSelect}
                    level={level + 1}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      )}
    </div>
  );
});

MenuItemComponent.displayName = 'MenuItemComponent';

/* ============================================
   MAIN COMPONENT
   ============================================ */

export const Dropdown = memo<DropdownProps>(({
  trigger,
  items,
  placement = 'bottom-start',
  className = '',
  menuClassName = '',
  closeOnSelect = true,
  disabled = false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleClose = useCallback(() => {
    setIsOpen(false);
  }, []);

  const handleToggle = useCallback(() => {
    if (!disabled) {
      setIsOpen(prev => !prev);
    }
  }, [disabled]);

  useClickOutside(containerRef, handleClose);
  useKeyPress('Escape', handleClose);

  const placementClass = PLACEMENT_STYLES[placement];

  return (
    <div ref={containerRef} className={`relative inline-block ${className}`}>
      {/* Trigger */}
      <div onClick={handleToggle} className={disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}>
        {trigger}
      </div>

      {/* Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            variants={ANIMATION_VARIANTS.menu}
            initial="hidden"
            animate="visible"
            exit="exit"
            className={`
              absolute ${placementClass} min-w-[220px] z-50
              ${menuClassName}
            `}
          >
            <div className="p-1 rounded-xl shadow-2xl border-2 border-neutral-200 dark:border-neutral-700 bg-white/95 dark:bg-neutral-900/95 backdrop-blur-xl">
              {items.map((item) => (
                <MenuItemComponent
                  key={item.id}
                  item={item}
                  onClose={handleClose}
                  closeOnSelect={closeOnSelect}
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});

Dropdown.displayName = 'Dropdown';

export default Dropdown;
