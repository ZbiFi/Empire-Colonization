# main.py
import json

from game_menu import GameMenuWindow
from save_load_windows import SaveLoadWindow
from settings_window import SettingsWindow

LANG = "en"  # "pl" / "en" / "de"

import os
from localization import Localization
import sys
import tkinter as tk
from ctypes import windll
from tkinter import ttk
from datetime import timedelta
import pygame
from PIL import Image, ImageTk
from buildings import BuildingsMixin
from map_generator import generate_map, MAP_SIZE
from constants import *
from missions import MissionsMixin
from relations import RelationsMixin
from ships import ShipsMixin
from map_views import MapUIMixin
from tooltip import Tooltip
from settings_manager import load_settings, save_settings

def load_font_ttf(path):
    """
    Ładuje font TTF do pamięci procesu Windows.
    Dzięki temu można go używać w Tkinterze,
    nawet po spakowaniu do EXE.
    """
    FR_PRIVATE = 0x10
    FR_NOT_ENUM = 0x20
    path = os.path.abspath(path)
    windll.gdi32.AddFontResourceExW(path, FR_PRIVATE, 0)

class ColonySimulator(MissionsMixin, ShipsMixin, RelationsMixin, BuildingsMixin, MapUIMixin):

    def __init__(self, root):
        self.root = root
        # ---- settings (trwałe, wczytywane z settings.json) ----
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.settings = load_settings(base_dir, defaults={
            "lang": LANG,
            "music_volume": 0.2,
            "sfx_volume": 0.5,
        })
        lang = self.settings.get("lang", LANG)

        self.loc = Localization(lang, locales_dir=os.path.join(os.path.dirname(__file__), "loc"))
        self.root.title(self.loc.t("app.title"))
        self.root.geometry("1600x1000")

        # Załaduj wszystkie czcionki
        load_font_ttf(self.resource_path("fonts/Cinzel-Regular.ttf"))
        load_font_ttf(self.resource_path("fonts/Cinzel-Bold.ttf"))
        load_font_ttf(self.resource_path("fonts/IMFellEnglishSC-Regular.ttf"))
        load_font_ttf(self.resource_path("fonts/EBGaramond-Italic.ttf"))
        load_font_ttf(self.resource_path("fonts/MedievalSharp-Regular.ttf"))

        # grafika mapy (kafelki lasu itp.)
        self.init_map_graphics()
        self.init_ocean_tiles()
        self.init_mountains_tiles()
        self.init_forest_tiles()

        self.title_font = ("IM Fell English SC", 28, "bold")
        self.ui_font = ("EB Garamond Italic", 18)
        self.journal_font = ("EB Garamond Italic", 16)

        self.top_title_font = ("Cinzel", 16, "bold")
        self.top_info_font = ("EB Garamond Italic", 14)

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")

        bg = self.style.lookup("TFrame", "background")
        self.root.configure(bg=bg)

        self.style.configure("Colonial.TButton",
                        font=self.ui_font, padding=(20, 8),
                        foreground="#2b1d12", background="#e3cfaa",
                        borderwidth=3, relief="raised"
                        )

        self.style.map("Colonial.TButton",
                  foreground=[("disabled", "#888"), ("pressed", "#1d130c"), ("active", "#2b1d12")],
                  background=[("disabled", "#d8c7a4"), ("pressed", "#c9ae7b"), ("active", "#f0ddba")],
                  relief=[("pressed", "sunken"), ("!pressed", "raised")]
                  )

        self.style.configure("ColonialSecondary.TButton",
                        font=self.ui_font, padding=(14, 6),
                        foreground="#3b2a18", background="#d9c39a",
                        borderwidth=1, relief="raised"
                        )

        self.style.map("ColonialSecondary.TButton",
                  background=[("pressed", "#c2aa7f"), ("active", "#e8d6af")],
                  relief=[("pressed", "sunken"), ("!pressed", "raised")]
                  )

        self.state = None
        self.location = None
        self.current_date = None
        self.people = 100
        self.busy_people = 0
        self.days_passed = 0

        # self.resources = {r: 5000 if r in ["drewno", "żywność", "skóry", "żelazo", "stal"] else 0 for r in RESOURCES}
        self.resources = {r: 0 for r in RESOURCES}

        self.resources["food"] = 100000
        self.resources["wood"] = 10000
        self.resources["skins"] = 1000
        self.resources["clothes"] = 1000
        self.resources["herbs"] = 1000
        self.resources["meds"] = 1000
        self.resources["iron"] = 1000
        self.resources["steel"] = 1000
        self.resources["cane"] = 1000
        self.resources["sugar"] = 1000
        self.resources["tobacco"] = 1000
        self.resources["cigars"] = 1000
        self.resources["coal"] = 1000
        self.resources["silver"] = 1000
        self.resources["gold"] = 1000
        self.resources["ducats"] = 10000

        # self.resources["food"] = 1000
        # self.resources["wood"] = 50
        # self.resources["iron"] = 30
        # self.resources["skins"] = 10
        # self.resources["silver"] = 10
        # self.resources["meds"] = 10
        # self.resources["ducats"] = 300

        self.buildings = []
        self.constructions = []
        self.upgrades_in_progress = []
        self.expeditions = []
        self.ships = []
        self.auto_sail_timer = None

        self.native_relations = {
            tribe: 50
            for tribe in random.sample(list(TRIBE_DISPLAY_KEYS.keys()), 3)
        }
        # reputacja z państwami europejskimi – na start 0, później własne państwo podbijemy
        self.europe_relations = {s: 0 for s in STATES}

        self.native_prod = {}
        self.native_cap = {}
        self.native_stock = {}

        for tribe in self.native_relations:
            prod_map = {}
            cap_map = {}
            stock_map = {}
            for res, econ in NATIVE_RESOURCE_ECONOMY.items():
                p_min, p_max = econ["daily_prod"]
                c_min, c_max = econ["stockpile"]
                prod_val = random.uniform(p_min, p_max)
                cap_val = random.uniform(c_min, c_max)
                prod_map[res] = prod_val
                cap_map[res] = cap_val
                stock_map[res] = cap_val  # startują pełni, żeby handel miał sens od razu
            self.native_prod[tribe] = prod_map
            self.native_cap[tribe] = cap_map
            self.native_stock[tribe] = stock_map

        # kumulacja wartości handlu (do progów reputacji)
        self.native_trade_value = {tribe: 0 for tribe in self.native_relations}
        self.europe_trade_value = {s: 0 for s in self.europe_relations}
        self.trade_reputation_threshold = 1000

        self.map_size = MAP_SIZE
        self.map_grid = None
        self.settlement_pos = None
        self.selected_building = None
        self.log_lines = []

        self.flagship_index = 0
        self.current_mission = None  # (end_date, required, sent, difficulty, mission_text, index)
        self.last_mission_date = None
        self.mission_multiplier = 1.0
        self.first_mission_given = False

        self.completed_missions = 0
        self.missions_to_win = 100

        # Mechanika misji indiańskich
        self.native_missions_active = {}  # tribe → dict z aktywną misją
        self.native_missions_cd = {}  # tribe → data kiedy mogą poprosić ponownie
        self.native_mission_multiplier = {}  # tribe → mnożnik trudności jak w misjach królewskich

        # przyszłe misje od Indian – na razie pusta lista
        # struktura np.: {"tribe": "Irokezi", "text": "...", "end": data, "progress": "..."}
        self.native_missions = []

        self.current_monarch = ""

        self.start_screen()
        pygame.mixer.init()
        self.init_sounds()


    # === Pomocnicze ===
    def log(self, text, color="black"):
        if not self.current_date: return
        entry = f"[{self.current_date.strftime('%d %b %Y')}] {text}"
        self.log_lines.append((entry, color))
        if len(self.log_lines) > 1000: self.log_lines.pop(0)
        self.update_log_display()

    def center_window(self, win):
        self.loc.t("dev.center_window_comment")
        win.update_idletasks()
        w = win.winfo_width()
        h = win.winfo_height()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

    def create_window(self, title, key=None):
        if key:
            if not hasattr(self, "_open_windows"):
                self._open_windows = {}
            old = self._open_windows.get(key)
            if old and old.winfo_exists():
                old.lift()
                old.focus_force()
                return old

        win = tk.Toplevel(self.root)
        win.title(title)
        BG = self.style.lookup("TFrame", "background")
        win.configure(bg=BG)

        if key:
            self._open_windows[key] = win

            def on_close():
                try:
                    win.destroy()
                finally:
                    self._open_windows.pop(key, None)

            win.protocol("WM_DELETE_WINDOW", on_close)

        return win

    def resource_path(self, filename):
        if getattr(sys, 'frozen', False):
            # tryb PyInstaller --onefile: pliki są w katalogu tymczasowym
            base = sys._MEIPASS
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, filename)

    def save_settings(self):
        """Zapisz aktualne ustawienia do settings.json."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        save_settings(base_dir, self.settings)

    def init_sounds(self):
        # MUZYKA TŁA
        music_path = self.resource_path("sounds/music.mp3")
        music_vol = float(self.settings.get("music_volume", 0.2))
        sfx_vol = float(self.settings.get("sfx_volume", 0.5))
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(loops=1)  # -1 = gra w pętli bez końca
        except Exception as e:
            print(self.loc.t("error.music_load_failed"), e)

        pygame.mixer.music.set_volume(music_vol)

        # tu od razu przygotujemy dźwięki efektów
        self.sounds = {}
        try:
            self.sounds["new_mission"] = pygame.mixer.Sound(self.resource_path("sounds/new_mission.wav"))
            self.sounds["ship_arrived"] = pygame.mixer.Sound(self.resource_path("sounds/anchor.wav"))
            self.sounds["building_done"] = pygame.mixer.Sound(self.resource_path("sounds/building_done.wav"))
        except Exception as e:
            print(self.loc.t("error.sound_load_failed"), e)

        # ustaw głośność SFX od razu
        for snd in self.sounds.values():
            try:
                snd.set_volume(sfx_vol)
            except Exception:
                pass

    def play_sound(self, name):
        snd = getattr(self, "sounds", {}).get(name)
        if snd:
            snd.play()

    def open_settings(self):
        # singleton: nie otwieraj wielu okien naraz
        if getattr(self, "_settings_win", None) and self._settings_win.winfo_exists():
            self._settings_win.lift()
            return
        self._settings_win = SettingsWindow(self)

    def open_game_menu(self):
        """Otwiera menu gry tylko jeśli nie ma innych otwartych okien."""
        others = []
        for w in self.root.winfo_children():
            if isinstance(w, tk.Toplevel) and w.winfo_exists():
                if getattr(self, "_game_menu_win", None) and w == self._game_menu_win.win:
                    continue
                others.append(w)

        if others:
            try:
                others[0].lift(); others[0].focus_force()
            except Exception:
                pass
            return

        if getattr(self, "_game_menu_win", None) and self._game_menu_win.win.winfo_exists():
            self._game_menu_win.win.lift();
            return

        self._game_menu_win = GameMenuWindow(self)

    def update_log_display(self):
        if not hasattr(self, 'log_text'): return
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        for text, color in self.log_lines[-100:]:
            self.log_text.insert(tk.END, text + "\n", color)
            self.log_text.tag_config(color, foreground=color)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def free_workers(self):
        # ile osób pracuje w budynkach (nie liczymy dzielnic i namiotów)
        workers_in_buildings = sum(
            b.get("workers", 0)
            for b in self.buildings
            if not b.get("is_district", False) and b["base"] not in ["tent"]
        )

        # Wolni = wszyscy ludzie - ci w budowach/expedycjach - ci w budynkach
        return max(0, self.people - self.busy_people - workers_in_buildings)

    def can_afford(self, cost):
        # tworzymy kopię, by nie modyfikować oryginału
        real_cost = cost.copy()

        # --- BONUS HOLANDII ---
        if self.state == "netherlands":
            mult = STATES[self.state].get("build_cost", 1)
            real_cost = {r: int(a * mult) for r, a in real_cost.items()}

        return all(self.resources.get(r, 0) >= a for r, a in real_cost.items())

    def spend_resources(self, cost):
        # tworzymy kopię, by nie modyfikować oryginału
        real_cost = cost.copy()

        # --- BONUS HOLANDII ---
        if self.state == "netherlands":
            mult = STATES[self.state].get("build_cost", 1)
            real_cost = {r: int(a * mult) for r, a in real_cost.items()}

        # faktyczne pobranie zasobów
        for r, a in real_cost.items():
            self.resources[r] -= a

    def get_monarch(self):
        # zabezpieczenie na wypadek złego self.state
        if self.state not in STATES:
            return self.loc.t("state.unknown_ruler")

        year = self.current_date.year
        for monarch in STATES[self.state]["rulers"]:
            if monarch["start"] <= year <= monarch["end"]:
                if self.current_monarch != monarch.get("name_key"):
                    self.europe_relations[self.state] = 50
                self.current_monarch = monarch.get("name_key")
                return self.loc.t(monarch.get("name_key"), default="Nieznany")

        return self.loc.t("state.unknown_ruler")


    # === Start gry ===
    def start_screen(self):

        # jeśli start menu już istnieje (np. po zmianie języka), usuń je
        if getattr(self, "start_container", None) is not None and self.start_container.winfo_exists():
            self.start_container.destroy()

        self.start_container = tk.Frame(self.root)
        self.start_container.pack(fill="both", expand=True)

        def update_state_bonus(*_):

            display = self.state_var.get()
            state = self.state_display_to_id.get(display, display)
            data = STATES.get(state, {})
            bonus_key = data.get('bonus_key')
            bonus_text = self.loc.t(bonus_key, default='') if bonus_key else ''

            if bonus_text:
                self.state_bonus_var.set(self.loc.t('ui.state_bonus_prefix', default='Bonus: {bonus}', bonus=bonus_text))
            else:
                self.state_bonus_var.set(self.loc.t('ui.state_bonus_none', default='Bonus: brak unikalnego efektu.'))

        # === TŁO Z OBRAZU ===
        try:
            img_path = self.resource_path("img/colony.jpg")
            bg_image = Image.open(img_path)

            # dopasuj do okna (1600x1000 jak w __init__)
            bg_image = bg_image.resize((1600, 1000), Image.LANCZOS)

            # musimy trzymać referencję w self, inaczej obraz zniknie
            self.start_bg_image = ImageTk.PhotoImage(bg_image)

            bg_label = tk.Label(self.start_container, image=self.start_bg_image)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(self.loc.t("error.background_load_failed"), e)
            bg_label = tk.Label(self.start_container)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        try:
            gear_img_path = self.resource_path("img/gear.png")
            gear_img = Image.open(gear_img_path).resize((32, 32), Image.LANCZOS)
            self.gear_icon_main = ImageTk.PhotoImage(gear_img)  # trzymaj referencję!
        except Exception as e:
            print("gear.png load failed:", e)
            self.gear_icon_main = None

        self.settings_btn_main = ttk.Button(
            bg_label,
            image=self.gear_icon_main,
            command=self.open_settings,
            style="ColonialSecondary.TButton"
        )
        if self.gear_icon_main is None:
            self.settings_btn_main.config(text="⚙")

        # prawy górny róg start menu
        self.settings_btn_main.place(relx=1.0, rely=0.0, anchor="ne", x=-12, y=12)

        Tooltip(self.settings_btn_main, self.loc.t("screen.settings.title", default="Settings"))

        # === GŁÓWNA RAMKA NA PRZYCISKI / WYBÓR PAŃSTWA ===
        frame = ttk.Frame(bg_label, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text=self.loc.t("app.title"), font=self.title_font).pack(pady=20)
        ttk.Label(frame, text=self.loc.t("ui.choose_state"), font=self.ui_font).pack(pady=10)

        # Build localized state display list (display -> state_id)
        self.state_display_to_id = {self.loc.t(STATES[s]['name_key'], default=s): s for s in STATES}
        self.state_id_to_display = {v: k for k, v in self.state_display_to_id.items()}
        state_display_values = list(self.state_display_to_id.keys())
        self.state_var = tk.StringVar(value=state_display_values[0])
        combo = ttk.Combobox(
            frame,
            textvariable=self.state_var,
            values=state_display_values,
            state="readonly",
            width=30
        )
        combo.pack(pady=5)

        # === Bonus wybranego państwa ===
        self.state_bonus_var = tk.StringVar(value="")

        # Ramka o stałej wysokości – nic nie przeskakuje
        bonus_frame = ttk.Frame(frame, height=60)  # możesz skorygować 60 na 50/70 wg uznania
        bonus_frame.pack(pady=(5, 10), fill="x")
        bonus_frame.pack_propagate(False)  # NIE zmieniaj rozmiaru ramki pod zawartość

        self.state_bonus_label = ttk.Label(
            bonus_frame,
            textvariable=self.state_bonus_var,
            font=("EB Garamond Italic", 12),   # mniejsza czcionka
            foreground="darkgreen",
            anchor="center",
            justify="center",
            wraplength=500,  # szerokość w pikselach, przy której tekst sam się zawija
        )
        self.state_bonus_label.pack(expand=True)

        # aktualizuj bonus przy każdej zmianie wyboru
        self.state_var.trace_add("write", update_state_bonus)
        # ustaw tekst dla domyślnego państwa (Portugalia)
        update_state_bonus()

        ttk.Button(
            frame,
            text=self.loc.t("ui.random_state"),
            style="ColonialSecondary.TButton",
            command=lambda: self.state_var.set(random.choice(state_display_values))
        ).pack(pady=(8, 10))

        # === Wybór wielkości mapy ===
        ttk.Label(frame, text=self.loc.t("ui.map_size"), font=self.ui_font).pack(pady=(10, 5))

        self.map_size_var = tk.StringVar(value=self.loc.t("difficulty.map.medium", default=self.loc.t("difficulty.map.medium")))
        map_size_options = [
            self.loc.t("difficulty.map.tiny"),
            self.loc.t("difficulty.map.small"),
            self.loc.t("difficulty.map.medium"),
            self.loc.t("difficulty.map.large"),
            self.loc.t("difficulty.map.huge"),
        ]

        map_size_combo = ttk.Combobox(
            frame,
            textvariable=self.map_size_var,
            values=map_size_options,
            state="readonly",
            width=30
        )
        map_size_combo.pack(pady=5)

        ttk.Label(frame, text=self.loc.t("ui.game_length"), font=self.ui_font).pack(pady=(15, 5))

        self.game_length_var = tk.StringVar(value="normal")

        lengths = [
            (self.loc.t("difficulty.length.flash"), "flash"),
            (self.loc.t("difficulty.length.fast"), "fast"),
            (self.loc.t("difficulty.length.normal"), "normal"),
            (self.loc.t("difficulty.length.long"), "long"),
            (self.loc.t("difficulty.length.marathon"), "marathon"),
            (self.loc.t("difficulty.length.epic"), "epic"),
        ]

        length_frame = ttk.Frame(frame)
        length_frame.pack(anchor="w", padx=100)

        for text, val in lengths:
            ttk.Radiobutton(
                length_frame,
                text=text,
                variable=self.game_length_var,
                value=val
            ).pack(anchor="w")

        btn_row = ttk.Frame(frame)
        btn_row.pack(pady=10)

        start_btn = ttk.Button(frame, text=self.loc.t("ui.start_game"), style="Colonial.TButton", command=self.start_game)
        start_btn.pack(pady=10)

        start_btn = ttk.Button(frame, text=self.loc.t("ui.load_game"), style="Colonial.TButton", command=self.load_game_dialog)
        start_btn.pack(pady=10)

        self.current_screen = "start"

    def load_game_dialog(self):
        SaveLoadWindow(self, mode="load")
        return

    def start_game(self):

        display = self.state_var.get()
        self.state = self.state_display_to_id.get(display, display)
        if not self.state:
            return

        # klucz nazwy państwa masz w STATES[self.state]['name_key']
        self.state_display = self.loc.t(STATES[self.state]["name_key"], default=self.state)
        if not self.state: return

        if self.state == "france":
            self.trade_reputation_threshold = STATES[self.state]["reputation_threshold"]

        # ustawienie długości gry na podstawie wyboru na ekranie startowym
        length_key = getattr(self, "game_length_var", None).get() if hasattr(self, "game_length_var") else "normal"

        length_map = {
            "flash": 1,
            "fast": 30,
            "normal": 50,
            "long": 70,
            "marathon": 100,
            "epic": 150,
        }
        self.missions_to_win = length_map.get(length_key, 50)

        # własne państwo startuje z lepszą reputacją, reszta pozostaje 0
        self.europe_relations[self.state] = 50

        # --- losujemy KLUCZ lokacji, a tłumaczenie robimy na bieżąco ---
        self.location_key = random.choice([
            "map.gulf_of_mexico",
            "map.brazil_coast",
            "map.caribbean",
            "map.florida",
            "map.patagonia",
            "map.hudson_bay",
            "map.bahamas",
            "map.orinoco_delta",
            "map.peru_coast",
            "map.new_york"
        ])
        self.location = self.loc.t(self.location_key)
        if "pop_start" in STATES[self.state]:
            self.people += STATES[self.state]["pop_start"]

        # wybór wielkości mapy z ekranu startowego
        size_label = getattr(self, "map_size_var", None).get() if hasattr(self, "map_size_var") else self.loc.t("difficulty.map.medium")
        size_map = {
            self.loc.t("difficulty.map.tiny"): 6,
            self.loc.t("difficulty.map.small"): 7,
            self.loc.t("difficulty.map.medium"): 8,
            self.loc.t("difficulty.map.large"): 9,
            self.loc.t("difficulty.map.huge"): 10,
        }

        self.map_size = size_map.get(size_label, 8)

        self.map_grid, self.settlement_pos = generate_map(self.map_size)
        self.map_size = len(self.map_grid)
        self.current_date = generate_start_date()

        # Start systemu po 6 miesiącach
        self.native_missions_enabled_start = self.current_date + timedelta(days=180)

        sy, sx = self.settlement_pos
        for _ in range(3):
            tent = {"base": "tent", "level": 0, "workers": 0, "pos": (sy, sx)}
            self.buildings.append(tent)
            self.map_grid[sy][sx]["building"].append(tent)

        self.ships = [(None, None, {}, SHIP_STATUS_IN_PORT, 0)]
        self.flagship_index = 0
        self.auto_sail_timer = self.current_date + timedelta(days=14)
        self.main_game()

    def calculate_storage_limits(self):
        """
        Zwraca (food_limit, goods_limit).
        Bazowo 1000/1000, potem dodaje bonusy ze spichlerzy/magazynów i ich ulepszeń.
        """
        food_limit = BASE_FOOD_LIMIT
        goods_limit = BASE_GOODS_LIMIT

        for b in self.buildings:
            if b.get("is_district"):
                continue

            base_key = b["base"]
            level = b.get("level", 0)
            base_def = BUILDINGS.get(base_key, {})

            # bonus z poziomu bazowego (jeśli istnieje w definicji)
            food_limit += base_def.get("food_limit", 0)
            goods_limit += base_def.get("goods_limit", 0)

            # bonus z ulepszeń (jeśli istnieją)
            upgrades = base_def.get("upgrades", [])
            if level > 0 and upgrades:
                up_def = upgrades[min(level - 1, len(upgrades) - 1)]
                food_limit += up_def.get("food_limit", 0)
                goods_limit += up_def.get("goods_limit", 0)

        return food_limit, goods_limit

    def order_colonists(self, state):
        self.loc.t("ui.order_colonists")
        if state != self.state:
            self.log(self.loc.t("ui.order_only_own_state"), "red")
            return

        win = self.create_window(self.loc.t("ui.order_colonists"), key="ui.order_colonists")
        win.geometry("460x420")
        win.resizable(False, False)

        # === Fonty spójne z resztą UI (misje/top bar) ===
        title_font = getattr(self, "top_title_font", ("Cinzel", 16, "bold"))
        info_font = getattr(self, "top_info_font", ("EB Garamond Italic", 14))
        small_info_font = (info_font[0], max(10, info_font[1] - 2))
        small_info_bold = (info_font[0], max(10, info_font[1] - 2), "bold")

        # === Nagłówek ===
        ttk.Label(win, text=self.loc.t("ui.order_new_colonists"), font=title_font).pack(pady=12)

        # === Liczba kolonistów (slider) ===
        amount_frame = ttk.Frame(win)
        amount_frame.pack(pady=8, fill="x", padx=20)

        ttk.Label(amount_frame, text=self.loc.t("ui.num_colonists"), font=small_info_bold).pack(anchor="w")

        amount_var = tk.IntVar(value=1)
        slider = tk.Scale(
            amount_frame,
            from_=1, to=20,
            orient="horizontal",
            variable=amount_var,
            length=380,
            font=small_info_font
        )
        slider.pack(pady=5)

        amount_lbl = ttk.Label(amount_frame, text="1", foreground="blue", font=small_info_bold)
        amount_lbl.pack(anchor="w")

        def update_amount_label(*_):
            amount_lbl.config(text=str(amount_var.get()))
            update_costs()

        amount_var.trace_add("write", update_amount_label)

        # === Wybór metody płatności ===
        method_frame = ttk.LabelFrame(win, text=self.loc.t("ui.payment_method"))
        method_frame.pack(pady=10, fill="x", padx=20)

        payment_method = tk.StringVar(value="reputation")

        ttk.Radiobutton(
            method_frame,
            text=self.loc.t("ui.pay_with_reputation"),
            variable=payment_method,
            value="reputation"
        ).pack(anchor="w", padx=10, pady=3)

        ttk.Radiobutton(
            method_frame,
            text=self.loc.t("ui.pay_with_ducats"),
            variable=payment_method,
            value="gold"
        ).pack(anchor="w", padx=10, pady=3)

        # === Koszty ===
        cost_frame = ttk.Frame(win)
        cost_frame.pack(pady=10, fill="x", padx=20)
        rep_cost_lbl = ttk.Label(cost_frame, text=self.loc.t("ui.rep_cost_fixed"), foreground="purple", font=small_info_font)
        gold_cost_lbl = ttk.Label(cost_frame, text=self.loc.t("ui.ducat_cost_fixed"), foreground="gold", font=small_info_font)
        rep_cost_lbl.pack(anchor="w")
        gold_cost_lbl.pack(anchor="w")

        def update_costs():
            amt = amount_var.get()
            rep_cost = amt * 10
            gold_cost = amt * 1000
            rep_cost_lbl.config(
                text=self.loc.t("screen.diplomacy.rep_cost", rep_cost=rep_cost)
            )
            gold_cost_lbl.config(
                text=self.loc.t("screen.diplomacy.gold_cost", gold_cost=gold_cost)
            )

            # Podświetl aktywną metodę
            if payment_method.get() == "reputation":
                rep_cost_lbl.config(font=small_info_bold, foreground="purple")
                gold_cost_lbl.config(font=small_info_font, foreground="gray")
            else:
                rep_cost_lbl.config(font=small_info_font, foreground="gray")
                gold_cost_lbl.config(font=small_info_bold, foreground="DarkOrange")

        payment_method.trace_add("write", lambda *_: update_costs())
        update_costs()

        # === Przyciski ===
        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=15)

        def confirm_order():
            amt = amount_var.get()
            method = payment_method.get()

            if method == "reputation":
                cost = amt * 10
                if self.europe_relations[self.state] < cost:
                    self.log(self.loc.t("ui.not_enough_reputation", cost=cost), "red")
                    return
                self.europe_relations[self.state] -= cost
                self.log(self.loc.t("log.colonists_ordered_rep", amt=amt, cost=cost), "purple")
            else:
                cost = amt * 1000
                if self.resources["ducats"] < cost:
                    self.log(self.loc.t("ui.not_enough_ducats", cost=cost), "red")
                    return
                self.resources["ducats"] -= cost
                self.log(self.loc.t("log.colonists_ordered_ducats", amt=amt, cost=cost), "purple")

            # Znajdź statek do transportu
            target_ship = None
            earliest = None
            for i, ship in enumerate(self.ships):
                a_eu = ship[0] if len(ship) > 0 else None
                status = ship[3] if len(ship) > 3 else SHIP_STATUS_IN_PORT
                if status in (SHIP_STATUS_TO_EUROPE, SHIP_STATUS_IN_EUROPE_PORT) and a_eu:
                    if earliest is None or a_eu < earliest:
                        earliest = a_eu
                        target_ship = i

            if target_ship is None:
                target_ship = next((i for i, s in enumerate(self.ships) if s[3] == SHIP_STATUS_IN_PORT), 0)

            # Upewnij się, że statek ma 5 elementów
            current = self.ships[target_ship]
            if len(current) < 7:
                # dopnij brakujące pola jak w _ensure_ship_names
                self._ensure_ship_names()
                current = self.ships[target_ship]

            a_eu, a_back, load, st, pend, name, stype = current
            self.ships[target_ship] = (a_eu, a_back, load, st, pend + amt, name, stype)

            self.log(self.loc.t("log.colonists_delivered_soon", amt=amt), "blue")
            win.destroy()

        ttk.Button(btn_frame, text=self.loc.t("ui.order"), command=confirm_order).pack(side="left", padx=8)
        ttk.Button(btn_frame, text=self.loc.t("ui.cancel"), command=win.destroy).pack(side="left", padx=8)

        # wyśrodkuj okno zamawiania kolonistów
        self.center_window(win)

    def update_loc_state_text(self):
        loc_txt = self.loc.t(getattr(self, "location_key", ""), default=getattr(self, "location", ""))
        if self.state in STATES:
            state_txt = self.loc.t(STATES[self.state]["name_key"], default=self.state)
        else:
            state_txt = getattr(self, "state_display", "")
        if hasattr(self, "loc_state_lbl") and self.loc_state_lbl.winfo_exists():
            self.loc_state_lbl.config(text=f"{loc_txt} | {state_txt} | ")

    # === Główny ekran ===
    def main_game(self):
        for w in self.root.winfo_children(): w.destroy()

        top = ttk.Frame(self.root);
        top.pack(fill="x", padx=10, pady=5)
        for col in range(3): top.columnconfigure(col, weight=1)

        self.day_lbl = ttk.Label(top, text="", font=self.top_title_font if hasattr(self, "top_title_font") else ("Cinzel", 14, "bold"))
        self.day_lbl.grid(row=0, column=0, sticky="w")

        center_frame = ttk.Frame(top);
        center_frame.grid(row=0, column=1)
        self.loc_state_lbl = ttk.Label(center_frame, text="", font=self.top_info_font if hasattr(self, "top_info_font") else ("EB Garamond Italic", 12))
        self.loc_state_lbl.pack(side="left");
        self.update_loc_state_text()

        self.monarch_lbl = ttk.Label(center_frame, text=self.loc.t("ui.monarch_placeholder"),
                                     font=((self.top_info_font[0] if hasattr(self, "top_info_font") else "EB Garamond Italic"),
                                           self.top_info_font[1] if hasattr(self, "top_info_font") else 12, "bold"))
        self.monarch_lbl.pack(side="left")

        right_frame = ttk.Frame(top);
        right_frame.grid(row=0, column=2, sticky="e", padx=10)
        self.mission_counter_label = ttk.Label(
            right_frame,
            text=self.loc.t("ui.royal_missions_completed", completed=self.completed_missions, to_win=self.missions_to_win),
            font=((self.top_info_font[0] if hasattr(self, "top_info_font") else "EB Garamond Italic"),
                  self.top_info_font[1] if hasattr(self, "top_info_font") else 12, "bold"),
            foreground="purple"
        )
        self.mission_counter_label.pack(side="left")
        Tooltip(self.mission_counter_label, self.loc.t("tooltip.royal_missions_info"))

        try:
            if not hasattr(self, "gear_icon_menu") or self.gear_icon_menu is None:
                gear_img = Image.open(self.resource_path("img/gear.png")).resize((22, 22), Image.LANCZOS)
                self.gear_icon_menu = ImageTk.PhotoImage(gear_img)
        except Exception as e:
            print("gear.png load failed (menu):", e);
            self.gear_icon_menu = None

        self.game_menu_btn = ttk.Button(right_frame, image=self.gear_icon_menu, command=self.open_game_menu,
                                        style="ColonialSecondary.TButton", width=2)
        if self.gear_icon_menu is None: self.game_menu_btn.config(text="⚙")
        self.game_menu_btn.pack(side="left", padx=(8, 0))
        Tooltip(self.game_menu_btn, self.loc.t("ui.game_menu.tooltip", default="Menu"))

        self.pop_frame = ttk.Frame(top);
        self.pop_frame.grid(row=1, column=0, columnspan=3, pady=(2, 0))
        base_font = self.top_info_font if hasattr(self, "top_info_font") else ("EB Garamond Italic", 12)

        self.pop_lbl = ttk.Label(self.pop_frame, text=self.loc.t("ui.population_placeholder"), font=base_font)
        self.pop_lbl.pack(side="left", padx=5);
        self.pop_tooltip = Tooltip(self.pop_lbl, self.loc.t("tooltip.population"))
        ttk.Label(self.pop_frame, text="|", font=base_font).pack(side="left", padx=5)
        self.work_lbl = ttk.Label(self.pop_frame, text=self.loc.t("ui.free_workers_placeholder"), font=base_font)
        self.work_lbl.pack(side="left", padx=5)
        self.work_tooltip = Tooltip(self.work_lbl, self.loc.t("tooltip.free_workers_info"))

        self.res_frame = ttk.LabelFrame(self.root, text=self.loc.t("ui.resources"));
        self.res_frame.pack(fill="x", padx=10, pady=5)
        self.res_labels, self.res_net_labels = {}, {}
        row = ttk.Frame(self.res_frame);
        row.pack(fill="x")

        for i, res in enumerate(RESOURCES):
            if i % 6 == 0 and i > 0: row = ttk.Frame(self.res_frame); row.pack(fill="x")
            cell = ttk.Frame(row)
            cell.pack(side="left", padx=2)
            res_key = RESOURCE_DISPLAY_KEYS.get(res, res)
            res_name = self.loc.t(res_key, default=res)
            lbl = ttk.Label(cell, text=f"{res_name}: {int(self.resources[res])}", width=26, anchor="w")
            lbl.pack(side="left")
            self.res_labels[res] = lbl
            net_lbl = ttk.Label(cell, text="", width=8, anchor="w", foreground="gray")
            net_lbl.pack(side="left")
            self.res_net_labels[res] = net_lbl

        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=10, pady=5)
        groups = [
            [("ui.ships", self.ships_menu), ("ui.native_trade", self.native_menu), ("ui.diplomacy", self.diplomacy_menu)],
            [("ui.buildings_btn", self.show_buildings_screen), ("ui.map", self.show_world_map), ("ui.missions", self.show_missions_overview)],
            [("ui.wait_1_day", lambda: self.advance_date(1)), ("ui.wait_3_days", lambda: self.advance_date(3)), ("ui.wait_7_days", lambda: self.advance_date(7))]
        ]
        for col in range(3): action_frame.grid_columnconfigure(col, weight=1, uniform="actions")
        self.action_buttons = []

        current_row = 0
        for gi, group in enumerate(groups):
            for col, (key, cmd) in enumerate(group):
                pad_top = 0 if gi == 0 else 10
                btn = ttk.Button(action_frame, text=self.loc.t(key), command=cmd)
                btn.grid(row=current_row, column=col, padx=5, pady=(pad_top, 5), sticky="ew")
                self.action_buttons.append((key, btn))
            current_row += 1

        self.log_frame = ttk.LabelFrame(self.root, text=self.loc.t("ui.journal"))
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_text = tk.Text(self.log_frame, height=10, state=tk.DISABLED, wrap=tk.WORD, font=self.journal_font, bg="#e1d2ad", fg="#3b2a1a")
        self.log_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(self.log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.log_text.tag_configure("spacing", spacing3=4)
        self.log_text.tag_add("spacing", "1.0", "end")
        if not getattr(self, "log_lines", []):
            self.log(self.loc.t("log.colonization_started"), "green")
            self.log(self.loc.t("story.monarch_order", monarch=self.get_monarch()), "green")
        self.update_display()
        self.current_screen = "game"

    def refresh_game_texts(self):
        """Odświeża statyczne napisy w UI gry po zmianie języka."""
        if getattr(self, "current_screen", None) != "game": return

        self.update_loc_state_text()

        if hasattr(self, "mission_counter_label") and self.mission_counter_label.winfo_exists():
            self.mission_counter_label.config(text=self.loc.t("ui.royal_missions_completed",
                                                              completed=self.completed_missions, to_win=self.missions_to_win))

        if hasattr(self, "res_frame") and self.res_frame.winfo_exists(): self.res_frame.config(text=self.loc.t("ui.resources"))
        if hasattr(self, "build_frame") and self.build_frame.winfo_exists(): self.build_frame.config(text=self.loc.t("ui.buildings"))
        if hasattr(self, "log_frame") and self.log_frame.winfo_exists(): self.log_frame.config(text=self.loc.t("ui.journal"))

        if hasattr(self, "action_buttons"):
            for key, btn in self.action_buttons:
                if btn.winfo_exists(): btn.config(text=self.loc.t(key))

        if getattr(self, "_game_menu_win", None) and self._game_menu_win.win.winfo_exists():
            self._game_menu_win.refresh_texts()

        self.update_display();
        self.update_log_display()

    def advance_date(self, days):

        # Liczymy dzień po dniu, ale śmierć z głodu losujemy zbiorczo
        initial_food = self.resources["food"]
        food = initial_food
        starvation_days = 0
        max_excess = 0  # do logowania przeludnienia

        for _ in range(days):
            self.days_passed += 1
            cap = self.calculate_population_capacity()

            if self.people > cap:
                excess = self.people - cap
                max_excess = max(max_excess, excess)

                base_food = cap * FOOD_CONSUMPTION_PER_PERSON
                extra_food = excess * FOOD_CONSUMPTION_PER_PERSON * FOOD_OVERCROWDING_MULTIPLIER
                food_needed = int(base_food + extra_food)
            else:
                excess = 0
                food_needed = int(self.people * FOOD_CONSUMPTION_PER_PERSON)

            if food >= food_needed:
                food -= food_needed
            else:
                # brak jedzenia tego dnia → głód
                food = 0
                starvation_days += 1

        # ile żywności rzeczywiście zużyli ludzie w tej turze
        people_food_consumption = max(0, initial_food - food)

        # przeludnienie — tylko log (brak wypędzania)
        if max_excess > 0:
            self.log(
                self.loc.t("log.overcrowding", excess=max_excess),
                "orange"
            )

        # jeśli w tej turze wystąpił głód choć jednego dnia → losowa śmiertelność
        if starvation_days > 0 and self.people > 0:
            # szansa przeżycia jednego kolonisty po N dniach głodu
            survival_prob = 0.95 ** starvation_days
            deaths = 0
            for _ in range(self.people):
                # jeśli wylosujemy wynik > survival_prob → kolonista umiera
                if random.random() > survival_prob:
                    deaths += 1

            if deaths > 0:
                self.people -= deaths
                self.log(
                    self.loc.t(
                        "log.starvation_deaths",
                        days=starvation_days,
                        deaths=deaths
                    ),
                    "red"
                )

        # po dziennej pętli głodu mamy finalną żywność w zmiennej `food`
        # ustaw ją w zasobach, żeby stan się zgadzał
        self.resources["food"] = food

        # --- PRODUKCJA / KONSUMPCJA DZIEŃ PO DNIU ---
        for _ in range(days):

            # --- dzienna produkcja plemion indiańskich ---
            for tribe in self.native_relations:
                prod_map = self.native_prod.get(tribe, {})
                cap_map = self.native_cap.get(tribe, {})
                stock_map = self.native_stock.get(tribe, {})
                for res, prod_val in prod_map.items():
                    cap_val = cap_map.get(res, 0)
                    cur = stock_map.get(res, 0)
                    new_amt = min(cap_val, cur + prod_val)
                    stock_map[res] = new_amt
                self.native_stock[tribe] = stock_map

            building_data = self.calculate_production()
            daily_net = {r: 0 for r in RESOURCES}

            for b, prod, cons, eff in building_data:
                # jeśli nie działa (brak wejść) to pomijamy
                if eff == 0 and any(cons.values()):
                    continue

                for res, amt in prod.items():
                    daily_net[res] += amt * eff

                for res, amt in cons.items():
                    daily_net[res] -= amt * eff

            # ograniczamy dzienne zużycie do dostępnych zasobów
            food_limit, goods_limit = self.calculate_storage_limits()

            # żeby nie spamować co turę tym samym
            if not hasattr(self, "_full_storage_logged"):
                self._full_storage_logged = set()

            for res, change in daily_net.items():
                if change < 0:
                    available = self.resources.get(res, 0)
                    to_consume = min(available, -change)
                    self.resources[res] -= to_consume

                elif change > 0:
                    cur = self.resources.get(res, 0)

                    # rozróżnienie food vs goods
                    limit = food_limit if res == "food" else goods_limit

                    if cur >= limit:
                        # produkcja staje – nic nie dodajemy
                        # log tylko raz na dany surowiec na dzień
                        key = (self.current_date, res)
                        if key not in self._full_storage_logged:
                            res_name = self.loc.t(RESOURCE_DISPLAY_KEYS.get(res, res), default=res)
                            self.log(self.loc.t("log.no_storage_space", res=res_name), "DarkOrange")
                            self._full_storage_logged.add(key)
                        continue

                    # jak jest miejsce częściowo, to dotnij produkcję do limitu
                    addable = min(change, limit - cur)
                    self.resources[res] = cur + addable

            # --- czas i misje ---
            self.current_date += timedelta(days=1)

            # sprawdź misje indiańskie każdego dnia
            self.try_generate_native_missions()

        if self.current_mission is not None and self.current_mission[0] < self.current_date:
            end, req, sent, diff, text, idx = self.current_mission
            rep_penalty = 10 * diff
            self.log(self.loc.t("log.royal_mission_failed", penalty=rep_penalty), "red")
            self.europe_relations[self.state] = max(0, self.europe_relations[self.state] - rep_penalty)
            self.current_mission = None

    def update_display(self):
        if not hasattr(self, "day_lbl") or not self.current_date:
            return
        self.day_lbl.config(text=self.loc.t("ui.date_label", date=self.current_date.strftime('%d %B %Y')))

        self.monarch_lbl.config(
            text=self.loc.t("ui.monarch_label", monarch=self.get_monarch())
        )
        cap = self.calculate_population_capacity()
        self.pop_lbl.config(
            text=self.loc.t("ui.population_label", people=self.people, cap=cap)
        )

        free = self.free_workers()
        self.work_lbl.config(text=self.loc.t("ui.free_workers_label", free=free), foreground=("goldenrod" if free > 0 else "black"))

        food_limit, goods_limit = self.calculate_storage_limits()

        for res, lbl in self.res_labels.items():
            res_key = RESOURCE_DISPLAY_KEYS.get(res, res)
            res_name = self.loc.t(res_key, default=res)

            cur = int(self.resources.get(res, 0))

            # jeśli nie chcesz limitu dla dukatów, zostaw jak było
            if res == "ducats":
                lbl.config(text=f"{res_name}: {cur}", foreground="black")
                continue

            limit = food_limit if res == "food" else goods_limit
            lbl.config(text=f"{res_name}: {cur} / {limit}")

            # kolory progowe
            if cur > limit:
                color = "red"
            elif cur >= 0.8 * limit:
                color = "#FF9000"
            else:
                color = "black"

            lbl.config(foreground=color)

        building_data = self.calculate_production()
        net_total = {r: 0 for r in RESOURCES}

        # uwzględnij dzienne zużycie pożywienia przez ludzi w szacunkach netto
        cap = self.calculate_population_capacity()
        if self.people > cap:
            excess = self.people - cap
            base_food = cap * FOOD_CONSUMPTION_PER_PERSON
            extra_food = excess * FOOD_CONSUMPTION_PER_PERSON * FOOD_OVERCROWDING_MULTIPLIER
            food_needed = base_food + extra_food
        else:
            food_needed = self.people * FOOD_CONSUMPTION_PER_PERSON
        net_total["food"] -= food_needed

        # produkcja netto z budynków (lista nie jest już wyświetlana na głównym ekranie)
        for b, prod, cons, eff in building_data:
            if b.get("is_district"):
                continue
            local_net = {r: prod.get(r, 0) - cons.get(r, 0) for r in RESOURCES}
            for r, v in local_net.items():
                net_total[r] += v * eff

        # aktualizuj zmiany netto przy surowcach
        if hasattr(self, "res_net_labels"):
            for r, v in net_total.items():
                if abs(v) < 0.05:
                    txt = " (≈0)"
                    color = "gray"
                elif v > 0:
                    txt = f" (+{v:.1f})"
                    color = "darkgreen"
                else:
                    # zużycie: jeśli brak surowca na stanie -> czerwony, jeśli jest -> żółty
                    txt = f" ({v:.1f})"
                    color = "red" if self.resources.get(r, 0) <= 0 else "goldenrod"

                lbl = self.res_net_labels.get(r)
                if lbl:
                    lbl.config(text=txt, foreground=color)

        finished = [c for c in self.constructions if c[0] <= self.current_date]
        for c in finished:
            self.constructions.remove(c)
            new_b = c[1]
            self.buildings.append(new_b)
            self.busy_people -= c[2]
            y, x = new_b["pos"]
            self.map_grid[y][x]["building"].append(new_b)

            nice_name = self.get_building_display_name(new_b)
            self.log(self.loc.t("log.completed_generic", nice_name=nice_name), "green")
            self.play_sound("building_done")

        finished_upgrades = [u for u in self.upgrades_in_progress if u[0] <= self.current_date]
        for u in finished_upgrades:
            self.upgrades_in_progress.remove(u)
            idx = u[1]
            old_level = self.buildings[idx]["level"]
            self.buildings[idx]["level"] = u[2]
            if "capacity" in BUILDINGS[self.buildings[idx]["base"]]["upgrades"][u[2]-1]:
                self.buildings[idx]["capacity"] = BUILDINGS[self.buildings[idx]["base"]]["upgrades"][u[2]-1]["capacity"]
            workers_used = BUILDINGS[self.buildings[idx]["base"]]["upgrades"][old_level].get("workers", 1)
            self.busy_people -= workers_used
            base_data = BUILDINGS[self.buildings[idx]["base"]]
            # nazwa PRZED ulepszeniem
            if old_level == 0:
                old_name = self.loc.t(base_data.get("name_key"), default=self.buildings[idx]["base"])
            else:
                old_name = base_data["upgrades"][old_level - 1].get("name_key",
                    self.loc.t(base_data.get("name_key"), default=self.buildings[idx]["base"])
                )
            # nazwa PO ulepszeniu
            new_name = base_data["upgrades"][u[2] - 1].get("name_key",
                self.loc.t(base_data.get("name_key"), default=self.buildings[idx]["base"])
            )

            self.log(self.loc.t("log.upgrade_done"), "DarkOrange")
            self.play_sound("building_done")

        self.process_arriving_ships()
        self.auto_send_empty_ship()

        self.root.after(100, self.update_display)

        exp_done = [e for e in self.expeditions if e[0] <= self.current_date]
        for e in exp_done:
            self.expeditions.remove(e)
            self.finish_expedition(e)

        if self.people <= 0 and not getattr(self, "game_over", False):
            self.game_over = True
            self.death_game()
            return

    def clear_root(self):
        for w in self.root.winfo_children():
            # NIE kasuj otwartych okien (settings, itp.)
            if isinstance(w, tk.Toplevel):
                continue
            w.destroy()

    def refresh_start_screen(self):

        self.start_screen()

# ============== URUCHOMIENIE ==============
if __name__ == "__main__":
    root = tk.Tk()
    app = ColonySimulator(root)
    root.mainloop()