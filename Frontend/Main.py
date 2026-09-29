import json
import math
import os
import re
import ssl
import threading
import urllib.request

from kivy.app import App
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import (Color, RoundedRectangle, Rectangle, Line, Ellipse,
                           InstructionGroup)
from kivy.clock import Clock
from kivy.properties import (ListProperty, StringProperty, BooleanProperty,
                             NumericProperty)
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.storage.jsonstore import JsonStore

# ----------------------------------------------------------------------
# Paleta de colores
# ----------------------------------------------------------------------
COLOR_BG = (0.043, 0.055, 0.098, 1)          # fondo azul-negro
COLOR_CANVAS = (0.063, 0.075, 0.110, 1)      # fondo del mapa
COLOR_CARD = (0.098, 0.114, 0.161, 1)        # tarjetas / cajones
COLOR_CARD_LIGHT = (0.145, 0.165, 0.220, 1)  # bordes / inputs
COLOR_BORDER = (0.220, 0.240, 0.290, 1)      # bordes sutiles
COLOR_GOLD = (0.949, 0.729, 0.078, 1)        # acentos
COLOR_GOLD_DARK = (0.20, 0.17, 0.06, 1)      # fondo dorado tenue
COLOR_TEXT = (0.937, 0.941, 0.949, 1)        # texto principal
COLOR_TEXT_MUTED = (0.560, 0.588, 0.650, 1)  # texto secundario
COLOR_RED = (0.898, 0.263, 0.263, 1)         # borrar / alerta
COLOR_GREEN = (0.298, 0.808, 0.400, 1)       # exito

Window.clearcolor = COLOR_BG
if platform in ("win", "linux", "macosx"):
    Window.size = (390, 800)  # tamano de celular para probar en escritorio


# ----------------------------------------------------------------------
# DATOS DEL ESTACIONAMIENTO (plano del "Mapa cargado")
# El plano se define en horizontal (640 x 400) y se dibuja girado 90°.
# Cada cajon: (x, y, ancho, alto) en unidades del plano horizontal.
# ----------------------------------------------------------------------
FILAS = {"A": 16, "B": 9, "C": 9, "D": 8, "E": 2, "F": 11}


def _build_spots():
    s = {}
    for i in range(16):                                   # Fila A: lateral derecho
        s[f"A-{i + 1:02d}"] = (32 + 36 * i, 8, 30, 46)
    for i in range(9):                                    # Fila B (arriba) / C (abajo)
        s[f"B-{i + 1:02d}"] = (8, 70 + 33 * i, 48, 29)
        s[f"C-{i + 1:02d}"] = (584, 70 + 33 * i, 48, 29)
    for i in range(4):                                    # Fila D: centro
        s[f"D-{i + 1:02d}"] = (130, 110 + 33 * i, 48, 29)
        s[f"D-{i + 5:02d}"] = (274, 110 + 33 * i, 48, 29)
    s["E-01"] = (196, 110, 30, 46)                        # Fila E
    s["E-02"] = (234, 110, 30, 46)
    for i in range(5):                                    # Fila F
        s[f"F-{i + 1:02d}"] = (372, 110 + 33 * i, 48, 29)
    for i in range(6):
        s[f"F-{i + 6:02d}"] = (452, 110 + 33 * i, 48, 29)
    return s


SPOTS = _build_spots()

# ----------------------------------------------------------------------
# CONEXION CON EL MICROSERVICIO (API Localizador de Cajon)
# La app descarga el mapa del nivel desde la API, lo guarda en el celular
# y despues funciona sin senal. Si no hay internet usa el ultimo mapa
# guardado o, en su defecto, el mapa integrado en el codigo.
# ----------------------------------------------------------------------
API_URL = os.environ.get("ALZ_API_URL", "https://parking-proyect.onrender.com").rstrip("/")
NIVEL_ID = "S1"
API_TIMEOUT = 45           # segundos (el plan gratis de Render tarda en "despertar")
TAMANOS = {"A": (30, 46), "E": (30, 46)}   # (ancho, alto); las demas filas: (48, 29)
BUILTIN_SPOTS = dict(SPOTS)                # mapa integrado (respaldo)
_ID_RE = re.compile(r"^[A-Z]-\d{2}$")


def spots_from_api(cajones):
    """Convierte la lista de cajones de la API en {id: (x, y, ancho, alto)}."""
    if not isinstance(cajones, list) or not cajones:
        raise ValueError("El servidor no devolvio cajones")
    spots = {}
    for c in cajones:
        try:
            sid = str(c["id_cajon"]).upper()
            x, y = int(c["column_cajon"]), int(c["fila_cajon"])
        except (KeyError, TypeError, ValueError):
            raise ValueError("Cajon con formato invalido")
        if not _ID_RE.match(sid):
            raise ValueError(f"Id de cajon invalido: {sid}")
        w, h = TAMANOS.get(sid[0], (48, 29))
        spots[sid] = (x, y, w, h)
    return spots


def apply_spots(spots):
    """Reemplaza el mapa en uso y recalcula cuantos cajones tiene cada fila."""
    SPOTS.clear()
    SPOTS.update(spots)
    for letter in FILAS:
        total = sum(1 for sid in spots if sid[0] == letter)
        if total:
            FILAS[letter] = total


def _ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return None

# Referencias: (texto, x, y, es_acceso) -> centro en el plano horizontal
REFS = [
    ("Escalera B", 100, 365, False),
    ("Caseta\nde pago", 226, 365, True),
    ("Salida\npeatonal", 354, 365, False),
    ("Escalera A", 479, 365, False),
    ("Elevador 2", 546, 330, False),
    ("Entrada\nPlaza Norte", 546, 215, True),
]

SRC_H = 400.0                    # alto del plano horizontal
PLAN_W, PLAN_H = 400.0, 640.0    # tamano del plano ya girado (vertical)


def near_refs(spot, n=2):
    """Las n referencias (no accesos) mas cercanas a un cajon: 'Cerca de: ...'."""
    sx, sy, sw, sh = SPOTS[spot]
    cx, cy = sx + sw / 2, sy + sh / 2
    cands = [r for r in REFS if not r[3]]
    ranked = sorted(cands, key=lambda r: (r[1] - cx) ** 2 + (r[2] - cy) ** 2)
    return ", ".join(r[0].replace("\n", " ") for r in ranked[:n])


