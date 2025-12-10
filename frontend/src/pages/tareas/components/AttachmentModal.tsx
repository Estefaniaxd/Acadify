import React from 'react';
import { X, Upload, Link as LinkIcon, FileText, Presentation, Table, Palette, Video } from 'lucide-react';

interface AttachmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectFile: () => void;
  onSelectLink: () => void;
  onSelectGoogleDrive: () => void;
  onCreateDoc: () => void;
  onCreateSlides: () => void;
  onCreateSheets: () => void;
  onCreateDrawing: () => void;
  onCreateVideo: () => void;
}

const AttachmentModal: React.FC<AttachmentModalProps> = ({
  isOpen,
  onClose,
  onSelectFile,
  onSelectLink,
  onSelectGoogleDrive,
  onCreateDoc,
  onCreateSlides,
  onCreateSheets,
  onCreateDrawing,
  onCreateVideo
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md mx-4" onClick={(e) => e.stopPropagation()}>
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Agregar o crear</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        <div className="p-4 space-y-1">
          {/* Adjuntar opciones */}
          <button
            onClick={onSelectGoogleDrive}
            className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors text-left"
          >
            <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded">
              <svg className="h-5 w-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M8 0l6.5 11.5L8 23H1.5L8 11.5 1.5 0z"/>
                <path fill="#34A853" d="M23 23H8l-6.5-11.5L8 0z"/>
                <path fill="#FBBC04" d="M8 0h15l-6.5 11.5z"/>
              </svg>
            </div>
            <span className="text-gray-900 dark:text-white font-medium">Google Drive</span>
          </button>

          <button
            onClick={onSelectLink}
            className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors text-left"
          >
            <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded">
              <LinkIcon className="h-5 w-5 text-gray-700 dark:text-gray-300" />
            </div>
            <span className="text-gray-900 dark:text-white font-medium">Vínculo</span>
          </button>

          <button
            onClick={onSelectFile}
            className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors text-left"
          >
            <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded">
              <Upload className="h-5 w-5 text-gray-700 dark:text-gray-300" />
            </div>
            <span className="text-gray-900 dark:text-white font-medium">Archivo</span>
          </button>

          {/* Divider */}
          <div className="py-2">
            <div className="border-t border-gray-200 dark:border-gray-700"></div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 px-3">Crear nuevo</p>
          </div>

          {/* Crear opciones */}
          <button
            onClick={onCreateDoc}
            className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors text-left"
          >
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded">
              <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            </div>
            <span className="text-gray-900 dark:text-white font-medium">Documentos</span>
          </button>

          <button
            onClick={onCreateSlides}
            className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors text-left"
          >
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded">
              <Presentation className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
            </div>
            <span className="text-gray-900 dark:text-white font-medium">Presentaciones</span>
          </button>

          <button
            onClick={onCreateSheets}
            className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors text-left"
          >
            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded">
              <Table className="h-5 w-5 text-green-600 dark:text-green-400" />
            </div>
            <span className="text-gray-900 dark:text-white font-medium">Hojas de cálculo</span>
          </button>

          <button
            onClick={onCreateDrawing}
            className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors text-left"
          >
            <div className="p-2 bg-pink-100 dark:bg-pink-900/30 rounded">
              <Palette className="h-5 w-5 text-pink-600 dark:text-pink-400" />
            </div>
            <span className="text-gray-900 dark:text-white font-medium">Dibujos</span>
          </button>

          <button
            onClick={onCreateVideo}
            className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors text-left"
          >
            <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded">
              <Video className="h-5 w-5 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-gray-900 dark:text-white font-medium">Vids</span>
              <span className="text-xs bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 px-2 py-0.5 rounded">Novedad</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AttachmentModal;
