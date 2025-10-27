from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from src.core.config import get_settings

router = APIRouter(prefix="/dev-email", tags=["development-email"])
settings = get_settings()

@router.get("/confirm-login/{user_id}", response_class=HTMLResponse)
async def confirm_login_security(user_id: str, request: Request):
    """Página de desarrollo para confirmar login de seguridad"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Confirmación de Login - Acadify Dev</title>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0; padding: 40px 20px; min-height: 100vh;
                display: flex; align-items: center; justify-content: center;
            }}
            .container {{ 
                background: white; padding: 40px; border-radius: 20px;
                box-shadow: 0 20px 50px rgba(0,0,0,0.1); max-width: 500px; text-align: center;
            }}
            .success {{ color: #059669; font-size: 64px; margin-bottom: 20px; }}
            h1 {{ color: #1f2937; margin-bottom: 10px; }}
            .info {{ color: #6b7280; margin-bottom: 30px; }}
            .details {{ background: #f9fafb; padding: 20px; border-radius: 12px; margin: 20px 0; }}
            .back-btn {{ 
                display: inline-block; padding: 12px 24px; background: #667eea;
                color: white; text-decoration: none; border-radius: 8px; margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success">✅</div>
            <h1>Login Confirmado</h1>
            <p class="info">Has confirmado que el login fue autorizado por ti.</p>
            
            <div class="details">
                <strong>🔒 Modo Desarrollo</strong><br>
                Usuario ID: {user_id}<br>
                Esta es una página de prueba para desarrollo.<br>
                En producción, esto registraría la confirmación en la base de datos.
            </div>
            
            <p>✨ En producción, esto:</p>
            <ul style="text-align: left; color: #4b5563;">
                <li>Marcaría el login como confirmado</li>
                <li>Actualizaría el estado de seguridad</li>
                <li>Enviaría confirmación al equipo de seguridad</li>
                <li>Registraría la acción en los logs</li>
            </ul>
            
            <a href="javascript:window.close()" class="back-btn">Cerrar ventana</a>
        </div>
    </body>
    </html>
    """
    
    return html_content

@router.get("/report-login/{user_id}", response_class=HTMLResponse)
async def report_suspicious_login(user_id: str, request: Request):
    """Página de desarrollo para reportar login sospechoso"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reporte de Seguridad - Acadify Dev</title>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
                margin: 0; padding: 40px 20px; min-height: 100vh;
                display: flex; align-items: center; justify-content: center;
            }}
            .container {{ 
                background: white; padding: 40px; border-radius: 20px;
                box-shadow: 0 20px 50px rgba(0,0,0,0.1); max-width: 500px; text-align: center;
            }}
            .alert {{ color: #dc2626; font-size: 64px; margin-bottom: 20px; }}
            h1 {{ color: #1f2937; margin-bottom: 10px; }}
            .info {{ color: #6b7280; margin-bottom: 30px; }}
            .details {{ background: #fef2f2; padding: 20px; border-radius: 12px; margin: 20px 0; }}
            .actions {{ 
                background: #f0fdf4; padding: 20px; border-radius: 12px; margin: 20px 0;
                border-left: 4px solid #059669;
            }}
            .back-btn {{ 
                display: inline-block; padding: 12px 24px; background: #dc2626;
                color: white; text-decoration: none; border-radius: 8px; margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="alert">🚨</div>
            <h1>Login Reportado</h1>
            <p class="info">Has reportado este login como sospechoso.</p>
            
            <div class="details">
                <strong>⚠️ Modo Desarrollo</strong><br>
                Usuario ID: {user_id}<br>
                Esta es una página de prueba para desarrollo.<br>
                En producción, esto activaría el protocolo de seguridad.
            </div>
            
            <div class="actions">
                <p><strong>🛡️ Acciones que se tomarían en producción:</strong></p>
                <ul style="text-align: left; color: #374151;">
                    <li>🔒 Bloqueo inmediato de la sesión sospechosa</li>
                    <li>📧 Notificación al equipo de seguridad</li>
                    <li>🔑 Forzar cambio de contraseña</li>
                    <li>📱 Activar verificación 2FA si no está activa</li>
                    <li>📊 Registro en sistema de auditoría</li>
                    <li>🚨 Alerta de seguridad a otros usuarios si es necesario</li>
                </ul>
            </div>
            
            <p style="color: #059669; font-weight: bold;">✅ Tu cuenta está ahora más segura</p>
            
            <a href="javascript:window.close()" class="back-btn">Cerrar ventana</a>
        </div>
    </body>
    </html>
    """
    
    return html_content

@router.get("/account-action/{action_type}/{user_id}", response_class=HTMLResponse)
async def generic_account_action(action_type: str, user_id: str, request: Request):
    """Página genérica para otras acciones de cuenta en desarrollo"""
    
    action_configs = {
        "restore": {
            "icon": "🔄",
            "title": "Cuenta Restaurada",
            "color": "#059669",
            "bg": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
            "message": "Tu cuenta ha sido restaurada exitosamente."
        },
        "support": {
            "icon": "🎧", 
            "title": "Soporte Contactado",
            "color": "#3b82f6",
            "bg": "linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)",
            "message": "Tu solicitud de soporte ha sido registrada."
        },
        "security": {
            "icon": "🛡️",
            "title": "Configuración de Seguridad", 
            "color": "#8b5cf6",
            "bg": "linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%)",
            "message": "Configuración de seguridad actualizada."
        }
    }
    
    config = action_configs.get(action_type, {
        "icon": "ℹ️", "title": "Acción Ejecutada", "color": "#6b7280",
        "bg": "linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)",
        "message": f"Acción '{action_type}' ejecutada."
    })
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{config['title']} - Acadify Dev</title>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: {config['bg']};
                margin: 0; padding: 40px 20px; min-height: 100vh;
                display: flex; align-items: center; justify-content: center;
            }}
            .container {{ 
                background: white; padding: 40px; border-radius: 20px;
                box-shadow: 0 20px 50px rgba(0,0,0,0.1); max-width: 500px; text-align: center;
            }}
            .icon {{ color: {config['color']}; font-size: 64px; margin-bottom: 20px; }}
            h1 {{ color: #1f2937; margin-bottom: 10px; }}
            .details {{ background: #f9fafb; padding: 20px; border-radius: 12px; margin: 20px 0; }}
            .back-btn {{ 
                display: inline-block; padding: 12px 24px; background: {config['color']};
                color: white; text-decoration: none; border-radius: 8px; margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">{config['icon']}</div>
            <h1>{config['title']}</h1>
            <p>{config['message']}</p>
            
            <div class="details">
                <strong>🔧 Modo Desarrollo</strong><br>
                Acción: {action_type}<br>
                Usuario ID: {user_id}<br>
                Timestamp: {{"{{ datetime.now() }}"}}<br><br>
                Esta es una página de prueba para desarrollo.
            </div>
            
            <a href="javascript:window.close()" class="back-btn">Cerrar ventana</a>
        </div>
    </body>
    </html>
    """
    
    return html_content