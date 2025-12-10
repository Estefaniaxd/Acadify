import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ArrowLeft,
    User,
    Search,
    Filter,
    CheckCircle,
    Clock,
    AlertCircle,
    FileText,
    Download,
    ExternalLink,
    MessageSquare,
    Save,
    Sparkles,
    ChevronRight,
    MoreVertical,
    Calendar,
    Award,
    Loader2,
    ChevronLeft,
    ChevronRight as ChevronRightIcon
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { apiClientTareas } from '../../modules/tareas/api';
import { Tarea, EntregaTarea, EstadoEntrega } from '../../modules/tareas/types';

export default function CalificarTareaPage() {
    const { tareaId } = useParams<{ tareaId: string }>();
    const navigate = useNavigate();

    // Estados principales
    const [tarea, setTarea] = useState<Tarea | null>(null);
    const [entregas, setEntregas] = useState<EntregaTarea[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedEntregaId, setSelectedEntregaId] = useState<string | null>(null);
    const [gradeError, setGradeError] = useState<string | null>(null);

    // Estados de filtros y paginación
    const [filtroEstado, setFiltroEstado] = useState<EstadoEntrega | 'TODOS'>('TODOS');
    const [busqueda, setBusqueda] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 10;

    // Estados de calificación
    const [calificacion, setCalificacion] = useState<number | ''>('');
    const [comentarios, setComentarios] = useState('');
    const [saving, setSaving] = useState(false);

    // Estados de IA
    const [generatingAI, setGeneratingAI] = useState(false);

    useEffect(() => {
        if (tareaId) {
            cargarDatos();
        }
    }, [tareaId]);

    useEffect(() => {
        if (selectedEntregaId && entregas.length > 0) {
            const entrega = entregas.find(e => e.entrega_id === selectedEntregaId);
            if (entrega) {
                setCalificacion(entrega.calificacion || '');
                setComentarios(entrega.comentarios_docente || '');
            }
        }
    }, [selectedEntregaId, entregas]);

    const cargarDatos = async () => {
        if (!tareaId) return;

        try {
            setLoading(true);
            // 1. Cargar tarea
            const tareaData = await apiClientTareas.obtenerTarea(tareaId);
            setTarea(tareaData);

            // 2. Cargar entregas
            const entregasData = await apiClientTareas.obtenerEntregasTarea(tareaId);
            setEntregas(entregasData);

            // Seleccionar la primera entrega si no hay ninguna seleccionada
            if (entregasData.length > 0 && !selectedEntregaId) {
                setSelectedEntregaId(entregasData[0].entrega_id);
            }

        } catch (error) {
            console.error('Error cargando datos:', error);
            toast.error('Error al cargar la información');
        } finally {
            setLoading(false);
        }
    };

    /**
     * Extrae el nombre original del archivo desde los metadatos
     */
    const getArchivoNombre = (entrega: EntregaTarea): string => {
        // Intentar obtener desde archivos_adicionales primero
        if (entrega.archivos_adicionales && Array.isArray(entrega.archivos_adicionales)) {
            const primerArchivo = entrega.archivos_adicionales[0];
            if (primerArchivo?.nombre_original) {
                return primerArchivo.nombre_original;
            }
            if (primerArchivo?.nombre) {
                return primerArchivo.nombre;
            }
        }

        // Fallback a archivo_url (muestra UUID)
        if (entrega.archivo_url) {
            return entrega.archivo_url.split('/').pop() || 'Archivo';
        }

        return 'Sin archivo';
    };

    const validateGrade = (value: number | null): boolean => {
        if (value === null || value === undefined) {
            setGradeError(null);
            return false;
        }

        // Basic range validation
        if (value < 0 || value > 5) {
            setGradeError('La calificación debe estar entre 0.0 y 5.0');
            return false;
        }

        // Check against task max if configured
        if (tarea?.puntuacion_maxima && value > tarea.puntuacion_maxima) {
            setGradeError(`La calificación no puede exceder ${tarea.puntuacion_maxima}`);
            return false;
        }

        setGradeError(null);
        return true;
    };

    const handleGuardarCalificacion = async () => {
        if (!selectedEntregaId || calificacion === null) return;

        // Validate before saving
        if (!validateGrade(calificacion)) {
            return;
        }

        try {
            setSaving(true);
            await apiClientTareas.calificarEntrega(selectedEntregaId, {
                calificacion: calificacion,
                comentarios: comentarios
            });

            toast.success('Calificación guardada exitosamente');
            await cargarDatos(); // Reload data to ensure consistency
        } catch (error) {
            console.error('Error guardando calificación:', error);
            toast.error('Error al guardar la calificación');
        } finally {
            setSaving(false);
        }
    };

    const handleGenerarIA = async () => {
        if (!selectedEntregaId) return;

        // ❌ NO generar IA para entregas dummy (estudiantes sin entrega)
        if (selectedEntregaId.startsWith('dummy_')) {
            toast.error('Este estudiante no ha entregado la tarea todavía');
            return;
        }

        try {
            setGeneratingAI(true);
            const response = await apiClientTareas.generarRetroalimentacionIndividual(selectedEntregaId, {
                incluir_calificacion: true,
                nivel_detalle: 'completo'
            });

            console.log('🤖 Respuesta de IA:', response);  // Debug

            if (response.success && response.retroalimentacion) {
                const retro = response.retroalimentacion;

                // Actualizar formulario con sugerencias de IA
                if (retro.calificacion_sugerida) {
                    setCalificacion(retro.calificacion_sugerida);
                    validateGrade(retro.calificacion_sugerida); // Validate AI suggested grade
                }

                // ✅ Construir texto completo de retroalimentación desde todos los campos disponibles
                let textoRetro = '';

                // Opción 1: Campo directo 'retroalimentacion_texto'
                if (retro.retroalimentacion_texto) {
                    textoRetro = retro.retroalimentacion_texto;
                }
                // Opción 2: Campos estructurados (análisis, fortalezas, etc.)
                else {
                    if (retro.analisis) textoRetro += `**Análisis:**\n${retro.analisis}\n\n`;
                    if (retro.fortalezas) {
                        textoRetro += `**Fortalezas:**\n`;
                        if (Array.isArray(retro.fortalezas)) {
                            retro.fortalezas.forEach((f: string) => textoRetro += `- ${f}\n`);
                        } else {
                            textoRetro += `${retro.fortalezas}\n`;
                        }
                        textoRetro += '\n';
                    }
                    if (retro.debilidades || retro.areas_mejora) {
                        textoRetro += `**Áreas de Mejora:**\n`;
                        const areas = retro.debilidades || retro.areas_mejora;
                        if (Array.isArray(areas)) {
                            areas.forEach((a: string) => textoRetro += `- ${a}\n`);
                        } else {
                            textoRetro += `${areas}\n`;
                        }
                        textoRetro += '\n';
                    }
                    if (retro.recomendaciones || retro.sugerencias) {
                        textoRetro += `**Recomendaciones:**\n`;
                        const recs = retro.recomendaciones || retro.sugerencias;
                        if (Array.isArray(recs)) {
                            recs.forEach((r: string) => textoRetro += `- ${r}\n`);
                        } else {
                            textoRetro += `${recs}\n`;
                        }
                    }
                }

                if (textoRetro) {
                    setComentarios(prev => {
                        const separator = prev ? '\n\n--- Análisis IA ---\n\n' : '';
                        return prev + separator + textoRetro;
                    });
                    toast.success('Análisis de IA generado correctamente');
                } else {
                    console.warn('⚠️ Retroalimentación vacía:', retro);
                    toast.warning('IA generó respuesta pero sin contenido textual');
                }
            } else {
                console.warn('⚠️ Respuesta sin retroalimentación:', response);
                toast.warning('No se pudo obtener la retroalimentación');
            }

        } catch (error) {
            console.error('Error generando IA:', error);
            toast.error('Error al generar análisis de IA');
        } finally {
            setGeneratingAI(false);
        }
    };

    // Filtrado y búsqueda
    const entregasFiltradas = entregas.filter(entrega => {
        const cumpleEstado = filtroEstado === 'TODOS' || entrega.estado === filtroEstado;
        const nombreCompleto = `${entrega.estudiante_nombre || ''} ${entrega.estudiante_apellido || ''}`.toLowerCase();
        const cumpleBusqueda = nombreCompleto.includes(busqueda.toLowerCase()) ||
            entrega.estudiante_id.toLowerCase().includes(busqueda.toLowerCase());
        return cumpleEstado && cumpleBusqueda;
    });

    // Paginación
    const totalPages = Math.ceil(entregasFiltradas.length / itemsPerPage);
    const paginatedEntregas = entregasFiltradas.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
    );

    const selectedEntrega = entregas.find(e => e.entrega_id === selectedEntregaId);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-[#18181b] flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
        );
    }

    if (!tarea) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-[#18181b] flex items-center justify-center">
                <div className="text-center">
                    <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Tarea no encontrada</h2>
                    <button onClick={() => navigate(-1)} className="mt-4 text-blue-600 hover:underline">Volver</button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-[#18181b] flex flex-col">
            {/* Header */}
            <header className="bg-white dark:bg-[#1f1f23] border-b border-gray-200 dark:border-gray-700 px-6 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => navigate(-1)}
                            className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400 transition-colors"
                        >
                            <ArrowLeft className="h-5 w-5" />
                        </button>
                        <div>
                            <h1 className="text-lg font-bold text-gray-900 dark:text-white">{tarea.titulo}</h1>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Calificando entregas</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="text-right mr-4">
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {entregas.filter(e => e.estado === EstadoEntrega.CALIFICADA).length} / {entregas.length}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Calificadas</p>
                        </div>
                    </div>
                </div>
            </header>

            <div className="flex-1 flex overflow-hidden">
                {/* Sidebar - Lista de Estudiantes */}
                <aside className="w-80 bg-white dark:bg-[#1f1f23] border-r border-gray-200 dark:border-gray-700 flex flex-col">
                    <div className="p-4 border-b border-gray-200 dark:border-gray-700 space-y-3">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Buscar estudiante..."
                                value={busqueda}
                                onChange={(e) => { setBusqueda(e.target.value); setCurrentPage(1); }}
                                className="w-full pl-9 pr-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                        </div>
                        <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
                            <button
                                onClick={() => { setFiltroEstado('TODOS'); setCurrentPage(1); }}
                                className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${filtroEstado === 'TODOS'
                                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                                    : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                                    }`}
                            >
                                Todos
                            </button>
                            <button
                                onClick={() => { setFiltroEstado(EstadoEntrega.ENTREGADA); setCurrentPage(1); }}
                                className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${filtroEstado === EstadoEntrega.ENTREGADA
                                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                    : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                                    }`}
                            >
                                Por calificar
                            </button>
                            <button
                                onClick={() => { setFiltroEstado(EstadoEntrega.CALIFICADA); setCurrentPage(1); }}
                                className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${filtroEstado === EstadoEntrega.CALIFICADA
                                    ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400'
                                    : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                                    }`}
                            >
                                Calificadas
                            </button>
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto">
                        {paginatedEntregas.length === 0 ? (
                            <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                                <p className="text-sm">No se encontraron entregas</p>
                            </div>
                        ) : (
                            <div className="divide-y divide-gray-100 dark:divide-gray-800">
                                {paginatedEntregas.map((entrega) => (
                                    <button
                                        key={entrega.entrega_id}
                                        onClick={() => setSelectedEntregaId(entrega.entrega_id)}
                                        className={`w-full p-4 flex items-center gap-3 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors text-left ${selectedEntregaId === entrega.entrega_id ? 'bg-blue-50 dark:bg-blue-900/10 border-l-4 border-blue-500' : 'border-l-4 border-transparent'
                                            }`}
                                    >
                                        <div className="h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center flex-shrink-0">
                                            <User className="h-5 w-5 text-gray-500 dark:text-gray-400" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                                {entrega.estudiante_nombre && entrega.estudiante_apellido
                                                    ? `${entrega.estudiante_nombre} ${entrega.estudiante_apellido}`
                                                    : `Estudiante ${entrega.estudiante_id.substring(0, 8)}...`}
                                            </p>
                                            <div className="flex items-center gap-2 mt-1">
                                                {entrega.estado === EstadoEntrega.CALIFICADA ? (
                                                    <span className="inline-flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
                                                        <CheckCircle className="h-3 w-3" /> {entrega.calificacion} pts
                                                    </span>
                                                ) : entrega.estado === EstadoEntrega.ENTREGADA ? (
                                                    <span className="inline-flex items-center gap-1 text-xs text-orange-600 dark:text-orange-400">
                                                        <Clock className="h-3 w-3" /> Pendiente
                                                    </span>
                                                ) : (
                                                    <span className="text-xs text-gray-500">Sin entregar</span>
                                                )}
                                            </div>
                                        </div>
                                        <ChevronRight className="h-4 w-4 text-gray-400" />
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Paginación */}
                    {totalPages > 1 && (
                        <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between bg-gray-50 dark:bg-[#1f1f23]">
                            <button
                                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                disabled={currentPage === 1}
                                className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <ChevronLeft className="h-4 w-4" />
                            </button>
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                                {currentPage} / {totalPages}
                            </span>
                            <button
                                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                disabled={currentPage === totalPages}
                                className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <ChevronRightIcon className="h-4 w-4" />
                            </button>
                        </div>
                    )}
                </aside>

                {/* Main Content - Área de calificación */}
                <main className="flex-1 overflow-y-auto bg-gray-50 dark:bg-[#18181b] p-6">
                    {selectedEntrega ? (
                        <div className="max-w-4xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">

                            {/* Columna Izquierda: Contenido de la entrega (2 cols) */}
                            <div className="lg:col-span-2 space-y-6">
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="bg-white dark:bg-[#1f1f23] rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6"
                                >
                                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                        <FileText className="h-5 w-5 text-blue-500" /> Contenido de la entrega
                                    </h2>

                                    {/* Contenido Unificado */}
                                    <div className="space-y-6">
                                        {/* Texto */}
                                        {selectedEntrega.contenido_texto && (
                                            <div>
                                                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Texto</h3>
                                                <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg text-gray-800 dark:text-gray-200 whitespace-pre-wrap border border-gray-100 dark:border-gray-800">
                                                    {selectedEntrega.contenido_texto}
                                                </div>
                                            </div>
                                        )}

                                        {/* Archivos y Enlaces combinados */}
                                        {((selectedEntrega.archivos_adicionales && selectedEntrega.archivos_adicionales.length > 0) || (selectedEntrega.enlaces_externos && selectedEntrega.enlaces_externos.length > 0)) && (
                                            <div>
                                                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Adjuntos</h3>
                                                <div className="grid grid-cols-1 gap-3">
                                                    {/* TODOS los Archivos desde archivos_adicionales */}
                                                    {selectedEntrega.archivos_adicionales?.map((archivo, idx) => (
                                                        <a
                                                            key={idx}
                                                            href={`http://localhost:8000${archivo.url}`}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-800 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/20 transition-colors group"
                                                        >
                                                            <div className="p-2 bg-white dark:bg-blue-900/30 rounded-md">
                                                                <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                                                            </div>
                                                            <div className="flex-1">
                                                                <p className="font-medium text-blue-900 dark:text-blue-100">
                                                                    {archivo.nombre_original || archivo.nombre || 'Archivo'}
                                                                </p>
                                                                <p className="text-xs text-blue-700 dark:text-blue-300">
                                                                    Documento {idx + 1}
                                                                </p>
                                                            </div>
                                                            <Download className="h-4 w-4 text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                                                        </a>
                                                    ))}

                                                    {/* Enlaces Externos */}
                                                    {selectedEntrega.enlaces_externos?.map((link, idx) => (
                                                        <a
                                                            key={idx}
                                                            href={link.url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/10 border border-green-100 dark:border-green-800 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/20 transition-colors group"
                                                        >
                                                            <div className="p-2 bg-white dark:bg-green-900/30 rounded-md">
                                                                <ExternalLink className="h-5 w-5 text-green-600 dark:text-green-400" />
                                                            </div>
                                                            <div className="flex-1">
                                                                <p className="font-medium text-green-900 dark:text-green-100">
                                                                    {link.titulo || link.url}
                                                                </p>
                                                                <p className="text-xs text-green-700 dark:text-green-300">Enlace externo</p>
                                                            </div>
                                                            <ExternalLink className="h-4 w-4 text-green-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                                                        </a>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {!selectedEntrega.contenido_texto && !selectedEntrega.archivo_url && (!selectedEntrega.enlaces_externos || selectedEntrega.enlaces_externos.length === 0) && (
                                            <div className="text-center py-8 text-gray-500 dark:text-gray-400 italic">
                                                Esta entrega no tiene contenido visible.
                                            </div>
                                        )}
                                    </div>
                                </motion.div>
                            </div>

                            {/* Columna Derecha: Formulario de Calificación (1 col) */}
                            <div className="space-y-6">
                                <motion.div
                                    initial={{ opacity: 0, x: 10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    className="bg-white dark:bg-[#1f1f23] rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 sticky top-6"
                                >
                                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                                        <Award className="h-5 w-5 text-purple-500" /> Evaluación
                                    </h2>

                                    <div className="space-y-6">
                                        {/* Input Calificación */}
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                                Calificación (Max: {tarea.puntuacion_maxima})
                                            </label>
                                            <div>
                                                <div className="flex items-center space-x-3">
                                                    <input
                                                        type="number"
                                                        step="0.1"
                                                        min="0"
                                                        max="5"
                                                        value={calificacion === null ? '' : calificacion}
                                                        onChange={(e) => {
                                                            const val = parseFloat(e.target.value);
                                                            const newCalificacion = isNaN(val) ? null : val;
                                                            setCalificacion(newCalificacion);
                                                            validateGrade(newCalificacion);
                                                        }}
                                                        className={`w-24 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 ${gradeError
                                                            ? 'border-red-500 focus:ring-red-500'
                                                            : 'border-gray-300 focus:ring-blue-500'
                                                            } [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none`}
                                                        placeholder="0.0"
                                                    />
                                                    <span className="text-gray-600 dark:text-gray-400">/ 5.0</span>
                                                </div>
                                                {gradeError && (
                                                    <div className="text-red-600 text-sm mt-1">
                                                        {gradeError}
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        {/* Botón IA */}
                                        <button
                                            onClick={handleGenerarIA}
                                            disabled={generatingAI}
                                            className="w-full flex items-center justify-center gap-2 py-2 px-4 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 hover:from-indigo-500/20 hover:to-purple-500/20 border border-indigo-200 dark:border-indigo-800 rounded-lg text-indigo-700 dark:text-indigo-300 transition-all text-sm font-medium"
                                        >
                                            {generatingAI ? (
                                                <Loader2 className="h-4 w-4 animate-spin" />
                                            ) : (
                                                <Sparkles className="h-4 w-4" />
                                            )}
                                            {generatingAI ? 'Analizando...' : 'Sugerir con IA'}
                                        </button>

                                        {/* Comentarios */}
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                                Retroalimentación
                                            </label>
                                            <textarea
                                                rows={6}
                                                value={comentarios}
                                                onChange={(e) => setComentarios(e.target.value)}
                                                className="w-full p-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 outline-none resize-none transition-all"
                                                placeholder="Escribe tus comentarios aquí..."
                                            />
                                        </div>

                                        {/* Botón Guardar */}
                                        <button
                                            onClick={handleGuardarCalificacion}
                                            disabled={saving || !!gradeError || calificacion === null}
                                            className={`w-full py-3 px-4 rounded-lg flex items-center justify-center gap-2 font-medium transition-colors ${saving || !!gradeError || calificacion === null
                                                ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                                                : 'bg-green-500 hover:bg-green-600 text-white'
                                                }`}
                                        >
                                            {saving && <Loader2 className="h-4 w-4 animate-spin" />}
                                            {saving ? 'Guardando...' : 'Guardar Calificación'}
                                        </button>
                                    </div>
                                </motion.div>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-gray-500 dark:text-gray-400">
                            <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-full mb-4">
                                <User className="h-8 w-8 text-gray-400" />
                            </div>
                            <p className="text-lg font-medium">Selecciona un estudiante</p>
                            <p className="text-sm">Elige una entrega de la lista para calificar</p>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
}
