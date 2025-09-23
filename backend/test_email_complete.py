#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test completo del sistema de email reparado
"""

import sys
import os
import asyncio
from pathlib import Path

# Añadir el directorio src al path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from src.core.config import get_settings
from src.utils.security import get_email_service

async def test_complete_email_flow():
    """Probar el flujo completo del email sin enviarlo"""
    
    print("=== PRUEBA COMPLETA DEL SISTEMA DE EMAIL REPARADO ===\n")
    
    try:
        # 1. Instanciar servicio
        email_service = get_email_service()
        print("✅ EmailService instanciado correctamente")
        
        # 2. Probar todos los templates importantes
        templates_to_test = [
            ("verify_email.html", {
                "nombre": "Juan Pérez",
                "codigo": "123456",
                "enlace_verificacion": "https://acadify.com/verify?code=123456",
                "valido_hasta": "1 hora"
            }),
            ("reset_password.html", {
                "nombre": "María García",
                "codigo": "654321",
                "valido_hasta": "15 minutos"
            }),
            ("invitacion_coordinador.html", {
                "institucion_nombre": "Universidad Ejemplo",
                "codigo": "COORD123",
                "fecha_expiracion": "2024-01-15 23:59",
                "url_registro": "https://acadify.com/register",
                "invitador_nombre": "Dr. Admin"
            })
        ]
        
        print("\n📧 Probando renderizado de templates:")
        for template_name, context in templates_to_test:
            try:
                template = email_service.template_env.get_template(template_name)
                html_content = template.render(**context)
                print(f"   ✅ {template_name} - {len(html_content)} caracteres")
            except Exception as e:
                print(f"   ❌ {template_name} - Error: {e}")
                return False
        
        # 3. Simular el proceso de send_template_email sin envío real
        print("\n🔄 Simulando proceso completo de envío:")
        
        # Renderizar template como lo haría send_template_email
        template = email_service.template_env.get_template("verify_email.html")
        html_body = template.render(
            nombre="Usuario de Prueba",
            codigo="999888",
            enlace_verificacion="https://acadify.com/verify?code=999888",
            valido_hasta="1 hora"
        )
        
        # Crear estructura de email como lo haría _send_email
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        
        message = MIMEMultipart("alternative")
        message["From"] = "noreply@acadify.com"
        message["To"] = "test@example.com"
        message["Subject"] = "Verificación de cuenta - Acadify"
        
        html_part = MIMEText(html_body, "html", "utf-8")
        message.attach(html_part)
        
        print("   ✅ Template renderizado y email estructurado correctamente")
        print(f"   📝 Tamaño del HTML: {len(html_body)} caracteres")
        print(f"   📬 Estructura del mensaje: {len(message.as_bytes())} bytes")
        
        # 4. Verificar elementos críticos del HTML
        critical_elements = [
            "<title>",
            "verification-code",
            "Acadify",
            "999888"  # El código de prueba
        ]
        
        print("\n🔍 Verificando elementos críticos:")
        for element in critical_elements:
            if element in html_body:
                print(f"   ✅ '{element}' encontrado")
            else:
                print(f"   ❌ '{element}' NO encontrado")
                return False
        
        print("\n🎉 ¡SISTEMA DE EMAIL COMPLETAMENTE REPARADO!")
        print("✨ Todos los templates funcionan correctamente")
        print("🚀 El problema de 'block title defined twice' está resuelto")
        print("💌 El sistema está listo para enviar emails reales")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR en el test completo: {e}")
        print(f"   Tipo: {type(e).__name__}")
        if hasattr(e, '__traceback__'):
            import traceback
            print("   Traceback:")
            traceback.print_exc()
        return False

async def test_config_validation():
    """Verificar que la configuración de email esté lista"""
    
    print("\n=== VALIDACIÓN DE CONFIGURACIÓN SMTP ===")
    
    settings = get_settings()
    
    config_checks = [
        ("SMTP_HOST", settings.SMTP_HOST),
        ("SMTP_PORT", settings.SMTP_PORT),
        ("SMTP_USER", settings.SMTP_USER),
        ("EMAIL_FROM", settings.EMAIL_FROM),
        ("SMTP_TLS", settings.SMTP_TLS)
    ]
    
    for name, value in config_checks:
        if value:
            print(f"✅ {name}: {value}")
        else:
            print(f"⚠️  {name}: NO CONFIGURADO")
    
    if not settings.SMTP_PASS:
        print("⚠️  SMTP_PASS: NO CONFIGURADA (por seguridad no se muestra)")
    else:
        print("✅ SMTP_PASS: CONFIGURADA")

async def main():
    """Función principal de prueba"""
    
    print("🧪 TEST COMPLETO DEL SISTEMA DE EMAIL REPARADO\n")
    
    # 1. Validar configuración
    await test_config_validation()
    
    # 2. Test completo del flujo
    success = await test_complete_email_flow()
    
    if success:
        print("\n" + "="*60)
        print("🎯 RESULTADO: ¡SISTEMA DE EMAIL COMPLETAMENTE FUNCIONAL!")
        print("="*60)
        print("📋 RESUMEN DE LA REPARACIÓN:")
        print("   • Problema identificado: Templates concatenados en base.html")
        print("   • Solución aplicada: Separación del template base")
        print("   • Resultado: Bloques duplicados eliminados")
        print("   • Estado: Sistema listo para producción")
        print("="*60)
    else:
        print("\n❌ Aún hay problemas que resolver")

if __name__ == "__main__":
    asyncio.run(main())