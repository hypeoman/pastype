import ctypes
import sys

import pyautogui

pyautogui.FAILSAFE = True

# ASCII goes through key presses (works over VNC); other chars use Windows Unicode input.
KEYS = {"\n": "enter", "\r": None, "\t": "tab", " ": "space",
        **{c: c for c in "abcdefghijklmnopqrstuvwxyz0123456789-=[]\\;'/,."}}
SHIFT = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+{}|:\"<>?",
                 "abcdefghijklmnopqrstuvwxyz1234567890-=[]\\;'/,."))

if sys.platform == "win32":
    from ctypes import wintypes

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]

    class _InputUnion(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT), ("pad", ctypes.c_byte * 32)]  # pad to MOUSEINPUT size

    class INPUT(ctypes.Structure):
        _anonymous_ = ("u",)
        _fields_ = [("type", wintypes.DWORD), ("u", _InputUnion)]

def _unicode_inputs(char):
    data = char.encode("utf-16-le")  # chars outside BMP become surrogate pairs
    codes = [int.from_bytes(data[i:i + 2], "little") for i in range(0, len(data), 2)]
    # type=1 INPUT_KEYBOARD, flags 4 KEYEVENTF_UNICODE, 2 KEYEVENTF_KEYUP
    return [INPUT(type=1, ki=KEYBDINPUT(0, code, 4 | up, 0, 0)) for code in codes for up in (0, 2)]

def _press_unicode(char):
    inputs = _unicode_inputs(char)
    array = (INPUT * len(inputs))(*inputs)
    if ctypes.windll.user32.SendInput(len(inputs), array, ctypes.sizeof(INPUT)) != len(inputs):
        raise OSError(f"Windows rejected input of {char!r} (is the target window running as Administrator?)")

def _sleep(seconds, stop):
    return stop.wait(seconds) if seconds > 0 else stop.is_set()

def type_text(text, char_delay, line_delay, start_delay, stop, progress):
    if _sleep(start_delay, stop):
        return
    for index, char in enumerate(text, 1):
        if stop.is_set():
            return
        if char in SHIFT:
            pyautogui.hotkey("shift", SHIFT[char])
        elif KEYS.get(char):
            pyautogui.press(KEYS[char])
        elif char not in KEYS and sys.platform == "win32":
            _press_unicode(char)
        progress(index, len(text))
        if _sleep(line_delay if char == "\n" else char_delay, stop):
            return
