import React from 'react';
import { FileText, Download, X } from 'lucide-react';

export interface Archivo {
  url: string;
  nombre: string;
  nombre_original?: string;
  tamaño?: number;
  preview?: string;
}

interface ArchivoCardProps {
  archivo: Archivo;
  onDelete?: () => void;
  onDownload?: (url: string, nombre: string) => void;
  showDelete?: boolean;
  variant?: 'default' | 'reference';
}

/**
 * Componente reutilizable para mostrar archivos
 * Se usa en:
 * - Pre-entrega (archivos locales)
 * - Post-entrega (archivos subidos)
 * - Referencia (archivos de entrega anterior)
 */
export function ArchivoCard({
  archivo,
  onDelete,
  onDownload,
  showDelete = false,
  variant = 'default'
}: ArchivoCardProps) {
  const handleDownloadClick = (e: React.MouseEvent) => {
    e.preventDefault();
    
    if (onDownload) {
      onDownload(archivo.url, archivo.nombre);
    } else {
      // Fallback: crear link y simular click
      const link = document.createElement('a');
      link.href = archivo.url;
      link.download = archivo.nombre || 'archivo';
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const variantClasses = {
    default: {
      bg: 'bg-blue-50 dark:bg-blue-900/10',
      border: 'border border-blue-200 dark:border-blue-800/40',
      icon: 'text-blue-600 dark:text-blue-400',
      text: 'text-gray-700 dark:text-gray-300',
      hover: 'hover:bg-blue-100/50 dark:hover:bg-blue-900/20'
    },
    reference: {
      bg: 'bg-amber-50 dark:bg-amber-900/10',
      border: 'border border-amber-200 dark:border-amber-800/40',
      icon: 'text-amber-600 dark:text-amber-400',
      text: 'text-gray-700 dark:text-gray-300',
      hover: 'hover:bg-amber-100/50 dark:hover:bg-amber-900/20'
    }
  };

  const colors = variantClasses[variant];

  return (
    <div
      className={`flex items-center gap-3 p-3 rounded-lg ${colors.bg} ${colors.border} group transition-colors ${colors.hover}`}
    >
      {/* Icono de archivo */}
      <div className="flex-shrink-0">
        {archivo.preview ? (
          <img
            src={archivo.preview}
            alt="preview"
            className="h-8 w-8 object-cover rounded bg-white dark:bg-gray-800"
          />
        ) : (
          <FileText className={`h-5 w-5 ${colors.icon}`} />
        )}
      </div>

      {/* Información del archivo */}
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium ${colors.text} truncate`}>
          {archivo.nombre || archivo.nombre_original || 'Archivo sin nombre'}
        </p>
        {archivo.tamaño && (
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {(archivo.tamaño / 1024 / 1024).toFixed(2)} MB
          </p>
        )}
      </div>

      {/* Botones de acción */}
      <div className="flex items-center gap-1 flex-shrink-0">
        {/* Descargar */}
        <button
          onClick={handleDownloadClick}
          type="button"
          title="Descargar archivo"
          className={`p-2 rounded ${colors.icon} hover:bg-white/50 dark:hover:bg-gray-700/50 transition-colors opacity-0 group-hover:opacity-100`}
        >
          <Download className="h-4 w-4" />
        </button>

        {/* Eliminar (si aplica) */}
        {showDelete && onDelete && (
          <button
            onClick={onDelete}
            type="button"
            title="Eliminar archivo"
            className="p-2 rounded text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors opacity-0 group-hover:opacity-100"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}
