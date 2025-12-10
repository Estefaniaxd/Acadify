/**
 * Modal principal para Google Workspace
 * 
 * Presenta todas las opciones para agregar/crear recursos:
 * - Subir archivos
 * - Agregar enlaces
 * - Seleccionar de Google Drive
 * - Crear: Documento, Hoja de cálculo, Presentación, Dibujo, Formulario
 * 
 * Design Principles:
 * - Component Composition: Usa OptionCard reutilizable
 * - Clean UI: Organizado por secciones
 * - Responsive: Grid adaptable
 */

import React, { useState, useEffect } from 'react';
import {
    Upload,
    Link as LinkIcon,
    FolderOpen,
    FileText,
    Table,
    Presentation,
    Pencil,
    FormInput,
    X,
    Loader2,
} from 'lucide-react';
import type { OAuthStatus } from '../../services/oauth.service';
import { type GoogleResourceCreate } from '../../hooks/useGoogleWorkspace';

interface GoogleWorkspaceModalProps {
    onClose: () => void;
    onResourceCreated?: (resource: any) => void;
    onFileUpload?: () => void;
    onLinkAdd?: () => void;
    createResource: (data: GoogleResourceCreate) => Promise<any>;
    isCreating: boolean;
    isCheckingAuth: boolean;
    isGoogleLinked: boolean;
    oauthStatus: OAuthStatus | null;
    onConnectGoogle: () => void;
}

interface OptionCardProps {
    icon: React.ReactNode;
    title: string;
    color: string;
    onClick: () => void;
    disabled?: boolean;
}

function OptionCard({ icon, title, color, onClick, disabled }: OptionCardProps) {
    const colorClasses = {
        blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/30',
        green: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/30',
        yellow: 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400 hover:bg-yellow-100 dark:hover:bg-yellow-900/30',
        red: 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/30',
        purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 hover:bg-purple-100 dark:hover:bg-purple-900/30',
    };

    return (
        <button
            onClick={(e) => {
                console.log('🟢 OptionCard clicked:', title);
                e.stopPropagation();
                onClick();
            }}
            disabled={disabled}
            className={`
        p-4 rounded-lg transition-all duration-200
        flex flex-col items-center gap-2
        ${colorClasses[color as keyof typeof colorClasses]}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer transform hover:scale-105'}
      `}
        >
            <div className="w-8 h-8">
                {icon}
            </div>
            <span className="text-sm font-medium">{title}</span>
        </button>
    );
}

