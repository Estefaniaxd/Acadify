/**
 * Pagination Component
 * Sistema de paginación con ellipsis inteligente
 * Sigue principios SOLID y mejores prácticas de accesibilidad
 */

import React, { useMemo, memo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, MoreHorizontal } from 'lucide-react';
;

/* ============================================
   TYPES & INTERFACES
   ============================================ */

export type PaginationSize = 'sm' | 'md' | 'lg';

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  size?: PaginationSize;
  showFirstLast?: boolean; // Mostrar botones primera/última
  showPageInfo?: boolean; // Mostrar "Página X de Y"
  siblingCount?: number; // Cantidad de páginas a mostrar alrededor de la actual
  className?: string;
  disabled?: boolean;
  // Para mostrar info de items
  totalItems?: number;
  itemsPerPage?: number;
  itemLabel?: string; // e.g., "resultados", "productos"
}

/* ============================================
   CONFIGURATION
   ============================================ */

const SIZE_STYLES: Record<PaginationSize, {
  button: string;
  text: string;
}> = {
  sm: {
    button: 'w-8 h-8 text-xs',
    text: 'text-xs'
  },
  md: {
    button: 'w-10 h-10 text-sm',
    text: 'text-sm'
  },
  lg: {
    button: 'w-12 h-12 text-base',
    text: 'text-base'
  }
};

/* ============================================
   HELPER FUNCTIONS
   ============================================ */

/**
 * Genera array de números de página con ellipsis
 * Ejemplo: [1, "...", 5, 6, 7, "...", 10]
 */
const generatePageNumbers = (
  currentPage: number,
  totalPages: number,
  siblingCount: number
): (number | string)[] => {
  const totalPageNumbers = siblingCount + 5;

  if (totalPages <= totalPageNumbers) {
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  }

  const leftSiblingIndex = Math.max(currentPage - siblingCount, 1);
  const rightSiblingIndex = Math.min(currentPage + siblingCount, totalPages);

  const shouldShowLeftEllipsis = leftSiblingIndex > 2;
  const shouldShowRightEllipsis = rightSiblingIndex < totalPages - 1;

  if (!shouldShowLeftEllipsis && shouldShowRightEllipsis) {
    const leftItemCount = 3 + 2 * siblingCount;
    const leftRange = Array.from({ length: leftItemCount }, (_, i) => i + 1);
    return [...leftRange, '...', totalPages];
  }

  if (shouldShowLeftEllipsis && !shouldShowRightEllipsis) {
    const rightItemCount = 3 + 2 * siblingCount;
    const rightRange = Array.from(
      { length: rightItemCount },
      (_, i) => totalPages - rightItemCount + i + 1
    );
    return [1, '...', ...rightRange];
  }

  if (shouldShowLeftEllipsis && shouldShowRightEllipsis) {
    const middleRange = Array.from(
      { length: rightSiblingIndex - leftSiblingIndex + 1 },
      (_, i) => leftSiblingIndex + i
    );
    return [1, '...', ...middleRange, '...', totalPages];
  }

  return [];
};

/* ============================================
   SUB-COMPONENTS
   ============================================ */

interface PageButtonProps {
  page: number | string;
  isActive?: boolean;
  onClick?: () => void;
  disabled?: boolean;
  size: PaginationSize;
}

const PageButton = memo<PageButtonProps>(({ 
  page, 
  isActive, 
  onClick, 
  disabled,
  size 
}) => {
  const sizeClass = SIZE_STYLES[size].button;
  const isEllipsis = page === '...';

  if (isEllipsis) {
    return (
      <div className={`${sizeClass} flex items-center justify-center text-neutral-400 dark:text-neutral-600`}>
        <MoreHorizontal className="w-5 h-5" />
      </div>
    );
  }

  return (
    <motion.button
      onClick={onClick}
      disabled={disabled || isActive}
      whileHover={!disabled && !isActive ? { scale: 1.05 } : {}}
      whileTap={!disabled && !isActive ? { scale: 0.95 } : {}}
      className={`
        ${sizeClass}
        flex items-center justify-center rounded-lg font-semibold
        transition-all duration-200
        focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-900
        ${isActive
          ? 'bg-gradient-to-r from-violet-600 to-purple-600 dark:from-violet-500 dark:to-purple-500 text-white shadow-lg shadow-violet-500/30 cursor-default'
          : disabled
            ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-400 dark:text-neutral-600 cursor-not-allowed'
            : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-violet-50 dark:hover:bg-violet-950/30 hover:text-violet-600 dark:hover:text-violet-400 border-2 border-neutral-200 dark:border-neutral-700 hover:border-violet-200 dark:hover:border-violet-800'
        }
      `}
      aria-label={`Página ${page}`}
      aria-current={isActive ? 'page' : undefined}
    >
      {page}
    </motion.button>
  );
});

PageButton.displayName = 'PageButton';

/* ============================================
   MAIN COMPONENT
   ============================================ */

