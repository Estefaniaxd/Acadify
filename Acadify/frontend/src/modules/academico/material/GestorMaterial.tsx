import React, { useState, useEffect } from 'react';
import { 
  MaterialEducativo, 
  CarpetaMaterial, 
  TipoMaterialEducativo, 
  EstadoMaterial,
  FiltrosMaterial 
} from '../types.js';

interface GestorMaterialProps {
  carpetaInicial?: CarpetaMaterial;
  onMaterialSeleccionado?: (material: MaterialEducativo) => void;
}

const GestorMaterial: React.FC<GestorMaterialProps> = ({ 
  carpetaInicial = CarpetaMaterial.OTROS,
  onMaterialSeleccionado 
}) => {
  const [materiales, setMateriales] = useState<MaterialEducativo[]>([]);
  const [carpetaActual, setCarpetaActual] = useState<CarpetaMaterial>(carpetaInicial);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busqueda, setBusqueda] = useState('');
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [materialSeleccionado, setMaterialSeleccionado] = useState<MaterialEducativo | null>(null);

  useEffect(() => {
    cargarMateriales();
  }, [carpetaActual]);

  const cargarMateriales = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simular llamada a API
      const materialesSimulados: MaterialEducativo[] = [
        {
          material_id: '1',
          titulo: 'Introducción a las Matemáticas',
          descripcion: 'Material introductorio para estudiantes de primer año',
          tipo_material: TipoMaterialEducativo.PDF,
          carpeta: CarpetaMaterial.LECTURAS,
          url_archivo: '/materials/intro-math.pdf',
          formato_archivo: 'pdf',
          tamano_archivo: 2048000,
          version: 1,
          es_version_actual: true,
          estado: EstadoMaterial.ACTIVO,
          numero_descargas: 45,
          fecha_creacion: new Date().toISOString(),
        },
        {
          material_id: '2',
          titulo: 'Guía de Ejercicios - Álgebra',
          descripcion: 'Ejercicios prácticos con soluciones detalladas',
          tipo_material: TipoMaterialEducativo.PDF,
          carpeta: CarpetaMaterial.GUIAS,
          url_archivo: '/materials/algebra-exercises.pdf',
          formato_archivo: 'pdf',
          tamano_archivo: 1024000,
          version: 2,
          es_version_actual: true,
          estado: EstadoMaterial.ACTIVO,
          numero_descargas: 67,
          fecha_creacion: new Date().toISOString(),
        }
      ];
      
      // Filtrar por carpeta actual
      const materialesFiltrados = materialesSimulados.filter(
        m => m.carpeta === carpetaActual
      );
      
      setMateriales(materialesFiltrados);
    } catch (err) {
      setError('Error al cargar el material educativo');
      console.error('Error cargando material:', err);
    } finally {
      setLoading(false);
    }
  };

  const getCarpetaIcon = (carpeta: CarpetaMaterial): string => {
    const iconos = {
      [CarpetaMaterial.LECTURAS]: '📚',
      [CarpetaMaterial.GUIAS]: '📋',
      [CarpetaMaterial.TAREAS]: '✏️',
      [CarpetaMaterial.EXAMENES]: '📝',
      [CarpetaMaterial.RECURSOS]: '🔧',
      [CarpetaMaterial.MULTIMEDIA]: '🎬',
      [CarpetaMaterial.EJERCICIOS]: '💪',
      [CarpetaMaterial.BIBLIOGRAFIAS]: '📖',
      [CarpetaMaterial.OTROS]: '📁',
    };
    return iconos[carpeta] || '📁';
  };

  const getCarpetaNombre = (carpeta: CarpetaMaterial): string => {
    const nombres = {
      [CarpetaMaterial.LECTURAS]: 'Lecturas',
      [CarpetaMaterial.GUIAS]: 'Guías',
      [CarpetaMaterial.TAREAS]: 'Tareas',
      [CarpetaMaterial.EXAMENES]: 'Exámenes',
      [CarpetaMaterial.RECURSOS]: 'Recursos',
      [CarpetaMaterial.MULTIMEDIA]: 'Multimedia',
      [CarpetaMaterial.EJERCICIOS]: 'Ejercicios',
      [CarpetaMaterial.BIBLIOGRAFIAS]: 'Bibliografías',
      [CarpetaMaterial.OTROS]: 'Otros',
    };
    return nombres[carpeta] || 'Otros';
  };

  const getTipoMaterialIcon = (tipo: TipoMaterialEducativo): string => {
    const iconos = {
      [TipoMaterialEducativo.PDF]: '📄',
      [TipoMaterialEducativo.VIDEO]: '🎥',
      [TipoMaterialEducativo.AUDIO]: '🎵',
      [TipoMaterialEducativo.IMAGEN]: '🖼️',
      [TipoMaterialEducativo.PRESENTACION]: '📊',
      [TipoMaterialEducativo.DOCUMENTO]: '📃',
      [TipoMaterialEducativo.HOJA_DE_CALCULO]: '📈',
      [TipoMaterialEducativo.ENLACE]: '🔗',
      [TipoMaterialEducativo.INTERACTIVO]: '🎮',
      [TipoMaterialEducativo.CODIGO_FUENTE]: '💻',
      [TipoMaterialEducativo.OTRO]: '📎',
    };
    return iconos[tipo] || '📎';
  };

  const formatearTamano = (bytes?: number): string => {
    if (!bytes) return 'Desconocido';
    
    const sizes = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < sizes.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)} ${sizes[unitIndex]}`;
  };

  const handleDescargar = (material: MaterialEducativo) => {
    // Simular descarga
    const link = document.createElement('a');
    link.href = material.url_archivo;
    link.download = `${material.titulo}.${material.formato_archivo}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bg-white rounded-lg border shadow-sm">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Material Educativo
          </h2>
          <button 
            onClick={() => setMostrarFormulario(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            + Subir Material
          </button>
        </div>

        {/* Navegador de carpetas */}
        <div className="flex gap-2 flex-wrap">
          {Object.values(CarpetaMaterial).map((carpeta) => (
            <button
              key={carpeta}
              onClick={() => setCarpetaActual(carpeta)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                carpetaActual === carpeta
                  ? 'bg-blue-100 text-blue-800 border border-blue-200'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <span>{getCarpetaIcon(carpeta)}</span>
              {getCarpetaNombre(carpeta)}
            </button>
          ))}
        </div>

        {/* Barra de búsqueda */}
        <div className="mt-4">
          <input
            type="text"
            placeholder="Buscar material..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Contenido */}
      <div className="p-6">
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Cargando material...</p>
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <div className="text-red-500 mb-2">⚠️</div>
            <p className="text-red-600">{error}</p>
            <button 
              onClick={cargarMateriales}
              className="mt-2 px-4 py-2 bg-red-100 text-red-800 rounded-lg hover:bg-red-200 transition-colors"
            >
              Reintentar
            </button>
          </div>
        ) : materiales.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">{getCarpetaIcon(carpetaActual)}</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No hay material en {getCarpetaNombre(carpetaActual)}
            </h3>
            <p className="text-gray-600 mb-4">
              Sube el primer archivo para esta carpeta
            </p>
            <button 
              onClick={() => setMostrarFormulario(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Subir Material
            </button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {materiales.map((material) => (
              <div
                key={material.material_id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                {/* Header del archivo */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">
                      {getTipoMaterialIcon(material.tipo_material)}
                    </span>
                    <div>
                      <h3 className="font-medium text-gray-900 text-sm">
                        {material.titulo}
                      </h3>
                      <p className="text-xs text-gray-500">
                        {formatearTamano(material.tamano_archivo)} • v{material.version}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button
                      onClick={() => handleDescargar(material)}
                      className="p-1 text-gray-600 hover:text-blue-600 transition-colors"
                      title="Descargar"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </button>
                    <button
                      className="p-1 text-gray-600 hover:text-gray-800 transition-colors"
                      title="Opciones"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Descripción */}
                {material.descripcion && (
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {material.descripcion}
                  </p>
                )}

                {/* Metadatos */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">Descargas:</span>
                    <span className="font-medium">{material.numero_descargas}</span>
                  </div>
                  
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">Subido:</span>
                    <span className="font-medium">
                      {new Date(material.fecha_creacion).toLocaleDateString()}
                    </span>
                  </div>

                  {material.tags && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {material.tags.split(',').map((tag, index) => (
                        <span 
                          key={index}
                          className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
                        >
                          {tag.trim()}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Acciones */}
                <div className="mt-4 pt-3 border-t border-gray-100">
                  <button
                    onClick={() => handleDescargar(material)}
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg text-sm hover:bg-blue-700 transition-colors"
                  >
                    Descargar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GestorMaterial;