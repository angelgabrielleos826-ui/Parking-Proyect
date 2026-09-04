# map_loader

Librería privada para el **cargado, validación y almacenamiento** de mapas
del microservicio *Localizador de Cajón*.

La librería **no dibuja ni resalta nada** — esa responsabilidad es del
front/cliente. Aquí solo se maneja la data: niveles y cajones (fila/columna).

## Instalación (modo desarrollo)

```bash
pip install -e ".[dev]"
```

## Uso básico

```python
from map_loader import cargar_mapa, MapaStorage

# 1. Cargar y validar un mapa desde archivo
niveles, cajones = cargar_mapa("mapa.json")

# 2. Guardarlo
storage = MapaStorage()
storage.guardar(niveles, cajones)

# 3. Consultar un cajón (esto usaría el endpoint de consulta)
cajon = storage.obtener_cajon("C-001")
print(cajon.ubicar_cajon())  # {"fila": 0, "columna": 0}

# 4. Consultar todos los cajones de un nivel
cajones_nivel = storage.obtener_por_nivel("N1")
```

## Formato del archivo de mapa (JSON)

```json
{
    "niveles": [
        {"id_nivel": "N1", "numero_nivel": 1}
    ],
    "cajones": [
        {"id_nivel": "N1", "id_cajon": "C-001", "fila_cajon": 0, "column_cajon": 0}
    ]
}
```

## Correr las pruebas

```bash
pytest
```

## Estructura

```
src/map_loader/
├── models.py       # Nivel y Mapas (entidades de datos, con Pydantic)
├── loader.py        # Lee y parsea el archivo de mapa
├── validator.py      # Valida reglas de negocio (niveles válidos, sin duplicados)
├── storage.py        # Guarda/recupera niveles y cajones (JSON en disco)
└── exceptions.py    # Excepciones propias de la librería
```
