import React, { memo, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Calendar,
  Clock,
  User,
  Star,
  FileText,
  Target,
  CheckCircle,
  AlertCircle,
  BookOpen,
  Award,
  MessageSquare,
  Upload,
  Eye,
  X
} from 'lucide-react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Badge, BadgeVariant } from '../ui/Badge';
import { Card } from '../ui/Card';

/* ==========================================================================
   📋 TAREA PREVIEW MODAL
   Modal profesional para mostrar detalles completos de tarea con navegación
   
   Características:
   - Vista completa de todos los metadatos de la tarea
   - Información del profesor y criterios de evaluación
   - Estado de entregas (para profesores)
   - Botón de navegación a página de entrega (estudiantes)
   - Diseño responsive y accesible
   ========================================================================== */

export interface TareaPreviewModalProps {
  /** Si el modal está abierto */
  isOpen: boolean;

  /** Callback al cerrar */
  onClose: () => void;

  /** Datos completos de la tarea */
  tarea: {
    // IDs
    id?: string;
    tarea_id?: string;

    // Información básica
    titulo?: string;
    descripcion?: string;
    instrucciones?: string;

    // Fechas
    fecha_asignacion?: string;
    fecha_limite?: string;
    fecha_inicio_disponible?: string;

    // Clasificación
    tipo?: string;
    prioridad?: 'baja' | 'media' | 'alta' | 'urgente';
    categoria?: string;
    tags?: string[];

    // Configuración de entrega
    permite_entrega_tardia?: boolean;
    permite_entregas_tardias?: boolean;
    penalizacion_tardia?: number;
    intentos_maximos?: number;
    formato_entrega?: string;
    tamano_maximo_mb?: number;
    restricciones_archivo?: any;

    // Evaluación
    puntuacion_maxima?: number;
    peso_evaluacion?: number;
    peso_calificacion?: number;
    rubrica_id?: string;
    rubrica?: any;
    criterios_evaluacion?: string;

    // Gamificación
    puntos_base?: number;
    puntos_bonificacion?: number;

    // IA
    habilitar_retroalimentacion_ia?: boolean;
    prompt_ia_personalizado?: string;

    // Estado y visibilidad
    estado?: string;
    visible_estudiantes?: boolean;
    requiere_confirmacion_lectura?: boolean;

    // Relaciones
    docente_id?: string;
    docente_nombre?: string;
    docente_email?: string;
    grupo_id?: string;
    clase_id?: string;

    // Información adicional
    tiempo_estimado?: number;
    objetivos?: string;
    recursos_necesarios?: string;
    archivo_adjunto?: string;

    // Entregas (solo para profesores)
    entregas?: any[];
    total_entregas?: number;
    entregas_pendientes?: number;
    entregas_calificadas?: number;
    promedio_calificaciones?: number;
    esta_vencida?: boolean;

    // Campos calculados
    _datosCompletos?: boolean;
  };

  /** ID de la entrega seleccionada (opcional) */
  entregaId?: string;

  /** Si el usuario actual es estudiante */
  isStudentUser?: boolean;

  /** ID del curso */
  cursoId?: string;
}

/**
 * Formatea fecha para display amigable
 */
const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return 'No especificada';

  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateString;
  }
};

/**
 * Calcula días restantes hasta fecha límite
 */
const getDaysUntilDeadline = (deadlineString: string | undefined): number | null => {
  if (!deadlineString) return null;

  try {
    const deadline = new Date(deadlineString);
    const now = new Date();
    const diffTime = deadline.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  } catch {
    return null;
  }
};

/**
 * Obtiene color y texto para prioridad
 */
const getPriorityInfo = (prioridad: string | undefined): { color: BadgeVariant; text: string; icon: any } => {
  switch (prioridad?.toLowerCase()) {
    case 'urgente':
      return { color: 'danger', text: 'Urgente', icon: AlertCircle };
    case 'alta':
      return { color: 'danger', text: 'Alta', icon: AlertCircle };
    case 'media':
      return { color: 'warning', text: 'Media', icon: Clock };
    case 'baja':
      return { color: 'success', text: 'Baja', icon: CheckCircle };
    default:
      return { color: 'default', text: 'Normal', icon: CheckCircle };
  }
};

/**
 * Componente principal del modal
 */
