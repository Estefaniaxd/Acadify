/**
 * Hook personalizado para operaciones con Google Workspace
 * 
 * Maneja la creación, vinculación y eliminación de recursos Google
 * (Docs, Sheets, Slides, Drawings, Forms) en tareas.
 * 
 * Clean Code Principles:
 * - Single Responsibility: Solo maneja operaciones Google Workspace
 * - Custom Hook Pattern: Encapsula lógica reutilizable
 */

import { useState, useCallback, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClientTareas } from '../modules/tareas/api';
import oauthService, { type OAuthStatus } from '../services/oauth.service';

export interface GoogleResource {
    id: string;
    type: 'document' | 'spreadsheet' | 'presentation' | 'drawing' | 'form' | 'drive_file';
    name: string;
    url: string;
    created_at: string;
    shared_with_teacher: boolean;
    linked?: boolean;
}

export interface GoogleResourceCreate {
    type: string;
    title: string;
    folder_id?: string;
    initial_content?: string;
    headers?: string[];
    description?: string;
    share_with_teacher?: boolean;
}

export function useGoogleWorkspace(tareaId: string) {
    const queryClient = useQueryClient();
    const [isCreating, setIsCreating] = useState(false);
    const [oauthStatus, setOauthStatus] = useState<OAuthStatus | null>(null);
    const [isCheckingAuth, setIsCheckingAuth] = useState(true);

    // Query para obtener recursos vinculados
    const {
        data: resources = [],
        isLoading,
        error,
    } = useQuery<GoogleResource[]>({
        queryKey: ['google-workspace-resources', tareaId],
        queryFn: async () => {
            const response = await fetch(
                `/api/tareas/${tareaId}/google-workspace/resources`,
                {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    },
                }
            );
            if (!response.ok) {
                throw new Error('Error al obtener recursos');
            }
            return response.json();
        },
        enabled: !!tareaId,
    });

    // Mutation para crear recurso
    const createMutation = useMutation({
        mutationFn: async (data: GoogleResourceCreate) => {
            const response = await fetch(
                `/api/tareas/${tareaId}/google-workspace/create`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    },
                    body: JSON.stringify(data),
                }
            );
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error al crear recurso');
            }
            return response.json();
        },
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ['google-workspace-resources', tareaId]
            });
        },
    });

    // Mutation para eliminar recurso
    const deleteMutation = useMutation({
        mutationFn: async ({ resourceId, deleteFromDrive = false }: {
            resourceId: string;
            deleteFromDrive?: boolean;
        }) => {
            const response = await fetch(
                `/api/tareas/${tareaId}/google-workspace/${resourceId}?delete_from_drive=${deleteFromDrive}`,
                {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    },
                }
            );
            if (!response.ok) {
                throw new Error('Error al eliminar recurso');
            }
        },
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ['google-workspace-resources', tareaId]
            });
        },
    });

    // Función para crear recurso
    const createResource = useCallback(async (data: GoogleResourceCreate) => {
        if (isCheckingAuth) {
            throw new Error('Verificando tu conexión con Google. Inténtalo de nuevo en un momento.');
        }

        if (!oauthStatus?.is_linked) {
            throw new Error('Conecta tu cuenta de Google antes de crear recursos.');
        }

        if (oauthStatus?.needs_relink || oauthStatus?.has_credentials === false) {
            throw new Error('Tu sesión de Google caducó. Vuelve a vincular tu cuenta para continuar.');
        }

        setIsCreating(true);
        try {
            const result = await createMutation.mutateAsync(data);
            return result;
        } finally {
            setIsCreating(false);
        }
    }, [createMutation, isCheckingAuth, oauthStatus]);

    // Función para eliminar recurso
    const deleteResource = useCallback(async (
        resourceId: string,
        deleteFromDrive = false
    ) => {
        await deleteMutation.mutateAsync({ resourceId, deleteFromDrive });
    }, [deleteMutation]);

    const fetchOAuthStatus = useCallback(async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            setOauthStatus(null);
            setIsCheckingAuth(false);
            return;
        }

        setIsCheckingAuth(true);
        try {
            const status = await oauthService.getGoogleStatus(token);
            setOauthStatus({
                ...status,
                has_credentials: status.has_credentials ?? status.is_linked,
                needs_relink: status.needs_relink ?? false,
            });
        } catch (err) {
            console.warn('No se pudo obtener el estado de OAuth de Google:', err);
            setOauthStatus({
                is_linked: false,
                provider: 'google',
                has_credentials: false,
                needs_relink: false,
            });
        } finally {
            setIsCheckingAuth(false);
        }
    }, []);

    useEffect(() => {
        fetchOAuthStatus();
    }, [fetchOAuthStatus]);

    const connectGoogleAccount = useCallback(() => {
        const currentUrl = window.location.href;
        const linkUrl = oauthService.getGoogleLinkUrl(currentUrl);
        window.location.href = linkUrl;
    }, []);

    return {
        resources,
        isLoading,
        error,
        isCreating,
        createResource,
        deleteResource,
        isDeleting: deleteMutation.isPending,
        oauthStatus,
        isCheckingAuth,
        refreshOAuthStatus: fetchOAuthStatus,
        connectGoogleAccount,
    };
}
