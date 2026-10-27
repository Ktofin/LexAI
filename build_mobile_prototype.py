#!/usr/bin/env python3
"""
LexAI Legal — 6-Screen Interactive Mobile Prototype (iPhone 14/15/16: 390×844 px).
Designed specifically for mobile ergonomics:
1. 01_Mobile_Welcome: Value proposition in 3 steps, instant scan CTA, trust bar.
2. 02_Mobile_Auth: Clean login form, Face ID biometric quick access, SSO & guest test.
3. 03_Mobile_Dashboard: 2x2 compact KPI cards, quick filters, contract cards with SPARK & risk scores, bottom tab bar + FAB.
4. 04_Mobile_Processing: Live document sheet on top with highlighted clause, issues stream below, completion progress bar.
5. 05_Mobile_Contract_Inspector: Sticky risk banner, Redline diff card, Voice note player, Judicial predictor, Diadoc export.
6. 06_Mobile_Risk_Analytics: Executive metrics (18.4M ₽ saved), risk breakdown bars, weekly dynamic, lawyer workload.
"""

import socket
import json
import time
import os
import sys

PORT = 9897
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(WORKSPACE_DIR, "Legal_AI_Analyst.figcraft")
EXPORT_DIR = os.path.join(WORKSPACE_DIR, "renders")
os.makedirs(EXPORT_DIR, exist_ok=True)

