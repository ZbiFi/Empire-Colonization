# missions.py
import random
from datetime import timedelta
import tkinter as tk
from tkinter import ttk

from constants import ROYAL_MISSIONS, EUROPE_PRICES


class MissionsMixin:
    def deliver_new_mission(self):
        mission_idx = random.randint(0, len(ROYAL_MISSIONS) - 1)
        mission = ROYAL_MISSIONS[mission_idx]

        growth = random.uniform(1.05, 1.15)
        self.mission_multiplier *= growth
        difficulty = int(self.mission_multiplier * 10) / 10  # <-- jak wcześniej

        required = {}
        for res, base_amt in mission["base"].items():
            required[res] = max(1, int(base_amt * self.mission_multiplier))

        end_date = self.current_date + timedelta(days=365)
        monarch = self.get_monarch()
        mission_text = (
            f"Jego Królewska Mość {monarch} żąda: " +
            ", ".join(f"{v} {res}" for res, v in required.items()) +
            f". Termin: {end_date.strftime('%d %b %Y')}  (1 rok)."
        )

        # (end_date, required, sent, difficulty, mission_text, mission_idx)
        self.current_mission = (end_date, required.copy(), {}, difficulty, mission_text, mission_idx)
        self.log(mission_text, "purple")

    def pay_mission_with_gold(self):
        if not self.current_mission:
            self.log("Brak aktywnej misji!", "red")
            return

        end, req, sent, diff, text, idx = self.current_mission

        # czego jeszcze brakuje
        remaining = {r: req[r] - sent.get(r, 0) for r in req if sent.get(r, 0) < req[r]}
        if not remaining:
            self.log("Misja już wykonana!", "gray")
            return

        # wartość brakujących towarów wg cen europejskich
        total_value = sum(a * EUROPE_PRICES.get(r, 10) for r, a in remaining.items())

        # *** TU ZMIANA ***
        # zamiast stałego 1.5 bierzemy poziom trudności diff jako mnożnik
        # (możesz to łatwo zmienić, np. na diff * 1.2, jeśli będzie za tanio/drogo)
        cost = int(total_value * diff)

        if self.resources["dukaty"] < cost:
            self.log(f"Za mało dukatów! Potrzeba: {cost}", "red")
            return

        self.resources["dukaty"] -= cost
        self.log(f"Misja opłacona dukatami: {cost}. +reputacja", "gold")

        # nagroda jak poprzednio
        self.europe_relations[self.state] = min(100, self.europe_relations[self.state] + 10 * diff)
        self.current_mission = None

    def show_mission_window(self):
        if not self.current_mission:
            self.log("Brak aktywnej misji.", "gray")
            return

        win = tk.Toplevel(self.root)
        win.title("Misja Królewska")
        end, req, sent, diff, text, idx = self.current_mission

        ttk.Label(win, text=text, wraplength=500, justify="center", font=("Arial", 11)).pack(pady=10)
        ttk.Label(win, text=f"Pozostało: {(end - self.current_date).days} dni", foreground="red").pack(pady=5)

        # POSTĘP MISJI
        frame = ttk.Frame(win)
        frame.pack(pady=10)
        for r in req:
            have = sent.get(r, 0)
            need = req[r]
            color = "green" if have >= need else "orange" if have > 0 else "red"
            ttk.Label(frame, text=f"{r}: {have}/{need}", foreground=color).pack()

        # KOSZT DUKATÓW – liczony tak samo jak w pay_mission_with_gold
        remaining = {r: req[r] - sent.get(r, 0) for r in req if sent.get(r, 0) < req[r]}
        if remaining:
            total_value = sum(a * EUROPE_PRICES.get(r, 10) for r, a in remaining.items())
            dukaty_cost = int(total_value * diff)   # *** też tylko ta linijka zmieniona względem starej wersji ***

            cost_lbl = ttk.Label(
                win,
                text=f"Koszt spłacenia dukatami: {dukaty_cost}",
                foreground="orange",
                font=("Arial", 10, "bold")
            )
            cost_lbl.pack(pady=5)
        else:
            ttk.Label(
                win,
                text="Misja już wykonana!",
                foreground="green",
                font=("Arial", 10, "bold")
            ).pack(pady=5)

        ttk.Button(
            win,
            text="Opłać dukatami",
            command=lambda: [self.pay_mission_with_gold(), win.destroy()]
        ).pack(pady=10)
        ttk.Button(win, text="Zamknij", command=win.destroy).pack(pady=5)
