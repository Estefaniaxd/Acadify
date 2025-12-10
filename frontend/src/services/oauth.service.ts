/**
 * Servicio de OAuth para Google
 * 
 * Maneja la autenticación OAuth con Google incluyendo:
 * - Inicio de sesión con Google
 * - Vinculación de cuentas
 * - Desvinculación de cuentas
 * - Verificación de estado
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface OAuthStatus {
    is_linked: boolean;
    provider: string;
    provider_email?: string;
    linked_at?: string;
    expires_at?: string | null;
    has_credentials?: boolean;
    needs_relink?: boolean;
}

export interface OAuthLinkResponse {
    success: boolean;
    message: string;
    provider: string;
    provider_email: string;
}

export interface OAuthCallbackResponse {
    success: boolean;
    message: string;
    user_email: string;
    is_new_user: boolean;
    access_token: string;
    token_type: string;
}

class OAuthService {
    /**
     * Inicia el flujo de OAuth con Google
     * Redirige al usuario a la página de autorización de Google
     */
    initiateGoogleLogin(): void {
        const loginUrl = `${API_URL}/auth/google/login`;
        window.location.href = loginUrl;
    }

    /**
     * Maneja el callback de Google OAuth
     * @param code - Código de autorización de Google
     * @param state - Estado para validación CSRF
     */
    async handleGoogleCallback(code: string, state?: string): Promise<OAuthCallbackResponse> {
        try {
            const params = new URLSearchParams({ code });
            if (state) {
                params.append('state', state);
            }

            const response = await axios.get<OAuthCallbackResponse>(
                `${API_URL}/auth/google/callback?${params.toString()}`
            );

            return response.data;
        } catch (error) {
            console.error('Error en callback de OAuth:', error);
            throw error;
        }
    }

    /**
     * Vincula una cuenta de Google a un usuario existente
     * @param code - Código de autorización de Google
     * @param accessToken - Token de acceso del usuario actual
     */
    async linkGoogleAccount(code: string, accessToken: string): Promise<OAuthLinkResponse> {
        try {
            const response = await axios.post<OAuthLinkResponse>(
                `${API_URL}/auth/google/link`,
                null,
                {
                    params: { code },
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                }
            );

            return response.data;
        } catch (error) {
            console.error('Error al vincular cuenta de Google:', error);
            throw error;
        }
    }

    /**
     * Desvincula la cuenta de Google del usuario actual
     * @param accessToken - Token de acceso del usuario actual
     */
    async unlinkGoogleAccount(accessToken: string): Promise<{ success: boolean; message: string }> {
        try {
            const response = await axios.delete<{ success: boolean; message: string }>(
                `${API_URL}/auth/google/unlink`,
                {
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                }
            );

            return response.data;
        } catch (error) {
            console.error('Error al desvincular cuenta de Google:', error);
            throw error;
        }
    }

    /**
     * Obtiene el estado de vinculación de Google del usuario actual
     * @param accessToken - Token de acceso del usuario actual
     */
    async getGoogleStatus(accessToken: string): Promise<OAuthStatus> {
        try {
            const response = await axios.get<OAuthStatus>(
                `${API_URL}/auth/google/status`,
                {
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                }
            );

            return response.data;
        } catch (error) {
            console.error('Error al obtener estado de OAuth:', error);
            throw error;
        }
    }

    /**
     * Genera la URL de autorización de Google para vincular cuenta
     * (Similar a initiateGoogleLogin pero para vincular, no para login)
     */
    getGoogleLinkUrl(redirectUrl?: string): string {
        const url = new URL(`${API_URL}/auth/google/login?action=link`);
        if (redirectUrl) {
            url.searchParams.set('redirect_url', redirectUrl);
        }
        return url.toString();
    }
}

export const oauthService = new OAuthService();
export default oauthService;
