import pygame
import random as random_module
import sys
import os
import math
import threading
import urllib.request
import shutil
import subprocess
import platform as _platform_mod
import socket as _socket_mod
import json as _json_mod
import collections as _collections_mod

_IS_FROZEN = bool(getattr(sys, 'frozen', False))
if _IS_FROZEN:
    _SCRIPT_PATH = os.path.abspath(sys.executable)
else:
    _SCRIPT_PATH = os.path.abspath(__file__)

def _get_data_dir():
    _sys = sys.platform
    if _sys == 'darwin':
        base = os.path.expanduser('~/Library/Application Support')
    elif _sys == 'win32':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:
        base = os.path.expanduser('~/.local/share')
    d = os.path.join(base, 'ElFarolRojo')
    os.makedirs(d, exist_ok=True)
    return d

DATA_DIR = _get_data_dir()
os.chdir(DATA_DIR)  


_CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')

_DEFAULT_CONFIG = {
    'first_run':  True,
    'volume':     0.75,
    'resolution': '1920x1080',
    'language':   'es',
    'autoupdate': True,
}

_RESOLUTIONS = {
    '1920x1080': (1920, 1080),
    '1600x900':  (1600, 900),
    '1280x720':  (1280, 720),
    'windowed':  (1280, 720),
}
_RESOLUTION_ORDER = ['1920x1080', '1600x900', '1280x720', 'windowed']

