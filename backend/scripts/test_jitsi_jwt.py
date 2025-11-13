"""
Script de pruebas para el generador de JWT de Jitsi Meet.

Valida todas las funciones del módulo jitsi_jwt incluyendo:
- Generación de tokens (moderador, participante, custom)
- Validación y decodificación
- Expiración de tokens
- Extracción de información
- Refresh de tokens

Ejecutar:
    python scripts/test_jitsi_jwt.py
"""

import sys
import time
from pathlib import Path
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone

# Añadir directorio raíz al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Imports del sistema
from src.utils.jitsi_jwt import (
    generate_jitsi_token,
    generate_moderator_token,
    generate_participant_token,
    decode_jitsi_token,
    validate_jitsi_token,
    get_token_expiration,
    is_token_expired,
    get_token_room_name,
    get_token_user_id,
    is_moderator_token,
    refresh_jitsi_token,
    generate_test_token,
    now_utc,
)


# ===============================
# Test Data
# ===============================

TEST_USER_ID = UUID("123e4567-e89b-12d3-a456-426614174000")
TEST_ROOM_NAME = "clase-matematicas-101"
TEST_USER_NAME = "Juan Pérez"
TEST_USER_EMAIL = "juan.perez@acadify.com"
TEST_USER_AVATAR = "https://acadify.com/avatars/juan.jpg"


# ===============================
# Test Helpers
# ===============================

def print_test_header(test_name: str):
    """Imprime un header para cada test"""
    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)


def print_success(message: str):
    """Imprime mensaje de éxito"""
    print(f"✅ {message}")


def print_error(message: str):
    """Imprime mensaje de error"""
    print(f"❌ {message}")


def print_info(message: str):
    """Imprime mensaje informativo"""
    print(f"ℹ️  {message}")


# ===============================
# Test Functions
# ===============================

def test_generate_jitsi_token():
    """Test 1: Generación básica de token JWT"""
    print_test_header("Generación básica de token JWT")
    
    try:
        token = generate_jitsi_token(
            user_id=TEST_USER_ID,
            room_name=TEST_ROOM_NAME,
            user_name=TEST_USER_NAME,
            user_email=TEST_USER_EMAIL,
            user_avatar=TEST_USER_AVATAR,
            is_moderator=False,
            expiration_minutes=60
        )
        
        print_success("Token generado correctamente")
        print_info(f"Token (primeros 50 chars): {token[:50]}...")
        print_info(f"Longitud del token: {len(token)} caracteres")
        
        # Validar que el token tiene formato JWT (3 partes separadas por puntos)
        parts = token.split(".")
        if len(parts) == 3:
            print_success("Token tiene formato JWT válido (3 partes)")
        else:
            print_error(f"Token tiene formato inválido: {len(parts)} partes")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error al generar token: {e}")
        return False


def test_decode_token():
    """Test 2: Decodificación de token JWT"""
    print_test_header("Decodificación de token JWT")
    
    try:
        # Generar token
        token = generate_jitsi_token(
            user_id=TEST_USER_ID,
            room_name=TEST_ROOM_NAME,
            user_name=TEST_USER_NAME,
            user_email=TEST_USER_EMAIL,
            user_avatar=TEST_USER_AVATAR,
            is_moderator=True,
            expiration_minutes=60
        )
        
        # Decodificar token
        payload = decode_jitsi_token(token)
        
        print_success("Token decodificado correctamente")
        print_info(f"Room: {payload.get('room')}")
        print_info(f"Moderator: {payload.get('moderator')}")
        print_info(f"User ID: {payload.get('context', {}).get('user', {}).get('id')}")
        print_info(f"User Name: {payload.get('context', {}).get('user', {}).get('name')}")
        
        # Validaciones
        validations = [
            (payload.get('room') == TEST_ROOM_NAME, "Room name correcto"),
            (payload.get('moderator') == True, "Moderator flag correcto"),
            (payload.get('context', {}).get('user', {}).get('id') == str(TEST_USER_ID), "User ID correcto"),
            (payload.get('context', {}).get('user', {}).get('name') == TEST_USER_NAME, "User name correcto"),
            (payload.get('aud') == "acadify", "Audience correcto"),
            (payload.get('iss') == "acadify", "Issuer correcto"),
            ('exp' in payload, "Expiration present"),
            ('iat' in payload, "Issued at present"),
        ]
        
        all_valid = True
        for valid, message in validations:
            if valid:
                print_success(message)
            else:
                print_error(message)
                all_valid = False
        
        return all_valid
    except Exception as e:
        print_error(f"Error al decodificar token: {e}")
        return False


