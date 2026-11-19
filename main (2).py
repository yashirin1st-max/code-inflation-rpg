# Code Inflation RPG — Kivy versiyasi (ovoz + qobiliyatlar, tuzatilgan)
# PC: pip install kivy  ->  python main.py
# APK: buildozer android debug  (buildozer.spec: source.include_exts = py,png,jpg,kv,atlas,ttf)
# Shrift: fonts/DejaVuSans.ttf faylini main.py yoniga qo'ying (belgilar ✦ ♜ ➶ ko'rinishi uchun)
# Boshqaruv: PC da WASD / strelkalar + SPACE (hujum) + Q (qobiliyat), telefonda joystick + tugmalar
import math, random, json, os, re, wave as wave_mod, struct
from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')
from kivy.app import App
from kivy.core.window import Window
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.graphics import Color, Rectangle, Ellipse, Line, Triangle
from kivy.clock import Clock
import kivy

Window.clearcolor = (0.03, 0.06, 0.2, 1)
if platform != 'android':
    try:
        Window.size = (1100, 700)
    except Exception:
        pass

# ---------- SHRIFT ----------
_HERE = os.path.dirname(os.path.abspath(__file__))
def setup_font():
    cands = [
        os.path.join(_HERE, "fonts", "DejaVuSans.ttf"),
        os.path.join(_HERE, "DejaVuSans.ttf"),
        os.path.join(kivy.kivy_data_dir, "fonts", "DejaVuSans.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            try:
                LabelBase.register(DEFAULT_FONT, fn_regular=c, fn_bold=c)
                return True
            except Exception:
                pass
    return False
setup_font()

# Shrift qo'llab-quvvatlamaydigan belgilarni (emoji) tozalaydi
_NONBMP = re.compile('[\U00010000-\U0010FFFF\uFE0F\u200D]')
def T(s):
    s = str(s).replace('🪙', '$').replace('♾', '∞').replace('⏸', '').replace('⭐', '★')
    return _NONBMP.sub('', s).strip()

def fmt(n):
    return f"{n:,}".replace(",", " ")

def data_path(name):
    app = App.get_running_app()
    base = app.user_data_dir if app else _HERE
    try:
        os.makedirs(base, exist_ok=True)
    except Exception:
        pass
    return os.path.join(base, name)

# ---------- MASOFA (ekran nisbati bilan) ----------
ASPECT = 1.0
def dist(ax, ay, bx, by):
    return math.hypot((ax - bx) * ASPECT, ay - by)

# ---------- DATA ----------
HEROES = {
    "Dasturchi": {"hp": 110, "mp": 60, "atk": 18, "def": 10, "spd": 3.3, "color": (0.16,0.59,1), "mark": "</>"},
    "Sehrgar":   {"hp": 80, "mp": 120, "atk": 24, "def": 6, "spd": 3.0, "color": (0.69,0.35,1), "mark": "✦"},
    "Kamondan":  {"hp": 95, "mp": 75, "atk": 20, "def": 8, "spd": 3.7, "color": (0.27,0.8,0.43), "mark": "➶"},
    "Ritsar":    {"hp": 145, "mp": 45, "atk": 17, "def": 17, "spd": 2.7, "color": (0.75,0.8,0.88), "mark": "♜"},
    "Assassin":  {"hp": 85, "mp": 70, "atk": 27, "def": 5, "spd": 4.2, "color": (0.92,0.25,0.33), "mark": "✦"},
}
ITEMS = [
    {"name": "Bash xanjari", "kind": "Qurol", "price": 130, "atk": 4, "icon": "⚔"},
    {"name": "Java nayzasi", "kind": "Qurol", "price": 390, "atk": 7, "icon": "⚔"},
    {"name": "Python qilichi", "kind": "Qurol", "price": 510, "atk": 8, "icon": "⚔"},
    {"name": "Sehrli kamon", "kind": "Qurol", "price": 800, "atk": 10, "icon": "➶"},
    {"name": "C++ boltasi", "kind": "Qurol", "price": 970, "atk": 11, "icon": "⚔"},
    {"name": "Kvant qilichi", "kind": "Qurol", "price": 2050, "atk": 16, "icon": "⚔"},
    {"name": "Cheksiz sikl qilichi", "kind": "Qurol", "price": 4610, "atk": 24, "icon": "⚔"},
    {"name": "Charm kiyim", "kind": "Zirh", "price": 90, "def": 3, "icon": "♜"},
    {"name": "Zanjirli zirh", "kind": "Zirh", "price": 250, "def": 5, "icon": "♜"},
    {"name": "Temir zirh", "kind": "Zirh", "price": 490, "def": 7, "icon": "♜"},
    {"name": "Fayrvol zirhi", "kind": "Zirh", "price": 640, "def": 8, "icon": "♜"},
    {"name": "Kriptografik zirh", "kind": "Zirh", "price": 1440, "def": 12, "icon": "♜"},
    {"name": "Oltin zirh", "kind": "Zirh", "price": 1690, "def": 13, "icon": "♜"},
    {"name": "Ajdarho tangachasi", "kind": "Zirh", "price": 3240, "def": 18, "icon": "♜"},
    {"name": "Kod bilaguzugi", "kind": "Aksessuar", "price": 130, "atk": 2, "def": 2, "icon": "◉"},
    {"name": "Himoya tumori", "kind": "Aksessuar", "price": 200, "def": 5, "icon": "✧"},
    {"name": "Quvvat uzugi", "kind": "Aksessuar", "price": 200, "atk": 5, "icon": "◉"},
    {"name": "Server taqinchog'i", "kind": "Aksessuar", "price": 290, "atk": 3, "def": 3, "icon": "◉"},
    {"name": "Git amuleti", "kind": "Aksessuar", "price": 650, "atk": 5, "def": 4, "icon": "✧"},
    {"name": "Neyron tojchasi", "kind": "Aksessuar", "price": 1350, "atk": 7, "def": 6, "icon": "✧"},
    {"name": "Algoritm yuragi", "kind": "Aksessuar", "price": 2890, "atk": 10, "def": 9, "icon": "♥"},
    {"name": "Qizil eliksir", "kind": "Dori", "price": 70, "heal": 45, "icon": "♥"},
    {"name": "Ko'k eliksir", "kind": "Dori", "price": 70, "mana": 35, "icon": "♦"},
]
ENEMIES = [
    ("Yashil maxluq", 38, 8, (0.35,0.86,0.33), "●"),
    ("Skelet", 52, 11, (0.86,0.88,0.92), "☠"),
    ("Goblin", 68, 14, (0.43,0.75,0.31), "♟"),
    ("Ajdarho", 125, 20, (0.92,0.29,0.25), "▲"),
]
BOSSES = [
    ("Kod Ajdarhosi", 320, 26, (0.92,0.29,0.25), "▲", "Olovli nafas!", "fire"),
    ("Bug Qiroli", 280, 24, (0.55,0.2,0.85), "☠", "Hamma buglar shohi!", "swarm"),
    ("Server Dev", 380, 28, (0.2,0.6,0.9), "♜", "Server quladi!", "stun"),
    ("Neyron Tarmoq", 340, 30, (0.1,0.9,0.7), "✦", "U o'rganmoqda...", "learn"),
    ("Qora Xaker", 300, 32, (0.1,0.1,0.1), "☣", "Parolingiz buzildi!", "hack"),
    ("Cheksiz Sikl", 420, 30, (1,0.6,0.1), "∞", "while True: hujum!", "loop"),
    ("Virus Malika", 360, 27, (0.95,0.3,0.65), "♛", "Tizim zararlandi!", "poison"),
    ("Algoritm Golemi", 460, 34, (0.6,0.6,0.65), "♞", "O(n^2) zarba!", "slam"),
]
SPECIAL_INFO = {
    "fire": "Olovli nafas: yaqin bo'lsang katta zarba",
    "swarm": "Bug to'dasi: mayda buglar chaqiradi",
    "stun": "Server quladi: 1.5 soniya qotib qolasan",
    "learn": "Neyron o'rganish: HP tiklaydi + tezlashadi",
    "hack": "Xakerlik: tanga + mana o'g'irlaydi",
    "loop": "Cheksiz sikl: ketma-ket 3 ta tez zarba",
    "poison": "Virus: 5 soniya zahar (HP sekin kamayadi)",
    "slam": "Golem zarbi: yaqin atrofdagilarni uloqtiradi",
}
AREAS = [
    ("O'rmon", (0.15,0.41,0.22,1)),
    ("Qorong'u g'or", (0.12,0.10,0.20,1)),
    ("Lava vodiysi", (0.45,0.12,0.05,1)),
    ("Muz cho'qqisi", (0.45,0.70,0.85,1)),
    ("Kiber shahar", (0.05,0.10,0.35,1)),
    ("Kosmos stansiyasi", (0.05,0.05,0.15,1)),
]
ABILITIES = {
    'Dasturchi': {'name': 'Debug', 'desc': '5s: dushmanlar sekin + sen 2x tez urasan', 'cd': 25},
    'Sehrgar': {'name': 'Olov yomgiri', 'desc': 'Hamma dushmanga birdan katta zarba', 'cd': 30},
    'Kamondan': {'name': 'Aniq nishon', 'desc': 'Keyingi 3 ta oq 3x zarba, uzoqdan uradi', 'cd': 22},
    'Ritsar': {'name': 'Temir qalqon', 'desc': '6s: hech qanday zarba yemaysan', 'cd': 28},
    'Assassin': {'name': 'Soya zarbi', 'desc': 'Dushman ortiga teleport + 4x kritik', 'cd': 20},
}
ABILITY_MP_COST = 20   # 0 qilsangiz qobiliyat manasiz bo'ladi
MP_REGEN = 1.5         # soniyasiga

MYTHIC_ITEMS = []
_mythic_data = {
    "Dasturchi": {"weapon": ("Abadiy Kod Qilichi", "⚔", 120), "armor": ("Dasturchi Zirhi", "♜", 80), "acc": ("GitHub Toji", "✧", 60, 50)},
    "Sehrgar":   {"weapon": ("Galaktika Tayog'i", "✦", 140), "armor": ("Yulduz Mantiyasi", "♜", 70), "acc": ("Sehrli Ko'z", "✧", 70, 60)},
    "Kamondan":  {"weapon": ("Bo'ron Kamoni", "➶", 130), "armor": ("Shamol Zirhi", "♜", 75), "acc": ("Burgut Ko'zi", "◉", 65, 55)},
    "Ritsar":    {"weapon": ("Adolat Qilichi", "⚔", 110), "armor": ("Afsonaviy Qalqon", "♜", 110), "acc": ("Qirol Yuragi", "♥", 50, 70)},
    "Assassin":  {"weapon": ("Soya Xanjari", "⚔", 150), "armor": ("Soya Plashi", "♜", 60), "acc": ("Tungi Ko'z", "◉", 75, 45)},
}
for _hero, _d in _mythic_data.items():
    _w, _wicon, _watk = _d["weapon"]
    MYTHIC_ITEMS.append({"name": _w, "kind": "Qurol", "price": 1000000, "atk": _watk, "icon": _wicon, "hero": _hero, "mythic": True})
    _a, _aicon, _adef = _d["armor"]
    MYTHIC_ITEMS.append({"name": _a, "kind": "Zirh", "price": 1000000, "def": _adef, "icon": _aicon, "hero": _hero, "mythic": True})
    _c, _cicon, _catk, _cdef = _d["acc"]
    MYTHIC_ITEMS.append({"name": _c, "kind": "Aksessuar", "price": 1000000, "atk": _catk, "def": _cdef, "icon": _cicon, "hero": _hero, "mythic": True})
ITEMS.extend(MYTHIC_ITEMS)

TIER_COLORS = [(0.59,0.43,0.27),(0.67,0.69,0.73),(0.31,0.78,0.59),(0.27,0.59,1),(0.69,0.37,1),(1,0.75,0.18),(0.47,0.94,1)]

# ---------- OVOZ: tashqi faylsiz WAV sintez ----------
class SoundManager:
    def __init__(self):
        self.paths = {}; self.sounds = {}
        self.music_sound = None; self.music_kind = None
        try:
            from kivy.core.audio import SoundLoader as _SL
            self.SL = _SL
        except Exception:
            self.SL = None
    def _wav(self, name, freqs, dur, vol, wave_type, slide):
        if name in self.paths: return self.paths[name]
        try:
            sr = 22050; n = int(sr * dur); frames = bytearray()
            for i in range(n):
                tt = i / sr; v = 0.0
                for f0, amp in freqs:
                    f = f0 * (1 + slide * tt / dur) if slide else f0
                    ph = 2 * math.pi * f * tt
                    if wave_type == 'square': vv = 1.0 if math.sin(ph) > 0 else -1.0
                    elif wave_type == 'saw': vv = 2 * ((ph / (2 * math.pi)) % 1) - 1
                    else: vv = math.sin(ph)
                    v += vv * amp
                env = min(1.0, tt * 40) * (1 - tt / dur) ** 1.2
                frames += struct.pack('<h', int(max(-1, min(1, v * vol * env)) * 32767))
            path = data_path('snd_' + name + '.wav')
            with wave_mod.open(path, 'wb') as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(bytes(frames))
            self.paths[name] = path
            return path
        except Exception as e:
            print('sound gen', e); return None
    def _sound(self, name, freqs, dur, vol, wave_type, slide):
        if name in self.sounds: return self.sounds[name]
        s = None
        if self.SL:
            path = self._wav(name, freqs, dur, vol, wave_type, slide)
            if path:
                try: s = self.SL.load(path)
                except Exception: s = None
        self.sounds[name] = s
        return s
    def play(self, name, freqs, dur=0.25, vol=0.35, wave_type='square', slide=0):
        if STATE.settings.get('muted'): return
        try:
            s = self._sound(name, freqs, dur, vol, wave_type, slide)
            if s:
                s.volume = max(0, min(1, STATE.settings.get('sfx', 0.7)))
                s.stop(); s.play()
        except Exception as e:
            print('sound play', e)
    def swing(self): self.play('swing', [(500,0.6),(300,0.4)], 0.12, 0.35, 'square', -0.4)
    def hit(self): self.play('hit', [(200,0.8),(120,0.5)], 0.15, 0.35, 'square')
    def kill(self): self.play('kill', [(600,0.5),(900,0.4)], 0.25, 0.35, 'saw', 0.5)
    def coin(self): self.play('coin', [(1200,0.6),(1800,0.5)], 0.18, 0.35, 'sine', 0.3)
    def levelup(self): self.play('levelup', [(523,0.5),(659,0.5),(784,0.5),(1046,0.6)], 0.6, 0.4, 'sine', 0.2)
    def boss_roar(self): self.play('boss', [(80,0.9),(60,0.7)], 0.8, 0.5, 'saw', -0.2)
    def portal(self): self.play('portal', [(300,0.5),(600,0.5),(1200,0.5)], 0.6, 0.4, 'sine', 1.0)
    def buy(self): self.play('buy', [(900,0.5),(1300,0.5)], 0.2, 0.35, 'sine', 0.3)
    def error(self): self.play('error', [(200,0.7),(150,0.7)], 0.25, 0.35, 'square', -0.2)
    def hurt(self): self.play('hurt', [(180,0.8)], 0.2, 0.35, 'saw', -0.3)
    def ability(self, hero):
        m = {'Dasturchi': ([(800,0.5),(1000,0.5)], 0.3, 'square'), 'Sehrgar': ([(200,0.8),(100,0.7)], 0.5, 'saw'),
             'Kamondan': ([(1500,0.6)], 0.15, 'sine'), 'Ritsar': ([(400,0.7),(600,0.6)], 0.4, 'sine'),
             'Assassin': ([(2000,0.4),(1500,0.4)], 0.2, 'sine')}
        f, d, w = m.get(hero, ([(800,0.5)], 0.3, 'square'))
        self.play('ability_' + hero, f, d, 0.5, w)
    def stop_music(self):
        if self.music_sound:
            try: self.music_sound.stop()
            except Exception: pass
        self.music_sound = None; self.music_kind = None
    def music(self, kind):
        if STATE.settings.get('muted'):
            self.stop_music(); return
        vol = max(0, min(1, STATE.settings.get('music', 0.5) * 0.6))
        if self.music_kind == kind:
            if self.music_sound: self.music_sound.volume = vol
            return
        self.stop_music(); self.music_kind = kind  # xato bo'lsa ham har kadrda qayta urinmaydi
        try:
            freqs = ([(110,0.4),(130,0.4),(110,0.4),(165,0.4)] if kind == 'boss'
                     else [(440,0.3),(550,0.3),(660,0.3),(880,0.3)] if kind == 'portal'
                     else [(262,0.3),(330,0.3),(392,0.3),(330,0.3)])
            path = self._wav('music_' + kind, freqs, 1.2, 0.15, 'sine', 0.05)
            if path and self.SL:
                s = self.SL.load(path)
                if s:
                    s.volume = vol; s.loop = True; s.play(); self.music_sound = s
        except Exception as e:
            print('music', e)
SOUND = SoundManager()

# ---------- STATE ----------
class Player:
    def __init__(self, hero="Dasturchi"):
        self.hero = hero
        d = HEROES[hero]
        self.max_hp, self.hp = d["hp"], d["hp"]
        self.max_mp, self.mp = d["mp"], float(d["mp"])
        self.atk, self.defense, self.speed = d["atk"], d["def"], d["spd"]
        self.x, self.y = 0.35, 0.5
        self.level, self.xp, self.coins = 1, 0, 250
        self.inventory = []
        self.equipped = {"Qurol": None, "Zirh": None, "Aksessuar": None}
        self.attack_cd = 0
        self.facing = 1
        self.stunned = 0
        self.poisoned = 0
        self.poison_timer = 0
        self.ability_cd = 0
        self.ability_active = ''
        self.ability_timer = 0
        self.precise_shots = 0
        self.shadow_next = False
        self.invisible_timer = 0
    def reset_effects(self):
        self.stunned = 0; self.poisoned = 0; self.ability_active = ''; self.ability_timer = 0
        self.precise_shots = 0; self.shadow_next = False; self.invisible_timer = 0
    def bonus(self, k): return sum(i.get(k, 0) for i in self.equipped.values() if i)
    def total(self, k):
        base = {"atk": self.atk, "def": self.defense, "hp": self.max_hp, "mp": self.max_mp}[k]
        return base + self.bonus(k)
    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.level * 100:
            self.xp -= self.level * 100; self.level += 1; leveled = True
            self.max_hp += 12; self.hp = self.max_hp; self.atk += 3; self.defense += 1
            self.max_mp += 5; self.mp = float(self.max_mp)
        return leveled

class Enemy:
    def __init__(self, wave, boss_data=None):
        if boss_data:
            name, hp, atk, color, mark, taunt, special = boss_data
            self.name, self.max_hp = name, hp + wave * 18
            self.hp, self.atk, self.color, self.mark = self.max_hp, atk + wave * 2, color, mark
            self.is_boss = True; self.taunt = taunt; self.special = special; self.speed = 0.9 + wave * 0.02
            self.special_cd = 4.0; self.loop_hits = 0; self.loop_timer = 0
        else:
            name, hp, atk, color, mark = random.choice(ENEMIES[:min(4, 1 + wave // 2)])
            self.name, self.max_hp = name, hp + wave * 7
            self.hp, self.atk, self.color, self.mark = self.max_hp, atk + wave * 2, color, mark
            self.is_boss = False; self.taunt = ""; self.special = ""; self.speed = 0.65 + wave * 0.035
            self.special_cd = 0; self.loop_hits = 0; self.loop_timer = 0
        self.x = random.uniform(0.08, 0.92); self.y = random.uniform(0.22, 0.88)
        self.hit_cd = 0

class GameState:
    def __init__(self):
        self.selected_hero = "Dasturchi"
        self.player = Player()
        self.enemies = []; self.wave = 1; self.kills = 0
        self.boss_count = 0; self.last_boss_name = None; self.boss_defeated = 0
        self.portal_active = False; self.portal_x = 0.8; self.portal_y = 0.5
        self.area_index = 0; self.portal_wave_timer = 0; self.boss_special_msg = ""
        self.flash = 0; self.flash_text = ""
        self.message = "Sarguzasht boshlashga tayyormisiz?"
        self.settings = {"music": 0.5, "sfx": 0.7, "muted": False}

    # ---------- sozlamalar ----------
    def load_settings(self):
        try:
            p = data_path("settings.json")
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    self.settings.update(json.load(f))
        except Exception:
            pass
    def save(self):
        try:
            with open(data_path("settings.json"), "w", encoding="utf-8") as f:
                json.dump(self.settings, f)
        except Exception:
            pass

    # ---------- saqlash ----------
    def save_path(self): return data_path("savegame.json")
    def has_save(self):
        try: return os.path.exists(self.save_path())
        except Exception: return False
    def save_game(self):
        try:
            pl = self.player
            data = {"hero": pl.hero, "hp": pl.hp, "max_hp": pl.max_hp, "mp": pl.mp, "max_mp": pl.max_mp,
                    "atk": pl.atk, "defense": pl.defense, "speed": pl.speed, "x": pl.x, "y": pl.y,
                    "level": pl.level, "xp": pl.xp, "coins": pl.coins, "inventory": pl.inventory,
                    "equipped": pl.equipped, "wave": self.wave, "kills": self.kills,
                    "boss_count": self.boss_count, "last_boss_name": self.last_boss_name,
                    "boss_defeated": self.boss_defeated, "portal_active": self.portal_active,
                    "portal_x": self.portal_x, "portal_y": self.portal_y, "area_index": self.area_index}
            tmp = self.save_path() + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f)
            os.replace(tmp, self.save_path())
            return True
        except Exception as e:
            print("save error", e); return False
    def load_game(self):
        try:
            with open(self.save_path(), encoding="utf-8") as f:
                d = json.load(f)
            pl = Player(d.get("hero", "Dasturchi"))
            pl.hp = d.get("hp", pl.max_hp); pl.max_hp = d.get("max_hp", pl.max_hp)
            pl.mp = float(d.get("mp", pl.max_mp)); pl.max_mp = d.get("max_mp", pl.max_mp)
            pl.atk = d.get("atk", pl.atk); pl.defense = d.get("defense", pl.defense); pl.speed = d.get("speed", pl.speed)
            pl.x = d.get("x", 0.35); pl.y = d.get("y", 0.5); pl.level = d.get("level", 1)
            pl.xp = d.get("xp", 0); pl.coins = d.get("coins", 250)
            pl.inventory = d.get("inventory", []); pl.equipped = d.get("equipped", {})
            for k in ("Qurol", "Zirh", "Aksessuar"):
                if k not in pl.equipped: pl.equipped[k] = None
            self.player = pl; self.selected_hero = pl.hero
            self.wave = d.get("wave", 1); self.kills = d.get("kills", 0)
            self.boss_count = d.get("boss_count", 0); self.last_boss_name = d.get("last_boss_name")
            self.boss_defeated = d.get("boss_defeated", 0)
            self.portal_active = d.get("portal_active", False)
            self.portal_x = d.get("portal_x", 0.82); self.portal_y = d.get("portal_y", 0.5)
            self.area_index = d.get("area_index", 0) % len(AREAS); self.portal_wave_timer = 0
            pl.reset_effects()
            if self.portal_active:
                self.enemies = []
            else:
                bc = self.boss_count
                self.spawn_wave(); self.boss_count = bc
            self.say(f"Davom etilmoqda! {AREAS[self.area_index][0]} - {self.wave}-to'lqin")
            return True
        except Exception as e:
            print("load error", e); return False
    def delete_save(self):
        try:
            if os.path.exists(self.save_path()): os.remove(self.save_path())
        except Exception: pass
    def save_summary(self):
        if not self.has_save(): return None
        try:
            with open(self.save_path(), encoding="utf-8") as f:
                d = json.load(f)
            return (f"{d.get('hero','?')} - Lv.{d.get('level',1)} - {d.get('wave',1)}-to'lqin - "
                    f"{AREAS[d.get('area_index',0) % len(AREAS)][0]} - 🪙 {d.get('coins',0)} - Boss: {d.get('boss_defeated',0)}")
        except Exception: return None

    # ---------- o'yin mantiqi ----------
    def spawn_wave(self):
        if self.wave % 5 == 0:
            pool = [b for b in BOSSES if b[0] != self.last_boss_name]
            boss_data = random.choice(pool)
            self.last_boss_name = boss_data[0]; self.boss_count += 1
            boss = Enemy(self.wave, boss_data=boss_data)
            boss.x, boss.y = 0.5, 0.55
            self.enemies = [boss] + [Enemy(self.wave) for _ in range(2)]
            self.say(f"BOSS! {boss_data[0]} paydo bo'ldi! {boss_data[5]}")
            SOUND.boss_roar(); self.boss_special_msg = SPECIAL_INFO.get(boss_data[6], "")
        else:
            self.enemies = [Enemy(self.wave) for _ in range(min(3 + self.wave, 9))]
    def start(self, hero=None):
        self.player = Player(hero or self.selected_hero); self.wave = 1; self.kills = 0
        self.boss_count = 0; self.last_boss_name = None; self.boss_defeated = 0
        self.portal_active = False; self.area_index = 0; self.portal_wave_timer = 0
        self.spawn_wave(); self.say("Sarguzasht boshlandi!"); self.save_game()
    def say(self, t): self.message = t

    # himoya: qalqon yoki soya paytida zarba/holat o'tmaydi
    def shielded(self):
        p = self.player
        return p.ability_active == 'shield' or p.invisible_timer > 0
    def hurt(self, dmg):
        p = self.player
        if dmg <= 0 or self.shielded(): return False
        p.hp -= dmg; SOUND.hurt()
        if p.hp <= 0: self._player_die()
        return True

    def use_ability(self):
        p = self.player; hero = p.hero
        info = ABILITIES.get(hero)
        if not info: return False
        if p.stunned > 0: self.say("Qotib qolding! Kuting..."); return False
        if p.ability_cd > 0:
            self.say(f"Qobiliyat hali tayyor emas! {p.ability_cd:.0f}s kuting."); SOUND.error(); return False
        if p.mp < ABILITY_MP_COST:
            self.say(f"Mana yetarli emas! Kerak: {ABILITY_MP_COST}"); SOUND.error(); return False
        if hero == 'Assassin' and not self.enemies:
            self.say("Atrofda dushman yo'q!"); return False
        boost = any(it and it.get('mythic') for it in p.equipped.values())
        mult = 2.0 if boost else 1.0
        tag = ' AFSONAVIY: kuchliroq!' if boost else ''
        p.mp -= ABILITY_MP_COST; p.ability_cd = info['cd']; SOUND.ability(hero)
        if hero == 'Dasturchi':
            p.ability_active = 'debug'; p.ability_timer = 5.0
            self.say('DEBUG! Dushmanlar sekinlashdi, sen 2x tez urasan!' + tag)
        elif hero == 'Sehrgar':
            dmg = int(p.total('atk') * 1.8 * mult)
            for e in list(self.enemies):
                self._damage(e, dmg)
            p.ability_active = 'fire_rain'; p.ability_timer = 1.0
            if not self.portal_active:
                self.say(f'Olov yomgiri! Hammaga {dmg} zarba!' + tag)
        elif hero == 'Kamondan':
            p.precise_shots = 3; p.ability_active = 'precise'; p.ability_timer = 12.0
            self.say('Aniq nishon! Keyingi 3 oq 3x zarba, uzoqdan uradi!' + tag)
        elif hero == 'Ritsar':
            p.ability_active = 'shield'; p.ability_timer = 6.0
            self.say('Temir qalqon! 6s zarba yemaysan!' + tag)
        elif hero == 'Assassin':
            target = min(self.enemies, key=lambda e: dist(e.x, e.y, p.x, p.y))
            p.x = max(0.05, min(0.95, target.x - 0.07 / ASPECT)); p.y = max(0.2, min(0.92, target.y))
            p.shadow_next = True; p.invisible_timer = 2.0; p.ability_active = 'shadow'; p.ability_timer = 2.0
            self.say('Soya zarbi! Keyingi hujum 4x kritik!' + tag)
        if boost and hero != 'Sehrgar' and p.ability_timer > 0:
            p.ability_timer *= 1.5
            if p.invisible_timer > 0: p.invisible_timer *= 1.5
        return True

    def buy(self, item):
        p = self.player
        if item.get("mythic") and item.get("hero") != p.hero:
            self.say(f"Bu afsonaviy buyum faqat {item.get('hero')} ga mos! Siz: {p.hero}"); SOUND.error(); return False
        if p.coins < item["price"]: self.say("Tangalar yetarli emas!"); SOUND.error(); return False
        p.coins -= item["price"]; p.inventory.append(dict(item)); self.say(item["name"] + " sotib olindi.")
        SOUND.buy(); self.save_game(); return True
    def equip(self, item):
        p = self.player
        if item.get("mythic") and item.get("hero") != p.hero:
            self.say(f"Bu afsonaviy buyum faqat {item.get('hero')} ga mos!"); return
        if item["kind"] in p.equipped:
            p.equipped[item["kind"]] = item; self.say(item["name"] + " jihozlandi!")
        elif item["kind"] == "Dori":
            if "heal" in item: p.hp = min(p.max_hp, p.hp + item["heal"])
            if "mana" in item: p.mp = min(p.max_mp, p.mp + item["mana"])
            p.inventory.remove(item); self.say("Eliksir ishlatildi!")

    def _damage(self, e, dmg):
        e.hp -= dmg
        if e.hp <= 0 and e in self.enemies:
            self._on_kill(e)
    def _on_kill(self, target):
        p = self.player
        was_boss = getattr(target, 'is_boss', False)
        if target in self.enemies: self.enemies.remove(target)
        SOUND.kill(); SOUND.coin()
        if was_boss:
            bonus_coins = 150 + self.wave * 25; bonus_xp = 150 + self.wave * 20
            p.coins += bonus_coins; self.boss_defeated += 1; self.kills += 1
            lv = p.gain_xp(bonus_xp)
            self.portal_active = True; self.portal_x = 0.82; self.portal_y = 0.5; self.portal_wave_timer = 0
            self.say(f"BOSS YENGILDI! {target.name} mag'lub! +{bonus_coins} tanga, +{bonus_xp} XP!"
                     + (" LEVEL UP!" if lv else "") + " PORTAL ochildi! Unga kiring!")
            self.save_game()
        else:
            p.coins += 25 + self.wave * 4
            lv = p.gain_xp(35 + self.wave * 5); self.kills += 1
            self.say("G'alaba! Tanga va tajriba olindi." + (" LEVEL UP!" if lv else ""))
        if lv: SOUND.levelup()
        if not self.enemies and not self.portal_active:
            self.wave += 1; p.hp = min(p.max_hp, p.hp + 18); self.spawn_wave()
            if self.wave % 5 != 0:
                self.say(f"{self.wave}-to'lqin boshlandi!")
            self.save_game()
    def attack(self):
        p = self.player
        if p.attack_cd > 0: return
        if p.stunned > 0: self.say("Qotib qolding! Kuting..."); return
        SOUND.swing()
        p.attack_cd = 0.19 if p.ability_active == 'debug' else 0.38
        rmul = 2.0 if p.ability_active == 'precise' else 1.0
        target = None; bd = 9
        for e in self.enemies:
            d = dist(e.x, e.y, p.x, p.y)
            reach = (0.22 if getattr(e, 'is_boss', False) else 0.14) * rmul
            if d < reach and d < bd:
                bd, target = d, e
        if target:
            dmg = max(1, p.total("atk") - self.wave)
            if p.precise_shots > 0:
                dmg *= 3; p.precise_shots -= 1
                if p.precise_shots == 0 and p.ability_active == 'precise':
                    p.ability_active = ''; p.ability_timer = 0
            if p.shadow_next:
                dmg *= 4; p.shadow_next = False
            SOUND.hit()
            self._damage(target, dmg)
        else:
            self.say("Hujum uchun maxluqqa yaqinlashing.")
    def enter_portal(self):
        p = self.player
        if not self.portal_active: return
        self.portal_active = False
        self.area_index = (self.area_index + 1) % len(AREAS)
        self.wave += 1; p.hp = min(p.max_hp, p.hp + int(p.max_hp * 0.3))
        self.enemies = []; self.spawn_wave()
        SOUND.portal(); self.say(f"Yangi hudud: {AREAS[self.area_index][0]}! {self.wave}-to'lqin boshlandi!"); self.save_game()
    def boss_special(self, boss, dt):
        p = self.player
        boss.special_cd -= dt
        if boss.loop_hits > 0:
            boss.loop_timer -= dt
            if boss.loop_timer <= 0 and dist(boss.x, boss.y, p.x, p.y) < 0.25:
                self.hurt(max(1, boss.atk // 2)); boss.loop_hits -= 1; boss.loop_timer = 0.35
                self.flash_text = "Cheksiz sikl zarbasi!"; self.flash = 0.4
            return
        if boss.special_cd > 0: return
        boss.special_cd = 5.0
        d = dist(boss.x, boss.y, p.x, p.y)
        sp = boss.special
        shield = self.shielded()
        if sp == "fire":
            if d < 0.35:
                self.hurt(max(1, boss.atk * 2)); self.flash_text = "Olovli nafas! Katta zarba!"; self.flash = 0.6
            else: self.flash_text = "Olovli nafas — uzoqda eding, qutilding!"; self.flash = 0.4
        elif sp == "swarm":
            for _ in range(3):
                m = Enemy(self.wave)
                m.x = max(0.05, min(0.95, boss.x + random.uniform(-0.15, 0.15)))
                m.y = max(0.2, min(0.9, boss.y + random.uniform(-0.15, 0.15)))
                self.enemies.append(m)
            self.flash_text = "Bug Qiroli 3 ta bug chaqirdi!"; self.flash = 0.6
        elif sp == "stun":
            if not shield: p.stunned = 1.5
            self.flash_text = "Server quladi! 1.5 soniya qotding!" if not shield else "Server quladi — himoya seni saqladi!"; self.flash = 0.6
        elif sp == "learn":
            heal = int(boss.max_hp * 0.12); boss.hp = min(boss.max_hp, boss.hp + heal); boss.speed += 0.05
            self.flash_text = f"Neyron o'rgandi! +{heal} HP, tezlashdi!"; self.flash = 0.6
        elif sp == "hack":
            if not shield:
                stolen = min(120, p.coins); p.coins -= stolen; p.mp = max(0, p.mp - 25)
                self.flash_text = f"Xaker {stolen} tanga + 25 mana o'g'irladi!"
            else: self.flash_text = "Xaker hujumi — himoya seni saqladi!"
            self.flash = 0.6
        elif sp == "loop":
            boss.loop_hits = 3; boss.loop_timer = 0.2; self.flash_text = "Cheksiz sikl boshlandi! Qoch!"; self.flash = 0.6
        elif sp == "poison":
            if not shield: p.poisoned = 5.0
            self.flash_text = "Virus yuqtirding! 5 soniya zahar!" if not shield else "Virus — himoya seni saqladi!"; self.flash = 0.6
        elif sp == "slam":
            if d < 0.38 and not shield:
                self.hurt(max(1, boss.atk * 2))
                p.x = max(0.05, min(0.95, p.x + (p.x - boss.x) * 1.5)); p.y = max(0.2, min(0.92, p.y + (p.y - boss.y) * 1.5))
                self.flash_text = "Golem zarbasi! Uloqtirilding!"; self.flash = 0.6
            else: self.flash_text = "Golem zarbasi — qochib qutilding!"; self.flash = 0.4
    def _player_die(self):
        p = self.player; p.hp = p.max_hp; p.coins = max(0, p.coins - 50); p.x, p.y = 0.35, 0.5
        p.reset_effects()
        self.say("Qahramon qayta tirildi. 50 tanga yo'qotildi.")

STATE = GameState()

def bonus_text(it):
    parts = []
    if "atk" in it: parts.append(f"+{it['atk']} hujum")
    if "def" in it: parts.append(f"+{it['def']} himoya")
    if "heal" in it: parts.append(f"+{it['heal']} HP")
    if "mana" in it: parts.append(f"+{it['mana']} mana")
    return ", ".join(parts)

def tier_of(item):
    if not item: return -1
    same = sorted([i for i in ITEMS if i["kind"] == item["kind"]], key=lambda x: x["price"])
    for idx, it in enumerate(same):
        if it["name"] == item["name"]: return idx
    return 0

# ---------- WIDGETS ----------
def btn(text, on_press=None, bg=(0.1,0.35,0.7,1), size_hint_y=None, height=52, font_size=18):
    b = Button(text=T(text), size_hint_y=size_hint_y, height=height, font_size=font_size, bold=True,
               background_normal='', background_color=bg, color=(1,1,1,1))
    if on_press: b.bind(on_press=on_press)
    return b

def lbl(text, size=16, color=(1,1,1,1), bold=False, halign='left'):
    l = Label(text=T(text), font_size=size, color=color, bold=bold, halign=halign, valign='middle',
              size_hint_y=None, height=size + 12)
    l.bind(size=lambda *a: setattr(l, 'text_size', (l.width, None)))
    return l

def rowlabel(text, size=15):
    l = Label(text=T(text), font_size=size, halign='left', valign='middle')
    l.bind(size=lambda inst, *a: setattr(inst, 'text_size', (inst.width, None)))
    return l

class Joystick(Widget):
    """Analog joystick: diagonal yurishni qo'llab-quvvatlaydi."""
    def __init__(self, on_change, **kw):
        super().__init__(**kw)
        self.on_change = on_change; self.knob = (0, 0)
        self.bind(pos=self._redraw, size=self._redraw); self._redraw()
    def _r(self): return max(1, min(self.width, self.height) / 2)
    def _redraw(self, *a):
        self.canvas.clear()
        cx, cy = self.center; r = self._r(); k = r * 0.4
        with self.canvas:
            Color(0.05, 0.2, 0.5, 0.5); Ellipse(pos=(cx - r, cy - r), size=(2 * r, 2 * r))
            Color(0.4, 0.7, 1, 0.9); Line(circle=(cx, cy, r), width=2)
            Color(0.3, 0.6, 1, 0.9); Ellipse(pos=(cx + self.knob[0] - k, cy + self.knob[1] - k), size=(2 * k, 2 * k))
    def _set(self, touch):
        cx, cy = self.center; r = self._r()
        dx, dy = touch.x - cx, touch.y - cy; d = math.hypot(dx, dy)
        if d > r: dx, dy = dx / d * r, dy / d * r
        self.knob = (dx, dy); vx, vy = dx / r, dy / r
        if math.hypot(vx, vy) < 0.2: vx = vy = 0
        self.on_change(vx, vy); self._redraw()
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self); self._set(touch); return True
        return False
    def on_touch_move(self, touch):
        if touch.grab_current is self: self._set(touch); return True
        return False
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self); self.reset(); return True
        return False
    def reset(self):
        self.knob = (0, 0); self.on_change(0, 0); self._redraw()

class GameCanvas(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.kb = set(); self.joy = [0, 0]; self._bg_key = None
        Clock.schedule_interval(self.update, 1 / 60)
    def move_vec(self):
        x = y = 0.0
        if 'l' in self.kb: x -= 1
        if 'r' in self.kb: x += 1
        if 'd' in self.kb: y -= 1
        if 'u' in self.kb: y += 1
        x += self.joy[0]; y += self.joy[1]
        ln = math.hypot(x, y)
        if ln > 1: x, y = x / ln, y / ln
        return x, y
    def update(self, dt):
        global ASPECT
        app = App.get_running_app()
        if not app or getattr(app, 'sm', None) is None or app.sm.current != 'game':
            return  # boshqa ekranda o'yin to'xtaydi
        if self.height <= 0: return
        ASPECT = self.width / self.height
        dt = min(dt, 0.1)
        p = STATE.player
        if p.attack_cd > 0: p.attack_cd -= dt
        if STATE.flash > 0: STATE.flash -= dt
        p.mp = min(p.max_mp, p.mp + MP_REGEN * dt)
        if p.ability_cd > 0: p.ability_cd -= dt
        if p.ability_timer > 0:
            p.ability_timer -= dt
            if p.ability_timer <= 0:
                p.ability_active = ''; p.precise_shots = 0
        if p.invisible_timer > 0: p.invisible_timer -= dt
        try:
            has_boss = any(getattr(e, 'is_boss', False) for e in STATE.enemies)
            SOUND.music('boss' if has_boss else ('portal' if STATE.portal_active else 'normal'))
        except Exception:
            pass
        if p.poisoned > 0:
            p.poisoned -= dt; p.poison_timer -= dt
            if p.poison_timer <= 0:
                p.poison_timer = 1.0; STATE.hurt(3)
        if p.stunned > 0: p.stunned -= dt
        if STATE.portal_active:
            STATE.portal_wave_timer += dt
            if dist(p.x, p.y, STATE.portal_x, STATE.portal_y) < 0.09:
                STATE.enter_portal(); self.draw(); return
            if STATE.portal_wave_timer >= 6.0:
                STATE.portal_wave_timer = 0
                STATE.enemies = [Enemy(STATE.wave) for _ in range(min(3 + STATE.wave, 9))]
                STATE.say("Portal ochiq! Dushmanlar kelmoqda! Portalga kiring!")
        for e in list(STATE.enemies):
            if getattr(e, 'is_boss', False): STATE.boss_special(e, dt)
        dx, dy = self.move_vec() if p.stunned <= 0 else (0, 0)
        if dx or dy:
            spd = p.speed * 0.35 * dt
            p.x = max(0.05, min(0.95, p.x + dx * spd / ASPECT)); p.y = max(0.2, min(0.92, p.y + dy * spd))
            if dx != 0: p.facing = 1 if dx > 0 else -1
        slow = 0.4 if p.ability_active == 'debug' else 1.0
        for e in list(STATE.enemies):
            ex, ey = p.x - e.x, p.y - e.y; d = max(0.001, dist(e.x, e.y, p.x, p.y))
            if d > 0.07:
                step = e.speed * 0.25 * dt * slow
                e.x += ex / d * step; e.y += ey / d * step
            else:
                e.hit_cd -= dt
                if e.hit_cd <= 0:
                    e.hit_cd = 1.0
                    STATE.hurt(max(1, e.atk - p.total("def") // 2))
        self.draw()
    def _draw_background(self):
        w, h = self.width, self.height
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*AREAS[STATE.area_index][1]); Rectangle(pos=self.pos, size=self.size)
            Color(0.19, 0.5, 0.25, 1)
            for yy in range(0, int(h), 42):
                for xx in range(0, int(w), 42):
                    if ((xx // 42 + yy // 42) % 2) == 0:
                        Rectangle(pos=(self.x + xx, self.y + yy), size=(42, 42))
            Color(0.37, 0.33, 0.25, 1); Rectangle(pos=(self.x + w * 0.42, self.y), size=(w * 0.16, h))
            for tx, ty in [(0.1,0.85),(0.22,0.75),(0.85,0.8),(0.8,0.45),(0.12,0.35),(0.88,0.3)]:
                Color(0.36, 0.23, 0.14, 1); Rectangle(pos=(self.x + w * tx - 5, self.y + h * ty), size=(10, 26))
                Color(0.08, 0.33, 0.18, 1); Ellipse(pos=(self.x + w * tx - 20, self.y + h * ty + 15), size=(40, 40))
    def draw(self):
        w, h = self.width, self.height
        key = (int(w), int(h), int(self.x), int(self.y), STATE.area_index)
        if key != self._bg_key:
            self._bg_key = key; self._draw_background()
        self.canvas.clear()  # faqat harakatlanuvchi qismlar
        with self.canvas:
            if STATE.portal_active:
                _px, _py = self.x + w * STATE.portal_x, self.y + h * STATE.portal_y
                Color(0.6, 0.2, 1, 0.5); Ellipse(pos=(_px - 42, _py - 52), size=(84, 104))
                Color(0.9, 0.6, 1, 1); Ellipse(pos=(_px - 30, _py - 40), size=(60, 80))
                Color(1, 1, 1, 1); Ellipse(pos=(_px - 14, _py - 20), size=(28, 40))
            for e in STATE.enemies:
                ex, ey = self.x + w * e.x, self.y + h * e.y
                _sc = 2.0 if getattr(e, 'is_boss', False) else 1.0
                if getattr(e, 'is_boss', False):
                    Color(1, 0.1, 0.1, 0.35); Ellipse(pos=(ex - 30, ey - 25), size=(60, 60))
                Color(0, 0, 0, 0.35); Ellipse(pos=(ex - 16 * _sc, ey - 18 * _sc), size=(32 * _sc, 9 * _sc))
                Color(*e.color, 1); Ellipse(pos=(ex - 13, ey - 12), size=(26, 26))
                Color(0.96, 0.79, 0.67, 1); Ellipse(pos=(ex - 11, ey + 2), size=(22, 22))
                Color(0.2, 0.2, 0.2, 1); Ellipse(pos=(ex - 5, ey + 10), size=(3, 3)); Ellipse(pos=(ex + 3, ey + 10), size=(3, 3))
                Color(0.1, 0.15, 0.3, 1); Rectangle(pos=(ex - 22, ey + 30), size=(44, 6))
                Color(1, 0.2, 0.2, 1); Rectangle(pos=(ex - 22, ey + 30), size=(44 * max(0, e.hp / e.max_hp), 6))
            p = STATE.player; px, py = self.x + w * p.x, self.y + h * p.y
            hero = HEROES[p.hero]
            armor = p.equipped["Zirh"]; arank = tier_of(armor)
            body = TIER_COLORS[arank] if arank >= 0 else hero["color"]
            alpha = 0.45 if p.invisible_timer > 0 else 1
            Color(0, 0, 0, 0.35); Ellipse(pos=(px - 17, py - 18), size=(34, 10))
            if arank >= 5:
                Color(0.59, 0.14, 0.24, alpha); Triangle(points=[px - 10, py + 2, px + 10, py + 2, px + 17, py + 32, px - 17, py + 32])
            Color(*body, alpha); Rectangle(pos=(px - 12, py), size=(24, 28))
            if armor:
                Color(1, 1, 1, alpha); Rectangle(pos=(px - 8, py + 7), size=(16, 11))
                Color(1, 0.75, 0.18, alpha); Rectangle(pos=(px - 12, py + 18), size=(24, 3))
            Color(0.96, 0.79, 0.67, alpha); Ellipse(pos=(px - 13, py + 26), size=(26, 26))
            Color(0.1, 0.09, 0.15, alpha); Ellipse(pos=(px - 5, py + 34), size=(4, 4)); Ellipse(pos=(px + 3, py + 34), size=(4, 4))
            if arank >= 1:
                Color(*body, alpha); Ellipse(pos=(px - 14, py + 32), size=(28, 14))
            if arank >= 4:
                Color(1, 0.75, 0.18, alpha); Triangle(points=[px - 3, py + 48, px, py + 62, px + 3, py + 48])
            if any(it and it.get("mythic") for it in p.equipped.values()):
                _ac = {"Dasturchi": (0,1,1,1), "Sehrgar": (1,0.3,1,1), "Kamondan": (0.3,1,0.3,1),
                       "Ritsar": (1,0.85,0.1,1), "Assassin": (0.6,0.2,1,1)}[p.hero]
                Color(*_ac); Line(circle=(px, py + 12, 44), width=3)
                Color(_ac[0], _ac[1], _ac[2], 0.25); Ellipse(pos=(px - 44, py - 32), size=(88, 88))
            ab = p.ability_active
            if ab == 'shield':
                Color(0.3, 0.7, 1, 0.6); Line(circle=(px, py + 12, 38), width=4)
            elif ab == 'debug':
                Color(0, 1, 1, 0.7); Line(circle=(px, py + 12, 42), width=3)
            elif ab == 'precise':
                Color(1, 0.85, 0.1, 0.7); Line(circle=(px, py + 12, 42), width=3)
            elif ab == 'shadow':
                Color(0.6, 0.2, 1, 0.5); Ellipse(pos=(px - 20, py - 10), size=(40, 50))
            elif ab == 'fire_rain':
                Color(1, 0.4, 0.1, 0.35); Ellipse(pos=(px - 90, py - 70), size=(180, 180))
            witem = p.equipped["Qurol"]; wrank = tier_of(witem)
            if witem:
                Color(*TIER_COLORS[wrank], 1); Line(points=[px + 12, py + 10, px + 34, py + 28], width=4)
                Color(1, 1, 1, 1); Line(points=[px + 12, py + 10, px + 34, py + 28], width=1)
            else:
                Color(0.47, 0.33, 0.2, 1); Line(points=[px + 12, py + 10, px + 28, py + 24], width=4)

# ---------- SCREENS ----------
class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw); self.build()
    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=24, spacing=12)
        root.add_widget(lbl("@Code Inflation RPG", 34, (0,0.9,1,1), True))
        root.add_widget(lbl("Dasturlash va sarguzashtlar olami!", 18, (0,0.9,1,1)))
        summary = STATE.save_summary()
        if summary:
            root.add_widget(lbl("Saqlangan o'yin bor:", 16, (0.3,1,0.5,1), True))
            root.add_widget(lbl(summary, 15))
            root.add_widget(btn("▶ DAVOM ETISH", lambda *a: self.continue_game(), bg=(0.1,0.65,0.25,1), height=60))
            root.add_widget(btn("YANGI O'YIN", lambda *a: self.new_game(), bg=(0.85,0.45,0.05,1), height=56))
        else:
            root.add_widget(lbl("Saqlangan o'yin yo'q — yangi sarguzasht boshlang!", 15, (0.7,0.7,0.8,1)))
            root.add_widget(btn("▶ O'YIN BOSHLASH", lambda *a: self.start(), bg=(0.1,0.65,0.25,1), height=60))
        root.add_widget(lbl(f"Yangi o'yin qahramoni: {STATE.selected_hero}", 15, (0.7,0.9,1,1)))
        root.add_widget(lbl(STATE.message, 16, (1,0.8,0.2,1), True))
        for txt, fn in [("QAHRAMONLAR", lambda *a: setattr(self.manager, 'current', 'heroes')),
                        ("DO'KON", lambda *a: setattr(self.manager, 'current', 'shop')),
                        ("JIHOZLAR", lambda *a: setattr(self.manager, 'current', 'equipment')),
                        ("SOZLAMALAR", lambda *a: setattr(self.manager, 'current', 'settings'))]:
            root.add_widget(btn(txt, fn, height=52))
        if summary:
            root.add_widget(btn("Saqlangan o'yinni o'chirish", lambda *a: self.delete_save(), bg=(0.6,0.15,0.15,1), height=44))
        root.add_widget(lbl("Avtomatik saqlash: har 10 soniyada + muhim hodisalarda", 12, (0.6,0.7,0.9,1)))
        self.add_widget(root)
    def start(self):
        STATE.start(); self.manager.current = 'game'
    def new_game(self):
        STATE.delete_save(); STATE.start(); self.manager.current = 'game'
    def continue_game(self):
        if STATE.load_game(): self.manager.current = 'game'
        else:
            STATE.start(); STATE.say("Saqlangan o'yinni ochib bo'lmadi, yangi o'yin boshlandi."); self.manager.current = 'game'
    def delete_save(self):
        STATE.delete_save(); STATE.say("Saqlangan o'yin o'chirildi."); self.build()
    def on_enter(self): self.build()

class HeroesScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw); self.build()
    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=16, spacing=8)
        root.add_widget(lbl("Yangi o'yin uchun qahramon", 26, (0,0.9,1,1), True))
        sc = ScrollView(); col = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None)
        col.bind(minimum_height=col.setter('height'))
        for name, d in HEROES.items():
            b = BoxLayout(orientation='vertical', size_hint_y=None, height=112, padding=8, spacing=2)
            b.add_widget(lbl(f"{name}  {d['mark']}  |  HP {d['hp']}  MP {d['mp']}  ATK {d['atk']}  DEF {d['def']}  SPD {d['spd']}", 16, bold=True))
            ab = ABILITIES[name]
            b.add_widget(lbl(f"★ {ab['name']}: {ab['desc']}", 13, (0.8,0.9,1,1)))
            chosen = STATE.selected_hero == name
            b.add_widget(btn("✓ TANLANGAN" if chosen else "Tanlash", lambda *a, n=name: self.pick(n),
                             bg=(0.1,0.6,0.3,1) if chosen else (0.1,0.35,0.7,1), height=38))
            col.add_widget(b)
        sc.add_widget(col); root.add_widget(sc)
        root.add_widget(btn("◀ Menyuga", lambda *a: setattr(self.manager, 'current', 'menu'), bg=(0.4,0.4,0.4,1)))
        self.add_widget(root)
    def pick(self, name):
        # Joriy o'yin va saqlangan progressga tegmaydi — faqat yangi o'yin uchun
        STATE.selected_hero = name; STATE.say(f"{name} tanlandi (yangi o'yinda ishlatiladi)."); self.build()
    def on_enter(self): self.build()

class ShopScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw); self.build()
    def build(self):
        self.clear_widgets()
        p = STATE.player
        root = BoxLayout(orientation='vertical', padding=16, spacing=8)
        root.add_widget(lbl(f"Do'kon  •  Tangalar: {fmt(p.coins)}  •  {STATE.message}", 16, (1,0.8,0.2,1), True))
        sc = ScrollView(); col = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        col.bind(minimum_height=col.setter('height'))
        for it in ITEMS:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=56, spacing=8)
            tag = f" ★ AFSONAVIY — faqat {it['hero']} | " if it.get("mythic") else " — "
            row.add_widget(rowlabel(f"{it['icon']} {it['name']} ({it['kind']}){tag}{bonus_text(it)}"))
            price = fmt(it['price']) + " 🪙" + (" ★" if it.get("mythic") else "")
            b = btn(f"{price}\nSotib ol", lambda *a, i=it: self.buy(i), bg=(0.1,0.6,0.3,1), height=48, font_size=14)
            b.size_hint_x = None; b.width = 150
            row.add_widget(b); col.add_widget(row)
        sc.add_widget(col); root.add_widget(sc)
        nav = BoxLayout(size_hint_y=None, height=52, spacing=8)
        nav.add_widget(btn("◀ O'yin", lambda *a: setattr(self.manager, 'current', 'game'), bg=(0.4,0.4,0.4,1)))
        nav.add_widget(btn("Inventar ▶", lambda *a: setattr(self.manager, 'current', 'inventory'), bg=(0.5,0.2,0.7,1)))
        root.add_widget(nav); self.add_widget(root)
    def buy(self, it):
        STATE.buy(it); self.build()
    def on_enter(self): self.build()

class InventoryScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw); self.build()
    def build(self):
        self.clear_widgets()
        p = STATE.player
        root = BoxLayout(orientation='vertical', padding=16, spacing=8)
        root.add_widget(lbl(f"Inventar  •  {STATE.message}", 20, (0,0.9,1,1), True))
        sc = ScrollView(); col = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        col.bind(minimum_height=col.setter('height'))
        if not p.inventory:
            col.add_widget(lbl("Hozircha bo'sh. Do'kondan buyum oling.", 16, (0.7,0.7,0.8,1)))
        for it in list(p.inventory):
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=52, spacing=8)
            row.add_widget(rowlabel(f"{it['icon']} {it['name']} ({it['kind']}) — {bonus_text(it)}"))
            act = "Ishlatish" if it["kind"] == "Dori" else "Kiyish"
            b = btn(act, lambda *a, i=it: self.use(i), bg=(0.1,0.6,0.3,1), height=42)
            b.size_hint_x = None; b.width = 120
            row.add_widget(b); col.add_widget(row)
        sc.add_widget(col); root.add_widget(sc)
        nav = BoxLayout(size_hint_y=None, height=52, spacing=8)
        nav.add_widget(btn("◀ O'yin", lambda *a: setattr(self.manager, 'current', 'game'), bg=(0.4,0.4,0.4,1)))
        nav.add_widget(btn("Do'kon", lambda *a: setattr(self.manager, 'current', 'shop'), bg=(0.1,0.35,0.7,1)))
        nav.add_widget(btn("Jihozlar", lambda *a: setattr(self.manager, 'current', 'equipment'), bg=(0.5,0.2,0.7,1)))
        root.add_widget(nav); self.add_widget(root)
    def use(self, it): STATE.equip(it); self.build()
    def on_enter(self): self.build()

class EquipmentScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw); self.build()
    def build(self):
        self.clear_widgets()
        p = STATE.player
        root = BoxLayout(orientation='vertical', padding=16, spacing=8)
        root.add_widget(lbl(f"Jihozlar — {p.hero}  |  Hujum {p.total('atk')}  Himoya {p.total('def')}", 18, (0,0.9,1,1), True))
        for kind in ("Qurol", "Zirh", "Aksessuar"):
            it = p.equipped[kind]
            nm = it["name"] if it else "Bo'sh"
            root.add_widget(lbl(f"{kind}: {nm}  ({bonus_text(it) if it else '-'})", 17))
            if it:
                root.add_widget(btn(f"{kind} ni yechish", lambda *a, k=kind: self.unequip(k), bg=(0.7,0.3,0.2,1), height=44))
        root.add_widget(lbl("Inventardan kiyish uchun Inventar ekraniga o'ting.", 14, (0.7,0.7,0.8,1)))
        _m = [it for it in p.equipped.values() if it and it.get("mythic")]
        if _m: root.add_widget(lbl("AFSONAVIY AURA FAOL: " + ", ".join(i["name"] for i in _m), 16, (1,0.85,0.1,1), True))
        root.add_widget(btn("◀ O'yin", lambda *a: setattr(self.manager, 'current', 'game'), bg=(0.4,0.4,0.4,1)))
        self.add_widget(root)
    def unequip(self, kind):
        STATE.player.equipped[kind] = None; STATE.say(f"{kind} yechildi."); self.build()
    def on_enter(self): self.build()

class SettingsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw); self.build()
    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=20, spacing=10)
        root.add_widget(lbl("Sozlamalar", 26, (0,0.9,1,1), True))
        root.add_widget(lbl("Musiqa", 16))
        s1 = Slider(min=0, max=1, value=STATE.settings["music"]); s1.bind(value=lambda *a: STATE.settings.update(music=s1.value)); root.add_widget(s1)
        root.add_widget(lbl("Ovoz (SFX)", 16))
        s2 = Slider(min=0, max=1, value=STATE.settings["sfx"]); s2.bind(value=lambda *a: STATE.settings.update(sfx=s2.value)); root.add_widget(s2)
        row = BoxLayout(spacing=8, size_hint_y=None, height=48)
        row.add_widget(lbl("Ovozsiz (Mute):", 16)); sw = Switch(active=STATE.settings["muted"])
        sw.bind(active=lambda *a: STATE.settings.update(muted=sw.active)); row.add_widget(sw); root.add_widget(row)
        root.add_widget(btn("Saqlash va Menyuga", lambda *a: self.save(), bg=(0.1,0.6,0.3,1)))
        root.add_widget(btn("◀ Orqaga", lambda *a: setattr(self.manager, 'current', 'menu'), bg=(0.4,0.4,0.4,1)))
        self.add_widget(root)
    def save(self): STATE.save(); self.manager.current = 'menu'
    def on_enter(self): self.build()

