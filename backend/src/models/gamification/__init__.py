"""
Módulo de modelos de gamificación.

Exporta todos los modelos relacionados con el sistema de gamificación:
- Puntos e insignias
- Tienda virtual
- Etiquetas de perfil
- Rachas
- Temas

Author: GitHub Copilot & Team
Date: 31 de octubre de 2025
"""

# Modelos existentes
from .usuario_puntos import UsuarioPuntos
from .historial_puntos import HistorialPuntos
from .insignia import Insignia
from .usuario_insignia import UsuarioInsignia
from .recompensa import Recompensa
from .usuario_recompensa import UsuarioRecompensa
from .racha_usuario import RachaUsuario
from .tema import Tema
from .tema_predefinido import TemaPredefinido
from .tema_personalizado import TemaPersonalizado

# Modelos nuevos - Tienda
from .tienda_item import TiendaItem
from .inventario_usuario import InventarioUsuario
from .transaccion_tienda import TransaccionTienda

# Modelos nuevos - Etiquetas
from .etiqueta_perfil import EtiquetaPerfil
from .usuario_etiqueta import UsuarioEtiqueta

# Modelos nuevos - Rachas
from .historial_racha import HistorialRacha
from .recompensa_racha import RecompensaRacha

__all__ = [
    # Puntos
    "UsuarioPuntos",
    "HistorialPuntos",
    # Insignias
    "Insignia",
    "UsuarioInsignia",
    # Recompensas
    "Recompensa",
    "UsuarioRecompensa",
    # Rachas
    "RachaUsuario",
    "HistorialRacha",
    "RecompensaRacha",
    # Temas
    "Tema",
    "TemaPredefinido",
    "TemaPersonalizado",
    # Tienda
    "TiendaItem",
    "InventarioUsuario",
    "TransaccionTienda",
    # Etiquetas
    "EtiquetaPerfil",
    "UsuarioEtiqueta",
]
