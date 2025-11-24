import tkinter as tk
from datetime import timedelta
from tkinter import ttk
import random

from constants import (
    NATIVE_PRICES,
    EUROPE_PRICES,
    STATES,
    NATIVE_MISSIONS_DETAILS,
    BLOCK_NATIVE_BUY,
    BLOCK_EUROPE_BUY, TRIBE_DISPLAY_KEYS, RESOURCE_DISPLAY_KEYS,
)


class RelationsMixin:

    def safe_int(self, var):
        try:
            return int(var.get())
        except Exception:
            return 0

    def state_name(self, state_id: str) -> str:
        data = STATES.get(state_id, {})
        key = data.get("name_key")
        return self.loc.t(key, default=state_id) if key else state_id

    def res_name(self, res_id: str) -> str:
        key = RESOURCE_DISPLAY_KEYS.get(res_id, res_id)
        return self.loc.t(key, default=res_id)

    # === WSPÓLNY HELPER DO WIERSZY HANDLU (spinbox + pionowe przyciski) ===
    def _create_trade_row(self, parent, res_name, max_q, unit_price,
                          price_prefix, on_change, with_max, stock_info=None):
        """
        Tworzy wiersz:
        [nazwa towaru] [Spinbox] [kolumny +1/-1, +10/-10, +100/-100, (opcjonalnie Max)] [etykieta ceny]
        Zwraca IntVar powiązany ze spinboxem.
        """
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=1)

        res_key = RESOURCE_DISPLAY_KEYS.get(res_name, res_name)
        nice_name = self.loc.t(res_key, default=res_name)

        label_text = nice_name if not stock_info else f"{nice_name } ({stock_info})"
        ttk.Label(frame, text=label_text, width=28 if stock_info else 15).pack(side="left")

        var = tk.IntVar(value=0)
        spin = tk.Spinbox(
            frame,
            from_=0,
            to=max_q,
            textvariable=var,
            width=5
        )
        spin.pack(side="left", padx=(0, 4))

        btn_col = ttk.Frame(frame)
        btn_col.pack(side="left", padx=2)

        def adjust(delta, v=var, m=max_q):
            try:
                cur = int(v.get())
            except Exception:
                cur = 0
            new = max(0, min(m, cur + delta))
            v.set(new)
            on_change()

        def add_pair(parent, txt_plus, d_plus, txt_minus, d_minus):
            col = ttk.Frame(parent)
            col.pack(side="left", padx=1)
            ttk.Button(col, text=txt_plus, width=5, padding=(3, -2),
                       command=lambda d=d_plus: adjust(d)).pack()
            ttk.Button(col, text=txt_minus, width=5, padding=(3, -2),
                       command=lambda d=d_minus: adjust(d)).pack()

        # kolumny: (+1/-1), (+10/-10), (+100/-100)
        add_pair(btn_col, "+1", 1, "-1", -1)
        add_pair(btn_col, "+10", 10, "-10", -10)
        add_pair(btn_col, "+100", 100, "-100", -100)

        if with_max:
            ttk.Button(
                btn_col,
                text=self.loc.t("ui.max_btn"),
                width=4,
                command=lambda v=var, m=max_q: (v.set(m), on_change())
            ).pack(side="left", padx=(4, 0), pady=(2, 0))

        ttk.Label(frame, text=f"{price_prefix} {unit_price}").pack(side="left", padx=5)

        # reaguj także na ręczną zmianę w spinboxie
        var.trace_add("write", lambda *args: on_change())

        return var

    def tribe_name(self, tribe: str) -> str:
        """Zwraca zlokalizowaną nazwę plemienia dla UI."""
        key = TRIBE_DISPLAY_KEYS.get(tribe)
        return self.loc.t(key, default=tribe) if key else tribe

    # === Relacje z Indianami ===
    def native_menu(self):
        win = self.create_window(self.loc.t("screen.native_menu.title"))
        for tribe in self.native_relations:
            rel = self.native_relations[tribe]
            frame = ttk.Frame(win)
            frame.pack(fill="x", padx=20, pady=3)

            ttk.Label(frame, text=f"{self.tribe_name(tribe)}: {rel}/100", width=25).pack(side="left")

            ttk.Button(
                frame,
                text=self.loc.t("ui.integrate_btn"),
                command=lambda t=tribe: self.integrate_natives(t)
            ).pack(side="right", padx=5)

            ttk.Button(
                frame,
                text=self.loc.t("ui.trade_btn"),
                command=lambda t=tribe: self.open_native_trade(t, win)
            ).pack(side="right", padx=5)

        ttk.Button(win, text=self.loc.t("ui.close"), command=win.destroy).pack(pady=10)

        # wyśrodkuj okno handlu z Indianami (lista plemion)
        self.center_window(win)

    def integrate_natives(self, tribe):
        """Integracja Indian z danym plemieniem: 1 osoba za 10 reputacji z tym plemieniem."""
        current_rel = self.native_relations.get(tribe, 0)

        if current_rel < 80:
            self.log(
                self.loc.t("log.integrate_not_enough_rep_min", tribe=self.tribe_name(tribe)),
                "red"
            )
            return

        max_people = current_rel // 10

        if max_people <= 0:
            self.log(
                self.loc.t("log.integrate_no_rep", tribe=self.tribe_name(tribe)),
                "red"
            )
            return

        win = self.create_window(self.loc.t("screen.integrate_native.title", tribe=self.tribe_name(tribe)))

        win.geometry("460x320")
        win.resizable(False, False)

        ttk.Label(
            win,
            text=self.loc.t("screen.integrate_native.header", tribe=self.tribe_name(tribe)),
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        ttk.Label(
            win,
            text=self.loc.t(
                "screen.integrate_native.info",
                rel=current_rel,
                max_people=max_people
            ),
            justify="center"
        ).pack(pady=5)

        amount_frame = ttk.Frame(win)
        amount_frame.pack(pady=10, fill="x", padx=20)

        ttk.Label(
            amount_frame,
            text=self.loc.t("screen.integrate_native.amount_label"),
            font=("Arial", 10)
        ).pack(anchor="w")

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
            text=self.loc.t("screen.integrate_native.amount_cost_one"),
            foreground="blue",
            font=("Arial", 11, "bold")
        )
        amount_lbl.pack(anchor="w")

        def update_amount_label(*_):
            n = amount_var.get()
            amount_lbl.config(
                text=self.loc.t(
                    "screen.integrate_native.amount_cost_n",
                    n=n,
                    cost=n * 10
                )
            )

        amount_var.trace_add("write", update_amount_label)

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=15)

        def confirm_integration():
            n = amount_var.get()
            cost = n * 10

            have = self.native_relations.get(tribe, 0)
            if have < cost:
                self.log(
                    self.loc.t("log.integrate_not_enough_rep_cost", tribe=self.tribe_name(tribe), cost=cost, have=have),
                    "red"
                )
                return

            self.native_relations[tribe] -= cost
            self.people += n

            self.log(
                self.loc.t("log.integrate_done", n=n, tribe=self.tribe_name(tribe), cost=cost),
                "purple"
            )

            win.destroy()

        ttk.Button(btn_frame, text=self.loc.t("ui.integrate"), command=confirm_integration).pack(side="left", padx=8)
        ttk.Button(btn_frame, text=self.loc.t("ui.cancel"), command=win.destroy).pack(side="left", padx=8)

        # wyśrodkuj okno integracji
        self.center_window(win)

    def get_native_price_modifier(self, rel):
        rel_norm = rel / 100.0
        sell_mod = 0.01 + 0.99 * rel_norm
        buy_mod = 2.0 - rel_norm
        if rel == 100:
            sell_mod, buy_mod = 1.5, 0.5
        if self.state == "england":
            sell_mod += STATES[self.state]["trade"]
            buy_mod -= STATES[self.state]["trade"]
        return sell_mod, buy_mod

    def open_native_trade(self, tribe, parent):
        """Handel z Indianami — UI takie jak handel z państwami,
        ale zamiast dukatów jest bilans ilościowy (value units)."""

        trade_win = self.create_window(
            self.loc.t("screen.native_trade.title", tribe=tribe)
        )
        trade_win.geometry("500x1200")  # stały rozmiar
        trade_win.resizable(False, False)


        rel = self.native_relations[tribe]
        sell_mod, buy_mod = self.get_native_price_modifier(rel)
        if self.state == "england":
            sell_mod += STATES[self.state]["trade"]
            buy_mod -= STATES[self.state]["trade"]

        blocked_txt = (self.res_name(r) for r in sorted(BLOCK_NATIVE_BUY))

        info_text = (
                self.loc.t("screen.native_trade.relations_line", tribe=self.tribe_name(tribe), rel=rel) + "\n" +
                self.loc.t("screen.native_trade.prices_line", sell_mod=sell_mod, buy_mod=buy_mod) + "\n" +
                self.loc.t("screen.native_trade.blocked_buy_line",
                           blocked=", ".join(blocked_txt))
        )

        ttk.Label(trade_win, text=info_text, justify="center").pack(pady=5)

        # --- SEKCJE (tak jak u Europejczyków) ---
        sell_frame = ttk.LabelFrame(trade_win, text=self.loc.t("screen.native_trade.sell_frame"))
        sell_frame.pack(fill="x", padx=15, pady=5)

        buy_frame = ttk.LabelFrame(trade_win, text=self.loc.t("screen.native_trade.buy_frame"))
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

            self.sell_sum_lbl.config(
                text=self.loc.t("screen.trade.summary_sell_value", gain=int(total_gain))
            )
            self.buy_sum_lbl.config(
                text=self.loc.t("screen.trade.summary_buy_value", cost=int(total_cost))
            )
            self.net_sum_lbl.config(
                text=self.loc.t("screen.trade.summary_net_value",
                                sign="+" if net >= 0 else "",
                                net=int(net))
            )

        sum_frame = ttk.Frame(trade_win)
        sum_frame.pack(pady=8)

        self.sell_sum_lbl = ttk.Label(sum_frame, text=self.loc.t("screen.trade.summary_sell_value", gain=0))
        self.buy_sum_lbl = ttk.Label(sum_frame, text=self.loc.t("screen.trade.summary_buy_value", cost=0))
        self.net_sum_lbl = ttk.Label(sum_frame, text=self.loc.t("screen.trade.summary_net_value", sign="", net=0))

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
                max_q = self.resources[res]
                var_s = self._create_trade_row(
                    parent=sell_frame,
                    res_name=res,
                    max_q=max_q,
                    unit_price=sell_price,
                    price_prefix="→",
                    on_change=update_sums,
                    with_max=True
                )
                sell_vars[res] = var_s

            # --- KUPNO U INDIAN ---
            if res not in BLOCK_NATIVE_BUY:
                native_stock = self.native_stock.get(tribe, {}).get(res, 0)
                max_q_buy = int(native_stock)
                debug_prod = self.native_prod.get(tribe, {}).get(res, 0)
                stock_info = self.loc.t(
                    "debug.native_stock_info",
                    stock=max_q_buy,
                    prod=f"{debug_prod:.1f}"
                )
                var_b = self._create_trade_row(
                    parent=buy_frame,
                    res_name=res,
                    max_q=max_q_buy,
                    unit_price=buy_price,
                    price_prefix="←",
                    on_change=update_sums,
                    with_max=True,
                    stock_info=stock_info
                )
                buy_vars[res] = var_b

        update_sums()

        # --- WYKONANIE TRANSAKCJI (zmodyfikowana wersja europejskiej) ---
        def execute_trade():
            sell = {r: self.safe_int(v) for r, v in sell_vars.items() if self.safe_int(v) > 0}
            buy = {r: self.safe_int(v) for r, v in buy_vars.items() if self.safe_int(v) > 0}

            if not sell and not buy:
                self.log(self.loc.t("log.trade_no_transaction"), "red")
                return

            total_gain = sum(sell.get(r, 0) * NATIVE_PRICES[r] * sell_mod for r in sell)
            total_cost = sum(buy.get(r, 0) * NATIVE_PRICES[r] * buy_mod for r in buy)

            # Zasoby wystarczą?
            for r, a in sell.items():
                if self.resources[r] < a:
                    self.log(self.loc.t("log.trade_not_enough_to_sell", res=r), "red")
                    return

            net = total_gain - total_cost
            if net < 0:
                # u Indian nie ma dukatów → bilans musi być >= 0
                self.log(self.loc.t("log.native_trade_negative_balance"), "red")
                return

            # wykonanie handlu
            for r, a in sell.items():
                self.resources[r] -= a
                # Indianie dostają towar do swojego magazynu (jeśli go śledzimy)
                if r in self.native_stock.get(tribe, {}):
                    cap = self.native_cap[tribe].get(r, 0)
                    cur = self.native_stock[tribe].get(r, 0)
                    self.native_stock[tribe][r] = min(cap, cur + a)

            for r, a in buy.items():
                self.resources[r] += a
                # Indianie sprzedają ze swojego stanu
                if r in self.native_stock.get(tribe, {}):
                    cur = self.native_stock[tribe].get(r, 0)
                    self.native_stock[tribe][r] = max(0, cur - a)

            net_word = (
                self.loc.t("screen.trade.net_gain") if net > 0
                else self.loc.t("screen.trade.net_zero")
            )
            self.log(
                self.loc.t("log.native_trade_result",
                           tribe=self.tribe_name(tribe), net_word=net_word, amount=int(net)),
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
                    self.loc.t("log.native_rel_change", tribe=self.tribe_name(tribe), rep_change=rep_change, new_rel=new_rel),
                    "purple"
                )

            trade_win.destroy()

        ttk.Button(trade_win, text=self.loc.t("ui.execute_trade"), command=execute_trade).pack(pady=10)
        ttk.Button(trade_win, text=self.loc.t("ui.cancel"), command=trade_win.destroy).pack(pady=5)

        # wyśrodkuj okno integracji
        self.center_window(trade_win)

    # === Dyplomacja z państwami europejskimi ===
    def diplomacy_menu(self):
        win = self.create_window(self.loc.t("screen.diplomacy.title"))

        for state, rel in self.europe_relations.items():
            frame = ttk.Frame(win)
            frame.pack(fill="x", padx=20, pady=3)

            ttk.Label(frame, text=f"{self.state_name(state)}: {rel}/100", width=25).pack(side="left")

            if state == self.state:
                ttk.Button(
                    frame,
                    text=self.loc.t("screen.diplomacy.order_button"),
                    command=lambda s=state: self.order_colonists(s)
                ).pack(side="right")

                ttk.Button(
                    frame,
                    text=self.loc.t("screen.diplomacy.gift_button"),
                    command=lambda s=state: self.send_diplomatic_gift(s)
                ).pack(side="right", padx=5)
            else:
                ttk.Button(
                    frame,
                    text=self.loc.t("ui.trade_btn"),
                    command=lambda s=state: self.open_europe_trade(s, win)
                ).pack(side="right")

                ttk.Button(
                    frame,
                    text=self.loc.t("ui.gift_btn_short"),
                    command=lambda s=state: self.send_diplomatic_gift(s)
                ).pack(side="right", padx=5)

        ttk.Label(
            win,
            text=self.loc.t("ui.gift_cost_line")
        ).pack(pady=10)

        ttk.Button(
            win,
            text=self.loc.t("ui.close_btn"),
            command=win.destroy
        ).pack(pady=10)

        # wyśrodkuj okno handlu z Indianami (lista plemion)
        self.center_window(win)

    def open_europe_trade(self, state, parent):
        """Handel z innym państwem za dukaty.
        Marża zależy liniowo od reputacji:
        - przy reputacji 0: sprzedaż 0.5x, kupno 1.5x
        - przy reputacji 100: sprzedaż 0.9x, kupno 1.1x
        Reputacja rośnie jak u Indian (progi 1000 + bonus za bardzo korzystny handel dla nich).
        """
        state_disp = self.state_name(state)
        trade_win = self.create_window(self.loc.t("screen.europe_trade.title", state=state_disp))

        trade_win.geometry("500x1350")  # stały rozmiar
        trade_win.resizable(False, False)

        def get_margins():
            rel = self.europe_relations.get(state, 0)
            t = max(0, min(100, rel)) / 100.0
            sell_mult = 0.5 + 0.4 * t
            buy_mult = 1.5 - 0.4 * t
            return sell_mult, buy_mult

        rel = self.europe_relations[state]
        sell_mult, buy_mult = get_margins()

        blocked_txt = (self.res_name(r) for r in sorted(BLOCK_EUROPE_BUY))

        info_text = (
                self.loc.t("screen.europe_trade.relations_line", state=state_disp, rel=rel) + "\n" +
                self.loc.t("screen.europe_trade.prices_line",
                           sell_pct=(sell_mult * 100), buy_pct=(buy_mult * 100)) + "\n" +
                self.loc.t("screen.europe_trade.blocked_buy_line",
                           blocked=", ".join(blocked_txt))
        )
        ttk.Label(trade_win, text=info_text, justify="center").pack(pady=5)

        sell_frame = ttk.LabelFrame(trade_win, text=self.loc.t("screen.europe_trade.sell_frame"))
        sell_frame.pack(fill="x", padx=15, pady=5)

        buy_frame = ttk.LabelFrame(trade_win, text=self.loc.t("screen.europe_trade.buy_frame"))
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

            self.sell_sum_lbl.config(
                text=self.loc.t("screen.trade.summary_sell_ducats", gain=int(total_gain))
            )
            self.buy_sum_lbl.config(
                text=self.loc.t("screen.trade.summary_buy_ducats", cost=int(total_cost))
            )
            net = total_gain - total_cost
            self.net_sum_lbl.config(
                text=self.loc.t("screen.trade.summary_net_ducats",
                                sign="+" if net >= 0 else "",
                                net=int(net))
            )

        sum_frame = ttk.Frame(trade_win)
        sum_frame.pack(pady=8)

        self.sell_sum_lbl = ttk.Label(sum_frame, text=self.loc.t("screen.trade.summary_sell_ducats", gain=0))
        self.buy_sum_lbl = ttk.Label(sum_frame, text=self.loc.t("screen.trade.summary_buy_ducats", cost=0))
        self.net_sum_lbl = ttk.Label(sum_frame, text=self.loc.t("screen.trade.summary_net_ducats", sign="", net=0))

        self.sell_sum_lbl.pack(side="left", padx=10)
        self.buy_sum_lbl.pack(side="left", padx=10)
        self.net_sum_lbl.pack(side="left", padx=10)

        sell_mult, buy_mult = get_margins()
        for res in EUROPE_PRICES.keys():
            have = self.resources.get(res, 0)

            # SPRZEDAŻ
            if have > 0:
                max_q = have
                price = int(EUROPE_PRICES[res] * sell_mult)
                var_s = self._create_trade_row(
                    parent=sell_frame,
                    res_name=res,
                    max_q=max_q,
                    unit_price=price,
                    price_prefix="→",
                    on_change=update_sums,
                    with_max=True
                )
                sell_vars[res] = var_s

            # KUPNO W EUROPIE ZABRONIONE DLA NIEKTÓRYCH TOWARÓW TYLKO WE WŁASNYM KRAJU
            if res not in BLOCK_EUROPE_BUY or self.state != state:
                max_q_buy = 999
                price_b = int(EUROPE_PRICES[res] * buy_mult)
                var_b = self._create_trade_row(
                    parent=buy_frame,
                    res_name=res,
                    max_q=max_q_buy,
                    unit_price=price_b,
                    price_prefix="←",
                    on_change=update_sums,
                    with_max=False
                )
                buy_vars[res] = var_b

        update_sums()

        def execute_trade():
            sell = {r: self.safe_int(v) for r, v in sell_vars.items() if self.safe_int(v) > 0}
            buy = {r: self.safe_int(v) for r, v in buy_vars.items() if self.safe_int(v) > 0}

            if not sell and not buy:
                self.log(self.loc.t("log.trade_no_transaction"), "red")
                return

            sell_mult, buy_mult = get_margins()

            total_gain = sum(sell.get(r, 0) * EUROPE_PRICES.get(r, 0) * sell_mult for r in sell)
            total_cost = sum(buy.get(r, 0) * EUROPE_PRICES.get(r, 0) * buy_mult for r in buy)

            net = total_gain - total_cost

            for r, a in sell.items():
                if self.resources.get(r, 0) < a:
                    self.log(self.loc.t("log.trade_not_enough_resource_generic", res=r), "red")
                    return

            if self.resources["ducats"] + net < 0:
                self.log(self.loc.t("log.trade_not_enough_ducats"), "red")
                return

            for r, a in sell.items():
                self.resources[r] -= a
            for r, a in buy.items():
                self.resources[r] = self.resources.get(r, 0) + a

            self.resources["ducats"] += net

            net_word = (
                self.loc.t("screen.trade.net_gain") if net > 0
                else self.loc.t("screen.trade.net_loss") if net < 0
                else self.loc.t("screen.trade.net_zero")
            )

            self.log(
                self.loc.t("log.europe_trade_result",
                           state=self.state_name(state), net_word=net_word, amount=abs(int(net))),
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
                    self.loc.t("log.europe_relations_change",
                               state=self.state_name(state), rep_change=rep_change, new_rel=new_rel),
                    "purple"
                )

            trade_win.destroy()

        ttk.Button(trade_win, text=self.loc.t("ui.execute_trade"), command=execute_trade).pack(pady=10)
        ttk.Button(trade_win, text=self.loc.t("ui.cancel"), command=trade_win.destroy).pack(pady=5)

        # wyśrodkuj okno integracji
        self.center_window(trade_win)

    def send_diplomatic_gift(self, state):

        cost = {"gold": 10, "food": 250, "silver": 20, "steel": 15}
        if not self.can_afford(cost):
            self.log(self.loc.t("log.gift_not_enough", state=self.state_name(state)), "red")
            return
        self.spend_resources(cost)
        self.europe_relations[state] = min(100, self.europe_relations[state] + 5)
        self.log(self.loc.t("log.gift_sent", state=self.state_name(state)), "purple")

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
                        self.loc.t("log.native_mission_expired", tribe=self.tribe_name(tribe)),
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
            "name_key": data["name_key"],
            "desc_key": data.get("desc_key", ""),
            "required": required,
            "sent": {},
            "end": end_date,
            "months_limit": months,
            "idx": idx,
        }

        self.native_missions_active[tribe] = mission

        mission_name = self.loc.t(data["name_key"], default=data["name_key"])
        self.log(
            self.loc.t(
                "log.native_mission_new",
                tribe=self.tribe_name(tribe),
                name=mission_name,
                months=months
            ),
            "purple"
        )
        self.play_sound("new_mission")

    def deliver_to_native_mission(self, tribe, resources):
        """resources = dict {res: amount} wysłanych towarów."""

        mission = self.native_missions_active.get(tribe)
        if not mission:
            self.log(self.loc.t("log.native_mission_none", tribe=self.tribe_name(tribe)), "gray")
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
                self.loc.t("log.native_mission_done", tribe=self.tribe_name(tribe), reward=reward),
                "green"
            )

            self.native_missions_active[tribe] = None

            # cooldown 2–3 miesiące
            cd = random.randint(60, 90)
            self.native_missions_cd[tribe] = self.current_date + timedelta(days=cd)

        return True
