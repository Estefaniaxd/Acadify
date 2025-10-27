"""
Generador de token válido para usuario específico
Ejecutar desde el backend para obtener un token que funcione en el frontend
"""

import sys
import os
sys.path.append('.')

from src.db.session import SessionLocal
from sqlalchemy import text
from src.core.config import settings
import jwt
from datetime import datetime, timedelta

def generar_token_usuario():
    """Genera token válido para el usuario que creó comentarios"""
    db = SessionLocal()
    
    try:
        # Buscar el usuario que creó comentarios (estefania londoño)
        user_result = db.execute(text('''
            SELECT u.usuario_id, u.nombres, u.apellidos, u.correo_institucional, u.rol
            FROM "Usuario" u
            JOIN "Comentario" c ON u.usuario_id = c.autor_id
            WHERE c.contenido = 'hola'
            LIMIT 1
        ''')).fetchone()
        
        if not user_result:
            print("❌ Usuario no encontrado")
            return None
            
        user_id, nombres, apellidos, email, rol = user_result
        
        # Crear token válido CON TODOS los campos requeridos
        payload = {
            'sub': str(user_id),           # ID del usuario
            'name': nombres,               # Nombre
            'last_name': apellidos,        # Apellido
            'email': email,                # Email
            'test_user': False,            # No es usuario de prueba
            'role': rol,                   # Rol (docente)
            'type': 'access',              # CAMPO REQUERIDO por la validación
            'exp': datetime.utcnow() + timedelta(hours=24),  # Expira en 24 horas
            'iat': datetime.utcnow(),      # Emitido ahora
            'jti': f'{user_id}-{int(datetime.utcnow().timestamp())}'  # ID único del token
        }
        
        # Generar token usando la clave secreta del sistema
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        print("=" * 80)
        print("🔑 TOKEN VÁLIDO GENERADO")
        print("=" * 80)
        print(f"👤 Usuario: {nombres} {apellidos}")
        print(f"📧 Email: {email}")
        print(f"🎯 Rol: {rol}")
        print(f"⏰ Válido por: 24 horas")
        print(f"🆔 User ID: {user_id}")
        print()
        print("🔗 INSTRUCCIONES:")
        print("1. Copia el token de abajo")
        print("2. Abre las herramientas de desarrollador del navegador (F12)")
        print("3. Ve a Application > Local Storage > http://localhost:5173")
        print("4. Busca la clave 'access_token' o créala si no existe")
        print("5. Pega el token como valor")
        print("6. Recarga la página")
        print()
        print("📝 TOKEN (copia este texto completo):")
        print("-" * 80)
        print(token)
        print("-" * 80)
        
        return token
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Generando token válido para pruebas...")
    print()
    generar_token_usuario()