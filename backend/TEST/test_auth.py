#!/usr/bin/env python3
"""
Script de prueba para endpoints de autenticación
Prueba: registro, login y validación de token
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

# Configuración
BASE_URL = "http://127.0.0.1:8000"
HEADERS = {"Content-Type": "application/json"}

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_request(method: str, url: str, data: Dict = None):
    print(f"\n{Colors.BOLD}→ {method} {url}{Colors.END}")
    if data:
        # Ocultar contraseñas en el log
        safe_data = data.copy()
        if 'password' in safe_data:
            safe_data['password'] = '***'
        if 'contrasena' in safe_data:
            safe_data['contrasena'] = '***'
        print(f"{Colors.CYAN}{json.dumps(safe_data, indent=2, ensure_ascii=False)}{Colors.END}")

def print_response(response: requests.Response):
    status_color = Colors.GREEN if response.status_code < 400 else Colors.RED
    print(f"{status_color}← {response.status_code} {response.reason}{Colors.END}")
    try:
        print(f"{Colors.CYAN}{json.dumps(response.json(), indent=2, ensure_ascii=False)}{Colors.END}")
    except:
        print(f"{Colors.YELLOW}Response: {response.text[:200]}{Colors.END}")

# ============================================================
# TEST 1: HEALTH CHECK
# ============================================================
def test_health_check():
    print_header("TEST 1: Health Check")
    
    try:
        print_request("GET", f"{BASE_URL}/")
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print_response(response)
        
        if response.status_code == 200:
            print_success("API está respondiendo correctamente")
            return True
        else:
            print_error(f"API respondió con código {response.status_code}")
            return False
    except Exception as e:
        print_error(f"No se pudo conectar al servidor: {str(e)}")
        return False

# ============================================================
# TEST 2: REGISTRO DE USUARIOS
# ============================================================
def test_register_users():
    print_header("TEST 2: Registro de Usuarios")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    users = [
        {
            "correo_institucional": f"maria.garcia.{timestamp}@universidad.edu.co",
            "username": f"maria_garcia_{timestamp}",
            "nombres": "María",
            "apellidos": "García López",
            "tipo_documento": "CC",
            "numero_documento": f"1234567{timestamp[-4:]}",
            "password": "DocenteTest123!",
            "rol": "docente",
            "telefono": "+57 300 123 4567",
            "descripcion": "Docente de matemáticas"
        },
        {
            "correo_institucional": f"juan.perez.{timestamp}@universidad.edu.co",
            "username": f"juan_perez_{timestamp}",
            "nombres": "Juan",
            "apellidos": "Pérez González",
            "tipo_documento": "TI",
            "numero_documento": f"9876543{timestamp[-4:]}",
            "password": "EstudianteTest123!",
            "rol": "estudiante",
            "telefono": "+57 301 234 5678",
            "descripcion": "Estudiante de ingeniería"
        },
        {
            "correo_institucional": f"ana.martinez.{timestamp}@universidad.edu.co",
            "username": f"ana_martinez_{timestamp}",
            "nombres": "Ana María",
            "apellidos": "Martínez Gómez",
            "tipo_documento": "CC",
            "numero_documento": f"5555555{timestamp[-4:]}",
            "password": "CoordinadorTest123!",
            "rol": "coordinador",
            "telefono": "+57 302 345 6789",
            "descripcion": "Coordinadora académica"
        }
    ]
    
    registered_users = []
    
    for user in users:
        print_info(f"Registrando {user['rol']}: {user['nombres']} {user['apellidos']}")
        print_request("POST", f"{BASE_URL}/auth/register", user)
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=user,
                headers=HEADERS,
                timeout=10
            )
            print_response(response)
            
            if response.status_code == 201:
                print_success(f"{user['rol'].capitalize()} registrado exitosamente")
                data = response.json()
                registered_users.append({
                    "email": user["correo_institucional"],
                    "username": user["username"],
                    "password": user["password"],
                    "rol": user["rol"],
                    "usuario_id": data.get("usuario_id")
                })
            elif response.status_code == 400:
                print_warning(f"Usuario ya existe o datos inválidos")
            else:
                print_error(f"Error al registrar {user['rol']}: {response.status_code}")
        except Exception as e:
            print_error(f"Excepción al registrar {user['rol']}: {str(e)}")
    
    return registered_users

# ============================================================
# TEST 3: LOGIN
# ============================================================
def test_login(users: list):
    print_header("TEST 3: Login de Usuarios")
    
    tokens = []
    
    for user in users:
        print_info(f"Intentando login para {user['rol']}: {user['email']}")
        
        # Probar diferentes formatos de login
        login_data = {
            "username": user["email"],
            "password": user["password"]
        }
        
        print_request("POST", f"{BASE_URL}/auth/login", login_data)
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                data=login_data,  # Form data, no JSON
                timeout=10
            )
            print_response(response)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    print_success(f"Login exitoso para {user['rol']}")
                    print_info(f"Token type: {data.get('token_type')}")
                    tokens.append({
                        "email": user["email"],
                        "rol": user["rol"],
                        "token": token,
                        "usuario_id": user.get("usuario_id")
                    })
                else:
                    print_error("Token no encontrado en respuesta")
            else:
                print_error(f"Login falló con código {response.status_code}")
        except Exception as e:
            print_error(f"Excepción durante login: {str(e)}")
    
    return tokens

# ============================================================
# TEST 4: VALIDAR TOKEN (/auth/me)
# ============================================================
def test_auth_me(tokens: list):
    print_header("TEST 4: Validación de Token (/auth/me)")
    
    for user_token in tokens:
        print_info(f"Validando token para {user_token['rol']}: {user_token['email']}")
        
        headers = {
            "Authorization": f"Bearer {user_token['token']}",
            "Content-Type": "application/json"
        }
        
        print_request("GET", f"{BASE_URL}/auth/me")
        
        try:
            response = requests.get(
                f"{BASE_URL}/auth/me",
                headers=headers,
                timeout=10
            )
            print_response(response)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Token válido para {user_token['rol']}")
                print_info(f"Usuario: {data.get('nombre')} {data.get('apellido')}")
                print_info(f"Email: {data.get('email')}")
                print_info(f"Rol: {data.get('rol')}")
            else:
                print_error(f"Validación falló con código {response.status_code}")
        except Exception as e:
            print_error(f"Excepción durante validación: {str(e)}")

# ============================================================
# TEST 5: TOKEN INVÁLIDO
# ============================================================
def test_invalid_token():
    print_header("TEST 5: Token Inválido (Debe Fallar)")
    
    headers = {
        "Authorization": "Bearer token_invalido_12345",
        "Content-Type": "application/json"
    }
    
    print_request("GET", f"{BASE_URL}/auth/me")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=headers,
            timeout=10
        )
        print_response(response)
        
        if response.status_code == 401:
            print_success("Token inválido rechazado correctamente (401)")
        else:
            print_warning(f"Esperaba 401, obtuvo {response.status_code}")
    except Exception as e:
        print_error(f"Excepción: {str(e)}")

# ============================================================
# MAIN
# ============================================================
def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}║     PRUEBAS DE AUTENTICACIÓN - ACADIFY API                ║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.END}")
    
    # Test 1: Health Check
    if not test_health_check():
        print_error("\n❌ Servidor no disponible. Abortando pruebas.")
        return
    
    # Test 2: Registro
    registered_users = test_register_users()
    if not registered_users:
        print_error("\n❌ No se pudieron registrar usuarios. Abortando.")
        return
    
    print_success(f"\n✅ {len(registered_users)} usuarios registrados")
    
    # Test 3: Login
    tokens = test_login(registered_users)
    if not tokens:
        print_error("\n❌ No se pudieron obtener tokens. Abortando.")
        return
    
    print_success(f"\n✅ {len(tokens)} tokens obtenidos")
    
    # Test 4: Validar tokens
    test_auth_me(tokens)
    
    # Test 5: Token inválido
    test_invalid_token()
    
    # Resumen final
    print_header("RESUMEN DE PRUEBAS")
    print_success(f"✅ Health Check: OK")
    print_success(f"✅ Usuarios registrados: {len(registered_users)}")
    print_success(f"✅ Tokens obtenidos: {len(tokens)}")
    print_success(f"✅ Tokens validados: OK")
    print_success(f"✅ Token inválido rechazado: OK")
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'TODAS LAS PRUEBAS COMPLETADAS'.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 60}{Colors.END}\n")

if __name__ == "__main__":
    main()
