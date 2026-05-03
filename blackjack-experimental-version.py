import pygame
import random as random_module
import sys
import os
import math
import threading
import urllib.request
import shutil

pygame.init()

VERSION = "0.3.0"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/humrand/blackjack-python/main/blackjack-experimental-version.py"

_IMAGE_BASE = "https://raw.githubusercontent.com/humrand/blackjack-python/main/imagenes/"
_IMAGE_FILES = {
    'farol-rojo':   ('farol-rojo.png',        'farol-rojo.png'),
    'rosita':       ('rosita.png',             'rosita.png'),
    'victor2':      ('victor2.png',            'victor2.png'),
    'victor3':      ('victor3.png',            'victor3.png'),
    'victor4':      ('victor4.png',            'victor4.png'),
    'victor5':      ('victor5.png',            'victor5.png'),
    'segurata-pierdes': ('segurata-pierdes.png', 'segurata-pierdes.png'),
    'rosita-seria': ('rosita-seria.png',       'rosita-seria.png'),
    'rosita-caos':  ('rosita-caos.png',        'rosita-caos.png'),
    'rosita-guino': ('rosita-gui%C3%B1o.png',  'rosita-guino.png'),
    'barcelona':    ('barcelona.png',          'barcelona.png'),
}
_image_cache = {}
_image_downloading = set()

def _ensure_imagenes_dir():
    os.makedirs('imagenes', exist_ok=True)

def _download_image_bg(key):
    """Descarga una imagen en segundo plano y la guarda en cache."""
    global _image_cache, _image_downloading
    if key in _image_cache or key not in _IMAGE_FILES:
        _image_downloading.discard(key)
        return
    url_file, local_file = _IMAGE_FILES[key]
    _ensure_imagenes_dir()
    local_path = os.path.join('imagenes', local_file)
    if not os.path.exists(local_path):
        try:
            url = _IMAGE_BASE + url_file
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            with open(local_path, 'wb') as f:
                f.write(data)
        except Exception as e:
            print(f"[IMG] Error descargando {key}: {e}")
            _image_cache[key] = None
            _image_downloading.discard(key)
            return
    try:
        img = pygame.image.load(local_path).convert_alpha()
        _image_cache[key] = img
    except Exception as e:
        print(f"[IMG] Error cargando {key}: {e}")
        _image_cache[key] = None
    _image_downloading.discard(key)

def get_story_image(key):
    """Devuelve la surface de la imagen (o None). Lanza descarga si falta."""
    if key is None:
        return None
    if key in _image_cache:
        return _image_cache[key]
    if key not in _image_downloading:
        _image_downloading.add(key)
        t = threading.Thread(target=_download_image_bg, args=(key,), daemon=True)
        t.start()
    return None  

def preload_images(*keys):
    for k in keys:
        get_story_image(k)

def draw_story_image(key, surf):
    """Dibuja la imagen de escena a pantalla completa."""
    img = get_story_image(key)
    if img is None:
        return
    iw, ih = img.get_size()
    scale  = max(ANCHO / iw, ALTO / ih)
    new_w  = int(iw * scale)
    new_h  = int(ih * scale)
    scaled = pygame.transform.smoothscale(img, (new_w, new_h))
    x = (ANCHO - new_w) // 2
    y = (ALTO  - new_h) // 2
    surf.blit(scaled, (x, y))


ANCHO, ALTO = 1920, 960

_dinfo = pygame.display.Info()
SCREEN_W = _dinfo.current_w
SCREEN_H = _dinfo.current_h
VENTANA_REAL = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
pygame.display.set_caption("Blackjack – El Farol Rojo")

VENTANA = pygame.Surface((ANCHO, ALTO))


def to_logical(pos):
    sx, sy = pos
    return (int(sx * ANCHO / SCREEN_W), int(sy * ALTO / SCREEN_H))


def flip_display():
    scaled = pygame.transform.scale(VENTANA, (SCREEN_W, SCREEN_H))
    VENTANA_REAL.blit(scaled, (0, 0))
    pygame.display.flip()


FUENTE         = pygame.font.SysFont("arial",  32, bold=True)
FUENTE_PEQUENA = pygame.font.SysFont("arial",  24, bold=True)
FUENTE_GRANDE  = pygame.font.SysFont("arial",  70, bold=True)
FUENTE_MSG     = pygame.font.SysFont("arial",  40, bold=True)
FUENTE_INSTR   = pygame.font.SysFont("arial",  20, bold=True)
FUENTE_STORY   = pygame.font.SysFont("arial",  28)
FUENTE_NAME    = pygame.font.SysFont("arial",  34, bold=True)
FUENTE_TITLE_B = pygame.font.SysFont("arial", 115, bold=True)
FUENTE_SUBTITLE= pygame.font.SysFont("arial",  52)
RELOJ          = pygame.time.Clock()

VERDE        = (20, 120, 20)
VERDE_OSCURO = (12,  80, 12)
BLANCO       = (255, 255, 255)
NEGRO        = (0,   0,   0)
ROJO         = (200, 0,   0)
DORADO       = (230, 190, 60)
STRONG_GREEN = (0,  150,  0)

