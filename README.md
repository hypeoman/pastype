# Pastype

Windows tool for typing clipboard text into the focused window. Install Python 3.11+, then install requirements.txt and run main.py.

F8 starts, F9 stops, F10 hides or shows the window. Settings are stored in the local app data folder under Pastype/settings.json (settings from the old ClipboardTyper folder are picked up automatically).

Build with PyInstaller and Pastype.spec; output is dist/Pastype.exe.

The app emits ordinary keyboard events. ASCII is sent as key presses; other characters (e.g. Cyrillic) use Windows Unicode input, which some VNC clients do not forward. PyAutoGUI's upper-left corner failsafe aborts typing.
