from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line, Ellipse
from kivy.clock import Clock
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.animation import Animation
 
# ----------------------------------------------------------------------
# Paleta de colores
# ----------------------------------------------------------------------
COLOR_BG = (0.043, 0.055, 0.098, 1)          # fondo azul-negro
COLOR_CARD = (0.098, 0.114, 0.161, 1)        # tarjetas
COLOR_CARD_LIGHT = (0.145, 0.165, 0.220, 1)  # tarjetas resaltadas / inputs
COLOR_BORDER = (0.220, 0.240, 0.290, 1)      # bordes sutiles
COLOR_GOLD = (0.949, 0.729, 0.078, 1)        # botones principales / acentos
COLOR_GOLD_DARK = (0.20, 0.17, 0.06, 1)      # fondo icono splash
COLOR_TEXT = (0.937, 0.941, 0.949, 1)        # texto principal (blanco)
COLOR_TEXT_MUTED = (0.560, 0.588, 0.650, 1)  # texto secundario gris
COLOR_RED = (0.898, 0.263, 0.263, 1)         # botones de borrar / alerta
COLOR_GREEN = (0.298, 0.808, 0.400, 1)       # estados de éxito
 
Window.clearcolor = COLOR_BG
 
 
# ----------------------------------------------------------------------
# Widgets reutilizables con esquinas redondeadas
# ----------------------------------------------------------------------
class RoundedBox(BoxLayout):
    """BoxLayout con fondo de color y esquinas redondeadas. Admite borde opcional."""
    bg_color = ListProperty(COLOR_CARD)
    radius = ListProperty([dp(14)])
    border_color = ListProperty(None)
    border_width = ListProperty([dp(1.5)])
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color = Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            self._border_color = Color(0, 0, 0, 0)
            self._border_line = Line(width=self.border_width[0] if self.border_width else dp(1.5))
        self.bind(pos=self._update, size=self._update, bg_color=self._update_color,
                  border_color=self._update_border_color)
        if self.border_color:
            self._update_border_color()
 
    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = self.radius
        r = self.radius[0] if self.radius else dp(14)
        self._border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, r)
 
    def _update_color(self, *args):
        self._color.rgba = self.bg_color
 
    def _update_border_color(self, *args):
        self._border_color.rgba = self.border_color if self.border_color else (0, 0, 0, 0)
 
 
class RoundedButton(ButtonBehavior, BoxLayout):
    """Botón custom con fondo redondeado."""
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
        self.bind(pos=self._update, size=self._update, bg_color=self._update_color)
        self._label = Label(
            text=self.text, color=self.text_color, font_size=self.font_size,
            bold=self.bold
        )
        self.add_widget(self._label)
        self.bind(text=lambda i, v: setattr(self._label, "text", v))
        self.bind(text_color=lambda i, v: setattr(self._label, "color", v))
 
    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = self.radius
 
    def _update_color(self, *args):
        self._color.rgba = self.bg_color
 
    def on_press(self):
        Animation.cancel_all(self)
        Animation(opacity=0.75, duration=0.08).start(self)
 
    def on_release(self):
        Animation(opacity=1, duration=0.12).start(self)
 
 
class ParkingSpotCell(ButtonBehavior, BoxLayout):
    """Una celda de cajón dentro de la grilla del estacionamiento."""
    spot_id = StringProperty("")
    selected = BooleanProperty(False)
 
    def __init__(self, spot_id, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.spot_id = spot_id
        self._on_select = on_select
        with self.canvas.before:
            self._color = Color(*COLOR_CARD_LIGHT)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(6)])
        self.bind(pos=self._update, size=self._update)
        self.label = Label(text=spot_id, color=COLOR_TEXT, font_size="11sp")
        self.add_widget(self.label)
 
    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
 
    def on_release(self):
        if self._on_select:
            self._on_select(self.spot_id)
 
    def set_selected(self, is_selected):
        self.selected = is_selected
        self._color.rgba = COLOR_GOLD if is_selected else COLOR_CARD_LIGHT
        self.label.color = (0.043, 0.055, 0.098, 1) if is_selected else COLOR_TEXT
 
 
class BaseScreen(Screen):
    """Screen con fondo sólido."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*COLOR_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
 
    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
 
 
def icon_badge(symbol, bg_color=COLOR_CARD_LIGHT, fg_color=COLOR_TEXT, size=dp(44), radius=None,
               font_size="16sp", bold=True):
    r = radius if radius is not None else [size / 2]
    badge = RoundedBox(bg_color=bg_color, radius=r, size_hint=(None, None), size=(size, size))
    badge.add_widget(Label(text=symbol, color=fg_color, font_size=font_size, bold=bold))
    return badge
 
 
class PhoneStatusIcons(Widget):
    """Los 3 iconos típicos de la barra de estado de un celular (señal / wifi / batería)."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color = Color(*COLOR_TEXT)
            self._signal_rects = [Rectangle() for _ in range(4)]
            self._wifi_lines = [Line(width=dp(1.4)) for _ in range(3)]
            self._battery_outline = Line(width=dp(1.3))
            self._battery_fill = Rectangle()
            self._battery_tip = Rectangle()
        self.bind(pos=self._redraw, size=self._redraw)
 
    def _redraw(self, *args):
        x, y = self.pos
        h = self.height
 
        # --- Señal (4 barras crecientes) ---
        bar_w = dp(3)
        gap = dp(2)
        base_h = dp(5)
        step = dp(2.3)
        sx = x
        for i, rect in enumerate(self._signal_rects):
            bh = base_h + step * i
            rect.pos = (sx, y + (h - dp(11)) / 2)
            rect.size = (bar_w, bh)
            sx += bar_w + gap
 
        # --- WiFi (3 arcos concéntricos) ---
        wifi_cx = x + dp(34)
        wifi_cy = y + h / 2 - dp(2)
        radii = [dp(3), dp(6), dp(9)]
        for line, r in zip(self._wifi_lines, radii):
            line.circle = (wifi_cx, wifi_cy, r, 35, 145)
 
        # --- Batería (contorno + relleno + terminal) ---
        bat_w, bat_h = dp(20), dp(10)
        bx = x + dp(50)
        by = y + (h - bat_h) / 2
        radius = dp(2)
        self._battery_outline.rounded_rectangle = (bx, by, bat_w, bat_h, radius)
        pad = dp(2)
        self._battery_fill.pos = (bx + pad, by + pad)
        self._battery_fill.size = (bat_w - pad * 2 - dp(2), bat_h - pad * 2)
        self._battery_tip.pos = (bx + bat_w, by + bat_h / 2 - dp(2))
        self._battery_tip.size = (dp(2), dp(4))
 
 
