# state_manager.py
from __future__ import annotations

import json
import os
from datetime import date, datetime
from copy import deepcopy
from pathlib import Path

SAVE_DIR = Path("saves")
# ==============================
# WHITELIST: stan gry do zapisu
# ==============================
SAVE_FIELDS = [
    # core
    "current_date", "days_passed", "people", "busy_people",
    "state", "state_display", "location", "location_key",
    "auto_sail_timer",

    # economy / map / builds
    "resources", "buildings", "constructions", "upgrades_in_progress",
    "map_size", "map_grid", "settlement_pos",

    # expeditions / ships
    "expeditions", "ships", "flagship_index",

    # relations / trade
    "native_relations", "europe_relations",
    "native_prod", "native_cap", "native_stock",
    "europe_trade_value", "native_trade_value",
    "trade_reputation_threshold", "native_missions_enabled_start",

    # missions royal + native
    "current_mission", "last_mission_date", "mission_multiplier",
    "first_mission_given", "completed_missions", "missions_to_win",
    "native_missions_active", "native_missions_cd",
    "native_mission_multiplier", "native_missions",

    # monarchy
    "current_monarch",

    # logs
    "log_lines",
]

# ===========================================
# Runtime-only: NIE zapisujemy i resetujemy
# ===========================================
RUNTIME_FIELDS = [
    "selected_building",
    "_game_menu_win", "_buildings_overview_win", "_buildings_overview_tree",
    "worker_sliders",
]


