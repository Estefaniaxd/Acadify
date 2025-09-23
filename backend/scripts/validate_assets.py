#!/usr/bin/env python3
"""
Script para validar assets de avatars.
Verifica integridad, formato y genera reportes.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Añadir el directorio src al path para importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.image_utils import (
    validate_asset_file, 
    STANDARD_RESOLUTION, 
    MAX_FILE_SIZE,
    normalize_image,
    save_normalized_image
)
from src.core.config import settings


class AssetValidator:
    """Validador de assets de avatars."""
    
    def __init__(self, assets_dir: str):
        """
        Inicializa el validador.
        
        Args:
            assets_dir: Directorio de assets a validar
        """
        self.assets_dir = Path(assets_dir)
        self.issues = defaultdict(list)
        self.stats = {
            'total_files': 0,
            'valid_files': 0,
            'invalid_files': 0,
            'normalized_files': 0,
            'categories': defaultdict(int),
            'file_sizes': [],
            'dimensions': defaultdict(int)
        }
    
    def validate_directory_structure(self) -> List[str]:
        """
        Valida la estructura de directorios.
        
        Returns:
            Lista de issues encontrados
        """
        issues = []
        
        if not self.assets_dir.exists():
            issues.append(f"Assets directory does not exist: {self.assets_dir}")
            return issues
        
        if not self.assets_dir.is_dir():
            issues.append(f"Assets path is not a directory: {self.assets_dir}")
            return issues
        
        # Verificar categorías esperadas
        expected_categories = {'base', 'hair', 'eyes', 'clothes', 'accessories', 'backgrounds'}
        found_categories = set()
        
        for item in self.assets_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                found_categories.add(item.name)
        
        missing_categories = expected_categories - found_categories
        if missing_categories:
            issues.append(f"Missing categories: {', '.join(missing_categories)}")
        
        unexpected_categories = found_categories - expected_categories
        if unexpected_categories:
            issues.append(f"Unexpected categories: {', '.join(unexpected_categories)}")
        
        # Verificar que las categorías no estén vacías
        for category in found_categories:
            category_path = self.assets_dir / category
            png_files = list(category_path.glob('*.png'))
            if not png_files:
                issues.append(f"Empty category: {category}")
        
        return issues
    
    def validate_asset_file_extended(self, file_path: Path) -> Dict[str, Any]:
        """
        Valida un archivo de asset con información extendida.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Dict con información de validación extendida
        """
        result = {
            'path': str(file_path),
            'valid': False,
            'issues': [],
            'warnings': [],
            'info': {}
        }
        
        try:
            # Validación básica
            validation = validate_asset_file(str(file_path))
            result['valid'] = validation['valid']
            result['info'] = validation
            
            # Verificaciones adicionales
            if not validation['has_transparency']:
                result['warnings'].append("No transparency detected - may not blend properly")
            
            if not validation['matches_standard']:
                result['warnings'].append(f"Non-standard resolution: {validation['dimensions']}")
            
            file_size_mb = validation['size'] / (1024 * 1024)
            if file_size_mb > 0.5:  # 500KB
                result['warnings'].append(f"Large file size: {file_size_mb:.2f}MB")
            
            # Verificar naming convention
            if not self._is_valid_filename(file_path.name):
                result['warnings'].append("Filename doesn't follow convention (category_number.png)")
            
        except Exception as e:
            result['valid'] = False
            result['issues'].append(str(e))
        
        return result
    
    def _is_valid_filename(self, filename: str) -> bool:
        """
        Verifica si el nombre del archivo sigue la convención.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            True si es válido
        """
        if not filename.endswith('.png'):
            return False
        
        name = filename[:-4]  # Remove .png
        
        # Check for category_number pattern
        if '_' not in name:
            return False
        
        parts = name.split('_')
        if len(parts) < 2:
            return False
        
        # Last part should be a number
        try:
            int(parts[-1])
            return True
        except ValueError:
            return False
    
    def validate_all_assets(self) -> Dict[str, Any]:
        """
        Valida todos los assets del directorio.
        
        Returns:
            Reporte completo de validación
        """
        print(f"Validating assets in: {self.assets_dir}")
        
        # Validar estructura de directorios
        structure_issues = self.validate_directory_structure()
        if structure_issues:
            self.issues['structure'] = structure_issues
        
        if not self.assets_dir.exists():
            return self._generate_report()
        
        # Validar archivos por categoría
        for category_path in self.assets_dir.iterdir():
            if category_path.is_dir() and not category_path.name.startswith('.'):
                category = category_path.name
                print(f"  Validating category: {category}")
                
                png_files = list(category_path.glob('*.png'))
                self.stats['categories'][category] = len(png_files)
                
                for file_path in png_files:
                    self.stats['total_files'] += 1
                    
                    # Validar archivo
                    validation = self.validate_asset_file_extended(file_path)
                    
                    if validation['valid']:
                        self.stats['valid_files'] += 1
                        
                        # Estadísticas
                        info = validation['info']
                        self.stats['file_sizes'].append(info['size'])
                        
                        dim_key = f"{info['dimensions'][0]}x{info['dimensions'][1]}"
                        self.stats['dimensions'][dim_key] += 1
                        
                        if info['matches_standard']:
                            self.stats['normalized_files'] += 1
                    else:
                        self.stats['invalid_files'] += 1
                        self.issues[f"{category}/{file_path.name}"] = validation['issues']
                    
                    # Agregar warnings si los hay
                    if validation['warnings']:
                        if 'warnings' not in self.issues:
                            self.issues['warnings'] = []
                        for warning in validation['warnings']:
                            self.issues['warnings'].append(f"{category}/{file_path.name}: {warning}")
        
        return self._generate_report()
    
    def _generate_report(self) -> Dict[str, Any]:
        """
        Genera reporte de validación.
        
        Returns:
            Reporte completo
        """
        # Calcular estadísticas adicionales
        if self.stats['file_sizes']:
            avg_size = sum(self.stats['file_sizes']) / len(self.stats['file_sizes'])
            max_size = max(self.stats['file_sizes'])
            min_size = min(self.stats['file_sizes'])
        else:
            avg_size = max_size = min_size = 0
        
        report = {
            'validation_summary': {
                'total_files': self.stats['total_files'],
                'valid_files': self.stats['valid_files'],
                'invalid_files': self.stats['invalid_files'],
                'success_rate': (self.stats['valid_files'] / max(self.stats['total_files'], 1)) * 100,
                'normalized_files': self.stats['normalized_files'],
                'normalization_rate': (self.stats['normalized_files'] / max(self.stats['valid_files'], 1)) * 100
            },
            'categories': dict(self.stats['categories']),
            'file_size_stats': {
                'average_kb': avg_size / 1024 if avg_size else 0,
                'max_kb': max_size / 1024 if max_size else 0,
                'min_kb': min_size / 1024 if min_size else 0,
                'total_mb': sum(self.stats['file_sizes']) / (1024 * 1024) if self.stats['file_sizes'] else 0
            },
            'dimension_stats': dict(self.stats['dimensions']),
            'issues': dict(self.issues)
        }
        
        return report
    
    async def normalize_non_standard_assets(self, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Normaliza assets que no tienen la resolución estándar.
        
        Args:
            output_dir: Directorio de salida (opcional)
            
        Returns:
            Reporte de normalización
        """
        if output_dir is None:
            output_dir = str(self.assets_dir / "normalized")
        
        output_path = Path(output_dir)
        
        print(f"Normalizing non-standard assets to: {output_path}")
        
        normalization_stats = {
            'processed': 0,
            'normalized': 0,
            'skipped': 0,
            'errors': []
        }
        
        for category_path in self.assets_dir.iterdir():
            if category_path.is_dir() and category_path.name not in ['normalized', '.git']:
                category = category_path.name
                category_output = output_path / category
                category_output.mkdir(parents=True, exist_ok=True)
                
                print(f"  Processing category: {category}")
                
                for file_path in category_path.glob('*.png'):
                    try:
                        normalization_stats['processed'] += 1
                        
                        # Verificar si necesita normalización
                        validation = validate_asset_file(str(file_path))
                        
                        if validation['matches_standard']:
                            normalization_stats['skipped'] += 1
                            continue
                        
                        # Normalizar
                        normalized_img = normalize_image(str(file_path))
                        output_file = category_output / file_path.name
                        
                        await save_normalized_image(normalized_img, str(output_file))
                        
                        print(f"    Normalized: {file_path.name}")
                        normalization_stats['normalized'] += 1
                        
                    except Exception as e:
                        error_msg = f"Error normalizing {file_path}: {str(e)}"
                        normalization_stats['errors'].append(error_msg)
                        print(f"    Error: {error_msg}")
        
        return normalization_stats


