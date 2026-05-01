import pygame
import random as random_module
import sys
import os
import math
import threading
import urllib.request
import shutil

pygame.init()

VERSION = "0.3.2"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/humrand/blackjack-python/main/blackjack-experimental-version.py"

ANCHO, ALTO = 1100, 720
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Blackjack Casino Edition")

FELT_DARK   = (14, 68, 22)
FELT_MID    = (22, 90, 30)
FELT_LIGHT  = (28, 108, 36)
GOLD        = (210, 170, 50)
GOLD_LIGHT  = (240, 205, 90)
GOLD_DARK   = (160, 125, 25)
BLANCO      = (255, 255, 255)
NEGRO       = (0,   0,   0)
ROJO        = (195, 30,  30)
ROJO_DARK   = (140, 15,  25)
CREMA       = (252, 248, 240)
GRIS_HUD    = (18,  22,  18)
VERDE       = (20, 120, 20)
VERDE_OSCURO= (12,  80, 12)
DORADO      = (230, 190, 60)
STRONG_GREEN= (0,  150,  0)

FUENTE       = pygame.font.SysFont("arial", 30, bold=True)
FUENTE_PEQUENA = pygame.font.SysFont("arial", 22, bold=True)
FUENTE_GRANDE  = pygame.font.SysFont("arial", 66, bold=True)
FUENTE_MSG     = pygame.font.SysFont("arial", 44, bold=True)
FUENTE_INSTR   = pygame.font.SysFont("arial", 19, bold=True)
FUENTE_CASINO  = pygame.font.SysFont("georgia", 15, bold=True)
FUENTE_CASINO_MD = pygame.font.SysFont("georgia", 18, bold=True)
FUENTE_BTN     = pygame.font.SysFont("arial", 21, bold=True)
RELOJ = pygame.time.Clock()

CARD_W = 96
CARD_H = 144
CARD_SPACING = 112

HAND_SEP   = 310
PEDIR_DELAY = 500
ROUND_DELAY = 2000
BET_MAX     = 250

SUIT_CHAR = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}

DEALER_Y   = 75
PLAYER_Y   = 395
SPLIT_DY   = 52

