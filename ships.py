# ships.py
import tkinter as tk
from tkinter import ttk
from datetime import timedelta
import random
from functools import partial

from constants import EUROPE_PRICES, RESOURCES, STATES, SHIP_STATUS_IN_EUROPE_PORT, SHIP_STATUS_RETURNING, SHIP_STATUS_IN_PORT, SHIP_STATUS_TO_EUROPE, SHIP_STATUS_KEYS, RESOURCE_DISPLAY_KEYS, SHIP_NAMES_BY_STATE, SHIP_TYPES, BUILDINGS
from tooltip import Tooltip


class ShipsMixin:
    def ships_menu(self):

        self._ensure_ship_names()
        win = self.create_window(self.loc.t("screen.ships.title"), key="screen.ships")
        win.geometry("800x600")

        info_font = ("EB Garamond", 15)
        small_info_font = ("EB Garamond", 13)
        small_info_bold = ("EB Garamond", 13, "bold")

        # ======= SCROLLOWANY GRID STATKÓW =======
        outer = ttk.Frame(win)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        # wysokość na min. 2 wiersze (każdy frame ~170-190px)
        self.ships_canvas = tk.Canvas(
            outer, height=380, highlightthickness=0,
            bg=self.style.lookup("TFrame", "background")
        )
        self.ships_canvas.grid(row=0, column=0, sticky="nsew")

        self.ships_scroll = ttk.Scrollbar(outer, orient="vertical", command=self.ships_canvas.yview)
        self.ships_scroll.grid(row=0, column=1, sticky="ns")
        self.ships_canvas.configure(yscrollcommand=self.ships_scroll.set)

        ships_frame = ttk.Frame(self.ships_canvas)
        ships_win = self.ships_canvas.create_window((0, 0), window=ships_frame, anchor="nw")

        for c in range(3):
            ships_frame.columnconfigure(c, weight=1, uniform="shipscols")

        scroll_needed = {"value": False}

        def _on_frame_configure(_evt=None):
            bbox = self.ships_canvas.bbox("all")
            if not bbox:
                self.ships_canvas.configure(scrollregion=(0, 0, 0, 0))
                scroll_needed["value"] = False
                if self.ships_scroll.winfo_ismapped():
                    self.ships_scroll.grid_remove()
                return

            self.ships_canvas.configure(scrollregion=bbox)
            content_h = bbox[3] - bbox[1]
            canvas_h = self.ships_canvas.winfo_height()

            if content_h <= canvas_h + 2:
                scroll_needed["value"] = False
                self.ships_canvas.yview_moveto(0)
                if self.ships_scroll.winfo_ismapped():
                    self.ships_scroll.grid_remove()
            else:
                scroll_needed["value"] = True
                if not self.ships_scroll.winfo_ismapped():
                    self.ships_scroll.grid()

        def _on_canvas_configure(evt):
            # dopasuj szerokość okna z listą do szerokości canvasa
            self.ships_canvas.itemconfig(ships_win, width=evt.width)

            # wymuś 3 równe kolumny nawet gdy część jest pusta
            col_w = max(1, evt.width // 3)
            for c in range(3):
                ships_frame.columnconfigure(c, minsize=col_w, uniform="shipscols")

        ships_frame.bind("<Configure>", _on_frame_configure)
        self.ships_canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(evt):
            if not scroll_needed["value"]:
                return
            self.ships_canvas.yview_scroll(int(-1 * (evt.delta / 120)), "units")

        self.ships_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ======= LISTA DO WYŚWIETLENIA (testowo 5 statków) =======
        display_ships = list(self.ships)

        # ======= RENDER 3-KOLUMNOWY =======
        for i, (arrival_to_eu, arrival_back, load, status, pending, ship_name, ship_type) in enumerate(display_ships):
            row, col = divmod(i, 3)
            is_flagship = (i == self.flagship_index)

            title = ship_name + (" ★" if is_flagship else "")
            frame = ttk.LabelFrame(ships_frame, text="")
            frame.grid(row=row, column=col, sticky="nsew", padx=6, pady=6, ipadx=6, ipady=4)

            name_font = (info_font[0], info_font[1], "bold")
            ttk.Label(frame, text=title, font=name_font).pack(anchor="w")

            status_key = SHIP_STATUS_KEYS.get(status, status)

            if status == "building":
                status_key = "ship.status.building"

            ttk.Label(
                frame,
                text=self.loc.t("screen.ships.status_line", status=self.loc.t(status_key)),
                font=small_info_bold
            ).pack(anchor="w")

            ship_data = SHIP_TYPES.get(ship_type, SHIP_TYPES["galleon"])
            stype_key = ship_data["name_key"]
            max_cargo = self._ship_capacity(ship_type)

            ttk.Label(
                frame,
                text=self.loc.t("screen.ships.type_line", type=self.loc.t(stype_key)),
                font=small_info_font
            ).pack(anchor="w")

            if status == "building" and arrival_to_eu:
                ttk.Label(
                    frame,
                    text=self.loc.t("screen.ships.building_until", date=arrival_to_eu.strftime("%d %b %Y")),
                    font=small_info_font,
                    foreground="DarkOrange"
                ).pack(anchor="w")

            # Pokazuj odpowiednie daty w zależności od statusu
            if status == SHIP_STATUS_TO_EUROPE and arrival_to_eu:
                ttk.Label(
                    frame,
                    text=self.loc.t("screen.ships.to_europe_date", date=arrival_to_eu.strftime("%d %b %Y")),
                    font=small_info_font
                ).pack(anchor="w")
                if arrival_back:
                    ttk.Label(
                        frame,
                        text=self.loc.t("screen.ships.return_date", date=arrival_back.strftime("%d %b %Y")),
                        font=small_info_font
                    ).pack(anchor="w")

            elif status == SHIP_STATUS_IN_EUROPE_PORT:
                days_left = max(0, 7 - (self.current_date - arrival_to_eu).days)
                ttk.Label(
                    frame,
                    text=self.loc.t("screen.ships.waiting_in_europe", days=days_left),
                    font=small_info_font
                ).pack(anchor="w")
                if arrival_back:
                    ttk.Label(
                        frame,
                        text=self.loc.t("screen.ships.return_date", date=arrival_back.strftime("%d %b %Y")),
                        font=small_info_font
                    ).pack(anchor="w")

            elif status == SHIP_STATUS_RETURNING and arrival_back:
                ttk.Label(
                    frame,
                    text=self.loc.t("screen.ships.return_date", date=arrival_back.strftime("%d %b %Y")),
                    font=small_info_font
                ).pack(anchor="w")

            if load:
                load_str = ", ".join(f"{r}: {a}" for r, a in load.items())
                total_units = sum(load.values())
                ttk.Label(
                    frame,
                    text=self.loc.t("screen.ships.cargo_line", cargo=load_str),
                    font=small_info_font
                ).pack(anchor="w")

                load_color = "red" if total_units > max_cargo else "black"
                ttk.Label(
                    frame,
                    text=self.loc.t("screen.ships.cargo_capacity_line", current=total_units, max=max_cargo),
                    foreground=load_color,
                    font=small_info_font
                ).pack(anchor="w")

                sell_mult = self.get_europe_sell_mult_for_player()
                gold = round(sum(a * EUROPE_PRICES.get(r, 0) * sell_mult for r, a in load.items()))
                ttk.Label(
                    frame,
                    text=self.loc.t("screen.ships.expected_profit_line", gold=gold),
                    font=small_info_font
                ).pack(anchor="w")

                if is_flagship and self.current_mission:
                    end, req, sent, diff, _, _ = self.current_mission
                    mission_part = {k: v for k, v in load.items() if k in req}
                    if mission_part:
                        mission_str = ", ".join(
                            f"{k}: {v} (wysłano {sent.get(k, 0)}/{req[k]})"
                            for k, v in mission_part.items()
                        )
                        ttk.Label(
                            frame,
                            text=self.loc.t("screen.ships.mission_cargo_line", mission_cargo=mission_str),
                            foreground="purple",
                            font=small_info_bold
                        ).pack(anchor="w")
            else:
                ttk.Label(frame, text=self.loc.t("screen.ships.cargo_empty"), font=small_info_font).pack(anchor="w")
                ttk.Label(frame, text=self.loc.t("screen.ships.cargo_capacity_line", current=0, max=max_cargo), font=small_info_font).pack(anchor="w")

            if status == SHIP_STATUS_IN_PORT:
                ttk.Button(
                    frame,
                    text=self.loc.t("ui.send"),
                    command=lambda idx=i: self.open_load_menu(idx, win)
                ).pack(pady=5)

        ttk.Label(
            win,
            text=self.loc.t("screen.ships.total_ducats", ducats=self.resources["ducats"]),
            font=info_font
        ).pack(pady=10)

        ttk.Button(win, text=self.loc.t("ui.build_ship"), command=lambda: self.open_build_ship_menu(win)).pack(pady=(8, 2))
        ttk.Button(win, text=self.loc.t("ui.close"), command=win.destroy).pack(pady=5)

        # wyśrodkuj okno statków
        self.center_window(win)

    def _ship_capacity(self, ship_type):
        """Zwraca ładowność statku wynikającą z jego typu (fallback na galleon)."""
        return SHIP_TYPES.get(ship_type, SHIP_TYPES["galleon"])["capacity"]

    def _ensure_ship_names(self):
        """Dla nowych gier i starych savów: dopina nazwy i typy do statków jeśli ich brak."""
        used = []
        new_list = []
        for ship in self.ships:
            # nowy format: (arrival_to_eu, arrival_back, load, status, pending, name, ship_type)
            if len(ship) == 7:
                new_list.append(ship);
                used.append(ship[5]);
                continue

            # format po dodaniu nazw (len==6) → dopnij ship_type
            if len(ship) == 6:
                arrival_to_eu, arrival_back, load, status, pending, name = ship
                ship_type = "galleon"  # default dla starych save’ów
                new_list.append((arrival_to_eu, arrival_back, load, status, pending, name, ship_type))
                used.append(name)
                continue

            # stary format: (arrival_to_eu, arrival_back, load, status, pending)
            arrival_to_eu, arrival_back, load, status, pending = ship
            name = self.get_random_ship_name(self.state, used)
            used.append(name)
            ship_type = "galleon"  # na start największa jednostka jak dotąd
            new_list.append((arrival_to_eu, arrival_back, load, status, pending, name, ship_type))

        self.ships = new_list

    def open_build_ship_menu(self, parent_win):
        build_win = self.create_window(self.loc.t("screen.build_ship.title"), key="screen.build_ship")
        build_win.geometry("600x900")

        info_font = ("EB Garamond", 15)
        small_info_font = ("EB Garamond", 13)

        outer = ttk.Frame(build_win)
        outer.pack(fill="both", expand=True, padx=12, pady=10)

        ttk.Label(outer, text=self.loc.t("screen.build_ship.header"), font=info_font).pack(anchor="center", pady=(0, 10))

        list_frame = ttk.Frame(outer)
        list_frame.pack(fill="both", expand=True)

        for stype, data in SHIP_TYPES.items():
            # karta o stałej wielkości
            card = ttk.Frame(list_frame, relief="groove", borderwidth=2)
            card.pack(fill="x", pady=6, padx=6)
            card.pack_propagate(False)
            card.configure(height=250)  # stała wysokość, możesz zmienić np. 160

            # tytuł typu na górze, wyśrodkowany i pogrubiony
            title = ttk.Label(
                card,
                text=self.loc.t(data["name_key"]),
                font=("Cinzel", 15, "bold")
            )
            title.pack(anchor="center", pady=(6, 4))

            cap = data.get("capacity", 0)
            spd = data.get("speed", 1.0)
            crew = data.get("crew", 0)
            days = data.get("build_time", 0)

            cost_str = ", ".join(
                f"{self.loc.t(RESOURCE_DISPLAY_KEYS.get(r, r), default=r)}: {a}"
                for r, a in data.get("cost", {}).items()
            )
            # --- wymagania przystani dla danego typu ---
            harbor_lvl = self._get_best_harbor_level()

            # wylicz req_lvl identycznie jak _harbor_allows_ship
            if "required_harbor_level" in data:
                req_lvl = int(data["required_harbor_level"])  # 1-based
            elif "tier" in data:
                req_lvl = max(1, int(data["tier"]))  # tier 1 -> lvl 1
            else:
                # fallback: kolejność w SHIP_TYPES (pierwszy typ = tier 1)
                types_order = list(SHIP_TYPES.keys())
                tier = types_order.index(stype) + 1 if stype in types_order else 1
                req_lvl = max(1, tier)  # tier 1 -> lvl 1

            # wyciągnij name_key wymaganej przystani / upgrade
            harbor_def = BUILDINGS.get("harbor", {})
            if req_lvl <= 0:
                required_harbor_key = harbor_def.get("name_key", "building.harbor.name")
            else:
                upgrades = harbor_def.get("upgrades", [])
                idx = min(req_lvl - 1, len(upgrades) - 1) if upgrades else 0
                required_harbor_key = upgrades[idx].get("name_key", harbor_def.get("name_key", "building.harbor.name"))

            has_required_harbor = harbor_lvl >= req_lvl

            # linia o przystani (kolorowana)
            ttk.Label(
                card,
                text=self.loc.t("screen.build_ship.required_harbor", harbor=self.loc.t(required_harbor_key)),
                font=small_info_font,
                foreground=("red" if not has_required_harbor else "black"),
                justify="left"
            ).pack(anchor="w", padx=10)

            info_text = (
                f"{self.loc.t('screen.build_ship.capacity_lbl')}: {cap}\n"
                f"{self.loc.t('screen.build_ship.speed_lbl')}: x{spd}\n"
                f"{self.loc.t('screen.build_ship.crew_lbl')}: {crew}\n"
                f"{self.loc.t('screen.build_ship.time_lbl')}: {days} {self.loc.t('ui.days')}\n"
                f"{self.loc.t('screen.build_ship.cost_lbl')}: {cost_str}"
            )

            ttk.Label(card, text=info_text, font=small_info_font, justify="left").pack(anchor="w", padx=10)

            btn = ttk.Button(
                card,
                text=self.loc.t("ui.build"),
                command=lambda t=stype, w=build_win: self.start_build_ship(t, w, parent_win)
            )
            btn.pack(pady=6)

            Tooltip(btn, self.loc.t("tooltip.build_ship_takes_people", crew=data.get("crew", 0)))

        ttk.Button(build_win, text=self.loc.t("ui.cancel"), command=build_win.destroy).pack(pady=6)
        self.center_window(build_win)

    def _get_best_harbor_level(self):
        """Zwraca najwyższy poziom przystani w kolonii albo -1 jeśli brak."""
        best = -1
        for b in getattr(self, "buildings", []):
            base_id = b.get("base")
            if base_id == "harbor":
                best = max(best, b.get("level", 0))
        return best

    def _harbor_allows_ship(self, ship_type):
        """
        True jeśli gracz ma przystań i jej poziom pozwala na budowę tego typu statku.
        Obsługuje dwa warianty:
          - jeśli SHIP_TYPES[type] ma pole required_harbor_level -> używa go
          - jeśli nie ma, bierze pole tier (1..3), a wymagany poziom = tier-1
          - jeśli nie ma ani required_harbor_level ani tier, to traktuje kolejność
            w SHIP_TYPES jako tier 1..N
        """
        data = SHIP_TYPES.get(ship_type, {})
        harbor_lvl = self._get_best_harbor_level()

        if harbor_lvl < 0:
            return False, "no_harbor", {}

        if "required_harbor_level" in data:
            req_lvl = int(data["required_harbor_level"])
        elif "tier" in data:
            req_lvl = max(1, int(data["tier"]))
        else:
            # fallback: kolejność w SHIP_TYPES (pierwszy typ = tier 1)
            types_order = list(SHIP_TYPES.keys())
            tier = types_order.index(ship_type) + 1 if ship_type in types_order else 1
            req_lvl = max(1, tier)

        if harbor_lvl < req_lvl:
            return False, "harbor_too_low", {"need": req_lvl, "have": harbor_lvl}

        return True, None, {}

    def start_build_ship(self, ship_type, build_win, parent_win):
        self._ensure_ship_names()
        data = SHIP_TYPES.get(ship_type)
        if not data:
            return

        ok, err, ctx = self._harbor_allows_ship(ship_type)
        if not ok:
            if err == "no_harbor":
                self.log(self.loc.t("log.no_harbor_for_ship"), "red")
            else:
                self.log(self.loc.t("log.harbor_level_too_low", level_needed=ctx["need"], level_have=ctx["have"]), "red")
            return

        # 1) sprawdź surowce
        cost = data.get("cost", {})
        missing = {r: a - self.resources.get(r, 0) for r, a in cost.items() if self.resources.get(r, 0) < a}
        if missing:
            miss_str = ", ".join(
                f"{self.loc.t(RESOURCE_DISPLAY_KEYS.get(r, r), default=r)}: {v}"
                for r, v in missing.items()
            )
            self.log(self.loc.t("log.not_enough_resources_for_ship", missing=miss_str), "red")
            return

        # 2) sprawdź wolnych ludzi (u Ciebie free_workers() jest w main)
        crew_needed = data.get("crew", 0)
        free_now = self.free_workers()
        if free_now < crew_needed:
            self.log(self.loc.t("log.not_enough_free_workers_for_ship", needed=crew_needed, free=free_now), "red")
            return

        # odejmij koszt
        for r, a in cost.items():
            self.resources[r] -= a

        # zabierz ludzi z puli na czas budowy
        self.people -= crew_needed

        # budowa: arrival_to_eu = data ukończenia
        finish_date = self.current_date + timedelta(days=data.get("build_time", 1))

        used = [s[5] for s in self.ships if len(s) >= 6]
        name = self.get_random_ship_name(self.state, used)

        self.ships.append((finish_date, None, {}, "building", 0, name, ship_type))
        self.log(self.loc.t("log.ship_build_started", name=name, days=data.get("build_time", 1)), "blue")

        try:
            build_win.destroy()
        except Exception:
            pass
        try:
            parent_win.destroy()
        except Exception:
            pass
        self.ships_menu()


    def calculate_load_time(self, load):
        return 1 + (sum(load.values()) // 500)

    def calculate_travel_days(self, ship_type):
        base = random.randint(40, 80)

        # prędkość państwa (jeśli brak, to 1.0)
        state_speed = STATES[self.state].get("speed", 1.0)

        # prędkość statku z typu (fallback na galleon)
        ship_speed = SHIP_TYPES.get(ship_type, SHIP_TYPES["galleon"]).get("speed", 1.0)

        # im większa prędkość, tym mniej dni
        days = int(base / state_speed / ship_speed)

        return max(1, days)

    def get_random_ship_name(self, state_key, used=None):
        """Losuje nazwę statku dla danego państwa, unikając już użytych."""
        pool = SHIP_NAMES_BY_STATE.get(state_key, [])
        if not pool:
            return f"Ship {random.randint(1, 999)}"
        used = set(used or [])
        candidates = [n for n in pool if n not in used]
        return random.choice(candidates if candidates else pool)

    def send_ship(self, load):
        self._ensure_ship_names()
        total_units = sum(load.values())

        free_ship = next((i for i, s in enumerate(self.ships) if s[3] == SHIP_STATUS_IN_PORT), None)
        if free_ship is None:
            self.log(self.loc.t("log.no_free_ship"), "red")
            return False

        # pojemność wynika z typu tego konkretnego statku
        ship_type = self.ships[free_ship][6]
        max_cargo = self._ship_capacity(ship_type)

        if total_units > max_cargo:
            self.log(
                self.loc.t("log.too_much_cargo", max_cargo=max_cargo, total=total_units),
                "red"
            )
            return False
        if free_ship is None:
            self.log(self.loc.t("log.no_free_ship"), "red")
            return False

        # zachowaj ewentualnych oczekujących kolonistów przypiętych do tego statku
        old_arrival_to_eu, old_arrival_back, old_load, old_status, pending, ship_name, ship_type  = self.ships[free_ship]

        mission_contribution = {}

        if self.current_mission and free_ship == self.flagship_index:
            end, req, sent, diff, text, idx = self.current_mission
            mission_completed_before = all(sent.get(r, 0) >= req[r] for r in req)

            for res in req:
                if res in load:
                    needed = req[res] - sent.get(res, 0)
                    if needed > 0:
                        contrib = min(load[res], needed)
                        mission_contribution[res] = contrib
                        sent[res] = sent.get(res, 0) + contrib

            if not mission_completed_before and all(sent.get(r, 0) >= req[r] for r in req):
                self.log(self.loc.t("log.royal_mission_completed_after_arrival"), "DarkOrange")
                self.europe_relations[self.state] = min(100, self.europe_relations[self.state] + 10 * diff)
                self.current_mission = None
                self.mission_multiplier *= 0.9
                self.last_mission_date = self.current_date
                self.complete_royal_mission()

        for r, a in load.items():
            self.resources[r] -= a

        load_time = self.calculate_load_time(load)
        travel_days = self.calculate_travel_days(ship_type)
        days_to_europe = load_time + travel_days
        days_in_europe = 7
        days_back = travel_days

        arrival_to_europe = self.current_date + timedelta(days=days_to_europe)
        arrival_back = arrival_to_europe + timedelta(days=days_in_europe + days_back)

        self.ships[free_ship] = (arrival_to_europe, arrival_back, load.copy(), SHIP_STATUS_TO_EUROPE, pending, ship_name, ship_type)
        self.auto_sail_timer = None

        self.log(
            self.loc.t(
                "log.ship_departed_summary",
                to_europe=arrival_to_europe.strftime("%d %b %Y"),
                back=arrival_back.strftime("%d %b %Y"),
                current=total_units,
                max=max_cargo
            ),
            "blue"
        )

        if mission_contribution:
            end, req, sent, diff, text, idx = self.current_mission if self.current_mission else (None, {}, {}, 0, "", 0)
            contrib_str = ", ".join(
                f"{k}: {v}/{req[k]}" for k, v in mission_contribution.items() if k in req
            )
            if contrib_str:
                self.loc.t("log.mission_contribution", cargo=contrib_str)

        return True

    def open_load_menu(self, ship_idx, parent):

        load_win = self.create_window(self.loc.t("screen.load_ship.title"), key="screen.load_ship")

        load_win.geometry("600x850")

        ship_type = self.ships[ship_idx][6]
        max_cargo = self._ship_capacity(ship_type)

        top_frame = ttk.Frame(load_win)
        top_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(top_frame, text=self.loc.t("screen.load_ship.capacity_label"), font=("Arial", 10, "bold")).pack(side="left")
        total_var = tk.IntVar(value=0)
        limit_lbl = ttk.Label(top_frame, text=f"0/{max_cargo}", font=("Arial", 10, "bold"))
        limit_lbl.pack(side="left", padx=10)
        over_lbl = ttk.Label(top_frame, text="", foreground="red")
        over_lbl.pack(side="left", padx=5)

        if self.current_mission and ship_idx == self.flagship_index:
            end, req, sent, diff, text, idx = self.current_mission
            mission_frame = ttk.LabelFrame(top_frame, text=self.loc.t("screen.load_ship.mission_progress"))
            mission_frame.pack(side="left", padx=20)
            for r in req:
                have = sent.get(r, 0)
                need = req[r]
                color = "green" if have >= need else "red"

                res_label = self.loc.t(RESOURCE_DISPLAY_KEYS.get(r, r), default=r)

                ttk.Label(mission_frame, text=f"{res_label}: {have}/{need}", foreground=color).pack()

        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side="right")

        def send():
            load = {r: v.get() for r, v in cargo_vars.items() if v.get() > 0}
            total = sum(load.values())
            if not load:
                self.log(self.loc.t("ui.empty_cargo"), "red")
                return
            if total > max_cargo:
                self.log(
                    self.loc.t(
                        "log.too_much_cargo",
                        max_cargo=max_cargo,
                        total=total
                    ),
                    "red"
                )
                return
            if self.send_ship(load):
                parent.destroy()
                load_win.destroy()

        ttk.Button(btn_frame, text=self.loc.t("ui.send"), command=send).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=self.loc.t("ui.cancel"), command=load_win.destroy).pack(side="left", padx=5)

        BG = self.style.lookup("TFrame", "background")  # kolor tła całego UI

        canvas = tk.Canvas(load_win, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(load_win, orient="vertical", command=canvas.yview)

        scrollable_frame = ttk.Frame(canvas, style="TFrame")  # styl TFrame = nasze tło
        scrollable_frame.configure(style="TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15, pady=5)
        scrollbar.pack(side="right", fill="y")

        cargo_vars = {}
        sliders = {}
        entries = {}

        def update_total(*args):
            total = 0
            for var in cargo_vars.values():
                try:
                    val = var.get()
                    total += int(val) if val != "" else 0
                except (ValueError, tk.TclError):
                    continue
            total_var.set(total)
            limit_lbl.config(
                text=f"{total}/{max_cargo}",
                foreground="red" if total > max_cargo else "blue"
            )
            over_lbl.config(
                text=self.loc.t("screen.load_ship.exceeded_by", over=total - max_cargo)
                if total > max_cargo else ""
            )

        for res in RESOURCES[:-1]:
            if self.resources[res] == 0:
                continue

            f = ttk.Frame(scrollable_frame)
            f.pack(fill="x", pady=4, padx=5)

            label_key = RESOURCE_DISPLAY_KEYS.get(res, res)  # fallback jakby nie było w mapie
            ttk.Label(
                f,
                text=self.loc.t(label_key, default=res),
                width=15,
                anchor="w"
            ).pack(side="left")

            var = tk.IntVar(value=0)
            cargo_vars[res] = var

            max_possible = self.resources[res]

            slider = tk.Scale(f, from_=0, to=max_possible, orient="horizontal", variable=var, length=200)
            slider.pack(side="left", padx=10)
            sliders[res] = slider

            entry = tk.Entry(f, width=7, justify="center", font=("Arial", 10))
            entry.pack(side="left", padx=5)
            entries[res] = entry
            entry.insert(0, "0")

            def set_max_for_res(r):
                current_total = sum(v.get() for v in cargo_vars.values() if v != cargo_vars[r])
                available_space = max_cargo  - current_total
                max_pos = min(self.resources[r], available_space)
                cargo_vars[r].set(max_pos)
                update_total()

            max_btn = ttk.Button(
                f,
                text=self.loc.t("ui.max"),
                width=5,
                command=partial(set_max_for_res, res)
            )
            max_btn.pack(side="left", padx=5)

            def make_sync_slider(e=entry, r=res, v=var, s=slider):
                def sync_slider(event=None):
                    raw = e.get().strip()
                    if not raw:
                        val = 0
                    else:
                        try:
                            val = int(raw)
                        except ValueError:
                            val = 0
                    val = max(0, min(val, self.resources[r]))
                    v.set(val)
                    e.delete(0, tk.END)
                    e.insert(0, str(val))
                    s.set(val)
                    update_total()
                return sync_slider

            def make_sync_entry(e=entry, v=var):
                def sync_entry(*args):
                    val = v.get()
                    e.delete(0, tk.END)
                    e.insert(0, str(val))
                    update_total()
                return sync_entry

            sync_slider_func = make_sync_slider()
            sync_entry_func = make_sync_entry()

            var.trace_add("write", sync_entry_func)
            entry.bind("<Return>", sync_slider_func)
            entry.bind("<FocusOut>", sync_slider_func)
            entry.bind("<KeyRelease>", lambda ev: load_win.after(50, sync_slider_func))

        update_total()
        # wyśrodkuj okno załadunku
        self.center_window(load_win)

    def process_arriving_ships(self):
        self._ensure_ship_names()
        for i, (arrival_to_eu, arrival_back, load, status, pending, ship_name, ship_type) in enumerate(self.ships):

            # 0) budowa statku skończona
            if status == "building" and arrival_to_eu and self.current_date >= arrival_to_eu:
                self.ships[i] = (None, None, {}, SHIP_STATUS_IN_PORT, pending, ship_name, ship_type)
                self.log(self.loc.t("log.ship_built", name=ship_name), "green")
                continue

            # 1. Statek dotarł do Europy → ROZŁADUNEK + MISJA + 7 DNI POSTOJU
            if status == SHIP_STATUS_TO_EUROPE and arrival_to_eu and self.current_date >= arrival_to_eu:
                if load:
                    excess = load.copy()

                    # === MISJA KRÓLEWSKA (tylko na flagowcu) ===
                    if i == self.flagship_index and self.current_mission:
                        _, req, sent, diff, text, idx = self.current_mission
                        for res in req:
                            if res in load:
                                sent_in_load = min(load[res], req[res] - sent.get(res, 0))
                                if sent_in_load > 0:
                                    sent[res] = sent.get(res, 0) + sent_in_load
                                    excess[res] -= sent_in_load
                                    if excess[res] <= 0:
                                        del excess[res]

                        if all(sent.get(r, 0) >= req[r] for r in req):
                            self.log(self.loc.t("log.royal_mission_done"), "DarkOrange")
                            self.europe_relations[self.state] = min(100, self.europe_relations[self.state] + 10 * diff)
                            self.current_mission = None
                            self.mission_multiplier *= 0.9
                            self.last_mission_date = self.current_date
                            self.complete_royal_mission()

                    # === SPRZEDAŻ NADMIARU ===
                    sell_mult = self.get_europe_sell_mult_for_player()
                    gold = round(sum(a * EUROPE_PRICES.get(r, 0) * sell_mult for r, a in load.items()))
                    if gold > 0:
                        excess_str = ", ".join(
                            f"{self.loc.t(RESOURCE_DISPLAY_KEYS.get(k, k), default=k)}: {v}"
                            for k, v in excess.items()
                        )
                        self.log(
                            self.loc.t(
                                "log.ship_unloaded_in_europe",
                                ship_name=ship_name,
                                cargo=excess_str,
                                gold=gold
                            ),
                            "green"
                        )
                        self.resources["ducats"] += gold

                # Statek pusty, czeka 7 dni
                departure_date = arrival_to_eu + timedelta(days=7)
                self.ships[i] = (arrival_to_eu, departure_date, {}, SHIP_STATUS_IN_EUROPE_PORT, pending, ship_name, ship_type)
                self.log(
                    self.loc.t("log.ship_waiting_in_europe", ship_name=ship_name),
                    "blue"
                )

            # 2. Koniec postoju → wypływa PUSTY w drogę powrotną
            elif status == SHIP_STATUS_IN_EUROPE_PORT    and self.current_date >= arrival_back:
                days_back = random.randint(60, 90)
                return_date = self.current_date + timedelta(days=days_back)
                self.ships[i] = (None, return_date, {}, SHIP_STATUS_RETURNING, pending, ship_name, ship_type)
                self.log(
                    self.loc.t(
                        "log.ship_sailed_from_europe",
                        ship_name=ship_name,
                        date=return_date.strftime("%d %b %Y")
                    ),
                    "blue"
                )

            # 3. Statek wrócił do kolonii
            elif status == SHIP_STATUS_RETURNING and arrival_back and self.current_date >= arrival_back:
                if pending > 0:
                    self.people += pending
                    self.log(
                        self.loc.t("log.colonists_arrived", pending=pending),
                        "green"
                    )
                    pending = 0  # zeruj po wysadzeniu
                self.ships[i] = (None, None, {}, SHIP_STATUS_IN_PORT, 0, ship_name, ship_type)
                self.auto_sail_timer = self.current_date + timedelta(days=14)

                self.log(
                    self.loc.t("log.ship_returned_ready", ship_name=ship_name),
                    "blue"
                )
                self.play_sound("ship_arrived")

                # Nowa misja (jeśli minęło 90 dni)
                if i == self.flagship_index:
                    if (self.last_mission_date is None or
                            (self.current_date - self.last_mission_date).days >= 90):
                        if not self.current_mission:
                            self.deliver_new_mission()

    def get_europe_sell_mult_for_player(self):
        # reputacja z własnym państwem europejskim
        rel = self.europe_relations.get(self.state, 0)
        t = max(0, min(100, rel)) / 100.0
        sell_mult = 0.5 + 0.4 * t

        # bonus handlowy gracza (Anglia/Wenecja)
        if self.state in ("england", "venice"):
            sell_mult += STATES[self.state]["trade"]

        return sell_mult

    def auto_send_empty_ship(self):
        if self.auto_sail_timer and self.current_date >= self.auto_sail_timer:
            free_ship = next((i for i, s in enumerate(self.ships) if s[3] == SHIP_STATUS_IN_PORT), None)
            if free_ship is not None:
                self.send_ship({})
                self.auto_sail_timer = None
