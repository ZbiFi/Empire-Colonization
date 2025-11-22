# ships.py
import tkinter as tk
from tkinter import ttk
from datetime import timedelta
import random
from functools import partial

from constants import MAX_SHIP_CARGO, EUROPE_PRICES, RESOURCES, STATES


class ShipsMixin:
    def ships_menu(self):

        win = self.create_window(f"Statki")

        ttk.Label(win, text="STATKI HANDLOWE", font=("Arial", 14, "bold")).pack(pady=10)

        for i, (arrival_to_eu, arrival_back, load, status, pending) in enumerate(self.ships):
            is_flagship = (i == self.flagship_index)
            frame = ttk.LabelFrame(win, text=f"Statek {i+1}{' (okręt flagowy)' if is_flagship else ''}")
            frame.pack(fill="x", padx=20, pady=5)

            if pending > 0:
                ttk.Label(frame, text=f"Oczekiwani koloniści: {pending}", foreground="purple").pack(anchor="w")

            ttk.Label(frame, text=f"Status: {status}").pack(anchor="w")

            # Pokazuj odpowiednie daty w zależności od statusu
            if status == "w drodze do Europy" and arrival_to_eu:
                ttk.Label(frame, text=f"Do Europy: {arrival_to_eu.strftime('%d %b %Y')}").pack(anchor="w")
                if arrival_back:
                    ttk.Label(frame, text=f"Powrót: {arrival_back.strftime('%d %b %Y')}").pack(anchor="w")
            elif status == "w porcie w Europie":
                days_left = max(0, 7 - (self.current_date - arrival_to_eu).days)
                ttk.Label(frame, text=f"Czeka w porcie: {days_left} dni").pack(anchor="w")
                if arrival_back:
                    ttk.Label(frame, text=f"Powrót: {arrival_back.strftime('%d %b %Y')}").pack(anchor="w")
            elif status == "w drodze powrotnej" and arrival_back:
                ttk.Label(frame, text=f"Powrót: {arrival_back.strftime('%d %b %Y')}").pack(anchor="w")

            if load:
                load_str = ", ".join(f"{r}: {a}" for r, a in load.items())
                total_units = sum(load.values())
                ttk.Label(frame, text=f"Ładunek: {load_str}").pack(anchor="w")
                load_color = "red" if total_units > MAX_SHIP_CARGO else "black"
                ttk.Label(frame, text=f"Ładowność: {total_units}/{MAX_SHIP_CARGO}",
                          foreground=load_color).pack(anchor="w")

                gold = sum(a * EUROPE_PRICES.get(r, 0) for r, a in load.items())
                ttk.Label(frame, text=f"Przewidywany zarobek: {gold} dukatów").pack(anchor="w")

                if is_flagship and self.current_mission:
                    end, req, sent, diff, _, _ = self.current_mission
                    mission_part = {k: v for k, v in load.items() if k in req}
                    if mission_part:
                        mission_str = ", ".join(
                            f"{k}: {v} (wysłano {sent.get(k, 0)}/{req[k]})"
                            for k, v in mission_part.items()
                        )
                        ttk.Label(frame, text=f"Do misji: {mission_str}", foreground="purple").pack(anchor="w")
            else:
                ttk.Label(frame, text="Ładunek: pusty").pack(anchor="w")
                ttk.Label(frame, text=f"Ładowność: 0/{MAX_SHIP_CARGO}").pack(anchor="w")

            if status == "w porcie":
                ttk.Button(
                    frame,
                    text="Wyślij",
                    command=lambda idx=i: self.open_load_menu(idx, win)
                ).pack(pady=5)

        ttk.Label(win, text=f"Łączne dukaty: {self.resources['dukaty']}").pack(pady=10)
        ttk.Button(win, text="Zamknij", command=win.destroy).pack(pady=5)

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
            self.log(f"Za dużo towarów! Max: {MAX_SHIP_CARGO}", "red")
            return False

        free_ship = next((i for i, s in enumerate(self.ships) if s[3] == "w porcie"), None)
        if free_ship is None:
            self.log("Brak wolnego statku!", "red")
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
                self.log("MISJA KRÓLEWSKA WYKONANA! (po dopłynięciu do Europy)", "DarkOrange")
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

        self.ships[free_ship] = (arrival_to_europe, arrival_back, load.copy(), "w drodze do Europy", pending)
        self.auto_sail_timer = None

        self.log(
            f"Statek wypłynął → Europa: {arrival_to_europe.strftime('%d %b %Y')} "
            f"→ Czeka 7 dni → Powrót: {arrival_back.strftime('%d %b %Y')} | "
            f"Ładunek: {total_units}/{MAX_SHIP_CARGO}",
            "blue",
        )

        if mission_contribution:
            end, req, sent, diff, text, idx = self.current_mission if self.current_mission else (None, {}, {}, 0, "", 0)
            contrib_str = ", ".join(
                f"{k}: {v}/{req[k]}" for k, v in mission_contribution.items() if k in req
            )
            if contrib_str:
                self.log(f"Do misji: {contrib_str}", "purple")

        return True

    def open_load_menu(self, ship_idx, parent):

        load_win = self.create_window(f"Załaduj statek")

        load_win.geometry("560x680")

        top_frame = ttk.Frame(load_win)
        top_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(top_frame, text="Ładowność:", font=("Arial", 10, "bold")).pack(side="left")
        total_var = tk.IntVar(value=0)
        limit_lbl = ttk.Label(top_frame, text=f"0/{MAX_SHIP_CARGO}", font=("Arial", 10, "bold"))
        limit_lbl.pack(side="left", padx=10)
        over_lbl = ttk.Label(top_frame, text="", foreground="red")
        over_lbl.pack(side="left", padx=5)

        if self.current_mission and ship_idx == self.flagship_index:
            end, req, sent, diff, text, idx = self.current_mission
            mission_frame = ttk.LabelFrame(top_frame, text="Postęp misji")
            mission_frame.pack(side="left", padx=20)
            for r in req:
                have = sent.get(r, 0)
                need = req[r]
                color = "green" if have >= need else "red"
                ttk.Label(mission_frame, text=f"{r}: {have}/{need}", foreground=color).pack()

        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side="right")

        def send():
            load = {r: v.get() for r, v in cargo_vars.items() if v.get() > 0}
            total = sum(load.values())
            if not load:
                self.log("Pusty ładunek!", "red")
                return
            if total > MAX_SHIP_CARGO:
                self.log(f"Za dużo! Max: {MAX_SHIP_CARGO} (masz {total})", "red")
                return
            if self.send_ship(load):
                parent.destroy()
                load_win.destroy()

        ttk.Button(btn_frame, text="Wyślij", command=send).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Anuluj", command=load_win.destroy).pack(side="left", padx=5)

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
            over_lbl.config(text=f"Przekroczono o {total - MAX_SHIP_CARGO}!" if total > MAX_SHIP_CARGO else "")

        for res in RESOURCES[:-1]:
            if self.resources[res] == 0:
                continue

            f = ttk.Frame(scrollable_frame)
            f.pack(fill="x", pady=4, padx=5)

            ttk.Label(f, text=res, width=15, anchor="w").pack(side="left")

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

            max_btn = ttk.Button(f, text="Max", width=5, command=partial(set_max_for_res, res))
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
            if status == "w drodze do Europy" and arrival_to_eu and self.current_date >= arrival_to_eu:
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
                            self.log("MISJA KRÓLEWSKA WYKONANA!", "DarkOrange")
                            self.europe_relations[self.state] = min(100, self.europe_relations[self.state] + 10 * diff)
                            self.current_mission = None
                            self.mission_multiplier *= 0.9
                            self.last_mission_date = self.current_date
                            self.complete_royal_mission()

                    # === SPRZEDAŻ NADMIARU ===
                    gold = sum(a * EUROPE_PRICES.get(r, 0) for r, a in excess.items())
                    if gold > 0:
                        excess_str = ", ".join(f"{k}: {v}" for k, v in excess.items())
                        self.log(
                            f"Statek powinien być {i+1} rozładowany w Europie: {excess_str} → {gold} dukatów",
                            "gold",
                        )
                        self.resources["dukaty"] += gold

                # Statek pusty, czeka 7 dni
                departure_date = arrival_to_eu + timedelta(days=7)
                self.ships[i] = (arrival_to_eu, departure_date, {}, "w porcie w Europie", pending)
                self.log(f"Statek powinien {i+1} czekać 7 dni w porcie europejskim...", "blue")

            # 2. Koniec postoju → wypływa PUSTY w drogę powrotną
            elif status == "w porcie w Europie" and self.current_date >= arrival_back:
                days_back = random.randint(60, 90)
                return_date = self.current_date + timedelta(days=days_back)
                self.ships[i] = (None, return_date, {}, "w drodze powrotnej", pending)
                self.log(
                    f"Statek {i+1} wypłynął z Europy → szacowany powrót: {return_date.strftime('%d %b %Y')}",
                    "blue",
                )

            # 3. Statek wrócił do kolonii
            elif status == "w drodze powrotnej" and arrival_back and self.current_date >= arrival_back:
                if pending > 0:
                    self.people += pending
                    self.log(f"Przybyło {pending} nowych kolonistów z Europy!", "green")
                    pending = 0  # zeruj po wysadzeniu
                self.ships[i] = (None, None, {}, "w porcie", 0)
                self.auto_sail_timer = self.current_date + timedelta(days=14)
                self.log(f"Statek {i+1} wrócił do kolonii. Gotowy do kolejnej podróży.", "blue")
                self.play_sound("ship_arrived")

                # Nowa misja (jeśli minęło 90 dni)
                if i == self.flagship_index:
                    if (self.last_mission_date is None or
                            (self.current_date - self.last_mission_date).days >= 90):
                        if not self.current_mission:
                            self.deliver_new_mission()

    def auto_send_empty_ship(self):
        if self.auto_sail_timer and self.current_date >= self.auto_sail_timer:
            free_ship = next((i for i, s in enumerate(self.ships) if s[3] == "w porcie"), None)
            if free_ship is not None:
                self.send_ship({})
                self.auto_sail_timer = None