KEYMAP = {119: 'u', 115: 'd', 97: 'l', 100: 'r', 273: 'u', 274: 'd', 276: 'l', 275: 'r'}

class GameScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical', spacing=4, padding=6)
        self.hud = Label(text="", font_size=14, size_hint_y=None, height=92, halign='left', valign='top')
        self.hud.bind(size=lambda *a: setattr(self.hud, 'text_size', (self.hud.width, None)))
        root.add_widget(self.hud)
        self.canvas_widget = GameCanvas(size_hint_y=1)
        root.add_widget(self.canvas_widget)
        controls = BoxLayout(orientation='horizontal', size_hint_y=None, height=140, spacing=8)
        self.joystick = Joystick(self.on_joy, size_hint_x=0.4)
        controls.add_widget(self.joystick)
        acts = BoxLayout(orientation='vertical', spacing=6)
        top = BoxLayout(spacing=6)
        top.add_widget(btn("⚔ HUJUM", lambda *a: STATE.attack(), bg=(0.85,0.2,0.2,1), size_hint_y=1))
        top.add_widget(btn("⭐ QOBILIYAT", lambda *a: STATE.use_ability(), bg=(0.6,0.2,0.85,1), size_hint_y=1, font_size=15))
        acts.add_widget(top)
        row2 = BoxLayout(spacing=6, size_hint_y=None, height=48)
        row2.add_widget(btn("Do'kon", lambda *a: setattr(self.manager, 'current', 'shop'), bg=(0.1,0.35,0.7,1), height=48, font_size=15))
        row2.add_widget(btn("Jihoz", lambda *a: setattr(self.manager, 'current', 'equipment'), bg=(0.5,0.2,0.7,1), height=48, font_size=15))
        row2.add_widget(btn("Sumka", lambda *a: setattr(self.manager, 'current', 'inventory'), bg=(0.2,0.6,0.3,1), height=48, font_size=15))
        acts.add_widget(row2); controls.add_widget(acts)
        root.add_widget(controls)
        root.add_widget(btn("Pauza / Menyu (saqlanadi)", lambda *a: self.pause_to_menu(), bg=(0.4,0.4,0.4,1), height=40))
        self.add_widget(root)
        Window.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)
    def on_joy(self, vx, vy):
        self.canvas_widget.joy = [vx, vy]
    def pause_to_menu(self):
        STATE.save_game(); STATE.say("O'yin saqlandi! Davom etish uchun DAVOM ETISH ni bosing."); self.manager.current = 'menu'
    def on_key_down(self, win, key, scancode, codepoint, modifiers):
        if self.manager.current != 'game': return False
        if key in KEYMAP: self.canvas_widget.kb.add(KEYMAP[key])
        if key == 32: STATE.attack()
        if key == 113: STATE.use_ability()   # Q
        if key == 101: self.manager.current = 'shop'
        if key == 105: self.manager.current = 'inventory'
        if key == 99: self.manager.current = 'equipment'
        if key in (27, 112): self.pause_to_menu()   # Esc / Android orqaga / P
        return False
    def on_key_up(self, win, key, scancode):
        if key in KEYMAP: self.canvas_widget.kb.discard(KEYMAP[key])
        return False
    def on_leave(self):
        self.canvas_widget.kb.clear(); self.canvas_widget.joy = [0, 0]; self.joystick.reset()
        SOUND.stop_music()
    def refresh(self):
        p = STATE.player
        boss = next((e for e in STATE.enemies if getattr(e, 'is_boss', False)), None)
        area = AREAS[STATE.area_index][0]
        if boss:
            extra = f"BOSS: {boss.name} HP {int(boss.hp)}/{boss.max_hp} | {STATE.boss_special_msg}"
        elif STATE.portal_active:
            extra = f"PORTAL OCHIQ! Yangi hududga o'tish uchun portalga kiring! Hudud: {area}"
        else:
            left = 5 - (STATE.wave % 5) if STATE.wave % 5 != 0 else 0
            extra = f"Hudud: {area} | Keyingi bossgacha: {left} to'lqin | Yengilgan boss: {STATE.boss_defeated}"
        status = ""
        if p.stunned > 0: status += f" Qotgan ({p.stunned:.1f}s)"
        if p.poisoned > 0: status += f" Zahar ({p.poisoned:.0f}s)"
        if STATE.flash > 0 and STATE.flash_text: status += f" | {STATE.flash_text}"
        ab = ABILITIES.get(p.hero, {}); nm = ab.get('name', '')
        if p.ability_active and p.ability_timer > 0: ab_line = f"⭐ {nm} FAOL! ({p.ability_timer:.0f}s) | "
        elif p.ability_cd > 0: ab_line = f"⭐ {nm} — tayyor bo'lishiga {p.ability_cd:.0f}s | "
        else: ab_line = f"⭐ {nm} TAYYOR! (Q / tugma) | "
        self.hud.text = T(f"@Code Inflation RPG  •  {p.hero} Lv.{p.level}  •  To'lqin {STATE.wave}  •  Mag'lubiyat {STATE.kills}\n"
                          f"♥ HP {int(p.hp)}/{p.max_hp}   ✦ MP {int(p.mp)}/{p.max_mp}   ⚔ {p.total('atk')}  ♜ {p.total('def')}   🪙 {fmt(p.coins)}   XP {p.xp}/{p.level*100}{status}\n"
                          f"{ab_line}{extra}\n{STATE.message}")
    def on_enter(self): self.refresh()

class RPGApp(App):
    sm = None
    def on_stop(self):
        try: STATE.save_game()
        except Exception: pass
    def on_pause(self):
        try:
            STATE.save_game(); SOUND.stop_music()
        except Exception: pass
        return True
    def build(self):
        STATE.load_settings()
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu')); sm.add_widget(HeroesScreen(name='heroes'))
        sm.add_widget(GameScreen(name='game')); sm.add_widget(ShopScreen(name='shop'))
        sm.add_widget(InventoryScreen(name='inventory')); sm.add_widget(EquipmentScreen(name='equipment'))
        sm.add_widget(SettingsScreen(name='settings'))
        self.sm = sm
        Clock.schedule_interval(self.autosave, 10)
        Clock.schedule_interval(lambda dt: self.refresh_hud(), 0.1)
        return sm
    def autosave(self, dt):
        if self.sm and self.sm.current == 'game':
            STATE.save_game()
    def refresh_hud(self):
        try:
            if self.sm.current == 'game':
                self.sm.get_screen('game').refresh()
        except Exception: pass

if __name__ == '__main__':
    RPGApp().run()
