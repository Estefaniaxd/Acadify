"""CRUD del módulo académico.

Exporta todas las instancias CRUD para acceso centralizado.
"""

from .crud_curso import curso_crud
from .crud_grupo import grupo_crud
from .crud_inscripcion import inscripcion_crud
from .crud_institucion import institucion_crud
from .crud_periodo_academico import periodo_academico_crud
from .crud_programa import programa_crud


__all__ = [
    "curso_crud",
    "grupo_crud",
    "inscripcion_crud",
    "institucion_crud",
    "periodo_academico_crud",
    "programa_crud",
]
