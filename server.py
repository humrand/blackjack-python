#!/usr/bin/env python3
"""
poker_server.py  —  Servidor de Texas Hold'em para El Farol Rojo  (UDP)
=======================================================================
Uso:
    python3 poker_server.py [--port 5555] [--min-players 2] [--max-players 6]

Protocolo: JSON sobre UDP, un objeto por datagrama.
"""

import argparse, json, random, socket, threading, itertools, time
from collections import Counter

VALORES = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
PALOS   = ['S','H','D','C']
HEARTBEAT_TIMEOUT = 20
HEARTBEAT_CHECK   = 5

def nueva_baraja():
    deck = [(v, p) for v in VALORES for p in PALOS]
    random.shuffle(deck)
    return deck

def val_num(v):
    m = {'A':14,'K':13,'Q':12,'J':11,'10':10}
    return m.get(str(v), int(v))

def eval_5(hand5):
    vs  = [c[0] for c in hand5]
    ss  = [c[1] for c in hand5]
    cnt = Counter(vs)
    freq = sorted(cnt.values(), reverse=True)
    nums = sorted(val_num(v) for v in vs)
    is_fl = len(set(ss)) == 1
    uniq = set(nums)
    is_st = len(uniq) == 5 and nums[-1] - nums[0] == 4
    if not is_st and uniq == {14, 2, 3, 4, 5}:
        is_st = True; nums = [1, 2, 3, 4, 5]
    is_royal = is_st and is_fl and nums[-1] == 14
    nd = sorted(nums, reverse=True)
    if is_royal:                return (8, nd)
    if is_st and is_fl:         return (7, nd)
    if freq[0] == 4:
        qv = max(val_num(v) for v, c in cnt.items() if c == 4)
        kk = sorted((val_num(v) for v, c in cnt.items() if c != 4), reverse=True)
        return (6, [qv] + kk)
    if freq[0] == 3 and len(freq) > 1 and freq[1] == 2:
        tv = max(val_num(v) for v, c in cnt.items() if c == 3)
        pv = max(val_num(v) for v, c in cnt.items() if c == 2)
        return (5, [tv, pv])
    if is_fl:   return (4, nd)
    if is_st:   return (3, nd)
    if freq[0] == 3:
        tv = max(val_num(v) for v, c in cnt.items() if c == 3)
        kk = sorted((val_num(v) for v, c in cnt.items() if c != 3), reverse=True)
        return (2, [tv] + kk)
    if freq[0] == 2 and len(freq) > 1 and freq[1] == 2:
        pvs = sorted((val_num(v) for v, c in cnt.items() if c == 2), reverse=True)
        kk  = sorted((val_num(v) for v, c in cnt.items() if c == 1), reverse=True)
        return (1, pvs + kk)
    if freq[0] == 2:
        pv = max(val_num(v) for v, c in cnt.items() if c == 2)
        kk = sorted((val_num(v) for v, c in cnt.items() if c != 2), reverse=True)
        return (0, [pv] + kk)
    return (-1, nd)

RANK_NAMES = {
    8:'Escalera Real', 7:'Escalera de Color', 6:'Póker (4 iguales)',
    5:'Full House', 4:'Color', 3:'Escalera', 2:'Trío',
    1:'Doble Pareja', 0:'Pareja', -1:'Carta Alta'
}

def best_hand(cards):
    best = None
    for combo in itertools.combinations(cards, min(5, len(cards))):
        sc = eval_5(combo)
        if best is None or sc > best:
            best = sc
    return best, RANK_NAMES.get(best[0] if best else -1, 'Carta Alta')


_udp_sock = None

class Player:
    def __init__(self, addr, name, money):
        self.addr      = addr
        self.name      = name
        self.money     = money
        self.hand      = []
        self.folded    = False
        self.active    = True
        self.last_seen = time.time()

    def send(self, obj):
        global _udp_sock
        try:
            _udp_sock.sendto((json.dumps(obj) + '\n').encode('utf-8'), self.addr)
        except Exception:
            self.active = False


