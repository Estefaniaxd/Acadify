import sys
import os
import logging
from fastapi.testclient import TestClient

# Add backend to path
sys.path.append(os.getcwd())

# Mock authentication to bypass login
from src.api import deps
from src.models.auth.usuario import Usuario

def mock_get_current_user():
    return Usuario(
        usuario_id="c3d4e5f6-a7b8-4c5d-1e2f-3a4b5c6d7e8f", 
        nombres="Juan", 
        apellidos="Docente", 
        correo_institucional="juanestebanmartinezmacias@gmail.com",
        rol="docente"
    )

# Import app AFTER setting up mocks/env if needed
from src.main import app

# Override dependency
app.dependency_overrides[deps.get_current_user] = mock_get_current_user

client = TestClient(app)

def test_rachas_405():
    print("\n--- TESTING RACHAS (Expect 200, checking for 405) ---")
    # The URL reported as failing is /api/gamification/rachas/mi-racha
    response = client.get("/api/gamification/rachas/mi-racha")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text}")
    else:
        print("✅ Rachas endpoint works!")

def test_invitaciones_500():
    print("\n--- TESTING INVITACIONES (Expect 200, checking for 500) ---")
    response = client.get("/invitaciones/mis-invitaciones")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text}")
    else:
        print("✅ Invitaciones endpoint works!")

def test_submissions_500():
    print("\n--- TESTING SUBMISSIONS (Expect 200, checking for 500) ---")
    # Task ID from logs: fdde58b0-1c15-4c65-a2c2-5cbe499ce5cf
    tarea_id = "fdde58b0-1c15-4c65-a2c2-5cbe499ce5cf"
    response = client.get(f"/api/tareas/{tarea_id}/entregas")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text}")
    else:
        print(f"✅ Submissions endpoint works! Found {len(response.json())} items.")

def test_reacciones_404():
    print("\n--- TESTING REACCIONES (Checking for 404) ---")
    # ID from logs: task-53aa75fe-c78f-451e-835e-1e3b1c67f930
    # URL: /api/cursos/reacciones/comentarios/{id}
    # Note: The log shows /api/cursos/reacciones/comentarios/...
    # Let's check if this route exists in the router.
    comment_id = "task-53aa75fe-c78f-451e-835e-1e3b1c67f930"
    response = client.get(f"/api/cursos/reacciones/comentarios/{comment_id}")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text}")

if __name__ == "__main__":
    try:
        test_rachas_405()
        test_invitaciones_500()
        test_submissions_500()
        test_reacciones_404()
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
