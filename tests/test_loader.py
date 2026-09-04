from pathlib import Path
import pytest

from map_loader import cargar_mapa, MapaInvalidoError

FIXTURE = Path(__file__).parent / "fixtures" / "mapa_ejemplo.json"


def test_cargar_mapa_valido():
    niveles, cajones = cargar_mapa(FIXTURE)
    assert len(niveles) == 2
    assert len(cajones) == 3
    assert niveles[0].id_nivel == "N1"
    assert cajones[0].id_cajon == "C-001"


def test_cargar_mapa_json_invalido():
    with pytest.raises(MapaInvalidoError):
        cargar_mapa("esto no es json {{{")


def test_cargar_mapa_sin_llaves_requeridas():
    with pytest.raises(MapaInvalidoError):
        cargar_mapa('{"algo": []}')


def test_cargar_mapa_formato_no_soportado():
    with pytest.raises(MapaInvalidoError):
        cargar_mapa(FIXTURE, formato="geojson")
