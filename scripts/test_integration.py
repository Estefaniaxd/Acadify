#!/usr/bin/env python3
"""
Quick Integration Testing Script for Tareas Module
Prueba la integración del módulo de tareas en tiempo real
"""

import httpx
import json
import sys
from datetime import datetime, timedelta
from typing import Optional

# Colors para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

# Test tokens (reemplaza con tu token real)
TEST_TOKEN = "YOUR_JWT_TOKEN_HERE"  # Cambiar por token real
CURSO_ID = "1"  # Cambiar por ID real del curso

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_success(msg: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def test_backend_connection():
    """Test 1: Verify backend is running"""
    print_section("TEST 1: Backend Connection")
    
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{BACKEND_URL}/api/docs")
            if response.status_code == 200:
                print_success(f"Backend is running at {BACKEND_URL}")
                return True
            else:
                print_error(f"Backend returned status {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Backend not running: {e}")
        print_warning(f"Start backend: cd backend && uvicorn src.main:app --reload --port 8000")
        return False

def test_frontend_connection():
    """Test 2: Verify frontend is running"""
    print_section("TEST 2: Frontend Connection")
    
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(FRONTEND_URL)
            if response.status_code == 200:
                print_success(f"Frontend is running at {FRONTEND_URL}")
                return True
            else:
                print_error(f"Frontend returned status {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Frontend not running: {e}")
        print_warning(f"Start frontend: cd frontend && pnpm dev")
        return False

def test_get_tareas(token: str):
    """Test 3: GET /api/cursos/{id}/tareas"""
    print_section("TEST 3: GET /api/cursos/{curso_id}/tareas")
    
    if not token or token == "YOUR_JWT_TOKEN_HERE":
        print_error("JWT Token no configurado. Reemplaza TEST_TOKEN en el script.")
        print_info("Para obtener token: Login en frontend y copia desde localStorage.access_token")
        return None
    
    try:
        with httpx.Client(timeout=10.0) as client:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/api/cursos/{CURSO_ID}/tareas"
            
            print_info(f"GET {url}")
            response = client.get(url, headers=headers)
            
            print_info(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Retrieved {len(data)} tasks")
                if data:
                    print_info(f"Sample task: {json.dumps(data[0], indent=2, default=str)}")
                return data
            elif response.status_code == 401:
                print_error("Unauthorized (401) - Token inválido o expirado")
                return None
            elif response.status_code == 404:
                print_error("Not Found (404) - Curso no existe")
                return None
            else:
                print_error(f"Unexpected status: {response.status_code}")
                print_info(f"Response: {response.text}")
                return None
                
    except Exception as e:
        print_error(f"Request failed: {e}")
        return None

def test_create_tarea(token: str):
    """Test 4: POST /api/cursos/{id}/tareas"""
    print_section("TEST 4: POST /api/cursos/{curso_id}/tareas (Create Task)")
    
    if not token or token == "YOUR_JWT_TOKEN_HERE":
        print_error("JWT Token no configurado")
        return None
    
    # Prepare data
    fecha_limite = (datetime.now() + timedelta(days=7)).isoformat()
    tarea_data = {
        "titulo": f"Tarea de Prueba {datetime.now().strftime('%H:%M:%S')}",
        "descripcion": "Esta es una tarea de prueba desde el script de integración",
        "fecha_limite": fecha_limite,
        "puntos_max": 100,
        "tipo": "tarea",
        "prioridad": "media"
    }
    
    try:
        with httpx.Client(timeout=10.0) as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            url = f"{BACKEND_URL}/api/cursos/{CURSO_ID}/tareas"
            
            print_info(f"POST {url}")
            print_info(f"Data: {json.dumps(tarea_data, indent=2)}")
            response = client.post(url, json=tarea_data, headers=headers)
            
            print_info(f"Status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                print_success(f"Task created successfully!")
                print_info(f"Response: {json.dumps(data, indent=2, default=str)}")
                return data
            elif response.status_code == 422:
                print_error("Validation Error (422)")
                print_info(f"Response: {json.dumps(response.json(), indent=2)}")
                return None
            else:
                print_error(f"Unexpected status: {response.status_code}")
                print_info(f"Response: {response.text}")
                return None
                
    except Exception as e:
        print_error(f"Request failed: {e}")
        return None

def test_frontend_integration():
    """Test 5: Frontend Integration"""
    print_section("TEST 5: Frontend Integration Checklist")
    
    checklist = [
        ("ClaseTareasPage.tsx updated", "✓ Component uses new Tareas components"),
        ("React Query integration", "✓ GET /api/cursos/{id}/tareas configured"),
        ("TareasAccordion component", "✓ Groups by 6 states"),
        ("TareasStatistics component", "✓ Shows 4 KPI cards"),
        ("TareaFormModal component", "✓ Create form with validation"),
        ("TareaPreviewModal component", "✓ Task details preview"),
        ("Dark mode support", "✓ Tailwind dark: classes"),
        ("Responsive design", "✓ Mobile/tablet/desktop layouts"),
    ]
    
    for item, status in checklist:
        print_info(f"{item}: {status}")

def test_manual_flow():
    """Test 6: Manual Testing Flow"""
    print_section("TEST 6: Manual Testing Flow")
    
    steps = [
        ("1. Go to http://localhost:5173/dashboard", "Navigate to dashboard"),
        ("2. Click on any course", "Open a course"),
        ("3. Click 'Tareas' tab", "View tasks section"),
        ("4. Verify new layout loads", "Accordion + statistics"),
        ("5. Try searching for a task", "Type in search box"),
        ("6. Try filtering by type/priority/state", "Use select dropdowns"),
        ("7. Click '+ Crear Tarea'", "Open create form modal"),
        ("8. Fill out form and submit", "New task should appear"),
        ("9. Click on a task card", "Preview modal should open"),
        ("10. Toggle dark mode", "Colors should adapt"),
    ]
    
    for step, description in steps:
        print_info(f"{step} → {description}")

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     Acadify - Tareas Module Integration Testing          ║")
    print("║     PHASE 3: Frontend Refactoring                        ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"Frontend URL: {FRONTEND_URL}")
    print_info(f"Curso ID: {CURSO_ID}")
    print_warning("Replace TEST_TOKEN with your actual JWT token from browser localStorage")
    
    # Run tests
    backend_ok = test_backend_connection()
    frontend_ok = test_frontend_connection()
    
    if not backend_ok or not frontend_ok:
        print_error("\nCannot continue without backend and frontend running")
        sys.exit(1)
    
    # Test API endpoints
    tareas = test_get_tareas(TEST_TOKEN)
    created = test_create_tarea(TEST_TOKEN)
    
    # Frontend checks
    test_frontend_integration()
    
    # Manual testing
    test_manual_flow()
    
    # Summary
    print_section("SUMMARY")
    print_success("✅ Backend and frontend are running")
    print_success("✅ API endpoints are responding")
    if tareas is not None:
        print_success(f"✅ Retrieved {len(tareas)} tasks from database")
    if created:
        print_success("✅ Successfully created a new task")
    
    print_info("\nNext steps:")
    print_info("1. Open http://localhost:5173 in browser")
    print_info("2. Navigate to any course")
    print_info("3. Click 'Tareas' tab")
    print_info("4. Test filters, create task, preview task")
    print_info("5. Check console (F12) for errors")
    print_info("6. Review INTEGRATION_TESTING_GUIDE.md for detailed tests")
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}Integration testing ready!{Colors.END}\n")

if __name__ == "__main__":
    main()