class PokerRoom:
    STARTING_MONEY = 3000
    STREETS = ['pre_flop', 'flop', 'turn', 'river']

    def __init__(self, min_players=2, max_players=6):
        self.min_players  = min_players
        self.max_players  = max_players
        self.players: list[Player] = []
        self.lock         = threading.Lock()
        self.game_running = False
        self.deck         = []
        self.community    = []
        self.pot          = 0
        self.blind        = 50
        self.dealer_idx   = 0
        self.street_bets  = {}
        self._action_event   = threading.Event()
        self._pending_action = None

    def broadcast_all(self, obj):
        for p in self.players: p.send(obj)

    def _players_info(self):
        return [{'name': p.name, 'money': p.money, 'folded': p.folded} for p in self.players]

    def broadcast_lobby(self):
        self.broadcast_all({'type': 'lobby', 'players': [p.name for p in self.players]})

    def get_player_by_addr(self, addr):
        for p in self.players:
            if p.addr == addr: return p
        return None

    def add_player(self, addr, name):
        with self.lock:
            if len(self.players) >= self.max_players:
                try: _udp_sock.sendto((json.dumps({'type':'error','msg':'Sala llena'})+'\n').encode(), addr)
                except: pass
                return None
            existing = {p.name for p in self.players}
            orig = name; i = 2
            while name in existing: name = f"{orig}{i}"; i += 1
            p = Player(addr, name, self.STARTING_MONEY)
            self.players.append(p)
            print(f"[+] {name} conectado desde {addr}")
            self.broadcast_lobby()
            if not self.game_running and len(self.players) >= self.min_players:
                threading.Thread(target=self._run_game, daemon=True).start()
            else:
                p.send({'type':'waiting','msg':f'Esperando jugadores ({len(self.players)}/{self.min_players})...'})
            return p

    def remove_player(self, player):
        with self.lock:
            if player in self.players:
                self.players.remove(player)
                print(f"[-] {player.name} desconectado")
            player.active = False
        self.broadcast_lobby()
        self._action_event.set()

    def heartbeat_checker(self):
        while True:
            time.sleep(HEARTBEAT_CHECK)
            now = time.time()
            with self.lock:
                dead = [p for p in self.players if now - p.last_seen > HEARTBEAT_TIMEOUT]
            for p in dead:
                print(f"[TIMEOUT] {p.name} sin heartbeat, eliminando")
                self.remove_player(p)

    def _run_game(self):
        self.game_running = True
        print("[GAME] Partida iniciada")
        try:
            while True:
                with self.lock:
                    active = [p for p in self.players if p.active]
                if len(active) < 2:
                    print("[GAME] Menos de 2 jugadores. Fin.")
                    break
                self._play_hand()
                time.sleep(4)
                self.broadcast_all({'type': 'next_hand'})
        finally:
            self.game_running = False

    def _play_hand(self):
        with self.lock:
            active_players = [p for p in self.players if p.active]

        self.deck = nueva_baraja()
        self.community = []
        self.pot = 0
        for p in active_players:
            p.folded = False; p.hand = []

        n = len(active_players)
        sb_idx = self.dealer_idx % n
        bb_idx = (self.dealer_idx + 1) % n
        self.dealer_idx = (self.dealer_idx + 1) % n

        blind = self.blind
        for idx, p in enumerate(active_players):
            amt = blind if idx == sb_idx else (blind * 2 if idx == bb_idx else blind)
            paid = min(amt, p.money)
            p.money -= paid; self.pot += paid

        for _ in range(2):
            for p in active_players: p.hand.append(self.deck.pop())

        for p in active_players:
            p.send({'type':'deal','hand':p.hand,'pot':self.pot,'blind':blind,
                    'my_money':p.money,'players':self._players_info()})

        streets_community = {
            'pre_flop': [],
            'flop':  [self.deck.pop() for _ in range(3)],
            'turn':  [self.deck.pop()],
            'river': [self.deck.pop()],
        }

        for street in self.STREETS:
            new_cards = streets_community[street]
            if new_cards:
                self.community.extend(new_cards)
                time.sleep(0.8)
                self.broadcast_all({'type':'community','cards':self.community,'pot':self.pot})
                time.sleep(0.4)

            self.street_bets = {p.name: 0 for p in active_players}
            to_call = 0
            start_idx = (self.dealer_idx + 1) % n if n > 0 else 0
            acted = set()
            order = [(start_idx + i) % n for i in range(n)]
            loop_count = 0

            while True:
                loop_count += 1
                if loop_count > n * 4: break

                non_folded = [p for p in active_players if not p.folded and p.active]
                if len(non_folded) <= 1: break

                next_actor = None
                for offset in range(n):
                    idx2 = order[(loop_count - 1 + offset) % n]
                    p = active_players[idx2]
                    if not p.folded and p.active and p.name not in acted:
                        next_actor = p; break

                if next_actor is None:
                    if all(self.street_bets.get(p.name,0) >= to_call
                           for p in active_players if not p.folded and p.active):
                        break
                    acted = set()
                    for offset in range(n):
                        idx2 = order[offset % n]; p = active_players[idx2]
                        if not p.folded and p.active: next_actor = p; break

                if next_actor is None: break

                p_call_needed = max(0, to_call - self.street_bets.get(next_actor.name, 0))
                next_actor.send({'type':'your_turn','street':street,
                                 'pot':self.pot,'to_call':p_call_needed})

                self._action_event.clear()
                self._pending_action = None
                deadline = time.time() + 60
                while time.time() < deadline:
                    self._action_event.wait(timeout=1.0)
                    self._action_event.clear()
                    if self._pending_action and self._pending_action[0] == next_actor.name: break
                    if not next_actor.active:
                        self._pending_action = (next_actor.name, 'fold', 0); break

                if self._pending_action is None:
                    self._pending_action = (next_actor.name, 'check' if p_call_needed==0 else 'fold', 0)

                _, action, amount = self._pending_action
                acted.add(next_actor.name)
                log_amount = 0

                if action == 'fold':
                    next_actor.folded = True
                elif action == 'call':
                    paid = min(p_call_needed, next_actor.money)
                    next_actor.money -= paid; self.pot += paid
                    self.street_bets[next_actor.name] = self.street_bets.get(next_actor.name,0) + paid
                    log_amount = paid
                elif action == 'raise':
                    total = min(p_call_needed + amount, next_actor.money)
                    next_actor.money -= total; self.pot += total
                    self.street_bets[next_actor.name] = self.street_bets.get(next_actor.name,0) + total
                    to_call = self.street_bets[next_actor.name]
                    acted = {next_actor.name}
                    log_amount = total

                self.broadcast_all({'type':'player_action','player':next_actor.name,
                                    'action':action,'amount':log_amount,
                                    'pot':self.pot,'players':self._players_info()})
                time.sleep(0.3)

                non_folded = [p for p in active_players if not p.folded and p.active]
                if len(non_folded) <= 1: break

            non_folded = [p for p in active_players if not p.folded and p.active]
            if len(non_folded) == 1:
                winner = non_folded[0]; winner.money += self.pot
                for p in active_players:
                    p.send({'type':'result','winner':winner.name,'hand_name':'Todos se retiraron',
                            'pot':self.pot,'my_money':p.money,'players':self._players_info()})
                self.pot = 0; return

        non_folded = [p for p in active_players if not p.folded and p.active]
        scored = []
        for p in non_folded:
            score, hand_name = best_hand(p.hand + self.community)
            scored.append((score, p, hand_name))
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score = scored[0][0]
        winners = [x for x in scored if x[0] == best_score]
        split = self.pot // len(winners)
        for _, w, _ in winners: w.money += split
        winner_p = winners[0][1]; hand_name = winners[0][2]
        for p in active_players:
            p.send({'type':'result','winner':winner_p.name,'hand_name':hand_name,
                    'pot':self.pot,'my_money':p.money,'players':self._players_info()})
        self.pot = 0

    def receive_action(self, player, action, amount):
        self._pending_action = (player.name, action, amount)
        self._action_event.set()


