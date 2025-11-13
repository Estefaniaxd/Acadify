#!/usr/bin/env python3
"""
Script Python para ejecutar la migración del Sistema de Misiones
Alternativa al script bash para mayor compatibilidad
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Intentar importar psycopg2
try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ Error: psycopg2 no está instalado")
    print("Instálalo con: pip install psycopg2-binary")
    sys.exit(1)

# Colores ANSI
class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color


def print_header():
    """Imprime el encabezado del script"""
    print(f"{Colors.BLUE}============================================{Colors.NC}")
    print(f"{Colors.BLUE}  Sistema de Misiones - Migración DB{Colors.NC}")
    print(f"{Colors.BLUE}============================================{Colors.NC}")
    print()


def load_env_vars() -> dict:
    """Carga variables de entorno desde .env"""
    env_path = Path(__file__).parent.parent / '.env'
    
    if not env_path.exists():
        print(f"{Colors.RED}❌ Error: No se encuentra el archivo .env en {env_path}{Colors.NC}")
        print(f"{Colors.YELLOW}Por favor, crea un archivo .env con DATABASE_URL{Colors.NC}")
        sys.exit(1)
    
    env_vars = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")
    
    return env_vars


def parse_database_url(database_url: str) -> dict:
    """Parse DATABASE_URL en componentes"""
    # Formato: postgresql://user:password@host:port/database
    import re
    pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/([^\?]+)'
    match = re.match(pattern, database_url)
    
    if not match:
        print(f"{Colors.RED}❌ Error: Formato inválido de DATABASE_URL{Colors.NC}")
        print(f"Formato esperado: postgresql://user:password@host:port/database")
        sys.exit(1)
    
    user, password, host, port, database = match.groups()
    
    return {
        'user': user,
        'password': password,
        'host': host,
        'port': int(port),
        'database': database
    }


def connect_database(db_config: dict) -> Optional[psycopg2.extensions.connection]:
    """Conecta a la base de datos"""
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        return conn
    except psycopg2.Error as e:
        print(f"{Colors.RED}❌ Error al conectar a la base de datos:{Colors.NC}")
        print(f"  {e}")
        return None


def execute_migration(conn: psycopg2.extensions.connection, script_path: Path) -> bool:
    """Ejecuta el script de migración"""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        with conn.cursor() as cur:
            cur.execute(sql_script)
            conn.commit()
        
        return True
    except psycopg2.Error as e:
        print(f"{Colors.RED}❌ Error al ejecutar la migración:{Colors.NC}")
        print(f"  {e}")
        conn.rollback()
        return False
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Error: No se encuentra el archivo {script_path}{Colors.NC}")
        return False


def verify_migration(conn: psycopg2.extensions.connection) -> None:
    """Verifica que la migración se ejecutó correctamente"""
    print(f"\n{Colors.BLUE}Verificando datos...{Colors.NC}")
    
    try:
        with conn.cursor() as cur:
            # Contar ENUMs
            cur.execute("""
                SELECT COUNT(*) 
                FROM pg_type 
                WHERE typname IN ('tipo_mision', 'estado_mision', 'frecuencia_mision', 'dificultad_mision')
            """)
            enums_count = cur.fetchone()[0]
            
            # Contar tablas
            cur.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_name IN ('misiones', 'misiones_usuario')
            """)
            tables_count = cur.fetchone()[0]
            
            # Contar misiones
            cur.execute("SELECT COUNT(*) FROM misiones")
            misiones_count = cur.fetchone()[0]
            
            # Mostrar resultados
            print(f"  • ENUMs creados: {enums_count}/4")
            print(f"  • Tablas creadas: {tables_count}/2")
            print(f"  • Misiones de ejemplo: {misiones_count}")
            
            # Mostrar misiones por frecuencia
            cur.execute("""
                SELECT frecuencia, COUNT(*) as total
                FROM misiones
                GROUP BY frecuencia
                ORDER BY frecuencia
            """)
            print(f"\n{Colors.BLUE}Distribución de misiones:{Colors.NC}")
            for row in cur.fetchall():
                print(f"  • {row[0].capitalize()}: {row[1]} misiones")
            
    except psycopg2.Error as e:
        print(f"{Colors.YELLOW}⚠️  No se pudo verificar la migración: {e}{Colors.NC}")


def main():
    """Función principal"""
    print_header()
    
    # Cargar variables de entorno
    env_vars = load_env_vars()
    print(f"{Colors.GREEN}✓{Colors.NC} Variables de entorno cargadas\n")
    
    # Verificar DATABASE_URL
    if 'DATABASE_URL' not in env_vars:
        print(f"{Colors.RED}❌ Error: DATABASE_URL no está definida en .env{Colors.NC}")
        sys.exit(1)
    
    # Parsear DATABASE_URL
    db_config = parse_database_url(env_vars['DATABASE_URL'])
    
    # Mostrar configuración
    print(f"{Colors.BLUE}Configuración de Base de Datos:{Colors.NC}")
    print(f"  Host: {db_config['host']}")
    print(f"  Puerto: {db_config['port']}")
    print(f"  Database: {db_config['database']}")
    print(f"  Usuario: {db_config['user']}")
    print()
    
    # Pedir confirmación
    respuesta = input(f"{Colors.YELLOW}¿Ejecutar migración? (s/N): {Colors.NC}")
    if respuesta.lower() not in ['s', 'si', 'y', 'yes']:
        print(f"{Colors.RED}Migración cancelada{Colors.NC}")
        sys.exit(0)
    
    print(f"\n{Colors.BLUE}Ejecutando migración...{Colors.NC}\n")
    
    # Conectar a la base de datos
    conn = connect_database(db_config)
    if conn is None:
        sys.exit(1)
    
    # Ejecutar migración
    script_path = Path(__file__).parent / '001_sistema_misiones.sql'
    success = execute_migration(conn, script_path)
    
    if success:
        print(f"\n{Colors.GREEN}============================================{Colors.NC}")
        print(f"{Colors.GREEN}  ✓ Migración completada exitosamente{Colors.NC}")
        print(f"{Colors.GREEN}============================================{Colors.NC}")
        
        # Verificar migración
        verify_migration(conn)
        
        print(f"\n{Colors.GREEN}✓ Sistema de misiones listo para usar{Colors.NC}")
    else:
        print(f"\n{Colors.RED}============================================{Colors.NC}")
        print(f"{Colors.RED}  ❌ Error al ejecutar la migración{Colors.NC}")
        print(f"{Colors.RED}============================================{Colors.NC}")
        sys.exit(1)
    
    # Cerrar conexión
    conn.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Migración cancelada por el usuario{Colors.NC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error inesperado: {e}{Colors.NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
