# game_menu.py
import tkinter as tk
from tkinter import ttk


class GameMenuWindow:
    """Okno menu gry (pauza)."""

    def __init__(self, app):
        self.app = app
        self.loc = app.loc

        # singleton okna – przez create_window z kluczem
        self.win = app.create_window(self.loc.t("ui.game_menu.title"), key="ui.game_menu")
        self.win.geometry("450x450")
        self.win.resizable(False, False)

        BG = app.style.lookup("TFrame", "background")
        self.win.configure(bg=BG)

        title_font = getattr(app, "top_title_font", ("Cinzel", 16, "bold"))
        btn_font = getattr(app, "ui_font", ("EB Garamond Italic", 16))

        container = ttk.Frame(self.win, padding=20)
        container.pack(fill="both", expand=True)

        self.title_lbl = ttk.Label(
            container,
            font=title_font
        )
        self.title_lbl.pack(pady=(0, 12))

        self.btn_continue = ttk.Button(
            container, style="Colonial.TButton", command=self.close
        )
        self.btn_continue.pack(fill="x", pady=6)

        self.btn_save = ttk.Button(
            container, style="Colonial.TButton", command=self.save_game_placeholder
        )
        self.btn_save.pack(fill="x", pady=6)

        self.btn_load = ttk.Button(
            container, style="Colonial.TButton", command=self.load_game_placeholder
        )
        self.btn_load.pack(fill="x", pady=6)

        self.btn_options = ttk.Button(
            container, style="Colonial.TButton", command=self.open_options
        )
        self.btn_options.pack(fill="x", pady=6)

        self.btn_quit = ttk.Button(
            container, style="Colonial.TButton", command=self.confirm_quit
        )
        self.btn_quit.pack(fill="x", pady=6)

        self.refresh_texts()
        app.center_window(self.win)

    # --- akcje ---
    def close(self):
        if self.win and self.win.winfo_exists():
            self.win.destroy()

    def save_game_placeholder(self):
        # na razie nic nie robi
        return

    def load_game_placeholder(self):
        # na razie nic nie robi
        return

    def refresh_texts(self):
        """Odświeża napisy w menu gry po zmianie języka."""
        if not (self.win and self.win.winfo_exists()):
            return

        self.win.title(self.loc.t("ui.game_menu.title"))
        self.title_lbl.config(text=self.loc.t("ui.game_menu.title"))
        self.btn_continue.config(text=self.loc.t("ui.game_menu.continue"))
        self.btn_save.config(text=self.loc.t("ui.game_menu.save"))
        self.btn_load.config(text=self.loc.t("ui.game_menu.load"))
        self.btn_options.config(text=self.loc.t("ui.game_menu.options"))
        self.btn_quit.config(text=self.loc.t("ui.game_menu.quit"))

    def open_options(self):
        self.app.open_settings()

    def confirm_quit(self):
        """Okno potwierdzenia wyjścia."""
        confirm = self.app.create_window(
            self.loc.t("ui.confirm_exit.title"),
            key="ui.confirm_exit"
        )
        confirm.geometry("380x180")
        confirm.resizable(False, False)

        frame = ttk.Frame(confirm, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=self.loc.t("ui.confirm_exit.question"),
            font=getattr(self.app, "top_info_font", ("EB Garamond Italic", 14))
        ).pack(pady=(10, 20))

        btn_row = ttk.Frame(frame)
        btn_row.pack()

        ttk.Button(
            btn_row,
            text=self.loc.t("ui.yes"),
            style="ColonialSecondary.TButton",
            command=lambda: self.quit_game(confirm)
        ).pack(side="left", padx=10)

        ttk.Button(
            btn_row,
            text=self.loc.t("ui.no"),
            style="ColonialSecondary.TButton",
            command=confirm.destroy
        ).pack(side="left", padx=10)

        self.app.center_window(confirm)

    def quit_game(self, confirm_win):
        try:
            if confirm_win and confirm_win.winfo_exists():
                confirm_win.destroy()
        finally:
            # zamknięcie gry
            self.app.root.destroy()