# ----------------------------------------------------------------------
# Widgets reutilizables
# ----------------------------------------------------------------------
class RoundedBox(BoxLayout):
    """BoxLayout con fondo redondeado y borde opcional."""
    bg_color = ListProperty(COLOR_CARD)
    radius = ListProperty([dp(14)])
    border_color = ListProperty([0, 0, 0, 0])
    border_width = NumericProperty(dp(1.5))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color = Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            self._bcolor = Color(*self.border_color)
            self._bline = Line(width=self.border_width)
        self.bind(
            pos=self._update, size=self._update, radius=self._update,
            bg_color=lambda i, v: setattr(self._color, "rgba", v),
            border_color=lambda i, v: setattr(self._bcolor, "rgba", v),
            border_width=lambda i, v: setattr(self._bline, "width", v),
        )
        self._update()

    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = self.radius
        self._bline.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius[0])


class RoundedButton(ButtonBehavior, BoxLayout):
    """Boton con fondo redondeado."""
    text = StringProperty("")
    bg_color = ListProperty(COLOR_GOLD)
    text_color = ListProperty((0.043, 0.055, 0.098, 1))
    font_size = StringProperty("16sp")
    bold = BooleanProperty(True)
    radius = ListProperty([dp(14)])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color = Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
        self.bind(pos=self._update, size=self._update,
                  bg_color=lambda i, v: setattr(self._color, "rgba", v))
        self._label = Label(text=self.text, color=self.text_color,
                            font_size=self.font_size, bold=self.bold)
        self.add_widget(self._label)
        self.bind(text=lambda i, v: setattr(self._label, "text", v),
                  text_color=lambda i, v: setattr(self._label, "color", v))

    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = self.radius

    def on_press(self):
        Animation.cancel_all(self)
        Animation(opacity=0.75, duration=0.08).start(self)

    def on_release(self):
        Animation(opacity=1, duration=0.12).start(self)


class FilaChip(ButtonBehavior, RoundedBox):
    """Boton de fila (A, B, C...). Se ilumina en dorado cuando esta activo."""

    def __init__(self, letter, **kwargs):
        super().__init__(radius=[dp(10)], bg_color=COLOR_BG, border_color=COLOR_BORDER,
                         border_width=dp(1), **kwargs)
        self.letter = letter
        self.lbl = Label(text=letter, font_size="18sp", bold=True, color=COLOR_TEXT)
        self.add_widget(self.lbl)

    def set_active(self, on):
        self.bg_color = COLOR_GOLD_DARK if on else COLOR_BG
        self.border_color = COLOR_GOLD if on else COLOR_BORDER
        self.border_width = dp(2) if on else dp(1)
        self.lbl.color = COLOR_GOLD if on else COLOR_TEXT