CARD_W        = 96
CARD_H        = 144
CARD_SPACING  = 125
HAND_SEP      = 300
PEDIR_DELAY   = 500
ROUND_DELAY   = 2000
BET_MAX       = 50000
SUIT_CHAR     = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
DECK_POS      = (ANCHO // 2, 20)
DEALER_POS    = (ANCHO // 2, 60)
PLAYER_STACK_POS = (120, ALTO - 70)
BANK_POS      = (ANCHO // 2, 40)
EPIC_WIN_THRESHOLD = 10000
DEALER_SETTLE_DELAY = 900

difficulty_level   = 0
rosa_secret_done   = False

def get_symbol_font(size):
    candidates = ["Symbola","DejaVuSans","DejaVu Sans","FreeSerif",
                  "Segoe UI Symbol","Arial Unicode MS","Noto Sans Symbols2","Noto Sans Symbols"]
    local_paths = [os.path.join("fonts","Symbola.ttf"),
                   os.path.join("fonts","DejaVuSans.ttf"),
                   os.path.join("fonts","DejaVuSans-Oblique.ttf")]
    for p in local_paths:
        if os.path.exists(p):
            try:    return pygame.font.Font(p, size)
            except: pass
    for name in candidates:
        try:
            path = pygame.font.match_font(name)
            if path:
                try:    return pygame.font.Font(path, size)
                except: pass
        except: pass
    return pygame.font.SysFont("arial", size, bold=True)

SYMBOL_FONT    = get_symbol_font(56)
FACE_SYMBOL_MAP = {"J": '♚', "K": '♚', "Q": '♛'}

_RRNG = random_module.Random(7331)
_RAIN = [(_RRNG.randint(0, ANCHO), _RRNG.randint(0, ALTO),
          _RRNG.uniform(200, 460), _RRNG.randint(12, 34))
         for _ in range(140)]


def draw_rain(surf, now, alpha=100):
    t = now / 1000.0
    for bx, by, sp, ln in _RAIN:
        y = (by + t * sp) % (ALTO + 60)
        x = int(bx + y * 0.17) % ANCHO
        s = pygame.Surface((2, ln), pygame.SRCALPHA)
        s.fill((160, 195, 235, alpha))
        surf.blit(s, (x, int(y)))


class Carta:
    def __init__(self, valor, palo, valor_num, color, dest_x, dest_y, start_pos=None):
        self.valor = valor; self.palo = palo
        self.valor_num = valor_num; self.color = color
        if start_pos:
            self.x, self.y = float(start_pos[0]), float(start_pos[1])
        else:
            self.x, self.y = float(DECK_POS[0]), float(DECK_POS[1])
        self.dest_x = float(dest_x); self.dest_y = float(dest_y)
        self.w = CARD_W; self.h = CARD_H
        self.oculta = False; self.flipping = False
        self.flip_start = 0; self.flip_duration = 300
        self.front = None; self.back = None; self.flip_target_back = False
        self.scale = 1.0; self.target_scale = 1.0; self.scale_speed = 0.22
        self.hover_glow = 0.0 
        self._create_faces()

    def _create_faces(self):
        self.front = self.crear_front()
        self.back  = self.crear_back()

    def crear_front(self):
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(surf, BLANCO, (0,0,self.w,self.h), border_radius=12)
        pygame.draw.rect(surf, NEGRO,  (0,0,self.w,self.h), 2, border_radius=12)
        idx = FUENTE_PEQUENA.render(self.valor, True, self.color)
        surf.blit(idx, (8, 6))
        idx_rot = pygame.transform.rotate(idx, 180)
        surf.blit(idx_rot, (self.w - idx_rot.get_width()-8, self.h - idx_rot.get_height()-6))
        try:
            if self.valor in FACE_SYMBOL_MAP:
                sym_surf = SYMBOL_FONT.render(FACE_SYMBOL_MAP[self.valor], True, self.color)
            else:
                sym_surf = SYMBOL_FONT.render(SUIT_CHAR.get(self.palo,'?'), True, self.color)
            surf.blit(sym_surf, ((self.w-sym_surf.get_width())//2, (self.h-sym_surf.get_height())//2-6))
        except Exception:
            simple = FUENTE_GRANDE.render(self.valor, True, self.color) if self.valor in FACE_SYMBOL_MAP \
                     else FUENTE_PEQUENA.render(self.palo, True, self.color)
            surf.blit(simple, ((self.w-simple.get_width())//2, (self.h-simple.get_height())//2))
        return surf

    def crear_back(self):
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (150,0,0), (0,0,self.w,self.h), border_radius=12)
        pygame.draw.rect(surf, NEGRO,     (0,0,self.w,self.h), 2, border_radius=12)
        for i in range(12, self.w-12, 20):
            for j in range(12, self.h-12, 24):
                pygame.draw.circle(surf, (220,70,70), (i,j), 5)
        return surf

    def start_flip(self, now, to_back=False):
        if not self.flipping:
            self.flipping = True; self.flip_start = now
            self.flip_target_back = bool(to_back)

    def actualizar(self, now):
        dx = self.dest_x - self.x; dy = self.dest_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0.5:
            speed = min(0.22 + dist * 0.003, 0.55)
            self.x += dx * speed; self.y += dy * speed
        else:
            self.x = self.dest_x; self.y = self.dest_y
        if abs(self.scale - self.target_scale) > 0.001:
            self.scale += (self.target_scale - self.scale) * self.scale_speed
        else:
            self.scale = self.target_scale
        target_glow = 1.0 if self.target_scale > 1.01 else 0.0
        self.hover_glow += (target_glow - self.hover_glow) * 0.25

    def dibujar(self, now):
        rx, ry = int(self.x), int(self.y)
        if not self.flipping:
            surf_to_blit = self.back if self.oculta else self.front
            nw = max(1, int(self.w * self.scale)); nh = max(1, int(self.h * self.scale))
            scaled = pygame.transform.smoothscale(surf_to_blit, (nw, nh))
            bx = rx-(nw-self.w)//2; by = ry-(nh-self.h)//2
            if self.hover_glow > 0.02:
                alpha = int(self.hover_glow * 180)
                glow_w = nw + 8; glow_h = nh + 8
                glow_surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*DORADO, alpha), (0,0,glow_w,glow_h), border_radius=14)
                VENTANA.blit(glow_surf, (bx-4, by-4))
            VENTANA.blit(scaled, (bx, by))
            return
        progreso = (now - self.flip_start) / self.flip_duration
        if progreso >= 1:
            self.flipping = False; self.oculta = bool(self.flip_target_back)
            surf_to_blit = self.back if self.oculta else self.front
            nw = max(1, int(self.w*self.scale)); nh = max(1, int(self.h*self.scale))
            scaled = pygame.transform.smoothscale(surf_to_blit, (nw, nh))
            VENTANA.blit(scaled, (rx-(nw-self.w)//2, ry-(nh-self.h)//2)); return
        if self.flip_target_back:
            escala = (1-progreso*2) if progreso < 0.5 else ((progreso-0.5)*2)
            surf = self.front if progreso < 0.5 else self.back
        else:
            escala = (1-progreso*2) if progreso < 0.5 else ((progreso-0.5)*2)
            surf = self.back if progreso < 0.5 else self.front
        ancho = max(1, int(self.w*escala)); h_final = max(1, int(self.h*self.scale))
        scaled = pygame.transform.smoothscale(surf, (ancho, h_final))
        x_blit = rx + (self.w-ancho)//2 - ((int(self.w*self.scale)-self.w)//2)
        VENTANA.blit(scaled, (x_blit, ry-(h_final-self.h)//2))


def get_chip_style(value):
    v = int(value)
    if   1 <= v <= 10:  return {'shape':'circle','r':14,'color':(180,30,30)}
    if  11 <= v <= 34:  return {'shape':'circle','r':18,'color':(220,120,20)}
    if  35 <= v <= 64:  return {'shape':'circle','r':22,'color':(20,160,80)}
    if  65 <= v <= 99:  return {'shape':'circle','r':26,'color':(30,120,220)}
    if 100 <= v <= 199: return {'shape':'rect','w':48,'h':28,'color':(20,150,80)}
    if 200 <= v <= 250: return {'shape':'rect','w':56,'h':32,'color':(220,100,160)}
    return {'shape':'circle','r':20,'color':(200,150,60)}

def create_placed_chip(value, x, y):
    style = get_chip_style(value)
    base = {'x':float(x),'y':float(y),'value':int(value),
            'moving':False,'vx':0.0,'vy':0.0,'target_x':x,'target_y':y}
    base.update(style); return base

def make_chip_move_dict(value, sx, sy, tx, ty, speed=6.0):
    dx=tx-sx; dy=ty-sy; dist=math.hypot(dx,dy)
    vx = (dx/dist*speed) if dist else 0.0
    vy = (dy/dist*speed) if dist else 0.0
    style = get_chip_style(value)
    d = {'x':float(sx),'y':float(sy),'vx':vx,'vy':vy,'target_x':tx,'target_y':ty,'value':int(value),'moving':True}
    d.update(style); return d

def _chip_font_for_circle(r):
    return pygame.font.SysFont("arial", max(10,int(r*0.7)), bold=True)

def _chip_font_for_rect(h):
    return pygame.font.SysFont("arial", max(12,int(h*0.6)), bold=True)


TABLE_STYLES = [
    {'name':'verde clásico','color':VERDE},
    {'name':'rojo casino',  'color':(100,20,20)},
    {'name':'negro lujo',   'color':(20,20,20)},
]
TABLE_STYLE_IDX = 0

DEALER_AVATAR = None
if os.path.exists(os.path.join("images","dealer.png")):
    try:
        img = pygame.image.load(os.path.join("images","dealer.png")).convert_alpha()
        DEALER_AVATAR = pygame.transform.smoothscale(img,(120,120))
    except: pass


def draw_portero(surf, cx, fy):
    """Bruno el Portero – traje oscuro, corpulento, amenazante."""
    SC  = (28, 32, 48); SK  = (175, 125, 80)
    SH  = (12,  12, 18); TIE = (170, 20,  25)
    pygame.draw.ellipse(surf, SH, (cx-56, fy-18, 46, 20))
    pygame.draw.ellipse(surf, SH, (cx+10, fy-18, 46, 20))
    pygame.draw.rect(surf, SC, (cx-54, fy-158, 40, 143), border_radius=6)
    pygame.draw.rect(surf, SC, (cx+14, fy-158, 40, 143), border_radius=6)
    pygame.draw.rect(surf, SC, (cx-72, fy-305, 144, 152), border_radius=10)
    pygame.draw.polygon(surf, (225,225,225), [(cx-9,fy-305),(cx+9,fy-305),(cx+4,fy-245),(cx-4,fy-245)])
    pygame.draw.polygon(surf, TIE, [(cx-7,fy-298),(cx+7,fy-298),(cx+3,fy-255),(cx-3,fy-255)])
    pygame.draw.rect(surf, SC, (cx-108, fy-288, 40, 115), border_radius=8)
    pygame.draw.circle(surf, SK, (cx-88, fy-170), 18)
    pygame.draw.rect(surf, SC, (cx+68,  fy-288, 40, 115), border_radius=8)
    pygame.draw.circle(surf, SK, (cx+88, fy-170), 18)
    pygame.draw.rect(surf, SK, (cx-15, fy-338, 30, 36))
    pygame.draw.circle(surf, SK, (cx, fy-360), 44)
    pygame.draw.ellipse(surf, (30,20,15), (cx-44, fy-407, 88, 50))
    pygame.draw.rect(surf, (40,30,20), (cx-27, fy-373, 20, 10), border_radius=3)
    pygame.draw.rect(surf, (40,30,20), (cx+7,  fy-373, 20, 10), border_radius=3)
    pygame.draw.line(surf, (20,15,10), (cx-30,fy-388),(cx-8,fy-380), 4)
    pygame.draw.line(surf, (20,15,10), (cx+8, fy-388),(cx+30,fy-380), 4)
    pygame.draw.line(surf, (120,70,50),(cx-14,fy-340),(cx+14,fy-340), 3)
    pygame.draw.line(surf, (140,80,60),(cx+18,fy-360),(cx+22,fy-345), 2)


def draw_camarera(surf, cx, fy):
    """Rosa la Camarera – parte superior visible sobre la barra."""
    DC = (145, 48, 72); SK = (215, 175, 130)
    AP = (238, 232, 215); HR = (75,  38, 18)
    pygame.draw.rect(surf, DC, (cx-44, fy-285, 88, 140), border_radius=8)
    pygame.draw.rect(surf, AP, (cx-30, fy-275, 60, 115), border_radius=5)
    pygame.draw.rect(surf, DC, (cx-86, fy-272, 44, 90), border_radius=7)
    pygame.draw.circle(surf, SK, (cx-64, fy-178), 15)
    pygame.draw.rect(surf, (130,190,220), (cx-76, fy-240, 24, 48), border_radius=4)
    pygame.draw.rect(surf, (80,130,160),  (cx-76, fy-240, 24, 48), 2, border_radius=4)
    pygame.draw.rect(surf, (180,220,240,120), (cx-74, fy-238, 12, 10))
    pygame.draw.rect(surf, DC, (cx+42,  fy-272, 44, 100), border_radius=7)
    pygame.draw.circle(surf, SK, (cx+64, fy-168), 15)
    pygame.draw.rect(surf, SK, (cx-13, fy-318, 26, 36))
    pygame.draw.circle(surf, SK, (cx, fy-340), 38)
    pygame.draw.circle(surf, HR, (cx, fy-340), 38)
    pygame.draw.ellipse(surf, SK, (cx-32, fy-360, 64, 50))
    pygame.draw.circle(surf, HR, (cx, fy-378), 22)
    pygame.draw.circle(surf, HR, (cx-16,fy-372), 14)
    pygame.draw.circle(surf, HR, (cx+16,fy-372), 14)
    pygame.draw.circle(surf, (60,38,25), (cx-14, fy-350), 6)
    pygame.draw.circle(surf, (60,38,25), (cx+14, fy-350), 6)
    pygame.draw.circle(surf, BLANCO, (cx-16, fy-352), 3)
    pygame.draw.circle(surf, BLANCO, (cx+12, fy-352), 3)
    pygame.draw.arc(surf, (165,80,80), (cx-16, fy-337, 32, 16), math.pi, 2*math.pi, 3)
    pygame.draw.circle(surf, DORADO, (cx-38, fy-342), 5)
    pygame.draw.circle(surf, DORADO, (cx+38, fy-342), 5)


def draw_victor(surf, cx, fy, nervous=False):
    """Víctor Carvalho – el antagonista elegante y calculador."""
    SC = (18,  14, 28); WC = (235, 235, 235)
    GC = (185, 155, 42); SK = (215, 185, 145); HC = (12, 8, 22)
    pygame.draw.ellipse(surf, (8,6,14), (cx-43, fy-22, 38, 20))
    pygame.draw.ellipse(surf, (8,6,14), (cx+5,  fy-22, 43, 20))
    pygame.draw.rect(surf, SC, (cx-42, fy-175, 30, 156), border_radius=5)
    pygame.draw.rect(surf, SC, (cx+12, fy-175, 30, 156), border_radius=5)
    pygame.draw.rect(surf, SC, (cx-52, fy-325, 104, 156), border_radius=7)
    pygame.draw.rect(surf, GC, (cx-34, fy-322, 68, 140), border_radius=5)
    pygame.draw.polygon(surf, WC, [(cx-11,fy-325),(cx+11,fy-325),(cx+5,fy-282),(cx-5,fy-282)])
    pygame.draw.polygon(surf, (175,15,15),
                        [(cx-16,fy-318),(cx,fy-308),(cx+16,fy-318),
                         (cx+16,fy-302),(cx,fy-312),(cx-16,fy-302)])
    pygame.draw.line(surf, DORADO, (cx+30,fy-300),(cx+22,fy-265), 2)
    pygame.draw.circle(surf, DORADO, (cx+22,fy-260), 6)
    pygame.draw.rect(surf, SC, (cx-82, fy-318, 30, 130), border_radius=6)
    pygame.draw.circle(surf, SK, (cx-67, fy-184), 14)
    pygame.draw.rect(surf, SC, (cx+52, fy-318, 30, 130), border_radius=6)
    pygame.draw.circle(surf, SK, (cx+67, fy-184), 14)
    pygame.draw.rect(surf, SK, (cx-12, fy-358, 24, 36))
    pygame.draw.ellipse(surf, SK, (cx-36, fy-415, 72, 62))
    pygame.draw.ellipse(surf, HC, (cx-36, fy-415, 72, 36))
    ey = fy - 394
    pygame.draw.rect(surf, (28,22,38), (cx-26, ey, 20, 9), border_radius=2)
    pygame.draw.rect(surf, (28,22,38), (cx+6,  ey, 20, 9), border_radius=2)
    pygame.draw.line(surf, HC, (cx-28,ey-13),(cx-8,ey-6),  3)
    pygame.draw.line(surf, HC, (cx+8, ey-11),(cx+28,ey-6), 3)
    pygame.draw.arc(surf, (145,75,65), (cx-4, fy-377, 30, 18), math.pi+0.4, 2*math.pi-0.1, 3)
    bw = 96; tw = 54; hh = 48; hy = fy - 416
    pygame.draw.rect(surf, HC, (cx-tw//2, hy-hh, tw, hh), border_radius=5)
    pygame.draw.rect(surf, HC, (cx-bw//2, hy-6,  bw,  8))
    pygame.draw.rect(surf, GC, (cx-tw//2, hy-10, tw,  8))
    if nervous:
        for sx2, sy2 in [(cx+34,fy-410),(cx+44,fy-395)]:
            pygame.draw.polygon(surf, (120,185,225),
                                [(sx2,sy2-14),(sx2+6,sy2),(sx2-6,sy2)])


def draw_bg_title(surf, now):
    surf.fill((4, 2, 8))
    t = now / 1000.0
    flicker = 0.82 + 0.18 * math.sin(t * 3.1) * math.sin(t * 7.3)
    cx, cy = ANCHO // 2, ALTO // 2 - 90
    for r in range(260, 0, -18):
        a = max(0, int(22 * (1 - r/260) * flicker))
        gs = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (210, 55, 25, a), (r, r), r)
        surf.blit(gs, (cx-r, cy-r))
    title_col = (int(235*flicker), int(70*flicker), int(22*flicker))
    title_surf = FUENTE_TITLE_B.render("EL FAROL ROJO", True, title_col)
    surf.blit(title_surf, (cx - title_surf.get_width()//2, cy - title_surf.get_height()//2))
    sub = FUENTE_SUBTITLE.render("Barcelona  ·  1987", True, (180, 148, 90))
    surf.blit(sub, (cx - sub.get_width()//2, cy + title_surf.get_height()//2 + 28))
    lw = title_surf.get_width() + 60
    pygame.draw.line(surf,
        (int(DORADO[0]*flicker), int(DORADO[1]*flicker), int(DORADO[2]*flicker)),
        (cx-lw//2, cy + title_surf.get_height()//2 + 20),
        (cx+lw//2, cy + title_surf.get_height()//2 + 20), 2)
    draw_rain(surf, now, alpha=80)
    grad = pygame.Surface((ANCHO, 220), pygame.SRCALPHA)
    for i in range(220):
        grad.fill((0,0,0, int(200*(i/220))), (0,i,ANCHO,1))
    surf.blit(grad, (0, ALTO-220))


def draw_bg_street(surf, now):
    surf.fill((6, 9, 20))
    t = now / 1000.0
    pygame.draw.rect(surf, (18, 20, 30), (0, 0, 580, ALTO))
    _WIN_ON  = (200, 178, 95); _WIN_OFF = (22, 24, 36)
    for wx, wy in [(70,110),(190,110),(310,110),(70,250),(190,250),(310,250),(70,390),(190,390)]:
        wc = _WIN_ON if (wx+wy) % 5 != 0 else _WIN_OFF
        pygame.draw.rect(surf, wc, (wx, wy, 50, 65), border_radius=4)
        pygame.draw.rect(surf, (28,30,42), (wx, wy, 50, 65), 2, border_radius=4)
    pygame.draw.rect(surf, (15, 17, 26), (1340, 0, ANCHO-1340, ALTO))
    for wx, wy in [(1380,90),(1520,90),(1660,90),(1800,90),(1380,225),(1520,225),(1660,225),(1800,270)]:
        wc = _WIN_ON if (wx+wy) % 5 != 1 else _WIN_OFF
        pygame.draw.rect(surf, wc, (wx, wy, 50, 65), border_radius=4)
        pygame.draw.rect(surf, (28,30,42), (wx, wy, 50, 65), 2, border_radius=4)
    pygame.draw.rect(surf, (20, 23, 34), (0, 680, ANCHO, ALTO-680))
    for i in range(0, ANCHO, 88):
        pygame.draw.line(surf, (26, 29, 42), (i,680),(i,ALTO), 1)
    for j in range(680, ALTO, 44):
        pygame.draw.line(surf, (24, 27, 38), (0,j),(ANCHO,j), 1)
    ref = pygame.Surface((340, 180), pygame.SRCALPHA)
    for ry in range(180):
        a = max(0, int(38*(1-ry/180)*abs(math.sin(t+ry*0.08))))
        ref.fill((220,155,55,a),(0,ry,340,1))
    surf.blit(ref, (740, 680))
    dx, dy, dw, dh = 740, 310, 340, 395
    glow = pygame.Surface((500, 600), pygame.SRCALPHA)
    for r in range(240, 0, -14):
        a = max(0, int(35*(1-r/240)))
        pygame.draw.ellipse(glow, (225,155,55,a),(240-r,280-r,r*2,r*2))
    surf.blit(glow, (dx+dw//2-250, dy+dh//2-280))
    pygame.draw.rect(surf, (175, 115, 38), (dx, dy, dw, dh))
    pygame.draw.rect(surf, (60, 38, 16), (dx-18, dy-12, dw+36, dh+12), 18, border_radius=6)
    pygame.draw.rect(surf, (88, 55, 22), (dx-8, dy-5, dw+16, dh+5), 4, border_radius=4)
    lx2, ly2 = dx+dw//2, dy-48
    pygame.draw.rect(surf, (38,28,12), (lx2-9, ly2-55, 18, 56))
    pygame.draw.rect(surf, (58,48,18), (lx2-22, ly2-78, 44, 50), border_radius=7)
    pygame.draw.rect(surf, (88,68,28), (lx2-22, ly2-78, 44, 50), 3, border_radius=7)
    fa = int(100 + 28*math.sin(t*2.5))
    fg = pygame.Surface((90, 90), pygame.SRCALPHA)
    pygame.draw.circle(fg, (255,205,85,fa),(45,45),45)
    surf.blit(fg, (lx2-45, ly2-100))
    sf = 0.75 + 0.25*math.sin(t*2.8)
    sc2 = (int(228*sf), int(48*sf), int(18*sf))
    sign_s = FUENTE_PEQUENA.render("★  EL FAROL ROJO  ★", True, sc2)
    surf.blit(sign_s, (dx+dw//2-sign_s.get_width()//2, dy-115))
    draw_rain(surf, now, alpha=95)


def draw_bg_bar_base(surf, now):
    surf.fill((32, 19, 10))
    t = now / 1000.0
    pygame.draw.rect(surf, (48, 28, 13), (0, 780, ANCHO, 180))
    for i in range(0, ANCHO, 110):
        pygame.draw.line(surf, (38,22,10),(i,780),(i,ALTO),1)
    for j in range(780,ALTO,55):
        pygame.draw.line(surf,(36,21,9),(0,j),(ANCHO,j),1)
    pygame.draw.rect(surf, (42, 26, 13), (0, 0, ANCHO, 790))
    bcols = [(38,80,38),(85,40,18),(155,125,40),(28,58,92),
             (118,28,28),(62,82,58),(205,165,60),(28,52,80),(165,80,145)]
    for sy in [155, 290, 440]:
        pygame.draw.rect(surf, (78, 48, 22), (180, sy, 1250, 16), border_radius=3)
        for i, bx in enumerate(range(200, 1415, 75)):
            bc = bcols[i % len(bcols)]
            bh = 55 + (i % 4)*14
            pygame.draw.rect(surf, bc, (bx, sy-bh, 20, bh-8), border_radius=4)
            pygame.draw.rect(surf, bc, (bx+5, sy-bh-16, 10, 18), border_radius=2)
            hi_c = tuple(min(255,c+70) for c in bc)
            pygame.draw.line(surf, hi_c, (bx+4, sy-bh+4),(bx+4, sy-12), 2)
    for lx2 in [480, 960, 1440]:
        lamp = pygame.Surface((280, 380), pygame.SRCALPHA)
        for r in range(140, 0, -8):
            a = max(0, int(22*(1-r/140)))
            pygame.draw.ellipse(lamp, (230,182,78,a),(140-r,140-r,r*2,r*2))
        surf.blit(lamp, (lx2-140, -40))
        pygame.draw.ellipse(surf,(55,45,24),(lx2-18,  2, 36, 14))
        pygame.draw.ellipse(surf,(195,168,74),(lx2-13, 12, 26, 18))
    for i in range(5):
        sx2 = 300 + i*300; sy2 = 380+i*22
        for j in range(9):
            a2 = max(0, 38-j*4)
            sx3 = sx2 + int(14*math.sin(t+i+j*0.45))
            sy3 = int(sy2 - j*28 + 18*math.sin(t*0.65+i))
            sm = pygame.Surface((28,28), pygame.SRCALPHA)
            pygame.draw.circle(sm,(82,64,48,a2),(14,14),14)
            surf.blit(sm,(sx3,sy3))
    for sx2 in [310, 530, 750, 970, 1190]:
        pygame.draw.ellipse(surf,(72,42,20),(sx2-26, 582, 52, 18))
        pygame.draw.line(surf,(60,36,18),(sx2,600),(sx2,780), 6)
        pygame.draw.ellipse(surf,(50,30,14),(sx2-22, 775, 44, 12))


def draw_bar_counter_overlay(surf, now):
    pygame.draw.rect(surf, (105, 65, 30), (0, 597, ANCHO, 16))
    pygame.draw.rect(surf,  (82, 50, 24), (0, 613, ANCHO, 170))
    pygame.draw.rect(surf,  (60, 36, 16), (0, 779, ANCHO,   6))
    ref = pygame.Surface((ANCHO, 8), pygame.SRCALPHA)
    ref.fill((255,255,255,18))
    surf.blit(ref, (0, 598))


def draw_bg_table_scene(surf, now):
    surf.fill((7, 5, 12))
    t = now/1000.0
    cx2 = ANCHO//2
    for y in range(0, ALTO):
        sp2 = int(y * 0.52)
        a2 = max(0, int(32 * (1-y/ALTO)))
        if sp2 > 0:
            sl = pygame.Surface((sp2*2, 1), pygame.SRCALPHA)
            sl.fill((228,198,118,a2))
            surf.blit(sl, (cx2-sp2, y))
    tr = pygame.Rect(cx2-540, 380, 1080, 330)
    pygame.draw.ellipse(surf, (17, 88, 17), tr)
    pygame.draw.ellipse(surf, (11, 62, 11), tr, 4)
    pygame.draw.ellipse(surf, (8,  42,  8), tr.inflate(-38,-18), 2)
    pygame.draw.ellipse(surf, (58, 34, 14), tr.inflate(24, 12), 18)
    for lpx in [cx2-440, cx2, cx2+440]:
        pygame.draw.rect(surf, (38, 23, 11), (lpx-9, 695, 18, 130))
    sh = pygame.Surface((1200, 80), pygame.SRCALPHA)
    for sy2 in range(80):
        sh.fill((0,0,0,int(60*(1-sy2/80))),(0,sy2,1200,1))
    surf.blit(sh, (cx2-600, 700))
    for i in range(12):
        px = int(200 + i*130 + 40*math.sin(t*0.3+i))
        py = int(250 + 80*math.sin(t*0.5+i*0.7))
        pa = pygame.Surface((4,4), pygame.SRCALPHA)
        pygame.draw.circle(pa,(200,180,120,int(25+15*math.sin(t+i))),(2,2),2)
        surf.blit(pa,(px,py))


def draw_bg_street_dawn(surf, now):
    for y in range(ALTO):
        r2 = y/ALTO
        r = int(28+128*r2); g = int(12+52*r2); b = int(58-38*r2)
        pygame.draw.line(surf,(r,g,b),(0,y),(ANCHO,y))
    for bx2,by2,bw2 in [(0,185,420),(390,295,310),(660,148,260),(920,260,200),
                        (1080,230,300),(1350,175,370),(1680,290,ANCHO-1680)]:
        pygame.draw.rect(surf,(14,9,20),(bx2,by2,bw2,ALTO-by2))
    pygame.draw.rect(surf,(22,15,28),(0,688,ANCHO,ALTO-688))
    ref = pygame.Surface((ANCHO,180), pygame.SRCALPHA)
    t2  = now/1000.0
    for i in range(0,ANCHO,9):
        a2 = max(0, int(28+18*math.sin(t2+i*0.018)))
        ref.fill((192,112,56,a2),(i,0,9,180))
    surf.blit(ref,(0,688))
    for i,(sx2,sy2) in enumerate([(155,65),(410,32),(680,110),(1180,52),(1460,82),(1740,42),(290,98)]):
        a2 = max(0, int(165 - now/28 + i*22)) % 165
        st = pygame.Surface((4,4), pygame.SRCALPHA)
        pygame.draw.circle(st,(252,248,195,min(a2,165)),(2,2),2)
        surf.blit(st,(sx2,sy2))
    off_col = (55, 18, 8)
    ns = pygame.font.SysFont("verdana",18,bold=True).render("EL FAROL ROJO", True, off_col)
    surf.blit(ns,(48, 68))


_SPEAKER_COLORS = {
    'Portero': (185,185,225), 'Bruno': (185,185,225),
    'Rosa':    (235,162,162), 'Camarera': (235,162,162),
    'Víctor':  (185,125,232),
    'Tú':      (125,225,162),
    'narrador':DORADO,
}


def wrap_story(text, font, max_w):
    words = text.split()
    lines2 = []; cur = ""
    for w in words:
        test = (cur+" "+w).strip()
        if font.size(test)[0] <= max_w: cur = test
        else:
            if cur: lines2.append(cur)
            cur = w
    if cur: lines2.append(cur)
    return lines2


def draw_dialogue_box(surf, speaker, text, now):
    BOX_H = 215; BOX_Y = ALTO - BOX_H; PAD = 65
    bg = pygame.Surface((ANCHO, BOX_H), pygame.SRCALPHA)
    bg.fill((3, 2, 8, 218))
    surf.blit(bg, (0, BOX_Y))
    pygame.draw.line(surf, DORADO, (0, BOX_Y), (ANCHO, BOX_Y), 2)
    pygame.draw.line(surf, (80,65,30), (PAD, BOX_Y+8), (ANCHO-PAD, BOX_Y+8), 1)
    narrador_mode = (speaker in ('narrador', ''))
    if narrador_mode:
        text_y = BOX_Y + 32
    else:
        sc2 = _SPEAKER_COLORS.get(speaker, DORADO)
        name_s = FUENTE_NAME.render(speaker, True, sc2)
        surf.blit(name_s, (PAD, BOX_Y + 18))
        text_y = BOX_Y + 18 + name_s.get_height() + 6
    max_w2 = ANCHO - PAD * 2
    lines2 = wrap_story(text, FUENTE_STORY, max_w2)
    txt_col = (195,195,195) if narrador_mode else BLANCO
    for i, line in enumerate(lines2[:4]):
        ls = FUENTE_STORY.render(line, True, txt_col)
        surf.blit(ls, (PAD, text_y + i*34))
    if (now // 550) % 2 == 0:
        cont = FUENTE_INSTR.render("[ ESPACIO  o  clic  para continuar ]", True, (125,112,88))
        surf.blit(cont, (ANCHO - cont.get_width() - PAD, ALTO - 26))

def draw_choice_box(surf, options, now):
    """Dibuja el cuadro de elección del jugador. Devuelve lista de Rect para clic."""
    BTN_H   = 54
    PAD_X   = 72
    GAP     = 10
    HEADER_H = 52
    total_h = HEADER_H + len(options) * (BTN_H + GAP) + 22
    BOX_Y   = ALTO - total_h - 8

    bg = pygame.Surface((ANCHO, ALTO - BOX_Y), pygame.SRCALPHA)
    bg.fill((3, 2, 8, 222))
    surf.blit(bg, (0, BOX_Y))
    pygame.draw.line(surf, DORADO, (0, BOX_Y), (ANCHO, BOX_Y), 2)
    pygame.draw.line(surf, (80, 65, 30), (PAD_X, BOX_Y + 8), (ANCHO - PAD_X, BOX_Y + 8), 1)

    sc = _SPEAKER_COLORS.get('Tú', (125, 225, 162))
    header = FUENTE_NAME.render("¿Qué dices?", True, sc)
    surf.blit(header, (PAD_X, BOX_Y + 12))

    hint = FUENTE_INSTR.render("[ pulsa 1 / 2 / 3 / 4  o  haz clic ]", True, (100, 90, 70))
    surf.blit(hint, (ANCHO - hint.get_width() - PAD_X, BOX_Y + 18))

    mouse_pos = to_logical(pygame.mouse.get_pos())
    btn_rects = []
    btn_y = BOX_Y + HEADER_H

    for i, opt in enumerate(options):
        btn_w    = ANCHO - PAD_X * 2
        btn_rect = pygame.Rect(PAD_X, btn_y, btn_w, BTN_H)
        hovered  = btn_rect.collidepoint(mouse_pos)

        bg_col = (55, 95, 68) if hovered else (26, 44, 32)
        bsurf  = pygame.Surface((btn_w, BTN_H), pygame.SRCALPHA)
        bsurf.fill((*bg_col, 230))
        surf.blit(bsurf, (PAD_X, btn_y))
        border_col = DORADO if hovered else (75, 115, 85)
        pygame.draw.rect(surf, border_col, btn_rect, 1, border_radius=7)

        num_s = FUENTE_PEQUENA.render(f"[{i + 1}]", True, DORADO)
        surf.blit(num_s, (PAD_X + 14, btn_y + (BTN_H - num_s.get_height()) // 2))

        txt_col = (210, 255, 220) if hovered else BLANCO
        txt     = FUENTE_STORY.render(opt['label'], True, txt_col)
        surf.blit(txt, (PAD_X + 62, btn_y + (BTN_H - txt.get_height()) // 2))

        btn_rects.append(btn_rect)
        btn_y += BTN_H + GAP

    return btn_rects


INTRO_SCENES = [
    {
        'bg': 'title', 'chars': [], 'counter': False,
        'lines': [
            ('narrador', 'Barcelona. 1987.'),
            ('narrador', 'El Barrio Gótico lleva siglos guardando secretos. Esta noche guardará uno más.'),
            ('narrador', 'Al final del Carrer del Bisbe, en un portal sin número, existe un lugar que no aparece en ningún mapa.'),
            ('narrador', '"El Farol Rojo". Un casino clandestino que opera desde hace años con total impunidad.'),
            ('narrador', 'Su propietario, Víctor Carvalho, no ha perdido una partida de blackjack en tres años. Nadie sabe cómo lo hace.'),
            ('narrador', 'Tú llegas con mil fichas, una teoría y una promesa que te hiciste a ti mismo.'),
            ('narrador', 'Esta noche, alguien va a perder.'),
        ]
    },
    {
        'bg': 'street', 'chars': [('portero', ANCHO//2+300, 760)], 'counter': False,
        'scene_image': 'farol-rojo',
        'lines': [
            ('Portero', '¿A dónde crees que vas, amigo?'),
            ('CHOICE', [
                {
                    'label': '"Vengo a jugar."',
                    'tu_text': 'Vengo a jugar.',
                    'reactions': [
                        ('Portero', 'Aquí no entra cualquiera. Este no es un sitio para turistas.'),
                    ],
                    'effect': {}
                },
                {
                    'label': '"Tengo una cita con Víctor."',
                    'tu_text': 'Tengo una cita con Víctor. Dice que me esperaba.',
                    'reactions': [
                        ('Portero', '(Frunce el ceño.) ¿Con el jefe? Nadie tiene "citas" con Víctor...'),
                        ('Portero', '(Tras una pausa.) Pero algo en tu cara dice que no mientes. Venga.'),
                    ],
                    'effect': {}
                },
                {
                    'label': '"He oído que aquí hay acción de verdad."',
                    'tu_text': 'He oído que aquí hay acción de verdad. Vine a comprobarlo.',
                    'reactions': [
                        ('Portero', '(Resopla.) Todo el mundo "ha oído". Lo que no todo el mundo tiene es pasta para respaldarlo.'),
                    ],
                    'effect': {}
                },
                {
                    'label': '"Un amigo me recomendó este lugar. Dice que no hay otro igual."',
                    'tu_text': 'Un amigo mío me recomendó este lugar. Dice que no hay otro igual en toda Barcelona.',
                    'reactions': [
                        ('Portero', '(Entrecierra los ojos.) ¿Qué amigo?'),
                        ('Tú', 'El tipo no da su nombre. Solo su palabra.'),
                        ('Portero', '(Bufido.) Típico. Bueno... si alguien te mandó, algo sabes. Adelante.'),
                    ],
                    'effect': {}
                },
            ]),
            ('CHOICE', [
                {
                    'label': '"Mil fichas. ¿Suficiente?"',
                    'tu_text': 'Tengo mil fichas y no tengo prisa. ¿Suficiente?',
                    'reactions': [
                        ('Portero', '(Te mira de arriba abajo durante un momento largo.)'),
                        ('Portero', '...Pasa. Pero sabe que nadie ha salido de aquí ganando. Nadie.'),
                    ],
                    'effect': {}
                },
                {
                    'label': '"Las suficientes para limpiar la mesa de Víctor."',
                    'tu_text': 'Las suficientes para limpiar la mesa de Víctor. Y sobrar.',
                    'reactions': [
                        ('Portero', '(Casi sonríe.) Otro que viene con ganas. Venga, pasa antes de que me arrepienta.'),
                        ('Portero', 'Que conste: nadie ha salido de aquí ganando. Nadie.'),
                    ],
                    'effect': {'money': 50, 'msg': '+50 fichas — el portero queda impresionado'}
                },
                {
                    'label': '"Las justas. Pero sé lo que hago."',
                    'tu_text': 'Las justas. Pero sé exactamente lo que hago.',
                    'reactions': [
                        ('Portero', '(Una pausa. Te estudia de arriba abajo.)'),
                        ('Portero', 'Esa mirada... he visto esa mirada antes. Dos veces. Uno salió rico. El otro no salió.'),
                        ('Portero', 'A ver en cuál de los dos te conviertes tú. Adelante.'),
                    ],
                    'effect': {}
                },
            ]),
            ('CHOICE', [
                {
                    'label': '"Hay una primera vez para todo."',
                    'tu_text': 'Hay una primera vez para todo.',
                    'reactions': [],
                    'effect': {}
                },
                {
                    'label': '"Esta noche las cosas cambian."',
                    'tu_text': 'Esta noche las cosas van a cambiar, amigo.',
                    'reactions': [],
                    'effect': {}
                },
                {
                    'label': '(Entras sin decir nada.)',
                    'tu_text': '...',
                    'reactions': [],
                    'effect': {}
                },
                {
                    'label': '"¿Y tú, amigo? ¿Cuánto llevas aquí?"',
                    'tu_text': '¿Y tú? ¿Cuánto tiempo llevas cuidando esta puerta?',
                    'reactions': [
                        ('Portero', '(Te mira sorprendido. Nadie le pregunta eso.)'),
                        ('Portero', 'Seis años. Seis años viendo entrar a gente con sueños y salir con deudas.'),
                        ('Portero', '(En voz baja.) Tú... ten cuidado, ¿eh? Víctor no es lo que parece.'),
                    ],
                    'effect': {'money': 75, 'msg': '+75 fichas — el portero te tiene simpatía'}
                },
            ]),
        ]
    },
    {
        'bg': 'bar', 'chars': [('camarera', ANCHO//2-180, 770)], 'counter': True,
        'scene_image': 'rosita',
        'lines': [
            ('Rosa', 'Primera vez que te veo por aquí.'),
            ('Tú', 'Primera vez que vengo. Dicen que aquí sirven las mejores cartas de Barcelona.'),
            ('Rosa', '(Sonríe) Y el peor whisky. Te lo advierto. ¿Qué te pongo?'),
            ('CHOICE', [
                {
                    'label': '"Nada. Estoy aquí por Víctor."',
                    'tu_text': 'Nada por ahora. Estoy aquí por Víctor.',
                    'reactions': [
                        ('Rosa', '(La sonrisa desaparece.) Cuidado con él. Lleva tres años sin perder. Dicen que ve las cartas antes de que salgan.'),
                    ],
                    'effect': {}
                },
                {
                    'label': '"Ponme lo que tú tomarías."',
                    'tu_text': 'Ponme lo que tú tomarías. Y cuéntame algo sobre este sitio.',
                    'reactions': [
                        ('Rosa', '(Sonríe con melancolía.) Un Laphroaig, entonces. Y sobre este sitio... todo lo que ves tiene dueño. Incluidas las cartas.'),
                        ('Rosa', 'Un consejo gratis: cuando Víctor se toque el nudo de la corbata, tiene buena mano. Guárdatelo.'),
                        ('narrador', '(Rosa te pasa discretamente un billete doblado. +100 fichas para la partida.)'),
                    ],
                    'effect': {'money': 100, 'msg': '+100 fichas — Rosa confía en ti'}
                },
                {
                    'label': '"El whisky más caro. Lo celebro por adelantado."',
                    'tu_text': 'El whisky más caro que tengas. Esta noche lo celebro por adelantado.',
                    'reactions': [
                        ('Rosa', '(Arquea una ceja.) Confiado. Me gusta. Aunque aquí los que llegan muy seguros... suelen salir más callados.'),
                        ('narrador', '(El whisky de malta llega rápido. Vacías la copa de un trago. −50 fichas de tu bolsillo.)'),
                    ],
                    'effect': {'money': -50, 'msg': '−50 fichas — ese whisky era caro de verdad'}
                },
                {
                    'label': '"¿Qué recomiendas tú para una noche larga?"',
                    'tu_text': '¿Qué recomiendas tú para una noche larga, Rosa?',
                    'reactions': [
                        ('Rosa', '(Se apoya en la barra con una sonrisa cómplice.) Para una noche larga...'),
                        ('Rosa', 'Agua con gas. La cabeza despejada vale más que cualquier carta.'),
                        ('narrador', '(Rosa añade con discreción un par de fichas al montón.) Un extra, de mi parte.'),
                    ],
                    'effect': {'money': 80, 'msg': '+80 fichas — el consejo de Rosa tiene precio'}
                },
            ]),
            ('CHOICE', [
                {
                    'label': '"¿Y si pierde? ¿Qué pasa entonces?"',
                    'tu_text': '¿Y si pierde? ¿Qué pasa?',
                    'reactions': [
                        ('Rosa', 'Eso... nadie lo sabe. Nunca ha pasado. Nadie ha llegado tan lejos.'),
                        ('Tú', 'Pues esta noche vamos a descubrirlo.'),
                        ('Rosa', '(En voz baja) Ten cuidado. En serio.'),
                    ],
                    'effect': {}
                },
                {
                    'label': '"¿Le has visto hacer trampa alguna vez?"',
                    'tu_text': '¿Tú le has visto hacer trampa alguna vez?',
                    'reactions': [
                        ('Rosa', '(Pausa. Baja la voz.) No exactamente... pero hay momentos en que las cartas parecen obedecerle. Como si las conociera de antes.'),
                        ('Rosa', 'Nada demostrable. Nunca nada demostrable. Ten cuidado, ¿de acuerdo?'),
                    ],
                    'effect': {}
                },
                {
                    'label': '"¿Puedo pedirte algo... más personal?"',
                    'tu_text': '¿Puedo pedirte algo más personal, Rosa?',
                    'reactions': [
                        ('Rosa', '(Te mira un instante demasiado largo. Después apoya los codos en la barra y baja la voz.)'),
                        ('Rosa', 'La puerta azul al fondo. Cinco minutos. Nadie mira hacia allí a esta hora.'),
                        ('narrador', 'Lo que ocurrió al fondo del pasillo, entre cajas de Laphroaig y la penumbra azul, queda ahí.'),
                        ('narrador', 'Cinco minutos que se notaron más que cinco horas.'),
                        ('narrador', 'De vuelta en la barra, Rosa sirve una copa sin mirarte. Pero sonríe.'),
                        ('Rosa', '(En voz muy baja, arreglándose el cabello.) Gana esta noche, ¿de acuerdo?'),
                        ('Tú', 'Ahora tengo más motivos para hacerlo.'),
                        ('Rosa', '(Una sonrisa que intenta esconder, sin éxito.) Anda ya...'),
                        ('narrador', 'Su perfume te acompañará el resto de la noche. +150 fichas — Rosa tiene fe en ti.'),
                    ],
                    'effect': {'money': 150, 'msg': '+150 fichas — Rosa tiene fe en ti', 'rosa_secret': True}
                },
                {
                    'label': '"¿Por qué sigues trabajando para Víctor?"',
                    'tu_text': '¿Por qué sigues trabajando para alguien como Víctor?',
                    'reactions': [
                        ('Rosa', '(Una pausa larga. Limpia el vaso sin mirarte.)'),
                        ('Rosa', 'Porque las deudas no se pagan solas. Y porque... todavía no ha llegado nadie que lo saque de ahí.'),
                        ('Rosa', '(Te mira fijamente.) Quizás esta noche cambia eso.'),
                        ('narrador', '(Algo en su voz suena a esperanza. +60 fichas — un pequeño empujón de su parte.)'),
                    ],
                    'effect': {'money': 60, 'msg': '+60 fichas — Rosa deposita su esperanza en ti'}
                },
            ]),
        ]
    },
    {
        'bg': 'table', 'chars': [('victor', ANCHO//2+210, 730)], 'counter': False,
        'scene_image': 'victor2',
        'lines': [
            ('Víctor', 'Vaya, vaya... carne fresca. Hacía tiempo que no veía una cara nueva.'),
            ('Víctor', 'Siéntate. ¿Cuánto dinero traes?'),
            ('Tú', 'Mil fichas.'),
            ('Víctor', '(Ríe suavemente.) Suficiente para entretenernos unas horas. Quizás.'),
            ('Víctor', 'Las reglas son simples: gana el que llega a 21 sin pasarse. Yo soy la banca.'),
            ('Víctor', 'Y en este establecimiento... la banca siempre gana. Siempre.'),
            ('CHOICE', [
                {
                    'label': '"Si llego a 10.000… me dices cómo haces trampa."',
                    'tu_text': 'De acuerdo. Pero tengo una condición.',
                    'reactions': [
                        ('Víctor', '(Arquea una ceja.) ¿Condición? Eso es... inusual.'),
                        ('Tú', 'Si llego a diez mil fichas... me dices cómo lo haces. Cómo haces trampa.'),
                        ('Víctor', '(Pausa larga. Te mira fijamente. Luego sonríe.) ...Trato hecho, forastero. Suerte.'),
                        ('Víctor', 'La vas a necesitar.'),
                        ('narrador', '[ MODO NORMAL — Meta: 10.000 fichas. La banca no se rinde fácil, pero tampoco es invencible. ]'),
                    ],
                    'effect': {'difficulty': 0}
                },
                {
                    'label': '"Si llego a 25.000… que toda la sala lo sepa."',
                    'tu_text': 'Si llego a veinticinco mil fichas... quiero que esta sala sepa que la banca puede perder.',
                    'reactions': [
                        ('Víctor', '(Una sonrisa fría, casi apreciativa.) Ambicioso. Me gustan los ambiciosos.'),
                        ('Víctor', 'Suelen quedarse sin nada antes del amanecer. Pero... de acuerdo. Trato hecho.'),
                        ('Víctor', 'Veamos de qué pasta estás hecho, forastero.'),
                        ('narrador', '[ MODO DIFÍCIL — Meta: 25.000 fichas. Víctor ordena a sus crupiers que jueguen más agresivo. ]'),
                    ],
                    'effect': {'difficulty': 1}
                },
                {
                    'label': '"Si llego a 50.000… este casino es mío."',
                    'tu_text': 'Si llego a cincuenta mil fichas... este casino pasa a ser mío. En espíritu.',
                    'reactions': [
                        ('Víctor', '(Una carcajada seca.) ¡Cincuenta mil! Hace años que nadie me desafía así.'),
                        ('Víctor', '(Se inclina hacia adelante.) Acepto. Pero cuando pierdas... y perderás... sal por esa puerta y no vuelvas.'),
                        ('narrador', '[ MODO MUY DIFÍCIL — Meta: 50.000 fichas. La banca juega sin misericordia. ]'),
                    ],
                    'effect': {'difficulty': 2}
                },
                {
                    'label': '"Sin condiciones. Solo voy a ganar. 100.000."',
                    'tu_text': 'Sin condiciones, Víctor. Cien mil fichas. Solo vengo a ganar.',
                    'reactions': [
                        ('Víctor', '(Se recuesta en la silla. Un silencio largo y tenso.)'),
                        ('Víctor', 'Cien mil. Nadie... absolutamente nadie ha pronunciado esa cifra aquí.'),
                        ('Víctor', '(La sonrisa se congela.) Muy bien. Sin condiciones. Pero a este nivel... la banca no tiene piedad.'),
                        ('narrador', '[ MODO EXTREMO — Meta: 100.000 fichas. La banca juega sin compasión. Buena suerte. ]'),
                    ],
                    'effect': {'difficulty': 3}
                },
            ]),
            ('narrador', '¡Que empiece el juego!'),
        ]
    },
]

def build_win_ending_scenes():
    rosa_lines = []
    if rosa_secret_done:
        rosa_lines = [
            ('narrador', 'Alguien te espera en el Café del Born cuando abra. Con el mismo perfume de anoche.'),
            ('narrador', 'Ya le has mandado un mensaje. Solo dos palabras: "Lo conseguí."'),
            ('narrador', 'Su respuesta llegó antes de doblar la primera esquina: "Ya lo sabía. ;)"'),
        ]
    diff_narrador = {
        0: 'Lo lograste en modo Normal. Víctor nunca imaginó que alguien llegaría tan lejos.',
        1: 'Lo lograste en modo Difícil. La banca jugó sin piedad y aun así no fue suficiente.',
        2: 'Lo lograste en modo Muy Difícil. Cincuenta mil fichas. Una hazaña que nadie olvidará.',
        3: 'Lo lograste en modo EXTREMO. Cien mil fichas. Ni Víctor mismo se lo creerá jamás.',
    }
    return [
        {
            'bg': 'table', 'chars': [('victor_nervioso', ANCHO//2+210, 730)], 'counter': False,
            'scene_image': 'victor3',
            'line_images': [None, None, None, None, None, None, None, 'victor4'],
            'lines': [
                ('narrador', 'El número imposible.'),
                ('narrador', 'El aire en la sala cambió. Fue como si alguien hubiera apagado la música sin tocar nada.'),
                ('Víctor', '...'),
                ('Víctor', '¿Cómo?'),
                ('Tú', 'Ya sabes lo que eso significa, Víctor.'),
                ('Víctor', '¡No! ¡Trampa! ¡Este hombre está haciendo trampa de alguna manera!'),
                ('Tú', 'Las cartas no mienten, Víctor. Tú sí.'),
                ('Víctor', '(Se pone de pie, volcando la silla.) ¡Garduño! ¡Enrique! ¡Sacad a este hombre de aquí ahora mismo!'),
            ]
        },
        {
            'bg': 'bar', 'chars': [('camarera', ANCHO//2-180, 770)], 'counter': True,
            'scene_image': 'rosita-caos',
            'line_images': [None, None, None, None, None, None, None, None, 'rosita-guino'],
            'lines': [
                ('narrador', 'Dos hombres muy grandes se levantan de las sombras. El ambiente se congela.'),
                ('narrador', 'Y entonces Rosa actúa.'),
                ('Rosa', '¡Ay, Dios mío, qué torpe soy!'),
                ('narrador', 'Rosa vuelca toda la barra de un golpe. Una cascada de botellas, vasos y whisky de treinta años inunda el suelo.'),
                ('narrador', 'El caos es inmediato y total. Gritos, cristales rotos, gente empujando.'),
                ('narrador', 'En medio de la confusión, tú te guardas los billetes y caminas tranquilamente hacia la puerta.'),
                ('Portero', '¡Eh! ¡Para ahí!'),
                ('narrador', 'Pero el portero tiene los pies empapados de Macallan del 62 y otras prioridades.'),
                ('Rosa', '(Te guiña un ojo desde el otro lado del caos.)'),
            ]
        },
        {
            'bg': 'street_dawn', 'chars': [], 'counter': False,
            'scene_image': 'barcelona',
            'lines': [
                ('narrador', 'El aire de la madrugada huele a lluvia limpia. A libertad.'),
                ('narrador', 'Caminas despacio por los adoquines mojados. No hay prisa. Ya no.'),
                ('narrador', 'Detrás de ti, el neón de "El Farol Rojo" parpadea dos veces y se apaga.'),
                ('narrador', diff_narrador.get(difficulty_level, diff_narrador[0])),
                ('narrador', 'Y tú lo habías encontrado.'),
                ('narrador', 'La ciudad empieza a despertar. Huele a café y a pan recién hecho.'),
            ] + rosa_lines + [
                ('narrador', '─────────  FIN  ─────────'),
            ]
        },
    ]

LOSE_ENDING_SCENES = [
    {
        'bg': 'table', 'chars': [('victor', ANCHO//2+210, 730)], 'counter': False,
        'scene_image': 'victor5',
        'lines': [
            ('narrador', 'Y así terminó.'),
            ('Víctor', 'Ya está. Eso es todo lo que tenías.'),
            ('Víctor', 'Ha sido... entretenido. Para mí.'),
            ('Tú', '...'),
            ('Víctor', '(Sin levantar la vista de las fichas.) La puerta está donde la dejaste. Buenas noches.'),
            ('narrador', 'No había nada más que decir.'),
        ]
    },
    {
        'bg': 'street', 'chars': [], 'counter': False,
        'scene_image': 'segurata-pierdes',
        'lines': [
            ('narrador', 'Volviste a la calle con los bolsillos vacíos y la cabeza llena de preguntas.'),
            ('narrador', 'La lluvia seguía ahí. Indiferente. Como siempre.'),
            ('narrador', 'Víctor seguía dentro, invicto. De momento.'),
            ('narrador', 'Pero el juego no había terminado. Solo esta ronda.'),
            ('narrador', 'Mañana es otro día. Y tú sabes dónde está la puerta.'),
            ('narrador', '¿Lo intentas de nuevo?'),
        ]
    },
]


app_state         = 'main_menu'
game_mode         = 'story'     
story_scenes_data = INTRO_SCENES
story_scene_idx   = 0
story_line_idx    = 0
epic_win_triggered = False
main_menu_hovered = -1

story_choice_active  = False      
story_choice_options = []          
story_choice_rects   = []          
story_injected_lines = []         
story_injected_idx   = 0          
story_in_injection   = False       

preload_images('farol-rojo', 'rosita', 'rosita-seria', 'victor2', 'victor3', 'victor4', 'victor5', 'rosita-caos', 'rosita-guino', 'barcelona', 'segurata-pierdes')


def _start_story(scenes, new_state):
    global story_scenes_data, story_scene_idx, story_line_idx, app_state
    story_scenes_data = scenes
    story_scene_idx   = 0
    story_line_idx    = 0
    app_state         = new_state


def _apply_choice(idx):
    """Aplica la elección del jugador: inyecta las reacciones y avanza la historia."""
    global story_choice_active, story_choice_options, story_choice_rects
    global story_injected_lines, story_injected_idx, story_in_injection, player_money
    global difficulty_level, EPIC_WIN_THRESHOLD, rosa_secret_done

    opt    = story_choice_options[idx]
    effect = opt.get('effect', {})
    if 'money' in effect:
        player_money = max(0, player_money + effect['money'])
    if 'difficulty' in effect:
        difficulty_level = effect['difficulty']
        thresholds = {0: 10000, 1: 25000, 2: 50000, 3: 100000}
        EPIC_WIN_THRESHOLD = thresholds.get(difficulty_level, 10000)
    if effect.get('rosa_secret'):
        rosa_secret_done = True

    injected = []
    tu_text = opt.get('tu_text', '')
    if tu_text:
        injected.append(('Tú', tu_text))
    for line in opt.get('reactions', []):
        injected.append(line)

    story_choice_active  = False
    story_choice_options = []
    story_choice_rects   = []

    if injected:
        story_injected_lines = injected
        story_injected_idx   = 0
        story_in_injection   = True
    else:
        _story_advance_scene()


def _story_advance_scene():
    """Avanza un paso dentro de la escena / al siguiente bloque de escenas."""
    global story_scenes_data, story_scene_idx, story_line_idx, app_state
    global player_money, stats, current_bet, current_bet_input, last_bet, epic_win_triggered

    story_line_idx += 1
    scene = story_scenes_data[story_scene_idx]
    if story_line_idx >= len(scene['lines']):
        story_scene_idx += 1
        story_line_idx   = 0
        if story_scene_idx >= len(story_scenes_data):
            if app_state == 'intro':
                app_state = 'game'
                nueva_ronda()
            elif app_state == 'win_ending':
                pygame.quit(); sys.exit()
            elif app_state == 'lose_ending':
                app_state = 'main_menu'


def _story_advance():
    global story_in_injection, story_injected_lines, story_injected_idx

    if story_in_injection:
        story_injected_idx += 1
        if story_injected_idx >= len(story_injected_lines):
            story_in_injection   = False
            story_injected_lines = []
            story_injected_idx   = 0
            _story_advance_scene()
        return

    _story_advance_scene()


def _render_story(now):
    global story_scenes_data, story_scene_idx, story_line_idx
    global story_choice_active, story_choice_options, story_choice_rects
    global story_in_injection, story_injected_lines, story_injected_idx

    if story_scene_idx >= len(story_scenes_data):
        return
    scene       = story_scenes_data[story_scene_idx]
    bg          = scene['bg']
    has_counter = scene.get('counter', False)
    if bg == 'title':         draw_bg_title(VENTANA, now)
    elif bg == 'street':      draw_bg_street(VENTANA, now)
    elif bg == 'bar':         draw_bg_bar_base(VENTANA, now)
    elif bg == 'table':       draw_bg_table_scene(VENTANA, now)
    elif bg == 'street_dawn': draw_bg_street_dawn(VENTANA, now)
    else:                     VENTANA.fill(NEGRO)

    scene_img_key = scene.get('scene_image')
    if not story_in_injection:
        line_images = scene.get('line_images')
        if line_images and story_line_idx < len(line_images) and line_images[story_line_idx] is not None:
            img_key = line_images[story_line_idx]
        else:
            img_key = scene_img_key
    else:
        img_key = scene_img_key
    if img_key:
        draw_story_image(img_key, VENTANA)

    if has_counter:
        draw_bar_counter_overlay(VENTANA, now)

    if story_in_injection:
        story_choice_active = False
        if story_injected_idx < len(story_injected_lines):
            speaker2, text2 = story_injected_lines[story_injected_idx]
            draw_dialogue_box(VENTANA, speaker2, text2, now)
        return

    if story_line_idx < len(scene['lines']):
        current_line = scene['lines'][story_line_idx]
        if current_line[0] == 'CHOICE':
            choices = current_line[1]
            rects = draw_choice_box(VENTANA, choices, now)
            story_choice_active  = True
            story_choice_options = choices
            story_choice_rects   = rects
        else:
            story_choice_active = False
            speaker2, text2 = current_line
            draw_dialogue_box(VENTANA, speaker2, text2, now)


def crear_baraja():
    palos = [("S",NEGRO),("H",ROJO),("D",ROJO),("C",NEGRO)]
    valores = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
    baraja2 = []
    for palo,color in palos:
        for v in valores:
            if v=="A": vn=11
            elif v in ["J","Q","K"]: vn=10
            else: vn=int(v)
            baraja2.append((v,palo,vn,color))
    random_module.shuffle(baraja2)
    return baraja2

def calcular(mano):
    total = sum(c[2] for c in mano)
    ases  = sum(1 for c in mano if c[0]=="A")
    while total > 21 and ases:
        total -= 10; ases -= 1
    return total

def calcular_visible(mano):
    vis = [c for c in mano if (not c[4].oculta) and (not c[4].flipping) and (abs(c[4].x-c[4].dest_x)<1)]
    if not vis: return 0
    total = sum(c[2] for c in vis)
    ases  = sum(1 for c in vis if c[0]=="A")
    while total > 21 and ases:
        total -= 10; ases -= 1
    return total


baraja = []
jugador = []; jugador_hands = None; current_hand_index = 0
split_active = False; banca = []

player_money = 1000; current_bet = 10; bet_locked = False
current_bet_input = ""; last_bet = None

insurance_offered = False; insurance_bet = 0; insurance_taken = False
doubledown_flags = []; per_hand_bets = None

stats = {'played':0,'won':0,'lost':0,'blackjacks':0}

state = 'betting'; dealing_step = 0; next_deal = 0
dealer_thinking = False; next_action = 0; last_pedir_time = 0; round_end_time = 0
dealer_target = 17

clearing = False; clear_phase = None; clearing_cards = []
particles = []; chips_anim = []; placed_chip = None; player_chip_stack = []

overlay_flash = {'active':False,'color':(0,0,0),'alpha':0,'start':0,'duration':400}

update_status = None; update_msg = ""; update_notif_time = 0; update_restart_time = 0
DOTS_BTN      = pygame.Rect(ANCHO-46,  8,   38,  28)
REINICIAR_BTN = pygame.Rect(ANCHO-140, ALTO-44, 130, 34)

nueva_ronda_pending = False
mensaje = ""

paused = False


def _sha256(path):
    import hashlib
    try:
        with open(path,"rb") as f: return hashlib.sha256(f.read()).hexdigest()
    except: return None

def _check_for_updates():
    global update_status, update_msg, update_notif_time, update_restart_time
    import tempfile, time
    tmp_path = None
    try:
        url = GITHUB_RAW_URL + f"?nocache={int(time.time())}"
        req = urllib.request.Request(url, headers={"Cache-Control":"no-cache","Pragma":"no-cache"})
        res = urllib.request.urlopen(req, timeout=15)
        remote_data = res.read()
        fd, tmp_path = tempfile.mkstemp(suffix=".py")
        with os.fdopen(fd,"wb") as f: f.write(remote_data)
        local_path = os.path.abspath(__file__)
        sha_local  = _sha256(local_path)
        sha_remote = _sha256(tmp_path)
        if sha_remote is None:
            update_status = "error"; update_msg = "No se pudo calcular hash remoto"
        elif sha_local == sha_remote:
            update_status = "up_to_date"; update_msg = "Ya tienes la última versión"
        else:
            try:
                shutil.copy2(tmp_path, local_path)
                update_status = "restarting"; update_msg = "¡Actualizado! Reiniciando..."
                update_restart_time = pygame.time.get_ticks()
            except Exception as e:
                update_status = "error"; update_msg = f"No se pudo escribir: {str(e)[:40]}"
    except Exception as e:
        update_status = "error"; update_msg = f"Error: {str(e)[:55]}"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try: os.unlink(tmp_path)
            except: pass
    update_notif_time = pygame.time.get_ticks()


def get_current_hand():
    global split_active, jugador, jugador_hands, current_hand_index
    if split_active and jugador_hands: return jugador_hands[current_hand_index]
    return jugador

def iter_player_hands():
    if split_active and jugador_hands:
        for h in jugador_hands: yield h
    else: yield jugador

def repartir(mano, y, oculta=False, start_pos=None):
    global baraja, split_active, jugador_hands
    if not baraja: baraja = crear_baraja()
    v, p, val, color = baraja.pop()
    if split_active and jugador_hands and mano in jugador_hands:
        hand_idx = jugador_hands.index(mano)
        base_x = 120 + hand_idx * HAND_SEP
        x = base_x + len(mano) * CARD_SPACING
    else:
        x = 200 + len(mano) * CARD_SPACING
    carta = Carta(v, p, val, color, x, y, start_pos=start_pos)
    carta.oculta = oculta
    mano.append((v, p, val, color, carta))

def revelar_banca(now):
    for c in banca:
        if c[4].oculta: c[4].start_flip(now)

def schedule_dealer_target():
    global difficulty_level
    if difficulty_level == 0:
        return 18 if random_module.random() < 0.15 else 17
    elif difficulty_level == 1:
        return 19 if random_module.random() < 0.20 else 18
    else:  
        return 19 if random_module.random() < 0.35 else 18

def spawn_particles(x, y, color, count=40):
    for _ in range(count):
        angle = random_module.random()*2*math.pi
        speed = random_module.random()*random_module.random()*10+1.5
        vx2 = math.cos(angle)*speed; vy2 = math.sin(angle)*speed
        life = random_module.random()*900+500
        particles.append([x,y,vx2,vy2,life,color])

def reiniciar_partida():
    global player_money, stats, current_bet_input, current_bet, last_bet, epic_win_triggered
    global rosa_secret_done
    player_money = 1000; stats = {'played':0,'won':0,'lost':0,'blackjacks':0}
    current_bet_input = ""; current_bet = 10; last_bet = None
    epic_win_triggered = False
    rosa_secret_done = False
    nueva_ronda()

def clip_text_right(text, font, max_w):
    """Recorta texto por la izquierda hasta que cabe en max_w píxeles."""
    txt = text
    while font.size(txt)[0] > max_w and len(txt) > 0:
        txt = txt[1:]
    return txt

def nueva_ronda():
    global baraja, jugador, banca, state, dealing_step, next_deal, mensaje, dealer_thinking, next_action
    global last_pedir_time, round_end_time, current_bet, bet_locked, player_money, stats, placed_chip, chips_anim
    global split_active, jugador_hands, current_hand_index, doubledown_flags, player_chip_stack, clearing_cards
    global per_hand_bets, clearing, clear_phase, insurance_offered, insurance_taken, insurance_bet, dealer_target
    baraja = crear_baraja(); jugador = []; banca = []
    jugador_hands = None; split_active = False; current_hand_index = 0; doubledown_flags = []
    mensaje = ""; dealing_step = 0; next_deal = pygame.time.get_ticks()+300
    dealer_thinking = False; next_action = 0; last_pedir_time = 0; round_end_time = 0
    dealer_target = 17
    state = 'betting'; bet_locked = False; placed_chip = None; chips_anim = []
    player_chip_stack = []; clearing_cards = []; per_hand_bets = None
    clearing = False; clear_phase = None
    insurance_offered = False; insurance_taken = False; insurance_bet = 0


def _apply_chip_result(results):
    global placed_chip, player_chip_stack, overlay_flash
    if placed_chip:
        if any(r in ('win','blackjack') for r in results):
            sx, sy = placed_chip['x'], placed_chip['y']
            tx, ty = ANCHO+120, -120; speed = 10.0
            dx = tx-sx; dy = ty-sy; dist = math.hypot(dx,dy) or 1.0
            placed_chip.update({'moving':True,'vx':dx/dist*speed,'vy':dy/dist*speed,
                                 'target_x':tx,'target_y':ty,'expire_on_arrival':True})
        elif all(r=='tie' for r in results):
            sx, sy = placed_chip['x'], placed_chip['y']
            tx, ty = ANCHO//2, ALTO-120; speed = 10.0
            dx = tx-sx; dy = ty-sy; dist = math.hypot(dx,dy) or 1.0
            placed_chip.update({'moving':True,'vx':dx/dist*speed,'vy':dy/dist*speed,
                                 'target_x':tx,'target_y':ty,'expire_on_arrival':True})
        else:
            sx, sy = placed_chip['x'], placed_chip['y']
            tx, ty = BANK_POS; speed = 10.0
            dx = tx-sx; dy = ty-sy; dist = math.hypot(dx,dy) or 1.0
            placed_chip.update({'moving':True,'vx':dx/dist*speed,'vy':dy/dist*speed,
                                 'target_x':tx,'target_y':ty,'expire_on_arrival':True})
    player_chip_stack = []
    now2 = pygame.time.get_ticks()
    if any(r in ('win','blackjack') for r in results):
        spawn_particles(ANCHO//2, ALTO//2+40, DORADO, count=20)
        overlay_flash.update({'active':True,'color':(255,255,255),'alpha':180,'start':now2,'duration':300})
    elif all(r=='tie' for r in results):
        overlay_flash.update({'active':True,'color':(200,200,200),'alpha':120,'start':now2,'duration':220})
    else:
        spawn_particles(ANCHO//2, ALTO//2, ROJO, count=25)
        overlay_flash.update({'active':True,'color':(150,0,0),'alpha':180,'start':now2,'duration':350})


nueva_ronda()


bj_player_money    = 5000
bj_current_bet     = 100
bj_bet_input       = ""
bj_last_bet        = None
bj_menu_btn        = pygame.Rect(ANCHO - 160, ALTO - 44, 148, 34)


def bj_reiniciar():
    global bj_player_money, bj_current_bet, bj_bet_input, bj_last_bet
    global player_money, current_bet, current_bet_input, last_bet, stats
    global epic_win_triggered
    bj_player_money = 5000; bj_current_bet = 100
    bj_bet_input = ""; bj_last_bet = None
    player_money = bj_player_money; current_bet = bj_current_bet
    current_bet_input = ""; last_bet = None; epic_win_triggered = False
    stats = {'played':0,'won':0,'lost':0,'blackjacks':0}
    nueva_ronda()


def _sync_bj_money():
    """Keep bj_player_money in sync with player_money while in BJ mode."""
    global bj_player_money
    bj_player_money = player_money


from collections import Counter as _Counter
from itertools import combinations as _combinations

HE_DECK_X        = ANCHO // 2
HE_DECK_Y        = 30
HE_COMMUNITY_Y   = ALTO // 2 - 72
HE_PLAYER_Y      = ALTO - 230
HE_DEALER_Y      = 82
HE_CARD_GAP      = 128   
BET_MAX_HOLDEM   = 5000

he_player_money  = 3000
he_blind         = 50
he_blind_input   = ""
he_state         = 'betting'   
he_pot           = 0
he_street_bet    = 0         
he_raise_input   = ""
he_in_raise      = False      
he_deck          = []
he_player_cards  = []         
he_dealer_cards  = []
he_community_cards = []
he_mensaje       = ""
he_player_hand_name  = ""
he_dealer_hand_name  = ""
he_winner        = ""         
he_result_timer  = 0
he_stats         = {'played':0,'won':0,'lost':0,'tied':0}
he_menu_btn      = pygame.Rect(ANCHO-164, ALTO-44, 152, 34)
he_reiniciar_btn = pygame.Rect(ANCHO-324, ALTO-44, 152, 34)
_FUENTE_HE_BIG   = pygame.font.SysFont("arial", 56, bold=True)
_FUENTE_HE_SMALL = pygame.font.SysFont("arial", 20, bold=True)
poker_player_money = he_player_money   

HE_AI_CARD_GAP = 58   
HE_AI_POSITIONS = [
    (190, 150),  
    (190, 540),  
    (1634, 150),
    (1634, 540),  
]
HE_AI_NAMES = ["JUGADOR 1", "JUGADOR 2", "JUGADOR 3", "JUGADOR 4"]
he_ai_cards  = [[], [], [], []]   
he_ai_money  = [3000, 3000, 3000, 3000]
he_ai_hand_names = ["", "", "", ""]  
he_ai_winner = False  

he_raise_btn = pygame.Rect(0, 0, 230, 38)  

he_ai_turn_active       = False
he_ai_turn_idx          = 0
he_ai_turn_phase        = 'announcing'  
he_ai_turn_timer        = 0
he_ai_actions           = []
he_ai_folded            = [False, False, False, False]
he_ai_raised_this_round = False   
he_ai_raise_amount      = 0      
_HE_ANNOUNCE_MS         = 650
_HE_DECIDE_MS           = 900

def _he_ai_compute_action(ai_idx):
    """Decide what AI player ai_idx does. Returns action string and modifies pot/money."""
    global he_pot, he_ai_money, he_ai_folded, he_ai_raised_this_round, he_ai_raise_amount
    if he_ai_folded[ai_idx]:
        return "ya retirado"
    ai_hand = he_ai_cards[ai_idx] if ai_idx < len(he_ai_cards) else []
    money = he_ai_money[ai_idx]
    if money <= 0:
        he_ai_folded[ai_idx] = True
        return "se retira (sin fichas)"
    if ai_hand and he_community_cards:
        ac = [(e[0],e[1],e[2],e[3]) for e in ai_hand]
        cc = [(e[0],e[1],e[2],e[3]) for e in he_community_cards]
        score, _ = evaluate_holdem_hand(ac + cc)
        rank = score[0] if score else -1
    elif ai_hand:
        ac = [(e[0],e[1],e[2],e[3]) for e in ai_hand]
        score, _ = evaluate_holdem_hand(ac)
        rank = score[0] if score else -1
    else:
        rank = -1
    r = random_module.random()
    call_amt = min(he_blind, money)

    def do_raise(mult_lo, mult_hi):
        global he_pot, he_ai_raised_this_round, he_ai_raise_amount
        amt = min(he_blind * random_module.randint(mult_lo, mult_hi), money)
        he_pot += amt; he_ai_money[ai_idx] -= amt
        he_ai_raised_this_round = True
        he_ai_raise_amount = max(he_ai_raise_amount, amt)
        return amt

    if rank >= 5:       
        if r < 0.80:
            amt = do_raise(3, 7)
            return f"SUBE {amt}"
        else:
            he_pot += call_amt; he_ai_money[ai_idx] -= call_amt
            return "iguala"
    elif rank >= 3:     
        if r < 0.50:
            amt = do_raise(2, 4)
            return f"sube {amt}"
        else:
            he_pot += call_amt; he_ai_money[ai_idx] -= call_amt
            return "iguala"
    elif rank >= 0:      
        if r < 0.22:
            he_ai_folded[ai_idx] = True
            return "se retira"
        elif r < 0.38:
            amt = do_raise(1, 2)
            return f"sube {amt}"
        else:
            he_pot += call_amt; he_ai_money[ai_idx] -= call_amt
            return "iguala"
    else:               
        if r < 0.50:
            he_ai_folded[ai_idx] = True
            return "se retira"
        elif r < 0.65:
            amt = do_raise(1, 3)
            return f"farolea y sube {amt}"
        else:
            he_pot += call_amt; he_ai_money[ai_idx] -= call_amt
            return "iguala"


def _he_start_ai_turns(now):
    """Call this instead of _advance_street to let AIs play their turns first."""
    global he_ai_turn_active, he_ai_turn_idx, he_ai_turn_phase, he_ai_turn_timer
    global he_ai_actions, he_ai_raised_this_round, he_ai_raise_amount
    he_ai_turn_active       = True
    he_ai_turn_idx          = 0
    he_ai_turn_phase        = 'announcing'
    he_ai_turn_timer        = now
    he_ai_actions           = []
    he_ai_raised_this_round = False
    he_ai_raise_amount      = 0


def _he_update_ai_turns(now):
    """Called every frame when he_ai_turn_active is True. Drives the AI turn sequence."""
    global he_ai_turn_active, he_ai_turn_idx, he_ai_turn_phase, he_ai_turn_timer
    global he_ai_actions, he_street_bet
    elapsed = now - he_ai_turn_timer
    if he_ai_turn_phase == 'announcing':
        if elapsed >= _HE_ANNOUNCE_MS:
            action = _he_ai_compute_action(he_ai_turn_idx)
            he_ai_actions.append(f"{HE_AI_NAMES[he_ai_turn_idx]}: {action}")
            he_ai_turn_phase = 'deciding'
            he_ai_turn_timer = now
    elif he_ai_turn_phase == 'deciding':
        if elapsed >= _HE_DECIDE_MS:
            he_ai_turn_idx += 1
            if he_ai_turn_idx >= len(HE_AI_NAMES):
                he_ai_turn_active = False
                if all(he_ai_folded):
                    _he_all_folded_win(now)
                elif he_ai_raised_this_round:
                    he_street_bet = he_ai_raise_amount
                else:
                    _advance_street(now)
            else:
                he_ai_turn_phase = 'announcing'
                he_ai_turn_timer = now


def _he_card_x(i, total, card_gap=None):
    g = card_gap or HE_CARD_GAP
    total_w = total * CARD_W + (total - 1) * (g - CARD_W)
    start_x = ANCHO // 2 - total_w // 2
    return start_x + i * g

def _he_val_num(v):
    m = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, '10': 10}
    if v in m: return m[v]
    return int(v)

def _he_eval_5(hand5):
    """Returns (rank_int, tiebreaker_list) for exactly 5 cards."""
    vs  = [c[0] for c in hand5]
    ss  = [c[1] for c in hand5]
    cnt = _Counter(vs)
    freq = sorted(cnt.values(), reverse=True)
    nums = sorted(_he_val_num(v) for v in vs)
    is_fl = len(set(ss)) == 1
    unique_nums = set(nums)
    is_st = (len(unique_nums) == 5) and (nums[-1] - nums[0] == 4)
    if not is_st and unique_nums == {14, 2, 3, 4, 5}:
        is_st = True; nums = [1, 2, 3, 4, 5]
    is_royal = is_st and is_fl and nums[-1] == 14
    nd = sorted(nums, reverse=True)
    if is_royal:                       return (8, nd)
    if is_st and is_fl:                return (7, nd)
    if freq[0] == 4:
        qv = max([_he_val_num(v) for v,c in cnt.items() if c == 4])
        kk = sorted([_he_val_num(v) for v,c in cnt.items() if c != 4], reverse=True)
        return (6, [qv] + kk)
    if freq[0] == 3 and len(freq) > 1 and freq[1] == 2:
        tv = max([_he_val_num(v) for v,c in cnt.items() if c == 3])
        pv = max([_he_val_num(v) for v,c in cnt.items() if c == 2])
        return (5, [tv, pv])
    if is_fl:                          return (4, nd)
    if is_st:                          return (3, nd)
    if freq[0] == 3:
        tv = max([_he_val_num(v) for v,c in cnt.items() if c == 3])
        kk = sorted([_he_val_num(v) for v,c in cnt.items() if c != 3], reverse=True)
        return (2, [tv] + kk)
    if freq[0] == 2 and len(freq) > 1 and freq[1] == 2:
        pvs = sorted([_he_val_num(v) for v,c in cnt.items() if c == 2], reverse=True)
        kk  = sorted([_he_val_num(v) for v,c in cnt.items() if c == 1], reverse=True)
        return (1, pvs + kk)
    if freq[0] == 2:
        pv = max([_he_val_num(v) for v,c in cnt.items() if c == 2])
        kk = sorted([_he_val_num(v) for v,c in cnt.items() if c != 2], reverse=True)
        return (0, [pv] + kk)
    return (-1, nd)

_HE_RANK_NAMES = {
    8: 'Escalera Real', 7: 'Escalera de Color', 6: 'Póker (4 iguales)',
    5: 'Full House', 4: 'Color', 3: 'Escalera', 2: 'Trío',
    1: 'Doble Pareja', 0: 'Pareja', -1: 'Carta Alta'
}

def evaluate_holdem_hand(cards_7):
    """Best 5-card hand from 7 cards (or fewer). Returns (score_tuple, name_str)."""
    best = None; best_name = 'Carta Alta'
    pool = list(cards_7)
    n = len(pool)
    k = min(5, n)
    for combo in _combinations(pool, k):
        sc = _he_eval_5(combo)
        if best is None or sc > best:
            best = sc; best_name = _HE_RANK_NAMES.get(sc[0], 'Carta Alta')
    return best, best_name

def _he_deal_card(deck, dest_x, dest_y, face_down=False):
    if not deck: deck[:] = crear_baraja()
    v, p, val, color = deck.pop()
    c = Carta(v, p, val, color, dest_x, dest_y, start_pos=(HE_DECK_X, HE_DECK_Y))
    c.oculta = face_down
    return (v, p, val, color, c)

def he_reiniciar():
    global he_player_money, he_blind, he_blind_input, he_state, he_stats
    global he_pot, he_street_bet, he_raise_input, he_in_raise
    global he_deck, he_player_cards, he_dealer_cards, he_community_cards
    global he_mensaje, he_player_hand_name, he_dealer_hand_name, he_winner
    global poker_player_money, he_ai_cards, he_ai_money, he_ai_hand_names, he_ai_winner
    he_player_money = 3000; he_blind = 50; he_blind_input = ""
    he_stats = {'played':0,'won':0,'lost':0,'tied':0}
    poker_player_money = 3000
    he_pot = 0; he_street_bet = 0; he_raise_input = ""; he_in_raise = False
    he_deck = []; he_player_cards = []; he_dealer_cards = []; he_community_cards = []
    he_mensaje = ""; he_player_hand_name = ""; he_dealer_hand_name = ""; he_winner = ""
    he_ai_cards = [[], [], [], []]; he_ai_money = [3000, 3000, 3000, 3000]
    he_ai_hand_names = ["", "", "", ""]; he_ai_winner = False
    he_state = 'betting'
    global he_ai_turn_active, he_ai_turn_idx, he_ai_actions, he_ai_folded
    he_ai_turn_active = False; he_ai_turn_idx = 0
    he_ai_actions = []; he_ai_folded = [False, False, False, False]
    global he_ai_raised_this_round, he_ai_raise_amount
    he_ai_raised_this_round = False; he_ai_raise_amount = 0

def he_start_hand(now):
    """Deal pre-flop: 2 to player, 2 to dealer (face down), 2 to each AI player (face down), post blinds."""
    global he_state, he_pot, he_street_bet, he_deck
    global he_player_cards, he_dealer_cards, he_community_cards
    global he_mensaje, he_player_hand_name, he_dealer_hand_name, he_winner
    global he_in_raise, he_raise_input, he_ai_cards, he_ai_hand_names, he_ai_winner
    he_deck = crear_baraja()
    he_community_cards = []
    he_mensaje = ""; he_player_hand_name = ""; he_dealer_hand_name = ""; he_winner = ""
    he_in_raise = False; he_raise_input = ""
    he_ai_hand_names = ["", "", "", ""]; he_ai_winner = False
    global he_ai_folded, he_ai_turn_active, he_ai_actions
    he_ai_folded = [False, False, False, False]
    he_ai_turn_active = False; he_ai_actions = []
    global he_ai_raised_this_round, he_ai_raise_amount
    he_ai_raised_this_round = False; he_ai_raise_amount = 0
    px = [_he_card_x(i, 2) for i in range(2)]
    dx = [_he_card_x(i, 2) for i in range(2)]
    he_player_cards = [_he_deal_card(he_deck, px[i], HE_PLAYER_Y) for i in range(2)]
    he_dealer_cards = []
    he_ai_cards = []
    for ai_i, (ax, ay) in enumerate(HE_AI_POSITIONS):
        ai_hand = [
            _he_deal_card(he_deck, ax,                ay, face_down=True),
            _he_deal_card(he_deck, ax + HE_AI_CARD_GAP, ay, face_down=True),
        ]
        he_ai_cards.append(ai_hand)
    he_pot = he_blind * 6
    he_street_bet = 0   
    he_state = 'pre_flop'

def _he_dealer_act(raise_amount=0):
    """Simple dealer bot: always calls any raise."""
    global he_pot
    if raise_amount > 0:
        he_pot += raise_amount  

def he_do_flop(now):
    global he_community_cards, he_state
    for i in range(3):
        cx = _he_card_x(i, 5)
        he_community_cards.append(_he_deal_card(he_deck, cx, HE_COMMUNITY_Y))
    he_state = 'flop'

def he_do_turn(now):
    global he_community_cards, he_state
    i = len(he_community_cards)
    cx = _he_card_x(i, 5)
    he_community_cards.append(_he_deal_card(he_deck, cx, HE_COMMUNITY_Y))
    he_state = 'turn'

def he_do_river(now):
    global he_community_cards, he_state
    i = len(he_community_cards)
    cx = _he_card_x(i, 5)
    he_community_cards.append(_he_deal_card(he_deck, cx, HE_COMMUNITY_Y))
    he_state = 'river'

def he_do_showdown(now):
    global he_state, he_winner, he_player_hand_name, he_dealer_hand_name
    global he_player_money, he_pot, he_mensaje, he_stats
    global poker_player_money, he_ai_hand_names, he_ai_winner
    for ai_i, ai_hand in enumerate(he_ai_cards):
        if not he_ai_folded[ai_i]:
            for entry in ai_hand:
                entry[4].start_flip(now, to_back=False)
                entry[4].oculta = False
    pc = [(e[0],e[1],e[2],e[3]) for e in he_player_cards]
    cc = [(e[0],e[1],e[2],e[3]) for e in he_community_cards]
    ps, pn = evaluate_holdem_hand(pc + cc)
    he_player_hand_name = pn; he_dealer_hand_name = ""
    ai_scores = []
    active_ai_indices = []
    for ai_i, ai_hand in enumerate(he_ai_cards):
        if he_ai_folded[ai_i]:
            he_ai_hand_names[ai_i] = ""
            ai_scores.append(None)
        else:
            ac = [(e[0],e[1],e[2],e[3]) for e in ai_hand]
            a_sc, a_nm = evaluate_holdem_hand(ac + cc)
            he_ai_hand_names[ai_i] = a_nm
            ai_scores.append(a_sc)
            active_ai_indices.append(ai_i)
    active_scores = [ai_scores[i] for i in active_ai_indices]
    all_active = [ps] + active_scores
    best_score = max(all_active)
    he_ai_winner = False
    if ps == best_score and all(ps >= s for s in active_scores):
        if all(ps == s for s in active_scores):
            he_winner = 'tie'; he_player_money += he_pot // len(all_active)
            he_mensaje = f"Empate — {pn}"
            he_stats['tied'] += 1
        else:
            he_winner = 'player'; he_player_money += he_pot
            he_mensaje = f"¡Ganaste! {pn}  (+{he_pot} fichas)"
            he_stats['won'] += 1
            spawn_particles(ANCHO//2, ALTO//2, DORADO, count=55)
            overlay_flash.update({'active':True,'color':(255,220,0),'alpha':200,'start':now,'duration':400})
    else:
        he_ai_winner = True
        he_winner = 'dealer'
        winners = [HE_AI_NAMES[i] for i in active_ai_indices if ai_scores[i] == best_score]
        he_mensaje = f"{', '.join(winners)} gana. Tu mano: {pn}"
        he_stats['lost'] += 1
        spawn_particles(ANCHO//2, ALTO//2, ROJO, count=30)
        overlay_flash.update({'active':True,'color':(150,0,0),'alpha':180,'start':now,'duration':350})
    poker_player_money = he_player_money
    he_stats['played'] += 1
    he_state = 'result'

def _he_all_folded_win(now):
    """All AI players folded — player wins the pot without showdown."""
    global he_state, he_winner, he_mensaje, he_stats, he_player_money, poker_player_money
    he_winner = 'player'
    he_player_money += he_pot
    poker_player_money = he_player_money
    he_mensaje = f"¡Todos se retiraron! Ganas el bote (+{he_pot} fichas)"
    he_stats['won'] += 1; he_stats['played'] += 1
    spawn_particles(ANCHO//2, ALTO//2, DORADO, count=55)
    overlay_flash.update({'active':True,'color':(255,220,0),'alpha':200,'start':now,'duration':400})
    he_state = 'result'

def he_fold(now):
    global he_state, he_winner, he_mensaje, he_stats, poker_player_money
    he_winner = 'fold'; he_state = 'result'
    he_mensaje = "Te has retirado. Pierdes la ciega."
    he_stats['played'] += 1; he_stats['lost'] += 1
    overlay_flash.update({'active':True,'color':(100,0,0),'alpha':140,'start':now,'duration':280})

def he_player_check_or_call(now):
    """Player checks or calls. If responding to an AI raise → advance street directly."""
    global he_pot, he_street_bet, he_player_money, poker_player_money
    if he_street_bet > 0:
        call_amt = min(he_street_bet, he_player_money)
        he_player_money -= call_amt; poker_player_money = he_player_money
        he_pot += call_amt
        he_street_bet = 0
        _advance_street(now)
    else:
        he_street_bet = 0
        _he_start_ai_turns(now)

def he_player_raise(amount, now):
    """Player raises by `amount`. Dealer + 4 AI players call."""
    global he_pot, he_street_bet, he_player_money, poker_player_money
    amount = max(1, min(amount, he_player_money))
    he_player_money -= amount; he_pot += amount * 5  
    poker_player_money = he_player_money
    he_street_bet = 0
    _he_start_ai_turns(now)

def _advance_street(now):
    global he_state
    if he_state == 'pre_flop': he_do_flop(now)
    elif he_state == 'flop':   he_do_turn(now)
    elif he_state == 'turn':   he_do_river(now)
    elif he_state == 'river':  he_do_showdown(now)

def _draw_he_btn(label, rect, col_normal, col_hover, mouse_pos, border=NEGRO):
    hov = rect.collidepoint(mouse_pos)
    col = col_hover if hov else col_normal
    pygame.draw.rect(VENTANA, col, rect, border_radius=9)
    pygame.draw.rect(VENTANA, border, rect, 2, border_radius=9)
    ts = FUENTE_PEQUENA.render(label, True, BLANCO)
    VENTANA.blit(ts, (rect.centerx - ts.get_width()//2, rect.centery - ts.get_height()//2))
    return hov

def _render_poker(now):
    global he_blind_input, he_raise_input, he_in_raise, he_state
    global he_player_money, he_pot, he_street_bet, he_mensaje
    global poker_player_money, he_raise_btn

    mouse_pos = to_logical(pygame.mouse.get_pos())

    VENTANA.fill((8, 52, 8))
    for y in range(0, ALTO, 38):
        pygame.draw.line(VENTANA, (6, 44, 6), (0, y), (ANCHO, y), 1)
    for x in range(0, ANCHO, 38):
        pygame.draw.line(VENTANA, (6, 44, 6), (x, 0), (x, ALTO), 1)
    pygame.draw.ellipse(VENTANA, (12, 80, 12), (180, 80, ANCHO-360, ALTO-160))
    pygame.draw.ellipse(VENTANA, DORADO,       (180, 80, ANCHO-360, ALTO-160), 3)
    pygame.draw.ellipse(VENTANA, (8, 60, 8),   (210, 98, ANCHO-420, ALTO-196), 1)

    title_s = FUENTE_PEQUENA.render("♠  TEXAS HOLD'EM  ♠", True, DORADO)
    VENTANA.blit(title_s, (ANCHO//2 - title_s.get_width()//2, 38))

    pl = FUENTE_PEQUENA.render("TÚ", True, (180, 240, 190))
    VENTANA.blit(pl, (ANCHO//2 - pl.get_width()//2, HE_PLAYER_Y - 30))

    if he_state not in ('betting',):
        cl = _FUENTE_HE_SMALL.render("CARTAS COMUNITARIAS", True, (180, 160, 80))
        VENTANA.blit(cl, (ANCHO//2 - cl.get_width()//2, HE_COMMUNITY_Y - 26))

    if he_state not in ('betting',):
        for i in range(5):
            sx = _he_card_x(i, 5); sy = HE_COMMUNITY_Y
            slot = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
            slot.fill((0, 0, 0, 60))
            VENTANA.blit(slot, (sx, sy))
            pygame.draw.rect(VENTANA, (80, 120, 80), (sx, sy, CARD_W, CARD_H), 1, border_radius=10)

    if he_state not in ('betting',):
        for ai_i, (ax, ay) in enumerate(HE_AI_POSITIONS):
            name = HE_AI_NAMES[ai_i]
            folded = he_ai_folded[ai_i] if ai_i < len(he_ai_folded) else False
            if folded:
                name_col = (100, 80, 80)
            elif he_state == 'result' and he_ai_hand_names[ai_i]:
                name_col = (255, 160, 160)
            else:
                name_col = (220, 180, 100)
            name_s = _FUENTE_HE_SMALL.render(name, True, name_col)
            VENTANA.blit(name_s, (ax, ay - 22))
            if folded:
                total_w = 2 * CARD_W + HE_AI_CARD_GAP - CARD_W
                fold_bg = pygame.Surface((total_w, CARD_H), pygame.SRCALPHA)
                fold_bg.fill((0, 0, 0, 60))
                VENTANA.blit(fold_bg, (ax, ay))
                pygame.draw.rect(VENTANA, (80, 50, 50), (ax, ay, total_w, CARD_H), 1, border_radius=8)
                fold_s = _FUENTE_HE_SMALL.render("RETIRADO", True, (140, 80, 80))
                VENTANA.blit(fold_s, (ax + total_w // 2 - fold_s.get_width() // 2,
                                      ay + CARD_H // 2 - fold_s.get_height() // 2))
            else:
                for ci in range(2):
                    if ci < len(he_ai_cards[ai_i]):
                        c = he_ai_cards[ai_i][ci][4]
                        c.actualizar(now); c.dibujar(now)
                    else:
                        slot2 = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
                        slot2.fill((0, 0, 0, 50))
                        VENTANA.blit(slot2, (ax + ci * HE_AI_CARD_GAP, ay))
                        pygame.draw.rect(VENTANA, (60, 100, 60),
                                         (ax + ci * HE_AI_CARD_GAP, ay, CARD_W, CARD_H), 1, border_radius=8)
                if he_state == 'result' and he_ai_hand_names[ai_i]:
                    hn_s = _FUENTE_HE_SMALL.render(he_ai_hand_names[ai_i], True, (255, 200, 180))
                    VENTANA.blit(hn_s, (ax, ay + CARD_H + 6))

    for i, entry in enumerate(he_community_cards):
        c = entry[4]
        c.target_scale = 1.12 if pygame.Rect(int(c.x), int(c.y), CARD_W, CARD_H).collidepoint(mouse_pos) else 1.0
        c.actualizar(now); c.dibujar(now)
    for i, entry in enumerate(he_player_cards):
        c = entry[4]
        c.target_scale = 1.12 if pygame.Rect(int(c.x), int(c.y), CARD_W, CARD_H).collidepoint(mouse_pos) else 1.0
        c.actualizar(now); c.dibujar(now)

    if he_state not in ('betting',) and he_player_cards and he_community_cards:
        pc_live = [(e[0],e[1],e[2],e[3]) for e in he_player_cards]
        cc_live = [(e[0],e[1],e[2],e[3]) for e in he_community_cards]
        _, live_name = evaluate_holdem_hand(pc_live + cc_live)
        hand_rank = {n: i for i, n in enumerate([
            'Carta Alta','Pareja','Doble Pareja','Trío','Escalera',
            'Color','Full House','Póker (4 iguales)','Escalera de Color','Escalera Real'
        ])}
        rank_val = hand_rank.get(live_name, 0)
        if rank_val >= 7:
            live_col = (255, 220, 0)
        elif rank_val >= 4:
            live_col = (120, 255, 120)
        elif rank_val >= 2:
            live_col = (180, 220, 255)
        else:
            live_col = (200, 200, 200)
        combo_bg = pygame.Surface((340, 32), pygame.SRCALPHA)
        combo_bg.fill((0, 0, 0, 170))
        combo_x = ANCHO // 2 - 170
        combo_y = HE_PLAYER_Y + CARD_H + 8
        VENTANA.blit(combo_bg, (combo_x, combo_y))
        pygame.draw.rect(VENTANA, live_col, (combo_x, combo_y, 340, 32), 1, border_radius=6)
        combo_lbl = FUENTE_PEQUENA.render(f"Tu mano: {live_name}", True, live_col)
        VENTANA.blit(combo_lbl, (ANCHO//2 - combo_lbl.get_width()//2, combo_y + 4))

    if he_state not in ('betting',):
        pot_s = FUENTE_PEQUENA.render(f"BOTE: {he_pot} fichas", True, DORADO)
        pot_bg = pygame.Surface((pot_s.get_width()+24, pot_s.get_height()+10), pygame.SRCALPHA)
        pot_bg.fill((0,0,0,160))
        px2 = ANCHO//2 - pot_bg.get_width()//2
        py2 = HE_COMMUNITY_Y + CARD_H + 14
        VENTANA.blit(pot_bg, (px2, py2))
        VENTANA.blit(pot_s, (px2+12, py2+5))

    if he_state == 'result' and he_player_hand_name:
        phn_s = FUENTE_PEQUENA.render(f"Tu mano: {he_player_hand_name}", True, (180, 255, 180))
        VENTANA.blit(phn_s, (ANCHO//2 - phn_s.get_width()//2, HE_PLAYER_Y + CARD_H + 10))

    box_w = 960; pad = 16; lh = 32
    box_h = 130; bx = (ANCHO - box_w) // 2; by = ALTO - box_h - 14
    bg_s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    bg_s.fill((0, 0, 0, 190))
    VENTANA.blit(bg_s, (bx, by))
    pygame.draw.rect(VENTANA, NEGRO, (bx, by, box_w, box_h), 2, border_radius=10)

    y_o = by + pad
    chips_s = FUENTE_PEQUENA.render(f"Fichas: {he_player_money}", True, DORADO)
    VENTANA.blit(chips_s, (bx + pad, y_o))

    if he_state == 'betting':
        inp_lbl = FUENTE_PEQUENA.render("Ciega:", True, BLANCO)
        VENTANA.blit(inp_lbl, (bx + pad, y_o + lh))
        inp_w = 200; inp_h = 34
        inp_x = bx + pad + inp_lbl.get_width() + 12
        inp_bg = pygame.Surface((inp_w, inp_h), pygame.SRCALPHA)
        inp_bg.fill((20, 20, 20, 230))
        VENTANA.blit(inp_bg, (inp_x, y_o + lh - 4))
        pygame.draw.rect(VENTANA, NEGRO, (inp_x, y_o + lh - 4, inp_w, inp_h), 2, border_radius=6)
        disp = clip_text_right(he_blind_input if he_blind_input else str(he_blind), FUENTE_PEQUENA, inp_w-12)
        dt = FUENTE_PEQUENA.render(disp, True, BLANCO)
        VENTANA.blit(dt, (inp_x + 8, y_o + lh + (inp_h - dt.get_height())//2 - 4))
        hint = FUENTE_INSTR.render("ENTER para repartir · Todos postean la ciega · Máx "+str(BET_MAX_HOLDEM), True, (160,160,160))
        VENTANA.blit(hint, (bx + (box_w - hint.get_width())//2, y_o + lh*2 + 4))

    elif he_state in ('pre_flop', 'flop', 'turn', 'river'):
        street_labels = {'pre_flop': 'PRE-FLOP', 'flop': 'FLOP', 'turn': 'TURN', 'river': 'RIVER'}
        sl = FUENTE_PEQUENA.render(street_labels.get(he_state,''), True, (220, 200, 120))
        VENTANA.blit(sl, (bx + pad, y_o + lh))

        if he_ai_turn_active:
            cur_name = HE_AI_NAMES[he_ai_turn_idx] if he_ai_turn_idx < len(HE_AI_NAMES) else ""
            if he_ai_turn_phase == 'announcing':
                turn_txt = f"▶  Le toca a  {cur_name}"
                turn_col = (255, 220, 80)
            else:
                last_action = he_ai_actions[-1] if he_ai_actions else ""
                turn_txt = f"✓  {last_action}"
                turn_col = (120, 255, 160)
            turn_surf = FUENTE_MSG.render(turn_txt, True, turn_col)
            turn_bg = pygame.Surface((turn_surf.get_width() + 40, turn_surf.get_height() + 16), pygame.SRCALPHA)
            turn_bg.fill((0, 0, 0, 210))
            tx = ANCHO // 2 - turn_bg.get_width() // 2
            ty = by - turn_bg.get_height() - 12
            VENTANA.blit(turn_bg, (tx, ty))
            pygame.draw.rect(VENTANA, turn_col, (tx, ty, turn_bg.get_width(), turn_bg.get_height()), 2, border_radius=10)
            VENTANA.blit(turn_surf, (tx + 20, ty + 8))
            if he_ai_actions:
                log_y = ty - len(he_ai_actions) * 26 - 8
                for log_line in he_ai_actions:
                    log_s = _FUENTE_HE_SMALL.render(log_line, True, (200, 200, 200))
                    log_bg = pygame.Surface((log_s.get_width() + 20, log_s.get_height() + 6), pygame.SRCALPHA)
                    log_bg.fill((0, 0, 0, 160))
                    lx = ANCHO // 2 - log_bg.get_width() // 2
                    VENTANA.blit(log_bg, (lx, log_y))
                    VENTANA.blit(log_s, (lx + 10, log_y + 3))
                    log_y += 26
        elif he_in_raise:
            rl = FUENTE_PEQUENA.render("Sube (+fichas):", True, BLANCO)
            VENTANA.blit(rl, (bx + pad, y_o + lh*2))
            inp_x = bx + pad + rl.get_width() + 12; inp_w = 200; inp_h = 32
            inp_bg = pygame.Surface((inp_w, inp_h), pygame.SRCALPHA)
            inp_bg.fill((30, 20, 0, 230))
            VENTANA.blit(inp_bg, (inp_x, y_o + lh*2 - 2))
            pygame.draw.rect(VENTANA, DORADO, (inp_x, y_o + lh*2 - 2, inp_w, inp_h), 2, border_radius=6)
            dt = FUENTE_PEQUENA.render(clip_text_right(he_raise_input, FUENTE_PEQUENA, inp_w-12), True, BLANCO)
            VENTANA.blit(dt, (inp_x + 8, y_o + lh*2 + (inp_h - dt.get_height())//2 - 2))
            cancel_s = FUENTE_INSTR.render("ENTER para confirmar · ESC para cancelar", True, (180,160,100))
            VENTANA.blit(cancel_s, (bx + (box_w - cancel_s.get_width())//2, y_o + lh*3))
        else:
            btn_w = 230; btn_h = 38; gap = 18
            total_bw = 3*btn_w + 2*gap; bx_btns = ANCHO//2 - total_bw//2
            by_btns = by + box_h - btn_h - pad
            fold_r  = pygame.Rect(bx_btns,               by_btns, btn_w, btn_h)
            call_r  = pygame.Rect(bx_btns+btn_w+gap,     by_btns, btn_w, btn_h)
            he_raise_btn.update(bx_btns+2*(btn_w+gap), by_btns, btn_w, btn_h)
            _draw_he_btn("F: Retirarse",  fold_r,  (120,30,30), (180,50,50), mouse_pos)
            call_lbl = "C: Check" if he_street_bet == 0 else f"C: Igualar ({he_street_bet}) — ¡alguien subió!"
            _draw_he_btn(call_lbl, call_r, (30,80,140), (50,120,200), mouse_pos)
            _draw_he_btn("SUBIR",  he_raise_btn, (120,90,0), (200,150,0), mouse_pos, border=DORADO)
            hint2 = FUENTE_INSTR.render("F=Retirarse  C=Check/Igualar  Click SUBIR para apostar más", True, (120,120,120))
            VENTANA.blit(hint2, (bx + (box_w - hint2.get_width())//2, y_o + lh))

    elif he_state == 'result':
        res_col = DORADO if he_winner == 'player' else (ROJO if he_winner in ('dealer','fold') else (200,200,200))
        msg_s = FUENTE_MSG.render(he_mensaje, True, res_col)
        VENTANA.blit(msg_s, (ANCHO//2 - msg_s.get_width()//2, by + (box_h - msg_s.get_height())//2 - 10))
        hint3 = FUENTE_INSTR.render("ENTER / S para siguiente mano", True, (140,140,140))
        VENTANA.blit(hint3, (ANCHO//2 - hint3.get_width()//2, by + box_h - hint3.get_height() - 8))

    st_s = _FUENTE_HE_SMALL.render(
        f"G:{he_stats['won']} P:{he_stats['lost']} E:{he_stats['tied']}", True, (160,160,160))
    VENTANA.blit(st_s, (bx + box_w - st_s.get_width() - pad, y_o))

    _draw_he_btn("ESC: Menú",    he_menu_btn,      (30,70,140), (50,110,200), mouse_pos)
    _draw_he_btn("R: Reiniciar", he_reiniciar_btn, (140,30,30), (200,55,55), mouse_pos)

    if he_player_money <= 0 and he_state == 'betting':
        rb = FUENTE_PEQUENA.render("Sin fichas — pulsa R para reiniciar", True, ROJO)
        VENTANA.blit(rb, (ANCHO//2 - rb.get_width()//2, ALTO//2))


def _start_poker_mode():
    global app_state, game_mode
    game_mode = 'poker'
    app_state = 'poker'
    he_reiniciar()


MENU_OPTIONS = [
    {'label': 'Modo Historia',     'sub': 'Blackjack narrativo · Barcelona 1987 · Empieza con 1.000 fichas'},
    {'label': 'BlackJack',         'sub': 'Blackjack infinito · Sin historia · Empieza con 5.000 fichas'},
    {'label': 'Texas Hold\'em',    'sub': 'Poker Texas Hold\'em · Ciegas, flop, turn y river · Empieza con 3.000 fichas'},
]

FUENTE_MENU_TITLE = pygame.font.SysFont("arial", 92, bold=True)
FUENTE_MENU_OPT   = pygame.font.SysFont("arial", 44, bold=True)
FUENTE_MENU_SUB   = pygame.font.SysFont("arial", 24)


def _render_main_menu(now):
    """Draw the main menu screen."""
    global main_menu_hovered
    VENTANA.fill((6, 4, 14))
    draw_rain(VENTANA, now, alpha=55)

    t_surf = FUENTE_MENU_TITLE.render("El Farol Rojo", True, DORADO)
    t_x = (ANCHO - t_surf.get_width()) // 2
    VENTANA.blit(t_surf, (t_x, 120))

    sub_surf = FUENTE_SUBTITLE.render("Blackjack · Barcelona · 1987", True, (160, 140, 90))
    VENTANA.blit(sub_surf, ((ANCHO - sub_surf.get_width()) // 2, 230))

    pygame.draw.line(VENTANA, DORADO, (ANCHO//2 - 340, 310), (ANCHO//2 + 340, 310), 1)

    mouse_pos = to_logical(pygame.mouse.get_pos())
    main_menu_hovered = -1
    btn_start_y = 380
    btn_h = 110
    btn_w = 860
    gap = 24

    for i, opt in enumerate(MENU_OPTIONS):
        bx = (ANCHO - btn_w) // 2
        by = btn_start_y + i * (btn_h + gap)
        rect = pygame.Rect(bx, by, btn_w, btn_h)
        hovered = rect.collidepoint(mouse_pos)
        if hovered:
            main_menu_hovered = i

        bg_alpha = 210 if hovered else 160
        bg_col = (55, 95, 68) if hovered else (22, 36, 26)
        bg_s = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        bg_s.fill((*bg_col, bg_alpha))
        VENTANA.blit(bg_s, (bx, by))
        border_col = DORADO if hovered else (70, 110, 80)
        pygame.draw.rect(VENTANA, border_col, rect, 2, border_radius=10)

        num_s = FUENTE_MENU_OPT.render(f"[{i+1}]", True, DORADO)
        VENTANA.blit(num_s, (bx + 24, by + (btn_h - num_s.get_height()) // 2))

        lbl_col = (220, 255, 225) if hovered else BLANCO
        lbl_s = FUENTE_MENU_OPT.render(opt['label'], True, lbl_col)
        VENTANA.blit(lbl_s, (bx + 90, by + 20))
        sub_s = FUENTE_MENU_SUB.render(opt['sub'], True, (160, 190, 165) if hovered else (120, 140, 125))
        VENTANA.blit(sub_s, (bx + 92, by + 20 + lbl_s.get_height() + 4))

    hint = FUENTE_INSTR.render("Pulsa 1 · 2  o  haz clic para seleccionar", True, (90, 80, 60))
    VENTANA.blit(hint, ((ANCHO - hint.get_width()) // 2, btn_start_y + len(MENU_OPTIONS) * (btn_h + gap) + 18))

    ver_s = FUENTE_INSTR.render(f"v{VERSION}", True, (60, 55, 45))
    VENTANA.blit(ver_s, (ANCHO - ver_s.get_width() - 14, ALTO - ver_s.get_height() - 10))


_pause_started_at = 0

def _resume_game():
    """Reanuda el juego compensando todos los timers por el tiempo en pausa."""
    global paused, next_deal, next_action, round_end_time, _pause_started_at
    elapsed = pygame.time.get_ticks() - _pause_started_at
    if next_deal   > 0: next_deal   += elapsed
    if next_action > 0: next_action += elapsed
    if round_end_time > 0: round_end_time += elapsed
    paused = False


def _render_pause_menu(now):
    """Dibuja el menú de pausa encima de la partida en curso."""
    global paused, app_state

    dim = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 195))
    VENTANA.blit(dim, (0, 0))

    BOX_W = 700; BOX_H = 420
    BOX_X = (ANCHO - BOX_W) // 2; BOX_Y = ALTO // 2 - BOX_H // 2 - 30
    box_bg = pygame.Surface((BOX_W, BOX_H), pygame.SRCALPHA)
    box_bg.fill((8, 14, 8, 240))
    VENTANA.blit(box_bg, (BOX_X, BOX_Y))
    pygame.draw.rect(VENTANA, DORADO, (BOX_X, BOX_Y, BOX_W, BOX_H), 2, border_radius=14)
    pygame.draw.rect(VENTANA, (80, 65, 30), (BOX_X+6, BOX_Y+6, BOX_W-12, BOX_H-12), 1, border_radius=10)

    title_surf = FUENTE_GRANDE.render("PAUSA", True, DORADO)
    VENTANA.blit(title_surf, (ANCHO // 2 - title_surf.get_width() // 2, BOX_Y + 28))
    pygame.draw.line(VENTANA, (80, 65, 30),
                     (BOX_X + 40, BOX_Y + 28 + title_surf.get_height() + 8),
                     (BOX_X + BOX_W - 40, BOX_Y + 28 + title_surf.get_height() + 8), 1)

    mouse_pos = to_logical(pygame.mouse.get_pos())
    BTN_W = 560; BTN_H = 88; GAP = 22
    BX = (ANCHO - BTN_W) // 2
    BY0 = ALTO // 2 - 20          
    BY1 = BY0 + BTN_H + GAP       

    pause_opts = [
        ("[1]  Continuar", BY0, False),
        ("[2]  Menú Principal", BY1, True),
    ]
    for label, by, goes_menu in pause_opts:
        rect = pygame.Rect(BX, by, BTN_W, BTN_H)
        hovered = rect.collidepoint(mouse_pos)
        bg_col = (55, 95, 68) if (hovered and not goes_menu) else \
                 (100, 30, 30) if (hovered and goes_menu) else (22, 36, 26)
        bg_s = pygame.Surface((BTN_W, BTN_H), pygame.SRCALPHA)
        bg_s.fill((*bg_col, 225))
        VENTANA.blit(bg_s, (BX, by))
        border_col = DORADO if hovered else (70, 110, 80)
        pygame.draw.rect(VENTANA, border_col, rect, 2, border_radius=10)
        lbl_col = (220, 255, 225) if (hovered and not goes_menu) else \
                  (255, 180, 180) if (hovered and goes_menu) else BLANCO
        lbl = FUENTE_MENU_OPT.render(label, True, lbl_col)
        VENTANA.blit(lbl, (BX + (BTN_W - lbl.get_width()) // 2,
                            by + (BTN_H - lbl.get_height()) // 2))

    hint = FUENTE_INSTR.render("ESC para reanudar  ·  1 / 2 o clic para elegir", True, (90, 80, 60))
    VENTANA.blit(hint, (ANCHO // 2 - hint.get_width() // 2, BY1 + BTN_H + 22))


def _start_story_mode():
    global app_state, game_mode, story_scenes_data, story_scene_idx, story_line_idx
    global player_money, current_bet, current_bet_input, last_bet, stats, epic_win_triggered
    global difficulty_level, EPIC_WIN_THRESHOLD, rosa_secret_done
    global story_choice_active, story_choice_options, story_choice_rects
    global story_injected_lines, story_injected_idx, story_in_injection
    game_mode = 'story'
    player_money = 1000; current_bet = 10; current_bet_input = ""; last_bet = None
    stats = {'played':0,'won':0,'lost':0,'blackjacks':0}; epic_win_triggered = False
    difficulty_level = 0; EPIC_WIN_THRESHOLD = 10000; rosa_secret_done = False
    story_scenes_data = INTRO_SCENES; story_scene_idx = 0; story_line_idx = 0
    story_choice_active = False; story_choice_options = []; story_choice_rects = []
    story_injected_lines = []; story_injected_idx = 0; story_in_injection = False
    app_state = 'intro'


def _start_infinite_mode():
    global app_state, game_mode
    game_mode = 'infinite'
    app_state = 'blackjack'
    bj_reiniciar()


while True:
    RELOJ.tick(60)
    now = pygame.time.get_ticks()

    if update_status == 'restarting' and update_restart_time != 0:
        if now >= update_restart_time + 2000:
            pygame.quit(); os.execv(sys.executable, [sys.executable]+sys.argv)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            if paused:
                _resume_game()          
            elif app_state in ('game', 'blackjack'):
                paused = True; _pause_started_at = now  
            elif app_state == 'poker':
                app_state = 'main_menu'
            elif app_state in ('intro', 'win_ending', 'lose_ending'):
                app_state = 'main_menu' 
            else:
                pygame.quit(); sys.exit()

        if paused:
            _PAUSE_BTN_W = 560; _PAUSE_BTN_H = 88; _PAUSE_GAP = 22
            _PAUSE_BX    = (ANCHO - _PAUSE_BTN_W) // 2
            _PAUSE_BY0   = ALTO // 2 - 20
            _PAUSE_BY1   = _PAUSE_BY0 + _PAUSE_BTN_H + _PAUSE_GAP 
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                lpos = to_logical(evento.pos)
                if pygame.Rect(_PAUSE_BX, _PAUSE_BY0, _PAUSE_BTN_W, _PAUSE_BTN_H).collidepoint(lpos):
                    _resume_game()
                elif pygame.Rect(_PAUSE_BX, _PAUSE_BY1, _PAUSE_BTN_W, _PAUSE_BTN_H).collidepoint(lpos):
                    _resume_game(); app_state = 'main_menu'
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1: _resume_game()
                elif evento.key == pygame.K_2: _resume_game(); app_state = 'main_menu'
            continue

        if app_state == 'main_menu':
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1: _start_story_mode()
                elif evento.key == pygame.K_2: _start_infinite_mode()
                elif evento.key == pygame.K_3: _start_poker_mode()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                lpos = to_logical(evento.pos)
                btn_w = 860; btn_h = 110; gap = 24; btn_start_y = 380
                for i in range(len(MENU_OPTIONS)):
                    bx = (ANCHO - btn_w) // 2
                    by = btn_start_y + i * (btn_h + gap)
                    if pygame.Rect(bx, by, btn_w, btn_h).collidepoint(lpos):
                        if i == 0: _start_story_mode()
                        elif i == 1: _start_infinite_mode()
                        elif i == 2: _start_poker_mode()
            continue

        if app_state == 'poker':
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                if he_in_raise:
                    he_in_raise = False
                else:
                    app_state = 'main_menu'
                continue
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                lpos = to_logical(evento.pos)
                if he_menu_btn.collidepoint(lpos):
                    app_state = 'main_menu'; continue
                if he_reiniciar_btn.collidepoint(lpos):
                    he_reiniciar(); continue
                if he_state in ('pre_flop','flop','turn','river') and not he_in_raise and not he_ai_turn_active:
                    if he_raise_btn.collidepoint(lpos):
                        he_in_raise = True; he_raise_input = ""; continue
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    he_reiniciar(); continue
                if he_state == 'betting':
                    if evento.key == pygame.K_BACKSPACE:
                        he_blind_input = he_blind_input[:-1]
                    elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        try:
                            val = int(he_blind_input) if he_blind_input.strip() else he_blind
                            if val <= 0: pass
                            elif val > BET_MAX_HOLDEM: he_mensaje = f"Máx. {BET_MAX_HOLDEM}"
                            elif val*2 > he_player_money: he_mensaje = "Fichas insuficientes para la ciega"
                            else:
                                he_blind = val
                                he_player_money -= he_blind; poker_player_money = he_player_money
                                he_blind_input = ""
                                he_start_hand(now)
                        except ValueError:
                            he_mensaje = "Ciega inválida"
                    elif evento.unicode and evento.unicode.isdigit():
                        if len(he_blind_input) < 6: he_blind_input += evento.unicode
                elif he_state in ('pre_flop','flop','turn','river'):
                    if he_ai_turn_active:
                        pass 
                    elif he_in_raise:
                        if evento.key == pygame.K_BACKSPACE:
                            he_raise_input = he_raise_input[:-1]
                        elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            try:
                                amt = int(he_raise_input) if he_raise_input.strip() else 0
                                if amt > 0 and amt <= he_player_money:
                                    he_in_raise = False; he_player_raise(amt, now)
                                else:
                                    he_mensaje = "Cantidad inválida"
                            except ValueError:
                                he_mensaje = "Número inválido"
                        elif evento.key == pygame.K_ESCAPE:
                            he_in_raise = False
                        elif evento.unicode and evento.unicode.isdigit():
                            if len(he_raise_input) < 6: he_raise_input += evento.unicode
                    else:
                        if evento.key == pygame.K_f:
                            he_fold(now)
                        elif evento.key in (pygame.K_c, pygame.K_RETURN, pygame.K_KP_ENTER):
                            he_player_check_or_call(now)
                elif he_state == 'result':
                    if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_s):
                        if he_player_money <= 0:
                            he_reiniciar()
                        else:
                            he_player_money -= he_blind; poker_player_money = he_player_money
                            he_start_hand(now)
            continue

        if app_state == 'blackjack':
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                lpos = to_logical(evento.pos)
                if bj_menu_btn.collidepoint(lpos):
                    app_state = 'main_menu'; continue
                if REINICIAR_BTN.collidepoint(lpos):
                    bj_reiniciar(); continue
                if DOTS_BTN.collidepoint(lpos):
                    if update_status != 'checking':
                        update_status = 'checking'; update_msg = "Comprobando..."
                        update_notif_time = pygame.time.get_ticks()
                        threading.Thread(target=_check_for_updates, daemon=True).start()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                bj_reiniciar(); continue

        if app_state in ('intro','win_ending','lose_ending'):
            if story_choice_active:
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    lpos = to_logical(evento.pos)
                    for i, rect in enumerate(story_choice_rects):
                        if rect.collidepoint(lpos) and i < len(story_choice_options):
                            _apply_choice(i)
                            break
                if evento.type == pygame.KEYDOWN:
                    key_idx = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3}.get(evento.key, -1)
                    if 0 <= key_idx < len(story_choice_options):
                        _apply_choice(key_idx)
            else:
                advance = False
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE: advance = True
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:   advance = True
                if advance: _story_advance()
            continue

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            lpos = to_logical(evento.pos)
            if REINICIAR_BTN.collidepoint(lpos):
                reiniciar_partida(); continue
            if DOTS_BTN.collidepoint(lpos):
                if update_status != 'checking':
                    update_status = 'checking'; update_msg = "Comprobando..."
                    update_notif_time = pygame.time.get_ticks()
                    threading.Thread(target=_check_for_updates, daemon=True).start()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                reiniciar_partida(); continue

            if state == 'game_over':
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    reiniciar_partida()
                continue

            if evento.key == pygame.K_m:
                TABLE_STYLE_IDX = (TABLE_STYLE_IDX+1) % len(TABLE_STYLES)

            if state == 'betting':
                if evento.key == pygame.K_BACKSPACE:
                    current_bet_input = current_bet_input[:-1]
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_s):
                    try:
                        if current_bet_input.strip() == "":
                            if last_bet is None:
                                mensaje = "Escribe una apuesta"; round_end_time = now
                            else:
                                bet_val = int(last_bet)
                                if   bet_val <= 0:            mensaje = "Apuesta inválida"; round_end_time = now
                                elif bet_val > BET_MAX:       mensaje = f"Apuesta máx. {BET_MAX}"; round_end_time = now
                                elif bet_val > player_money:  mensaje = "No tienes suficiente dinero"; round_end_time = now
                                else:
                                    current_bet = bet_val; player_money -= current_bet; bet_locked = True
                                    state = 'dealing'; dealing_step = 0; next_deal = now+300; mensaje = ""
                                    placed_chip = create_placed_chip(current_bet, ANCHO//2, ALTO-120)
                                    current_bet_input = ""
                        else:
                            bet_val = int(current_bet_input)
                            if   bet_val <= 0:            mensaje = "Apuesta inválida"; round_end_time = now
                            elif bet_val > BET_MAX:       mensaje = f"Apuesta máx. {BET_MAX}"; round_end_time = now
                            elif bet_val > player_money:  mensaje = "No tienes suficiente dinero"; round_end_time = now
                            else:
                                current_bet = bet_val; player_money -= current_bet; bet_locked = True
                                state = 'dealing'; dealing_step = 0; next_deal = now+300; mensaje = ""
                                placed_chip = create_placed_chip(current_bet, ANCHO//2, ALTO-120)
                                last_bet = current_bet; current_bet_input = ""
                    except ValueError:
                        mensaje = "Apuesta inválida"; round_end_time = now
                else:
                    if evento.unicode and evento.unicode.isdigit():
                        if len(current_bet_input) < 6: current_bet_input += evento.unicode

            elif state == 'player':
                if evento.key == pygame.K_d:
                    hand = get_current_hand()
                    if split_active and not doubledown_flags:
                        doubledown_flags = [False]*len(jugador_hands)
                    can_double = False
                    if split_active:
                        can_double = (len(hand)==2 and
                                      player_money>=(per_hand_bets[current_hand_index] if per_hand_bets else current_bet) and
                                      (not doubledown_flags[current_hand_index]))
                    else:
                        can_double = (len(hand)==2 and player_money>=current_bet and (not doubledown_flags))
                    if can_double:
                        if split_active:
                            bet_to_deduct = per_hand_bets[current_hand_index] if per_hand_bets else current_bet
                            player_money -= bet_to_deduct; doubledown_flags[current_hand_index] = True
                            if per_hand_bets: per_hand_bets[current_hand_index] *= 2
                            else: per_hand_bets = [current_bet, current_bet]; per_hand_bets[current_hand_index] *= 2
                            dest_y2 = 200+current_hand_index*70; repartir(hand, dest_y2)
                            if current_hand_index < len(jugador_hands)-1: current_hand_index += 1
                            else:
                                state = 'dealer'; revelar_banca(now); dealer_thinking = False
                                dealer_target = schedule_dealer_target(); next_action = now+600
                        else:
                            player_money -= current_bet; current_bet *= 2; repartir(hand, 200)
                            state = 'dealer'; revelar_banca(now); dealer_thinking = False
                            dealer_target = schedule_dealer_target(); next_action = now+600

                if evento.key == pygame.K_p:
                    hand = get_current_hand()
                    if len(hand)==2 and (hand[0][2]==hand[1][2]) and player_money>=current_bet:
                        jugador_hands = [[],[]]
                        jugador_hands[0].append(hand[0]); jugador_hands[1].append(hand[1])
                        jugador[:] = jugador_hands[0]; split_active = True; current_hand_index = 0
                        player_money -= current_bet; last_bet = current_bet
                        per_hand_bets = [current_bet, current_bet]; doubledown_flags = [False, False]
                        state = 'player'
                        for i, h in enumerate(jugador_hands):
                            base_x2 = 120+i*HAND_SEP; dest_y3 = 200+i*70
                            for idx2, ct2 in enumerate(h):
                                c2 = ct2[4]; c2.dest_x = base_x2+idx2*CARD_SPACING; c2.dest_y = dest_y3
                                c2.target_scale = 1.06 if i==current_hand_index else 1.0
                                c2.oculta = False; c2.start_flip(now, to_back=False)

                if evento.key == pygame.K_i and insurance_offered and not insurance_taken:
                    insurance_bet = min(current_bet//2, player_money)
                    if insurance_bet > 0: player_money -= insurance_bet; insurance_taken = True

                if evento.key == pygame.K_SPACE:
                    if (now >= last_pedir_time+PEDIR_DELAY) and (not clearing):
                        dest_y4 = 200+current_hand_index*70 if (split_active and jugador_hands) else 200
                        repartir(get_current_hand(), dest_y4); last_pedir_time = now

                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if split_active:
                        if current_hand_index < len(jugador_hands)-1: current_hand_index += 1
                        else:
                            state = 'dealer'; revelar_banca(now); dealer_thinking = False
                            dealer_target = schedule_dealer_target(); next_action = now+600
                    else:
                        state = 'dealer'; revelar_banca(now); dealer_thinking = False
                        dealer_target = schedule_dealer_target(); next_action = now+600

            elif state == 'round_end':
                if evento.key == pygame.K_s:
                    if not clearing:
                        player_cards2 = sum(jugador_hands,[]) if jugador_hands else jugador
                        all_cards2 = banca + player_cards2
                        if not all_cards2: nueva_ronda()
                        else:
                            clearing_cards = list(all_cards2)
                            for ct3 in clearing_cards:
                                c3 = ct3[4]; c3.oculta = False; c3.start_flip(now, to_back=True)
                            clearing = True; clear_phase = 'flipping'

    if app_state == 'game':
        if player_money >= EPIC_WIN_THRESHOLD and not epic_win_triggered and state == 'betting':
            epic_win_triggered = True
            _start_story(build_win_ending_scenes(), 'win_ending')
        elif player_money <= 0 and state == 'betting' and not epic_win_triggered:
            _start_story(LOSE_ENDING_SCENES, 'lose_ending')

    if app_state == 'main_menu':
        _render_main_menu(now)
        flip_display()
        continue

    if app_state in ('intro','win_ending','lose_ending'):
        _render_story(now)
        flip_display()
        continue

    if app_state == 'poker' and he_ai_turn_active:
        _he_update_ai_turns(now)

    if app_state == 'poker':
        _render_poker(now)
        flip_display()
        continue

    if app_state == 'blackjack':
        _sync_bj_money()
        if player_money <= 0 and state == 'betting':
            player_money = 5000; bj_player_money = 5000
            stats = {'played':0,'won':0,'lost':0,'blackjacks':0}
            nueva_ronda()
    if state == 'game_over':
        VENTANA.fill((4, 2, 8))
        draw_rain(VENTANA, now, alpha=60)
        txt1 = FUENTE_GRANDE.render("Sin fichas... Víctor sonríe.", True, (210,70,25))
        txt2 = FUENTE.render("ENTER o R: volver a empezar con 1000 fichas", True, (180,148,90))
        VENTANA.blit(txt1, ((ANCHO - txt1.get_width())//2, ALTO//2 - 60))
        VENTANA.blit(txt2, ((ANCHO - txt2.get_width())//2, ALTO//2 + 20))
        flip_display()
        continue

    style = TABLE_STYLES[TABLE_STYLE_IDX]
    VENTANA.fill(style['color'])

    if DEALER_AVATAR:
        VENTANA.blit(DEALER_AVATAR, (ANCHO//2 - DEALER_AVATAR.get_width()//2, 0))

    if state == 'dealing' and (not clearing) and now >= next_deal and not paused:
        if dealing_step == 0:
            repartir(jugador, 200, start_pos=DECK_POS)
        elif dealing_step == 1:
            repartir(banca, 50, True, start_pos=DECK_POS)
        elif dealing_step == 2:
            repartir(jugador, 200, start_pos=DECK_POS)
        elif dealing_step == 3:
            repartir(banca, 50, True, start_pos=DECK_POS)
        elif dealing_step == 4:
            if banca:
                if banca[0][0] == 'A':
                    insurance_offered = True; insurance_taken = False; insurance_bet = 0
                banca[0][4].start_flip(now)
            state = 'player'
            if not split_active:
                if len(jugador) == 2 and calcular(jugador) == 21:
                    revelar_banca(now)
                    mensaje = "BLACKJACK!"
                    state = 'dealer'; dealer_thinking = False
                    dealer_target = schedule_dealer_target(); next_action = now+600
        dealing_step += 1
        next_deal = now + 400

    if state == 'dealer' and (not clearing) and not paused:
        cards_settled = len(banca) > 0 and all(
            (not c[4].flipping) and (abs(c[4].x - c[4].dest_x) < 1) for c in banca)
        if cards_settled:
            if not dealer_thinking:
                dealer_thinking = True
                think_delay = DEALER_SETTLE_DELAY + random_module.randint(-200, 800)
                next_action = now + max(400, think_delay)
            elif now >= next_action:
                pb = calcular(banca)
                hands = list(iter_player_hands())
                any_player_blackjack = any(len(h)==2 and calcular(h)==21 for h in hands)
                dealer_blackjack = (len(banca)==2 and calcular(banca)==21)

                if any_player_blackjack and not dealer_blackjack:
                    dealer_thinking = False; revelar_banca(now)
                    if insurance_taken:
                        insurance_taken = False; insurance_offered = False
                    results = []
                    for idx, hand in enumerate(hands):
                        bet_amt = per_hand_bets[idx] if (per_hand_bets and idx < len(per_hand_bets)) else current_bet
                        pj = calcular(hand)
                        if len(hand)==2 and calcular(hand)==21 and not dealer_blackjack:
                            player_money += int(bet_amt * 2.5) + 25
                            stats['blackjacks'] += 1; stats['won'] += 1
                            results.append('blackjack')
                        else:
                            if pj > 21:               rtype = 'lose'
                            elif pb > 21 or pj > pb:  rtype = 'win'
                            elif pj < pb:             rtype = 'lose'
                            else:                     rtype = 'tie'
                            if rtype == 'win':   player_money += bet_amt*2; stats['won'] += 1
                            elif rtype == 'tie': player_money += bet_amt
                            else:                stats['lost'] += 1
                            results.append(rtype)
                    stats['played'] += 1
                    if any(r == 'blackjack' for r in results): mensaje = "BLACKJACK!"
                    elif any(r == 'win' for r in results):    mensaje = "HAS GANADO"
                    elif all(r == 'tie' for r in results):    mensaje = "EMPATE"
                    else:                                      mensaje = "HAS PERDIDO"
                    _apply_chip_result(results)
                    state = 'round_end'; round_end_time = now

                elif pb < dealer_target:
                    repartir(banca, 50)
                    dealer_thinking = True
                    next_action = now + DEALER_SETTLE_DELAY + random_module.randint(0, 600)

                else:
                    dealer_thinking = False
                    dealer_blackjack = (len(banca)==2 and calcular(banca)==21)
                    if insurance_taken:
                        if dealer_blackjack: player_money += insurance_bet * 2
                        insurance_taken = False; insurance_offered = False
                    hands2 = list(iter_player_hands())
                    results = []
                    for idx, hand in enumerate(hands2):
                        bet_amt = per_hand_bets[idx] if (per_hand_bets and idx < len(per_hand_bets)) else current_bet
                        pj = calcular(hand)
                        if len(hand)==2 and calcular(hand)==21 and not dealer_blackjack:
                            player_money += int(bet_amt * 2.5) + 25
                            stats['blackjacks'] += 1; stats['won'] += 1
                            results.append('blackjack')
                        else:
                            if pj > 21:               rtype = 'lose'
                            elif pb > 21 or pj > pb:  rtype = 'win'
                            elif pj < pb:             rtype = 'lose'
                            else:                     rtype = 'tie'
                            if rtype == 'win':   player_money += bet_amt*2; stats['won'] += 1
                            elif rtype == 'tie': player_money += bet_amt
                            else:                stats['lost'] += 1
                            results.append(rtype)
                    stats['played'] += 1
                    if any(r == 'blackjack' for r in results): mensaje = "BLACKJACK!"
                    elif any(r == 'win' for r in results):    mensaje = "HAS GANADO"
                    elif all(r == 'tie' for r in results):    mensaje = "EMPATE"
                    else:                                      mensaje = "HAS PERDIDO"
                    _apply_chip_result(results)
                    per_hand_bets = None
                    state = 'round_end'; round_end_time = now

    for mano in [banca]:
        for c in mano:
            c[4].target_scale = 1.0
            c[4].actualizar(now); c[4].dibujar(now)

    _mouse_lp = to_logical(pygame.mouse.get_pos())
    if split_active and jugador_hands:
        for i, hand in enumerate(jugador_hands):
            hand_offset_x = 120 + i * HAND_SEP
            offset_y = 200 + i*70
            is_active = (i == current_hand_index and state == 'player')
            target_for_hand = 1.06 if is_active else 1.0
            for idx, c in enumerate(hand):
                c[4].dest_x = hand_offset_x + idx * CARD_SPACING
                c[4].dest_y = offset_y
                hovered_c = pygame.Rect(int(c[4].x), int(c[4].y), CARD_W, CARD_H).collidepoint(_mouse_lp)
                c[4].target_scale = max(target_for_hand, 1.12 if hovered_c else 1.0)
                c[4].actualizar(now); c[4].dibujar(now)
    else:
        for c in jugador:
            hovered_c = pygame.Rect(int(c[4].x), int(c[4].y), CARD_W, CARD_H).collidepoint(_mouse_lp)
            c[4].target_scale = 1.12 if hovered_c else 1.0
            c[4].actualizar(now); c[4].dibujar(now)

    hand = get_current_hand()
    player_visible = calcular_visible(hand)
    if state == 'player' and player_visible != 0 and not paused:
        if player_visible == 21:
            if split_active and current_hand_index < len(jugador_hands)-1:
                current_hand_index += 1
            else:
                state = 'dealer'; revelar_banca(now); dealer_thinking = False
                dealer_target = schedule_dealer_target(); next_action = now+600
        elif player_visible > 21:
            if split_active and current_hand_index < len(jugador_hands)-1:
                overlay_flash.update({'active':True,'color':(150,0,0),'alpha':200,'start':now,'duration':300})
                mensaje = f"MANO {current_hand_index+1} BUST"; current_hand_index += 1; last_pedir_time = now
            elif split_active and current_hand_index == len(jugador_hands)-1:
                overlay_flash.update({'active':True,'color':(150,0,0),'alpha':200,'start':now,'duration':300})
                mensaje = f"MANO {current_hand_index+1} BUST"
                revelar_banca(now); state = 'dealer'; dealer_thinking = False
                dealer_target = schedule_dealer_target(); next_action = now+600
            else:
                mensaje = "HAS PERDIDO"; stats['lost'] += 1; stats['played'] += 1
                overlay_flash.update({'active':True,'color':(150,0,0),'alpha':200,'start':now,'duration':350})
                revelar_banca(now); state = 'round_end'; round_end_time = now
                if placed_chip:
                    sx, sy = placed_chip['x'], placed_chip['y']
                    tx, ty = BANK_POS; speed = 10.0
                    dx = tx - sx; dy = ty - sy; dist = math.hypot(dx, dy) or 1.0
                    placed_chip.update({'moving':True,'vx':dx/dist*speed,'vy':dy/dist*speed,
                                        'target_x':tx,'target_y':ty,'expire_on_arrival':True})

    if state == 'round_end' and (not clearing) and round_end_time != 0 and now >= round_end_time + ROUND_DELAY and not paused:
        player_cards = sum(jugador_hands,[]) if jugador_hands else jugador
        all_cards = banca + player_cards
        if not all_cards:
            nueva_ronda()
        else:
            clearing_cards = list(all_cards)
            for ct4 in clearing_cards:
                ct4[4].oculta = False; ct4[4].start_flip(now, to_back=True)
            clearing = True; clear_phase = 'flipping'
        round_end_time = 0

    if clearing and not paused:
        if clear_phase == 'flipping':
            flips_done = all((not c[4].flipping) for c in clearing_cards)
            if flips_done:
                for idx, c in enumerate(clearing_cards):
                    c[4].dest_x = ANCHO + 80 + idx * 30
                    c[4].target_scale = 0.9
                clear_phase = 'moving'
        elif clear_phase == 'moving':
            if not clearing_cards:
                clearing = False; clear_phase = None; nueva_ronda()
            else:
                done = all(c[4].x >= c[4].dest_x - 1 for c in clearing_cards)
                if done:
                    clearing = False; clear_phase = None; clearing_cards = []; nueva_ronda()

    if any(c[4].oculta for c in banca):
        texto = " + ".join("?" if c[4].oculta else str(c[2]) for c in banca)
        VENTANA.blit(FUENTE.render(f"Banca: {texto}", True, BLANCO), (50, 20))
    else:
        banca_visible = calcular_visible(banca)
        VENTANA.blit(FUENTE.render(f"Banca: {banca_visible}", True, BLANCO), (50, 20))

    if split_active and jugador_hands:
        left = f"Mano 1: {calcular(jugador_hands[0])}"
        right = f"Mano 2: {calcular(jugador_hands[1])}"
        surf = FUENTE.render(f"{left}    {right}", True, BLANCO)
        VENTANA.blit(surf, (50, ALTO - 220))
    else:
        VENTANA.blit(FUENTE.render(f"Jugador: {calcular(jugador)}", True, BLANCO), (50, 380))

    if state == 'betting':
        instrucciones = ["Escribe tu apuesta y pulsa ENTER"]
    elif state == 'player':
        instrucciones = ["ESPACIO: Pedir  ENTER: Plantarse  D: Doblar  P: Dividir  I: Seguro"]
    elif state in ('dealing', 'dealer'):
        instrucciones = ["Esperando..."]
    else:
        instrucciones = ["S = Siguiente ronda"]

    if insurance_offered and not insurance_taken and state == 'player':
        instrucciones = ["I: Tomar seguro  |  " + instrucciones[0]]

    box_w = 860; padding = 12; line_h = 28
    box_h = line_h * (len(instrucciones) + 4) + padding
    reglas_x = (ANCHO - box_w) // 2
    reglas_y = ALTO - box_h - 20

    s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    VENTANA.blit(s, (reglas_x, reglas_y))
    pygame.draw.rect(VENTANA, NEGRO, (reglas_x, reglas_y, box_w, box_h), 2, border_radius=8)
    y_off = reglas_y + padding

    label_money = FUENTE_PEQUENA.render(f"Fichas: {player_money}", True, DORADO)
    VENTANA.blit(label_money, (reglas_x + padding, y_off))

    input_box_w = 220; input_box_h = 36
    input_box_x = reglas_x + box_w - input_box_w - padding
    input_box_y = y_off - 6
    input_bg = pygame.Surface((input_box_w, input_box_h), pygame.SRCALPHA)
    input_bg.fill((20, 20, 20, 230))
    VENTANA.blit(input_bg, (input_box_x, input_box_y))
    pygame.draw.rect(VENTANA, NEGRO, (input_box_x, input_box_y, input_box_w, input_box_h), 2, border_radius=6)

    display_text = current_bet_input if state == 'betting' else str(current_bet)

    txt_to_show = clip_text_right(display_text, FUENTE_PEQUENA, input_box_w - 16)
    txt_surf = FUENTE_PEQUENA.render(txt_to_show, True, BLANCO)
    VENTANA.blit(txt_surf, (input_box_x + 8, input_box_y + (input_box_h - txt_surf.get_height()) // 2))
    lbl_ap = FUENTE_PEQUENA.render("Apuesta:", True, BLANCO)
    VENTANA.blit(lbl_ap, (input_box_x - lbl_ap.get_width() - 12, input_box_y + (input_box_h - lbl_ap.get_height()) // 2))

    y_off += line_h
    diff_labels = {0: 'Normal', 1: 'Difícil', 2: 'Muy Difícil', 3: 'EXTREMO'}
    diff_colors = {0: BLANCO, 1: (255, 200, 80), 2: (255, 140, 40), 3: (255, 80, 80)}
    diff_label  = diff_labels.get(difficulty_level, 'Normal')
    diff_color  = diff_colors.get(difficulty_level, BLANCO)
    surf_chips = FUENTE_PEQUENA.render(
        f"Máx apuesta: {BET_MAX}  |  Meta: {EPIC_WIN_THRESHOLD} fichas  |  Dificultad: {diff_label}",
        True, diff_color)
    VENTANA.blit(surf_chips, (reglas_x + padding, y_off))
    y_off += line_h

    for linea in instrucciones:
        surf2 = FUENTE_INSTR.render(linea, True, BLANCO)
        text_x = reglas_x + (box_w - surf2.get_width()) // 2
        VENTANA.blit(surf2, (text_x, y_off))
        y_off += 24

    if mensaje:
        if "BLACKJACK" in mensaje.upper():
            surf_m = FUENTE_GRANDE.render(mensaje, True, DORADO)
        elif "GAN" in mensaje.upper():
            surf_m = FUENTE_MSG.render(mensaje, True, DORADO)
        elif "EMPATE" in mensaje.upper():
            surf_m = FUENTE_MSG.render(mensaje, True, (200, 200, 200))
        else:
            surf_m = FUENTE_MSG.render(mensaje, True, ROJO)
        msg_x = (ANCHO - surf_m.get_width()) // 2
        VENTANA.blit(surf_m, (msg_x, ALTO // 2 + 20))

    if placed_chip:
        if placed_chip.get('moving'):
            placed_chip['x'] += placed_chip['vx']
            placed_chip['y'] += placed_chip['vy']
            if math.hypot(placed_chip['x']-placed_chip['target_x'],
                          placed_chip['y']-placed_chip['target_y']) < 8:
                placed_chip['x'] = placed_chip['target_x']
                placed_chip['y'] = placed_chip['target_y']
                placed_chip['moving'] = False
                if placed_chip.get('expire_on_arrival'):
                    placed_chip = None
        if placed_chip:
            if placed_chip.get('shape') == 'rect':
                w = placed_chip.get('w', 44); h = placed_chip.get('h', 28)
                rect = pygame.Rect(int(placed_chip['x']-w//2), int(placed_chip['y']-h//2), w, h)
                pygame.draw.rect(VENTANA, placed_chip['color'], rect, border_radius=8)
                pygame.draw.rect(VENTANA, NEGRO, rect, 2, border_radius=8)
                font = _chip_font_for_rect(h)
                txt = font.render(str(placed_chip['value']), True, BLANCO)
                VENTANA.blit(txt, (rect.centerx-txt.get_width()//2, rect.centery-txt.get_height()//2))
            else:
                r = placed_chip.get('r', 20)
                cx = int(placed_chip['x']); cy = int(placed_chip['y'])
                pygame.draw.circle(VENTANA, placed_chip['color'], (cx, cy), r)
                pygame.draw.circle(VENTANA, NEGRO, (cx, cy), r, 2)
                font = _chip_font_for_circle(r)
                txt = font.render(str(placed_chip['value']), True, BLANCO)
                VENTANA.blit(txt, (cx-txt.get_width()//2, cy-txt.get_height()//2))

    for i, c in enumerate(player_chip_stack[-12:]):
        x = PLAYER_STACK_POS[0] + (i % 6) * 10
        y = PLAYER_STACK_POS[1] - (i // 6) * 6
        pygame.draw.circle(VENTANA, (220,170,60), (int(x), int(y)), 18)
        pygame.draw.circle(VENTANA, NEGRO, (int(x), int(y)), 18, 2)
        txt = FUENTE_PEQUENA.render(str(c['value']), True, BLANCO)
        VENTANA.blit(txt, (int(x-txt.get_width()//2), int(y-txt.get_height()//2)))

    for c in chips_anim[:]:
        c['x'] += c['vx']; c['y'] += c['vy']
        if math.hypot(c['x']-c['target_x'], c['y']-c['target_y']) < 8:
            try: chips_anim.remove(c)
            except ValueError: pass
            continue
        if c.get('shape') == 'rect':
            w = c.get('w', 44); h = c.get('h', 28)
            rect = pygame.Rect(int(c['x']-w//2), int(c['y']-h//2), w, h)
            pygame.draw.rect(VENTANA, c['color'], rect, border_radius=8)
            pygame.draw.rect(VENTANA, NEGRO, rect, 2, border_radius=8)
            font = _chip_font_for_rect(h)
            txt = font.render(str(c['value']), True, BLANCO)
            VENTANA.blit(txt, (rect.centerx-txt.get_width()//2, rect.centery-txt.get_height()//2))
        else:
            r = c.get('r', 20)
            pygame.draw.circle(VENTANA, c['color'], (int(c['x']), int(c['y'])), r)
            pygame.draw.circle(VENTANA, NEGRO, (int(c['x']), int(c['y'])), r, 2)
            font = _chip_font_for_circle(r)
            txt = font.render(str(c['value']), True, BLANCO)
            VENTANA.blit(txt, (int(c['x']-txt.get_width()//2), int(c['y']-txt.get_height()//2)))

    dt = RELOJ.get_time()
    for p in particles[:]:
        p[0] += p[2]; p[1] += p[3]; p[4] -= dt; p[3] += 0.12
        if p[4] <= 0:
            particles.remove(p); continue
        alpha = max(0, min(255, int(255 * (p[4] / 1200.0))))
        surf_p = pygame.Surface((6, 6), pygame.SRCALPHA)
        surf_p.fill((*p[5], alpha))
        VENTANA.blit(surf_p, (p[0], p[1]))

    if overlay_flash['active']:
        elapsed = now - overlay_flash['start']
        if elapsed > overlay_flash['duration']:
            overlay_flash['active'] = False
        else:
            a = int(overlay_flash['alpha'] * (1 - (elapsed / overlay_flash['duration'])))
            ov = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            ov.fill((*overlay_flash['color'], a))
            VENTANA.blit(ov, (0, 0))

    mouse_pos = to_logical(pygame.mouse.get_pos())
    btn_hovered = DOTS_BTN.collidepoint(mouse_pos)
    btn_color = (80,80,80) if not btn_hovered else (120,120,120)
    pygame.draw.rect(VENTANA, btn_color, DOTS_BTN, border_radius=6)
    pygame.draw.rect(VENTANA, NEGRO, DOTS_BTN, 1, border_radius=6)
    dots_surf = FUENTE_PEQUENA.render("...", True, BLANCO)
    VENTANA.blit(dots_surf, (DOTS_BTN.centerx-dots_surf.get_width()//2,
                              DOTS_BTN.centery-dots_surf.get_height()//2))

    if update_status is not None:
        elapsed_notif = now - update_notif_time
        is_permanent = update_status in ('checking', 'restarting')
        show_notif = is_permanent or (elapsed_notif < 5000)
        if show_notif:
            alpha_notif = 230
            if not is_permanent and elapsed_notif > 3500:
                alpha_notif = max(0, int(230 * (1-(elapsed_notif-3500)/1500)))
            if update_status == 'restarting':
                notif_color = (20,100,200)
                secs_left = max(0, 2-(now-update_restart_time)//1000)
                display_msg = f"¡Actualizado! Reiniciando en {secs_left}s..."
            else:
                display_msg = update_msg
                notif_color = (30,120,50) if update_status=='up_to_date' else \
                              (40,40,40)  if update_status=='checking'   else (150,30,30)
            notif_surf = FUENTE_PEQUENA.render(display_msg, True, BLANCO)
            nw = notif_surf.get_width()+24; nh = notif_surf.get_height()+14
            nx = ANCHO-nw-10; ny = DOTS_BTN.bottom+6
            bg = pygame.Surface((nw, nh), pygame.SRCALPHA)
            bg.fill((*notif_color, alpha_notif))
            VENTANA.blit(bg, (nx, ny))
            pygame.draw.rect(VENTANA, NEGRO, (nx, ny, nw, nh), 1, border_radius=6)
            VENTANA.blit(notif_surf, (nx+12, ny+7))

    r_hovered = REINICIAR_BTN.collidepoint(mouse_pos)
    r_color = (140,30,30) if not r_hovered else (180,50,50)
    pygame.draw.rect(VENTANA, r_color, REINICIAR_BTN, border_radius=7)
    pygame.draw.rect(VENTANA, NEGRO, REINICIAR_BTN, 1, border_radius=7)
    r_txt = FUENTE_PEQUENA.render("R: Reiniciar", True, BLANCO)
    VENTANA.blit(r_txt, (REINICIAR_BTN.centerx-r_txt.get_width()//2,
                          REINICIAR_BTN.centery-r_txt.get_height()//2))

    if app_state == 'blackjack':
        m_hovered = bj_menu_btn.collidepoint(mouse_pos)
        m_col = (30, 70, 140) if not m_hovered else (50, 100, 190)
        pygame.draw.rect(VENTANA, m_col, bj_menu_btn, border_radius=7)
        pygame.draw.rect(VENTANA, NEGRO, bj_menu_btn, 1, border_radius=7)
        m_txt = FUENTE_PEQUENA.render("ESC: Menú principal", True, BLANCO)
        VENTANA.blit(m_txt, (bj_menu_btn.centerx - m_txt.get_width()//2,
                              bj_menu_btn.centery - m_txt.get_height()//2))
        inf_s = FUENTE_PEQUENA.render(
            f"♠ BlackJack Infinito  |  Ganadas: {stats['won']}  Perdidas: {stats['lost']}",
            True, DORADO)
        VENTANA.blit(inf_s, (ANCHO//2 - inf_s.get_width()//2, ALTO - 88))

    if paused:
        _render_pause_menu(now)

    flip_display()
