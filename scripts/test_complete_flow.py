#!/usr/bin/env python3
"""
TEST COMPLETO - Flujo de entrega de tarea con archivos

Simula:
1. Usuario sube archivo
2. Entrega tarea
3. Verifica que se guardó en BD
4. Verifica que se puede obtener entrega con archivos
5. Verifica que se puede cancelar y preserva archivos
"""

import sys
from pathlib import Path
import json
import requests
from io import BytesIO

# Configuración
API_URL = "http://localhost:8000"
HEADERS_ESTUDIANTE = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ZTU4ZmQyNi00ZTQyLTQxN2YtOTQ3OS1mYmI1NTU1MTEzMDEiLCJleHAiOjE3MzI3ODE5OTcsInJvbCI6ImVzdHVkaWFudGUifQ.u6scYBDvb-7Xb6gPYXl_L-WQ0cagmKzjbQFkKJhz-8Y"
}

print("=" * 80)
print("🧪 TEST COMPLETO: FLUJO DE ENTREGA CON ARCHIVOS")
print("=" * 80)

# PASO 1: Obtener una tarea
print("\n1️⃣  PASO 1: Obtener tarea...")
try:
    # Primero obtener tareas del curso
    resp_tareas = requests.get(
        f"{API_URL}/api/cursos/tareas/0a91fd26-4e42-417f-9479-fbb5555113d1/tareas",
        headers=HEADERS_ESTUDIANTE
    )
    print(f"   Status: {resp_tareas.status_code}")
    
    if resp_tareas.status_code == 200:
        tareas_data = resp_tareas.json()
        if isinstance(tareas_data, dict) and 'data' in tareas_data:
            tareas = tareas_data['data']
        elif isinstance(tareas_data, list):
            tareas = tareas_data
        else:
            tareas = []
        
        if tareas:
            tarea = tareas[0]
            tarea_id = tarea.get('tarea_id')
            print(f"   ✅ Encontrada tarea: {tarea_id}")
            print(f"      Título: {tarea.get('titulo')}")
            print(f"      Mi entrega ID: {tarea.get('mi_entrega_id')}")
        else:
            print("   ❌ No hay tareas disponibles")
            sys.exit(1)
    else:
        print(f"   ❌ Error: {resp_tareas.text}")
        sys.exit(1)

