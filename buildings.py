# buildings.py
import tkinter as tk
from tkinter import ttk
from datetime import timedelta

from constants import BUILDINGS, RESOURCES, STATES
from tooltip import Tooltip


class BuildingsMixin:
    # === Pomocnicze dot. osady / pól ===
    def get_settlement_areas(self):
        return [
            (y, x)
            for y in range(self.map_size)
            for x in range(self.map_size)
            if self.map_grid[y][x]["terrain"] in ["settlement", "district"]
        ]

    def get_free_settlement_slots(self):
        total = 0
        for y in range(self.map_size):
            for x in range(self.map_size):
                cell = self.map_grid[y][x]
                if cell["terrain"] not in ["settlement", "district"]:
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
                if self.map_grid[ny][nx]["terrain"] in ["settlement", "district"]:
                    return True
        return False

    # === Nazwa budynku na podstawie poziomu (tent -> chata -> dom) ===
    def get_building_display_name(self, b):
        base_data = BUILDINGS[b["base"]]
        level = b.get("level", 0)
        if level > 0 and level <= len(base_data["upgrades"]):
            return base_data["upgrades"][level - 1].get("name", b["base"])
        # dla poziomu 0 używamy przyjaznej nazwy z constants.py
        return base_data.get("name", b["base"])

    # === Pojemność populacji (z budynków mieszkalnych) ===
    def calculate_population_capacity(self):
        from constants import BUILDINGS

        total = 0
        base_data = BUILDINGS["tent"]

        for b in self.buildings:
            if b["base"] != "tent":
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

            # --- produkcja bazowa ---
            for res, amt in base.get("base_prod", {}).items():
                # dla kopalni: zamiast sztucznego zasobu z constants
                # używamy faktycznego surowca z pola (węgiel/żelazo/srebro/złoto)
                target_res = res
                if b["base"] == "mine" and b.get("resource"):
                    target_res = b["resource"]

                bonus = 1.0
                # premie państw zależne od surowca (po mapowaniu)
                if self.state == "sweden" and target_res == "wood":
                    bonus = STATES[self.state]["wood"]
                if self.state == "denmark" and target_res == "food":
                    bonus = STATES[self.state]["food"]
                if self.state == "brandenburg" and target_res == "steel":
                    bonus = STATES[self.state]["steel"]

                # bonus Genui dla wszystkich kopalń
                if self.state == "genua" and b["base"] == "mine":
                    bonus *= STATES[self.state].get("mine", 1.0)

                prod[target_res] = prod.get(target_res, 0) + amt * workers * bonus

            # --- ulepszenia (poziomy 1+) ---
            if level > 0:
                up = base["upgrades"][level - 1]

                # standardowo: klucz "prod" jak w innych budynkach;
                # ale gdybyś w kopalni trzymał to w "base_prod", też to złapiemy
                upgrade_prod = up.get("prod", up.get("base_prod", {}))

                for res, amt in upgrade_prod.items():
                    target_res = res
                    if b["base"] == "mine" and b.get("resource"):
                        target_res = b["resource"]

                    bonus = 1.0
                    if self.state == "sweden" and target_res == "wood":
                        bonus = STATES[self.state]["wood"]
                    if self.state == "denmark" and target_res == "food":
                        bonus = STATES[self.state]["food"]
                    if self.state == "brandenburg" and target_res == "steel":
                        bonus = STATES[self.state]["steel"]

                    if self.state == "genua" and b["base"] == "mine":
                        bonus *= STATES[self.state].get("mine", 1.0)

                    prod[target_res] = prod.get(target_res, 0) + amt * workers * bonus

            # --- konsumpcja surowców ---
            cons = {}
            if "consumes" in base:
                for res, amt in base["consumes"].items():
                    cons[res] = amt * workers

            # --- sprawdzenie, czy starcza surowców (wydajność) ---
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
            self.log(
                self.loc.t(
                    "log.cannot_build_here",
                    building=self.loc.t(f"building.{name}.name", default=name),
                    terrain=self.loc.t(f"terrain.{cell['terrain']}.name", default=cell["terrain"])
                ),
                "red"
            )
            return

        if data.get("requires_settlement"):
            if cell["terrain"] not in ["settlement", "district"]:
                self.log(self.loc.t("ui.must_be_in_settlement"), "red")
                return
            used = len([b for b in cell["building"] if not b.get("is_district", False)])
            in_progress = [c for c in self.constructions if c[1]["pos"] == (y, x)]
            if used + len(in_progress) >= 5:
                self.log(self.loc.t("ui.no_space_in_settlement"), "red")
                return
        else:
            if cell["building"]:
                self.log(self.loc.t("log.building_already_exists"), "red")
                return
            if any(c[1]["pos"] == (y, x) for c in self.constructions):
                self.log(self.loc.t("log.construction_in_progress_here"), "red")
                return

        if data.get("requires_adjacent_settlement"):
            if not self.is_adjacent_to_settlement(pos):
                self.log(self.loc.t("log.requires_adjacent_settlement"), "red")
                return
            if cell["terrain"] == "sea" and name != "harbor":
                self.log(self.loc.t("log.cannot_build_on_sea"), "red")
                return

        if not self.can_afford(data["base_cost"]):
            self.log(self.loc.t("log.not_enough_resources"), "red")
            return
        if self.free_workers() < data["base_workers"]:
            self.log(self.loc.t("ui.not_enough_workers"), "red")
            return

        self.spend_resources(data["base_cost"])
        start_date = self.current_date
        end_date = start_date + timedelta(days=data["build_time"])
        new_b = {"base": name, "level": 0, "workers": 0, "pos": pos}
        if name == "mine":
            new_b["resource"] = cell["resource"]
        if name == "district":
            new_b["is_district"] = True
            cell["terrain"] = "district"
        if name == "tent":
            new_b["capacity"] = 4

        self.constructions.append((end_date, new_b, data["base_workers"], start_date))
        self.busy_people += data["base_workers"]
        name = self.get_building_display_name(new_b)
        self.log(
            self.loc.t(
                "log.construction_started",
                building=name,
                date=end_date.strftime('%d %b %Y')
            ),
            "blue"
        )

    # === Ulepszenia (w górę) ===
    def start_upgrade(self, building_idx):
        b = self.buildings[building_idx]
        base_data = BUILDINGS[b["base"]]
        current_level = b.get("level", 0)

        # 🔒 jeśli ten budynek już ma ulepszenie w toku – nie zaczynamy kolejnego
        if any(u[1] == building_idx for u in self.upgrades_in_progress):
            self.log(self.loc.t("ui.building_already_in_progress"), "red")
            return

        if current_level >= len(base_data["upgrades"]):
            self.log(self.loc.t("ui.max_level_reached"), "red")
            return

        upgrade = base_data["upgrades"][current_level]
        cost = upgrade.get("cost", {})
        workers_needed = upgrade.get("workers", 1)
        build_time = upgrade.get("build_time", 7)

        if self.state == "netherlands":
            mult = STATES[self.state]["build_cost"]  # np. 0.8
            cost = {k: int(v * mult) for k, v in cost.items()}

        if not self.can_afford(cost):
            self.log(self.loc.t("ui.not_enough_resources"), "red")
            return
        if self.free_workers() < workers_needed:
            self.log(self.loc.t("ui.not_enough_workers"), "red")
            return

        self.spend_resources(cost)
        start_date = self.current_date
        end_date = start_date + timedelta(days=build_time)

        # (end_date, building_idx, new_level, start_date)
        self.upgrades_in_progress.append((end_date, building_idx, current_level + 1, start_date))
        self.busy_people += workers_needed

        self.log(
            self.loc.t(
                "log.upgrading_started",
                building=self.get_building_display_name(b),
                level=current_level + 1,
                date=end_date.strftime('%d %b %Y')
            ),
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
            self.log(self.loc.t("ui.upgrade_cancelled_no_refund"), "orange")

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
                if b["base"] == "tent":
                    b["capacity"] = BUILDINGS["tent"].get("capacity", 4)

            current_name = self.get_building_display_name(b)
            self.log(
                self.loc.t(
                    "log.building_downgraded",
                    level=new_level,
                    building=current_name
                ),
                "orange",
            )
            return

        # ZBURZENIE BUDYNKU (poziom 0, zwrot 50% kosztu budowy)
        base_cost = base_data.get("base_cost", {})
        for r, a in base_cost.items():
            self.resources[r] = self.resources.get(r, 0) + a // 2

        self.buildings.pop(building_idx)
        self.map_grid[y][x]["building"] = [bb for bb in self.map_grid[y][x]["building"] if bb is not b]
        self.log(self.loc.t("log.building_demolished_refund"), "orange")

    def cancel_upgrade(self, building_idx):
        """Anuluje trwające ulepszenie budynku, zwraca 100% surowców i zwalnia ludzi."""
        b = self.buildings[building_idx]
        base_data = BUILDINGS[b["base"]]

        # znajdź ulepszenia w toku dotyczące tego budynku
        to_cancel = [u for u in self.upgrades_in_progress if u[1] == building_idx]

        if not to_cancel:
            self.log(self.loc.t("log.no_upgrade_to_cancel"), "red")
            return

        for u in to_cancel:
            end_date, idx, new_level, start_date = u

            prev_level = new_level - 1
            upgrades = base_data.get("upgrades", [])

            # --- zwrot surowców ---
            if 0 <= prev_level < len(upgrades):
                original_cost = upgrades[prev_level].get("cost", {}).copy()

                # uwzględnij bonus Holandii (koszty budowy -20%)
                if self.state == "netherlands":
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

        self.log(self.loc.t("log.upgrade_cancelled_refunded"), "orange")

    # === Menu: Ulepsz/Zdegraduj (jeden przycisk) ===
    def show_upgrade_menu(self):

        win = self.create_window(self.loc.t("screen.buildings.manage_title"))

        # fonty spójne z resztą UI (misje)
        title_font = getattr(self, "top_title_font", ("Cinzel", 14, "bold"))

        ttk.Label(
            win,
            text=self.loc.t("screen.buildings.choose_building_label"),
            font=title_font
        ).pack(pady=10)

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
                label_text += self.loc.t("ui.upgrading_suffix")
            ttk.Label(frame, text=label_text, width=40).pack(side="left")

            # --- NOWY: przycisk ZATRZYMAJ ULEPSZENIE ---
            if in_progress:
                cancel_btn = ttk.Button(
                    frame,
                    text=self.loc.t("ui.cancel_upgrade"),
                    command=lambda idx=i: [self.cancel_upgrade(idx), win.destroy()],
                )
                cancel_btn.pack(side="right", padx=5)

            # --- przycisk ULEPSZ (tylko gdy NIE w trakcie ulepszania) ---
            if level < len(upgrades) and not in_progress:
                has_any = True
                next_up = upgrades[level]
                up_name = next_up.get(
                    "name",
                    self.loc.t("ui.level_fallback", level=level + 1)
                )
                cost_str = ", ".join(f"{k}: {v}" for k, v in next_up.get("cost", {}).items()) \
                           or self.loc.t("ui.none")
                time = next_up.get("build_time", 7)

                up_btn = ttk.Button(
                    frame,
                    text=self.loc.t(
                        "ui.upgrade_to_with_cost_time",
                        upgrade=up_name,
                        cost=cost_str,
                        days=time
                    ),
                    command=lambda idx=i: [self.start_upgrade(idx), win.destroy()],
                )
                up_btn.pack(side="right", padx=5)

            # --- przycisk ZDEGRADUJ/ZBURZ (zawsze dostępny) ---
            if level > 0:
                if level == 1:
                    prev_name = b["base"]
                else:
                    prev_name = upgrades[level - 2].get("name", b["base"])
                text = self.loc.t(
                    "ui.downgrade_to_with_refund_note",
                    prev=prev_name
                )
            else:
                text = self.loc.t("ui.demolish_with_refund_note")

            de_btn = ttk.Button(
                frame,
                text=text,
                command=lambda idx=i: [self.degrade_or_demolish(idx), win.destroy()],
            )
            de_btn.pack(side="right", padx=5)


        if not has_any:
            ttk.Label(
                win,
                text=self.loc.t("screen.buildings.no_buildings_to_upgrade"),
                foreground="gray",
            ).pack(pady=20)

        ttk.Button(win, text=self.loc.t("ui.close"), command=win.destroy).pack(pady=10)

        # wyśrodkuj okno statków
        self.center_window(win)

    # === Menu budowy ===

    def build_menu(self):

        win = self.create_window(self.loc.t("screen.build_menu.title"))

        # styl dla budynków, na które gracza nie stać
        if not hasattr(self, "_cant_afford_building_style"):
            style = ttk.Style()
            style.configure("CantAffordBuilding.TButton", foreground="red")
            self._cant_afford_building_style = True

        for name, data in BUILDINGS.items():
            # koszt z uwzględnieniem bonusu Holandii
            display_cost = data["base_cost"].copy()
            if self.state == "netherlands":
                mult = STATES[self.state]["build_cost"]  # np. 0.8
                display_cost = {k: int(v * mult) for k, v in display_cost.items()}

            cost_str = ", ".join(f"{k}: {v}" for k, v in display_cost.items()) or self.loc.t("ui.none")
            build_time = data.get("build_time", 0)
            base_workers = data.get("base_workers", 0)
            desc = data.get("desc") or data.get("description", "")

            # === Wiersz dla jednego budynku ===
            row = ttk.Frame(win)
            row.pack(fill="x", padx=20, pady=3)

            display_name = data.get("name", name)

            # 1) Przycisk z nazwą budynku (po lewej)
            btn = ttk.Button(
                row,
                text=display_name,
                command=lambda n=name: self.select_for_building(n, win),
                width=18,
            )

            # jeśli gracza nie stać na budynek → czerwony tekst
            if not self.can_afford(data["base_cost"]):
                btn.configure(style="CantAffordBuilding.TButton")

            btn.pack(side="left")

            # Tooltip z informacją CO robi budynek
            Tooltip(
                btn,
                lambda n=name, d=data: self.get_building_tooltip_text(n, d)
            )

            # 2) Ramka z informacjami o budynku (po prawej)
            info_frame = ttk.Frame(row)
            info_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))

            info_parts = []
            if build_time:
                info_parts.append(self.loc.t("ui.build_time_days", days=build_time))
            if base_workers:
                info_parts.append(self.loc.t("ui.work_places", workers=base_workers))
            info_parts.append(self.loc.t("ui.cost_prefix", cost=cost_str))
            if desc:
                info_parts.append(desc)

            info_text = " | ".join(info_parts)

            ttk.Label(
                info_frame,
                text=info_text,
                justify="left",
                anchor="w",
                wraplength=600,
            ).pack(fill="x")

        ttk.Button(win, text=self.loc.t("ui.cancel"), command=win.destroy).pack(pady=10)

        # wyśrodkuj okno
        self.center_window(win)

    def get_building_tooltip_text(self, name, data):
        """
        Tooltip po najechaniu na nazwę budynku:
        - namiot: +X mieszkań
        - dzielnica: +5 miejsc na budowle
        - kopalnia: produkcja zależna od surowca i poziomu
        - reszta: +prod / pracownik, -koszt / pracownik
        wszystko z uwzględnieniem bonusów państwa.
        """

        # === NAMIOT ===
        if name == "tent":
            cap = data.get("capacity", 0)
            return self.loc.t("tooltip.tent_capacity", cap=cap)

        # === DZIELNICA ===
        if name == "district":
            return self.loc.t("tooltip.district_slots")

        # === BUDYNKI PRODUKCYJNE I KOPALNIA ===

        # 1) produkcja bazowa
        base_prod = data.get("base_prod", {}) or {}

        # 2) produkcja z ulepszeń (pokazać poziomy)
        upgrades = data.get("upgrades", []) or []

        # Tooltip dla kopalni oraz innych budynków produkcyjnych
        lines = []

        # === bazowa produkcja ===
        if base_prod:
            for res, amount in base_prod.items():
                display_res = res

                # kopalnia: „trzcina” → prawdziwy surowiec ('węgiel', 'żelazo', 'srebro', 'złoto')
                if name == "mine":
                    display_res = self.loc.t("tooltip.mine_resource_placeholder")

                # premie państw
                bonus = 1.0
                if self.state == "sweden" and display_res == "wood":
                    bonus = STATES[self.state]["wood"]
                if self.state == "denmark" and display_res == "food":
                    bonus = STATES[self.state]["food"]
                if self.state == "brandenburg" and display_res == "steel":
                    bonus = STATES[self.state]["steel"]
                if self.state == "genua" and name == "mine":
                    bonus *= STATES[self.state].get("mine", 1.0)

                real_amount = amount * bonus
                lines.append(self.loc.t(
                    "tooltip.production_line",
                    level=0,
                    amount=f"{real_amount:g}",
                    res=display_res
                ))

        # === produkcja z ulepszeń ===
        for idx, up in enumerate(upgrades, start=1):
            up_prod = up.get("prod", up.get("base_prod", {})) or {}
            for res, amount in up_prod.items():
                display_res = res
                if name == "mine":
                    display_res = self.loc.t("tooltip.mine_resource_placeholder")

                bonus = 1.0
                if self.state == "sweden" and display_res == "wood":
                    bonus = STATES[self.state]["wood"]
                if self.state == "denmark" and display_res == "food":
                    bonus = STATES[self.state]["food"]
                if self.state == "brandenburg" and display_res == "steel":
                    bonus = STATES[self.state]["steel"]
                if self.state == "genua" and name == "mine":
                    bonus *= STATES[self.state].get("mine", 1.0)

                real_amount = amount * bonus
                lines.append(self.loc.t(
                    "tooltip.production_line",
                    level=idx,
                    amount=f"{real_amount:g}",
                    res=display_res
                ))

        if not lines:
            return self.loc.t("screen.buildings.no_direct_production")

        # Jeśli to kopalnia — dodaj precyzję opisu

        if name == "mine":
            return (
                    self.loc.t("tooltip.mine_header")
                    + "\n"
                    + "\n".join(lines)
            )

        return "\n".join(lines)
    def select_for_building(self, name, win):
        self.selected_building = name
        win.destroy()
        self.show_map()

    # === Zarządzanie pracownikami ===
    def manage_workers(self):

        win = self.create_window(self.loc.t("screen.workers.title"))

        title_font = getattr(self, "top_title_font", ("Cinzel", 14, "bold"))

        self.worker_sliders = []
        for i, b in enumerate(self.buildings):
            if b["base"] in ["district", "tent"]:
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
                text=self.loc.t("screen.buildings.no_jobs"),
                foreground="red",
                font=title_font
            ).pack(pady=15)
            ttk.Button(win, text=self.loc.t("ui.close"), command=win.destroy).pack(pady=5)
            self.center_window(win)
            return

            # wyśrodkuj okno statków
            self.center_window(win)
            return

        def save():
            # ile ludzi pracuje teraz (przed zmianą suwaków)
            current_total = sum(self.buildings[idx].get("workers", 0) for idx, _ in self.worker_sliders)

            # ile będzie pracować po zmianie suwaków
            new_total = sum(s.get() for _, s in self.worker_sliders)

            # o ile rośnie zapotrzebowanie na pracowników
            delta = new_total - current_total

            # jeśli trzeba więcej ludzi niż mamy WOLNYCH -> błąd
            if delta > self.free_workers():
                self.log(self.loc.t("log.not_enough_free_workers"), "red")
                return

            # zapisujemy nowe wartości
            for idx, scale in self.worker_sliders:
                self.buildings[idx]["workers"] = scale.get()

            self.log(self.loc.t("log.workers_assigned"), "green")
            win.destroy()

        ttk.Button(win, text=self.loc.t("ui.confirm"), command=save).pack(pady=10)

        # wyśrodkuj okno statków
        self.center_window(win)