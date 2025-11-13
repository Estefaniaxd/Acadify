import { HTMLAttributes } from 'react';

/* ==========================================================================
   💀 SKELETON COMPONENT
   Skeleton loader para estados de carga
   ========================================================================== */

export interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  /** Ancho del skeleton (CSS value) */
  width?: string | number;
  
  /** Alto del skeleton (CSS value) */
  height?: string | number;
  
  /** Forma del skeleton */
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
  
  /** Número de líneas (para variant="text") */
  lines?: number;
  
  /** Animar el skeleton */
  animated?: boolean;
}

/**
 * Obtener clases según variante
 */
const getVariantClasses = (variant: NonNullable<SkeletonProps['variant']>): string => {
  const variants = {
    text: 'rounded h-4',
    circular: 'rounded-full',
    rectangular: 'rounded-none',
    rounded: 'rounded-lg',
  };
  
  return variants[variant];
};

/**
 * Skeleton Component
 * 
 * Placeholder animado para estados de carga con:
 * - 4 variantes de forma
 * - Tamaño personalizable
 * - Animación pulsante
 * - Soporte para múltiples líneas
 * 
 * @example
 * ```tsx
 * // Texto simple
 * <Skeleton variant="text" width="200px" />
 * 
 * // Avatar circular
 * <Skeleton variant="circular" width={40} height={40} />
 * 
 * // Card completo
 * <Skeleton variant="rounded" width="100%" height={200} />
 * 
 * // Múltiples líneas de texto
 * <Skeleton variant="text" lines={3} />
 * ```
 */
export const Skeleton: React.FC<SkeletonProps> = ({
  width,
  height,
  variant = 'text',
  lines = 1,
  animated = true,
  className = '',
  style,
  ...props
}) => {
  const variantClasses = getVariantClasses(variant);
  
  const baseClasses = [
    'bg-neutral-200 dark:bg-neutral-800',
    animated && 'animate-pulse',
    variantClasses,
    className,
  ]
    .filter(Boolean)
    .join(' ');
  
  const skeletonStyle = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
    ...style,
  };
  
  // Si es texto con múltiples líneas
  if (variant === 'text' && lines > 1) {
    return (
      <div className="space-y-2" {...props}>
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={baseClasses}
            style={{
              ...skeletonStyle,
              // Última línea más corta
              width: index === lines - 1 ? '80%' : skeletonStyle.width,
            }}
          />
        ))}
      </div>
    );
  }
  
  // Skeleton simple
  return (
    <div
      className={baseClasses}
      style={skeletonStyle}
      {...props}
    />
  );
};

/**
 * SkeletonCard - Card skeleton predefinido
 */
export const SkeletonCard: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`space-y-4 ${className}`}>
    <Skeleton variant="rectangular" width="100%" height={200} />
    <Skeleton variant="text" width="60%" />
    <Skeleton variant="text" lines={2} />
  </div>
);

/**
 * SkeletonAvatar - Avatar skeleton con texto
 */
export const SkeletonAvatar: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`flex items-center gap-3 ${className}`}>
    <Skeleton variant="circular" width={40} height={40} />
    <div className="flex-1 space-y-2">
      <Skeleton variant="text" width="40%" />
      <Skeleton variant="text" width="60%" />
    </div>
  </div>
);

/**
 * SkeletonList - Lista de skeletons
 */
export const SkeletonList: React.FC<{ count?: number; className?: string }> = ({
  count = 3,
  className = '',
}) => (
  <div className={`space-y-4 ${className}`}>
    {Array.from({ length: count }).map((_, index) => (
      <SkeletonAvatar key={index} />
    ))}
  </div>
);

Skeleton.displayName = 'Skeleton';

export default Skeleton;
