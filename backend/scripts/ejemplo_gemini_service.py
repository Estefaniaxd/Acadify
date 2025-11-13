"""
Ejemplo de uso del GeminiService para retroalimentación con IA.

Este script demuestra cómo usar el servicio de IA para analizar
entregas de estudiantes y generar retroalimentación estructurada.

Author: Gemini AI Assistant
Date: 31 octubre 2025

Uso:
    python scripts/ejemplo_gemini_service.py
"""

import asyncio
import sys
import os
from pathlib import Path
import json
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.ai import GeminiService, AIConfig
from src.services.ai.helpers import FileProcessor
from src.models.academic.tarea import Tarea
from src.models.academic.tarea import EntregaTarea
from datetime import datetime
from uuid import uuid4


async def ejemplo_completo():
    """Ejemplo completo de uso del GeminiService."""
    
    print("=" * 80)
    print("EJEMPLO DE USO: GeminiService - Retroalimentación con IA")
    print("=" * 80)
    print()
    
    # ==================== 1. Configuración ====================
    
    print("📋 Paso 1: Configurando el servicio...")
    
    # Opción A: Usar configuración por defecto (lee de .env)
    service = GeminiService()
    
    # Opción B: Configuración personalizada
    # config = AIConfig(
    #     api_key="tu_api_key_aqui",
    #     model="gemini-1.5-flash",
    #     temperature=0.7,
    #     max_output_tokens=4096
    # )
    # service = GeminiService(config=config)
    
    # Inicializar conexión
    try:
        await service.inicializar()
        print("✅ Servicio inicializado correctamente\n")
    except Exception as e:
        print(f"❌ Error inicializando servicio: {e}")
        print("💡 Asegúrate de tener GEMINI_API_KEY en tu .env")
        return
    
    # ==================== 2. Crear datos de ejemplo ====================
    
    print("📝 Paso 2: Creando tarea y entrega de ejemplo...")
    
    # Tarea con rúbrica
    tarea_ejemplo = Tarea(
        tarea_id=uuid4(),
        titulo="Implementar Sistema de Autenticación",
        descripcion="Crea un sistema de autenticación básico con login y registro",
        instrucciones=(
            "Implementa:\n"
            "1. Registro de usuarios con validación de email\n"
            "2. Login con JWT tokens\n"
            "3. Middleware de protección de rutas\n"
            "4. Manejo de errores robusto\n"
        ),
        tipo="ejercicios",
        rubrica={
            "criterios": [
                {
                    "nombre": "Funcionalidad",
                    "peso": 40,
                    "descripcion": "El código funciona correctamente",
                    "niveles": [
                        {"nombre": "Excelente", "puntos": 5.0, "descripcion": "Todo funciona perfectamente"},
                        {"nombre": "Bueno", "puntos": 4.0, "descripcion": "Funciona con errores menores"},
                        {"nombre": "Regular", "puntos": 3.0, "descripcion": "Funciona parcialmente"},
                    ]
                },
                {
                    "nombre": "Calidad del Código",
                    "peso": 30,
                    "descripcion": "Código limpio, legible y mantenible",
                },
                {
                    "nombre": "Manejo de Errores",
                    "peso": 20,
                    "descripcion": "Validaciones y manejo de excepciones",
                },
                {
                    "nombre": "Documentación",
                    "peso": 10,
                    "descripcion": "Comentarios y docstrings",
                }
            ]
        },
        habilitar_retroalimentacion_ia=True,
        prompt_ia_personalizado=(
            "Enfócate especialmente en la seguridad del sistema de autenticación. "
            "Revisa que las contraseñas se hasheen correctamente y que los tokens "
            "sean seguros."
        )
    )
    
    # Entrega del estudiante (código de ejemplo)
    codigo_estudiante = '''"""
Sistema de autenticación básico.
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "mi_clave_secreta"
ALGORITHM = "HS256"

class User(BaseModel):
    email: EmailStr
    password: str

users_db = {}

@app.post("/register")
def register(user: User):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    hashed_password = pwd_context.hash(user.password)
    users_db[user.email] = {"email": user.email, "password": hashed_password}
    
    return {"message": "Usuario registrado exitosamente"}

@app.post("/login")
def login(user: User):
    if user.email not in users_db:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    stored_user = users_db[user.email]
    if not pwd_context.verify(user.password, stored_user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    token = jwt.encode(
        {"sub": user.email, "exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return {"access_token": token, "token_type": "bearer"}
'''
    
    entrega_ejemplo = EntregarTarea(
        entrega_id=uuid4(),
        tarea_id=tarea_ejemplo.tarea_id,
        estudiante_id=uuid4(),
        fecha_entrega=datetime.utcnow(),
        es_tardia=False,
        intentos=1,
        archivo_metadata={
            "nombre": "auth_system.py",
            "mime_type": "text/x-python",
            "tamaño_bytes": len(codigo_estudiante.encode()),
        }
    )
    
    print("✅ Tarea y entrega creadas\n")
    
    # ==================== 3. Generar retroalimentación ====================
    
    print("🤖 Paso 3: Generando retroalimentación con IA...")
    print("⏳ Esto puede tomar 10-30 segundos...")
    print()
    
    try:
        resultado = await service.generar_retroalimentacion(
            entrega=entrega_ejemplo,
            tarea=tarea_ejemplo,
            archivo_contenido=codigo_estudiante,
            opciones={
                "include_calificacion": True,
                "temperature": 0.7  # Balance creatividad/precisión
            }
        )
        
        print("✅ Retroalimentación generada exitosamente!\n")
        
        # ==================== 4. Mostrar resultados ====================
        
        print("=" * 80)
        print("RESULTADOS DEL ANÁLISIS")
        print("=" * 80)
        print()
        
        print(f"🎯 Modelo usado: {resultado['modelo_usado']}")
        print(f"📊 Calificación sugerida: {resultado.get('calificacion_sugerida', 'N/A')}/5.0")
        print(f"📈 Nivel de cumplimiento: {resultado['nivel_cumplimiento']}")
        print(f"⏱️ Tiempo de procesamiento: {resultado['metadata']['duracion_segundos']}s")
        print(f"🔢 Tokens usados: {resultado['metadata']['tokens_total']}")
        print()
        
        print("-" * 80)
        print("📝 ANÁLISIS GENERAL")
        print("-" * 80)
        print(resultado['analisis_general'])
        print()
        
        print("-" * 80)
        print("✨ FORTALEZAS")
        print("-" * 80)
        for idx, fortaleza in enumerate(resultado['fortalezas'], 1):
            print(f"{idx}. {fortaleza}")
        print()
        
        print("-" * 80)
        print("⚠️ ÁREAS DE MEJORA")
        print("-" * 80)
        for idx, area in enumerate(resultado['areas_mejora'], 1):
            print(f"{idx}. {area}")
        print()
        
        print("-" * 80)
        print("💡 SUGERENCIAS ESPECÍFICAS")
        print("-" * 80)
        for idx, sug in enumerate(resultado['sugerencias_especificas'], 1):
            print(f"\n{idx}. Ubicación: {sug.get('ubicacion', 'General')}")
            print(f"   Problema: {sug.get('problema')}")
            print(f"   Sugerencia: {sug.get('sugerencia')}")
            if sug.get('ejemplo'):
                print(f"   Ejemplo:\n   {sug.get('ejemplo')}")
        print()
        
        if resultado['cumple_rubrica']:
            print("-" * 80)
            print("📋 EVALUACIÓN POR CRITERIOS")
            print("-" * 80)
            for criterio, eval in resultado['cumple_rubrica'].items():
                if isinstance(eval, dict):
                    print(f"\n{criterio}:")
                    print(f"   Puntos: {eval.get('puntos', 0)}/5.0")
                    print(f"   Comentario: {eval.get('comentario', '')}")
            print()
        
        if resultado.get('puntos_clave_missing'):
            print("-" * 80)
            print("❌ CONCEPTOS FALTANTES")
            print("-" * 80)
            for concepto in resultado['puntos_clave_missing']:
                print(f"• {concepto}")
            print()
        
        if resultado.get('recursos_recomendados'):
            print("-" * 80)
            print("📚 RECURSOS RECOMENDADOS")
            print("-" * 80)
            for recurso in resultado['recursos_recomendados']:
                print(f"\n• {recurso.get('titulo')}")
                if recurso.get('url'):
                    print(f"  URL: {recurso.get('url')}")
                if recurso.get('descripcion'):
                    print(f"  {recurso.get('descripcion')}")
            print()
        
        # ==================== 5. Estadísticas de uso ====================
        
        print("=" * 80)
        print("ESTADÍSTICAS DE USO")
        print("=" * 80)
        print()
        
        stats = service.get_estadisticas()
        print(f"Requests totales: {stats['requests_totales']}")
        print(f"Tokens totales: {stats['tokens_totales']:,}")
        print()
        
        cost_tracker = service.get_cost_tracker()
        costo = cost_tracker.calcular_costo_estimado(plan="free")
        print(f"Plan gratuito: {'✅ Sí' if costo['en_plan_gratuito'] else '❌ No'}")
        print(f"Tokens input: {costo['tokens_input']:,}")
        print(f"Tokens output: {costo['tokens_output']:,}")
        
        if not costo['en_plan_gratuito']:
            print(f"Costo estimado: ${costo['costo_total']:.4f} USD")
        
        # Verificar límites
        limites = cost_tracker.verificar_limites_plan_gratuito()
        print()
        print("Límites plan gratuito:")
        print(f"  RPM: {limites['requests_este_minuto']}/{limites['limite_rpm']}")
        print(f"  TPM: {limites['tokens_este_minuto']:,}/{limites['limite_tpm']:,}")
        print(f"  RPD: {limites['requests_hoy']}/{limites['limite_rpd']}")
        
        alerta = cost_tracker.generar_alerta_limites()
        if alerta:
            print()
            print("⚠️ ALERTAS:")
            print(alerta)
        
        # ==================== 6. Exportar resultado ====================
        
        print()
        print("=" * 80)
        print("EXPORTAR RESULTADO")
        print("=" * 80)
        print()
        
        output_file = "resultado_retroalimentacion.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Resultado exportado a: {output_file}")
    
    except Exception as e:
        print(f"❌ Error generando retroalimentación: {e}")
        import traceback
        traceback.print_exc()


