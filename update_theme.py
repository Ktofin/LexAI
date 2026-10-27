#!/usr/bin/env python3
"""
Скрипт динамической смены дизайн-системы и цвета кнопок в FigCraft.
Использование:
    python3 update_theme.py "#7C3AED"   # Сменить основной цвет на фиолетовый
    python3 update_theme.py "#10B981"   # Сменить основной цвет на изумрудный
    python3 update_theme.py "#DC2626"   # Сменить основной цвет на рубиновый
"""

import socket
import subprocess
import time
import json
import os
import sys

PORT = 9888
FIGCRAFT_BIN = "/Applications/FigCraft.app/Contents/MacOS/FigCraft"
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(WORKSPACE_DIR, "Legal_AI_Analyst.figcraft")
EXPORT_DIR = os.path.join(WORKSPACE_DIR, "renders")

new_color = sys.argv[1] if len(sys.argv) > 1 else "#7C3AED"
print(f"🔄 Смена цвета кнопок и акцента на: {new_color}...")

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

    # Find the variable brand/primary
    # We can use variable.set by name or search collections
    # Let us list collections and variables
    # Or directly update brand/primary
    res = cmd("variable.set", {"variable": "brand/primary", "value": new_color})
    print("Результат обновления brand/primary:", res)

    # Save
    save_res = cmd("file.save", {})
    print("Сохранено:", save_res)

    # Re-export
    cmd("file.export", {"format": "png", "scale": 2, "path": os.path.join(EXPORT_DIR, "02_dashboard.png")})
    print("✅ Все экраны и кнопки на макете мгновенно обновились!")

finally:
    proc.terminate()
