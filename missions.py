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
        difficulty = int(self.mission_multiplier * 1.5)  # <-- jak wcześniej

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
        self.log(f"Misja opłacona dukatami: {cost}. +reputacja", "DarkOrange")

        # nagroda jak poprzednio
        self.europe_relations[self.state] = min(100, self.europe_relations[self.state] + 10 * diff)
        self.complete_royal_mission()

    def show_missions_overview(self):
        """Okno zbiorcze wszystkich misji: królewskich i indiańskich.
           Z tego okna można natychmiast wypełnić misje (bez handlu, bez opóźnień).
        """

        win = self.create_window("Misje")
        win.geometry("650x800")

        # === GRID NA OKNIE: content + bottom bar ===
        win.grid_rowconfigure(0, weight=1)  # content rośnie
        win.grid_rowconfigure(1, weight=0)  # bottom nie rośnie
        win.grid_columnconfigure(0, weight=1)

        content_frame = ttk.Frame(win)
        content_frame.grid(row=0, column=0, sticky="nsew")

        bottom_frame = ttk.Frame(win)
        bottom_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=8)

        # ====== FONTY SPÓJNE Z RESZTĄ UI (main.py) ======
        top_title_font = getattr(self, "top_title_font", ("Cinzel", 14, "bold"))
        top_info_font = getattr(self, "top_info_font", ("EB Garamond Italic", 12))
        bold_info_font = (top_info_font[0], top_info_font[1], "bold")

        # ====== GŁÓWNY TYTUŁ OKNA ======
        ttk.Label(
            content_frame,
            text="MISJE",
            font=(top_title_font[0], top_title_font[1] + 2, "bold"),
            anchor="center",
            justify="center"
        ).pack(pady=(8, 4))

        ttk.Separator(content_frame, orient="horizontal").pack(fill="x", padx=12, pady=(0, 8))

        # ============================
        # 1. MISJA KRÓLEWSKA
        # ============================
        royal_frame = ttk.LabelFrame(content_frame, text="")
        royal_frame.pack(fill="x", padx=12, pady=8)

        ttk.Label(
            royal_frame,
            text="✦ MISJA KRÓLEWSKA ✦",
            font=top_title_font,
            anchor="center",
            justify="center"
        ).pack(fill="x", pady=(6, 8))

        ttk.Separator(royal_frame, orient="horizontal").pack(fill="x", padx=8, pady=(0, 8))

        if not self.current_mission:
            ttk.Label(
                royal_frame,
                text="Brak aktywnej misji królewskiej.",
                foreground="gray",
                font=top_info_font,
                anchor="center",
                justify="center"
            ).pack(pady=8, fill="x")
        else:
            end, req, sent, diff, text, idx = self.current_mission

            # --- PRZYWRÓCONE: name na górze + desc poniżej ---
            try:
                mission_def = ROYAL_MISSIONS[idx]
                mname = mission_def.get("name", "Misja królewska")
                mdesc = mission_def.get("desc", text)
            except Exception:
                mname = "Misja królewska"
                mdesc = text

            ttk.Label(
                royal_frame,
                text=mname,
                wraplength=600,
                justify="center",
                anchor="center",
                font=(bold_info_font[0], bold_info_font[1] + 1, "bold")
            ).pack(pady=6, fill="x")

            if mdesc:
                ttk.Label(
                    royal_frame,
                    text=mdesc,
                    wraplength=600,
                    justify="center",
                    font=(top_info_font[0], top_info_font[1] + 1)
                ).pack(pady=6, fill="x")

            ttk.Label(
                royal_frame,
                text=f"Pozostało: {(end - self.current_date).days} dni",
                foreground="red",
                font=top_info_font,
                anchor="center",
                justify="center"
            ).pack(fill="x", pady=3)

            progress_frame = ttk.Frame(royal_frame)
            progress_frame.pack(pady=6, fill="x")

            for r in req:
                have = sent.get(r, 0)
                need = req[r]
                color = "green" if have >= need else ("orange" if have > 0 else "red")
                ttk.Label(
                    progress_frame,
                    text=f"{r}: {have}/{need}",
                    foreground=color,
                    font=top_info_font,
                    anchor="center",
                    justify="center"
                ).pack(fill="x")

            remaining = {
                r: req[r] - sent.get(r, 0)
                for r in req
                if sent.get(r, 0) < req[r]
            }

            if remaining:
                total_value = sum(a * EUROPE_PRICES.get(r, 10) for r, a in remaining.items())
                dukaty_cost = int(total_value * diff)

                ttk.Label(
                    royal_frame,
                    text=f"Koszt spłacenia dukatami: {dukaty_cost}",
                    foreground="orange",
                    font=bold_info_font,
                    anchor="center",
                    justify="center"
                ).pack(pady=(6, 4), fill="x")

                def _pay_and_maybe_close(cost=dukaty_cost):
                    # jeśli nie ma dość dukatów -> pay_mission_with_gold zaloguje błąd, ale nie zamykamy okna
                    if self.resources.get("dukaty", 0) < cost:
                        self.pay_mission_with_gold()
                        return
                    # jak ma dość -> opłać i zamknij
                    self.pay_mission_with_gold()
                    win.destroy()

                ttk.Button(
                    royal_frame,
                    text="Opłać dukatami",
                    command=_pay_and_maybe_close
                ).pack(pady=(4, 8), anchor="center")

            else:
                ttk.Label(
                    royal_frame,
                    text="Misja już wykonana!",
                    foreground="green",
                    font=bold_info_font,
                    anchor="center",
                    justify="center"
                ).pack(pady=8, fill="x")

        # ============================
        # 2. MISJE INDIAŃSKIE (SCROLL tylko gdy potrzebny)
        # ============================
        native_frame = ttk.LabelFrame(content_frame, text="")
        native_frame.pack(fill="both", expand=True, padx=12, pady=8)

        ttk.Label(
            native_frame,
            text="✦ MISJE INDIAŃSKIE ✦",
            font=top_title_font,
            anchor="center",
            justify="center"
        ).pack(fill="x", pady=(6, 8))

        ttk.Separator(native_frame, orient="horizontal").pack(fill="x", padx=8, pady=(0, 8))

        bg = win.cget("background")
        native_canvas = tk.Canvas(native_frame, highlightthickness=0, background=bg)
        native_scrollbar = ttk.Scrollbar(native_frame, orient="vertical", command=native_canvas.yview)
        native_canvas.configure(yscrollcommand=native_scrollbar.set)

        native_scrollbar.pack(side="right", fill="y")
        native_canvas.pack(side="left", fill="both", expand=True)

        native_list = ttk.Frame(native_canvas)
        native_window = native_canvas.create_window((0, 0), window=native_list, anchor="nw")

        scroll_needed = {"value": False}

        def _native_update_scrollregion(event=None):
            native_canvas.configure(scrollregion=native_canvas.bbox("all"))
            native_canvas.itemconfigure(native_window, width=native_canvas.winfo_width())

            bbox = native_canvas.bbox("all")
            if not bbox:
                scroll_needed["value"] = False
                if native_scrollbar.winfo_ismapped():
                    native_scrollbar.pack_forget()
                return

            content_h = bbox[3] - bbox[1]
            canvas_h = native_canvas.winfo_height()

            if content_h <= canvas_h + 2:
                scroll_needed["value"] = False
                native_canvas.yview_moveto(0)
                if native_scrollbar.winfo_ismapped():
                    native_scrollbar.pack_forget()
            else:
                scroll_needed["value"] = True
                if not native_scrollbar.winfo_ismapped():
                    native_scrollbar.pack(side="right", fill="y")

        native_list.bind("<Configure>", _native_update_scrollregion)
        native_canvas.bind("<Configure>", _native_update_scrollregion)

        def _on_mousewheel(e):
            if scroll_needed["value"]:
                native_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        def _bind_mousewheel(_):
            native_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(_):
            native_canvas.unbind_all("<MouseWheel>")

        native_canvas.bind("<Enter>", _bind_mousewheel)
        native_canvas.bind("<Leave>", _unbind_mousewheel)

        any_native = False

        for tribe, mission in self.native_missions_active.items():
            if not mission:
                continue

            any_native = True

            mframe = ttk.Frame(native_list)
            mframe.pack(fill="x", pady=8, padx=6)

            ttk.Label(
                mframe,
                text=f"{tribe}: {mission['name']}",
                font=bold_info_font,
                anchor="center",
                justify="center"
            ).pack(fill="x")

            ttk.Label(
                mframe,
                text=mission.get("desc", ""),
                wraplength=600,
                justify="center",
                font=top_info_font,
                anchor="center"
            ).pack(fill="x", pady=2)

            ttk.Label(
                mframe,
                text=f"Termin: {mission['end'].strftime('%d %b %Y')} "
                     f"(pozostało {(mission['end'] - self.current_date).days} dni)",
                foreground="red",
                font=top_info_font,
                anchor="center",
                justify="center"
            ).pack(fill="x", pady=1)

            req = mission["required"]
            sent = mission["sent"]

            resource_sources = [
                "storage", "warehouse", "inventory", "goods",
                "colony_resources", "resources"
            ]

            for r in req:
                need = req[r]

                player_have = 0
                for src in resource_sources:
                    d = getattr(self, src, None)
                    if isinstance(d, dict) and r in d:
                        player_have = d.get(r, 0)
                        break

                if player_have >= need:
                    color = "green"
                elif player_have > 0:
                    color = "orange"
                else:
                    color = "red"

                have_sent = sent.get(r, 0)

                ttk.Label(
                    mframe,
                    text=f"{r}: {have_sent}/{need}",
                    foreground=color,
                    font=top_info_font,
                    anchor="center",
                    justify="center"
                ).pack(fill="x")

            def make_finish_fn(tribe=tribe, mission=mission):
                def finish_now():
                    missing = {}
                    required = mission.get("required", {})

                    resource_sources = [
                        "storage", "warehouse", "inventory", "goods",
                        "colony_resources", "resources"
                    ]

                    for r, need in required.items():
                        have = 0
                        for src in resource_sources:
                            d = getattr(self, src, None)
                            if isinstance(d, dict) and r in d:
                                have = d.get(r, 0)
                                break
                        if have < need:
                            missing[r] = (have, need)

                    if missing:
                        msg = (
                                "Nie masz wystarczających surowców do wykonania misji od "
                                + str(tribe) + ": "
                                + ", ".join([f"{r} {have}/{need}" for r, (have, need) in missing.items()])
                        )
                        self.log(msg, "red")
                        return

                    for r in required:
                        mission["sent"][r] = required[r]

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

                    self.native_missions_active[tribe] = None
                    cd = random.randint(30, 60)
                    self.native_missions_cd[tribe] = self.current_date + timedelta(days=cd)

                    win.destroy()

                return finish_now

            ttk.Button(
                mframe,
                text="Wypełnij misję teraz",
                command=make_finish_fn()
            ).pack(pady=6, anchor="center")

            ttk.Separator(native_list, orient="horizontal").pack(fill="x", padx=10, pady=6)

        if not any_native:
            ttk.Label(
                native_list,
                text="Brak aktywnych misji indiańskich.",
                foreground="gray",
                font=top_info_font,
                anchor="center",
                justify="center"
            ).pack(pady=8, fill="x")

        # ============================
        # BOTTOM BAR — ZAMKNIJ
        # ============================
        ttk.Separator(bottom_frame, orient="horizontal").pack(fill="x", pady=(0, 6))

        ttk.Button(
            bottom_frame,
            text="Zamknij",
            command=win.destroy
        ).pack(anchor="center")

        self.center_window(win)

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

        win = self.create_window(f"ZWYCIĘSTWO!")

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