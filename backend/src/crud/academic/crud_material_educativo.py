from sqlalchemy.orm import Session, selectinload
from ..base import CRUDBase
from ...models.academic.material_educativo import MaterialEducativo
from ...schemas.academic.material_educativo import MaterialEducativoCreate, MaterialEducativoUpdate, MaterialEducativoSubirVersion
from ...enums.academic.material_educativo_enums import TipoMaterialEducativo, CarpetaMaterial, EstadoMaterial
from uuid import UUID
from typing import List, Optional
from sqlalchemy import and_, or_, func, desc
import hashlib
import os


class CRUDMaterialEducativo(CRUDBase[MaterialEducativo, MaterialEducativoCreate, MaterialEducativoUpdate]):
    
    def get(self, db: Session, material_id: UUID) -> Optional[MaterialEducativo]:
        """Obtiene material educativo por ID con relaciones"""
        return db.query(MaterialEducativo).options(
            selectinload(MaterialEducativo.autor),
            selectinload(MaterialEducativo.versiones_anteriores)
        ).filter(MaterialEducativo.material_id == material_id).first()

    def get_multi_by_carpeta(
        self, 
        db: Session, 
        carpeta: CarpetaMaterial,
        skip: int = 0, 
        limit: int = 100,
        solo_activos: bool = True
    ) -> List[MaterialEducativo]:
        """Obtiene material por carpeta"""
        query = db.query(MaterialEducativo).filter(MaterialEducativo.carpeta == carpeta)
        
        if solo_activos:
            query = query.filter(MaterialEducativo.estado == EstadoMaterial.activo)
            
        return query.filter(
            MaterialEducativo.es_version_actual == True
        ).offset(skip).limit(limit).all()

    def get_multi_by_autor(
        self, 
        db: Session, 
        autor_id: UUID,
        skip: int = 0, 
        limit: int = 100
    ) -> List[MaterialEducativo]:
        """Obtiene material por autor"""
        return db.query(MaterialEducativo).filter(
            and_(
                MaterialEducativo.autor_id == autor_id,
                MaterialEducativo.es_version_actual == True
            )
        ).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: MaterialEducativoCreate) -> MaterialEducativo:
        """Crea nuevo material educativo"""
        # Calcular hash si no se proporciona
        if not obj_in.hash_archivo and obj_in.url_archivo:
            obj_in.hash_archivo = self._calcular_hash_archivo(obj_in.url_archivo)
            
        db_obj = MaterialEducativo(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, 
        db: Session, 
        db_obj: MaterialEducativo, 
        obj_in: MaterialEducativoUpdate
    ) -> MaterialEducativo:
        """Actualiza material educativo existente"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def subir_nueva_version(
        self, 
        db: Session, 
        material_id: UUID, 
        nueva_version: MaterialEducativoSubirVersion,
        autor_id: UUID
    ) -> MaterialEducativo:
        """Sube una nueva versión del material"""
        
        # Obtener material original
        material_original = self.get(db, material_id)
        if not material_original:
            raise ValueError("Material original no encontrado")
        
        # Marcar la versión actual como no actual
        material_original.es_version_actual = False
        db.add(material_original)
        
        # Calcular nueva versión
        ultima_version = db.query(func.max(MaterialEducativo.version)).filter(
            MaterialEducativo.material_original_id == material_id
        ).scalar() or material_original.version
        
        nueva_version_numero = ultima_version + 1
        
        # Calcular hash
        hash_archivo = nueva_version.hash_archivo or self._calcular_hash_archivo(nueva_version.url_archivo)
        
        # Crear nueva versión
        nueva_version_obj = MaterialEducativo(
            titulo=material_original.titulo,
            descripcion=material_original.descripcion,
            tipo_material=material_original.tipo_material,
            carpeta=material_original.carpeta,
            url_archivo=nueva_version.url_archivo,
            formato_archivo=nueva_version.formato_archivo,
            tamano_archivo=nueva_version.tamano_archivo,
            hash_archivo=hash_archivo,
            version=nueva_version_numero,
            material_original_id=material_id,
            es_version_actual=True,
            autor_id=autor_id,
            tags=material_original.tags
        )
        
        db.add(nueva_version_obj)
        db.commit()
        db.refresh(nueva_version_obj)
        return nueva_version_obj

    def buscar_material(
        self, 
        db: Session, 
        termino_busqueda: str,
        carpeta: Optional[CarpetaMaterial] = None,
        tipo_material: Optional[TipoMaterialEducativo] = None,
        autor_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MaterialEducativo]:
        """Busca material educativo"""
        query = db.query(MaterialEducativo)
        
        # Solo versiones actuales
        query = query.filter(MaterialEducativo.es_version_actual == True)
        query = query.filter(MaterialEducativo.estado == EstadoMaterial.activo)
        
        # Búsqueda por término
        query = query.filter(
            or_(
                MaterialEducativo.titulo.ilike(f"%{termino_busqueda}%"),
                MaterialEducativo.descripcion.ilike(f"%{termino_busqueda}%"),
                MaterialEducativo.tags.ilike(f"%{termino_busqueda}%")
            )
        )
        
        # Filtros adicionales
        if carpeta:
            query = query.filter(MaterialEducativo.carpeta == carpeta)
        if tipo_material:
            query = query.filter(MaterialEducativo.tipo_material == tipo_material)
        if autor_id:
            query = query.filter(MaterialEducativo.autor_id == autor_id)
            
        return query.offset(skip).limit(limit).all()

    def registrar_descarga(self, db: Session, material_id: UUID) -> bool:
        """Registra una descarga del material"""
        material = self.get(db, material_id)
        if not material:
            return False
            
        material.numero_descargas += 1
        material.fecha_ultimo_acceso = func.now()
        
        db.add(material)
        db.commit()
        return True

    def _calcular_hash_archivo(self, url_archivo: str) -> Optional[str]:
        """Calcula el hash SHA-256 de un archivo"""
        try:
            # Si es una ruta local, calcular hash del archivo
            if os.path.exists(url_archivo):
                with open(url_archivo, 'rb') as f:
                    return hashlib.sha256(f.read()).hexdigest()
            else:
                # Para URLs remotas, usar la URL como base para el hash
                return hashlib.sha256(url_archivo.encode()).hexdigest()
        except Exception:
            return None


material_educativo_crud = CRUDMaterialEducativo(MaterialEducativo, id_field="material_id")