# =========================
# SERIALIZE (export)
# =========================
def _to_jsonable(obj):
    """Rekurencyjnie zamienia obiekty na typy JSON-owe."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj

    if isinstance(obj, (date, datetime)):
        return obj.isoformat()

    if isinstance(obj, (tuple, set)):
        return [_to_jsonable(x) for x in obj]

    if isinstance(obj, list):
        return [_to_jsonable(x) for x in obj]

    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}

    if hasattr(obj, "__dict__"):
        return _to_jsonable(obj.__dict__)

    return str(obj)


def export_state(sim, *, version=1):
    """
    Zwraca dict gotowy do zapisu w JSON:
    {
      "version": <int>,
      "state": { ... tylko whitelista ... }
    }
    """
    state = {}
    for f in SAVE_FIELDS:
        if hasattr(sim, f):
            state[f] = _to_jsonable(deepcopy(getattr(sim, f)))
    return {"version": version, "state": state}


# =========================
# DESERIALIZE (import)
# =========================
DATE_FIELDS_TOP = {"current_date", "last_mission_date", "auto_sail_timer", "native_missions_enabled_start"}

def _from_iso(s: str):
    """Spróbuj zamienić ISO string na date/datetime; jeśli nie pasuje, zwróć s."""
    if not isinstance(s, str):
        return s
    try:
        if "T" in s:
            return datetime.fromisoformat(s)
        return date.fromisoformat(s)
    except Exception:
        return s


def _restore_positions_in_building(b):
    """Przywraca tuple w budynku."""
    if isinstance(b, dict):
        if "pos" in b and isinstance(b["pos"], list) and len(b["pos"]) == 2:
            b["pos"] = tuple(b["pos"])
    return b


def _restore_state_field(field_name, value):
    """Field-specific restore: daty, tuple, struktury list."""
    if field_name in DATE_FIELDS_TOP:
        return _from_iso(value)

    if field_name == "settlement_pos":
        if isinstance(value, list) and len(value) == 2:
            return tuple(value)
        return value

    if field_name == "buildings":
        if isinstance(value, list):
            return [_restore_positions_in_building(deepcopy(b)) for b in value]
        return value

    if field_name == "expeditions":
        # (end_date, (y,x), "explore")
        out = []
        if isinstance(value, list):
            for e in value:
                if isinstance(e, list) and len(e) >= 3:
                    end_d = _from_iso(e[0])
                    pos = tuple(e[1]) if isinstance(e[1], list) and len(e[1]) == 2 else e[1]
                    kind = e[2]
                    out.append((end_d, pos, kind))
                else:
                    out.append(e)
        return out

    if field_name == "constructions":
        # (end_date, building_dict, cost_dict, start_date)
        out = []
        if isinstance(value, list):
            for c in value:
                if isinstance(c, list) and len(c) == 4:
                    end_d = _from_iso(c[0])
                    b = _restore_positions_in_building(deepcopy(c[1]))
                    cost = deepcopy(c[2])
                    start_d = _from_iso(c[3])
                    out.append((end_d, b, cost, start_d))
                else:
                    out.append(c)
        return out

    if field_name == "upgrades_in_progress":
        # jeśli masz listę podobną do constructions: (end, b, start, ...)
        out = []
        if isinstance(value, list):
            for u in value:
                if isinstance(u, list) and len(u) >= 3:
                    end_d = _from_iso(u[0])
                    b = _restore_positions_in_building(deepcopy(u[1]))
                    start_d = _from_iso(u[2])
                    rest = tuple(u[3:]) if len(u) > 3 else ()
                    out.append((end_d, b, start_d, *rest))
                else:
                    out.append(u)
        return out

    if field_name == "ships":
        # formaty:
        # 7: (arrival_to_eu, arrival_back, load, status, pending, name, ship_type)
        # 6: (arrival_to_eu, arrival_back, load, status, pending, name)
        # 5: (arrival_to_eu, arrival_back, load, status, pending)
        out = []
        if isinstance(value, list):
            for s in value:
                if isinstance(s, list) and len(s) == 7:
                    arrival_to_eu = _from_iso(s[0]) if s[0] else None
                    arrival_back = _from_iso(s[1]) if s[1] else None
                    load = deepcopy(s[2]) if isinstance(s[2], dict) else {}
                    status = s[3]
                    pending = s[4]
                    name = s[5]
                    ship_type = s[6]
                    out.append((arrival_to_eu, arrival_back, load, status, pending, name, ship_type))

                elif isinstance(s, list) and len(s) == 6:
                    arrival_to_eu = _from_iso(s[0]) if s[0] else None
                    arrival_back = _from_iso(s[1]) if s[1] else None
                    load = deepcopy(s[2]) if isinstance(s[2], dict) else {}
                    status = s[3]
                    pending = s[4]
                    name = s[5]
                    out.append((arrival_to_eu, arrival_back, load, status, pending, name))

                elif isinstance(s, list) and len(s) == 5:
                    arrival_to_eu = _from_iso(s[0]) if s[0] else None
                    arrival_back = _from_iso(s[1]) if s[1] else None
                    load = deepcopy(s[2]) if isinstance(s[2], dict) else {}
                    status = s[3]
                    pending = s[4]
                    out.append((arrival_to_eu, arrival_back, load, status, pending))

                else:
                    out.append(s)
        return out

    if field_name == "map_grid":
        # mapa to 2D lista dictów; przywróć tuple pos w buildingach w komórkach
        if isinstance(value, list):
            grid = deepcopy(value)
            for row in grid:
                if not isinstance(row, list):
                    continue
                for cell in row:
                    if isinstance(cell, dict) and isinstance(cell.get("building"), list):
                        cell["building"] = [_restore_positions_in_building(b) for b in cell["building"]]
            return grid
        return value

    return value


def _migrate_state(version, state):
    """Szkielet migracji na przyszłość."""
    # Tu w przyszłości dopisujesz:
    # if version == 1:
    #     state.setdefault("event_flags", {})
    return state


def import_state(sim, payload, *, do_runtime_reset=True):
    """
    Wgrywa stan gry z dict-a.
    payload może być:
      - całe {"version": x, "state": {...}}
      - albo samo {...} (wtedy version=1).

    Zakładamy, że pełny reset gry był wykonany wcześniej.
    """

    if payload is None:
        return

    if isinstance(payload, dict) and "state" in payload:
        version = payload.get("version", 1)
        state = payload.get("state", {})
    else:
        version = 1
        state = payload if isinstance(payload, dict) else {}

    state = _migrate_state(version, deepcopy(state))

    # ustaw pola z whitelisty
    for f in SAVE_FIELDS:
        if f in state:
            setattr(sim, f, _restore_state_field(f, state[f]))

    # runtime reset po imporcie (żeby nie zostały stare tryby/okna)
    if do_runtime_reset:
        for rf in RUNTIME_FIELDS:
            if hasattr(sim, rf):
                setattr(sim, rf, None)

        sim.selected_building = None

def _ensure_save_dir():
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

def _sanitize_name(name: str) -> str:
    # prosta sanityzacja na nazwę pliku
    safe = "".join(c for c in name.strip() if c.isalnum() or c in " _-").strip()
    return safe[:40] if safe else "save"

def list_saves():
    """Zwraca listę dictów: {path, name, date, meta} posortowaną od najnowszych."""
    _ensure_save_dir()
    out = []
    for p in SAVE_DIR.glob("*.json"):
        try:
            with open(p, "r", encoding="utf8") as f:
                payload = json.load(f)
            st = payload.get("state", {})
            name = st.get("save_name", p.stem)
            date_str = st.get("save_time", "")
            meta = st.get("save_meta", "")
            out.append({"path": str(p), "name": name, "date": date_str, "meta": meta})
        except Exception:
            # jeśli plik uszkodzony, i tak pokaż go w liście
            out.append({"path": str(p), "name": p.stem, "date": "", "meta": ""})
    # sortuj po dacie pliku (fallback)
    out.sort(key=lambda x: os.path.getmtime(x["path"]), reverse=True)
    return out

def save_to_file(sim, name: str):
    """Zapisuje stan gry do pliku JSON."""
    _ensure_save_dir()
    name_safe = _sanitize_name(name)
    path = SAVE_DIR / f"{name_safe}.json"

    payload = export_state(sim, version=1)

    # metadane save'a (żeby ładnie pokazać w liście)
    st = payload["state"]
    st["save_name"] = name
    st["save_time"] = datetime.now().strftime("%d %b %Y %H:%M")
    # możesz tu dać cokolwiek chcesz jako meta (np. lokacja, dzień)
    day = st.get("days_passed", 0)
    loc = st.get("location", "")
    st["save_meta"] = f"{loc} • Day {day}" if loc else f"Day {day}"

    with open(path, "w", encoding="utf8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return str(path)

def load_from_file(sim, path: str):
    """Wczytuje zapis z pliku JSON i aplikuje do gry."""
    with open(path, "r", encoding="utf8") as f:
        payload = json.load(f)
    return payload