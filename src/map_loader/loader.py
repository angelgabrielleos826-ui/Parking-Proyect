"""
loader.py
---------
Se encarga de LEER y PARSEAR el archivo de mapa (por ahora solo JSON)
y convertirlo en objetos Nivel y Mapas. Esta es la función que, a
futuro, usaría el endpoint donde el "personal operativo" carga el mapa.

Formato de archivo esperado (JSON):
{
    "niveles": [
        {"id_nivel": "N1", "numero_nivel": 1}
    ],
    "cajones": [
        {"id_nivel": "N1", "id_cajon": "C-001", "fila_cajon": 0, "column_cajon": 0}
    ]
}
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Union

from pydantic import ValidationError

from .models import Nivel, Mapas
from .validator import validar_mapa
from .exceptions import MapaInvalidoError


def cargar_mapa(
    archivo: Union[str, Path, bytes],
    formato: str = "json",
) -> tuple[list[Nivel], list[Mapas]]:
    """
    Carga un mapa desde un archivo (ruta) o desde bytes ya leídos.

    Args:
        archivo: ruta al archivo (str/Path) o el contenido ya en bytes/str.
        formato: por ahora solo se soporta "json". Se deja el parámetro
                 para poder agregar "geojson" u otros formatos después
                 sin romper la firma de la función.

    Returns:
        Una tupla (niveles, cajones) ya validada y lista para usarse
        o guardarse con MapaStorage.

    Raises:
        MapaInvalidoError: si el archivo no es JSON válido, le faltan
                            campos, o no pasa las reglas de negocio.
    """
    if formato != "json":
        raise MapaInvalidoError(f"Formato '{formato}' no soportado todavía.")

    contenido = _leer_contenido(archivo)

    try:
        data = json.loads(contenido)
    except json.JSONDecodeError as e:
        raise MapaInvalidoError(f"El archivo no es un JSON válido: {e}") from e

    if "niveles" not in data or "cajones" not in data:
        raise MapaInvalidoError(
            "El JSON debe tener las llaves 'niveles' y 'cajones'."
        )

    try:
        niveles = [Nivel(**n) for n in data["niveles"]]
        cajones = [Mapas(**c) for c in data["cajones"]]
    except ValidationError as e:
        # Pydantic ya valida tipos/campos faltantes; solo la "traducimos"
        # a nuestra excepción propia para que el resto de la librería
        # sea consistente (todo error de mapa = MapaInvalidoError).
        raise MapaInvalidoError(f"Datos de mapa inválidos: {e}") from e

    # Aquí se validan las reglas de negocio (niveles existentes, sin duplicados, etc.)
    validar_mapa(niveles, cajones)

    return niveles, cajones


def _leer_contenido(archivo: Union[str, Path, bytes]) -> str:
    """Función auxiliar: normaliza la entrada (ruta, Path o bytes) a un string."""
    if isinstance(archivo, bytes):
        return archivo.decode("utf-8")
    if isinstance(archivo, (str, Path)) and Path(archivo).exists():
        return Path(archivo).read_text(encoding="utf-8")
    if isinstance(archivo, str):
        # Puede que ya sea el contenido JSON como string (no una ruta)
        return archivo
    raise MapaInvalidoError("Tipo de 'archivo' no soportado para cargar_mapa().")