class BaseScreen(Screen):
    """Screen con fondo solido."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*COLOR_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size


def mk_label(text, size="12sp", color=COLOR_TEXT, bold=False, halign="left", height=None, **kw):
    lbl = Label(text=text, font_size=size, color=color, bold=bold,
                halign=halign, valign="middle", **kw)
    if height:
        lbl.size_hint_y = None
        lbl.height = height
    lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
    return lbl


# ----------------------------------------------------------------------
# Iconos vectoriales
# ----------------------------------------------------------------------
class VectorIcon(Widget):
    color_rgba = ListProperty(COLOR_GOLD)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color = Color(*self.color_rgba)
            self.setup()
        self.bind(pos=self._redraw, size=self._redraw,
                  color_rgba=lambda i, v: setattr(self._color, "rgba", v))
        self._redraw()

    def setup(self):
        pass

    def _redraw(self, *args):
        pass


class PhoneStatusIcons(VectorIcon):
    color_rgba = ListProperty(COLOR_TEXT)

    def setup(self):
        self._signal = [Rectangle() for _ in range(4)]
        self._wifi = [Line(width=dp(1.4)) for _ in range(3)]
        self._bat = Line(width=dp(1.3))
        self._bat_fill = Rectangle()
        self._bat_tip = Rectangle()

    def _redraw(self, *args):
        x, y = self.pos
        h = self.height
        sx = x
        for i, rect in enumerate(self._signal):
            rect.pos = (sx, y + (h - dp(11)) / 2)
            rect.size = (dp(3), dp(5) + dp(2.3) * i)
            sx += dp(5)
        cx, cy = x + dp(34), y + h / 2 - dp(2)
        for line, r in zip(self._wifi, [dp(3), dp(6), dp(9)]):
            line.circle = (cx, cy, r, -55, 55)          # arco hacia arriba
        bw, bh = dp(20), dp(10)
        bx, by = x + dp(50), y + (h - bh) / 2
        self._bat.rounded_rectangle = (bx, by, bw, bh, dp(2))
        self._bat_fill.pos = (bx + dp(2), by + dp(2))
        self._bat_fill.size = (bw - dp(6), bh - dp(4))
        self._bat_tip.pos = (bx + bw, by + bh / 2 - dp(2))
        self._bat_tip.size = (dp(2), dp(4))


class CheckIcon(VectorIcon):
    color_rgba = ListProperty(COLOR_GREEN)

    def setup(self):
        self._line = Line(width=dp(1.8), cap="round", joint="round")

    def _redraw(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        self._line.points = [x + w * 0.12, y + h * 0.52, x + w * 0.40, y + h * 0.18,
                             x + w * 0.90, y + h * 0.82]


class DotIcon(VectorIcon):
    def setup(self):
        self._ellipse = Ellipse()

    def _redraw(self, *args):
        d = min(self.width, self.height) * 0.5
        self._ellipse.pos = (self.center_x - d / 2, self.center_y - d / 2)
        self._ellipse.size = (d, d)


class CarIcon(VectorIcon):
    def setup(self):
        self._body = Line(width=dp(1.6), joint="round", cap="round")
        self._w1 = Line(width=dp(1.4))
        self._w2 = Line(width=dp(1.4))

    def _redraw(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        self._body.points = [
            x + w * 0.05, y + h * 0.40, x + w * 0.20, y + h * 0.62,
            x + w * 0.35, y + h * 0.62, x + w * 0.42, y + h * 0.78,
            x + w * 0.62, y + h * 0.78, x + w * 0.70, y + h * 0.62,
            x + w * 0.85, y + h * 0.62, x + w * 0.95, y + h * 0.40,
            x + w * 0.90, y + h * 0.28, x + w * 0.10, y + h * 0.28,
            x + w * 0.05, y + h * 0.40,
        ]
        r = w * 0.09
        self._w1.circle = (x + w * 0.28, y + h * 0.28, r)
        self._w2.circle = (x + w * 0.72, y + h * 0.28, r)


class PencilIcon(VectorIcon):
    def setup(self):
        self._body = Line(width=dp(1.6), joint="round", cap="round", close=True)
        self._tip = Line(width=dp(1.2))

    def _redraw(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        self._body.points = [x + w * 0.15, y + h * 0.15, x + w * 0.30, y + h * 0.10,
                             x + w * 0.90, y + h * 0.70, x + w * 0.80, y + h * 0.90,
                             x + w * 0.20, y + h * 0.30]
        self._tip.points = [x + w * 0.15, y + h * 0.15, x + w * 0.20, y + h * 0.30]


class PinIcon(VectorIcon):
    show_check = BooleanProperty(False)

    def setup(self):
        self._outline = Line(width=dp(1.6), joint="round", cap="round")
        self._check = Line(width=dp(1.6), cap="round", joint="round")
        self.bind(show_check=self._redraw)

    def _redraw(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        cx, top_cy, r = x + w * 0.5, y + h * 0.62, w * 0.30
        pts = []
        for deg in range(-40, 221, 10):
            rad = math.radians(deg)
            pts += [cx + r * math.cos(rad), top_cy + r * math.sin(rad)]
        pts += [cx, y + h * 0.06]
        self._outline.points = pts
        self._check.points = ([cx - r * 0.5, top_cy, cx - r * 0.1, top_cy - r * 0.4,
                               cx + r * 0.55, top_cy + r * 0.45] if self.show_check else [])


class NoEntryIcon(VectorIcon):
    color_rgba = ListProperty(COLOR_RED)

    def setup(self):
        self._circle = Line(width=dp(1.6))
        self._slash = Line(width=dp(1.6), cap="round")

    def _redraw(self, *args):
        cx, cy = self.center_x, self.center_y
        r = min(self.width, self.height) * 0.42
        self._circle.circle = (cx, cy, r)
        a = math.radians(45)
        self._slash.points = [cx - r * math.cos(a), cy - r * math.sin(a),
                              cx + r * math.cos(a), cy + r * math.sin(a)]


class CompassIcon(VectorIcon):
    def setup(self):
        self._circle = Line(width=dp(1.5))
        self._needle = Line(width=dp(1.3), close=True, joint="round")

    def _redraw(self, *args):
        cx, cy = self.center_x, self.center_y
        r = min(self.width, self.height) * 0.42
        self._circle.circle = (cx, cy, r)
        self._needle.points = [cx, cy + r * 0.6, cx + r * 0.28, cy,
                               cx, cy - r * 0.6, cx - r * 0.28, cy]


class WarningTriangleIcon(VectorIcon):
    color_rgba = ListProperty(COLOR_RED)

    def setup(self):
        self._tri = Line(width=dp(1.8), joint="round", cap="round", close=True)
        self._bar = Line(width=dp(2), cap="round")
        self._dot = Ellipse()

    def _redraw(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        self._tri.points = [x + w * 0.5, y + h * 0.90, x + w * 0.06, y + h * 0.12,
                            x + w * 0.94, y + h * 0.12]
        self._bar.points = [x + w * 0.5, y + h * 0.60, x + w * 0.5, y + h * 0.38]
        d = w * 0.07
        self._dot.pos = (x + w * 0.5 - d / 2, y + h * 0.28 - d / 2)
        self._dot.size = (d, d)


class GoldProgressBar(Widget):
    def __init__(self, value=0, maximum=100, **kwargs):
        super().__init__(**kwargs)
        self._val = value
        self._maximum = maximum
        with self.canvas:
            Color(*COLOR_CARD_LIGHT)
            self._track = RoundedRectangle(radius=[dp(3)])
            Color(*COLOR_GOLD)
            self._fill = RoundedRectangle(radius=[dp(3)])
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def set_value(self, v):
        self._val = max(0, min(self._maximum, v))
        self._redraw()

    def _redraw(self, *args):
        self._track.pos = self.pos
        self._track.size = self.size
        ratio = self._val / self._maximum
        self._fill.pos = self.pos
        self._fill.size = (max(self.width * ratio, dp(2) if ratio > 0 else 0), self.height)


# ----------------------------------------------------------------------
# MAPA DEL ESTACIONAMIENTO (plano girado, con cajon iluminado)
# ----------------------------------------------------------------------
class ParkingMap(StencilView):
    """Dibuja el plano completo. Asigna selected = "C-08" para iluminar un cajon.
    crop=True muestra solo la parte superior (usado como fondo atenuado)."""
    selected = StringProperty("")
    pulse = NumericProperty(0.0)
    crop = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._static = InstructionGroup()
        self._dyn = InstructionGroup()
        self.canvas.add(self._static)
        self.canvas.add(self._dyn)
        self._tex_cache = {}
        self._anim = None
        self.bind(pos=self._draw_static, size=self._draw_static, crop=self._draw_static)
        self.bind(pos=self._draw_dyn, size=self._draw_dyn, pulse=self._draw_dyn)
        self.bind(selected=lambda *a: self.restart())

    # ---------- geometria: plano horizontal -> pantalla (girado 90°) ----------
    def _mappers(self):
        pad = dp(8)
        aw, ah = self.width - 2 * pad, self.height - 2 * pad
        s = aw / PLAN_W if self.crop else min(aw / PLAN_W, ah / PLAN_H)
        ox = self.x + pad + (aw - PLAN_W * s) / 2
        top = self.top - pad - (0 if self.crop else (ah - PLAN_H * s) / 2)

        def R(x, y, w, h):
            return (ox + (SRC_H - y - h) * s, top - (x + w) * s, h * s, w * s)

        def C(cx, cy):
            return (ox + (SRC_H - cy) * s, top - cx * s)

        return s, R, C

    # ---------- texto ----------
    def _tex(self, text, size, bold=True):
        key = (text, round(size, 1), bold)
        t = self._tex_cache.get(key)
        if t is None:
            lbl = CoreLabel(text=text, font_size=max(size, 1), bold=bold, halign="center")
            lbl.refresh()
            t = self._tex_cache[key] = lbl.texture
        return t

    def _text(self, g, text, cx, cy, size, color, bold=True):
        t = self._tex(text, size, bold)
        g.add(Color(*color))
        g.add(Rectangle(texture=t, pos=(cx - t.width / 2, cy - t.height / 2), size=t.size))

    # ---------- capa estatica ----------
    def _draw_static(self, *args):
        g = self._static
        g.clear()
        if self.width < 10 or self.height < 10:
            return
        s, R, C = self._mappers()
        k = s / 0.8
        r = dp(16)
        g.add(Color(*COLOR_CANVAS))
        g.add(RoundedRectangle(pos=self.pos, size=self.size, radius=[r]))
        g.add(Color(*COLOR_CARD_LIGHT))
        g.add(Line(rounded_rectangle=(self.x, self.y, self.width, self.height, r), width=1))

        x, y, w, h = R(0, 0, 640, 400)                      # muro perimetral
        g.add(Line(rounded_rectangle=(x, y, w, h, dp(10)), width=dp(1.5)))

        for sid, (sx, sy, sw, sh) in SPOTS.items():         # cajones
            x, y, w, h = R(sx, sy, sw, sh)
            g.add(Color(*COLOR_CARD))
            g.add(RoundedRectangle(pos=(x, y), size=(w, h), radius=[dp(4)]))
            g.add(Color(*COLOR_CARD_LIGHT))
            g.add(Line(rounded_rectangle=(x, y, w, h, dp(4)), width=1))
            self._text(g, sid, x + w / 2, y + h / 2, 9 * k, COLOR_TEXT_MUTED)

        x, y, w, h = R(190, 166, 72, 64)                    # nucleo escaleras/elevadores
        g.add(Color(*COLOR_CARD))
        g.add(RoundedRectangle(pos=(x, y), size=(w, h), radius=[dp(6)]))
        g.add(Color(*COLOR_CARD_LIGHT))
        g.add(Line(rounded_rectangle=(x, y, w, h, dp(6)), width=1))
        self._text(g, "Esc./Elev.", x + w / 2, y + h / 2, 8 * k, COLOR_TEXT)

        x, y, w, h = R(130, 250, 192, 62)                   # rampa de acceso vehicular
        cx, cy = x + w / 2, y + h / 2
        g.add(Color(*COLOR_CARD))
        g.add(RoundedRectangle(pos=(x, y), size=(w, h), radius=[dp(8)]))
        g.add(Color(*COLOR_CARD_LIGHT))
        g.add(Line(rounded_rectangle=(x, y, w, h, dp(8)), width=1))
        self._text(g, "Rampa de\nacceso\nvehicular", cx, cy + 14 * s, 9 * k, COLOR_TEXT_MUTED)
        a = 5 * s
        g.add(Color(*COLOR_GOLD))
        g.add(Line(points=[cx, cy - 22 * s, cx, cy - 52 * s], width=dp(1.6), cap="round"))
        g.add(Line(points=[cx - a, cy - 44 * s, cx, cy - 52 * s, cx + a, cy - 44 * s],
                   width=dp(1.6), cap="round", joint="round"))

        for name, rx, ry, gold in REFS:                     # referencias
            cx, cy = C(rx, ry)
            t = self._tex(name, 8 * k)
            cw, ch = t.width + dp(12), t.height + dp(8)
            g.add(Color(*COLOR_CARD))
            g.add(RoundedRectangle(pos=(cx - cw / 2, cy - ch / 2), size=(cw, ch), radius=[dp(6)]))
            g.add(Color(*COLOR_CARD_LIGHT))
            g.add(Line(rounded_rectangle=(cx - cw / 2, cy - ch / 2, cw, ch, dp(6)), width=1))
            self._text(g, name, cx, cy, 8 * k, COLOR_GOLD if gold else COLOR_TEXT)

    # ---------- capa dinamica: cajon iluminado ----------
    def _draw_dyn(self, *args):
        g = self._dyn
        g.clear()
        sp = SPOTS.get(self.selected)
        if not sp or self.width < 10 or self.height < 10:
            return
        s, R, C = self._mappers()
        k = s / 0.8
        x, y, w, h = R(*sp)
        p = self.pulse
        gl = dp(2) + dp(5) * p
        g.add(Color(*COLOR_GOLD[:3], 0.10 + 0.22 * p))       # resplandor pulsante
        g.add(RoundedRectangle(pos=(x - gl, y - gl), size=(w + 2 * gl, h + 2 * gl),
                               radius=[dp(4) + gl]))
        g.add(Color(*COLOR_CARD))                            # tapa la etiqueta gris
        g.add(RoundedRectangle(pos=(x, y), size=(w, h), radius=[dp(4)]))
        g.add(Color(*COLOR_GOLD[:3], 0.20))
        g.add(RoundedRectangle(pos=(x, y), size=(w, h), radius=[dp(4)]))
        g.add(Color(*COLOR_GOLD))
        g.add(Line(rounded_rectangle=(x, y, w, h, dp(4)), width=dp(2)))
        self._text(g, self.selected, x + w / 2, y + h / 2 + dp(3), 9 * k, COLOR_GOLD)
        d = dp(4) + dp(2) * p
        g.add(Color(*COLOR_GOLD))
        g.add(Ellipse(pos=(x + w / 2 - d / 2, y + dp(4)), size=(d, d)))

    # ---------- animacion de pulso ----------
    def halt(self):
        if self._anim:
            self._anim.cancel(self)
            self._anim = None

    def restart(self):
        self.halt()
        self.pulse = 0.0
        self._draw_dyn()
        if self.selected in SPOTS:
            a = (Animation(pulse=1.0, d=0.9, t="in_out_sine")
                 + Animation(pulse=0.0, d=0.9, t="in_out_sine"))
            a.repeat = True
            a.start(self)
            self._anim = a


# ----------------------------------------------------------------------
# Piezas de layout compartidas
# ----------------------------------------------------------------------
def status_bar():
    bar = BoxLayout(size_hint=(1, None), height=dp(28), padding=(dp(16), 0))
    bar.add_widget(Label(text="9:41", color=COLOR_TEXT, font_size="13sp", bold=True,
                         size_hint=(None, 1), width=dp(60), halign="left"))
    bar.add_widget(Label(text=""))
    bar.add_widget(PhoneStatusIcons(size_hint=(None, 1), width=dp(74)))
    return bar


def screen_title(text, subtitle=None):
    box = BoxLayout(orientation="vertical", size_hint=(1, None),
                    height=dp(60) if subtitle else dp(36), padding=(dp(20), 0))
    box.add_widget(mk_label(text, "22sp", COLOR_TEXT, True, height=dp(30)))
    if subtitle:
        box.add_widget(mk_label(subtitle, "13sp", COLOR_TEXT_MUTED, height=dp(20)))
    return box


def nav_header(title, sub):
    """Encabezado 'Nivel -1' + subtitulo (texto o widget) + boton brujula."""
    box = BoxLayout(size_hint=(1, None), height=dp(52))
    left = BoxLayout(orientation="vertical")
    left.add_widget(mk_label(title, "20sp", COLOR_TEXT, True, height=dp(28)))
    if isinstance(sub, str):
        sub = mk_label(sub, "11sp", COLOR_TEXT_MUTED, height=dp(18))
    left.add_widget(sub)
    box.add_widget(left)
    wrap = AnchorLayout(anchor_x="right", anchor_y="center", size_hint=(None, 1), width=dp(44))
    bg = RoundedBox(bg_color=COLOR_CARD, border_color=COLOR_BORDER, border_width=dp(1),
                    radius=[dp(20)], size_hint=(None, None), size=(dp(40), dp(40)))
    inner = AnchorLayout(anchor_x="center", anchor_y="center")
    inner.add_widget(CompassIcon(size_hint=(None, None), size=(dp(20), dp(20))))
    bg.add_widget(inner)
    wrap.add_widget(bg)
    box.add_widget(wrap)
    return box


def bottom_dock(height, spacing=dp(6)):
    return RoundedBox(orientation="vertical", bg_color=COLOR_CARD, border_color=COLOR_BORDER,
                      border_width=dp(1), radius=[dp(18), dp(18), 0, 0],
                      padding=dp(20), spacing=spacing, size_hint=(1, None), height=height)


# ----------------------------------------------------------------------
# 1. SPLASH / BIENVENIDA
# ----------------------------------------------------------------------
class SplashScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        root.add_widget(status_bar())

        body = BoxLayout(orientation="vertical", padding=(dp(30), dp(20)), spacing=dp(16))
        body.add_widget(BoxLayout(size_hint=(1, 0.35)))

        icon_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, None), height=dp(80))
        icon = RoundedBox(bg_color=(0, 0, 0, 0), border_color=COLOR_GOLD, border_width=dp(2),
                          radius=[dp(18)], size_hint=(None, None), size=(dp(64), dp(64)))
        icon.add_widget(Label(text="P", color=COLOR_GOLD, font_size="26sp", bold=True))
        icon_wrap.add_widget(icon)
        body.add_widget(icon_wrap)

        body.add_widget(Label(text="AlzParking", color=COLOR_TEXT, font_size="26sp", bold=True,
                              size_hint=(1, None), height=dp(46)))

        badge_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, None), height=dp(24))
        badge = RoundedBox(bg_color=COLOR_CARD, radius=[dp(12)], spacing=dp(6), padding=(dp(10), 0),
                           size_hint=(None, None), size=(dp(156), dp(22)))
        dot_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(None, 1), width=dp(8))
        dot_wrap.add_widget(DotIcon(size_hint=(None, None), size=(dp(14), dp(14))))
        badge.add_widget(dot_wrap)
        badge.add_widget(Label(text="100% LOCAL & OFFLINE", color=COLOR_TEXT_MUTED,
                               font_size="9sp", bold=True))
        badge_wrap.add_widget(badge)
        body.add_widget(badge_wrap)

        body.add_widget(BoxLayout(size_hint=(1, 0.05)))
        body.add_widget(Label(text="Encuentra tu auto fácilmente", color=COLOR_TEXT, font_size="16sp",
                              bold=True, size_hint=(1, None), height=dp(26)))
        desc = Label(text="Guarda el número de tu cajón al estacionar.\n"
                          "Nosotros iluminamos en el mapa. Sin cuentas, sin señal ni ruido.",
                     color=COLOR_TEXT_MUTED, font_size="12sp", halign="center", valign="top",
                     size_hint=(1, None), height=dp(50))
        desc.bind(size=lambda i, v: setattr(i, "text_size", v))
        body.add_widget(desc)
        body.add_widget(BoxLayout(size_hint=(1, 1)))

        btn = RoundedButton(text=">  Comenzar", size_hint=(1, None), height=dp(50))
        btn.bind(on_release=lambda i: self.goto_help())
        body.add_widget(btn)

        dots = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, None), height=dp(20))
        dots.add_widget(RoundedBox(bg_color=COLOR_TEXT_MUTED, radius=[dp(2)],
                                   size_hint=(None, None), size=(dp(80), dp(4))))
        body.add_widget(dots)

        root.add_widget(body)
        self.add_widget(root)

    def goto_help(self):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "help"


# ----------------------------------------------------------------------
# 2. PANTALLA DE AYUDA
# ----------------------------------------------------------------------
class HelpScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        root.add_widget(status_bar())

        body = BoxLayout(orientation="vertical", padding=(dp(24), dp(16)), spacing=dp(14))
        body.add_widget(screen_title("¿Cómo funciona?", "Guía rápida de 3 pasos sencillos"))

        steps = [
            (CarIcon, "1. Estaciona tu auto", "Estaciónate libremente en el nivel -1 del subterráneo."),
            (PencilIcon, "2. Guarda tu cajón",
             "Elige la fila e ingresa el número impreso en el piso o columna (ej. C-08)."),
            (PinIcon, "3. Encuéntralo en el mapa",
             "La app iluminará tu cajón para que sepas exactamente dónde volver."),
        ]
        for IconCls, title, desc in steps:
            card = RoundedBox(bg_color=COLOR_CARD, radius=[dp(14)], size_hint=(1, None),
                              height=dp(78), padding=dp(14), spacing=dp(12))
            icon_box = RoundedBox(bg_color=COLOR_CARD_LIGHT, radius=[dp(10)],
                                  size_hint=(None, 1), width=dp(44))
            wrap = AnchorLayout(anchor_x="center", anchor_y="center")
            wrap.add_widget(IconCls(size_hint=(None, None), size=(dp(22), dp(22))))
            icon_box.add_widget(wrap)
            card.add_widget(icon_box)

            text_box = BoxLayout(orientation="vertical")
            text_box.add_widget(mk_label(title, "14sp", COLOR_TEXT, True, height=dp(22)))
            d = mk_label(desc, "11sp", COLOR_TEXT_MUTED)
            d.valign = "top"
            text_box.add_widget(d)
            card.add_widget(text_box)
            body.add_widget(card)

        note = RoundedBox(bg_color=COLOR_CARD, radius=[dp(14)], size_hint=(1, None),
                          height=dp(60), padding=dp(14), spacing=dp(10))
        wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(None, 1), width=dp(26))
        wrap.add_widget(NoEntryIcon(size_hint=(None, None), size=(dp(22), dp(22))))
        note.add_widget(wrap)
        note_lbl = mk_label("[b]Funciona 100% offline.[/b] No requieres cuenta ni cobertura; "
                            "el sistema queda guardado en tu celular.", "10sp", COLOR_TEXT_MUTED)
        note_lbl.markup = True
        note.add_widget(note_lbl)
        body.add_widget(note)

        body.add_widget(BoxLayout(size_hint=(1, 1)))
        btn = RoundedButton(text="Entendido", size_hint=(1, None), height=dp(50))
        btn.bind(on_release=lambda i: self.goto_download())
        body.add_widget(btn)

        root.add_widget(body)
        self.add_widget(root)

    def goto_download(self):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "download"


# ----------------------------------------------------------------------
# 3. DESCARGA DE MAPA
# ----------------------------------------------------------------------
class MapDownloadScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pendiente = False
        root = BoxLayout(orientation="vertical")
        root.add_widget(status_bar())

        body = BoxLayout(orientation="vertical", padding=(dp(24), dp(20)), spacing=dp(18))
        body.add_widget(BoxLayout(size_hint=(1, 0.3)))

        badge_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, None), height=dp(70))
        badge = RoundedBox(bg_color=COLOR_CARD, radius=[dp(35)], size_hint=(None, None), size=(dp(70), dp(70)))
        inner = AnchorLayout(anchor_x="center", anchor_y="center")
        self.download_pin = PinIcon(size_hint=(None, None), size=(dp(30), dp(30)))
        inner.add_widget(self.download_pin)
        badge.add_widget(inner)
        badge_wrap.add_widget(badge)
        body.add_widget(badge_wrap)

        status_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, None), height=dp(26))
        self.status_pill = RoundedBox(bg_color=(0, 0, 0, 0), radius=[dp(13)], spacing=dp(6),
                                      padding=(dp(12), 0), size_hint=(None, None), size=(dp(270), dp(22)))
        self.status_icon_wrap = AnchorLayout(anchor_x="center", anchor_y="center",
                                             size_hint=(None, 1), width=0)
        self.status_pill.add_widget(self.status_icon_wrap)
        self.status_lbl = Label(text="Descargando...", color=COLOR_TEXT_MUTED, font_size="11sp", bold=True)
        self.status_pill.add_widget(self.status_lbl)
        status_wrap.add_widget(self.status_pill)
        body.add_widget(status_wrap)

        self.title_lbl = Label(text="Descargando mapa del Nivel -1...", color=COLOR_TEXT,
                               font_size="16sp", bold=True, size_hint=(1, None), height=dp(24))
        body.add_widget(self.title_lbl)

        self.progress = GoldProgressBar(value=15, size_hint=(1, None), height=dp(6))
        body.add_widget(self.progress)

        desc = Label(text="Necesitarás conexión a internet solo esta vez. El resto de la app "
                          "funcionará totalmente sin señal.",
                     color=COLOR_TEXT_MUTED, font_size="11sp", halign="center", valign="top",
                     size_hint=(1, None), height=dp(40))
        desc.bind(size=lambda i, v: setattr(i, "text_size", v))
        body.add_widget(desc)
        body.add_widget(BoxLayout(size_hint=(1, 1)))

        self.btn = RoundedButton(text="Continuar al Mapa", size_hint=(1, None), height=dp(50),
                                 bg_color=COLOR_CARD_LIGHT, text_color=COLOR_TEXT_MUTED)
        self.btn.disabled = True
        self.btn.bind(on_release=lambda i: self.goto_map())
        body.add_widget(self.btn)

        root.add_widget(body)
        self.add_widget(root)

    def on_enter(self):
        self.progress.set_value(10)
        self.btn.disabled = True
        self.btn.bg_color = COLOR_CARD_LIGHT
        self.btn.text_color = COLOR_TEXT_MUTED
        self.title_lbl.text = "Descargando mapa del Nivel -1..."
        self.status_lbl.text = "Descargando..."
        self.status_lbl.color = COLOR_TEXT_MUTED
        self.status_pill.border_color = [0, 0, 0, 0]
        self.status_icon_wrap.clear_widgets()
        self.status_icon_wrap.width = 0
        self.download_pin.show_check = False
        self._pendiente = True
        Clock.unschedule(self._tick)
        Clock.schedule_interval(self._tick, 0.15)
        App.get_running_app().descargar_mapa(self._terminar)   # pide el mapa a la API

    def on_leave(self):
        Clock.unschedule(self._tick)

    def _tick(self, dt):
        # La barra avanza hasta 90% mientras se espera la respuesta del servidor
        if self._pendiente and self.progress._val < 90:
            self.progress.set_value(self.progress._val + 3)

    def _terminar(self, origen):
        """origen: 'servidor' (mapa nuevo), 'guardado' o 'integrado' (sin conexion)."""
        self._pendiente = False
        Clock.unschedule(self._tick)
        self.progress.set_value(100)
        textos = {
            "servidor": "Descarga Completada",
            "guardado": "Sin conexión: mapa guardado",
            "integrado": "Sin conexión: mapa integrado",
        }
        self.title_lbl.text = "Mapa del Nivel -1 listo"
        self.status_lbl.text = textos.get(origen, "Descarga Completada")
        self.status_lbl.color = COLOR_GOLD
        self.status_pill.border_color = COLOR_GOLD
        self.status_icon_wrap.clear_widgets()
        self.status_icon_wrap.width = dp(16)
        self.status_icon_wrap.add_widget(
            CheckIcon(size_hint=(None, None), size=(dp(12), dp(12)), color_rgba=COLOR_GOLD))
        self.download_pin.show_check = True
        self.btn.disabled = False
        self.btn.bg_color = COLOR_GOLD
        self.btn.text_color = (0.043, 0.055, 0.098, 1)

    def goto_map(self):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "empty_map"


# ----------------------------------------------------------------------
# 4. MAPA - ESTADO VACIO
# ----------------------------------------------------------------------
class EmptyMapScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        root.add_widget(status_bar())

        mid = BoxLayout(orientation="vertical", padding=(dp(16), dp(4), dp(16), dp(8)), spacing=dp(8))
        mid.add_widget(nav_header("Nivel -1", "Estacionamiento Subterráneo"))
        self.map = ParkingMap(size_hint=(1, 1))
        mid.add_widget(self.map)
        root.add_widget(mid)

        dock = bottom_dock(dp(150))
        dock.add_widget(mk_label("¿Dónde te estacionaste?", "15sp", COLOR_TEXT, True, height=dp(22)))
        dock.add_widget(mk_label("Guarda tu cajón para no perder el auto", "11sp",
                                 COLOR_TEXT_MUTED, height=dp(16)))
        btn = RoundedButton(text="+  Guardar mi cajón", size_hint=(1, None), height=dp(50))
        btn.bind(on_release=lambda i: self.goto_selection())
        dock.add_widget(btn)
        root.add_widget(dock)
        self.add_widget(root)

    def on_pre_enter(self):
        self.map.selected = ""

    def goto_selection(self):
        self.manager.transition = SlideTransition(direction="up")
        self.manager.current = "selection"


# ----------------------------------------------------------------------
# 5. SELECCION DE CAJON (fila A-F + teclado numerico)
# ----------------------------------------------------------------------
class SpotSelectionScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fila = "A"
        self.entered = ""
        root = BoxLayout(orientation="vertical")
        root.add_widget(status_bar())

        body = BoxLayout(orientation="vertical", padding=(dp(16), dp(6), dp(16), dp(10)), spacing=dp(10))
        body.add_widget(mk_label("Nivel -1", "20sp", COLOR_TEXT, True, height=dp(30)))

        # Mapa de fondo atenuado (solo la parte superior del plano)
        self.bg_map = ParkingMap(crop=True, opacity=0.3, size_hint=(1, None), height=dp(90))
        body.add_widget(self.bg_map)

        panel = RoundedBox(orientation="vertical", bg_color=COLOR_CARD, border_color=COLOR_BORDER,
                           border_width=dp(1), radius=[dp(18)], padding=dp(16), spacing=dp(10),
                           size_hint=(1, 1))
        panel.add_widget(Label(text="INGRESA TU FILA Y CAJÓN", color=COLOR_TEXT_MUTED, font_size="11sp",
                               bold=True, size_hint=(1, None), height=dp(16)))

        self.display_lbl = Label(text="A-__", color=COLOR_GOLD, font_size="34sp", bold=True,
                                 size_hint=(1, None), height=dp(52))
        panel.add_widget(self.display_lbl)

        self.hint = mk_label("", "10sp", COLOR_TEXT_MUTED, halign="center", height=dp(30))
        panel.add_widget(self.hint)

        # Selector de fila
        chips_row = BoxLayout(size_hint=(1, None), height=dp(40), spacing=dp(8))
        self.chips = {}
        for letter in FILAS:
            chip = FilaChip(letter)
            chip.bind(on_release=lambda i: self._set_fila(i.letter))
            self.chips[letter] = chip
            chips_row.add_widget(chip)
        panel.add_widget(chips_row)

        # Teclado numerico
        keypad = GridLayout(cols=3, spacing=dp(8), size_hint=(1, None), height=dp(170))
        for k in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "Borrar", "0", "Aceptar"]:
            special = k in ("Borrar", "Aceptar")
            b = RoundedButton(text=k, bg_color=COLOR_CARD if special else COLOR_BG,
                              text_color=COLOR_GOLD if k == "Aceptar" else COLOR_TEXT,
                              font_size="13sp" if special else "18sp", bold=True)
            b.bind(on_release=lambda i, key=k: self._key(key))
            keypad.add_widget(b)
        panel.add_widget(keypad)
        body.add_widget(panel)

        confirm_btn = RoundedButton(text="Confirmar cajón", size_hint=(1, None), height=dp(50))
        confirm_btn.bind(on_release=lambda i: self.confirm())
        body.add_widget(confirm_btn)

        root.add_widget(body)
        self.add_widget(root)
        self._set_fila("A")

    def on_pre_enter(self):
        self.entered = ""
        self._refresh()

    def _set_fila(self, letter):
        self.fila = letter
        self.entered = ""
        for L, chip in self.chips.items():
            chip.set_active(L == letter)
        self._refresh()

    def _key(self, key):
        if key == "Borrar":
            self.entered = self.entered[:-1]
        elif key == "Aceptar":
            return self.confirm()
        elif len(self.entered) < 2:
            self.entered += key
        self._refresh()

    def _refresh(self):
        self.display_lbl.text = f"{self.fila}-{self.entered.ljust(2, '_')}"
        self.hint.color = COLOR_TEXT_MUTED
        self.hint.text = (f"Fila {self.fila}: cajones del 01 al {FILAS[self.fila]:02d}. "
                          "Verifica el número pintado en el piso o columna junto a tu auto.")

    def confirm(self):
        if not self.entered:
            return
        n = int(self.entered)
        if not 1 <= n <= FILAS[self.fila]:
            self.hint.color = COLOR_RED
            self.hint.text = (f"El cajón {self.fila}-{n:02d} no existe. "
                              f"La fila {self.fila} va del 01 al {FILAS[self.fila]:02d}.")
            return
        spot = f"{self.fila}-{n:02d}"
        App.get_running_app().save_spot(spot)              # guarda en el celular
        self.entered = ""
        self._refresh()
        self.manager.get_screen("saved").refresh(spot)     # prepara el mapa iluminado
        self.manager.transition = FadeTransition()
        self.manager.current = "saved"


# ----------------------------------------------------------------------
# 6. MAPA - CAJON GUARDADO (el cajon se ilumina en el mapa)
# ----------------------------------------------------------------------
class SavedSpotScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spot = ""
        root = BoxLayout(orientation="vertical")
        root.add_widget(status_bar())

        success = BoxLayout(size_hint=(1, None), height=dp(18), spacing=dp(4))
        success.add_widget(DotIcon(size_hint=(None, 1), width=dp(16)))
        success.add_widget(mk_label("Cajón Guardado Con Éxito", "11sp", COLOR_GOLD, True))

        mid = BoxLayout(orientation="vertical", padding=(dp(16), dp(4), dp(16), dp(8)), spacing=dp(8))
        mid.add_widget(nav_header("Nivel -1", success))
        self.map = ParkingMap(size_hint=(1, 1))
        mid.add_widget(self.map)
        root.add_widget(mid)

        dock = bottom_dock(dp(176), spacing=dp(12))
        row = BoxLayout(size_hint=(1, None), height=dp(72))
        info = BoxLayout(orientation="vertical", spacing=dp(2))
        info.add_widget(mk_label("UBICACIÓN DE TU AUTO", "11sp", COLOR_GOLD, True, height=dp(16)))
        self.spot_lbl = mk_label("Cajón", "24sp", COLOR_TEXT, True, height=dp(32))
        info.add_widget(self.spot_lbl)
        self.near_lbl = mk_label("", "12sp", COLOR_TEXT_MUTED, height=dp(18))
        info.add_widget(self.near_lbl)
        row.add_widget(info)
        icon_wrap = AnchorLayout(anchor_x="right", anchor_y="center", size_hint=(None, 1), width=dp(60))
        icon_box = RoundedBox(bg_color=COLOR_GOLD_DARK, radius=[dp(16)], size_hint=(None, None),
                              size=(dp(56), dp(56)))
        inner = AnchorLayout(anchor_x="center", anchor_y="center")
        inner.add_widget(CarIcon(size_hint=(None, None), size=(dp(28), dp(28))))
        icon_box.add_widget(inner)
        icon_wrap.add_widget(icon_box)
        row.add_widget(icon_wrap)
        dock.add_widget(row)

        actions = BoxLayout(size_hint=(1, None), height=dp(44), spacing=dp(12))
        delete_btn = RoundedButton(text="Borrar registro", bg_color=(0.20, 0.09, 0.09, 1),
                                   text_color=COLOR_RED, font_size="14sp", radius=[dp(10)])
        delete_btn.bind(on_release=lambda i: self.goto_delete_confirm())
        actions.add_widget(delete_btn)
        dock.add_widget(actions)

        root.add_widget(dock)
        self.add_widget(root)

    def refresh(self, spot):
        self.spot = spot
        self.spot_lbl.text = f"Cajón {spot}"
        self.near_lbl.text = f"Cerca de: {near_refs(spot)}"
        self.map.selected = spot          # <- aqui se ilumina el cajon

    def on_enter(self):
        self.map.restart()

    def on_leave(self):
        self.map.halt()

    def goto_delete_confirm(self):
        self.manager.get_screen("delete_confirm").set_spot(self.spot)
        self.manager.transition = FadeTransition()
        self.manager.current = "delete_confirm"


# ----------------------------------------------------------------------
# 7. CONFIRMACION DE BORRADO
# ----------------------------------------------------------------------
class DeleteConfirmScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spot = ""
        self.overlay = FloatLayout()
        self.add_widget(self.overlay)
        with self.overlay.canvas.before:
            Color(0.02, 0.03, 0.05, 0.85)
            self._bg_rect = Rectangle(pos=self.overlay.pos, size=self.overlay.size)
        self.overlay.bind(pos=self._update_overlay, size=self._update_overlay)

        self.dialog = RoundedBox(orientation="vertical", bg_color=COLOR_CARD, radius=[dp(18)],
                                 padding=dp(22), spacing=dp(14), size_hint=(0.85, None),
                                 height=dp(230), pos_hint={"center_x": 0.5, "center_y": 0.5})

        icon_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, None), height=dp(46))
        icon_bg = RoundedBox(bg_color=(0.25, 0.08, 0.08, 1), radius=[dp(23)],
                             size_hint=(None, None), size=(dp(46), dp(46)))
        inner = AnchorLayout(anchor_x="center", anchor_y="center")
        inner.add_widget(WarningTriangleIcon(size_hint=(None, None), size=(dp(24), dp(24))))
        icon_bg.add_widget(inner)
        icon_wrap.add_widget(icon_bg)
        self.dialog.add_widget(icon_wrap)

        self.question_lbl = Label(text="", color=COLOR_TEXT, font_size="14sp", bold=True,
                                  halign="center", size_hint=(1, None), height=dp(44))
        self.dialog.add_widget(self.question_lbl)

        note = Label(text="Esta acción eliminará el registro resaltado de tu mapa local. "
                          "Deberás ingresarlo nuevamente cuando reestaciones.",
                     color=COLOR_TEXT_MUTED, font_size="10sp", halign="center", valign="top",
                     size_hint=(1, None), height=dp(40))
        note.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.dialog.add_widget(note)

        confirm_btn = RoundedButton(text="Sí, borrar registro", bg_color=COLOR_RED,
                                    text_color=(1, 1, 1, 1), size_hint=(1, None), height=dp(42))
        confirm_btn.bind(on_release=lambda i: self.confirm_delete())
        self.dialog.add_widget(confirm_btn)

        cancel_btn = RoundedButton(text="Cancelar", bg_color=(0, 0, 0, 0), text_color=COLOR_TEXT_MUTED,
                                   size_hint=(1, None), height=dp(30))
        cancel_btn.bind(on_release=lambda i: self.cancel())
        self.dialog.add_widget(cancel_btn)
        self.overlay.add_widget(self.dialog)

    def _update_overlay(self, *args):
        self._bg_rect.pos = self.overlay.pos
        self._bg_rect.size = self.overlay.size

    def set_spot(self, spot):
        self.spot = spot
        self.question_lbl.text = f"¿Seguro que quieres borrar el registro\ndel cajón {spot}?"

    def confirm_delete(self):
        App.get_running_app().clear_spot()
        self.manager.get_screen("saved").map.selected = ""   # apaga el cajon iluminado
        self.manager.transition = FadeTransition()
        self.manager.current = "empty_map"

    def cancel(self):
        self.manager.transition = FadeTransition()
        self.manager.current = "saved"


# ----------------------------------------------------------------------
# APP
# ----------------------------------------------------------------------
class AlzParkingApp(App):
    saved_spot = StringProperty(allownone=True)

    def build(self):
        self.title = "AlzParking"
        Window.clearcolor = COLOR_BG
        self.store = JsonStore(os.path.join(self.user_data_dir, "alzparking.json"))
        self.cargar_mapa_guardado()      # usa el ultimo mapa descargado (offline)

        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(HelpScreen(name="help"))
        sm.add_widget(MapDownloadScreen(name="download"))
        sm.add_widget(EmptyMapScreen(name="empty_map"))
        sm.add_widget(SpotSelectionScreen(name="selection"))
        sm.add_widget(SavedSpotScreen(name="saved"))
        sm.add_widget(DeleteConfirmScreen(name="delete_confirm"))

        # Si ya hay un cajon guardado, abre directo el mapa con el cajon iluminado
        if self.store.exists("spot"):
            spot = self.store.get("spot")["value"]
            if spot in SPOTS:
                self.saved_spot = spot
                sm.get_screen("saved").refresh(spot)
                sm.current = "saved"
        return sm

    # ---------- mapa desde la API ----------
    def cargar_mapa_guardado(self):
        if self.store.exists("mapa"):
            try:
                apply_spots(spots_from_api(self.store.get("mapa")["cajones"]))
                return True
            except Exception:
                pass
        return False

    def descargar_mapa(self, on_done):
        """Pide GET /niveles/{NIVEL_ID}/cajones en un hilo aparte (no congela la UI)."""
        def trabajo():
            try:
                req = urllib.request.Request(
                    f"{API_URL}/niveles/{NIVEL_ID}/cajones",
                    headers={"Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=API_TIMEOUT,
                                            context=_ssl_context()) as r:
                    datos = json.loads(r.read().decode("utf-8"))
                spots = spots_from_api(datos)
            except Exception as e:
                print("[AlzParking] No se pudo descargar el mapa:", e)
                Clock.schedule_once(lambda dt: self._mapa_sin_conexion(on_done))
                return
            Clock.schedule_once(lambda dt: self._mapa_descargado(datos, spots, on_done))

        threading.Thread(target=trabajo, daemon=True).start()

    def _mapa_descargado(self, datos, spots, on_done):
        apply_spots(spots)
        self.store.put("mapa", cajones=datos)      # queda guardado para usar sin senal
        self.redibujar_mapas()
        on_done("servidor")

    def _mapa_sin_conexion(self, on_done):
        if self.cargar_mapa_guardado():
            origen = "guardado"
        else:
            apply_spots(BUILTIN_SPOTS)
            origen = "integrado"
        self.redibujar_mapas()
        on_done(origen)

    def redibujar_mapas(self):
        for pantalla in self.root.screens:
            for nombre in ("map", "bg_map"):
                m = getattr(pantalla, nombre, None)
                if m is not None:
                    m._draw_static()
                    m._draw_dyn()

    def save_spot(self, spot):
        self.saved_spot = spot
        self.store.put("spot", value=spot)

    def clear_spot(self):
        self.saved_spot = None
        if self.store.exists("spot"):
            self.store.delete("spot")


if __name__ == "__main__":
    AlzParkingApp().run()