/**
 * Punto de entrada principal del módulo de Invitaciones
 * Exporta tipos, servicios, hooks y componentes
 */

// Tipos
export * from './types';

// Servicios
export { default as invitacionService } from './services/invitacionService';

// Hooks
export {
  // Query keys
  invitacionesKeys,
  
  // Queries
  useInvitaciones,
  useInvitacion,
  useValidarToken,
  useEstadisticasInvitaciones,
  useHistorialInvitacion,
  useNotificacionesInvitacion,
  useInvitacionesPorInstitucion,
  
  // Mutations
  useCrearInvitacion,
  useReenviarInvitacion,
  useCancelarInvitacion,
  useAceptarInvitacion,
  useRechazarInvitacion,
  useMarcarNotificacionLeida,
  
  // Combinados
  useInvitacionOperations,
  
  // Helpers
  usePrefetchInvitacion,
  useInvalidateInvitaciones,
} from './hooks/useInvitaciones';

// Componentes
export { default as FormularioInvitacion } from './components/FormularioInvitacion';
export { default as ListaInvitaciones } from './components/ListaInvitaciones';
export { default as AceptarInvitacion } from './components/AceptarInvitacion';
export { default as NotificationCenter } from './components/NotificationCenter';

// Páginas
export { RegistroCoordinadorPage } from '../../pages/invitaciones/RegistroCoordinadorPage';
