import pygame
import random as random_module
import sys
import os
import math
import threading
import urllib.request

pygame.init()

VERSION = "0.1.0"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/humrand/blackjack-python/main/blackjack_V0.1.py"

ANCHO, ALTO = 1000, 700
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Blackjack 2D - FIXED - Hand Anim v4")

FUENTE = pygame.font.SysFont("arial", 32, bold=True)
FUENTE_PEQUENA = pygame.font.SysFont("arial", 24, bold=True)
FUENTE_GRANDE = pygame.font.SysFont("arial", 70, bold=True)
FUENTE_MSG = pygame.font.SysFont("arial", 40, bold=True)
FUENTE_INSTR = pygame.font.SysFont("arial", 20, bold=True)
RELOJ = pygame.time.Clock()

VERDE = (20, 120, 20)
VERDE_OSCURO = (12, 80, 12)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (200, 0, 0)
DORADO = (230, 190, 60)
STRONG_GREEN = (0, 150, 0)

CARD_W = 96
CARD_H = 144
CARD_SPACING = 125

HAND_SEP = 300

PEDIR_DELAY = 500
ROUND_DELAY = 2000

BET_MAX = 250

SUIT_CHAR = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}

DECK_POS = (ANCHO // 2, 20)
DEALER_POS = (ANCHO // 2, 60)
PLAYER_STACK_POS = (120, ALTO - 70)
BANK_POS = (ANCHO // 2, 40)

def get_symbol_font(size):
    candidates = [
        "Symbola",
        "DejaVuSans",
        "DejaVu Sans",
        "FreeSerif",
        "Segoe UI Symbol",
        "Arial Unicode MS",
        "Noto Sans Symbols2",
        "Noto Sans Symbols"
    ]
    local_paths = [
        os.path.join("fonts", "Symbola.ttf"),
        os.path.join("fonts", "DejaVuSans.ttf"),
        os.path.join("fonts", "DejaVuSans-Oblique.ttf")
    ]
    for p in local_paths:
        if os.path.exists(p):
            try:
                return pygame.font.Font(p, size)
            except Exception:
                pass
    for name in candidates:
        try:
            path = pygame.font.match_font(name)
            if path:
                try:
                    return pygame.font.Font(path, size)
                except Exception:
                    pass
        except Exception:
            pass
    return pygame.font.SysFont("arial", size, bold=True)

SYMBOL_FONT = get_symbol_font(56)
FACE_SYMBOL_MAP = {"J": '♚', "K": '♚', "Q": '♛'}

def crear_baraja():
    palos = [("S", NEGRO), ("H", ROJO), ("D", ROJO), ("C", NEGRO)]
    valores = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    baraja = []
    for palo, color in palos:
        for v in valores:
            if v == "A":
                valor_num = 11
            elif v in ["J", "Q", "K"]:
                valor_num = 10
            else:
                valor_num = int(v)
            baraja.append((v, palo, valor_num, color))
    random_module.shuffle(baraja)
    return baraja

def calcular(mano):
    total = sum(c[2] for c in mano)
    ases = sum(1 for c in mano if c[0] == "A")
    while total > 21 and ases:
        total -= 10
        ases -= 1
    return total

def calcular_visible(mano):
    visibles = [c for c in mano if (not c[4].oculta) and (not c[4].flipping) and (abs(c[4].x - c[4].dest_x) < 1)]
    if not visibles:
        return 0
    total = sum(c[2] for c in visibles)
    ases = sum(1 for c in visibles if c[0] == "A")
    while total > 21 and ases:
        total -= 10
        ases -= 1
    return total

class Carta:
    def __init__(self, valor, palo, valor_num, color, dest_x, dest_y, start_pos=None):
        self.valor = valor
        self.palo = palo
        self.valor_num = valor_num
        self.color = color
        if start_pos:
            self.x, self.y = float(start_pos[0]), float(start_pos[1])
        else:
            self.x, self.y = float(DECK_POS[0]), float(DECK_POS[1])
        self.dest_x = float(dest_x)
        self.dest_y = float(dest_y)
        self.w = CARD_W
        self.h = CARD_H
        self.oculta = False
        self.flipping = False
        self.flip_start = 0
        self.flip_duration = 300
        self.front = None
        self.back = None
        self.flip_target_back = False
        self.scale = 1.0
        self.target_scale = 1.0
        self.scale_speed = 0.12
        self._create_faces()

    def _create_faces(self):
        self.front = self.crear_front()
        self.back = self.crear_back()

    def crear_front(self):
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(surf, BLANCO, (0, 0, self.w, self.h), border_radius=12)
        pygame.draw.rect(surf, NEGRO, (0, 0, self.w, self.h), 2, border_radius=12)
        idx = FUENTE_PEQUENA.render(self.valor, True, self.color)
        surf.blit(idx, (8, 6))
        idx_rot = pygame.transform.rotate(idx, 180)
        surf.blit(idx_rot, (self.w - idx_rot.get_width() - 8, self.h - idx_rot.get_height() - 6))
        try:
            if self.valor in FACE_SYMBOL_MAP:
                face_char = FACE_SYMBOL_MAP[self.valor]
                sym_surf = SYMBOL_FONT.render(face_char, True, self.color)
                surf.blit(sym_surf, ((self.w - sym_surf.get_width()) // 2, (self.h - sym_surf.get_height()) // 2 - 6))
            else:
                symbol_char = SUIT_CHAR.get(self.palo, '?')
                sym_surf = SYMBOL_FONT.render(symbol_char, True, self.color)
                surf.blit(sym_surf, ((self.w - sym_surf.get_width()) // 2, (self.h - sym_surf.get_height()) // 2 - 6))
        except Exception:
            if self.valor in FACE_SYMBOL_MAP:
                simple = FUENTE_GRANDE.render(self.valor, True, self.color)
            else:
                simple = FUENTE_PEQUENA.render(self.palo, True, self.color)
            surf.blit(simple, ((self.w - simple.get_width()) // 2, (self.h - simple.get_height()) // 2))
        return surf

    def crear_back(self):
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (150, 0, 0), (0, 0, self.w, self.h), border_radius=12)
        pygame.draw.rect(surf, NEGRO, (0, 0, self.w, self.h), 2, border_radius=12)
        step_x = 20
        step_y = 24
        for i in range(12, self.w - 12, step_x):
            for j in range(12, self.h - 12, step_y):
                pygame.draw.circle(surf, (220, 70, 70), (i, j), 5)
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
        surf_to_blit = None
        if not self.flipping:
            surf_to_blit = self.back if self.oculta else self.front
            new_w = max(1, int(self.w * self.scale))
            new_h = max(1, int(self.h * self.scale))
            scaled = pygame.transform.smoothscale(surf_to_blit, (new_w, new_h))
            VENTANA.blit(scaled, (rx - (new_w - self.w)//2, ry - (new_h - self.h)//2))
            return
        progreso = (now - self.flip_start) / self.flip_duration
        if progreso >= 1:
            self.flipping = False
            self.oculta = bool(self.flip_target_back)
            surf_to_blit = self.back if self.oculta else self.front
            new_w = max(1, int(self.w * self.scale))
            new_h = max(1, int(self.h * self.scale))
            scaled = pygame.transform.smoothscale(surf_to_blit, (new_w, new_h))
            VENTANA.blit(scaled, (rx - (new_w - self.w)//2, ry - (new_h - self.h)//2))
            return
        if self.flip_target_back:
            if progreso < 0.5:
                escala = 1 - progreso * 2
                surf = self.front
            else:
                escala = (progreso - 0.5) * 2
                surf = self.back
        else:
            if progreso < 0.5:
                escala = 1 - progreso * 2
                surf = self.back
            else:
                escala = (progreso - 0.5) * 2
                surf = self.front
        ancho = max(1, int(self.w * escala))
        h_final = max(1, int(self.h * self.scale))
        scaled = pygame.transform.smoothscale(surf, (ancho, h_final))
        x_blit = rx + (self.w - ancho)//2 - ( (int(self.w*self.scale) - self.w)//2 )
        y_blit = ry - (h_final - self.h)//2
        VENTANA.blit(scaled, (x_blit, y_blit))

def get_chip_style(value):
    v = int(value)
    if 1 <= v <= 10:
        return {'shape': 'circle', 'r': 14, 'color': (180, 30, 30)}
    if 11 <= v <= 34:
        return {'shape': 'circle', 'r': 18, 'color': (220, 120, 20)}
    if 35 <= v <= 64:
        return {'shape': 'circle', 'r': 22, 'color': (20, 160, 80)}
    if 65 <= v <= 99:
        return {'shape': 'circle', 'r': 26, 'color': (30, 120, 220)}
    if 100 <= v <= 199:
        return {'shape': 'rect', 'w': 48, 'h': 28, 'color': (20, 150, 80)}
    if 200 <= v <= 250:
        return {'shape': 'rect', 'w': 56, 'h': 32, 'color': (220, 100, 160)}
    return {'shape': 'circle', 'r': 20, 'color': (200, 150, 60)}

def create_placed_chip(value, x, y):
    style = get_chip_style(value)
    base = {'x': float(x), 'y': float(y), 'value': int(value),
            'moving': False, 'vx': 0.0, 'vy': 0.0, 'target_x': x, 'target_y': y}
    base.update(style)
    return base

def make_chip_move_dict(value, sx, sy, tx, ty, speed=6.0):
    dx = tx - sx; dy = ty - sy
    dist = math.hypot(dx, dy)
    if dist == 0:
        vx = vy = 0.0
    else:
        vx = dx / dist * speed
        vy = dy / dist * speed
    style = get_chip_style(value)
    d = {'x': float(sx), 'y': float(sy), 'vx': vx, 'vy': vy,
         'target_x': tx, 'target_y': ty, 'value': int(value), 'moving': True}
    d.update(style)
    return d

def _chip_font_for_circle(r):
    size = max(10, int(r * 0.7))
    return pygame.font.SysFont("arial", size, bold=True)

def _chip_font_for_rect(h):
    size = max(12, int(h * 0.6))
    return pygame.font.SysFont("arial", size, bold=True)

TABLE_STYLES = [
    {'name': 'verde clásico', 'color': VERDE},
    {'name': 'rojo casino', 'color': (100, 20, 20)},
    {'name': 'negro lujo', 'color': (20, 20, 20)}
]
TABLE_STYLE_IDX = 0

DEALER_AVATAR = None
if os.path.exists(os.path.join("images", "dealer.png")):
    try:
        img = pygame.image.load(os.path.join("images", "dealer.png")).convert_alpha()
        DEALER_AVATAR = pygame.transform.smoothscale(img, (120, 120))
    except Exception:
        DEALER_AVATAR = None

baraja = []
jugador = []
jugador_hands = None
current_hand_index = 0
split_active = False

banca = []

player_money = 1000
current_bet = 10
bet_locked = False
current_bet_input = ""
last_bet = None

insurance_offered = False
insurance_bet = 0
insurance_taken = False

doubledown_flags = []
per_hand_bets = None

stats = {'played': 0, 'won': 0, 'lost': 0, 'blackjacks': 0}

state = 'betting'
dealing_step = 0
next_deal = 0
dealer_thinking = False
next_action = 0
last_pedir_time = 0
round_end_time = 0

DEALER_SETTLE_DELAY = 900

clearing = False
clear_phase = None
clearing_cards = []

particles = []
chips_anim = []
placed_chip = None
player_chip_stack = []

overlay_flash = {'active': False, 'color': (0, 0, 0), 'alpha': 0, 'start': 0, 'duration': 400}

update_status = None  
update_msg = ""
update_notif_time = 0
DOTS_BTN = pygame.Rect(ANCHO - 46, 8, 38, 28)

def _check_for_updates():
    global update_status, update_msg, update_notif_time
    try:
        req = urllib.request.urlopen(GITHUB_RAW_URL, timeout=6)
        content = req.read().decode('utf-8', errors='ignore')
        remote_version = None
        for line in content.splitlines():
            if line.startswith('VERSION'):
                parts = line.split('=')
                if len(parts) == 2:
                    remote_version = parts[1].strip().strip('"').strip("'")
                    break
        if remote_version is None:
            update_status = 'error'
            update_msg = "No se pudo leer la version remota"
        elif remote_version == VERSION:
            update_status = 'up_to_date'
            update_msg = f"Ya tienes la ultima version ({VERSION})"
        else:
            update_status = 'available'
            update_msg = f"Nueva version disponible: {remote_version}  (actual: {VERSION})"
    except Exception as e:
        update_status = 'error'
        update_msg = "Sin conexion o repo no alcanzable"
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
        for h in jugador_hands:
            yield h
    else:
        yield jugador

def repartir(mano, y, oculta=False, start_pos=None):
    global baraja, split_active, jugador_hands
    if not baraja:
        baraja = crear_baraja()
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
        if c[4].oculta:
            c[4].start_flip(now)

def schedule_dealer_target():
    return 18 if random_module.random() < 0.15 else 17

def spawn_particles(x, y, color, count=30):
    for _ in range(count):
        angle = random_module.random() * 2 * math.pi
        speed = random_module.random() * random_module.random() * 8 + 2
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        life = random_module.random() * 800 + 400
        particles.append([x, y, vx, vy, life, color])

def reiniciar_partida():
    global player_money, stats, current_bet_input, current_bet, last_bet
    player_money = 1000
    stats = {'played': 0, 'won': 0, 'lost': 0, 'blackjacks': 0}
    current_bet_input = ""
    current_bet = 10
    last_bet = None
    nueva_ronda()

def nueva_ronda():
    global baraja, jugador, banca, state, dealing_step, next_deal, mensaje, dealer_thinking, next_action
    global last_pedir_time, round_end_time, current_bet, bet_locked, player_money, stats, placed_chip, chips_anim
    global split_active, jugador_hands, current_hand_index, doubledown_flags, player_chip_stack, clearing_cards, per_hand_bets
    baraja = crear_baraja()
    jugador = []
    banca = []
    jugador_hands = None
    split_active = False
    current_hand_index = 0
    doubledown_flags = []
    mensaje = ""
    dealing_step = 0
    next_deal = pygame.time.get_ticks() + 300
    dealer_thinking = False
    next_action = 0
    last_pedir_time = 0
    round_end_time = 0
    state = 'betting'
    bet_locked = False
    placed_chip = None
    chips_anim = []
    player_chip_stack = []
    clearing_cards = []
    per_hand_bets = None

nueva_ronda()

while True:
    RELOJ.tick(60)
    now = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if DOTS_BTN.collidepoint(evento.pos):
                if update_status != 'checking':
                    update_status = 'checking'
                    update_msg = "Comprobando..."
                    update_notif_time = pygame.time.get_ticks()
                    threading.Thread(target=_check_for_updates, daemon=True).start()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                reiniciar_partida()
                continue
            if state == 'game_over':
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    player_money = 1000
                    stats = {'played': 0, 'won': 0, 'lost': 0, 'blackjacks': 0}
                    current_bet_input = ""
                    current_bet = 10
                    nueva_ronda()
                continue
            if evento.key == pygame.K_m:
                TABLE_STYLE_IDX = (TABLE_STYLE_IDX + 1) % len(TABLE_STYLES)
            if state == 'betting':
                if evento.key == pygame.K_BACKSPACE:
                    current_bet_input = current_bet_input[:-1]
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_s):
                    try:
                        if current_bet_input.strip() == "":
                            if last_bet is None:
                                mensaje = "Escribe una apuesta"
                                round_end_time = now
                            else:
                                bet_val = int(last_bet)
                                if bet_val <= 0:
                                    mensaje = "Apuesta invalida"
                                    round_end_time = now
                                elif bet_val > BET_MAX:
                                    mensaje = f"Apuesta max {BET_MAX}"
                                    round_end_time = now
                                elif bet_val > player_money:
                                    mensaje = "No tienes suficiente dinero"
                                    round_end_time = now
                                else:
                                    current_bet = bet_val
                                    player_money -= current_bet
                                    bet_locked = True
                                    state = 'dealing'
                                    dealing_step = 0
                                    next_deal = now + 300
                                    mensaje = ""
                                    placed_chip = create_placed_chip(current_bet, ANCHO//2, ALTO-120)
                                    current_bet_input = ""
                        else:
                            bet_val = int(current_bet_input)
                            if bet_val <= 0:
                                mensaje = "Apuesta invalida"
                                round_end_time = now
                            elif bet_val > BET_MAX:
                                mensaje = f"Apuesta max {BET_MAX}"
                                round_end_time = now
                            elif bet_val > player_money:
                                mensaje = "No tienes suficiente dinero"
                                round_end_time = now
                            else:
                                current_bet = bet_val
                                player_money -= current_bet
                                bet_locked = True
                                state = 'dealing'
                                dealing_step = 0
                                next_deal = now + 300
                                mensaje = ""
                                placed_chip = create_placed_chip(current_bet, ANCHO//2, ALTO-120)
                                last_bet = current_bet
                                current_bet_input = ""
                    except ValueError:
                        mensaje = "Apuesta invalida"
                        round_end_time = now
                else:
                    if evento.unicode and evento.unicode.isdigit():
                        if len(current_bet_input) < 6:
                            current_bet_input += evento.unicode

            elif state == 'player':
                if evento.key == pygame.K_d:
                    hand = get_current_hand()
                    if split_active and not doubledown_flags:
                        doubledown_flags = [False] * len(jugador_hands)
                    can_double = False
                    if split_active:
                        can_double = (len(hand) == 2 and player_money >= (per_hand_bets[current_hand_index] if per_hand_bets else current_bet) and (not doubledown_flags[current_hand_index]))
                    else:
                        can_double = (len(hand) == 2 and player_money >= current_bet and (not doubledown_flags))
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
                            dest_y = 200 + current_hand_index * 70
                            repartir(hand, dest_y)
                            if current_hand_index < len(jugador_hands)-1:
                                current_hand_index += 1
                            else:
                                state = 'dealer'
                                revelar_banca(now)
                                dealer_thinking = False
                                dealer_target = schedule_dealer_target()
                                next_action = now + 600
                        else:
                            player_money -= current_bet
                            current_bet *= 2
                            dest_y = 200
                            repartir(hand, dest_y)
                            state = 'dealer'
                            revelar_banca(now)
                            dealer_thinking = False
                            dealer_target = schedule_dealer_target()
                            next_action = now + 600

                if evento.key == pygame.K_p:
                    hand = get_current_hand()
                    if len(hand) == 2 and (hand[0][2] == hand[1][2]) and player_money >= current_bet:
                        jugador_hands = [[], []]
                        jugador_hands[0].append(hand[0])
                        jugador_hands[1].append(hand[1])
                        jugador[:] = jugador_hands[0]
                        split_active = True
                        current_hand_index = 0
                        player_money -= current_bet
                        last_bet = current_bet
                        per_hand_bets = [current_bet, current_bet]
                        doubledown_flags = [False, False]
                        state = 'player'
                        for i, h in enumerate(jugador_hands):
                            base_x = 120 + i * HAND_SEP
                            dest_y = 200 + i * 70
                            for idx, card_tuple in enumerate(h):
                                c_obj = card_tuple[4]
                                c_obj.dest_x = base_x + idx * CARD_SPACING
                                c_obj.dest_y = dest_y
                                c_obj.target_scale = 1.06 if i == current_hand_index else 1.0
                                c_obj.oculta = False
                                c_obj.start_flip(now, to_back=False)

                if evento.key == pygame.K_i and insurance_offered and not insurance_taken:
                    insurance_bet = min(current_bet // 2, player_money)
                    if insurance_bet > 0:
                        player_money -= insurance_bet
                        insurance_taken = True

                if evento.key == pygame.K_SPACE:
                    if (now >= last_pedir_time + PEDIR_DELAY) and (not clearing):
                        if split_active and jugador_hands:
                            dest_y = 200 + current_hand_index * 70
                        else:
                            dest_y = 200
                        repartir(get_current_hand(), dest_y)
                        last_pedir_time = now

                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if split_active:
                        if current_hand_index < len(jugador_hands) - 1:
                            current_hand_index += 1
                        else:
                            state = 'dealer'
                            revelar_banca(now)
                            dealer_thinking = False
                            dealer_target = schedule_dealer_target()
                            next_action = now + 600
                    else:
                        state = 'dealer'
                        revelar_banca(now)
                        dealer_thinking = False
                        dealer_target = schedule_dealer_target()
                        next_action = now + 600

            elif state == 'round_end':
                if evento.key == pygame.K_s:
                    if not clearing:
                        player_cards = sum(jugador_hands, []) if jugador_hands else jugador
                        all_cards = banca + player_cards
                        if not all_cards:
                            nueva_ronda()
                        else:
                            clearing_cards = list(all_cards)
                            for card_tuple in clearing_cards:
                                c = card_tuple[4]
                                c.oculta = False
                                c.start_flip(now, to_back=True)
                            clearing = True
                            clear_phase = 'flipping'

    if player_money <= 0 and state == 'betting' and state != 'game_over':
        state = 'game_over'

    if state == 'game_over':
        VENTANA.fill((0,0,0))
        txt1 = FUENTE_GRANDE.render("Te has quedado sin fichas", True, BLANCO)
        txt2 = FUENTE.render("ENTER o R: volver a empezar (1000 fichas)", True, BLANCO)
        VENTANA.blit(txt1, ((ANCHO - txt1.get_width())//2, ALTO//2 - 60))
        VENTANA.blit(txt2, ((ANCHO - txt2.get_width())//2, ALTO//2 + 20))
        pygame.display.update()
        continue

    style = TABLE_STYLES[TABLE_STYLE_IDX]
    VENTANA.fill(style['color'])

    if DEALER_AVATAR:
        VENTANA.blit(DEALER_AVATAR, (ANCHO//2 - DEALER_AVATAR.get_width()//2, 0))
    else:
        pass

    if state == 'dealing' and (not clearing) and now >= next_deal:
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
                    insurance_offered = True
                    insurance_taken = False
                    insurance_bet = 0
                banca[0][4].start_flip(now)
            state = 'player'
            if split_active:
                pass
            else:
                if len(jugador) == 2 and calcular(jugador) == 21:
                    revelar_banca(now)
                    mensaje = "BLACKJACK!"
                    state = 'dealer'
                    dealer_thinking = False
                    dealer_target = schedule_dealer_target()
                    next_action = now + 600
        dealing_step += 1
        next_deal = now + 400

    if state == 'dealer' and (not clearing):
        cards_settled = len(banca) > 0 and all((not c[4].flipping) and (abs(c[4].x - c[4].dest_x) < 1) for c in banca)
        if cards_settled:
            if not dealer_thinking:
                dealer_thinking = True
                think_delay = DEALER_SETTLE_DELAY + random_module.randint(-200, 800)
                next_action = now + max(400, think_delay)
            else:
                if now >= next_action:
                    pb = calcular(banca)
                    if 'dealer_target' not in globals():
                        dealer_target = schedule_dealer_target()
                    hands = list(iter_player_hands())
                    any_player_blackjack = any(len(h) == 2 and calcular(h) == 21 for h in hands)
                    dealer_blackjack = (len(banca) == 2 and calcular(banca) == 21)
                    if any_player_blackjack and not dealer_blackjack:
                        dealer_thinking = False
                        revelar_banca(now)
                        if insurance_taken:
                            if dealer_blackjack:
                                player_money += insurance_bet * 2
                            insurance_taken = False
                            insurance_offered = False
                        results = []
                        for idx, hand in enumerate(hands):
                            bet_amt = per_hand_bets[idx] if (per_hand_bets and idx < len(per_hand_bets)) else current_bet
                            pj = calcular(hand)
                            round_result_type = None
                            if len(hand) == 2 and calcular(hand) == 21 and not dealer_blackjack:
                                payout = int(bet_amt * 2.5)
                                player_money += payout
                                player_money += 25
                                stats['blackjacks'] += 1
                                stats['won'] += 1
                                round_result_type = 'blackjack'
                            else:
                                if pj > 21:
                                    round_result_type = 'lose'
                                elif pb > 21 or pj > pb:
                                    round_result_type = 'win'
                                elif pj < pb:
                                    round_result_type = 'lose'
                                else:
                                    round_result_type = 'tie'
                                if round_result_type == 'win':
                                    player_money += bet_amt * 2
                                    stats['won'] += 1
                                elif round_result_type == 'tie':
                                    player_money += bet_amt
                                else:
                                    stats['lost'] += 1
                            results.append(round_result_type)
                        stats['played'] += 1
                        if any(r == 'blackjack' for r in results):
                            mensaje = "BLACKJACK!"
                        elif any(r == 'win' for r in results):
                            mensaje = "HAS GANADO"
                        elif all(r == 'tie' for r in results):
                            mensaje = "EMPATE"
                        else:
                            mensaje = "HAS PERDIDO"
                        if placed_chip:
                            if any(r in ('win', 'blackjack') for r in results):
                                sx, sy = placed_chip['x'], placed_chip['y']
                                tx, ty = ANCHO + 120, -120
                                speed = 10.0
                                dx = tx - sx; dy = ty - sy
                                dist = math.hypot(dx, dy) or 1.0
                                placed_chip.update({'moving': True, 'vx': dx/dist*speed, 'vy': dy/dist*speed, 'target_x': tx, 'target_y': ty, 'expire_on_arrival': True})
                            elif all(r == 'tie' for r in results):
                                sx, sy = placed_chip['x'], placed_chip['y']
                                tx, ty = ANCHO//2, ALTO - 120
                                speed = 10.0
                                dx = tx - sx; dy = ty - sy
                                dist = math.hypot(dx, dy) or 1.0
                                placed_chip.update({'moving': True, 'vx': dx/dist*speed, 'vy': dy/dist*speed, 'target_x': tx, 'target_y': ty, 'expire_on_arrival': True})
                            else:
                                sx, sy = placed_chip['x'], placed_chip['y']
                                tx, ty = BANK_POS
                                speed = 10.0
                                dx = tx - sx; dy = ty - sy
                                dist = math.hypot(dx, dy) or 1.0
                                placed_chip.update({'moving': True, 'vx': dx/dist*speed, 'vy': dy/dist*speed, 'target_x': tx, 'target_y': ty, 'expire_on_arrival': True})
                        player_chip_stack = []
                        if any(r in ('win','blackjack') for r in results):
                            spawn_particles(ANCHO//2, ALTO//2 + 40, DORADO, count=20)
                            overlay_flash.update({'active':True,'color':(255,255,255),'alpha':180,'start':now,'duration':300})
                        elif all(r=='tie' for r in results):
                            overlay_flash.update({'active':True,'color':(200,200,200),'alpha':120,'start':now,'duration':220})
                        else:
                            spawn_particles(ANCHO//2, ANCHO//2, ROJO, count=25)
                            overlay_flash.update({'active':True,'color':(150,0,0),'alpha':180,'start':now,'duration':350})
                        per_hand_bets = None
                        state = 'round_end'
                        round_end_time = now
                        continue
                    if pb < 17 and pb < dealer_target:
                        repartir(banca, 50)
                        dealer_thinking = True
                        next_action = now + DEALER_SETTLE_DELAY + random_module.randint(0, 600)
                    else:
                        dealer_thinking = False
                        dealer_blackjack = (len(banca) == 2 and calcular(banca) == 21)
                        if insurance_taken:
                            if dealer_blackjack:
                                player_money += insurance_bet * 2
                            insurance_taken = False
                            insurance_offered = False
                        hands = list(iter_player_hands())
                        results = []
                        for idx, hand in enumerate(hands):
                            bet_amt = per_hand_bets[idx] if (per_hand_bets and idx < len(per_hand_bets)) else current_bet
                            pj = calcular(hand)
                            round_result_type = None
                            if len(hand) == 2 and calcular(hand) == 21 and not dealer_blackjack:
                                payout = int(bet_amt * 2.5)
                                player_money += payout
                                player_money += 25
                                stats['blackjacks'] += 1
                                stats['won'] += 1
                                round_result_type = 'blackjack'
                            else:
                                if pj > 21:
                                    round_result_type = 'lose'
                                elif pb > 21 or pj > pb:
                                    round_result_type = 'win'
                                elif pj < pb:
                                    round_result_type = 'lose'
                                else:
                                    round_result_type = 'tie'
                                if round_result_type == 'win':
                                    player_money += bet_amt * 2
                                    stats['won'] += 1
                                elif round_result_type == 'tie':
                                    player_money += bet_amt
                                else:
                                    stats['lost'] += 1
                            results.append(round_result_type)
                        stats['played'] += 1
                        if any(r == 'blackjack' for r in results):
                            mensaje = "BLACKJACK!"
                        elif any(r == 'win' for r in results):
                            mensaje = "HAS GANADO"
                        elif all(r == 'tie' for r in results):
                            mensaje = "EMPATE"
                        else:
                            mensaje = "HAS PERDIDO"
                        if placed_chip:
                            if any(r in ('win', 'blackjack') for r in results):
                                sx, sy = placed_chip['x'], placed_chip['y']
                                tx, ty = ANCHO + 120, -120
                                speed = 10.0
                                dx = tx - sx; dy = ty - sy
                                dist = math.hypot(dx, dy) or 1.0
                                placed_chip.update({'moving': True, 'vx': dx/dist*speed, 'vy': dy/dist*speed, 'target_x': tx, 'target_y': ty, 'expire_on_arrival': True})
                            elif all(r == 'tie' for r in results):
                                sx, sy = placed_chip['x'], placed_chip['y']
                                tx, ty = ANCHO//2, ALTO - 120
                                speed = 10.0
                                dx = tx - sx; dy = ty - sy
                                dist = math.hypot(dx, dy) or 1.0
                                placed_chip.update({'moving': True, 'vx': dx/dist*speed, 'vy': dy/dist*speed, 'target_x': tx, 'target_y': ty, 'expire_on_arrival': True})
                            else:
                                sx, sy = placed_chip['x'], placed_chip['y']
                                tx, ty = BANK_POS
                                speed = 10.0
                                dx = tx - sx; dy = ty - sy
                                dist = math.hypot(dx, dy) or 1.0
                                placed_chip.update({'moving': True, 'vx': dx/dist*speed, 'vy': dy/dist*speed, 'target_x': tx, 'target_y': ty, 'expire_on_arrival': True})
                        player_chip_stack = []
                        if any(r in ('win','blackjack') for r in results):
                            spawn_particles(ANCHO//2, ALTO//2 + 40, DORADO, count=20)
                            overlay_flash.update({'active':True,'color':(255,255,255),'alpha':180,'start':now,'duration':300})
                        elif all(r=='tie' for r in results):
                            overlay_flash.update({'active':True,'color':(200,200,200),'alpha':120,'start':now,'duration':220})
                        else:
                            spawn_particles(ANCHO//2, ANCHO//2, ROJO, count=25)
                            overlay_flash.update({'active':True,'color':(150,0,0),'alpha':180,'start':now,'duration':350})
                        per_hand_bets = None
                        state = 'round_end'
                        round_end_time = now

    for mano in [banca]:
        for c in mano:
            c[4].target_scale = 1.0
            c[4].actualizar(now)
            c[4].dibujar(now)

    if split_active and jugador_hands:
        for i, hand in enumerate(jugador_hands):
            hand_offset_x = 120 + i * HAND_SEP
            offset_y = 200 + i*70
            is_active = (i == current_hand_index and state == 'player')
            target_for_hand = 1.06 if is_active else 1.0
            for idx, c in enumerate(hand):
                c[4].dest_x = hand_offset_x + idx * CARD_SPACING
                c[4].dest_y = offset_y
                c[4].target_scale = target_for_hand
                c[4].actualizar(now)
                c[4].dibujar(now)
    else:
        for c in jugador:
            c[4].target_scale = 1.0
            c[4].actualizar(now)
            c[4].dibujar(now)

    hand = get_current_hand()
    player_visible = calcular_visible(hand)
    if state == 'player' and player_visible != 0:
        if player_visible == 21:
            if split_active and current_hand_index < len(jugador_hands)-1:
                current_hand_index += 1
            else:
                state = 'dealer'
                revelar_banca(now)
                dealer_thinking = False
                dealer_target = schedule_dealer_target()
                next_action = now + 600
        elif player_visible > 21:
            if split_active and current_hand_index < len(jugador_hands) - 1:
                overlay_flash.update({'active':True,'color':(150,0,0),'alpha':200,'start':now,'duration':300})
                mensaje = f"MANO {current_hand_index+1} BUST"
                current_hand_index += 1
                last_pedir_time = now
            elif split_active and current_hand_index == len(jugador_hands) - 1:
                overlay_flash.update({'active':True,'color':(150,0,0),'alpha':200,'start':now,'duration':300})
                mensaje = f"MANO {current_hand_index+1} BUST"
                revelar_banca(now)
                state = 'dealer'
                dealer_thinking = False
                dealer_target = schedule_dealer_target()
                next_action = now + 600
            else:
                mensaje = "HAS PERDIDO"
                stats['lost'] += 1
                stats['played'] += 1
                overlay_flash.update({'active':True,'color':(150,0,0),'alpha':200,'start':now,'duration':350})
                revelar_banca(now)
                state = 'round_end'
                round_end_time = now
                if placed_chip:
                    sx, sy = placed_chip['x'], placed_chip['y']
                    tx, ty = BANK_POS
                    speed = 10.0
                    dx = tx - sx; dy = ty - sy
                    dist = math.hypot(dx, dy) or 1.0
                    placed_chip.update({'moving': True, 'vx': dx/dist*speed, 'vy': dy/dist*speed, 'target_x': tx, 'target_y': ty, 'expire_on_arrival': True})

    if state == 'round_end' and (not clearing) and round_end_time != 0 and now >= round_end_time + ROUND_DELAY:
        player_cards = sum(jugador_hands, []) if jugador_hands else jugador
        all_cards = banca + player_cards
        if not all_cards:
            nueva_ronda()
        else:
            clearing_cards = list(all_cards)
            for mano in clearing_cards:
                mano[4].oculta = False
                mano[4].start_flip(now, to_back=True)
            clearing = True
            clear_phase = 'flipping'
        round_end_time = 0

    if clearing:
        if clear_phase == 'flipping':
            flips_done = all((not c[4].flipping) for c in clearing_cards)
            if flips_done:
                for idx, c in enumerate(clearing_cards):
                    c[4].dest_x = ANCHO + 80 + idx * 30
                    c[4].target_scale = 0.9
                clear_phase = 'moving'
        elif clear_phase == 'moving':
            if not clearing_cards:
                clearing = False
                clear_phase = None
                nueva_ronda()
            else:
                done = all(c[4].x >= c[4].dest_x - 1 for c in clearing_cards)
                if done:
                    clearing = False
                    clear_phase = None
                    clearing_cards = []
                    nueva_ronda()

    if any(c[4].oculta for c in banca):
        texto = " + ".join("?" if c[4].oculta else str(c[2]) for c in banca)
        VENTANA.blit(FUENTE.render(f"Banca: {texto}", True, BLANCO), (50, 20))
    else:
        banca_visible = calcular_visible(banca)
        VENTANA.blit(FUENTE.render(f"Banca: {banca_visible}", True, BLANCO), (50, 20))

    if split_active and jugador_hands:
        left = f"Mano 1: {calcular(jugador_hands[0])}"
        right = f"Mano 2: {calcular(jugador_hands[1])}"
        hud_y = ALTO - 220
        surf = FUENTE.render(f"{left}    {right}", True, BLANCO)
        VENTANA.blit(surf, (50, hud_y))
    else:
        VENTANA.blit(FUENTE.render(f"Jugador: {calcular(jugador)}", True, BLANCO), (50, 380))

    if state == 'betting':
        instrucciones = ["Escribe tu apuesta"]
    elif state == 'player':
        instrucciones = ["ESPACIO: Pedir  ENTER: Plantarse  D: Doblar  P: Dividir"]
    elif state in ('dealing', 'dealer'):
        instrucciones = ["Esperando..."]
    else:
        instrucciones = ["S = Siguiente ronda"]

    box_w = 760
    padding = 12
    line_h = 28
    box_h = line_h * (len(instrucciones) + 4) + padding
    reglas_x = (ANCHO - box_w) // 2
    reglas_y = ALTO - box_h - 20

    s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    VENTANA.blit(s, (reglas_x, reglas_y))
    pygame.draw.rect(VENTANA, NEGRO, (reglas_x, reglas_y, box_w, box_h), 2, border_radius=8)
    y_off = reglas_y + padding

    label_money = FUENTE_PEQUENA.render(f"Dinero: {player_money}", True, BLANCO)
    VENTANA.blit(label_money, (reglas_x + padding, y_off))

    input_box_w = 220
    input_box_h = 36
    input_box_x = reglas_x + box_w - input_box_w - padding
    input_box_y = y_off - 6
    input_bg = pygame.Surface((input_box_w, input_box_h), pygame.SRCALPHA)
    input_bg.fill((20, 20, 20, 230))
    VENTANA.blit(input_bg, (input_box_x, input_box_y))
    pygame.draw.rect(VENTANA, NEGRO, (input_box_x, input_box_y, input_box_w, input_box_h), 2, border_radius=6)

    if state == 'betting':
        display_text = current_bet_input if current_bet_input else ""
    else:
        display_text = str(current_bet)

    def clip_text_right(text, font, max_w):
        txt = text
        if font.size(txt)[0] <= max_w:
            return txt
        while font.size(txt)[0] > max_w and len(txt) > 0:
            txt = txt[1:]
        return txt

    txt_to_show = clip_text_right(display_text, FUENTE_PEQUENA, input_box_w - 16)
    txt_surf = FUENTE_PEQUENA.render(txt_to_show, True, BLANCO)
    VENTANA.blit(txt_surf, (input_box_x + 8, input_box_y + (input_box_h - txt_surf.get_height()) // 2))

    lbl_ap = FUENTE_PEQUENA.render("Apuesta:", True, BLANCO)
    VENTANA.blit(lbl_ap, (input_box_x - lbl_ap.get_width() - 12, input_box_y + (input_box_h - lbl_ap.get_height()) // 2))

    y_off += line_h

    chips_text = f"Máx apuesta: {BET_MAX}"
    surf_chips = FUENTE_PEQUENA.render(chips_text, True, BLANCO)
    VENTANA.blit(surf_chips, (reglas_x + padding, y_off))
    y_off += line_h

    for linea in instrucciones:
        surf = FUENTE_INSTR.render(linea, True, BLANCO)
        text_x = reglas_x + (box_w - surf.get_width()) // 2
        VENTANA.blit(surf, (text_x, y_off))
        y_off += 24

    if mensaje:
        if "BLACKJACK" in mensaje.upper():
            surf = FUENTE_GRANDE.render(mensaje, True, DORADO)
        elif "GAN" in mensaje.upper():
            surf = FUENTE_MSG.render(mensaje, True, DORADO)
        elif "EMPATE" in mensaje.upper():
            surf = FUENTE_MSG.render(mensaje, True, (200, 200, 200))
        else:
            surf = FUENTE_MSG.render(mensaje, True, ROJO)
        msg_x = (ANCHO - surf.get_width()) // 2
        msg_y = ALTO // 2 + 20
        VENTANA.blit(surf, (msg_x, msg_y))

    if placed_chip:
        if placed_chip.get('moving'):
            placed_chip['x'] += placed_chip['vx']
            placed_chip['y'] += placed_chip['vy']
            if math.hypot(placed_chip['x'] - placed_chip['target_x'], placed_chip['y'] - placed_chip['target_y']) < 8:
                placed_chip['x'] = placed_chip['target_x']
                placed_chip['y'] = placed_chip['target_y']
                placed_chip['moving'] = False
                if placed_chip.get('expire_on_arrival'):
                    placed_chip = None
        if placed_chip:
            if placed_chip.get('shape') == 'rect':
                w = placed_chip.get('w', 44); h = placed_chip.get('h', 28)
                rect = pygame.Rect(int(placed_chip['x'] - w//2), int(placed_chip['y'] - h//2), w, h)
                pygame.draw.rect(VENTANA, placed_chip['color'], rect, border_radius=8)
                pygame.draw.rect(VENTANA, NEGRO, rect, 2, border_radius=8)
                font = _chip_font_for_rect(h)
                txt = font.render(str(placed_chip['value']), True, BLANCO)
                VENTANA.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
            else:
                r = placed_chip.get('r', 20)
                cx = int(placed_chip['x'])
                cy = int(placed_chip['y'])
                pygame.draw.circle(VENTANA, placed_chip['color'], (cx, cy), r)
                pygame.draw.circle(VENTANA, NEGRO, (cx, cy), r, 2)
                font = _chip_font_for_circle(r)
                txt = font.render(str(placed_chip['value']), True, BLANCO)
                VENTANA.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))

    for i, c in enumerate(player_chip_stack[-12:]):
        x = PLAYER_STACK_POS[0] + (i % 6) * 10
        y = PLAYER_STACK_POS[1] - (i // 6) * 6
        pygame.draw.circle(VENTANA, (220,170,60), (int(x), int(y)), 18)
        pygame.draw.circle(VENTANA, NEGRO, (int(x), int(y)), 18, 2)
        txt = FUENTE_PEQUENA.render(str(c['value']), True, BLANCO)
        VENTANA.blit(txt, (int(x - txt.get_width()//2), int(y - txt.get_height()//2)))

    for c in chips_anim[:]:
        c['x'] += c['vx']; c['y'] += c['vy']
        if math.hypot(c['x'] - c['target_x'], c['y'] - c['target_y']) < 8:
            try:
                chips_anim.remove(c)
            except ValueError:
                pass
            continue
        if c.get('shape') == 'rect':
            w = c.get('w', 44); h = c.get('h', 28)
            rect = pygame.Rect(int(c['x'] - w//2), int(c['y'] - h//2), w, h)
            pygame.draw.rect(VENTANA, c['color'], rect, border_radius=8)
            pygame.draw.rect(VENTANA, NEGRO, rect, 2, border_radius=8)
            font = _chip_font_for_rect(h)
            txt = font.render(str(c['value']), True, BLANCO)
            VENTANA.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
        else:
            r = c.get('r', 20)
            pygame.draw.circle(VENTANA, c['color'], (int(c['x']), int(c['y'])), r)
            pygame.draw.circle(VENTANA, NEGRO, (int(c['x']), int(c['y'])), r, 2)
            font = _chip_font_for_circle(r)
            txt = font.render(str(c['value']), True, BLANCO)
            VENTANA.blit(txt, (int(c['x'] - txt.get_width()//2), int(c['y'] - txt.get_height()//2)))

    dt = RELOJ.get_time()
    for p in particles[:]:
        p[0] += p[2]; p[1] += p[3]; p[4] -= dt; p[3] += 0.12
        if p[4] <= 0:
            particles.remove(p); continue
        alpha = max(0, min(255, int(255 * (p[4] / 1200.0))))
        surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        surf.fill((*p[5], alpha))
        VENTANA.blit(surf, (p[0], p[1]))

    if overlay_flash['active']:
        elapsed = now - overlay_flash['start']
        if elapsed > overlay_flash['duration']:
            overlay_flash['active'] = False
        else:
            a = int(overlay_flash['alpha'] * (1 - (elapsed / overlay_flash['duration'])))
            ov = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            ov.fill((*overlay_flash['color'], a))
            VENTANA.blit(ov, (0, 0))

    mouse_pos = pygame.mouse.get_pos()
    btn_hovered = DOTS_BTN.collidepoint(mouse_pos)
    btn_color = (80, 80, 80) if not btn_hovered else (120, 120, 120)
    pygame.draw.rect(VENTANA, btn_color, DOTS_BTN, border_radius=6)
    pygame.draw.rect(VENTANA, NEGRO, DOTS_BTN, 1, border_radius=6)
    dots_surf = FUENTE_PEQUENA.render("...", True, BLANCO)
    VENTANA.blit(dots_surf, (DOTS_BTN.centerx - dots_surf.get_width()//2,
                              DOTS_BTN.centery - dots_surf.get_height()//2))

    if update_status is not None:
        elapsed_notif = now - update_notif_time
        show_notif = (update_status == 'checking') or (elapsed_notif < 5000)
        if show_notif:
            alpha_notif = 230
            if update_status != 'checking' and elapsed_notif > 3500:
                alpha_notif = max(0, int(230 * (1 - (elapsed_notif - 3500) / 1500)))
            notif_color = (30, 120, 50) if update_status == 'up_to_date' else \
                          (180, 120, 0) if update_status == 'available' else \
                          (40, 40, 40) if update_status == 'checking' else (150, 30, 30)
            notif_surf = FUENTE_PEQUENA.render(update_msg, True, BLANCO)
            nw = notif_surf.get_width() + 24
            nh = notif_surf.get_height() + 14
            nx = ANCHO - nw - 10
            ny = DOTS_BTN.bottom + 6
            bg = pygame.Surface((nw, nh), pygame.SRCALPHA)
            bg.fill((*notif_color, alpha_notif))
            VENTANA.blit(bg, (nx, ny))
            pygame.draw.rect(VENTANA, NEGRO, (nx, ny, nw, nh), 1, border_radius=6)
            VENTANA.blit(notif_surf, (nx + 12, ny + 7))

    reiniciar_rect = pygame.Rect(ANCHO - 140, ALTO - 44, 130, 34)
    r_hovered = reiniciar_rect.collidepoint(mouse_pos)
    r_color = (140, 30, 30) if not r_hovered else (180, 50, 50)
    pygame.draw.rect(VENTANA, r_color, reiniciar_rect, border_radius=7)
    pygame.draw.rect(VENTANA, NEGRO, reiniciar_rect, 1, border_radius=7)
    r_txt = FUENTE_PEQUENA.render("R: Reiniciar", True, BLANCO)
    VENTANA.blit(r_txt, (reiniciar_rect.centerx - r_txt.get_width()//2,
                          reiniciar_rect.centery - r_txt.get_height()//2))

    if pygame.mouse.get_pressed()[0] and reiniciar_rect.collidepoint(mouse_pos):
        reiniciar_partida()

    pygame.display.update()
