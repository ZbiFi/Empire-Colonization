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

        if not self.first_mission_given:
            self.mission_multiplier = 1
            self.first_mission_given = True

        else:
            self.mission_multiplier *= growth
        difficulty = int(self.mission_multiplier * 10) / 10  # <-- jak wcześniej

        required = {}
        missionName = mission["name"]
        for res, base_amt in mission["base"].items():
            required[res] = max(1, int(base_amt * self.mission_multiplier))

        end_date = self.current_date + timedelta(days=365)
        monarch = self.get_monarch()
        mission_text = (
            f"Jego Królewska Mość {monarch} żąda na {missionName}: " +
            ", ".join(f"{v} {res}" for res, v in required.items()) +
            f". Termin: {end_date.strftime('%d %b %Y')}  (1 rok). "
        )

        # (end_date, required, sent, difficulty, mission_text, mission_idx)
        self.current_mission = (end_date, required.copy(), {}, difficulty, mission_text, mission_idx)
        self.log(mission_text, "purple")
        self.play_sound("new_mission")

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
        self.complete_royal_mission()

    def show_missions_overview(self):
        """Okno zbiorcze: misja królewska + (w przyszłości) misje indiańskie."""
        win = tk.Toplevel(self.root)
        win.title("Misje")

        # === Sekcja: misje królewskie ===
        royal_frame = ttk.LabelFrame(win, text="Misja królewska")
        royal_frame.pack(fill="x", padx=10, pady=10)

        if self.current_mission:
            end, req, sent, diff, text, idx = self.current_mission

            ttk.Label(
                royal_frame,
                text=text,
                wraplength=550,
                justify="left"
            ).pack(pady=5, anchor="w")

            ttk.Label(
                royal_frame,
                text=f"Termin: {end.strftime('%d %b %Y')} (pozostało {(end - self.current_date).days} dni)",
                foreground="red"
            ).pack(pady=2, anchor="w")

            prog_frame = ttk.Frame(royal_frame)
            prog_frame.pack(pady=5, fill="x")

            for r in req:
                have = sent.get(r, 0)
                need = req[r]
                if have >= need:
                    color = "green"
                elif have > 0:
                    color = "orange"
                else:
                    color = "red"
                ttk.Label(
                    prog_frame,
                    text=f"{r}: {have}/{need}",
                    foreground=color
                ).pack(anchor="w")

            ttk.Button(
                royal_frame,
                text="Szczegóły misji królewskiej",
                command=self.show_mission_window
            ).pack(pady=5, anchor="w")

        else:
            ttk.Label(
                royal_frame,
                text="Brak aktywnej misji królewskiej.",
                foreground="gray"
            ).pack(pady=5, anchor="w")

        # === Sekcja: misje indiańskie (przygotowane pod przyszłe funkcje) ===
        native_frame = ttk.LabelFrame(win, text="Misje indiańskie")
        native_frame.pack(fill="x", padx=10, pady=5)

        missions = getattr(self, "native_missions", [])

        if missions:
            for m in missions:
                tribe = m.get("tribe", "Nieznane plemię")
                text = m.get("text", "")
                end = m.get("end", None)
                progress = m.get("progress", "")

                line = f"{tribe}: {text}"
                if end:
                    line += f" (termin: {end.strftime('%d %b %Y')})"
                if progress:
                    line += f" | Postęp: {progress}"

                ttk.Label(native_frame, text=line, wraplength=550, justify="left").pack(
                    pady=2, anchor="w"
                )
        else:
            ttk.Label(
                native_frame,
                text="Brak aktywnych misji od plemion indiańskich.\n(Pojawią się w przyszłych aktualizacjach.)",
                foreground="gray",
                justify="left"
            ).pack(pady=5, anchor="w")

        ttk.Button(win, text="Zamknij", command=win.destroy).pack(pady=10)
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

    def complete_royal_mission(self):
        """Wywoływane po ukończeniu misji królewskiej."""
        self.completed_missions += 1
        self.mission_counter_label.config(
            text=f"Misje królewskie wykonane: {self.completed_missions} / {self.missions_to_win}"
        )

        # self.log("Misja królewska wykonana!", "green")
        self.current_mission = None

        if self.completed_missions >= self.missions_to_win:
            self.win_game()

    def win_game(self):
        win = tk.Toplevel(self.root)
        win.title("ZWYCIĘSTWO!")

        ttk.Label(
            win,
            text="🎉 WYGRAŁEŚ! 🎉",
            font=("Arial", 22, "bold"),
            foreground="green"
        ).pack(pady=20)

        ttk.Label(
            win,
            text=f"Wykonałeś {self.missions_to_win} królewskich misji.\nKolonia stała się legendą!",
            font=("Arial", 12)
        ).pack(pady=10)

        ttk.Button(win, text="Zakończ grę", command=self.root.quit).pack(pady=15)