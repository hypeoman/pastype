import json
from pathlib import Path

PATH = Path.home() / "AppData" / "Local" / "Pastype" / "settings.json"
OLD_PATH = Path.home() / "AppData" / "Local" / "ClipboardTyper" / "settings.json"  # pre-rename settings
DEFAULTS = {"char_delay": 15, "line_delay": 200, "start_delay": 3, "hotkeys": True}

def load():
    try:
        data = json.loads((PATH if PATH.exists() else OLD_PATH).read_text(encoding="utf-8"))
        return {**DEFAULTS, **{k: data[k] for k in DEFAULTS if k in data}}
    except (OSError, ValueError, TypeError):
        return DEFAULTS.copy()

def save(data):
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
