import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface SaveAvatarDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string, isActive: boolean, isPublic: boolean) => void;
  isSaving: boolean;
}

export const SaveAvatarDialog: React.FC<SaveAvatarDialogProps> = ({
  isOpen,
  onClose,
  onSave,
  isSaving
}) => {
  const [name, setName] = useState('');
  const [isActive, setIsActive] = useState(false);
  const [isPublic, setIsPublic] = useState(true);
  const [nameError, setNameError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validación
    if (!name.trim()) {
      setNameError('El nombre es requerido');
      return;
    }
    
    if (name.trim().length < 2) {
      setNameError('El nombre debe tener al menos 2 caracteres');
      return;
    }
    
    if (name.trim().length > 100) {
      setNameError('El nombre no puede tener más de 100 caracteres');
      return;
    }
    
    setNameError('');
    onSave(name.trim(), isActive, isPublic);
  };

  const handleClose = () => {
    if (!isSaving) {
      setName('');
      setIsActive(false);
      setIsPublic(true);
      setNameError('');
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
          onClick={handleClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: "spring", duration: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-6 w-full max-w-md"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                Guardar Avatar
              </h2>
              <button
                onClick={handleClose}
                disabled={isSaving}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors p-1"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Name Input */}
              <div>
                <label htmlFor="avatar-name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nombre del Avatar *
                </label>
                <input
                  id="avatar-name"
                  type="text"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value);
                    if (nameError) setNameError('');
                  }}
                  placeholder="Ej: Mi Avatar Favorito"
                  disabled={isSaving}
                  className={`block w-full px-3 py-2 border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors ${
                    nameError
                      ? 'border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20'
                      : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700'
                  } text-gray-900 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed`}
                  autoFocus
                />
                {nameError && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-1 text-sm text-red-600 dark:text-red-400"
                  >
                    {nameError}
                  </motion.p>
                )}
              </div>

              {/* Options */}
              <div className="space-y-4">
                {/* Set as Active */}
                <div className="flex items-center">
                  <input
                    id="is-active"
                    type="checkbox"
                    checked={isActive}
                    onChange={(e) => setIsActive(e.target.checked)}
                    disabled={isSaving}
                    className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 dark:border-gray-600 rounded disabled:opacity-50"
                  />
                  <label htmlFor="is-active" className="ml-3 block text-sm text-gray-700 dark:text-gray-300">
                    Establecer como avatar activo
                  </label>
                </div>

                {/* Public/Private */}
                <div className="flex items-center">
                  <input
                    id="is-public"
                    type="checkbox"
                    checked={isPublic}
                    onChange={(e) => setIsPublic(e.target.checked)}
                    disabled={isSaving}
                    className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 dark:border-gray-600 rounded disabled:opacity-50"
                  />
                  <label htmlFor="is-public" className="ml-3 block text-sm text-gray-700 dark:text-gray-300">
                    Hacer público (visible para otros usuarios)
                  </label>
                </div>
              </div>

              {/* Help Text */}
              <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-blue-700 dark:text-blue-200">
                      Tu avatar se guardará permanentemente. Podrás editarlo, activarlo/desactivarlo o eliminarlo más tarde desde tu galería.
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-3 space-y-reverse space-y-3 sm:space-y-0">
                <button
                  type="button"
                  onClick={handleClose}
                  disabled={isSaving}
                  className="w-full sm:w-auto px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isSaving || !name.trim()}
                  className="w-full sm:w-auto px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-600 to-blue-600 border border-transparent rounded-lg shadow-sm hover:from-purple-700 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  {isSaving ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Guardando...
                    </div>
                  ) : (
                    'Guardar Avatar'
                  )}
                </button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};