async def ejemplo_procesamiento_archivo():
    """Ejemplo de procesamiento de diferentes tipos de archivos."""
    
    print("\n" + "=" * 80)
    print("EJEMPLO: Procesamiento de Archivos")
    print("=" * 80)
    print()
    
    # Crear archivo de ejemplo
    archivo_py = "ejemplo_codigo.py"
    with open(archivo_py, 'w', encoding='utf-8') as f:
        f.write('''def suma(a, b):
    """Suma dos números."""
    return a + b

def resta(a, b):
    """Resta dos números."""
    return a - b

print(suma(5, 3))
''')
    
    print(f"✅ Archivo de ejemplo creado: {archivo_py}")
    print()
    
    # Procesar archivo
    with open(archivo_py, 'rb') as f:
        try:
            contenido = FileProcessor.extraer_contenido(
                archivo=f,
                nombre_archivo=archivo_py,
                mime_type="text/x-python"
            )
            
            print("📄 Contenido extraído:")
            print("-" * 80)
            print(contenido)
            print("-" * 80)
            print()
            
            # Validar
            f.seek(0)
            validacion = FileProcessor.validar_archivo(
                archivo=f,
                nombre_archivo=archivo_py,
                max_size_mb=20
            )
            
            print("✅ Validación:")
            print(f"   Válido: {validacion['valido']}")
            print(f"   Tamaño: {validacion['tamano_mb']} MB")
            print(f"   Tipo: {validacion['tipo']}")
            
            if validacion['razones']:
                print(f"   Razones: {', '.join(validacion['razones'])}")
        
        except Exception as e:
            print(f"❌ Error procesando archivo: {e}")
    
    # Limpiar
    os.remove(archivo_py)


if __name__ == "__main__":
    print()
    print("🚀 Iniciando ejemplos de GeminiService...")
    print()
    
    # Ejecutar ejemplos
    asyncio.run(ejemplo_completo())
    asyncio.run(ejemplo_procesamiento_archivo())
    
    print()
    print("=" * 80)
    print("✅ EJEMPLOS COMPLETADOS")
    print("=" * 80)
