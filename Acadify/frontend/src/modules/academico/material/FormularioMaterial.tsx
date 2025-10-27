import React, { useState } from 'react';
import { 
  MaterialEducativo, 
  CarpetaMaterial, 
  TipoMaterialEducativo, 
  EstadoMaterial 
} from '../types.js';

interface FormularioMaterialProps {
  onSubmit: (material: Partial<MaterialEducativo>) => Promise<void>;
  onCancel: () => void;
  materialInicial?: MaterialEducativo | null;
  carpetaSugerida?: CarpetaMaterial;
}

const FormularioMaterial: React.FC<FormularioMaterialProps> = ({
  onSubmit,
  onCancel,
  materialInicial = null,
  carpetaSugerida = CarpetaMaterial.OTROS
}) => {
  const [formData, setFormData] = useState({
    titulo: materialInicial?.titulo || '',
    descripcion: materialInicial?.descripcion || '',
    tipo_material: materialInicial?.tipo_material || TipoMaterialEducativo.PDF,
    carpeta: materialInicial?.carpeta || carpetaSugerida,
    tags: materialInicial?.tags || '',
    estado: materialInicial?.estado || EstadoMaterial.ACTIVO,
    url_drive: materialInicial?.url_drive || '',
    es_publico: materialInicial?.es_publico || false,
    requiere_autenticacion: materialInicial?.requiere_autenticacion || true,
  });

  const [archivo, setArchivo] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const tiposPermitidos: Record<TipoMaterialEducativo, string[]> = {
    [TipoMaterialEducativo.PDF]: ['.pdf'],
    [TipoMaterialEducativo.VIDEO]: ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
    [TipoMaterialEducativo.AUDIO]: ['.mp3', '.wav', '.ogg', '.m4a'],
    [TipoMaterialEducativo.IMAGEN]: ['.jpg', '.jpeg', '.png', '.gif', '.svg'],
    [TipoMaterialEducativo.PRESENTACION]: ['.ppt', '.pptx', '.odp'],
    [TipoMaterialEducativo.DOCUMENTO]: ['.doc', '.docx', '.odt', '.rtf'],
    [TipoMaterialEducativo.HOJA_DE_CALCULO]: ['.xls', '.xlsx', '.ods'],
    [TipoMaterialEducativo.CODIGO_FUENTE]: ['.js', '.py', '.java', '.cpp', '.c', '.html', '.css'],
    [TipoMaterialEducativo.ENLACE]: [],
    [TipoMaterialEducativo.INTERACTIVO]: ['.html', '.zip'],
    [TipoMaterialEducativo.OTRO]: ['*']
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setArchivo(file);
      
      // Auto-detectar tipo de material basado en extensión
      const extension = file.name.toLowerCase().split('.').pop();
      let tipoDetectado = TipoMaterialEducativo.OTRO;
      
      for (const [tipo, extensiones] of Object.entries(tiposPermitidos)) {
        if (extensiones.includes(`.${extension}`)) {
          tipoDetectado = tipo as TipoMaterialEducativo;
          break;
        }
      }
      
      setFormData(prev => ({
        ...prev,
        tipo_material: tipoDetectado,
        titulo: prev.titulo || file.name.replace(/\.[^/.]+$/, "")
      }));
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      setArchivo(file);
      
      // Auto-detectar tipo
      const extension = file.name.toLowerCase().split('.').pop();
      let tipoDetectado = TipoMaterialEducativo.OTRO;
      
      for (const [tipo, extensiones] of Object.entries(tiposPermitidos)) {
        if (extensiones.includes(`.${extension}`)) {
          tipoDetectado = tipo as TipoMaterialEducativo;
          break;
        }
      }
      
      setFormData(prev => ({
        ...prev,
        tipo_material: tipoDetectado,
        titulo: prev.titulo || file.name.replace(/\.[^/.]+$/, "")
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validaciones
      if (!formData.titulo.trim()) {
        throw new Error('El título es obligatorio');
      }

      if (formData.tipo_material !== TipoMaterialEducativo.ENLACE && !archivo && !materialInicial) {
        throw new Error('Debe seleccionar un archivo o proporcionar una URL');
      }

      // Preparar datos para enviar
      const materialData: Partial<MaterialEducativo> = {
        ...formData,
        titulo: formData.titulo.trim(),
        descripcion: formData.descripcion?.trim() || undefined,
        tags: formData.tags?.trim() || undefined,
      };

      // Si hay archivo, simular subida
      if (archivo) {
        // En la implementación real, aquí subirías el archivo
        materialData.formato_archivo = archivo.name.split('.').pop()?.toLowerCase();
        materialData.tamano_archivo = archivo.size;
        materialData.url_archivo = `/uploads/${Date.now()}-${archivo.name}`;
      }

      await onSubmit(materialData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al procesar el material');
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

  const formatearTamano = (bytes: number): string => {
    const sizes = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < sizes.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)} ${sizes[unitIndex]}`;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">
              {materialInicial ? 'Editar Material' : 'Subir Material Educativo'}
            </h2>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Contenido */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Información básica */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Título *
              </label>
              <input
                type="text"
                name="titulo"
                value={formData.titulo}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Nombre del material"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descripción
              </label>
              <textarea
                name="descripcion"
                value={formData.descripcion}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Descripción del contenido..."
              />
            </div>
          </div>

          {/* Clasificación */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tipo de Material
              </label>
              <select
                name="tipo_material"
                value={formData.tipo_material}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {Object.values(TipoMaterialEducativo).map((tipo) => (
                  <option key={tipo} value={tipo}>
                    {tipo.charAt(0).toUpperCase() + tipo.slice(1).replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Carpeta
              </label>
              <select
                name="carpeta"
                value={formData.carpeta}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {Object.values(CarpetaMaterial).map((carpeta) => (
                  <option key={carpeta} value={carpeta}>
                    {getCarpetaIcon(carpeta)} {carpeta.charAt(0).toUpperCase() + carpeta.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Etiquetas
            </label>
            <input
              type="text"
              name="tags"
              value={formData.tags}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="matemáticas, álgebra, ejercicios (separadas por comas)"
            />
            <p className="text-xs text-gray-500 mt-1">
              Separa las etiquetas con comas para facilitar la búsqueda
            </p>
          </div>

          {/* Archivo o URL */}
          {formData.tipo_material === TipoMaterialEducativo.ENLACE ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                URL del Recurso *
              </label>
              <input
                type="url"
                name="url_drive"
                value={formData.url_drive}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="https://..."
                required
              />
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Archivo *
              </label>
              <div
                className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                  dragOver
                    ? 'border-blue-400 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                {archivo ? (
                  <div className="space-y-2">
                    <div className="text-2xl">📎</div>
                    <p className="text-sm font-medium text-gray-900">
                      {archivo.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatearTamano(archivo.size)}
                    </p>
                    <button
                      type="button"
                      onClick={() => setArchivo(null)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remover archivo
                    </button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <div className="text-4xl text-gray-400">📁</div>
                    <p className="text-sm text-gray-600">
                      Arrastra y suelta tu archivo aquí, o{' '}
                      <label className="text-blue-600 hover:text-blue-800 cursor-pointer underline">
                        selecciona un archivo
                        <input
                          type="file"
                          onChange={handleFileChange}
                          className="hidden"
                          accept={
                            tiposPermitidos[formData.tipo_material]?.join(',') || '*'
                          }
                        />
                      </label>
                    </p>
                    <p className="text-xs text-gray-500">
                      Archivos permitidos: {tiposPermitidos[formData.tipo_material]?.join(', ') || 'Todos'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Configuración */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-gray-900">Configuración</h3>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                name="es_publico"
                checked={formData.es_publico}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm text-gray-700">
                Hacer público (visible para todos)
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="requiere_autenticacion"
                checked={formData.requiere_autenticacion}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm text-gray-700">
                Requiere autenticación para descargar
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Estado
              </label>
              <select
                name="estado"
                value={formData.estado}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {Object.values(EstadoMaterial).map((estado) => (
                  <option key={estado} value={estado}>
                    {estado.charAt(0).toUpperCase() + estado.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Acciones */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Procesando...' : (materialInicial ? 'Actualizar' : 'Subir Material')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FormularioMaterial;