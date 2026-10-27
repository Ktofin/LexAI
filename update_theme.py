#!/usr/bin/env python3
"""
Скрипт динамической смены дизайн-системы и цвета кнопок в FigCraft (Anthropic Dark).
Использование:
    python3 update_theme.py "#D97757"   # Фирменный терракотовый Anthropic (по умолчанию)
    python3 update_theme.py "#E05D5D"   # Рубиновый / Crimson
    python3 update_theme.py "#9D94E8"   # Аметистовый / Amethyst
    python3 update_theme.py "#52A874"   # Изумрудный / Forest Sage
    python3 update_theme.py "#E5A93C"   # Теплый янтарь / Ochre
"""

import socket
import subprocess
import time
import json
import os
import sys

PORT = 9897
FIGCRAFT_BIN = "/Applications/FigCraft.app/Contents/MacOS/FigCraft"
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(WORKSPACE_DIR, "Legal_AI_Analyst.figcraft")
EXPORT_DIR = os.path.join(WORKSPACE_DIR, "renders")

new_color = sys.argv[1] if len(sys.argv) > 1 else "#D97757"
print(f"🔄 Смена основного акцента brand/primary на: {new_color}...")

proc = subprocess.Popen([FIGCRAFT_BIN, "--control", str(PORT), FILE_PATH])
time.sleep(2.0)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", PORT))

    def cmd(action, params={}):
        req = json.dumps({"id": 1, "method": "engine.execute", "params": {"command": action, "params": params}}) + "\n"
        s.sendall(req.encode("utf-8"))
        buf = b""
        s.settimeout(10.0)
        while True:
            chunk = s.recv(16384)
            if not chunk: break
            buf += chunk
            if b"\n" in buf: break
        res = json.loads(buf.decode("utf-8"))
        return res.get("result")

    # Update variable brand/primary
    res = cmd("variable.set", {"variable": "brand/primary", "value": new_color})
    print("Результат обновления brand/primary:", res)

    # Save changes
    save_res = cmd("file.save", {})
    print("Сохранено в файл:", save_res)

    # Re-export dashboard preview
    cmd("file.export", {"format": "png", "scale": 2, "path": os.path.join(EXPORT_DIR, "02_dashboard_dark.png")})
    print(f"✅ Готово! Все кнопки на всех страницах и экранах мгновенно перекрашены в {new_color}!")

finally:
    proc.terminate()