def print_report(report: Dict[str, Any]):
    """
    Imprime un reporte formateado.
    
    Args:
        report: Reporte de validación
    """
    print("\n" + "="*60)
    print("ASSET VALIDATION REPORT")
    print("="*60)
    
    # Resumen
    summary = report['validation_summary']
    print(f"Total Files: {summary['total_files']}")
    print(f"Valid Files: {summary['valid_files']}")
    print(f"Invalid Files: {summary['invalid_files']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Normalized Files: {summary['normalized_files']}")
    print(f"Normalization Rate: {summary['normalization_rate']:.1f}%")
    
    # Categorías
    print(f"\nCategories:")
    for category, count in report['categories'].items():
        print(f"  {category}: {count} files")
    
    # Estadísticas de tamaño
    size_stats = report['file_size_stats']
    print(f"\nFile Size Statistics:")
    print(f"  Average: {size_stats['average_kb']:.1f} KB")
    print(f"  Maximum: {size_stats['max_kb']:.1f} KB")
    print(f"  Minimum: {size_stats['min_kb']:.1f} KB")
    print(f"  Total: {size_stats['total_mb']:.2f} MB")
    
    # Dimensiones
    print(f"\nDimension Statistics:")
    for dimension, count in report['dimension_stats'].items():
        print(f"  {dimension}: {count} files")
    
    # Issues
    if report['issues']:
        print(f"\nISSUES FOUND:")
        for category, issues in report['issues'].items():
            print(f"\n{category.upper()}:")
            if isinstance(issues, list):
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print(f"  - {issues}")
    else:
        print(f"\n✅ No issues found!")
    
    print("="*60)


