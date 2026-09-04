"""
exceptions.py
-------------
Excepciones propias de la librería. Tener excepciones personalizadas
(en vez de usar Exception genérico) permite que el microservicio que
consuma la librería pueda capturarlas específicamente y responder,
por ejemplo, con el código HTTP correcto (404, 400, etc.).
"""


class MapLoaderError(Exception):
    """Excepción base de la librería. Todas las demás heredan de esta,
    así el microservicio puede capturar 'MapLoaderError' de forma genérica
    si no le interesa el detalle exacto."""


class MapaInvalidoError(MapLoaderError):
    """Se lanza cuando el archivo de mapa no cumple con el formato o
    reglas de negocio esperadas (ej. campos faltantes, tipos incorrectos)."""


class NivelNoEncontradoError(MapLoaderError):
    """Se lanza cuando se busca un id_nivel que no existe."""

    def __init__(self, id_nivel: str):
        self.id_nivel = id_nivel
        super().__init__(f"No se encontró el nivel con id_nivel='{id_nivel}'")


class CajonNoEncontradoError(MapLoaderError):
    """Se lanza cuando se busca un id_cajon que no existe."""

    def __init__(self, id_cajon: str):
        self.id_cajon = id_cajon
        super().__init__(f"No se encontró el cajón con id_cajon='{id_cajon}'")


class CajonDuplicadoError(MapLoaderError):
    """Se lanza cuando dos cajones ocupan la misma posición (fila, columna)
    dentro del mismo nivel, o cuando se repite un id_cajon."""
