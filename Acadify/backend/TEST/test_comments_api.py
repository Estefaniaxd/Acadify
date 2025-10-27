#!/usr/bin/env python3
"""
Script para probar la API de comentarios directamente
"""
import requests
import json

# Token válido actualizado con campo 'type' y 24 horas de validez
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmMmYyZDE2NC1jYmFkLTQ1YzQtOWE5Zi01NmRlZjk4MGYwMzMiLCJuYW1lIjoiZ" + \
        "XN0ZWZhbmlhIiwibGFzdF9uYW1lIjoibG9uZG9cdTAwZjFvIiwiZW1haWwiOiJlc3RlZmFuaWFYRERAZ21haWwuY29tIiwidGVzdF91c2VyIjpmYWxzZSIs" + \
        "InJvbGUiOiJkb2NlbnRlIiwidHlwZSI6ImFjY2VzcyIsImV4cCI6MTc1OTM0Nzk1MywiaWF0IjoxNzU5MjYxNTUzLCJqdGkiOiJmMmYyZDE2NC1jYmFk" + \
        "LTQ1YzQtOWE5Zi01NmRlZjk4MGYwMzMtMTc1OTI3OTU1MyJ9.-epp89kdgX0B-DRvGgguLgsj6DUyKZc7k5PBNlXl0r8"

CURSO_ID = "322e6b11-f95a-494c-8cba-d01531d515cd"
BASE_URL = "http://127.0.0.1:8000"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_get_comments():
    """Probar obtener comentarios"""
    print("🔄 Probando GET comentarios...")
    
    url = f"{BASE_URL}/academic/cursos/{CURSO_ID}/comentarios"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Comentarios obtenidos: {len(data.get('data', []))}")
            for comment in data.get('data', []):
                print(f"  - {comment.get('autor')}: {comment.get('contenido')[:50]}...")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_create_comment():
    """Probar crear comentario"""
    print("\n🔄 Probando POST comentario...")
    
    url = f"{BASE_URL}/academic/cursos/{CURSO_ID}/comentarios"
    
    data = {
        "contenido": "Este es un comentario de prueba desde script Python",
        "tipo": "comentario",
        "archivos": []
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Comentario creado exitosamente")
        else:
            print(f"❌ Error creando comentario: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    print("🧪 PRUEBAS DE API DE COMENTARIOS")
    print("=" * 50)
    
    test_get_comments()
    test_create_comment()
    
    print("\n🔄 Verificando comentarios después de crear...")
    test_get_comments()