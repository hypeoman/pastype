# Pastype

Types the clipboard text into the focused window, key by key. Useful where pasting is blocked: VNC/remote consoles, VM viewers, web terminals, installers.

## Usage

### Option 1: download a release

1. Open [Releases](https://github.com/hypeoman/pastype/releases) and download the file for your OS:
   - Windows: `Pastype-windows.exe`
   - macOS (Apple Silicon): `Pastype-macos.tar.gz`
   - Linux (x86_64): `Pastype-linux.tar.gz`
2. Run it:
   - Windows: double-click `Pastype-windows.exe`.
   - macOS / Linux:
     ```sh
     tar -xzf Pastype-*.tar.gz
     ./Pastype
     ```
3. See the per-OS notes below before first use.

### Option 2: run from source

Requires Python 3.11+ with tkinter.

```sh
git clone https://github.com/hypeoman/pastype.git
cd pastype
pip install -r requirements.txt
python main.py
```

To build a binary yourself: `pyinstaller Pastype.spec` → `dist/Pastype.exe` (or `dist/Pastype` on macOS/Linux). PyInstaller only builds for the OS it runs on.

### How to type

1. Copy text to the clipboard and press **Начать ввод** (or **F8**), or type/paste text into the **Свой текст** field and press **Ввести из поля**. Confirm.
2. Switch to the target window within the start delay (3 s by default).
3. **F9** or **Остановить** stops typing. **F10** hides/shows the window.

Settings: character delay (ms), line delay (ms, after each Enter), start delay (s). Increase the delays if the target drops characters (slow VNC links, web consoles).

Emergency stop: move the mouse to the **top-left corner** of the screen — PyAutoGUI's failsafe aborts typing.

Settings are saved to `~/AppData/Local/Pastype/settings.json` (on Windows: `%LOCALAPPDATA%\Pastype\settings.json`). Settings from the old `ClipboardTyper` folder are picked up automatically.

## How text is typed

- ASCII letters, digits, punctuation, Enter and Tab are sent as ordinary key presses (Shift is added for uppercase and symbols). This works through VNC and remote consoles.
- The keys are those of the **US layout**: switch the target to an English layout, otherwise e.g. `;` may come out as `ж`.
- Other characters (Cyrillic, accented letters, emoji) are sent with Windows Unicode input — **Windows only**. Many VNC clients and remote consoles do not forward Unicode input, so expect those characters to be lost there.
- `\r` is ignored, so Windows line endings produce one Enter per line.

## Per-OS notes and limitations

### Windows

- Fully supported: typing, Unicode, global hotkeys.
- The exe is unsigned: SmartScreen may show "Windows protected your PC" → **More info → Run anyway**. Some antivirus programs flag PyInstaller binaries as false positives.
- Windows blocks input into windows running **as Administrator** from a non-elevated program. To type into an elevated window (admin terminal, installer), run Pastype as Administrator too.

### macOS

- Release binary is built for **Apple Silicon** only. On Intel Macs, run from source.
- The binary is unsigned. If macOS refuses to open it, remove the quarantine flag:
  ```sh
  xattr -d com.apple.quarantine Pastype
  ```
- Grant **Accessibility** permission (System Settings → Privacy & Security → Accessibility) to Pastype, or to your terminal when running from source. Without it, keystrokes are silently dropped.
- Global hotkeys (F8/F9/F10) are unreliable on macOS (the `keyboard` library needs root there). If enabling them shows an error, uncheck **Глобальные горячие клавиши** and use the buttons. On Mac keyboards F-keys may also require **Fn**.
- No Unicode: only ASCII is typed, other characters are skipped.
- From source: Homebrew Python needs tkinter installed separately: `brew install python-tk`.

### Linux

- Works on **X11 only**. Under **Wayland**, emulated keystrokes do not reach other windows; log into an X11 session ("GNOME on Xorg" etc.).
- Global hotkeys need **root** (the `keyboard` library reads `/dev/input` directly). Without root, enabling hotkeys shows an error — uncheck them and use the buttons. Running the whole app with `sudo` may in turn fail to open the X display.
- No Unicode: only ASCII is typed, other characters are skipped.
- Release binary is built for x86_64 on the current Ubuntu; very old distros may lack a new enough glibc — run from source there.
- From source: install tkinter and the clipboard tool, e.g. on Debian/Ubuntu:
  ```sh
  sudo apt install python3-tk xclip
  ```
  (`pyperclip` needs `xclip` or `xsel` to read the clipboard.)

## Releasing

Push a tag starting with `v` (e.g. `git tag v0.1.0 && git push origin v0.1.0`). GitHub Actions builds Windows, macOS and Linux binaries and publishes them as a release.
