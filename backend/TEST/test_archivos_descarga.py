#!/usr/bin/env python3
"""
Script para verificar URLs de archivos y que sean accesibles
"""

import sys
sys.path.append('/home/esteban/Acadify/backend/src')

import os
import json
import psycopg2
import requests
from psycopg2.extras import RealDictCursor

# Configuración
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'acadify_db',
    'user': 'postgres',
    'password': '243019'
}

API_BASE_URL = "http://localhost:8000"  # Ajustar si es diferente

def test_archivo_urls():
    """Probar que las URLs de archivos sean accesibles"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔗 PROBANDO URLs DE ARCHIVOS")
        print("=" * 60)
        
        # Obtener comentarios con archivos
        cursor.execute("""
            SELECT comentario_id, contenido, archivos_adjuntos, fecha_creacion
            FROM "Comentario" 
            WHERE archivos_adjuntos IS NOT NULL 
            AND archivos_adjuntos::text != 'null',
            AND archivos_adjuntos::text != '[]'
            ORDER BY fecha_creacion DESC
            LIMIT 3
        """)
        
        comentarios = cursor.fetchall()
        
        for comentario in comentarios:
            print(f"\n📝 COMENTARIO: {comentario['comentario_id']}")
            print(f"   Contenido: {comentario['contenido']}")
            
            if comentario['archivos_adjuntos']:
                archivos_raw = comentario['archivos_adjuntos']
                
                for i, archivo in enumerate(archivos_raw, 1):
                    if isinstance(archivo, dict):
                        nombre = archivo.get("nombre", archivo.get("filename", f"archivo_{i}"))
                        url_relativa = archivo.get("url", "")
                        tipo = archivo.get("tipo", archivo.get("type", "unknown"))
                        tamaño = archivo.get("tamaño", archivo.get("size", 0))
                        
                        print(f"\n   📎 ARCHIVO {i}: {nombre}")
                        print(f"      Tipo: {tipo}")
                        print(f"      Tamaño: {tamaño:,} bytes")
                        print(f"      URL relativa: {url_relativa}")
                        
                        # Construir URL completa
                        if url_relativa.startswith('/'):
                            url_completa = f"{API_BASE_URL}{url_relativa}"
                        else:
                            url_completa = f"{API_BASE_URL}/static/uploads/cursos/{nombre}"
                        
                        print(f"      URL completa: {url_completa}")
                        
                        # Verificar archivo físico
                        if url_relativa.startswith('/static'):
                            ruta_fisica = f"/home/esteban/Acadify/backend{url_relativa}"
                        else:
                            ruta_fisica = f"/home/esteban/Acadify/backend/static/uploads/cursos/{nombre}"
                        
                        if os.path.exists(ruta_fisica):
                            size_fisica = os.path.getsize(ruta_fisica)
                            print(f"      ✅ Archivo físico existe ({size_fisica:,} bytes)")
                            
                            # Verificar que el tamaño coincida
                            if abs(size_fisica - tamaño) < 100:  # Tolerancia de 100 bytes
                                print(f"      ✅ Tamaño coincide")
                            else:
                                print(f"      ⚠️ Tamaño no coincide: BD={tamaño}, Físico={size_fisica}")
                            
                        else:
                            print(f"      ❌ Archivo físico no existe: {ruta_fisica}")
                        
                        # Intentar hacer una petición HTTP (si hay servidor corriendo)
                        try:
                            response = requests.head(url_completa, timeout=5)
                            if response.status_code == 200:
                                print(f"      ✅ URL HTTP accesible (status: {response.status_code})")
                                headers = response.headers
                                if 'content-length' in headers:
                                    print(f"      📏 Content-Length: {headers['content-length']} bytes")
                                if 'content-type' in headers:
                                    print(f"      📄 Content-Type: {headers['content-type']}")
                            else:
                                print(f"      ⚠️ URL HTTP responde con status: {response.status_code}")
                        except requests.exceptions.RequestException:
                            print(f"      ⚠️ No se puede verificar HTTP (servidor no corriendo?)")
                        
                        print(f"      🔗 URL para frontend: {url_completa}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Verificación de URLs completada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando URLs: {e}")
        return False

def generar_test_descarga():
    """Generar código HTML para probar descargas"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("\n🧪 GENERANDO TEST DE DESCARGA")
        print("=" * 60)
        
        # Obtener un archivo de ejemplo
        cursor.execute("""
            SELECT comentario_id, archivos_adjuntos
            FROM "Comentario" 
            WHERE archivos_adjuntos IS NOT NULL 
            ORDER BY fecha_creacion DESC
            LIMIT 1
        """)
        
        comentario = cursor.fetchone()
        if comentario and comentario['archivos_adjuntos']:
            archivo = comentario['archivos_adjuntos'][0]
            nombre = archivo.get("nombre", archivo.get("filename", "test.jpg"))
            url = archivo.get("url", "")
            tipo = archivo.get("tipo", archivo.get("type", ""))
            
            # Generar HTML de prueba
            html_test = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test de Descarga</title>
</head>
<body>
    <h1>Test de Descarga de Archivos</h1>
    <h2>Archivo: {nombre}</h2>
    <p>Tipo: {tipo}</p>
    <p>URL: {API_BASE_URL}{url}</p>
    
    <div style="margin: 20px 0;">,
        <button onclick="descargarArchivo()">🔽 Descargar Archivo</button>,
        <button onclick="abrirArchivo()">👁️ Abrir en Nueva Pestaña</button>
    </div>
    
    <script>
        function descargarArchivo() {{
            const link = document.createElement('a');,
            link.href = '{API_BASE_URL}{url}';,
            link.download = '{nombre}';,
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            console.log('Descarga iniciada para: {nombre}');
        }}
        
        function abrirArchivo() {{
            window.open('{API_BASE_URL}{url}', '_blank');
            console.log('Abriendo archivo: {nombre}');
        }}
    </script>
</body>
</html>
            """
            
            # Guardar archivo de test
            with open('/home/esteban/Acadify/test_descarga.html', 'w', encoding='utf-8') as f:
                f.write(html_test)
            
            print(f"✅ Test HTML generado: /home/esteban/Acadify/test_descarga.html")
            print(f"🔗 Archivo de prueba: {nombre}")
            print(f"📁 URL: {API_BASE_URL}{url}")
            print(f"\n💡 Para probar:")
            print(f"   1. Asegúrate de que el backend esté corriendo en {API_BASE_URL}")
            print(f"   2. Abre test_descarga.html en el navegador")
            print(f"   3. Prueba los botones de descarga y vista previa")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN COMPLETA DE ARCHIVOS")
    print("=" * 60)
    
    urls_ok = test_archivo_urls()
    test_ok = generar_test_descarga()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN:")
    print(f"   URLs verificadas: {'✅' if urls_ok else '❌'}")
    print(f"   Test generado: {'✅' if test_ok else '❌'}")
    
    if urls_ok and test_ok:
        print("\n🎉 ¡VERIFICACIÓN COMPLETA!")
        print("   - Usa test_descarga.html para probar descargas")
        print("   - Revisa los logs del frontend para debugging")
    else:
        print("\n⚠️ Hay problemas que revisar")