def test_moderator_token():
    """Test 3: Token de moderador con features especiales"""
    print_test_header("Token de moderador con features especiales")
    
    try:
        token = generate_moderator_token(
            user_id=TEST_USER_ID,
            room_name=TEST_ROOM_NAME,
            user_name=TEST_USER_NAME,
            user_email=TEST_USER_EMAIL,
            user_avatar=TEST_USER_AVATAR,
            expiration_minutes=120
        )
        
        payload = decode_jitsi_token(token)
        
        print_success("Token de moderador generado")
        
        # Validar que es moderador
        if payload.get('moderator'):
            print_success("Flag de moderador activado")
        else:
            print_error("Flag de moderador NO activado")
            return False
        
        # Validar features de moderador
        features = payload.get('context', {}).get('features', {})
        
        moderator_features = {
            'recording': True,
            'livestreaming': True,
            'transcription': True,
            'screen-sharing': True,
        }
        
        features_valid = True
        for feature, expected_value in moderator_features.items():
            actual_value = features.get(feature)
            if actual_value == expected_value:
                print_success(f"Feature '{feature}': {actual_value}")
            else:
                print_error(f"Feature '{feature}': expected {expected_value}, got {actual_value}")
                features_valid = False
        
        return features_valid
    except Exception as e:
        print_error(f"Error al generar token de moderador: {e}")
        return False


def test_participant_token():
    """Test 4: Token de participante regular"""
    print_test_header("Token de participante regular")
    
    try:
        token = generate_participant_token(
            user_id=TEST_USER_ID,
            room_name=TEST_ROOM_NAME,
            user_name=TEST_USER_NAME,
            user_email=TEST_USER_EMAIL,
            user_avatar=TEST_USER_AVATAR,
            expiration_minutes=60
        )
        
        payload = decode_jitsi_token(token)
        
        print_success("Token de participante generado")
        
        # Validar que NO es moderador
        if not payload.get('moderator'):
            print_success("No tiene flag de moderador (correcto)")
        else:
            print_error("Tiene flag de moderador (incorrecto)")
            return False
        
        # Validar features de participante (sin permisos administrativos)
        features = payload.get('context', {}).get('features', {})
        
        restricted_features = {
            'recording': False,
            'livestreaming': False,
            'transcription': False,
        }
        
        features_valid = True
        for feature, expected_value in restricted_features.items():
            actual_value = features.get(feature)
            if actual_value == expected_value:
                print_success(f"Feature '{feature}': {actual_value} (sin permisos)")
            else:
                print_error(f"Feature '{feature}': expected {expected_value}, got {actual_value}")
                features_valid = False
        
        return features_valid
    except Exception as e:
        print_error(f"Error al generar token de participante: {e}")
        return False


def test_token_validation():
    """Test 5: Validación de tokens"""
    print_test_header("Validación de tokens")
    
    try:
        # Token válido
        valid_token = generate_jitsi_token(
            user_id=TEST_USER_ID,
            room_name=TEST_ROOM_NAME,
            user_name=TEST_USER_NAME,
            expiration_minutes=60
        )
        
        if validate_jitsi_token(valid_token):
            print_success("Token válido reconocido correctamente")
        else:
            print_error("Token válido rechazado incorrectamente")
            return False
        
        # Token inválido (manipulado)
        invalid_token = valid_token + "manipulated"
        
        if not validate_jitsi_token(invalid_token):
            print_success("Token inválido rechazado correctamente")
        else:
            print_error("Token inválido aceptado incorrectamente")
            return False
        
        # Token completamente inventado
        fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.signature"
        
        if not validate_jitsi_token(fake_token):
            print_success("Token falso rechazado correctamente")
        else:
            print_error("Token falso aceptado incorrectamente")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error en validación de tokens: {e}")
        return False


def test_token_expiration():
    """Test 6: Expiración de tokens"""
    print_test_header("Expiración de tokens")
    
    try:
        # Token con expiración corta (1 minuto)
        short_token = generate_jitsi_token(
            user_id=TEST_USER_ID,
            room_name=TEST_ROOM_NAME,
            user_name=TEST_USER_NAME,
            expiration_minutes=1
        )
        
        # Verificar que no ha expirado inmediatamente
        if not is_token_expired(short_token):
            print_success("Token recién creado no está expirado")
        else:
            print_error("Token recién creado marcado como expirado")
            return False
        
        # Obtener fecha de expiración
        expiration = get_token_expiration(short_token)
        if expiration:
            print_success(f"Expiración: {expiration.isoformat()}")
            
            # Calcular tiempo restante
            now = now_utc()
            time_remaining = (expiration - now).total_seconds()
            print_info(f"Tiempo restante: {time_remaining:.2f} segundos")
            
            if 50 <= time_remaining <= 70:  # ~60 segundos ±10
                print_success("Tiempo de expiración correcto (~60 segundos)")
            else:
                print_error(f"Tiempo de expiración incorrecto: {time_remaining} segundos")
                return False
        else:
            print_error("No se pudo obtener fecha de expiración")
            return False
        
        # Token con expiración muy corta para probar expiración
        print_info("Generando token con expiración de 0 minutos...")
        expired_token = generate_jitsi_token(
            user_id=TEST_USER_ID,
            room_name=TEST_ROOM_NAME,
            user_name=TEST_USER_NAME,
            expiration_minutes=0  # Expira inmediatamente
        )
        
        # Esperar un segundo
        time.sleep(1)
        
        # Verificar que está expirado
        if is_token_expired(expired_token):
            print_success("Token expirado detectado correctamente")
        else:
            print_error("Token expirado NO detectado")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error en prueba de expiración: {e}")
        return False


