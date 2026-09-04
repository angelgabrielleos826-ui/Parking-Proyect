import pytest

from map_loader import MapaStorage, Nivel, Mapas
from map_loader import NivelNoEncontradoError, CajonNoEncontradoError


@pytest.fixture
def storage(tmp_path):
    ruta = tmp_path / "test_storage.json"
    return MapaStorage(ruta_almacenamiento=ruta)


def test_guardar_y_obtener_cajon(storage):
    niveles = [Nivel(id_nivel="N1", numero_nivel=1)]
    cajones = [Mapas(id_nivel="N1", id_cajon="C-001", fila_cajon=0, column_cajon=0)]
    storage.guardar(niveles, cajones)

    cajon = storage.obtener_cajon("C-001")
    assert cajon.id_cajon == "C-001"
    assert cajon.ubicar_cajon() == {"fila": 0, "columna": 0}


def test_obtener_cajon_inexistente_lanza_error(storage):
    with pytest.raises(CajonNoEncontradoError):
        storage.obtener_cajon("NO-EXISTE")


def test_obtener_nivel_inexistente_lanza_error(storage):
    with pytest.raises(NivelNoEncontradoError):
        storage.obtener_nivel("NO-EXISTE")


def test_obtener_por_nivel(storage):
    niveles = [Nivel(id_nivel="N1", numero_nivel=1)]
    cajones = [
        Mapas(id_nivel="N1", id_cajon="C-001", fila_cajon=0, column_cajon=0),
        Mapas(id_nivel="N1", id_cajon="C-002", fila_cajon=0, column_cajon=1),
    ]
    storage.guardar(niveles, cajones)
    resultado = storage.obtener_por_nivel("N1")
    assert len(resultado) == 2


def test_persistencia_a_disco(tmp_path):
    ruta = tmp_path / "persistencia.json"
    storage1 = MapaStorage(ruta_almacenamiento=ruta)
    storage1.guardar(
        [Nivel(id_nivel="N1", numero_nivel=1)],
        [Mapas(id_nivel="N1", id_cajon="C-001", fila_cajon=0, column_cajon=0)],
    )

    # Nueva instancia, misma ruta: debe cargar lo ya guardado
    storage2 = MapaStorage(ruta_almacenamiento=ruta)
    cajon = storage2.obtener_cajon("C-001")
    assert cajon.id_cajon == "C-001"
