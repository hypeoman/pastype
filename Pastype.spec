# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
a = Analysis(["main.py"], pathex=[], binaries=[], datas=[],
             hiddenimports=collect_submodules("pyautogui"), hookspath=[],
             hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="Pastype",
          console=False, upx=True, disable_windowed_traceback=False)
