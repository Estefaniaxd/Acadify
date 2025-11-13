#!/usr/bin/env python3
"""
Test Email Service - Verificar envío de emails
"""
import asyncio
import sys
from src.services.auth.email_service import EmailService
from src.core.config import settings

def test_email_config():
    """Verificar configuración de email"""
    print("=" * 60)
    print("📧 CONFIGURACIÓN DE EMAIL")
    print("=" * 60)
    print(f"SMTP Host: {settings.SMTP_HOST}")
    print(f"SMTP Port: {settings.SMTP_PORT}")
    print(f"SMTP User: {settings.SMTP_USER or '❌ NO CONFIGURADO'}")
    print(f"SMTP Pass: {'✅ Configurado' if settings.SMTP_PASS else '❌ NO CONFIGURADO'}")
    print(f"Email From: {settings.EMAIL_FROM}")
    print()
    
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        print("⚠️  SMTP no está configurado. El envío de emails fallará.")
        print()
        print("Para configurar:")
        print("1. Crea un archivo .env en la raíz del proyecto")
        print("2. Agrega:")
        print("   SMTP_USER=tu_email@gmail.com")
        print("   SMTP_PASS=tu_app_password")
        print()
        return False
    return True

async def test_send_email(to_email: str):
    """Probar envío de email de verificación"""
    print("=" * 60)
    print("📨 PROBANDO ENVÍO DE EMAIL")
    print("=" * 60)
    print(f"Destinatario: {to_email}")
    print()
    
    email_service = EmailService()
    
    # Crear contenido HTML simple
    verification_code = "123456"
    subject = "Test - Verificación de cuenta Acadify"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #4A90E2;">🎓 Verificación de cuenta - Acadify</h2>
            <p>Hola,</p>
            <p>Este es un <strong>email de prueba</strong> del sistema Acadify.</p>
            <p>Tu código de verificación es:</p>
            <div style="background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; margin: 20px 0;">
                {verification_code}
            </div>
            <p>Este código expira en 1 hora.</p>
            <br>
            <p style="color: #666; font-size: 12px;">
                Si no solicitaste este email, ignóralo.
            </p>
        </body>
    </html>
    """
    
    print("⏳ Enviando email...")
    try:
        # Usar el método asíncrono
        await email_service.send_email_async(to_email, subject, html_content)
        print("✅ Email enviado exitosamente!")
        print()
        print(f"📬 Revisa tu bandeja de entrada: {to_email}")
        print("   (También revisa la carpeta de spam)")
        return True
    except Exception as e:
        print(f"❌ Error al enviar email: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 60)
    print("🧪 TEST DE SERVICIO DE EMAIL")
    print("=" * 60 + "\n")
    
    # 1. Verificar configuración
    if not test_email_config():
        sys.exit(1)
    
    # 2. Obtener email de prueba
    test_email_address = "juanitomm2408@gmail.com"
    print(f"Email de prueba: {test_email_address}\n")
    
    # 3. Enviar email de prueba
    asyncio.run(test_send_email(test_email_address))

if __name__ == "__main__":
    main()
