/**
 * Botón de Login con Google
 * 
 * Componente que inicia el flujo de OAuth con Google
 */

import { FcGoogle } from 'react-icons/fc';
import { oauthService } from '../../services/oauth.service';

interface GoogleLoginButtonProps {
    text?: string;
    className?: string;
    disabled?: boolean;
}

export const GoogleLoginButton: React.FC<GoogleLoginButtonProps> = ({
    text = 'Continuar con Google',
    className = '',
    disabled = false,
}) => {
    const handleGoogleLogin = () => {
        oauthService.initiateGoogleLogin();
    };

    return (
        <button
            onClick={handleGoogleLogin}
            disabled={disabled}
            className={`
        flex items-center justify-center gap-3 w-full
        px-4 py-3 rounded-lg border-2 border-gray-300
        bg-white hover:bg-gray-50 
        transition-all duration-200
        font-medium text-gray-700
        disabled:opacity-50 disabled:cursor-not-allowed
        hover:shadow-md
        ${className}
      `}
        >
            <FcGoogle className="text-2xl" />
            <span>{text}</span>
        </button>
    );
};

export default GoogleLoginButton;
