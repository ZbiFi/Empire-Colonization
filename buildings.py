# buildings.py
import tkinter as tk
from tkinter import ttk
from datetime import timedelta

from constants import BUILDINGS, RESOURCES, STATES


class BuildingsMixin:
    # === Pomocnicze dot. osady / pól ===
    def get_settlement_areas(self):
        return [
            (y, x)
            for y in range(self.map_size)
            for x in range(self.map_size)
            if self.map_grid[y][x]["terrain"] in ["osada", "dzielnica"]
        ]

    def get_free_settlement_slots(self):
        total = 0
        for y in range(self.map_size):
            for x in range(self.map_size):
                cell = self.map_grid[y][x]
                if cell["terrain"] not in ["osada", "dzielnica"]:
                    continue
                used = len([b for b in cell["building"] if not b.get("is_district", False)])
                in_progress = [c for c in self.constructions if c[1]["pos"] == (y, x)]
                used += len(in_progress)
                total += max(0, 5 - used)
        return total

    def get_buildings_in_cell(self, pos):
        y, x = pos
        return self.map_grid[y][x]["building"]

    def is_adjacent_to_settlement(self, pos):
        y, x = pos
        for dy, dx in [
            (0, 1),
            (1, 0),
            (0, -1),
            (-1, 0),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.map_size and 0 <= nx < self.map_size:
                if self.map_grid[ny][nx]["terrain"] in ["osada", "dzielnica"]:
                    return True
        return False

    # === Nazwa budynku na podstawie poziomu (namiot -> chata -> dom) ===
    def get_building_display_name(self, b):
        base_data = BUILDINGS[b["base"]]
        level = b.get("level", 0)
        if level > 0 and level <= len(base_data["upgrades"]):
            return base_data["upgrades"][level - 1].get("name", b["base"])
        return b["base"]

    # === Pojemność populacji (z budynków mieszkalnych) ===
    def calculate_population_capacity(self):
        from constants import BUILDINGS

        total = 0
        base_data = BUILDINGS["namiot"]

        for b in self.buildings:
            if b["base"] != "namiot":
                continue

            level = b.get("level", 0)

            # --- poziom 0 ---
            if level == 0:
                total += base_data.get("capacity", 0)

            # --- poziomy 1+ ---
            else:
                upgrades = base_data.get("upgrades", [])
                if 1 <= level <= len(upgrades):
                    total += upgrades[level - 1].get("capacity", 0)
                else:
                    # fallback – nie powinno się zdarzyć
                    total += base_data.get("capacity", 0)

        return total

    # === Produkcja ===
    def calculate_production(self):
        building_output = []

        for b in self.buildings:
            if b.get("is_district"):
                continue
            base = BUILDINGS[b["base"]]
            level = b.get("level", 0)
            workers = b.get("workers", 0)
            if not workers:
                building_output.append((b, {r: 0 for r in RESOURCES}, {}, 0.0))
                continue

            prod = {}
            for res, amt in base.get("base_prod", {}).items():
                bonus = 1
                # premie państw
                if self.state == "Szwecja" and res == "drewno":
                    bonus = STATES[self.state]["wood"]
                if self.state == "Dania" and res == "żywność":
                    bonus = STATES[self.state]["food"]
                if self.state == "Brandenburgia" and res == "stal":
                    bonus = STATES[self.state]["steel"]
                prod[res] = amt * workers * bonus

            # ulepszenia
            if level > 0:
                up = base["upgrades"][level - 1]
                for res, amt in up.get("prod", {}).items():
                    prod[res] = prod.get(res, 0) + amt * workers

            # kopalnie z przypisanym surowcem
            if b["base"] == "kopalnia" and b.get("resource"):
                resource = b["resource"]
                base_amount = (1 + level * 0.5) * workers

                if self.state == "Genua":
                    bonus = STATES[self.state]["mine"]
                    base_amount *= bonus

                prod[resource] = base_amount

            cons = {}
            if "consumes" in base:
                for res, amt in base["consumes"].items():
                    cons[res] = amt * workers

            # sprawdzamy, czy starcza surowców na konsumpcję
            efficiency = 1.0
            for res, needed in cons.items():
                available = self.resources.get(res, 0)
                if needed > 0 and available < needed:
                    efficiency = min(efficiency, available / needed)

            building_output.append((b, prod, cons, efficiency))

        return building_output

    def get_max_workers(self, b):
        base = BUILDINGS[b["base"]]
        level = b.get("level", 0)
        if level == 0:
            return base["base_workers"]
        upgrade = base["upgrades"][level - 1]
        return upgrade.get("workers", base["base_workers"])

    # === Budowa ===
    def start_construction_at(self, name, pos):
        y, x = pos
        data = BUILDINGS[name]
        cell = self.map_grid[y][x]

        if cell["terrain"] not in data.get("allowed_terrain", []):
            self.log(f"{name} nie może być budowany na {cell['terrain']}!", "red")
            return

        if data.get("requires_settlement"):
            if cell["terrain"] not in ["osada", "dzielnica"]:
                self.log("Tylko w osadzie/dzielnicy!", "red")
                return
            used = len([b for b in cell["building"] if not b.get("is_district", False)])
            in_progress = [c for c in self.constructions if c[1]["pos"] == (y, x)]
            if used + len(in_progress) >= 5:
                self.log("Brak miejsca w osadzie! (5/5, w tym budowa)", "red")
                return
        else:
            if cell["building"]:
                self.log("Już coś tu jest!", "red")
                return
            if any(c[1]["pos"] == (y, x) for c in self.constructions):
                self.log("Trwa budowa na tym polu!", "red")
                return

        if data.get("requires_adjacent_settlement"):
            if not self.is_adjacent_to_settlement(pos):
                self.log("Musi sąsiadować z osadą!", "red")
                return
            if cell["terrain"] == "morze" and name != "przystań":
                self.log("Nie na morzu!", "red")
                return

        if not self.can_afford(data["base_cost"]):
            self.log("Za mało surowców!", "red")
            return
        if self.free_workers() < data["base_workers"]:
            self.log("Za mało wolnych ludzi!", "red")
            return

        self.spend_resources(data["base_cost"])
        start_date = self.current_date
        end_date = start_date + timedelta(days=data["build_time"])
        new_b = {"base": name, "level": 0, "workers": 0, "pos": pos}
        if name == "kopalnia":
            new_b["resource"] = cell["resource"]
        if name == "dzielnica":
            new_b["is_district"] = True
            cell["terrain"] = "dzielnica"
        if name == "namiot":
            new_b["capacity"] = 4

        self.constructions.append((end_date, new_b, data["base_workers"], start_date))
        self.busy_people += data["base_workers"]
        self.log(f"Budowa: {name} → {end_date.strftime('%d %b %Y')}", "blue")

    # === Ulepszenia (w górę) ===
    def start_upgrade(self, building_idx):
        b = self.buildings[building_idx]
        base_data = BUILDINGS[b["base"]]
        current_level = b.get("level", 0)

        # 🔒 jeśli ten budynek już ma ulepszenie w toku – nie zaczynamy kolejnego
        if any(u[1] == building_idx for u in self.upgrades_in_progress):
            self.log("To ulepszenie jest już w trakcie realizacji!", "red")
            return

        if current_level >= len(base_data["upgrades"]):
            self.log("Maksymalny poziom!", "red")
            return

        upgrade = base_data["upgrades"][current_level]
        cost = upgrade.get("cost", {})
        workers_needed = upgrade.get("workers", 1)
        build_time = upgrade.get("build_time", 7)

        if self.state == "Holandia":
            mult = STATES[self.state]["build_cost"]  # np. 0.8
            cost = {k: int(v * mult) for k, v in cost.items()}

        if not self.can_afford(cost):
            self.log("Za mało surowców na ulepszenie!", "red")
            return
        if self.free_workers() < workers_needed:
            self.log("Za mało wolnych ludzi!", "red")
            return

        self.spend_resources(cost)
        start_date = self.current_date
        end_date = start_date + timedelta(days=build_time)

        # (end_date, building_idx, new_level, start_date)
        self.upgrades_in_progress.append((end_date, building_idx, current_level + 1, start_date))
        self.busy_people += workers_needed

        self.log(
            f"Ulepszanie: {self.get_building_display_name(b)} → poziom {current_level + 1} "
            f"→ {end_date.strftime('%d %b %Y')}",
            "purple",
        )

    # === Degradacja / zburzenie (w dół) ===
    def degrade_or_demolish(self, building_idx):
        b = self.buildings[building_idx]
        base_data = BUILDINGS[b["base"]]
        level = b.get("level", 0)
        y, x = b["pos"]

        # 🔄 jeśli jest trwające ulepszenie tego budynku – przerwij je
        to_cancel = [u for u in self.upgrades_in_progress if u[1] == building_idx]
        for u in to_cancel:
            _, _, new_level, _ = u
            prev_level = new_level - 1
            upgrades = base_data.get("upgrades", [])
            workers_needed = 1
            if 0 <= prev_level < len(upgrades):
                workers_needed = upgrades[prev_level].get("workers", 1)
            self.busy_people -= workers_needed
            self.upgrades_in_progress.remove(u)
        if to_cancel:
            self.log("Przerwano trwające ulepszenie tego budynku (bez zwrotu surowców).", "orange")

        # DEGRADACJA POZIOMU (zwraca 50% kosztu poprzedniego ulepszenia)
        if level > 0:
            prev_upgrade = base_data["upgrades"][level - 1]
            prev_cost = prev_upgrade.get("cost", {})
            for r, a in prev_cost.items():
                self.resources[r] = self.resources.get(r, 0) + a // 2

            new_level = level - 1
            b["level"] = new_level

            # po degradacji dopasuj capacity, jeśli zdefiniowane
            if new_level > 0:
                new_up = base_data["upgrades"][new_level - 1]
                if "capacity" in new_up:
                    b["capacity"] = new_up["capacity"]
            else:
                if b["base"] == "namiot":
                    b["capacity"] = BUILDINGS["namiot"].get("capacity", 4)

            current_name = self.get_building_display_name(b)
            self.log(
                f"Zdegradowano budynek do poziomu {new_level}: {current_name} "
                f"(zwrot 50% kosztu ulepszenia).",
                "orange",
            )
            return

        # ZBURZENIE BUDYNKU (poziom 0, zwrot 50% kosztu budowy)
        base_cost = base_data.get("base_cost", {})
        for r, a in base_cost.items():
            self.resources[r] = self.resources.get(r, 0) + a // 2

        self.buildings.pop(building_idx)
        self.map_grid[y][x]["building"] = [bb for bb in self.map_grid[y][x]["building"] if bb is not b]
        self.log("Zburzono budynek. Zwrot: 50% kosztu budowy.", "orange")

    def cancel_upgrade(self, building_idx):
        """Anuluje trwające ulepszenie budynku, zwraca 100% surowców i zwalnia ludzi."""
        b = self.buildings[building_idx]
        base_data = BUILDINGS[b["base"]]

        # znajdź ulepszenia w toku dotyczące tego budynku
        to_cancel = [u for u in self.upgrades_in_progress if u[1] == building_idx]

        if not to_cancel:
            self.log("Brak ulepszenia do zatrzymania.", "red")
            return

        for u in to_cancel:
            end_date, idx, new_level, start_date = u

            prev_level = new_level - 1
            upgrades = base_data.get("upgrades", [])

            # --- zwrot surowców ---
            if 0 <= prev_level < len(upgrades):
                original_cost = upgrades[prev_level].get("cost", {}).copy()

                # uwzględnij bonus Holandii (koszty budowy -20%)
                if self.state == "Holandia":
                    mult = STATES[self.state]["build_cost"]  # np. 0.8
                    original_cost = {k: int(v * mult) for k, v in original_cost.items()}

                # zwracamy 100%
                for r, a in original_cost.items():
                    self.resources[r] = self.resources.get(r, 0) + a

            # --- zwrot robotników ---
            workers_used = upgrades[prev_level].get("workers", 1) if 0 <= prev_level < len(upgrades) else 1
            self.busy_people -= workers_used

            # usuń zadanie ulepszenia
            self.upgrades_in_progress.remove(u)

        self.log("Ulepszenie zatrzymane — zwrócono wszystkie surowce i robotników.", "orange")

    # === Menu: Ulepsz/Zdegraduj (jeden przycisk) ===
    def show_upgrade_menu(self):
        win = tk.Toplevel(self.root)
        win.title("Ulepsz / Zdegraduj / Zatrzymaj")
        ttk.Label(win, text="Wybierz budynek:", font=("Arial", 12, "bold")).pack(pady=10)

        has_any = False
        for i, b in enumerate(self.buildings):
            if b.get("is_district"):
                continue

            base_data = BUILDINGS[b["base"]]
            upgrades = base_data.get("upgrades", [])
            level = b.get("level", 0)
            current_name = self.get_building_display_name(b)

            in_progress = any(u[1] == i for u in self.upgrades_in_progress)

            frame = ttk.Frame(win)
            frame.pack(fill="x", padx=20, pady=3)

            # nazwa + poziom + informacja o statusie ulepszenia
            label_text = f"{current_name} ({b['pos'][0]},{b['pos'][1]}) [poziom {level}]"
            if in_progress:
                label_text += " (ulepszanie w toku)"
            ttk.Label(frame, text=label_text, width=40).pack(side="left")

            # --- NOWY: przycisk ZATRZYMAJ ULEPSZENIE ---
            if in_progress:
                cancel_btn = ttk.Button(
                    frame,
                    text="Zatrzymaj ulepszenie",
                    command=lambda idx=i: [self.cancel_upgrade(idx), win.destroy()],
                )
                cancel_btn.pack(side="right", padx=5)

            # --- przycisk ULEPSZ (tylko gdy NIE w trakcie ulepszania) ---
            if level < len(upgrades) and not in_progress:
                has_any = True
                next_up = upgrades[level]
                up_name = next_up.get("name", f"Poziom {level + 1}")
                cost_str = ", ".join(f"{k}: {v}" for k, v in next_up.get("cost", {}).items()) or "brak"
                time = next_up.get("build_time", 7)

                up_btn = ttk.Button(
                    frame,
                    text=f"Ulepsz → {up_name}\n({cost_str} | {time} dni)",
                    command=lambda idx=i: [self.start_upgrade(idx), win.destroy()],
                )
                up_btn.pack(side="right", padx=5)

            # --- przycisk ZDEGRADUJ/ZBURZ (zawsze dostępny) ---
            if level > 0:
                if level == 1:
                    prev_name = b["base"]
                else:
                    prev_name = upgrades[level - 2].get("name", b["base"])
                text = f"Zdegraduj → {prev_name}\n(+50% kosztu ulepszenia)"
            else:
                text = "Zburz\n(+50% kosztu budowy)"

            de_btn = ttk.Button(
                frame,
                text=text,
                command=lambda idx=i: [self.degrade_or_demolish(idx), win.destroy()],
            )
            de_btn.pack(side="right", padx=5)


        if not has_any:
            ttk.Label(
                win,
                text="Brak budynków do ulepszenia (lub wszystkie są gotowe).",
                foreground="gray",
            ).pack(pady=20)

        ttk.Button(win, text="Zamknij", command=win.destroy).pack(pady=10)

    # === Menu budowy ===
    def build_menu(self):
        win = tk.Toplevel(self.root)
        win.title("Buduj")
        for name, data in BUILDINGS.items():
            display_cost = data["base_cost"].copy()
            if self.state == "Holandia":
                mult = STATES[self.state]["build_cost"]  # np. 0.8
                display_cost = {k: int(v * mult) for k, v in display_cost.items()}

            cost = ", ".join(f"{k}: {v}" for k, v in display_cost.items()) or "brak"

            btn = ttk.Button(
                win,
                text=f"{name} | {data['build_time']} dni | {cost}",
                command=lambda n=name: self.select_for_building(n, win),
            )
            btn.pack(fill="x", padx=20, pady=2)
        ttk.Button(win, text="Anuluj", command=win.destroy).pack(pady=10)

    def select_for_building(self, name, win):
        self.selected_building = name
        win.destroy()
        self.show_map()

    # === Zarządzanie pracownikami ===
    def manage_workers(self):
        win = tk.Toplevel(self.root)
        win.title("Pracownicy")

        self.worker_sliders = []
        for i, b in enumerate(self.buildings):
            if b["base"] in ["dzielnica", "namiot"]:
                continue

            max_w = self.get_max_workers(b)
            if max_w <= 0:
                # budynek bez miejsc pracy – pomijamy
                continue

            frame = ttk.Frame(win)
            frame.pack(fill="x", padx=10, pady=3)

            ttk.Label(
                frame,
                text=f"{self.get_building_display_name(b)} ({b['pos'][0]},{b['pos'][1]})",
                width=30,
            ).pack(side="left")

            scale = tk.Scale(frame, from_=0, to=max_w, orient="horizontal", length=200)
            scale.set(b.get("workers", 0))
            scale.pack(side="right")

            self.worker_sliders.append((i, scale))

        # jeśli nie ma żadnych miejsc pracy
        if not self.worker_sliders:
            ttk.Label(
                win,
                text="Brak miejsc pracy",
                foreground="red",
                font=("Arial", 11, "bold"),
            ).pack(pady=15)
            ttk.Button(win, text="Zamknij", command=win.destroy).pack(pady=5)
            return

        def save():
            total = sum(s.get() for _, s in self.worker_sliders)
            if total > self.free_workers() + self.busy_people:
                self.log("Za dużo!", "red")
                return
            for idx, scale in self.worker_sliders:
                self.buildings[idx]["workers"] = scale.get()
            self.log("Pracownicy przydzieleni.", "green")
            win.destroy()

        ttk.Button(win, text="Zatwierdź", command=save).pack(pady=10)
