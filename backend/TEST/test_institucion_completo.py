"""
Test completo del sistema de instituciones mejorado.

Prueba:
1. Creación de institución con todos los campos nuevos
2. Búsqueda por filtros (modalidad, tipo, etc.)
3. Verificación de dominio de email
4. Registro automático por dominio
5. Estadísticas de institución
"""

import requests
import json
import random
from datetime import datetime
from uuid import uuid4

# Configuración
BASE_URL = "http://localhost:8000"
DB_CONFIG = {
    "host": "localhost",
    "database": "acadify_db",
    "user": "postgres",
    "password": "243019"
}

class ColoresTerminal:
    HEADER = '\033[95m',
    OKBLUE = '\033[94m',
    OKCYAN = '\033[96m',
    OKGREEN = '\033[92m',
    WARNING = '\033[93m',
    FAIL = '\033[91m',
    ENDC = '\033[0m',
    BOLD = '\033[1m'

def print_title(msg):
    print(f"\n{ColoresTerminal.HEADER}{ColoresTerminal.BOLD}{'='*60}{ColoresTerminal.ENDC}")
    print(f"{ColoresTerminal.HEADER}{ColoresTerminal.BOLD}{msg}{ColoresTerminal.ENDC}")
    print(f"{ColoresTerminal.HEADER}{ColoresTerminal.BOLD}{'='*60}{ColoresTerminal.ENDC}\n")

def print_success(msg):
    print(f"{ColoresTerminal.OKGREEN}✓ {msg}{ColoresTerminal.ENDC}")

def print_info(msg):
    print(f"{ColoresTerminal.OKCYAN}ℹ {msg}{ColoresTerminal.ENDC}")

def print_error(msg):
    print(f"{ColoresTerminal.FAIL}✗ {msg}{ColoresTerminal.ENDC}")