def _load_config():
    cfg = dict(_DEFAULT_CONFIG)
    try:
        if os.path.exists(_CONFIG_FILE):
            with open(_CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded = _json_mod.load(f)
            if isinstance(loaded, dict):
                cfg.update({k: v for k, v in loaded.items() if k in _DEFAULT_CONFIG})
    except Exception as e:
        print(f"[CONFIG] No se pudo leer config.json: {e}")
    if cfg.get('resolution') not in _RESOLUTIONS:
        cfg['resolution'] = _DEFAULT_CONFIG['resolution']
    try:
        cfg['volume'] = max(0.0, min(1.0, float(cfg.get('volume', 0.75))))
    except Exception:
        cfg['volume'] = 0.75
    if cfg.get('language') not in ('es', 'en'):
        cfg['language'] = 'es'
    return cfg

def save_config():
    try:
        with open(_CONFIG_FILE, 'w', encoding='utf-8') as f:
            _json_mod.dump(CONFIG, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[CONFIG] No se pudo guardar config.json: {e}")

CONFIG = _load_config()
IS_FIRST_RUN = bool(CONFIG.get('first_run', True))

_TRANSLATIONS = {
    'settings_title':      {'es': 'Ajustes',                              'en': 'Settings'},
    'settings_volume':     {'es': 'Volumen',                              'en': 'Volume'},
    'settings_resolution': {'es': 'Resolucion',                          'en': 'Resolution'},
    'settings_language':   {'es': 'Idioma',                              'en': 'Language'},
    'settings_autoupdate': {'es': 'Buscar actualizaciones al iniciar',   'en': 'Check for updates on startup'},
    'settings_close':      {'es': 'Cerrar',                              'en': 'Close'},
    'settings_on':         {'es': 'Activado',                            'en': 'On'},
    'settings_off':        {'es': 'Desactivado',                         'en': 'Off'},
    'settings_windowed':   {'es': 'Ventana',                             'en': 'Windowed'},
    'settings_hint':       {'es': 'Los cambios de resolucion se aplican al instante.',
                             'en': 'Resolution changes apply instantly.'},
    'settings_applied':    {'es': 'Resolucion aplicada',                  'en': 'Resolution applied'},
    'settings_button':     {'es': 'Ajustes',                             'en': 'Settings'},
    'menu_story_label':    {'es': 'Modo Historia',                       'en': 'Story Mode'},
    'menu_story_sub':      {'es': 'Blackjack narrativo · Barcelona 1987 · Empieza con 1.000 fichas',
                             'en': 'Narrative blackjack · Barcelona 1987 · Start with 1,000 chips'},
    'menu_bj_label':       {'es': 'BlackJack',                           'en': 'Blackjack'},
    'menu_bj_sub':         {'es': 'Blackjack infinito · Sin historia · Empieza con 5.000 fichas',
                             'en': 'Endless blackjack · No story · Start with 5,000 chips'},
    'menu_poker_label':    {'es': "Texas Hold'em",                       'en': "Texas Hold'em"},
    'menu_poker_sub':      {'es': "Poker Texas Hold'em · Ciegas, flop, turn y river · Empieza con 3.000 fichas",
                             'en': "Texas Hold'em poker · Blinds, flop, turn & river · Start with 3,000 chips"},
    'menu_update_label':   {'es': 'Buscar actualizaciones',              'en': 'Check for updates'},
    'menu_update_sub':     {'es': 'Comprueba si hay una nueva version disponible en GitHub',
                             'en': 'Check if a new version is available on GitHub'},
    'menu_subtitle':       {'es': 'Blackjack · Barcelona · 1987',        'en': 'Blackjack · Barcelona · 1987'},
    'menu_hint':           {'es': 'Haz clic para seleccionar',           'en': 'Click to select'},
    'menu_open_folder':    {'es': 'Abrir carpeta de datos del juego',    'en': 'Open game data folder'},
    'menu_hard_reset':     {'es': 'Hard Reset · Borrar datos y reiniciar','en': 'Hard Reset · Erase data and restart'},
    'pause_resume':        {'es': 'Continuar',                           'en': 'Resume'},
    'pause_menu':          {'es': 'Menu principal',                      'en': 'Main menu'},
    'update_checking':     {'es': 'Comprobando...',                      'en': 'Checking...'},
    'update_uptodate':     {'es': 'Ya tienes la ultima version',         'en': "You're already on the latest version"},
    'update_no_github':     {'es': 'Sin respuesta de GitHub API',        'en': 'No response from GitHub API'},
    'update_no_hash':       {'es': 'No se pudo calcular hash remoto',    'en': "Couldn't calculate remote hash"},
    'update_syntax_err':    {'es': 'Actualiz. con error sintaxis: línea {line}', 'en': 'Update has a syntax error: line {line}'},
    'update_verify_fail':   {'es': 'No se pudo verificar actualiz.: {err}', 'en': "Couldn't verify update: {err}"},
    'update_restarting':    {'es': '¡Actualizado! Reiniciando...',       'en': 'Updated! Restarting...'},
    'update_write_fail':    {'es': 'No se pudo escribir: {err}',         'en': "Couldn't write file: {err}"},
    'update_error':         {'es': 'Error: {err}',                      'en': 'Error: {err}'},
    'update_no_release':    {'es': 'Sin datos de release en GitHub',     'en': 'No release data on GitHub'},
    'update_no_binary':     {'es': 'Release {tag} sin binario para esta plataforma', 'en': 'Release {tag} has no binary for this platform'},
    'update_invalid_bin':   {'es': 'Binario descargado inválido',        'en': 'Downloaded binary is invalid'},
    'update_replace_fail':  {'es': 'No se pudo reemplazar binario: {err}', 'en': "Couldn't replace binary: {err}"},

    'game_title':          {'es': 'El Farol Rojo',                       'en': 'El Farol Rojo'},
    'barcelona_1987':       {'es': 'Barcelona  ·  1987',                 'en': 'Barcelona  ·  1987'},
    'made_by':              {'es': 'hecho por Humrandbm y Dreame282',    'en': 'made by Humrandbm and Dreame282'},
    'reiniciar_btn':         {'es': 'R: Reiniciar',                      'en': 'R: Restart'},
    'esc_menu_principal':    {'es': 'ESC: Menú principal',               'en': 'ESC: Main menu'},
    'esc_menu':              {'es': 'ESC: Menú',                         'en': 'ESC: Menu'},
    'bj_infinito_stats':     {'es': "♠ BlackJack Infinito  |  Ganadas: {won}  Perdidas: {lost}",
                               'en': "♠ Endless BlackJack  |  Won: {won}  Lost: {lost}"},
    'updated_restarting':    {'es': '¡Actualizado! Reiniciando en {secs}s...', 'en': 'Updated! Restarting in {secs}s...'},

    'pause_title':           {'es': 'PAUSA',                             'en': 'PAUSED'},
    'pause_hint':             {'es': 'ESC para reanudar  ·  haz clic para elegir', 'en': 'ESC to resume  ·  click to choose'},

    'story_continue':         {'es': '[ ESPACIO  o  clic  para continuar ]', 'en': '[ SPACE  or  click  to continue ]'},
    'story_choice_header':    {'es': '¿Qué dices?',                       'en': 'What do you say?'},
    'story_choice_hint':      {'es': '[ haz clic para elegir ]',          'en': '[ click to choose ]'},

    'erase_title':            {'es': '⚠  ¿Borrar todos los datos?',       'en': '⚠  Erase all data?'},
    'erase_line1':             {'es': 'Se borrarán guardados, imágenes y música descargada.', 'en': 'Saved data, images and downloaded music will be deleted.'},
    'erase_line2':             {'es': 'El juego se reiniciará automáticamente.', 'en': 'The game will restart automatically.'},
    'erase_confirm':           {'es': 'Borrar y reiniciar',               'en': 'Erase and restart'},
    'erase_cancel':            {'es': 'Cancelar',                         'en': 'Cancel'},

    'dl_error_title':          {'es': 'Error de descarga',                'en': 'Download error'},
    'dl_error_line':           {'es': 'No se pudo descargar: {name}',     'en': "Couldn't download: {name}"},
    'dl_error_hint':           {'es': 'Comprueba tu conexión a internet e inténtalo de nuevo.', 'en': 'Check your internet connection and try again.'},
    'dl_retry':                {'es': 'Reintentar',                       'en': 'Retry'},
    'dl_continue_risky':       {'es': 'Continuar  (puede arruinar la experiencia)', 'en': 'Continue  (may ruin the experience)'},
    'dl_close_game':           {'es': 'Cerrar juego',                     'en': 'Close game'},
    'dl_downloading':          {'es': 'Descargando paquetes necesarios de internet...', 'en': 'Downloading required packages from the internet...'},
    'dl_progress':             {'es': '[{i}/{total}]  {name}',            'en': '[{i}/{total}]  {name}'},
    'dl_ready':                {'es': '¡Listo!',                          'en': 'Ready!'},

    'bj_banca':                {'es': 'Banca: {texto}',                   'en': 'Dealer: {texto}'},
    'bj_mano1':                {'es': 'Mano 1: {v}',                      'en': 'Hand 1: {v}'},
    'bj_mano2':                {'es': 'Mano 2: {v}',                      'en': 'Hand 2: {v}'},
    'bj_jugador':              {'es': 'Jugador: {v}',                     'en': 'Player: {v}'},
    'bj_type_bet':             {'es': 'Escribe tu apuesta y pulsa ENTER', 'en': 'Type your bet and press ENTER'},
    'bj_controls':             {'es': 'ESPACIO: Pedir  ENTER: Plantarse  D: Doblar  P: Dividir  I: Seguro',
                                 'en': 'SPACE: Hit  ENTER: Stand  D: Double  P: Split  I: Insurance'},
    'bj_next_round':           {'es': 'S = Siguiente ronda',              'en': 'S = Next round'},
    'bj_insurance_take':       {'es': 'I: Tomar seguro  |  ',             'en': 'I: Take insurance  |  '},
    'bj_dificil':              {'es': 'Difícil',                          'en': 'Hard'},
    'bj_muy_dificil':          {'es': 'Muy Difícil',                      'en': 'Very Hard'},
    'bj_chips':                {'es': '💰 Fichas: {v}',                   'en': '💰 Chips: {v}'},
    'bj_bet':                  {'es': '🎰 Apuesta: {v}',                  'en': '🎰 Bet: {v}'},
    'bj_max_dif':              {'es': 'Máx: {max}  ·  Dificultad: {diff}', 'en': 'Max: {max}  ·  Difficulty: {diff}'},
    'bj_max_meta_dif':         {'es': 'Máx: {max}  ·  Meta: {meta}  ·  Dificultad: {diff}', 'en': 'Max: {max}  ·  Goal: {meta}  ·  Difficulty: {diff}'},
    'bj_no_chips_victor':      {'es': 'Sin fichas... Víctor sonríe.',      'en': 'Out of chips... Víctor smiles.'},
    'bj_enter_restart':        {'es': 'ENTER o R: volver a empezar con 1000 fichas', 'en': 'ENTER or R: start over with 1,000 chips'},
    'bj_blackjack':            {'es': 'BLACKJACK!',                       'en': 'BLACKJACK!'},
    'bj_has_ganado':           {'es': 'HAS GANADO',                       'en': 'YOU WIN'},
    'bj_empate':               {'es': 'EMPATE',                           'en': 'PUSH'},
    'bj_has_perdido':          {'es': 'HAS PERDIDO',                      'en': 'YOU LOSE'},
    'bj_hand_bust':            {'es': 'MANO {n} BUST',                    'en': 'HAND {n} BUST'},
    'bj_bet_empty':            {'es': 'Escribe una apuesta',              'en': 'Enter a bet'},
    'bj_bet_invalid':          {'es': 'Apuesta inválida',                 'en': 'Invalid bet'},
    'bj_bet_max':              {'es': 'Apuesta máx. {max}',               'en': 'Max bet {max}'},
    'bj_not_enough_money':     {'es': 'No tienes suficiente dinero',      'en': "You don't have enough money"},
    'bj_no_chips':             {'es': 'Sin fichas — pulsa R para reiniciar', 'en': 'Out of chips — press R to restart'},
    'bj_waiting':              {'es': 'Esperando...',                     'en': 'Waiting...'},

    'he_title':                {'es': "♠  TEXAS HOLD'EM  ♠",              'en': "♠  TEXAS HOLD'EM  ♠"},
    'he_community':            {'es': 'CARTAS COMUNITARIAS',              'en': 'COMMUNITY CARDS'},
    'he_your_hand':            {'es': 'Tu mano: {v}',                     'en': 'Your hand: {v}'},
    'he_pot':                  {'es': 'BOTE: {v} fichas',                 'en': 'POT: {v} chips'},
    'he_chips':                {'es': 'Fichas: {v}',                      'en': 'Chips: {v}'},
    'he_deal_hint':            {'es': 'ENTER para repartir · Todos postean la ciega · Máx {max}', 'en': 'ENTER to deal · Everyone posts the blind · Max {max}'},
    'he_turn_of':              {'es': '▶  Le toca a  {name}',             'en': "▶  It's  {name}'s  turn"},
    'he_last_action':          {'es': '✓  {action}',                      'en': '✓  {action}'},
    'he_raise_label':          {'es': 'Sube (+fichas):',                  'en': 'Raise (+chips):'},
    'he_raise_btn':            {'es': 'SUBIR',                            'en': 'RAISE'},
    'he_confirm_cancel':       {'es': 'ENTER para confirmar · ESC para cancelar', 'en': 'ENTER to confirm · ESC to cancel'},
    'he_fold':                 {'es': 'F: Retirarse',                     'en': 'F: Fold'},
    'he_check':                {'es': 'C: Check',                         'en': 'C: Check'},
    'he_call':                 {'es': 'C: Igualar ({amt}) — ¡alguien subió!', 'en': 'C: Call ({amt}) — someone raised!'},
    'he_controls':             {'es': 'F=Retirarse  C=Check/Igualar  Click SUBIR para apostar más', 'en': 'F=Fold  C=Check/Call  Click RAISE to bet more'},
    'he_next_hand':            {'es': 'ENTER / S para siguiente mano',    'en': 'ENTER / S for next hand'},
    'he_stats':                {'es': 'G:{won} P:{lost} E:{tied}',        'en': 'W:{won} L:{lost} T:{tied}'},
    'he_no_chips':             {'es': 'Sin fichas — pulsa R para reiniciar', 'en': 'Out of chips — press R to restart'},
    'he_blind_insufficient':   {'es': 'Fichas insuficientes para la ciega', 'en': 'Not enough chips for the blind'},
    'he_blind_invalid':        {'es': 'Ciega inválida',                   'en': 'Invalid blind'},
    'he_amount_invalid':       {'es': 'Cantidad inválida',                'en': 'Invalid amount'},
    'he_number_invalid':       {'es': 'Número inválido',                  'en': 'Invalid number'},
    'he_max_blind':            {'es': 'Máx. {max}',                       'en': 'Max. {max}'},
    'he_you_folded':           {'es': 'Te has retirado. Pierdes la ciega.', 'en': 'You folded. You lose the blind.'},
    'he_tie':                  {'es': 'Empate — {pn}',                    'en': 'Tie — {pn}'},
    'he_you_won':              {'es': '¡Ganaste! {pn}  (+{pot} fichas)',  'en': 'You won! {pn}  (+{pot} chips)'},
    'he_they_won':             {'es': '{winners} gana. Tu mano: {pn}',    'en': '{winners} wins. Your hand: {pn}'},
    'he_all_folded':           {'es': '¡Todos se retiraron! Ganas el bote (+{pot} fichas)', 'en': 'Everyone folded! You win the pot (+{pot} chips)'},

    'hand_high_card':          {'es': 'Carta Alta',                       'en': 'High Card'},
    'hand_pair':                {'es': 'Pareja',                          'en': 'Pair'},
    'hand_two_pair':            {'es': 'Doble Pareja',                    'en': 'Two Pair'},
    'hand_trips':               {'es': 'Trío',                            'en': 'Three of a Kind'},
    'hand_straight':            {'es': 'Escalera',                        'en': 'Straight'},
    'hand_flush':                {'es': 'Color',                          'en': 'Flush'},
    'hand_full_house':           {'es': 'Full House',                     'en': 'Full House'},
    'hand_quads':                {'es': 'Póker (4 iguales)',              'en': 'Four of a Kind'},
    'hand_straight_flush':       {'es': 'Escalera de Color',              'en': 'Straight Flush'},
    'hand_royal_flush':          {'es': 'Escalera Real',                  'en': 'Royal Flush'},

    'he_ai_call':                {'es': 'iguala',                          'en': 'calls'},
    'he_ai_folds':               {'es': 'se retira',                      'en': 'folds'},
    'he_ai_folds_broke':         {'es': 'se retira (sin fichas)',         'en': 'folds (out of chips)'},
    'he_ai_already_folded':      {'es': 'ya retirado',                    'en': 'already folded'},
    'he_ai_bluff_raise':         {'es': 'farolea y sube {amt}',           'en': 'bluffs and raises {amt}'},
    'he_ai_raise':                {'es': 'sube {amt}',                    'en': 'raises {amt}'},
    'he_ai_raise_amt':            {'es': 'SUBE {amt}',                    'en': 'RAISES {amt}'},

    'he_you_label':             {'es': 'TÚ',                               'en': 'YOU'},

    'poker_how':                  {'es': '¿Cómo quieres jugar?',           'en': 'How do you want to play?'},
    'poker_online_title':          {'es': "🌐  Jugar Online",              'en': '🌐  Play Online'},
    'poker_online_sub':            {'es': 'Conecta a una partida con jugadores reales vía red', 'en': 'Connect to a game with real players over the network'},
    'poker_offline_title':         {'es': '🤖  Jugar Offline',             'en': '🤖  Play Offline'},
    'poker_offline_sub':           {'es': 'Partida local contra bots · Sin conexión necesaria', 'en': 'Local game against bots · No connection needed'},
    'poker_connect_title':          {'es': 'Conectar al servidor',         'en': 'Connect to server'},
    'poker_server_ip':              {'es': 'IP del servidor',              'en': 'Server IP'},
    'poker_your_name':               {'es': 'Tu nombre',                   'en': 'Your name'},
    'poker_connect_fail_timeout':    {'es': 'No se pudo conectar: tiempo de espera agotado', 'en': "Couldn't connect: timed out"},
    'poker_connect_fail':            {'es': 'No se pudo conectar: {e}',    'en': "Couldn't connect: {e}"},
    'poker_disconnected':            {'es': 'Desconectado del servidor.',  'en': 'Disconnected from server.'},
    'poker_unknown_error':           {'es': 'Error desconocido',           'en': 'Unknown error'},
    'poker_waiting_players':         {'es': 'Esperando jugadores...',      'en': 'Waiting for players...'},
    'poker_waiting_room':            {'es': 'Sala de espera',              'en': 'Waiting room'},
    'poker_waiting_players_dots':    {'es': 'Esperando jugadores{dots}',   'en': 'Waiting for players{dots}'},
    'poker_connected_count':         {'es': 'Conectados: {n}  ·  Se necesitan mínimo {min}', 'en': 'Connected: {n}  ·  Minimum needed: {min}'},
    'poker_reload_free':             {'es': 'RECARGAR GRATIS',             'en': 'FREE RELOAD'},
    'poker_waiting_hand':            {'es': 'Esperando mano',              'en': 'Waiting for hand'},
    'poker_waiting_turn':            {'es': 'Esperando turno...',          'en': "Waiting for your turn..."},
    'poker_you_won_hand':            {'es': '¡GANASTE! — {hand}  (+{pot})', 'en': 'YOU WON! — {hand}  (+{pot})'},
    'poker_they_won_hand':           {'es': '{winner} GANA — {hand}',      'en': '{winner} WINS — {hand}'},
    'poker_waiting_next_hand':       {'es': 'Esperando siguiente mano...', 'en': 'Waiting for next hand...'},
    'poker_no_chips_reload':         {'es': 'Sin fichas — recarga gratis para seguir jugando', 'en': 'Out of chips — free reload to keep playing'},
    'poker_esc_disconnect':          {'es': 'ESC: desconectar y volver',   'en': 'ESC: disconnect and go back'},
    'poker_esc_back':                {'es': 'ESC: volver',                 'en': 'ESC: back'},
    'poker_esc_back_main':           {'es': 'ESC: volver al menú principal', 'en': 'ESC: back to main menu'},
    'poker_port':                    {'es': 'Puerto',                      'en': 'Port'},
    'poker_connecting':              {'es': 'Conectando...',               'en': 'Connecting...'},
    'poker_connect_btn':             {'es': 'Conectar',                    'en': 'Connect'},
}

def TR(key):
    entry = _TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(CONFIG.get('language', 'es'), entry.get('es', key))

def TRF(key, **kwargs):
    """TR() con formateo de variables: TRF('bj_chips', v=100)."""
    try:
        return TR(key).format(**kwargs)
    except Exception:
        return TR(key)

STORY_TR = {
    'Barcelona. 1987.': 'Barcelona. 1987.',
    'El Barrio Gótico lleva siglos guardando secretos. Esta noche guardará uno más.':
        'The Gothic Quarter has kept secrets for centuries. Tonight it will keep one more.',
    'Al final del Carrer del Bisbe, en un portal sin número, existe un lugar que no aparece en ningún mapa.':
        'At the end of Carrer del Bisbe, behind a doorway with no number, there is a place that appears on no map.',
    '"El Farol Rojo". Un casino clandestino que opera desde hace años con total impunidad.':
        '"El Farol Rojo." An underground casino that has operated for years with total impunity.',
    'Su propietario, Víctor Carvalho, no ha perdido una partida de blackjack en tres años. Nadie sabe cómo lo hace.':
        'Its owner, Víctor Carvalho, hasn\'t lost a game of blackjack in three years. No one knows how he does it.',
    'Tú llegas con mil fichas, una teoría y una promesa que te hiciste a ti mismo.':
        'You arrive with a thousand chips, a theory, and a promise you made to yourself.',
    'Esta noche, alguien va a perder.': 'Tonight, someone is going to lose.',

    '¿A dónde crees que vas, amigo?': 'Where do you think you\'re going, friend?',
    'Primera vez que te veo por aquí.': 'First time I\'ve seen you around here.',
    'Primera vez que vengo. Dicen que aquí sirven las mejores cartas de Barcelona.':
        'First time I\'ve come. They say the best cards in Barcelona are dealt here.',
    '(Sonríe) Y el peor whisky. Te lo advierto. ¿Qué te pongo?':
        '(Smiles) And the worst whisky. Fair warning. What can I get you?',
    'Vaya, vaya... carne fresca. Hacía tiempo que no veía una cara nueva.':
        'Well, well... fresh meat. It\'s been a while since I saw a new face.',
    'Siéntate. ¿Cuánto dinero traes?': 'Sit down. How much money are you carrying?',
    'Mil fichas.': 'A thousand chips.',
    '(Ríe suavemente.) Suficiente para entretenernos unas horas. Quizás.':
        '(Chuckles softly.) Enough to entertain us for a few hours. Maybe.',
    'Las reglas son simples: gana el que llega a 21 sin pasarse. Yo soy la banca.':
        'The rules are simple: whoever gets to 21 without going over wins. I am the house.',
    'Y en este establecimiento... la banca siempre gana. Siempre.':
        'And in this establishment... the house always wins. Always.',
    '¡Que empiece el juego!': 'Let the game begin!',

    '"Vengo a jugar."': '"I\'m here to play."',
    'Vengo a jugar.': 'I\'m here to play.',
    '"Tengo una cita con Víctor."': '"I have an appointment with Víctor."',
    'Tengo una cita con Víctor. Dice que me esperaba.': 'I have an appointment with Víctor. He said he was expecting me.',
    '"He oído que aquí hay acción de verdad."': '"I heard there\'s real action in here."',
    'He oído que aquí hay acción de verdad. Vine a comprobarlo.': 'I heard there\'s real action in here. I came to see for myself.',
    '"Un amigo me recomendó este lugar. Dice que no hay otro igual."':
        '"A friend recommended this place. Said there\'s nowhere else like it."',
    'Un amigo mío me recomendó este lugar. Dice que no hay otro igual en toda Barcelona.':
        'A friend of mine recommended this place. He says there\'s nowhere else like it in all of Barcelona.',
    '"Mil fichas. ¿Suficiente?"': '"A thousand chips. Enough?"',
    'Tengo mil fichas y no tengo prisa. ¿Suficiente?': 'I\'ve got a thousand chips and no hurry. Enough?',
    '"Las suficientes para limpiar la mesa de Víctor."': '"Enough to clean out Víctor\'s table."',
    'Las suficientes para limpiar la mesa de Víctor. Y sobrar.': 'Enough to clean out Víctor\'s table. With plenty to spare.',
    '"Las justas. Pero sé lo que hago."': '"Just enough. But I know what I\'m doing."',
    'Las justas. Pero sé exactamente lo que hago.': 'Just enough. But I know exactly what I\'m doing.',
    '"Hay una primera vez para todo."': '"There\'s a first time for everything."',
    'Hay una primera vez para todo.': 'There\'s a first time for everything.',
    '"Esta noche las cosas cambian."': '"Tonight things change."',
    'Esta noche las cosas van a cambiar, amigo.': 'Tonight things are going to change, my friend.',
    '(Entras sin decir nada.)': '(You walk in without a word.)',
    '...': '...',
    '"¿Y tú, amigo? ¿Cuánto llevas aquí?"': '"And you, friend? How long have you been here?"',
    '¿Y tú? ¿Cuánto tiempo llevas cuidando esta puerta?': 'And you? How long have you been guarding this door?',
    '"Nada. Estoy aquí por Víctor."': '"Nothing. I\'m here for Víctor."',
    'Nada por ahora. Estoy aquí por Víctor.': 'Nothing for now. I\'m here for Víctor.',
    '"Ponme lo que tú tomarías."': '"Give me whatever you\'d have."',
    'Ponme lo que tú tomarías. Y cuéntame algo sobre este sitio.': 'Give me whatever you\'d have. And tell me something about this place.',
    '"El whisky más caro. Lo celebro por adelantado."': '"The most expensive whisky. I\'m celebrating in advance."',
    'El whisky más caro que tengas. Esta noche lo celebro por adelantado.':
        'The most expensive whisky you\'ve got. Tonight I\'m celebrating in advance.',
    '"¿Qué recomiendas tú para una noche larga?"': '"What do you recommend for a long night?"',
    '¿Qué recomiendas tú para una noche larga, Rosa?': 'What do you recommend for a long night, Rosa?',
    '"¿Y si pierde? ¿Qué pasa entonces?"': '"And if he loses? What happens then?"',
    '¿Y si pierde? ¿Qué pasa?': 'And if he loses? What happens?',
    '"¿Le has visto hacer trampa alguna vez?"': '"Have you ever seen him cheat?"',
    '¿Tú le has visto hacer trampa alguna vez?': 'Have you ever seen him cheat?',
    '"¿Puedo pedirte algo... más personal?"': '"Can I ask you something... more personal?"',
    '¿Puedo pedirte algo más personal, Rosa?': 'Can I ask you something more personal, Rosa?',
    '"¿Por qué sigues trabajando para Víctor?"': '"Why do you keep working for Víctor?"',
    '¿Por qué sigues trabajando para alguien como Víctor?': 'Why do you keep working for someone like Víctor?',
    '"Gracias por el consejo, Rosa. Esta noche me traerá suerte."': '"Thanks for the advice, Rosa. It\'ll bring me luck tonight."',
    'Gracias por los consejos, Rosa. Esta noche me traerán suerte.': 'Thanks for the advice, Rosa. It\'ll bring me luck tonight.',
    '"Oye, ¿me acompañas tú a la mesa de suerte?"': '"Hey, why don\'t you come sit with me at the table for luck?"',
    'Oye, ¿y si me acompañas a la mesa esta noche? Serías mi amuleto de la suerte.':
        'Hey, what if you sat with me at the table tonight? You\'d be my good-luck charm.',
    '[Comportamiento inapropiado con Rosa — Final Malo]': '[Inappropriate behavior toward Rosa — Bad Ending]',
    '"Si llego a 10.000… me dices cómo haces trampa."': '"If I reach 10,000... you tell me how you cheat."',
    'De acuerdo. Pero tengo una condición.': 'Fine. But I have one condition.',
    '"Si llego a 25.000… que toda la sala lo sepa."': '"If I reach 25,000... let the whole room know it."',
    'Si llego a veinticinco mil fichas... quiero que esta sala sepa que la banca puede perder.':
        'If I reach twenty-five thousand chips... I want this whole room to know the house can lose.',
    '"Si llego a 50.000… este casino es mío."': '"If I reach 50,000... this casino is mine."',
    'Si llego a cincuenta mil fichas... este casino pasa a ser mío. En espíritu.':
        'If I reach fifty thousand chips... this casino becomes mine. In spirit.',
    '"Sin condiciones. Solo voy a ganar. 100.000."': '"No conditions. I\'m just here to win. 100,000."',
    'Sin condiciones, Víctor. Cien mil fichas. Solo vengo a ganar.': 'No conditions, Víctor. One hundred thousand chips. I\'m only here to win.',

    '+50 fichas — el portero queda impresionado': '+50 chips — the doorman is impressed',
    '+75 fichas — el portero te tiene simpatía': '+75 chips — the doorman has taken a liking to you',
    '+100 fichas — Rosa confía en ti': '+100 chips — Rosa trusts you',
    '−50 fichas — ese whisky era caro de verdad': '−50 chips — that whisky was genuinely expensive',
    '+80 fichas — el consejo de Rosa tiene precio': '+80 chips — Rosa\'s advice comes at a price',
    '+150 fichas — Rosa tiene fe en ti': '+150 chips — Rosa believes in you',
    '+60 fichas — Rosa deposita su esperanza en ti': '+60 chips — Rosa is putting her hope in you',

    'Aquí no entra cualquiera. Este no es un sitio para turistas.':
        'Not just anyone gets in here. This isn\'t a place for tourists.',
    '(Frunce el ceño.) ¿Con el jefe? Nadie tiene "citas" con Víctor...':
        '(Frowns.) With the boss? Nobody has "appointments" with Víctor...',
    '(Tras una pausa.) Pero algo en tu cara dice que no mientes. Venga.':
        '(After a pause.) But something about your face says you\'re not lying. Go on in.',
    '(Resopla.) Todo el mundo "ha oído". Lo que no todo el mundo tiene es pasta para respaldarlo.':
        '(Snorts.) Everybody\'s "heard." What not everybody has is the cash to back it up.',
    '(Entrecierra los ojos.) ¿Qué amigo?': '(Narrows his eyes.) What friend?',
    'El tipo no da su nombre. Solo su palabra.': 'The guy doesn\'t give his name. Just his word.',
    '(Bufido.) Típico. Bueno... si alguien te mandó, algo sabes. Adelante.':
        '(Snorts.) Typical. Well... if someone sent you, you must know something. Go ahead.',
    '(Te mira de arriba abajo durante un momento largo.)': '(He looks you up and down for a long moment.)',
    '...Pasa. Pero sabe que nadie ha salido de aquí ganando. Nadie.':
        '...Go in. But know that no one has ever walked out of here a winner. No one.',
    '(Casi sonríe.) Otro que viene con ganas. Venga, pasa antes de que me arrepienta.':
        '(Almost smiles.) Another one full of ambition. Go on, get in before I change my mind.',
    'Que conste: nadie ha salido de aquí ganando. Nadie.': 'For the record: no one has ever walked out of here a winner. No one.',
    '(Una pausa. Te estudia de arriba abajo.)': '(A pause. He studies you head to toe.)',
    'Esa mirada... he visto esa mirada antes. Dos veces. Uno salió rico. El otro no salió.':
        'That look... I\'ve seen that look before. Twice. One left rich. The other never left.',
    'A ver en cuál de los dos te conviertes tú. Adelante.': 'Let\'s see which one you turn out to be. Go on in.',
    '(Te mira sorprendido. Nadie le pregunta eso.)': '(He looks at you, surprised. No one ever asks him that.)',
    'Seis años. Seis años viendo entrar a gente con sueños y salir con deudas.':
        'Six years. Six years watching people walk in with dreams and walk out with debts.',
    '(En voz baja.) Tú... ten cuidado, ¿eh? Víctor no es lo que parece.':
        '(Quietly.) You... be careful, all right? Víctor isn\'t what he seems.',

    '(La sonrisa desaparece.) Cuidado con él. Lleva tres años sin perder. Dicen que ve las cartas antes de que salgan.':
        '(The smile fades.) Careful with him. He hasn\'t lost in three years. They say he sees the cards before they\'re dealt.',
    '(Sonríe con melancolía.) Un Laphroaig, entonces. Y sobre este sitio... todo lo que ves tiene dueño. Incluidas las cartas.':
        '(Smiles wistfully.) A Laphroaig, then. And about this place... everything you see has an owner. Including the cards.',
    'Un consejo gratis: cuando Víctor se toque el nudo de la corbata, tiene buena mano. Guárdatelo.':
        'Free advice: when Víctor touches the knot of his tie, he\'s got a good hand. Keep that in mind.',
    '(Rosa te pasa discretamente un billete doblado. +100 fichas para la partida.)':
        '(Rosa discreetly slips you a folded bill. +100 chips for the game.)',
    '(Arquea una ceja.) Confiado. Me gusta. Aunque aquí los que llegan muy seguros... suelen salir más callados.':
        '(Raises an eyebrow.) Confident. I like that. Though around here, the ones who arrive so sure of themselves... tend to leave a lot quieter.',
    '(El whisky de malta llega rápido. Vacías la copa de un trago. −50 fichas de tu bolsillo.)':
        '(The single malt arrives quickly. You down the glass in one go. −50 chips from your pocket.)',
    '(Se apoya en la barra con una sonrisa cómplice.) Para una noche larga...':
        '(Leans on the bar with a knowing smile.) For a long night...',
    'Agua con gas. La cabeza despejada vale más que cualquier carta.':
        'Sparkling water. A clear head is worth more than any card.',
    '(Rosa añade con discreción un par de fichas al montón.) Un extra, de mi parte.':
        '(Rosa discreetly adds a couple of chips to the pile.) A little extra, on the house.',
    'Eso... nadie lo sabe. Nunca ha pasado. Nadie ha llegado tan lejos.':
        'That... nobody knows. It\'s never happened. No one has ever gotten that far.',
    'Pues esta noche vamos a descubrirlo.': 'Well, tonight we\'re going to find out.',
    '(En voz baja) Ten cuidado. En serio.': '(Quietly) Be careful. I mean it.',
    '(Pausa. Baja la voz.) No exactamente... pero hay momentos en que las cartas parecen obedecerle. Como si las conociera de antes.':
        '(Pause. Lowers her voice.) Not exactly... but there are moments when the cards seem to obey him. As if he already knew them.',
    'Nada demostrable. Nunca nada demostrable. Ten cuidado, ¿de acuerdo?':
        'Nothing provable. Never anything provable. Just be careful, okay?',
    '(Te mira un instante demasiado largo. Después apoya los codos en la barra y baja la voz.)':
        '(She looks at you a moment too long. Then she leans her elbows on the bar and lowers her voice.)',
    'La puerta azul al fondo. Cinco minutos. Nadie mira hacia allí a esta hora.':
        'The blue door at the back. Five minutes. Nobody looks that way at this hour.',
    'Lo que ocurrió al fondo del pasillo, entre cajas de Laphroaig y la penumbra azul, queda ahí.':
        'What happened at the end of that hallway, among crates of Laphroaig and the blue half-light, stays there.',
    'Cinco minutos que se notaron más que cinco horas.': 'Five minutes that felt like five hours.',
    'De vuelta en la barra, Rosa sirve una copa sin mirarte. Pero sonríe.':
        'Back at the bar, Rosa pours a drink without looking at you. But she\'s smiling.',
    '(En voz muy baja, arreglándose el cabello.) Gana esta noche, ¿de acuerdo?':
        '(Very quietly, fixing her hair.) Win tonight, all right?',
    'Ahora tengo más motivos para hacerlo.': 'Now I have even more reason to.',
    '(Una sonrisa que intenta esconder, sin éxito.) Anda ya...':
        '(A smile she tries and fails to hide.) Oh, get out of here...',
    'Su perfume te acompañará el resto de la noche. +150 fichas — Rosa tiene fe en ti.':
        'Her perfume will stay with you the rest of the night. +150 chips — Rosa believes in you.',
    '(Una pausa larga. Limpia el vaso sin mirarte.)': '(A long pause. She wipes the glass without looking at you.)',
    'Porque las deudas no se pagan solas. Y porque... todavía no ha llegado nadie que lo saque de ahí.':
        'Because debts don\'t pay themselves. And because... nobody\'s come along yet who can get him out of this.',
    '(Te mira fijamente.) Quizás esta noche cambia eso.': '(Looks straight at you.) Maybe tonight that changes.',
    '(Algo en su voz suena a esperanza. +60 fichas — un pequeño empujón de su parte.)':
        '(Something in her voice sounds like hope. +60 chips — a small push from her.)',
    '(Asiente con una sonrisa tranquila.) Eso espero. Ya sé dónde encontrarte si ganas.':
        '(Nods with a calm smile.) I hope so. I know where to find you if you win.',
    '(Sonríe con paciencia.) Tengo trabajo. Y tú tienes una partida que ganar. Anda.':
        '(Smiles patiently.) I\'ve got work to do. And you\'ve got a game to win. Go on.',
    'Algo en tu actitud cruza una línea que no debería haberse cruzado.':
        'Something in your attitude crosses a line that should never have been crossed.',
    '(Te mira fijamente. Después levanta la mano hacia el fondo de la sala.) Marcos.':
        '(She stares at you. Then raises her hand toward the back of the room.) Marcos.',
    'El hombre más grande que has visto en tu vida emerge de las sombras.':
        'The biggest man you\'ve ever seen steps out of the shadows.',
    '¿Algún problema, Rosa?': 'Any trouble, Rosa?',
    '(Sin apartar los ojos de ti.) Este señor ya se iba.': '(Without taking her eyes off you.) This gentleman was just leaving.',

    '(Arquea una ceja.) ¿Condición? Eso es... inusual.': '(Raises an eyebrow.) A condition? That\'s... unusual.',
    'Si llego a diez mil fichas... me dices cómo lo haces. Cómo haces trampa.':
        'If I reach ten thousand chips... you tell me how you do it. How you cheat.',
    '(Pausa larga. Te mira fijamente. Luego sonríe.) ...Trato hecho, forastero. Suerte.':
        '(Long pause. He stares at you. Then smiles.) ...Deal, stranger. Good luck.',
    'La vas a necesitar.': 'You\'re going to need it.',
    '[ MODO NORMAL — Meta: 10.000 fichas. La banca no se rinde fácil, pero tampoco es invencible. ]':
        '[ NORMAL MODE — Goal: 10,000 chips. The house doesn\'t give up easily, but it isn\'t invincible either. ]',
    '(Una sonrisa fría, casi apreciativa.) Ambicioso. Me gustan los ambiciosos.':
        '(A cold, almost appreciative smile.) Ambitious. I like ambitious people.',
    'Suelen quedarse sin nada antes del amanecer. Pero... de acuerdo. Trato hecho.':
        'They usually end up with nothing by dawn. But... fine. Deal.',
    'Veamos de qué pasta estás hecho, forastero.': 'Let\'s see what you\'re made of, stranger.',
    '[ MODO DIFÍCIL — Meta: 25.000 fichas. Víctor ordena a sus crupiers que jueguen más agresivo. ]':
        '[ HARD MODE — Goal: 25,000 chips. Víctor orders his dealers to play more aggressively. ]',
    '(Una carcajada seca.) ¡Cincuenta mil! Hace años que nadie me desafía así.':
        '(A dry laugh.) Fifty thousand! It\'s been years since anyone challenged me like that.',
    '(Se inclina hacia adelante.) Acepto. Pero cuando pierdas... y perderás... sal por esa puerta y no vuelvas.':
        '(Leans forward.) I accept. But when you lose... and you will lose... walk out that door and don\'t come back.',
    '[ MODO MUY DIFÍCIL — Meta: 50.000 fichas. La banca juega sin misericordia. ]':
        '[ VERY HARD MODE — Goal: 50,000 chips. The house plays without mercy. ]',
    '(Se recuesta en la silla. Un silencio largo y tenso.)': '(He leans back in his chair. A long, tense silence.)',
    'Cien mil. Nadie... absolutamente nadie ha pronunciado esa cifra aquí.':
        'One hundred thousand. Nobody... absolutely nobody has ever said that number in here.',
    '(La sonrisa se congela.) Muy bien. Sin condiciones. Pero a este nivel... la banca no tiene piedad.':
        '(His smile freezes.) Very well. No conditions. But at this level... the house shows no mercy.',
    '[ MODO EXTREMO — Meta: 100.000 fichas. La banca juega sin compasión. Buena suerte. ]':
        '[ EXTREME MODE — Goal: 100,000 chips. The house plays without compassion. Good luck. ]',

    'A mitad de la calle oyes pasos rápidos detrás de ti.': 'Halfway down the street you hear quick footsteps behind you.',
    '(Sin aliento.) ¡Espera!': '(Breathless.) Wait!',
    'Rosa lleva el abrigo a medio poner y una botella de champán robada al bar bajo el brazo.':
        'Rosa has her coat half on and a bottle of champagne swiped from the bar tucked under her arm.',
    '¿No deberías estar trabajando?': 'Shouldn\'t you be working?',
    '(Sonriendo.) Esta noche no. Esta noche yo también me voy.': '(Smiling.) Not tonight. Tonight I\'m getting out too.',
    'Le das la mano sin decir nada. Ella no la suelta.': 'You take her hand without a word. She doesn\'t let go.',
    'Sabía que lo conseguirías. Lo sabía desde el principio.': 'I knew you\'d pull it off. I knew it from the start.',
    'No me lo creía ni yo.': 'Even I didn\'t believe it.',
    '(Levanta la botella.) ¿Celebramos?': '(Raises the bottle.) Shall we celebrate?',
    'El corcho sale disparado y rebota contra los adoquines mojados. Rosa ríe — alto, sin disimulo, como si la ciudad entera necesitara saberlo.':
        'The cork shoots off and bounces on the wet cobblestones. Rosa laughs — loud, unashamed, as if the whole city needed to know.',
    'Es la primera vez en mucho tiempo que oyes reír así a alguien.':
        'It\'s the first time in a long while you\'ve heard anyone laugh like that.',
    'Los dos caminan hacia el mar. El champán se enfría con la brisa. El neón de El Farol Rojo se apaga para siempre detrás.':
        'The two of you walk toward the sea. The champagne cools in the breeze. Behind you, the neon sign of El Farol Rojo goes dark forever.',
    '─────────  FIN  ─────────': '─────────  THE END  ─────────',

    'Diez mil fichas. La mesa entera se queda en silencio.': 'Ten thousand chips. The whole table falls silent.',
    '¿Cómo?': 'What?',
    'Ya sabes lo que acordamos, Víctor.': 'You know what we agreed, Víctor.',
    '(Una pausa larga. Sus ojos te estudian.) ...Bien.': '(A long pause. His eyes study you.) ...Fine.',
    '(En voz baja, casi solo para ti.) El segundo crupier de la derecha. Lleva cuatro años marcando las cartas con la uña.':
        '(Quietly, almost just for you.) The second dealer on the right. He\'s been marking the cards with his fingernail for four years.',
    'Nunca esperé tener que decirlo. Nunca.': 'I never expected to have to say it. Never.',
    'Lo sé. Gracias por cumplir tu palabra.': 'I know. Thank you for keeping your word.',
    'Al salir, el susurro ya recorre la sala.': 'As you leave, the whisper is already spreading through the room.',
    'El hombre que hizo hablar a Víctor Carvalho.': 'The man who made Víctor Carvalho talk.',
    'Rosa te espera junto a la barra con una sonrisa que no intenta esconder.':
        'Rosa is waiting by the bar with a smile she doesn\'t bother to hide.',
    '(En voz baja.) ¿Te lo dijo?': '(Quietly.) Did he tell you?',
    'Me lo dijo.': 'He told me.',
    '(Larga pausa.) Bien. Ya era hora.': '(Long pause.) Good. About time.',
    'Dos grandes se levantan, pero Víctor los detiene con un gesto. Esta vez, la puerta es tuya.':
        'Two big men stand up, but Víctor stops them with a gesture. This time, the door is yours.',
    '(Abre la puerta sin decir nada.)': '(He opens the door without a word.)',
    '(Te guiña un ojo desde el otro lado de la sala.)': '(She winks at you from across the room.)',
    'El aire de la madrugada huele a lluvia limpia. A libertad.': 'The early-morning air smells of clean rain. Of freedom.',
    'Caminas despacio por los adoquines mojados.': 'You walk slowly over the wet cobblestones.',
    'Detrás de ti, el neón de "El Farol Rojo" parpadea dos veces y se apaga.':
        'Behind you, the neon sign of "El Farol Rojo" flickers twice and goes dark.',
    'Lo lograste en modo Normal. Víctor nunca imaginó que alguien le haría hablar.':
        'You did it on Normal mode. Víctor never imagined anyone could make him talk.',
    'La ciudad empieza a despertar. Huele a café y a pan recién hecho.':
        'The city is starting to wake up. It smells of coffee and fresh bread.',

    'Veinticinco mil fichas. La sala entera lo vio.': 'Twenty-five thousand chips. The whole room saw it.',
    'El murmullo empieza en las mesas de los laterales y viaja hasta el fondo.':
        'The murmur starts at the side tables and travels all the way to the back.',
    '(Se pone de pie lentamente.) ¡Trampa! ¡Este hombre ha hecho trampa!':
        '(Slowly stands up.) Cheat! This man is cheating!',
    'Las cartas no mienten, Víctor. Toda la sala lo vio.': 'The cards don\'t lie, Víctor. The whole room saw it.',
    'Un crupier anciano al fondo suelta las cartas sobre la mesa y mueve la cabeza.':
        'An old dealer at the back sets down his cards and shakes his head.',
    'Él también lo sabe. Todos lo saben.': 'He knows it too. Everyone knows it.',
    '(Su voz pierde fuerza.) ...Garduño. Enrique.': '(His voice loses its force.) ...Garduño. Enrique.',
    'Los dos hombres se levantan, pero el ambiente ya se giró.': 'The two men stand up, but the mood in the room has already turned.',
    'Tres jugadores de las otras mesas se ponen de pie entre tú y ellos.':
        'Three players from the other tables stand up between you and them.',
    'Nadie dice nada. No hace falta.': 'Nobody says anything. They don\'t need to.',
    '¡Ay, Dios mío, qué torpe!': 'Oh my God, how clumsy of me!',
    'Rosa vuelca la barra entera. Cristales, botellas, caos total.': 'Rosa knocks over the entire bar. Glass, bottles, total chaos.',
    'En medio del tumulto, tú caminas tranquilamente hacia la puerta.':
        'In the middle of the uproar, you calmly walk toward the door.',
    '(Te sostiene la puerta abierta. Con respeto.)': '(He holds the door open for you. With respect.)',
    '(Te guiña un ojo desde el otro lado del caos.)': '(She winks at you from across the chaos.)',
    'El aire de la madrugada tiene sabor a victoria.': 'The early-morning air tastes of victory.',
    'No solo la tuya. La de todos los que perdieron antes que tú.': 'Not just yours. The victory of everyone who lost before you.',
    'Detrás de ti, el neón de "El Farol Rojo" parpadea y se apaga.':
        'Behind you, the neon sign of "El Farol Rojo" flickers and goes dark.',
    'Lo lograste en modo Difícil. La banca jugó sin piedad y aun así no fue suficiente.':
        'You did it on Hard mode. The house played without mercy, and it still wasn\'t enough.',
    'Veinticinco mil fichas. Una hazaña que el Barrio Gótico no olvidará.':
        'Twenty-five thousand chips. A feat the Gothic Quarter will not forget.',

    'Cincuenta mil fichas. Nadie en esta sala creyó que fuera posible.':
        'Fifty thousand chips. No one in this room believed it was possible.',
    'Ni siquiera tú, en el fondo.': 'Not even you, deep down.',
    '(Volcando la silla.) ¡Imposible! ¡Imposible, digo!': '(Knocking over his chair.) Impossible! I say impossible!',
    'Este casino es mío. En espíritu. Y tú lo sabes.': 'This casino is mine. In spirit. And you know it.',
    '(Mira hacia la puerta trasera. Calcula.)': '(Glances at the back door. Calculating.)',
    'Pero los crupiers se pusieron de pie. Rosa bloqueó la barra. Hasta Marcos, el portero, dio un paso al lado.':
        'But the dealers stood up. Rosa blocked the bar. Even Marcos, the doorman, stepped aside.',
    '(En voz muy baja, solo para ti.) ...¿Cómo lo hiciste?': '(Very quietly, just for you.) ...How did you do it?',
    'La sala entera te abre paso. No como a un ganador. Como a alguien que tiene razón.':
        'The whole room clears a path for you. Not like a winner. Like someone who was right.',
    '(Con voz firme.) Esta noche, el Farol Rojo tiene un nuevo campeón.':
        '(In a firm voice.) Tonight, El Farol Rojo has a new champion.',
    'Aplausos. Lentos al principio. Luego toda la sala.': 'Applause. Slow at first. Then the whole room.',
    'Víctor observa desde el fondo, solo, con las manos vacías.': 'Víctor watches from the back, alone, empty-handed.',
    'Cincuenta años de impunidad terminaron esta noche.': 'Fifty years of impunity ended tonight.',
    '(Te abre la puerta principal con las dos manos.)': '(He opens the main door for you with both hands.)',
    '(Te guiña un ojo. Hay algo diferente en su cara — parece libre.)':
        '(She winks at you. There\'s something different about her face — she looks free.)',
    'La madrugada de Barcelona te recibe como a un fantasma victorioso.':
        'The Barcelona dawn welcomes you like a triumphant ghost.',
    'Detrás de ti, "El Farol Rojo" parpadea y se apaga para siempre.':
        'Behind you, "El Farol Rojo" flickers and goes dark forever.',
    'Lo lograste en modo Muy Difícil. Cincuenta mil fichas. Una hazaña que nadie olvidará.':
        'You did it on Very Hard mode. Fifty thousand chips. A feat no one will forget.',
    'El Barrio Gótico guarda secretos. Esta noche guarda uno más: el tuyo.':
        'The Gothic Quarter keeps secrets. Tonight it keeps one more: yours.',

    'Cien mil fichas.': 'One hundred thousand chips.',
    'El número imposible. El que nadie se atrevió a perseguir en tres años.':
        'The impossible number. The one no one dared chase in three years.',
    'El aire se detuvo. La música se detuvo. Todo se detuvo.': 'The air stopped. The music stopped. Everything stopped.',
    '(En pie. La cara descompuesta.) No... no puede ser...': '(Standing. His face falls apart.) No... it can\'t be...',
    'Ya lo es, Víctor. Ya lo es.': 'It already is, Víctor. It already is.',
    '(Las manos le tiemblan. Por primera vez en su vida, tiemblan.)':
        '(His hands are shaking. For the first time in his life, they\'re shaking.)',
    'Nadie en la sala se mueve. El hombre que nunca perdió acaba de perderlo todo.':
        'No one in the room moves. The man who never lost has just lost everything.',
    '(En un susurro.) ...¿Quién eres tú?': '(In a whisper.) ...Who are you?',
    'Los dos matones no se mueven. Nadie se mueve.': 'The two thugs don\'t move. No one moves.',
    'Hay cosas que el dinero no puede detener, y esta noche todo el mundo lo siente.':
        'There are things money can\'t stop, and tonight everyone feels it.',
    '(Deja caer el vaso que estaba limpiando. Se acerca despacio.)':
        '(Drops the glass she was cleaning. Walks over slowly.)',
    'Tres años trabajando para ese hombre. Tres años esperando esto.':
        'Three years working for that man. Three years waiting for this.',
    'Rosa vuelca la barra entera. Un diluvio de cristal y whisky caro.':
        'Rosa knocks over the entire bar. A flood of glass and expensive whisky.',
    'En el caos absoluto, tú caminas hacia la puerta con calma de cirujano.':
        'In the total chaos, you walk to the door with a surgeon\'s calm.',
    '(Se hace a un lado. Asiente una sola vez.)': '(Steps aside. Nods once.)',
    '(Te guiña un ojo desde el otro lado del infierno.)': '(She winks at you from across the wreckage.)',
    'Afuera, la ciudad respira.': 'Outside, the city breathes.',
    'Cien mil fichas. El número que nadie pronunció jamás en El Farol Rojo.':
        'One hundred thousand chips. The number no one ever spoke inside El Farol Rojo.',
    'Hasta esta noche.': 'Until tonight.',
    'Detrás de ti, el neón parpadea tres veces y se apaga para siempre. Ya no volverá a encenderse.':
        'Behind you, the neon sign flickers three times and goes dark forever. It will never light up again.',
    'Lo lograste en modo EXTREMO. Cien mil fichas. Ni Víctor mismo se lo creerá jamás.':
        'You did it on EXTREME mode. One hundred thousand chips. Even Víctor himself will never quite believe it.',
    'Hay cosas que no se explican. Tú eres una de ellas.': 'Some things can\'t be explained. You are one of them.',

    'Marcos no te da tiempo a reaccionar. Dos manos del tamaño de jamones te agarran por los hombros.':
        'Marcos doesn\'t give you time to react. Two ham-sized hands grab you by the shoulders.',
    'Fin de la noche, amigo.': 'Night\'s over, friend.',
    '¡Espera, espera! Solo estaba...': 'Wait, wait! I was just...',
    'Ya lo he visto. Y ella también lo ha visto. Vamos.': 'I already saw it. And so did she. Let\'s go.',
    'Cruzas la sala entera escoltado. Cada par de ojos se vuelve hacia ti. El silencio es peor que cualquier insulto.':
        'You\'re marched across the entire room. Every pair of eyes turns toward you. The silence is worse than any insult.',
    '(Desde la barra, sin mirarte.) Buenas noches.': '(From the bar, without looking at you.) Good night.',
    'No hay emoción en su voz. Solo distancia.': 'There\'s no emotion in her voice. Only distance.',
    'La puerta se cierra detrás de ti con un golpe seco.': 'The door slams shut behind you with a dull thud.',
    'El Barrio Gótico te devuelve el frío de siempre. La lluvia. Los adoquines mojados.':
        'The Gothic Quarter greets you with its usual cold. The rain. The wet cobblestones.',
    'No perdiste dinero en la mesa de Víctor. Ni siquiera llegaste a sentarte.':
        'You didn\'t lose any money at Víctor\'s table. You never even got to sit down.',
    'Pero saliste igual de vacío.': 'But you walked out just as empty.',
    'En algún lugar detrás de esa puerta, Rosa sigue trabajando. Sin pensar en ti.':
        'Somewhere behind that door, Rosa keeps working. Without a thought for you.',
    'Algunas derrotas no tienen que ver con las cartas.': 'Some defeats have nothing to do with the cards.',
    '─────────  FINAL MALO  ─────────': '─────────  BAD ENDING  ─────────',

    'Construye las escenas de derrota según la dificultad actual.':
        'Builds the defeat scenes based on the current difficulty.',

    'Y así terminó.': 'And so it ended.',
    'Ya está. Eso es todo lo que tenías.': 'That\'s it. That was everything you had.',
    'Ha sido... entretenido. Para mí.': 'It\'s been... entertaining. For me.',
    '(Sin levantar la vista de las fichas.) La puerta está donde la dejaste. Buenas noches.':
        '(Without looking up from the chips.) The door\'s right where you left it. Good night.',
    'No había nada más que decir.': 'There was nothing more to say.',
    'Volviste a la calle con los bolsillos vacíos y la cabeza llena de preguntas.':
        'You went back out into the street with empty pockets and a head full of questions.',
    'La lluvia seguía ahí. Indiferente. Como siempre.': 'The rain was still there. Indifferent. As always.',
    'Víctor seguía dentro, invicto. De momento.': 'Víctor was still inside, undefeated. For now.',
    'Pero el juego no había terminado. Solo esta ronda.': 'But the game wasn\'t over. Only this round.',
    'Mañana es otro día. Y tú sabes dónde está la puerta.': 'Tomorrow is another day. And you know where the door is.',

    'Las fichas desaparecieron una a una. Cada mano, una pequeña muerte.':
        'The chips disappeared one by one. Each hand, a small death.',
    '(Con una sonrisa lenta.) Veinticinco mil... qué ambición tan hermosa.':
        '(With a slow smile.) Twenty-five thousand... what beautiful ambition.',
    'Lástima que la ambición sin suerte no llegue muy lejos, ¿verdad?':
        'Pity that ambition without luck doesn\'t get you very far, does it?',
    'Las cartas no estuvieron de mi lado esta noche.': 'The cards weren\'t on my side tonight.',
    'Las cartas nunca están de tu lado, forastero. Solo de la mía.': 'The cards are never on your side, stranger. Only mine.',
    'Se recostó en la silla con la comodidad de alguien que nunca ha tenido que preocuparse.':
        'He leaned back in his chair with the ease of someone who has never had to worry.',
    'La noche te devuelve a los adoquines mojados del Barrio Gótico.':
        'The night sends you back to the wet cobblestones of the Gothic Quarter.',
    'Veinticinco mil fichas. Casi lo tocaste. Casi.': 'Twenty-five thousand chips. You almost had it. Almost.',
    'Víctor sigue ahí dentro, intacto, con esa sonrisa que nunca se mueve del todo.':
        'Víctor is still in there, untouched, with that smile that never quite moves.',
    'Pero esta vez llegaste más lejos de lo que esperaba. Y lo sabe.':
        'But this time you got further than he expected. And he knows it.',

    'Cincuenta mil fichas. Nadie había llegado tan cerca. Nadie.': 'Fifty thousand chips. No one had ever come this close. No one.',
    'Hasta hoy.': 'Until today.',
    '(Frunciendo ligeramente el ceño.) Has aguantado más de lo esperado.': '(Frowning slightly.) You held out longer than expected.',
    'Eso es porque sé lo que haces, Víctor.': 'That\'s because I know what you\'re doing, Víctor.',
    '(Una pausa demasiado larga.) No sé de qué hablas. La suerte te ha abandonado. Eso es todo.':
        '(A pause that lasts too long.) I don\'t know what you\'re talking about. Your luck ran out. That\'s all.',
    'Pero su voz tiene una grieta que antes no estaba ahí.': 'But there\'s a crack in his voice that wasn\'t there before.',
    'La puerta, forastero. Y esta vez... no tan tranquilo como antes.':
        'The door, stranger. And this time... not so calm as before.',
    'El frío de la madrugada te golpea en la cara.': 'The cold of early morning hits you in the face.',
    'Cincuenta mil fichas. Estuviste a un suspiro de doblarle.': 'Fifty thousand chips. You were a heartbeat away from breaking him.',
    'Y Víctor lo sabe. Por primera vez en tres años, alguien le ha puesto nervioso.':
        'And Víctor knows it. For the first time in three years, someone has made him nervous.',
    'El Farol Rojo nunca volverá a ser del todo lo mismo.': 'El Farol Rojo will never quite be the same again.',
    'Ni tú tampoco.': 'And neither will you.',

    'Cien mil fichas. Nadie había pronunciado esa cifra en este casino. Nadie la había perseguido.':
        'One hundred thousand chips. No one had ever spoken that number in this casino. No one had ever chased it.',
    '(Se pone de pie. Algo en sus ojos cambió.)': '(He stands up. Something in his eyes has changed.)',
    'Yo... no esperaba esto. En tres años, nadie...': 'I... didn\'t expect this. In three years, no one has...',
    'Ya lo sé, Víctor. Y tú también lo sabes.': 'I know, Víctor. And you know it too.',
    'Un silencio largo cae sobre la sala. Todos miran.': 'A long silence falls over the room. Everyone is watching.',
    '(En voz muy baja.) La puerta. Y... vuelve cuando quieras.': '(Very quietly.) The door. And... come back whenever you want.',
    'Es lo más cercano a respeto que Víctor Carvalho ha mostrado jamás.':
        'It\'s the closest thing to respect Víctor Carvalho has ever shown.',
    'La ciudad todavía duerme. Aún no amanece.': 'The city is still asleep. Dawn hasn\'t broken yet.',
    'Cien mil fichas. Lo perseguiste hasta el borde del abismo y casi lo empujaste.':
        'One hundred thousand chips. You chased him to the edge of the abyss and nearly pushed him over.',
    'Víctor sigue dentro. Pero algo se quebró esta noche en El Farol Rojo.':
        'Víctor is still inside. But something broke tonight in El Farol Rojo.',
    'Puedes sentirlo en el aire, como el olor a ozono antes de una tormenta.':
        'You can feel it in the air, like the smell of ozone before a storm.',
    'Este lugar nunca ha conocido a nadie como tú. Y ahora lo sabe.':
        'This place has never known anyone like you. And now it knows.',
}

_SPEAKER_TR = {
    'narrador': {'es': 'narrador', 'en': 'Narrator'},
    'Portero':  {'es': 'Portero',  'en': 'Doorman'},
    'Camarera': {'es': 'Camarera', 'en': 'Waitress'},
    'Tú':       {'es': 'Tú',       'en': 'You'},
}

def S(text):
    """Traduce una linea de dialogo/opcion del Modo Historia al idioma activo."""
    if CONFIG.get('language', 'es') == 'en':
        return STORY_TR.get(text, text)
    return text

def S_SPEAKER(speaker):
    """Traduce el nombre mostrado de un personaje (mantiene la key original para logica interna)."""
    entry = _SPEAKER_TR.get(speaker)
    if not entry:
        return speaker
    return entry.get(CONFIG.get('language', 'es'), speaker)


def open_data_folder():
    """Abre la carpeta de datos en el explorador del sistema."""
    try:
        if sys.platform == 'darwin':
            subprocess.Popen(['open', DATA_DIR])
        elif sys.platform == 'win32':
            subprocess.Popen(['explorer', DATA_DIR])
        else:
            subprocess.Popen(['xdg-open', DATA_DIR])
    except Exception as e:
        print(f"[FOLDER] No se pudo abrir carpeta: {e}")

pygame.init()
pygame.mixer.init()

VERSION = "1.6.6"
GITHUB_RAW_URL  = "https://raw.githubusercontent.com/humrand/blackjack-python/main/El_farol_rojo.py"
GITHUB_API_URL  = "https://api.github.com/repos/humrand/blackjack-python/commits?path=El_farol_rojo.py&per_page=1"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/humrand/blackjack-python/{sha}/El_farol_rojo.py"
_COMMIT_SHA_FILE = os.path.join(_get_data_dir(), '.last_commit_sha')

GITHUB_RELEASES_API      = "https://api.github.com/repos/humrand/blackjack-python/releases/latest"
_RELEASE_ASSET_NAME_LINUX   = "ElFarolRojo-linux"
_RELEASE_ASSET_NAME_WINDOWS = "ElFarolRojo-windows.exe"
_LAST_VERSION_FILE = os.path.join(_get_data_dir(), '.last_release_tag')

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
    'rosita-dedo':  ('rosita-dedo.png',        'rosita-dedo.png'),
    'cuarto-oscuro':('cuarto-oscuro.png',      'cuarto-oscuro.png'),
    'rosita-fichas':('rosita-fichas.png',      'rosita-fichas.png'),
    'mesa':          ('mesa.png',               'mesa.png'),
}
_image_cache = {}
_image_downloading = set()

_CARDS_BASE_URL  = "https://raw.githubusercontent.com/humrand/blackjack-python/main/imagenes/cards/"
_card_img_cache       = {}
_card_img_downloading = set()

_VALOR_MAP = {
    'A': 'ace', '2': '2', '3': '3', '4': '4', '5': '5',
    '6': '6', '7': '7', '8': '8', '9': '9', '10': '10',
    'J': 'jack', 'Q': 'queen', 'K': 'king'
}
_PALO_MAP = {
    'S': 'spades', 'H': 'hearts', 'D': 'diamonds', 'C': 'clubs'
}

def _card_filename(valor, palo):
    """Convierte valor+palo internos al nombre de archivo del repositorio.
    Ej: ('A','S') → 'ace_of_spades.png', ('10','H') → '10_of_hearts.png'
    """
    v = _VALOR_MAP.get(str(valor), str(valor).lower())
    p = _PALO_MAP.get(str(palo), str(palo).lower())
    return f"{v}_of_{p}.png"

def _ensure_cards_dir():
    os.makedirs(os.path.join('imagenes', 'cards'), exist_ok=True)

def _download_card_bg(key, filename):
    """Descarga una imagen de carta en segundo plano."""
    if key in _card_img_cache:
        _card_img_downloading.discard(key); return
    _ensure_cards_dir()
    local_path = os.path.join('imagenes', 'cards', filename)
    if not os.path.exists(local_path):
        try:
            url = _CARDS_BASE_URL + filename
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            with open(local_path, 'wb') as f:
                f.write(data)
        except Exception as e:
            print(f"[CARD] Error descargando {filename}: {e}")
            _card_img_cache[key] = None
            _card_img_downloading.discard(key); return
    try:
        img = pygame.image.load(local_path).convert_alpha()
        _card_img_cache[key] = img
    except Exception as e:
        print(f"[CARD] Error cargando {filename}: {e}")
        _card_img_cache[key] = None
    _card_img_downloading.discard(key)

def get_card_image(valor, palo):
    """Devuelve Surface de la carta descargada, o None si no está lista."""
    key = f"{valor}{palo}"
    if key in _card_img_cache:
        return _card_img_cache[key]
    if key not in _card_img_downloading:
        _card_img_downloading.add(key)
        filename = _card_filename(valor, palo)
        t = threading.Thread(target=_download_card_bg, args=(key, filename), daemon=True)
        t.start()
    return None

def get_card_back_image():
    """Devuelve Surface del reverso descargado, o None si no está listo."""
    key = "__back__"
    if key in _card_img_cache:
        return _card_img_cache[key]
    if key not in _card_img_downloading:
        _card_img_downloading.add(key)
        t = threading.Thread(target=_download_card_bg, args=(key, "back.png"), daemon=True)
        t.start()
    return None

_MUSIC_URL   = "https://raw.githubusercontent.com/humrand/blackjack-python/main/music/coffee%20time.mp3"
_MUSIC_LOCAL = os.path.join("music", "coffee_time.mp3")
_music_ready = False
_music_volume = 0.18   
music_muted  = False
_music_context = None

def eff_vol(base_volume):
    """Aplica el multiplicador de volumen de ajustes y el mute al volumen base."""
    if music_muted:
        return 0.0
    mult = CONFIG.get('volume', 0.75) if 'CONFIG' in globals() else 0.75
    return max(0.0, min(1.0, base_volume * mult))

def _apply_live_volume():
    """Aplica el volumen actual a la musica que este sonando en ese momento."""
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(eff_vol(_music_volume))
        if _SFX_CHANNEL:
            _SFX_CHANNEL.set_volume(eff_vol(_story_sfx_volume))
    except Exception:
        pass

def _download_and_start_music():
    """Descarga la música en segundo plano y la arranca en bucle."""
    global _music_ready, _music_context
    os.makedirs("music", exist_ok=True)
    if not os.path.exists(_MUSIC_LOCAL):
        try:
            req = urllib.request.Request(_MUSIC_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            with open(_MUSIC_LOCAL, 'wb') as f:
                f.write(data)
        except Exception as e:
            print(f"[MUSIC] Error descargando música: {e}"); return
    try:
        pygame.mixer.music.load(_MUSIC_LOCAL)
        pygame.mixer.music.set_volume(eff_vol(_music_volume))
        pygame.mixer.music.play(-1)
        _music_ready = True
        _music_context = 'menu'
    except Exception as e:
        print(f"[MUSIC] Error cargando música: {e}")

def toggle_mute():
    global music_muted
    music_muted = not music_muted
    if music_muted:
        pygame.mixer.music.set_volume(0.0)
        if _SFX_CHANNEL:
            _SFX_CHANNEL.set_volume(0.0)
    else:
        pygame.mixer.music.set_volume(eff_vol(_music_volume))
        if _SFX_CHANNEL:
            _SFX_CHANNEL.set_volume(eff_vol(_story_sfx_volume))


_STORY_MUSIC_FILES = {
    'lluvia':  (os.path.join('music', 'sounds-storymode', 'lluvia.mp3'),
                'https://raw.githubusercontent.com/humrand/blackjack-python/main/music/sounds-storymode/lluvia.mp3'),
    'jazz':    (os.path.join('music', 'sounds-storymode', 'jazz.mp3'),
                'https://raw.githubusercontent.com/humrand/blackjack-python/main/music/sounds-storymode/jazz.mp3'),
    'coffee':  (os.path.join('music', 'coffee_time.mp3'),
                'https://raw.githubusercontent.com/humrand/blackjack-python/main/music/coffee%20time.mp3'),
}
_STORY_SFX_FILES = {
    'chips':   (os.path.join('music', 'sounds-storymode', 'chips.mp3'),
                'https://raw.githubusercontent.com/humrand/blackjack-python/main/music/sounds-storymode/chips.mp3'),
}
_story_sfx_cache      = {}
_story_current_track  = None
_SFX_CHANNEL          = None
_story_sfx_volume     = 0.22  


def _story_download_file(local_path, url):
    """Descarga un archivo de audio si no existe localmente."""
    if os.path.exists(local_path):
        return True
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = resp.read()
        with open(local_path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"[STORYMUSIC] Error descargando {os.path.basename(local_path)}: {e}")
        return False


def _play_story_track(key, volume=0.15, loop=True, fade_out_ms=1800):
    """Cambia la pista de fondo del modo historia con fade-out de la anterior."""
    global _story_current_track, _music_context
    if _story_current_track == key:
        return
    _story_current_track = key
    if key not in _STORY_MUSIC_FILES:
        return
    local_path, url = _STORY_MUSIC_FILES[key]

    def _do_play():
        global _music_context
        import time
        if not _story_download_file(local_path, url):
            return
        try:
            pygame.mixer.music.fadeout(fade_out_ms)
            time.sleep(fade_out_ms / 1000.0 + 0.15)
            pygame.mixer.music.load(local_path)
            pygame.mixer.music.set_volume(0.0)
            pygame.mixer.music.play(-1 if loop else 0)
            _music_context = 'story'
            if not music_muted:
                steps = 25
                for i in range(steps):
                    pygame.mixer.music.set_volume(eff_vol(volume) * (i + 1) / steps)
                    time.sleep(0.04)
                pygame.mixer.music.set_volume(eff_vol(volume))
        except Exception as e:
            print(f"[STORYMUSIC] Error reproduciendo '{key}': {e}")

    threading.Thread(target=_do_play, daemon=True).start()


def _play_story_sfx(key, volume=0.22):
    """Reproduce un efecto de sonido en canal secundario sin cortar la música."""
    global _SFX_CHANNEL, _story_sfx_cache, _story_sfx_volume
    _story_sfx_volume = volume
    if key not in _STORY_SFX_FILES:
        return

    def _do_sfx():
        global _SFX_CHANNEL, _story_sfx_cache
        local_path, url = _STORY_SFX_FILES[key]
        if not _story_download_file(local_path, url):
            return
        if key not in _story_sfx_cache:
            try:
                _story_sfx_cache[key] = pygame.mixer.Sound(local_path)
            except Exception as e:
                print(f"[STORYSFX] Error cargando '{key}': {e}")
                return
        snd = _story_sfx_cache[key]
        snd.set_volume(eff_vol(volume))
        channel = pygame.mixer.find_channel(True)
        if channel:
            channel.play(snd)

    threading.Thread(target=_do_sfx, daemon=True).start()


import array as _tw_arr

_VOICE_FREQS = {
    'narrador': 255,
    'Rosa':     530,
    'Camarera': 530,
    'Portero':  155,
    'Bruno':    155,
    'Víctor':   305,
    'Tú':       415,
}
_voice_sounds  = {} 
_voice_channel = None

def _make_voice_sound(freq=400):
    """Genera tono corto tipo Undertale sin numpy."""
    try:
        mfreq, msize, mch = pygame.mixer.get_init()
        dur_ms = 44
        n      = int(mfreq * dur_ms / 1000)
        maxval = (1 << (abs(msize) - 1)) - 1
        tc     = 'h' if abs(msize) >= 16 else 'b'
        buf    = _tw_arr.array(tc)
        for i in range(n):
            env  = (1.0 - i / n) ** 0.55
            samp = int(maxval * 0.21 * env *
                       math.sin(2 * math.pi * freq * i / mfreq))
            if mch == 2:
                buf.append(samp); buf.append(samp)
            else:
                buf.append(samp)
        return pygame.mixer.Sound(buffer=buf)
    except Exception as e:
        print(f"[TW] Error sintetizando voz: {e}")
        return None

def _get_voice_sound(speaker):
    freq = _VOICE_FREQS.get(speaker, 380)
    if freq not in _voice_sounds:
        _voice_sounds[freq] = _make_voice_sound(freq)
    return _voice_sounds[freq]

_tw = {
    'speaker':    None,
    'text':       '',
    'shown':      0,
    'done':       False,
    'last_t':     0,
    'next_delay': 0,
}

def _tw_char_delay(text, idx):
    """Retardo aleatorio hasta el siguiente carácter."""
    if idx <= 0 or idx > len(text):
        return random_module.randint(30, 72)
    prev = text[idx - 1]
    if prev in '.!?…':  return random_module.randint(210, 400)
    if prev in ',;:–—': return random_module.randint(85, 155)
    if prev == ' ':     return random_module.randint(8, 28)
    return random_module.randint(26, 78)

def _tw_set(speaker, text, now):
    """Inicializa el typewriter para un nuevo parlamento."""
    global _tw
    _tw['speaker']    = speaker
    _tw['text']       = text
    _tw['shown']      = 0
    _tw['done']       = len(text) == 0
    _tw['last_t']     = now
    _tw['next_delay'] = _tw_char_delay(text, 0)

def _tw_update(now):
    """Avanza el typewriter y emite el sonido de voz por letra."""
    global _tw, _voice_channel
    if _tw['done']:
        return
    elapsed = now - _tw['last_t']
    while elapsed >= _tw['next_delay'] and not _tw['done']:
        elapsed        -= _tw['next_delay']
        _tw['shown']   += 1
        _tw['last_t']   = now - elapsed
        if _tw['shown'] >= len(_tw['text']):
            _tw['shown'] = len(_tw['text'])
            _tw['done']  = True
            break
        ch = _tw['text'][_tw['shown'] - 1]
        if ch.isalpha() and not music_muted:
            snd = _get_voice_sound(_tw['speaker'])
            if snd:
                if _voice_channel is None or not _voice_channel.get_busy():
                    _voice_channel = pygame.mixer.find_channel(False)
                if _voice_channel:
                    _voice_channel.play(snd)
        _tw['next_delay'] = _tw_char_delay(_tw['text'], _tw['shown'])

def _tw_finish():
    """Revela el texto completo al instante."""
    global _tw
    _tw['shown'] = len(_tw['text'])
    _tw['done']  = True


def _story_check_music_for_scene(scenes_data, scene_idx):
    """Lanza la música correcta según la escena actual del modo historia."""
    if scene_idx >= len(scenes_data):
        return
    scene = scenes_data[scene_idx]
    img   = scene.get('scene_image', '')

    if img in ('victor2', 'victor3', 'victor4', 'victor5'):
        _play_story_track('coffee', volume=0.13, loop=True, fade_out_ms=1500)
    elif img in ('rosita', 'rosita-seria', 'rosita-guino', 'rosita-caos',
                 'rosita-dedo', 'rosita-fichas'):
        _play_story_track('jazz', volume=0.11, loop=True, fade_out_ms=1600)

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

_story_scaled_cache = {}

def draw_story_image(key, surf):
    """Dibuja la imagen de escena a pantalla completa."""
    img = get_story_image(key)
    if img is None:
        return
    cache_key = (key, ANCHO, ALTO)
    cached = _story_scaled_cache.get(cache_key)
    if cached is None:
        iw, ih = img.get_size()
        scale  = max(ANCHO / iw, ALTO / ih)
        new_w  = int(iw * scale)
        new_h  = int(ih * scale)
        scaled = pygame.transform.smoothscale(img, (new_w, new_h))
        x = (ANCHO - new_w) // 2
        y = (ALTO  - new_h) // 2
        cached = (scaled, x, y)
        _story_scaled_cache[cache_key] = cached
    surf.blit(cached[0], (cached[1], cached[2]))


ANCHO, ALTO = _RESOLUTIONS.get(CONFIG.get('resolution', '1920x1080'), (1920, 1080))
IS_WINDOWED = (CONFIG.get('resolution') == 'windowed')
if IS_WINDOWED:
    ANCHO, ALTO = 1280, 720

_dinfo = pygame.display.Info()
SCREEN_W = _dinfo.current_w
SCREEN_H = _dinfo.current_h
_display_flags = pygame.SCALED if IS_WINDOWED else (pygame.FULLSCREEN | pygame.SCALED)
VENTANA_REAL = pygame.display.set_mode((ANCHO, ALTO), _display_flags)
pygame.display.set_caption("Blackjack – El Farol Rojo")

VENTANA = pygame.Surface((ANCHO, ALTO))


def to_logical(pos):
    return (int(pos[0]), int(pos[1]))


def _safe_render(font, text, aa, color, fallback_text=None):
    """
    Renderiza texto con una fuente evitando el crash
    'pygame.error: Text has zero width'.

    Ese error salta cuando la fuente elegida (p.ej. Arial en Windows/Wine)
    no tiene ningun glifo para alguno de los caracteres del texto (típico
    con emojis como 📁 🎰 💰 en plataformas donde no hay una fuente de
    emoji instalada). En vez de crashear, probamos con un texto alternativo
    y, si tampoco funciona, nos quedamos solo con los caracteres ASCII.
    """
    try:
        surf = font.render(text, aa, color)
        if surf.get_width() > 0:
            return surf
    except pygame.error:
        pass

    if fallback_text is not None:
        try:
            surf = font.render(fallback_text, aa, color)
            if surf.get_width() > 0:
                return surf
        except pygame.error:
            pass

    stripped = "".join(c for c in text if 32 <= ord(c) < 127) or " "
    try:
        surf = font.render(stripped, aa, color)
        if surf.get_width() > 0:
            return surf
    except pygame.error:
        pass

    return font.render(" ", aa, color)


def flip_display():
    VENTANA_REAL.blit(VENTANA, (0, 0))
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

DEALER_CARD_Y  = 140    
PLAYER_CARD_Y  = 550    

_CARD_X_ORIGIN = ANCHO // 2 - CARD_SPACING // 2 - CARD_W // 2  

_gameboy_win_snd  = None
_gameboy_lose_snd = None
_gameboy_channel  = None

def _make_gameboy_sound(notes_freqs, note_ms=85):
    """Genera un jingle estilo GameBoy (onda cuadrada) sin numpy."""
    import array as _arr
    try:
        mfreq, msize, mch = pygame.mixer.get_init()
        maxval = (1 << (abs(msize) - 1)) - 1
        tc = 'h' if abs(msize) >= 16 else 'b'
        buf = _arr.array(tc)
        for i, (freq, dur_ms) in enumerate(notes_freqs):
            n = int(mfreq * dur_ms / 1000)
            for s in range(n):
                env = max(0.0, 1.0 - s / n)
                period = mfreq / max(freq, 1)
                phase = (s % max(1, int(period))) / max(1, period)
                wave = maxval if phase < 0.5 else -maxval
                samp = int(wave * 0.35 * env)
                if mch == 2:
                    buf.append(samp); buf.append(samp)
                else:
                    buf.append(samp)
        return pygame.mixer.Sound(buffer=buf)
    except Exception as e:
        print(f"[GAMEBOY] Error: {e}"); return None

def _init_gameboy_sounds():
    global _gameboy_win_snd, _gameboy_lose_snd
    win_notes  = [(523,90),(659,90),(784,90),(1047,200)]  
    lose_notes = [(392,90),(330,90),(262,200)]             
    _gameboy_win_snd  = _make_gameboy_sound(win_notes)
    _gameboy_lose_snd = _make_gameboy_sound(lose_notes)

threading.Thread(target=_init_gameboy_sounds, daemon=True).start()

def _play_gameboy(win=True):
    global _gameboy_channel
    if music_muted: return
    snd = _gameboy_win_snd if win else _gameboy_lose_snd
    if snd is None: return
    ch = pygame.mixer.find_channel(True)
    if ch:
        _gameboy_channel = ch
        ch.play(snd)

difficulty_level   = 0
rosa_secret_done   = False
rosa_kicked        = False

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
_RAIN_SURF_CACHE = {}

def _get_rain_surf(length, alpha):
    key = (int(length), int(alpha))
    surf = _RAIN_SURF_CACHE.get(key)
    if surf is None:
        surf = pygame.Surface((2, int(length)), pygame.SRCALPHA)
        surf.fill((160, 195, 235, int(alpha)))
        _RAIN_SURF_CACHE[key] = surf
    return surf


def draw_rain(surf, now, alpha=100):
    t = now / 1000.0
    alpha = int(alpha)
    for bx, by, sp, ln in _RAIN:
        y = (by + t * sp) % (ALTO + 60)
        x = int(bx + y * 0.17) % ANCHO
        surf.blit(_get_rain_surf(ln, alpha), (x, int(y)))


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
        self._front_from_img = False
        self._back_from_img = False
        self._scaled_cache = {}
        self._flip_cache = {}
        self._create_faces()

    def _create_faces(self):
        self.front = self.crear_front()
        self.back  = self.crear_back()

    def crear_front(self):
        img = get_card_image(self.valor, self.palo)
        if img is not None:
            self._front_from_img = True
            return pygame.transform.smoothscale(img, (self.w, self.h))
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
            simple = FUENTE_GRANDE.render(self.valor, True, self.color) if self.valor in FACE_SYMBOL_MAP                      else FUENTE_PEQUENA.render(self.palo, True, self.color)
            surf.blit(simple, ((self.w-simple.get_width())//2, (self.h-simple.get_height())//2))
        return surf

    def crear_back(self):
        img = get_card_back_image()
        if img is not None:
            self._back_from_img = True
            return pygame.transform.smoothscale(img, (self.w, self.h))
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (150,0,0), (0,0,self.w,self.h), border_radius=12)
        pygame.draw.rect(surf, NEGRO,     (0,0,self.w,self.h), 2, border_radius=12)
        for i in range(12, self.w-12, 20):
            for j in range(12, self.h-12, 24):
                pygame.draw.circle(surf, (220,70,70), (i,j), 5)
        return surf

    def _scaled_face(self, face_name, surf):
        key = (face_name, int(round(self.scale * 1000)))
        cached = self._scaled_cache.get(key)
        if cached is None:
            nw = max(1, int(self.w * self.scale))
            nh = max(1, int(self.h * self.scale))
            if nw == self.w and nh == self.h:
                cached = surf
            else:
                cached = pygame.transform.smoothscale(surf, (nw, nh))
            self._scaled_cache[key] = cached
        return cached

    def start_flip(self, now, to_back=False):
        if not self.flipping:
            self.flipping = True; self.flip_start = now
            self.flip_target_back = bool(to_back)

    def actualizar(self, now):
        if not self._front_from_img:
            img = get_card_image(self.valor, self.palo)
            if img is not None:
                self.front = pygame.transform.smoothscale(img, (self.w, self.h))
                self._front_from_img = True
        if not self._back_from_img:
            img = get_card_back_image()
            if img is not None:
                self.back = pygame.transform.smoothscale(img, (self.w, self.h))
                self._back_from_img = True
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
            scaled = self._scaled_face('back' if self.oculta else 'front', surf_to_blit)
            nw, nh = scaled.get_size()
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
            scaled = self._scaled_face('back' if self.oculta else 'front', surf_to_blit)
            nw, nh = scaled.get_size()
            VENTANA.blit(scaled, (rx-(nw-self.w)//2, ry-(nh-self.h)//2))
            return

        if self.flip_target_back:
            escala = (1-progreso*2) if progreso < 0.5 else ((progreso-0.5)*2)
            surf = self.front if progreso < 0.5 else self.back
            face_name = 'front' if progreso < 0.5 else 'back'
        else:
            escala = (1-progreso*2) if progreso < 0.5 else ((progreso-0.5)*2)
            surf = self.back if progreso < 0.5 else self.front
            face_name = 'back' if progreso < 0.5 else 'front'

        ancho = max(1, int(self.w * escala))
        h_final = max(1, int(self.h * self.scale))
        scale_key = (face_name, ancho, h_final)
        scaled = self._flip_cache.get(scale_key)
        if scaled is None:
            scaled = pygame.transform.smoothscale(surf, (ancho, h_final))
            self._flip_cache[scale_key] = scaled
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
    sign_s = _safe_render(FUENTE_PEQUENA, "★  EL FAROL ROJO  ★", True, sc2, fallback_text="EL FAROL ROJO")
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
    disp_text = S(text)
    if _tw['speaker'] != speaker or _tw['text'] != disp_text:
        _tw_set(speaker, disp_text, now)
    _tw_update(now)
    displayed = disp_text[:_tw['shown']]

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
        name_s = FUENTE_NAME.render(S_SPEAKER(speaker), True, sc2)
        surf.blit(name_s, (PAD, BOX_Y + 18))
        text_y = BOX_Y + 18 + name_s.get_height() + 6
    max_w2 = ANCHO - PAD * 2
    lines2 = wrap_story(displayed, FUENTE_STORY, max_w2)
    txt_col = (195,195,195) if narrador_mode else BLANCO
    for i, line in enumerate(lines2[:4]):
        ls = FUENTE_STORY.render(line, True, txt_col)
        surf.blit(ls, (PAD, text_y + i*34))
    if _tw['done'] and (now // 550) % 2 == 0:
        cont = FUENTE_INSTR.render(TR('story_continue'), True, (125,112,88))
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
    header = FUENTE_NAME.render(TR('story_choice_header'), True, sc)
    surf.blit(header, (PAD_X, BOX_Y + 12))

    hint = FUENTE_INSTR.render(TR('story_choice_hint'), True, (100, 90, 70))
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

        txt_col = (210, 255, 220) if hovered else BLANCO
        txt     = FUENTE_STORY.render(S(opt['label']), True, txt_col)
        surf.blit(txt, (PAD_X + 22, btn_y + (BTN_H - txt.get_height()) // 2))

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
                    'reaction_images': [
                        None,
                        'rosita-dedo',
                        'cuarto-oscuro',
                        'cuarto-oscuro',
                        'rosita',
                        'rosita',
                        'rosita',
                        'rosita',
                        'rosita-fichas',
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
            ('CHOICE', [
                {
                    'label': '"Gracias por el consejo, Rosa. Esta noche me traerá suerte."',
                    'tu_text': 'Gracias por los consejos, Rosa. Esta noche me traerán suerte.',
                    'reactions': [
                        ('Rosa', '(Asiente con una sonrisa tranquila.) Eso espero. Ya sé dónde encontrarte si ganas.'),
                    ],
                    'effect': {}
                },
                {
                    'label': '"Oye, ¿me acompañas tú a la mesa de suerte?"',
                    'tu_text': 'Oye, ¿y si me acompañas a la mesa esta noche? Serías mi amuleto de la suerte.',
                    'reactions': [
                        ('Rosa', '(Sonríe con paciencia.) Tengo trabajo. Y tú tienes una partida que ganar. Anda.'),
                    ],
                    'effect': {}
                },
                {
                    'label': '[Comportamiento inapropiado con Rosa — Final Malo]',
                    'tu_text': '...',
                    'reactions': [
                        ('narrador', 'Algo en tu actitud cruza una línea que no debería haberse cruzado.'),
                        ('Rosa', '(Te mira fijamente. Después levanta la mano hacia el fondo de la sala.) Marcos.'),
                        ('narrador', 'El hombre más grande que has visto en tu vida emerge de las sombras.'),
                        ('Portero', '¿Algún problema, Rosa?'),
                        ('Rosa', '(Sin apartar los ojos de ti.) Este señor ya se iba.'),
                    ],
                    'reaction_images': [
                        None, 'rosita-seria', 'segurata-pierdes', 'segurata-pierdes', 'rosita-seria',
                    ],
                    'effect': {'segurata_expulsion': True}
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
            ('narrador', 'A mitad de la calle oyes pasos rápidos detrás de ti.'),
            ('Rosa', '(Sin aliento.) ¡Espera!'),
            ('narrador', 'Rosa lleva el abrigo a medio poner y una botella de champán robada al bar bajo el brazo.'),
            ('Tú', '¿No deberías estar trabajando?'),
            ('Rosa', '(Sonriendo.) Esta noche no. Esta noche yo también me voy.'),
            ('narrador', 'Le das la mano sin decir nada. Ella no la suelta.'),
            ('Rosa', 'Sabía que lo conseguirías. Lo sabía desde el principio.'),
            ('Tú', 'No me lo creía ni yo.'),
            ('Rosa', '(Levanta la botella.) ¿Celebramos?'),
            ('narrador', 'El corcho sale disparado y rebota contra los adoquines mojados. Rosa ríe — alto, sin disimulo, como si la ciudad entera necesitara saberlo.'),
            ('narrador', 'Es la primera vez en mucho tiempo que oyes reír así a alguien.'),
            ('narrador', 'Los dos caminan hacia el mar. El champán se enfría con la brisa. El neón de El Farol Rojo se apaga para siempre detrás.'),
        ]

    d = difficulty_level

    if d == 0:
        table_scenes = [
            {
                'bg': 'table', 'chars': [('victor_nervioso', ANCHO//2+210, 730)], 'counter': False,
                'scene_image': 'victor3',
                'line_images': [None, None, None, None, None, None, None, 'victor4'],
                'lines': [
                    ('narrador', 'Diez mil fichas. La mesa entera se queda en silencio.'),
                    ('Víctor', '...'),
                    ('Víctor', '¿Cómo?'),
                    ('Tú', 'Ya sabes lo que acordamos, Víctor.'),
                    ('Víctor', '(Una pausa larga. Sus ojos te estudian.) ...Bien.'),
                    ('Víctor', '(En voz baja, casi solo para ti.) El segundo crupier de la derecha. Lleva cuatro años marcando las cartas con la uña.'),
                    ('Víctor', 'Nunca esperé tener que decirlo. Nunca.'),
                    ('Tú', 'Lo sé. Gracias por cumplir tu palabra.'),
                ]
            },
            {
                'bg': 'bar', 'chars': [('camarera', ANCHO//2-180, 770)], 'counter': True,
                'scene_image': 'rosita-caos',
                'line_images': [None, None, None, None, None, None, None, None, 'rosita-guino'],
                'lines': [
                    ('narrador', 'Al salir, el susurro ya recorre la sala.'),
                    ('narrador', 'El hombre que hizo hablar a Víctor Carvalho.'),
                    ('narrador', 'Rosa te espera junto a la barra con una sonrisa que no intenta esconder.'),
                    ('Rosa', '(En voz baja.) ¿Te lo dijo?'),
                    ('Tú', 'Me lo dijo.'),
                    ('Rosa', '(Larga pausa.) Bien. Ya era hora.'),
                    ('narrador', 'Dos grandes se levantan, pero Víctor los detiene con un gesto. Esta vez, la puerta es tuya.'),
                    ('Portero', '(Abre la puerta sin decir nada.)'),
                    ('Rosa', '(Te guiña un ojo desde el otro lado de la sala.)'),
                ]
            },
        ]
        dawn_lines = [
            ('narrador', 'El aire de la madrugada huele a lluvia limpia. A libertad.'),
            ('narrador', 'Caminas despacio por los adoquines mojados.'),
            ('narrador', 'Detrás de ti, el neón de "El Farol Rojo" parpadea dos veces y se apaga.'),
            ('narrador', 'Lo lograste en modo Normal. Víctor nunca imaginó que alguien le haría hablar.'),
            ('narrador', 'La ciudad empieza a despertar. Huele a café y a pan recién hecho.'),
        ] + rosa_lines + [('narrador', '─────────  FIN  ─────────')]

    elif d == 1:
        table_scenes = [
            {
                'bg': 'table', 'chars': [('victor_nervioso', ANCHO//2+210, 730)], 'counter': False,
                'scene_image': 'victor3',
                'line_images': [None, None, None, None, None, None, 'victor4'],
                'lines': [
                    ('narrador', 'Veinticinco mil fichas. La sala entera lo vio.'),
                    ('narrador', 'El murmullo empieza en las mesas de los laterales y viaja hasta el fondo.'),
                    ('Víctor', '(Se pone de pie lentamente.) ¡Trampa! ¡Este hombre ha hecho trampa!'),
                    ('Tú', 'Las cartas no mienten, Víctor. Toda la sala lo vio.'),
                    ('narrador', 'Un crupier anciano al fondo suelta las cartas sobre la mesa y mueve la cabeza.'),
                    ('narrador', 'Él también lo sabe. Todos lo saben.'),
                    ('Víctor', '(Su voz pierde fuerza.) ...Garduño. Enrique.'),
                ]
            },
            {
                'bg': 'bar', 'chars': [('camarera', ANCHO//2-180, 770)], 'counter': True,
                'scene_image': 'rosita-caos',
                'line_images': [None, None, None, None, None, None, None, 'rosita-guino'],
                'lines': [
                    ('narrador', 'Los dos hombres se levantan, pero el ambiente ya se giró.'),
                    ('narrador', 'Tres jugadores de las otras mesas se ponen de pie entre tú y ellos.'),
                    ('narrador', 'Nadie dice nada. No hace falta.'),
                    ('Rosa', '¡Ay, Dios mío, qué torpe!'),
                    ('narrador', 'Rosa vuelca la barra entera. Cristales, botellas, caos total.'),
                    ('narrador', 'En medio del tumulto, tú caminas tranquilamente hacia la puerta.'),
                    ('Portero', '(Te sostiene la puerta abierta. Con respeto.)'),
                    ('Rosa', '(Te guiña un ojo desde el otro lado del caos.)'),
                ]
            },
        ]
        dawn_lines = [
            ('narrador', 'El aire de la madrugada tiene sabor a victoria.'),
            ('narrador', 'No solo la tuya. La de todos los que perdieron antes que tú.'),
            ('narrador', 'Detrás de ti, el neón de "El Farol Rojo" parpadea y se apaga.'),
            ('narrador', 'Lo lograste en modo Difícil. La banca jugó sin piedad y aun así no fue suficiente.'),
            ('narrador', 'Veinticinco mil fichas. Una hazaña que el Barrio Gótico no olvidará.'),
        ] + rosa_lines + [('narrador', '─────────  FIN  ─────────')]

    elif d == 2:
        table_scenes = [
            {
                'bg': 'table', 'chars': [('victor_nervioso', ANCHO//2+210, 730)], 'counter': False,
                'scene_image': 'victor3',
                'line_images': [None, None, None, None, None, 'victor4', None],
                'lines': [
                    ('narrador', 'Cincuenta mil fichas. Nadie en esta sala creyó que fuera posible.'),
                    ('narrador', 'Ni siquiera tú, en el fondo.'),
                    ('Víctor', '(Volcando la silla.) ¡Imposible! ¡Imposible, digo!'),
                    ('Tú', 'Este casino es mío. En espíritu. Y tú lo sabes.'),
                    ('Víctor', '(Mira hacia la puerta trasera. Calcula.)'),
                    ('narrador', 'Pero los crupiers se pusieron de pie. Rosa bloqueó la barra. Hasta Marcos, el portero, dio un paso al lado.'),
                    ('Víctor', '(En voz muy baja, solo para ti.) ...¿Cómo lo hiciste?'),
                ]
            },
            {
                'bg': 'bar', 'chars': [('camarera', ANCHO//2-180, 770)], 'counter': True,
                'scene_image': 'rosita-caos',
                'line_images': [None, None, None, None, None, None, 'rosita-guino'],
                'lines': [
                    ('narrador', 'La sala entera te abre paso. No como a un ganador. Como a alguien que tiene razón.'),
                    ('Rosa', '(Con voz firme.) Esta noche, el Farol Rojo tiene un nuevo campeón.'),
                    ('narrador', 'Aplausos. Lentos al principio. Luego toda la sala.'),
                    ('narrador', 'Víctor observa desde el fondo, solo, con las manos vacías.'),
                    ('narrador', 'Cincuenta años de impunidad terminaron esta noche.'),
                    ('Portero', '(Te abre la puerta principal con las dos manos.)'),
                    ('Rosa', '(Te guiña un ojo. Hay algo diferente en su cara — parece libre.)'),
                ]
            },
        ]
        dawn_lines = [
            ('narrador', 'La madrugada de Barcelona te recibe como a un fantasma victorioso.'),
            ('narrador', 'Detrás de ti, "El Farol Rojo" parpadea y se apaga para siempre.'),
            ('narrador', 'Lo lograste en modo Muy Difícil. Cincuenta mil fichas. Una hazaña que nadie olvidará.'),
            ('narrador', 'El Barrio Gótico guarda secretos. Esta noche guarda uno más: el tuyo.'),
        ] + rosa_lines + [('narrador', '─────────  FIN  ─────────')]

    else:
        table_scenes = [
            {
                'bg': 'table', 'chars': [('victor_nervioso', ANCHO//2+210, 730)], 'counter': False,
                'scene_image': 'victor3',
                'line_images': [None, None, None, None, None, None, 'victor4', None],
                'lines': [
                    ('narrador', 'Cien mil fichas.'),
                    ('narrador', 'El número imposible. El que nadie se atrevió a perseguir en tres años.'),
                    ('narrador', 'El aire se detuvo. La música se detuvo. Todo se detuvo.'),
                    ('Víctor', '(En pie. La cara descompuesta.) No... no puede ser...'),
                    ('Tú', 'Ya lo es, Víctor. Ya lo es.'),
                    ('Víctor', '(Las manos le tiemblan. Por primera vez en su vida, tiemblan.)'),
                    ('narrador', 'Nadie en la sala se mueve. El hombre que nunca perdió acaba de perderlo todo.'),
                    ('Víctor', '(En un susurro.) ...¿Quién eres tú?'),
                ]
            },
            {
                'bg': 'bar', 'chars': [('camarera', ANCHO//2-180, 770)], 'counter': True,
                'scene_image': 'rosita-caos',
                'line_images': [None, None, None, None, None, None, None, 'rosita-guino'],
                'lines': [
                    ('narrador', 'Los dos matones no se mueven. Nadie se mueve.'),
                    ('narrador', 'Hay cosas que el dinero no puede detener, y esta noche todo el mundo lo siente.'),
                    ('Rosa', '(Deja caer el vaso que estaba limpiando. Se acerca despacio.)'),
                    ('Rosa', 'Tres años trabajando para ese hombre. Tres años esperando esto.'),
                    ('narrador', 'Rosa vuelca la barra entera. Un diluvio de cristal y whisky caro.'),
                    ('narrador', 'En el caos absoluto, tú caminas hacia la puerta con calma de cirujano.'),
                    ('Portero', '(Se hace a un lado. Asiente una sola vez.)'),
                    ('Rosa', '(Te guiña un ojo desde el otro lado del infierno.)'),
                ]
            },
        ]
        dawn_lines = [
            ('narrador', 'Afuera, la ciudad respira.'),
            ('narrador', 'Cien mil fichas. El número que nadie pronunció jamás en El Farol Rojo.'),
            ('narrador', 'Hasta esta noche.'),
            ('narrador', 'Detrás de ti, el neón parpadea tres veces y se apaga para siempre. Ya no volverá a encenderse.'),
            ('narrador', 'Lo lograste en modo EXTREMO. Cien mil fichas. Ni Víctor mismo se lo creerá jamás.'),
            ('narrador', 'Hay cosas que no se explican. Tú eres una de ellas.'),
        ] + rosa_lines + [('narrador', '─────────  FIN  ─────────')]

    return table_scenes + [
        {
            'bg': 'street_dawn', 'chars': [], 'counter': False,
            'scene_image': 'barcelona',
            'lines': dawn_lines,
        },
    ]

_RESTART_CHOICE = ('CHOICE', [
    {
        'label': 'Volver a intentarlo — esta vez será diferente.',
        'tu_text': 'No. Todavía no. Esta noche no ha terminado.',
        'reactions': [],
        'effect': {'restart_game': True}
    },
    {
        'label': 'Volver al menú principal.',
        'tu_text': '...',
        'reactions': [],
        'effect': {'go_menu': True}
    },
])

KICKED_ENDING_SCENES = [
    {
        'bg': 'bar', 'chars': [('portero', ANCHO//2+300, 760)], 'counter': True,
        'scene_image': 'segurata-pierdes',
        'lines': [
            ('narrador', 'Marcos no te da tiempo a reaccionar. Dos manos del tamaño de jamones te agarran por los hombros.'),
            ('Portero', 'Fin de la noche, amigo.'),
            ('Tú', '¡Espera, espera! Solo estaba...'),
            ('Portero', 'Ya lo he visto. Y ella también lo ha visto. Vamos.'),
            ('narrador', 'Cruzas la sala entera escoltado. Cada par de ojos se vuelve hacia ti. El silencio es peor que cualquier insulto.'),
            ('Rosa', '(Desde la barra, sin mirarte.) Buenas noches.'),
            ('narrador', 'No hay emoción en su voz. Solo distancia.'),
        ]
    },
    {
        'bg': 'street', 'chars': [], 'counter': False,
        'scene_image': 'farol-rojo',
        'lines': [
            ('narrador', 'La puerta se cierra detrás de ti con un golpe seco.'),
            ('narrador', 'El Barrio Gótico te devuelve el frío de siempre. La lluvia. Los adoquines mojados.'),
            ('narrador', 'No perdiste dinero en la mesa de Víctor. Ni siquiera llegaste a sentarte.'),
            ('narrador', 'Pero saliste igual de vacío.'),
            ('narrador', 'En algún lugar detrás de esa puerta, Rosa sigue trabajando. Sin pensar en ti.'),
            ('narrador', 'Algunas derrotas no tienen que ver con las cartas.'),
            ('narrador', '─────────  FINAL MALO  ─────────'),
            _RESTART_CHOICE,
        ]
    },
]

def build_lose_ending_scenes():
    """Construye las escenas de derrota según la dificultad actual."""
    d = difficulty_level

    if d == 0:
        table_lines = [
            ('narrador', 'Y así terminó.'),
            ('Víctor', 'Ya está. Eso es todo lo que tenías.'),
            ('Víctor', 'Ha sido... entretenido. Para mí.'),
            ('Tú', '...'),
            ('Víctor', '(Sin levantar la vista de las fichas.) La puerta está donde la dejaste. Buenas noches.'),
            ('narrador', 'No había nada más que decir.'),
        ]
        street_lines = [
            ('narrador', 'Volviste a la calle con los bolsillos vacíos y la cabeza llena de preguntas.'),
            ('narrador', 'La lluvia seguía ahí. Indiferente. Como siempre.'),
            ('narrador', 'Víctor seguía dentro, invicto. De momento.'),
            ('narrador', 'Pero el juego no había terminado. Solo esta ronda.'),
            ('narrador', 'Mañana es otro día. Y tú sabes dónde está la puerta.'),
            _RESTART_CHOICE,
        ]
    elif d == 1:
        table_lines = [
            ('narrador', 'Las fichas desaparecieron una a una. Cada mano, una pequeña muerte.'),
            ('Víctor', '(Con una sonrisa lenta.) Veinticinco mil... qué ambición tan hermosa.'),
            ('Víctor', 'Lástima que la ambición sin suerte no llegue muy lejos, ¿verdad?'),
            ('Tú', 'Las cartas no estuvieron de mi lado esta noche.'),
            ('Víctor', 'Las cartas nunca están de tu lado, forastero. Solo de la mía.'),
            ('narrador', 'Se recostó en la silla con la comodidad de alguien que nunca ha tenido que preocuparse.'),
        ]
        street_lines = [
            ('narrador', 'La noche te devuelve a los adoquines mojados del Barrio Gótico.'),
            ('narrador', 'Veinticinco mil fichas. Casi lo tocaste. Casi.'),
            ('narrador', 'Víctor sigue ahí dentro, intacto, con esa sonrisa que nunca se mueve del todo.'),
            ('narrador', 'Pero esta vez llegaste más lejos de lo que esperaba. Y lo sabe.'),
            _RESTART_CHOICE,
        ]
    elif d == 2:
        table_lines = [
            ('narrador', 'Cincuenta mil fichas. Nadie había llegado tan cerca. Nadie.'),
            ('narrador', 'Hasta hoy.'),
            ('Víctor', '(Frunciendo ligeramente el ceño.) Has aguantado más de lo esperado.'),
            ('Tú', 'Eso es porque sé lo que haces, Víctor.'),
            ('Víctor', '(Una pausa demasiado larga.) No sé de qué hablas. La suerte te ha abandonado. Eso es todo.'),
            ('narrador', 'Pero su voz tiene una grieta que antes no estaba ahí.'),
            ('Víctor', 'La puerta, forastero. Y esta vez... no tan tranquilo como antes.'),
        ]
        street_lines = [
            ('narrador', 'El frío de la madrugada te golpea en la cara.'),
            ('narrador', 'Cincuenta mil fichas. Estuviste a un suspiro de doblarle.'),
            ('narrador', 'Y Víctor lo sabe. Por primera vez en tres años, alguien le ha puesto nervioso.'),
            ('narrador', 'El Farol Rojo nunca volverá a ser del todo lo mismo.'),
            ('narrador', 'Ni tú tampoco.'),
            _RESTART_CHOICE,
        ]
    else:
        table_lines = [
            ('narrador', 'Cien mil fichas. Nadie había pronunciado esa cifra en este casino. Nadie la había perseguido.'),
            ('narrador', 'Hasta esta noche.'),
            ('Víctor', '(Se pone de pie. Algo en sus ojos cambió.)'),
            ('Víctor', 'Yo... no esperaba esto. En tres años, nadie...' ),
            ('Tú', 'Ya lo sé, Víctor. Y tú también lo sabes.'),
            ('narrador', 'Un silencio largo cae sobre la sala. Todos miran.'),
            ('Víctor', '(En voz muy baja.) La puerta. Y... vuelve cuando quieras.'),
            ('narrador', 'Es lo más cercano a respeto que Víctor Carvalho ha mostrado jamás.'),
        ]
        street_lines = [
            ('narrador', 'La ciudad todavía duerme. Aún no amanece.'),
            ('narrador', 'Cien mil fichas. Lo perseguiste hasta el borde del abismo y casi lo empujaste.'),
            ('narrador', 'Víctor sigue dentro. Pero algo se quebró esta noche en El Farol Rojo.'),
            ('narrador', 'Puedes sentirlo en el aire, como el olor a ozono antes de una tormenta.'),
            ('narrador', 'Este lugar nunca ha conocido a nadie como tú. Y ahora lo sabe.'),
            _RESTART_CHOICE,
        ]

    return [
        {
            'bg': 'table', 'chars': [('victor', ANCHO//2+210, 730)], 'counter': False,
            'scene_image': 'victor5',
            'lines': table_lines,
        },
        {
            'bg': 'street', 'chars': [], 'counter': False,
            'scene_image': 'segurata-pierdes',
            'lines': street_lines,
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
story_injected_lines  = []         
story_injected_images = []         
story_injected_idx    = 0          
story_in_injection    = False       

preload_images('farol-rojo', 'rosita', 'rosita-seria', 'victor2', 'victor3', 'victor4', 'victor5', 'rosita-caos', 'rosita-guino', 'barcelona', 'segurata-pierdes', 'rosita-dedo', 'cuarto-oscuro', 'rosita-fichas')


def _start_story(scenes, new_state):
    global story_scenes_data, story_scene_idx, story_line_idx, app_state
    story_scenes_data = scenes
    story_scene_idx   = 0
    story_line_idx    = 0
    app_state         = new_state


def _apply_choice(idx):
    """Aplica la elección del jugador: inyecta las reacciones y avanza la historia."""
    global story_choice_active, story_choice_options, story_choice_rects
    global story_injected_lines, story_injected_images, story_injected_idx, story_in_injection, player_money
    global difficulty_level, EPIC_WIN_THRESHOLD, rosa_secret_done, rosa_kicked, app_state

    opt    = story_choice_options[idx]
    effect = opt.get('effect', {})

    if effect.get('restart_game'):
        story_choice_active = False
        story_choice_options = []
        story_choice_rects = []
        _start_story_mode()
        return
    if effect.get('go_menu'):
        story_choice_active = False
        story_choice_options = []
        story_choice_rects = []
        app_state = 'main_menu'
        return

    if 'money' in effect:
        diff_multipliers = {0: 1.0, 1: 2.5, 2: 5.0, 3: 10.0}
        mult = diff_multipliers.get(difficulty_level, 1.0)
        scaled = int(effect['money'] * mult) if effect['money'] > 0 else effect['money']
        player_money = max(0, player_money + scaled)
    if 'difficulty' in effect:
        difficulty_level = effect['difficulty']
        thresholds = {0: 10000, 1: 25000, 2: 50000, 3: 100000}
        EPIC_WIN_THRESHOLD = thresholds.get(difficulty_level, 10000)
    if effect.get('rosa_secret'):
        rosa_secret_done = True
    if effect.get('segurata_expulsion'):
        rosa_kicked = True

    injected = []
    injected_imgs = []
    tu_text = opt.get('tu_text', '')
    if tu_text:
        injected.append(('Tú', tu_text))
        injected_imgs.append(None)
    reaction_images = opt.get('reaction_images', [])
    for i, line in enumerate(opt.get('reactions', [])):
        injected.append(line)
        img = reaction_images[i] if i < len(reaction_images) else None
        injected_imgs.append(img)

    story_choice_active  = False
    story_choice_options = []
    story_choice_rects   = []

    if injected:
        story_injected_lines  = injected
        story_injected_images = injected_imgs
        story_injected_idx    = 0
        story_in_injection    = True
    else:
        if rosa_kicked:
            _start_story(KICKED_ENDING_SCENES, 'kicked_ending')
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
        _story_check_music_for_scene(story_scenes_data, story_scene_idx)
        if story_scene_idx >= len(story_scenes_data):
            if app_state == 'intro':
                app_state = 'game'
                nueva_ronda()
            elif app_state == 'win_ending':
                pygame.quit(); sys.exit()
            elif app_state in ('lose_ending', 'kicked_ending'):
                pass


def _story_advance():
    global story_in_injection, story_injected_lines, story_injected_images, story_injected_idx
    global rosa_kicked

    if story_in_injection:
        story_injected_idx += 1
        if story_injected_idx >= len(story_injected_lines):
            story_in_injection    = False
            story_injected_lines  = []
            story_injected_images = []
            story_injected_idx    = 0
            if rosa_kicked:
                _start_story(KICKED_ENDING_SCENES, 'kicked_ending')
            else:
                _story_advance_scene()
        else:
            if (story_injected_idx < len(story_injected_images) and
                    story_injected_images[story_injected_idx] == 'rosita-fichas'):
                _play_story_sfx('chips', volume=0.20)
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
        inj_img = story_injected_images[story_injected_idx] if story_injected_idx < len(story_injected_images) else None
        img_key = inj_img if inj_img is not None else scene_img_key
    if img_key:
        draw_story_image(img_key, VENTANA)

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
            get_card_image(v, palo)
    get_card_back_image()
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
MUTE_BTN      = pygame.Rect(ANCHO-90,  8,   38,  28)

threading.Thread(target=_download_and_start_music, daemon=True).start()

nueva_ronda_pending = False
mensaje = ""

paused = False


def _sha256(path):
    import hashlib
    try:
        with open(path,"rb") as f: return hashlib.sha256(f.read()).hexdigest()
    except: return None

def _check_for_updates_source():
    """Auto-actualizador para cuando el juego corre como script .py normal.
    Descarga el .py más reciente de GitHub y lo compara/reemplaza por hash."""
    global update_status, update_msg, update_notif_time, update_restart_time
    import tempfile, time, json
    tmp_path = None
    try:

        api_url = GITHUB_API_URL + f"&_ts={int(time.time())}"
        api_req = urllib.request.Request(
            api_url,
            headers={
                "User-Agent":    "blackjack-updater/1.0",
                "Accept":        "application/vnd.github.v3+json",
                "Cache-Control": "no-cache, no-store",
                "Pragma":        "no-cache",
            }
        )
        commits    = json.loads(urllib.request.urlopen(api_req, timeout=12).read())
        if not commits:
            update_status = "error"; update_msg = TR('update_no_github')
            update_notif_time = pygame.time.get_ticks(); return
        latest_sha = commits[0].get('sha', '')

        saved_sha = ''
        if os.path.exists(_COMMIT_SHA_FILE):
            try:
                with open(_COMMIT_SHA_FILE, 'r') as f:
                    saved_sha = f.read().strip()
            except Exception:
                pass

        if latest_sha and latest_sha == saved_sha:
            update_status = "up_to_date"; update_msg = TR('update_uptodate')
            update_notif_time = pygame.time.get_ticks(); return

        raw_url = GITHUB_RAW_BASE.format(sha=latest_sha)
        raw_req = urllib.request.Request(
            raw_url,
            headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"}
        )
        remote_data = urllib.request.urlopen(raw_req, timeout=20).read()

        fd, tmp_path = tempfile.mkstemp(suffix=".py")
        with os.fdopen(fd, "wb") as f: f.write(remote_data)

        local_path = _SCRIPT_PATH
        sha_local  = _sha256(local_path)
        sha_remote = _sha256(tmp_path)

        if sha_remote is None:
            update_status = "error"; update_msg = TR('update_no_hash')
        elif sha_local == sha_remote:
            try:
                with open(_COMMIT_SHA_FILE, 'w') as f: f.write(latest_sha)
            except Exception: pass
            update_status = "up_to_date"; update_msg = TR('update_uptodate')
        else:
            try:
                import ast as _ast
                with open(tmp_path, 'r', encoding='utf-8', errors='replace') as f:
                    _src = f.read()
                _ast.parse(_src)
            except SyntaxError as _se:
                update_status = "error"
                update_msg = TRF('update_syntax_err', line=_se.lineno)
            except Exception as _e:
                update_status = "error"
                update_msg = TRF('update_verify_fail', err=str(_e)[:35])
            else:
                try:
                    shutil.copy2(tmp_path, local_path)
                    try:
                        with open(_COMMIT_SHA_FILE, 'w') as f: f.write(latest_sha)
                    except Exception: pass
                    update_status = "restarting"; update_msg = TR('update_restarting')
                    update_restart_time = pygame.time.get_ticks()
                except Exception as e:
                    update_status = "error"
                    update_msg = TRF('update_write_fail', err=str(e)[:40])
    except Exception as e:
        update_status = "error"; update_msg = TRF('update_error', err=str(e)[:55])
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try: os.unlink(tmp_path)
            except: pass
    update_notif_time = pygame.time.get_ticks()


def _release_asset_name():
    """Nombre del asset a buscar en el Release de GitHub según la plataforma."""
    if sys.platform == 'win32':
        return _RELEASE_ASSET_NAME_WINDOWS
    return _RELEASE_ASSET_NAME_LINUX


_pending_external_restart = False

def _schedule_windows_update_swap(new_path, target_path):
    """Programa (Windows) un script .bat desasociado que espera a que este
    proceso termine, sustituye el .exe antiguo por el nuevo y lo relanza.
    Necesario porque Windows no permite sobrescribir un .exe en ejecucion."""
    global _pending_external_restart
    try:
        pid = os.getpid()
        bat_fd, bat_path = tempfile.mkstemp(suffix=".bat", prefix="efr_update_")
        script = (
            "@echo off\r\n"
            ":wait\r\n"
            f"tasklist /FI \"PID eq {pid}\" 2>NUL | find \"{pid}\" >NUL\r\n"
            "if not errorlevel 1 (\r\n"
            "    timeout /t 1 /nobreak >nul\r\n"
            "    goto wait\r\n"
            ")\r\n"
            f"del /f /q \"{target_path}\"\r\n"
            f"move /y \"{new_path}\" \"{target_path}\"\r\n"
            f"start \"\" \"{target_path}\"\r\n"
            "del \"%~f0\"\r\n"
        )
        with os.fdopen(bat_fd, "w") as f:
            f.write(script)
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        subprocess.Popen(
            ["cmd", "/c", bat_path],
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
            close_fds=True,
        )
        _pending_external_restart = True
    except Exception as e:
        print(f"[UPDATE] No se pudo programar el swap en Windows: {e}")


def _check_for_updates_frozen():
    """Auto-actualizador para cuando el juego corre como ejecutable compilado
    (PyInstaller). En vez de descargar el .py, descarga el binario publicado
    en el último Release de GitHub y sustituye el ejecutable actual."""
    global update_status, update_msg, update_notif_time, update_restart_time
    import tempfile, time, json
    tmp_path = None
    try:
        api_url = GITHUB_RELEASES_API + f"?_ts={int(time.time())}"
        api_req = urllib.request.Request(
            api_url,
            headers={
                "User-Agent":    "blackjack-updater/1.0",
                "Accept":        "application/vnd.github.v3+json",
                "Cache-Control": "no-cache, no-store",
                "Pragma":        "no-cache",
            }
        )
        release = json.loads(urllib.request.urlopen(api_req, timeout=12).read())
        latest_tag = str(release.get('tag_name', '')).lstrip('v').strip()
        if not latest_tag:
            update_status = "error"; update_msg = TR('update_no_release')
            update_notif_time = pygame.time.get_ticks(); return

        saved_tag = ''
        if os.path.exists(_LAST_VERSION_FILE):
            try:
                with open(_LAST_VERSION_FILE, 'r') as f:
                    saved_tag = f.read().strip()
            except Exception:
                pass

        if latest_tag == saved_tag or latest_tag == VERSION:
            update_status = "up_to_date"; update_msg = TR('update_uptodate')
            update_notif_time = pygame.time.get_ticks(); return

        assets = release.get('assets', []) or []
        wanted_name = _release_asset_name()
        asset_url = None
        for a in assets:
            if a.get('name') == wanted_name:
                asset_url = a.get('browser_download_url')
                break
        if not asset_url:
            update_status = "error"
            update_msg = TRF('update_no_binary', tag=latest_tag)
            update_notif_time = pygame.time.get_ticks(); return

        bin_req = urllib.request.Request(
            asset_url, headers={"User-Agent": "Mozilla/5.0"}
        )
        remote_data = urllib.request.urlopen(bin_req, timeout=60).read()

        fd, tmp_path = tempfile.mkstemp(suffix=".new")
        with os.fdopen(fd, "wb") as f:
            f.write(remote_data)

        if not remote_data or len(remote_data) < 1024:
            update_status = "error"; update_msg = TR('update_invalid_bin')
            update_notif_time = pygame.time.get_ticks(); return

        try:
            os.chmod(tmp_path, 0o755)

            if sys.platform == 'win32':

                new_path = _SCRIPT_PATH + ".new"
                shutil.move(tmp_path, new_path)
                tmp_path = None
                _schedule_windows_update_swap(new_path, _SCRIPT_PATH)
                try:
                    with open(_LAST_VERSION_FILE, 'w') as f: f.write(latest_tag)
                except Exception: pass
                update_status = "restarting"; update_msg = TR('update_restarting')
                update_restart_time = pygame.time.get_ticks()
            else:
                os.replace(tmp_path, _SCRIPT_PATH)
                tmp_path = None
                try:
                    with open(_LAST_VERSION_FILE, 'w') as f: f.write(latest_tag)
                except Exception: pass
                update_status = "restarting"; update_msg = TR('update_restarting')
                update_restart_time = pygame.time.get_ticks()
        except Exception as e:
            update_status = "error"
            update_msg = TRF('update_replace_fail', err=str(e)[:35])
    except Exception as e:
        update_status = "error"; update_msg = TRF('update_error', err=str(e)[:55])
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try: os.unlink(tmp_path)
            except: pass
    update_notif_time = pygame.time.get_ticks()


def _check_for_updates():
    """Punto de entrada único del auto-actualizador: elige la estrategia
    correcta según si el juego corre como script .py o como ejecutable
    compilado."""
    if _IS_FROZEN:
        _check_for_updates_frozen()
    else:
        _check_for_updates_source()


def _restart_process():
    """Reinicia el juego, funcionando tanto en modo script como compilado.
    - Modo script: relanza con el mismo intérprete de Python (sys.executable)
      pasándole la ruta del .py.
    - Modo compilado: relanza directamente el ejecutable (sys.executable ES
      el propio binario; no hay intérprete "por fuera" al que llamar)."""
    try:
        if _IS_FROZEN:
            os.execv(_SCRIPT_PATH, [_SCRIPT_PATH])
        else:
            os.execv(sys.executable, [sys.executable, _SCRIPT_PATH])
    except Exception:
        try:
            if _IS_FROZEN:
                subprocess.Popen([_SCRIPT_PATH])
            else:
                subprocess.Popen([sys.executable, _SCRIPT_PATH])
        finally:
            pygame.quit()
            sys.exit(0)


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
        x = _CARD_X_ORIGIN + len(mano) * CARD_SPACING
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
    global rosa_secret_done, rosa_kicked
    player_money = 1000; stats = {'played':0,'won':0,'lost':0,'blackjacks':0}
    current_bet_input = ""; current_bet = 10; last_bet = None
    epic_win_triggered = False
    rosa_secret_done = False
    rosa_kicked = False
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
HE_AI_NAMES_ES = ["JUGADOR 1", "JUGADOR 2", "JUGADOR 3", "JUGADOR 4"]
HE_AI_NAMES_EN = ["PLAYER 1", "PLAYER 2", "PLAYER 3", "PLAYER 4"]

class _HEAiNamesProxy(list):
    """Lista que se traduce dinamicamente segun CONFIG['language'] en cada acceso."""
    def _cur(self):
        return HE_AI_NAMES_EN if CONFIG.get('language', 'es') == 'en' else HE_AI_NAMES_ES
    def __getitem__(self, i):
        return self._cur()[i]
    def __len__(self):
        return len(self._cur())
    def __iter__(self):
        return iter(self._cur())

HE_AI_NAMES = _HEAiNamesProxy()
he_ai_cards  = [[], [], [], []]   
he_ai_money  = [3000, 3000, 3000, 3000]
he_ai_hand_names = ["", "", "", ""]  
he_ai_winner = False  

he_raise_btn = pygame.Rect(0, 0, 230, 38)  

_HE_AI_MODEL_LOCAL = os.path.join('test', 'he_ai_model.json')
_HE_AI_MODEL_URL   = "https://raw.githubusercontent.com/humrand/blackjack-python/main/test/he_ai_model.json"
_he_ai_model = None
_he_ai_model_ready = False

def _download_text_file(local_path, url, timeout=25):
    """Descarga un archivo de texto si no existe."""
    if os.path.exists(local_path):
        return True
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        with open(local_path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"[JSON] Error descargando {os.path.basename(local_path)}: {e}")
        return False

def _load_he_ai_model():
    """Carga el modelo JSON del poker una sola vez."""
    global _he_ai_model, _he_ai_model_ready
    if _he_ai_model_ready:
        return _he_ai_model
    _he_ai_model_ready = True

    _download_text_file(_HE_AI_MODEL_LOCAL, _HE_AI_MODEL_URL, timeout=25)
    try:
        import json as _json
        with open(_HE_AI_MODEL_LOCAL, 'r', encoding='utf-8') as f:
            _he_ai_model = _json.load(f)
    except Exception as e:
        print(f"[JSON] No se pudo cargar he_ai_model.json: {e}")
        _he_ai_model = None
    return _he_ai_model

def _he_ai_current_stage():
    if he_state == 'pre_flop':
        return 'preflop'
    if he_state == 'flop':
        return 'flop'
    if he_state == 'turn':
        return 'turn'
    if he_state == 'river':
        return 'river'
    return he_state

def _he_ai_strength_rank(ai_idx):
    ai_hand = he_ai_cards[ai_idx] if ai_idx < len(he_ai_cards) else []
    if not ai_hand:
        return -1
    cards = [(e[0], e[1], e[2], e[3]) for e in ai_hand]
    if he_community_cards:
        cards += [(e[0], e[1], e[2], e[3]) for e in he_community_cards]
    score, _ = evaluate_holdem_hand(cards)
    return score[0] if score else -1

def _he_ai_apply_call(ai_idx, money, call_amt):
    global he_pot, he_ai_money
    paid = min(call_amt, money)
    if paid > 0:
        he_pot += paid
        he_ai_money[ai_idx] -= paid
    return paid

def _he_ai_apply_raise(ai_idx, money, amount):
    global he_pot, he_ai_money, he_ai_raised_this_round, he_ai_raise_amount
    amt = min(amount, money)
    if amt > 0:
        he_pot += amt
        he_ai_money[ai_idx] -= amt
        he_ai_raised_this_round = True
        he_ai_raise_amount = max(he_ai_raise_amount, amt)
    return amt

def _he_ai_pick_from_model(ai_idx):
    """Intenta decidir la acción del AI usando el JSON externo."""
    model = _load_he_ai_model()
    if model is None:
        return None

    stage = _he_ai_current_stage()
    rank = _he_ai_strength_rank(ai_idx)
    money = he_ai_money[ai_idx] if ai_idx < len(he_ai_money) else 0
    call_amt = min(he_blind, money)

    def _apply_rule(rule):
        if not isinstance(rule, dict):
            return None
        action = str(rule.get('action', '')).lower().strip()
        if action in ('fold', 'retire', 'se retira'):
            he_ai_folded[ai_idx] = True
            return rule.get('text', TR('he_ai_folds'))
        if action in ('call', 'iguala', 'check'):
            _he_ai_apply_call(ai_idx, money, call_amt)
            return rule.get('text', TR('he_ai_call'))
        if action in ('raise', 'sube', 'farolea y sube'):
            mult = rule.get('raise_mult', rule.get('mult', 1))
            try:
                mult = max(1, int(mult))
            except Exception:
                mult = 1
            amt = _he_ai_apply_raise(ai_idx, money, he_blind * mult)
            prefix = rule.get('text_prefix', TR('he_ai_raise').split(' ')[0])
            return f"{prefix} {amt}".strip() if amt else None
        return None

    def _match_rank_rule(node):
        if not isinstance(node, dict):
            return None
        for bucket in ('by_rank', 'ranks', 'rank_map'):
            buckets = node.get(bucket)
            if isinstance(buckets, dict):
                for key in (str(rank), rank, str(max(0, rank))):
                    if key in buckets:
                        res = _apply_rule(buckets[key]) if isinstance(buckets[key], dict) else buckets[key]
                        if res is not None:
                            return res
        return None

    if isinstance(model, list):
        for rule in model:
            if not isinstance(rule, dict):
                continue
            min_rank = rule.get('min_rank', rule.get('rank_min', -999))
            max_rank = rule.get('max_rank', rule.get('rank_max', 999))
            if min_rank <= rank <= max_rank:
                res = _apply_rule(rule)
                if res is not None:
                    return res
        return None

    if not isinstance(model, dict):
        return None

    for key in (stage, he_state, 'default', 'general'):
        node = model.get(key)
        if node is None:
            continue

        if isinstance(node, list):
            for rule in node:
                res = _apply_rule(rule)
                if res is not None:
                    return res

        if isinstance(node, dict):
            res = _match_rank_rule(node)
            if res is not None:
                return res

            if any(k in node for k in ('fold_prob', 'call_prob', 'raise_prob', 'raise_mult')):
                import random as _rnd
                r = _rnd.random()
                fold_p = float(node.get('fold_prob', 0.0) or 0.0)
                call_p = float(node.get('call_prob', 0.0) or 0.0)
                raise_p = float(node.get('raise_prob', 0.0) or 0.0)
                if r < fold_p:
                    he_ai_folded[ai_idx] = True
                    return node.get('fold_text', TR('he_ai_folds'))
                if r < fold_p + raise_p:
                    mult = node.get('raise_mult', 1)
                    try:
                        mult = max(1, int(mult))
                    except Exception:
                        mult = 1
                    amt = _he_ai_apply_raise(ai_idx, money, he_blind * mult)
                    return f"{node.get('raise_text_prefix', TR('he_ai_raise').split(' ')[0])} {amt}".strip() if amt else None
                if r < fold_p + raise_p + call_p:
                    _he_ai_apply_call(ai_idx, money, call_amt)
                    return node.get('call_text', TR('he_ai_call'))

            action = str(node.get('action', '')).lower().strip()
            if action:
                res = _apply_rule(node)
                if res is not None:
                    return res

    return None

he_ai_turn_active       = False
he_ai_turn_idx          = 0
he_ai_turn_phase        = 'announcing'  
he_ai_turn_timer        = 0
he_ai_actions           = []
he_ai_folded            = [False, False, False, False]
he_ai_raised_this_round = False   
he_ai_raise_amount      = 0      
_HE_ANNOUNCE_MS         = 650

he_deal_queue      = []   
he_deal_next_time  = 0    
he_dealing         = False  
_HE_DECIDE_MS           = 900

def _he_ai_compute_action(ai_idx):
    """Decide what AI player ai_idx does, prefiriendo el modelo JSON externo."""
    model_action = _he_ai_pick_from_model(ai_idx)
    if model_action is not None:
        return model_action

    global he_pot, he_ai_money, he_ai_folded, he_ai_raised_this_round, he_ai_raise_amount
    if he_ai_folded[ai_idx]:
        return TR('he_ai_already_folded')
    ai_hand = he_ai_cards[ai_idx] if ai_idx < len(he_ai_cards) else []
    money = he_ai_money[ai_idx]
    if money <= 0:
        he_ai_folded[ai_idx] = True
        return TR('he_ai_folds_broke')
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
            return TRF('he_ai_raise_amt', amt=amt)
        else:
            he_pot += call_amt; he_ai_money[ai_idx] -= call_amt
            return TR('he_ai_call')
    elif rank >= 3:
        if r < 0.50:
            amt = do_raise(2, 4)
            return TRF('he_ai_raise', amt=amt)
        else:
            he_pot += call_amt; he_ai_money[ai_idx] -= call_amt
            return TR('he_ai_call')
    elif rank >= 0:
        if r < 0.22:
            he_ai_folded[ai_idx] = True
            return TR('he_ai_folds')
        elif r < 0.38:
            amt = do_raise(1, 2)
            return TRF('he_ai_raise', amt=amt)
        else:
            he_pot += call_amt; he_ai_money[ai_idx] -= call_amt
            return TR('he_ai_call')
    else:
        if r < 0.50:
            he_ai_folded[ai_idx] = True
            return TR('he_ai_folds')
        elif r < 0.65:
            amt = do_raise(1, 3)
            return TRF('he_ai_bluff_raise', amt=amt)
        else:
            he_pot += call_amt; he_ai_money[ai_idx] -= call_amt
            return TR('he_ai_call')


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


def _he_process_deal_queue(now):
    """Procesa la cola de reparto secuencial. Llamar cada frame."""
    global he_deal_queue, he_deal_next_time, he_dealing, he_state
    if not he_dealing or not he_deal_queue:
        if he_dealing and not he_deal_queue:
            he_dealing = False
            if he_state == 'dealing_preflop':
                he_state = 'pre_flop'
            elif he_state == 'dealing_flop':
                he_state = 'flop'
        return
    if now >= he_deal_next_time:
        action = he_deal_queue.pop(0)
        action()
        if he_deal_queue:
            delay = 500 if he_state == 'dealing_flop' else 130
            he_deal_next_time = now + delay
        else:
            he_dealing = False
            if he_state == 'dealing_preflop':
                he_state = 'pre_flop'
            elif he_state == 'dealing_flop':
                he_state = 'flop'


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
    8: 'hand_royal_flush', 7: 'hand_straight_flush', 6: 'hand_quads',
    5: 'hand_full_house', 4: 'hand_flush', 3: 'hand_straight', 2: 'hand_trips',
    1: 'hand_two_pair', 0: 'hand_pair', -1: 'hand_high_card'
}

def evaluate_holdem_hand(cards_7):
    """Best 5-card hand from 7 cards (or fewer). Returns (score_tuple, name_key)."""
    best = None; best_name = 'hand_high_card'
    pool = list(cards_7)
    n = len(pool)
    k = min(5, n)
    for combo in _combinations(pool, k):
        sc = _he_eval_5(combo)
        if best is None or sc > best:
            best = sc; best_name = _HE_RANK_NAMES.get(sc[0], 'hand_high_card')
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
    global he_deal_queue, he_deal_next_time, he_dealing
    he_deal_queue = []; he_deal_next_time = 0; he_dealing = False

def he_start_hand(now):
    """Deal pre-flop de forma secuencial: 1 carta a cada jugador en orden, luego la 2ª vuelta."""
    global he_state, he_pot, he_street_bet, he_deck
    global he_player_cards, he_dealer_cards, he_community_cards
    global he_mensaje, he_player_hand_name, he_dealer_hand_name, he_winner
    global he_in_raise, he_raise_input, he_ai_cards, he_ai_hand_names, he_ai_winner
    global he_deal_queue, he_deal_next_time, he_dealing
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

    he_player_cards = []
    he_dealer_cards = []
    he_ai_cards = [[], [], [], []]

    px = [_he_card_x(i, 2) for i in range(2)]

    deal_steps = []
    for round_i in range(2):
        def _deal_player(ri=round_i, _px=px):
            he_player_cards.append(_he_deal_card(he_deck, _px[ri], HE_PLAYER_Y))
        deal_steps.append(_deal_player)
        for ai_i, (ax, ay) in enumerate(HE_AI_POSITIONS):
            x_pos = ax + (HE_AI_CARD_GAP if round_i == 1 else 0)
            def _deal_ai(ai=ai_i, axx=x_pos, ayy=ay):
                he_ai_cards[ai].append(_he_deal_card(he_deck, axx, ayy, face_down=True))
            deal_steps.append(_deal_ai)

    he_deal_queue = deal_steps
    he_pot = he_blind * 6
    he_street_bet = 0
    he_dealing = True
    he_deal_next_time = now + 80  
    he_state = 'dealing_preflop'

def _he_dealer_act(raise_amount=0):
    """Simple dealer bot: always calls any raise."""
    global he_pot
    if raise_amount > 0:
        he_pot += raise_amount  

def he_do_flop(now):
    global he_community_cards, he_state
    global he_deal_queue, he_deal_next_time, he_dealing
    deal_steps = []
    for i in range(3):
        cx = _he_card_x(i, 5)
        def _deal_flop_card(cx=cx):
            he_community_cards.append(_he_deal_card(he_deck, cx, HE_COMMUNITY_Y))
        deal_steps.append(_deal_flop_card)
    he_deal_queue = deal_steps
    he_dealing = True
    he_deal_next_time = now + 80
    he_state = 'dealing_flop'

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
            he_mensaje = TRF('he_tie', pn=TR(pn))
            he_stats['tied'] += 1
        else:
            he_winner = 'player'; he_player_money += he_pot
            he_mensaje = TRF('he_you_won', pn=TR(pn), pot=he_pot)
            he_stats['won'] += 1
            spawn_particles(ANCHO//2, ALTO//2, DORADO, count=55)
            overlay_flash.update({'active':True,'color':(255,220,0),'alpha':200,'start':now,'duration':400})
    else:
        he_ai_winner = True
        he_winner = 'dealer'
        winners = [HE_AI_NAMES[i] for i in active_ai_indices if ai_scores[i] == best_score]
        he_mensaje = TRF('he_they_won', winners=', '.join(winners), pn=TR(pn))
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
    he_mensaje = TRF('he_all_folded', pot=he_pot)
    he_stats['won'] += 1; he_stats['played'] += 1
    spawn_particles(ANCHO//2, ALTO//2, DORADO, count=55)
    overlay_flash.update({'active':True,'color':(255,220,0),'alpha':200,'start':now,'duration':400})
    he_state = 'result'

def he_fold(now):
    global he_state, he_winner, he_mensaje, he_stats, poker_player_money
    he_winner = 'fold'; he_state = 'result'
    he_mensaje = TR('he_you_folded')
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

    title_s = _safe_render(FUENTE_PEQUENA, TR('he_title'), True, DORADO, fallback_text="TEXAS HOLD'EM")
    VENTANA.blit(title_s, (ANCHO//2 - title_s.get_width()//2, 38))

    pl = FUENTE_PEQUENA.render(TR('he_you_label'), True, (180, 240, 190))
    VENTANA.blit(pl, (ANCHO//2 - pl.get_width()//2, HE_PLAYER_Y - 30))

    if he_state not in ('betting',):
        cl = _FUENTE_HE_SMALL.render(TR('he_community'), True, (180, 160, 80))
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
                    hn_s = _FUENTE_HE_SMALL.render(TR(he_ai_hand_names[ai_i]), True, (255, 200, 180))
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
            'hand_high_card','hand_pair','hand_two_pair','hand_trips','hand_straight',
            'hand_flush','hand_full_house','hand_quads','hand_straight_flush','hand_royal_flush'
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
        combo_lbl = FUENTE_PEQUENA.render(TRF('he_your_hand', v=TR(live_name)), True, live_col)
        VENTANA.blit(combo_lbl, (ANCHO//2 - combo_lbl.get_width()//2, combo_y + 4))

    if he_state not in ('betting',):
        pot_s = FUENTE_PEQUENA.render(TRF('he_pot', v=he_pot), True, DORADO)
        pot_bg = pygame.Surface((pot_s.get_width()+24, pot_s.get_height()+10), pygame.SRCALPHA)
        pot_bg.fill((0,0,0,160))
        px2 = ANCHO//2 - pot_bg.get_width()//2
        py2 = HE_COMMUNITY_Y + CARD_H + 14
        VENTANA.blit(pot_bg, (px2, py2))
        VENTANA.blit(pot_s, (px2+12, py2+5))

    if he_state == 'result' and he_player_hand_name:
        phn_s = FUENTE_PEQUENA.render(TRF('he_your_hand', v=TR(he_player_hand_name)), True, (180, 255, 180))
        VENTANA.blit(phn_s, (ANCHO//2 - phn_s.get_width()//2, HE_PLAYER_Y + CARD_H + 10))

    box_w = 960; pad = 16; lh = 32
    box_h = 130; bx = (ANCHO - box_w) // 2; by = ALTO - box_h - 14
    bg_s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    bg_s.fill((0, 0, 0, 190))
    VENTANA.blit(bg_s, (bx, by))
    pygame.draw.rect(VENTANA, NEGRO, (bx, by, box_w, box_h), 2, border_radius=10)

    y_o = by + pad
    chips_s = FUENTE_PEQUENA.render(TRF('he_chips', v=he_player_money), True, DORADO)
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
        hint = FUENTE_INSTR.render(TRF('he_deal_hint', max=BET_MAX_HOLDEM), True, (160,160,160))
        VENTANA.blit(hint, (bx + (box_w - hint.get_width())//2, y_o + lh*2 + 4))

    elif he_state in ('dealing_preflop', 'dealing_flop'):
        dots = '.' * ((now // 300) % 4)
        deal_s = FUENTE_PEQUENA.render("Repartiendo" + dots, True, (220, 200, 120))
        VENTANA.blit(deal_s, (bx + (box_w - deal_s.get_width()) // 2, y_o + lh))

    elif he_state in ('pre_flop', 'flop', 'turn', 'river'):
        street_labels = {'pre_flop': 'PRE-FLOP', 'flop': 'FLOP', 'turn': 'TURN', 'river': 'RIVER'}
        sl = FUENTE_PEQUENA.render(street_labels.get(he_state,''), True, (220, 200, 120))
        VENTANA.blit(sl, (bx + pad, y_o + lh))

        if he_ai_turn_active:
            cur_name = HE_AI_NAMES[he_ai_turn_idx] if he_ai_turn_idx < len(HE_AI_NAMES) else ""
            if he_ai_turn_phase == 'announcing':
                turn_txt = TRF('he_turn_of', name=cur_name)
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
            rl = FUENTE_PEQUENA.render(TR('he_raise_label'), True, BLANCO)
            VENTANA.blit(rl, (bx + pad, y_o + lh*2))
            inp_x = bx + pad + rl.get_width() + 12; inp_w = 200; inp_h = 32
            inp_bg = pygame.Surface((inp_w, inp_h), pygame.SRCALPHA)
            inp_bg.fill((30, 20, 0, 230))
            VENTANA.blit(inp_bg, (inp_x, y_o + lh*2 - 2))
            pygame.draw.rect(VENTANA, DORADO, (inp_x, y_o + lh*2 - 2, inp_w, inp_h), 2, border_radius=6)
            dt = FUENTE_PEQUENA.render(clip_text_right(he_raise_input, FUENTE_PEQUENA, inp_w-12), True, BLANCO)
            VENTANA.blit(dt, (inp_x + 8, y_o + lh*2 + (inp_h - dt.get_height())//2 - 2))
            cancel_s = FUENTE_INSTR.render(TR('he_confirm_cancel'), True, (180,160,100))
            VENTANA.blit(cancel_s, (bx + (box_w - cancel_s.get_width())//2, y_o + lh*3))
        else:
            btn_w = 230; btn_h = 38; gap = 18
            total_bw = 3*btn_w + 2*gap; bx_btns = ANCHO//2 - total_bw//2
            by_btns = by + box_h - btn_h - pad
            fold_r  = pygame.Rect(bx_btns,               by_btns, btn_w, btn_h)
            call_r  = pygame.Rect(bx_btns+btn_w+gap,     by_btns, btn_w, btn_h)
            he_raise_btn.update(bx_btns+2*(btn_w+gap), by_btns, btn_w, btn_h)
            _draw_he_btn(TR('he_fold'),  fold_r,  (120,30,30), (180,50,50), mouse_pos)
            call_lbl = TR('he_check') if he_street_bet == 0 else TRF('he_call', amt=he_street_bet)
            _draw_he_btn(call_lbl, call_r, (30,80,140), (50,120,200), mouse_pos)
            _draw_he_btn(TR('he_raise_btn'),  he_raise_btn, (120,90,0), (200,150,0), mouse_pos, border=DORADO)
            hint2 = FUENTE_INSTR.render(TR('he_controls'), True, (120,120,120))
            VENTANA.blit(hint2, (bx + (box_w - hint2.get_width())//2, y_o + lh))

    elif he_state == 'result':
        res_col = DORADO if he_winner == 'player' else (ROJO if he_winner in ('dealer','fold') else (200,200,200))
        msg_s = FUENTE_MSG.render(he_mensaje, True, res_col)
        VENTANA.blit(msg_s, (ANCHO//2 - msg_s.get_width()//2, by + (box_h - msg_s.get_height())//2 - 10))
        hint3 = FUENTE_INSTR.render(TR('he_next_hand'), True, (140,140,140))
        VENTANA.blit(hint3, (ANCHO//2 - hint3.get_width()//2, by + box_h - hint3.get_height() - 8))

    st_s = _FUENTE_HE_SMALL.render(
        TRF('he_stats', won=he_stats['won'], lost=he_stats['lost'], tied=he_stats['tied']), True, (160,160,160))
    VENTANA.blit(st_s, (bx + box_w - st_s.get_width() - pad, y_o))

    _draw_he_btn(TR("esc_menu"),    he_menu_btn,      (30,70,140), (50,110,200), mouse_pos)
    _draw_he_btn(TR("reiniciar_btn"), he_reiniciar_btn, (140,30,30), (200,55,55), mouse_pos)

    if he_player_money <= 0 and he_state == 'betting':
        rb = FUENTE_PEQUENA.render(TR('he_no_chips'), True, ROJO)
        VENTANA.blit(rb, (ANCHO//2 - rb.get_width()//2, ALTO//2))


def _start_poker_mode():
    global app_state, game_mode
    game_mode = 'poker'
    app_state = 'poker'
    he_reiniciar()


ONLINE_DEFAULT_PORT = 5555

_online_sock          = None          
_online_server_addr   = None          
_online_recv_thread   = None
_online_ping_thread   = None
_online_msg_queue     = _collections_mod.deque()  

_online_ip_input      = ""
_online_port_input    = str(ONLINE_DEFAULT_PORT)
_online_name_input    = "Jugador"
_online_active_field  = 'ip'         
_online_connect_error = ""
_online_connecting    = False

_online_lobby_players = []            
_online_hand          = []          
_online_community     = []            
_online_other_players = []           
_online_pot           = 0
_online_blind         = 50
_online_my_money      = 3000
_online_my_turn       = False
_online_to_call       = 0
_online_street        = ""
_online_message       = ""           
_online_in_raise      = False
_online_raise_input   = ""
_online_action_log    = []          
_online_result        = None       
_online_result_timer  = 0
_online_game_started  = False
_online_min_players   = 2


def _online_recv_loop(sock):
    """Hilo de recepción UDP: recibe datagramas JSON del servidor y los encola."""
    buf = b""
    sock.settimeout(1.0)
    while True:
        try:
            data, _ = sock.recvfrom(65507)
            buf += data
        except _socket_mod.timeout:
            if sock.fileno() == -1:
                break
            continue
        except Exception:
            break
        while b'\n' in buf:
            line, buf = buf.split(b'\n', 1)
            line = line.strip()
            if line:
                try:
                    msg = _json_mod.loads(line.decode('utf-8', errors='replace'))
                    if msg.get('type') != 'pong':  
                        _online_msg_queue.append(msg)
                except Exception:
                    pass
    _online_msg_queue.append({'type': 'disconnected'})


def _online_ping_loop(sock, server_addr):
    """Hilo de heartbeat: envía ping cada 5s para mantener la conexión viva."""
    import time as _time
    while True:
        _time.sleep(5)
        if sock.fileno() == -1:
            break
        try:
            sock.sendto((_json_mod.dumps({'type': 'ping'}) + '\n').encode('utf-8'), server_addr)
        except Exception:
            break


def _online_send(obj):
    """Envía un datagrama JSON al servidor."""
    global _online_sock, _online_server_addr
    if _online_sock is None or _online_server_addr is None:
        return
    try:
        _online_sock.sendto((_json_mod.dumps(obj) + '\n').encode('utf-8'), _online_server_addr)
    except Exception as e:
        print(f"[ONLINE] Error enviando: {e}")


def _online_connect(ip, port, name):
    """Crea socket UDP, envía join y espera respuesta inicial del servidor."""
    global _online_sock, _online_server_addr, _online_recv_thread, _online_ping_thread
    global _online_connect_error, _online_connecting, app_state, _online_name_input
    import time as _time
    try:
        port = int(port)
        s = _socket_mod.socket(_socket_mod.AF_INET, _socket_mod.SOCK_DGRAM)
        s.settimeout(6)
        server_addr = (ip, port)
        s.sendto((_json_mod.dumps({'type': 'join', 'name': name}) + '\n').encode('utf-8'), server_addr)
        data, _ = s.recvfrom(65507)           
        s.settimeout(None)
        _online_sock        = s
        _online_server_addr = server_addr
        for line in data.split(b'\n'):
            line = line.strip()
            if line:
                try: _online_msg_queue.append(_json_mod.loads(line.decode('utf-8', errors='replace')))
                except: pass
        _online_recv_thread = threading.Thread(target=_online_recv_loop, args=(s,), daemon=True)
        _online_recv_thread.start()
        _online_ping_thread = threading.Thread(target=_online_ping_loop, args=(s, server_addr), daemon=True)
        _online_ping_thread.start()
        _online_connecting    = False
        _online_connect_error = ""
        app_state = 'poker_online_lobby'
    except _socket_mod.timeout:
        _online_connect_error = TR('poker_connect_fail_timeout')
        _online_connecting = False
        try: s.close()
        except: pass
    except Exception as e:
        _online_connect_error = TRF('poker_connect_fail', e=e)
        _online_connecting = False
        try: s.close()
        except: pass


def _online_disconnect():
    global _online_sock, _online_server_addr, _online_game_started
    try:
        if _online_sock:
            _online_sock.close()
    except Exception:
        pass
    _online_sock        = None
    _online_server_addr = None
    _online_game_started = False
    _online_msg_queue.clear()


def _online_make_carta(v, p, dest_x, dest_y):
    """Crea un objeto Carta para una carta recibida del servidor."""
    val_map = {'A':11,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,'Q':10,'K':10}
    color_map = {'H': ROJO, 'D': ROJO, 'S': NEGRO, 'C': NEGRO}
    val   = val_map.get(str(v), 10)
    color = color_map.get(str(p), NEGRO)
    return Carta(str(v), str(p), val, color, dest_x, dest_y,
                 start_pos=(ANCHO // 2, 30))


def _online_process_messages(now):
    """Procesa mensajes del servidor en el hilo principal (llamar cada frame)."""
    global app_state, _online_lobby_players, _online_game_started
    global _online_hand, _online_community, _online_other_players
    global _online_pot, _online_blind, _online_my_money
    global _online_my_turn, _online_to_call, _online_street
    global _online_message, _online_action_log, _online_result, _online_result_timer
    global _online_in_raise

    while _online_msg_queue:
        msg = _online_msg_queue.popleft()
        mtype = msg.get('type', '')

        if mtype == 'disconnected':
            _online_message = TR('poker_disconnected')
            app_state = 'poker_online_connect'
            _online_disconnect()

        elif mtype == 'lobby':
            _online_lobby_players = msg.get('players', [])
            _online_game_started = False

        elif mtype == 'deal':
            _online_game_started = True
            _online_result = None
            _online_in_raise = False
            _online_action_log = []
            _online_my_turn = False
            _online_message = ""

            raw_hand = msg.get('hand', [])
            _online_hand = []
            for idx, (v, p) in enumerate(raw_hand):
                dest_x = _he_card_x(idx, 2)
                _online_hand.append(_online_make_carta(v, p, dest_x, HE_PLAYER_Y))

            _online_community = []
            _online_pot        = msg.get('pot', 0)
            _online_blind      = msg.get('blind', 50)
            _online_my_money   = msg.get('my_money', _online_my_money)
            raw_players        = msg.get('players', [])
            _online_other_players = [p for p in raw_players
                                     if p.get('name') != _online_name_input]
            if app_state != 'poker_online_game':
                app_state = 'poker_online_game'

        elif mtype == 'community':
            raw = msg.get('cards', [])
            n = len(raw)
            _online_community = []
            for idx, (v, p) in enumerate(raw):
                cx = _he_card_x(idx, 5)
                _online_community.append(_online_make_carta(v, p, cx, HE_COMMUNITY_Y))
            _online_pot = msg.get('pot', _online_pot)

        elif mtype == 'your_turn':
            _online_my_turn  = True
            _online_to_call  = msg.get('to_call', 0)
            _online_street   = msg.get('street', _online_street)
            _online_pot      = msg.get('pot', _online_pot)
            _online_in_raise = False

        elif mtype == 'player_action':
            name   = msg.get('player', '?')
            action = msg.get('action', '')
            amount = msg.get('amount', 0)
            if amount:
                log_line = f"{name}: {action} {amount}"
            else:
                log_line = f"{name}: {action}"
            _online_action_log.append(log_line)
            if len(_online_action_log) > 6:
                _online_action_log.pop(0)
            _online_pot = msg.get('pot', _online_pot)
            if action == 'rebuy' and name == _online_name_input:
                _online_my_money = int(amount) if amount else _online_my_money
            for pp in msg.get('players', []):
                for op in _online_other_players:
                    if op['name'] == pp['name']:
                        op.update(pp)

        elif mtype == 'result':
            _online_result       = msg
            _online_result_timer = now
            _online_my_turn      = False
            _online_my_money     = msg.get('my_money', _online_my_money)
            _online_pot          = 0

        elif mtype == 'next_hand':
            _online_result   = None
            _online_my_turn  = False
            _online_message  = ""
            _online_in_raise = False

        elif mtype == 'error':
            _online_message = msg.get('msg', TR('poker_unknown_error'))

        elif mtype == 'waiting':
            _online_message = msg.get('msg', TR('poker_waiting_players'))



_FUENTE_OL_TITLE = None
_FUENTE_OL_BTN   = None
_FUENTE_OL_SUB   = None

def _get_online_fonts():
    global _FUENTE_OL_TITLE, _FUENTE_OL_BTN, _FUENTE_OL_SUB
    if _FUENTE_OL_TITLE is None:
        _FUENTE_OL_TITLE = pygame.font.SysFont("arial", 56, bold=True)
        _FUENTE_OL_BTN   = pygame.font.SysFont("arial", 34, bold=True)
        _FUENTE_OL_SUB   = pygame.font.SysFont("arial", 22)
    return _FUENTE_OL_TITLE, _FUENTE_OL_BTN, _FUENTE_OL_SUB


def _render_poker_mode_select(now):
    """Pantalla de selección: Online / Offline."""
    VENTANA.fill((6, 4, 14))
    draw_rain(VENTANA, now, alpha=45)
    ft, fb, fs = _get_online_fonts()

    title = ft.render("Texas Hold'em", True, DORADO)
    VENTANA.blit(title, (ANCHO//2 - title.get_width()//2, 180))
    sub = fs.render(TR('poker_how'), True, (160, 140, 90))
    VENTANA.blit(sub, (ANCHO//2 - sub.get_width()//2, 260))
    pygame.draw.line(VENTANA, DORADO, (ANCHO//2-280, 300), (ANCHO//2+280, 300), 1)

    mouse_pos = to_logical(pygame.mouse.get_pos())
    BTN_W = 560; BTN_H = 110; GAP = 28
    BX = ANCHO//2 - BTN_W//2
    opts = [
        (TR('poker_online_title'),  TR('poker_online_sub'), 360),
        (TR('poker_offline_title'), TR('poker_offline_sub'),   360 + BTN_H + GAP),
    ]
    rects = []
    for label, hint, by in opts:
        rect = pygame.Rect(BX, by, BTN_W, BTN_H)
        hov  = rect.collidepoint(mouse_pos)
        bg_col = (55, 95, 68) if hov else (22, 36, 26)
        bg_s   = pygame.Surface((BTN_W, BTN_H), pygame.SRCALPHA)
        bg_s.fill((*bg_col, 220 if hov else 160))
        VENTANA.blit(bg_s, (BX, by))
        pygame.draw.rect(VENTANA, DORADO if hov else (70, 110, 80), rect, 2, border_radius=12)
        lbl_s = fb.render(label, True, (220, 255, 225) if hov else BLANCO)
        VENTANA.blit(lbl_s, (BX + 32, by + 20))
        hint_s = fs.render(hint, True, (160, 190, 165) if hov else (110, 130, 115))
        VENTANA.blit(hint_s, (BX + 32, by + 20 + lbl_s.get_height() + 6))
        rects.append(rect)

    back_s = fs.render(TR('poker_esc_back_main'), True, (80, 70, 55))
    VENTANA.blit(back_s, (ANCHO//2 - back_s.get_width()//2, 700))
    return rects 


def _render_poker_online_connect(now):
    """Pantalla de conexión: IP, puerto, nombre."""
    global _online_active_field
    VENTANA.fill((6, 4, 14))
    draw_rain(VENTANA, now, alpha=45)
    ft, fb, fs = _get_online_fonts()

    title = ft.render(TR('poker_connect_title'), True, DORADO)
    VENTANA.blit(title, (ANCHO//2 - title.get_width()//2, 120))
    pygame.draw.line(VENTANA, DORADO, (ANCHO//2-320, 195), (ANCHO//2+320, 195), 1)

    mouse_pos = to_logical(pygame.mouse.get_pos())
    fields = [
        ('ip',   TR('poker_server_ip'),  _online_ip_input,   340),
        ('port', TR('poker_port'),       _online_port_input, 440),
        ('name', TR('poker_your_name'),  _online_name_input, 540),
    ]
    field_rects = {}
    FW = 560; FH = 48; FX = ANCHO//2 - FW//2
    for key, label, value, fy in fields:
        lbl_s = fs.render(label, True, (180, 160, 90))
        VENTANA.blit(lbl_s, (FX, fy - 24))
        active = (_online_active_field == key)
        bg = pygame.Surface((FW, FH), pygame.SRCALPHA)
        bg.fill((30, 30, 30, 230))
        VENTANA.blit(bg, (FX, fy))
        border_col = DORADO if active else (80, 100, 80)
        frect = pygame.Rect(FX, fy, FW, FH)
        pygame.draw.rect(VENTANA, border_col, frect, 2, border_radius=7)
        cursor = ('|' if (now // 420) % 2 == 0 else '') if active else ''
        disp = clip_text_right(value + cursor, FUENTE_PEQUENA, FW - 16)
        txt_s = FUENTE_PEQUENA.render(disp, True, BLANCO)
        VENTANA.blit(txt_s, (FX + 10, fy + (FH - txt_s.get_height())//2))
        field_rects[key] = frect

    conn_rect = pygame.Rect(ANCHO//2 - 140, 630, 280, 58)
    conn_hov  = conn_rect.collidepoint(mouse_pos) and not _online_connecting
    conn_col  = (55, 95, 68) if conn_hov else (30, 60, 40)
    conn_bg   = pygame.Surface((280, 58), pygame.SRCALPHA)
    conn_bg.fill((*conn_col, 230))
    VENTANA.blit(conn_bg, (ANCHO//2 - 140, 630))
    pygame.draw.rect(VENTANA, DORADO if conn_hov else (60, 110, 70), conn_rect, 2, border_radius=10)
    label_txt = TR('poker_connecting') if _online_connecting else TR('poker_connect_btn')
    conn_lbl  = fb.render(label_txt, True, (220, 255, 225) if conn_hov else BLANCO)
    VENTANA.blit(conn_lbl, (conn_rect.centerx - conn_lbl.get_width()//2,
                             conn_rect.centery - conn_lbl.get_height()//2))

    if _online_connect_error:
        err_s = fs.render(_online_connect_error, True, (255, 100, 80))
        VENTANA.blit(err_s, (ANCHO//2 - err_s.get_width()//2, 704))

    back_s = fs.render(TR('poker_esc_back'), True, (80, 70, 55))
    VENTANA.blit(back_s, (ANCHO//2 - back_s.get_width()//2, 740))

    return field_rects, conn_rect


def _render_poker_online_lobby(now):
    """Sala de espera online."""
    VENTANA.fill((6, 4, 14))
    draw_rain(VENTANA, now, alpha=45)
    ft, fb, fs = _get_online_fonts()

    title = ft.render(TR('poker_waiting_room'), True, DORADO)
    VENTANA.blit(title, (ANCHO//2 - title.get_width()//2, 140))

    dots = '.' * ((now // 350) % 4)
    wait_s = fb.render(TRF('poker_waiting_players_dots', dots=dots), True, (200, 180, 90))
    VENTANA.blit(wait_s, (ANCHO//2 - wait_s.get_width()//2, 240))

    n = len(_online_lobby_players)
    need_s = fs.render(TRF('poker_connected_count', n=n, min=_online_min_players),
                       True, (160, 200, 160))
    VENTANA.blit(need_s, (ANCHO//2 - need_s.get_width()//2, 310))

    pygame.draw.line(VENTANA, (70, 60, 30), (ANCHO//2-260, 345), (ANCHO//2+260, 345), 1)
    for i, pname in enumerate(_online_lobby_players):
        icon_col = DORADO if pname == _online_name_input else (180, 200, 180)
        icon = "▶ " if pname == _online_name_input else "• "
        p_s = fb.render(icon + pname, True, icon_col)
        VENTANA.blit(p_s, (ANCHO//2 - p_s.get_width()//2, 370 + i * 52))

    if _online_message:
        msg_s = fs.render(_online_message, True, (255, 200, 100))
        VENTANA.blit(msg_s, (ANCHO//2 - msg_s.get_width()//2, 650))

    back_s = fs.render(TR('poker_esc_disconnect'), True, (80, 70, 55))
    VENTANA.blit(back_s, (ANCHO//2 - back_s.get_width()//2, 740))


def _render_poker_online_game(now):
    """Mesa de poker online — misma UI que el modo offline."""
    mouse_pos = to_logical(pygame.mouse.get_pos())

    VENTANA.fill((8, 52, 8))
    for y in range(0, ALTO, 38):
        pygame.draw.line(VENTANA, (6, 44, 6), (0, y), (ANCHO, y), 1)
    for x in range(0, ANCHO, 38):
        pygame.draw.line(VENTANA, (6, 44, 6), (x, 0), (x, ALTO), 1)
    pygame.draw.ellipse(VENTANA, (12, 80, 12), (180, 80, ANCHO-360, ALTO-160))
    pygame.draw.ellipse(VENTANA, DORADO,       (180, 80, ANCHO-360, ALTO-160), 3)
    pygame.draw.ellipse(VENTANA, (8, 60, 8),   (210, 98, ANCHO-420, ALTO-196), 1)

    title_s = _safe_render(FUENTE_PEQUENA, TR('he_title'), True, DORADO, fallback_text="TEXAS HOLD'EM")
    VENTANA.blit(title_s, (ANCHO//2 - title_s.get_width()//2, 38))

    pl = FUENTE_PEQUENA.render(TR('he_you_label'), True, (180, 240, 190))
    VENTANA.blit(pl, (ANCHO//2 - pl.get_width()//2, HE_PLAYER_Y - 30))

    cl = _FUENTE_HE_SMALL.render(TR('he_community'), True, (180, 160, 80))
    VENTANA.blit(cl, (ANCHO//2 - cl.get_width()//2, HE_COMMUNITY_Y - 26))
    for i in range(5):
        sx = _he_card_x(i, 5); sy = HE_COMMUNITY_Y
        slot = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        slot.fill((0, 0, 0, 60))
        VENTANA.blit(slot, (sx, sy))
        pygame.draw.rect(VENTANA, (80, 120, 80), (sx, sy, CARD_W, CARD_H), 1, border_radius=10)

    _ol_result_hand_map = {}
    if _online_result:
        winner_name = _online_result.get('winner', '')
        hand_nm     = _online_result.get('hand_name', '')
        if winner_name and hand_nm:
            _ol_result_hand_map[winner_name] = hand_nm

    for ai_i, (ax, ay) in enumerate(HE_AI_POSITIONS):
        if ai_i >= len(_online_other_players):
            break
        op = _online_other_players[ai_i]
        op_name  = op.get('name', '?')
        folded   = op.get('folded', False)
        op_money = op.get('money', 0)

        if folded:
            name_col = (100, 80, 80)
        elif _online_result and op_name in _ol_result_hand_map:
            name_col = (255, 160, 160)
        else:
            name_col = (220, 180, 100)

        name_s = _FUENTE_HE_SMALL.render(op_name, True, name_col)
        VENTANA.blit(name_s, (ax, ay - 22))
        money_s = _FUENTE_HE_SMALL.render(f"${op_money}", True, (160, 200, 160))
        VENTANA.blit(money_s, (ax, ay - 42))

        total_w = 2 * CARD_W + HE_AI_CARD_GAP - CARD_W
        if folded:
            fold_bg = pygame.Surface((total_w, CARD_H), pygame.SRCALPHA)
            fold_bg.fill((0, 0, 0, 60))
            VENTANA.blit(fold_bg, (ax, ay))
            pygame.draw.rect(VENTANA, (80, 50, 50), (ax, ay, total_w, CARD_H), 1, border_radius=8)
            fold_s = _FUENTE_HE_SMALL.render("RETIRADO", True, (140, 80, 80))
            VENTANA.blit(fold_s, (ax + total_w//2 - fold_s.get_width()//2,
                                   ay + CARD_H//2 - fold_s.get_height()//2))
        else:
            for ci in range(2):
                bx2 = ax + ci * HE_AI_CARD_GAP
                back = get_card_back_image()
                if back:
                    scaled = pygame.transform.smoothscale(back, (CARD_W, CARD_H))
                    VENTANA.blit(scaled, (bx2, ay))
                else:
                    slot2 = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
                    slot2.fill((0, 0, 0, 50))
                    VENTANA.blit(slot2, (bx2, ay))
                    pygame.draw.rect(VENTANA, (60, 100, 60), (bx2, ay, CARD_W, CARD_H), 1, border_radius=8)
            if _online_result and op_name in _ol_result_hand_map:
                hn_s = _FUENTE_HE_SMALL.render(_ol_result_hand_map[op_name], True, (255, 200, 180))
                VENTANA.blit(hn_s, (ax, ay + CARD_H + 6))

    for c in _online_community:
        c.target_scale = 1.12 if pygame.Rect(int(c.x), int(c.y), CARD_W, CARD_H).collidepoint(mouse_pos) else 1.0
        c.actualizar(now); c.dibujar(now)

    for c in _online_hand:
        c.target_scale = 1.12 if pygame.Rect(int(c.x), int(c.y), CARD_W, CARD_H).collidepoint(mouse_pos) else 1.0
        c.actualizar(now); c.dibujar(now)

    if _online_hand and _online_community:
        pc_live = [(c.valor, c.palo, c.valor_num, c.color) for c in _online_hand]
        cc_live = [(c.valor, c.palo, c.valor_num, c.color) for c in _online_community]
        _, live_name = evaluate_holdem_hand(pc_live + cc_live)
        hand_rank = {n: i for i, n in enumerate([
            'hand_high_card','hand_pair','hand_two_pair','hand_trips','hand_straight',
            'hand_flush','hand_full_house','hand_quads','hand_straight_flush','hand_royal_flush'
        ])}
        rank_val = hand_rank.get(live_name, 0)
        if rank_val >= 7:   live_col = (255, 220, 0)
        elif rank_val >= 4: live_col = (120, 255, 120)
        elif rank_val >= 2: live_col = (180, 220, 255)
        else:               live_col = (200, 200, 200)
        combo_bg = pygame.Surface((340, 32), pygame.SRCALPHA)
        combo_bg.fill((0, 0, 0, 170))
        combo_x = ANCHO // 2 - 170
        combo_y = HE_PLAYER_Y + CARD_H + 8
        VENTANA.blit(combo_bg, (combo_x, combo_y))
        pygame.draw.rect(VENTANA, live_col, (combo_x, combo_y, 340, 32), 1, border_radius=6)
        combo_lbl = FUENTE_PEQUENA.render(TRF('he_your_hand', v=TR(live_name)), True, live_col)
        VENTANA.blit(combo_lbl, (ANCHO//2 - combo_lbl.get_width()//2, combo_y + 4))

    pot_s = FUENTE_PEQUENA.render(TRF('he_pot', v=_online_pot), True, DORADO)
    pot_bg = pygame.Surface((pot_s.get_width()+24, pot_s.get_height()+10), pygame.SRCALPHA)
    pot_bg.fill((0, 0, 0, 160))
    px2 = ANCHO//2 - pot_bg.get_width()//2
    py2 = HE_COMMUNITY_Y + CARD_H + 14
    VENTANA.blit(pot_bg, (px2, py2))
    VENTANA.blit(pot_s, (px2+12, py2+5))

    if _online_result and _online_hand:
        ol_r_hand = _online_result.get('hand_name', '')
        phn_col = (180, 255, 180) if _online_result.get('winner') == _online_name_input else (255, 180, 180)
        phn_s = FUENTE_PEQUENA.render(TRF('he_your_hand', v=ol_r_hand), True, phn_col)
        VENTANA.blit(phn_s, (ANCHO//2 - phn_s.get_width()//2, HE_PLAYER_Y + CARD_H + 10))

    if _online_action_log and not _online_result:
        box_w_tmp = 960; bx_tmp = (ANCHO - box_w_tmp)//2; by_tmp = ALTO - 130 - 14
        last_action = _online_action_log[-1]
        turn_col  = (120, 255, 160)
        turn_surf = _safe_render(FUENTE_MSG, f"✓  {last_action}", True, turn_col, fallback_text=f"OK  {last_action}")
        turn_bg   = pygame.Surface((turn_surf.get_width() + 40, turn_surf.get_height() + 16), pygame.SRCALPHA)
        turn_bg.fill((0, 0, 0, 210))
        tx = ANCHO // 2 - turn_bg.get_width() // 2
        ty = by_tmp - turn_bg.get_height() - 12
        VENTANA.blit(turn_bg, (tx, ty))
        pygame.draw.rect(VENTANA, turn_col, (tx, ty, turn_bg.get_width(), turn_bg.get_height()), 2, border_radius=10)
        VENTANA.blit(turn_surf, (tx + 20, ty + 8))
        if len(_online_action_log) > 1:
            log_y = ty - len(_online_action_log[:-1]) * 26 - 8
            for log_line in _online_action_log[:-1]:
                log_s  = _FUENTE_HE_SMALL.render(log_line, True, (200, 200, 200))
                log_bg = pygame.Surface((log_s.get_width() + 20, log_s.get_height() + 6), pygame.SRCALPHA)
                log_bg.fill((0, 0, 0, 160))
                lx = ANCHO // 2 - log_bg.get_width() // 2
                VENTANA.blit(log_bg, (lx, log_y))
                VENTANA.blit(log_s, (lx + 10, log_y + 3))
                log_y += 26

    box_w = 960; pad = 16; lh = 32
    box_h = 130; bx = (ANCHO - box_w)//2; by = ALTO - box_h - 14
    bg_s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    bg_s.fill((0, 0, 0, 190))
    VENTANA.blit(bg_s, (bx, by))
    pygame.draw.rect(VENTANA, NEGRO, (bx, by, box_w, box_h), 2, border_radius=10)

    y_o = by + pad
    chips_s = FUENTE_PEQUENA.render(TRF('he_chips', v=_online_my_money), True, DORADO)
    VENTANA.blit(chips_s, (bx + pad, y_o))

    he_ol_menu_btn = he_menu_btn
    he_ol_rebuy_btn = pygame.Rect(ANCHO-324, ALTO-44, 152, 34)
    _draw_he_btn(TR("esc_menu"),    he_ol_menu_btn,   (30,70,140), (50,110,200), mouse_pos)
    if _online_my_money <= 0:
        _draw_he_btn(TR('poker_reload_free'), he_ol_rebuy_btn, (22,120,60), (35,170,80), mouse_pos)
    else:
        he_ol_rebuy_btn = pygame.Rect(0,0,0,0)

    is_in_game = _online_game_started and bool(_online_hand)
    is_result  = _online_result is not None

    if not is_in_game and not is_result:
        dots = '.' * ((now // 300) % 4)
        deal_s = FUENTE_PEQUENA.render(TR('poker_waiting_hand') + dots, True, (220, 200, 120))
        VENTANA.blit(deal_s, (bx + (box_w - deal_s.get_width()) // 2, y_o + lh))

    elif is_in_game and not is_result:
        street_labels = {'pre_flop': 'PRE-FLOP', 'flop': 'FLOP', 'turn': 'TURN', 'river': 'RIVER'}
        if _online_street:
            sl = FUENTE_PEQUENA.render(street_labels.get(_online_street, _online_street.upper()),
                                       True, (220, 200, 120))
            VENTANA.blit(sl, (bx + pad, y_o + lh))

        if _online_my_turn and not _online_in_raise:
            btn_w = 230; btn_h = 38; gap = 18
            total_bw = 3*btn_w + 2*gap; bx_btns = ANCHO//2 - total_bw//2
            by_btns  = by + box_h - btn_h - pad

            he_ol_fold_btn  = pygame.Rect(bx_btns,             by_btns, btn_w, btn_h)
            he_ol_call_btn  = pygame.Rect(bx_btns+btn_w+gap,   by_btns, btn_w, btn_h)
            he_ol_raise_btn = pygame.Rect(bx_btns+2*(btn_w+gap), by_btns, btn_w, btn_h)

            _draw_he_btn(TR('he_fold'),  he_ol_fold_btn,  (120,30,30),  (180,50,50),  mouse_pos)
            call_lbl = TR('he_check') if _online_to_call == 0 else TRF('he_call', amt=_online_to_call).split(" —")[0]
            _draw_he_btn(call_lbl, he_ol_call_btn, (30,80,140), (50,120,200), mouse_pos)
            _draw_he_btn(TR('he_raise_btn'), he_ol_raise_btn, (120,90,0), (200,150,0), mouse_pos, border=DORADO)
            hint2 = FUENTE_INSTR.render(TR('he_controls'),
                                        True, (120,120,120))
            VENTANA.blit(hint2, (bx + (box_w - hint2.get_width())//2, y_o + lh))

            he_ol_fold_btn_ret  = he_ol_fold_btn
            he_ol_call_btn_ret  = he_ol_call_btn
            he_ol_raise_btn_ret = he_ol_raise_btn
        else:
            he_ol_fold_btn_ret  = pygame.Rect(0,0,0,0)
            he_ol_call_btn_ret  = pygame.Rect(0,0,0,0)
            he_ol_raise_btn_ret = pygame.Rect(0,0,0,0)

        if _online_my_turn and _online_in_raise:
            rl = FUENTE_PEQUENA.render(TR('he_raise_label'), True, BLANCO)
            VENTANA.blit(rl, (bx + pad, y_o + lh*2))
            inp_x = bx + pad + rl.get_width() + 12; inp_w = 200; inp_h = 32
            inp_bg = pygame.Surface((inp_w, inp_h), pygame.SRCALPHA)
            inp_bg.fill((30, 20, 0, 230))
            VENTANA.blit(inp_bg, (inp_x, y_o + lh*2 - 2))
            pygame.draw.rect(VENTANA, DORADO, (inp_x, y_o + lh*2 - 2, inp_w, inp_h), 2, border_radius=6)
            disp2 = clip_text_right(_online_raise_input + ('|' if (now//400)%2==0 else ''),
                                    FUENTE_PEQUENA, inp_w-12)
            dt2 = FUENTE_PEQUENA.render(disp2, True, BLANCO)
            VENTANA.blit(dt2, (inp_x+8, y_o + lh*2 + (inp_h-dt2.get_height())//2 - 2))
            cancel_s = FUENTE_INSTR.render(TR('he_confirm_cancel'), True, (180,160,100))
            VENTANA.blit(cancel_s, (bx + (box_w - cancel_s.get_width())//2, y_o + lh*3))
        elif not _online_my_turn:
            wait_s = FUENTE_PEQUENA.render(TR('poker_waiting_turn'), True, (160, 160, 160))
            VENTANA.blit(wait_s, (bx + pad, y_o + lh))

    elif is_result:
        winner  = _online_result.get('winner', '?')
        hand_nm = _online_result.get('hand_name', '')
        pot_won = _online_result.get('pot', 0)
        is_me   = (winner == _online_name_input)
        res_col = DORADO if is_me else ROJO
        if is_me:
            mensaje = TRF('poker_you_won_hand', hand=hand_nm, pot=pot_won)
        else:
            mensaje = TRF('poker_they_won_hand', winner=winner, hand=hand_nm)
        msg_s = FUENTE_MSG.render(mensaje, True, res_col)
        VENTANA.blit(msg_s, (ANCHO//2 - msg_s.get_width()//2, by + (box_h - msg_s.get_height())//2 - 10))
        hint3 = FUENTE_INSTR.render(TR('poker_waiting_next_hand'), True, (140,140,140))
        VENTANA.blit(hint3, (ANCHO//2 - hint3.get_width()//2, by + box_h - hint3.get_height() - 8))
        he_ol_fold_btn_ret  = pygame.Rect(0,0,0,0)
        he_ol_call_btn_ret  = pygame.Rect(0,0,0,0)
        he_ol_raise_btn_ret = pygame.Rect(0,0,0,0)

    else:
        he_ol_fold_btn_ret  = pygame.Rect(0,0,0,0)
        he_ol_call_btn_ret  = pygame.Rect(0,0,0,0)
        he_ol_raise_btn_ret = pygame.Rect(0,0,0,0)

    if _online_message and not is_result:
        msg_s2 = FUENTE_PEQUENA.render(_online_message, True, (255,200,100))
        VENTANA.blit(msg_s2, (ANCHO//2 - msg_s2.get_width()//2, ALTO//2))

    if _online_my_money <= 0:
        low_s = FUENTE_INSTR.render(TR('poker_no_chips_reload'), True, (255, 180, 120))
        VENTANA.blit(low_s, (ANCHO//2 - low_s.get_width()//2, by - 28))

    return (he_ol_menu_btn,
            he_ol_fold_btn_ret, he_ol_call_btn_ret,
            he_ol_call_btn_ret, he_ol_raise_btn_ret, he_ol_rebuy_btn)


def _menu_options():
    return [
        {'label': TR('menu_story_label'), 'sub': TR('menu_story_sub')},
        {'label': TR('menu_bj_label'),    'sub': TR('menu_bj_sub')},
        {'label': TR('menu_poker_label'), 'sub': TR('menu_poker_sub')},
        {'label': TR('menu_update_label'),'sub': TR('menu_update_sub')},
    ]

MENU_OPTIONS = _menu_options()

FUENTE_MENU_TITLE = pygame.font.SysFont("arial", 92, bold=True)
FUENTE_MENU_OPT   = pygame.font.SysFont("arial", 44, bold=True)
FUENTE_MENU_SUB   = pygame.font.SysFont("arial", 24)

def _download_noto_emoji():
    """Descarga NotoColorEmoji.ttf si no existe (URL oficial del README del repo)."""
    font_dir  = os.path.join(DATA_DIR, "fonts")
    font_path = os.path.join(font_dir, "NotoColorEmoji.ttf")
    if os.path.exists(font_path):
        return font_path
    url = "https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf"
    try:
        os.makedirs(font_dir, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        with open(font_path, "wb") as f:
            f.write(data)
        return font_path
    except Exception as e:
        print(f"[EMOJI FONT] No se pudo descargar NotoColorEmoji: {e}")
        return None

def _font_can_render(font, sample="📁"):
    """Comprueba que una fuente realmente puede dibujar el carácter dado."""
    try:
        return font.render(sample, True, (255, 255, 255)).get_width() > 0
    except pygame.error:
        return False


def _load_emoji_font(size):
    """Carga NotoColorEmoji descargada o busca una del sistema.

    Solo devuelve una fuente si de verdad puede renderizar emojis; si
    ninguna funciona (típico en Windows/Wine sin fuente de emoji
    instalada) devolvemos Arial igualmente, pero _safe_render() se
    encargará de no crashear cuando falte el glifo.
    """
    font_path = os.path.join(DATA_DIR, "fonts", "NotoColorEmoji.ttf")
    if os.path.exists(font_path):
        try:
            f = pygame.font.Font(font_path, size)
            if _font_can_render(f):
                return f
        except Exception:
            pass
    for name in ["Noto Color Emoji", "Segoe UI Emoji", "Apple Color Emoji",
                 "Noto Emoji", "Noto Sans Symbols2", "DejaVu Sans"]:
        try:
            path = pygame.font.match_font(name)
            if path:
                f = pygame.font.Font(path, size)
                if _font_can_render(f):
                    return f
        except Exception:
            pass
    return pygame.font.SysFont("arial", size, bold=True)

threading.Thread(target=_download_noto_emoji, daemon=True).start()

FUENTE_EMOJI = _load_emoji_font(22)

_emoji_font_checked = False
def _get_emoji_font():
    """Recarga FUENTE_EMOJI si NotoColorEmoji ya se descargó."""
    global FUENTE_EMOJI, _emoji_font_checked
    if not _emoji_font_checked:
        fp = os.path.join(DATA_DIR, "fonts", "NotoColorEmoji.ttf")
        if os.path.exists(fp):
            try:
                f = pygame.font.Font(fp, 22)
                if _font_can_render(f):
                    FUENTE_EMOJI = f
            except Exception:
                pass
            _emoji_font_checked = True
    return FUENTE_EMOJI

_MENU_BTN_BASE_W = 860
_MENU_BTN_H = 110
_MENU_BTN_GAP = 24
_MENU_BTN_START_Y = 380
_MENU_BTN_POKER_EXTRA_W = 28
_MENU_HOVER_TARGET = 1.045
_menu_btn_scales = [1.0 for _ in MENU_OPTIONS]
main_menu_button_rects = []
_hard_reset_confirm = False

settings_open      = False
_settings_anim     = 0.0     
_settings_gear_scale = 1.0
_settings_dragging_volume = False
_settings_pending_resolution = CONFIG.get('resolution', '1920x1080')
_settings_restart_hint = False
_settings_applied_at = -999999

_GEAR_BTN_RECT = pygame.Rect(24, 24, 56, 56)

def apply_resolution(res_key):
    """
    Cambia la resolucion del juego en caliente (sin reiniciar el proceso).

    Recrea la ventana/superficie real con el nuevo tamano y recalcula todas
    las constantes de layout (posiciones de mazo, botones, etc.) que se
    calcularon una sola vez a partir de ANCHO/ALTO al arrancar el juego.
    """
    global ANCHO, ALTO, IS_WINDOWED, VENTANA_REAL, VENTANA
    global DECK_POS, DEALER_POS, PLAYER_STACK_POS, BANK_POS, _CARD_X_ORIGIN, _RAIN
    global DOTS_BTN, REINICIAR_BTN, MUTE_BTN, bj_menu_btn
    global HE_DECK_X, HE_COMMUNITY_Y, HE_PLAYER_Y, he_menu_btn, he_reiniciar_btn
    global _settings_applied_at

    new_windowed = (res_key == 'windowed')
    new_ancho, new_alto = _RESOLUTIONS.get(res_key, (1920, 1080))
    if new_windowed:
        new_ancho, new_alto = 1280, 720

    if new_ancho == ANCHO and new_alto == ALTO and new_windowed == IS_WINDOWED:
        CONFIG['resolution'] = res_key
        save_config()
        return

    flags = pygame.SCALED if new_windowed else (pygame.FULLSCREEN | pygame.SCALED)
    try:
        new_ventana_real = pygame.display.set_mode((new_ancho, new_alto), flags)
    except pygame.error as e:
        print(f"[RESOLUTION] No se pudo cambiar de resolucion: {e}")
        return

    ANCHO, ALTO = new_ancho, new_alto
    IS_WINDOWED = new_windowed
    VENTANA_REAL = new_ventana_real
    VENTANA = pygame.Surface((ANCHO, ALTO))

    DECK_POS          = (ANCHO // 2, 20)
    DEALER_POS        = (ANCHO // 2, 60)
    PLAYER_STACK_POS  = (120, ALTO - 70)
    BANK_POS          = (ANCHO // 2, 40)
    _CARD_X_ORIGIN    = ANCHO // 2 - CARD_SPACING // 2 - CARD_W // 2

    _RAIN[:] = [(_RRNG.randint(0, ANCHO), _RRNG.randint(0, ALTO),
                 _RRNG.uniform(200, 460), _RRNG.randint(12, 34))
                for _ in range(140)]

    DOTS_BTN      = pygame.Rect(ANCHO-46,  8,   38,  28)
    REINICIAR_BTN = pygame.Rect(ANCHO-140, ALTO-44, 130, 34)
    MUTE_BTN      = pygame.Rect(ANCHO-90,  8,   38,  28)
    bj_menu_btn   = pygame.Rect(ANCHO - 160, ALTO - 44, 148, 34)

    HE_DECK_X        = ANCHO // 2
    HE_COMMUNITY_Y   = ALTO // 2 - 72
    HE_PLAYER_Y      = ALTO - 230
    he_menu_btn      = pygame.Rect(ANCHO-164, ALTO-44, 152, 34)
    he_reiniciar_btn = pygame.Rect(ANCHO-324, ALTO-44, 152, 34)

    main_menu_button_rects[:] = [_main_menu_rect(i) for i in range(len(MENU_OPTIONS))]

    _story_scaled_cache.clear()

    CONFIG['resolution'] = res_key
    save_config()
    _settings_applied_at = pygame.time.get_ticks()

def open_settings():
    global settings_open, _settings_pending_resolution, _settings_restart_hint
    settings_open = True
    _settings_pending_resolution = CONFIG.get('resolution', '1920x1080')
    _settings_restart_hint = False

def close_settings(save=True):
    global settings_open, _settings_dragging_volume
    if save:
        save_config()
    settings_open = False
    _settings_dragging_volume = False

def _draw_gear_icon(surf, cx, cy, radius, color):
    """Dibuja un icono de engranaje sencillo mediante primitivas de pygame."""
    import math as _m
    radius = int(radius)
    teeth = 8
    for i in range(teeth):
        ang = (2 * _m.pi / teeth) * i
        x1 = cx + _m.cos(ang) * (radius * 0.62)
        y1 = cy + _m.sin(ang) * (radius * 0.62)
        x2 = cx + _m.cos(ang) * (radius * 1.05)
        y2 = cy + _m.sin(ang) * (radius * 1.05)
        pygame.draw.line(surf, color, (int(x1), int(y1)), (int(x2), int(y2)), max(3, radius // 5))
    pygame.draw.circle(surf, color, (int(cx), int(cy)), int(radius * 0.62), max(2, radius // 6))
    pygame.draw.circle(surf, color, (int(cx), int(cy)), int(radius * 0.24))

def draw_settings_gear_button(surf, now, mouse_pos):
    """Dibuja el boton de engranaje con una pequena animacion de hover."""
    global _settings_gear_scale
    hovered = _GEAR_BTN_RECT.collidepoint(mouse_pos) and not settings_open and not _hard_reset_confirm
    target = 1.18 if hovered else 1.0
    _settings_gear_scale += (target - _settings_gear_scale) * 0.2
    r = int(28 * _settings_gear_scale)
    cx, cy = _GEAR_BTN_RECT.center
    bg_col = (55, 95, 68) if hovered else (22, 36, 26)
    border_col = DORADO if hovered else (70, 110, 80)
    pygame.draw.circle(surf, bg_col, (cx, cy), r + 10)
    pygame.draw.circle(surf, border_col, (cx, cy), r + 10, 2)
    gear_col = (220, 255, 225) if hovered else BLANCO
    _draw_gear_icon(surf, cx, cy, r * 0.55, gear_col)
    return hovered

_SETTINGS_PANEL_W = 640
_SETTINGS_PANEL_H = 560

def _settings_panel_rect(anim):
    """El panel entra deslizandose y con fade, controlado por 'anim' (0-1)."""
    ease = 1 - (1 - anim) ** 3  
    w, h = _SETTINGS_PANEL_W, _SETTINGS_PANEL_H
    x = (ANCHO - w) // 2
    y_target = (ALTO - h) // 2
    y_start = y_target - 40
    y = int(y_start + (y_target - y_start) * ease)
    return pygame.Rect(x, y, w, h), ease

def render_settings_panel(surf, now, mouse_pos, mouse_pressed):
    """Dibuja (y anima la apertura/cierre de) el panel de ajustes."""
    global _settings_anim, settings_open

    target_anim = 1.0 if settings_open else 0.0
    _settings_anim += (target_anim - _settings_anim) * 0.22
    if not settings_open and _settings_anim < 0.01:
        _settings_anim = 0.0
        return {}
    if settings_open and _settings_anim > 0.995:
        _settings_anim = 1.0

    anim = _settings_anim
    ov = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    ov.fill((0, 0, 0, int(180 * anim)))
    surf.blit(ov, (0, 0))

    rect, ease = _settings_panel_rect(anim)
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill((20, 22, 18, int(245 * ease)))
    surf.blit(panel, rect.topleft)
    pygame.draw.rect(surf, DORADO, rect, 2, border_radius=16)

    hit = {}
    if ease < 0.35:
        return hit 

    font_title = pygame.font.SysFont("arial", 40, bold=True)
    font_label = pygame.font.SysFont("arial", 24, bold=True)
    font_small = pygame.font.SysFont("arial", 19)

    pad = 40
    y = rect.y + 32
    title_s = font_title.render(TR('settings_title'), True, DORADO)
    surf.blit(title_s, (rect.x + pad, y))

    close_r = pygame.Rect(rect.right - 60, rect.y + 24, 36, 36)
    close_hov = close_r.collidepoint(mouse_pos)
    pygame.draw.rect(surf, (90, 30, 30) if close_hov else (50, 20, 20), close_r, border_radius=8)
    pygame.draw.rect(surf, (220, 90, 90), close_r, 1, border_radius=8)
    x_s = font_label.render("X", True, BLANCO)
    surf.blit(x_s, (close_r.centerx - x_s.get_width() // 2, close_r.centery - x_s.get_height() // 2))
    hit['close'] = close_r

    y += 70

    vol_label = font_label.render(f"{TR('settings_volume')}: {int(CONFIG['volume']*100)}%", True, BLANCO)
    surf.blit(vol_label, (rect.x + pad, y))
    y += 36
    slider_w = rect.width - pad * 2
    slider_r = pygame.Rect(rect.x + pad, y, slider_w, 10)
    pygame.draw.rect(surf, (60, 60, 60), slider_r, border_radius=5)
    fill_w = max(0, min(slider_w, int(slider_w * CONFIG['volume'])))
    pygame.draw.rect(surf, DORADO, (slider_r.x, slider_r.y, fill_w, slider_r.height), border_radius=5)
    knob_x = slider_r.x + fill_w
    pygame.draw.circle(surf, BLANCO, (knob_x, slider_r.centery), 10)
    pygame.draw.circle(surf, DORADO, (knob_x, slider_r.centery), 10, 2)
    hit['volume_slider'] = slider_r
    y += 44

    res_label = font_label.render(TR('settings_resolution'), True, BLANCO)
    surf.blit(res_label, (rect.x + pad, y))
    y += 34
    res_rects = []
    bx = rect.x + pad
    res_labels = {
        '1920x1080': '1920×1080',
        '1600x900':  '1600×900',
        '1280x720':  '1280×720',
        'windowed':  TR('settings_windowed'),
    }
    for res_key in _RESOLUTION_ORDER:
        lbl = res_labels[res_key]
        w_btn = font_small.size(lbl)[0] + 28
        r_btn = pygame.Rect(bx, y, w_btn, 34)
        selected = (_settings_pending_resolution == res_key)
        hov = r_btn.collidepoint(mouse_pos)
        bgc = (60, 100, 70) if selected else ((45, 45, 50) if hov else (32, 32, 36))
        pygame.draw.rect(surf, bgc, r_btn, border_radius=8)
        pygame.draw.rect(surf, DORADO if selected else (90, 90, 95), r_btn, 1, border_radius=8)
        lbl_s = font_small.render(lbl, True, BLANCO)
        surf.blit(lbl_s, (r_btn.centerx - lbl_s.get_width() // 2, r_btn.centery - lbl_s.get_height() // 2))
        res_rects.append((res_key, r_btn))
        bx += w_btn + 10
    hit['resolution_buttons'] = res_rects
    y += 50
    _since_applied = now - _settings_applied_at
    if _settings_restart_hint and 0 <= _since_applied < 1800:
        fade = 1.0 - max(0.0, (_since_applied - 1200) / 600) if _since_applied > 1200 else 1.0
        alpha = max(0, min(255, int(255 * fade)))
        applied_s = _safe_render(font_small, f"{TR('settings_applied')} ✓", True, (150, 230, 150),
                                  fallback_text=TR('settings_applied'))
        applied_s.set_alpha(alpha)
        surf.blit(applied_s, (rect.x + pad, y))
    y += 28

    lang_label = font_label.render(TR('settings_language'), True, BLANCO)
    surf.blit(lang_label, (rect.x + pad, y))
    y += 34
    lang_rects = []
    bx = rect.x + pad
    for lang_key, lbl in (('es', 'Espanol'), ('en', 'English')):
        w_btn = font_small.size(lbl)[0] + 28
        r_btn = pygame.Rect(bx, y, w_btn, 34)
        selected = (CONFIG.get('language') == lang_key)
        hov = r_btn.collidepoint(mouse_pos)
        bgc = (60, 100, 70) if selected else ((45, 45, 50) if hov else (32, 32, 36))
        pygame.draw.rect(surf, bgc, r_btn, border_radius=8)
        pygame.draw.rect(surf, DORADO if selected else (90, 90, 95), r_btn, 1, border_radius=8)
        lbl_s = font_small.render(lbl, True, BLANCO)
        surf.blit(lbl_s, (r_btn.centerx - lbl_s.get_width() // 2, r_btn.centery - lbl_s.get_height() // 2))
        lang_rects.append((lang_key, r_btn))
        bx += w_btn + 10
    hit['language_buttons'] = lang_rects
    y += 56

    auto_label = font_label.render(TR('settings_autoupdate'), True, BLANCO)
    surf.blit(auto_label, (rect.x + pad, y))
    toggle_r = pygame.Rect(rect.right - pad - 90, y - 6, 90, 34)
    on = bool(CONFIG.get('autoupdate', True))
    pygame.draw.rect(surf, (50, 110, 60) if on else (70, 40, 40), toggle_r, border_radius=17)
    knob_cx = toggle_r.right - 20 if on else toggle_r.left + 20
    pygame.draw.circle(surf, BLANCO, (knob_cx, toggle_r.centery), 13)
    onoff_s = font_small.render(TR('settings_on') if on else TR('settings_off'), True, (200, 255, 200) if on else (255, 200, 200))
    surf.blit(onoff_s, (rect.x + pad, y + 26))
    hit['autoupdate_toggle'] = toggle_r
    y += 70

    hint2 = font_small.render(TR('settings_hint'), True, (150, 150, 150))
    surf.blit(hint2, (rect.x + pad, rect.bottom - 40))

    return hit

def handle_settings_click(pos):
    """Procesa un clic dentro del panel de ajustes. Devuelve True si se consumio el clic."""
    global settings_open, _settings_pending_resolution, _settings_restart_hint
    hit = getattr(render_settings_panel, '_last_hit', None)
    if not hit:
        return False
    if 'close' in hit and hit['close'].collidepoint(pos):
        close_settings(save=True)
        return True
    if 'resolution_buttons' in hit:
        for res_key, r_btn in hit['resolution_buttons']:
            if r_btn.collidepoint(pos):
                _settings_pending_resolution = res_key
                apply_resolution(res_key)
                _settings_restart_hint = True
                return True
    if 'language_buttons' in hit:
        for lang_key, r_btn in hit['language_buttons']:
            if r_btn.collidepoint(pos):
                CONFIG['language'] = lang_key
                save_config()
                _refresh_language_texts()
                return True
    if 'autoupdate_toggle' in hit and hit['autoupdate_toggle'].collidepoint(pos):
        CONFIG['autoupdate'] = not bool(CONFIG.get('autoupdate', True))
        save_config()
        return True
    if 'volume_slider' in hit and hit['volume_slider'].collidepoint(pos):
        return True
    return False

def _refresh_language_texts():
    """Reconstruye textos dependientes del idioma (menu principal, etc.)."""
    global MENU_OPTIONS
    MENU_OPTIONS[:] = _menu_options()

def _do_hard_reset():
    """Borra la carpeta de datos de ElFarolRojo y reinicia el juego desde cero."""
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
    try:
        os.chdir(os.path.expanduser('~'))
        shutil.rmtree(DATA_DIR, ignore_errors=True)
    except Exception as e:
        print(f"[RESET] Error borrando datos: {e}")
    _restart_process()

def _main_menu_rect(i):
    w = _MENU_BTN_BASE_W + (_MENU_BTN_POKER_EXTRA_W if i == 2 else 0)
    x = (ANCHO - w) // 2
    y = _MENU_BTN_START_Y + i * (_MENU_BTN_H + _MENU_BTN_GAP)
    return pygame.Rect(x, y, w, _MENU_BTN_H)

def _ensure_main_menu_music():
    """Reproduce Coffee Time siempre que el usuario esté en el menú principal."""
    global _music_context
    try:
        if _music_context != 'menu' or not pygame.mixer.music.get_busy():
            if os.path.exists(_MUSIC_LOCAL):
                pygame.mixer.music.load(_MUSIC_LOCAL)
                pygame.mixer.music.set_volume(eff_vol(_music_volume))
                pygame.mixer.music.play(-1)
                _music_context = 'menu'
            else:
                threading.Thread(target=_download_and_start_music, daemon=True).start()
    except Exception as e:
        print(f"[MUSIC] No se pudo asegurar la música del menú: {e}")


def _render_main_menu(now):
    """Draw the main menu screen."""
    global main_menu_hovered, main_menu_button_rects
    _ensure_main_menu_music()
    VENTANA.fill((6, 4, 14))
    draw_rain(VENTANA, now, alpha=55)

    t_surf = FUENTE_MENU_TITLE.render("El Farol Rojo", True, DORADO)
    t_x = (ANCHO - t_surf.get_width()) // 2
    VENTANA.blit(t_surf, (t_x, 120))

    sub_surf = FUENTE_SUBTITLE.render(TR('menu_subtitle'), True, (160, 140, 90))
    VENTANA.blit(sub_surf, ((ANCHO - sub_surf.get_width()) // 2, 230))

    pygame.draw.line(VENTANA, DORADO, (ANCHO//2 - 340, 310), (ANCHO//2 + 340, 310), 1)

    mouse_pos = to_logical(pygame.mouse.get_pos())
    draw_settings_gear_button(VENTANA, now, mouse_pos)
    main_menu_hovered = -1
    main_menu_button_rects = []
    btn_start_y = _MENU_BTN_START_Y

    menu_locked = _hard_reset_confirm or settings_open

    for i, opt in enumerate(MENU_OPTIONS):
        base_rect = _main_menu_rect(i)
        hovered = base_rect.collidepoint(mouse_pos) and not menu_locked
        if hovered:
            main_menu_hovered = i

        target = _MENU_HOVER_TARGET if hovered else 1.0
        _menu_btn_scales[i] += (target - _menu_btn_scales[i]) * 0.18
        scale = _menu_btn_scales[i]

        draw_w = max(1, int(base_rect.width * scale))
        draw_h = max(1, int(base_rect.height * scale))
        draw_x = base_rect.centerx - draw_w // 2
        draw_y = base_rect.centery - draw_h // 2 - (3 if hovered else 0)
        draw_rect = pygame.Rect(draw_x, draw_y, draw_w, draw_h)
        main_menu_button_rects.append(draw_rect)

        if menu_locked:
            bg_alpha = 120
            bg_col = (26, 28, 30)
            border_col = (90, 90, 95)
            lbl_col = (170, 170, 175)
            sub_col = (115, 115, 120)
        else:
            bg_alpha = 220 if hovered else 160
            bg_col = (55, 95, 68) if hovered else (22, 36, 26)
            border_col = DORADO if hovered else (70, 110, 80)
            lbl_col = (220, 255, 225) if hovered else BLANCO
            sub_col = (160, 190, 165) if hovered else (120, 140, 125)

        bg_s = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
        bg_s.fill((*bg_col, bg_alpha))
        VENTANA.blit(bg_s, (draw_x, draw_y))
        pygame.draw.rect(VENTANA, border_col, draw_rect, 2, border_radius=10)

        lbl_s = FUENTE_MENU_OPT.render(opt['label'], True, lbl_col)
        lbl_y = draw_y + 18
        VENTANA.blit(lbl_s, (draw_x + 36, lbl_y))
        sub_s = FUENTE_MENU_SUB.render(opt['sub'], True, sub_col)
        VENTANA.blit(sub_s, (draw_x + 38, lbl_y + lbl_s.get_height() + 4))

    hint = FUENTE_INSTR.render(TR('menu_hint'), True, (90, 80, 60) if not menu_locked else (70, 70, 75))
    VENTANA.blit(hint, ((ANCHO - hint.get_width()) // 2, btn_start_y + len(MENU_OPTIONS) * (_MENU_BTN_H + _MENU_BTN_GAP) - 4))

    folder_btn_w = 470
    folder_btn_h = 50
    folder_btn_x = (ANCHO - folder_btn_w) // 2
    folder_btn_y = btn_start_y + len(MENU_OPTIONS) * (_MENU_BTN_H + _MENU_BTN_GAP) + 30
    folder_rect = pygame.Rect(folder_btn_x, folder_btn_y, folder_btn_w, folder_btn_h)
    folder_hov = folder_rect.collidepoint(mouse_pos) and not menu_locked
    fb_col = (45, 70, 55) if folder_hov else ((28, 32, 30) if menu_locked else (25, 40, 32))
    fb_s = pygame.Surface((folder_btn_w, folder_btn_h), pygame.SRCALPHA)
    fb_s.fill((*fb_col, 220 if not menu_locked else 140))
    VENTANA.blit(fb_s, (folder_btn_x, folder_btn_y))
    fb_border = DORADO if folder_hov else ((90, 90, 95) if menu_locked else (55, 90, 65))
    pygame.draw.rect(VENTANA, fb_border, folder_rect, 1, border_radius=8)

    folder_text_font = pygame.font.SysFont("arial", 21, bold=True)
    icon_col = (230, 250, 235) if folder_hov else ((155, 155, 160) if menu_locked else (160, 190, 165))
    icon_surf = _safe_render(_get_emoji_font(), "📁", True, icon_col, fallback_text="[+]")
    icon_surf = pygame.transform.smoothscale(
        icon_surf,
        (max(1, int(icon_surf.get_width() * 0.60)), max(1, int(icon_surf.get_height() * 0.60)))
    )
    text_surf = folder_text_font.render(TR('menu_open_folder'), True, icon_col)
    ix = folder_btn_x + 18
    iy = folder_btn_y + (folder_btn_h - icon_surf.get_height()) // 2 - 1
    tx = ix + icon_surf.get_width() + 12
    ty = folder_btn_y + (folder_btn_h - text_surf.get_height()) // 2 + 1
    VENTANA.blit(icon_surf, (ix, iy))
    VENTANA.blit(text_surf, (tx, ty))
    _render_main_menu._folder_rect = folder_rect

    reset_btn_w = 470
    reset_btn_h = 50
    reset_btn_x = (ANCHO - reset_btn_w) // 2
    reset_btn_y = folder_btn_y + folder_btn_h + 12
    reset_rect  = pygame.Rect(reset_btn_x, reset_btn_y, reset_btn_w, reset_btn_h)
    reset_hov   = reset_rect.collidepoint(mouse_pos) and not menu_locked
    rb_col      = (90, 28, 28) if reset_hov else ((28, 14, 14) if menu_locked else (40, 12, 12))
    rb_s        = pygame.Surface((reset_btn_w, reset_btn_h), pygame.SRCALPHA)
    rb_s.fill((*rb_col, 210 if not menu_locked else 140))
    VENTANA.blit(rb_s, (reset_btn_x, reset_btn_y))
    rb_border   = (220, 70, 70) if reset_hov else ((110, 85, 85) if menu_locked else (100, 35, 35))
    pygame.draw.rect(VENTANA, rb_border, reset_rect, 1, border_radius=8)
    reset_text_font = pygame.font.SysFont("arial", 20, bold=True)
    icon_col_r  = (255, 190, 190) if reset_hov else ((145, 110, 110) if menu_locked else (165, 90, 90))
    reset_icon  = _safe_render(_get_emoji_font(), "⚠", True, icon_col_r, fallback_text="!")
    reset_icon  = pygame.transform.smoothscale(
        reset_icon,
        (max(1, int(reset_icon.get_width() * 0.58)), max(1, int(reset_icon.get_height() * 0.58)))
    )
    reset_text  = reset_text_font.render(TR('menu_hard_reset'), True, icon_col_r)
    rix = reset_btn_x + 18
    riy = reset_btn_y + (reset_btn_h - reset_icon.get_height()) // 2 - 1
    rtx = rix + reset_icon.get_width() + 12
    rty = reset_btn_y + (reset_btn_h - reset_text.get_height()) // 2 + 1
    VENTANA.blit(reset_icon, (rix, riy))
    VENTANA.blit(reset_text, (rtx, rty))
    _render_main_menu._hard_reset_rect = reset_rect
    if _hard_reset_confirm:
        ov2 = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        ov2.fill((0, 0, 0, 185))
        VENTANA.blit(ov2, (0, 0))
        dlg_w, dlg_h = 700, 270
        dlg_x = (ANCHO - dlg_w) // 2
        dlg_y = (ALTO  - dlg_h) // 2
        dlg_s = pygame.Surface((dlg_w, dlg_h), pygame.SRCALPHA)
        dlg_s.fill((18, 6, 6, 245))
        VENTANA.blit(dlg_s, (dlg_x, dlg_y))
        pygame.draw.rect(VENTANA, (210, 55, 55), (dlg_x, dlg_y, dlg_w, dlg_h), 2, border_radius=14)
        warn_s = FUENTE_MSG.render(TR('erase_title'), True, (255, 110, 110))
        VENTANA.blit(warn_s, (dlg_x + (dlg_w - warn_s.get_width()) // 2, dlg_y + 30))
        sub_s2 = FUENTE_MENU_SUB.render(
            TR('erase_line1'), True, (200, 155, 155))
        VENTANA.blit(sub_s2, (dlg_x + (dlg_w - sub_s2.get_width()) // 2, dlg_y + 95))
        sub_s3 = FUENTE_MENU_SUB.render(
            TR('erase_line2'), True, (170, 130, 130))
        VENTANA.blit(sub_s3, (dlg_x + (dlg_w - sub_s3.get_width()) // 2, dlg_y + 125))
        btn_y2      = dlg_y + 170
        confirm_r   = pygame.Rect(dlg_x + 70,  btn_y2, 240, 62)
        cancel_r    = pygame.Rect(dlg_x + dlg_w - 310, btn_y2, 240, 62)
        conf_hov    = confirm_r.collidepoint(mouse_pos)
        canc_hov    = cancel_r.collidepoint(mouse_pos)
        pygame.draw.rect(VENTANA, (170, 35, 35) if conf_hov else (90, 18, 18), confirm_r, border_radius=9)
        pygame.draw.rect(VENTANA, (230, 70, 70), confirm_r, 2, border_radius=9)
        pygame.draw.rect(VENTANA, (30, 75, 44)  if canc_hov else (16, 44, 26), cancel_r,  border_radius=9)
        pygame.draw.rect(VENTANA, (65, 170, 90), cancel_r,  2, border_radius=9)
        conf_txt = FUENTE_MENU_SUB.render(TR('erase_confirm'), True, BLANCO)
        canc_txt = FUENTE_MENU_SUB.render(TR('erase_cancel'),           True, BLANCO)
        VENTANA.blit(conf_txt, (confirm_r.centerx - conf_txt.get_width() // 2,
                                 confirm_r.centery - conf_txt.get_height() // 2))
        VENTANA.blit(canc_txt, (cancel_r.centerx  - canc_txt.get_width() // 2,
                                 cancel_r.centery  - canc_txt.get_height() // 2))
        _render_main_menu._confirm_rect = confirm_r
        _render_main_menu._cancel_rect  = cancel_r

    ver_s = FUENTE_INSTR.render(f"v{VERSION}", True, (60, 55, 45))
    VENTANA.blit(ver_s, (ANCHO - ver_s.get_width() - 14, ALTO - ver_s.get_height() - 10))

    if update_status is not None:
        elapsed_notif = now - update_notif_time
        is_permanent  = update_status in ('checking', 'restarting')
        show_notif    = is_permanent or (elapsed_notif < 6000)
        if show_notif:
            alpha_notif = 230
            if not is_permanent and elapsed_notif > 4500:
                alpha_notif = max(0, int(230 * (1 - (elapsed_notif - 4500) / 1500)))
            if update_status == 'restarting':
                notif_color = (20, 100, 200)
                secs_left   = max(0, 2 - (now - update_restart_time) // 1000)
                display_msg = TRF('updated_restarting', secs=secs_left)
            else:
                display_msg = update_msg
                notif_color = (30, 120, 50) if update_status == 'up_to_date' else \
                              (40, 40, 40)  if update_status == 'checking'   else (150, 30, 30)
            notif_surf = FUENTE_PEQUENA.render(display_msg, True, BLANCO)
            nw = notif_surf.get_width() + 24; nh = notif_surf.get_height() + 14
            nx = ANCHO - nw - 14; ny = ALTO - nh - 36
            bg = pygame.Surface((nw, nh), pygame.SRCALPHA)
            bg.fill((*notif_color, alpha_notif))
            VENTANA.blit(bg, (nx, ny))
            pygame.draw.rect(VENTANA, NEGRO, (nx, ny, nw, nh), 1, border_radius=6)
            VENTANA.blit(notif_surf, (nx + 12, ny + 7))

    _MENU_FADE_MS = 900
    elapsed_fade = now - _menu_fade_start
    if elapsed_fade < _MENU_FADE_MS:
        alpha_fade = max(0, int(255 * (1.0 - elapsed_fade / _MENU_FADE_MS)))
        ov = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        ov.fill((0, 0, 0, alpha_fade))
        VENTANA.blit(ov, (0, 0))

    mouse_pressed = pygame.mouse.get_pressed()[0]
    hit = render_settings_panel(VENTANA, now, mouse_pos, mouse_pressed)
    render_settings_panel._last_hit = hit


_pause_started_at = 0
main_menu_button_rects = [_main_menu_rect(i) for i in range(len(MENU_OPTIONS))]

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

    title_surf = FUENTE_GRANDE.render(TR("pause_title"), True, DORADO)
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
        (TR('pause_resume'), BY0, False),
        (TR('pause_menu'), BY1, True),
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

    hint = FUENTE_INSTR.render(TR("pause_hint"), True, (90, 80, 60))
    VENTANA.blit(hint, (ANCHO // 2 - hint.get_width() // 2, BY1 + BTN_H + 22))


def _start_story_mode():
    global app_state, game_mode, story_scenes_data, story_scene_idx, story_line_idx
    global player_money, current_bet, current_bet_input, last_bet, stats, epic_win_triggered
    global difficulty_level, EPIC_WIN_THRESHOLD, rosa_secret_done, _story_current_track
    global story_choice_active, story_choice_options, story_choice_rects
    global story_injected_lines, story_injected_idx, story_in_injection
    game_mode = 'story'
    player_money = 1000; current_bet = 10; current_bet_input = ""; last_bet = None
    stats = {'played':0,'won':0,'lost':0,'blackjacks':0}; epic_win_triggered = False
    difficulty_level = 0; EPIC_WIN_THRESHOLD = 10000; rosa_secret_done = False
    story_scenes_data = INTRO_SCENES; story_scene_idx = 0; story_line_idx = 0
    story_choice_active = False; story_choice_options = []; story_choice_rects = []
    story_injected_lines = []; story_injected_images = []; story_injected_idx = 0; story_in_injection = False
    _story_current_track = None
    _play_story_track('lluvia', volume=0.16, loop=True, fade_out_ms=1300)
    app_state = 'intro'


def _start_infinite_mode():
    global app_state, game_mode
    game_mode = 'infinite'
    app_state = 'blackjack'
    bj_reiniciar()


def splash_screen():
    """Muestra el logo del juego con fade-in y fade-out antes de entrar al menú."""
    _LOGO_URL        = "https://raw.githubusercontent.com/humrand/blackjack-python/main/imagenes/logo.png"
    _LOGO_LOCAL      = os.path.join("imagenes", "logo.png")
    _LOGO_KEVIN_URL  = "https://raw.githubusercontent.com/humrand/blackjack-python/main/imagenes/logo-kevin.jpg"
    _LOGO_KEVIN_LOCAL= os.path.join("imagenes", "logo-kevin.jpg")

    _ensure_imagenes_dir()
    for _url, _local in ((_LOGO_URL, _LOGO_LOCAL), (_LOGO_KEVIN_URL, _LOGO_KEVIN_LOCAL)):
        if not os.path.exists(_local):
            try:
                req = urllib.request.Request(_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read()
                with open(_local, 'wb') as f:
                    f.write(data)
            except Exception as e:
                print(f"[SPLASH] No se pudo descargar {os.path.basename(_local)}: {e}")

    try:
        logo = pygame.image.load(_LOGO_LOCAL).convert_alpha()
    except Exception as e:
        print(f"[SPLASH] No se pudo cargar el logo: {e}")
        return

    logo_kevin = None
    try:
        if os.path.exists(_LOGO_KEVIN_LOCAL):
            logo_kevin = pygame.image.load(_LOGO_KEVIN_LOCAL).convert_alpha()
    except Exception as e:
        print(f"[SPLASH] No se pudo cargar logo-kevin: {e}")

    GAP          = 80                     
    max_h        = int(ALTO * 0.55)
    max_w_each   = int(ANCHO * 0.38)

    lw, lh = logo.get_size()
    scale  = min(max_w_each / lw, max_h / lh, 1.0)
    logo   = pygame.transform.smoothscale(logo, (int(lw * scale), int(lh * scale)))
    lw, lh = logo.get_size()

    if logo_kevin is not None:
        kw, kh = logo_kevin.get_size()
        kscale = min(max_w_each / kw, max_h / kh, 1.0)
        logo_kevin = pygame.transform.smoothscale(logo_kevin, (int(kw * kscale), int(kh * kscale)))
        kw, kh = logo_kevin.get_size()

        total_w  = lw + GAP + kw
        base_x   = ANCHO // 2 - total_w // 2
        logo_x   = base_x
        logo_y   = ALTO  // 2 - lh // 2
        kevin_x  = base_x + lw + GAP
        kevin_y  = ALTO  // 2 - kh // 2
        hint_y   = ALTO  // 2 + max(lh, kh) // 2 + 30
    else:
        logo_x   = ANCHO // 2 - lw // 2
        logo_y   = ALTO  // 2 - lh // 2
        hint_y   = logo_y + lh + 30

    FADE_IN   = 700
    HOLD      = 2000
    FADE_OUT  = 800
    TOTAL     = FADE_IN + HOLD + FADE_OUT

    start = pygame.time.get_ticks()

    while True:
        now     = pygame.time.get_ticks()
        elapsed = now - start

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return

        if elapsed < FADE_IN:
            alpha = int(255 * elapsed / FADE_IN)
        elif elapsed < FADE_IN + HOLD:
            alpha = 255
        else:
            fade_prog = (elapsed - FADE_IN - HOLD) / FADE_OUT
            alpha = max(0, int(255 * (1.0 - fade_prog)))

        VENTANA.fill(NEGRO)

        logo_copy = logo.copy()
        logo_copy.set_alpha(alpha)
        VENTANA.blit(logo_copy, (logo_x, logo_y))

        if logo_kevin is not None:
            kevin_copy = logo_kevin.copy()
            kevin_copy.set_alpha(alpha)
            VENTANA.blit(kevin_copy, (kevin_x, kevin_y))

        if FADE_IN < elapsed < FADE_IN + HOLD:
            blink = (elapsed // 500) % 2 == 0
            if blink:
                hint = FUENTE_PEQUENA.render(TR('made_by'), True, DORADO)
                hint_alpha = int(200 * (elapsed - FADE_IN) / HOLD)
                hint.set_alpha(hint_alpha)
                VENTANA.blit(hint, (ANCHO // 2 - hint.get_width() // 2, hint_y))

        flip_display()

        if elapsed >= TOTAL:
            break

        RELOJ.tick(60)


def _loading_error_dialog(failed_name):
    """Muestra un diálogo de error de descarga con 3 opciones.
    Devuelve: 'continue', 'retry' o 'quit'."""
    FUENTE_ERR_TITLE = pygame.font.SysFont("arial", 38, bold=True)
    FUENTE_ERR_SUB   = pygame.font.SysFont("arial", 24)
    FUENTE_BTN       = pygame.font.SysFont("arial", 26, bold=True)

    BTN_CONTINUE = pygame.Rect(ANCHO//2 - 380, ALTO//2 + 30,  740, 58)
    BTN_RETRY    = pygame.Rect(ANCHO//2 - 180, ALTO//2 + 104, 360, 58)
    BTN_QUIT     = pygame.Rect(ANCHO//2 - 180, ALTO//2 + 176, 360, 58)

    clock_err = pygame.time.Clock()
    while True:
        mouse_pos = to_logical(pygame.mouse.get_pos())

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                pos = to_logical(ev.pos)
                if BTN_CONTINUE.collidepoint(pos):
                    return 'continue'
                if BTN_RETRY.collidepoint(pos):
                    return 'retry'
                if BTN_QUIT.collidepoint(pos):
                    return 'quit'

        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        VENTANA.blit(overlay, (0, 0))

        box_w, box_h = 860, 320
        box_x = ANCHO//2 - box_w//2
        box_y = ALTO//2  - box_h//2 - 20
        pygame.draw.rect(VENTANA, (22, 12, 8),  (box_x, box_y, box_w, box_h), border_radius=14)
        pygame.draw.rect(VENTANA, (160, 40, 30),(box_x, box_y, box_w, box_h), 3, border_radius=14)

        title_s = _safe_render(FUENTE_ERR_TITLE, "⚠  " + TR('dl_error_title'), True, (230, 80, 60), fallback_text=TR('dl_error_title'))
        VENTANA.blit(title_s, (ANCHO//2 - title_s.get_width()//2, box_y + 22))

        sub_s = FUENTE_ERR_SUB.render(TRF('dl_error_line', name=failed_name), True, (200, 185, 170))
        VENTANA.blit(sub_s, (ANCHO//2 - sub_s.get_width()//2, box_y + 74))
        sub2  = FUENTE_ERR_SUB.render(TR('dl_error_hint'), True, (160, 150, 140))
        VENTANA.blit(sub2, (ANCHO//2 - sub2.get_width()//2, box_y + 104))

        c_hov = BTN_CONTINUE.collidepoint(mouse_pos)
        c_col = (80, 55, 20) if c_hov else (55, 38, 12)
        pygame.draw.rect(VENTANA, c_col, BTN_CONTINUE, border_radius=10)
        pygame.draw.rect(VENTANA, DORADO, BTN_CONTINUE, 2, border_radius=10)
        c_txt = FUENTE_BTN.render(TR('dl_continue_risky'), True, DORADO)
        VENTANA.blit(c_txt, (BTN_CONTINUE.centerx - c_txt.get_width()//2,
                              BTN_CONTINUE.centery - c_txt.get_height()//2))

        r_hov = BTN_RETRY.collidepoint(mouse_pos)
        r_col = (20, 70, 140) if r_hov else (14, 48, 100)
        pygame.draw.rect(VENTANA, r_col, BTN_RETRY, border_radius=10)
        pygame.draw.rect(VENTANA, (100, 160, 240), BTN_RETRY, 2, border_radius=10)
        r_txt = FUENTE_BTN.render(TR('dl_retry'), True, (180, 220, 255))
        VENTANA.blit(r_txt, (BTN_RETRY.centerx - r_txt.get_width()//2,
                              BTN_RETRY.centery - r_txt.get_height()//2))

        q_hov = BTN_QUIT.collidepoint(mouse_pos)
        q_col = (100, 18, 18) if q_hov else (68, 12, 12)
        pygame.draw.rect(VENTANA, q_col, BTN_QUIT, border_radius=10)
        pygame.draw.rect(VENTANA, (200, 50, 50), BTN_QUIT, 2, border_radius=10)
        q_txt = FUENTE_BTN.render(TR('dl_close_game'), True, (255, 140, 140))
        VENTANA.blit(q_txt, (BTN_QUIT.centerx - q_txt.get_width()//2,
                              BTN_QUIT.centery - q_txt.get_height()//2))

        flip_display()
        clock_err.tick(60)


def loading_screen():
    """Descarga todos los assets de GitHub mostrando progreso."""
    os.makedirs(os.path.join('imagenes', 'cards'), exist_ok=True)
    os.makedirs('music', exist_ok=True)
    os.makedirs(os.path.join('music', 'sounds-storymode'), exist_ok=True)
    os.makedirs('test', exist_ok=True)

    def _build_file_list():
        all_files = []
        for fname in ('mesa.png', 'logo.png'):
            url = _IMAGE_BASE + fname
            local = os.path.join('imagenes', fname)
            all_files.append((url, local, fname))
        for key, (url_file, local_file) in _IMAGE_FILES.items():
            if key == 'mesa': continue
            all_files.append((_IMAGE_BASE + url_file,
                              os.path.join('imagenes', local_file),
                              local_file))
        _suits_map  = [('S','spades'),('H','hearts'),('D','diamonds'),('C','clubs')]
        _values_map = [('A','ace'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),
                       ('7','7'),('8','8'),('9','9'),('10','10'),
                       ('J','jack'),('Q','queen'),('K','king')]
        for v_k, v_n in _values_map:
            for s_k, s_n in _suits_map:
                fname = f"{v_n}_of_{s_n}.png"
                all_files.append((_CARDS_BASE_URL + fname,
                                   os.path.join('imagenes', 'cards', fname),
                                   f"cartas/{fname}"))
        all_files.append((_CARDS_BASE_URL + "back.png",
                           os.path.join('imagenes', 'cards', 'back.png'),
                           "cartas/back.png"))
        for key, (local_path, url) in {**_STORY_MUSIC_FILES, **_STORY_SFX_FILES}.items():
            all_files.append((url, local_path, os.path.basename(local_path)))
        all_files.append((_MUSIC_URL, _MUSIC_LOCAL, "coffee_time.mp3"))
        all_files.append((_HE_AI_MODEL_URL, _HE_AI_MODEL_LOCAL, "he_ai_model.json"))
        return all_files

    FUENTE_LOAD  = pygame.font.SysFont("arial", 36, bold=True)
    FUENTE_FILE  = pygame.font.SysFont("arial", 24)
    FUENTE_PCT   = pygame.font.SysFont("arial", 28, bold=True)

    while True:   
        all_files   = _build_file_list()
        to_download = [(u, l, n) for u, l, n in all_files if not os.path.exists(l)]

        if not to_download:
            break   

        total      = len(to_download)
        retry_all  = False

        for i, (url, local, name) in enumerate(to_download):
            VENTANA.fill((4, 2, 10))

            title = FUENTE_LOAD.render(TR('dl_downloading'), True, DORADO)
            VENTANA.blit(title, (ANCHO//2 - title.get_width()//2, ALTO//2 - 140))

            status = FUENTE_FILE.render(TRF('dl_progress', i=i+1, total=total, name=name), True, (200, 210, 200))
            VENTANA.blit(status, (ANCHO//2 - status.get_width()//2, ALTO//2 - 65))

            bw = 700; bh = 26
            bx = ANCHO//2 - bw//2; by = ALTO//2
            pygame.draw.rect(VENTANA, (30, 30, 30), (bx, by, bw, bh), border_radius=10)
            fill_w = int(bw * i / total) if total else 0
            if fill_w > 0:
                pygame.draw.rect(VENTANA, DORADO, (bx, by, fill_w, bh), border_radius=10)
            pygame.draw.rect(VENTANA, (80, 65, 30), (bx, by, bw, bh), 2, border_radius=10)

            pct_txt = FUENTE_PCT.render(f"{int(100 * i / total)}%", True, (200, 200, 200))
            VENTANA.blit(pct_txt, (ANCHO//2 - pct_txt.get_width()//2, by + bh + 14))

            flip_display()
            pygame.event.pump()

            if not os.path.exists(local):
                download_ok = False
                try:
                    os.makedirs(os.path.dirname(local), exist_ok=True)
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=20) as resp:
                        data = resp.read()
                    with open(local, 'wb') as f:
                        f.write(data)
                    download_ok = True
                except Exception as e:
                    print(f"[LOADING] Error descargando {name}: {e}")

                if not download_ok:
                    decision = _loading_error_dialog(name)
                    if decision == 'quit':
                        pygame.quit(); sys.exit()
                    elif decision == 'retry':
                        retry_all = True
                        break   

        if retry_all:
            continue  
        break          

    VENTANA.fill((4, 2, 10))
    done = pygame.font.SysFont("arial", 48, bold=True).render(TR('dl_ready'), True, (80, 220, 80))
    VENTANA.blit(done, (ANCHO//2 - done.get_width()//2, ALTO//2 - 30))
    bw = 700
    pygame.draw.rect(VENTANA, DORADO, (ANCHO//2 - bw//2, ALTO//2 + 30, bw, 26), border_radius=10)
    flip_display()
    _deadline = pygame.time.get_ticks() + 1500
    while _gameboy_win_snd is None and pygame.time.get_ticks() < _deadline:
        pygame.time.delay(30)
        pygame.event.pump()
    _play_gameboy(win=True)
    pygame.time.delay(700)


_menu_fade_start = 0
loading_screen()
splash_screen()
_menu_fade_start = pygame.time.get_ticks()

if CONFIG.get('autoupdate', True):
    update_status = 'checking'; update_msg = TR('update_checking')
    update_notif_time = pygame.time.get_ticks()
    threading.Thread(target=_check_for_updates, daemon=True).start()

if IS_FIRST_RUN:
    open_settings()
    CONFIG['first_run'] = False
    save_config()


while True:
    RELOJ.tick(60)
    now = pygame.time.get_ticks()

    if update_status == 'restarting' and update_restart_time != 0:
        if now >= update_restart_time + 2000:
            pygame.quit()
            if _pending_external_restart:
                sys.exit()   
            else:
                _restart_process()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_m:
            toggle_mute()

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if MUTE_BTN.collidepoint(to_logical(evento.pos)):
                toggle_mute()

        if settings_open:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                close_settings(save=True)
                continue
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                lpos = to_logical(evento.pos)
                hit = getattr(render_settings_panel, '_last_hit', None) or {}
                if hit.get('volume_slider') and hit['volume_slider'].collidepoint(lpos):
                    _settings_dragging_volume = True
                    slider = hit['volume_slider']
                    CONFIG['volume'] = max(0.0, min(1.0, (lpos[0] - slider.x) / slider.width))
                    _apply_live_volume()
                else:
                    handle_settings_click(lpos)
                continue
            if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                if _settings_dragging_volume:
                    _settings_dragging_volume = False
                    save_config()
                continue
            if evento.type == pygame.MOUSEMOTION and _settings_dragging_volume:
                hit = getattr(render_settings_panel, '_last_hit', None) or {}
                slider = hit.get('volume_slider')
                if slider:
                    lpos = to_logical(evento.pos)
                    CONFIG['volume'] = max(0.0, min(1.0, (lpos[0] - slider.x) / slider.width))
                    _apply_live_volume()
                continue
            continue

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            if paused:
                _resume_game()          
            elif app_state in ('game', 'blackjack'):
                paused = True; _pause_started_at = now  
            elif app_state == 'poker':
                app_state = 'main_menu'
            elif app_state == 'poker_mode_select':
                app_state = 'main_menu'
            elif app_state == 'poker_online_connect':
                app_state = 'poker_mode_select'
            elif app_state == 'poker_online_lobby':
                _online_disconnect(); app_state = 'poker_mode_select'
            elif app_state == 'poker_online_game':
                _online_disconnect(); app_state = 'poker_mode_select'
            elif app_state in ('intro', 'win_ending', 'lose_ending', 'kicked_ending'):
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
                if _hard_reset_confirm:
                    if evento.key == pygame.K_ESCAPE:
                        _hard_reset_confirm = False
                    continue
                if evento.key == pygame.K_1: _start_story_mode()
                elif evento.key == pygame.K_2: _start_infinite_mode()
                elif evento.key == pygame.K_3: app_state = 'poker_mode_select'
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                lpos = to_logical(evento.pos)

                if _GEAR_BTN_RECT.collidepoint(lpos):
                    open_settings()
                    continue

                if _hard_reset_confirm:
                    confirm_r2 = getattr(_render_main_menu, '_confirm_rect', None)
                    cancel_r2  = getattr(_render_main_menu, '_cancel_rect',  None)
                    if confirm_r2 and confirm_r2.collidepoint(lpos):
                        _do_hard_reset()
                    elif cancel_r2 and cancel_r2.collidepoint(lpos):
                        _hard_reset_confirm = False
                    continue

                for i, rect in enumerate(main_menu_button_rects):
                    if rect.collidepoint(lpos):
                        _hard_reset_confirm = False
                        if i == 0: _start_story_mode()
                        elif i == 1: _start_infinite_mode()
                        elif i == 2: app_state = 'poker_mode_select'
                        elif i == 3:
                            if update_status != 'checking':
                                update_status = 'checking'; update_msg = TR('update_checking')
                                update_notif_time = pygame.time.get_ticks()
                                threading.Thread(target=_check_for_updates, daemon=True).start()
                folder_r = getattr(_render_main_menu, '_folder_rect', None)
                if folder_r and folder_r.collidepoint(lpos):
                    open_data_folder()
                reset_r = getattr(_render_main_menu, '_hard_reset_rect', None)
                if reset_r and reset_r.collidepoint(lpos):
                    _hard_reset_confirm = True
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
                if he_state in ('dealing_preflop', 'dealing_flop'):
                    continue
                if he_state == 'betting':
                    if evento.key == pygame.K_BACKSPACE:
                        he_blind_input = he_blind_input[:-1]
                    elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        try:
                            val = int(he_blind_input) if he_blind_input.strip() else he_blind
                            if val <= 0: pass
                            elif val > BET_MAX_HOLDEM: he_mensaje = TRF('he_max_blind', max=BET_MAX_HOLDEM)
                            elif val*2 > he_player_money: he_mensaje = TR('he_blind_insufficient')
                            else:
                                he_blind = val
                                he_player_money -= he_blind; poker_player_money = he_player_money
                                he_blind_input = ""
                                he_start_hand(now)
                        except ValueError:
                            he_mensaje = TR('he_blind_invalid')
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
                                    he_mensaje = TR('he_amount_invalid')
                            except ValueError:
                                he_mensaje = TR('he_number_invalid')
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

        if app_state == 'poker_mode_select':
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                lpos = to_logical(evento.pos)
                rects = getattr(_render_poker_mode_select, '_last_rects', [])
                if len(rects) >= 2:
                    if rects[0].collidepoint(lpos):   
                        app_state = 'poker_online_connect'
                    elif rects[1].collidepoint(lpos):  
                        _start_poker_mode()
            continue

        if app_state == 'poker_online_connect':
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                lpos = to_logical(evento.pos)
                frects, conn_r = getattr(_render_poker_online_connect, '_last_data', ({}, None))
                for key, fr in frects.items():
                    if fr.collidepoint(lpos):
                        _online_active_field = key
                if conn_r and conn_r.collidepoint(lpos) and not _online_connecting:
                    _online_connecting = True
                    _online_connect_error = ""
                    threading.Thread(target=_online_connect,
                                     args=(_online_ip_input, _online_port_input, _online_name_input),
                                     daemon=True).start()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_BACKSPACE:
                    if _online_active_field == 'ip':
                        _online_ip_input = _online_ip_input[:-1]
                    elif _online_active_field == 'port':
                        _online_port_input = _online_port_input[:-1]
                    elif _online_active_field == 'name':
                        _online_name_input = _online_name_input[:-1]
                elif evento.key == pygame.K_TAB:
                    fields_order = ['ip', 'port', 'name']
                    idx = fields_order.index(_online_active_field)
                    _online_active_field = fields_order[(idx + 1) % len(fields_order)]
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if not _online_connecting:
                        _online_connecting = True
                        _online_connect_error = ""
                        threading.Thread(target=_online_connect,
                                         args=(_online_ip_input, _online_port_input, _online_name_input),
                                         daemon=True).start()
                elif evento.unicode and len(evento.unicode) == 1:
                    ch = evento.unicode
                    if _online_active_field == 'ip' and len(_online_ip_input) < 64:
                        _online_ip_input += ch
                    elif _online_active_field == 'port' and ch.isdigit() and len(_online_port_input) < 6:
                        _online_port_input += ch
                    elif _online_active_field == 'name' and len(_online_name_input) < 20:
                        _online_name_input += ch
            continue

        if app_state == 'poker_online_lobby':
            _online_process_messages(now)
            continue

        if app_state == 'poker_online_game':
            _online_process_messages(now)
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                lpos = to_logical(evento.pos)
                btns = getattr(_render_poker_online_game, '_last_btns', None)
                if btns:
                    menu_b, fold_b, call_b, check_b, raise_b, rebuy_b = btns
                    if menu_b.collidepoint(lpos):
                        _online_disconnect(); app_state = 'poker_mode_select'
                    elif rebuy_b.collidepoint(lpos) and _online_my_money <= 0:
                        _online_send({'type':'action','action':'rebuy'})
                    elif _online_my_turn and not _online_in_raise:
                        if fold_b.collidepoint(lpos):
                            _online_send({'type':'action','action':'fold'})
                            _online_my_turn = False
                        elif _online_my_money > 0 and _online_to_call > 0 and call_b.collidepoint(lpos):
                            _online_send({'type':'action','action':'call'})
                            _online_my_turn = False
                        elif _online_my_money > 0 and _online_to_call == 0 and check_b.collidepoint(lpos):
                            _online_send({'type':'action','action':'check'})
                            _online_my_turn = False
                        elif _online_my_money > 0 and raise_b.collidepoint(lpos):
                            _online_in_raise = True; _online_raise_input = ""
            if evento.type == pygame.KEYDOWN:
                if app_state != 'poker_online_game':
                    continue
                if _online_my_turn:
                    if _online_in_raise:
                        if evento.key == pygame.K_BACKSPACE:
                            _online_raise_input = _online_raise_input[:-1]
                        elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            try:
                                amt = int(_online_raise_input) if _online_raise_input.strip() else 0
                                if amt > 0:
                                    _online_send({'type':'action','action':'raise','amount':amt})
                                    _online_my_turn = False; _online_in_raise = False
                            except ValueError:
                                pass
                        elif evento.key == pygame.K_ESCAPE:
                            _online_in_raise = False
                        elif evento.unicode and evento.unicode.isdigit():
                            if len(_online_raise_input) < 6:
                                _online_raise_input += evento.unicode
                    else:
                        if evento.key == pygame.K_f:
                            _online_send({'type':'action','action':'fold'})
                            _online_my_turn = False
                        elif evento.key == pygame.K_c and _online_my_money > 0:
                            action = 'call' if _online_to_call > 0 else 'check'
                            _online_send({'type':'action','action':action})
                            _online_my_turn = False
                        elif evento.key == pygame.K_r:
                            if _online_my_money <= 0:
                                _online_send({'type':'action','action':'rebuy'})
                            else:
                                _online_in_raise = True; _online_raise_input = ""
            continue


        if app_state == 'blackjack':
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                lpos = to_logical(evento.pos)
                if bj_menu_btn.collidepoint(lpos):
                    app_state = 'main_menu'; continue
                if REINICIAR_BTN.collidepoint(lpos):
                    bj_reiniciar(); continue
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                bj_reiniciar(); continue

        if app_state in ('intro','win_ending','lose_ending','kicked_ending'):
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
                if advance:
                    if not _tw['done']:
                        _tw_finish()          
                    else:
                        _story_advance()      
            continue

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            lpos = to_logical(evento.pos)
            if REINICIAR_BTN.collidepoint(lpos):
                reiniciar_partida(); continue
            if DOTS_BTN.collidepoint(lpos):
                if update_status != 'checking':
                    update_status = 'checking'; update_msg = TR('update_checking')
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
                                mensaje = TR('bj_bet_empty'); round_end_time = now
                            else:
                                bet_val = int(last_bet)
                                if   bet_val <= 0:            mensaje = TR('bj_bet_invalid'); round_end_time = now
                                elif bet_val > BET_MAX:       mensaje = TRF('bj_bet_max', max=BET_MAX); round_end_time = now
                                elif bet_val > player_money:  mensaje = TR('bj_not_enough_money'); round_end_time = now
                                else:
                                    current_bet = bet_val; player_money -= current_bet; bet_locked = True
                                    state = 'dealing'; dealing_step = 0; next_deal = now+300; mensaje = ""
                                    placed_chip = create_placed_chip(current_bet, ANCHO//2, ALTO-120)
                                    current_bet_input = ""
                        else:
                            bet_val = int(current_bet_input)
                            if   bet_val <= 0:            mensaje = TR('bj_bet_invalid'); round_end_time = now
                            elif bet_val > BET_MAX:       mensaje = TRF('bj_bet_max', max=BET_MAX); round_end_time = now
                            elif bet_val > player_money:  mensaje = TR('bj_not_enough_money'); round_end_time = now
                            else:
                                current_bet = bet_val; player_money -= current_bet; bet_locked = True
                                state = 'dealing'; dealing_step = 0; next_deal = now+300; mensaje = ""
                                placed_chip = create_placed_chip(current_bet, ANCHO//2, ALTO-120)
                                last_bet = current_bet; current_bet_input = ""
                    except ValueError:
                        mensaje = TR('bj_bet_invalid'); round_end_time = now
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
                            dest_y2 = PLAYER_CARD_Y+current_hand_index*70; repartir(hand, dest_y2)
                            if current_hand_index < len(jugador_hands)-1: current_hand_index += 1
                            else:
                                state = 'dealer'; revelar_banca(now); dealer_thinking = False
                                dealer_target = schedule_dealer_target(); next_action = now+600
                        else:
                            player_money -= current_bet; current_bet *= 2; repartir(hand, PLAYER_CARD_Y)
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
                            base_x2 = 120+i*HAND_SEP; dest_y3 = PLAYER_CARD_Y+i*70
                            for idx2, ct2 in enumerate(h):
                                c2 = ct2[4]; c2.dest_x = base_x2+idx2*CARD_SPACING; c2.dest_y = dest_y3
                                c2.target_scale = 1.06 if i==current_hand_index else 1.0
                                c2.oculta = False; c2.start_flip(now, to_back=False)

                if evento.key == pygame.K_i and insurance_offered and not insurance_taken:
                    insurance_bet = min(current_bet//2, player_money)
                    if insurance_bet > 0: player_money -= insurance_bet; insurance_taken = True

                if evento.key == pygame.K_SPACE:
                    if (now >= last_pedir_time+PEDIR_DELAY) and (not clearing):
                        dest_y4 = PLAYER_CARD_Y+current_hand_index*70 if (split_active and jugador_hands) else PLAYER_CARD_Y
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
            _start_story(build_lose_ending_scenes(), 'lose_ending')

    if app_state == 'main_menu':
        _render_main_menu(now)
        flip_display()
        continue

    if app_state in ('intro','win_ending','lose_ending','kicked_ending'):
        _render_story(now)
        flip_display()
        continue

    if app_state == 'poker' and he_ai_turn_active:
        _he_update_ai_turns(now)

    if app_state == 'poker' and he_dealing:
        _he_process_deal_queue(now)

    if app_state == 'poker':
        _render_poker(now)
        flip_display()
        continue

    if app_state == 'poker_mode_select':
        rects = _render_poker_mode_select(now)
        _render_poker_mode_select._last_rects = rects
        flip_display()
        continue

    if app_state == 'poker_online_connect':
        _online_process_messages(now)
        frects, conn_r = _render_poker_online_connect(now)
        _render_poker_online_connect._last_data = (frects, conn_r)
        flip_display()
        continue

    if app_state == 'poker_online_lobby':
        _online_process_messages(now)
        _render_poker_online_lobby(now)
        flip_display()
        continue

    if app_state == 'poker_online_game':
        _online_process_messages(now)
        btns = _render_poker_online_game(now)
        _render_poker_online_game._last_btns = btns
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
        txt1 = FUENTE_GRANDE.render(TR('bj_no_chips_victor'), True, (210,70,25))
        txt2 = FUENTE.render(TR('bj_enter_restart'), True, (180,148,90))
        VENTANA.blit(txt1, ((ANCHO - txt1.get_width())//2, ALTO//2 - 60))
        VENTANA.blit(txt2, ((ANCHO - txt2.get_width())//2, ALTO//2 + 20))
        flip_display()
        continue

    style = TABLE_STYLES[TABLE_STYLE_IDX]
    _mesa_img = _image_cache.get('mesa')
    if _mesa_img is not None:
        mesa_key = ('mesa', ANCHO, ALTO)
        cached = _story_scaled_cache.get(mesa_key)
        if cached is None:
            mw, mh = _mesa_img.get_size()
            scale_m = max(ANCHO / mw, ALTO / mh)
            ms_w = int(mw * scale_m); ms_h = int(mh * scale_m)
            mesa_scaled = pygame.transform.smoothscale(_mesa_img, (ms_w, ms_h))
            mx = (ANCHO - ms_w) // 2; my = (ALTO - ms_h) // 2
            cached = (mesa_scaled, mx, my)
            _story_scaled_cache[mesa_key] = cached
        VENTANA.blit(cached[0], (cached[1], cached[2]))
    else:
        VENTANA.fill(style['color'])
        get_story_image('mesa')  

    if DEALER_AVATAR:
        VENTANA.blit(DEALER_AVATAR, (ANCHO//2 - DEALER_AVATAR.get_width()//2, 0))

    if state == 'dealing' and (not clearing) and now >= next_deal and not paused:
        if dealing_step == 0:
            repartir(jugador, PLAYER_CARD_Y, start_pos=DECK_POS)
        elif dealing_step == 1:
            repartir(banca, DEALER_CARD_Y, True, start_pos=DECK_POS)
        elif dealing_step == 2:
            repartir(jugador, PLAYER_CARD_Y, start_pos=DECK_POS)
        elif dealing_step == 3:
            repartir(banca, DEALER_CARD_Y, True, start_pos=DECK_POS)
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
                    elif any(r == 'win' for r in results):    mensaje = "WIN"
                    elif all(r == 'tie' for r in results):    mensaje = "TIE"
                    else:                                      mensaje = "LOSE"
                    _apply_chip_result(results)
                    state = 'round_end'; round_end_time = now

                elif pb < dealer_target:
                    repartir(banca, DEALER_CARD_Y)
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
                    elif any(r == 'win' for r in results):    mensaje = "WIN"
                    elif all(r == 'tie' for r in results):    mensaje = "TIE"
                    else:                                      mensaje = "LOSE"
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
            offset_y = PLAYER_CARD_Y + i*70
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
                mensaje = f"BUST:{current_hand_index+1}"; current_hand_index += 1; last_pedir_time = now
            elif split_active and current_hand_index == len(jugador_hands)-1:
                overlay_flash.update({'active':True,'color':(150,0,0),'alpha':200,'start':now,'duration':300})
                mensaje = f"BUST:{current_hand_index+1}"
                revelar_banca(now); state = 'dealer'; dealer_thinking = False
                dealer_target = schedule_dealer_target(); next_action = now+600
            else:
                mensaje = "LOSE"; stats['lost'] += 1; stats['played'] += 1
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
        VENTANA.blit(FUENTE.render(TRF('bj_banca', texto=texto), True, BLANCO), (50, DEALER_CARD_Y - 30))
    else:
        banca_visible = calcular_visible(banca)
        VENTANA.blit(FUENTE.render(TRF('bj_banca', texto=banca_visible), True, BLANCO), (50, DEALER_CARD_Y - 30))

    if split_active and jugador_hands:
        left = TRF('bj_mano1', v=calcular(jugador_hands[0]))
        right = TRF('bj_mano2', v=calcular(jugador_hands[1]))
        surf = FUENTE.render(f"{left}    {right}", True, BLANCO)
        VENTANA.blit(surf, (50, PLAYER_CARD_Y - 30))
    else:
        VENTANA.blit(FUENTE.render(TRF('bj_jugador', v=calcular(jugador)), True, BLANCO), (50, PLAYER_CARD_Y - 30))

    if state == 'betting':
        instrucciones = [TR('bj_type_bet')]
    elif state == 'player':
        instrucciones = [TR('bj_controls')]
    elif state in ('dealing', 'dealer'):
        instrucciones = [TR('bj_waiting')]
    else:
        instrucciones = [TR('bj_next_round')]

    if insurance_offered and not insurance_taken and state == 'player':
        instrucciones = [TR('bj_insurance_take') + instrucciones[0]]

    diff_colors = {0: BLANCO, 1: (255, 200, 80), 2: (255, 140, 40), 3: (255, 80, 80)}
    diff_label  = {0: 'Normal', 1: TR('bj_dificil'), 2: TR('bj_muy_dificil'), 3: 'EXTREMO'}.get(difficulty_level, 'Normal')
    diff_color  = diff_colors.get(difficulty_level, BLANCO)

    box_w   = ANCHO - 40; padding = 14; lh = 30
    box_h   = lh * 3 + padding * 2
    reglas_x = 20
    reglas_y = ALTO - box_h - 16

    s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 195))
    VENTANA.blit(s, (reglas_x, reglas_y))
    pygame.draw.rect(VENTANA, (60, 50, 20), (reglas_x, reglas_y, box_w, box_h), 2, border_radius=10)

    y_off = reglas_y + padding

    display_text = current_bet_input if state == 'betting' else str(current_bet)
    txt_to_show  = clip_text_right(display_text, FUENTE_PEQUENA, 200)

    col1 = _safe_render(FUENTE_PEQUENA, TRF('bj_chips', v=player_money), True, DORADO, fallback_text=TRF('he_chips', v=player_money))
    col2 = _safe_render(FUENTE_PEQUENA, TRF('bj_bet', v=txt_to_show), True, BLANCO, fallback_text=TRF('bj_bet', v=txt_to_show).replace('🎰 ', ''))
    if app_state == 'blackjack':
        col3_txt = TRF('bj_max_dif', max=BET_MAX, diff=diff_label)
    else:
        col3_txt = TRF('bj_max_meta_dif', max=BET_MAX, meta=EPIC_WIN_THRESHOLD, diff=diff_label)
    col3 = FUENTE_PEQUENA.render(col3_txt, True, diff_color)

    VENTANA.blit(col1, (reglas_x + padding, y_off))
    col2_x = reglas_x + box_w // 3
    VENTANA.blit(col2, (col2_x, y_off))
    col3_x = reglas_x + box_w * 2 // 3
    VENTANA.blit(col3, (col3_x, y_off))

    if state == 'betting':
        ib_w = 180; ib_h = 28
        ib_x = col2_x + col2.get_width() + 8; ib_y = y_off - 2
        ib_bg = pygame.Surface((ib_w, ib_h), pygame.SRCALPHA)
        ib_bg.fill((30, 30, 30, 240))
        VENTANA.blit(ib_bg, (ib_x, ib_y))
        pygame.draw.rect(VENTANA, DORADO, (ib_x, ib_y, ib_w, ib_h), 2, border_radius=5)
        ib_txt = clip_text_right(current_bet_input + ('|' if (now//400)%2==0 else ''), FUENTE_PEQUENA, ib_w-10)
        ib_surf = FUENTE_PEQUENA.render(ib_txt, True, DORADO)
        VENTANA.blit(ib_surf, (ib_x + 6, ib_y + (ib_h - ib_surf.get_height())//2))

    y_off += lh

    pygame.draw.line(VENTANA, (50, 42, 16), (reglas_x+8, y_off-4), (reglas_x+box_w-8, y_off-4), 1)
    for linea in instrucciones:
        surf2 = FUENTE_INSTR.render(linea, True, (200, 210, 200))
        tx2   = reglas_x + (box_w - surf2.get_width()) // 2
        VENTANA.blit(surf2, (tx2, y_off))
        y_off += lh - 4

    if mensaje:
        if mensaje == "BLACKJACK!":
            surf_m = FUENTE_GRANDE.render(TR('bj_blackjack'), True, DORADO)
        elif mensaje == "WIN":
            surf_m = FUENTE_MSG.render(TR('bj_has_ganado'), True, DORADO)
        elif mensaje == "TIE":
            surf_m = FUENTE_MSG.render(TR('bj_empate'), True, (200, 200, 200))
        elif mensaje == "LOSE":
            surf_m = FUENTE_MSG.render(TR('bj_has_perdido'), True, ROJO)
        elif mensaje.startswith("BUST:"):
            surf_m = FUENTE_MSG.render(TRF('bj_hand_bust', n=mensaje.split(":", 1)[1]), True, ROJO)
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

    mute_hovered = MUTE_BTN.collidepoint(mouse_pos)
    if music_muted:
        mute_bg = (120, 30, 30) if not mute_hovered else (160, 50, 50)
        mute_label = "\u266a\u2715"
    else:
        mute_bg = (40, 80, 40) if not mute_hovered else (60, 120, 60)
        mute_label = "\u266a"
    pygame.draw.rect(VENTANA, mute_bg, MUTE_BTN, border_radius=6)
    pygame.draw.rect(VENTANA, NEGRO, MUTE_BTN, 1, border_radius=6)
    try:
        mute_surf = FUENTE_PEQUENA.render(mute_label, True, BLANCO)
    except Exception:
        mute_surf = FUENTE_PEQUENA.render("M" if music_muted else "\u266a", True, BLANCO)
    VENTANA.blit(mute_surf, (MUTE_BTN.centerx-mute_surf.get_width()//2,
                              MUTE_BTN.centery-mute_surf.get_height()//2))

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
                display_msg = TRF('updated_restarting', secs=secs_left)
            else:
                display_msg = update_msg
                notif_color = (30,120,50) if update_status=='up_to_date' else \
                              (40,40,40)  if update_status=='checking'   else (150,30,30)
            notif_surf = FUENTE_PEQUENA.render(display_msg, True, BLANCO)
            nw = notif_surf.get_width()+24; nh = notif_surf.get_height()+14
            nx = ANCHO-nw-10; ny = MUTE_BTN.bottom+6
            bg = pygame.Surface((nw, nh), pygame.SRCALPHA)
            bg.fill((*notif_color, alpha_notif))
            VENTANA.blit(bg, (nx, ny))
            pygame.draw.rect(VENTANA, NEGRO, (nx, ny, nw, nh), 1, border_radius=6)
            VENTANA.blit(notif_surf, (nx+12, ny+7))

    r_hovered = REINICIAR_BTN.collidepoint(mouse_pos)
    r_color = (140,30,30) if not r_hovered else (180,50,50)
    pygame.draw.rect(VENTANA, r_color, REINICIAR_BTN, border_radius=7)
    pygame.draw.rect(VENTANA, NEGRO, REINICIAR_BTN, 1, border_radius=7)
    r_txt = FUENTE_PEQUENA.render(TR("reiniciar_btn"), True, BLANCO)
    VENTANA.blit(r_txt, (REINICIAR_BTN.centerx-r_txt.get_width()//2,
                          REINICIAR_BTN.centery-r_txt.get_height()//2))

    if app_state == 'blackjack':
        m_hovered = bj_menu_btn.collidepoint(mouse_pos)
        m_col = (30, 70, 140) if not m_hovered else (50, 100, 190)
        pygame.draw.rect(VENTANA, m_col, bj_menu_btn, border_radius=7)
        pygame.draw.rect(VENTANA, NEGRO, bj_menu_btn, 1, border_radius=7)
        m_txt = FUENTE_PEQUENA.render(TR("esc_menu_principal"), True, BLANCO)
        VENTANA.blit(m_txt, (bj_menu_btn.centerx - m_txt.get_width()//2,
                              bj_menu_btn.centery - m_txt.get_height()//2))
        inf_s = FUENTE_PEQUENA.render(
            TRF('bj_infinito_stats', won=stats['won'], lost=stats['lost']),
            True, DORADO)
        VENTANA.blit(inf_s, (ANCHO//2 - inf_s.get_width()//2, ALTO - 88))

    if paused:
        _render_pause_menu(now)

    flip_display()
