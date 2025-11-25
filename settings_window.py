# settings_window.py
import tkinter as tk
from tkinter import ttk
import pygame


class SettingsWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.loc = app.loc

        self._pending_lang = app.settings.get("lang", "pl")

        self.title(self.loc.t("screen.settings.title", default="Settings"))
        self.resizable(False, False)

        # Flaga do bezpiecznego zamykania / trace
        self._closing = False

        BG = app.style.lookup("TFrame", "background")
        self.configure(bg=BG)

        # jeśli nie masz settings dict – utwórz minimalny
        if not hasattr(app, "settings"):
            app.settings = {
                "lang": getattr(app.loc, "lang", "pl"),
                "music_volume": 0.2,
                "sfx_volume": 0.5,
                "start_date_preset": "random",
            }

        container = ttk.Frame(self, padding=12)
        container.pack(fill="both", expand=True)

        title_font = getattr(app, "top_title_font", ("Cinzel", 14, "bold"))
        info_font = getattr(app, "top_info_font", ("EB Garamond Italic", 12))

        ttk.Label(
            container,
            text=self.loc.t("screen.settings.header", default="SETTINGS"),
            font=title_font
        ).pack(pady=(0, 8))

        # =========================================================
        # 1) JĘZYK
        # =========================================================
        lang_frame = ttk.LabelFrame(
            container,
            text=self.loc.t("settings.language.title", default="Language")
        )
        lang_frame.pack(fill="x", pady=6)

        ttk.Label(
            lang_frame,
            text=self.loc.t("settings.language.label", default="Choose language:"),
            font=info_font
        ).pack(anchor="w", padx=8, pady=(6, 2))

        self.lang_var = tk.StringVar(value=app.settings.get("lang", "pl"))
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=["pl", "en", "de"],
            state="readonly",
            width=10
        )
        lang_combo.pack(anchor="w", padx=8, pady=(0, 6))

        def on_lang_change(*_):
            if self._closing or not self.winfo_exists():
                return

            # tylko zapamiętaj wybór – bez przełączania języka w loc
            self._pending_lang = self.lang_var.get()
            app.settings["lang"] = self._pending_lang

        self._lang_trace_id = self.lang_var.trace_add("write", on_lang_change)

        # =========================================================
        # 2) MUZYKA (głośność)
        # =========================================================
        music_frame = ttk.LabelFrame(
            container,
            text=self.loc.t("settings.music.title", default="Music")
        )
        music_frame.pack(fill="x", pady=6)

        ttk.Label(
            music_frame,
            text=self.loc.t("settings.music.volume", default="Music volume:"),
            font=info_font
        ).pack(anchor="w", padx=8, pady=(6, 2))

        self.music_var = tk.DoubleVar(value=app.settings.get("music_volume", 0.2))

        music_scale = tk.Scale(
            music_frame,
            from_=0.0, to=1.0, resolution=0.05,
            orient="horizontal", variable=self.music_var, length=280
        )
        music_scale.pack(anchor="w", padx=8, pady=(0, 6))

        def on_music_change(*_):
            vol = float(self.music_var.get())
            app.settings["music_volume"] = vol
            try:
                pygame.mixer.music.set_volume(vol)
            except Exception:
                pass

        self.music_var.trace_add("write", on_music_change)

        # =========================================================
        # 3) DŹWIĘKI (głośność)
        # =========================================================
        sfx_frame = ttk.LabelFrame(
            container,
            text=self.loc.t("settings.sfx.title", default="Sounds")
        )
        sfx_frame.pack(fill="x", pady=6)

        ttk.Label(
            sfx_frame,
            text=self.loc.t("settings.sfx.volume", default="Sounds volume:"),
            font=info_font
        ).pack(anchor="w", padx=8, pady=(6, 2))

        self.sfx_var = tk.DoubleVar(value=app.settings.get("sfx_volume", 0.5))

        sfx_scale = tk.Scale(
            sfx_frame,
            from_=0.0, to=1.0, resolution=0.05,
            orient="horizontal", variable=self.sfx_var, length=280
        )
        sfx_scale.pack(anchor="w", padx=8, pady=(0, 6))

        def on_sfx_change(*_):
            vol = float(self.sfx_var.get())
            app.settings["sfx_volume"] = vol
            for snd in getattr(app, "sounds", {}).values():
                try:
                    snd.set_volume(vol)
                except Exception:
                    pass

        self.sfx_var.trace_add("write", on_sfx_change)

        # =========================================================
        # PRZYCISK ZAMKNIĘCIA
        # =========================================================
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=(8, 0), fill="x")

        ttk.Button(
            btn_frame,
            text=self.loc.t("ui.close", default="Close"),
            command=self.on_close
        ).pack()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        app.center_window(self)

    def refresh_texts(self):
        """Minimalny refresh tego okna po zmianie języka."""
        if not self.winfo_exists():
            return
        self.title(self.loc.t("screen.settings.title", default="Settings"))
        # jeśli chcesz pełny live-refresh sekcji/labeli, dopisz później.

    def on_close(self):
        """Zamknięcie okna: dopiero teraz odświeżamy główne menu."""
        if self._closing:
            return
        self._closing = True

        # zdejmij trace żeby nie strzelał po destroy
        try:
            self.lang_var.trace_remove("write", self._lang_trace_id)
        except Exception:
            pass

        # zastosuj język dopiero przy zamykaniu okna
        new_lang = getattr(self, "_pending_lang", self.app.settings.get("lang", "pl"))
        if new_lang != getattr(self.app.loc, "lang", None):
            self.app.settings["lang"] = new_lang
            self.app.loc.load_language(new_lang)
        # zapisz ustawienia na dysk
        self.app.save_settings()

        # odśwież odpowiedni ekran dopiero po zamknięciu
        if getattr(self.app, "current_screen", "start") == "start":
            self.app.refresh_start_screen()
        else:
            # jesteśmy w trakcie gry – tylko odśwież teksty UI gry
            if hasattr(self.app, "refresh_game_texts"):
                self.app.refresh_game_texts()

        self.destroy()
