#!/usr/bin/env python3
"""Simple test para verificar la funcionalidad básica del email"""

print("=== TEST SIMPLE DE EMAIL ===")

# 1. Test de importaciones
print("\n1. Verificando importaciones...")
try:
    import aiosmtplib
    print("✅ aiosmtplib importado correctamente")
except ImportError as e:
    print(f"❌ Error importando aiosmtplib: {e}")

try:
    from jinja2 import Environment, FileSystemLoader
    print("✅ jinja2 importado correctamente")
except ImportError as e:
    print(f"❌ Error importando jinja2: {e}")

try:
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    print("✅ email.mime importado correctamente")
except ImportError as e:
    print(f"❌ Error importando email.mime: {e}")

# 2. Test de template básico
print("\n2. Verificando template básico...")
try:
    template_content = """
    <html>
    <body>
        <h1>Hola {{ nombre }}!</h1>
        <p>Este es un email de prueba con código: {{ codigo }}</p>
    </body>
    </html>
    """
    
    from jinja2 import Template
    template = Template(template_content)
    result = template.render(nombre="Usuario", codigo="123456")
    
    print("✅ Template renderizado correctamente")
    print(f"   Longitud: {len(result)} caracteres")
    
except Exception as e:
    print(f"❌ Error renderizando template: {e}")

# 3. Test de configuración mínima
print("\n3. Verificando estructura básica de email...")
try:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Test"
    msg["From"] = "test@acadify.com"
    msg["To"] = "user@example.com"
    
    html_part = MIMEText("<h1>Test</h1>", "html", "utf-8")
    msg.attach(html_part)
    
    print("✅ Estructura de email creada correctamente")
    
except Exception as e:
    print(f"❌ Error creando estructura de email: {e}")

print("\n=== TEST COMPLETADO ===")