class CheckIcon(Widget):
    """Palomita (check) vectorial para estados de éxito."""
    color_rgba = ListProperty(COLOR_GREEN)
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color = Color(*self.color_rgba)
            self._line = Line(width=dp(1.8), cap="round", joint="round")
        self.bind(pos=self._redraw, size=self._redraw, color_rgba=self._update_color)
 
    def _update_color(self, *args):
        self._color.rgba = self.color_rgba
 
    def _redraw(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        self._line.points = [
            x + w * 0.12, y + h * 0.52,
            x + w * 0.40, y + h * 0.18,
            x + w * 0.90, y + h * 0.82,
        ]
 
 
class DotIcon(Widget):
    """Punto/pin de ubicación vectorial (círculo relleno)."""
    color_rgba = ListProperty(COLOR_GOLD)
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color = Color(*self.color_rgba)
            self._ellipse = Ellipse()
        self.bind(pos=self._redraw, size=self._redraw, color_rgba=self._update_color)
 
    def _update_color(self, *args):
        self._color.rgba = self.color_rgba
 
    def _redraw(self, *args):
        d = min(self.width, self.height) * 0.5
        cx = self.center_x - d / 2
        cy = self.center_y - d / 2
        self._ellipse.pos = (cx, cy)
        self._ellipse.size = (d, d)
 
 
class CarIcon(Widget):
    """Icono vectorial de auto visto."""
    color_rgba = ListProperty(COLOR_GOLD)
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color = Color(*self.color_rgba)
            self._body = Line(width=dp(1.6), joint="round", cap="round")
            self._wheel1 = Line(width=dp(1.4))
            self._wheel2 = Line(width=dp(1.4))
        self.bind(pos=self._redraw, size=self._redraw, color_rgba=self._update_color)
 
    def _update_color(self, *args):
        self._color.rgba = self.color_rgba
 
    def _redraw(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        # silueta simplificada tipo "auto" (carrocería + parabrisas)
        self._body.points = [
            x + w * 0.05, y + h * 0.40,
            x + w * 0.20, y + h * 0.62,
            x + w * 0.35, y + h * 0.62,
            x + w * 0.42, y + h * 0.78,
            x + w * 0.62, y + h * 0.78,
            x + w * 0.70, y + h * 0.62,
            x + w * 0.85, y + h * 0.62,
            x + w * 0.95, y + h * 0.40,
            x + w * 0.90, y + h * 0.28,
            x + w * 0.10, y + h * 0.28,
            x + w * 0.05, y + h * 0.40,
        ]
        r = w * 0.09
        self._wheel1.circle = (x + w * 0.28, y + h * 0.28, r)
        self._wheel2.circle = (x + w * 0.72, y + h * 0.28, r)
 
 
class PencilIcon(Widget):
    """Icono vectorial de lápiz para el paso 'Guarda el número'."""
    color_rgba = ListProperty(COLOR_GOLD)
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color = Color(*self.color_rgba)
            self._body = Line(width=dp(1.6), joint="round", cap="round", close=True)
            self._tip_line = Line(width=dp(1.2))
        self.bind(pos=self._redraw, size=self._redraw, color_rgba=self._update_color)
 
    def _update_color(self, *args):
        self._color.rgba = self.color_rgba
 
    def _redraw(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        self._body.points = [
            x + w * 0.15, y + h * 0.15,
            x + w * 0.30, y + h * 0.10,
            x + w * 0.90, y + h * 0.70,
            x + w * 0.80, y + h * 0.90,
            x + w * 0.20, y + h * 0.30,
        ]
        self._tip_line.points = [
            x + w * 0.15, y + h * 0.15,
            x + w * 0.20, y + h * 0.30,
        ]
 
 
class PinIcon(Widget):
    """Icono vectorial de pin de ubicación."""
    color_rgba = ListProperty(COLOR_GOLD)
    show_check = BooleanProperty(False)
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color = Color(*self.color_rgba)
            self._outline = Line(width=dp(1.6), joint="round", cap="round")
            self._check = Line(width=dp(1.6), cap="round", joint="round")
        self.bind(pos=self._redraw, size=self._redraw, color_rgba=self._update_color,
                  show_check=self._redraw)
 
    def _update_color(self, *args):
        self._color.rgba = self.color_rgba
 
    def _redraw(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        cx = x + w * 0.5
        top_cy = y + h * 0.62
        r = w * 0.30
        import math
        pts = []
        # arco superior de la gota (de -40° a 220°, dejando la punta abajo)
        for deg in range(-40, 221, 10):
            rad = math.radians(deg)
            pts.append(cx + r * math.cos(rad))
            pts.append(top_cy + r * math.sin(rad))
        # punta inferior
        pts += [cx, y + h * 0.06]
        self._outline.points = pts
        if self.show_check:
            self._check.points = [
                cx - r * 0.5, top_cy,
                cx - r * 0.1, top_cy - r * 0.4,
                cx + r * 0.55, top_cy + r * 0.45,
            ]
        else:
            self._check.points = []
 
 
class NoEntryIcon(Widget):
    """Icono de 'prohibido', usado en el aviso de 'Funciona 100% offline'."""
    color_rgba = ListProperty(COLOR_RED)
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color = Color(*self.color_rgba)
            self._circle = Line(width=dp(1.6))
            self._slash = Line(width=dp(1.6), cap="round")
        self.bind(pos=self._redraw, size=self._redraw, color_rgba=self._update_color)
 
    def _update_color(self, *args):
        self._color.rgba = self.color_rgba
 
    def _redraw(self, *args):
        cx, cy = self.center_x, self.center_y
        r = min(self.width, self.height) * 0.42
        self._circle.circle = (cx, cy, r)
        import math
        ang = math.radians(45)
        self._slash.points = [
            cx - r * math.cos(ang), cy - r * math.sin(ang),
            cx + r * math.cos(ang), cy + r * math.sin(ang),
        ]
 
 
class CompassIcon(Widget):
    """Icono de brújula."""
    color_rgba = ListProperty(COLOR_GOLD)
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color = Color(*self.color_rgba)
            self._circle = Line(width=dp(1.5))
            self._needle = Line(width=dp(1.3), close=True, joint="round")
        self.bind(pos=self._redraw, size=self._redraw, color_rgba=self._update_color)
 
    def _update_color(self, *args):
        self._color.rgba = self.color_rgba
 
    def _redraw(self, *args):
        cx, cy = self.center_x, self.center_y
        r = min(self.width, self.height) * 0.42
        self._circle.circle = (cx, cy, r)
        self._needle.points = [
            cx, cy + r * 0.6,
            cx + r * 0.28, cy,
            cx, cy - r * 0.6,
            cx - r * 0.28, cy,
        ]
 
 
class ChevronDownIcon(Widget):
    """Pequeña flecha/chevron apuntando hacia abajo."""
    color_rgba = ListProperty(COLOR_GOLD)
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color = Color(*self.color_rgba)
            self._line = Line(width=dp(1.6), cap="round", joint="round")
        self.bind(pos=self._redraw, size=self._redraw, color_rgba=self._update_color)
 
    def _update_color(self, *args):
        self._color.rgba = self.color_rgba
 
    def _redraw(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        self._line.points = [
            x + w * 0.15, y + h * 0.62,
            x + w * 0.5, y + h * 0.30,
            x + w * 0.85, y + h * 0.62,
        ]
 
 
class CrosshairIcon(Widget):
    """Icono circular con una 'X' en el centro (usado para Escalera/Elevador,
    a modo de marcador de punto de interés en el mapa)."""
    color_rgba = ListProperty(COLOR_TEXT)
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color = Color(*self.color_rgba)
            self._circle = Line(width=dp(1.3))
            self._x1 = Line(width=dp(1.2), cap="round")
            self._x2 = Line(width=dp(1.2), cap="round")
        self.bind(pos=self._redraw, size=self._redraw, color_rgba=self._update_color)
 
    def _update_color(self, *args):
        self._color.rgba = self.color_rgba
 
    def _redraw(self, *args):
        cx, cy = self.center_x, self.center_y
        r = min(self.width, self.height) * 0.46
        self._circle.circle = (cx, cy, r)
        k = r * 0.45
        self._x1.points = [cx - k, cy - k, cx + k, cy + k]
        self._x2.points = [cx - k, cy + k, cx + k, cy - k]
 
 
class WarningTriangleIcon(Widget):
    """Triángulo de alerta con signo de exclamación adentro."""
    color_rgba = ListProperty(COLOR_RED)
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color = Color(*self.color_rgba)
            self._triangle = Line(width=dp(1.8), joint="round", cap="round", close=True)
            self._bar = Line(width=dp(2), cap="round")
            self._dot = Ellipse()
        self.bind(pos=self._redraw, size=self._redraw, color_rgba=self._update_color)
 
    def _update_color(self, *args):
        self._color.rgba = self.color_rgba
        self._dot.pos = self._dot.pos 
 
    def _redraw(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        self._triangle.points = [
            x + w * 0.5, y + h * 0.90,
            x + w * 0.06, y + h * 0.12,
            x + w * 0.94, y + h * 0.12,
        ]
        self._bar.points = [x + w * 0.5, y + h * 0.60, x + w * 0.5, y + h * 0.38]
        dot_d = w * 0.07
        self._dot.pos = (x + w * 0.5 - dot_d / 2, y + h * 0.28 - dot_d / 2)
        self._dot.size = (dot_d, dot_d)
 
 
class GoldProgressBar(Widget):
    """Barra de progreso vectorial en dorado."""
    value = ListProperty([0])  # usamos lista para forzar refresco simple
    max_value = 100
 
    def __init__(self, **kwargs):
        self._val = kwargs.pop("value", 0)
        self.max_value = kwargs.pop("max", 100)
        super().__init__(**kwargs)
        with self.canvas:
            self._track_color = Color(*COLOR_CARD_LIGHT)
            self._track = RoundedRectangle(radius=[dp(3)])
            self._fill_color = Color(*COLOR_GOLD)
            self._fill = RoundedRectangle(radius=[dp(3)])
        self.bind(pos=self._redraw, size=self._redraw)
 
    def set_value(self, v):
        self._val = max(0, min(self.max_value, v))
        self._redraw()
 
    def _redraw(self, *args):
        self._track.pos = self.pos
        self._track.size = self.size
        ratio = self._val / self.max_value if self.max_value else 0
        fw = max(self.height, self.width * ratio)  # nunca menos que un círculo completo
        fw = self.width * ratio
        self._fill.pos = self.pos
        self._fill.size = (max(fw, dp(2) if ratio > 0 else 0), self.height)
 
 
def status_bar():
    """Barra de estado simulada."""
    bar = BoxLayout(size_hint=(1, None), height=dp(28), padding=(dp(16), 0))
    bar.add_widget(Label(text="9:41", color=COLOR_TEXT, font_size="13sp", bold=True,
                          size_hint=(None, 1), width=dp(60), halign="left"))
    bar.add_widget(Label(text=""))
    bar.add_widget(PhoneStatusIcons(size_hint=(None, 1), width=dp(74)))
    return bar
 
 
def screen_title(text, subtitle=None):
    box = BoxLayout(orientation="vertical", size_hint=(1, None), height=dp(60) if subtitle else dp(36),
                     padding=(dp(20), 0))
    box.add_widget(Label(text=text, color=COLOR_TEXT, font_size="22sp", bold=True,
                          halign="left", size_hint=(1, None), height=dp(30)))
    if subtitle:
        lbl = Label(text=subtitle, color=COLOR_TEXT_MUTED, font_size="13sp",
                     halign="left", size_hint=(1, None), height=dp(20))
        lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        box.add_widget(lbl)
    return box
 
 
# ----------------------------------------------------------------------
# 1. SPLASH / BIENVENIDA
# ----------------------------------------------------------------------
class SplashScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        root.add_widget(status_bar())
 
        body = BoxLayout(orientation="vertical", padding=(dp(30), dp(20)), spacing=dp(16))
        body.add_widget(BoxLayout(size_hint=(1, 0.35)))  # spacer
 
        # Icono: cuadrado redondeado con borde dorado y la "P" en el centro
        icon_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, None), height=dp(80))
        icon = RoundedBox(bg_color=(0, 0, 0, 0), border_color=COLOR_GOLD, border_width=[dp(2)],
                           radius=[dp(18)], size_hint=(None, None), size=(dp(64), dp(64)))
        icon.add_widget(Label(text="P", color=COLOR_GOLD, font_size="26sp", bold=True))
        icon_wrap.add_widget(icon)
        body.add_widget(icon_wrap)
 
        title = Label(text="AlzParking", color=COLOR_TEXT, font_size="26sp", bold=True,
                      size_hint=(1, None), height=dp(46))
        body.add_widget(title)
 
        badge_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, None), height=dp(24))
        badge_inner = RoundedBox(bg_color=COLOR_CARD, radius=[dp(12)], spacing=dp(6),
                                  padding=(dp(10), 0),
                                  size_hint=(None, None), size=(dp(156), dp(22)))
        dot_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(None, 1), width=dp(8))
        dot_wrap.add_widget(DotIcon(size_hint=(None, None), size=(dp(7), dp(7)), color_rgba=COLOR_GOLD))
        badge_inner.add_widget(dot_wrap)
        badge_inner.add_widget(Label(text="100% LOCAL & OFFLINE", color=COLOR_TEXT_MUTED,
                                      font_size="9sp", bold=True))
        badge_wrap.add_widget(badge_inner)
        body.add_widget(badge_wrap)
 
        body.add_widget(BoxLayout(size_hint=(1, 0.05)))
 
        subtitle = Label(text="Encuentra tu auto fácilmente", color=COLOR_TEXT, font_size="16sp",
                          bold=True, size_hint=(1, None), height=dp(26))
        body.add_widget(subtitle)
 
        desc = Label(
            text="Guarda el número de tu cajón al estacionar.\n"
                 "Nosotros iluminamos en el mapa. Sin cuentas, sin señal ni ruido.",
            color=COLOR_TEXT_MUTED, font_size="12sp", halign="center", valign="top",
            size_hint=(1, None), height=dp(50)
        )
        desc.bind(size=lambda i, v: setattr(i, "text_size", v))
        body.add_widget(desc)
 
        body.add_widget(BoxLayout(size_hint=(1, 1)))  # spacer flexible
 
        btn = RoundedButton(text=">  Comenzar", size_hint=(1, None), height=dp(50))
        btn.bind(on_release=lambda i: self.goto_help())
        body.add_widget(btn)
 
        dots = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, None), height=dp(20))
        dot = RoundedBox(bg_color=COLOR_TEXT_MUTED, radius=[dp(2)], size_hint=(None, None), size=(dp(80), dp(4)))
        dots.add_widget(dot)
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
            (PencilIcon, "2. Guarda el número", "Ingresa el número de cajón en el que te dejaste tu columna."),
            (PinIcon, "3. Encuéntralo en el mapa", "La app iluminará tu cajón para que sepas exactamente dónde volver."),
        ]
        for IconCls, title, desc in steps:
            card = RoundedBox(bg_color=COLOR_CARD, radius=[dp(14)], size_hint=(1, None), height=dp(78),
                               padding=dp(14), spacing=dp(12))
            icon_box = RoundedBox(bg_color=COLOR_CARD_LIGHT, radius=[dp(10)], size_hint=(None, 1), width=dp(44))
            icon_inner_wrap = AnchorLayout(anchor_x="center", anchor_y="center")
            icon_inner_wrap.add_widget(IconCls(size_hint=(None, None), size=(dp(22), dp(22)),
                                                color_rgba=COLOR_GOLD))
            icon_box.add_widget(icon_inner_wrap)
            card.add_widget(icon_box)
 
            text_box = BoxLayout(orientation="vertical")
            t = Label(text=title, color=COLOR_TEXT, font_size="14sp", bold=True,
                      halign="left", size_hint=(1, None), height=dp(22))
            t.bind(size=lambda i, v: setattr(i, "text_size", v))
            d = Label(text=desc, color=COLOR_TEXT_MUTED, font_size="11sp",
                      halign="left", valign="top", size_hint=(1, 1))
            d.bind(size=lambda i, v: setattr(i, "text_size", v))
            text_box.add_widget(t)
            text_box.add_widget(d)
            card.add_widget(text_box)
            body.add_widget(card)
 
        note = RoundedBox(bg_color=COLOR_CARD, radius=[dp(14)], size_hint=(1, None), height=dp(60),
                           padding=dp(14), spacing=dp(10))
        note_icon_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(None, 1), width=dp(26))
        note_icon_wrap.add_widget(NoEntryIcon(size_hint=(None, None), size=(dp(22), dp(22)), color_rgba=COLOR_RED))
        note.add_widget(note_icon_wrap)
        note_lbl = Label(text="[b]Funciona 100% offline.[/b] No requieres cuenta ni cobertura; "
                               "el sistema queda guardado en tu celular.",
                          markup=True,
                          color=COLOR_TEXT_MUTED, font_size="10sp", halign="left", valign="middle")
        note_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
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
        root = BoxLayout(orientation="vertical")
        root.add_widget(status_bar())
 
        body = BoxLayout(orientation="vertical", padding=(dp(24), dp(20)), spacing=dp(18))
        body.add_widget(BoxLayout(size_hint=(1, 0.3)))
 
        badge_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, None), height=dp(70))
        badge = RoundedBox(bg_color=COLOR_CARD, radius=[dp(35)], size_hint=(None, None), size=(dp(70), dp(70)))
        badge_icon_wrap = AnchorLayout(anchor_x="center", anchor_y="center")
        self.download_pin = PinIcon(size_hint=(None, None), size=(dp(30), dp(30)), color_rgba=COLOR_GOLD)
        badge_icon_wrap.add_widget(self.download_pin)
        badge.add_widget(badge_icon_wrap)
        badge_wrap.add_widget(badge)
        body.add_widget(badge_wrap)
 
        status_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, None), height=dp(26))
        self.status_pill = RoundedBox(bg_color=(0, 0, 0, 0), radius=[dp(13)], spacing=dp(6),
                                       padding=(dp(12), 0), size_hint=(None, None), size=(dp(220), dp(22)))
        self.status_icon_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(None, 1), width=0)
        self.status_pill.add_widget(self.status_icon_wrap)
        self.status_lbl = Label(text="Descargando...", color=COLOR_TEXT_MUTED, font_size="11sp", bold=True)
        self.status_pill.add_widget(self.status_lbl)
        status_wrap.add_widget(self.status_pill)
        body.add_widget(status_wrap)
 
        self.title_lbl = Label(text="Descargando mapa del Nivel -1...", color=COLOR_TEXT,
                                font_size="16sp", bold=True, size_hint=(1, None), height=dp(24))
        body.add_widget(self.title_lbl)
 
        self.progress = GoldProgressBar(max=100, value=15, size_hint=(1, None), height=dp(6))
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
        self.btn.bind(on_release=lambda i: self.goto_map() if not self.btn.disabled else None)
        body.add_widget(self.btn)
 
        root.add_widget(body)
        self.add_widget(root)
 
    def on_enter(self):
        self.progress.set_value(15)
        self.btn.disabled = True
        self.btn.bg_color = COLOR_CARD_LIGHT
        self.btn.text_color = COLOR_TEXT_MUTED
        self.status_lbl.text = "Descargando..."
        self.status_lbl.color = COLOR_TEXT_MUTED
        self.status_pill.bg_color = (0, 0, 0, 0)
        self.status_pill.border_color = None
        self.status_icon_wrap.clear_widgets()
        self.status_icon_wrap.width = 0
        self.download_pin.color_rgba = COLOR_GOLD
        self.download_pin.show_check = False
        Clock.schedule_interval(self._tick, 0.15)
 
    def _tick(self, dt):
        self.progress.set_value(self.progress._val + 12)
        if self.progress._val >= 100:
            self.progress.set_value(100)
            self.status_lbl.text = "Descarga Completada"
            self.status_lbl.color = COLOR_GOLD
            self.status_pill.border_color = COLOR_GOLD
            self.status_icon_wrap.width = dp(16)
            self.status_icon_wrap.add_widget(
                CheckIcon(size_hint=(None, None), size=(dp(12), dp(12)), color_rgba=COLOR_GOLD))
            self.download_pin.show_check = True
            self.title_lbl.text = "Descargando mapa del Nivel -1..."
            self.btn.disabled = False
            self.btn.bg_color = COLOR_GOLD
            self.btn.text_color = (0.043, 0.055, 0.098, 1)
            return False
 
    def goto_map(self):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "empty_map"
 
 
