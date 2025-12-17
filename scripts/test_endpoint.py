#!/usr/bin/env python3

import requests
import json

# Probar el endpoint de comentarios
url = "http://localhost:8000/api/cursos/1/comentarios"
headers = {"Content-Type": "application/json"}
data = {"contenido": "Test comment", "tipo": "comentario", "archivos": []}

print("🧪 Probando endpoint de comentarios...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 401:
        print("✅ Endpoint responde correctamente - requiere autenticación")
    else:
        print(f"⚠️ Respuesta inesperada: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"❌ Error de conexión: {e}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")