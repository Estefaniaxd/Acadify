import enum


class TipoMaterialEducativo(str, enum.Enum):
    pdf = "pdf"
    video = "video"
    audio = "audio"
    imagen = "imagen"
    presentacion = "presentacion"
    documento = "documento"
    hoja_de_calculo = "hoja_de_calculo"
    enlace = "enlace"
    interactivo = "interactivo"
    codigo_fuente = "codigo_fuente"
    otro = "otro"


class CarpetaMaterial(str, enum.Enum):
    lecturas = "lecturas"
    guias = "guias"
    tareas = "tareas"
    examenes = "examenes"
    recursos = "recursos"
    multimedia = "multimedia"
    ejercicios = "ejercicios"
    bibliografias = "bibliografias"
    otros = "otros"


class EstadoMaterial(str, enum.Enum):
    activo = "activo"
    archivado = "archivado"
    borrador = "borrador"
    revision = "revision"
