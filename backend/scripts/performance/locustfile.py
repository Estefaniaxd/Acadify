"""
Locust Load Testing para Acadify API

Escenarios de carga para endpoints críticos del sistema.
Ejecutar con: locust -f locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between, tag
import random
import json
from datetime import datetime

# Test user credentials
TEST_USER = {
    "identifier": "docente@senasofia.edu.co",  # Docente user for general testing
    "password": "docente123"
}

ADMIN_USER = {
    "identifier": "admin_sena",  # Admin uses username not email
    "password": "admin123"
}

READONLY_USER = {
    "identifier": "estudiante@senasofia.edu.co",  # Estudiante user for read-only testing
    "password": "estudiante123"
}

# Real IDs from database (created by create_complete_test_data.py)
CURSO_IDS = [
    "08731f15-701f-46cb-8c41-79dbfd8f86eb",  # CURST101
    "7bcf2a98-d6f3-4477-8a59-38674d18bbe9",  # CURST102
    "fcac461b-6f88-41b4-9269-9e2fba5e202b",  # CURST103
    "6c8bafde-e7c2-492e-be79-b651905acedf",  # CURST201
    "2dccd744-3e8f-4bba-864d-96f488134b50",  # CURST202
    "e887046c-0d29-4c17-bbf0-367d09de9ff7",  # CURST301
]

INSTITUCION_IDS = [
    "3b85274d-e14d-4de9-aed0-8f7ba51734a5",  # SENA Centro Tecnológico
    "e6e39011-22e1-4533-8c40-7cd28aa9fdf2",  # Instituto Técnico Nacional
    "40d9595a-3658-4d6e-b404-53adacea447a",  # Centro de Formación Empresarial
]

COMENTARIO_IDS = []  # Se rellenarán dinámicamente


class AcadifyUser(HttpUser):
    """
    Usuario que simula comportamiento real en Acadify.
    
    Wait time: 1-3 segundos entre requests (comportamiento humano)
    """
    wait_time = between(1, 3)
    token = None
    
    def on_start(self):
        """Ejecutar al inicio: login y obtener token"""
        response = self.client.post("/auth/login", json=TEST_USER)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
    
    @task(5)
    @tag('cursos', 'list')
    def listar_mis_cursos(self):
        """Listar mis cursos - endpoint más usado (peso 5)"""
        self.client.get("/api/cursos/mis-cursos", name="GET /api/cursos/mis-cursos")
    
    @task(3)
    @tag('cursos', 'detail')
    def ver_curso_detail(self):
        """Ver detalles de un curso (peso 3)"""
        curso_id = random.choice(CURSO_IDS)
        self.client.get(f"/api/cursos/{curso_id}", name="GET /api/cursos/{id}")
    
    @task(4)
    @tag('cursos', 'personas')
    def ver_personas_curso(self):
        """Ver personas de un curso - endpoint nuevo (peso 4)"""
        curso_id = random.choice(CURSO_IDS)
        self.client.get(
            f"/api/cursos/{curso_id}/personas",
            name="GET /api/cursos/{id}/personas"
        )
    
    @task(2)
    @tag('perfil')
    def ver_mi_perfil(self):
        """Ver perfil propio (peso 2)"""
        self.client.get("/api/users/me/perfil", name="GET /api/users/me/perfil")
    
    @task(3)
    @tag('comentarios', 'list')
    def ver_comentarios_curso(self):
        """Ver comentarios de un curso (peso 3)"""
        curso_id = random.choice(CURSO_IDS)
        self.client.get(
            f"/api/cursos/{curso_id}/comentarios",
            name="GET /api/cursos/{id}/comentarios"
        )
    
    @task(2)
    @tag('instituciones', 'list')
    def listar_instituciones(self):
        """Listar instituciones (peso 2)"""
        self.client.get("/api/instituciones/", name="GET /api/instituciones/")
    
    @task(2)
    @tag('instituciones', 'detail')
    def ver_detalle_institucion(self):
        """Ver detalle de institución (peso 2)"""
        inst_id = random.choice(INSTITUCION_IDS)
        self.client.get(f"/api/instituciones/{inst_id}", name="GET /api/instituciones/{id}")


class AdminUser(HttpUser):
    """
    Administrador que realiza operaciones de gestión.
    
    Wait time: 2-5 segundos (menos frecuente, tareas más complejas)
    """
    wait_time = between(2, 5)
    token = None
    
    def on_start(self):
        """Login como admin"""
        response = self.client.post("/auth/login", json=ADMIN_USER)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(3)
    @tag('instituciones', 'admin')
    def listar_instituciones(self):
        """Listar instituciones (peso 3)"""
        self.client.get("/api/instituciones/", name="GET /api/instituciones/ (admin)")
    
    @task(2)
    @tag('instituciones', 'stats', 'admin')
    def ver_estadisticas(self):
        """Ver estadísticas de institución específica (peso 2)"""
        inst_id = random.choice(INSTITUCION_IDS)
        self.client.get(
            f"/api/instituciones/{inst_id}/estadisticas",
            name="GET /api/instituciones/{id}/estadisticas (admin)"
        )
    
    @task(2)
    @tag('cursos', 'admin')
    def listar_cursos(self):
        """Listar cursos (peso 2)"""
        self.client.get("/api/cursos/mis-cursos", name="GET /api/cursos/mis-cursos (admin)")
    
    @task(1)
    @tag('cursos', 'detail', 'admin')
    def ver_curso_detalle(self):
        """Ver detalle de curso (peso 1)"""
        curso_id = random.choice(CURSO_IDS)
        self.client.get(f"/api/cursos/{curso_id}", name="GET /api/cursos/{id} (admin)")


class ReadOnlyUser(HttpUser):
    """
    Usuario que solo consulta (visitante, lector).
    
    Wait time: 0.5-2 segundos (muy activo, solo lectura)
    """
    wait_time = between(0.5, 2)
    token = None
    
    def on_start(self):
        """Login como usuario"""
        response = self.client.post("/auth/login", json=READONLY_USER)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(5)
    @tag('cursos', 'readonly')
    def navegar_cursos(self):
        """Navegar lista de cursos (peso 5 - muy frecuente)"""
        self.client.get("/api/cursos/mis-cursos", name="GET /api/cursos/mis-cursos (readonly)")
    
    @task(4)
    @tag('cursos', 'detail', 'readonly')
    def ver_detalle_curso(self):
        """Ver detalle de curso (peso 4)"""
        curso_id = random.choice(CURSO_IDS)
        self.client.get(f"/api/cursos/{curso_id}", name="GET /api/cursos/{id} (readonly)")
    
    @task(3)
    @tag('instituciones', 'readonly')
    def ver_instituciones(self):
        """Ver instituciones (peso 3)"""
        self.client.get("/api/instituciones/", name="GET /api/instituciones/ (readonly)")
    
    @task(2)
    @tag('perfil', 'readonly')
    def ver_perfil(self):
        """Ver perfil propio (peso 2)"""
        self.client.get("/api/users/me/perfil", name="GET /api/users/me/perfil (readonly)")
    
    @task(2)
    @tag('comentarios', 'readonly')
    def leer_comentarios(self):
        """Leer comentarios de curso (peso 2)"""
        curso_id = random.choice(CURSO_IDS)
        self.client.get(
            f"/api/cursos/{curso_id}/comentarios",
            name="GET /api/cursos/{id}/comentarios (readonly)"
        )


# Configuración de carga (puede sobrescribirse desde CLI)
"""
Ejemplos de ejecución:

# Básico (interfaz web en http://localhost:8089)
locust -f locustfile.py --host=http://localhost:8000

# Headless (sin interfaz, directo)
locust -f locustfile.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 60s

# Solo endpoints de lectura
locust -f locustfile.py --host=http://localhost:8000 --tags readonly

# Solo operaciones de admin
locust -f locustfile.py --host=http://localhost:8000 --tags admin

# Excluir creación de comentarios
locust -f locustfile.py --host=http://localhost:8000 --exclude-tags create

# Generar reporte HTML
locust -f locustfile.py --host=http://localhost:8000 --headless -u 50 -r 5 -t 120s --html=report.html

Parámetros:
-u: Número de usuarios concurrentes
-r: Tasa de spawn (usuarios/segundo)
-t: Duración del test (ej: 60s, 5m, 1h)
--host: URL del servidor
--html: Generar reporte HTML
--csv: Generar CSVs con estadísticas
--tags: Ejecutar solo tasks con estos tags
--exclude-tags: Excluir tasks con estos tags
"""