def test_token_information_extraction():
    """Test 7: Extracción de información del token"""
    print_test_header("Extracción de información del token")
    
    try:
        token = generate_jitsi_token(
            user_id=TEST_USER_ID,
            room_name=TEST_ROOM_NAME,
            user_name=TEST_USER_NAME,
            is_moderator=True,
            expiration_minutes=60
        )
        
        # Extraer room name
        extracted_room = get_token_room_name(token)
        if extracted_room == TEST_ROOM_NAME:
            print_success(f"Room name extraído correctamente: {extracted_room}")
        else:
            print_error(f"Room name incorrecto: expected {TEST_ROOM_NAME}, got {extracted_room}")
            return False
        
        # Extraer user ID
        extracted_user_id = get_token_user_id(token)
        if extracted_user_id == str(TEST_USER_ID):
            print_success(f"User ID extraído correctamente: {extracted_user_id}")
        else:
            print_error(f"User ID incorrecto: expected {TEST_USER_ID}, got {extracted_user_id}")
            return False
        
        # Verificar si es moderador
        if is_moderator_token(token):
            print_success("Token de moderador detectado correctamente")
        else:
            print_error("Token de moderador NO detectado")
            return False
        
        # Verificar con token de participante
        participant_token = generate_participant_token(
            user_id=TEST_USER_ID,
            room_name=TEST_ROOM_NAME,
            user_name=TEST_USER_NAME,
            expiration_minutes=60
        )
        
        if not is_moderator_token(participant_token):
            print_success("Token de participante (no moderador) detectado correctamente")
        else:
            print_error("Token de participante detectado como moderador")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error en extracción de información: {e}")
        return False


def test_token_refresh():
    """Test 8: Refresh de tokens"""
    print_test_header("Refresh de tokens")
    
    try:
        # Generar token original
        original_token = generate_jitsi_token(
            user_id=TEST_USER_ID,
            room_name=TEST_ROOM_NAME,
            user_name=TEST_USER_NAME,
            user_email=TEST_USER_EMAIL,
            is_moderator=True,
            expiration_minutes=60
        )
        
        print_success("Token original generado")
        original_exp = get_token_expiration(original_token)
        print_info(f"Expiración original: {original_exp.isoformat() if original_exp else 'N/A'}")
        
        # Esperar un segundo
        time.sleep(1)
        
        # Refresh token con nueva expiración
        refreshed_token = refresh_jitsi_token(original_token, expiration_minutes=120)
        
        if refreshed_token:
            print_success("Token refrescado correctamente")
            
            refreshed_exp = get_token_expiration(refreshed_token)
            print_info(f"Expiración refrescada: {refreshed_exp.isoformat() if refreshed_exp else 'N/A'}")
            
            # Validar que la nueva expiración es posterior
            if refreshed_exp and original_exp:
                if refreshed_exp > original_exp:
                    print_success("Nueva expiración es posterior a la original")
                    
                    # Calcular diferencia esperada (~60 minutos más)
                    diff_seconds = (refreshed_exp - original_exp).total_seconds()
                    expected_diff = 60 * 60  # 60 minutos
                    
                    if 3500 <= diff_seconds <= 3700:  # ~3600 segundos ±100
                        print_success(f"Diferencia de expiración correcta: {diff_seconds:.0f} segundos (~60 min)")
                    else:
                        print_error(f"Diferencia de expiración incorrecta: {diff_seconds:.0f} segundos")
                        return False
                else:
                    print_error("Nueva expiración NO es posterior")
                    return False
            
            # Validar que mantiene los mismos datos de usuario
            original_payload = decode_jitsi_token(original_token)
            refreshed_payload = decode_jitsi_token(refreshed_token)
            
            if original_payload.get('room') == refreshed_payload.get('room'):
                print_success("Room name mantenido en refresh")
            else:
                print_error("Room name cambió en refresh")
                return False
            
            if original_payload.get('moderator') == refreshed_payload.get('moderator'):
                print_success("Moderator flag mantenido en refresh")
            else:
                print_error("Moderator flag cambió en refresh")
                return False
        else:
            print_error("Refresh retornó None")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error en refresh de token: {e}")
        return False


