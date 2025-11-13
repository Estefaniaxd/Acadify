#!/usr/bin/env python3
"""
FieldValidator - Validador Inteligente de Campos de Modelos
===========================================================

Arquitectura: Clean Code + SOLID Principles
- Single Responsibility: Cada clase hace UNA cosa
- Open/Closed: Extensible sin modificar código existente
- Dependency Inversion: Depende de abstracciones, no implementaciones

Author: GitHub Copilot
Date: 1 nov 2025
"""

import re
import ast
from pathlib import Path
from typing import Dict, Set, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


# ==================== VALUE OBJECTS ====================

@dataclass(frozen=True)
class ModelStructure:
    """Value Object: Estructura inmutable de un modelo"""
    name: str
    fields: Set[str]
    primary_key: str
    
    def has_field(self, field_name: str) -> bool:
        """Verifica si el campo existe"""
        return field_name in self.fields


@dataclass
class ValidationResult:
    """Value Object: Resultado de validación"""
    file_path: Path
    total_fields: int
    invalid_fields: List[str]
    valid: bool
    
    @property
    def invalid_count(self) -> int:
        return len(self.invalid_fields)


# ==================== ESTRATEGIAS ====================

class FieldExtractor(ABC):
    """Strategy Pattern: Extractor de campos"""
    
    @abstractmethod
    def extract_fields(self, content: str, class_name: str) -> Set[str]:
        """Extrae campos de un modelo"""
        pass


class SQLAlchemyFieldExtractor(FieldExtractor):
    """Extractor para modelos SQLAlchemy"""
    
    def extract_fields(self, content: str, class_name: str) -> Set[str]:
        """Extrae campos de modelo SQLAlchemy"""
        fields = set()
        
        # Buscar la clase
        class_pattern = rf'class {class_name}\(.*?\):'
        class_match = re.search(class_pattern, content)
        
        if not class_match:
            return fields
            
        # Extraer contenido de la clase
        start = class_match.end()
        
        # Buscar siguiente clase o fin de archivo
        next_class = re.search(r'\nclass \w+\(', content[start:])
        end = start + next_class.start() if next_class else len(content)
        
        class_content = content[start:end]
        
        # Extraer todos los Column()
        column_pattern = r'(\w+)\s*=\s*Column\('
        for match in re.finditer(column_pattern, class_content):
            field_name = match.group(1)
            fields.add(field_name)
            
        # Extraer relationship() también
        rel_pattern = r'(\w+)\s*=\s*relationship\('
        for match in re.finditer(rel_pattern, class_content):
            field_name = match.group(1)
            fields.add(field_name)
            
        return fields


# ==================== REPOSITORIOS ====================

class ModelRepository:
    """Repository Pattern: Gestiona acceso a modelos"""
    
    def __init__(self, models_dir: Path, extractor: FieldExtractor):
        self.models_dir = models_dir
        self.extractor = extractor
        self._cache: Dict[str, ModelStructure] = {}
        
    def get_model_structure(self, model_name: str, relative_path: str) -> Optional[ModelStructure]:
        """Obtiene estructura de un modelo (con caché)"""
        
        # Cache hit
        if model_name in self._cache:
            return self._cache[model_name]
            
        # Cache miss - cargar
        model_file = self.models_dir / relative_path
        
        if not model_file.exists():
            return None
            
        content = model_file.read_text()
        fields = self.extractor.extract_fields(content, model_name)
        
        # Detectar primary key
        pk = self._detect_primary_key(content, model_name)
        
        structure = ModelStructure(
            name=model_name,
            fields=fields,
            primary_key=pk
        )
        
        # Guardar en caché
        self._cache[model_name] = structure
        
        return structure
        
    def _detect_primary_key(self, content: str, class_name: str) -> str:
        """Detecta la primary key del modelo"""
        # Buscar pattern: algo_id = Column(...primary_key=True...)
        pk_pattern = r'(\w+)\s*=\s*Column\([^)]*primary_key\s*=\s*True'
        match = re.search(pk_pattern, content)
        
        if match:
            return match.group(1)
            
        # Default: nombre_clase_id en minúsculas
        return f"{class_name.lower()}_id"


# ==================== SERVICIO PRINCIPAL ====================