def recv_loop(sock, room: PokerRoom):
    buf_by_addr = {}
    while True:
        try:
            data, addr = sock.recvfrom(65507)
        except Exception as e:
            print(f"[!] recvfrom error: {e}"); continue

        chunk = buf_by_addr.get(addr, b"") + data
        while b'\n' in chunk:
            line, chunk = chunk.split(b'\n', 1)
            line = line.strip()
            if not line: continue
            try:
                msg = json.loads(line.decode('utf-8', errors='replace'))
            except Exception:
                continue

            mtype  = msg.get('type', '')
            player = room.get_player_by_addr(addr)

            if mtype == 'ping':
                if player: player.last_seen = time.time()
                sock.sendto((json.dumps({'type':'pong'})+'\n').encode(), addr)

            elif mtype == 'join' and player is None:
                room.add_player(addr, str(msg.get('name','Jugador'))[:20])

            elif mtype == 'action' and player is not None:
                player.last_seen = time.time()
                room.receive_action(player, str(msg.get('action','fold')).lower(), int(msg.get('amount',0)))

        buf_by_addr[addr] = chunk


def main():
    global _udp_sock
    parser = argparse.ArgumentParser(description="Servidor Poker UDP — El Farol Rojo")
    parser.add_argument('--port',        type=int, default=5555)
    parser.add_argument('--min-players', type=int, default=2)
    parser.add_argument('--max-players', type=int, default=6)
    args = parser.parse_args()

    room = PokerRoom(min_players=args.min_players, max_players=args.max_players)
    _udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _udp_sock.bind(('0.0.0.0', args.port))
    print(f"[SERVER] UDP en 0.0.0.0:{args.port} (mín {args.min_players}, máx {args.max_players})")

    threading.Thread(target=room.heartbeat_checker, daemon=True).start()
    try:
        recv_loop(_udp_sock, room)
    except KeyboardInterrupt:
        print("\n[SERVER] Detenido.")
    finally:
        _udp_sock.close()

if __name__ == '__main__':
    main()
