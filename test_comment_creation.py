#!/usr/bin/env python3
"""
Test script para verificar la creación de comentarios con archivos adjuntos.
"""

import requests
import json
from typing import Dict, Any

def test_create_comment_with_attachments():
    """Test crear comentario con archivos adjuntos."""

    # URL del endpoint
    base_url = "http://localhost:8000"
    endpoint = "/api/cursos/test-curso-id/comentarios"

    # Datos de prueba (sin curso_id, viene de URL)
    test_data = {
        "contenido": "Comentario de prueba con archivos adjuntos",
        "tipo": "comentario",
        "archivos_adjuntos": [
            {
                "nombre": "documento.pdf",
                "url": "https://example.com/documento.pdf",
                "tipo": "application/pdf",
                "tamano": 1024000
            },
            {
                "nombre": "imagen.jpg",
                "url": "https://example.com/imagen.jpg",
                "tipo": "image/jpeg",
                "tamano": 512000
            }
        ]
    }

    print("📤 Enviando request de prueba:")
    print(f"URL: {base_url}{endpoint}")
    print(f"Data: {json.dumps(test_data, indent=2)}")

    try:
        # Hacer request sin autenticación primero para ver el error de validación
        response = requests.post(
            f"{base_url}{endpoint}",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )

        print(f"\n📨 Response Status: {response.status_code}")
        print(f"📨 Response Headers: {dict(response.headers)}")

        if response.status_code == 422:
            print("❌ Error 422 - Unprocessable Entity")
            print("📨 Response Body:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
        elif response.status_code == 401:
            print("✅ Error 401 - Sin autenticación (esperado)")
            print("📨 Response Body:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
        else:
            print(f"📨 Response Body: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - El servidor no está corriendo")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_create_comment_with_attachments()