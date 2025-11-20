# main.py
import os
import sys
import tkinter as tk
from ctypes import windll
from tkinter import ttk
from datetime import datetime, timedelta
import random
import math
from functools import partial

import pygame
from PIL import Image, ImageTk

from buildings import BuildingsMixin
from map_generator import generate_map, MAP_SIZE
from constants import *
from missions import MissionsMixin
from relations import RelationsMixin
from ships import ShipsMixin


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

class ColonySimulator(MissionsMixin, ShipsMixin, RelationsMixin, BuildingsMixin):
    def __init__(self, root):
        self.root = root
        self.root.title("Imperium Kolonii")
        self.root.geometry("1600x1000")

        # Załaduj wszystkie czcionki
        load_font_ttf(self.resource_path("fonts/Cinzel-Regular.ttf"))
        load_font_ttf(self.resource_path("fonts/Cinzel-Bold.ttf"))
        load_font_ttf(self.resource_path("fonts/IMFellEnglishSC-Regular.ttf"))
        load_font_ttf(self.resource_path("fonts/EBGaramond-Italic.ttf"))
        load_font_ttf(self.resource_path("fonts/MedievalSharp-Regular.ttf"))


        self.title_font = ("IM Fell English SC", 28, "bold")
        self.ui_font = ("EB Garamond Italic", 18)
        self.journal_font = ("EB Garamond Italic", 14)

        self.top_title_font = ("Cinzel", 14, "bold")
        self.top_info_font = ("EB Garamond Italic", 12)

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
        self.people = 10
        self.busy_people = 0

        # self.resources = {r: 5000 if r in ["drewno", "żywność", "skóry", "żelazo", "stal"] else 0 for r in RESOURCES}
        self.resources = {r: 0 for r in RESOURCES}
        self.resources["żywność"] = 1000
        self.resources["drewno"] = 50
        self.resources["żelazo"] = 30
        self.resources["skóry"] = 10
        self.resources["srebro"] = 10
        self.resources["medykamenty"] = 10
        self.resources["dukaty"] = 300

        self.buildings = []
        self.constructions = []
        self.upgrades_in_progress = []
        self.expeditions = []
        self.ships = []
        self.auto_sail_timer = None

        self.native_relations = {tribe: 50 for tribe in random.sample(TRIBES, 3)}
        # reputacja z państwami europejskimi – na start 0, później własne państwo podbijemy
        self.europe_relations = {s: 0 for s in STATES}

        # kumulacja wartości handlu (do progów reputacji)
        self.native_trade_value = {tribe: 0 for tribe in self.native_relations}
        self.europe_trade_value = {s: 0 for s in self.europe_relations}
        self.trade_reputation_threshold = 1000

        if self.state == "Francja":
            self.trade_reputation_threshold += STATES[self.state]["reputation_threshold"]

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

        self.start_screen()
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
        """Wyśrodkuj podane okno na ekranie."""
        win.update_idletasks()
        w = win.winfo_width()
        h = win.winfo_height()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

    def create_window(self, title):
        win = tk.Toplevel(self.root)
        win.title(title)
        BG = self.style.lookup("TFrame", "background")
        win.configure(bg=BG)
        return win

    def resource_path(self, filename):
        if getattr(sys, 'frozen', False):
            # tryb PyInstaller --onefile: pliki są w katalogu tymczasowym
            base = sys._MEIPASS
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, filename)

    def init_sounds(self):
        # MUZYKA TŁA
        music_path = self.resource_path("sounds/music.mp3")
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.4)  # głośność 0.0–1.0
            pygame.mixer.music.play(loops=-1)  # -1 = gra w pętli bez końca
        except Exception as e:
            print("Nie udało się załadować muzyki:", e)

        # tu od razu przygotujemy dźwięki efektów
        self.sounds = {}
        try:
            self.sounds["new_mission"] = pygame.mixer.Sound(self.resource_path("sounds/new_mission.wav"))
            self.sounds["ship_arrived"] = pygame.mixer.Sound(self.resource_path("sounds/anchor.wav"))
            self.sounds["building_done"] = pygame.mixer.Sound(self.resource_path("sounds/building_done.wav"))
        except Exception as e:
            print("Nie udało się załadować któregoś z efektów dźwiękowych:", e)

    def play_sound(self, name):
        snd = getattr(self, "sounds", {}).get(name)
        if snd:
            snd.play()

    def get_cell_size(self):
        """
        Dynamiczny rozmiar pola mapy w pikselach.
        Mapa zawsze stara się zmieścić w ~600x600, niezależnie od self.map_size.
        """
        max_map_pixels = 600  # docelowy „bok” mapy w pikselach
        cell = max_map_pixels // self.map_size
        # trochę ograniczeń, żeby nie było śmiesznie małe / ogromne
        cell = max(40, min(100, cell))
        return cell

    def update_log_display(self):
        if not hasattr(self, 'log_text'): return
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        for text, color in self.log_lines[-100:]:
            self.log_text.insert(tk.END, text + "\n", color)
            self.log_text.tag_config(color, foreground=color)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def free_workers(self): return max(0, self.people - self.busy_people)

    def can_afford(self, cost):
        # tworzymy kopię, by nie modyfikować oryginału
        real_cost = cost.copy()

        # --- BONUS HOLANDII ---
        if self.state == "Holandia":
            mult = STATES[self.state].get("build_cost", 1)
            real_cost = {r: int(a * mult) for r, a in real_cost.items()}

        return all(self.resources.get(r, 0) >= a for r, a in real_cost.items())

    def spend_resources(self, cost):
        # tworzymy kopię, by nie modyfikować oryginału
        real_cost = cost.copy()

        # --- BONUS HOLANDII ---
        if self.state == "Holandia":
            mult = STATES[self.state].get("build_cost", 1)
            real_cost = {r: int(a * mult) for r, a in real_cost.items()}

        # faktyczne pobranie zasobów
        for r, a in real_cost.items():
            self.resources[r] -= a

    def get_monarch(self):
        for monarch in STATES[self.state]['rulers']:
            if self.current_date.year > monarch["start"] and self.current_date.year <= monarch["end"]:
                if self.current_monarch != monarch["name"]:
                    self.europe_relations[self.state] = 50
                return monarch["name"]
        return "Nieznany"

    # === Start gry ===
    def start_screen(self):

        # wyczyść stare widgety
        for w in self.root.winfo_children():
            w.destroy()

        # === TŁO Z OBRAZU ===
        try:
            img_path = self.resource_path("img/colony.jpg")
            bg_image = Image.open(img_path)

            # dopasuj do okna (1600x1000 jak w __init__)
            bg_image = bg_image.resize((1600, 1000), Image.LANCZOS)

            # musimy trzymać referencję w self, inaczej obraz zniknie
            self.start_bg_image = ImageTk.PhotoImage(bg_image)

            bg_label = tk.Label(self.root, image=self.start_bg_image)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Nie udało się załadować tła colony.jpg:", e)
            bg_label = tk.Label(self.root)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # === GŁÓWNA RAMKA NA PRZYCISKI / WYBÓR PAŃSTWA ===
        frame = ttk.Frame(bg_label, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="IMPERIUM KOLONII", font=self.title_font).pack(pady=20)
        ttk.Label(frame, text="Wybierz państwo:", font=self.ui_font).pack(pady=10)

        self.state_var = tk.StringVar(value="Portugalia")
        combo = ttk.Combobox(
            frame,
            textvariable=self.state_var,
            values=list(STATES.keys()),
            state="readonly",
            width=30
        )
        combo.pack(pady=5)

        ttk.Label(frame, text="Długość gry (liczba misji królewskich):", font=self.ui_font).pack(pady=(15, 5))

        self.game_length_var = tk.StringVar(value="zwykla")

        lengths = [
            ("Błyskawiczna (15 misji)", "blyskawiczna"),
            ("Szybka (30 misji)", "szybka"),
            ("Zwykła (50 misji)", "zwykla"),
            ("Długa (70 misji)", "dluga"),
            ("Maraton (100 misji)", "maraton"),
            ("Epicka (150 misji)", "epicka"),
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

        ttk.Button(frame, text="Losowe Państwo", style="ColonialSecondary.TButton", command=lambda: self.state_var.set(random.choice(list(STATES.keys())))).pack(pady=10)
        ttk.Button(frame, text="Rozpocznij", style="Colonial.TButton", command=self.start_game).pack(pady=10)


    def start_game(self):
        self.state = self.state_var.get()
        if not self.state: return

        # ustawienie długości gry na podstawie wyboru na ekranie startowym
        length_key = getattr(self, "game_length_var", None).get() if hasattr(self, "game_length_var") else "zwykla"

        length_map = {
            "blyskawiczna": 15,
            "szybka": 30,
            "zwykla": 50,
            "dluga": 70,
            "maraton": 100,
            "epicka": 150,
        }
        self.missions_to_win = length_map.get(length_key, 50)

        # własne państwo startuje z lepszą reputacją, reszta pozostaje 0
        self.europe_relations[self.state] = 50

        self.location = random.choice([
            "Zatoka Meksykańska", "Wybrzeże Brazylii", "Karaiby", "Floryda", "Patagonia",
            "Zatoka Hudsona", "Wyspy Bahama", "Delta Orinoko", "Wybrzeże Peru", "Nowy Jork"
        ])
        if "pop_start" in STATES[self.state]:
            self.people += STATES[self.state]["pop_start"]

        self.map_grid, self.settlement_pos = generate_map(self.map_size)
        self.map_size = len(self.map_grid)
        self.current_date = generate_start_date()

        # Start systemu po 6 miesiącach
        self.native_missions_enabled_start = self.current_date + timedelta(days=180)

        sy, sx = self.settlement_pos
        for _ in range(3):
            tent = {"base": "namiot", "level": 0, "workers": 0, "pos": (sy, sx)}
            self.buildings.append(tent)
            self.map_grid[sy][sx]["building"].append(tent)

        self.ships = [(None, None, {}, "w porcie", 0)]
        self.flagship_index = 0
        self.auto_sail_timer = self.current_date + timedelta(days=14)
        self.main_game()

    def order_colonists(self, state):
        """Zamówienie nowych kolonistów z Europy – nowe okno z wyborem metody i sliderem."""
        if state != self.state:
            self.log("Możesz zamawiać kolonistów tylko od własnego państwa!", "red")
            return

        win = self.create_window(f"Zamów kolonistów z Europy")

        win.geometry("460x380")
        win.resizable(False, False)

        # === Nagłówek ===
        ttk.Label(win, text="Zamów nowych kolonistów", font=("Arial", 14, "bold")).pack(pady=12)

        # === Liczba kolonistów (slider) ===
        amount_frame = ttk.Frame(win)
        amount_frame.pack(pady=8, fill="x", padx=20)

        ttk.Label(amount_frame, text="Liczba kolonistów:", font=("Arial", 10)).pack(anchor="w")
        amount_var = tk.IntVar(value=1)
        slider = tk.Scale(amount_frame, from_=1, to=20, orient="horizontal", variable=amount_var, length=380)
        slider.pack(pady=5)

        amount_lbl = ttk.Label(amount_frame, text="1", foreground="blue", font=("Arial", 11, "bold"))
        amount_lbl.pack(anchor="w")

        def update_amount_label(*_):
            amount_lbl.config(text=str(amount_var.get()))
            update_costs()

        amount_var.trace_add("write", update_amount_label)

        # === Wybór metody płatności ===
        method_frame = ttk.LabelFrame(win, text="Metoda płatności")
        method_frame.pack(pady=10, fill="x", padx=20)

        payment_method = tk.StringVar(value="reputation")

        ttk.Radiobutton(method_frame, text="Reputacją (10 za osobę)", variable=payment_method, value="reputation").pack(anchor="w", padx=10, pady=3)
        ttk.Radiobutton(method_frame, text="Dukatami (1000 za osobę)", variable=payment_method, value="gold").pack(anchor="w", padx=10, pady=3)

        # === Koszty ===
        cost_frame = ttk.Frame(win)
        cost_frame.pack(pady=10, fill="x", padx=20)

        rep_cost_lbl = ttk.Label(cost_frame, text="Koszt reputacji: 10", foreground="purple")
        gold_cost_lbl = ttk.Label(cost_frame, text="Koszt dukatów: 1000", foreground="gold")
        rep_cost_lbl.pack(anchor="w")
        gold_cost_lbl.pack(anchor="w")

        def update_costs():
            amt = amount_var.get()
            rep_cost = amt * 10
            gold_cost = amt * 1000
            rep_cost_lbl.config(text=f"Koszt reputacji: {rep_cost}")
            gold_cost_lbl.config(text=f"Koszt dukatów: {gold_cost}")

            # Podświetl aktywną metodę
            if payment_method.get() == "reputation":
                rep_cost_lbl.config(font=("Arial", 10, "bold"), foreground="purple")
                gold_cost_lbl.config(font=("Arial", 10), foreground="gray")
            else:
                rep_cost_lbl.config(font=("Arial", 10), foreground="gray")
                gold_cost_lbl.config(font=("Arial", 10, "bold"), foreground="gold")

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
                    self.log(f"Za mało reputacji! Potrzeba: {cost}", "red")
                    return
                self.europe_relations[self.state] -= cost
                self.log(f"Zamówiono {amt} kolonistów – zapłacono {cost} reputacji.", "purple")
            else:
                cost = amt * 1000
                if self.resources["dukaty"] < cost:
                    self.log(f"Za mało dukatów! Potrzeba: {cost}", "red")
                    return
                self.resources["dukaty"] -= cost
                self.log(f"Zamówiono {amt} kolonistów – zapłacono {cost} dukatów.", "purple")

            # Znajdź statek do transportu
            target_ship = None
            earliest = None
            for i, ship in enumerate(self.ships):
                a_eu = ship[0] if len(ship) > 0 else None
                status = ship[3] if len(ship) > 3 else "w porcie"
                if status in ("w drodze do Europy", "w porcie w Europie") and a_eu:
                    if earliest is None or a_eu < earliest:
                        earliest = a_eu
                        target_ship = i

            if target_ship is None:
                target_ship = next((i for i, s in enumerate(self.ships) if s[3] == "w porcie"), 0)

            # Upewnij się, że statek ma 5 elementów
            current = self.ships[target_ship]
            if len(current) == 4:
                a_eu, a_back, load, st = current
                self.ships[target_ship] = (a_eu, a_back, load, st, 0)
                current = self.ships[target_ship]

            a_eu, a_back, load, st, pend = current
            self.ships[target_ship] = (a_eu, a_back, load, st, pend + amt)

            self.log(f"Kolonizatorzy ({amt}) zostaną dostarzeni najbliższym statkiem z Europy.", "blue")
            win.destroy()

        ttk.Button(btn_frame, text="Zamów", command=confirm_order).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Anuluj", command=win.destroy).pack(side="left", padx=8)

        # wyśrodkuj okno zamawiania kolonistów
        self.center_window(win)

    # === Mapa ===
    def show_map(self):

        win = self.create_window(f"Buduj - wybierz pole")

        canvas_width = 850
        canvas_height = 850
        canvas = tk.Canvas(win, width=canvas_width, height=canvas_height, bg=self.style.lookup("TFrame", "background"),
                   highlightthickness=0)
        canvas.pack(pady=10)

        cell_size = self.get_cell_size()
        map_pixel_size = self.map_size * cell_size

        # wyśrodkuj mapę na canvasie
        offset_x = (canvas_width - map_pixel_size) // 2
        offset_y = 40  # u góry trochę miejsca na tytuł / legendę

        def draw():
            canvas.delete("all")
            for y in range(self.map_size):
                for x in range(self.map_size):
                    cell = self.map_grid[y][x]

                    if not cell["discovered"]:
                        canvas.create_rectangle(
                            offset_x + x * cell_size,
                            offset_y + y * cell_size,
                            offset_x + (x + 1) * cell_size,
                            offset_y + (y + 1) * cell_size,
                            fill="#888888",
                            outline="gray"
                        )
                        continue

                    color = BASE_COLORS[cell["terrain"]]
                    outline = "gray"
                    width = 1
                    if cell["terrain"] in ["osada", "dzielnica"]:
                        outline = "yellow"
                        width = 3

                    canvas.create_rectangle(
                        offset_x + x * cell_size,
                        offset_y + y * cell_size,
                        offset_x + (x + 1) * cell_size,
                        offset_y + (y + 1) * cell_size,
                        fill=color,
                        outline=outline,
                        width=width
                    )

                    building_in_progress = next((c for c in self.constructions if c[1]["pos"] == (y, x)), None)
                    if building_in_progress:
                        end, _, _, start = building_in_progress
                        total_days = (end - start).days
                        elapsed = (self.current_date - start).days
                        pct = min(100, max(0, int(elapsed / total_days * 100))) if total_days > 0 else 0
                        canvas.create_text(
                            offset_x + x * cell_size + cell_size // 2,
                            offset_y + y * cell_size + cell_size // 2 + 20,
                            text=f"{pct}%",
                            fill="white",
                            font=("Arial", 9, "bold")
                        )

                    if cell["terrain"] in ["osada", "dzielnica"]:
                        buildings_here = [b for b in cell["building"] if not b.get("is_district", False)]
                        used = len(buildings_here)
                        canvas.create_text(
                            offset_x + x * cell_size + cell_size // 2,
                            offset_y + y * cell_size + cell_size // 2 - 20,
                            text=f"{cell['terrain'].capitalize()}",
                            fill="white",
                            font=("Arial", 9, "bold")
                        )
                        canvas.create_text(
                            offset_x + x * cell_size + cell_size // 2,
                            offset_y + y * cell_size + cell_size // 2,
                            text=f"{used}/5",
                            fill="yellow",
                            font=("Arial", 10, "bold")
                        )

                    if cell["terrain"] == "wzniesienia" and cell["resource"]:
                        rc = MINE_COLORS[cell["resource"]]
                        canvas.create_rectangle(
                            offset_x + x * cell_size + cell_size - 20,
                            offset_y + y * cell_size + cell_size - 20,
                            offset_x + x * cell_size + cell_size - 5,
                            offset_y + y * cell_size + cell_size - 5,
                            fill=rc,
                            outline="black"
                        )

                    if self.selected_building:
                        data = BUILDINGS[self.selected_building]
                        if cell["terrain"] not in data.get("allowed_terrain", []):
                            continue
                        if not data.get("requires_settlement"):
                            if cell["building"] or any(c[1]["pos"] == (y, x) for c in self.constructions):
                                continue
                        if data.get("requires_settlement"):
                            if cell["terrain"] not in ["osada", "dzielnica"]:
                                continue
                            used = len([b for b in cell["building"] if not b.get("is_district", False)])
                            in_progress = len([c for c in self.constructions if c[1]["pos"] == (y, x)])
                            if used + in_progress >= 5:
                                continue
                        if data.get("requires_adjacent_settlement"):
                            if not self.is_adjacent_to_settlement((y, x)):
                                continue
                            if cell["terrain"] == "morze" and self.selected_building != "przystań":
                                continue

                        canvas.create_rectangle(
                            offset_x + x * cell_size,
                            offset_y + y * cell_size,
                            offset_x + (x + 1) * cell_size,
                            offset_y + (y + 1) * cell_size,
                            outline="lime",
                            width=3
                        )

            self.draw_legend(canvas, offset_x, offset_y, cell_size)

        def click(event):
            x = (event.x - offset_x) // cell_size
            y = (event.y - offset_y) // cell_size
            if (
                0 <= x < self.map_size
                and 0 <= y < self.map_size
                and self.map_grid[y][x]["discovered"]
            ):
                if self.selected_building:
                    self.start_construction_at(self.selected_building, (y, x))
                    self.selected_building = None
                    win.destroy()

        canvas.bind("<Button-1>", click)
        draw()
        ttk.Button(win, text="Anuluj", command=win.destroy).pack(pady=5)

        # wyśrodkuj okno mapy
        self.center_window(win)

    def draw_legend(self, canvas, offset_x, offset_y, cell_size):
        legend_y = offset_y + self.map_size * cell_size + 30

        # środek mapy (żeby ładnie wyśrodkować legendę)
        center_x = offset_x + (self.map_size * cell_size) / 2

        # tytuł
        canvas.create_text(center_x, legend_y, text="LEGENDA", anchor="center", font=("Arial", 14, "bold"))

        # --- grupa: tereny ---
        terrain_spacing = 80
        terrain_y = legend_y + 50
        terrain_items = list(BASE_COLORS.items())
        terrain_count = len(terrain_items)
        terrain_total_width = (terrain_count - 1) * terrain_spacing
        terrain_start_x = center_x - terrain_total_width / 2

        for i, (name, color) in enumerate(terrain_items):
            x = terrain_start_x + i * terrain_spacing
            canvas.create_rectangle(x - 10, terrain_y - 10, x + 10, terrain_y + 10, fill=color, outline="black")
            canvas.create_text(x, terrain_y + 22, text=name.capitalize(), anchor="center", font=("Arial", 10))

        # --- grupa: surowce kopalniane ---
        mine_spacing = 80
        mine_y = terrain_y + 70
        mine_items = list(MINE_RESOURCES)
        mine_count = len(mine_items)
        mine_total_width = (mine_count - 1) * mine_spacing
        mine_start_x = center_x - mine_total_width / 2

        for i, res in enumerate(mine_items):
            x = mine_start_x + i * mine_spacing
            color = MINE_COLORS[res]
            canvas.create_rectangle(x - 10, mine_y - 10, x + 10, mine_y + 10, fill=color, outline="black")
            canvas.create_text(x, mine_y + 22, text=MINE_NAMES[res], anchor="center", font=("Arial", 10))

    # === Główny ekran ===
    def main_game(self):
        for w in self.root.winfo_children(): w.destroy()

        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=5)

        # 3 kolumny: lewa (data), środek (lokacja/państwo/monarcha), prawa (misje)
        for col in range(3):
            top.columnconfigure(col, weight=1)

        # ========== WIERSZ 1 ==========

        # Data po lewej
        self.day_lbl = ttk.Label(
            top,
            text="",
            font=self.top_title_font if hasattr(self, "top_title_font") else ("Cinzel", 14, "bold")
        )
        self.day_lbl.grid(row=0, column=0, sticky="w")

        # Środkowy frame: lokalizacja | państwo | Monarcha: XYZ
        center_frame = ttk.Frame(top)
        center_frame.grid(row=0, column=1)

        self.loc_state_lbl = ttk.Label(
            center_frame,
            text=f"{self.location} | {self.state} | ",
            font=self.top_info_font if hasattr(self, "top_info_font") else ("EB Garamond Italic", 12)
        )
        self.loc_state_lbl.pack(side="left")

        # Monarcha tuż po państwie, pogrubiony
        self.monarch_lbl = ttk.Label(
            center_frame,
            text="Monarcha: ...",
            font=( (self.top_info_font[0] if hasattr(self, "top_info_font") else "EB Garamond Italic"),
                   self.top_info_font[1] if hasattr(self, "top_info_font") else 12,
                   "bold")
        )
        self.monarch_lbl.pack(side="left")

        # Pogrubiony licznik misji po prawej
        if not hasattr(self, "completed_missions"):
            self.completed_missions = 0

        self.mission_counter_label = ttk.Label(
            top,
            text=f"Misje królewskie wykonane: {self.completed_missions} / {self.missions_to_win}",
            font=( (self.top_info_font[0] if hasattr(self, "top_info_font") else "EB Garamond Italic"),
                   self.top_info_font[1] if hasattr(self, "top_info_font") else 12,
                   "bold"),
            foreground="purple"
        )
        self.mission_counter_label.grid(row=0, column=2, sticky="e", padx=10)

        # ========== WIERSZ 2 – Ludzie / Wolni, wyśrodkowane ==========

        self.pop_frame = ttk.Frame(top)
        self.pop_frame.grid(row=1, column=0, columnspan=3, pady=(2, 0))

        base_font = self.top_info_font if hasattr(self, "top_info_font") else ("EB Garamond Italic", 12)

        self.pop_lbl = ttk.Label(self.pop_frame, text="Ludzie: 0 / 0", font=base_font)
        self.pop_lbl.pack(side="left", padx=5)

        ttk.Label(self.pop_frame, text="|", font=base_font).pack(side="left", padx=5)

        self.work_lbl = ttk.Label(self.pop_frame, text="Wolni: 0", font=base_font)
        self.work_lbl.pack(side="left", padx=5)


        res_frame = ttk.LabelFrame(self.root, text="Surowce"); res_frame.pack(fill="x", padx=10, pady=5)
        self.res_labels = {}
        row = ttk.Frame(res_frame); row.pack(fill="x")
        for i, res in enumerate(RESOURCES):
            if i % 6 == 0 and i > 0: row = ttk.Frame(res_frame); row.pack(fill="x")
            lbl = ttk.Label(row, text=f"{res}: {self.resources[res]}", width=18); lbl.pack(side="left"); self.res_labels[res] = lbl

        prod_frame = ttk.LabelFrame(self.root, text="Produkcja"); prod_frame.pack(fill="x", padx=10, pady=5)
        self.prod_label = ttk.Label(prod_frame, text=""); self.prod_label.pack()

        build_frame = ttk.LabelFrame(self.root, text="Budynki")
        build_frame.pack(fill="x", padx=10, pady=5)

        build_inner = ttk.Frame(build_frame)
        build_inner.pack(fill="both", expand=True)

        self.build_listbox = tk.Listbox(build_inner, height=8)
        self.build_listbox.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)

        build_scroll = ttk.Scrollbar(build_inner, orient="vertical", command=self.build_listbox.yview)
        build_scroll.pack(side="right", fill="y", padx=(0, 5), pady=5)

        self.build_listbox.config(yscrollcommand=build_scroll.set)

        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=10, pady=5)

        groups = [
            [("Buduj", self.build_menu),
             ("Ulepsz/Zdegraduj", self.show_upgrade_menu),
             ("Zarządzaj ludźmi", self.manage_workers)],

            [("Statki", self.ships_menu),
             ("Handel z Indianami", self.native_menu),
             ("Dyplomacja", self.diplomacy_menu)],

            [("Eksploruj", self.explore),
             ("Mapa", self.show_map),
             ("Misje", self.show_missions_overview)],

            [("Czekaj 1 dzień", lambda: self.advance_date(1)),
             ("Czekaj 3 dni", lambda: self.advance_date(3)),
             ("Czekaj 7 dni", lambda: self.advance_date(7))],
        ]

        # 3 kolumny dzielące szerokość *dla całego panelu* (uniform => te same w każdej linii)
        for col in range(3):
            action_frame.grid_columnconfigure(col, weight=1, uniform="actions")

        current_row = 0
        for group_index, group in enumerate(groups):
            for col, (text, command) in enumerate(group):
                # dodatkowy odstęp nad kolejnymi grupami
                top_padding = 0 if group_index == 0 else 10

                btn = ttk.Button(action_frame, text=text, command=command)
                btn.grid(
                    row=current_row,
                    column=col,
                    padx=5,
                    pady=(top_padding, 5),
                    sticky="ew",  # rozciąga się na całą szerokość kolumny
                )

            current_row += 1

        log_frame = ttk.LabelFrame(self.root, text="Dziennik");
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_text = tk.Text(
            log_frame,
            height=10,
            state=tk.DISABLED,
            wrap=tk.WORD,
            font=self.journal_font,
            bg="#e1d2ad",
            fg="#3b2a1a"
        )
        self.log_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Lepsza interlinia dla czytelności
        self.log_text.tag_configure("spacing", spacing3=4)
        self.log_text.tag_add("spacing", "1.0", "end")

        self.log("Kolonizacja rozpoczęta!", "green")
        self.log(f'{self.get_monarch()}, nasz monarcha wydał rozkaz, byś prowadził kolonię i ją rozbudował dla dobra naszego Imperium.', "green")
        self.update_display()

    def advance_date(self, days):
        if days > 1 and self.free_workers() < 1:
            self.log("Za mało ludzi!", "red")
            return

        # Liczymy dzień po dniu, ale śmierć z głodu losujemy zbiorczo
        food = self.resources["żywność"]
        starvation_days = 0
        max_excess = 0  # do logowania przeludnienia

        for _ in range(days):
            cap = self.calculate_population_capacity()

            if self.people > cap:
                excess = self.people - cap
                max_excess = max(max_excess, excess)
                base_food = cap
                extra_food = int(excess * 1.5)
                food_needed = base_food + extra_food
            else:
                excess = 0
                food_needed = self.people

            if food >= food_needed:
                food -= food_needed
            else:
                # brak jedzenia tego dnia → głód
                food = 0
                starvation_days += 1

        # zapisujemy nowy stan żywności
        self.resources["żywność"] = food

        # przeludnienie — tylko log (brak wypędzania)
        if max_excess > 0:
            self.log(
                f"Przeludnienie: {max_excess} osób ponad limit mieszkaniowy – zużywają +50% pożywienia.",
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
                    f"GŁÓD przez {starvation_days} dni! Zmarło {deaths} kolonistów.",
                    "red"
                )

        # --- PRODUKCJA (jak wcześniej, zbiorczo za 'days') ---
        building_data = self.calculate_production()
        total_net = {r: 0 for r in RESOURCES}

        for b, prod, cons, eff in building_data:
            if eff == 0 and any(cons.values()):
                continue
            for res, amt in prod.items():
                total_net[res] += amt * days * eff
            for res, amt in cons.items():
                total_net[res] -= amt * days * eff

        # ograniczamy zużycie do dostępnych zasobów
        for res, change in total_net.items():
            if change < 0:
                available = self.resources.get(res, 0)
                to_consume = min(available, -change)
                self.resources[res] -= to_consume
                total_net[res] = -to_consume

        # dodajemy produkcję
        for res, change in total_net.items():
            if change > 0:
                self.resources[res] += change

        # --- czas i misje ---
        self.current_date += timedelta(days=days)
        # self.log(f"Minęło {days} dni.", "blue")

        # sprawdź misje indiańskie każdego dnia
        self.try_generate_native_missions()

        if self.current_mission is not None and self.current_mission[0] < self.current_date:
            end, req, sent, diff, text, idx = self.current_mission
            self.log("MISJA KRÓLEWSKA NIE WYKONANA W TERMINIE! -reputacja", "red")
            self.europe_relations[self.state] = max(0, self.europe_relations[self.state] - 10 * diff)
            self.current_mission = None

    def update_display(self):
        if not hasattr(self, 'day_lbl'): return
        self.day_lbl.config(text=f"Data: {self.current_date.strftime('%d %B %Y')}")
        self.monarch_lbl.config(text=f" | Monarcha: {self.get_monarch()}")
        cap = self.calculate_population_capacity()
        self.pop_lbl.config(text=f"Ludzie: {self.people} / {cap}")
        self.work_lbl.config(text=f" | Wolni: {self.free_workers()}")

        for res, lbl in self.res_labels.items():
            lbl.config(text=f"{res}: {int(self.resources[res])}")

        building_data = self.calculate_production()
        net_total = {r: 0 for r in RESOURCES}

        # zapamiętaj aktualną pozycję przewinięcia
        first, last = self.build_listbox.yview()

        self.build_listbox.delete(0, tk.END)

        for b in self.buildings:
            if b.get("is_district"): continue
            name = b["base"]
            if b.get("level", 0) > 0:
                name = BUILDINGS[b["base"]]["upgrades"][b["level"] - 1].get("name", name)
            if b.get("resource"):
                name += f" [{b['resource']}]"

            data = next((d for d in building_data if d[0] is b), None)
            status = "—"
            color_tag = "black"

            if data:
                _, prod, cons, eff = data
                consumes_something = any(cons.values())
                missing_resources = consumes_something and eff < 1.0
                if missing_resources: color_tag = "red"
                local_net = {r: prod.get(r, 0) - cons.get(r, 0) for r in RESOURCES}
                prod_str = " | ".join(f"{r}: +{v:.1f}" for r, v in local_net.items() if v > 0.05)
                eff_str = f" ({eff:.0%})" if eff < 1 else ""
                status = f"{prod_str}{eff_str}" if prod_str else "—"
                for r, v in local_net.items():
                    net_total[r] += v * eff

            pos = b["pos"]
            cell = self.map_grid[pos[0]][pos[1]]
            area = "osada" if cell["terrain"] == "osada" else "dzielnica"
            line = f"{name} | Prac: {b.get('workers', 0)}/{self.get_max_workers(b)} | {status} | ({pos[0]},{pos[1]}) | {area}"
            self.build_listbox.insert(tk.END, line)
            self.build_listbox.itemconfig(tk.END, fg=color_tag)

        # przywróć poprzednią pozycję przewinięcia
        self.build_listbox.yview_moveto(first)

        final_items = [f"{r}: +{v:.1f}" for r, v in net_total.items() if v > 0.05]
        total_str = " | ".join(final_items) or "Brak"
        self.prod_label.config(text=total_str, foreground="black")

        finished = [c for c in self.constructions if c[0] <= self.current_date]
        for c in finished:
            self.constructions.remove(c)
            new_b = c[1]
            self.buildings.append(new_b)
            self.busy_people -= c[2]
            y, x = new_b["pos"]
            self.map_grid[y][x]["building"].append(new_b)
            self.log(f"Ukończono: {new_b['base']}", "green")
            self.play_sound("building_done")

        finished_upgrades = [u for u in self.upgrades_in_progress if u[0] <= self.current_date]
        for u in finished_upgrades:
            self.upgrades_in_progress.remove(u)
            idx = u[1]
            old_level = self.buildings[idx]["level"]
            self.buildings[idx]["level"] = u[2]
            if "capacity" in BUILDINGS[self.buildings[idx]["base"]]["upgrades"][u[2]-1]:
                self.buildings[idx]["capacity"] = BUILDINGS[self.buildings[idx]["base"]]["upgrades"][u[2]-1]["capacity"]
            workers_change = BUILDINGS[self.buildings[idx]["base"]]["upgrades"][u[2]-1].get("workers", 0) - \
                            (BUILDINGS[self.buildings[idx]["base"]]["upgrades"][old_level-1].get("workers", 0) if old_level > 0 else 0)
            self.busy_people -= workers_change
            self.log(f"Ukończono ulepszenie: {self.buildings[idx]['base']} → poziom {u[2]}", "gold")
            self.play_sound("building_done")

        self.process_arriving_ships()
        self.auto_send_empty_ship()

        self.root.after(100, self.update_display)

        exp_done = [e for e in self.expeditions if e[0] <= self.current_date]
        for e in exp_done:
            self.expeditions.remove(e)
            self.finish_expedition(e)

    def explore(self):
        if self.free_workers() < 3: self.log("Za mało ludzi!", "red"); return
        if self.resources["żywność"] < 15 and self.resources["drewno"] < 10: self.log("Za mało żywności lub drewna!", "red"); return
        self.show_explore_map()

    def show_explore_map(self):

        win = self.create_window(f"Eksploracja")

        # === INFORMACJE O KOSZTACH ===
        info_frame = ttk.Frame(win)
        info_frame.pack(pady=5)

        ttk.Label(
            info_frame,
            text="Koszt eksploracji:",
            font=("Arial", 12, "bold")
        ).pack()

        ttk.Label(
            info_frame,
            text="• 3 ludzie • 15 żywności • 10 drewna",
            justify="center",
            font=("Arial", 10)
        ).pack()

        canvas_width = 850
        canvas_height = 850
        canvas = tk.Canvas(win, width=canvas_width, height=canvas_height, bg=self.style.lookup("TFrame", "background"),
                   highlightthickness=0)
        canvas.pack(pady=1)

        cell_size = self.get_cell_size()
        map_pixel_size = self.map_size * cell_size
        offset_x = (canvas_width - map_pixel_size) // 2
        offset_y = 20

        def draw():
            canvas.delete("all")
            for y in range(self.map_size):
                for x in range(self.map_size):
                    cell = self.map_grid[y][x]
                    if not cell["discovered"]:
                        neighbors = [
                            (y + dy, x + dx)
                            for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                            if 0 <= y + dy < self.map_size and 0 <= x + dx < self.map_size
                        ]
                        if any(self.map_grid[ny][nx]["discovered"] for ny, nx in neighbors):
                            canvas.create_rectangle(
                                offset_x + x * cell_size,
                                offset_y + y * cell_size,
                                offset_x + (x + 1) * cell_size,
                                offset_y + (y + 1) * cell_size,
                                fill="#888888",
                                outline="yellow",
                                width=2
                            )
                            canvas.create_text(
                                offset_x + x * cell_size + cell_size // 2,
                                offset_y + y * cell_size + cell_size // 2,
                                text="?",
                                fill="white",
                                font=("Arial", 20, "bold")
                            )
                        continue

                    color = BASE_COLORS[cell["terrain"]]
                    canvas.create_rectangle(
                        offset_x + x * cell_size,
                        offset_y + y * cell_size,
                        offset_x + (x + 1) * cell_size,
                        offset_y + (y + 1) * cell_size,
                        fill=color,
                        outline="gray"
                    )

            self.draw_legend(canvas, offset_x, offset_y, cell_size)

        def click(event):
            x = (event.x - offset_x) // cell_size
            y = (event.y - offset_y) // cell_size
            if 0 <= x < self.map_size and 0 <= y < self.map_size:
                cell = self.map_grid[y][x]
                if not cell["discovered"]:
                    neighbors = [
                        (y + dy, x + dx)
                        for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                        if 0 <= y + dy < self.map_size and 0 <= x + dx < self.map_size
                    ]
                    if any(self.map_grid[ny][nx]["discovered"] for ny, nx in neighbors):

                        # ==== OBLICZ KOSZT I CZAS ====
                        days = random.randint(1, 3) + int(
                            math.hypot(y - self.settlement_pos[0], x - self.settlement_pos[1])
                        )
                        cost_food = 15
                        cost_wood = 10

                        # ==== OKNO POTWIERDZENIA ====
                        confirm = self.create_window("Potwierdź ekspedycję")

                        BG = self.style.lookup("TFrame", "background")

                        ttk.Label(
                            confirm,
                            text=f"Wyślij ekspedycję na pole ({y},{x})?",
                            font=self.top_title_font if hasattr(self, "top_title_font") else ("Cinzel", 14, "bold"),
                            background=BG
                        ).pack(pady=10)

                        ttk.Label(
                            confirm,
                            text=f"Czas wyprawy: {days} dni\nKoszt: 3 ludzie, {cost_food} żywności, {cost_wood} drewna",
                            justify="center",
                            font=self.top_info_font if hasattr(self, "top_info_font") else ("EB Garamond Italic", 12),
                            background=BG
                        ).pack(pady=5)

                        def do_explore():
                            if self.free_workers() < 3:
                                self.log("Za mało ludzi!", "red")
                                confirm.destroy()
                                return
                            if self.resources["żywność"] < cost_food or self.resources["drewno"] < cost_wood:
                                self.log("Za mało surowców!", "red")
                                confirm.destroy()
                                return

                            self.busy_people += 3
                            self.resources["żywność"] -= cost_food
                            self.resources["drewno"] -= cost_wood

                            end_date = self.current_date + timedelta(days=days)
                            self.expeditions.append((end_date, (y, x), "explore"))
                            self.log(
                                f"Eksploracja ({y},{x}): powrót {end_date.strftime('%d %b %Y')}",
                                "blue"
                            )
                            confirm.destroy()
                            win.destroy()

                        ttk.Button(confirm, text="Wyślij", command=do_explore).pack(side="left", padx=10, pady=10)
                        ttk.Button(confirm, text="Anuluj", command=confirm.destroy).pack(side="right", padx=10, pady=10)

        canvas.bind("<Button-1>", click)
        draw()
        ttk.Button(win, text="Anuluj", command=win.destroy).pack(pady=5)

        # wyśrodkuj okno eksploracji
        self.center_window(win)

    def finish_expedition(self, exp):
        self.busy_people -= 3
        y, x = exp[1]
        cell = self.map_grid[y][x]

        if exp[2] == "explore":
            cell["discovered"] = True
            res = cell["resource"] or "brak"
            self.log(f"Odkryto ({y},{x}): {cell['terrain']} | {res}", "gold")

            # ===== BONUS ZA EKSPLORACJĘ ZALEŻNY OD POLA =====
            terrain = cell["terrain"]

            # bonus eksploracyjny państwa (np. Hiszpania ma 'explore': 1.4)
            from constants import STATES
            explore_mult = STATES.get(self.state, {}).get("explore", 1.0)

            def scaled(amount):
                return max(1, int(amount * explore_mult))

            gains = []

            if terrain == "las":
                # trochę drewna i skór
                wood = scaled(50)
                skins = scaled(25)
                self.resources["drewno"] += wood
                self.resources["skóry"] += skins
                gains.append(f"drewno +{wood}")
                gains.append(f"skóry +{skins}")

            elif terrain == "pole":
                # zapasy żywności
                food = scaled(50)
                self.resources["żywność"] += food
                gains.append(f"żywność +{food}")

            elif terrain == "morze":
                # „ryby” jako żywność
                food = scaled(50)
                self.resources["żywność"] += food
                gains.append(f"żywność (ryby) +{food}")

            elif terrain == "wzniesienia":
                # jeśli jest surowiec kopalniany – trochę rudy
                ore_type = cell.get("resource")
                if ore_type:
                    ore_amt = scaled(50)
                    self.resources[ore_type] = self.resources.get(ore_type, 0) + ore_amt
                    gains.append(f"{ore_type} +{ore_amt}")
                else:
                    # jak nie ma konkretnego złoża, to coś symbolicznego
                    food = scaled(50)
                    self.resources["żywność"] += food
                    gains.append(f"żywność +{food}")

            else:
                # inne tereny – mały uniwersalny bonus
                food = scaled(50)
                self.resources["żywność"] += food
                gains.append(f"żywność +{food}")

            if gains:
                self.log(
                    "Eksploracja wróciła z łupami: " + ", ".join(gains),
                    "green"
                )


# ============== URUCHOMIENIE ==============
if __name__ == "__main__":
    root = tk.Tk()
    app = ColonySimulator(root)
    root.mainloop()