export default function GoogleWorkspaceModal({
    onClose,
    onResourceCreated,
    onFileUpload,
    onLinkAdd,
    createResource,
    isCreating,
    isCheckingAuth,
    isGoogleLinked,
    oauthStatus,
    onConnectGoogle,
}: GoogleWorkspaceModalProps) {
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [selectedType, setSelectedType] = useState<string>('');
    const [title, setTitle] = useState('');
    const [error, setError] = useState<string | null>(null);
    const hasValidGoogleConnection = oauthStatus
        ? Boolean(oauthStatus.is_linked && (oauthStatus.has_credentials ?? true) && !oauthStatus.needs_relink)
        : isGoogleLinked;
    const needsReconnect = Boolean(oauthStatus?.is_linked && (!oauthStatus?.has_credentials || oauthStatus?.needs_relink));
    const canUseGoogleWorkspace = hasValidGoogleConnection && !isCheckingAuth;

    const handleCreate = async (type: string) => {
        if (!canUseGoogleWorkspace) {
            setError(
                needsReconnect
                    ? 'Tu conexión con Google caducó. Re-vincula tu cuenta para continuar.'
                    : 'Conecta tu cuenta de Google antes de crear recursos.'
            );
            return;
        }
        console.log('🔵 handleCreate called with type:', type);
        setSelectedType(type);
        setShowCreateForm(true);
        setError(null);
        console.log('🔵 State updated - showCreateForm: true, selectedType:', type);
    };

    const handleSubmitCreate = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!title.trim()) {
            setError('Por favor ingresa un título');
            return;
        }

        try {
            const data: GoogleResourceCreate = {
                type: selectedType,
                title: title.trim(),
                share_with_teacher: true,
            };

            const result = await createResource(data);

            if (onResourceCreated) {
                onResourceCreated(result.resource);
            }

            // Abrir el recurso en nueva pestaña
            if (result.resource?.url) {
                window.open(result.resource.url, '_blank');
            }

            onClose();
        } catch (err: any) {
            setError(err.message || 'Error al crear recurso');
        }
    };

    const getTypeLabel = (type: string) => {
        const labels: Record<string, string> = {
            document: 'Documento',
            spreadsheet: 'Hoja de cálculo',
            presentation: 'Presentación',
            drawing: 'Dibujo',
            form: 'Formulario',
        };
        return labels[type] || type;
    };

    console.log('🔴 GoogleWorkspaceModal render - showCreateForm:', showCreateForm, 'selectedType:', selectedType);

    useEffect(() => {
        console.log('✅ GoogleWorkspaceModal MOUNTED');
        return () => console.log('❌ GoogleWorkspaceModal UNMOUNTED');
    }, []);

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={(e) => {
            console.log('🟣 Modal overlay clicked');
            if (e.target === e.currentTarget) {
                onClose();
            }
        }}>
            <div className="bg-white dark:bg-zinc-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between sticky top-0 bg-white dark:bg-zinc-800 z-10">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                        Agregar o crear
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6">
                    {!showCreateForm ? (
                        <div className="space-y-6">
                            <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-zinc-900/40 p-3 text-sm flex items-center justify-between gap-3">
                                {isCheckingAuth ? (
                                    <span className="text-gray-600 dark:text-gray-300 flex items-center gap-2">
                                        <Loader2 className="w-4 h-4 animate-spin" /> Verificando tu cuenta de Google...
                                    </span>
                                ) : canUseGoogleWorkspace ? (
                                    <span className="text-green-600 dark:text-green-400 text-left">
                                        Cuenta de Google conectada {oauthStatus?.provider_email ? `(${oauthStatus.provider_email})` : ''}
                                    </span>
                                ) : needsReconnect ? (
                                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between w-full gap-2">
                                        <p className="text-amber-600 dark:text-amber-400 text-left">
                                            Tu conexión con Google caducó. Reautoriza para seguir creando documentos.
                                        </p>
                                        <button
                                            type="button"
                                            onClick={onConnectGoogle}
                                            className="px-3 py-1.5 rounded-lg bg-amber-500 text-white text-xs font-medium hover:bg-amber-600"
                                        >
                                            Re-vincular Google
                                        </button>
                                    </div>
                                ) : (
                                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between w-full gap-2">
                                        <p className="text-red-600 dark:text-red-400 text-left">
                                            Necesitas vincular tu cuenta de Google para crear documentos compartidos.
                                        </p>
                                        <button
                                            type="button"
                                            onClick={onConnectGoogle}
                                            className="px-3 py-1.5 rounded-lg bg-red-600 text-white text-xs font-medium hover:bg-red-700"
                                        >
                                            Conectar con Google
                                        </button>
                                    </div>
                                )}
                            </div>

                            {/* Sección: Subir */}
                            <div>
                                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-3">
                                    Subir
                                </h3>
                                <div className="grid grid-cols-2 gap-3">
                                    <OptionCard
                                        icon={<Upload className="w-full h-full" />}
                                        title="Archivo"
                                        color="blue"
                                        onClick={() => {
                                            console.log('📎 Subir archivo clicked');
                                            onFileUpload?.();
                                            onClose();
                                        }}
                                    />
                                    <OptionCard
                                        icon={<LinkIcon className="w-full h-full" />}
                                        title="Enlace"
                                        color="green"
                                        onClick={() => {
                                            console.log('🔗 Agregar enlace clicked');
                                            onLinkAdd?.();
                                            onClose();
                                        }}
                                    />
                                </div>
                            </div>

                            {/* Sección: Google Drive */}
                            <div>
                                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-3">
                                    Google Drive
                                </h3>
                                <div className="grid grid-cols-1 gap-3">
                                    <OptionCard
                                        icon={<FolderOpen className="w-full h-full" />}
                                        title="Seleccionar de Drive"
                                        color="yellow"
                                        onClick={() => {
                                            if (!canUseGoogleWorkspace) {
                                                setError('Conecta tu cuenta de Google para acceder a Drive.');
                                                return;
                                            }
                                            console.log('📁 Seleccionar de Drive - Funcionalidad pendiente');
                                            // TODO: Implementar selector de Drive
                                        }}
                                        disabled={!canUseGoogleWorkspace}
                                    />
                                </div>
                            </div>

                            {/* Sección: Crear */}
                            <div>
                                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-3">
                                    Crear nuevo
                                </h3>
                                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                                    <OptionCard
                                        icon={<FileText className="w-full h-full" />}
                                        title="Documento"
                                        color="blue"
                                        onClick={() => handleCreate('document')}
                                        disabled={isCreating || !canUseGoogleWorkspace}
                                    />
                                    <OptionCard
                                        icon={<Table className="w-full h-full" />}
                                        title="Hoja de cálculo"
                                        color="green"
                                        onClick={() => handleCreate('spreadsheet')}
                                        disabled={isCreating || !canUseGoogleWorkspace}
                                    />
                                    <OptionCard
                                        icon={<Presentation className="w-full h-full" />}
                                        title="Presentación"
                                        color="yellow"
                                        onClick={() => handleCreate('presentation')}
                                        disabled={isCreating || !canUseGoogleWorkspace}
                                    />
                                    <OptionCard
                                        icon={<Pencil className="w-full h-full" />}
                                        title="Dibujo"
                                        color="red"
                                        onClick={() => handleCreate('drawing')}
                                        disabled={isCreating || !canUseGoogleWorkspace}
                                    />
                                    <OptionCard
                                        icon={<FormInput className="w-full h-full" />}
                                        title="Formulario"
                                        color="purple"
                                        onClick={() => handleCreate('form')}
                                        disabled={isCreating || !canUseGoogleWorkspace}
                                    />
                                </div>
                            </div>
                        </div>
                    ) : (
                        // Formulario de creación
                        <form onSubmit={handleSubmitCreate} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Crear {getTypeLabel(selectedType)}
                                </label>
                                <input
                                    type="text"
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    placeholder="Título del documento..."
                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent"
                                    autoFocus
                                    disabled={isCreating}
                                />
                            </div>

                            {error && (
                                <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300 text-sm">
                                    {error}
                                </div>
                            )}

                            <div className="flex gap-3">
                                <button
                                    type="button"
                                    onClick={() => {
                                        setShowCreateForm(false);
                                        setTitle('');
                                        setError(null);
                                    }}
                                    className="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-zinc-700 transition-colors"
                                    disabled={isCreating}
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    disabled={isCreating}
                                    className="flex-1 px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors font-medium disabled:opacity-50 flex items-center justify-center gap-2"
                                >
                                    {isCreating ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                            Creando...
                                        </>
                                    ) : (
                                        'Crear'
                                    )}
                                </button>
                            </div>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
}
