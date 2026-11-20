import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import clipboard
import config
from hotkeys import Hotkeys
from typer import type_text

class PastypeApp:
    def __init__(self, root):
        self.root = root
        root.title("Pastype")
        root.resizable(False, False)
        self.settings = config.load()
        self.events = queue.Queue()
        self.worker = None
        self.status = tk.StringVar(value="Ready")
        self.count = tk.StringVar(value="Clipboard: —")
        self.progress = tk.DoubleVar(value=0)
        self.char_delay = tk.StringVar(value=str(self.settings["char_delay"]))
        self.line_delay = tk.StringVar(value=str(self.settings["line_delay"]))
        self.start_delay = tk.StringVar(value=str(self.settings["start_delay"]))
        self.hotkey_enabled = tk.BooleanVar(value=self.settings["hotkeys"])
        self.hotkeys = Hotkeys(lambda: root.after(0, self.start),
                               lambda: root.after(0, self.stop),
                               lambda: root.after(0, self.toggle_window))
        self._build()
        self._toggle_hotkeys()
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(100, self._poll)

    def _build(self):
        f = ttk.Frame(self.root, padding=14)
        f.grid()
        ttk.Label(f, text="Pastype", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(f, textvariable=self.status).grid(row=1, column=0, sticky="w", pady=6)
        ttk.Label(f, text="Hotkeys: F8 type · F9 stop · F10 window").grid(row=2, column=0, columnspan=2, sticky="w")
        for row, label, var, limit in [(3, "Character delay (ms)", self.char_delay, 200),
                                       (4, "Line delay (ms)", self.line_delay, 1000),
                                       (5, "Start delay (s)", self.start_delay, 10)]:
            ttk.Label(f, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Spinbox(f, from_=0, to=limit, textvariable=var, width=8).grid(row=row, column=1, sticky="e")
        ttk.Checkbutton(f, text="Global hotkeys", variable=self.hotkey_enabled,
                        command=self._toggle_hotkeys).grid(row=6, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Label(f, textvariable=self.count).grid(row=7, column=0, columnspan=2, sticky="w")
        ttk.Progressbar(f, maximum=100, variable=self.progress, length=300).grid(row=8, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Label(f, text="Typed:").grid(row=9, column=0, sticky="w")
        self.progress_label = ttk.Label(f, text="0 / 0")
        self.progress_label.grid(row=9, column=1, sticky="e")
        buttons = ttk.Frame(f)
        buttons.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(buttons, text="Type clipboard", command=self.start).pack(side="left")
        ttk.Button(buttons, text="Stop", command=self.stop).pack(side="left", padx=6)
        ttk.Button(buttons, text="Test", command=self.test).pack(side="right")
        ttk.Label(f, text="Custom text:").grid(row=11, column=0, sticky="w", pady=(12, 3))
        self.text_box = tk.Text(f, width=40, height=6, wrap="word", undo=True)
        self.text_box.grid(row=12, column=0, columnspan=2, sticky="ew")
        ttk.Button(f, text="Type text", command=self.start_from_box).grid(row=13, column=0, sticky="w", pady=(6, 0))

    def _values(self):
        vals = (int(self.char_delay.get()), int(self.line_delay.get()), float(self.start_delay.get()))
        if not 0 <= vals[0] <= 200 or not 0 <= vals[1] <= 1000 or not 0 <= vals[2] <= 10:
            raise ValueError("Check the allowed delay ranges.")
        self.settings.update(char_delay=vals[0], line_delay=vals[1], start_delay=vals[2], hotkeys=self.hotkey_enabled.get())
        config.save(self.settings)
        return vals

    def start(self, text=None):
        if self.worker and self.worker.is_alive():
            return
        try:
            delays = self._values()
            text = clipboard.read_text() if text is None else text
        except Exception as exc:
            messagebox.showerror("Pastype", f"Settings or clipboard error: {exc}")
            return
        if not text:
            messagebox.showinfo("Pastype", "Nothing to type.")
            return
        if not messagebox.askyesno("Confirm typing", f"Type {len(text)} characters?\nSwitch to the target window."):
            return
        self.stop_event = threading.Event()
        self.status.set("Typing…")
        self.worker = threading.Thread(target=self._type, args=(text, *delays, self.stop_event), daemon=True)
        self.worker.start()

    def _type(self, text, char_delay, line_delay, start_delay, stop):
        try:
            type_text(text, char_delay / 1000, line_delay / 1000, start_delay, stop,
                      lambda done, total: self.events.put(("progress", done, total)))
            self.events.put(("done", "Stopped" if stop.is_set() else "Done"))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def stop(self):
        if hasattr(self, "stop_event"):
            self.stop_event.set()
            self.status.set("Stopping…")

    def start_from_box(self):
        self.start(self.text_box.get("1.0", "end-1c"))

    def test(self):
        self.start("Pastype: test 123\n")

    def _poll(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "progress":
                    _, done, total = event
                    self.progress.set(done * 100 / total)
                    self.progress_label.config(text=f"{done} / {total}")
                elif event[0] == "done":
                    self.status.set(event[1])
                else:
                    self.status.set("Error")
                    messagebox.showerror("Typing error", event[1])
        except queue.Empty:
            pass
        try:
            self.count.set(f"Clipboard: {len(clipboard.read_text())} characters")
        except Exception:
            self.count.set("Clipboard: unavailable")
        self.root.after(300, self._poll)

    def _toggle_hotkeys(self):
        try:
            self.hotkeys.set_enabled(self.hotkey_enabled.get())
        except Exception as exc:
            self.hotkey_enabled.set(False)
            messagebox.showerror("Hotkeys", str(exc))

    def toggle_window(self):
        self.root.withdraw() if self.root.state() != "withdrawn" else self.root.deiconify()

    def close(self):
        self.stop()
        self.hotkeys.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
