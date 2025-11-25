# save_load_windows.py
import tkinter as tk
from tkinter import ttk, messagebox as mb
from datetime import datetime

class SaveLoadWindow:
    """
    Unified okno do ZAPISU i WCZYTYWANIA.
    mode="save"  -> lista savów + na dole pole nazwy + przycisk ZAPISZ + Anuluj
    mode="load"  -> lista savów + tylko Anuluj
    Po prawej stronie każdego rekordu są przyciski:
      - Wczytaj (tylko w trybie load)
      - Zapisz (nadpisz) (tylko w trybie save)
      - Edytuj (zmiana nazwy)
      - Usuń (podwójne potwierdzenie)
    """

    def __init__(self, app, mode="load"):
        self.app = app
        self.mode = mode  # "save" / "load"
        self.win = app.create_window(
            app.loc.t("screen.save.title") if mode == "save" else app.loc.t("screen.load.title"),
            key=f"screen.{mode}_window"
        )

        self.win.columnconfigure(0, weight=1)
        outer = ttk.Frame(self.win, padding=12)
        outer.grid(row=0, column=0, sticky="nsew")
        outer.columnconfigure(0, weight=1)

        # sztuczne save'y na start
        self.saves = [
            {
                "name": app.loc.t("save.fake1.name", default="Autosave #1"),
                "date": "12 Nov 1607",
                "meta": app.loc.t("save.fake1.meta", default="Jamestown • Day 42")
            },
            {
                "name": app.loc.t("save.fake2.name", default="Manual Save"),
                "date": "18 Nov 1607",
                "meta": app.loc.t("save.fake2.meta", default="Fort Nassau • Day 57")
            }
        ]

        # ======= LISTA SAVÓW (środek okna) - scroll po ~5 rekordach =======
        list_wrap = ttk.Frame(outer)
        list_wrap.grid(row=0, column=0, sticky="nsew")
        list_wrap.columnconfigure(0, weight=1)
        list_wrap.rowconfigure(0, weight=1)

        # canvas o stałej wysokości (ok. 5 savów)
        self.list_canvas = tk.Canvas(list_wrap, height=420, highlightthickness=0,
                                     bg=self.app.style.lookup("TFrame", "background"))
        self.list_canvas.grid(row=0, column=0, sticky="nsew")

        self.list_scroll = ttk.Scrollbar(list_wrap, orient="vertical", command=self.list_canvas.yview)
        self.list_scroll.grid(row=0, column=1, sticky="ns")
        self.list_canvas.configure(yscrollcommand=self.list_scroll.set)

        # frame z rekordami wewnątrz canvasa
        self.list_frame = ttk.Frame(self.list_canvas)
        self._list_win = self.list_canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.list_frame.columnconfigure(0, weight=1)

        def _on_frame_configure(_evt=None):
            # ustaw scrollregion
            bbox = self.list_canvas.bbox("all")
            if not bbox:
                self.list_canvas.configure(scrollregion=(0, 0, 0, 0))
                self.list_scroll.state(["disabled"])
                return

            self.list_canvas.configure(scrollregion=bbox)

            # jeśli zawartość mieści się w canvasie -> scroll nieaktywny
            content_h = bbox[3] - bbox[1]
            canvas_h = self.list_canvas.winfo_height()

            if content_h <= canvas_h + 2:
                # blokujemy scroll i ustawiamy pasek na górze
                self.list_canvas.yview_moveto(0)
                self.list_scroll.state(["disabled"])
            else:
                self.list_scroll.state(["!disabled"])

        def _on_canvas_configure(evt):
            self.list_canvas.itemconfig(self._list_win, width=evt.width)

        self.list_frame.bind("<Configure>", _on_frame_configure)
        self.list_canvas.bind("<Configure>", _on_canvas_configure)

        self._render_list()

        # ======= DÓŁ OKNA =======
        if self.mode == "save":
            bottom = ttk.Frame(outer)
            bottom.grid(row=1, column=0, sticky="ew", pady=(10, 0))
            bottom.columnconfigure(0, weight=1)

            # pole nazwy
            name_row = ttk.Frame(bottom)
            name_row.grid(row=0, column=0, sticky="ew")
            name_row.columnconfigure(0, weight=1)

            ttk.Label(name_row, text=self.app.loc.t("screen.save.name_label")).grid(row=0, column=0, sticky="w")
            self.name_var = tk.StringVar(value="")
            self.name_entry = ttk.Entry(name_row, textvariable=self.name_var)
            self.name_entry.grid(row=1, column=0, sticky="ew", pady=(4, 6))

            # przycisk zapisz (nowy zapis)
            self.save_new_btn = ttk.Button(
                name_row, text=self.app.loc.t("ui.save"),
                command=self._save_new
            )
            self.save_new_btn.grid(row=1, column=1, padx=(8, 0))

            # anuluj na samym dole
            ttk.Button(bottom, text=self.app.loc.t("ui.cancel"), command=self.win.destroy).grid(row=2, column=0, pady=(8, 0), sticky="e")
        else:
            # tylko anuluj
            btn_row = ttk.Frame(outer)
            btn_row.grid(row=1, column=0, sticky="e", pady=(10, 0))
            ttk.Button(btn_row, text=self.app.loc.t("ui.cancel"), command=self.win.destroy).pack()

        self.app.center_window(self.win)

    # ========================= render listy =========================

        def _on_mousewheel(evt):
            if not self.list_canvas.winfo_exists():
                return
            # nie przewijaj gdy scrollbar disabled
            if "disabled" in self.list_scroll.state():
                return
            self.list_canvas.yview_scroll(int(-1 * (evt.delta / 120)), "units")

        self.list_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _render_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        for idx, s in enumerate(self.saves):
            row = ttk.Frame(self.list_frame, padding=6, relief="ridge")
            row.grid(row=idx, column=0, sticky="ew", pady=4)
            row.columnconfigure(0, weight=1)

            # lewa część: nazwa + meta + data
            left = ttk.Frame(row)
            left.grid(row=0, column=0, sticky="w")
            ttk.Label(left, text=s["name"], font=self.app.top_title_font if hasattr(self.app, "top_title_font") else ("Cinzel", 12, "bold")).pack(anchor="w")
            ttk.Label(left, text=s["meta"], foreground="gray").pack(anchor="w")
            ttk.Label(left, text=s["date"], foreground="gray").pack(anchor="w")

            # prawa część: przyciski
            right = ttk.Frame(row)
            right.grid(row=0, column=1, sticky="e", padx=(10, 0))

            if self.mode == "load":
                ttk.Button(right, text=self.app.loc.t("ui.load"), command=lambda i=idx: self._load(i)).pack(fill="x", pady=1)
            else:
                ttk.Button(right, text=self.app.loc.t("ui.save"), command=lambda i=idx: self._overwrite(i)).pack(fill="x", pady=1)

            ttk.Button(right, text=self.app.loc.t("ui.edit"), command=lambda i=idx: self._edit(i)).pack(fill="x", pady=1)
            ttk.Button(right, text=self.app.loc.t("ui.delete"), command=lambda i=idx: self._delete(i)).pack(fill="x", pady=1)

    # ========================= akcje =========================

    def _load(self, idx):
        # na razie nic nie robi (placeholder)
        self.app.log(self.app.loc.t("log.load_not_implemented"), "orange")

    def _overwrite(self, idx):
        # na razie nic nie robi (placeholder)
        self.app.log(self.app.loc.t("log.save_not_implemented"), "orange")

    def _save_new(self):
        name = self.name_var.get().strip()
        if not name:
            mb.showinfo(self.app.loc.t("screen.save.no_name_title"), self.app.loc.t("screen.save.no_name_text"))
            return

        now = datetime.now().strftime("%d %b %Y %H:%M")
        self.saves.insert(0, {"name": name, "date": now, "meta": self.app.loc.t("screen.save.new_meta", default="New Save")})
        self.name_var.set("")
        self._render_list()
        self.app.log(self.app.loc.t("log.save_not_implemented"), "orange")  # placeholder

    def _edit(self, idx):
        s = self.saves[idx]
        edit_win = self.app.create_window(self.app.loc.t("screen.edit_save.title"), key="screen.edit_save")
        frm = ttk.Frame(edit_win, padding=10); frm.pack(fill="both", expand=True)
        ttk.Label(frm, text=self.app.loc.t("screen.edit_save.label")).pack(anchor="w")

        var = tk.StringVar(value=s["name"])
        ent = ttk.Entry(frm, textvariable=var); ent.pack(fill="x", pady=6)

        def ok():
            new_name = var.get().strip()
            if new_name:
                s["name"] = new_name
                self._render_list()
            edit_win.destroy()

        btns = ttk.Frame(frm); btns.pack(anchor="e", pady=(6, 0))
        ttk.Button(btns, text=self.app.loc.t("ui.ok"), command=ok).pack(side="left", padx=4)
        ttk.Button(btns, text=self.app.loc.t("ui.cancel"), command=edit_win.destroy).pack(side="left", padx=4)
        self.app.center_window(edit_win)

    def _confirm_dialog(self, title_key, text_key, on_yes):
        """Spójne okno potwierdzenia TAK/NIE (styl jak wyjście z gry)."""
        dlg = self.app.create_window(self.app.loc.t(title_key), key="screen.confirm_generic")
        bg = self.app.style.lookup("TFrame", "background")

        frm = ttk.Frame(dlg, padding=12);
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text=self.app.loc.t(text_key), justify="center", background=bg).pack(pady=(4, 12))

        btns = ttk.Frame(frm);
        btns.pack()
        ttk.Button(btns, text=self.app.loc.t("ui.yes"), command=lambda: (dlg.destroy(), on_yes())).pack(side="left", padx=6)
        ttk.Button(btns, text=self.app.loc.t("ui.no"), command=dlg.destroy).pack(side="left", padx=6)

        self.app.center_window(dlg)

    def _delete(self, idx):
        def really_delete():
            self.saves.pop(idx)
            self._render_list()

        self._confirm_dialog("screen.delete_save.title", "screen.delete_save.q1", really_delete)