except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# PASO 2: Entregar tarea CON ARCHIVOS
print("\n2️⃣  PASO 2: Entregar tarea con 2 archivos...")
try:
    # Crear archivos de prueba
    file1 = ("documento.pdf", BytesIO(b"PDF content here"), "application/pdf")
    file2 = ("tarea.txt", BytesIO(b"This is a task content"), "text/plain")
    
    # Preparar multipart
    files = [
        ("archivos", file1),
        ("archivos", file2)
    ]
    data = {
        "contenido": "Entrega de tarea de prueba",
    }
    
    resp_entregar = requests.post(
        f"{API_URL}/api/cursos/tareas/{tarea_id}/entregar",
        files=files,
        data=data,
        headers=HEADERS_ESTUDIANTE
    )
    print(f"   Status: {resp_entregar.status_code}")
    print(f"   Response: {json.dumps(resp_entregar.json(), indent=2)}")
    
    if resp_entregar.status_code != 200:
        print(f"   ❌ Error entregando tarea")
        sys.exit(1)
    
    entrega_data = resp_entregar.json().get('data', {})
    entrega_id = entrega_data.get('entrega_id')
    archivos_respuesta = entrega_data.get('archivos', [])
    
    print(f"   ✅ Entrega registrada: {entrega_id}")
    print(f"   📁 Archivos retornados: {archivos_respuesta}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# PASO 3: Obtener entrega y verificar archivos
print("\n3️⃣  PASO 3: Obtener entrega y verificar que tiene archivos...")
try:
    resp_obtener = requests.get(
        f"{API_URL}/api/cursos/tareas/entregas/{entrega_id}",
        headers=HEADERS_ESTUDIANTE
    )
    print(f"   Status: {resp_obtener.status_code}")
    
    if resp_obtener.status_code == 200:
        entrega = resp_obtener.json()
        archivos = entrega.get('archivos', [])
        
        print(f"   📁 Archivos en BD: {len(archivos)}")
        
        for i, archivo in enumerate(archivos):
            if isinstance(archivo, dict):
                print(f"      {i+1}. URL: {archivo.get('url')}")
                print(f"         Nombre: {archivo.get('nombre')}")
            else:
                print(f"      {i+1}. URL: {archivo}")
        
        # Validar
        if len(archivos) >= 2:
            print(f"   ✅ Se guardaron {len(archivos)} archivos")
        else:
            print(f"   ⚠️  Solo se guardaron {len(archivos)} archivo(s) (esperado 2)")
            
        # Verificar que tienen nombres reales
        tiene_nombres_reales = False
        for archivo in archivos:
            if isinstance(archivo, dict) and 'nombre' in archivo:
                nombre = archivo['nombre']
                if nombre and not nombre.startswith('/'):
                    tiene_nombres_reales = True
                    break
        
        if tiene_nombres_reales:
            print(f"   ✅ Los archivos tienen nombres reales (no UUIDs)")
        else:
            print(f"   ❌ Los archivos NO tienen nombres reales")
    else:
        print(f"   ❌ Error: {resp_obtener.text}")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# PASO 4: Verificar que archivos existen en disco
print("\n4️⃣  PASO 4: Verificar que archivos existen en /uploads/entregas/...")
try:
    upload_dir = Path("/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/uploads/entregas")
    
    archivos_en_disco = list(upload_dir.glob("*"))
    print(f"   📁 Archivos en disco: {len(archivos_en_disco)}")
    
    if len(archivos_en_disco) > 0:
        print(f"   ✅ Existen archivos en /uploads/entregas/")
        # Mostrar últimos 5
        for archivo in archivos_en_disco[-5:]:
            print(f"      - {archivo.name}")
    else:
        print(f"   ❌ No hay archivos en /uploads/entregas/")
        
except Exception as e:
    print(f"   ⚠️  No se puede verificar disco: {e}")

# PASO 5: Cancelar entrega
print("\n5️⃣  PASO 5: Cancelar entrega...")
try:
    resp_cancelar = requests.delete(
        f"{API_URL}/api/cursos/tareas/entregas/{entrega_id}",
        headers=HEADERS_ESTUDIANTE
    )
    print(f"   Status: {resp_cancelar.status_code}")
    
    if resp_cancelar.status_code == 200:
        print(f"   ✅ Entrega cancelada")
    else:
        print(f"   ❌ Error: {resp_cancelar.text}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# PASO 6: Obtener entrega cancelada y verificar que PRESERVA archivos
print("\n6️⃣  PASO 6: Obtener entrega cancelada y verificar que archivos persisten...")
try:
    resp_obtener_cancelada = requests.get(
        f"{API_URL}/api/cursos/tareas/entregas/{entrega_id}",
        headers=HEADERS_ESTUDIANTE
    )
    print(f"   Status: {resp_obtener_cancelada.status_code}")
    
    if resp_obtener_cancelada.status_code == 200:
        entrega_cancelada = resp_obtener_cancelada.json()
        archivos_cancelada = entrega_cancelada.get('archivos', [])
        estado_cancelada = entrega_cancelada.get('estado')
        
        print(f"   Estado: {estado_cancelada}")
        print(f"   📁 Archivos después de cancelar: {len(archivos_cancelada)}")
        
        if len(archivos_cancelada) > 0:
            print(f"   ✅ Los archivos se mantienen después de cancelar")
            for archivo in archivos_cancelada:
                if isinstance(archivo, dict):
                    print(f"      - {archivo.get('nombre', 'Sin nombre')}")
        else:
            print(f"   ❌ Los archivos se eliminaron al cancelar")
    else:
        print(f"   ❌ Error: {resp_obtener_cancelada.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# PASO 7: Verificar descarga de archivo
print("\n7️⃣  PASO 7: Verificar que se pueden descargar los archivos...")
try:
    if archivos and isinstance(archivos[0], dict) and 'url' in archivos[0]:
        archivo_url = archivos[0]['url']
        print(f"   Intentando descargar: {archivo_url}")
        
        resp_descarga = requests.get(
            f"{API_URL}{archivo_url}",
            headers=HEADERS_ESTUDIANTE,
            allow_redirects=False
        )
        print(f"   Status: {resp_descarga.status_code}")
        
        if resp_descarga.status_code == 200:
            print(f"   ✅ Archivo se descarga correctamente")
            print(f"   Content-Type: {resp_descarga.headers.get('Content-Type')}")
            print(f"   Content-Length: {len(resp_descarga.content)} bytes")
        else:
            print(f"   ❌ Error descargando archivo (status {resp_descarga.status_code})")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# RESUMEN FINAL
print("\n" + "=" * 80)
print("✅ TEST COMPLETADO")
print("=" * 80)
