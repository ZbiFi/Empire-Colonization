# map_views.py
import math
import os, re
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

    def init_ocean_tiles(self):
        """Ładuje wszystkie pliki oceanu i rozbija ich nazwy na krawędzie/narożniki."""
        self.ocean_base_path = self.resource_path("img/tiles/ocean")
        self.ocean_tile_cache = {}   # (filename, cell_size) -> ImageTk.PhotoImage
        self.ocean_defs = []         # lista: {filename, card, inner, outer}

        if not os.path.isdir(self.ocean_base_path):
            return

        for fname in os.listdir(self.ocean_base_path):
            if not fname.endswith(".png"):
                continue
            base = fname.split(".")[0]  # np. ocean_northwest_southwest_outer_1
            parts = base.rsplit("_", 1)
            base_no_idx = parts[0] if parts[-1].isdigit() else base
            card, inner, outer = self._parse_ocean_name(base_no_idx)
            self.ocean_defs.append({
                "filename": fname,
                "card": card,
                "inner": inner,
                "outer": outer,
            })

        # na wszelki wypadek – mieć chociaż ocean_inner
        if not self.ocean_defs:
            self.ocean_defs.append({
                "filename": "ocean_inner.png",
                "card": set(),
                "inner": set(),
                "outer": set(),
            })

    def _parse_ocean_name(self, base_name: str):
        """
        base_name np. 'ocean_northwest_southwest_outer_southeast_inner'
        Zwraca (card, inner, outer):
        - card: {'N','E','S','W'}
        - inner/outer: {'NE','SE','SW','NW'}
        """
        s = base_name.replace("ocean_", "")
        card, inner, outer = set(), set(), set()

        tokens = s.split("_")
        pending_diags = []
        diag_map = {"northeast": "NE", "southeast": "SE", "southwest": "SW", "northwest": "NW"}

        for t in tokens:
            if t == "north_south":
                card.update(["N", "S"])
            elif t == "west_east":
                card.update(["W", "E"])
            elif t in ("north", "east", "south", "west"):
                card.add({"north": "N", "east": "E", "south": "S", "west": "W"}[t])
            elif t in diag_map:
                # zapamiętujemy diagonale aż do napotkania 'inner'/'outer'
                pending_diags.append(diag_map[t])
            elif t in ("inner", "outer"):
                # wszystkie zebrane diagonale traktujemy jako inner/outer
                for d in pending_diags:
                    if t == "inner":
                        inner.add(d)
                    else:
                        outer.add(d)
                pending_diags = []
            else:
                # ignorujemy inne tokeny
                pass

        return card, inner, outer

    def _describe_ocean_neighbors(self, neigh):
        """
        Na podstawie sąsiadów wyznacza:
        - card_req: krawędzie z lądem (N/E/S/W)
        - inner_req: wewnętrzne rogi (zatoki)
        - outer_req: na razie nie używane (zawsze puste),
                     zostawione dla kompatybilności z API.
        """
        N, NE, E, SE, S, SW, W, NW = (neigh[k] for k in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"])

        # krawędzie – po prostu gdzie jest ląd
        card_req = set()
        if N: card_req.add("N")
        if E: card_req.add("E")
        if S: card_req.add("S")
        if W: card_req.add("W")

        inner_req = set()
        outer_req = set()  # nie wyciągamy już outer z sąsiadów

        # wewnętrzne rogi – ląd po skosie, woda na bokach
        if NE and not N and not E:
            inner_req.add("NE")
        if SE and not S and not E:
            inner_req.add("SE")
        if SW and not S and not W:
            inner_req.add("SW")
        if NW and not N and not W:
            inner_req.add("NW")

        return card_req, inner_req, outer_req

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

    def _is_land(self, y, x):
        """True, jeśli to NIE jest morze (czyli ląd/brzeg)."""
        if 0 <= y < self.map_size and 0 <= x < self.map_size:
            return self.map_grid[y][x]["terrain"] != "morze"
        return False

    def pick_ocean_tile_name(self, neigh):
        """
        Wybiera NAJLEPIEJ pasujący kafelek oceanu biorąc pod uwagę
        wszystkich 8 sąsiadów (N, NE, E, SE, S, SW, W, NW).

        Zasady:
        - OUTER w nazwie kafla traktujemy jak normalne krawędzie:
          NE -> N+E, SE -> S+E, SW -> S+W, NW -> N+W
        - najpierw szukamy kafli z idealnie takim samym zestawem krawędzi
          i innerów jak wymagane,
        - potem supersety,
        - na końcu heurystyczny scoring.
        """
        if not hasattr(self, "ocean_defs") or not self.ocean_defs:
            self.init_ocean_tiles()

        if not self.ocean_defs:
            return "ocean_inner.png"

        card_req, inner_req, _ = self._describe_ocean_neighbors(neigh)

        # jeśli wszędzie woda – szukamy po prostu ocean_inner
        if not any(neigh.values()):
            for d in self.ocean_defs:
                if not d["card"] and not d["inner"] and not d["outer"]:
                    return d["filename"]
            return "ocean_inner.png"

        # pomocnicza funkcja: efektywne krawędzie kafla (card + outer→krawędzie)
        def effective_edges(d):
            edges = set(d["card"])
            for diag in d["outer"]:
                if diag == "NE":
                    edges.update(("N", "E"))
                elif diag == "SE":
                    edges.update(("S", "E"))
                elif diag == "SW":
                    edges.update(("S", "W"))
                elif diag == "NW":
                    edges.update(("N", "W"))
            return edges

        # --- 1. Perfekcyjne dopasowanie ---
        perfect = []
        for d in self.ocean_defs:
            edges = effective_edges(d)
            if edges == card_req and d["inner"] == inner_req:
                perfect.append(d)

        if perfect:
            return random.choice(perfect)["filename"]

        # --- 2. Supersety: kafle zawierające wszystkie wymagane krawędzie/innery ---
        superset = []
        for d in self.ocean_defs:
            edges = effective_edges(d)
            if card_req <= edges and inner_req <= d["inner"]:
                superset.append((d, edges))

        if superset:
            def extra_cost(item):
                d, edges = item
                return len(edges - card_req) + len(d["inner"] - inner_req)

            best_d, _ = min(superset, key=extra_cost)
            return best_d["filename"]

        # --- 3. Fallback: scoring heurystyczny ---
        best_name = "ocean_inner.png"
        best_score = -10**9

        for d in self.ocean_defs:
            edges = effective_edges(d)
            inner = d["inner"]
            outer = d["outer"]

            edge_match = len(card_req & edges)
            edge_missing = len(card_req - edges)
            edge_extra = len(edges - card_req)

            inner_match = len(inner_req & inner)
            inner_missing = len(inner_req - inner)
            inner_extra = len(inner - inner_req)

            score = 0
            # krawędzie są najważniejsze
            score += 20 * edge_match - 40 * edge_missing - 10 * edge_extra
            # zatoki – mniej ważne, ale nadal istotne
            score += 10 * inner_match - 15 * inner_missing - 5 * inner_extra

            # heurystyka dla przekątnych: jeśli jest ląd na diagonali,
            # to lekko premiujemy kafle z inner/outer w tym miejscu
            for diag in ("NE", "SE", "SW", "NW"):
                if neigh[diag]:
                    if diag in inner or diag in outer:
                        score += 3
                else:
                    if diag in inner or diag in outer:
                        score -= 2

            # delikatna kara za zbyt skomplikowane kafle
            complexity = len(edges) + len(inner) + len(outer)
            score -= 0.1 * complexity

            if score > best_score:
                best_score = score
                best_name = d["filename"]

        return best_name

    def get_ocean_neighbors(self, y, x):
        """Zwraca słownik booli: czy w danym kierunku jest ląd."""
        n = self._is_land(y - 1, x)
        ne = self._is_land(y - 1, x + 1)
        e = self._is_land(y, x + 1)
        se = self._is_land(y + 1, x + 1)
        s = self._is_land(y + 1, x)
        sw = self._is_land(y + 1, x - 1)
        w = self._is_land(y, x - 1)
        nw = self._is_land(y - 1, x - 1)
        return {"N": n, "NE": ne, "E": e, "SE": se, "S": s, "SW": sw, "W": w, "NW": nw}

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

    def get_ocean_tile_image(self, y, x, cell_size):
        """
        Zwraca ImageTk.PhotoImage z odpowiednim kaflem oceanu dla pola (y,x).
        """
        neigh = self.get_ocean_neighbors(y, x)
        filename = self.pick_ocean_tile_name(neigh)  # np. 'ocean_northwest_southwest_outer_1.png'

        print(f"({y},{x}) neigh={neigh} -> {filename}")
        key = (filename, cell_size)
        if key in self.ocean_tile_cache:
            return self.ocean_tile_cache[key]

        path = os.path.join(self.ocean_base_path, filename)
        try:
            img = Image.open(path).resize((cell_size, cell_size), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self.ocean_tile_cache[key] = tk_img
            return tk_img
        except Exception:
            # fallback: spróbuj ocean_inner, a jak nie ma – None
            try:
                inner_path = os.path.join(self.ocean_base_path, "ocean_inner.png")
                img = Image.open(inner_path).resize((cell_size, cell_size), Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                self.ocean_tile_cache[("ocean_inner.png", cell_size)] = tk_img
                return tk_img
            except Exception:
                return None

    # ===== MAPA BUDOWANIA =====
    def show_map(self):

        win = self.create_window("Buduj - wybierz pole")

        canvas_width = 850
        canvas_height = 850
        canvas = tk.Canvas(win, width=canvas_width, height=canvas_height, bg=self.style.lookup("TFrame", "background"), highlightthickness=0)
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

                    # nieodkryte pola
                    if not cell["discovered"]:
                        canvas.create_rectangle(offset_x + x * cell_size, offset_y + y * cell_size, offset_x + (x + 1) * cell_size, offset_y + (y + 1) * cell_size, fill="#888888", outline="gray")
                        continue

                    terrain = cell["terrain"]

                    # specjalna obsługa morza – najpierw tło lądu, potem kafel oceanu
                    if terrain == "morze":
                        # 1) tło pod przezroczystościami (np. plains)
                        try:
                            bg_img = self.get_plains_tile(cell_size)
                            canvas.create_image(
                                offset_x + x * cell_size,
                                offset_y + y * cell_size,
                                anchor="nw",
                                image=bg_img
                            )
                        except Exception:
                            # fallback: jednolity "grunt"
                            ground = BASE_COLORS.get("pole", "#7a6b4a")
                            canvas.create_rectangle(
                                offset_x + x * cell_size,
                                offset_y + y * cell_size,
                                offset_x + (x + 1) * cell_size,
                                offset_y + (y + 1) * cell_size,
                                fill=ground,
                                outline="gray",
                                width=1
                            )

                        # 2) kafelek oceanu z autotilingu – na wierzch
                        img = self.get_ocean_tile_image(y, x, cell_size)
                        if img:
                            canvas.create_image(
                                offset_x + x * cell_size,
                                offset_y + y * cell_size,
                                anchor="nw",
                                image=img
                            )
                        else:
                            # absolutny fallback – pełny prostokąt wody
                            color = BASE_COLORS["morze"]
                            canvas.create_rectangle(
                                offset_x + x * cell_size,
                                offset_y + y * cell_size,
                                offset_x + (x + 1) * cell_size,
                                offset_y + (y + 1) * cell_size,
                                fill=color,
                                outline="gray",
                                width=1
                            )
                        continue

                    color = BASE_COLORS[terrain]
                    outline = "gray"
                    width = 1
                    if terrain in ["osada", "dzielnica"]:
                        outline = "yellow"
                        width = 3

                    # tło (np. ramka osady / dzielnicy)
                    canvas.create_rectangle(offset_x + x * cell_size, offset_y + y * cell_size, offset_x + (x + 1) * cell_size, offset_y + (y + 1) * cell_size, fill=color, outline=outline, width=width)

                    # tekstury lasu / pola / wzniesień
                    if terrain == "las":
                        img = self.get_forest_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)
                    elif terrain == "pole":
                        img = self.get_plains_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)
                    elif terrain == "wzniesienia":
                        img = self.get_mountains_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)

                    # budynek w budowie – procent postępu
                    building_in_progress = next((c for c in self.constructions if c[1]["pos"] == (y, x)), None)
                    if building_in_progress:
                        end, _, _, start = building_in_progress
                        total_days = (end - start).days
                        elapsed = (self.current_date - start).days
                        pct = min(100, max(0, int(elapsed / total_days * 100))) if total_days > 0 else 0
                        canvas.create_text(offset_x + x * cell_size + cell_size // 2, offset_y + y * cell_size + cell_size // 2 + 20, text=f"{pct}%", fill="white", font=("Arial", 9, "bold"))

                    # opis osady / dzielnicy
                    if terrain in ["osada", "dzielnica"]:
                        buildings_here = [b for b in cell["building"] if not b.get("is_district", False)]
                        used = len(buildings_here)
                        canvas.create_text(offset_x + x * cell_size + cell_size // 2, offset_y + y * cell_size + cell_size // 2 - 20, text=f"{terrain.capitalize()}", fill="white", font=("Arial", 9, "bold"))
                        canvas.create_text(offset_x + x * cell_size + cell_size // 2, offset_y + y * cell_size + cell_size // 2, text=f"{used}/5", fill="yellow", font=("Arial", 10, "bold"))

                    # złoża na wzniesieniach – ikonki surowców
                    if terrain == "wzniesienia" and cell["resource"]:
                        icon = self.get_mine_icon(cell["resource"], cell_size)
                        if icon:
                            img_icon, icon_size = icon
                            cx = offset_x + x * cell_size + cell_size - 5 - icon_size // 2
                            cy = offset_y + y * cell_size + cell_size - 5 - icon_size // 2
                            canvas.create_image(cx, cy, image=img_icon)
                        else:
                            rc = MINE_COLORS[cell["resource"]]
                            canvas.create_rectangle(offset_x + x * cell_size + cell_size - 20, offset_y + y * cell_size + cell_size - 20, offset_x + x * cell_size + cell_size - 5, offset_y + y * cell_size + cell_size - 5, fill=rc, outline="black")

                    # zielone podświetlenia, gdzie można budować
                    if self.selected_building:
                        data = BUILDINGS[self.selected_building]

                        if terrain not in data.get("allowed_terrain", []):
                            continue

                        if not data.get("requires_settlement"):
                            if cell["building"] or any(c[1]["pos"] == (y, x) for c in self.constructions):
                                continue

                        if data.get("requires_settlement"):
                            if terrain not in ["osada", "dzielnica"]:
                                continue
                            used = len([b for b in cell["building"] if not b.get("is_district", False)])
                            in_progress = len([c for c in self.constructions if c[1]["pos"] == (y, x)])
                            if used + in_progress >= 5:
                                continue

                        if data.get("requires_adjacent_settlement"):
                            if not self.is_adjacent_to_settlement((y, x)):
                                continue
                            if terrain == "morze" and self.selected_building != "przystań":
                                continue

                        canvas.create_rectangle(offset_x + x * cell_size, offset_y + y * cell_size, offset_x + (x + 1) * cell_size, offset_y + (y + 1) * cell_size, outline="lime", width=3)

            self.draw_legend(canvas, offset_x, offset_y, cell_size)

        def click(event):
            x = (event.x - offset_x) // cell_size
            y = (event.y - offset_y) // cell_size
            if 0 <= x < self.map_size and 0 <= y < self.map_size and self.map_grid[y][x]["discovered"]:
                if self.selected_building:
                    self.start_construction_at(self.selected_building, (y, x))
                    self.selected_building = None
                    win.destroy()

        canvas.bind("<Button-1>", click)
        draw()
        ttk.Button(win, text="Anuluj", command=win.destroy).pack(pady=5)

        self.center_window(win)

    # ===== MAPA EKSPLORACJI =====
    def show_explore_map(self):

        win = self.create_window("Eksploracja")

        # informacje o kosztach
        info_frame = ttk.Frame(win)
        info_frame.pack(pady=5)

        ttk.Label(info_frame, text="Koszt eksploracji:", font=("Arial", 12, "bold")).pack()
        ttk.Label(info_frame, text="• 3 ludzie • 15 żywności • 10 drewna", justify="center", font=("Arial", 10)).pack()

        canvas_width = 850
        canvas_height = 850
        canvas = tk.Canvas(win, width=canvas_width, height=canvas_height, bg=self.style.lookup("TFrame", "background"), highlightthickness=0)
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

                    # nieodkryte pola, ale sąsiadujące z odkrytymi – potencjalne cele eksploracji
                    if not cell["discovered"]:
                        neighbors = [(y + dy, x + dx) for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)] if 0 <= y + dy < self.map_size and 0 <= x + dx < self.map_size]
                        if any(self.map_grid[ny][nx]["discovered"] for ny, nx in neighbors):
                            canvas.create_rectangle(offset_x + x * cell_size, offset_y + y * cell_size, offset_x + (x + 1) * cell_size, offset_y + (y + 1) * cell_size, fill="#888888", outline="yellow", width=2)
                            canvas.create_text(offset_x + x * cell_size + cell_size // 2, offset_y + y * cell_size + cell_size // 2, text="?", fill="white", font=("Arial", 20, "bold"))
                        continue

                    terrain = cell["terrain"]

                    if terrain == "morze":
                        # tło lądu pod przezroczystymi fragmentami
                        try:
                            bg_img = self.get_plains_tile(cell_size)
                            canvas.create_image(
                                offset_x + x * cell_size,
                                offset_y + y * cell_size,
                                anchor="nw",
                                image=bg_img
                            )
                        except Exception:
                            ground = BASE_COLORS.get("pole", "#7a6b4a")
                            canvas.create_rectangle(
                                offset_x + x * cell_size,
                                offset_y + y * cell_size,
                                offset_x + (x + 1) * cell_size,
                                offset_y + (y + 1) * cell_size,
                                fill=ground,
                                outline="gray"
                            )

                        img = self.get_ocean_tile_image(y, x, cell_size)
                        if img:
                            canvas.create_image(
                                offset_x + x * cell_size,
                                offset_y + y * cell_size,
                                anchor="nw",
                                image=img
                            )
                        else:
                            color = BASE_COLORS["morze"]
                            canvas.create_rectangle(
                                offset_x + x * cell_size,
                                offset_y + y * cell_size,
                                offset_x + (x + 1) * cell_size,
                                offset_y + (y + 1) * cell_size,
                                fill=color,
                                outline="gray"
                            )
                        continue

                    color = BASE_COLORS[terrain]
                    canvas.create_rectangle(offset_x + x * cell_size, offset_y + y * cell_size, offset_x + (x + 1) * cell_size, offset_y + (y + 1) * cell_size, fill=color, outline="gray")

                    # tekstury terenów
                    if terrain == "las":
                        img = self.get_forest_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)
                    elif terrain == "pole":
                        img = self.get_plains_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)
                    elif terrain == "wzniesienia":
                        img = self.get_mountains_tile(cell_size)
                        canvas.create_image(offset_x + x * cell_size, offset_y + y * cell_size, anchor="nw", image=img)

                    # opcjonalnie – ikona złoża również na mapie eksploracji
                    if terrain == "wzniesienia" and cell["resource"]:
                        icon = self.get_mine_icon(cell["resource"], cell_size)
                        if icon:
                            img_icon, icon_size = icon
                            cx = offset_x + x * cell_size + cell_size - 5 - icon_size // 2
                            cy = offset_y + y * cell_size + cell_size - 5 - icon_size // 2
                            canvas.create_image(cx, cy, image=img_icon)

            self.draw_legend(canvas, offset_x, offset_y, cell_size)

        def click(event):
            x = (event.x - offset_x) // cell_size
            y = (event.y - offset_y) // cell_size
            if not (0 <= x < self.map_size and 0 <= y < self.map_size):
                return

            cell = self.map_grid[y][x]
            if cell["discovered"]:
                return

            neighbors = [(y + dy, x + dx) for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)] if 0 <= y + dy < self.map_size and 0 <= x + dx < self.map_size]
            if not any(self.map_grid[ny][nx]["discovered"] for ny, nx in neighbors):
                return

            # koszt i czas wyprawy
            days = random.randint(1, 3) + int(math.hypot(y - self.settlement_pos[0], x - self.settlement_pos[1]))
            cost_food = 15
            cost_wood = 10

            confirm = self.create_window("Potwierdź ekspedycję")
            bg = self.style.lookup("TFrame", "background")

            ttk.Label(confirm, text=f"Wyślij ekspedycję na pole ({y},{x})?", font=getattr(self, "top_title_font", ("Cinzel", 14, "bold")), background=bg).pack(pady=10)
            ttk.Label(confirm, text=f"Czas wyprawy: {days} dni\nKoszt: 3 ludzie, {cost_food} żywności, {cost_wood} drewna", justify="center", font=getattr(self, "top_info_font", ("EB Garamond Italic", 12)), background=bg).pack(pady=5)

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
                self.log(f"Eksploracja ({y},{x}): powrót {end_date.strftime('%d %b %Y')}", "blue")
                confirm.destroy()
                win.destroy()

            ttk.Button(confirm, text="Wyślij", command=do_explore).pack(side="left", padx=10, pady=10)
            ttk.Button(confirm, text="Anuluj", command=confirm.destroy).pack(side="right", padx=10, pady=10)

        canvas.bind("<Button-1>", click)
        draw()
        ttk.Button(win, text="Anuluj", command=win.destroy).pack(pady=5)

        self.center_window(win)

