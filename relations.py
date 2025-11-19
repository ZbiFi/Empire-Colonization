# relations.py
import tkinter as tk
from datetime import timedelta
from tkinter import ttk
import random

from constants import NATIVE_PRICES, EUROPE_PRICES, STATES, NATIVE_MISSIONS_DETAILS, BLOCK_NATIVE_BUY, BLOCK_EUROPE_BUY


class RelationsMixin:

    def safe_int(self, var):
        try:
            return int(var.get())
        except:
            return 0

    # === Relacje z Indianami ===
    def native_menu(self):
        win = self.create_window(f"Handel z Indianami")
        for tribe in self.native_relations:
            rel = self.native_relations[tribe]
            frame = ttk.Frame(win)
            frame.pack(fill="x", padx=20, pady=3)

            ttk.Label(frame, text=f"{tribe}: {rel}/100", width=25).pack(side="left")

            ttk.Button(
                frame,
                text="Integracja",
                command=lambda t=tribe: self.integrate_natives(t)
            ).pack(side="right", padx=5)

            ttk.Button(
                frame,
                text="Handel",
                command=lambda t=tribe: self.open_native_trade(t, win)
            ).pack(side="right", padx=5)

        ttk.Button(win, text="Zamknij", command=win.destroy).pack(pady=10)

    def integrate_natives(self, tribe):
        """Integracja Indian z danym plemieniem: 1 osoba za 10 reputacji z tym plemieniem."""
        current_rel = self.native_relations.get(tribe, 0)

        if current_rel < 80:
            self.log(f"Za mało reputacji u {tribe}, aby prowadzić integrację (min. 80).", "red")
            return

        max_people = current_rel // 10
        if max_people <= 0:
            self.log(f"Brak reputacji na integrację z {tribe}.", "red")
            return

        win = self.create_window(f"Integracja z {tribe}")

        win.geometry("460x320")
        win.resizable(False, False)

        ttk.Label(
            win,
            text=f"Integracja z {tribe}",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        ttk.Label(
            win,
            text=(
                f"Reputacja z tym plemieniem: {current_rel}/100\n"
                f"Koszt: 10 reputacji za 1 osobę.\n"
                f"Maksymalnie możesz zintegrować: {max_people} osób."
            ),
            justify="center"
        ).pack(pady=5)

        amount_frame = ttk.Frame(win)
        amount_frame.pack(pady=10, fill="x", padx=20)

        ttk.Label(amount_frame, text="Liczba osób do integracji:", font=("Arial", 10)).pack(anchor="w")

        amount_var = tk.IntVar(value=1)
        slider = tk.Scale(
            amount_frame,
            from_=1,
            to=max_people,
            orient="horizontal",
            variable=amount_var,
            length=360
        )
        slider.pack(pady=5)

        amount_lbl = ttk.Label(
            amount_frame,
            text=f"1 (koszt: 10 reputacji)",
            foreground="blue",
            font=("Arial", 11, "bold")
        )
        amount_lbl.pack(anchor="w")

        def update_amount_label(*_):
            n = amount_var.get()
            amount_lbl.config(text=f"{n} (koszt: {n * 10} reputacji)")

        amount_var.trace_add("write", update_amount_label)

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=15)

        def confirm_integration():
            n = amount_var.get()
            cost = n * 10

            if self.native_relations.get(tribe, 0) < cost:
                self.log(
                    f"Za mało reputacji u {tribe}! Potrzeba {cost}, masz {self.native_relations.get(tribe, 0)}.",
                    "red"
                )
                return

            self.native_relations[tribe] -= cost
            self.people += n

            self.log(
                f"Zintegrowano {n} osób z plemienia {tribe}. "
                f"Kosztowało to {cost} reputacji z tym plemieniem.",
                "purple"
            )

            win.destroy()

        ttk.Button(btn_frame, text="Integruj", command=confirm_integration).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Anuluj", command=win.destroy).pack(side="left", padx=8)

    def get_native_price_modifier(self, rel):
        rel_norm = rel / 100.0
        sell_mod = 0.01 + 0.99 * rel_norm
        buy_mod = 2.0 - rel_norm
        if rel == 100:
            sell_mod, buy_mod = 1.5, 0.5
        if self.state == "Anglia":
            sell_mod += STATES[self.state]["trade"]
            buy_mod -= STATES[self.state]["trade"]
        return sell_mod, buy_mod

    def open_native_trade(self, tribe, parent):
        """Handel z Indianami — UI takie jak handel z państwami,
        ale zamiast dukatów jest bilans ilościowy (value units)."""

        trade_win = self.create_window(f"Handel z {tribe}")

        rel = self.native_relations[tribe]
        sell_mod, buy_mod = self.get_native_price_modifier(rel)
        if self.state == "Anglia":
            sell_mod += STATES[self.state]["trade"]
            buy_mod -= STATES[self.state]["trade"]

        ttk.Label(
            trade_win,
            text=(
                f"Relacje z {tribe}: {rel}/100\n"
                f"Ceny zależą od reputacji (sprzedaż x{sell_mod:.2f}, kupno x{buy_mod:.2f})."
            ),
            justify="center"
        ).pack(pady=5)

        # --- SEKCJE (tak jak u Europejczyków) ---
        sell_frame = ttk.LabelFrame(trade_win, text="Sprzedajesz (otrzymujesz wartość)")
        sell_frame.pack(fill="x", padx=15, pady=5)

        buy_frame = ttk.LabelFrame(trade_win, text="Kupujesz (oddajesz wartość)")
        buy_frame.pack(fill="x", padx=15, pady=5)

        sell_vars = {}
        buy_vars = {}

        # --- SUMY (identyczny wygląd jak w open_europe_trade) ---
        def update_sums(*args):
            total_gain = 0  # co Ty zyskujesz
            total_cost = 0  # co oni od Ciebie dostają

            for r, var in sell_vars.items():
                qty = self.safe_int(var)
                if qty > 0:
                    price = NATIVE_PRICES[r] * sell_mod
                    total_gain += qty * price

            for r, var in buy_vars.items():
                qty = self.safe_int(var)
                if qty > 0:
                    price = NATIVE_PRICES[r] * buy_mod
                    total_cost += qty * price

            net = total_gain - total_cost

            self.sell_sum_lbl.config(text=f"Sprzedaż: +{int(total_gain)}")
            self.buy_sum_lbl.config(text=f"Kupno: -{int(total_cost)}")
            self.net_sum_lbl.config(
                text=f"Bilans: {'+' if net >= 0 else ''}{int(net)}"
            )

        sum_frame = ttk.Frame(trade_win)
        sum_frame.pack(pady=8)

        self.sell_sum_lbl = ttk.Label(sum_frame, text="Sprzedaż: +0", foreground="green")
        self.buy_sum_lbl = ttk.Label(sum_frame, text="Kupno: -0", foreground="red")
        self.net_sum_lbl = ttk.Label(sum_frame, text="Bilans: 0", foreground="blue")

        self.sell_sum_lbl.pack(side="left", padx=10)
        self.buy_sum_lbl.pack(side="left", padx=10)
        self.net_sum_lbl.pack(side="left", padx=10)

        # --- LISTA TOWARÓW ---
        for res in NATIVE_PRICES.keys():
            base = NATIVE_PRICES[res]
            sell_price = int(base * sell_mod)
            buy_price = int(base * buy_mod)

            # SPRZEDAJESZ
            if self.resources[res] > 0:
                f = ttk.Frame(sell_frame)
                f.pack(fill="x", pady=1)
                ttk.Label(f, text=res, width=15).pack(side="left")

                var = tk.IntVar()
                spin = tk.Spinbox(f, from_=0, to=self.resources[res],
                                  textvariable=var, width=8)
                spin.pack(side="right")

                ttk.Label(f, text=f"→ {sell_price}").pack(side="right", padx=5)

                sell_vars[res] = var
                var.trace_add("write", update_sums)

            # --- KUPNO U INDIAN ---
            if res not in BLOCK_NATIVE_BUY:
                f = ttk.Frame(buy_frame)
                f.pack(fill="x", pady=1)
                ttk.Label(f, text=res, width=15).pack(side="left")

                var = tk.IntVar()
                spin = tk.Spinbox(f, from_=0, to=999, textvariable=var, width=8)
                spin.pack(side="right")

                ttk.Label(f, text=f"← {buy_price}").pack(side="right", padx=5)

                buy_vars[res] = var
                var.trace_add("write", update_sums)

        update_sums()

        # --- WYKONANIE TRANSAKCJI (zmodyfikowana wersja europejskiej) ---
        def execute_trade():
            sell = {r: self.safe_int(v) for r, v in sell_vars.items() if self.safe_int(v) > 0}
            buy = {r: self.safe_int(v) for r, v in buy_vars.items() if self.safe_int(v) > 0}

            if not sell and not buy:
                self.log("Brak transakcji!", "red")
                return

            total_gain = sum(sell.get(r, 0) * NATIVE_PRICES[r] * sell_mod for r in sell)
            total_cost = sum(buy.get(r, 0) * NATIVE_PRICES[r] * buy_mod for r in buy)

            # Zasoby wystarczą?
            for r, a in sell.items():
                if self.resources[r] < a:
                    self.log(f"Za mało {r}!", "red")
                    return

            net = total_gain - total_cost
            if net < 0:
                # u Indian nie ma dukatów → bilans musi być >= 0
                self.log("Bilans ujemny! Nie masz wystarczającej wartości towarów.", "red")
                return

            # wykonanie handlu
            for r, a in sell.items():
                self.resources[r] -= a
            for r, a in buy.items():
                self.resources[r] += a

            self.log(
                f"Handel z {tribe}: "
                f"{'zysk' if net > 0 else 'na zero'} {int(net)} jednostek wartości.",
                "green" if net > 0 else "gray"
            )

            # --- REPUTACJA (jak ustalone) ---
            trade_value = int(max(total_cost, total_gain))

            previous = self.native_trade_value.get(tribe, 0)
            cumulative = previous + trade_value

            rep_from_volume = cumulative // self.trade_reputation_threshold
            self.native_trade_value[tribe] = cumulative % self.trade_reputation_threshold

            rep_change = rep_from_volume

            # bonus za 2×value (zysk dla Indian)
            profit_for_natives = max(abs(total_cost - total_gain), 0)
            value_they_give_us = total_cost

            if value_they_give_us > 100 and profit_for_natives >= 2 * value_they_give_us:
                rep_change += 1

            if rep_change > 0:
                old_rel = self.native_relations[tribe]
                new_rel = min(100, old_rel + rep_change)
                self.native_relations[tribe] = new_rel
                self.log(
                    f"Relacje z {tribe}: +{rep_change} (nowe: {new_rel}/100).",
                    "purple"
                )

            trade_win.destroy()

        ttk.Button(trade_win, text="Wykonaj handel", command=execute_trade).pack(pady=10)
        ttk.Button(trade_win, text="Anuluj", command=trade_win.destroy).pack(pady=5)

    # === Dyplomacja z państwami europejskimi ===
    def diplomacy_menu(self):
        win = self.create_window("Dyplomacja")

        for state, rel in self.europe_relations.items():
            frame = ttk.Frame(win)
            frame.pack(fill="x", padx=20, pady=3)

            ttk.Label(frame, text=f"{state}: {rel}/100", width=25).pack(side="left")

            if state == self.state:
                ttk.Button(
                    frame,
                    text="Zamówienie",
                    command=lambda s=state: self.order_colonists(s)
                ).pack(side="right")

                ttk.Button(
                    frame,
                    text="Dar (+5)",
                    command=lambda s=state: self.send_diplomatic_gift(s)
                ).pack(side="right", padx=5)
            else:
                ttk.Button(
                    frame,
                    text="Handel",
                    command=lambda s=state: self.open_europe_trade(s, win)
                ).pack(side="right")

                ttk.Button(
                    frame,
                    text="Dar (+5)",
                    command=lambda s=state: self.send_diplomatic_gift(s)
                ).pack(side="right", padx=5)

        ttk.Label(
            win,
            text="Dar: koszt 10 złota + 250 żywności + 20 srebra + 15 stali"
        ).pack(pady=10)

        ttk.Button(win, text="Zamknij", command=win.destroy).pack(pady=10)

    def open_europe_trade(self, state, parent):
        """Handel z innym państwem za dukaty.
        Marża zależy liniowo od reputacji:
        - przy reputacji 0: sprzedaż 0.5x, kupno 1.5x
        - przy reputacji 100: sprzedaż 0.9x, kupno 1.1x
        Reputacja rośnie jak u Indian (progi 1000 + bonus za bardzo korzystny handel dla nich).
        """
        trade_win = self.create_window(f"Handel z {state}")

        def get_margins():
            rel = self.europe_relations.get(state, 0)
            t = max(0, min(100, rel)) / 100.0
            sell_mult = 0.5 + 0.4 * t
            buy_mult = 1.5 - 0.4 * t
            return sell_mult, buy_mult

        rel = self.europe_relations[state]
        sell_mult, buy_mult = get_margins()

        ttk.Label(
            trade_win,
            text=(
                f"Relacje z {state}: {rel}/100\n"
                f"Ceny zależą od reputacji (sprzedaż: {(sell_mult * 100):.0f}% ceny, "
                f"kupno: {(buy_mult * 100):.0f}% ceny)."
            ),
            justify="center"
        ).pack(pady=5)

        sell_frame = ttk.LabelFrame(trade_win, text="Sprzedajesz (otrzymujesz dukaty)")
        sell_frame.pack(fill="x", padx=15, pady=5)

        buy_frame = ttk.LabelFrame(trade_win, text="Kupujesz (płacisz dukaty)")
        buy_frame.pack(fill="x", padx=15, pady=5)

        sell_vars = {}
        buy_vars = {}

        def update_sums(*args):
            sell_mult, buy_mult = get_margins()
            total_gain = 0
            total_cost = 0

            for r, var in sell_vars.items():
                qty = self.safe_int(var)
                if qty > 0:
                    price = EUROPE_PRICES.get(r, 0) * sell_mult
                    total_gain += qty * price

            for r, var in buy_vars.items():
                qty = self.safe_int(var)
                if qty > 0:
                    price = EUROPE_PRICES.get(r, 0) * buy_mult
                    total_cost += qty * price

            self.sell_sum_lbl.config(text=f"Sprzedaż: +{int(total_gain)} dukatów")
            self.buy_sum_lbl.config(text=f"Kupno: -{int(total_cost)} dukatów")
            net = total_gain - total_cost
            self.net_sum_lbl.config(
                text=f"Bilans: {'+' if net >= 0 else ''}{int(net)} dukatów"
            )

        sum_frame = ttk.Frame(trade_win)
        sum_frame.pack(pady=8)

        self.sell_sum_lbl = ttk.Label(sum_frame, text="Sprzedaż: +0 dukatów", foreground="green")
        self.buy_sum_lbl = ttk.Label(sum_frame, text="Kupno: -0 dukatów", foreground="red")
        self.net_sum_lbl = ttk.Label(sum_frame, text="Bilans: 0 dukatów", foreground="blue")

        self.sell_sum_lbl.pack(side="left", padx=10)
        self.buy_sum_lbl.pack(side="left", padx=10)
        self.net_sum_lbl.pack(side="left", padx=10)

        sell_mult, buy_mult = get_margins()
        for res in EUROPE_PRICES.keys():
            if self.resources.get(res, 0) > 0:
                f = ttk.Frame(sell_frame)
                f.pack(fill="x", pady=1)
                ttk.Label(f, text=f"{res}", width=15).pack(side="left")
                var = tk.IntVar()
                spin = tk.Spinbox(
                    f,
                    from_=0,
                    to=self.resources[res],
                    textvariable=var,
                    width=8
                )
                spin.pack(side="right")
                price = int(EUROPE_PRICES[res] * sell_mult)
                ttk.Label(f, text=f"→ {price} duk./szt.").pack(side="right", padx=5)
                sell_vars[res] = var
                var.trace_add("write", update_sums)

            # KUPNO W EUROPIE ZABRONIONE DLA NIEKTÓRYCH TOWARÓW
            if res not in BLOCK_EUROPE_BUY or self.state != state:
                f = ttk.Frame(buy_frame)
                f.pack(fill="x", pady=1)
                ttk.Label(f, text=f"{res}", width=15).pack(side="left")

                var = tk.IntVar()
                spin = tk.Spinbox(f, from_=0, to=999, textvariable=var, width=8)
                spin.pack(side="right")

                price = int(EUROPE_PRICES[res] * buy_mult)
                ttk.Label(f, text=f"← {price} duk./szt.").pack(side="right", padx=5)

                buy_vars[res] = var
                var.trace_add("write", update_sums)

        update_sums()

        def execute_trade():
            sell = {r: self.safe_int(v) for r, v in sell_vars.items() if self.safe_int(v) > 0}
            buy = {r: self.safe_int(v) for r, v in buy_vars.items() if self.safe_int(v) > 0}

            if not sell and not buy:
                self.log("Brak transakcji!", "red")
                return

            sell_mult, buy_mult = get_margins()

            total_gain = sum(sell.get(r, 0) * EUROPE_PRICES.get(r, 0) * sell_mult for r in sell)
            total_cost = sum(buy.get(r, 0) * EUROPE_PRICES.get(r, 0) * buy_mult for r in buy)

            net = total_gain - total_cost

            for r, a in sell.items():
                if self.resources.get(r, 0) < a:
                    self.log(f"Za mało {r}, aby sprzedać!", "red")
                    return

            if self.resources["dukaty"] + net < 0:
                self.log("Za mało dukatów na tę transakcję!", "red")
                return

            for r, a in sell.items():
                self.resources[r] -= a
            for r, a in buy.items():
                self.resources[r] = self.resources.get(r, 0) + a

            self.resources["dukaty"] += net

            self.log(
                f"Handel z {state}: "
                f"{'zysk' if net > 0 else 'strata' if net < 0 else 'na zero'} "
                f"{abs(int(net))} dukatów.",
                "green" if net > 0 else "orange" if net < 0 else "gray"
            )

            trade_value = int(max(total_gain, total_cost))
            prev = self.europe_trade_value.get(state, 0)
            cumulative = prev + trade_value

            rep_from_volume = cumulative // self.trade_reputation_threshold
            self.europe_trade_value[state] = cumulative % self.trade_reputation_threshold

            rep_change = 0
            if rep_from_volume > 0:
                rep_change += rep_from_volume

            profit_for_them = max(total_cost - total_gain, 0)
            value_they_give_us = total_cost

            if value_they_give_us > 100 and profit_for_them >= 2 * value_they_give_us:
                rep_change += 1

            if rep_change > 0:
                old_rel = self.europe_relations.get(state, 0)
                new_rel = min(100, old_rel + rep_change)
                self.europe_relations[state] = new_rel
                self.log(
                    f"Relacje z {state}: +{rep_change} (nowe: {new_rel}/100).",
                    "purple"
                )

            trade_win.destroy()

        ttk.Button(trade_win, text="Wykonaj handel", command=execute_trade).pack(pady=10)
        ttk.Button(trade_win, text="Anuluj", command=trade_win.destroy).pack(pady=5)

    def send_diplomatic_gift(self, state):

        cost = {"złoto": 10, "żywność": 250, "srebro": 20, "stal": 15}
        if not self.can_afford(cost):
            self.log(f"Za mało na dar dla {state}!", "red")
            return
        self.spend_resources(cost)
        self.europe_relations[state] = min(100, self.europe_relations[state] + 5)
        self.log(f"Dar do {state}: +5 relacji", "purple")

    def try_generate_native_missions(self):
        """Co dzień wywoływane: sprawdza, czy jakieś plemię powinno dostać misję."""

        if self.current_date < self.native_missions_enabled_start:
            return  # system jeszcze nie wystartował

        for tribe in self.native_relations.keys():

            # 1. Jeśli misja już trwa – sprawdź czy wygasła
            active = self.native_missions_active.get(tribe)
            if active:
                end = active["end"]
                if self.current_date >= end:
                    # MISJA NIEWYKONANA → kara
                    self.native_relations[tribe] = max(
                        0, self.native_relations[tribe] - 15
                    )
                    self.log(
                        f"Misja od {tribe} wygasła! Kara -15 reputacji.",
                        "red"
                    )
                    self.native_missions_active[tribe] = None
                    # cooldown 2–3 miesiące
                    cd = random.randint(60, 90)
                    self.native_missions_cd[tribe] = self.current_date + timedelta(days=cd)
                continue

            # 2. Jeśli brak misji aktywnej, ale cooldown trwa → nic nie rób
            cd_until = self.native_missions_cd.get(tribe)
            if cd_until and self.current_date < cd_until:
                continue

            # 3. Losowa szansa — np. 1/14 że dziś dane plemię poprosi o misję
            # żeby nie waliło się wszystko naraz
            if random.random() > 1 / 14:
                continue

            # 4. Generuj misję
            self.generate_native_mission(tribe)

    def generate_native_mission(self, tribe):
        """Tworzy nową misję dla konkretnego plemienia."""

        # pierwszy raz? ustaw mnożnik
        if tribe not in self.native_mission_multiplier:
            self.native_mission_multiplier[tribe] = 1.0
        else:
            # rośnie jak w misjach królewskich
            self.native_mission_multiplier[tribe] *= random.uniform(1.05, 1.12)

        multiplier = self.native_mission_multiplier[tribe]

        # wybór misji
        idx = random.randint(0, len(NATIVE_MISSIONS_DETAILS) - 1)
        data = NATIVE_MISSIONS_DETAILS[idx]

        # wymagania
        required = {
            res: max(1, int(base * multiplier))
            for res, base in data["base"].items()
        }

        # czas trwania 3–6 miesięcy
        months = random.randint(3, 6)
        end_date = self.current_date + timedelta(days=30 * months)

        mission = {
            "tribe": tribe,
            "name": data["name"],
            "desc": data.get("desc", ""),
            "required": required,
            "sent": {},
            "end": end_date,
            "months_limit": months,
            "idx": idx,
        }

        self.native_missions_active[tribe] = mission
        self.log(
            f"Nowa misja od plemienia {tribe}: {data['name']}. "
            f"Czas: {months} miesięcy.",
            "purple"
        )
        self.play_sound("new_mission")

        def deliver_to_native_mission(self, tribe, resources):
            """resources = dict {res: amount} wysłanych towarów."""

            mission = self.native_missions_active.get(tribe)
            if not mission:
                self.log(f"{tribe} nie ma aktywnej misji.", "gray")
                return False

            req = mission["required"]
            sent = mission["sent"]

            # dodaj zasoby
            for r, amount in resources.items():
                if r in req:
                    need = req[r] - sent.get(r, 0)
                    add = min(amount, need)
                    sent[r] = sent.get(r, 0) + add

            # sprawdzenie, czy skończone
            completed = all(sent.get(r, 0) >= req[r] for r in req)

            if completed:
                remaining_days = (mission["end"] - self.current_date).days
                full_months_left = max(0, remaining_days // 30)

                reward = 5 + full_months_left * 2

                self.native_relations[tribe] = min(
                    100, self.native_relations[tribe] + reward
                )
                self.log(
                    f"Misja od {tribe} wykonana! Nagroda: +{reward} reputacji.",
                    "green"
                )

                self.native_missions_active[tribe] = None

                # cooldown 2–3 miesiące
                cd = random.randint(60, 90)
                self.native_missions_cd[tribe] = self.current_date + timedelta(days=cd)

            return True
