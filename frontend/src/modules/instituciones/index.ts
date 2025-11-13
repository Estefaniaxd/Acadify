/**
 * Archivo de exportación principal del módulo Instituciones
 * Facilita las importaciones desde otros módulos
 */

// Components
export { ListaInstituciones } from './components/ListaInstituciones';
export { FormularioInstitucion } from './components/FormularioInstitucion';
export { InvitarCoordinadorModal } from './components/InvitarCoordinadorModal';

// Hooks
export {
  useInstituciones,
  useInstitucion,
  useEstadisticasInstitucion,
  useBuscarInstituciones,
  useCrearInstitucion,
  useActualizarInstitucion,
  useEliminarInstitucion,
  useToggleActivoInstitucion,
  useActualizarPersonalizacion,
  useSubirLogo,
  useInstitucionOperations,
  INSTITUCIONES_KEYS,
} from './hooks/useInstituciones';

// Services
export { institucionService } from './services/institucionService';
export { adminInstitucionService } from './services/adminInstitucionService';
export { coordinadorInstitucionService } from './services/coordinadorInstitucionService';

// Types
export type {
  Institucion,
  CrearInstitucionDTO,
  ActualizarInstitucionDTO,
  PersonalizacionInstitucion,
  Coordinador,
  ProgramaBasico,
  EstadisticasInstitucion,
  FiltrosInstitucion,
  RespuestaPaginada,
  InvitacionInfo,
  InvitarCoordinadorRequest,
  InvitarCoordinadorResponse,
  AceptarInvitacionRequest,
  AceptarInvitacionResponse,
  EstadisticasDetalladas,
  OnboardingStatus,
} from './types';

// Enums
export {
  TipoInstitucion,
  NivelEducativo,
  SectorInstitucion,
  ModalidadEnsenanza,
  TipoCalendario,
  EstadoInstitucion,
} from './types';
