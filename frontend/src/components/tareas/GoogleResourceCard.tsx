/**
 * Componente para mostrar un recurso de Google Workspace vinculado
 * 
 * Muestra información del recurso con iconos específicos por tipo
 * y acciones para abrir o eliminar.
 * 
 * Design Principles:
 * - Visual Clarity: Iconos y colores por tipo de recurso
 * - User Actions: Abrir en nueva pestaña, eliminar vínculo
 */

import React from 'react';
import {
    FileText,
    Table,
    Presentation,
    Pencil,
    FormInput,
    File,
    ExternalLink,
    Trash2,
} from 'lucide-react';
import { GoogleResource } from '../../hooks/useGoogleWorkspace';

interface GoogleResourceCardProps {
    resource: GoogleResource;
    onDelete: (id: string) => void;
    onOpen: (url: string) => void;
}

export default function GoogleResourceCard({
    resource,
    onDelete,
    onOpen,
}: GoogleResourceCardProps) {
    const getIconAndColor = (type: string) => {
        const configs = {
            document: {
                icon: <FileText className="w-5 h-5" />,
                color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
                label: 'Documento',
            },
            spreadsheet: {
                icon: <Table className="w-5 h-5" />,
                color: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
                label: 'Hoja de cálculo',
            },
            presentation: {
                icon: <Presentation className="w-5 h-5" />,
                color: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400',
                label: 'Presentación',
            },
            drawing: {
                icon: <Pencil className="w-5 h-5" />,
                color: 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400',
                label: 'Dibujo',
            },
            form: {
                icon: <FormInput className="w-5 h-5" />,
                color: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
                label: 'Formulario',
            },
            drive_file: {
                icon: <File className="w-5 h-5" />,
                color: 'bg-gray-100 dark:bg-gray-900/30 text-gray-600 dark:text-gray-400',
                label: 'Archivo',
            },
        };

        return configs[type as keyof typeof configs] || configs.drive_file;
    };

    const { icon, color, label } = getIconAndColor(resource.type);

    return (
        <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg flex items-center gap-3 hover:bg-gray-50 dark:hover:bg-zinc-800/50 transition-colors">
            {/* Icono */}
            <div className={`p-2 rounded ${color}`}>
                {icon}
            </div>

            {/* Información */}
            <div className="flex-1 min-w-0">
                <h4 className="font-medium text-gray-900 dark:text-gray-100 truncate">
                    {resource.name}
                </h4>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                    {label}
                    {resource.linked && ' • Vinculado'}
                    {resource.shared_with_teacher && ' • Compartido con docente'}
                </p>
            </div>

            {/* Acciones */}
            <div className="flex items-center gap-2">
                <button
                    onClick={() => onOpen(resource.url)}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors text-gray-600 dark:text-gray-400 hover:text-primary"
                    title="Abrir en nueva pestaña"
                >
                    <ExternalLink className="w-5 h-5" />
                </button>
                <button
                    onClick={() => onDelete(resource.id)}
                    className="p-2 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-colors text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                    title="Eliminar vínculo"
                >
                    <Trash2 className="w-5 h-5" />
                </button>
            </div>
        </div>
    );
}
