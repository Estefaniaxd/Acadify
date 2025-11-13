"""
Locust Load Testing SIMPLIFICADO para Acadify API

Test minimalista enfocado en endpoints verificados.
Ejecutar con: locust -f locustfile_simple.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import random

# Test user credentials
DOCENTE_USER = {
    "identifier": "docente@senasofia.edu.co",
    "password": "docente123"
}

# Real IDs from database
CURSO_IDS = [
    "08731f15-701f-46cb-8c41-79dbfd8f86eb",  # CURST101
    "7bcf2a98-d6f3-4477-8a59-38674d18bbe9",  # CURST102
    "fcac461b-6f88-41b4-9269-9e2fba5e202b",  # CURST103
    "6c8bafde-e7c2-492e-be79-b651905acedf",  # CURST201
    "2dccd744-3e8f-4bba-864d-96f488134b50",  # CURST202
    "e887046c-0d29-4c17-bbf0-367d09de9ff7",  # CURST301
]

INSTITUCION_IDS = [
    "3b85274d-e14d-4de9-aed0-8f7ba51734a5",
    "e6e39011-22e1-4533-8c40-7cd28aa9fdf2",
    "40d9595a-3658-4d6e-b404-53adacea447a",
]


class DocenteUser(HttpUser):
    """Usuario docente que ejecuta tareas básicas"""
    wait_time = between(1, 3)
    token = None
    
    def on_start(self):
        """Login y obtener token"""
        try:
            response = self.client.post("/auth/login", json=DOCENTE_USER)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            print(f"❌ Login exception: {e}")
    
    @task(5)
    def ver_mis_cursos(self):
        """Ver mis cursos - endpoint más usado"""
        with self.client.get("/api/cursos/mis-cursos", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(3)
    def ver_curso_detalle(self):
        """Ver detalle de un curso"""
        curso_id = random.choice(CURSO_IDS)
        with self.client.get(f"/api/cursos/{curso_id}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(4)
    def ver_personas_curso(self):
        """Ver personas de un curso"""
        curso_id = random.choice(CURSO_IDS)
        with self.client.get(f"/api/cursos/{curso_id}/personas", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(2)
    def ver_mi_perfil(self):
        """Ver mi perfil"""
        with self.client.get("/api/users/me/perfil", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(3)
    def ver_comentarios(self):
        """Ver comentarios de un curso"""
        curso_id = random.choice(CURSO_IDS)
        with self.client.get(f"/api/cursos/{curso_id}/comentarios", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(2)
    def listar_instituciones(self):
        """Listar instituciones"""
        with self.client.get("/api/instituciones/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(2)
    def ver_institucion_detalle(self):
        """Ver detalle de institución"""
        inst_id = random.choice(INSTITUCION_IDS)
        with self.client.get(f"/api/instituciones/{inst_id}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