export const Pagination = memo<PaginationProps>(({
  currentPage,
  totalPages,
  onPageChange,
  size = 'md',
  showFirstLast = true,
  showPageInfo = false,
  siblingCount = 1,
  className = '',
  disabled = false,
  totalItems,
  itemsPerPage,
  itemLabel = 'items'
}) => {
  const sizeClass = SIZE_STYLES[size];

  const pageNumbers = useMemo(
    () => generatePageNumbers(currentPage, totalPages, siblingCount),
    [currentPage, totalPages, siblingCount]
  );

  const handlePageChange = useCallback((page: number) => {
    if (page < 1 || page > totalPages || page === currentPage || disabled) return;
    onPageChange(page);
  }, [currentPage, totalPages, onPageChange, disabled]);

  // Calcular info de items
  const itemInfo = useMemo(() => {
    if (!totalItems || !itemsPerPage) return null;
    const start = (currentPage - 1) * itemsPerPage + 1;
    const end = Math.min(currentPage * itemsPerPage, totalItems);
    return { start, end };
  }, [totalItems, itemsPerPage, currentPage]);

  const isFirstPage = currentPage === 1;
  const isLastPage = currentPage === totalPages;

  return (
    <nav
      className={`flex flex-col sm:flex-row items-center justify-between gap-4 ${className}`}
      aria-label="Paginación"
    >
      {/* Items Info */}
      {itemInfo && (
        <div className={`${sizeClass.text} text-neutral-600 dark:text-neutral-400 font-medium`}>
          Mostrando <span className="font-bold text-neutral-900 dark:text-neutral-100">{itemInfo.start}</span> a{' '}
          <span className="font-bold text-neutral-900 dark:text-neutral-100">{itemInfo.end}</span> de{' '}
          <span className="font-bold text-neutral-900 dark:text-neutral-100">{totalItems}</span> {itemLabel}
        </div>
      )}

      {/* Page Info */}
      {showPageInfo && !itemInfo && (
        <div className={`${sizeClass.text} text-neutral-600 dark:text-neutral-400 font-medium`}>
          Página <span className="font-bold text-neutral-900 dark:text-neutral-100">{currentPage}</span> de{' '}
          <span className="font-bold text-neutral-900 dark:text-neutral-100">{totalPages}</span>
        </div>
      )}

      {/* Pagination Controls */}
      <div className="flex items-center gap-1">
        {/* First Page */}
        {showFirstLast && (
          <motion.button
            onClick={() => handlePageChange(1)}
            disabled={disabled || isFirstPage}
            whileHover={!disabled && !isFirstPage ? { scale: 1.05 } : {}}
            whileTap={!disabled && !isFirstPage ? { scale: 0.95 } : {}}
            className={`
              ${sizeClass.button}
              flex items-center justify-center rounded-lg
              transition-all duration-200
              focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-900
              ${disabled || isFirstPage
                ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-400 dark:text-neutral-600 cursor-not-allowed'
                : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-violet-50 dark:hover:bg-violet-950/30 hover:text-violet-600 dark:hover:text-violet-400 border-2 border-neutral-200 dark:border-neutral-700 hover:border-violet-200 dark:hover:border-violet-800'
              }
            `}
            aria-label="Primera página"
          >
            <ChevronsLeft className="w-5 h-5" />
          </motion.button>
        )}

        {/* Previous Page */}
        <motion.button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={disabled || isFirstPage}
          whileHover={!disabled && !isFirstPage ? { scale: 1.05 } : {}}
          whileTap={!disabled && !isFirstPage ? { scale: 0.95 } : {}}
          className={`
            ${sizeClass.button}
            flex items-center justify-center rounded-lg
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-900
            ${disabled || isFirstPage
              ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-400 dark:text-neutral-600 cursor-not-allowed'
              : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-violet-50 dark:hover:bg-violet-950/30 hover:text-violet-600 dark:hover:text-violet-400 border-2 border-neutral-200 dark:border-neutral-700 hover:border-violet-200 dark:hover:border-violet-800'
            }
          `}
          aria-label="Página anterior"
        >
          <ChevronLeft className="w-5 h-5" />
        </motion.button>

        {/* Page Numbers */}
        <div className="flex items-center gap-1">
          {pageNumbers.map((page, index) => (
            <PageButton
              key={`${page}-${index}`}
              page={page}
              isActive={page === currentPage}
              onClick={() => typeof page === 'number' && handlePageChange(page)}
              disabled={disabled}
              size={size}
            />
          ))}
        </div>

        {/* Next Page */}
        <motion.button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={disabled || isLastPage}
          whileHover={!disabled && !isLastPage ? { scale: 1.05 } : {}}
          whileTap={!disabled && !isLastPage ? { scale: 0.95 } : {}}
          className={`
            ${sizeClass.button}
            flex items-center justify-center rounded-lg
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-900
            ${disabled || isLastPage
              ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-400 dark:text-neutral-600 cursor-not-allowed'
              : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-violet-50 dark:hover:bg-violet-950/30 hover:text-violet-600 dark:hover:text-violet-400 border-2 border-neutral-200 dark:border-neutral-700 hover:border-violet-200 dark:hover:border-violet-800'
            }
          `}
          aria-label="Página siguiente"
        >
          <ChevronRight className="w-5 h-5" />
        </motion.button>

        {/* Last Page */}
        {showFirstLast && (
          <motion.button
            onClick={() => handlePageChange(totalPages)}
            disabled={disabled || isLastPage}
            whileHover={!disabled && !isLastPage ? { scale: 1.05 } : {}}
            whileTap={!disabled && !isLastPage ? { scale: 0.95 } : {}}
            className={`
              ${sizeClass.button}
              flex items-center justify-center rounded-lg
              transition-all duration-200
              focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-900
              ${disabled || isLastPage
                ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-400 dark:text-neutral-600 cursor-not-allowed'
                : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-violet-50 dark:hover:bg-violet-950/30 hover:text-violet-600 dark:hover:text-violet-400 border-2 border-neutral-200 dark:border-neutral-700 hover:border-violet-200 dark:hover:border-violet-800'
              }
            `}
            aria-label="Última página"
          >
            <ChevronsRight className="w-5 h-5" />
          </motion.button>
        )}
      </div>
    </nav>
  );
});

Pagination.displayName = 'Pagination';

export default Pagination;
