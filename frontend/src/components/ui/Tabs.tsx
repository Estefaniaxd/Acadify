/**
 * Tabs Component
 * Sistema de pestañas con navegación por teclado y animaciones
 * Sigue principios SOLID y mejores prácticas de accesibilidad
 */

import React, { useState, useRef, useEffect, useCallback, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { IconType } from 'react-icons';
import { useKeyPress } from '../../hooks/useKeyPress';

/* ============================================
   TYPES & INTERFACES
   ============================================ */

export type TabVariant = 'line' | 'enclosed' | 'pills' | 'solid';
export type TabSize = 'sm' | 'md' | 'lg';
export type TabOrientation = 'horizontal' | 'vertical';

export interface Tab {
  id: string;
  label: string;
  content: React.ReactNode;
  icon?: IconType;
  badge?: string | number;
  disabled?: boolean;
}

export interface TabsProps {
  tabs: Tab[];
  defaultTab?: string;
  variant?: TabVariant;
  size?: TabSize;
  orientation?: TabOrientation;
  onChange?: (tabId: string) => void;
  className?: string;
  tabListClassName?: string;
  tabPanelClassName?: string;
  isFitted?: boolean; // Tabs ocupan todo el ancho
  isLazy?: boolean; // Renderizar contenido solo cuando se activa
}

/* ============================================
   CONFIGURATION
   ============================================ */

const SIZE_STYLES: Record<TabSize, string> = {
  sm: 'text-sm px-3 py-2 gap-1.5',
  md: 'text-base px-4 py-2.5 gap-2',
  lg: 'text-lg px-5 py-3 gap-2.5'
};

const VARIANT_STYLES: Record<TabVariant, {
  container: string;
  tab: string;
  activeTab: string;
  inactiveTab: string;
}> = {
  line: {
    container: 'border-b-2 border-neutral-200 dark:border-neutral-700',
    tab: 'relative transition-colors duration-200',
    activeTab: 'text-violet-600 dark:text-violet-400 font-semibold',
    inactiveTab: 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-100'
  },
  enclosed: {
    container: 'border-b-2 border-neutral-200 dark:border-neutral-700',
    tab: 'rounded-t-lg border-x-2 border-t-2 border-transparent transition-all duration-200',
    activeTab: 'border-neutral-200 dark:border-neutral-700 border-b-transparent -mb-0.5 bg-white dark:bg-neutral-900 text-violet-600 dark:text-violet-400 font-semibold',
    inactiveTab: 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-100 hover:border-neutral-100 dark:hover:border-neutral-800'
  },
  pills: {
    container: 'gap-2',
    tab: 'rounded-full transition-all duration-200',
    activeTab: 'bg-violet-100 dark:bg-violet-900/50 text-violet-700 dark:text-violet-300 font-semibold shadow-sm',
    inactiveTab: 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 hover:text-neutral-900 dark:hover:text-neutral-100'
  },
  solid: {
    container: 'bg-neutral-100 dark:bg-neutral-800 rounded-lg p-1 gap-1',
    tab: 'rounded-md transition-all duration-200',
    activeTab: 'bg-white dark:bg-neutral-700 text-violet-600 dark:text-violet-400 font-semibold shadow-sm',
    inactiveTab: 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-100'
  }
};

/* ============================================
   MAIN COMPONENT
   ============================================ */

export const Tabs = memo<TabsProps>(({
  tabs,
  defaultTab,
  variant = 'line',
  size = 'md',
  orientation = 'horizontal',
  onChange,
  className = '',
  tabListClassName = '',
  tabPanelClassName = '',
  isFitted = false,
  isLazy = false
}) => {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);
  const [indicatorStyle, setIndicatorStyle] = useState({ left: 0, width: 0, top: 0, height: 0 });
  const tabRefs = useRef<Record<string, HTMLButtonElement | null>>({});
  const [renderedTabs, setRenderedTabs] = useState<Set<string>>(new Set([activeTab]));

  const styles = VARIANT_STYLES[variant];
  const sizeClass = SIZE_STYLES[size];
  const isVertical = orientation === 'vertical';

  // Actualizar indicador cuando cambia el tab activo
  useEffect(() => {
    const activeElement = tabRefs.current[activeTab];
    if (activeElement && variant === 'line') {
      const { offsetLeft, offsetWidth, offsetTop, offsetHeight } = activeElement;
      setIndicatorStyle({
        left: offsetLeft,
        width: offsetWidth,
        top: offsetTop,
        height: offsetHeight
      });
    }
  }, [activeTab, variant, tabs]);

  // Navegación por teclado
  const currentIndex = tabs.findIndex(tab => tab.id === activeTab);
  
  const navigateLeft = useCallback(() => {
    const enabledTabs = tabs.filter(t => !t.disabled);
    const currentEnabledIndex = enabledTabs.findIndex(t => t.id === activeTab);
    const prevIndex = currentEnabledIndex > 0 ? currentEnabledIndex - 1 : enabledTabs.length - 1;
    handleTabChange(enabledTabs[prevIndex].id);
  }, [activeTab, tabs]);

  const navigateRight = useCallback(() => {
    const enabledTabs = tabs.filter(t => !t.disabled);
    const currentEnabledIndex = enabledTabs.findIndex(t => t.id === activeTab);
    const nextIndex = currentEnabledIndex < enabledTabs.length - 1 ? currentEnabledIndex + 1 : 0;
    handleTabChange(enabledTabs[nextIndex].id);
  }, [activeTab, tabs]);

  useKeyPress('ArrowLeft', navigateLeft);
  useKeyPress('ArrowRight', navigateRight);
  useKeyPress('ArrowUp', isVertical ? navigateLeft : undefined);
  useKeyPress('ArrowDown', isVertical ? navigateRight : undefined);

  const handleTabChange = useCallback((tabId: string) => {
    const tab = tabs.find(t => t.id === tabId);
    if (tab?.disabled) return;
    
    setActiveTab(tabId);
    if (isLazy) {
      setRenderedTabs(prev => new Set([...prev, tabId]));
    }
    onChange?.(tabId);
  }, [tabs, onChange, isLazy]);

  const activeTabData = tabs.find(tab => tab.id === activeTab);

  return (
    <div 
      className={`flex ${isVertical ? 'flex-row gap-4' : 'flex-col'} ${className}`}
      role="tablist"
      aria-orientation={orientation}
    >
      {/* Tab List */}
      <div 
        className={`flex ${isVertical ? 'flex-col' : 'flex-row'} ${styles.container} ${isFitted && !isVertical ? 'w-full' : ''} ${tabListClassName}`}
      >
        {tabs.map((tab) => {
          const isActive = tab.id === activeTab;
          const Icon = tab.icon;

          return (
            <button
              key={tab.id}
              ref={(el) => (tabRefs.current[tab.id] = el)}
              role="tab"
              aria-selected={isActive}
              aria-controls={`panel-${tab.id}`}
              id={`tab-${tab.id}`}
              disabled={tab.disabled}
              onClick={() => handleTabChange(tab.id)}
              className={`
                flex items-center justify-center
                ${sizeClass}
                ${styles.tab}
                ${isActive ? styles.activeTab : styles.inactiveTab}
                ${isFitted && !isVertical ? 'flex-1' : ''}
                ${tab.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-900
              `}
            >
              {Icon && <Icon className="flex-shrink-0" />}
              <span className="whitespace-nowrap">{tab.label}</span>
              {tab.badge !== undefined && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className={`
                    inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded-full text-xs font-bold
                    ${isActive 
                      ? 'bg-violet-600 dark:bg-violet-500 text-white' 
                      : 'bg-neutral-200 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300'
                    }
                  `}
                >
                  {tab.badge}
                </motion.span>
              )}
            </button>
          );
        })}

        {/* Animated Indicator for line variant */}
        {variant === 'line' && (
          <motion.div
            className="absolute bottom-0 h-0.5 bg-gradient-to-r from-violet-600 to-purple-600 dark:from-violet-500 dark:to-purple-500 rounded-full"
            initial={false}
            animate={isVertical 
              ? { top: indicatorStyle.top, height: indicatorStyle.height, left: 'auto', right: 0, width: 3 }
              : { left: indicatorStyle.left, width: indicatorStyle.width }
            }
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          />
        )}
      </div>

      {/* Tab Panels */}
      <div className={`relative ${tabPanelClassName}`}>
        <AnimatePresence mode="wait">
          {tabs.map((tab) => {
            const isActive = tab.id === activeTab;
            const shouldRender = !isLazy || renderedTabs.has(tab.id);

            if (!shouldRender) return null;

            return (
              <motion.div
                key={tab.id}
                role="tabpanel"
                id={`panel-${tab.id}`}
                aria-labelledby={`tab-${tab.id}`}
                hidden={!isActive}
                initial={{ opacity: 0, y: 10 }}
                animate={{ 
                  opacity: isActive ? 1 : 0,
                  y: isActive ? 0 : 10,
                  display: isActive ? 'block' : 'none'
                }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="focus:outline-none"
                tabIndex={0}
              >
                {tab.content}
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
});

Tabs.displayName = 'Tabs';

export default Tabs;
