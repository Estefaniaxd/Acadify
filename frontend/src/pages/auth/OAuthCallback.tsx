/**
 * Página de Callback de OAuth
 * 
 * Maneja el callback de Google después de la autorización
 * Procesa el código de autorización y completa el login
 */

import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { oauthService } from '../../services/oauth.service';
import { useAuth } from '../../context/AuthContext';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

export const OAuthCallback: React.FC = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { login } = useAuth();
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [message, setMessage] = useState('Procesando autenticación...');

    useEffect(() => {
        const handleCallback = async () => {
            const token = searchParams.get('token');
            const email = searchParams.get('email');
            const isNewUser = searchParams.get('new_user') === 'true';
            const error = searchParams.get('error');

            // Si hay error de Google
            if (error) {
                setStatus('error');
                setMessage('Autenticación cancelada o error de Google');
                setTimeout(() => navigate('/login'), 3000);
                return;
            }

            // Si no hay token
            if (!token) {
                setStatus('error');
                setMessage('No se recibió token de autenticación');
                setTimeout(() => navigate('/login'), 3000);
                return;
            }

            try {
                setStatus('success');
                setMessage(isNewUser ? '¡Cuenta creada exitosamente!' : '¡Login exitoso!');

                // Guardar el token en localStorage y actualizar contexto inmediatamente
                console.log('OAuthCallback: Saving token to localStorage and calling login()', { token: token.substring(0, 10) + '...' });
                localStorage.setItem('access_token', token);
                login(token);
                console.log('OAuthCallback: login() called');

                // Obtener información del usuario (opcional) para tenerla disponible en el cliente
                try {
                    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
                    const userResponse = await fetch(`${apiUrl}/auth/me`, {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    if (userResponse.ok) {
                        const userData = await userResponse.json();
                        localStorage.setItem('user_profile', JSON.stringify(userData));
                    }
                } catch (error) {
                    console.error('Error obteniendo usuario:', error);
                } finally {
                    // Redirigir al dashboard independientemente del resultado
                    setTimeout(() => {
                        navigate('/dashboard');
                    }, 1500);
                }
            } catch (error: any) {
                console.error('Error en callback:', error);
                setStatus('error');
                setMessage('Error al procesar la autenticación');
                setTimeout(() => navigate('/login'), 4000);
            }
        };

        handleCallback();
    }, [searchParams, navigate, login]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
            <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full">
                <div className="flex flex-col items-center gap-4">
                    {status === 'loading' && (
                        <>
                            <Loader2 className="w-16 h-16 text-blue-600 animate-spin" />
                            <h2 className="text-2xl font-bold text-gray-800">Autenticando...</h2>
                            <p className="text-gray-600 text-center">{message}</p>
                        </>
                    )}

                    {status === 'success' && (
                        <>
                            <CheckCircle className="w-16 h-16 text-green-600" />
                            <h2 className="text-2xl font-bold text-gray-800">¡Éxito!</h2>
                            <p className="text-gray-600 text-center">{message}</p>
                            <p className="text-sm text-gray-500">Redirigiendo...</p>
                        </>
                    )}

                    {status === 'error' && (
                        <>
                            <XCircle className="w-16 h-16 text-red-600" />
                            <h2 className="text-2xl font-bold text-gray-800">Error</h2>
                            <p className="text-gray-600 text-center">{message}</p>
                            <p className="text-sm text-gray-500">Redirigiendo al login...</p>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default OAuthCallback;
