"""
Locust Load Testing - Sistema de Autenticación Acadify
======================================================

Tests de rendimiento para validar:
- Registro de usuarios
- Login con credenciales
- Refresh de tokens JWT
- Logout
- Recuperación de contraseña (solicitud)
- Verificación de email
- Obtener perfil de usuario actual
- Actualizar perfil

Objetivo: Validar que el sistema de autenticación es robusto,
sin fugas de memoria, sin errores de concurrencia, y mantiene
performance bajo carga.

Ejecución:
----------
# Test básico (10 usuarios, 1 usuario/seg, 30 segundos)
locust -f locustfile_auth.py --host=http://localhost:8000 --users 10 --spawn-rate 1 --run-time 30s --headless

# Test medio (50 usuarios, 5 usuarios/seg, 2 minutos)
locust -f locustfile_auth.py --host=http://localhost:8000 --users 50 --spawn-rate 5 --run-time 2m --headless

# Test alto (100 usuarios, 10 usuarios/seg, 5 minutos)
locust -f locustfile_auth.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 5m --headless

# Interfaz web (para monitoreo visual)
locust -f locustfile_auth.py --host=http://localhost:8000
# Abrir http://localhost:8089
"""

from locust import HttpUser, task, between, events
import random
import string
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AcadifyAuthUser(HttpUser):
    """
    Usuario simulado que ejecuta flujos de autenticación.
    
    Simula comportamiento real:
    - Registra una cuenta
    - Hace login
    - Obtiene su perfil
    - Actualiza su perfil
    - Hace logout
    - Intenta recuperar contraseña
    """
    
    # Tiempo de espera entre tareas (simula usuario real)
    wait_time = between(1, 3)  # Entre 1 y 3 segundos
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.refresh_token = None
        self.user_id = None
        self.email = None
        self.password = None
        self.nombre = None
        self.apellido = None
    
    def on_start(self):
        """Ejecutado cuando el usuario inicia (simula sesión nueva)"""
        logger.info("🚀 Usuario iniciado - preparando datos de prueba")
        self._generate_user_data()
    
    def _generate_user_data(self):
        """Genera datos aleatorios para un usuario único"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        self.email = f"test.{random_suffix}@acadify.com"
        self.password = f"TestPass123!{random_suffix[:4]}"
        self.nombre = f"TestUser{random_suffix[:4]}"
        self.apellido = f"Acadify{random_suffix[4:]}"
        
        logger.info(f"📧 Usuario generado: {self.email}")
    
    @task(10)
    def auth_flow_complete(self):
        """
        Flujo completo de autenticación (peso 10):
        1. Registro
        2. Login
        3. Obtener perfil
        4. Actualizar perfil
        5. Logout
        
        Este es el flujo más importante y tiene mayor peso.
        """
        # PASO 1: Registro
        if not self.token:
            success = self.register_user()
            if not success:
                logger.warning("⚠️  Registro falló, abortando flujo")
                return
        
        # PASO 2: Login (si no tiene token o quiere renovar sesión)
        if not self.token:
            success = self.login_user()
            if not success:
                logger.warning("⚠️  Login falló, abortando flujo")
                return
        
        # PASO 3: Obtener perfil
        self.get_user_profile()
        
        # PASO 4: Actualizar perfil (50% de probabilidad)
        if random.random() > 0.5:
            self.update_user_profile()
        
        # PASO 5: Logout (30% de probabilidad)
        if random.random() > 0.7:
            self.logout_user()
    
    @task(5)
    def login_existing_user(self):
        """
        Login con credenciales existentes (peso 5).
        Simula usuarios que ya tienen cuenta y solo hacen login.
        """
        # Usa credenciales de prueba pre-existentes
        predefined_users = [
            {"identifier": "adminacadify", "password": "Admin123!"},  # Admin usa username
            {"identifier": "docente@acadify.com", "password": "Admin123!"},
            {"identifier": "estudiante@acadify.com", "password": "Admin123!"},
        ]
        
        user = random.choice(predefined_users)
        
        with self.client.post(
            "/auth/login",
            json={
                "identifier": user["identifier"],
                "password": user["password"]
            },
            catch_response=True,
            name="POST /auth/login (existing user)"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                logger.info(f"✅ Login exitoso: {user['identifier']}")
                response.success()
            else:
                logger.error(f"❌ Login falló: {response.status_code} - {response.text[:100]}")
                response.failure(f"Login failed: {response.status_code}")
    
    @task(3)
    def refresh_token_task(self):
        """
        Refresh de token JWT (peso 3).
        Simula renovación de sesión sin re-login.
        """
        if not self.refresh_token:
            logger.debug("⏭️  No hay refresh_token, saltando")
            return
        
        with self.client.post(
            "/auth/refresh",
            json={"refresh_token": self.refresh_token},
            catch_response=True,
            name="POST /auth/refresh"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                logger.info("🔄 Token renovado exitosamente")
                response.success()
            else:
                logger.warning(f"⚠️  Refresh token falló: {response.status_code}")
                response.failure(f"Refresh failed: {response.status_code}")
    
    @task(2)
    def forgot_password_request(self):
        """
        Solicitud de recuperación de contraseña (peso 2).
        Simula usuarios que olvidan su contraseña.
        
        NOTA: El envío de email puede no funcionar si no hay
        configuración SMTP, pero el endpoint debe responder correctamente.
        """
        if not self.email:
            self._generate_user_data()
        
        with self.client.post(
            "/auth/forgot-password",
            json={"correo_institucional": self.email},  # FIX: era "email", ahora es "correo_institucional"
            catch_response=True,
            name="POST /auth/forgot-password"
        ) as response:
            if response.status_code in [200, 202]:  # 200 OK o 202 Accepted
                logger.info(f"📧 Recuperación de contraseña solicitada: {self.email}")
                response.success()
            elif response.status_code == 404:
                # Email no existe, es esperado para emails aleatorios
                logger.debug(f"ℹ️  Email no encontrado: {self.email}")
                response.success()  # No es un error del sistema
            else:
                logger.error(f"❌ Forgot password falló: {response.status_code}")
                response.failure(f"Forgot password failed: {response.status_code}")
    
    @task(1)
    def verify_email_simulation(self):
        """
        Simulación de verificación de email (peso 1).
        
        NOTA: El código real vendría por email, aquí simulamos
        el intento de verificación.
        """
        if not self.email:
            return
        
        # Código simulado (en producción vendría por email)
        fake_code = ''.join(random.choices(string.digits, k=6))
        
        with self.client.post(
            "/auth/verify-email",
            json={
                "usuario_id": str(self.user_id) if self.user_id else "00000000-0000-0000-0000-000000000000",  # FIX: era "email", ahora "usuario_id"
                "verification_code": fake_code  # FIX: era "code", ahora "verification_code"
            },
            catch_response=True,
            name="POST /auth/verify-email"
        ) as response:
            if response.status_code in [200, 400]:  # 400 es esperado (código inválido)
                logger.debug(f"ℹ️  Verificación intentada: {self.email}")
                response.success()  # No es un error del sistema
            else:
                logger.warning(f"⚠️  Verify email falló: {response.status_code}")
                response.failure(f"Verify email failed: {response.status_code}")
    
    # ============================================
    # MÉTODOS AUXILIARES (NO SON TASKS)
    # ============================================
    
    def register_user(self) -> bool:
        """Registra un nuevo usuario"""
        # Generar username único para admin o email para otros roles
        username = f"user{random.randint(10000, 99999)}"
        
        user_payload = {
            "correo_institucional": self.email,
            "username": username,  # Se requiere siempre según el esquema
            "nombres": self.nombre,
            "apellidos": self.apellido,
            "numero_documento": f"100{random.randint(1000000, 9999999)}",
            "tipo_documento": "cc",  # Debe ser minúscula según enum
            "rol": "estudiante",
            "telefono": f"300{random.randint(1000000, 9999999)}",
            "password": self.password
        }
        
        with self.client.post(
            "/auth/register",
            json=user_payload,  # FIX: era "payload" ahora es "user_payload"
            catch_response=True,
            name="POST /auth/register"
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.user_id = data.get("usuario_id")
                logger.info(f"✅ Registro exitoso: {self.email}")
                response.success()
                
                # Auto-login después de registro
                return self.login_user()
            elif response.status_code == 400:
                # Email ya existe, intenta login
                logger.info(f"ℹ️  Email ya existe, intentando login: {self.email}")
                response.success()  # No es un error del sistema
                return self.login_user()
            else:
                logger.error(f"❌ Registro falló: {response.status_code} - {response.text[:200]}")
                response.failure(f"Register failed: {response.status_code}")
                return False
    
    def login_user(self):
        """Hace login y obtiene tokens"""
        with self.client.post(
            "/auth/login",
            json={
                "identifier": self.email,
                "password": self.password
            },
            catch_response=True,
            name="POST /auth/login (new user)"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                logger.info(f"✅ Login exitoso: {self.email}")
                response.success()
                return True
            else:
                logger.error(f"❌ Login falló: {response.status_code} - {response.text[:100]}")
                response.failure(f"Login failed: {response.status_code}")
                return False
    
    def get_user_profile(self):
        """Obtiene el perfil del usuario actual"""
        if not self.token:
            logger.debug("⏭️  No hay token, saltando get_profile")
            return
        
        with self.client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True,
            name="GET /auth/me"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"✅ Perfil obtenido: {data.get('correo_institucional', data.get('username', 'unknown'))}")  # FIX: era 'email'
                response.success()
            elif response.status_code == 401:
                logger.info("🔑 Token expirado, regenerando...")
                self.token = None
                response.failure("Token expired")
            else:
                logger.warning(f"⚠️  Get profile falló: {response.status_code}")
                response.failure(f"Get profile failed: {response.status_code}")
    
    def update_user_profile(self):
        """Actualiza el perfil del usuario"""
        if not self.token:
            logger.debug("⏭️  No hay token, saltando update_profile")
            return
        
        payload = {
            "telefono": f"+57{random.randint(3000000000, 3999999999)}",
            "biografia": f"Usuario de prueba generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        with self.client.put(
            "/auth/me",
            headers={"Authorization": f"Bearer {self.token}"},
            json=payload,
            catch_response=True,
            name="PUT /auth/me"
        ) as response:
            if response.status_code == 200:
                logger.debug("✅ Perfil actualizado")
                response.success()
            elif response.status_code == 401:
                logger.info("🔑 Token expirado")
                self.token = None
                response.failure("Token expired")
            else:
                logger.warning(f"⚠️  Update profile falló: {response.status_code}")
                response.failure(f"Update profile failed: {response.status_code}")
    
    def logout_user(self):
        """Hace logout y limpia tokens"""
        if not self.token:
            return
        
        with self.client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True,
            name="POST /auth/logout"
        ) as response:
            if response.status_code == 200:
                logger.info(f"👋 Logout exitoso: {self.email}")
                self.token = None
                self.refresh_token = None
                response.success()
            else:
                logger.warning(f"⚠️  Logout falló: {response.status_code}")
                response.failure(f"Logout failed: {response.status_code}")


# ============================================
# EVENT HANDLERS (Estadísticas)
# ============================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Ejecutado al inicio del test"""
    logger.info("=" * 80)
    logger.info("🚀 INICIANDO LOAD TEST - SISTEMA DE AUTENTICACIÓN")
    logger.info("=" * 80)
    logger.info(f"Host: {environment.host}")
    logger.info(f"Usuarios objetivo: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    logger.info("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Ejecutado al final del test"""
    logger.info("=" * 80)
    logger.info("✅ LOAD TEST COMPLETADO - SISTEMA DE AUTENTICACIÓN")
    logger.info("=" * 80)
    
    # Obtener estadísticas
    stats = environment.stats
    
    logger.info("\n📊 RESUMEN DE ESTADÍSTICAS:")
    logger.info("-" * 80)
    
    for name, stat in stats.entries.items():
        if stat.num_requests > 0:
            logger.info(f"\n📍 {name}")
            logger.info(f"   Requests: {stat.num_requests}")
            logger.info(f"   Failures: {stat.num_failures} ({stat.fail_ratio * 100:.2f}%)")
            logger.info(f"   Avg: {stat.avg_response_time:.2f}ms")
            logger.info(f"   Min: {stat.min_response_time:.2f}ms")
            logger.info(f"   Max: {stat.max_response_time:.2f}ms")
            logger.info(f"   Median: {stat.median_response_time:.2f}ms")
            logger.info(f"   P95: {stat.get_response_time_percentile(0.95):.2f}ms")
            logger.info(f"   P99: {stat.get_response_time_percentile(0.99):.2f}ms")
            logger.info(f"   RPS: {stat.total_rps:.2f}")
    
    logger.info("\n" + "=" * 80)
    logger.info(f"📈 TOTAL:")
    logger.info(f"   Total Requests: {stats.total.num_requests}")
    logger.info(f"   Total Failures: {stats.total.num_failures}")
    logger.info(f"   Failure Rate: {stats.total.fail_ratio * 100:.2f}%")
    logger.info(f"   Avg Response Time: {stats.total.avg_response_time:.2f}ms")
    logger.info(f"   RPS: {stats.total.total_rps:.2f}")
    logger.info("=" * 80)
    
    # Validaciones
    if stats.total.fail_ratio > 0.05:  # Más de 5% de fallos
        logger.error("❌ ALERTA: Tasa de fallos superior al 5%")
    else:
        logger.info("✅ Tasa de fallos aceptable (< 5%)")
    
    if stats.total.avg_response_time > 500:  # Más de 500ms promedio
        logger.warning("⚠️  ALERTA: Tiempo de respuesta promedio > 500ms")
    else:
        logger.info("✅ Tiempo de respuesta aceptable (< 500ms)")


if __name__ == "__main__":
    import os
    print("\n" + "=" * 80)
    print("🧪 LOCUST LOAD TEST - SISTEMA DE AUTENTICACIÓN ACADIFY")
    print("=" * 80)
    print("\nOpciones de ejecución:")
    print("\n1️⃣  TEST BÁSICO (10 usuarios, 30 segundos):")
    print("   locust -f locustfile_auth.py --host=http://localhost:8000 \\")
    print("          --users 10 --spawn-rate 1 --run-time 30s --headless")
    print("\n2️⃣  TEST MEDIO (50 usuarios, 2 minutos):")
    print("   locust -f locustfile_auth.py --host=http://localhost:8000 \\")
    print("          --users 50 --spawn-rate 5 --run-time 2m --headless")
    print("\n3️⃣  TEST ALTO (100 usuarios, 5 minutos):")
    print("   locust -f locustfile_auth.py --host=http://localhost:8000 \\")
    print("          --users 100 --spawn-rate 10 --run-time 5m --headless")
    print("\n4️⃣  INTERFAZ WEB (monitoreo en tiempo real):")
    print("   locust -f locustfile_auth.py --host=http://localhost:8000")
    print("   Luego abrir: http://localhost:8089")
    print("\n" + "=" * 80 + "\n")
