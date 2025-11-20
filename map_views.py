# map_views.py
import math
import random
import tkinter as tk
from tkinter import ttk
from datetime import timedelta

from PIL import Image, ImageTk

from constants import BASE_COLORS, MINE_COLORS, MINE_RESOURCES, MINE_NAMES, BUILDINGS, STATES


class MapUIMixin:
    """
    Mixin odpowiedzialny za:
    - grafiki kafelków mapy (las, itp.)
    - rysowanie mapy budowy (show_map)
    - rysowanie mapy eksploracji (show_explore_map)
    """

    # ===== INICJALIZACJA GRAFIKI MAPY =====
    def init_map_graphics(self):
        """
        Wywołaj w __init__ klasy głównej po ustawieniu resource_path / stylu.
        """
        forest_path = self.resource_path("img/tiles/conifer_forest_inner.png")
        self.tile_forest_base = Image.open(forest_path)
        self.tile_forest_cache = {}  # cell_size -> ImageTk.PhotoImage

        plains_path = self.resource_path("img/tiles/plains.png")
        self.tile_plains_base = Image.open(plains_path)
        self.tile_plains_cache = {}  # cell_size -> ImageTk.PhotoImage

        mountains_path = self.resource_path("img/tiles/mountains_inner.png")
        self.tile_mountains_base = Image.open(mountains_path); self.tile_mountains_cache = {}

        sea_path = self.resource_path("img/tiles/ocean_inner.png")
        self.tile_sea_base = Image.open(sea_path); self.tile_sea_cache = {}

        # ikony surowców kopalnianych
        self.mine_icon_bases = {}
        self.mine_icon_cache = {}  # (key, size) -> ImageTk.PhotoImage
        for key, fname in {"coal": "coal.png", "iron": "iron.png", "silver": "silver.png", "gold": "gold.png"}.items():
            path = self.resource_path(f"img/tiles/{fname}")
            try:
                self.mine_icon_bases[key] = Image.open(path)
            except Exception:
                pass  # brak pliku = fallback na kolorowy kwadrat

        # miniaturki terenów (do legendy)
        self.terrain_icon_bases = {}  # nazwa terenu -> PIL.Image
        self.terrain_icon_cache = {}  # (terrain, size) -> ImageTk.PhotoImage
        for terrain, fname in {
            "las": "conifer_forest_inner.png",
            "pole": "plains.png",
            "wzniesienia": "mountains_inner.png",
            "morze": "ocean_inner.png",
        }.items():
            try:
                path = self.resource_path(f"img/tiles/{fname}")
                self.terrain_icon_bases[terrain] = Image.open(path)
            except Exception:
                pass  # jeśli nie ma pliku, zostanie prostokąt z BASE_COLORS

    def _mine_icon_key(self, res: str):
        """Mapuje nazwę surowca na klucz ikony (coal/iron/silver/gold)."""
        if not res: return None
        r = str(res).lower()
        if "węgiel" in r or "wegiel" in r or "coal" in r: return "coal"
        if "żelazo" in r or "zelazo" in r or "iron" in r: return "iron"
        if "srebro" in r or "silver" in r: return "silver"
        if "złoto" in r or "zloto" in r or "gold" in r: return "gold"
        if "las" in r or "las" in r or "forest" in r: return "forest"
        if "pole" in r or "pole" in r or "plains" in r: return "plains"
        if "wzgórze" in r or "wzgorze" in r or "mountains" in r: return "mountains"
        if "morze" in r or "morze" in r or "sea" in r: return "sea"
        return None

    def get_terrain_icon(self, terrain: str, cell_size: int):
        """Zwraca miniaturkę terenu do legendy albo None."""
        base = self.terrain_icon_bases.get(terrain)
        if not base: return None
        icon_size = max(18, min(32, int(cell_size * 0.6)))
        key = (terrain, icon_size)
        if key not in self.terrain_icon_cache:
            img = base.resize((icon_size, icon_size), Image.LANCZOS)
            self.terrain_icon_cache[key] = ImageTk.PhotoImage(img)
        return self.terrain_icon_cache[key]

    def get_mine_icon(self, res, cell_size: int):
        """Zwraca (PhotoImage, rozmiar) małej ikony surowca albo None jeśli brak."""
        key = self._mine_icon_key(res)
        if not key or key not in self.mine_icon_bases: return None
        icon_size = max(12, min(24, cell_size // 2))  # małe, ale czytelne
        cache_key = (key, icon_size)
        if cache_key not in self.mine_icon_cache:
            img = self.mine_icon_bases[key].resize((icon_size, icon_size), Image.LANCZOS)
            self.mine_icon_cache[cache_key] = ImageTk.PhotoImage(img)
        return self.mine_icon_cache[cache_key], icon_size

    def get_forest_tile(self, cell_size: int):
        """Zwraca kafelek lasu przeskalowany do aktualnego cell_size."""
        if cell_size not in self.tile_forest_cache:
            img = self.tile_forest_base.resize((cell_size, cell_size), Image.LANCZOS)
            self.tile_forest_cache[cell_size] = ImageTk.PhotoImage(img)
        return self.tile_forest_cache[cell_size]

    def get_plains_tile(self, cell_size: int):
        """Zwraca kafelek pola przeskalowany do aktualnego cell_size."""
        if cell_size not in self.tile_plains_cache:
            img = self.tile_plains_base.resize((cell_size, cell_size), Image.LANCZOS)
            self.tile_plains_cache[cell_size] = ImageTk.PhotoImage(img)
        return self.tile_plains_cache[cell_size]

    def get_mountains_tile(self, cell_size: int):
        """Zwraca kafelek wzgórz (wzniesienia) przeskalowany do aktualnego cell_size."""
        if cell_size not in self.tile_mountains_cache:
            img = self.tile_mountains_base.resize((cell_size, cell_size), Image.LANCZOS)
            self.tile_mountains_cache[cell_size] = ImageTk.PhotoImage(img)
        return self.tile_mountains_cache[cell_size]

    def get_sea_tile(self, cell_size: int):
        """Zwraca kafelek mórz przeskalowany do aktualnego cell_size."""
        if cell_size not in self.tile_sea_cache:
            img = self.tile_sea_base.resize((cell_size, cell_size), Image.LANCZOS)
            self.tile_sea_cache[cell_size] = ImageTk.PhotoImage(img)
        return self.tile_sea_cache[cell_size]

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

    # ===== LEGENDA =====
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
            icon = self.get_terrain_icon(name, cell_size)
            if icon:
                canvas.create_image(x, terrain_y, image=icon)
            else:
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
            icon = self.get_mine_icon(res, cell_size)
            if icon:
                img, icon_size = icon
                canvas.create_image(x, mine_y, image=img)
            else:
                color = MINE_COLORS[res]
                canvas.create_rectangle(x - 10, mine_y - 10, x + 10, mine_y + 10, fill=color, outline="black")
            canvas.create_text(x, mine_y + 22, text=MINE_NAMES[res], anchor="center", font=("Arial", 10))

    # ===== MAPA BUDOWANIA =====
    def show_map(self):

        win = self.create_window(f"Buduj - wybierz pole")

        canvas_width = 850
        canvas_height = 850
        canvas = tk.Canvas(
            win,
            width=canvas_width,
            height=canvas_height,
            bg=self.style.lookup("TFrame", "background"),
            highlightthickness=0,
        )
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
                            outline="gray",
                        )
                        continue

                    color = BASE_COLORS[cell["terrain"]]
                    outline = "gray"
                    width = 1
                    if cell["terrain"] in ["osada", "dzielnica"]:
                        outline = "yellow"
                        width = 3

                    # tło (np. ramka osady / dzielnicy)
                    canvas.create_rectangle(
                        offset_x + x * cell_size,
                        offset_y + y * cell_size,
                        offset_x + (x + 1) * cell_size,
                        offset_y + (y + 1) * cell_size,
                        fill=color,
                        outline=outline,
                        width=width,
                    )

                    # jeśli to las / pole / wzniesienia – nad prostokątem kładziemy teksturę
                    if cell["terrain"] == "las":
                        img = self.get_forest_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)
                    elif cell["terrain"] == "pole":
                        img = self.get_plains_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)
                    elif cell["terrain"] == "wzniesienia":
                        img = self.get_mountains_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)
                    elif cell["terrain"] == "morze":
                        img = self.get_sea_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)

                    # budynek w budowie
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
                            font=("Arial", 9, "bold"),
                        )

                    # opis osady / dzielnicy
                    if cell["terrain"] in ["osada", "dzielnica"]:
                        buildings_here = [b for b in cell["building"] if not b.get("is_district", False)]
                        used = len(buildings_here)
                        canvas.create_text(
                            offset_x + x * cell_size + cell_size // 2,
                            offset_y + y * cell_size + cell_size // 2 - 20,
                            text=f"{cell['terrain'].capitalize()}",
                            fill="white",
                            font=("Arial", 9, "bold"),
                        )
                        canvas.create_text(
                            offset_x + x * cell_size + cell_size // 2,
                            offset_y + y * cell_size + cell_size // 2,
                            text=f"{used}/5",
                            fill="yellow",
                            font=("Arial", 10, "bold"),
                        )

                    # złoża na wzniesieniach – mała ikonka węgla/żelaza/srebra/złota
                    if cell["terrain"] == "wzniesienia" and cell["resource"]:
                        icon = self.get_mine_icon(cell["resource"], cell_size)
                        if icon:
                            img, icon_size = icon
                            cx = offset_x + x * cell_size + cell_size - 5 - icon_size // 2
                            cy = offset_y + y * cell_size + cell_size - 5 - icon_size // 2
                            canvas.create_image(cx, cy, image=img)
                        else:
                            rc = MINE_COLORS[cell["resource"]]
                            canvas.create_rectangle(
                                offset_x + x * cell_size + cell_size - 20,
                                offset_y + y * cell_size + cell_size - 20,
                                offset_x + x * cell_size + cell_size - 5,
                                offset_y + y * cell_size + cell_size - 5,
                                fill=rc,
                                outline="black",
                            )

                    # zielone podświetlenia, gdzie można budować
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
                            width=3,
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

    # ===== MAPA EKSPLORACJI =====
    def show_explore_map(self):

        win = self.create_window(f"Eksploracja")

        # === INFORMACJE O KOSZTACH ===
        info_frame = ttk.Frame(win)
        info_frame.pack(pady=5)

        ttk.Label(
            info_frame,
            text="Koszt eksploracji:",
            font=("Arial", 12, "bold"),
        ).pack()

        ttk.Label(
            info_frame,
            text="• 3 ludzie • 15 żywności • 10 drewna",
            justify="center",
            font=("Arial", 10),
        ).pack()

        canvas_width = 850
        canvas_height = 850
        canvas = tk.Canvas(
            win,
            width=canvas_width,
            height=canvas_height,
            bg=self.style.lookup("TFrame", "background"),
            highlightthickness=0,
        )
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
                                width=2,
                            )
                            canvas.create_text(
                                offset_x + x * cell_size + cell_size // 2,
                                offset_y + y * cell_size + cell_size // 2,
                                text="?",
                                fill="white",
                                font=("Arial", 20, "bold"),
                            )
                        continue

                    color = BASE_COLORS[cell["terrain"]]
                    canvas.create_rectangle(
                        offset_x + x * cell_size,
                        offset_y + y * cell_size,
                        offset_x + (x + 1) * cell_size,
                        offset_y + (y + 1) * cell_size,
                        fill=color,
                        outline="gray",
                    )

                    if cell["terrain"] == "las":
                        img = self.get_forest_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)
                    elif cell["terrain"] == "pole":
                        img = self.get_plains_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)
                    elif cell["terrain"] == "wzniesienia":
                        img = self.get_mountains_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)
                    elif cell["terrain"] == "morze":
                        img = self.get_sea_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)

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

                        bg = self.style.lookup("TFrame", "background")

                        ttk.Label(
                            confirm,
                            text=f"Wyślij ekspedycję na pole ({y},{x})?",
                            font=getattr(self, "top_title_font", ("Cinzel", 14, "bold")),
                            background=bg,
                        ).pack(pady=10)

                        ttk.Label(
                            confirm,
                            text=(
                                f"Czas wyprawy: {days} dni\n"
                                f"Koszt: 3 ludzie, {cost_food} żywności, {cost_wood} drewna"
                            ),
                            justify="center",
                            font=getattr(self, "top_info_font", ("EB Garamond Italic", 12)),
                            background=bg,
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
                                "blue",
                            )
                            confirm.destroy()
                            win.destroy()

                        ttk.Button(confirm, text="Wyślij", command=do_explore).pack(
                            side="left", padx=10, pady=10
                        )
                        ttk.Button(confirm, text="Anuluj", command=confirm.destroy).pack(
                            side="right", padx=10, pady=10
                        )

        canvas.bind("<Button-1>", click)
        draw()
        ttk.Button(win, text="Anuluj", command=win.destroy).pack(pady=5)

        # wyśrodkuj okno eksploracji
        self.center_window(win)
