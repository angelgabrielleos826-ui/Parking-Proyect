"""
models.py
---------
Define las entidades del dominio, tal como se especificaron en el
diagrama UML de clases: Nivel y Mapas (que en realidad representa
un cajón dentro de un nivel).

Se usa Pydantic porque:
- Valida automáticamente los tipos de dato al crear un objeto.
- Se integra directo con FastAPI si el microservicio lo usa.
- Permite serializar/deserializar a JSON fácilmente (model_dump / model_validate).
"""

from __future__ import annotations
from pydantic import BaseModel, Field


class Nivel(BaseModel):
    """
    Representa un nivel del estacionamiento (ej. Planta Baja, Nivel 1, Nivel 2).

    Atributos:
        id_nivel: identificador único del nivel (ej. "N1").
        numero_nivel: número de nivel, útil para ordenar u mostrar (ej. 1, 2, 3).
    """
    id_nivel: str
    numero_nivel: int = Field(ge=0, description="Número de nivel, debe ser >= 0")

    def select_mapa(self, cajones: list["Mapas"]) -> list["Mapas"]:
        """
        Filtra y devuelve todos los cajones (Mapas) que pertenecen a este nivel.

        Nota de diseño: en el diagrama UML, selectMapa() no recibe parámetros
        porque ahí se asume que la clase tiene acceso directo a la base de datos.
        Aquí, como es una librería (sin estado de BD propio), recibe la lista
        de cajones ya cargada y filtra sobre ella. Quien quiera una versión
        "conectada a storage" puede usar MapaStorage.obtener_por_nivel() en su lugar.
        """
        return [cajon for cajon in cajones if cajon.id_nivel == self.id_nivel]


class Mapas(BaseModel):
    """
    Representa un cajón dentro de un mapa/nivel (nombre heredado del
    diagrama UML original; conceptualmente es un "Cajon").

    Atributos:
        id_nivel: FK hacia Nivel.id_nivel — a qué nivel pertenece este cajón.
        id_cajon: identificador único del cajón (ej. "C-014").
        column_cajon: posición en columna dentro de la cuadrícula del nivel.
        fila_cajon: posición en fila dentro de la cuadrícula del nivel.
    """
    id_nivel: str
    id_cajon: str
    column_cajon: int = Field(ge=0)
    fila_cajon: int = Field(ge=0)

    def ubicar_cajon(self) -> dict:
        """
        Devuelve la posición del cajón como un diccionario simple
        (fila, columna) — esto es lo que el front usaría para
        dibujar el resaltado sobre su propia representación del mapa.
        """
        return {"fila": self.fila_cajon, "columna": self.column_cajon}
