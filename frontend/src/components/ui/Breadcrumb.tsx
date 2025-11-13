/**
 * Breadcrumb Component
 * Navegación de rutas con separadores personalizables
 * Sigue principios SOLID y mejores prácticas de accesibilidad
 */

import React, { memo } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
;
import type { IconType } from 'react-icons';
import { ChevronRight, Home } from 'lucide-react';

/* ============================================
   TYPES & INTERFACES
   ============================================ */

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: IconType;
  isCurrentPage?: boolean;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  separator?: React.ReactNode;
  maxItems?: number; // Máximo de items antes de colapsar
  showHomeIcon?: boolean;
  className?: string;
  itemClassName?: string;
  separatorClassName?: string;
}

/* ============================================
   CONFIGURATION
   ============================================ */

const ANIMATION_VARIANTS = {
  container: {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05
      }
    }
  },
  item: {
    hidden: { opacity: 0, x: -10 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { duration: 0.2 }
    }
  }
};

/* ============================================
   HELPER COMPONENTS
   ============================================ */

interface BreadcrumbSeparatorProps {
  separator?: React.ReactNode;
  className?: string;
}

const BreadcrumbSeparator = memo<BreadcrumbSeparatorProps>(({ 
  separator, 
  className = '' 
}) => {
  const SeparatorIcon = typeof separator === 'function' ? separator as IconType : null;

  return (
    <span 
      className={`mx-2 text-neutral-400 dark:text-neutral-600 ${className}`}
      aria-hidden="true"
    >
      {SeparatorIcon ? (
        <SeparatorIcon className="w-4 h-4" />
      ) : separator ? (
        <>{separator}</>
      ) : (
        <ChevronRight className="w-4 h-4" />
      )}
    </span>
  );
});

BreadcrumbSeparator.displayName = 'BreadcrumbSeparator';

/* ============================================
   MAIN COMPONENT
   ============================================ */

export const Breadcrumb = memo<BreadcrumbProps>(({
  items,
  separator,
  maxItems,
  showHomeIcon = true,
  className = '',
  itemClassName = '',
  separatorClassName = ''
}) => {
  // Función para colapsar items si exceden maxItems
  const getDisplayItems = (): BreadcrumbItem[] => {
    if (!maxItems || items.length <= maxItems) {
      return items;
    }

    const firstItem = items[0];
    const lastItems = items.slice(-(maxItems - 1));
    
    return [
      firstItem,
      { label: '...', isCurrentPage: false },
      ...lastItems
    ];
  };

  const displayItems = getDisplayItems();

  return (
    <nav 
      aria-label="Breadcrumb"
      className={`flex items-center ${className}`}
    >
      <motion.ol
        variants={ANIMATION_VARIANTS.container}
        initial="hidden"
        animate="visible"
        className="flex items-center flex-wrap gap-1"
      >
        {displayItems.map((item, index) => {
          const isLast = index === displayItems.length - 1;
          const Icon = item.icon;
          const isEllipsis = item.label === '...';
          const isFirst = index === 0;

          return (
            <motion.li
              key={`${item.label}-${index}`}
              variants={ANIMATION_VARIANTS.item}
              className="flex items-center"
            >
              {/* Item Content */}
              {item.href && !item.isCurrentPage && !isEllipsis ? (
                <Link
                  to={item.href}
                  className={`
                    group flex items-center gap-1.5 px-2 py-1 rounded-md
                    text-sm font-medium transition-all duration-200
                    text-neutral-600 dark:text-neutral-400
                    hover:text-violet-600 dark:hover:text-violet-400
                    hover:bg-violet-50 dark:hover:bg-violet-950/30
                    focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-900
                    ${itemClassName}
                  `}
                >
                  {isFirst && showHomeIcon ? (
                    <Home className="w-4 h-4 group-hover:scale-110 transition-transform" />
                  ) : Icon ? (
                    <Icon className="w-4 h-4 group-hover:scale-110 transition-transform" />
                  ) : null}
                  <span className="group-hover:translate-x-0.5 transition-transform">
                    {item.label}
                  </span>
                </Link>
              ) : isEllipsis ? (
                <span className={`px-2 py-1 text-sm font-medium text-neutral-400 dark:text-neutral-600 ${itemClassName}`}>
                  {item.label}
                </span>
              ) : (
                <span
                  aria-current={item.isCurrentPage ? 'page' : undefined}
                  className={`
                    flex items-center gap-1.5 px-2 py-1 rounded-md
                    text-sm font-semibold
                    ${item.isCurrentPage 
                      ? 'text-violet-600 dark:text-violet-400 bg-violet-50 dark:bg-violet-950/30' 
                      : 'text-neutral-600 dark:text-neutral-400'
                    }
                    ${itemClassName}
                  `}
                >
                  {isFirst && showHomeIcon ? (
                    <Home className="w-4 h-4" />
                  ) : Icon ? (
                    <Icon className="w-4 h-4" />
                  ) : null}
                  <span>{item.label}</span>
                </span>
              )}

              {/* Separator */}
              {!isLast && (
                <BreadcrumbSeparator 
                  separator={separator}
                  className={separatorClassName}
                />
              )}
            </motion.li>
          );
        })}
      </motion.ol>
    </nav>
  );
});

Breadcrumb.displayName = 'Breadcrumb';

export default Breadcrumb;
