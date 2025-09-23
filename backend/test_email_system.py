#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema de email
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

async def test_email_service():
    """Probar el envío de emails con templates"""
    
    print("=== PRUEBA DEL SISTEMA DE EMAIL ===\n")
    
    # 1. Verificar configuración
    settings = get_settings()
    print("🔧 Configuración SMTP:")
    print(f"   Host: {settings.SMTP_HOST}")
    print(f"   Puerto: {settings.SMTP_PORT}")
    print(f"   Usuario: {settings.SMTP_USER}")
    print(f"   TLS: {settings.SMTP_TLS}")
    print(f"   Email From: {settings.EMAIL_FROM}")
    print(f"   Templates Dir: {settings.EMAIL_TEMPLATES_DIR}")
    
    # Verificar si hay configuración válida
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        print("❌ ERROR: Credenciales SMTP no configuradas")
        return False
    
    print("✅ Configuración SMTP parece válida\n")
    
    # 2. Probar instancia del servicio
    try:
        email_service = get_email_service()
        print("✅ EmailService instanciado correctamente\n")
    except Exception as e:
        print(f"❌ ERROR instanciando EmailService: {e}")
        return False
    
    # 3. Verificar templates disponibles
    templates_path = backend_dir / settings.EMAIL_TEMPLATES_DIR
    print(f"📁 Verificando templates en: {templates_path}")
    
    if not templates_path.exists():
        print(f"❌ ERROR: Directorio de templates no existe: {templates_path}")
        return False
    
    templates = list(templates_path.glob("*.html"))
    print(f"📄 Templates encontrados: {len(templates)}")
    for template in templates:
        print(f"   - {template.name}")
    print()
    
    # 4. Probar envío de email de prueba
    test_email = "test@example.com"  # Cambiar por email real para prueba
    
    try:
        print(f"📧 Probando envío de email a: {test_email}")
        
        # Usar template de verificación como prueba
        await email_service.send_template_email(
            to_email=test_email,
            subject="Prueba del sistema de email - Acadify",
            template_name="verify_email.html",
            context={
                "nombre": "Usuario de Prueba",
                "codigo": "123456",
                "enlace_verificacion": "https://acadify.com/verify?code=123456",
                "valido_hasta": "1 hora"
            }
        )
        
        print("✅ Email enviado exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR enviando email: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        
        # Detalles adicionales
        if hasattr(e, '__cause__') and e.__cause__:
            print(f"   Causa: {e.__cause__}")
        
        return False

async def test_template_rendering():
    """Probar renderizado de templates sin envío"""
    
    print("\n=== PRUEBA DE RENDERIZADO DE TEMPLATES ===\n")
    
    try:
        email_service = get_email_service()
        
        # Probar renderizado del template
        template = email_service.template_env.get_template("verify_email.html")
        html_content = template.render(
            nombre="Usuario de Prueba",
            codigo="123456", 
            enlace_verificacion="https://acadify.com/verify?code=123456",
            valido_hasta="1 hora"
        )
        
        print("✅ Template renderizado correctamente")
        print(f"📝 Longitud del HTML: {len(html_content)} caracteres")
        
        # Mostrar primeras líneas del HTML
        lines = html_content.split('\n')[:10]
        print("📄 Primeras líneas del HTML:")
        for i, line in enumerate(lines, 1):
            if line.strip():
                print(f"   {i:2d}: {line.strip()[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR renderizando template: {e}")
        return False

def check_dependencies():
    """Verificar dependencias necesarias"""
    
    print("\n=== VERIFICACIÓN DE DEPENDENCIAS ===\n")
    
    required_modules = [
        "aiosmtplib",
        "jinja2", 
        "email.mime.text",
        "email.mime.multipart"
    ]
    
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - NO DISPONIBLE")
            missing.append(module)
    
    if missing:
        print(f"\n🚨 Dependencias faltantes: {', '.join(missing)}")
        print("💡 Instalar con: pip install aiosmtplib jinja2")
        return False
    
    print("\n✅ Todas las dependencias están disponibles")
    return True

async def main():
    """Función principal de prueba"""
    
    print("🧪 DIAGNÓSTICO DEL SISTEMA DE EMAIL DE ACADIFY\n")
    
    # 1. Verificar dependencias
    deps_ok = check_dependencies()
    if not deps_ok:
        return
    
    # 2. Probar renderizado de templates
    template_ok = await test_template_rendering()
    if not template_ok:
        return
    
    # 3. Probar envío de email (comentado para evitar spam)
    # email_ok = await test_email_service()
    
    print("\n🎉 DIAGNÓSTICO COMPLETADO")
    print("💡 Para probar envío real, descomenta la línea email_ok y configura un email válido")

if __name__ == "__main__":
    asyncio.run(main())