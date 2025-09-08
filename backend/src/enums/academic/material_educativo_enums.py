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
