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

        # Seed do deterministycznego wyboru wariantów _1/_2/_3
        # Jeśli ustawisz self.tile_random_seed wcześniej (np. z save),
        # to ta linia go nie nadpisze.
        if not hasattr(self, "tile_random_seed"):
            self.tile_random_seed = random.randint(0, 2**31 - 1)

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

        # ikona budynku
        try:
            path = self.resource_path(f"img/tiles/building.png")
            self.building_icon_base = Image.open(path)
            self.building_icon_cache = {}  # size -> ImageTk.PhotoImage
        except Exception:
            self.building_icon_base = None
            self.building_icon_cache = {}

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

        # --- ikona osady/dzielnicy (camp.png) ---
        try:
            camp_path = self.resource_path("img/tiles/camp.png")
            self.camp_icon_base = Image.open(camp_path).convert("RGBA")
        except Exception:
            self.camp_icon_base = None
        self.camp_icon_cache = {}  # (size, small) -> ImageTk.PhotoImage

        # camp jako terrain-icon-base (żeby legenda działała bez wyjątków)
        if not hasattr(self, "terrain_icon_bases"):
            self.terrain_icon_bases = {}
        if self.camp_icon_base:
            self.terrain_icon_bases["osada"] = self.camp_icon_base
            self.terrain_icon_bases["dzielnica"] = self.camp_icon_base

    def get_building_icon(self, cell_size: int):
        """
        Zwraca (PhotoImage, rozmiar) ikony budynku, przeskalowanej do 1/4 kafla,
        albo None jeśli nie ma grafiki.
        """
        if not getattr(self, "building_icon_base", None):
            return None

        size = max(8, cell_size // 2)
        key = size

        if key not in self.building_icon_cache:
            img = self.building_icon_base.resize((size, size), Image.LANCZOS)
            self.building_icon_cache[key] = ImageTk.PhotoImage(img)

        return self.building_icon_cache[key], size

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

    def get_camp_icon(self, cell_size: int, small: bool = False):
        """Zwraca przeskalowaną ikonę camp.png dla osady/dzielnicy albo None."""
        if not getattr(self, "camp_icon_base", None):
            return None

        size = max(8, cell_size * 3 // 4 if small else cell_size)
        key = (size, small)

        if key not in self.camp_icon_cache:
            img = self.camp_icon_base.resize((size, size), Image.LANCZOS)
            self.camp_icon_cache[key] = ImageTk.PhotoImage(img)

        return self.camp_icon_cache[key], size

    def init_ocean_tiles(self):
        """Ładuje wszystkie pliki oceanu i rozbija ich nazwy na krawędzie/narożniki."""
        self.ocean_base_path = self.resource_path("img/tiles/ocean")
        self.ocean_tile_cache = {}   # (filename, cell_size) -> ImageTk.PhotoImage
        self.ocean_defs = []         # lista: {filename, card, inner, outer}
        self.ocean_tile_assignments = {}  # (y, x) -> filename (na przyszłość, jeśli chcesz je utrwalać)

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

    def init_forest_tiles(self):
        """Ładuje wszystkie pliki lasu i rozbija ich nazwy na krawędzie/narożniki."""
        self.forest_base_path = self.resource_path("img/tiles/forest")
        self.forest_tile_cache = {}  # (filename, cell_size) -> ImageTk.PhotoImage
        self.forest_defs = []  # lista: {filename, card, inner, outer}

        if not os.path.isdir(self.forest_base_path):
            return

        for fname in os.listdir(self.forest_base_path):
            if not fname.endswith(".png"):
                continue
            base = fname.split(".")[0]  # np. forest_north_south_1
            parts = base.rsplit("_", 1)
            base_no_idx = parts[0] if parts[-1].isdigit() else base

            # podmieniamy prefix forest_ -> ocean_, żeby użyć tego samego parsera
            norm = base_no_idx.replace("forest_", "ocean_")
            card, inner, outer = self._parse_ocean_name(norm)
            self.forest_defs.append({
                "filename": fname,
                "card": card,
                "inner": inner,
                "outer": outer,
            })

        if not self.forest_defs:
            # awaryjnie, żeby coś było
            self.forest_defs.append({
                "filename": "forest_inner.png",
                "card": set(),
                "inner": set(),
                "outer": set(),
            })

    def init_mountains_tiles(self):
        """Ładuje wszystkie pliki wzgórz i rozbija ich nazwy na krawędzie/narożniki."""
        self.mountains_base_path = self.resource_path("img/tiles/mountains")
        self.mountains_tile_cache = {}  # (filename, cell_size) -> ImageTk.PhotoImage
        self.mountains_defs = []  # lista: {filename, card, inner, outer}

        if not os.path.isdir(self.mountains_base_path):
            return

        for fname in os.listdir(self.mountains_base_path):
            if not fname.endswith(".png"):
                continue
            base = fname.split(".")[0]  # np. mountains_north_south_1
            parts = base.rsplit("_", 1)
            base_no_idx = parts[0] if parts[-1].isdigit() else base

            norm = base_no_idx.replace("mountains_", "ocean_")
            card, inner, outer = self._parse_ocean_name(norm)
            self.mountains_defs.append({
                "filename": fname,
                "card": card,
                "inner": inner,
                "outer": outer,
            })

        if not self.mountains_defs:
            self.mountains_defs.append({
                "filename": "mountains_inner.png",
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

    def _variant_group_key(self, filename: str) -> str:
        """
        Zwraca klucz grupy wariantów dla pliku:
        'ocean_north_1.png' -> 'ocean_north'
        'ocean_inner.png'   -> 'ocean_inner'
        """
        name = filename
        if name.lower().endswith(".png"):
            name = name[:-4]
        parts = name.rsplit("_", 1)
        if len(parts) == 2 and parts[1].isdigit():
            return parts[0]
        return name

    def _choose_tile_variant(self, base_filename: str, defs, terrain_tag: str, y: int, x: int) -> str:
        """
        Dla danego bazowego pliku (np. 'ocean_north_1.png') wybiera DETERMINISTYCZNIE
        jeden z wariantów tej samej grupy (_1/_2/_3) na podstawie:
        - self.tile_random_seed
        - terrain_tag (np. 'ocean')
        - grupy (np. 'ocean_north')
        - współrzędnych (y, x)
        """
        group_key = self._variant_group_key(base_filename)

        # znajdź wszystkie pliki z tej samej grupy
        variants = []
        for d in defs:
            fname = d["filename"]
            if self._variant_group_key(fname) == group_key:
                variants.append(fname)

        # jeśli nic nie znaleźliśmy, albo jest tylko jeden wariant – zwróć to co było
        if not variants:
            return base_filename
        if len(variants) == 1:
            return variants[0]

        variants = sorted(variants)  # stała kolejność

        # prosty deterministyczny "hash"
        seed = int(getattr(self, "tile_random_seed", 0)) & 0xFFFFFFFF
        key_str = f"{terrain_tag}:{group_key}:{y}:{x}"

        h = seed
        for ch in key_str:
            h = (h * 131 + ord(ch)) & 0xFFFFFFFF

        idx = h % len(variants)
        return variants[idx]

    def _pick_tile_from_defs(self, neigh, defs, empty_filename: str):
        """
        Ogólna logika dobierania kafelka (dla oceanu / lasu / wzgórz).
        - neigh: dict N/NE/.. -> bool (czy tam jest 'ląd' względem danego terenu)
        - defs: lista {filename, card, inner, outer}
        - empty_filename: nazwa 'pustego' tilesa (inner) na wypadek braku dopasowania
        """
        if not defs:
            return empty_filename

        card_req, inner_req, _ = self._describe_ocean_neighbors(neigh)

        # jeśli wszędzie "morze" / "las" / "góry" (czyli brak krawędzi) – szukamy czystego tilesa
        if not any(neigh.values()):
            for d in defs:
                if not d["card"] and not d["inner"] and not d["outer"]:
                    return d["filename"]
            return empty_filename

        # outer traktujemy jak dodatkowe krawędzie (NE => N+E itd.)
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
        for d in defs:
            edges = effective_edges(d)
            if edges == card_req and d["inner"] == inner_req:
                perfect.append(d)

        if perfect:
            return random.choice(perfect)["filename"]

        # --- 2. Supersety (kafel ma wszystko co trzeba + może coś ekstra) ---
        superset = []
        for d in defs:
            edges = effective_edges(d)
            if card_req <= edges and inner_req <= d["inner"]:
                superset.append((d, edges))

        if superset:
            def extra_cost(item):
                d, edges = item
                return len(edges - card_req) + len(d["inner"] - inner_req)

            best_d, _ = min(superset, key=extra_cost)
            return best_d["filename"]

        # --- 3. Fallback: prosty scoring ---
        best_name = empty_filename
        best_score = -10 ** 9

        for d in defs:
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
            score += 20 * edge_match - 40 * edge_missing - 10 * edge_extra
            score += 10 * inner_match - 15 * inner_missing - 5 * inner_extra

            # lekka kara za zbyt skomplikowane tilesy
            complexity = len(edges) + len(inner) + len(outer)
            score -= 0.1 * complexity

            if score > best_score:
                best_score = score
                best_name = d["filename"]

        return best_name

    def get_terrain_icon(self, terrain: str, cell_size: int):
        """Zwraca miniaturkę terenu do legendy albo None."""
        base = self.terrain_icon_bases.get(terrain)
        if not base: return None
        icon_size = max(18, min(32, int(cell_size * 0.6)))
        if terrain == "dzielnica":
            icon_size = max(12, icon_size // 2)  # 50% mniejsze
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

    def _is_not_terrain(self, y, x, terrain_name: str) -> bool:
        """
        True, jeśli pole NIE jest danym terenem (np. nie-las, nie-wzgórza).
        Używane do wykrywania 'krawędzi' lasu/wzgórz względem otoczenia.
        """
        if 0 <= y < self.map_size and 0 <= x < self.map_size:
            return self.map_grid[y][x]["terrain"] != terrain_name
        return False

    def pick_ocean_tile_name(self, neigh):
        if not hasattr(self, "ocean_defs") or not self.ocean_defs:
            self.init_ocean_tiles()
        return self._pick_tile_from_defs(neigh, self.ocean_defs, "ocean_inner.png")

    def pick_forest_tile_name(self, neigh):
        if not hasattr(self, "forest_defs") or not self.forest_defs:
            self.init_forest_tiles()
        return self._pick_tile_from_defs(neigh, self.forest_defs, "forest_inner.png")

    def pick_mountains_tile_name(self, neigh):
        if not hasattr(self, "mountains_defs") or not self.mountains_defs:
            self.init_mountains_tiles()
        return self._pick_tile_from_defs(neigh, self.mountains_defs, "mountains_inner.png")

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

    def get_forest_neighbors(self, y, x):
        """Sąsiedzi względem lasu: True tam, gdzie pole NIE jest lasem."""
        n = self._is_not_terrain(y - 1, x, "las")
        ne = self._is_not_terrain(y - 1, x + 1, "las")
        e = self._is_not_terrain(y, x + 1, "las")
        se = self._is_not_terrain(y + 1, x + 1, "las")
        s = self._is_not_terrain(y + 1, x, "las")
        sw = self._is_not_terrain(y + 1, x - 1, "las")
        w = self._is_not_terrain(y, x - 1, "las")
        nw = self._is_not_terrain(y - 1, x - 1, "las")
        return {"N": n, "NE": ne, "E": e, "SE": se, "S": s, "SW": sw, "W": w, "NW": nw}

    def get_mountains_neighbors(self, y, x):
        """Sąsiedzi względem wzgórz: True tam, gdzie pole NIE jest wzniesieniami."""
        n = self._is_not_terrain(y - 1, x, "wzniesienia")
        ne = self._is_not_terrain(y - 1, x + 1, "wzniesienia")
        e = self._is_not_terrain(y, x + 1, "wzniesienia")
        se = self._is_not_terrain(y + 1, x + 1, "wzniesienia")
        s = self._is_not_terrain(y + 1, x, "wzniesienia")
        sw = self._is_not_terrain(y + 1, x - 1, "wzniesienia")
        w = self._is_not_terrain(y, x - 1, "wzniesienia")
        nw = self._is_not_terrain(y - 1, x - 1, "wzniesienia")
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

    def get_ocean_tile_image(self, y, x, cell_size):
        """
        Zwraca ImageTk.PhotoImage z odpowiednim kaflem oceanu dla pola (y,x).
        Warianty _1/_2/_3 są wybierane DETERMINISTYCZNIE na podstawie:
        - self.tile_random_seed
        - położenia pola (y, x)
        - grupy kafla (np. ocean_north)
        """
        neigh = self.get_ocean_neighbors(y, x)
        # najpierw wybieramy "logiczny" kafel (kształt brzegów)
        filename = self.pick_ocean_tile_name(neigh)  # np. 'ocean_north_1.png'

        # a teraz deterministycznie wybieramy wariant _1/_2/_3
        if hasattr(self, "ocean_defs"):
            filename = self._choose_tile_variant(filename, self.ocean_defs, "ocean", y, x)

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

    def get_forest_tile_image(self, y, x, cell_size):
        """Auto-tiling lasu – przezroczysty kafel na tle plains."""
        neigh = self.get_forest_neighbors(y, x)
        # najpierw wybieramy "logiczny" kafel (kształt brzegu lasu)
        filename = self.pick_forest_tile_name(neigh)  # np. 'forest_north_1.png'

        # teraz deterministycznie wybieramy wariant _1/_2/_3
        if hasattr(self, "forest_defs"):
            filename = self._choose_tile_variant(filename, self.forest_defs, "forest", y, x)

        key = (filename, cell_size)
        if key in self.forest_tile_cache:
            return self.forest_tile_cache[key]

        path = os.path.join(self.forest_base_path, filename)
        try:
            img = Image.open(path).resize((cell_size, cell_size), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self.forest_tile_cache[key] = tk_img
            return tk_img
        except Exception:
            return None

    def get_mountains_tile_image(self, y, x, cell_size):
        """Auto-tiling wzgórz – przezroczysty kafel na tle plains."""
        neigh = self.get_mountains_neighbors(y, x)
        # najpierw wybieramy "logiczny" kafel (kształt brzegu wzgórz)
        filename = self.pick_mountains_tile_name(neigh)  # np. 'mountains_north_1.png'

        # teraz deterministycznie wybieramy wariant _1/_2/_3
        if hasattr(self, "mountains_defs"):
            filename = self._choose_tile_variant(filename, self.mountains_defs, "mountains", y, x)

        key = (filename, cell_size)
        if key in self.mountains_tile_cache:
            return self.mountains_tile_cache[key]

        path = os.path.join(self.mountains_base_path, filename)
        try:
            img = Image.open(path).resize((cell_size, cell_size), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self.mountains_tile_cache[key] = tk_img
            return tk_img
        except Exception:
            return None

    # ===== LEGENDA =====
    def draw_legend(self, canvas, offset_x, offset_y, cell_size):
        legend_y = offset_y + self.map_size * cell_size + 30

        center_x = offset_x + (self.map_size * cell_size) / 2

        # fonty spójne z UI
        title_font = getattr(self, "top_title_font", ("Cinzel", 14, "bold"))
        info_font = getattr(self, "top_info_font", ("EB Garamond Italic", 12))
        small_info_font = (info_font[0], max(8, info_font[1] - 2))
        small_info_bold = (info_font[0], max(8, info_font[1] - 2), "bold")

        # tytuł
        canvas.create_text(
            center_x, legend_y,
            text="LEGENDA",
            anchor="center",
            font=title_font
        )

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
                canvas.create_rectangle(x - 10, terrain_y - 10, x + 10, terrain_y + 10,
                                        fill=color, outline="black")
            canvas.create_text(
                x, terrain_y + 22,
                text=name.capitalize(),
                anchor="center",
                font=small_info_font
            )

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
                canvas.create_rectangle(x - 10, mine_y - 10, x + 10, mine_y + 10,
                                        fill=color, outline="black")

            canvas.create_text(
                x, mine_y + 22,
                text=MINE_NAMES[res],
                anchor="center",
                font=small_info_font
            )

    # ===== WSPÓLNE RYSOWANIE TERAENU =====
    def _draw_terrain_cell(self, canvas, x, y, offset_x, offset_y, cell_size):
        """
        Wspólne rysowanie JEDNEGO odkrytego pola mapy:
        - morze / las / wzniesienia: plains w tle + autotiling
        - osada / dzielnica: plains w tle + camp overlay (dzielnica 50% mniejsza)
        - pole: plains sprite
        - reszta terenów: prostokąt koloru
        """
        cell = self.map_grid[y][x]
        terrain = cell["terrain"]

        # ===== morze / las / wzniesienia (jak było) =====
        if terrain in ("morze", "las", "wzniesienia"):
            # tło – pole (plains)
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

            img = None
            if terrain == "morze":
                img = self.get_ocean_tile_image(y, x, cell_size)
                fallback_color = BASE_COLORS["morze"]
            elif terrain == "las":
                img = self.get_forest_tile_image(y, x, cell_size)
                fallback_color = BASE_COLORS["las"]
            else:  # "wzniesienia"
                img = self.get_mountains_tile_image(y, x, cell_size)
                fallback_color = BASE_COLORS["wzniesienia"]

            if img:
                canvas.create_image(
                    offset_x + x * cell_size,
                    offset_y + y * cell_size,
                    anchor="nw",
                    image=img
                )
            else:
                canvas.create_rectangle(
                    offset_x + x * cell_size,
                    offset_y + y * cell_size,
                    offset_x + (x + 1) * cell_size,
                    offset_y + (y + 1) * cell_size,
                    fill=fallback_color,
                    outline="gray"
                )
            return

        # ===== osada / dzielnica =====
        if terrain in ("osada", "dzielnica"):
            # tło jak "pole"
            try:
                bg_img = self.get_plains_tile(cell_size)
                canvas.create_image(
                    offset_x + x * cell_size,
                    offset_y + y * cell_size,
                    anchor="nw",
                    image=bg_img
                )
            except Exception:
                ground = BASE_COLORS.get("pole", "#CCCC99")
                canvas.create_rectangle(
                    offset_x + x * cell_size,
                    offset_y + y * cell_size,
                    offset_x + (x + 1) * cell_size,
                    offset_y + (y + 1) * cell_size,
                    fill=ground,
                    outline="gray"
                )

            # nakładka camp.png
            icon = self.get_camp_icon(cell_size, small=(terrain == "dzielnica"))
            if icon:
                img_icon, icon_size = icon
                if terrain == "osada":
                    canvas.create_image(
                        offset_x + x * cell_size,
                        offset_y + y * cell_size,
                        anchor="nw",
                        image=img_icon
                    )
                else:
                    off = (cell_size - icon_size) // 2
                    canvas.create_image(
                        offset_x + x * cell_size + off,
                        offset_y + y * cell_size + off,
                        anchor="nw",
                        image=img_icon
                    )
            return

        # ===== pole (plains sprite) =====
        if terrain == "pole":
            try:
                img = self.get_plains_tile(cell_size)
                canvas.create_image(
                    offset_x + x * cell_size,
                    offset_y + y * cell_size,
                    anchor="nw",
                    image=img
                )
            except Exception:
                # fallback na kolor jeśli plains.png nie ma
                color = BASE_COLORS.get("pole", "#CCCC99")
                canvas.create_rectangle(
                    offset_x + x * cell_size,
                    offset_y + y * cell_size,
                    offset_x + (x + 1) * cell_size,
                    offset_y + (y + 1) * cell_size,
                    fill=color,
                    outline="gray"
                )
            return

        # ===== reszta terenów =====
        color = BASE_COLORS[terrain]
        canvas.create_rectangle(
            offset_x + x * cell_size,
            offset_y + y * cell_size,
            offset_x + (x + 1) * cell_size,
            offset_y + (y + 1) * cell_size,
            fill=color,
            outline="gray"
        )

    # ===== MAPA BUDOWANIA =====
    def show_map(self):
        win = self.create_window("Buduj - wybierz pole")

        # fonty spójne z UI
        title_font = getattr(self, "top_title_font", ("Cinzel", 14, "bold"))
        info_font = getattr(self, "top_info_font", ("EB Garamond Italic", 12))
        tile_label_font = (info_font[0], max(8, info_font[1] - 2), "bold")
        tile_num_font = (info_font[0], max(9, info_font[1] - 1), "bold")

        # większy napis dla osady/dzielnicy
        settlement_label_font = (title_font[0], max(10, title_font[1] + 2), "bold")

        canvas_width = 850
        canvas_height = 850
        canvas = tk.Canvas(
            win, width=canvas_width, height=canvas_height,
            bg=self.style.lookup("TFrame", "background"),
            highlightthickness=0
        )
        canvas.pack(pady=10)

        cell_size = self.get_cell_size()
        map_pixel_size = self.map_size * cell_size

        offset_x = (canvas_width - map_pixel_size) // 2
        offset_y = 40

        def draw():
            canvas.delete("all")
            for y in range(self.map_size):
                for x in range(self.map_size):
                    cell = self.map_grid[y][x]

                    if not cell["discovered"]:
                        try:
                            if not hasattr(self, "terra_incognita_img") or cell_size not in self.terra_incognita_img:
                                path = self.resource_path("img/tiles/terra_incognita.png")
                                base = Image.open(path)
                                img = base.resize((cell_size, cell_size), Image.LANCZOS)
                                if not hasattr(self, "terra_incognita_img"):
                                    self.terra_incognita_img = {}
                                self.terra_incognita_img[cell_size] = ImageTk.PhotoImage(img)

                            canvas.create_image(
                                offset_x + x * cell_size,
                                offset_y + y * cell_size,
                                anchor="nw",
                                image=self.terra_incognita_img[cell_size]
                            )
                        except Exception:
                            canvas.create_rectangle(
                                offset_x + x * cell_size,
                                offset_y + y * cell_size,
                                offset_x + (x + 1) * cell_size,
                                offset_y + (y + 1) * cell_size,
                                fill="#888888",
                                outline="gray",
                            )
                        continue

                    terrain = cell["terrain"]

                    self._draw_terrain_cell(canvas, x, y, offset_x, offset_y, cell_size)

                    building_in_progress = next(
                        (c for c in self.constructions if c[1]["pos"] == (y, x)), None
                    )
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
                            font=tile_label_font
                        )

                    if terrain not in ["osada", "dzielnica"]:
                        buildings_here = [b for b in cell["building"] if not b.get("is_district", False)]
                        if buildings_here:
                            icon = self.get_building_icon(cell_size)
                            if icon:
                                img_icon, icon_size = icon
                                cx = offset_x + x * cell_size + cell_size // 2
                                cy = offset_y + y * cell_size + cell_size // 2
                                canvas.create_image(cx, cy, image=img_icon)

                    if terrain in ["osada", "dzielnica"]:
                        buildings_here = [b for b in cell["building"] if not b.get("is_district", False)]
                        used = len(buildings_here)
                        canvas.create_text(
                            offset_x + x * cell_size + cell_size // 2,
                            offset_y + y * cell_size + cell_size // 2 - 20,
                            text=f"{terrain.capitalize()}",
                            fill="white",
                            font=settlement_label_font
                        )
                        canvas.create_text(
                            offset_x + x * cell_size + cell_size // 2,
                            offset_y + y * cell_size + cell_size // 2,
                            text=f"{used}/5",
                            fill="yellow",
                            font=tile_num_font
                        )

                    if terrain == "wzniesienia" and cell["resource"]:
                        icon = self.get_mine_icon(cell["resource"], cell_size)
                        if icon:
                            img_icon, icon_size = icon
                            cx = offset_x + x * cell_size + cell_size - 5 - icon_size // 2
                            cy = offset_y + y * cell_size + cell_size - 5 - icon_size // 2
                            canvas.create_image(cx, cy, image=img_icon)
                        else:
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
            if 0 <= x < self.map_size and 0 <= y < self.map_size and self.map_grid[y][x]["discovered"]:
                if self.selected_building:
                    self.start_construction_at(self.selected_building, (y, x))
                    self.selected_building = None
                    win.destroy()

        canvas.bind("<Button-1>", click)
        draw()
        ttk.Button(win, text=self.loc.t("ui.cancel"), command=win.destroy).pack(pady=5)

        self.center_window(win)

    # ===== MAPA EKSPLORACJI =====
    def show_explore_map(self):
        win = self.create_window(self.loc.t("screen.exploration.title"))

        # fonty spójne z UI
        title_font = getattr(self, "top_title_font", ("Cinzel", 14, "bold"))
        info_font = getattr(self, "top_info_font", ("EB Garamond Italic", 12))
        tile_q_font = (title_font[0], max(14, title_font[1] + 6), "bold")

        info_frame = ttk.Frame(win)
        info_frame.pack(pady=5)

        ttk.Label(info_frame, text=self.loc.t("screen.exploration.cost_title"), font=title_font).pack()
        ttk.Label(
            info_frame,
            text=self.loc.t("screen.exploration.cost_line"),
            justify="center",
            font=info_font
        ).pack()

        canvas_width = 850
        canvas_height = 850
        canvas = tk.Canvas(
            win,
            width=canvas_width,
            height=canvas_height,
            bg=self.style.lookup("TFrame", "background"),
            highlightthickness=0
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
                                width=2
                            )
                            canvas.create_text(
                                offset_x + x * cell_size + cell_size // 2,
                                offset_y + y * cell_size + cell_size // 2,
                                text="?",
                                fill="white",
                                font=tile_q_font
                            )
                        continue

                    terrain = cell["terrain"]

                    self._draw_terrain_cell(canvas, x, y, offset_x, offset_y, cell_size)

                    if terrain == "wzniesienia" and cell["resource"]:
                        icon = self.get_mine_icon(cell["resource"], cell_size)
                        if icon:
                            img_icon, icon_size = icon
                            cx = offset_x + x * cell_size + cell_size - 5 - icon_size // 2
                            cy = offset_y + y * cell_size + cell_size - 5 - icon_size // 2
                            canvas.create_image(cx, cy, image=img_icon)

            self.draw_legend(canvas, offset_x, offset_y, cell_size)

        def debug_reveal_all():
            for row in self.map_grid:
                for cell in row:
                    cell["discovered"] = True
            draw()

        def click(event):
            x = (event.x - offset_x) // cell_size
            y = (event.y - offset_y) // cell_size
            if not (0 <= x < self.map_size and 0 <= y < self.map_size):
                return

            cell = self.map_grid[y][x]
            if cell["discovered"]:
                return

            neighbors = [
                (y + dy, x + dx)
                for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                if 0 <= y + dy < self.map_size and 0 <= x + dx < self.map_size
            ]
            if not any(self.map_grid[ny][nx]["discovered"] for ny, nx in neighbors):
                return

            days = random.randint(1, 3) + int(math.hypot(y - self.settlement_pos[0], x - self.settlement_pos[1]))
            cost_food = 15
            cost_wood = 10

            confirm = self.create_window(self.loc.t("screen.exploration.confirm_title"))
            bg = self.style.lookup("TFrame", "background")

            ttk.Label(
                confirm,
                text=self.loc.t("screen.exploration.confirm_send_to", y=y, x=x),
                font=title_font,
                background=bg
            ).pack(pady=10)

            ttk.Label(
                confirm,
                text=self.loc.t("screen.exploration.confirm_time_cost", days=days, food=cost_food, wood=cost_wood),
                justify="center",
                font=info_font,
                background=bg
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
                self.log(f"Eksploracja ({y},{x}): powrót {end_date.strftime('%d %b %Y')}", "blue")
                confirm.destroy()
                win.destroy()

            ttk.Button(confirm, text=self.loc.t("ui.send"), command=do_explore).pack(side="left", padx=10, pady=10)
            ttk.Button(confirm, text=self.loc.t("ui.cancel"), command=confirm.destroy).pack(side="right", padx=10, pady=10)

        # ttk.Button(
        #     info_frame,
        #     text="Odkryj wszystkie pola (debug)",
        #     command=debug_reveal_all,
        # ).pack(pady=2)

        canvas.bind("<Button-1>", click)
        draw()
        ttk.Button(win, text=self.loc.t("ui.cancel"), command=win.destroy).pack(pady=5)

        self.center_window(win)

