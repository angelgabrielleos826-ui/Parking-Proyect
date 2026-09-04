"""
map_loader
----------
Librería privada para el cargado, validación y almacenamiento de mapas
del microservicio Localizador de Cajón.

Uso típico:

    from map_loader import cargar_mapa, validar_mapa, MapaStorage

    niveles, cajones = cargar_mapa("mapa.json")
    storage = MapaStorage()
    storage.guardar(niveles, cajones)

    cajon = storage.obtener_cajon("C-001")
    print(cajon.ubicar_cajon())  # {"fila": 0, "columna": 0}

Todo lo que se importa aquí es la "API pública" de la librería —
lo que el microservicio debería usar. El resto (funciones auxiliares
internas como _leer_contenido) se queda como detalle de implementación.
"""

from .models import Nivel, Mapas
from .loader import cargar_mapa
from .validator import validar_mapa
from .storage import MapaStorage
from .exceptions import (
    MapLoaderError,
    MapaInvalidoError,
    NivelNoEncontradoError,
    CajonNoEncontradoError,
    CajonDuplicadoError,
)

__all__ = [
    "Nivel",
    "Mapas",
    "cargar_mapa",
    "validar_mapa",
    "MapaStorage",
    "MapLoaderError",
    "MapaInvalidoError",
    "NivelNoEncontradoError",
    "CajonNoEncontradoError",
    "CajonDuplicadoError",
]

__version__ = "0.1.0"