# ----------------------------------------------------------------------
# Grilla de cajones compartida entre EmptyMap y SavedSpot
# ----------------------------------------------------------------------
def build_spot_grid(spots_row_a, spots_row_b, on_select=None, highlighted=None):
    wrap = BoxLayout(orientation="vertical", spacing=dp(6), size_hint=(1, None), height=dp(150))
    cells = {}
    for row_name, spots in (("FILA A", spots_row_a), ("FILA B", spots_row_b)):
        row_wrap = BoxLayout(orientation="vertical", spacing=dp(4), size_hint=(1, None), height=dp(68))
        row_wrap.add_widget(Label(text=row_name, color=COLOR_TEXT_MUTED, font_size="10sp",
                                   bold=True, size_hint=(1, None), height=dp(14), halign="left"))
        grid = GridLayout(cols=len(spots), spacing=dp(4), size_hint=(1, None), height=dp(48))
        for s in spots:
            cell = ParkingSpotCell(s, on_select=on_select)
            if highlighted and s == highlighted:
                cell.set_selected(True)
            cells[s] = cell
            grid.add_widget(cell)
        row_wrap.add_widget(grid)
        wrap.add_widget(row_wrap)
    wrap.cells = cells
    return wrap
 
 
def facilities_row():
    row = BoxLayout(size_hint=(1, None), height=dp(34), spacing=dp(8))
    for label in ("Escalera B", "Elevador 2", "Escalera A"):
        chip = RoundedBox(bg_color=COLOR_CARD, radius=[dp(16)], padding=(dp(10), dp(4)), spacing=dp(6))
        icon_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(None, 1), width=dp(18))
        icon_wrap.add_widget(CrosshairIcon(size_hint=(None, None), size=(dp(16), dp(16)), color_rgba=COLOR_TEXT))
        chip.add_widget(icon_wrap)
        chip.add_widget(Label(text=label, color=COLOR_TEXT_MUTED, font_size="10sp"))
        row.add_widget(chip)
    return row
 
 