def crear_institucion_completa():
    """Paso 1: Crear una institución con todos los campos nuevos"""
    print_title("1️⃣ CREANDO INSTITUCIÓN CON CAMPOS EXTENDIDOS")
    
    import psycopg2
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    timestamp = datetime.now().strftime("%H%M%S")
    nombre = f"Universidad Tecnológica Test {timestamp}",
    dominio = f"utest{timestamp}.edu.co"
    
    institucion_data = {
        "nombre": nombre,
        "sigla": f"UTEST{timestamp}",
        "lema": "Innovación, Conocimiento y Excelencia",
        "logo_url": "https://via.placeholder.com/200/FF6B6B/FFFFFF?text=UTEST",
        "color_primario": "#FF6B6B",
        "color_secundario": "#4ECDC4",
        "tipo_institucion": "universidad",
        "usa_programas": True,
        "nivel_educativo": "superior",
        "sector": "privado",
        "modalidad_ensenanza": "hibrida",
        "tipo_calendario": "semestral",
        "jornadas": ["mañana", "tarde", "noche"],
        "direccion": "Calle 123 #45-67",
        "ciudad": "Bogotá",
        "pais": "Colombia",
        "correo_institucional": f"contacto@{dominio}",
        "telefono": "+57 1 234 5678",
        "nit": f"900{random.randint(100000, 999999)}-1",
        "dominio_principal": dominio,
        "dominios_adicionales": [f"alumni.{dominio}", f"docentes.{dominio}"],
        "website": f"https://www.{dominio}",
        "redes_sociales": {
            "facebook": f"https://facebook.com/utest{timestamp}",
            "instagram": f"@utest{timestamp}",
            "linkedin": f"https://linkedin.com/school/utest{timestamp}"
        },
        "acreditacion_nacional": "MEN Colombia - Alta Calidad",
        "acreditacion_internacional": "ISO 9001:2015",
        "capacidad_estudiantes": 5000,
        "numero_estudiantes_actual": 0,
        "numero_docentes": 0,
        "numero_programas_activos": 0,
        "configuracion_regional": {
            "idioma": "es",
            "zona_horaria": "America/Bogota",
            "moneda": "COP",
            "formato_fecha": "DD/MM/YYYY"
        },
        "campos_personalizados": {
            "codigo_SNIES": f"SNIES{random.randint(10000, 99999)}",
            "reconocimiento_MEN": "Resolución 12345 de 2020",
            "año_fundacion": 2020
        }
    }
    
    # Insertar en base de datos
    try:
        cur.execute("""
            INSERT INTO "Institucion" (
                nombre, sigla, lema, logo_url, color_primario, color_secundario,
                tipo_institucion, usa_programas, nivel_educativo, sector, modalidad_ensenanza,
                tipo_calendario, jornadas, direccion, ciudad, pais, correo_institucional,
                telefono, nit, dominio_principal, dominios_adicionales, website, redes_sociales,
                acreditacion_nacional, acreditacion_internacional, capacidad_estudiantes,
                numero_estudiantes_actual, numero_docentes, numero_programas_activos,
                configuracion_regional, campos_personalizados, estado
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'activa'
            ) RETURNING institucion_id;
        """, (
            institucion_data["nombre"],
            institucion_data["sigla"],
            institucion_data["lema"],
            institucion_data["logo_url"],
            institucion_data["color_primario"],
            institucion_data["color_secundario"],
            institucion_data["tipo_institucion"],
            institucion_data["usa_programas"],
            institucion_data["nivel_educativo"],
            institucion_data["sector"],
            institucion_data["modalidad_ensenanza"],
            institucion_data["tipo_calendario"],
            institucion_data["jornadas"],
            institucion_data["direccion"],
            institucion_data["ciudad"],
            institucion_data["pais"],
            institucion_data["correo_institucional"],
            institucion_data["telefono"],
            institucion_data["nit"],
            institucion_data["dominio_principal"],
            institucion_data["dominios_adicionales"],
            institucion_data["website"],
            json.dumps(institucion_data["redes_sociales"]),
            institucion_data["acreditacion_nacional"],
            institucion_data["acreditacion_internacional"],
            institucion_data["capacidad_estudiantes"],
            institucion_data["numero_estudiantes_actual"],
            institucion_data["numero_docentes"],
            institucion_data["numero_programas_activos"],
            json.dumps(institucion_data["configuracion_regional"]),
            json.dumps(institucion_data["campos_personalizados"])
        ))
        
        institucion_id = cur.fetchone()[0]
        conn.commit()
        
        print_success(f"Institución creada: {nombre}")
        print_info(f"   ID: {institucion_id}")
        print_info(f"   Dominio principal: {dominio}")
        print_info(f"   Dominios adicionales: {institucion_data['dominios_adicionales']}")
        print_info(f"   Modalidad: {institucion_data['modalidad_ensenanza']}")
        print_info(f"   Calendario: {institucion_data['tipo_calendario']}")
        print_info(f"   Capacidad: {institucion_data['capacidad_estudiantes']} estudiantes")
        
        cur.close()
        conn.close()
        
        return institucion_id, dominio, institucion_data
        
    except Exception as e:
        print_error(f"Error al crear institución: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        return None, None, None


def test_buscar_con_filtros():
    """Paso 2: Buscar instituciones con filtros"""
    print_title("2️⃣ BUSCANDO INSTITUCIONES CON FILTROS")
    
    # Búsqueda por modalidad híbrida
    print_info("Buscando instituciones con modalidad híbrida...")
    response = requests.get(
        f"{BASE_URL}/instituciones/buscar",
        params={
            "modalidad_ensenanza": "hibrida",
            "estado": "activa",
            "limit": 10
        }
    )
    
    if response.status_code == 200:,
        instituciones = response.json()
        print_success(f"Encontradas {len(instituciones)} instituciones híbridas")
        for inst in instituciones[:3]:  # Mostrar máximo 3
            print_info(f"   - {inst['nombre']} ({inst['ciudad']})")
    else:
        print_error(f"Error en búsqueda: {response.status_code}")
    
    return response.status_code == 200


def test_verificar_dominio(dominio):
    """Paso 3: Verificar dominio de email"""
    print_title("3️⃣ VERIFICANDO DOMINIO DE EMAIL")
    
    email_estudiante = f"juan.perez@{dominio}"
    print_info(f"Verificando email: {email_estudiante}")
    
    response = requests.post(
        f"{BASE_URL}/instituciones/verificar-dominio",
        json={"email": email_estudiante}
    )
    
    if response.status_code == 200:,
        data = response.json()
        if data.get("encontrada"):
            inst = data["institucion"]
            print_success("¡Institución encontrada!")
            print_info(f"   Nombre: {inst['nombre']}")
            print_info(f"   Logo: {inst['logo_url']}")
            print_info(f"   Tipo: {inst['tipo_institucion']}")
            print_info(f"   Modalidad: {inst['modalidad_ensenanza']}")
            print_info(f"   Permite registro automático: {inst['permite_registro_automatico']}")
            return True
        else:
            print_error("No se encontró institución para este dominio")
            return False
    else:
        print_error(f"Error al verificar dominio: {response.status_code}")
        return False


def test_registro_automatico(dominio):
    """Paso 4: Registro automático por dominio"""
    print_title("4️⃣ REGISTRO AUTOMÁTICO POR DOMINIO")
    
    timestamp = datetime.now().strftime("%H%M%S")
    email_estudiante = f"estudiante.test{timestamp}@{dominio}"
    
    datos_registro = {
        "email": email_estudiante,
        "nombre": "María",
        "apellido": "González",
        "password": "Password123!",
        "rol": "estudiante"
    }
    
    print_info(f"Registrando usuario: {email_estudiante}")
    
    response = requests.post(
        f"{BASE_URL}/instituciones/registro-automatico",
        json=datos_registro,
    )
    
    if response.status_code == 200:,
        data = response.json()
        if data.get("success"):
            usuario = data["usuario"]
            institucion = data["institucion"]
            print_success(f"¡Usuario registrado exitosamente!")
            print_info(f"   ID: {usuario['id']}")
            print_info(f"   Email: {usuario['email']}")
            print_info(f"   Username: {usuario['username']}")
            print_info(f"   Rol: {usuario['rol']}")
            print_info(f"   Institución: {institucion['nombre']}")
            return True
        else:
            print_error("Falló el registro")
            return False
    else:
        print_error(f"Error en registro: {response.status_code} - {response.text}")
        return False


def test_estadisticas_institucion(institucion_id):
    """Paso 5: Obtener estadísticas de la institución"""
    print_title("5️⃣ OBTENIENDO ESTADÍSTICAS DE INSTITUCIÓN")
    
    response = requests.get(f"{BASE_URL}/instituciones/{institucion_id}/estadisticas")
    
    if response.status_code == 200:,
        stats = response.json()
        print_success("Estadísticas obtenidas:")
        print_info(f"   Nombre: {stats['nombre']}")
        print_info(f"   Programas: {stats['total_programas']}")
        print_info(f"   Cursos: {stats['total_cursos']} (activos: {stats['cursos_activos']})")
        print_info(f"   Estudiantes: {stats['numero_estudiantes_actual']}")
        print_info(f"   Docentes: {stats['numero_docentes']}")
        print_info(f"   Capacidad: {stats['capacidad_estudiantes']}")
        if stats.get('porcentaje_ocupacion') is not None:
            print_info(f"   Ocupación: {stats['porcentaje_ocupacion']}%")
        return True
    else:
        print_error(f"Error al obtener estadísticas: {response.status_code}")
        return False


def main():
    print_title("🧪 TEST COMPLETO: SISTEMA DE INSTITUCIONES MEJORADO")
    
    resultados = {
        "creacion": False,
        "filtros": False,
        "verificacion_dominio": False,
        "registro_automatico": False,
        "estadisticas": False
    }
    
    # 1. Crear institución completa
    institucion_id, dominio, institucion_data = crear_institucion_completa()
    if institucion_id:
        resultados["creacion"] = True
        
        # 2. Buscar con filtros
        resultados["filtros"] = test_buscar_con_filtros()
        
        # 3. Verificar dominio
        resultados["verificacion_dominio"] = test_verificar_dominio(dominio)
        
        # 4. Registro automático
        resultados["registro_automatico"] = test_registro_automatico(dominio)
        
        # 5. Estadísticas
        resultados["estadisticas"] = test_estadisticas_institucion(institucion_id)
    
    # Resumen final
    print_title("📊 RESUMEN DE RESULTADOS")
    
    total_tests = len(resultados)
    tests_exitosos = sum(resultados.values())
    
    for nombre, resultado in resultados.items():
        emoji = "✅" if resultado else "❌"
        print(f"{emoji} {nombre.replace('_', ' ').title()}: {'PASS' if resultado else 'FAIL'}")
    
    print(f"\n{ColoresTerminal.BOLD}Total: {tests_exitosos}/{total_tests} tests exitosos{ColoresTerminal.ENDC}")
    
    if tests_exitosos == total_tests:
        print(f"\n{ColoresTerminal.OKGREEN}{ColoresTerminal.BOLD}🎉 ¡TODOS LOS TESTS PASARON!{ColoresTerminal.ENDC}\n")
    else:
        print(f"\n{ColoresTerminal.WARNING}{ColoresTerminal.BOLD}⚠️  Algunos tests fallaron{ColoresTerminal.ENDC}\n")


if __name__ == "__main__":
    main()
