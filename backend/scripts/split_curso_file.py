#!/usr/bin/env python3
"""
Script para dividir curso.py (2804 líneas) en 6 archivos más manejables.
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
import shutil
from datetime import datetime
import time

class CursoSplitter:
    def __init__(self, backend_path: str):
        self.backend_path = Path(backend_path)
        self.curso_file = self.backend_path / "src/api/routes/academic/curso.py"
        self.output_dir = self.backend_path / "src/api/routes/academic"
        
    def read_curso_file(self) -> str:
        """Lee el contenido del archivo curso.py"""
        with open(self.curso_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def extract_imports(self, content: str) -> str:
        """Extrae la sección de imports"""
        lines = content.split('\n')
        imports = []
        in_imports = False
        
        for line in lines:
            if line.startswith('"""') or line.startswith("'''"):
                if in_imports:
                    break
                in_imports = True
                continue
            
            if in_imports and (line.startswith('from ') or line.startswith('import ') or line.strip() == ''):
                imports.append(line)
            elif in_imports and line.startswith('router = '):
                break
        
        return '\n'.join(imports)
    
    def extract_models(self, content: str) -> str:
        """Extrae los modelos Pydantic"""
        lines = content.split('\n')
        models = []
        in_model = False
        current_model = []
        indent_level = 0
        
        for i, line in enumerate(lines):
            if 'class ' in line and 'BaseModel' in line:
                in_model = True
                current_model = [line]
                indent_level = len(line) - len(line.lstrip())
            elif in_model:
                current_model.append(line)
                # Si encontramos una línea sin indentación o con menor indentación, terminó el modelo
                if line.strip() and not line.startswith(' ' * (indent_level + 1)) and i > 0:
                    if not line.strip().startswith('"""') and not line.strip().startswith('#'):
                        models.append('\n'.join(current_model[:-1]))
                        in_model = False
                        current_model = []
        
        return '\n\n'.join(models) if models else ''
    
    def find_function_end(self, lines: List[str], start_idx: int) -> int:
        """Encuentra el final de una función"""
        indent_level = len(lines[start_idx]) - len(lines[start_idx].lstrip())
        
        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':
                continue
            current_indent = len(line) - len(line.lstrip())
            
            # Si encontramos una línea con igual o menor indentación que no es parte de la función
            if current_indent <= indent_level and (line.startswith('async def ') or line.startswith('def ') or line.startswith('@')):
                return i - 1
        
        return len(lines) - 1
    
    def extract_endpoints(self, content: str) -> Dict[str, List[Tuple[str, str]]]:
        """Extrae endpoints categorizados"""
        lines = content.split('\n')
        endpoints = {
            'cursos': [],
            'inscripciones': [],
            'comentarios': [],
            'tareas': [],
            'archivos': [],
            'reacciones': []
        }
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.strip().startswith('@router.'):
                # Encontrar el endpoint completo
                decorator = line
                func_start = i + 1
                
                # Saltar líneas vacías o decoradores adicionales
                while func_start < len(lines) and (lines[func_start].strip() == '' or lines[func_start].strip().startswith('@')):
                    func_start += 1
                
                if func_start < len(lines) and 'async def ' in lines[func_start]:
                    func_end = self.find_function_end(lines, func_start)
                    
                    # Extraer todo el endpoint (decorador + función)
                    endpoint_lines = lines[i:func_end + 1]
                    endpoint_code = '\n'.join(endpoint_lines)
                    
                    # Categorizar
                    func_name = lines[func_start].strip()
                    path = decorator.lower()
                    
                    if 'debug' in path or 'debug' in func_name:
                        pass  # Ignorar debug endpoints
                    elif 'comentario' in path or 'comentario' in func_name or 'respuesta' in func_name:
                        endpoints['comentarios'].append((decorator, endpoint_code))
                    elif 'tarea' in path or 'tarea' in func_name:
                        endpoints['tareas'].append((decorator, endpoint_code))
                    elif 'archivo' in path or 'archivo' in func_name:
                        endpoints['archivos'].append((decorator, endpoint_code))
                    elif 'reacci' in path or 'reacci' in func_name:
                        endpoints['reacciones'].append((decorator, endpoint_code))
                    elif 'programa' in path or 'programa' in func_name or 'inscrib' in func_name or 'vincular' in func_name or 'codigo' in func_name or 'confirmar' in func_name:
                        endpoints['inscripciones'].append((decorator, endpoint_code))
                    else:
                        endpoints['cursos'].append((decorator, endpoint_code))
                    
                    i = func_end + 1
                    continue
            
            i += 1
        
        return endpoints
    
    def create_file_header(self, title: str, description: str) -> str:
        """Crea el header de un archivo"""
        return f'''"""
{title}

{description}
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Header
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import os
import uuid
import aiofiles
import json

from src.api import deps
from src.db.session import SessionLocal
from src.models.users.usuario import Usuario

# Importaciones para comentarios
from src.crud.communication.comentario import comentario as crud_comentario
from src.schemas.communication.comentario import ComentarioCreate, ComentarioResponse
from src.models.communication.comentario import TipoComentario, Comentario
from src.models.communication.reaccion import Reaccion

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

'''
    
    def create_router_line(self, prefix: str) -> str:
        """Crea la línea de configuración del router"""
        return f'# Configuración del router\nrouter = APIRouter(prefix="/cursos{prefix}")\n\n'
    
    def generate_files(self):
        """Genera los 6 archivos divididos"""
        print("\n" + "="*90)
        print("✂️  DIVIDIENDO ARCHIVO CURSO.PY")
        print("="*90)
        
        # 1. Leer archivo original
        content = self.read_curso_file()
        print(f"\n📖 Archivo original: {len(content)} caracteres, {len(content.splitlines())} líneas")
        
        # 2. Hacer backup
        backup_path = self.curso_file.parent / f"curso_backup_{int(datetime.now().timestamp())}.py"
        shutil.copy(self.curso_file, backup_path)
        print(f"💾 Backup creado: {backup_path.name}")
        
        # 3. Extraer componentes
        models = self.extract_models(content)
        endpoints = self.extract_endpoints(content)
        
        # 4. Generar archivos
        files_config = [
            {
                'name': 'cursos.py',
                'prefix': '',
                'title': 'Rutas de API para gestión básica de cursos',
                'description': 'Endpoints para listar y obtener detalles de cursos',
                'category': 'cursos'
            },
            {
                'name': 'inscripciones.py',
                'prefix': '/inscripciones',
                'title': 'Rutas de API para inscripciones y vinculación a cursos',
                'description': 'Endpoints para inscripción, vinculación y códigos de acceso',
                'category': 'inscripciones'
            },
            {
                'name': 'curso_comentarios.py',
                'prefix': '/comentarios',
                'title': 'Rutas de API para comentarios en cursos',
                'description': 'Endpoints para crear, editar, eliminar comentarios y respuestas',
                'category': 'comentarios'
            },
            {
                'name': 'curso_tareas.py',
                'prefix': '/tareas',
                'title': 'Rutas de API para tareas de cursos',
                'description': 'Endpoints para gestionar tareas de cursos',
                'category': 'tareas'
            },
            {
                'name': 'curso_archivos.py',
                'prefix': '/archivos',
                'title': 'Rutas de API para archivos de cursos',
                'description': 'Endpoints para subir y gestionar archivos de cursos',
                'category': 'archivos'
            },
            {
                'name': 'curso_reacciones.py',
                'prefix': '/reacciones',
                'title': 'Rutas de API para reacciones en cursos',
                'description': 'Endpoints para gestionar reacciones a comentarios',
                'category': 'reacciones'
            }
        ]
        
        print("\n📝 Generando archivos:")
        
        for config in files_config:
            file_path = self.output_dir / config['name']
            category_endpoints = endpoints.get(config['category'], [])
            
            if not category_endpoints and config['category'] not in ['archivos', 'reacciones']:
                print(f"   ⚠️  {config['name']}: Sin endpoints, saltando...")
                continue
            
            with open(file_path, 'w', encoding='utf-8') as f:
                # Header
                f.write(self.create_file_header(config['title'], config['description']))
                
                # Router
                f.write(self.create_router_line(config['prefix']))
                
                # Modelos (solo en algunos archivos)
                if config['category'] in ['inscripciones', 'cursos']:
                    f.write("# Modelos de datos\n")
                    if config['category'] == 'inscripciones':
                        f.write("""
class CourseInscriptionRequest(BaseModel):
    codigo_curso: str

class EstudianteVinculacionRequest(BaseModel):
    codigo_invitacion: Optional[str] = None

class CodigoInvitacionGenerate(BaseModel):
    programa_id: str
    descripcion: Optional[str] = None

""")
                    elif config['category'] == 'cursos':
                        f.write("""
class CourseResponse(BaseModel):
    success: bool
    message: str
    data: List[dict]
    total: int
    source: str
    user_role: str
    empty_state: bool
    empty_message: Optional[str] = None

""")
                
                # Endpoints
                f.write("# Endpoints\n\n")
                for _, endpoint_code in category_endpoints:
                    f.write(endpoint_code)
                    f.write("\n\n")
            
            print(f"   ✅ {config['name']}: {len(category_endpoints)} endpoints")
        
        print("\n" + "="*90)
        print("✅ DIVISIÓN COMPLETADA")
        print("="*90)
        print(f"\n📁 Archivos generados en: {self.output_dir}")
        print(f"💾 Backup original: {backup_path}")
        
        return files_config

def main():
    backend_path = "/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend"
    splitter = CursoSplitter(backend_path)
    
    print("="*90)
    print("🔪 DIVISIÓN AUTOMÁTICA DE CURSO.PY")
    print("="*90)
    print("\nEste script dividirá curso.py (2804 líneas) en 6 archivos:")
    print("  1. cursos.py - Gestión básica de cursos")
    print("  2. inscripciones.py - Inscripción y vinculación")
    print("  3. curso_comentarios.py - Sistema de comentarios")
    print("  4. curso_tareas.py - Gestión de tareas")
    print("  5. curso_archivos.py - Subida de archivos")
    print("  6. curso_reacciones.py - Sistema de reacciones")
    
    files = splitter.generate_files()
    
    print("\n" + "="*90)
    print("📋 SIGUIENTES PASOS")
    print("="*90)
    print("\n1. Actualizar src/api/routes.py para importar los nuevos routers")
    print("2. Crear services para separar lógica de negocio")
    print("3. Probar que todos los endpoints funcionen correctamente")
    print("\n" + "="*90)

if __name__ == "__main__":
    main()
