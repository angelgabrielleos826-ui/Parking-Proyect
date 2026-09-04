"""
validator.py
------------
Valida reglas de negocio que Pydantic, por sí solo, no puede checar
(porque dependen de comparar varios objetos entre sí, no solo un
objeto de forma aislada).

Reglas que valida:
1. Todo cajón (Mapas) debe referenciar un id_nivel que exista en la lista de niveles.
2. No puede haber dos cajones con el mismo id_cajon.
3. No puede haber dos cajones en la misma posición (fila, columna) dentro del mismo nivel.
"""

from __future__ import annotations
from .models import Nivel, Mapas
from .exceptions import MapaInvalidoError, CajonDuplicadoError


def validar_mapa(niveles: list[Nivel], cajones: list[Mapas]) -> None:
    """
    Valida la consistencia entre niveles y cajones.
    No devuelve nada si todo está bien; lanza una excepción si algo falla.
    """
    ids_nivel_validos = {nivel.id_nivel for nivel in niveles}

    ids_cajon_vistos: set[str] = set()
    posiciones_vistas: set[tuple[str, int, int]] = set()  # (id_nivel, fila, columna)

    for cajon in cajones:
        # Regla 1: el nivel referenciado debe existir
        if cajon.id_nivel not in ids_nivel_validos:
            raise MapaInvalidoError(
                f"El cajón '{cajon.id_cajon}' referencia un id_nivel "
                f"'{cajon.id_nivel}' que no existe en la lista de niveles."
            )

        # Regla 2: id_cajon no se repite
        if cajon.id_cajon in ids_cajon_vistos:
            raise CajonDuplicadoError(
                f"El id_cajon '{cajon.id_cajon}' está duplicado."
            )
        ids_cajon_vistos.add(cajon.id_cajon)

        # Regla 3: no hay dos cajones en la misma posición dentro del mismo nivel
        posicion = (cajon.id_nivel, cajon.fila_cajon, cajon.column_cajon)
        if posicion in posiciones_vistas:
            raise CajonDuplicadoError(
                f"Ya existe un cajón en fila={cajon.fila_cajon}, "
                f"columna={cajon.column_cajon} dentro del nivel '{cajon.id_nivel}'."
            )
        posiciones_vistas.add(posicion)