# ----------------------------------------------------------------------
# 4. MAPA - ESTADO VACÍO
# ----------------------------------------------------------------------
class EmptyMapScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        root.add_widget(status_bar())
 
        body = BoxLayout(orientation="vertical", padding=(dp(20), dp(10)), spacing=dp(12))
 
        header = BoxLayout(size_hint=(1, None), height=dp(30))
        title_lbl = Label(text="Nivel -1", color=COLOR_TEXT, font_size="20sp", bold=True,
                           halign="left", valign="middle", size_hint=(0.8, 1))
        title_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        header.add_widget(title_lbl)
        compass_wrap = AnchorLayout(anchor_x="right", anchor_y="center", size_hint=(0.2, 1))
        compass_bg = RoundedBox(bg_color=COLOR_CARD, radius=[dp(15)], size_hint=(None, None),
                                 size=(dp(30), dp(30)))
        compass_inner = AnchorLayout(anchor_x="center", anchor_y="center")
        compass_inner.add_widget(CompassIcon(size_hint=(None, None), size=(dp(18), dp(18)), color_rgba=COLOR_GOLD))
        compass_bg.add_widget(compass_inner)
        compass_wrap.add_widget(compass_bg)
        header.add_widget(compass_wrap)
        body.add_widget(header)
        subtitle_lbl = Label(text="Estacionamiento Subterráneo", color=COLOR_TEXT_MUTED,
                              font_size="11sp", halign="left", valign="middle",
                              size_hint=(1, None), height=dp(16))
        subtitle_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        body.add_widget(subtitle_lbl)
 
        dropdown = RoundedBox(bg_color=COLOR_CARD, radius=[dp(10)], size_hint=(1, None), height=dp(36),
                               padding=(dp(12), 0))
        dropdown.add_widget(Label(text="RAMPA DE ACCESO VEHICULAR", color=COLOR_TEXT,
                                   font_size="11sp", bold=True, halign="left"))
        chevron_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(None, 1), width=dp(20))
        chevron_wrap.add_widget(ChevronDownIcon(size_hint=(None, None), size=(dp(12), dp(12)), color_rgba=COLOR_GOLD))
        dropdown.add_widget(chevron_wrap)
        body.add_widget(dropdown)
 
        self.grid = build_spot_grid(
            ["A40", "A41", "A42", "A43", "A44"],
            ["B45", "B46", "B47", "B48", "B49"],
        )
        body.add_widget(self.grid)
 
        body.add_widget(facilities_row())
        body.add_widget(BoxLayout(size_hint=(1, 1)))
 
        prompt = Label(text="\u00BFD\u00F3nde te estacionaste?", color=COLOR_TEXT, font_size="15sp",
                        bold=True, size_hint=(1, None), height=dp(22))
        body.add_widget(prompt)
        sub = Label(text="Guarda tu cajón para no perder tu auto", color=COLOR_TEXT_MUTED,
                     font_size="11sp", size_hint=(1, None), height=dp(16))
        body.add_widget(sub)
 
        btn = RoundedButton(text="+  Guardar mi cajón", size_hint=(1, None), height=dp(50))
        btn.bind(on_release=lambda i: self.goto_selection())
        body.add_widget(btn)
 
        root.add_widget(body)
        self.add_widget(root)
 
    def goto_selection(self):
        self.manager.transition = SlideTransition(direction="up")
        self.manager.current = "selection"
 
 