def test_custom_features():
    """Test 9: Features personalizadas"""
    print_test_header("Features personalizadas")
    
    try:
        custom_features = {
            "recording": True,
            "livestreaming": True,
            "transcription": True,
            "screen-sharing": False,  # Deshabilitado
            "custom-feature": True,  # Feature custom
        }
        
        token = generate_jitsi_token(
            user_id=TEST_USER_ID,
            room_name=TEST_ROOM_NAME,
            user_name=TEST_USER_NAME,
            is_moderator=False,
            expiration_minutes=60,
            features=custom_features
        )
        
        payload = decode_jitsi_token(token)
        actual_features = payload.get('context', {}).get('features', {})
        
        print_success("Token con features personalizadas generado")
        
        # Validar cada feature
        all_valid = True
        for feature, expected_value in custom_features.items():
            actual_value = actual_features.get(feature)
            if actual_value == expected_value:
                print_success(f"Feature '{feature}': {actual_value}")
            else:
                print_error(f"Feature '{feature}': expected {expected_value}, got {actual_value}")
                all_valid = False
        
        return all_valid
    except Exception as e:
        print_error(f"Error en features personalizadas: {e}")
        return False


def test_context_extras():
    """Test 10: Contexto extra personalizado"""
    print_test_header("Contexto extra personalizado")
    
    try:
        context_extras = {
            "group": "grupo-matematicas",
            "institution": "Universidad Nacional",
            "course_id": "MATH101",
            "session_id": str(uuid4()),
        }
        
        token = generate_jitsi_token(
            user_id=TEST_USER_ID,
            room_name=TEST_ROOM_NAME,
            user_name=TEST_USER_NAME,
            is_moderator=False,
            expiration_minutes=60,
            context_extras=context_extras
        )
        
        payload = decode_jitsi_token(token)
        context = payload.get('context', {})
        
        print_success("Token con contexto extra generado")
        
        # Validar cada campo extra
        all_valid = True
        for key, expected_value in context_extras.items():
            actual_value = context.get(key)
            if actual_value == expected_value:
                print_success(f"Context '{key}': {actual_value}")
            else:
                print_error(f"Context '{key}': expected {expected_value}, got {actual_value}")
                all_valid = False
        
        return all_valid
    except Exception as e:
        print_error(f"Error en contexto extra: {e}")
        return False


def test_test_token_utility():
    """Test 11: Función de testing generate_test_token"""
    print_test_header("Función de testing generate_test_token")
    
    try:
        # Generar token de prueba
        test_token = generate_test_token(
            room_name="test-room-123",
            is_moderator=True,
            expiration_minutes=30
        )
        
        print_success("Token de prueba generado")
        
        # Validar que es un token válido
        if validate_jitsi_token(test_token):
            print_success("Token de prueba es válido")
        else:
            print_error("Token de prueba es inválido")
            return False
        
        # Decodificar y verificar
        payload = decode_jitsi_token(test_token)
        
        if payload.get('room') == "test-room-123":
            print_success("Room name correcto en token de prueba")
        else:
            print_error("Room name incorrecto en token de prueba")
            return False
        
        if payload.get('moderator') == True:
            print_success("Moderator flag correcto en token de prueba")
        else:
            print_error("Moderator flag incorrecto en token de prueba")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error en token de prueba: {e}")
        return False


# ===============================
# Main Test Runner
# ===============================

def run_all_tests():
    """Ejecuta todos los tests y reporta resultados"""
    print("\n" + "=" * 70)
    print("🧪 INICIANDO SUITE DE PRUEBAS - JITSI JWT GENERATOR")
    print("=" * 70)
    
    tests = [
        ("Generación básica de token", test_generate_jitsi_token),
        ("Decodificación de token", test_decode_token),
        ("Token de moderador", test_moderator_token),
        ("Token de participante", test_participant_token),
        ("Validación de tokens", test_token_validation),
        ("Expiración de tokens", test_token_expiration),
        ("Extracción de información", test_token_information_extraction),
        ("Refresh de tokens", test_token_refresh),
        ("Features personalizadas", test_custom_features),
        ("Contexto extra", test_context_extras),
        ("Función de testing", test_test_token_utility),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_error(f"Error inesperado en {test_name}: {e}")
            results.append((test_name, False))
            failed += 1
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 70)
    print(f"✅ Tests exitosos: {passed}/{len(tests)}")
    print(f"❌ Tests fallidos: {failed}/{len(tests)}")
    print(f"📊 Tasa de éxito: {(passed / len(tests) * 100):.1f}%")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        print("✅ Generador de JWT Jitsi completamente funcional")
        print("✅ Validaciones funcionando correctamente")
        print("✅ Tokens expiran correctamente")
        print("✅ Refresh de tokens funcional")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) fallaron. Revisar implementación.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
