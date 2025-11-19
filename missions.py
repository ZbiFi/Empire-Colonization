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
        """Okno zbiorcze wszystkich misji: królewskich i indiańskich.
           Z tego okna można natychmiast wypełnić misje (bez handlu, bez opóźnień).
        """

        win = tk.Toplevel(self.root)
        win.title("Misje")
        win.geometry("650x700")

        # ============================
        # 1. MISJA KRÓLEWSKA
        # ============================
        royal_frame = ttk.LabelFrame(win, text="Misja królewska")
        royal_frame.pack(fill="x", padx=10, pady=10)

        if self.current_mission:
            end, req, sent, diff, text, idx = self.current_mission

            ttk.Label(
                royal_frame,
                text=text,
                wraplength=600,
                justify="left"
            ).pack(pady=5, anchor="w")

            ttk.Label(
                royal_frame,
                text=f"Termin: {end.strftime('%d %b %Y')} "
                     f"(pozostało {(end - self.current_date).days} dni)",
                foreground="red"
            ).pack(anchor="w", pady=3)

            # POSTĘP
            for r in req:
                have = sent.get(r, 0)
                need = req[r]
                color = "green" if have >= need else ("orange" if have > 0 else "red")
                ttk.Label(
                    royal_frame,
                    text=f"{r}: {have}/{need}",
                    foreground=color
                ).pack(anchor="w")

            # ============================
            # PRZYCISK – NATYCHMIAST WYKONAJ
            # ============================
            def complete_royal_now():
                # wypełnij wszystko
                for r in req:
                    sent[r] = req[r]
                self.log("Misja królewska natychmiast wypełniona!", "gold")
                self.complete_royal_mission()
                win.destroy()

            ttk.Button(
                royal_frame,
                text="Wypełnij misję teraz",
                command=complete_royal_now
            ).pack(pady=8, anchor="w")

        else:
            ttk.Label(
                royal_frame,
                text="Brak aktywnej misji królewskiej.",
                foreground="gray"
            ).pack(pady=5, anchor="w")

        # ============================
        # 2. MISJE INDIAŃSKIE
        # ============================
        native_frame = ttk.LabelFrame(win, text="Misje indiańskie")
        native_frame.pack(fill="both", padx=10, pady=10)

        any_native = False

        for tribe, mission in self.native_missions_active.items():
            if not mission:
                continue

            any_native = True

            mframe = ttk.Frame(native_frame)
            mframe.pack(fill="x", pady=8)

            ttk.Label(
                mframe,
                text=f"{tribe}: {mission['name']}",
                font=("Arial", 11, "bold")
            ).pack(anchor="w")

            ttk.Label(
                mframe,
                text=mission.get("desc", ""),
                wraplength=600,
                justify="left"
            ).pack(anchor="w", pady=2)

            ttk.Label(
                mframe,
                text=f"Termin: {mission['end'].strftime('%d %b %Y')} "
                     f"(pozostało {(mission['end'] - self.current_date).days} dni)",
                foreground="red"
            ).pack(anchor="w")

            # POSTĘP
            req = mission["required"]
            sent = mission["sent"]

            for r in req:
                have = sent.get(r, 0)
                need = req[r]
                color = "green" if have >= need else ("orange" if have > 0 else "red")
                ttk.Label(
                    mframe,
                    text=f"{r}: {have}/{need}",
                    foreground=color
                ).pack(anchor="w")

            # ============================
            # PRZYCISK – WYPEŁNIJ MISJĘ TERAZ
            # ============================
            def make_finish_fn(tribe=tribe, mission=mission):
                def finish_now():
                    # pełne wypełnienie wymagań
                    for r in mission["required"]:
                        mission["sent"][r] = mission["required"][r]

                    # obliczenie nagrody
                    remaining_days = (mission["end"] - self.current_date).days
                    full_months_left = max(0, remaining_days // 30)
                    reward = 10 + 2 * full_months_left

                    self.native_relations[tribe] = min(
                        100, self.native_relations[tribe] + reward
                    )

                    self.log(
                        f"Misja od {tribe} wykonana! Nagroda: +{reward} reputacji.",
                        "green"
                    )

                    # zakończ misję
                    self.native_missions_active[tribe] = None

                    # cooldown 2–3 miesiące
                    cd = random.randint(60, 90)
                    self.native_missions_cd[tribe] = self.current_date + timedelta(days=cd)

                    win.destroy()

                return finish_now

            ttk.Button(
                mframe,
                text="Wypełnij misję teraz",
                command=make_finish_fn()
            ).pack(anchor="w", pady=6)

        if not any_native:
            ttk.Label(
                native_frame,
                text="Brak aktywnych misji indiańskich.",
                foreground="gray"
            ).pack(anchor="w", pady=5)

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