/**
 * Componente de Vinculación de Cuenta de Google
 * 
 * Permite a los usuarios vincular/desvincular su cuenta de Google
 * desde su perfil de usuario
 */

import { useState, useEffect } from 'react';
import { FcGoogle } from 'react-icons/fc';
import { Link2, Unlink, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { oauthService, OAuthStatus } from '../../services/oauth.service';

interface GoogleAccountLinkProps {
    accessToken: string;
}

export const GoogleAccountLink: React.FC<GoogleAccountLinkProps> = ({ accessToken }) => {
    const [status, setStatus] = useState<OAuthStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
    const needsRelink = Boolean(status?.needs_relink || status?.has_credentials === false);

    // Cargar estado de vinculación
    useEffect(() => {
        loadStatus();
    }, []);

    const loadStatus = async () => {
        try {
            setLoading(true);
            const statusData = await oauthService.getGoogleStatus(accessToken);
            setStatus(statusData);
        } catch (error) {
            console.error('Error al cargar estado:', error);
            setMessage({ type: 'error', text: 'Error al cargar el estado de vinculación' });
        } finally {
            setLoading(false);
        }
    };

    const handleLink = () => {
        const redirectUrl = window.location.href;
        const linkUrl = oauthService.getGoogleLinkUrl(redirectUrl);
        window.location.href = linkUrl;
    };

    const handleUnlink = async () => {
        if (!confirm('¿Estás seguro de que deseas desvincular tu cuenta de Google?')) {
            return;
        }

        try {
            setActionLoading(true);
            const response = await oauthService.unlinkGoogleAccount(accessToken);

            if (response.success) {
                setMessage({ type: 'success', text: 'Cuenta de Google desvinculada exitosamente' });
                await loadStatus(); // Recargar estado
            }
        } catch (error: any) {
            console.error('Error al desvincular:', error);
            setMessage({
                type: 'error',
                text: error.response?.data?.detail || 'Error al desvincular la cuenta'
            });
        } finally {
            setActionLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center p-6">
                <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-4">
                <FcGoogle className="text-3xl" />
                <div>
                    <h3 className="text-lg font-semibold text-gray-800">Cuenta de Google</h3>
                    <p className="text-sm text-gray-600">
                        {status?.is_linked
                            ? 'Tu cuenta está vinculada con Google'
                            : 'Vincula tu cuenta de Google para acceso rápido'}
                    </p>
                </div>
            </div>

            {message && (
                <div className={`
          mb-4 p-3 rounded-lg flex items-center gap-2
          ${message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}
        `}>
                    {message.type === 'success' ? (
                        <CheckCircle className="w-5 h-5" />
                    ) : (
                        <AlertCircle className="w-5 h-5" />
                    )}
                    <span className="text-sm">{message.text}</span>
                </div>
            )}

            {status?.is_linked ? (
                <div className="space-y-4">
                    {needsRelink ? (
                        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                            <div className="flex items-center gap-2 text-amber-800 mb-2">
                                <AlertCircle className="w-5 h-5" />
                                <span className="font-medium">Vuelve a autorizar Google</span>
                            </div>
                            <p className="text-sm text-amber-700">
                                Tu vínculo con Google caducó o no tiene permisos suficientes. Reautoriza para seguir usando Google Workspace.
                            </p>
                            <button
                                onClick={handleLink}
                                className="mt-3 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500 text-white text-sm font-medium hover:bg-amber-600"
                            >
                                <Link2 className="w-4 h-4" />
                                Re-vincular cuenta de Google
                            </button>
                        </div>
                    ) : (
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                            <div className="flex items-center gap-2 text-green-800 mb-2">
                                <CheckCircle className="w-5 h-5" />
                                <span className="font-medium">Cuenta vinculada</span>
                            </div>
                            <p className="text-sm text-green-700">
                                Email: <span className="font-medium">{status.provider_email}</span>
                            </p>
                            {status.linked_at && (
                                <p className="text-xs text-green-600 mt-1">
                                    Vinculada el {new Date(status.linked_at).toLocaleDateString('es-ES', {
                                        year: 'numeric',
                                        month: 'long',
                                        day: 'numeric'
                                    })}
                                </p>
                            )}
                        </div>
                    )}

                    <button
                        onClick={handleUnlink}
                        disabled={actionLoading}
                        className="
              flex items-center justify-center gap-2 w-full
              px-4 py-2 rounded-lg
              bg-red-50 hover:bg-red-100
              text-red-700 font-medium
              transition-colors duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
            "
                    >
                        {actionLoading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <Unlink className="w-5 h-5" />
                        )}
                        <span>Desvincular cuenta de Google</span>
                    </button>
                </div>
            ) : (
                <button
                    onClick={handleLink}
                    disabled={actionLoading}
                    className="
            flex items-center justify-center gap-2 w-full
            px-4 py-3 rounded-lg
            bg-blue-600 hover:bg-blue-700
            text-white font-medium
            transition-colors duration-200
            disabled:opacity-50 disabled:cursor-not-allowed
          "
                >
                    {actionLoading ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                        <Link2 className="w-5 h-5" />
                    )}
                    <span>Vincular cuenta de Google</span>
                </button>
            )}

            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-xs text-blue-800">
                    <strong>Beneficios:</strong> Acceso rápido con Google, integración con Google Drive para tareas,
                    y sincronización de documentos.
                </p>
            </div>
        </div>
    );
};

export default GoogleAccountLink;
