# tooltip.py
import tkinter as tk


class Tooltip:
    def __init__(self, widget, text, delay=500):
        """
        widget – kontrolka, do której tooltip ma być przypięty
        text – string LUB funkcja bezargumentowa zwracająca string
        delay – opóźnienie w ms przed pokazaniem (domyślnie 500 ms)
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self._id = None
        self._tipwindow = None

        if self.widget is not None:
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<ButtonPress>", self._on_leave)  # schowaj przy kliknięciu

    def _on_enter(self, event=None):
        self._schedule()

    def _on_leave(self, event=None):
        self._unschedule()
        self._hide_tip()

    def _schedule(self):
        self._unschedule()
        self._id = self.widget.after(self.delay, self._show_tip)

    def _unschedule(self):
        if self._id is not None:
            self.widget.after_cancel(self._id)
            self._id = None

    def _show_tip(self, event=None):
        if self._tipwindow is not None:
            return

        # dynamiczny tekst, jeśli text jest funkcją
        if callable(self.text):
            text = self.text()
        else:
            text = self.text

        if not text:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self._tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # bez ramek okna
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("EB Garamond Italic", 10),
        )
        label.pack(ipadx=4, ipady=2)

    def _hide_tip(self):
        if self._tipwindow is not None:
            self._tipwindow.destroy()
            self._tipwindow = None
