import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from localizador_api.main import crear_app

RUTA_FIXTURE = Path(__file__).parent / "fixtures" / "mapa_ejemplo.json"


@pytest.fixture
def client():
    return TestClient(crear_app(RUTA_FIXTURE))


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"estado": "ok"}


def test_obtener_cajon_existente(client):
    r = client.get("/cajones/C-002")
    assert r.status_code == 200
    body = r.json()
    assert body["id_cajon"] == "C-002"
    assert body["ubicacion"] == {"fila": 0, "columna": 1}


def test_obtener_cajon_ignora_mayusculas(client):
    assert client.get("/cajones/c-001").status_code == 200


def test_cajon_inexistente_devuelve_404(client):
    r = client.get("/cajones/C-999")
    assert r.status_code == 404
    assert "C-999" in r.json()["detalle"]


@pytest.mark.parametrize("valor", ["a b", "C_001", "x" * 30, "C-001;DROP", "%3Cscript%3E"])
def test_id_con_formato_invalido_devuelve_422(client, valor):
    assert client.get(f"/cajones/{valor}").status_code == 422


def test_listar_niveles(client):
    r = client.get("/niveles")
    assert r.status_code == 200
    assert {n["id_nivel"] for n in r.json()} == {"N1", "N2"}


def test_cajones_de_un_nivel(client):
    r = client.get("/niveles/N1/cajones")
    assert r.status_code == 200
    assert [c["id_cajon"] for c in r.json()] == ["C-001", "C-002"]


def test_nivel_inexistente_devuelve_404(client):
    assert client.get("/niveles/N9/cajones").status_code == 404


def test_cabeceras_de_seguridad(client):
    h = client.get("/health").headers
    assert h["x-content-type-options"] == "nosniff"
    assert h["x-frame-options"] == "DENY"
    assert "default-src 'none'" in h["content-security-policy"]


def test_docs_no_lleva_csp_estricta(client):
    r = client.get("/docs")
    assert r.status_code == 200
    assert "content-security-policy" not in r.headers


def test_mapa_invalido_lanza_error_al_arrancar(tmp_path):
    malo = tmp_path / "malo.json"
    malo.write_text(json.dumps({"niveles": []}))
    with pytest.raises(Exception):
        crear_app(malo)


def test_mapa_real_del_estacionamiento_carga(monkeypatch):
    monkeypatch.delenv("MAPA_PATH", raising=False)
    c = TestClient(crear_app())
    r = c.get("/cajones/C-08")
    assert r.status_code == 200
    assert len(c.get("/niveles/S1/cajones").json()) == 16 + 9 + 9 + 8 + 2 + 11
