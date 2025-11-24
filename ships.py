# ships.py
import tkinter as tk
from tkinter import ttk
from datetime import timedelta
import random
from functools import partial

from constants import MAX_SHIP_CARGO, EUROPE_PRICES, RESOURCES, STATES, SHIP_STATUS_IN_EUROPE_PORT, SHIP_STATUS_RETURNING, SHIP_STATUS_IN_PORT, SHIP_STATUS_TO_EUROPE, SHIP_STATUS_KEYS, RESOURCE_DISPLAY_KEYS


class ShipsMixin:
    def ships_menu(self):

        win = self.create_window(self.loc.t("screen.ships.title"))

        # fonty spójne z resztą UI (misje)
        title_font = getattr(self, "top_title_font", ("Cinzel", 16, "bold"))
        info_font = getattr(self, "top_info_font", ("EB Garamond Italic", 14))
        small_info_font = (info_font[0], max(10, info_font[1] - 2))
        small_info_bold = (info_font[0], max(10, info_font[1] - 2), "bold")

        ttk.Label(win, text=self.loc.t("screen.ships.header"), font=title_font).pack(pady=10)

        for i, (arrival_to_eu, arrival_back, load, status, pending) in enumerate(self.ships):
            is_flagship = (i == self.flagship_index)
            frame_title_key = "screen.ships.ship_frame_flagship" if is_flagship else "screen.ships.ship_frame"
            frame = ttk.LabelFrame(
                win,
                text=self.loc.t(frame_title_key, num=i + 1)
            )
            frame.pack(fill="x", padx=20, pady=5)

            if pending > 0:
                ttk.Label(
                    frame,
                    text=self.loc.t("screen.ships.pending_colonists", pending=pending),
                    foreground="purple",
                    font=small_info_bold
                ).pack(anchor="w")

            status_key = SHIP_STATUS_KEYS.get(status, status)

            ttk.Label(
                frame,
                text=self.loc.t(
                    "screen.ships.status_line",
                    status=self.loc.t(status_key)
                ),
                font=small_info_bold
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

                load_color = "red" if total_units > MAX_SHIP_CARGO else "black"
                ttk.Label(
                    frame,
                    text=self.loc.t("screen.ships.cargo_capacity_line", current=total_units, max=MAX_SHIP_CARGO),
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
                ttk.Label(frame, text=self.loc.t("screen.ships.cargo_capacity_line", current=0, max=MAX_SHIP_CARGO), font=small_info_font).pack(anchor="w")

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

        ttk.Button(win, text=self.loc.t("ui.close"), command=win.destroy).pack(pady=5)

        # wyśrodkuj okno statków
        self.center_window(win)

    def calculate_load_time(self, load):
        return 1 + (sum(load.values()) // 500)

    def calculate_travel_days(self):
        base = random.randint(40, 80)
        if STATES[self.state].get("speed"):
            base = int(base / STATES[self.state]["speed"])
        return base

    def send_ship(self, load):
        total_units = sum(load.values())
        if total_units > MAX_SHIP_CARGO:
            self.log(
                self.loc.t("log.too_much_cargo", max_cargo=MAX_SHIP_CARGO, total=total_units),
                "red"
            )
            return False

        free_ship = next((i for i, s in enumerate(self.ships) if s[3] == SHIP_STATUS_IN_PORT), None)
        if free_ship is None:
            self.log(self.loc.t("log.no_free_ship"), "red")
            return False

        # zachowaj ewentualnych oczekujących kolonistów przypiętych do tego statku
        old_arrival_to_eu, old_arrival_back, old_load, old_status, pending = self.ships[free_ship]

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
        travel_days = self.calculate_travel_days()
        days_to_europe = load_time + travel_days
        days_in_europe = 7
        days_back = travel_days

        arrival_to_europe = self.current_date + timedelta(days=days_to_europe)
        arrival_back = arrival_to_europe + timedelta(days=days_in_europe + days_back)

        self.ships[free_ship] = (arrival_to_europe, arrival_back, load.copy(), SHIP_STATUS_TO_EUROPE, pending)
        self.auto_sail_timer = None

        self.log(
            self.loc.t(
                "log.ship_departed_summary",
                to_europe=arrival_to_europe.strftime("%d %b %Y"),
                back=arrival_back.strftime("%d %b %Y"),
                current=total_units,
                max=MAX_SHIP_CARGO
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

        load_win = self.create_window(self.loc.t("screen.load_ship.title"))

        load_win.geometry("600x850")

        top_frame = ttk.Frame(load_win)
        top_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(top_frame, text=self.loc.t("screen.load_ship.capacity_label"), font=("Arial", 10, "bold")).pack(side="left")
        total_var = tk.IntVar(value=0)
        limit_lbl = ttk.Label(top_frame, text=f"0/{MAX_SHIP_CARGO}", font=("Arial", 10, "bold"))
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
            if total > MAX_SHIP_CARGO:
                self.log(
                    self.loc.t(
                        "log.too_much_cargo",
                        max_cargo=MAX_SHIP_CARGO,
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
                text=f"{total}/{MAX_SHIP_CARGO}",
                foreground="red" if total > MAX_SHIP_CARGO else "blue"
            )
            over_lbl.config(
                text=self.loc.t("screen.load_ship.exceeded_by", over=total - MAX_SHIP_CARGO)
                if total > MAX_SHIP_CARGO else ""
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
                available_space = MAX_SHIP_CARGO - current_total
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
        for i, (arrival_to_eu, arrival_back, load, status, pending) in enumerate(self.ships):

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
                                num=i + 1,
                                cargo=excess_str,
                                gold=gold
                            ),
                            "green"
                        )
                        self.resources["ducats"] += gold

                # Statek pusty, czeka 7 dni
                departure_date = arrival_to_eu + timedelta(days=7)
                self.ships[i] = (arrival_to_eu, departure_date, {}, SHIP_STATUS_IN_EUROPE_PORT, pending)
                self.log(
                    self.loc.t("log.ship_waiting_in_europe", num=i + 1),
                    "blue"
                )

            # 2. Koniec postoju → wypływa PUSTY w drogę powrotną
            elif status == SHIP_STATUS_IN_EUROPE_PORT    and self.current_date >= arrival_back:
                days_back = random.randint(60, 90)
                return_date = self.current_date + timedelta(days=days_back)
                self.ships[i] = (None, return_date, {}, SHIP_STATUS_RETURNING, pending)
                self.log(
                    self.loc.t(
                        "log.ship_sailed_from_europe",
                        num=i + 1,
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
                self.ships[i] = (None, None, {}, SHIP_STATUS_IN_PORT, 0)
                self.auto_sail_timer = self.current_date + timedelta(days=14)

                self.log(
                    self.loc.t("log.ship_returned_ready", num=i + 1),
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
