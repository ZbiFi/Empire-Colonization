# map_generator.py
import random

# Konfiguracja mapy
MAP_SIZE = 8
MINE_RESOURCES = ["węgiel", "żelazo", "srebro", "złoto"]
BASE_COLORS = {"morze": "#0066CC", "pole": "#CCCC99", "las": "#228B22", "wzniesienia": "#8B4513", "osada": "#000000"}
FERTILITY = {"nieurodzaj": 0.7, "średni": 1.0, "płodny": 1.3}


def is_edge(y, x, size):
    """Sprawdza, czy pole jest przy krawędzi mapy"""
    return y == 0 or y == size - 1 or x == 0 or x == size - 1


def get_neighbors(y, x, size):
    """Zwraca listę sąsiadów (8-kierunkowych) w granicach mapy"""
    neighbors = []
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dy == 0 and dx == 0:
                continue
            ny, nx = y + dy, x + dx
            if 0 <= ny < size and 0 <= nx < size:
                neighbors.append((ny, nx))
    return neighbors


def generate_map(size: int = MAP_SIZE):
    """
    Generuje mapę x:x z:
    - brzegiem wody (połączony, dotyka krawędzi)
    - osadą NIE na krawędzi
    - wokół osady (8 sąsiadów): dokładnie 1 morze, 1 pole, 1 las, 1 wzniesienie
    """
    grid = [[None for _ in range(size)] for _ in range(size)]

    # === 1. Generowanie brzegu wody (połączony, dotyka krawędzi) ===
    water_cells = []
    edge = random.choice(["top", "bottom", "left", "right"])

    # Startowy punkt na krawędzi
    if edge == "top":
        start = (0, random.randint(1, size - 2))
    elif edge == "bottom":
        start = (size - 1, random.randint(1, size - 2))
    elif edge == "left":
        start = (random.randint(1, size - 2), 0)
    else:  # right
        start = (random.randint(1, size - 2), size - 1)

    water_cells.append(start)
    grid[start[0]][start[1]] = {
        "terrain": "morze",
        "fertility": "średni",
        "building": [],
        "discovered": True,
        "quality_known": True,
        "resource": None
    }

    # Rozszerz wodę (co najmniej 6 pól, połączona)
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    while len(water_cells) < max(6, size):
        candidates = []
        for y, x in water_cells:
            for dy, dx in directions:
                ny, nx = y + dy, x + dx
                if 0 <= ny < size and 0 <= nx < size and grid[ny][nx] is None:
                    dist_to_edge = min(ny, size - 1 - ny, nx, size - 1 - nx)
                    weight = 2.0 if dist_to_edge <= 1 else 0.5
                    candidates.append((ny, nx, weight))

        if not candidates:
            break

        total_weight = sum(w for _, _, w in candidates)
        r = random.uniform(0, total_weight)
        acc = 0
        chosen = None
        for ny, nx, w in candidates:
            acc += w
            if r <= acc:
                chosen = (ny, nx)
                break

        if chosen:
            water_cells.append(chosen)
            grid[chosen[0]][chosen[1]] = {
                "terrain": "morze",
                "fertility": "średni",
                "building": [],
                "discovered": True,
                "quality_known": True,
                "resource": None
            }

    # === 2. Wypełnij resztę lądem (tymczasowo) ===
    for y in range(size):
        for x in range(size):
            if grid[y][x] is None:
                terrain = random.choices(["pole", "las", "wzniesienia"], weights=[50, 30, 20])[0]
                fertility = random.choices(["nieurodzaj", "średni", "płodny"], weights=[20, 60, 20])[0]
                resource = random.choice(MINE_RESOURCES) if terrain == "wzniesienia" else None
                grid[y][x] = {
                    "terrain": terrain,
                    "fertility": fertility,
                    "building": [],
                    "discovered": False,
                    "quality_known": False,
                    "resource": resource
                }

    # === 3. Wybierz pozycję osady: nie na krawędzi, sąsiaduje z woda, ma miejsce na 4 różne tereny ===
    possible_settlement = []
    for y in range(1, size - 1):
        for x in range(1, size - 1):
            if grid[y][x]["terrain"] == "morze":
                continue
            neighbors = get_neighbors(y, x, size)
            has_water = any(grid[ny][nx]["terrain"] == "morze" for ny, nx in neighbors)
            if has_water:
                # Sprawdź, czy da się umieścić 1 pole, 1 las, 1 wzniesienie (oprócz wody)
                land_neighbors = [(ny, nx) for ny, nx in neighbors if grid[ny][nx]["terrain"] != "morze"]
                if len(land_neighbors) >= 3:  # potrzebujemy co najmniej 3 pola lądu na różne tereny
                    possible_settlement.append((y, x))

    if not possible_settlement:
        # Fallback: wybierz dowolną nie-krawędziową komórkę z woda w sąsiedztwie
        for y in range(1, size - 1):
            for x in range(1, size - 1):
                if grid[y][x]["terrain"] != "morze":
                    if any(grid[ny][nx]["terrain"] == "morze" for ny, nx in get_neighbors(y, x, size)):
                        possible_settlement.append((y, x))
                        break
            if possible_settlement:
                break

    sy, sx = random.choice(possible_settlement)
    grid[sy][sx]["terrain"] = "osada"
    grid[sy][sx]["building"] = []
    grid[sy][sx]["discovered"] = True
    grid[sy][sx]["quality_known"] = True

    # === 4. Gwarancja: wokół osady dokładnie 1 morze, 1 pole, 1 las, 1 wzniesienie ===
    neighbors = get_neighbors(sy, sx, size)
    required = {"pole", "las", "wzniesienia"}
    placed = set()

    # Najpierw sprawdź, co już jest
    for ny, nx in neighbors:
        terrain = grid[ny][nx]["terrain"]
        if terrain in required:
            placed.add(terrain)

    # Woda musi być — już sprawdziliśmy, że jest
    water_count = sum(1 for ny, nx in neighbors if grid[ny][nx]["terrain"] == "morze")
    if water_count == 0:
        # Siłowo dodaj wodę w losowym sąsiedzie (jeśli coś pójdzie nie tak)
        land_n = [(ny, nx) for ny, nx in neighbors if grid[ny][nx]["terrain"] != "morze"]
        if land_n:
            wy, wx = random.choice(land_n)
            grid[wy][wx]["terrain"] = "morze"
            grid[wy][wx]["resource"] = None
            water_cells.append((wy, wx))

    # Ustaw brakujące tereny
    for terrain in required - placed:
        candidates = [(ny, nx) for ny, nx in neighbors if grid[ny][nx]["terrain"] not in ["morze", "osada"]]
        if candidates:
            ny, nx = random.choice(candidates)
            grid[ny][nx]["terrain"] = terrain
            grid[ny][nx]["resource"] = random.choice(MINE_RESOURCES) if terrain == "wzniesienia" else None

    # === 5. Odkryj osadę i wszystkich jej sąsiadów ===
    grid[sy][sx]["discovered"] = True
    grid[sy][sx]["quality_known"] = True
    for ny, nx in neighbors:
        grid[ny][nx]["discovered"] = True
        grid[ny][nx]["quality_known"] = True

    return grid, (sy, sx)