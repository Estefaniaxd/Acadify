#!/usr/bin/env python3
"""
Script para popular dominios en instituciones existentes.
"""

import sys
import os

# Añadir el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.db.session import SessionLocal
from src.crud.academic.crud_institucion import institucion_crud


# Mapeo de instituciones conocidas a dominios
DOMINIOS_CONOCIDOS = {
    'arp': 'arp.edu.co',
    'ejemplo': 'ejemplo.edu.co',
    'demo': 'demo.edu.co',
    'sena': 'sena.edu.co',
    'unal': 'unal.edu.co',
    'udea': 'udea.edu.co',
}


def populate_domains():
    """Actualiza instituciones existentes con sus dominios"""
    db = SessionLocal()
    try:
        instituciones = institucion_crud.get_multi(db, skip=0, limit=1000)
        updated_count = 0
        
        print(f"Encontradas {len(instituciones)} instituciones")
        
        for inst in instituciones:
            # Intentar inferir dominio del nombre o sigla
            nombre_lower = inst.nombre.lower() if inst.nombre else ''
            sigla_lower = inst.sigla.lower() if inst.sigla else ''
            
            dominio_asignado = None
            
            # Buscar en mapeo conocido
            for key, domain in DOMINIOS_CONOCIDOS.items():
                if key in nombre_lower or key in sigla_lower:
                    dominio_asignado = domain
                    break
            
            # Si no se encontró dominio pero tiene correo, extraer dominio del correo
            if not dominio_asignado and inst.correo_institucional:
                dominio_asignado = inst.correo_institucional.split('@')[-1].lower()
            
            # Actualizar si se encontró dominio
            if dominio_asignado and not inst.dominio:
                institucion_crud.update(
                    db,
                    db_obj=inst,
                    obj_in={'dominio': dominio_asignado}
                )
                print(f"✅ {inst.nombre} → {dominio_asignado}")
                updated_count += 1
            elif inst.dominio:
                print(f"⏭️  {inst.nombre} ya tiene dominio: {inst.dominio}")
            else:
                print(f"⚠️  {inst.nombre} - no se pudo inferir dominio")
        
        db.commit()
        print(f"\n✅ Actualizadas {updated_count} instituciones")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_domains()
