"""
main.py
-------
Microservicio Localizador de Cajón (solo lectura).

Consulta la posición de un cajón dentro del mapa de un nivel. No maneja
usuarios ni ubicación en tiempo real: el mapa se carga al arrancar desde un
archivo JSON (variable de entorno MAPA_PATH) usando la librería map_loader.
"""

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, Path as PathParam, Request
from fastapi.responses import JSONResponse

from map_loader import (
    MapaStorage,
    MapLoaderError,
    CajonNoEncontradoError,
    NivelNoEncontradoError,
    cargar_mapa,
)

RUTA_MAPA_DEFAULT = Path(__file__).parent / "datos" / "mapa.json"
ID_PATRON = r"^[A-Za-z0-9-]{1,20}$"  # solo letras, números y guion

CABECERAS_SEGURIDAD = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}


def crear_app(ruta_mapa=None) -> FastAPI:
    ruta = Path(ruta_mapa or os.getenv("MAPA_PATH", RUTA_MAPA_DEFAULT))
    niveles, cajones = cargar_mapa(ruta)

    storage = MapaStorage(Path(tempfile.mkdtemp()) / "mapas_storage.json")
    storage.guardar(niveles, cajones)

    app = FastAPI(title="Localizador de Cajón", version="0.1.0")

    @app.middleware("http")
    async def agregar_cabeceras(request: Request, call_next):
        respuesta = await call_next(request)
        # /docs necesita cargar su propio JS/CSS, por eso no lleva CSP estricta
        for nombre, valor in CABECERAS_SEGURIDAD.items():
            if nombre == "Content-Security-Policy" and request.url.path.startswith(
                ("/docs", "/redoc")
            ):
                continue
            respuesta.headers[nombre] = valor
        return respuesta

    @app.exception_handler(MapLoaderError)
    async def manejar_error_mapa(request: Request, exc: MapLoaderError):
        codigo = 404 if isinstance(
            exc, (CajonNoEncontradoError, NivelNoEncontradoError)
        ) else 400
        return JSONResponse(status_code=codigo, content={"detalle": str(exc)})

    @app.get("/health")
    def health():
        return {"estado": "ok"}

    @app.get("/niveles")
    def listar_niveles():
        return [n.model_dump() for n in storage.listar_niveles()]

    @app.get("/niveles/{id_nivel}/cajones")
    def cajones_de_nivel(id_nivel: str = PathParam(pattern=ID_PATRON)):
        storage.obtener_nivel(id_nivel)  # 404 si no existe
        return [c.model_dump() for c in storage.obtener_por_nivel(id_nivel)]

    @app.get("/cajones/{id_cajon}")
    def obtener_cajon(id_cajon: str = PathParam(pattern=ID_PATRON)):
        cajon = storage.obtener_cajon(id_cajon.upper())
        return {**cajon.model_dump(), "ubicacion": cajon.ubicar_cajon()}

    return app


app = crear_app()
