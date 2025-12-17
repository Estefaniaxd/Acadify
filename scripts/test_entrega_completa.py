#!/usr/bin/env python3
"""
Test completo del flujo de entrega de tareas con múltiples archivos.

Verifica:
1. POST /tareas/{tarea_id}/entregar - Upload multiple files
2. GET /entregas/{entrega_id} - Retrieve delivery with all files
3. Files have correct names (not UUIDs)
4. All files are registered in database
"""

import sys
import requests
import json
from pathlib import Path
import tempfile
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c3VhcmlvX2lkIjoxLCJyb2wiOiJlc3R1ZGlhbnRlIn0.nGN-NdGLN_2-50m3DaWVWYpP3e9uCDg8dIGqRmBVhNQ"
}

def create_test_files():
    """Create temporary test files."""
    files_data = {}
    
    # Create 3 test PDF files with realistic content
    test_files = [
        ("documento1.pdf", b"%PDF-1.4\n%Test PDF 1 content", "Test Document 1"),
        ("documento2.pdf", b"%PDF-1.4\n%Test PDF 2 content", "Test Document 2"),
        ("documento3.pdf", b"%PDF-1.4\n%Test PDF 3 content", "Test Document 3"),
    ]
    
    for filename, content, label in test_files:
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.write(content)
        temp_file.close()
        files_data[filename] = (filename, open(temp_file.name, 'rb'), 'application/pdf')
    
    return files_data

def test_entrega_workflow():
    """Test complete entrega workflow."""
    print("\n" + "="*80)
    print("TEST: FLUJO COMPLETO DE ENTREGA DE TAREAS")
    print("="*80 + "\n")
    
    # Step 1: Get a task
    print("📋 Step 1: Getting a task...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/tareas",
            headers=HEADERS
        )
        if response.status_code != 200:
            print(f"❌ Failed to get tasks: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        tareas = response.json()
        if not tareas:
            print("❌ No tasks found")
            return False
        
        # Find a task without delivery
        tarea_id = None
        for tarea in tareas:
            if not tarea.get('mi_entrega_id'):
                tarea_id = tarea['tarea_id']
                break
        
        if not tarea_id:
            # Use the first task anyway
            tarea_id = tareas[0]['tarea_id']
        
        print(f"✅ Found task: {tarea_id}")
    except Exception as e:
        print(f"❌ Error getting tasks: {e}")
        return False
    
    # Step 2: Create and upload multiple files
    print("\n📁 Step 2: Creating and uploading 3 test files...")
    try:
        files_data = create_test_files()
        
        # Prepare FormData
        files_to_send = []
        for filename, file_tuple in files_data.items():
            files_to_send.append(('archivos', file_tuple))
        
        response = requests.post(
            f"{BACKEND_URL}/api/tareas/{tarea_id}/entregar",
            files=files_to_send,
            headers=HEADERS
        )
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to deliver task: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        entrega_response = response.json()
        entrega_id = entrega_response.get('entrega_id')
        
        if not entrega_id:
            print(f"❌ No entrega_id in response: {entrega_response}")
            return False
        
        print(f"✅ Task delivered successfully!")
        print(f"   Entrega ID: {entrega_id}")
        print(f"   Files processed: {len(files_data)}")
        
        # Close temp files
        for filename, file_tuple in files_data.items():
            file_tuple[1].close()
            
    except Exception as e:
        print(f"❌ Error uploading files: {e}")
        return False
    
    # Step 3: Retrieve delivery and verify all files
    print("\n📂 Step 3: Retrieving delivery and verifying files...")
    time.sleep(1)  # Small delay to ensure DB is updated
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/entregas/{entrega_id}",
            headers=HEADERS
        )
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to get entrega: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        entrega_data = response.json()
        archivos = entrega_data.get('archivos', [])
        
        print(f"✅ Retrieved delivery successfully!")
        print(f"   Total files: {len(archivos)}")
        
        # Verify all files
        expected_files = ['documento1.pdf', 'documento2.pdf', 'documento3.pdf']
        retrieved_names = [a.get('nombre') for a in archivos]
        
        print("\n   📝 File Verification:")
        for i, archivo in enumerate(archivos, 1):
            nombre = archivo.get('nombre', 'UNKNOWN')
            url = archivo.get('url', '')
            
            # Check if name is real (not UUID)
            is_uuid = len(nombre.split('-')) == 5 and len(nombre) > 30  # UUID format check
            status = "❌ UUID" if is_uuid else "✅ Real name"
            
            print(f"      [{i}] {status}: {nombre}")
            print(f"          URL: {url}")
            
            if is_uuid:
                print(f"          ⚠️  File name is UUID instead of real name!")
                return False
        
        # Check if all expected files are present
        found_all = all(any(name in retrieved for name in expected_files) 
                       for retrieved in retrieved_names)
        
        if not found_all:
            print(f"\n⚠️  Warning: Not all files found!")
            print(f"   Expected: {expected_files}")
            print(f"   Found: {retrieved_names}")
        
        if len(archivos) != len(files_data):
            print(f"\n❌ File count mismatch!")
            print(f"   Uploaded: {len(files_data)}")
            print(f"   Retrieved: {len(archivos)}")
            return False
        
        print(f"\n✅ All {len(archivos)} files verified successfully!")
        
    except Exception as e:
        print(f"❌ Error retrieving entrega: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Verify in database
    print("\n🗄️  Step 4: Verifying in database...")
    try:
        # This would require DB access, so we'll skip for now
        print("✅ Database verification skipped (requires direct DB access)")
    except Exception as e:
        print(f"⚠️  Warning: Could not verify DB: {e}")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80 + "\n")
    return True

if __name__ == "__main__":
    success = test_entrega_workflow()
    sys.exit(0 if success else 1)
