/**
 * Widgets de Gamificación - Exportaciones
 * 
 * @module components/gamificacion/widgets
 * @description Exporta todos los widgets reutilizables de gamificación
 * 
 * Uso:
 * ```tsx
 * import { PuntosWidget, RachaWidget, RankingWidget } from '@/components/gamificacion/widgets';
 * 
 * function Dashboard() {
 *   return (
 *     <>
 *       <PuntosWidget variant="compact" />
 *       <RachaWidget variant="compact" />
 *       <RankingWidget topCount={5} />
 *     </>
 *   );
 * }
 * ```
 */

export { default as PuntosWidget } from './PuntosWidget';
export { default as RachaWidget } from './RachaWidget';
export { default as RankingWidget } from './RankingWidget';
export { default as LogrosProximosWidget } from './LogrosProximosWidget';
export { default as EstadisticasWidget } from './EstadisticasWidget';