export const TareaPreviewModal: React.FC<TareaPreviewModalProps> = memo(({
  isOpen,
  onClose,
  tarea,
  entregaId,
  isStudentUser = true,
  cursoId
}) => {
  const navigate = useNavigate();
  const [fullTaskData, setFullTaskData] = useState(tarea);
  const [isLoading, setIsLoading] = useState(false);

  // Cargar datos completos de la tarea cuando el modal abre
  useEffect(() => {
    if (!isOpen || !cursoId || !fullTaskData.id && !fullTaskData.tarea_id) {
      return;
    }

    const tareaId = fullTaskData.tarea_id || fullTaskData.id;
    
    // Si ya tenemos muchos datos, no cargar de nuevo
    if (fullTaskData.descripcion && fullTaskData.criterios_evaluacion) {
      setFullTaskData(tarea);
      return;
    }

    setIsLoading(true);
    
    // Intentar cargar datos completos del API
    const loadTaskData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          setFullTaskData(tarea);
          setIsLoading(false);
          return;
        }

        // Intentar obtener la tarea completa desde el API
        const response = await fetch(`http://localhost:8000/api/cursos/${cursoId}/tareas/${tareaId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          console.log('✅ Datos completos de tarea cargados:', data);
          setFullTaskData(data.data || data);
        } else {
          console.warn('⚠️ No se pudieron cargar datos completos, usando datos parciales');
          setFullTaskData(tarea);
        }
      } catch (error) {
        console.error('❌ Error cargando datos completos de tarea:', error);
        setFullTaskData(tarea);
      } finally {
        setIsLoading(false);
      }
    };

    loadTaskData();
  }, [isOpen, cursoId, tarea]);

  // Extraer ID de la tarea (fallback chain)
  const tareaId = fullTaskData.tarea_id || fullTaskData.id;

  // Calcular días hasta deadline
  const daysUntilDeadline = getDaysUntilDeadline(fullTaskData.fecha_limite);

  // Información de prioridad
  const priorityInfo = getPriorityInfo(fullTaskData.prioridad);

  /**
   * Handler para navegación a página de entrega
   */
  const handleEntregarTarea = () => {
    console.log('🎯 handleEntregarTarea called');
    console.log('📋 tarea object:', tarea);
    console.log('🆔 fullTaskData.tarea_id:', fullTaskData.tarea_id);
    console.log('🆔 fullTaskData.id:', fullTaskData.id);
    console.log('🎯 tareaId extracted:', tareaId);
    console.log('🧭 navigate function:', typeof navigate);

    if (!tareaId) {
      console.error('❌ No se pudo obtener el ID de la tarea para navegación');
      alert('Error: No se pudo identificar la fullTaskData. Revisa la consola para más detalles.');
      return;
    }

    const ruta = `/tareas/${tareaId}/entregar`;
    console.log('🚀 Navegando a:', ruta);

    try {
      // Cerrar modal primero
      onClose();

      // Pequeño delay para asegurar que el modal se cerró
      setTimeout(() => {
        console.log('🔄 Ejecutando navigate...');
        navigate(ruta);
        console.log('✅ Navigate ejecutado');
      }, 100);
    } catch (error) {
      console.error('❌ Error en navegación:', error);
      alert('Error al navegar a la página de entrega: ' + error);
    }
  };

  /**
   * Renderiza sección de información básica
   */
  const renderBasicInfo = () => (
    <div className="space-y-4">
      {/* Título y prioridad */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white leading-tight">
            {fullTaskData.titulo || 'Tarea sin título'}
          </h3>
          <div className="flex items-center gap-2 mt-2">
            <Badge variant={priorityInfo.color} className="flex items-center gap-1">
              <priorityInfo.icon className="w-3 h-3" />
              {priorityInfo.text}
            </Badge>
            {fullTaskData.tipo && (
              <Badge variant="default" outline className="capitalize">
                {fullTaskData.tipo}
              </Badge>
            )}
            {fullTaskData.categoria && (
              <Badge variant="secondary">
                {fullTaskData.categoria}
              </Badge>
            )}
          </div>
        </div>

        {/* Puntos */}
        {fullTaskData.puntuacion_maxima && (
          <div className="flex items-center gap-2 px-3 py-2 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
            <Star className="w-5 h-5 text-yellow-600" />
            <span className="font-semibold text-yellow-800 dark:text-yellow-200">
              {fullTaskData.puntuacion_maxima} pts
            </span>
          </div>
        )}
      </div>

      {/* Descripción */}
      {fullTaskData.descripcion && (
        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Descripción
          </h4>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
            {fullTaskData.descripcion}
          </p>
        </div>
      )}

      {/* Instrucciones */}
      {fullTaskData.instrucciones && (
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2 flex items-center gap-2">
            <BookOpen className="w-4 h-4" />
            Instrucciones
          </h4>
          <p className="text-blue-800 dark:text-blue-200 leading-relaxed whitespace-pre-wrap">
            {fullTaskData.instrucciones}
          </p>
        </div>
      )}
    </div>
  );

  /**
   * Renderiza sección de fechas y estado
   */
  const renderDatesAndStatus = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Fechas */}
      <Card className="p-4">
        <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
          <Calendar className="w-4 h-4" />
          Fechas Importantes
        </h4>

        <div className="space-y-2 text-sm">
          {fullTaskData.fecha_asignacion && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Asignada:</span>
              <span className="font-medium">{formatDate(fullTaskData.fecha_asignacion)}</span>
            </div>
          )}

          {fullTaskData.fecha_inicio_disponible && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Disponible desde:</span>
              <span className="font-medium">{formatDate(fullTaskData.fecha_inicio_disponible)}</span>
            </div>
          )}

          {fullTaskData.fecha_limite && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Fecha límite:</span>
              <span className={`font-medium ${
                daysUntilDeadline !== null && daysUntilDeadline < 0
                  ? 'text-red-600 dark:text-red-400'
                  : daysUntilDeadline !== null && daysUntilDeadline <= 3
                  ? 'text-orange-600 dark:text-orange-400'
                  : 'text-green-600 dark:text-green-400'
              }`}>
                {formatDate(fullTaskData.fecha_limite)}
                {daysUntilDeadline !== null && (
                  <span className="ml-2 text-xs">
                    ({daysUntilDeadline < 0 ? `${Math.abs(daysUntilDeadline)} días tarde` :
                      daysUntilDeadline === 0 ? '¡Hoy!' :
                      daysUntilDeadline === 1 ? 'Mañana' :
                      `${daysUntilDeadline} días`})
                  </span>
                )}
              </span>
            </div>
          )}

          {fullTaskData.tiempo_estimado && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Tiempo estimado:</span>
              <span className="font-medium">{fullTaskData.tiempo_estimado} minutos</span>
            </div>
          )}
        </div>
      </Card>

      {/* Estado y configuración */}
      <Card className="p-4">
        <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
          <Target className="w-4 h-4" />
          Estado y Configuración
        </h4>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Estado:</span>
            <Badge variant={fullTaskData.estado === 'asignada' ? 'default' : 'secondary'}>
              {fullTaskData.estado || 'Asignada'}
            </Badge>
          </div>

          {(fullTaskData.permite_entrega_tardia || fullTaskData.permite_entregas_tardias) && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Entrega tardía:</span>
              <Badge variant="success" outline className="text-green-600 border-green-600">
                Permitida
              </Badge>
            </div>
          )}

          {fullTaskData.intentos_maximos && fullTaskData.intentos_maximos > 1 && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Intentos máximos:</span>
              <span className="font-medium">{fullTaskData.intentos_maximos}</span>
            </div>
          )}

          {fullTaskData.tamano_maximo_mb && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Tamaño máximo:</span>
              <span className="font-medium">{fullTaskData.tamano_maximo_mb} MB</span>
            </div>
          )}

          {fullTaskData.formato_entrega && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Formato:</span>
              <span className="font-medium">{fullTaskData.formato_entrega}</span>
            </div>
          )}
        </div>
      </Card>
    </div>
  );

  /**
   * Renderiza sección de evaluación
   */
  const renderEvaluation = () => (
    <div className="space-y-4">
      {/* Criterios de evaluación */}
      {fullTaskData.criterios_evaluacion && (
        <Card className="p-4">
          <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <Award className="w-4 h-4" />
            Criterios de Evaluación
          </h4>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
            {fullTaskData.criterios_evaluacion}
          </p>
        </Card>
      )}

      {/* Rúbrica */}
      {fullTaskData.rubrica && (
        <Card className="p-4">
          <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            Rúbrica de Evaluación
          </h4>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Rúbrica detallada disponible para evaluación
          </div>
        </Card>
      )}

      {/* Información adicional */}
      {(fullTaskData.objetivos || fullTaskData.recursos_necesarios) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {fullTaskData.objetivos && (
            <Card className="p-4">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                <Target className="w-4 h-4" />
                Objetivos
              </h4>
              <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
                {fullTaskData.objetivos}
              </p>
            </Card>
          )}

          {fullTaskData.recursos_necesarios && (
            <Card className="p-4">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                <BookOpen className="w-4 h-4" />
                Recursos Necesarios
              </h4>
              <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
                {fullTaskData.recursos_necesarios}
              </p>
            </Card>
          )}
        </div>
      )}
    </div>
  );

  /**
   * Renderiza sección de profesor (si hay información)
   */
  const renderProfessorInfo = () => {
    if (!fullTaskData.docente_nombre && !fullTaskData.docente_email) return null;

    return (
      <Card className="p-4 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
        <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-3 flex items-center gap-2">
          <User className="w-4 h-4" />
          Información del Profesor
        </h4>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-100 dark:bg-blue-800 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <p className="font-medium text-blue-900 dark:text-blue-100">
              {fullTaskData.docente_nombre || 'Profesor'}
            </p>
            {fullTaskData.docente_email && (
              <p className="text-sm text-blue-700 dark:text-blue-300">
                {fullTaskData.docente_email}
              </p>
            )}
          </div>
        </div>
      </Card>
    );
  };

  /**
   * Renderiza estadísticas de entregas (solo para profesores)
   */
  const renderDeliveryStats = () => {
    if (isStudentUser || !fullTaskData.entregas) return null;

    const stats = {
      total: fullTaskData.total_entregas || fullTaskData.entregas.length,
      pendientes: fullTaskData.entregas_pendientes || fullTaskData.entregas.filter((e: any) => e.estado === 'borrador' || e.estado === 'en_revision').length,
      calificadas: fullTaskData.entregas_calificadas || fullTaskData.entregas.filter((e: any) => e.estado === 'calificada').length,
      promedio: fullTaskData.promedio_calificaciones || 0
    };

    return (
      <Card className="p-4 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
        <h4 className="font-semibold text-green-900 dark:text-green-100 mb-3 flex items-center gap-2">
          <Upload className="w-4 h-4" />
          Estadísticas de Entregas
        </h4>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
              {stats.total}
            </p>
            <p className="text-xs text-green-700 dark:text-green-300">Total</p>
          </div>

          <div>
            <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
              {stats.pendientes}
            </p>
            <p className="text-xs text-orange-700 dark:text-orange-300">Pendientes</p>
          </div>

          <div>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {stats.calificadas}
            </p>
            <p className="text-xs text-blue-700 dark:text-blue-300">Calificadas</p>
          </div>

          <div>
            <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {stats.promedio.toFixed(1)}
            </p>
            <p className="text-xs text-purple-700 dark:text-purple-300">Promedio</p>
          </div>
        </div>
      </Card>
    );
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Vista Previa: ${fullTaskData.titulo || 'Tarea'}`}
      description="Detalles completos de la tarea asignada"
      size="2xl"
      footer={
        <div className="flex items-center justify-end gap-3">
          <Button variant="secondary" onClick={onClose}>
            Cerrar
          </Button>

          {/* Botón de entregar tarea (solo para estudiantes) */}
          {isStudentUser && tareaId && (
            <Button
              onClick={handleEntregarTarea}
              className="bg-emerald-600 hover:bg-emerald-700 text-white flex items-center gap-2"
            >
              <Upload className="w-4 h-4" />
              Entregar Tarea
            </Button>
          )}
        </div>
      }
    >
      <div className="space-y-6">
        {/* Indicador de carga */}
        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <span className="ml-3 text-gray-600 dark:text-gray-400">Cargando datos de la tarea...</span>
          </div>
        )}

        {!isLoading && (
          <>
            {/* Información básica */}
            {renderBasicInfo()}

            {/* Fechas y estado */}
            {renderDatesAndStatus()}

            {/* Información del profesor */}
            {renderProfessorInfo()}

            {/* Estadísticas de entregas (profesores) */}
            {renderDeliveryStats()}

            {/* Evaluación y criterios */}
            {renderEvaluation()}

            {/* Tags */}
            {fullTaskData.tags && fullTaskData.tags.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Etiquetas</h4>
                <div className="flex flex-wrap gap-2">
                  {fullTaskData.tags.map((tag, index) => (
                    <Badge key={index} variant="default" outline>
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Debug info (solo en desarrollo) */}
            {process.env.NODE_ENV === 'development' && (
              <details className="mt-6 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
                <summary className="cursor-pointer font-medium text-gray-700 dark:text-gray-300">
                  🐛 Debug Info (Desarrollo)
                </summary>
                <pre className="mt-2 text-xs text-gray-600 dark:text-gray-400 overflow-auto">
                  {JSON.stringify({
                    tareaId,
                    isStudentUser,
                    hasNavigate: !!navigate,
                    tareaKeys: Object.keys(fullTaskData),
                    entregasCount: fullTaskData.entregas?.length || 0,
                    isLoadingData: isLoading
                  }, null, 2)}
                </pre>
              </details>
            )}
          </>
        )}
      </div>
    </Modal>
  );
});

TareaPreviewModal.displayName = 'TareaPreviewModal';

export default TareaPreviewModal;