import keyboard

class Hotkeys:
    def __init__(self, start, stop, toggle):
        self.callbacks = (start, stop, toggle)
        self.enabled = False
        self.handles = []

    def set_enabled(self, enabled):
        if enabled == self.enabled:
            return
        if enabled:
            for key, callback in zip(("F8", "F9", "F10"), self.callbacks):
                self.handles.append(keyboard.add_hotkey(key, callback))
        else:
            for handle in self.handles:
                keyboard.remove_hotkey(handle)
            self.handles.clear()
        self.enabled = enabled

    def close(self):
        self.set_enabled(False)
