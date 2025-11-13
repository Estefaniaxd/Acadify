"""
Test de carga para el sistema de avatares de Acadify
Simula múltiples usuarios creando, actualizando y consultando avatares

Uso:
    locust -f locustfile_avatar.py --users 20 --spawn-rate 2 --run-time 1m
    
Opciones avanzadas:
    --headless: Sin interfaz web
    --host http://localhost:8000: Especificar host
    --csv avatar_results: Exportar a CSV
"""

from locust import HttpUser, task, between
import random
import json

# Configuración de usuarios de prueba
TEST_USERS = [
    {"email": "docente@acadify.com", "password": "Admin123!"},
    {"email": "estudiante@acadify.com", "password": "Admin123!"},
]

# Layers de prueba para avatares
TEST_LAYERS = [
    {"category": "base", "file": "base/light_skin_male.png"},
    {"category": "hair", "file": "hair/short_brown.png"},
    {"category": "eyes", "file": "eyes/brown_eyes.png"},
]

class AvatarUser(HttpUser):
    """
    Simula un usuario que interactúa con el sistema de avatares.
    """
    
    wait_time = between(1, 3)  # Espera entre 1-3 segundos entre requests
    
    def on_start(self):
        """Se ejecuta al inicio para cada usuario simulado."""
        self.auth_token = None
        self.avatar_id = None
        self.user_data = random.choice(TEST_USERS)
        self.login()
    
    def login(self):
        """Login para obtener token de autenticación."""
        response = self.client.post(
            "/auth/login",
            json=self.user_data,
            name="🔐 Login"
        )
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
            print(f"✅ Login exitoso para {self.user_data['email']}")
        else:
            print(f"❌ Login falló: {response.status_code}")
    
    def get_headers(self):
        """Retorna headers con autenticación."""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    @task(5)
    def get_assets(self):
        """
        Obtiene el manifest de assets disponibles.
        Endpoint público, no requiere autenticación.
        Peso: 5 (se ejecuta más frecuentemente)
        """
        response = self.client.get(
            "/avatar/assets",
            name="📦 GET /avatar/assets"
        )
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("total_assets", 0)
            # print(f"✅ Assets obtenidos: {total}")
        else:
            print(f"❌ Error obteniendo assets: {response.status_code}")
    
    @task(3)
    def generate_preview(self):
        """
        Genera un preview de avatar.
        Simula la selección de capas en el editor.
        Peso: 3
        """
        if not self.auth_token:
            return
        
        # Seleccionar capas aleatorias
        num_layers = random.randint(1, len(TEST_LAYERS))
        selected_layers = random.sample(TEST_LAYERS, num_layers)
        
        request_data = {
            "base_gender": random.choice(["male", "female"]),
            "layers": selected_layers
        }
        
        response = self.client.post(
            "/avatar/preview",
            json=request_data,
            name="🖼️ POST /avatar/preview"
        )
        
        if response.status_code == 200:
            data = response.json()
            # print(f"✅ Preview generado: {data.get('preview_url')}")
        else:
            print(f"❌ Error generando preview: {response.status_code}")
    
    @task(2)
    def get_my_avatars(self):
        """
        Obtiene los avatares del usuario actual.
        Peso: 2
        """
        if not self.auth_token:
            return
        
        response = self.client.get(
            "/avatar/me",
            headers=self.get_headers(),
            name="👤 GET /avatar/me"
        )
        
        if response.status_code == 200:
            data = response.json()
            avatars = data.get("avatars", [])
            if avatars and not self.avatar_id:
                self.avatar_id = avatars[0]["id"]
            # print(f"✅ Avatares del usuario: {len(avatars)}")
        else:
            print(f"❌ Error obteniendo avatares: {response.status_code}")
    
    @task(1)
    def create_avatar(self):
        """
        Crea un nuevo avatar.
        Solo se ejecuta ocasionalmente para no llenar la BD.
        Peso: 1
        """
        if not self.auth_token:
            return
        
        avatar_data = {
            "name": f"Load Test Avatar {random.randint(1000, 9999)}",
            "base_gender": random.choice(["male", "female"]),
            "layers": TEST_LAYERS,
            "is_active": True,
            "is_public": True
        }
        
        response = self.client.post(
            "/avatar/save",
            headers=self.get_headers(),
            json=avatar_data,
            name="💾 POST /avatar/save"
        )
        
        if response.status_code == 201:
            data = response.json()
            self.avatar_id = data.get("id")
            print(f"✅ Avatar creado: {data.get('name')}")
        elif response.status_code == 400:
            # Avatar duplicado, es normal
            pass
        else:
            print(f"❌ Error creando avatar: {response.status_code}")
    
    @task(1)
    def update_avatar(self):
        """
        Actualiza un avatar existente.
        Peso: 1
        """
        if not self.auth_token or not self.avatar_id:
            return
        
        update_data = {
            "name": f"Updated Avatar {random.randint(1000, 9999)}",
            "is_active": True
        }
        
        response = self.client.put(
            f"/avatar/{self.avatar_id}",
            headers=self.get_headers(),
            json=update_data,
            name="✏️ PUT /avatar/{id}"
        )
        
        if response.status_code == 200:
            # print(f"✅ Avatar actualizado")
            pass
        else:
            print(f"❌ Error actualizando avatar: {response.status_code}")


class HeavyAvatarUser(HttpUser):
    """
    Usuario que hace operaciones más pesadas (composición de avatares).
    Simula uso intensivo del sistema.
    """
    
    wait_time = between(2, 5)  # Más tiempo entre requests
    
    def on_start(self):
        """Se ejecuta al inicio para cada usuario simulado."""
        self.auth_token = None
        self.user_data = random.choice(TEST_USERS)
        self.login()
    
    def login(self):
        """Login para obtener token de autenticación."""
        response = self.client.post(
            "/auth/login",
            json=self.user_data,
            name="🔐 Login (Heavy)"
        )
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
    
    @task
    def create_complex_avatar(self):
        """
        Crea avatares con muchas capas (máxima complejidad).
        """
        if not self.auth_token:
            return
        
        # Todas las capas posibles
        complex_layers = TEST_LAYERS.copy()
        
        avatar_data = {
            "name": f"Complex Avatar {random.randint(1000, 9999)}",
            "base_gender": "male",
            "layers": complex_layers,
            "is_active": True,
            "is_public": True
        }
        
        response = self.client.post(
            "/avatar/save",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            json=avatar_data,
            name="🔥 POST /avatar/save (Complex)"
        )


if __name__ == "__main__":
    import os
    os.system("locust -f locustfile_avatar.py --users 20 --spawn-rate 2")
