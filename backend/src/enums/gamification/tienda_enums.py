"""
Enums para el sistema de tienda virtual.

Este módulo define los tipos y categorías de items disponibles en la tienda,
así como los niveles de rareza para el sistema de gamificación.

Author: GitHub Copilot & Team
Date: 31 de octubre de 2025
Version: 1.0.0
"""

import enum


class CategoriaItem(str, enum.Enum):
    """
    Categorías de items disponibles en la tienda.
    
    Cada categoría representa un tipo de item que los usuarios
    pueden comprar con sus puntos acumulados.
    """
    # Ropa y apariencia de avatar
    CABELLO = "cabello"
    OJOS = "ojos"
    BOCA = "boca"
    ROPA_SUPERIOR = "ropa_superior"
    ROPA_INFERIOR = "ropa_inferior"
    ZAPATOS = "zapatos"
    ACCESORIOS_CABEZA = "accesorios_cabeza"
    ACCESORIOS_CARA = "accesorios_cara"
    ACCESORIOS_CUERPO = "accesorios_cuerpo"
    
    # Personalización de perfil
    FONDO_AVATAR = "fondo_avatar"
    MARCO_AVATAR = "marco_avatar"
    FONDO_PERFIL = "fondo_perfil"
    
    # Etiquetas
    ETIQUETA = "etiqueta"
    
    # Items funcionales
    FUNCIONAL = "funcional"
    
    # Otros
    OTRO = "otro"


class RarezaItem(str, enum.Enum):
    """
    Niveles de rareza para items de la tienda.
    
    Define la rareza de los items, lo cual afecta:
    - Precio en puntos
    - Disponibilidad
    - Requisitos de nivel
    - Visualización en la tienda
    """
    COMUN = "comun"              # ⬜ Blanco - 50-150 pts
    RARO = "raro"                # 🟦 Azul - 150-400 pts
    EPICO = "epico"              # 🟪 Púrpura - 500-1000 pts
    LEGENDARIO = "legendario"    # 🟧 Dorado - 1000-2500 pts


class MetodoAdquisicion(str, enum.Enum):
    """
    Métodos por los cuales un usuario puede adquirir un item.
    """
    COMPRA = "compra"            # Comprado con puntos
    REGALO = "regalo"            # Regalado por admin/evento
    LOGRO = "logro"              # Desbloqueado por logro
    EVENTO = "evento"            # Item de evento temporal
    INICIAL = "inicial"          # Item inicial gratuito
