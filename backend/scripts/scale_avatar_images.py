"""
Script para escalar imágenes de avatares a 512x512px.
Este script NO debe ejecutarse ahora, está preparado para futuras actualizaciones.

Uso:
    python scripts/scale_avatar_images.py --input=ruta/nueva_ropa --output=static/assets/categoria

Características:
    - Escala manteniendo aspect ratio
    - Añade padding transparente si es necesario
    - Optimiza PNG
    - Genera backup antes de procesar
    - Crea manifest automáticamente
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

try:
    from PIL import Image
    import hashlib
    import json
except ImportError:
    print("❌ Error: PIL (Pillow) no está instalado")
    print("Instalar con: pip install Pillow")
    sys.exit(1)

# Resolución estándar para avatares
STANDARD_SIZE = (512, 512)
SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.webp']


class ImageScaler:
    """Clase para escalar y normalizar imágenes de avatares."""
    
    def __init__(self, backup: bool = True, optimize: bool = True):
        self.backup = backup
        self.optimize = optimize
        self.processed = []
        self.errors = []
    
    def scale_image(
        self, 
        input_path: str, 
        output_path: str,
        size: Tuple[int, int] = STANDARD_SIZE
    ) -> bool:
        """
        Escala una imagen a tamaño estándar manteniendo aspect ratio.
        
        Args:
            input_path: Ruta de la imagen original
            output_path: Ruta donde guardar la imagen escalada
            size: Tamaño objetivo (width, height)
            
        Returns:
            True si se procesó correctamente, False si hubo error
        """
        try:
            # Abrir imagen
            with Image.open(input_path) as img:
                # Convertir a RGBA si no lo es (para transparencia)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Calcular nuevo tamaño manteniendo aspect ratio
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Crear canvas del tamaño objetivo con transparencia
                canvas = Image.new('RGBA', size, (0, 0, 0, 0))
                
                # Centrar la imagen en el canvas
                x = (size[0] - img.width) // 2
                y = (size[1] - img.height) // 2
                canvas.paste(img, (x, y), img)
                
                # Crear directorio de salida si no existe
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Guardar imagen optimizada
                if self.optimize:
                    canvas.save(
                        output_path, 
                        'PNG', 
                        optimize=True,
                        compress_level=9
                    )
                else:
                    canvas.save(output_path, 'PNG')
                
                # Verificar tamaño final
                final_img = Image.open(output_path)
                if final_img.size != size:
                    raise ValueError(f"Tamaño final incorrecto: {final_img.size}")
                
                self.processed.append(output_path)
                return True
                
        except Exception as e:
            error_msg = f"Error procesando {input_path}: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return False
    
    def process_directory(
        self, 
        input_dir: str, 
        output_dir: str,
        category: str,
        recursive: bool = False
    ) -> dict:
        """
        Procesa todas las imágenes de un directorio.
        
        Args:
            input_dir: Directorio con imágenes originales
            output_dir: Directorio de salida
            category: Categoría para el manifest (hair, clothes, etc.)
            recursive: Si procesar subdirectorios
            
        Returns:
            Dict con estadísticas del proceso
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            raise ValueError(f"Directorio no existe: {input_dir}")
        
        # Crear backup si está habilitado
        if self.backup:
            backup_dir = input_path.parent / f"backup_{input_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"📦 Creando backup en: {backup_dir}")
            shutil.copytree(input_path, backup_dir)
        
        # Encontrar todas las imágenes
        if recursive:
            pattern = '**/*'
        else:
            pattern = '*'
        
        image_files = []
        for ext in SUPPORTED_FORMATS:
            image_files.extend(input_path.glob(f"{pattern}{ext}"))
        
        total_files = len(image_files)
        print(f"\n📂 Encontradas {total_files} imágenes en {input_dir}")
        print(f"🎯 Procesando a {STANDARD_SIZE[0]}x{STANDARD_SIZE[1]}px...")
        
        manifest_data = []
        
        for idx, img_file in enumerate(image_files, 1):
            # Mantener estructura de subdirectorios
            relative_path = img_file.relative_to(input_path)
            output_file = output_path / relative_path.with_suffix('.png')
            
            print(f"[{idx}/{total_files}] {relative_path}...", end=' ')
            
            if self.scale_image(str(img_file), str(output_file)):
                print("✅")
                
                # Agregar al manifest
                file_stats = os.stat(output_file)
                manifest_data.append({
                    "filename": str(relative_path.with_suffix('.png')),
                    "display_name": relative_path.stem.replace('_', ' ').title(),
                    "category": category,
                    "file_size": file_stats.st_size,
                    "width": STANDARD_SIZE[0],
                    "height": STANDARD_SIZE[1],
                    "hash": self._get_file_hash(output_file)
                })
            else:
                print("❌")
        
        # Guardar manifest
        manifest_file = output_path / f"{category}_manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📝 Manifest guardado en: {manifest_file}")
        
        return {
            "total": total_files,
            "processed": len(self.processed),
            "errors": len(self.errors),
            "manifest": str(manifest_file)
        }
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calcula hash SHA256 de un archivo."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def print_summary(self, stats: dict):
        """Imprime resumen del proceso."""
        print("\n" + "="*60)
        print("📊 RESUMEN DEL PROCESO")
        print("="*60)
        print(f"Total imágenes encontradas: {stats['total']}")
        print(f"✅ Procesadas correctamente: {stats['processed']}")
        print(f"❌ Con errores: {stats['errors']}")
        
        if stats['errors'] > 0:
            print("\n⚠️  ERRORES:")
            for error in self.errors:
                print(f"   - {error}")
        
        print(f"\n📦 Manifest generado: {stats['manifest']}")
        print("="*60)


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description='Escala imágenes de avatares a 512x512px',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Escalar nueva ropa de camisas
  python scripts/scale_avatar_images.py \\
      --input=nueva_ropa/camisas \\
      --output=static/assets/shirt \\
      --category=shirt

  # Escalar accesorios sin backup
  python scripts/scale_avatar_images.py \\
      --input=nueva_ropa/accessories \\
      --output=static/assets/accessories \\
      --category=accessories \\
      --no-backup

  # Escalar recursivamente subdirectorios
  python scripts/scale_avatar_images.py \\
      --input=nueva_ropa/completo \\
      --output=static/assets \\
      --category=mixed \\
      --recursive
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Directorio con imágenes originales'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Directorio de salida para imágenes escaladas'
    )
    
    parser.add_argument(
        '--category', '-c',
        required=True,
        choices=['hair', 'eyes', 'base', 'clothes', 'shirt', 'pants', 'accessories', 'backgrounds', 'mixed'],
        help='Categoría de las imágenes'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='No crear backup de imágenes originales'
    )
    
    parser.add_argument(
        '--no-optimize',
        action='store_true',
        help='No optimizar compresión PNG'
    )
    
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Procesar subdirectorios recursivamente'
    )
    
    parser.add_argument(
        '--size',
        type=int,
        nargs=2,
        default=[512, 512],
        metavar=('WIDTH', 'HEIGHT'),
        help='Tamaño objetivo (default: 512 512)'
    )
    
    args = parser.parse_args()
    
    # Validar rutas
    if not os.path.exists(args.input):
        print(f"❌ Error: El directorio de entrada no existe: {args.input}")
        sys.exit(1)
    
    # Confirmar antes de procesar
    print("⚠️  ADVERTENCIA: Este script modificará las imágenes")
    print(f"📁 Input:  {args.input}")
    print(f"📁 Output: {args.output}")
    print(f"📏 Tamaño: {args.size[0]}x{args.size[1]}px")
    print(f"📦 Backup: {'NO' if args.no_backup else 'SÍ'}")
    
    confirm = input("\n¿Continuar? (s/N): ")
    if confirm.lower() != 's':
        print("❌ Cancelado por el usuario")
        sys.exit(0)
    
    # Procesar imágenes
    scaler = ImageScaler(
        backup=not args.no_backup,
        optimize=not args.no_optimize
    )
    
    try:
        # Actualizar tamaño si se especificó
        global STANDARD_SIZE
        STANDARD_SIZE = tuple(args.size)
        
        stats = scaler.process_directory(
            input_dir=args.input,
            output_dir=args.output,
            category=args.category,
            recursive=args.recursive
        )
        
        scaler.print_summary(stats)
        
        # Exit code basado en errores
        sys.exit(1 if stats['errors'] > 0 else 0)
        
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