# ----------------------------------------------------------------------
# 5. SELECCIÓN DE CAJÓN (teclado numérico)
# ----------------------------------------------------------------------
class SpotSelectionScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entered = ""
        root = BoxLayout(orientation="vertical")
        root.add_widget(status_bar())
 
        body = BoxLayout(orientation="vertical", padding=(dp(20), dp(10)), spacing=dp(14))
 
        header = BoxLayout(size_hint=(1, None), height=dp(30))
        header_title = Label(text="Nivel -1", color=COLOR_TEXT, font_size="20sp", bold=True,
                              halign="left", valign="middle", size_hint=(1, 1))
        header_title.bind(size=lambda i, v: setattr(i, "text_size", v))
        header.add_widget(header_title)
        body.add_widget(header)
 
        # Mini mapa de fondo (deshabilitado visualmente)
        self.mini_grid = build_spot_grid(
            ["A40", "A41", "A42", "A43", "A44"],
            ["B45", "B46", "B47", "B48", "B49"],
        )
        body.add_widget(self.mini_grid)
 
        panel = RoundedBox(orientation="vertical", bg_color=COLOR_CARD, radius=[dp(18), dp(18), 0, 0],
                            padding=dp(20), spacing=dp(14), size_hint=(1, 1))
        panel.add_widget(Label(text="INGRESA TU CAJÓN", color=COLOR_TEXT_MUTED, font_size="11sp",
                                bold=True, size_hint=(1, None), height=dp(18)))
 
        self.display_lbl = Label(text="___", color=COLOR_GOLD, font_size="34sp", bold=True,
                                  size_hint=(1, None), height=dp(50))
        panel.add_widget(self.display_lbl)
 
        hint = Label(text="Verifica el número pintado en el piso o cuéntalo junto a tu columna.",
                     color=COLOR_TEXT_MUTED, font_size="10sp", halign="center",
                     size_hint=(1, None), height=dp(26))
        hint.bind(size=lambda i, v: setattr(i, "text_size", v))
        panel.add_widget(hint)
 
        keypad = GridLayout(cols=3, spacing=dp(8), size_hint=(1, None), height=dp(170))
        keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "Borrar", "0", "Aceptar"]
        for k in keys:
            b = RoundedButton(text=k, bg_color=COLOR_CARD_LIGHT, text_color=COLOR_TEXT,
                               font_size="16sp", bold=(k in ("Borrar", "Aceptar")))
            b.bind(on_release=self._make_key_handler(k))
            keypad.add_widget(b)
        panel.add_widget(keypad)
        body.add_widget(panel)
 
        self.confirm_btn = RoundedButton(text="Confirmar cajón", size_hint=(1, None), height=dp(50))
        self.confirm_btn.bind(on_release=lambda i: self.confirm())
        body.add_widget(self.confirm_btn)
 
        root.add_widget(body)
        self.add_widget(root)
 
    def _make_key_handler(self, key):
        def handler(instance):
            if key == "Borrar":
                self.entered = self.entered[:-1]
            elif key == "Aceptar":
                self.confirm()
                return
            elif len(self.entered) < 3:
                self.entered += key
            display = self.entered.ljust(3, "_")
            self.display_lbl.text = display
        return handler
 
    def confirm(self):
        if len(self.entered) == 3:
            app = App.get_running_app()
            app.saved_spot = self.entered
            self.entered = ""
            self.display_lbl.text = "___"
            self.manager.get_screen("saved").refresh(app.saved_spot)
            self.manager.transition = FadeTransition()
            self.manager.current = "saved"
 
 
