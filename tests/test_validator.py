import pytest

from map_loader import validar_mapa, Nivel, Mapas
from map_loader import MapaInvalidoError, CajonDuplicadoError


def test_mapa_valido_no_lanza_error():
    niveles = [Nivel(id_nivel="N1", numero_nivel=1)]
    cajones = [Mapas(id_nivel="N1", id_cajon="C-001", fila_cajon=0, column_cajon=0)]
    validar_mapa(niveles, cajones)  # no debe lanzar nada


def test_cajon_con_nivel_inexistente():
    niveles = [Nivel(id_nivel="N1", numero_nivel=1)]
    cajones = [Mapas(id_nivel="N9", id_cajon="C-001", fila_cajon=0, column_cajon=0)]
    with pytest.raises(MapaInvalidoError):
        validar_mapa(niveles, cajones)


def test_id_cajon_duplicado():
    niveles = [Nivel(id_nivel="N1", numero_nivel=1)]
    cajones = [
        Mapas(id_nivel="N1", id_cajon="C-001", fila_cajon=0, column_cajon=0),
        Mapas(id_nivel="N1", id_cajon="C-001", fila_cajon=1, column_cajon=1),
    ]
    with pytest.raises(CajonDuplicadoError):
        validar_mapa(niveles, cajones)


def test_posicion_duplicada_en_mismo_nivel():
    niveles = [Nivel(id_nivel="N1", numero_nivel=1)]
    cajones = [
        Mapas(id_nivel="N1", id_cajon="C-001", fila_cajon=0, column_cajon=0),
        Mapas(id_nivel="N1", id_cajon="C-002", fila_cajon=0, column_cajon=0),
    ]
    with pytest.raises(CajonDuplicadoError):
        validar_mapa(niveles, cajones)
