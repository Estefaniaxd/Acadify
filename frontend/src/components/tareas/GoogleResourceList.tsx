/**
 * Componente para listar recursos de Google Workspace
 * 
 * Muestra todos los recursos vinculados a una tarea con
 * estados de carga y vacío.
 */

import React from 'react';
import { Loader2, FolderOpen } from 'lucide-react';
import GoogleResourceCard from './GoogleResourceCard';
import { GoogleResource } from '../../hooks/useGoogleWorkspace';

interface GoogleResourceListProps {
    resources: GoogleResource[];
    isLoading?: boolean;
    onDelete: (id: string) => void;
    onOpen: (url: string) => void;
}

export default function GoogleResourceList({
    resources,
    isLoading,
    onDelete,
    onOpen,
}: GoogleResourceListProps) {
    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
            </div>
        );
    }

    if (resources.length === 0) {
        return null;
    }

    return (
        <div className="space-y-3">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Recursos vinculados ({resources.length})
            </p>
            {resources.map((resource) => (
                <GoogleResourceCard
                    key={resource.id}
                    resource={resource}
                    onDelete={onDelete}
                    onOpen={onOpen}
                />
            ))}
        </div>
    );
}