# ----------------------------------------------------------------------
# 6. MAPA - CAJÓN GUARDADO CON ÉXITO
# ----------------------------------------------------------------------
class SavedSpotScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spot_number = "047"
        self.root_body = BoxLayout(orientation="vertical")
        self.add_widget(self.root_body)
        self._build()
 
    def _build(self):
        self.root_body.clear_widgets()
        self.root_body.add_widget(status_bar())
 
        body = BoxLayout(orientation="vertical", padding=(dp(20), dp(10)), spacing=dp(10))
 
        header = BoxLayout(orientation="vertical", size_hint=(1, None), height=dp(46))
        top = BoxLayout(size_hint=(1, None), height=dp(28))
        top_title = Label(text="Nivel -1", color=COLOR_TEXT, font_size="20sp", bold=True,
                           halign="left", valign="middle", size_hint=(0.8, 1))
        top_title.bind(size=lambda i, v: setattr(i, "text_size", v))
        top.add_widget(top_title)
        compass_wrap = AnchorLayout(anchor_x="right", anchor_y="center", size_hint=(0.2, 1))
        compass_bg = RoundedBox(bg_color=COLOR_CARD, radius=[dp(15)], size_hint=(None, None),
                                 size=(dp(30), dp(30)))
        compass_inner = AnchorLayout(anchor_x="center", anchor_y="center")
        compass_inner.add_widget(CompassIcon(size_hint=(None, None), size=(dp(18), dp(18)), color_rgba=COLOR_GOLD))
        compass_bg.add_widget(compass_inner)
        compass_wrap.add_widget(compass_bg)
        top.add_widget(compass_wrap)
        header.add_widget(top)
        success = BoxLayout(size_hint=(1, None), height=dp(18), spacing=dp(4))
        success.add_widget(CheckIcon(size_hint=(None, 1), width=dp(16), color_rgba=COLOR_GREEN))
        success.add_widget(Label(text="Cajón Guardado Con Éxito", color=COLOR_GREEN, font_size="11sp",
                                  bold=True, halign="left"))
        header.add_widget(success)
        body.add_widget(header)
 
        self.grid = build_spot_grid(
            ["A40", "A41", "A42", "A43", "A44"],
            ["B45", "B46", "B47", "B48", "B49"],
            highlighted="B" + self.spot_number[-2:] if False else None,
        )
        body.add_widget(self.grid)
        # Resaltar la celda correspondiente
        target_id = None
        for sid in self.grid.cells:
            if self.spot_number[-2:] in sid:
                target_id = sid
                break
        if target_id:
            self.grid.cells[target_id].set_selected(True)
 
        body.add_widget(facilities_row())
 
        info = RoundedBox(orientation="vertical", bg_color=COLOR_CARD, radius=[dp(14)],
                           padding=dp(14), spacing=dp(8), size_hint=(1, None), height=dp(150))
        info.add_widget(Label(text="UBICACIÓN DE TU AUTO", color=COLOR_TEXT_MUTED, font_size="10sp",
                               bold=True, size_hint=(1, None), height=dp(16), halign="left"))
        row = BoxLayout(size_hint=(1, None), height=dp(40))
        self.spot_lbl = Label(text=f"Cajón {self.spot_number}", color=COLOR_TEXT, font_size="18sp",
                               bold=True, halign="left", size_hint=(0.7, 1))
        row.add_widget(self.spot_lbl)
        pin = RoundedBox(bg_color=COLOR_GOLD_DARK, border_color=COLOR_GOLD, border_width=[dp(1.5)],
                          radius=[dp(8)], size_hint=(None, None), size=(dp(34), dp(34)))
        pin_dot_wrap = AnchorLayout(anchor_x="center", anchor_y="center")
        pin_dot_wrap.add_widget(CarIcon(size_hint=(None, None), size=(dp(20), dp(20)), color_rgba=COLOR_GOLD))
        pin.add_widget(pin_dot_wrap)
        row.add_widget(pin)
        info.add_widget(row)
        info.add_widget(Label(text="Cerca de Escalera B, Elevador 2", color=COLOR_TEXT_MUTED,
                               font_size="10sp", halign="left", size_hint=(1, None), height=dp(16)))
 
        actions = BoxLayout(size_hint=(1, None), height=dp(42), spacing=dp(10))
        delete_btn = RoundedButton(text="Borrar registro", bg_color=(0.20, 0.09, 0.09, 1),
                                    text_color=COLOR_RED, font_size="12sp")
        delete_btn.bind(on_release=lambda i: self.goto_delete_confirm())
        map_btn = RoundedButton(text="Ver Mapa", bg_color=COLOR_CARD_LIGHT,
                                 text_color=COLOR_TEXT, font_size="12sp")
        map_btn.bind(on_release=lambda i: None)  # ya estamos en el mapa
        actions.add_widget(delete_btn)
        actions.add_widget(map_btn)
        info.add_widget(actions)
 
        body.add_widget(info)
        body.add_widget(BoxLayout(size_hint=(1, 1)))
 
        self.root_body.add_widget(body)
 
    def refresh(self, spot_number):
        self.spot_number = spot_number
        self._build()
 
    def goto_delete_confirm(self):
        self.manager.get_screen("delete_confirm").set_spot(self.spot_number)
        self.manager.transition = FadeTransition()
        self.manager.current = "delete_confirm"
 
 