async def main():
    """Función principal del script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate avatar assets')
    parser.add_argument('--assets-dir', default=settings.AVATAR_ASSETS_PATH,
                       help='Assets directory to validate')
    parser.add_argument('--normalize', action='store_true',
                       help='Normalize non-standard assets')
    parser.add_argument('--output-dir', 
                       help='Output directory for normalized assets')
    
    args = parser.parse_args()
    
    print("=== Avatar Assets Validator ===")
    print(f"Assets directory: {args.assets_dir}")
    
    # Crear validador
    validator = AssetValidator(args.assets_dir)
    
    # Validar assets
    report = validator.validate_all_assets()
    print_report(report)
    
    # Normalizar si se solicita
    if args.normalize:
        print(f"\n{'='*60}")
        print("NORMALIZING ASSETS")
        print("="*60)
        
        normalization_report = await validator.normalize_non_standard_assets(args.output_dir)
        
        print(f"\nNormalization Results:")
        print(f"  Processed: {normalization_report['processed']}")
        print(f"  Normalized: {normalization_report['normalized']}")
        print(f"  Skipped: {normalization_report['skipped']}")
        
        if normalization_report['errors']:
            print(f"  Errors:")
            for error in normalization_report['errors']:
                print(f"    - {error}")
    
    # Exit code basado en resultados
    if report['validation_summary']['invalid_files'] > 0:
        print(f"\n❌ Validation failed: {report['validation_summary']['invalid_files']} invalid files")
        sys.exit(1)
    else:
        print(f"\n✅ Validation passed: all files are valid")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())