print(f"🔄 Подключение к открытому FigCraft на порту {PORT}...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(("127.0.0.1", PORT))
except Exception as e:
    print(f"❌ Ошибка подключения к порту {PORT}: {e}")
    sys.exit(1)

def cmd(action, params=None):
    if params is None: params = {}
    req = json.dumps({"id": 1, "method": "engine.execute", "params": {"command": action, "params": params}}) + "\n"
    s.sendall(req.encode("utf-8"))
    buf = b""
    s.settimeout(15.0)
    while True:
        chunk = s.recv(16384)
        if not chunk: break
        buf += chunk
        if b"\n" in buf: break
    res = json.loads(buf.decode("utf-8"))
    if "error" in res and res["error"]:
        print(f"⚠️ Ошибка команды {action}: {res['error']}")
    return res.get("result")

# Design Tokens (Anthropic Warm Linen & Terracotta)
tokens = {
    "brand/primary": "#D97757",       # Terracotta
    "brand/primary-hover": "#C56546",
    "brand/primary-light": "#FAECE7", # Soft Terracotta tint
    
    "light/bg": "#FAF9F5",            # Warm Linen Canvas
    "light/card": "#FFFFFF",          # Elevated Pure Card
    "light/card-tint": "#F5F3ED",     # Secondary Card Tint
    "light/card-warm": "#FBF7F0",     # Warm Zone
    "light/border": "#E5E3D8",        # Subtle Border
    "light/border-subtle": "#EFECE6",
    "light/border-dark": "#D5D2C5",
    
    "light/text-main": "#141413",     # Obsidian
    "light/text-sec": "#66645E",      # Muted Charcoal
    "light/text-muted": "#918E85",    # Subtle caption
    
    "light/crit-bg": "#FEF2F2",       # Red Critical Alert
    "light/crit-bdr": "#FECACA",
    "light/crit-txt": "#DC2626",
    
    "light/contra-bg": "#F5F3FF",     # Purple Contradiction Alert
    "light/contra-bdr": "#DDD6FE",
    "light/contra-txt": "#7C3AED",
    
    "light/warn-bg": "#FFFBEB",       # Amber Warning
    "light/warn-bdr": "#FDE68A",
    "light/warn-txt": "#B45309",
    
    "light/safe-bg": "#F0FDF4",       # Emerald Safe
    "light/safe-bdr": "#BBF7D0",
    "light/safe-txt": "#15803D",
    
    "light/blue-bg": "#EFF6FF",       # Blue Information
    "light/blue-bdr": "#BFDBFE",
    "light/blue-txt": "#2563EB",
}

# Helpers
def make_text(parent, text, font_size=12, font_style="Regular", fill=None, width=None, **kwargs):
    props = {"fontSize": font_size, "fontStyle": font_style}
    if fill: props["fill"] = fill
    if width:
        props["width"] = width
        props["textAutoResize"] = "height"
    else:
        props["textAutoResize"] = "widthAndHeight"
    node = cmd("node.create", {"type": "text", "parent": parent, "text": text, "props": props})
    return node["id"] if node else None

def make_btn(parent, text, variant="primary", size="md", width=350, **kwargs):
    cfg = {
        "lg": {"h": 46, "font": 14, "r": 8},
        "md": {"h": 40, "font": 13, "r": 6},
        "sm": {"h": 32, "font": 12, "r": 6},
        "xs": {"h": 26, "font": 11, "r": 4}
    }.get(size, {"h": 40, "font": 13, "r": 6})
    
    bg, stroke, stroke_w, txt_c = None, None, 0, tokens["light/text-main"]
    if variant == "primary":
        bg, txt_c = tokens["brand/primary"], "#FFFFFF"
    elif variant == "secondary":
        bg, stroke, stroke_w, txt_c = tokens["light/card-tint"], tokens["light/border"], 1, tokens["light/text-main"]
    elif variant == "outline":
        stroke, stroke_w, txt_c = tokens["light/border"], 1, tokens["light/text-main"]
    elif variant == "danger":
        bg, stroke, stroke_w, txt_c = tokens["light/crit-bg"], tokens["light/crit-bdr"], 1, tokens["light/crit-txt"]
    elif variant == "success":
        bg, stroke, stroke_w, txt_c = tokens["light/safe-bg"], tokens["light/safe-bdr"], 1, tokens["light/safe-txt"]
        
    props = {
        "cornerRadius": cfg["r"], "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"
    }
    if bg: props["fill"] = bg
    else: props["fills"] = []
    if stroke: props["stroke"], props["strokeWeight"] = stroke, stroke_w
    
    b = cmd("frame.create", {"parent": parent, "width": width, "height": cfg["h"], "props": props})
    cmd("node.create", {"type": "text", "parent": b["id"], "text": text, "props": {"fontSize": cfg["font"], "fontStyle": "Bold", "fill": txt_c}})
    return b["id"]

def make_badge(parent, text, btype="safe", size="compact", **kwargs):
    cfg = {"compact": {"h": 20, "font": 10, "px": 8, "dot": 5}, "regular": {"h": 24, "font": 11, "px": 10, "dot": 6}}.get(size, {"h": 20, "font": 10, "px": 8, "dot": 5})
    mapping = {
        "critical": (tokens["light/crit-bg"], tokens["light/crit-bdr"], tokens["light/crit-txt"]),
        "contradiction": (tokens["light/contra-bg"], tokens["light/contra-bdr"], tokens["light/contra-txt"]),
        "warning": (tokens["light/warn-bg"], tokens["light/warn-bdr"], tokens["light/warn-txt"]),
        "safe": (tokens["light/safe-bg"], tokens["light/safe-bdr"], tokens["light/safe-txt"]),
        "blue": (tokens["light/blue-bg"], tokens["light/blue-bdr"], tokens["light/blue-txt"]),
        "primary": (tokens["brand/primary-light"], tokens["brand/primary"], tokens["brand/primary"]),
    }
    bg, bdr, txt_c = mapping.get(btype, mapping["safe"])
    min_w = int(len(text) * cfg["font"] * 0.70 + 2 * cfg["px"] + cfg["dot"] + 6)
    badge = cmd("frame.create", {
        "parent": parent, "width": min_w, "height": cfg["h"],
        "props": {"fill": bg, "stroke": bdr, "strokeWeight": 1, "cornerRadius": 100, "layout": "horizontal", "padding": [0, cfg["px"], 0, cfg["px"]], "gap": 5, "crossAlign": "center"}
    })
    cmd("frame.create", {"parent": badge["id"], "width": cfg["dot"], "height": cfg["dot"], "props": {"fill": txt_c, "cornerRadius": cfg["dot"] // 2}})
    cmd("node.create", {"type": "text", "parent": badge["id"], "text": text, "props": {"fontSize": cfg["font"], "fontStyle": "Bold", "fill": txt_c}})
    return badge["id"]

def make_ios_status_bar(parent, width=390):
    sb = cmd("frame.create", {
        "parent": parent, "width": width, "height": 44,
        "props": {"fills": [], "layout": "horizontal", "padding": [0, 20, 0, 20], "mainAlign": "spaceBetween", "crossAlign": "center"}
    })
    # Time
    cmd("node.create", {"type": "text", "parent": sb["id"], "text": "09:41", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": tokens["light/text-main"]}})
    # Dynamic Island pill
    di = cmd("frame.create", {"parent": sb["id"], "width": 110, "height": 26, "props": {"fill": "#000000", "cornerRadius": 13, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
    cmd("frame.create", {"parent": di["id"], "width": 10, "height": 10, "props": {"fill": "#1C1C1E", "cornerRadius": 5}})
    # Battery & Signal
    cmd("node.create", {"type": "text", "parent": sb["id"], "text": "5G  􀛨", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens["light/text-main"]}})
    return sb["id"]

def make_ios_tab_bar(parent, active_tab="Договоры", width=390):
    bar = cmd("frame.create", {
        "parent": parent, "width": width, "height": 64,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "layout": "vertical", "padding": [6, 16, 6, 16], "mainAlign": "spaceBetween", "crossAlign": "center"
        }
    })
    items_row = cmd("frame.create", {"parent": bar["id"], "width": width - 32, "height": 42, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceAround", "crossAlign": "center"}})
    tabs = [
        ("Договоры", "📄"),
        ("Аналитика", "📊"),
        ("Playbook", "⚙️"),
        ("Команда", "👥")
    ]
    for name, icon in tabs:
        is_act = (name == active_tab)
        item = cmd("frame.create", {"parent": items_row["id"], "width": 64, "height": 40, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "crossAlign": "center", "gap": 2}})
        cmd("node.create", {"type": "text", "parent": item["id"], "text": icon, "props": {"fontSize": 14}})
        cmd("node.create", {"type": "text", "parent": item["id"], "text": name, "props": {"fontSize": 10, "fontStyle": "Bold" if is_act else "Regular", "fill": tokens["brand/primary"] if is_act else tokens["light/text-sec"]}})
    
    # Home indicator
    cmd("frame.create", {"parent": bar["id"], "width": 134, "height": 4, "props": {"fill": tokens["light/text-main"], "cornerRadius": 2}})
    return bar["id"]

# ==============================================================================
# PREPARE PAGE 4 (📱 Mobile Screens — iOS)
# ==============================================================================
p4_id = 15405
print(f"Очистка старых экранов на Page 4 (id={p4_id})...")
p4_info = cmd("node.get", {"id": p4_id})
if p4_info and "children" in p4_info:
    old_ids = [c["id"] for c in p4_info["children"]]
    if old_ids:
        cmd("edit.delete", {"ids": old_ids})
        print(f"  Удалено старых узлов: {len(old_ids)}")


# ==============================================================================
# SCREEN 1: 01_Mobile_Welcome (390×844)
# ==============================================================================
print("\n[1/6] Сборка 01_Mobile_Welcome...")
m1 = cmd("frame.create", {
    "parent": p4_id, "name": "01_Mobile_Welcome", "x": 0, "y": 0, "width": 390, "height": 844,
    "props": {"fill": tokens["light/bg"], "clip": True, "layout": "vertical", "gap": 0}
})
make_ios_status_bar(m1["id"])

# Header bar (h=44)
h1 = cmd("frame.create", {
    "parent": m1["id"], "width": 390, "height": 44,
    "props": {"fills": [], "layout": "horizontal", "padding": [0, 20, 0, 20], "mainAlign": "spaceBetween", "crossAlign": "center"}
})
logo_b = cmd("frame.create", {"parent": h1["id"], "width": 140, "height": 26, "props": {"fills": [], "layout": "horizontal", "gap": 6, "crossAlign": "center"}})
mark = cmd("frame.create", {"parent": logo_b["id"], "width": 22, "height": 22, "props": {"fill": tokens["brand/primary"], "cornerRadius": 5, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": mark["id"], "text": "§", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": "#FFFFFF"}})
make_text(logo_b["id"], "LexAI Legal", font_size=16, font_style="Bold", fill=tokens["light/text-main"])
make_badge(h1["id"], "152-ФЗ Контур", "safe", size="compact")

# Scrollable body (w=390, h=756)
b1 = cmd("frame.create", {
    "parent": m1["id"], "width": 390, "height": 756,
    "props": {"fills": [], "layout": "vertical", "padding": [12, 20, 16, 20], "gap": 12, "crossAlign": "center"}
})

# Hero Card
hc = cmd("frame.create", {
    "parent": b1["id"], "width": 350, "height": 290,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 12, "layout": "vertical", "padding": 16, "gap": 10
    }
})
make_badge(hc["id"], "ИИ-аналитик на базе GigaChat", "primary", size="compact")
make_text(hc["id"], "Аудит договоров и защита от рисков за 90 секунд", font_size=18, font_style="Bold", fill=tokens["light/text-main"], width=318)
make_text(hc["id"], "Автоматически сопоставляет разделы, выявляет несоразмерную неустойку и формирует протокол разногласий.", font_size=12, fill=tokens["light/text-sec"], width=318)

# Buttons inside hero
make_btn(hc["id"], "Попробовать бесплатно →", "primary", size="md", width=318)
make_btn(hc["id"], "Запросить демо для юротдела", "secondary", size="md", width=318)

# Trust row
t_row = cmd("frame.create", {"parent": hc["id"], "width": 318, "height": 20, "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
make_text(t_row["id"], "✓ 100% On-Premise", font_size=10, font_style="Bold", fill=tokens["light/safe-txt"])
make_text(t_row["id"], "✓ ст. 333 ГК РФ", font_size=10, font_style="Bold", fill=tokens["light/safe-txt"])
make_text(t_row["id"], "✓ СПАРК", font_size=10, font_style="Bold", fill=tokens["light/safe-txt"])

# Steps section header
make_text(b1["id"], "Плюсы платформы в 3 шага:", font_size=14, font_style="Bold", fill=tokens["light/text-main"], width=350)

# Steps vertical list
steps = [
    ("ШАГ 01", "primary", "Мгновенная загрузка и умный OCR", "PDF, DOCX и нераспознанные сканы до 50 МБ. Двуязычные тексты RU / EN."),
    ("ШАГ 02", "contradiction", "Поиск скрытых рисков и коллизий", "Проверка по ст. 333, 401 ГК РФ и поиск нестыковок между разделами договора."),
    ("ШАГ 03", "safe", "Готовый протокол разногласий", "Безопасные формулировки, экспорт в .DOCX и передача в Диадок СЭД в 1 клик.")
]
for step_num, b_type, s_title, s_desc in steps:
    sc = cmd("frame.create", {
        "parent": b1["id"], "width": 350, "height": 92,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "cornerRadius": 10, "layout": "vertical", "padding": 10, "gap": 4
        }
    })
    s_top = cmd("frame.create", {"parent": sc["id"], "width": 330, "height": 20, "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
    make_badge(s_top["id"], step_num, b_type, size="compact")
    make_text(s_top["id"], s_title, font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=230)
    make_text(sc["id"], s_desc, font_size=11, fill=tokens["light/text-sec"], width=330)

# Integrations footer
int_f = cmd("frame.create", {"parent": b1["id"], "width": 350, "height": 26, "props": {"fill": tokens["light/card-tint"], "cornerRadius": 6, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
make_text(int_f["id"], "Готовые интеграции: 1С • Диадок • СПАРК • Мой Арбитр", font_size=10, font_style="Bold", fill=tokens["light/text-sec"])


# ==============================================================================
# SCREEN 2: 02_Mobile_Auth (390×844)
# ==============================================================================
print("\n[2/6] Сборка 02_Mobile_Auth...")
m2 = cmd("frame.create", {
    "parent": p4_id, "name": "02_Mobile_Auth", "x": 430, "y": 0, "width": 390, "height": 844,
    "props": {"fill": tokens["light/bg"], "clip": True, "layout": "vertical", "gap": 0}
})
make_ios_status_bar(m2["id"])

# Header bar
h2 = cmd("frame.create", {
    "parent": m2["id"], "width": 390, "height": 44,
    "props": {"fills": [], "layout": "horizontal", "padding": [0, 20, 0, 20], "mainAlign": "spaceBetween", "crossAlign": "center"}
})
back_b = cmd("frame.create", {"parent": h2["id"], "width": 100, "height": 24, "props": {"fills": [], "layout": "horizontal", "gap": 6, "crossAlign": "center"}})
make_text(back_b["id"], "← Назад", font_size=13, font_style="Bold", fill=tokens["brand/primary"])
make_badge(h2["id"], "Шлюз 152-ФЗ", "safe", size="compact")

# Content Body
b2 = cmd("frame.create", {
    "parent": m2["id"], "width": 390, "height": 756,
    "props": {"fills": [], "layout": "vertical", "padding": [12, 20, 16, 20], "gap": 12, "crossAlign": "center"}
})

# Login Card
lc = cmd("frame.create", {
    "parent": b2["id"], "width": 350, "height": 415,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 12, "layout": "vertical", "padding": 14, "gap": 10
    }
})
make_badge(lc["id"], "Авторизация юриста", "primary", size="compact")
make_text(lc["id"], "Вход в рабочий кабинет", font_size=18, font_style="Bold", fill=tokens["light/text-main"], width=318)
make_text(lc["id"], "Введите корпоративный email для доступа к реестру договоров.", font_size=11, fill=tokens["light/text-sec"], width=318)

# Input 1: Email
cmd("node.create", {"type": "text", "parent": lc["id"], "text": "Корпоративный Email / Логин:", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": tokens["light/text-sec"]}})
in1 = cmd("frame.create", {"parent": lc["id"], "width": 318, "height": 36, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 12, 0, 12], "crossAlign": "center"}})
make_text(in1["id"], "alexey.smirnov@technosnab.ru", font_size=12, fill=tokens["light/text-main"])

# Input 2: Password
pw_lbl = cmd("frame.create", {"parent": lc["id"], "width": 318, "height": 16, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(pw_lbl["id"], "Пароль учетной записи:", font_size=11, font_style="Bold", fill=tokens["light/text-sec"])
make_text(pw_lbl["id"], "Забыли пароль?", font_size=11, font_style="Bold", fill=tokens["brand/primary"])
in2 = cmd("frame.create", {"parent": lc["id"], "width": 318, "height": 36, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 12, 0, 12], "crossAlign": "center"}})
make_text(in2["id"], "••••••••••••••••", font_size=14, fill=tokens["light/text-main"])

# Remember device
rem_row = cmd("frame.create", {"parent": lc["id"], "width": 318, "height": 18, "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
make_badge(rem_row["id"], "ГОСТ 2FA", "safe", size="compact")
make_text(rem_row["id"], "Запомнить сессию на смартфоне", font_size=11, fill=tokens["light/text-sec"])

# Submit Button
make_btn(lc["id"], "Войти в систему →", "primary", size="md", width=318)

# Biometric & SSO buttons
make_btn(lc["id"], "👤 Войти через Face ID / Touch ID", "secondary", size="sm", width=318)
make_btn(lc["id"], "Вход через Keycloak / Active Directory", "outline", size="xs", width=318)

# Guest Test Card below
gt = cmd("frame.create", {
    "parent": b2["id"], "width": 350, "height": 115,
    "props": {
        "fill": tokens["light/card-warm"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": 10, "gap": 4
    }
})
make_badge(gt["id"], "Экспресс-тест без входа", "primary", size="compact")
make_text(gt["id"], "Проверьте 3 страницы договора без регистрации", font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=326)
make_text(gt["id"], "Мгновенный расчет неустойки по ст. 333 ГК РФ и экспресс-вердикт.", font_size=10, fill=tokens["light/text-sec"], width=326)
make_btn(gt["id"], "Запустить экспресс-тест (3 стр.) →", "secondary", size="sm", width=326)


# ==============================================================================
# SCREEN 3: 03_Mobile_Dashboard (390×844)
# ==============================================================================
print("\n[3/6] Сборка 03_Mobile_Dashboard...")
m3 = cmd("frame.create", {
    "parent": p4_id, "name": "03_Mobile_Dashboard", "x": 860, "y": 0, "width": 390, "height": 844,
    "props": {"fill": tokens["light/bg"], "clip": True, "layout": "vertical", "gap": 0}
})
make_ios_status_bar(m3["id"])

# User header (h=52)
uh = cmd("frame.create", {
    "parent": m3["id"], "width": 390, "height": 52,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "layout": "horizontal", "padding": [0, 20, 0, 20], "mainAlign": "spaceBetween", "crossAlign": "center"
    }
})
u_info = cmd("frame.create", {"parent": uh["id"], "width": 240, "height": 38, "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
av3 = cmd("frame.create", {"parent": u_info["id"], "width": 34, "height": 34, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["brand/primary"], "strokeWeight": 1.5, "cornerRadius": 17, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": av3["id"], "text": "АС", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens["brand/primary"]}})
u_txt = cmd("frame.create", {"parent": u_info["id"], "width": 190, "height": 34, "props": {"fills": [], "layout": "vertical", "mainAlign": "center"}})
make_text(u_txt["id"], "Алексей Смирнов", font_size=13, font_style="Bold", fill=tokens["light/text-main"])
make_text(u_txt["id"], "Ведущий юрист • ТехноСнаб", font_size=11, fill=tokens["light/text-sec"])
make_badge(uh["id"], "3 критических риска", "critical", size="compact")

# Dashboard Content Body (h=684)
b3 = cmd("frame.create", {
    "parent": m3["id"], "width": 390, "height": 684,
    "props": {"fills": [], "layout": "vertical", "padding": [10, 20, 10, 20], "gap": 10, "crossAlign": "center"}
})

# 2x2 KPI Grid (w=350, h=136)
kpi_grid = cmd("frame.create", {"parent": b3["id"], "width": 350, "height": 136, "props": {"fills": [], "layout": "vertical", "gap": 8}})
kpi_r1 = cmd("frame.create", {"parent": kpi_grid["id"], "width": 350, "height": 64, "props": {"fills": [], "layout": "horizontal", "gap": 8}})
kpi_r2 = cmd("frame.create", {"parent": kpi_grid["id"], "width": 350, "height": 64, "props": {"fills": [], "layout": "horizontal", "gap": 8}})

kpis = [
    (kpi_r1, "24", "В обработке", "warning", tokens["light/warn-txt"]),
    (kpi_r1, "3", "Критических риска", "critical", tokens["light/crit-txt"]),
    (kpi_r2, "118", "Согласовано", "safe", tokens["light/safe-txt"]),
    (kpi_r2, "142 ч", "Сэкономлено", "blue", tokens["light/blue-txt"]),
]
for p_row, val, lbl, b_t, col in kpis:
    kc = cmd("frame.create", {
        "parent": p_row["id"], "width": 171, "height": 64,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "cornerRadius": 8, "layout": "vertical", "padding": [8, 12, 8, 12], "mainAlign": "center", "gap": 2
        }
    })
    cmd("node.create", {"type": "text", "parent": kc["id"], "text": val, "props": {"fontSize": 18, "fontStyle": "Bold", "fill": col}})
    make_text(kc["id"], lbl, font_size=10, fill=tokens["light/text-sec"])

# Search input (w=350, h=36)
sinp = cmd("frame.create", {
    "parent": b3["id"], "width": 350, "height": 36,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 6, "layout": "horizontal", "padding": [0, 12, 0, 12], "crossAlign": "center", "gap": 8
    }
})
cmd("node.create", {"type": "text", "parent": sinp["id"], "text": "🔍", "props": {"fontSize": 12}})
make_text(sinp["id"], "Поиск по номеру, контрагенту или ИНН...", font_size=11, fill=tokens["light/text-muted"])

# Filter pills scroll (w=350, h=26)
fpills = cmd("frame.create", {"parent": b3["id"], "width": 350, "height": 26, "props": {"fills": [], "layout": "horizontal", "gap": 6, "crossAlign": "center"}})
make_badge(fpills["id"], "Все (145)", "primary", size="compact")
make_badge(fpills["id"], "Высокий риск (3)", "critical", size="compact")
make_badge(fpills["id"], "На подписи (12)", "warning", size="compact")
make_badge(fpills["id"], "Согласовано", "safe", size="compact")

# Contract Cards List (3 cards)
contracts = [
    ("Договор поставки оборудования № 48/2026", "critical", "Высокий (3)", "ООО «ПромСтанкоКомплект» • СПАРК 74", "Несоразмерная неустойка 5%/день (2.42 млн ₽) • Коллизия п. 3.2 vs 6.4", "4.85 млн ₽"),
    ("Договор аренды помещений № 12-А/2026", "safe", "Безопасно", "ПАО «Бизнес Центр Сити» • СПАРК 92", "Все условия соответствуют Playbook. Замечаний нет.", "850 000 ₽"),
    ("Договор подряда на разработку ПО № П-09", "warning", "Внимание (1)", "ООО «Диджитал Системс» • СПАРК 68", "Невыгодная территориальная подсудность (Арбитраж г. Пермь).", "2.10 млн ₽")
]

for c_title, c_btype, c_blbl, c_party, c_risk, c_sum in contracts:
    cc = cmd("frame.create", {
        "parent": b3["id"], "width": 350, "height": 118,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "cornerRadius": 10, "layout": "vertical", "padding": 10, "gap": 4
        }
    })
    c_top = cmd("frame.create", {"parent": cc["id"], "width": 330, "height": 20, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
    make_text(c_top["id"], c_title, font_size=11, font_style="Bold", fill=tokens["light/text-main"], width=220)
    make_badge(c_top["id"], c_blbl, c_btype, size="compact")
    
    make_text(cc["id"], c_party, font_size=10, font_style="Bold", fill=tokens["light/text-sec"], width=330)
    make_text(cc["id"], c_risk, font_size=10, fill=tokens["light/crit-txt"] if c_btype == "critical" else tokens["light/text-sec"], width=330)
    
    c_bot = cmd("frame.create", {"parent": cc["id"], "width": 330, "height": 20, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
    make_text(c_bot["id"], f"Сумма: {c_sum}", font_size=10, font_style="Bold", fill=tokens["light/text-main"])
    make_text(c_bot["id"], "Открыть анализ →", font_size=11, font_style="Bold", fill=tokens["brand/primary"])

# Bottom Tab Bar
make_ios_tab_bar(m3["id"], active_tab="Договоры")


# ==============================================================================
# SCREEN 4: 04_Mobile_Processing (390×844)
# ==============================================================================
print("\n[4/6] Сборка 04_Mobile_Processing...")
m4 = cmd("frame.create", {
    "parent": p4_id, "name": "04_Mobile_Processing", "x": 1290, "y": 0, "width": 390, "height": 844,
    "props": {"fill": tokens["light/bg"], "clip": True, "layout": "vertical", "gap": 0}
})
make_ios_status_bar(m4["id"])

# Header bar
h4 = cmd("frame.create", {
    "parent": m4["id"], "width": 390, "height": 44,
    "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "layout": "horizontal", "padding": [0, 20, 0, 20], "mainAlign": "spaceBetween", "crossAlign": "center"}
})
b_back = cmd("frame.create", {"parent": h4["id"], "width": 220, "height": 24, "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
make_text(b_back["id"], "← Реестр", font_size=12, font_style="Bold", fill=tokens["brand/primary"])
make_text(b_back["id"], "Договор № 48/2026", font_size=12, font_style="Bold", fill=tokens["light/text-main"])
make_badge(h4["id"], "OCR 68%", "primary", size="compact")

# Processing Content Body
b4 = cmd("frame.create", {
    "parent": m4["id"], "width": 390, "height": 736,
    "props": {"fills": [], "layout": "vertical", "padding": [10, 20, 10, 20], "gap": 10, "crossAlign": "center"}
})

# Scanning Status Card
sc_card = cmd("frame.create", {
    "parent": b4["id"], "width": 350, "height": 60,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "vertical", "padding": 8, "gap": 4
    }
})
st_r = cmd("frame.create", {"parent": sc_card["id"], "width": 334, "height": 20, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(st_r["id"], "⚡ ИИ-сканирование: Страница 2 из 6", font_size=11, font_style="Bold", fill=tokens["light/text-main"])
make_text(st_r["id"], "~10 сек", font_size=10, fill=tokens["light/text-sec"])
# Progress bar
p_bar = cmd("frame.create", {"parent": sc_card["id"], "width": 334, "height": 8, "props": {"fill": tokens["light/border"], "cornerRadius": 4}})
cmd("frame.create", {"parent": p_bar["id"], "width": 227, "height": 8, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4}})
make_text(sc_card["id"], "Найдено дефектов: 3 • Формирование протокола: 85%", font_size=10, fill=tokens["light/crit-txt"])

# Segmented Switcher
seg = cmd("frame.create", {"parent": b4["id"], "width": 350, "height": 32, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": 2, "gap": 2}})
s1_btn = cmd("frame.create", {"parent": seg["id"], "width": 172, "height": 26, "props": {"fill": tokens["light/card"], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": s1_btn["id"], "text": "📄 Документ (Стр. 2)", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": tokens["brand/primary"]}})
s2_btn = cmd("frame.create", {"parent": seg["id"], "width": 172, "height": 26, "props": {"fills": [], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": s2_btn["id"], "text": "⚠️ Дефекты (3)", "props": {"fontSize": 11, "fill": tokens["light/text-sec"]}})

# Live Document Sheet Card (w=350, h=390)
doc_c = cmd("frame.create", {
    "parent": b4["id"], "width": 350, "height": 390,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": 12, "gap": 8
    }
})
doc_h = cmd("frame.create", {"parent": doc_c["id"], "width": 326, "height": 20, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(doc_h["id"], "ДОГОВОР ПОСТАВКИ № 48/2026", font_size=11, font_style="Bold", fill=tokens["light/text-main"])
make_badge(doc_h["id"], "Live лист", "blue", size="compact")

make_text(doc_c["id"], "3. ПОРЯДОК РАСЧЕТОВ И ЦЕНА", font_size=10, font_style="Bold", fill=tokens["light/text-sec"])

# Clause 3.2 (Purple collision)
c32 = cmd("frame.create", {
    "parent": doc_c["id"], "width": 326, "height": 84,
    "props": {
        "fill": tokens["light/contra-bg"], "stroke": tokens["light/contra-bdr"], "strokeWeight": 1,
        "cornerRadius": 6, "layout": "vertical", "padding": 8, "gap": 3
    }
})
c32_h = cmd("frame.create", {"parent": c32["id"], "width": 310, "height": 18, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(c32_h["id"], "П. 3.2 [КОЛЛИЗИЯ]", font_size=10, font_style="Bold", fill=tokens["light/contra-txt"])
make_badge(c32_h["id"], "Коллизия", "contradiction", size="compact")
make_text(c32["id"], "«Оплата 100% производится Покупателем в течение 5 дней с даты счета Поставщика...»", font_size=10, fill=tokens["light/text-main"], width=310)
make_text(c32["id"], "↳ Противоречит п. 6.4 (срок 30 дней после подписания Акта)", font_size=9, font_style="Bold", fill=tokens["light/contra-txt"], width=310)

make_text(doc_c["id"], "7. ОТВЕТСТВЕННОСТЬ СТОРОН", font_size=10, font_style="Bold", fill=tokens["light/text-sec"])

# Clause 7.3 (Red critical)
c73 = cmd("frame.create", {
    "parent": doc_c["id"], "width": 326, "height": 92,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1,
        "cornerRadius": 6, "layout": "vertical", "padding": 8, "gap": 3
    }
})
c73_h = cmd("frame.create", {"parent": c73["id"], "width": 310, "height": 18, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(c73_h["id"], "П. 7.3 [РИСК 333 ГК]", font_size=10, font_style="Bold", fill=tokens["light/crit-txt"])
make_badge(c73_h["id"], "ст. 333 ГК", "critical", size="compact")
make_text(c73["id"], "«Неустойка 5% от суммы Договора за каждый день просрочки без ограничения суммы...»", font_size=10, fill=tokens["light/text-main"], width=310)
make_text(c73["id"], "↳ За 20 дней неустойка превысит всю сумму (2 425 000 ₽)!", font_size=9, font_style="Bold", fill=tokens["light/crit-txt"], width=310)

# Clause 9.1 (Blue scanning)
c91 = cmd("frame.create", {
    "parent": doc_c["id"], "width": 326, "height": 48,
    "props": {
        "fill": tokens["light/blue-bg"], "stroke": tokens["light/blue-bdr"], "strokeWeight": 1,
        "cornerRadius": 6, "layout": "vertical", "padding": 6, "gap": 2
    }
})
make_text(c91["id"], "🔍 Пункт 9.1 [СКАНИРУЕТСЯ...]: Форс-мажорные основания...", font_size=10, font_style="Bold", fill=tokens["light/blue-txt"])
make_text(c91["id"], "Сверка со ст. 401 ГК РФ и регламентом ТПП РФ...", font_size=9, fill=tokens["light/text-sec"])

# Bottom Action Card
bot_act = cmd("frame.create", {
    "parent": b4["id"], "width": 350, "height": 110,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": 12, "gap": 8, "crossAlign": "center"
    }
})
make_text(bot_act["id"], "Готово к формированию протокола разногласий", font_size=11, font_style="Bold", fill=tokens["light/text-main"])
make_btn(bot_act["id"], "Перейти к протоколу разногласий →", "primary", size="md", width=326)
make_text(bot_act["id"], "🔒 100% On-Premise изоляция в контуре компании", font_size=10, fill=tokens["light/safe-txt"])


# ==============================================================================
# SCREEN 5: 05_Mobile_Contract_Inspector (390×844)
# ==============================================================================
print("\n[5/6] Сборка 05_Mobile_Contract_Inspector...")
m5 = cmd("frame.create", {
    "parent": p4_id, "name": "05_Mobile_Contract_Inspector", "x": 1720, "y": 0, "width": 390, "height": 844,
    "props": {"fill": tokens["light/bg"], "clip": True, "layout": "vertical", "gap": 0}
})
make_ios_status_bar(m5["id"])

# Header bar
h5 = cmd("frame.create", {
    "parent": m5["id"], "width": 390, "height": 44,
    "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "layout": "horizontal", "padding": [0, 20, 0, 20], "mainAlign": "spaceBetween", "crossAlign": "center"}
})
h5_l = cmd("frame.create", {"parent": h5["id"], "width": 240, "height": 24, "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
make_text(h5_l["id"], "← Реестр", font_size=12, font_style="Bold", fill=tokens["brand/primary"])
make_text(h5_l["id"], "Договор № 48", font_size=13, font_style="Bold", fill=tokens["light/text-main"])
make_badge(h5["id"], "Критический", "critical", size="compact")

# Inspector Body
b5 = cmd("frame.create", {
    "parent": m5["id"], "width": 390, "height": 736,
    "props": {"fills": [], "layout": "vertical", "padding": [10, 20, 10, 20], "gap": 10, "crossAlign": "center"}
})

# Executive Risk Banner
rb = cmd("frame.create", {
    "parent": b5["id"], "width": 350, "height": 72,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "vertical", "padding": 8, "gap": 3
    }
})
rb_t = cmd("frame.create", {"parent": rb["id"], "width": 334, "height": 18, "props": {"fills": [], "layout": "horizontal", "gap": 6, "crossAlign": "center"}})
make_badge(rb_t["id"], "НЕ ПОДПИСЫВАТЬ", "critical", size="compact")
make_text(rb_t["id"], "Риск штрафа: 2 425 000 ₽", font_size=11, font_style="Bold", fill=tokens["light/crit-txt"])
make_text(rb["id"], "Выявлена чрезмерная неустойка 5%/день (ст. 333 ГК РФ) и разрыв сроков оплаты. Рекомендован протокол разногласий.", font_size=10, fill=tokens["light/text-main"], width=334)

# Redline Diff Card (w=350, h=210)
rd = cmd("frame.create", {
    "parent": b5["id"], "width": 350, "height": 210,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": 12, "gap": 6
    }
})
rd_h = cmd("frame.create", {"parent": rd["id"], "width": 326, "height": 20, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(rd_h["id"], "Несоразмерная неустойка (п. 7.3)", font_size=12, font_style="Bold", fill=tokens["light/text-main"])
make_badge(rd_h["id"], "Риск 95/100", "critical", size="compact")

# Original text (red strikethrough)
ot = cmd("frame.create", {"parent": rd["id"], "width": 326, "height": 48, "props": {"fill": tokens["light/crit-bg"], "cornerRadius": 4, "layout": "vertical", "padding": 6}})
make_text(ot["id"], "Было: «...неустойка в размере 5% от суммы за каждый день без ограничения суммы.»", font_size=10, fill=tokens["light/crit-txt"], width=314)

# Recommended text (green)
rt = cmd("frame.create", {"parent": rd["id"], "width": 326, "height": 56, "props": {"fill": tokens["light/safe-bg"], "stroke": tokens["light/safe-bdr"], "strokeWeight": 1, "cornerRadius": 4, "layout": "vertical", "padding": 6}})
make_text(rt["id"], "Стало: «...неустойка 0.1% в день, но не более 10% от стоимости не поставленного Товара.»", font_size=10, font_style="Bold", fill=tokens["light/safe-txt"], width=314)

# Diff Actions
rd_act = cmd("frame.create", {"parent": rd["id"], "width": 326, "height": 32, "props": {"fills": [], "layout": "horizontal", "gap": 8}})
make_btn(rd_act["id"], "✓ Принять правку", "primary", size="sm", width=159)
make_btn(rd_act["id"], "Своя редакция", "secondary", size="sm", width=159)

# Voice Note Card
vn = cmd("frame.create", {
    "parent": b5["id"], "width": 350, "height": 84,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": 10, "gap": 4
    }
})
vn_h = cmd("frame.create", {"parent": vn["id"], "width": 330, "height": 18, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(vn_h["id"], "🎙 Заметка: Алексей (Юрист)", font_size=11, font_style="Bold", fill=tokens["light/text-main"])
make_text(vn_h["id"], "▶ 00:18 / 00:35", font_size=10, font_style="Bold", fill=tokens["brand/primary"])

# Waveform simulated
wv = cmd("frame.create", {"parent": vn["id"], "width": 330, "height": 8, "props": {"fill": tokens["light/border"], "cornerRadius": 4}})
cmd("frame.create", {"parent": wv["id"], "width": 160, "height": 8, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4}})
make_text(vn["id"], "«Неустойка по п. 7.3 завышена в 50 раз, суды снижают по ст. 333 ГК РФ до 0.1%. Лимит 10% согласован.»", font_size=9, fill=tokens["light/text-sec"], width=330)

# Judicial Predictor & SPARK Card
jp = cmd("frame.create", {
    "parent": b5["id"], "width": 350, "height": 68,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": 8, "gap": 3
    }
})
make_text(jp["id"], "⚖️ Судебный предиктор: 84% шанс снижения штрафа судом", font_size=10, font_style="Bold", fill=tokens["brand/primary"])
make_text(jp["id"], "🏢 Контрагент: СПАРК 74/100 • 2 иска в Арбитраже на 1.4 млн ₽", font_size=10, fill=tokens["light/text-sec"])

# Floating Export Buttons
make_btn(b5["id"], "Сформировать протокол в Диадок СЭД", "primary", size="lg", width=350)
make_btn(b5["id"], "Скачать .DOCX протокол разногласий", "secondary", size="md", width=350)


# ==============================================================================
# SCREEN 6: 06_Mobile_Risk_Analytics (390×844)
# ==============================================================================
print("\n[6/6] Сборка 06_Mobile_Risk_Analytics...")
m6 = cmd("frame.create", {
    "parent": p4_id, "name": "06_Mobile_Risk_Analytics", "x": 2150, "y": 0, "width": 390, "height": 844,
    "props": {"fill": tokens["light/bg"], "clip": True, "layout": "vertical", "gap": 0}
})
make_ios_status_bar(m6["id"])

# Header bar
h6 = cmd("frame.create", {
    "parent": m6["id"], "width": 390, "height": 44,
    "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "layout": "horizontal", "padding": [0, 20, 0, 20], "mainAlign": "spaceBetween", "crossAlign": "center"}
})
make_text(h6["id"], "Аналитика рисков", font_size=15, font_style="Bold", fill=tokens["light/text-main"])
make_badge(h6["id"], "Октябрь 2026 ▾", "primary", size="compact")

# Analytics Body (h=684)
b6 = cmd("frame.create", {
    "parent": m6["id"], "width": 390, "height": 684,
    "props": {"fills": [], "layout": "vertical", "padding": [10, 20, 10, 20], "gap": 10, "crossAlign": "center"}
})

# Top 2 Metric Cards
m_row = cmd("frame.create", {"parent": b6["id"], "width": 350, "height": 72, "props": {"fills": [], "layout": "horizontal", "gap": 10}})
m1_c = cmd("frame.create", {"parent": m_row["id"], "width": 170, "height": 72, "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 8, "layout": "vertical", "padding": 8, "mainAlign": "center", "gap": 2}})
cmd("node.create", {"type": "text", "parent": m1_c["id"], "text": "18.4 млн ₽", "props": {"fontSize": 18, "fontStyle": "Bold", "fill": tokens["light/safe-txt"]}})
make_text(m1_c["id"], "Предотвращено штрафов", font_size=10, fill=tokens["light/text-sec"])

m2_c = cmd("frame.create", {"parent": m_row["id"], "width": 170, "height": 72, "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 8, "layout": "vertical", "padding": 8, "mainAlign": "center", "gap": 2}})
cmd("node.create", {"type": "text", "parent": m2_c["id"], "text": "142 ч", "props": {"fontSize": 18, "fontStyle": "Bold", "fill": tokens["light/blue-txt"]}})
make_text(m2_c["id"], "Сэкономлено юристами", font_size=10, fill=tokens["light/text-sec"])

# Risk Categories Bars Card (w=350, h=180)
rc_c = cmd("frame.create", {
    "parent": b6["id"], "width": 350, "height": 180,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": 12, "gap": 8
    }
})
make_text(rc_c["id"], "Структура рисков компании", font_size=12, font_style="Bold", fill=tokens["light/text-main"])

risk_bars = [
    ("Несоразмерная неустойка (ст. 333)", "42%", tokens["light/crit-txt"], 140),
    ("Коллизии между разделами", "28%", tokens["light/contra-txt"], 95),
    ("Невыгодная подсудность споров", "18%", tokens["light/warn-txt"], 60),
    ("Односторонний отказ контрагента", "12%", tokens["light/blue-txt"], 40)
]
for r_name, r_pct, r_color, r_w in risk_bars:
    r_item = cmd("frame.create", {"parent": rc_c["id"], "width": 326, "height": 26, "props": {"fills": [], "layout": "vertical", "gap": 2}})
    r_top = cmd("frame.create", {"parent": r_item["id"], "width": 326, "height": 14, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween"}})
    make_text(r_top["id"], r_name, font_size=10, fill=tokens["light/text-main"])
    make_text(r_top["id"], r_pct, font_size=10, font_style="Bold", fill=r_color)
    bar_bg = cmd("frame.create", {"parent": r_item["id"], "width": 326, "height": 6, "props": {"fill": tokens["light/card-tint"], "cornerRadius": 3}})
    cmd("frame.create", {"parent": bar_bg["id"], "width": r_w, "height": 6, "props": {"fill": r_color, "cornerRadius": 3}})

# Weekly Dynamics Card
wd_c = cmd("frame.create", {
    "parent": b6["id"], "width": 350, "height": 110,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": 10, "gap": 6
    }
})
wd_h = cmd("frame.create", {"parent": wd_c["id"], "width": 330, "height": 18, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(wd_h["id"], "Динамика проверок за неделю", font_size=11, font_style="Bold", fill=tokens["light/text-main"])
make_badge(wd_h["id"], "+14% рост", "safe", size="compact")

# Day bars
day_row = cmd("frame.create", {"parent": wd_c["id"], "width": 330, "height": 52, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "max"}})
days = [("Пн", 18, 30), ("Вт", 24, 38), ("Ср", 32, 50), ("Чт", 28, 44), ("Пт", 19, 32)]
for d_name, d_cnt, d_h in days:
    d_col = cmd("frame.create", {"parent": day_row["id"], "width": 40, "height": 52, "props": {"fills": [], "layout": "vertical", "mainAlign": "max", "crossAlign": "center", "gap": 2}})
    cmd("frame.create", {"parent": d_col["id"], "width": 24, "height": d_h, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4}})
    make_text(d_col["id"], d_name, font_size=9, fill=tokens["light/text-sec"])

# Team Workload Mini Card
tw_c = cmd("frame.create", {
    "parent": b6["id"], "width": 350, "height": 92,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": 8, "gap": 4
    }
})
make_text(tw_c["id"], "Загрузка юристов в реальном времени:", font_size=11, font_style="Bold", fill=tokens["light/text-main"])
lawyers = [
    ("Алексей Смирнов", "14 дог. • 98% точн.", "safe", "В норме"),
    ("Ольга Васильева", "8 дог. • 95% точн.", "warning", "Нагрузка 85%")
]
for l_name, l_stat, l_btype, l_blbl in lawyers:
    lr = cmd("frame.create", {"parent": tw_c["id"], "width": 334, "height": 26, "props": {"fill": tokens["light/card-tint"], "cornerRadius": 4, "layout": "horizontal", "padding": [0, 8, 0, 8], "mainAlign": "spaceBetween", "crossAlign": "center"}})
    make_text(lr["id"], l_name, font_size=10, font_style="Bold", fill=tokens["light/text-main"])
    make_text(lr["id"], l_stat, font_size=9, fill=tokens["light/text-sec"])
    make_badge(lr["id"], l_blbl, l_btype, size="compact")

# Export Report Button
make_btn(b6["id"], "📤 Отправить PDF-отчет директору в Telegram", "secondary", size="md", width=350)

# Bottom Tab Bar
make_ios_tab_bar(m6["id"], active_tab="Аналитика")


# ==============================================================================
# SAVE & EXPORT MOBILE PNGs
# ==============================================================================
print("\n💾 Сохранение файла с мобильными экранами...")
save_res = cmd("file.save", {})
print(f"  Результат сохранения: {save_res}")

print("\n📸 Экспорт PNG рендеров всех 6 мобильных экранов...")
mobile_frames = [
    (m1["id"], "screen_mobile_01_welcome.png"),
    (m2["id"], "screen_mobile_02_auth.png"),
    (m3["id"], "screen_mobile_03_dashboard.png"),
    (m4["id"], "screen_mobile_04_processing.png"),
    (m5["id"], "screen_mobile_05_analysis.png"),
    (m6["id"], "screen_mobile_06_analytics.png"),
]

for fid, fname in mobile_frames:
    out_p = os.path.join(EXPORT_DIR, fname)
    res = cmd("file.export", {"ids": [fid], "format": "png", "scale": 2, "path": out_p})
    print(f"  ✓ Экспортирован: {fname}")

print("\n✨ ВСЕ 6 МОБИЛЬНЫХ ЭКРАНОВ УСПЕШНО СОЗДАНЫ И ЭКСПОРТИРОВАНЫ!")