# ----------------------------------------------------------------------
# 7. CONFIRMACIÓN DE BORRADO (modal sobre el mapa)
# ----------------------------------------------------------------------
class DeleteConfirmScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spot_number = "047"
        self.overlay = FloatLayout()
        self.add_widget(self.overlay)
 
        # fondo oscuro semitransparente
        with self.overlay.canvas.before:
            Color(0.02, 0.03, 0.05, 0.85)
            self._bg_rect = Rectangle(pos=self.overlay.pos, size=self.overlay.size)
        self.overlay.bind(pos=self._update_bg, size=self._update_bg)
 
        self.dialog = RoundedBox(orientation="vertical", bg_color=COLOR_CARD, radius=[dp(18)],
                                  padding=dp(22), spacing=dp(14),
                                  size_hint=(0.85, None), height=dp(220),
                                  pos_hint={"center_x": 0.5, "center_y": 0.5})
 
        icon_wrap = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, None), height=dp(46))
        icon_bg = RoundedBox(bg_color=(0.25, 0.08, 0.08, 1), radius=[dp(23)], size_hint=(None, None),
                              size=(dp(46), dp(46)))
        icon_inner = AnchorLayout(anchor_x="center", anchor_y="center")
        icon_inner.add_widget(WarningTriangleIcon(size_hint=(None, None), size=(dp(24), dp(24)),
                                                    color_rgba=COLOR_RED))
        icon_bg.add_widget(icon_inner)
        icon_wrap.add_widget(icon_bg)
        self.dialog.add_widget(icon_wrap)
 
        self.question_lbl = Label(
            text="¿Seguro que quieres borrar el registro\ndel cajón 047?",
            color=COLOR_TEXT, font_size="14sp", bold=True, halign="center",
            size_hint=(1, None), height=dp(44)
        )
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
 
    def _update_bg(self, *args):
        self._bg_rect.pos = self.overlay.pos
        self._bg_rect.size = self.overlay.size
 
    def set_spot(self, spot_number):
        self.spot_number = spot_number
        self.question_lbl.text = f"¿Seguro que quieres borrar el registro\ndel cajón {spot_number}?"
 
    def confirm_delete(self):
        app = App.get_running_app()
        app.saved_spot = None
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
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(HelpScreen(name="help"))
        sm.add_widget(MapDownloadScreen(name="download"))
        sm.add_widget(EmptyMapScreen(name="empty_map"))
        sm.add_widget(SpotSelectionScreen(name="selection"))
        sm.add_widget(SavedSpotScreen(name="saved"))
        sm.add_widget(DeleteConfirmScreen(name="delete_confirm"))
        return sm
 
 
if __name__ == "__main__":
    AlzParkingApp().run()
 