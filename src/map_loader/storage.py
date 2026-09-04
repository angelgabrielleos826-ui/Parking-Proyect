"""
storage.py
----------
Se encarga de GUARDAR y RECUPERAR niveles/cajones. Está deliberadamente
desacoplado del resto de la librería: hoy guarda en un archivo JSON local,
pero si mañana el microservicio necesita guardar en una base de datos
(Postgres, S3, etc.), solo se reemplaza esta clase — el resto de la
librería (loader, validator, models) no se entera del cambio.
"""

from __future__ import annotations
import json
from pathlib import Path

from .models import Nivel, Mapas
from .exceptions import NivelNoEncontradoError, CajonNoEncontradoError


class MapaStorage:
    """
    Implementación simple de almacenamiento basada en un archivo JSON.

    En memoria mantiene dos diccionarios (para acceso O(1) por id) y
    los sincroniza a disco cada vez que se llama a guardar().
    """

    def __init__(self, ruta_almacenamiento: str | Path = "mapas_storage.json"):
        self.ruta = Path(ruta_almacenamiento)
        self._niveles: dict[str, Nivel] = {}
        self._cajones: dict[str, Mapas] = {}
        self._cargar_desde_disco_si_existe()

    # ---------- Escritura ----------

    def guardar(self, niveles: list[Nivel], cajones: list[Mapas]) -> None:
        """Guarda (o reemplaza) niveles y cajones, y persiste a disco."""
        for nivel in niveles:
            self._niveles[nivel.id_nivel] = nivel
        for cajon in cajones:
            self._cajones[cajon.id_cajon] = cajon
        self._guardar_a_disco()

    # ---------- Lectura ----------

    def obtener_nivel(self, id_nivel: str) -> Nivel:
        if id_nivel not in self._niveles:
            raise NivelNoEncontradoError(id_nivel)
        return self._niveles[id_nivel]

    def obtener_cajon(self, id_cajon: str) -> Mapas:
        if id_cajon not in self._cajones:
            raise CajonNoEncontradoError(id_cajon)
        return self._cajones[id_cajon]

    def obtener_por_nivel(self, id_nivel: str) -> list[Mapas]:
        """Devuelve todos los cajones que pertenecen a un nivel dado."""
        return [c for c in self._cajones.values() if c.id_nivel == id_nivel]

    def listar_niveles(self) -> list[Nivel]:
        return list(self._niveles.values())

    # ---------- Persistencia a disco (detalle interno) ----------

    def _guardar_a_disco(self) -> None:
        data = {
            "niveles": [n.model_dump() for n in self._niveles.values()],
            "cajones": [c.model_dump() for c in self._cajones.values()],
        }
        self.ruta.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _cargar_desde_disco_si_existe(self) -> None:
        if not self.ruta.exists():
            return
        data = json.loads(self.ruta.read_text(encoding="utf-8"))
        for n in data.get("niveles", []):
            nivel = Nivel(**n)
            self._niveles[nivel.id_nivel] = nivel
        for c in data.get("cajones", []):
            cajon = Mapas(**c)
            self._cajones[cajon.id_cajon] = cajon
