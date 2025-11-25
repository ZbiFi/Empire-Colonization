# reset_manager.py
import random
from datetime import timedelta

from constants import (
    RESOURCES, STATES, TRIBE_DISPLAY_KEYS,
    NATIVE_RESOURCE_ECONOMY, MAP_SIZE,
    SHIP_STATUS_IN_PORT
)

def reset_game_state(sim, *, to_start_screen=True, keep_settings=True):
    """
    Twardy reset runtime'owego stanu gry.
    - sim: instancja ColonySimulator.
    - to_start_screen: czy po resecie pokazać menu startowe.
    - keep_settings: nie ruszaj sim.settings i sim.loc (język, głośności).
    """

    # --- 0) Zatrzymaj timery/tryby zależne od gry ---
    sim.auto_sail_timer = None
    sim.selected_building = None
    sim.current_screen = "start"

    # --- 1) Podstawowe zmienne gry ---
    sim.state = None
    sim.state_display = None
    sim.location = None
    sim.location_key = None
    sim.current_date = None
    sim.people = 10
    sim.busy_people = 0
    sim.days_passed = 0

    # --- 2) Zasoby (jak w __init__) ---
    sim.resources = {r: 0 for r in RESOURCES}
    # DEV-owe startowe stany z main.py (możesz wyciąć kiedy przejdziesz na proper start)
    sim.resources.update({
        "food": 1000, "wood": 1000, "skins": 1000, "clothes": 1000,
        "herbs": 1000, "meds": 1000, "iron": 1000, "steel": 1000,
        "cane": 1000, "sugar": 1000, "tobacco": 1000, "cigars": 1000,
        "coal": 1000, "silver": 1000, "gold": 1000, "ducats": 1000
    })

    # --- 3) Budynki / konstrukcje / ekspedycje ---
    sim.buildings = []
    sim.constructions = []
    sim.upgrades_in_progress = []
    sim.expeditions = []

    # --- 4) Statki ---
    sim.ships = []
    sim.flagship_index = 0

    # --- 5) Relacje / handel ---
    sim.native_relations = {
        tribe: 50 for tribe in random.sample(list(TRIBE_DISPLAY_KEYS.keys()), 3)
    }
    sim.europe_relations = {s: 0 for s in STATES}
    sim.europe_trade_value = {s: 0 for s in sim.europe_relations}
    sim.native_trade_value = {tribe: 0 for tribe in sim.native_relations}

    # --- 6) Produkcja/stock plemion ---
    sim.native_prod = {}
    sim.native_cap = {}
    sim.native_stock = {}
    for tribe in sim.native_relations:
        prod_map, cap_map, stock_map = {}, {}, {}
        for res, econ in NATIVE_RESOURCE_ECONOMY.items():
            p_min, p_max = econ["daily_prod"]
            c_min, c_max = econ["stockpile"]
            prod_val = random.uniform(p_min, p_max)
            cap_val = random.uniform(c_min, c_max)
            prod_map[res] = prod_val
            cap_map[res] = cap_val
            stock_map[res] = cap_val
        sim.native_prod[tribe] = prod_map
        sim.native_cap[tribe] = cap_map
        sim.native_stock[tribe] = stock_map

    sim.trade_reputation_threshold = 1000
    sim.native_missions_enabled_start = None

    # --- 7) Misje królewskie / indiańskie ---
    sim.current_mission = None
    sim.last_mission_date = None
    sim.mission_multiplier = 1.0
    sim.first_mission_given = False
    sim.completed_missions = 0
    sim.missions_to_win = 100

    sim.native_missions_active = {}
    sim.native_missions_cd = {}
    sim.native_mission_multiplier = {}
    sim.native_missions = []

    sim.current_monarch = ""

    # --- 8) Mapa ---
    sim.map_size = MAP_SIZE
    sim.map_grid = None
    sim.settlement_pos = None

    # --- 9) Logi ---
    sim.log_lines = []

    # --- 10) UI / okna ---
    # zamknij wszystkie toplevele poza tymi singletonami trzymanymi w sim
    for w in sim.root.winfo_children():
        try:
            if w.winfo_exists() and w.winfo_class() == "Toplevel":
                w.destroy()
        except Exception:
            pass
    # wyczyść kontener gry jeśli istnieje
    if getattr(sim, "game_container", None) is not None and sim.game_container.winfo_exists():
        sim.game_container.destroy()
        sim.game_container = None

    # --- 11) Przywróć start screen ---
    if to_start_screen:
        # wyczyść wszystko z root (jak robi main_game)
        for w in sim.root.winfo_children():
            try: w.destroy()
            except Exception: pass
        sim.start_screen()