class FieldValidatorService:
    """Service: Validador de campos en tests"""
    
    # Mapeo de modelos a sus archivos
    MODEL_PATHS = {
        "Evaluacion": "evaluaciones/evaluacion_expandida.py",
        "IntentoEvaluacion": "evaluaciones/intento_respuesta_gamificacion.py",
        "RespuestaEstudiante": "evaluaciones/intento_respuesta_gamificacion.py",
        "ConfiguracionAntiTrampa": "evaluaciones/configuracion_antitrampa.py",
        "Curso": "academic/curso.py",
        "PreguntaEvaluacion": "evaluaciones/evaluacion_expandida.py",
    }
    
    def __init__(self, backend_dir: Path):
        self.backend_dir = backend_dir
        self.models_dir = backend_dir / "src" / "models"
        self.test_dir = backend_dir / "TEST"
        
        # Dependency Injection
        extractor = SQLAlchemyFieldExtractor()
        self.repository = ModelRepository(self.models_dir, extractor)
        
        self.corrections_made = 0
        
    def load_all_models(self) -> Dict[str, ModelStructure]:
        """Carga estructura de todos los modelos"""
        structures = {}
        
        for model_name, rel_path in self.MODEL_PATHS.items():
            structure = self.repository.get_model_structure(model_name, rel_path)
            if structure:
                structures[model_name] = structure
                
        return structures
        
    def find_invalid_fields_in_file(
        self, 
        test_file: Path, 
        model_structures: Dict[str, ModelStructure]
    ) -> Dict[str, List[str]]:
        """Encuentra campos inválidos en un archivo de test"""
        
        content = test_file.read_text()
        invalid_by_model = {}
        
        for model_name, structure in model_structures.items():
            # Buscar constructores del modelo: ModelName(
            pattern = rf'{model_name}\s*\('
            
            for match in re.finditer(pattern, content):
                # Extraer argumentos del constructor
                start = match.end()
                
                # Buscar el cierre del constructor (maneja anidamiento)
                paren_count = 1
                end = start
                
                while end < len(content) and paren_count > 0:
                    if content[end] == '(':
                        paren_count += 1
                    elif content[end] == ')':
                        paren_count -= 1
                    end += 1
                    
                constructor_content = content[start:end-1]
                
                # Extraer nombres de argumentos keyword
                arg_pattern = r'\b(\w+)\s*='
                for arg_match in re.finditer(arg_pattern, constructor_content):
                    field_name = arg_match.group(1)
                    
                    # Verificar si el campo es válido
                    if not structure.has_field(field_name):
                        if model_name not in invalid_by_model:
                            invalid_by_model[model_name] = []
                        invalid_by_model[model_name].append(field_name)
                        
        return invalid_by_model
        
    def remove_invalid_fields(
        self, 
        test_file: Path, 
        invalid_fields: Dict[str, List[str]]
    ) -> int:
        """Elimina campos inválidos de un archivo"""
        
        content = test_file.read_text()
        original = content
        corrections = 0
        
        # Obtener lista única de campos a eliminar
        all_invalid = set()
        for fields in invalid_fields.values():
            all_invalid.update(fields)
            
        # Eliminar cada campo inválido
        for field in all_invalid:
            # Pattern: campo=valor, o campo=valor)
            patterns = [
                rf',\s*{field}\s*=[^,\)]+(?=,)',  # campo=valor, (con coma después)
                rf',\s*{field}\s*=[^,\)]+(?=\))',  # campo=valor) (antes de cierre)
                rf'\n\s+{field}\s*=[^,\n]+,?\n',   # campo=valor en línea propia
            ]
            
            for pattern in patterns:
                new_content = re.sub(pattern, '', content)
                if new_content != content:
                    content = new_content
                    corrections += 1
                    break
                    
        if content != original:
            test_file.write_text(content)
            
        return corrections
        
    def validate_and_fix_all(self) -> List[ValidationResult]:
        """Valida y corrige todos los archivos de test"""
        
        print("🔍 FieldValidator - Análisis Inteligente")
        print("=" * 70)
        
        # Cargar modelos
        print("\n📚 Cargando estructura de modelos...")
        model_structures = self.load_all_models()
        
        for name, struct in model_structures.items():
            print(f"   ✅ {name}: {len(struct.fields)} campos, PK={struct.primary_key}")
            
        # Validar cada archivo
        results = []
        test_files = list(self.test_dir.glob("test_*.py"))
        
        print(f"\n🔎 Analizando {len(test_files)} archivos de test...")
        
        for test_file in test_files:
            invalid = self.find_invalid_fields_in_file(test_file, model_structures)
            
            if invalid:
                print(f"\n📝 {test_file.name}:")
                
                total_invalid = sum(len(fields) for fields in invalid.values())
                
                for model, fields in invalid.items():
                    unique_fields = list(set(fields))
                    print(f"   ❌ {model}: {unique_fields}")
                    
                # Corregir
                corrections = self.remove_invalid_fields(test_file, invalid)
                self.corrections_made += corrections
                
                print(f"   ✅ Eliminados {corrections} campos inválidos")
                
                results.append(ValidationResult(
                    file_path=test_file,
                    total_fields=total_invalid,
                    invalid_fields=list(set(f for fields in invalid.values() for f in fields)),
                    valid=False
                ))
            else:
                results.append(ValidationResult(
                    file_path=test_file,
                    total_fields=0,
                    invalid_fields=[],
                    valid=True
                ))
                
        return results


# ==================== MAIN ====================

def main():
    """Función principal"""
    import os
    
    backend_dir = Path(os.getcwd())
    validator = FieldValidatorService(backend_dir)
    
    results = validator.validate_and_fix_all()
    
    print(f"\n{'=' * 70}")
    print(f"✅ COMPLETADO: {validator.corrections_made} correcciones aplicadas")
    
    invalid_files = [r for r in results if not r.valid]
    print(f"📊 Archivos corregidos: {len(invalid_files)}/{len(results)}")
    print(f"{'=' * 70}\n")
    
    # Verificar sintaxis
    print("🔍 Verificando sintaxis...")
    all_valid = True
    for result in results:
        try:
            compile(result.file_path.read_text(), result.file_path.name, 'exec')
        except SyntaxError as e:
            print(f"   ❌ {result.file_path.name}: {e}")
            all_valid = False
            
    if all_valid:
        print("   ✅ Sintaxis válida en todos los archivos\n")
        print("🎯 Ejecuta los tests:")
        print("venv/bin/python -m pytest TEST/ -v --tb=short")


if __name__ == "__main__":
    main()