DECK_POS   = (ANCHO // 2, 22)
DEALER_POS = (ANCHO // 2, DEALER_Y)
PLAYER_STACK_POS = (115, ALTO - 72)
BANK_POS   = (ANCHO // 2, 38)

_BW, _BH, _BY = 148, 46, 555
BTN_HIT    = pygame.Rect(ANCHO//2 - 318, _BY, _BW, _BH)
BTN_STAND  = pygame.Rect(ANCHO//2 - 158, _BY, _BW, _BH)
BTN_DOUBLE = pygame.Rect(ANCHO//2 +   8, _BY, _BW, _BH)
BTN_SPLIT  = pygame.Rect(ANCHO//2 + 168, _BY, _BW, _BH)
BTN_BET    = pygame.Rect(ANCHO//2 -  74, _BY, 148, _BH)
BTN_NEXT   = pygame.Rect(ANCHO//2 -  74, _BY, 148, _BH)

def get_symbol_font(size):
    candidates = ["Symbola","DejaVuSans","DejaVu Sans","FreeSerif",
                  "Segoe UI Symbol","Arial Unicode MS","Noto Sans Symbols2","Noto Sans Symbols"]
    local_paths = [os.path.join("fonts","Symbola.ttf"),
                   os.path.join("fonts","DejaVuSans.ttf"),
                   os.path.join("fonts","DejaVuSans-Oblique.ttf")]
    for p in local_paths:
        if os.path.exists(p):
            try: return pygame.font.Font(p, size)
            except Exception: pass
    for name in candidates:
        try:
            path = pygame.font.match_font(name)
            if path:
                try: return pygame.font.Font(path, size)
                except Exception: pass
        except Exception: pass
    return pygame.font.SysFont("arial", size, bold=True)

SYMBOL_FONT    = get_symbol_font(50)
SYMBOL_FONT_SM = get_symbol_font(18)
SYMBOL_FONT_LG = get_symbol_font(68)

def crear_baraja():
    palos = [("S", NEGRO), ("H", ROJO), ("D", ROJO), ("C", NEGRO)]
    valores = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
    baraja = []
    for palo, color in palos:
        for v in valores:
            if   v == "A":               valor_num = 11
            elif v in ["J","Q","K"]:     valor_num = 10
            else:                        valor_num = int(v)
            baraja.append((v, palo, valor_num, color))
    random_module.shuffle(baraja)
    return baraja

def calcular(mano):
    total = sum(c[2] for c in mano)
    ases  = sum(1 for c in mano if c[0] == "A")
    while total > 21 and ases:
        total -= 10; ases -= 1
    return total

def calcular_visible(mano):
    visibles = [c for c in mano if (not c[4].oculta) and (not c[4].flipping) and (abs(c[4].x - c[4].dest_x) < 1)]
    if not visibles: return 0
    total = sum(c[2] for c in visibles)
    ases  = sum(1 for c in visibles if c[0] == "A")
    while total > 21 and ases:
        total -= 10; ases -= 1
    return total

class Carta:
    def __init__(self, valor, palo, valor_num, color, dest_x, dest_y, start_pos=None):
        self.valor     = valor
        self.palo      = palo
        self.valor_num = valor_num
        self.color     = color
        if start_pos:
            self.x, self.y = float(start_pos[0]), float(start_pos[1])
        else:
            self.x, self.y = float(DECK_POS[0]), float(DECK_POS[1])
        self.dest_x = float(dest_x)
        self.dest_y = float(dest_y)
        self.w = CARD_W
        self.h = CARD_H
        self.oculta        = False
        self.flipping      = False
        self.flip_start    = 0
        self.flip_duration = 300
        self.front = None
        self.back  = None
        self.flip_target_back = False
        self.scale       = 1.0
        self.target_scale = 1.0
        self.scale_speed = 0.12
        self._create_faces()

    def _create_faces(self):
        self.front = self.crear_front()
        self.back  = self.crear_back()

    def crear_front(self):
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(surf, CREMA,  (0, 0, self.w, self.h), border_radius=11)
        pygame.draw.rect(surf, (195, 190, 180), (0, 0, self.w, self.h), 1, border_radius=11)
        pygame.draw.rect(surf, (220, 215, 205), (2, 2, self.w-4, self.h-4), 1, border_radius=10)

        col      = self.color
        suit_char = SUIT_CHAR.get(self.palo, '?')

        r_surf = FUENTE_PEQUENA.render(self.valor, True, col)
        surf.blit(r_surf, (6, 4))
        r_rot  = pygame.transform.rotate(r_surf, 180)
        surf.blit(r_rot, (self.w - r_rot.get_width() - 6, self.h - r_rot.get_height() - 4))

        try:
            s_mini = SYMBOL_FONT_SM.render(suit_char, True, col)
            surf.blit(s_mini, (6, 4 + r_surf.get_height() + 1))
            s_rot  = pygame.transform.rotate(s_mini, 180)
            surf.blit(s_rot, (self.w - s_rot.get_width() - 6, self.h - s_rot.get_height() - r_rot.get_height() - 5))
        except Exception:
            pass

        cx = self.w // 2
        cy = self.h // 2

        if self.valor in ("J", "Q", "K"):
            fc_bg = (255, 225, 225) if col == ROJO else (225, 225, 255)
            pygame.draw.rect(surf, fc_bg, (10, 26, self.w-20, self.h-52), border_radius=4)
            pygame.draw.rect(surf, col,    (10, 26, self.w-20, self.h-52), 1, border_radius=4)
            face_font = pygame.font.SysFont("georgia", 52, bold=True)
            face_s = face_font.render(self.valor, True, col)
            surf.blit(face_s, (cx - face_s.get_width()//2, cy - face_s.get_height()//2 + 4))
            try:
                crown_s = SYMBOL_FONT.render('♛', True, col)
                surf.blit(crown_s, (cx - crown_s.get_width()//2, 30))
            except Exception:
                pass

        elif self.valor == "A":
            try:
                big_s = SYMBOL_FONT_LG.render(suit_char, True, col)
                surf.blit(big_s, (cx - big_s.get_width()//2, cy - big_s.get_height()//2 - 4))
            except Exception:
                simple = FUENTE_GRANDE.render(suit_char, True, col)
                surf.blit(simple, (cx - simple.get_width()//2, cy - simple.get_height()//2))

        else:
            try:
                pip_s = SYMBOL_FONT.render(suit_char, True, col)
                surf.blit(pip_s, (cx - pip_s.get_width()//2, cy - pip_s.get_height()//2 - 4))
            except Exception:
                simple = FUENTE_PEQUENA.render(suit_char, True, col)
                surf.blit(simple, (cx - simple.get_width()//2, cy - simple.get_height()//2))

        return surf

    def crear_back(self):
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(surf, ROJO_DARK, (0, 0, self.w, self.h), border_radius=11)
        pygame.draw.rect(surf, GOLD,      (0, 0, self.w, self.h), 2, border_radius=11)
        pygame.draw.rect(surf, GOLD_LIGHT,(4, 4, self.w-8, self.h-8), 1, border_radius=9)

        for i in range(8, self.w-8, 14):
            for j in range(8, self.h-8, 14):
                pygame.draw.rect(surf, (175, 35, 48), (i, j, 6, 6), border_radius=1)

        pts = [(self.w//2, 16), (self.w-16, self.h//2),
               (self.w//2, self.h-16), (16, self.h//2)]
        pygame.draw.polygon(surf, GOLD, pts, 1)

        pts2 = [(self.w//2, 30), (self.w-30, self.h//2),
                (self.w//2, self.h-30), (30, self.h//2)]
        pygame.draw.polygon(surf, GOLD_DARK, pts2, 1)

        try:
            em = SYMBOL_FONT_SM.render('♦', True, GOLD)
            surf.blit(em, (self.w//2 - em.get_width()//2, self.h//2 - em.get_height()//2))
        except Exception:
            pass

        return surf

    def start_flip(self, now, to_back=False):
        if not self.flipping:
            self.flipping = True
            self.flip_start = now
            self.flip_target_back = bool(to_back)

    def actualizar(self, now):
        speed = 0.15
        dx = self.dest_x - self.x
        dy = self.dest_y - self.y
        if abs(dx) > 0.5 or abs(dy) > 0.5:
            self.x += dx * speed
            self.y += dy * speed
        else:
            self.x = self.dest_x
            self.y = self.dest_y
        if abs(self.scale - self.target_scale) > 0.001:
            self.scale += (self.target_scale - self.scale) * self.scale_speed
        else:
            self.scale = self.target_scale

    def dibujar(self, now):
        rx, ry = int(self.x), int(self.y)
        if not self.flipping:
            surf_to_blit = self.back if self.oculta else self.front
            new_w = max(1, int(self.w * self.scale))
            new_h = max(1, int(self.h * self.scale))
            scaled = pygame.transform.smoothscale(surf_to_blit, (new_w, new_h))
            sh = pygame.Surface((new_w, new_h), pygame.SRCALPHA)
            sh.fill((0, 0, 0, 60))
            VENTANA.blit(sh, (rx - (new_w-self.w)//2 + 3, ry - (new_h-self.h)//2 + 4))
            VENTANA.blit(scaled, (rx - (new_w-self.w)//2, ry - (new_h-self.h)//2))
            return

        progreso = (now - self.flip_start) / self.flip_duration
        if progreso >= 1:
            self.flipping = False
            self.oculta   = bool(self.flip_target_back)
            surf_to_blit  = self.back if self.oculta else self.front
            new_w = max(1, int(self.w * self.scale))
            new_h = max(1, int(self.h * self.scale))
            scaled = pygame.transform.smoothscale(surf_to_blit, (new_w, new_h))
            VENTANA.blit(scaled, (rx - (new_w-self.w)//2, ry - (new_h-self.h)//2))
            return

        if self.flip_target_back:
            if progreso < 0.5:
                escala = 1 - progreso * 2;   surf = self.front
            else:
                escala = (progreso-0.5) * 2; surf = self.back
        else:
            if progreso < 0.5:
                escala = 1 - progreso * 2;   surf = self.back
            else:
                escala = (progreso-0.5) * 2; surf = self.front

        ancho   = max(1, int(self.w * escala))
        h_final = max(1, int(self.h * self.scale))
        scaled  = pygame.transform.smoothscale(surf, (ancho, h_final))
        x_blit  = rx + (self.w - ancho)//2 - ((int(self.w*self.scale) - self.w)//2)
        y_blit  = ry - (h_final - self.h)//2
        VENTANA.blit(scaled, (x_blit, y_blit))

CHIP_PALETTE = {
    'red':    (200,  40,  40),
    'orange': (220, 120,  20),
    'green':  ( 30, 160,  70),
    'blue':   ( 40, 120, 220),
    'teal':   ( 20, 150, 120),
    'pink':   (210,  80, 160),
    'gold':   (210, 170,  50),
}

def get_chip_style(value):
    v = int(value)
    if   1  <= v <= 10:  return {'shape':'circle','r':16,'color':CHIP_PALETTE['red']}
    if  11  <= v <= 34:  return {'shape':'circle','r':18,'color':CHIP_PALETTE['orange']}
    if  35  <= v <= 64:  return {'shape':'circle','r':20,'color':CHIP_PALETTE['green']}
    if  65  <= v <= 99:  return {'shape':'circle','r':22,'color':CHIP_PALETTE['blue']}
    if 100  <= v <= 199: return {'shape':'rect',  'w':50,'h':30,'color':CHIP_PALETTE['teal']}
    if 200  <= v <= 250: return {'shape':'rect',  'w':58,'h':33,'color':CHIP_PALETTE['pink']}
    return {'shape':'circle','r':20,'color':CHIP_PALETTE['gold']}

def _chip_font_for_circle(r):
    return pygame.font.SysFont("arial", max(10, int(r*0.72)), bold=True)

def _chip_font_for_rect(h):
    return pygame.font.SysFont("arial", max(12, int(h*0.62)), bold=True)

def _draw_chip_3d(surface, cx, cy, r, color, value):
    """Draw a casino-style 3-D chip."""
    sh = pygame.Surface((r*2+6, r*2+6), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0,0,0,80), (r+3, r+4), r)
    surface.blit(sh, (cx-r-3, cy-r-3))
    pygame.draw.circle(surface, color, (cx, cy), r)
    dk = tuple(max(0, c-60) for c in color)
    pygame.draw.circle(surface, dk, (cx, cy), r, 3)
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        nx = cx + int((r-5)*math.cos(rad))
        ny = cy + int((r-5)*math.sin(rad))
        pygame.draw.circle(surface, BLANCO, (nx, ny), 2)
    for i in range(3):
        alpha = 120 - i*35
        arc_s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.arc(arc_s, (255,255,255,alpha),
                        (0, 0, r*2, r*2),
                        math.pi*0.65, math.pi*1.35, 2+i)
        surface.blit(arc_s, (cx-r, cy-r))
    font = _chip_font_for_circle(r)
    txt = font.render(str(value), True, BLANCO)
    surface.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))

def _draw_chip_rect_3d(surface, cx, cy, w, h, color, value):
    """Draw a rectangular plaque chip."""
    x, y = cx - w//2, cy - h//2
    sh = pygame.Surface((w+4, h+4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0,0,0,80), (2,3,w,h), border_radius=7)
    surface.blit(sh, (x-2, y-2))
    pygame.draw.rect(surface, color, (x, y, w, h), border_radius=7)
    dk = tuple(max(0, c-60) for c in color)
    pygame.draw.rect(surface, dk,    (x, y, w, h), 2, border_radius=7)
    for nx in [x+5, x+w-8]:
        pygame.draw.rect(surface, BLANCO, (nx, cy-h//4, 3, h//2), border_radius=1)
    shine = pygame.Surface((w-4, h//2), pygame.SRCALPHA)
    shine.fill((255,255,255,45))
    surface.blit(shine, (x+2, y+2))
    font = _chip_font_for_rect(h)
    txt = font.render(str(value), True, BLANCO)
    surface.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))

def render_chip_dict(surface, c):
    if c.get('shape') == 'rect':
        _draw_chip_rect_3d(surface, int(c['x']), int(c['y']),
                           c.get('w',50), c.get('h',30), c['color'], c['value'])
    else:
        _draw_chip_3d(surface, int(c['x']), int(c['y']),
                      c.get('r',20), c['color'], c['value'])

def create_placed_chip(value, x, y):
    style = get_chip_style(value)
    base  = {'x':float(x),'y':float(y),'value':int(value),
             'moving':False,'vx':0.0,'vy':0.0,'target_x':x,'target_y':y}
    base.update(style)
    return base

def make_chip_move_dict(value, sx, sy, tx, ty, speed=6.0):
    dx = tx - sx; dy = ty - sy
    dist = math.hypot(dx, dy)
    vx = (dx/dist*speed) if dist else 0.0
    vy = (dy/dist*speed) if dist else 0.0
    style = get_chip_style(value)
    d = {'x':float(sx),'y':float(sy),'vx':vx,'vy':vy,
         'target_x':tx,'target_y':ty,'value':int(value),'moving':True}
    d.update(style)
    return d

_CASINO_TEXT_FONT = pygame.font.SysFont("georgia", 14, bold=True)
_DIVIDER_FONT     = pygame.font.SysFont("georgia", 12, bold=True)

def draw_table_bg():
    """Render the casino felt, gold trim and decorative text."""
    VENTANA.fill((6, 24, 8))

    for i in range(7):
        vs = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        b  = i * 18
        a  = 22 + i * 14
        inner = pygame.Rect(b, b, ANCHO-b*2, ALTO-b*2)
        vs.fill((0, 0, 0, a))
        pygame.draw.rect(vs, (0,0,0,0), inner)
        VENTANA.blit(vs, (0,0))

    felt_rect = pygame.Rect(28, 14, ANCHO-56, ALTO-28)
    pygame.draw.rect(VENTANA, FELT_MID,  felt_rect, border_radius=90)
    pygame.draw.rect(VENTANA, GOLD,      felt_rect, 3,  border_radius=90)
    pygame.draw.rect(VENTANA, GOLD_DARK, felt_rect, 1,  border_radius=90)

    inner_felt = pygame.Rect(44, 28, ANCHO-88, ALTO-56)
    pygame.draw.rect(VENTANA, FELT_LIGHT, inner_felt, border_radius=80)

    strip_y = 32
    txt_bj = _CASINO_TEXT_FONT.render("♦  BLACKJACK PAYS  3 : 2  ♦", True, GOLD)
    VENTANA.blit(txt_bj, (ANCHO//2 - txt_bj.get_width()//2, strip_y))

    div_y = 285
    sep_s = pygame.Surface((ANCHO-100, 2), pygame.SRCALPHA)
    sep_s.fill((*GOLD_DARK, 140))
    VENTANA.blit(sep_s, (50, div_y))

    lbl_dealer = _DIVIDER_FONT.render("D E A L E R", True, GOLD_DARK)
    VENTANA.blit(lbl_dealer, (ANCHO//2 - lbl_dealer.get_width()//2, div_y + 4))

    bet_cx, bet_cy = ANCHO//2, ALTO - 148
    pygame.draw.circle(VENTANA, FELT_DARK,  (bet_cx, bet_cy), 62)
    pygame.draw.circle(VENTANA, GOLD,       (bet_cx, bet_cy), 62, 2)
    pygame.draw.circle(VENTANA, GOLD_DARK,  (bet_cx, bet_cy), 56, 1)

    bet_lbl = _DIVIDER_FONT.render("BET", True, GOLD_DARK)
    VENTANA.blit(bet_lbl, (bet_cx - bet_lbl.get_width()//2, bet_cy - bet_lbl.get_height()//2))

    rules_txt = _CASINO_TEXT_FONT.render("DEALER MUST STAND ON 17  •  INSURANCE PAYS 2:1", True, GOLD_DARK)
    VENTANA.blit(rules_txt, (ANCHO//2 - rules_txt.get_width()//2, ALTO - 26))

    dk_x, dk_y = ANCHO - 70, 18
    for i in range(5, 0, -1):
        pygame.draw.rect(VENTANA, ROJO_DARK, (dk_x+i, dk_y+i, 46, 62), border_radius=5)
        pygame.draw.rect(VENTANA, GOLD,      (dk_x+i, dk_y+i, 46, 62), 1, border_radius=5)
    pygame.draw.rect(VENTANA, ROJO_DARK, (dk_x, dk_y, 46, 62), border_radius=5)
    pygame.draw.rect(VENTANA, GOLD,      (dk_x, dk_y, 46, 62), 1, border_radius=5)
    dk_lbl = pygame.font.SysFont("arial", 9, bold=True).render("DECK", True, GOLD_DARK)
    VENTANA.blit(dk_lbl, (dk_x+23-dk_lbl.get_width()//2, dk_y+26))

def draw_hud_panel(rect, alpha=200):
    s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(s, (10, 18, 10, alpha), (0,0,rect.w,rect.h), border_radius=10)
    pygame.draw.rect(s, (*GOLD_DARK, 180),   (0,0,rect.w,rect.h), 1, border_radius=10)
    VENTANA.blit(s, (rect.x, rect.y))

def draw_score_label(text, x, y, color=BLANCO, font=None):
    if font is None: font = FUENTE
    sh = font.render(text, True, (0,0,0))
    VENTANA.blit(sh, (x+1, y+1))
    VENTANA.blit(font.render(text, True, color), (x, y))

BTN_DEFS = {
    'hit':    (BTN_HIT,    "HIT [SPACE]",   ( 35, 140,  65)),
    'stand':  (BTN_STAND,  "STAND [ENTER]", (165,  45,  35)),
    'double': (BTN_DOUBLE, "DOUBLE [D]",    (175, 125,  25)),
    'split':  (BTN_SPLIT,  "SPLIT [P]",     ( 45,  80, 185)),
}

def draw_action_buttons(state, mouse_pos, split_active, hand, player_money_,
                        current_bet_, doubledown_flags_, current_hand_index_,
                        per_hand_bets_):
    if state == 'player':
        can_double = False
        if split_active:
            if doubledown_flags_ and current_hand_index_ < len(doubledown_flags_):
                bet_amt = (per_hand_bets_[current_hand_index_]
                           if per_hand_bets_ and current_hand_index_ < len(per_hand_bets_)
                           else current_bet_)
                can_double = (len(hand) == 2 and player_money_ >= bet_amt
                              and not doubledown_flags_[current_hand_index_])
            else:
                can_double = (len(hand) == 2 and player_money_ >= current_bet_)
        else:
            can_double = (len(hand) == 2 and player_money_ >= current_bet_
                          and not doubledown_flags_)

        can_split = (len(hand) == 2 and hand[0][2] == hand[1][2]
                     and player_money_ >= current_bet_ and not split_active)

        active_map = {'hit': True, 'stand': True, 'double': can_double, 'split': can_split}

        for key, (rect, label, base_color) in BTN_DEFS.items():
            enabled = active_map[key]
            col = base_color if enabled else (55, 55, 55)
            hover = rect.collidepoint(mouse_pos) and enabled
            if hover:
                col = tuple(min(255, c+45) for c in col)

            sh = pygame.Surface((rect.w+2, rect.h+2), pygame.SRCALPHA)
            pygame.draw.rect(sh, (0,0,0,90), (2,2,rect.w,rect.h), border_radius=9)
            VENTANA.blit(sh, (rect.x, rect.y))

            pygame.draw.rect(VENTANA, col, rect, border_radius=9)
            border_col = GOLD if enabled else (80, 80, 80)
            pygame.draw.rect(VENTANA, border_col, rect, 2, border_radius=9)

            if enabled:
                shine_s = pygame.Surface((rect.w-4, rect.h//2-2), pygame.SRCALPHA)
                shine_s.fill((255,255,255,30))
                VENTANA.blit(shine_s, (rect.x+2, rect.y+2))

            txt = FUENTE_BTN.render(label, True, BLANCO if enabled else (100,100,100))
            VENTANA.blit(txt, (rect.centerx - txt.get_width()//2,
                               rect.centery - txt.get_height()//2))

    elif state == 'betting':
        col  = (35, 120, 55)
        hover = BTN_BET.collidepoint(mouse_pos)
        if hover: col = (45, 155, 70)
        sh = pygame.Surface((BTN_BET.w+2, BTN_BET.h+2), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0,0,0,90), (2,2,BTN_BET.w,BTN_BET.h), border_radius=9)
        VENTANA.blit(sh, (BTN_BET.x, BTN_BET.y))
        pygame.draw.rect(VENTANA, col,  BTN_BET, border_radius=9)
        pygame.draw.rect(VENTANA, GOLD, BTN_BET, 2, border_radius=9)
        txt = FUENTE_BTN.render("DEAL  [ENTER]", True, BLANCO)
        VENTANA.blit(txt, (BTN_BET.centerx - txt.get_width()//2,
                           BTN_BET.centery  - txt.get_height()//2))

    elif state == 'round_end':
        col  = (28, 80, 130)
        hover = BTN_NEXT.collidepoint(mouse_pos)
        if hover: col = (40, 105, 165)
        sh = pygame.Surface((BTN_NEXT.w+2, BTN_NEXT.h+2), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0,0,0,90), (2,2,BTN_NEXT.w,BTN_NEXT.h), border_radius=9)
        VENTANA.blit(sh, (BTN_NEXT.x, BTN_NEXT.y))
        pygame.draw.rect(VENTANA, col,  BTN_NEXT, border_radius=9)
        pygame.draw.rect(VENTANA, GOLD, BTN_NEXT, 2, border_radius=9)
        txt = FUENTE_BTN.render("NEXT ROUND  [S]", True, BLANCO)
        VENTANA.blit(txt, (BTN_NEXT.centerx - txt.get_width()//2,
                           BTN_NEXT.centery  - txt.get_height()//2))

def draw_mensaje(mensaje, now):
    if not mensaje: return
    upper = mensaje.upper()
    if "BLACKJACK" in upper:
        color = GOLD_LIGHT; font = FUENTE_GRANDE
    elif "GAN" in upper:
        color = (100, 240, 120); font = FUENTE_MSG
    elif "EMPATE" in upper:
        color = (200, 200, 200); font = FUENTE_MSG
    else:
        color = (255, 90, 90); font = FUENTE_MSG

    surf = font.render(mensaje, True, color)
    sw, sh = surf.get_size()
    mx = ANCHO//2 - sw//2
    my = ALTO//2 - 10

    pad = 18
    pill = pygame.Surface((sw+pad*2, sh+pad), pygame.SRCALPHA)
    pygame.draw.rect(pill, (0,0,0,170), (0,0,sw+pad*2,sh+pad), border_radius=12)
    VENTANA.blit(pill, (mx-pad, my-pad//2))

    sh_s = font.render(mensaje, True, (0,0,0))
    VENTANA.blit(sh_s, (mx+2, my+2))
    VENTANA.blit(surf, (mx, my))

TABLE_STYLES   = [
    {'name':'verde clásico', 'color':VERDE},
    {'name':'rojo casino',   'color':(100,20,20)},
    {'name':'negro lujo',    'color':(20,20,20)},
]
TABLE_STYLE_IDX = 0

DEALER_AVATAR = None
if os.path.exists(os.path.join("images","dealer.png")):
    try:
        img = pygame.image.load(os.path.join("images","dealer.png")).convert_alpha()
        DEALER_AVATAR = pygame.transform.smoothscale(img, (120,120))
    except Exception:
        DEALER_AVATAR = None

baraja = []
jugador = []
jugador_hands = None
current_hand_index = 0
split_active = False

banca = []

player_money      = 1000
current_bet       = 10
bet_locked        = False
current_bet_input = ""
last_bet          = None

insurance_offered = False
insurance_bet     = 0
insurance_taken   = False

doubledown_flags = []
per_hand_bets    = None

stats = {'played':0,'won':0,'lost':0,'blackjacks':0}

state          = 'betting'
dealing_step   = 0
next_deal      = 0
dealer_thinking= False
next_action    = 0
last_pedir_time= 0
round_end_time = 0

DEALER_SETTLE_DELAY = 900

clearing       = False
clear_phase    = None
clearing_cards = []

particles       = []
chips_anim      = []
placed_chip     = None
player_chip_stack = []

overlay_flash = {'active':False,'color':(0,0,0),'alpha':0,'start':0,'duration':400}

update_status      = None
update_msg         = ""
update_notif_time  = 0
update_restart_time= 0
DOTS_BTN = pygame.Rect(ANCHO-46, 8, 38, 28)

def _sha256(path):
    import hashlib
    try:
        with open(path,"rb") as f: return hashlib.sha256(f.read()).hexdigest()
    except Exception: return None

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
            update_status="error"; update_msg="No se pudo calcular hash remoto"
        elif sha_local == sha_remote:
            update_status="up_to_date"; update_msg="Ya tienes la ultima version"
        else:
            try:
                shutil.copy2(tmp_path, local_path)
                update_status="restarting"; update_msg="Actualizado! Reiniciando..."
                update_restart_time = pygame.time.get_ticks()
            except Exception as e:
                update_status="error"; update_msg=f"No se pudo escribir: {str(e)[:40]}"
    except Exception as e:
        update_status="error"; update_msg=f"Error: {str(e)[:55]}"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try: os.unlink(tmp_path)
            except Exception: pass
    update_notif_time = pygame.time.get_ticks()

nueva_ronda_pending = False
mensaje = ""

def get_current_hand():
    global split_active, jugador, jugador_hands, current_hand_index
    if split_active and jugador_hands:
        return jugador_hands[current_hand_index]
    return jugador

def iter_player_hands():
    if split_active and jugador_hands:
        for h in jugador_hands: yield h
    else:
        yield jugador

def repartir(mano, y, oculta=False, start_pos=None):
    global baraja, split_active, jugador_hands
    if not baraja: baraja = crear_baraja()
    v, p, val, color = baraja.pop()
    if split_active and jugador_hands and mano in jugador_hands:
        hand_idx = jugador_hands.index(mano)
        base_x   = 120 + hand_idx * HAND_SEP
        x        = base_x + len(mano) * CARD_SPACING
    else:
        x = 200 + len(mano) * CARD_SPACING
    carta        = Carta(v, p, val, color, x, y, start_pos=start_pos)
    carta.oculta = oculta
    mano.append((v, p, val, color, carta))

def revelar_banca(now):
    for c in banca:
        if c[4].oculta: c[4].start_flip(now)

def schedule_dealer_target():
    return 18 if random_module.random() < 0.15 else 17

def spawn_particles(x, y, color, count=30):
    for _ in range(count):
        angle = random_module.random() * 2 * math.pi
        speed = random_module.random() * random_module.random() * 8 + 2
        vx    = math.cos(angle) * speed
        vy    = math.sin(angle) * speed
        life  = random_module.random() * 800 + 400
        particles.append([x, y, vx, vy, life, color])

def reiniciar_partida():
    global player_money, stats, current_bet_input, current_bet, last_bet
    player_money      = 1000
    stats             = {'played':0,'won':0,'lost':0,'blackjacks':0}
    current_bet_input = ""
    current_bet       = 10
    last_bet          = None
    nueva_ronda()

def nueva_ronda():
    global baraja, jugador, banca, state, dealing_step, next_deal, mensaje
    global dealer_thinking, next_action, last_pedir_time, round_end_time
    global current_bet, bet_locked, player_money, stats, placed_chip, chips_anim
    global split_active, jugador_hands, current_hand_index, doubledown_flags
    global player_chip_stack, clearing_cards, per_hand_bets
    global insurance_offered, insurance_taken, insurance_bet, clearing, clear_phase
    baraja            = crear_baraja()
    jugador           = []
    banca             = []
    jugador_hands     = None
    split_active      = False
    current_hand_index= 0
    doubledown_flags  = []
    mensaje           = ""
    dealing_step      = 0
    next_deal         = pygame.time.get_ticks() + 300
    dealer_thinking   = False
    next_action       = 0
    last_pedir_time   = 0
    round_end_time    = 0
    state             = 'betting'
    bet_locked        = False
    placed_chip       = None
    chips_anim        = []
    player_chip_stack = []
    clearing_cards    = []
    per_hand_bets     = None
    insurance_offered = False
    insurance_taken   = False
    insurance_bet     = 0
    clearing          = False
    clear_phase       = None

nueva_ronda()

def do_hit(now):
    global last_pedir_time, split_active, jugador_hands, current_hand_index
    if (now >= last_pedir_time + PEDIR_DELAY) and (not clearing):
        if split_active and jugador_hands:
            dy = PLAYER_Y + current_hand_index * SPLIT_DY
        else:
            dy = PLAYER_Y
        repartir(get_current_hand(), dy)
        last_pedir_time = now

def do_stand(now):
    global state, dealer_thinking, dealer_target, next_action
    global split_active, jugador_hands, current_hand_index
    if split_active:
        if current_hand_index < len(jugador_hands)-1:
            current_hand_index += 1
        else:
            state           = 'dealer'
            revelar_banca(now)
            dealer_thinking = False
            dealer_target   = schedule_dealer_target()
            next_action     = now + 600
    else:
        state           = 'dealer'
        revelar_banca(now)
        dealer_thinking = False
        dealer_target   = schedule_dealer_target()
        next_action     = now + 600

def do_double(now):
    global state, dealer_thinking, dealer_target, next_action, player_money
    global current_bet, doubledown_flags, current_hand_index, per_hand_bets
    hand = get_current_hand()
    if split_active and not doubledown_flags:
        doubledown_flags[:] = [False]*len(jugador_hands)
    can_double = False
    if split_active:
        can_double = (len(hand)==2 and player_money>=(per_hand_bets[current_hand_index] if per_hand_bets else current_bet) and (not doubledown_flags[current_hand_index]))
    else:
        can_double = (len(hand)==2 and player_money>=current_bet and (not doubledown_flags))
    if can_double:
        if split_active:
            bet_to_deduct = per_hand_bets[current_hand_index] if per_hand_bets else current_bet
            player_money -= bet_to_deduct
            doubledown_flags[current_hand_index] = True
            if per_hand_bets:
                per_hand_bets[current_hand_index] *= 2
            else:
                per_hand_bets = [current_bet, current_bet]
                per_hand_bets[current_hand_index] *= 2
            dest_y = PLAYER_Y + current_hand_index * SPLIT_DY
            repartir(hand, dest_y)
            if current_hand_index < len(jugador_hands)-1:
                current_hand_index += 1
            else:
                state           = 'dealer'
                revelar_banca(now)
                dealer_thinking = False
                dealer_target   = schedule_dealer_target()
                next_action     = now + 600
        else:
            player_money -= current_bet
            current_bet  *= 2
            repartir(hand, PLAYER_Y)
            state           = 'dealer'
            revelar_banca(now)
            dealer_thinking = False
            dealer_target   = schedule_dealer_target()
            next_action     = now + 600

def do_split(now):
    global split_active, jugador_hands, jugador, current_hand_index
    global player_money, current_bet, last_bet, per_hand_bets, doubledown_flags, state
    hand = get_current_hand()
    if len(hand)==2 and (hand[0][2]==hand[1][2]) and player_money>=current_bet:
        jugador_hands = [[], []]
        jugador_hands[0].append(hand[0])
        jugador_hands[1].append(hand[1])
        jugador[:] = jugador_hands[0]
        split_active        = True
        current_hand_index  = 0
        player_money       -= current_bet
        last_bet            = current_bet
        per_hand_bets       = [current_bet, current_bet]
        doubledown_flags    = [False, False]
        state               = 'player'
        for i, h in enumerate(jugador_hands):
            base_x = 120 + i * HAND_SEP
            dest_y = PLAYER_Y + i * SPLIT_DY
            for idx, card_tuple in enumerate(h):
                c_obj = card_tuple[4]
                c_obj.dest_x        = base_x + idx * CARD_SPACING
                c_obj.dest_y        = dest_y
                c_obj.target_scale  = 1.06 if i == current_hand_index else 1.0
                c_obj.oculta        = False
                c_obj.start_flip(now, to_back=False)

def do_place_bet(now):
    global current_bet, current_bet_input, player_money, bet_locked, state
    global dealing_step, next_deal, mensaje, placed_chip, last_bet, round_end_time
    try:
        raw = current_bet_input.strip()
        if raw == "":
            if last_bet is None:
                mensaje = "Escribe una apuesta"; round_end_time = now; return
            bet_val = int(last_bet)
        else:
            bet_val = int(raw)

        if   bet_val <= 0:           mensaje = "Apuesta invalida";            round_end_time = now
        elif bet_val > BET_MAX:      mensaje = f"Apuesta max {BET_MAX}";      round_end_time = now
        elif bet_val > player_money: mensaje = "No tienes suficiente dinero"; round_end_time = now
        else:
            current_bet        = bet_val
            player_money      -= current_bet
            bet_locked         = True
            state              = 'dealing'
            dealing_step       = 0
            next_deal          = now + 300
            mensaje            = ""
            placed_chip        = create_placed_chip(current_bet, ANCHO//2, ALTO-148)
            last_bet           = current_bet
            current_bet_input  = ""
    except ValueError:
        mensaje = "Apuesta invalida"; round_end_time = now

while True:
    RELOJ.tick(60)
    now = pygame.time.get_ticks()

    if update_status == 'restarting' and update_restart_time != 0:
        if now >= update_restart_time + 2000:
            pygame.quit()
            os.execv(sys.executable, [sys.executable] + sys.argv)

    mouse_pos = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            if DOTS_BTN.collidepoint(pos):
                if update_status != 'checking':
                    update_status      = 'checking'
                    update_msg         = "Comprobando..."
                    update_notif_time  = now
                    threading.Thread(target=_check_for_updates, daemon=True).start()


            if state == 'player':
                if BTN_HIT.collidepoint(pos):    do_hit(now)
                if BTN_STAND.collidepoint(pos):  do_stand(now)
                if BTN_DOUBLE.collidepoint(pos): do_double(now)
                if BTN_SPLIT.collidepoint(pos):  do_split(now)

            elif state == 'betting':
                if BTN_BET.collidepoint(pos):    do_place_bet(now)

            elif state == 'round_end':
                if BTN_NEXT.collidepoint(pos):
                    if not clearing:
                        player_cards = sum(jugador_hands,[]) if jugador_hands else jugador
                        all_cards    = banca + player_cards
                        if not all_cards:
                            nueva_ronda()
                        else:
                            clearing_cards = list(all_cards)
                            for ct in clearing_cards:
                                ct[4].oculta = False
                                ct[4].start_flip(now, to_back=True)
                            clearing    = True
                            clear_phase = 'flipping'

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                reiniciar_partida(); continue

            if state == 'game_over':
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    player_money      = 1000
                    stats             = {'played':0,'won':0,'lost':0,'blackjacks':0}
                    current_bet_input = ""
                    current_bet       = 10
                    nueva_ronda()
                continue

            if evento.key == pygame.K_m:
                TABLE_STYLE_IDX = (TABLE_STYLE_IDX + 1) % len(TABLE_STYLES)

            if state == 'betting':
                if evento.key == pygame.K_BACKSPACE:
                    current_bet_input = current_bet_input[:-1]
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_s):
                    do_place_bet(now)
                else:
                    if evento.unicode and evento.unicode.isdigit():
                        if len(current_bet_input) < 6:
                            current_bet_input += evento.unicode

            elif state == 'player':
                if evento.key == pygame.K_d:                     do_double(now)
                if evento.key == pygame.K_p:                     do_split(now)
                if evento.key == pygame.K_i and insurance_offered and not insurance_taken:
                    insurance_bet = min(current_bet//2, player_money)
                    if insurance_bet > 0:
                        player_money    -= insurance_bet
                        insurance_taken  = True
                if evento.key == pygame.K_SPACE:                 do_hit(now)
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER): do_stand(now)

            elif state == 'round_end':
                if evento.key == pygame.K_s:
                    if not clearing:
                        player_cards = sum(jugador_hands,[]) if jugador_hands else jugador
                        all_cards    = banca + player_cards
                        if not all_cards:
                            nueva_ronda()
                        else:
                            clearing_cards = list(all_cards)
                            for ct in clearing_cards:
                                ct[4].oculta = False
                                ct[4].start_flip(now, to_back=True)
                            clearing    = True
                            clear_phase = 'flipping'

    if player_money <= 0 and state == 'betting' and state != 'game_over':
        state = 'game_over'

    if state == 'game_over':
        VENTANA.fill((8, 6, 14))
        for i in range(5):
            vs = pygame.Surface((ANCHO,ALTO),pygame.SRCALPHA)
            b  = i*28
            vs.fill((0,0,0,20))
            pygame.draw.rect(vs,(0,0,0,0),(b,b,ANCHO-b*2,ALTO-b*2))
            VENTANA.blit(vs,(0,0))
        tb = pygame.Surface((ANCHO,4),pygame.SRCALPHA)
        tb.fill((*GOLD,180))
        VENTANA.blit(tb,(0,ALTO//2-85))
        VENTANA.blit(tb,(0,ALTO//2+70))
        t1 = FUENTE_GRANDE.render("SIN FICHAS", True, GOLD)
        t2 = FUENTE.render("Has agotado todo tu dinero", True, (200,200,200))
        t3 = FUENTE_PEQUENA.render("Pulsa  ENTER  o  R  para volver a empezar con 1000 fichas", True, (160,160,160))
        VENTANA.blit(t1,(ANCHO//2-t1.get_width()//2, ALTO//2-80))
        VENTANA.blit(t2,(ANCHO//2-t2.get_width()//2, ALTO//2-8))
        VENTANA.blit(t3,(ANCHO//2-t3.get_width()//2, ALTO//2+50))
        pnl = pygame.Rect(ANCHO//2-160,ALTO//2+90,320,50)
        draw_hud_panel(pnl, alpha=180)
        sl = FUENTE_PEQUENA.render(
            f"Partidas: {stats['played']}   Ganadas: {stats['won']}   BJ: {stats['blackjacks']}", True, GOLD_DARK)
        VENTANA.blit(sl,(pnl.centerx-sl.get_width()//2, pnl.centery-sl.get_height()//2))
        pygame.display.update()
        continue

    if state == 'dealing' and (not clearing) and now >= next_deal:
        if   dealing_step == 0: repartir(jugador, PLAYER_Y, start_pos=DECK_POS)
        elif dealing_step == 1: repartir(banca,   DEALER_Y, True,  start_pos=DECK_POS)
        elif dealing_step == 2: repartir(jugador, PLAYER_Y, start_pos=DECK_POS)
        elif dealing_step == 3: repartir(banca,   DEALER_Y, True,  start_pos=DECK_POS)
        elif dealing_step == 4:
            if banca:
                if banca[0][0] == 'A':
                    insurance_offered = True
                    insurance_taken   = False
                    insurance_bet     = 0
                banca[0][4].start_flip(now)
            state = 'player'
            if not split_active:
                if len(jugador)==2 and calcular(jugador)==21:
                    revelar_banca(now)
                    mensaje         = "BLACKJACK!"
                    state           = 'dealer'
                    dealer_thinking = False
                    dealer_target   = schedule_dealer_target()
                    next_action     = now + 600
        dealing_step += 1
        next_deal     = now + 400

    if state == 'dealer' and (not clearing):
        cards_settled = len(banca)>0 and all((not c[4].flipping) and (abs(c[4].x-c[4].dest_x)<1) for c in banca)
        if cards_settled:
            if not dealer_thinking:
                dealer_thinking = True
                think_delay     = DEALER_SETTLE_DELAY + random_module.randint(-200,800)
                next_action     = now + max(400, think_delay)
            else:
                if now >= next_action:
                    pb = calcular(banca)
                    if 'dealer_target' not in globals():
                        dealer_target = schedule_dealer_target()
                    hands = list(iter_player_hands())
                    any_player_blackjack = any(len(h)==2 and calcular(h)==21 for h in hands)
                    dealer_blackjack     = (len(banca)==2 and calcular(banca)==21)

                    def settle_round():
                        global player_money, placed_chip, per_hand_bets, state, round_end_time, mensaje
                        if insurance_taken:
                            if dealer_blackjack: player_money += insurance_bet*2
                        results = []
                        for idx, hand in enumerate(hands):
                            bet_amt = per_hand_bets[idx] if (per_hand_bets and idx<len(per_hand_bets)) else current_bet
                            pj = calcular(hand)
                            rtype = None
                            if len(hand)==2 and calcular(hand)==21 and not dealer_blackjack:
                                player_money += int(bet_amt*2.5)+25
                                stats['blackjacks'] += 1
                                stats['won']        += 1
                                rtype = 'blackjack'
                            else:
                                if   pj > 21:           rtype = 'lose'
                                elif pb > 21 or pj > pb:rtype = 'win'
                                elif pj < pb:           rtype = 'lose'
                                else:                   rtype = 'tie'
                                if   rtype=='win': player_money += bet_amt*2; stats['won']  += 1
                                elif rtype=='tie': player_money += bet_amt
                                else:                                          stats['lost'] += 1
                            results.append(rtype)
                        stats['played'] += 1
                        if   any(r=='blackjack' for r in results): mensaje = "BLACKJACK!"
                        elif any(r=='win'       for r in results): mensaje = "HAS GANADO"
                        elif all(r=='tie'       for r in results): mensaje = "EMPATE"
                        else:                                       mensaje = "HAS PERDIDO"
                        if placed_chip:
                            if any(r in ('win','blackjack') for r in results):
                                tx,ty = ANCHO+120,-120
                            elif all(r=='tie' for r in results):
                                tx,ty = ANCHO//2, ALTO-148
                            else:
                                tx,ty = BANK_POS
                            sx,sy = placed_chip['x'], placed_chip['y']
                            dist  = math.hypot(tx-sx,ty-sy) or 1.0
                            placed_chip.update({'moving':True,'vx':(tx-sx)/dist*10,'vy':(ty-sy)/dist*10,
                                                'target_x':tx,'target_y':ty,'expire_on_arrival':True})
                        player_chip_stack[:] = []
                        if any(r in ('win','blackjack') for r in results):
                            spawn_particles(ANCHO//2, ALTO//2+40, DORADO, count=25)
                            overlay_flash.update({'active':True,'color':(255,255,255),'alpha':180,'start':now,'duration':300})
                        elif all(r=='tie' for r in results):
                            overlay_flash.update({'active':True,'color':(200,200,200),'alpha':120,'start':now,'duration':220})
                        else:
                            spawn_particles(ANCHO//2, ALTO//2, ROJO, count=25)
                            overlay_flash.update({'active':True,'color':(150,0,0),'alpha':180,'start':now,'duration':350})
                        per_hand_bets  = None
                        state          = 'round_end'
                        round_end_time = now

                    if any_player_blackjack and not dealer_blackjack:
                        dealer_thinking = False
                        revelar_banca(now)
                        settle_round()
                        continue

                    if pb < 17 and pb < dealer_target:
                        repartir(banca, DEALER_Y)
                        dealer_thinking = True
                        next_action     = now + DEALER_SETTLE_DELAY + random_module.randint(0,600)
                    else:
                        dealer_thinking = False
                        revelar_banca(now)
                        settle_round()

    for c in banca:
        c[4].target_scale = 1.0
        c[4].actualizar(now)
        c[4].dibujar(now)

    if split_active and jugador_hands:
        for i, hand in enumerate(jugador_hands):
            base_x   = 120 + i * HAND_SEP
            offset_y = PLAYER_Y + i * SPLIT_DY
            is_active = (i == current_hand_index and state == 'player')
            tscale    = 1.06 if is_active else 1.0
            for idx, c in enumerate(hand):
                c[4].dest_x       = base_x + idx * CARD_SPACING
                c[4].dest_y       = offset_y
                c[4].target_scale = tscale
                c[4].actualizar(now)
                c[4].dibujar(now)
    else:
        for c in jugador:
            c[4].target_scale = 1.0
            c[4].actualizar(now)
            c[4].dibujar(now)

    hand_cur = get_current_hand()
    player_visible = calcular_visible(hand_cur)
    if state == 'player' and player_visible != 0:
        if player_visible == 21:
            if split_active and current_hand_index < len(jugador_hands)-1:
                current_hand_index += 1
            else:
                state           = 'dealer'
                revelar_banca(now)
                dealer_thinking = False
                dealer_target   = schedule_dealer_target()
                next_action     = now + 600
        elif player_visible > 21:
            if split_active and current_hand_index < len(jugador_hands)-1:
                overlay_flash.update({'active':True,'color':(150,0,0),'alpha':200,'start':now,'duration':300})
                mensaje = f"MANO {current_hand_index+1} BUST"
                current_hand_index += 1
                last_pedir_time    = now
            elif split_active and current_hand_index == len(jugador_hands)-1:
                overlay_flash.update({'active':True,'color':(150,0,0),'alpha':200,'start':now,'duration':300})
                mensaje = f"MANO {current_hand_index+1} BUST"
                revelar_banca(now)
                state           = 'dealer'
                dealer_thinking = False
                dealer_target   = schedule_dealer_target()
                next_action     = now + 600
            else:
                mensaje = "HAS PERDIDO"
                stats['lost']  += 1
                stats['played']+= 1
                overlay_flash.update({'active':True,'color':(150,0,0),'alpha':200,'start':now,'duration':350})
                revelar_banca(now)
                state          = 'round_end'
                round_end_time = now
                if placed_chip:
                    sx,sy = placed_chip['x'], placed_chip['y']
                    tx,ty = BANK_POS
                    dist  = math.hypot(tx-sx,ty-sy) or 1.0
                    placed_chip.update({'moving':True,'vx':(tx-sx)/dist*10,'vy':(ty-sy)/dist*10,
                                        'target_x':tx,'target_y':ty,'expire_on_arrival':True})

    if state == 'round_end' and (not clearing) and round_end_time!=0 and now>=round_end_time+ROUND_DELAY:
        player_cards = sum(jugador_hands,[]) if jugador_hands else jugador
        all_cards    = banca + player_cards
        if not all_cards:
            nueva_ronda()
        else:
            clearing_cards = list(all_cards)
            for ct in clearing_cards:
                ct[4].oculta = False
                ct[4].start_flip(now, to_back=True)
            clearing    = True
            clear_phase = 'flipping'
        round_end_time = 0

    if clearing:
        if clear_phase == 'flipping':
            flips_done = all((not c[4].flipping) for c in clearing_cards)
            if flips_done:
                for idx, c in enumerate(clearing_cards):
                    c[4].dest_x    = ANCHO + 80 + idx*30
                    c[4].target_scale = 0.9
                clear_phase = 'moving'
        elif clear_phase == 'moving':
            if not clearing_cards:
                clearing = False; clear_phase = None; nueva_ronda()
            else:
                done = all(c[4].x >= c[4].dest_x-1 for c in clearing_cards)
                if done:
                    clearing = False; clear_phase = None
                    clearing_cards[:] = []
                    nueva_ronda()

    draw_table_bg()

    for c in banca:
        c[4].dibujar(now)

    if split_active and jugador_hands:
        for i, hand in enumerate(jugador_hands):
            for c in hand:
                c[4].dibujar(now)
    else:
        for c in jugador:
            c[4].dibujar(now)

    if clearing:
        for c in clearing_cards:
            c[4].dibujar(now)

    dealer_pnl = pygame.Rect(46, 15, 260, 48)
    draw_hud_panel(dealer_pnl)
    if any(c[4].oculta for c in banca):
        txt_parts = " + ".join("?" if c[4].oculta else str(c[2]) for c in banca)
        score_lbl = FUENTE.render(f"Banca: {txt_parts}", True, BLANCO)
    else:
        bv = calcular_visible(banca)
        score_lbl = FUENTE.render(f"Banca: {bv}", True,
                                  (255,100,100) if bv>21 else BLANCO)
    VENTANA.blit(score_lbl, (dealer_pnl.x+12, dealer_pnl.y + (dealer_pnl.h - score_lbl.get_height())//2))

    player_pnl = pygame.Rect(46, ALTO-72, ANCHO-92, 54)
    draw_hud_panel(player_pnl)

    if split_active and jugador_hands:
        lbl_left  = FUENTE.render(f"Mano 1: {calcular(jugador_hands[0])}", True, BLANCO)
        lbl_right = FUENTE.render(f"Mano 2: {calcular(jugador_hands[1])}", True, BLANCO)
        cx_split  = ANCHO//2
        VENTANA.blit(lbl_left,  (cx_split - 280, player_pnl.y + (player_pnl.h-lbl_left.get_height())//2))
        VENTANA.blit(lbl_right, (cx_split +  40, player_pnl.y + (player_pnl.h-lbl_right.get_height())//2))
    else:
        pv  = calcular(jugador)
        col = (255,100,100) if pv>21 else (GOLD_LIGHT if pv==21 else BLANCO)
        lbl = FUENTE.render(f"Jugador: {pv}", True, col)
        VENTANA.blit(lbl, (player_pnl.x+14, player_pnl.y+(player_pnl.h-lbl.get_height())//2))

    money_txt = FUENTE_PEQUENA.render(f"Fichas: {player_money}", True, GOLD)
    bet_txt   = FUENTE_PEQUENA.render(f"Apuesta: {current_bet}", True, (180,225,180))
    stat_txt  = FUENTE_PEQUENA.render(
        f"W:{stats['won']}  L:{stats['lost']}  BJ:{stats['blackjacks']}", True, (140,140,140))
    right_x = player_pnl.right - 14
    VENTANA.blit(money_txt, (right_x - money_txt.get_width(), player_pnl.y + 4))
    VENTANA.blit(bet_txt,   (right_x - bet_txt.get_width(),   player_pnl.y + 28))
    stat_x = player_pnl.centerx - stat_txt.get_width()//2
    VENTANA.blit(stat_txt,  (stat_x, player_pnl.y+(player_pnl.h-stat_txt.get_height())//2))

    if state == 'betting':
        inp_w, inp_h = 220, 38
        inp_x = ANCHO//2 - inp_w//2
        inp_y = _BY - 60
        inp_bg = pygame.Surface((inp_w, inp_h), pygame.SRCALPHA)
        pygame.draw.rect(inp_bg, (10,20,10,220), (0,0,inp_w,inp_h), border_radius=8)
        pygame.draw.rect(inp_bg, (*GOLD_DARK,200), (0,0,inp_w,inp_h), 1, border_radius=8)
        VENTANA.blit(inp_bg, (inp_x, inp_y))
        display_text = current_bet_input if current_bet_input else f"Última: {last_bet}" if last_bet else ""
        col_in = BLANCO if current_bet_input else (120,120,120)
        txt_in = FUENTE_PEQUENA.render(display_text, True, col_in)
        VENTANA.blit(txt_in, (inp_x+10, inp_y+(inp_h-txt_in.get_height())//2))
        if (now//500)%2==0 and state=='betting':
            curs_x = inp_x + 10 + txt_in.get_width() + 2
            pygame.draw.rect(VENTANA, BLANCO, (curs_x, inp_y+8, 2, inp_h-16))
        lbl_ap = FUENTE_PEQUENA.render(f"Apuesta (máx {BET_MAX}):", True, GOLD_DARK)
        VENTANA.blit(lbl_ap, (inp_x - lbl_ap.get_width() - 8,
                               inp_y + (inp_h - lbl_ap.get_height())//2))

    if state == 'betting':
        quick_vals = [10, 25, 50, 100, 250]
        qw, qh = 58, 28
        total_qw = len(quick_vals)*qw + (len(quick_vals)-1)*8
        qx_start = ANCHO//2 - total_qw//2
        qy = _BY - 100
        for qi, qv in enumerate(quick_vals):
            if qv > player_money: continue
            qrect = pygame.Rect(qx_start + qi*(qw+8), qy, qw, qh)
            qhov  = qrect.collidepoint(mouse_pos)
            qcol  = (45,105,55) if qhov else (28,72,35)
            pygame.draw.rect(VENTANA, qcol, qrect, border_radius=6)
            pygame.draw.rect(VENTANA, GOLD_DARK, qrect, 1, border_radius=6)
            ql = FUENTE_PEQUENA.render(str(qv), True, BLANCO)
            VENTANA.blit(ql, (qrect.centerx-ql.get_width()//2, qrect.centery-ql.get_height()//2))
            if pygame.mouse.get_pressed()[0] and qhov and state=='betting':
                current_bet_input = str(qv)

    if insurance_offered and not insurance_taken and state == 'player':
        ins_s = pygame.Surface((360,38), pygame.SRCALPHA)
        pygame.draw.rect(ins_s,(10,10,60,210),(0,0,360,38),border_radius=8)
        pygame.draw.rect(ins_s,(*GOLD_DARK,180),(0,0,360,38),1,border_radius=8)
        VENTANA.blit(ins_s,(ANCHO//2-180, DEALER_Y+CARD_H+12))
        itxt = FUENTE_PEQUENA.render("Seguro disponible  —  [I] para asegurar", True, GOLD)
        VENTANA.blit(itxt,(ANCHO//2-itxt.get_width()//2, DEALER_Y+CARD_H+20))

    draw_mensaje(mensaje, now)

    draw_action_buttons(state, mouse_pos, split_active, get_current_hand(),
                        player_money, current_bet, doubledown_flags,
                        current_hand_index, per_hand_bets)

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
            render_chip_dict(VENTANA, placed_chip)

    for i, c in enumerate(player_chip_stack[-14:]):
        px = PLAYER_STACK_POS[0] + (i%7)*11
        py = PLAYER_STACK_POS[1] - (i//7)*7
        _draw_chip_3d(VENTANA, int(px), int(py), 15, c['color'], c['value'])

    for ac in chips_anim[:]:
        ac['x'] += ac['vx']; ac['y'] += ac['vy']
        if math.hypot(ac['x']-ac['target_x'], ac['y']-ac['target_y']) < 8:
            try: chips_anim.remove(ac)
            except ValueError: pass
            continue
        render_chip_dict(VENTANA, ac)

    dt = RELOJ.get_time()
    for p in particles[:]:
        p[0] += p[2]; p[1] += p[3]; p[4] -= dt; p[3] += 0.10
        if p[4] <= 0:
            particles.remove(p); continue
        alpha = max(0, min(255, int(255*(p[4]/1200.0))))
        size = 7
        ps   = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(ps, (*p[5], alpha), (size//2, size//2), size//2)
        VENTANA.blit(ps, (p[0]-size//2, p[1]-size//2))

    if overlay_flash['active']:
        elapsed = now - overlay_flash['start']
        if elapsed > overlay_flash['duration']:
            overlay_flash['active'] = False
        else:
            a  = int(overlay_flash['alpha'] * (1 - elapsed/overlay_flash['duration']))
            ov = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            ov.fill((*overlay_flash['color'], a))
            VENTANA.blit(ov, (0,0))

    btn_hovered = DOTS_BTN.collidepoint(mouse_pos)
    btn_c       = (80,80,80) if not btn_hovered else (115,115,115)
    pygame.draw.rect(VENTANA, btn_c,  DOTS_BTN, border_radius=6)
    pygame.draw.rect(VENTANA, NEGRO,  DOTS_BTN, 1, border_radius=6)
    d_s = FUENTE_PEQUENA.render("···", True, BLANCO)
    VENTANA.blit(d_s, (DOTS_BTN.centerx-d_s.get_width()//2, DOTS_BTN.centery-d_s.get_height()//2))

    if update_status is not None:
        elapsed_notif  = now - update_notif_time
        is_permanent   = update_status in ('checking','restarting')
        show_notif     = is_permanent or (elapsed_notif < 5000)
        if show_notif:
            alpha_notif = 230
            if not is_permanent and elapsed_notif > 3500:
                alpha_notif = max(0, int(230*(1-(elapsed_notif-3500)/1500)))
            if update_status == 'restarting':
                notif_color  = (20,100,200)
                secs_left    = max(0, 2-(now-update_restart_time)//1000)
                display_msg  = f"Actualizado! Reiniciando en {secs_left}s..."
            else:
                display_msg = update_msg
                notif_color = (30,120,50) if update_status=='up_to_date' else \
                              (40,40,40)  if update_status=='checking'   else (150,30,30)
            ns  = FUENTE_PEQUENA.render(display_msg, True, BLANCO)
            nw, nh = ns.get_width()+24, ns.get_height()+14
            nx, ny = ANCHO-nw-10, DOTS_BTN.bottom+6
            bg  = pygame.Surface((nw,nh), pygame.SRCALPHA)
            bg.fill((*notif_color, alpha_notif))
            VENTANA.blit(bg,(nx,ny))
            pygame.draw.rect(VENTANA,NEGRO,(nx,ny,nw,nh),1,border_radius=6)
            VENTANA.blit(ns,(nx+12,ny+7))

    reiniciar_rect = pygame.Rect(ANCHO-142, ALTO-66, 134, 36)
    r_hov   = reiniciar_rect.collidepoint(mouse_pos)
    r_col   = (155,35,35) if not r_hov else (190,55,55)
    pygame.draw.rect(VENTANA, r_col,  reiniciar_rect, border_radius=7)
    pygame.draw.rect(VENTANA, NEGRO,  reiniciar_rect, 1, border_radius=7)
    r_txt = FUENTE_PEQUENA.render("R: Reiniciar", True, BLANCO)
    VENTANA.blit(r_txt,(reiniciar_rect.centerx-r_txt.get_width()//2,
                        reiniciar_rect.centery-r_txt.get_height()//2))
    if pygame.mouse.get_pressed()[0] and r_hov:
        reiniciar_partida()

    pygame.display.update()
