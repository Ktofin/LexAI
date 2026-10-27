#!/usr/bin/env python3
"""
LexAI Legal — 8-Screen Interactive Light Theme Prototype in FigCraft.
Directly implements user feedback:
1. Replaced telemetry terminal: Screen 04 now features a live document view on the left
   with highlighting clauses, and real-time discovered issues/risks on the right.
2. Cleaned onboarding & auth: Split into a dedicated Welcome / Benefits presentation screen (01)
   and a focused Auth / Login screen (02).
3. Removed all persona percentage badges (50%, 25%) before login.
4. Welcome presentation explains platform advantages in 3 clear steps.
5. Preserved full domain richness: civil code validator (ст. 333, 401, 421 ГК РФ),
   conflict detection, Redline Diff, voice notes, judicial predictor, SPARK diligence,
   Playbook IF/THEN rules, 1C/Diadoc/Telegram integrations.
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
    "brand/primary": "#D97757",       # Anthropic Terracotta
    "brand/primary-hover": "#C56546",
    "brand/primary-light": "#FAECE7", # Terracotta soft tint
    
    "light/bg": "#FAF9F5",            # Warm Linen Canvas
    "light/card": "#FFFFFF",          # Pure Card
    "light/card-tint": "#F5F3ED",     # Secondary Card Tint
    "light/card-warm": "#FBF7F0",     # Subtle warm zone
    "light/border": "#E5E3D8",        # Subtle Linen Border
    "light/border-subtle": "#EFECE6",
    "light/border-dark": "#D5D2C5",
    
    "light/text-main": "#141413",     # Obsidian / Near Black
    "light/text-sec": "#66645E",      # Muted Charcoal
    "light/text-muted": "#918E85",    # Subtle caption
    
    "light/crit-bg": "#FEF2F2",       # Critical Red Alert
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

    "light/critical-bg": "#FEF2F2",
    "light/critical-bdr": "#FECACA",
    "light/critical-txt": "#DC2626",
    
    "light/contradiction-bg": "#F5F3FF",
    "light/contradiction-bdr": "#DDD6FE",
    "light/contradiction-txt": "#7C3AED",
    
    "light/warning-bg": "#FFFBEB",
    "light/warning-bdr": "#FDE68A",
    "light/warning-txt": "#B45309",
}

# Variable lookup for dynamic binding
var_ids = {}
vlist = cmd("variable.list", {}) or []
if isinstance(vlist, list):
    for v in vlist:
        if "name" in v and "id" in v:
            var_ids[v["name"]] = v["id"]

def bind(node_id, field, var_name):
    if var_name in var_ids:
        cmd("variable.bind", {"ids": [node_id], "field": field, "variable": var_ids[var_name]})

# TEXT HELPER
def make_text(parent, text, font_size=12, font_style="Regular", fill=None, width=None, **kwargs):
    props = {
        "fontSize": font_size,
        "fontStyle": font_style
    }
    if fill: props["fill"] = fill
    if width:
        props["width"] = width
        props["textAutoResize"] = "height"
    else:
        props["textAutoResize"] = "widthAndHeight"
    for k, v in kwargs.items():
        props[k] = v
    node = cmd("node.create", {"type": "text", "parent": parent, "text": text, "props": props})
    return node["id"] if node else None

# BUTTON HELPER
def make_btn(parent, text, variant="primary", theme="light", size="md", width=None, state="default", **kwargs):
    t_pre = "light"
    cfg = {
        "lg": {"h": 46, "font": 14, "px": 20, "py": 12, "r": 8},
        "md": {"h": 38, "font": 13, "px": 16, "py": 9, "r": 6},
        "sm": {"h": 30, "font": 12, "px": 12, "py": 5, "r": 6},
        "xs": {"h": 24, "font": 11, "px": 8,  "py": 3, "r": 4}
    }.get(size, {"h": 38, "font": 13, "px": 16, "py": 9, "r": 6})

    min_required_w = int(len(text) * cfg["font"] * 0.70 + 2 * cfg["px"])
    actual_w = max(width, min_required_w) if width else min_required_w

    bg, stroke, stroke_w, txt_c, opacity = None, None, 0, tokens[f"{t_pre}/text-main"], 1.0
    if variant == "primary":
        bg, txt_c = tokens["brand/primary"], "#FFFFFF"
        if state == "hover": bg = tokens["brand/primary-hover"]
        elif state == "disabled": opacity = 0.45
    elif variant == "secondary":
        bg, stroke, stroke_w, txt_c = tokens[f"{t_pre}/card-tint"], tokens[f"{t_pre}/border"], 1, tokens[f"{t_pre}/text-main"]
        if state == "hover": bg = tokens[f"{t_pre}/border"]
        elif state == "disabled": opacity = 0.45
    elif variant == "outline":
        stroke, stroke_w, txt_c = tokens[f"{t_pre}/border"], 1, tokens[f"{t_pre}/text-main"]
    elif variant == "danger":
        bg, stroke, stroke_w, txt_c = tokens[f"{t_pre}/crit-bg"], tokens[f"{t_pre}/crit-bdr"], 1, tokens[f"{t_pre}/crit-txt"]
    elif variant == "success":
        bg, stroke, stroke_w, txt_c = tokens[f"{t_pre}/safe-bg"], tokens[f"{t_pre}/safe-bdr"], 1, tokens[f"{t_pre}/safe-txt"]
    elif variant == "ghost":
        txt_c = tokens[f"{t_pre}/text-sec"]

    props = {
        "cornerRadius": cfg["r"], "layout": "horizontal", "mainAlign": "center", "crossAlign": "center",
        "padding": [cfg["py"], cfg["px"], cfg["py"], cfg["px"]], "opacity": opacity
    }
    if bg: props["fill"] = bg
    else: props["fills"] = []
    if stroke and stroke_w > 0: props["stroke"], props["strokeWeight"] = stroke, stroke_w

    b = cmd("frame.create", {"parent": parent, "width": actual_w, "height": cfg["h"], "props": props})
    if variant == "primary" and state == "default" and "brand/primary" in var_ids:
        bind(b["id"], "fill", "brand/primary")
    cmd("node.create", {"type": "text", "parent": b["id"], "text": text, "props": {"fontSize": cfg["font"], "fontStyle": "Bold", "fill": txt_c}})
    return b["id"]

# BADGE HELPER
def make_badge(parent, text, btype="safe", theme="light", size="regular", **kwargs):
    t_pre = "light"
    cfg = {"regular": {"h": 24, "font": 11, "px": 10, "dot": 6}, "compact": {"h": 20, "font": 10, "px": 8, "dot": 5}}.get(size, {"h": 24, "font": 11, "px": 10, "dot": 6})
    mapping = {
        "critical": (tokens[f"{t_pre}/crit-bg"], tokens[f"{t_pre}/crit-bdr"], tokens[f"{t_pre}/crit-txt"]),
        "contradiction": (tokens[f"{t_pre}/contra-bg"], tokens[f"{t_pre}/contra-bdr"], tokens[f"{t_pre}/contra-txt"]),
        "warning": (tokens[f"{t_pre}/warn-bg"], tokens[f"{t_pre}/warn-bdr"], tokens[f"{t_pre}/warn-txt"]),
        "safe": (tokens[f"{t_pre}/safe-bg"], tokens[f"{t_pre}/safe-bdr"], tokens[f"{t_pre}/safe-txt"]),
        "blue": (tokens[f"{t_pre}/blue-bg"], tokens[f"{t_pre}/blue-bdr"], tokens[f"{t_pre}/blue-txt"]),
        "primary": (tokens["brand/primary-light"], tokens["brand/primary"], tokens["brand/primary"]),
    }
    bg, bdr, txt_c = mapping.get(btype, mapping["safe"])
    min_badge_w = int(len(text) * cfg["font"] * 0.70 + 2 * cfg["px"] + cfg["dot"] + 8)
    badge = cmd("frame.create", {
        "parent": parent, "width": min_badge_w, "height": cfg["h"],
        "props": {"fill": bg, "stroke": bdr, "strokeWeight": 1, "cornerRadius": 100, "layout": "horizontal", "padding": [0, cfg["px"], 0, cfg["px"]], "gap": 6, "crossAlign": "center"}
    })
    cmd("frame.create", {"parent": badge["id"], "width": cfg["dot"], "height": cfg["dot"], "props": {"fill": txt_c, "cornerRadius": cfg["dot"] // 2}})
    cmd("node.create", {"type": "text", "parent": badge["id"], "text": text, "props": {"fontSize": cfg["font"], "fontStyle": "Bold", "fill": txt_c}})
    return badge["id"]

# UNIFIED APP NAVBAR
def make_app_navbar(parent, active_tab="Договоры", user_name="Алексей Смирнов", user_role="Юрист"):
    nav = cmd("frame.create", {
        "parent": parent, "name": "AppNavbar", "x": 0, "y": 0, "width": 1440, "height": 64,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "layout": "horizontal", "padding": [0, 36, 0, 36], "mainAlign": "spaceBetween", "crossAlign": "center"
        }
    })
    # Left container: Logo + Tabs
    n_l = cmd("frame.create", {"parent": nav["id"], "width": 860, "height": 40, "props": {"fills": [], "layout": "horizontal", "gap": 24, "crossAlign": "center"}})
    
    # Brand logo box
    brand_box = cmd("frame.create", {"parent": n_l["id"], "width": 155, "height": 30, "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
    mark = cmd("frame.create", {"parent": brand_box["id"], "width": 24, "height": 24, "props": {"fill": tokens["brand/primary"], "cornerRadius": 6, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
    cmd("node.create", {"type": "text", "parent": mark["id"], "text": "§", "props": {"fontSize": 15, "fontStyle": "Bold", "fill": "#FFFFFF"}})
    make_text(brand_box["id"], "LexAI Legal", font_size=18, font_style="Bold", fill=tokens["light/text-main"], width=115)
    
    # Engine badge
    make_badge(n_l["id"], "GigaChat Enterprise", "primary", size="compact")
    
    # Navigation Tabs
    tabs_box = cmd("frame.create", {"parent": n_l["id"], "width": 510, "height": 34, "props": {"fills": [], "layout": "horizontal", "gap": 14, "crossAlign": "center"}})
    tabs = [("Договоры", 80), ("Аналитика рисков", 130), ("Корпоративный Playbook", 175), ("Команда", 80)]
    for tab_name, tw in tabs:
        is_act = (tab_name == active_tab)
        tb = cmd("frame.create", {
            "parent": tabs_box["id"], "width": tw, "height": 32,
            "props": {
                "fill": tokens["brand/primary-light"] if is_act else "#00000000",
                "cornerRadius": 6, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"
            }
        })
        make_text(tb["id"], tab_name, font_size=13, font_style="Bold" if is_act else "Regular", fill=tokens["brand/primary"] if is_act else tokens["light/text-sec"])
    
    # Right container: User Profile + Role badge
    n_r = cmd("frame.create", {"parent": nav["id"], "width": 340, "height": 40, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 12, "crossAlign": "center"}})
    make_badge(n_r["id"], f"Роль: {user_role}", "blue", size="compact")
    make_text(n_r["id"], user_name, font_size=13, font_style="Bold", fill=tokens["light/text-main"], width=130)
    
    # Avatar circle with dynamic initials
    initials = "".join([part[0] for part in user_name.split()[:2]]) if user_name else "ЮР"
    av = cmd("frame.create", {"parent": n_r["id"], "width": 34, "height": 34, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["brand/primary"], "strokeWeight": 1.5, "cornerRadius": 17, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
    cmd("node.create", {"type": "text", "parent": av["id"], "text": initials, "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens["brand/primary"]}})
    return nav["id"]

# ==============================================================================
# PREPARE PAGE 3 (☀️ Screens — Light Theme)
# ==============================================================================
print("Очистка старых экранов на Page 3 (☀️ Screens — Light Theme)...")
p3_info = cmd("node.get", {"id": 3})
if p3_info and "children" in p3_info:
    old_ids = [c["id"] for c in p3_info["children"]]
    if old_ids:
        cmd("edit.delete", {"ids": old_ids})
        print(f"  Удалено старых узлов: {len(old_ids)}")

p3_id = 3


# ==============================================================================
# SCREEN 1: 01_Welcome_Presentation_Light (x=0, y=0)
# Приветственный экран: ценностное предложение, плюсы в 3 простых шага, социальные доказательства
# ==============================================================================
print("\n[1/8] Сборка экрана 01_Welcome_Presentation_Light (Приветственный экран / Плюсы платформы)...")
f1 = cmd("frame.create", {
    "parent": p3_id, "name": "01_Welcome_Presentation_Light", "x": 0, "y": 0, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f1_id = f1["id"]

# Public Navbar (Height 64)
p_nav = cmd("frame.create", {
    "parent": f1_id, "name": "PublicNavbar", "x": 0, "y": 0, "width": 1440, "height": 64,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "layout": "horizontal", "padding": [0, 40, 0, 40], "mainAlign": "spaceBetween", "crossAlign": "center"
    }
})
pn_l = cmd("frame.create", {"parent": p_nav["id"], "width": 320, "height": 36, "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
mark1 = cmd("frame.create", {"parent": pn_l["id"], "width": 26, "height": 26, "props": {"fill": tokens["brand/primary"], "cornerRadius": 6, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": mark1["id"], "text": "§", "props": {"fontSize": 16, "fontStyle": "Bold", "fill": "#FFFFFF"}})
make_text(pn_l["id"], "LexAI Legal", font_size=19, font_style="Bold", fill=tokens["light/text-main"])
make_badge(pn_l["id"], "On-Premise 152-ФЗ", "primary", size="compact")

# Middle navigation links
pn_m = cmd("frame.create", {"parent": p_nav["id"], "width": 580, "height": 36, "props": {"fills": [], "layout": "horizontal", "gap": 22, "crossAlign": "center"}})
nav_links = ["Преимущества", "Как это работает", "Интеграции", "Безопасность", "Тарифы"]
for nl in nav_links:
    make_text(pn_m["id"], nl, font_size=13, font_style="Bold" if nl == "Преимущества" else "Regular", fill=tokens["brand/primary"] if nl == "Преимущества" else tokens["light/text-sec"])

# Right Action Buttons
pn_r = cmd("frame.create", {"parent": p_nav["id"], "width": 320, "height": 36, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 12, "crossAlign": "center"}})
make_btn(pn_r["id"], "Демо-проверка", "secondary", "light", "sm", width=125)
make_btn(pn_r["id"], "Войти в систему →", "primary", "light", "sm", width=155)

# Welcome Body Container
w_body = cmd("frame.create", {
    "parent": f1_id, "name": "WelcomeBody", "x": 40, "y": 84, "width": 1360, "height": 870,
    "props": {"fills": [], "layout": "vertical", "gap": 22}
})

# HERO SECTION (Card 1360 x 280)
hero_card = cmd("frame.create", {
    "parent": w_body["id"], "width": 1360, "height": 260,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 14, "layout": "vertical", "padding": [28, 36, 28, 36], "gap": 12
    }
})
# Hero Pill
make_badge(hero_card["id"], "✨ ИИ-аналитик договоров на базе GigaChat Enterprise и норм Гражданского кодекса РФ", "primary", size="regular")
# Hero Headline
make_text(hero_card["id"], "Интеллектуальный аудит договоров и защита от скрытых правовых рисков за 90 секунд", font_size=28, font_style="Bold", fill=tokens["light/text-main"], width=1280)
# Hero Subtitle
make_text(hero_card["id"], "Нейросетевой ассистент практикующего юриста и руководителя: автоматически сопоставляет разделы документа, мгновенно находит несоразмерную неустойку, скрытые штрафы и готовит юридически безупречный протокол разногласий.", font_size=14, fill=tokens["light/text-sec"], width=1280)

# Hero CTA row
cta_row = cmd("frame.create", {"parent": hero_card["id"], "width": 1280, "height": 46, "props": {"fills": [], "layout": "horizontal", "gap": 16, "crossAlign": "center"}})
make_btn(cta_row["id"], "Попробовать бесплатно →", "primary", "light", "lg", width=250)
make_btn(cta_row["id"], "Запросить демо для юротдела", "secondary", "light", "lg", width=280)

# Trust badges row
trust_row = cmd("frame.create", {"parent": cta_row["id"], "width": 670, "height": 30, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 18, "crossAlign": "center"}})
make_text(trust_row["id"], "✓ 100% On-Premise", font_size=12, font_style="Bold", fill=tokens["light/safe-txt"])
make_text(trust_row["id"], "✓ Судебная практика", font_size=12, font_style="Bold", fill=tokens["light/safe-txt"])
make_text(trust_row["id"], "✓ Соответствие 152-ФЗ", font_size=12, font_style="Bold", fill=tokens["light/safe-txt"])

# 3-STEP VALUE SECTION («Плюсы платформы в 3 простых шага»)
make_text(w_body["id"], "Плюсы платформы LexAI Legal в 3 простых шага:", font_size=18, font_style="Bold", fill=tokens["light/text-main"])

steps_grid = cmd("frame.create", {"parent": w_body["id"], "width": 1360, "height": 280, "props": {"fills": [], "layout": "horizontal", "gap": 20}})

steps_data = [
    ("ШАГ 01", "primary", "Мгновенная загрузка и умный OCR",
     "Поддерживает файлы .PDF и .DOCX любого объема, включая нераспознанные сканы и двуязычные договоры (RU / EN). Автоматически распознает структуру, стороны и реквизиты контрагентов.",
     [("PDF / DOCX до 50 МБ", "blue"), ("⚡ 1 400 слов/с", "safe"), ("OCR сканов", "primary")]),
    
    ("ШАГ 02", "contradiction", "Поиск скрытых рисков и коллизий",
     "Проверяет условия по статьям 333, 401, 421 ГК РФ и корпоративному Playbook. Выявляет несоразмерные штрафы и логические нестыковки между разделами (например, п. 3.2 vs п. 6.4).",
     [("ст. 333, 401 ГК РФ", "critical"), ("Детектор коллизий", "contradiction"), ("Playbook", "primary")]),
    
    ("ШАГ 03", "safe", "Готовый протокол разногласий",
     "ИИ мгновенно формулирует юридически безопасные редакции взамен опасных формулировок контрагента. Экспорт в редактируемый .DOCX и передача в СЭД Диадок или 1С в 1 клик.",
     [("DOCX / PDF", "safe"), ("Суд. предиктор: 84%", "primary"), ("1 клик в СЭД", "blue")])
]

for s_num, s_badge_t, s_title, s_desc, s_tags in steps_data:
    sc = cmd("frame.create", {
        "parent": steps_grid["id"], "width": 440, "height": 270,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "cornerRadius": 12, "layout": "vertical", "padding": [20, 22, 20, 22], "gap": 10
        }
    })
    # Step header
    sh = cmd("frame.create", {"parent": sc["id"], "width": 396, "height": 26, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
    make_badge(sh["id"], s_num, s_badge_t, size="compact")
    make_badge(sh["id"], "Автоматизировано", "blue", size="compact")
    # Title
    make_text(sc["id"], s_title, font_size=15, font_style="Bold", fill=tokens["light/text-main"], width=396)
    # Description
    make_text(sc["id"], s_desc, font_size=12, fill=tokens["light/text-sec"], width=396)
    # Tags Row
    st_row = cmd("frame.create", {"parent": sc["id"], "width": 396, "height": 30, "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
    for tag_txt, tag_type in s_tags:
        make_badge(st_row["id"], tag_txt, tag_type, size="compact")

# BOTTOM INTEGRATION & SECURITY BANNER (Card 1360 x 85)
b_card = cmd("frame.create", {
    "parent": w_body["id"], "width": 1360, "height": 80,
    "props": {
        "fill": tokens["light/card-warm"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "horizontal", "padding": [0, 28, 0, 28], "mainAlign": "spaceBetween", "crossAlign": "center"
    }
})
bc_l = cmd("frame.create", {"parent": b_card["id"], "width": 500, "height": 44, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
make_text(bc_l["id"], "Готовая интеграция с корпоративной инфраструктурой:", font_size=13, font_style="Bold", fill=tokens["light/text-main"])
make_text(bc_l["id"], "Прямой обмен договорами без ручного копирования файлов между СЭД и юристами.", font_size=11, fill=tokens["light/text-sec"])

bc_r = cmd("frame.create", {"parent": b_card["id"], "width": 780, "height": 40, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 10, "crossAlign": "center"}})
for sys_name in ["1С:Документооборот 3.0", "Диадок СЭД", "СПАРК", "Мой Арбитр", "GigaChat On-Premise"]:
    make_badge(bc_r["id"], sys_name, "primary", size="compact")


# ==============================================================================
# SCREEN 2: 02_Auth_Login_Light (x=1500, y=0)
# Сфокусированный экран авторизации: чистый вход без лишней нагрузки и без процентов!
# ==============================================================================
print("\n[2/8] Сборка экрана 02_Auth_Login_Light (Экран авторизации / Вход в систему)...")
f2 = cmd("frame.create", {
    "parent": p3_id, "name": "02_Auth_Login_Light", "x": 1500, "y": 0, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f2_id = f2["id"]

# Simple Auth Navbar
a_nav = cmd("frame.create", {
    "parent": f2_id, "name": "AuthNav", "x": 0, "y": 0, "width": 1440, "height": 64,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "layout": "horizontal", "padding": [0, 40, 0, 40], "mainAlign": "spaceBetween", "crossAlign": "center"
    }
})
an_l = cmd("frame.create", {"parent": a_nav["id"], "width": 400, "height": 36, "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
mark2 = cmd("frame.create", {"parent": an_l["id"], "width": 26, "height": 26, "props": {"fill": tokens["brand/primary"], "cornerRadius": 6, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": mark2["id"], "text": "§", "props": {"fontSize": 16, "fontStyle": "Bold", "fill": "#FFFFFF"}})
make_text(an_l["id"], "LexAI Legal", font_size=19, font_style="Bold", fill=tokens["light/text-main"])
make_badge(an_l["id"], "Защищенный шлюз авторизации", "safe", size="compact")

an_r = cmd("frame.create", {"parent": a_nav["id"], "width": 400, "height": 36, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 14, "crossAlign": "center"}})
make_text(an_r["id"], "Нужна помощь?", font_size=12, fill=tokens["light/text-muted"])
make_btn(an_r["id"], "Техподдержка 152-ФЗ", "secondary", "light", "sm", width=160)

# Center Auth Content Layout (Two balanced cards)
a_body = cmd("frame.create", {
    "parent": f2_id, "name": "AuthBody", "x": 170, "y": 140, "width": 1100, "height": 720,
    "props": {"fills": [], "layout": "horizontal", "gap": 40, "crossAlign": "center"}
})

# LEFT: Focused Login Card (Width 560, Height 640)
l_card = cmd("frame.create", {
    "parent": a_body["id"], "width": 560, "height": 620,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 16, "layout": "vertical", "padding": [36, 40, 36, 40], "gap": 14
    }
})

# Login Card Header
make_badge(l_card["id"], "Авторизация пользователя", "primary", size="compact")
make_text(l_card["id"], "Вход в рабочий кабинет", font_size=24, font_style="Bold", fill=tokens["light/text-main"], width=480)
make_text(l_card["id"], "Введите ваш корпоративный email и пароль для доступа к реестру договоров и проверкам.", font_size=13, fill=tokens["light/text-sec"], width=480)

# Input 1: Corporate Email
make_text(l_card["id"], "Корпоративный Email / Логин:", font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=480)
inp_m = cmd("frame.create", {"parent": l_card["id"], "width": 480, "height": 42, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 16, 0, 16], "crossAlign": "center"}})
make_text(inp_m["id"], "alexey.smirnov@technosnab.ru", font_size=13, fill=tokens["light/text-main"])

# Input 2: Password with forgot link
p_lbl_row = cmd("frame.create", {"parent": l_card["id"], "width": 480, "height": 20, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(p_lbl_row["id"], "Пароль учетной записи:", font_size=12, font_style="Bold", fill=tokens["light/text-main"])
make_text(p_lbl_row["id"], "Забыли пароль?", font_size=11, font_style="Bold", fill=tokens["brand/primary"])

inp_p = cmd("frame.create", {"parent": l_card["id"], "width": 480, "height": 42, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 16, 0, 16], "crossAlign": "center"}})
make_text(inp_p["id"], "••••••••••••••••••••", font_size=14, fill=tokens["light/text-muted"])

# Remember me checkbox
chk_box = cmd("frame.create", {"parent": l_card["id"], "width": 480, "height": 24, "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
make_badge(chk_box["id"], "ГОСТ 2FA", "safe", size="compact")
make_text(chk_box["id"], "Запомнить сессию на этом доверенном рабочем месте юриста", font_size=11, fill=tokens["light/text-sec"])

# Primary Login Button
make_btn(l_card["id"], "Войти в систему →", "primary", "light", "lg", width=480)

# Divider
div_row = cmd("frame.create", {"parent": l_card["id"], "width": 480, "height": 20, "props": {"fills": [], "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
make_text(div_row["id"], "— или через корпоративные системы авторизации —", font_size=11, fill=tokens["light/text-muted"])

# SSO Buttons
make_btn(l_card["id"], "Вход через Корпоративный SSO (Keycloak / AD)", "secondary", "light", "md", width=480)
make_btn(l_card["id"], "Вход через ЕСИА / Госуслуги (для юрлиц)", "secondary", "light", "md", width=480)

# RIGHT: Trust & Guest Demo Card (Width 500, Height 620)
r_card = cmd("frame.create", {
    "parent": a_body["id"], "width": 500, "height": 620,
    "props": {
        "fill": tokens["light/card-warm"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 16, "layout": "vertical", "padding": [36, 36, 36, 36], "gap": 16
    }
})

# Guest Test Box
make_badge(r_card["id"], "Экспресс-тест для руководителя", "primary", size="compact")
make_text(r_card["id"], "Хотите оценить возможности без входа?", font_size=20, font_style="Bold", fill=tokens["light/text-main"], width=428)
make_text(r_card["id"], "Проверьте первые 3 страницы любого договора прямо сейчас без регистрации: получите расчет финансовых рисков по ст. 333 ГК РФ и экспресс-вердикт для директора.", font_size=13, fill=tokens["light/text-sec"], width=428)

make_btn(r_card["id"], "Запустить экспресс-тест (3 страницы) →", "secondary", "light", "md", width=428)

# Security Bullet Points
make_text(r_card["id"], "Корпоративные гарантии безопасности:", font_size=14, font_style="Bold", fill=tokens["light/text-main"], width=428)

bullets = [
    ("🔒 Изолированный контур On-Premise", "Договоры обрабатываются в закрытом периметре и не используются для обучения моделей."),
    ("🛡️ Защита коммерческой тайны и 152-ФЗ", "Шифрование каналов связи по ГОСТ, двухфакторная аутентификация и неизменяемый журнал действий."),
    ("👥 Ролевой доступ в департаменте", "Разделение прав между практикующими юристами, руководителем отдела и дирекцией.")
]

for b_t, b_d in bullets:
    b_box = cmd("frame.create", {"parent": r_card["id"], "width": 428, "height": 55, "props": {"fills": [], "layout": "vertical", "gap": 2}})
    make_text(b_box["id"], b_t, font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=428)
    make_text(b_box["id"], b_d, font_size=11, fill=tokens["light/text-sec"], width=428)

make_text(r_card["id"], "Подключение организации: corp@lexai-legal.ru • +7 (495) 120-45-88", font_size=11, fill=tokens["light/text-muted"])


# ==============================================================================
# SCREEN 3: 03_Dashboard_Light (x=3000, y=0)
# Рабочий стол юриста: реестр договоров, СПАРК-рейтинг, фильтры, пакетная загрузка
# ==============================================================================
print("\n[3/8] Сборка экрана 03_Dashboard_Light (Главная / Реестр договоров)...")
f3 = cmd("frame.create", {
    "parent": p3_id, "name": "03_Dashboard_Light", "x": 3000, "y": 0, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f3_id = f3["id"]
make_app_navbar(f3_id, "Договоры", "Алексей Смирнов", "Юрист")

d_body = cmd("frame.create", {
    "parent": f3_id, "name": "DashboardBody", "x": 36, "y": 84, "width": 1368, "height": 870,
    "props": {"fills": [], "layout": "vertical", "gap": 16}
})

# TOP COMMAND BAR
cmd_bar = cmd("frame.create", {
    "parent": d_body["id"], "width": 1368, "height": 44,
    "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}
})
cmd_l = cmd("frame.create", {"parent": cmd_bar["id"], "width": 630, "height": 40, "props": {"fills": [], "layout": "horizontal", "gap": 16, "crossAlign": "center"}})
make_text(cmd_l["id"], "Реестр договоров и аудит", font_size=20, font_style="Bold", fill=tokens["light/text-main"], width=270)
mode_box = cmd("frame.create", {"parent": cmd_l["id"], "width": 340, "height": 34, "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [2, 2, 2, 2], "gap": 2}})
m_b1 = cmd("frame.create", {"parent": mode_box["id"], "width": 166, "height": 28, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": m_b1["id"], "text": "Вид юриста (детальный)", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": "#FFFFFF"}})
m_b2 = cmd("frame.create", {"parent": mode_box["id"], "width": 166, "height": 28, "props": {"fills": [], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": m_b2["id"], "text": "Вид директора (Executive)", "props": {"fontSize": 11, "fill": tokens["light/text-sec"]}})

cmd_r = cmd("frame.create", {"parent": cmd_bar["id"], "width": 720, "height": 40, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 12, "crossAlign": "center"}})
s_inp = cmd("frame.create", {"parent": cmd_r["id"], "width": 260, "height": 36, "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 14, 0, 14], "crossAlign": "center"}})
make_text(s_inp["id"], "🔍 Поиск контрагента, ИНН...", font_size=11, fill=tokens["light/text-muted"])
make_btn(cmd_r["id"], "+ Пакетная загрузка", "secondary", "light", "sm", width=180)
make_btn(cmd_r["id"], "Загрузить договор", "primary", "light", "sm", width=160)

# 4 KPI CARDS
kpi_row = cmd("frame.create", {"parent": d_body["id"], "width": 1368, "height": 96, "props": {"fills": [], "layout": "horizontal", "gap": 16}})
kpis = [
    ("Проверено договоров", "148 шт.", "+18 за текущую неделю", "safe", tokens["brand/primary"], "В норме"),
    ("Предотвращено штрафов", "18.4 млн ₽", "По ст. 333 ГК РФ и лимитам", "critical", tokens["light/crit-txt"], "Защита активов"),
    ("Логических коллизий", "19 коллизий", "Несовпадение сроков и оплат", "contradiction", tokens["light/contra-txt"], "Коллизии"),
    ("Точность анализа ИИ", "98.2%", "Верифицировано юристами", "safe", tokens["light/safe-txt"], "Отлично")
]
for kt, kv, ks, ktype, top_color, badge_text in kpis:
    card = cmd("frame.create", {
        "parent": kpi_row["id"], "width": 330, "height": 96,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "cornerRadius": 10, "layout": "vertical", "padding": [0, 18, 14, 18], "gap": 6
        }
    })
    cmd("frame.create", {"parent": card["id"], "width": 330, "height": 4, "props": {"fill": top_color, "cornerRadius": 2}})
    chdr = cmd("frame.create", {"parent": card["id"], "width": 294, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
    make_text(chdr["id"], kt, font_size=11, font_style="Bold", fill=tokens["light/text-sec"])
    make_badge(chdr["id"], badge_text, ktype, size="compact")
    make_text(card["id"], kv, font_size=20, font_style="Bold", fill=tokens["light/text-main"])
    make_text(card["id"], ks, font_size=11, fill=tokens["light/text-muted"])

# Filter pills row
filters_row = cmd("frame.create", {"parent": d_body["id"], "width": 1368, "height": 32, "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
make_text(filters_row["id"], "Фильтры:", font_size=12, font_style="Bold", fill=tokens["light/text-muted"], width=65)
pills = [
    ("Все договоры (148)", True, 135),
    ("Критический риск (12)", False, 145),
    ("Коллизии сроков (19)", False, 140),
    ("Требуют правок (24)", False, 140),
    ("Согласовано (98)", False, 120),
    ("Поставка (64)", False, 105),
    ("Аренда (28)", False, 90),
    ("Подряд (32)", False, 95)
]
for p_name, is_act, pw in pills:
    pb = cmd("frame.create", {
        "parent": filters_row["id"], "width": pw, "height": 28,
        "props": {
            "fill": tokens["brand/primary-light"] if is_act else tokens["light/card"],
            "stroke": tokens["brand/primary"] if is_act else tokens["light/border"],
            "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"
        }
    })
    cmd("node.create", {"type": "text", "parent": pb["id"], "text": p_name, "props": {"fontSize": 11, "fontStyle": "Bold" if is_act else "Regular", "fill": tokens["brand/primary"] if is_act else tokens["light/text-sec"]}})

# REGISTRY TABLE CONTAINER
t_card = cmd("frame.create", {
    "parent": d_body["id"], "width": 1368, "height": 640,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "clip": True
    }
})

# Table Header
t_hdr = cmd("frame.create", {
    "parent": t_card["id"], "width": 1368, "height": 42,
    "props": {
        "fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "layout": "horizontal", "padding": [0, 24, 0, 24], "crossAlign": "center"
    }
})
cols = [
    ("Документ и контрагент", 310),
    ("СПАРК / Проверка", 175),
    ("Тип и сумма", 165),
    ("Оценка риска ИИ", 165),
    ("Выявленные дефекты", 275),
    ("Статус", 120),
    ("Действия", 110)
]
for c_title, cw in cols:
    make_text(t_hdr["id"], c_title, font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=cw)

# 5 Contract Rows
contracts = [
    ("Договор_поставки_станков_№48-2026.docx", "ООО «ПромМашСервис»", "СПАРК: 89/100 (Высокий)", "safe", "Поставка • 4.85 млн ₽", "Критический (78/100)", "critical", "Штраф 5%/день + Коллизия п. 3.2 vs 6.4", "Требует правок", "critical", "Открыть", "primary"),
    ("NDA_Соглашение_о_конфиденциальности.pdf", "ООО «ТехноПарк Групп»", "СПАРК: 94/100 (Надежный)", "safe", "NDA • Без цены", "Безопасно (12/100)", "safe", "0 рисков • Полное соответствие Playbook", "Согласовано", "safe", "Резюме", "secondary"),
    ("Договор_подряда_на_монтаж_v2.docx", "АО «СтройИнжиниринг»", "СПАРК: 72/100 (Внимание)", "warning", "Подряд • 12.3 млн ₽", "Средний риск (45/100)", "warning", "1 риск: Нет предела ответственности", "На согласовании", "warning", "Открыть", "secondary"),
    ("Аренда_складского_комплекса_Север.pdf", "АО «СеверЛогистик»", "СПАРК: 65/100 (2 иска)", "critical", "Аренда • 850 тыс. ₽/мес", "Критический (65/100)", "critical", "2 риска: Скрытая индексация ставки 25%", "Отклонено ИИ", "critical", "Открыть", "danger"),
    ("Лицензионный_договор_ПО_v2.docx", "ООО «СофтЛаб Технологии»", "СПАРК: 98/100 (Идеально)", "safe", "Лицензия • 1.2 млн ₽", "Безопасно (08/100)", "safe", "0 рисков • Стандартная форма", "Готово к подписи", "safe", "Резюме", "secondary")
]

for doc_name, cp_name, spark_info, spark_type, c_type_sum, r_score, r_type, defects, st_text, st_type, btn_txt, btn_var in contracts:
    row = cmd("frame.create", {
        "parent": t_card["id"], "width": 1368, "height": 64,
        "props": {
            "fills": [], "stroke": tokens["light/border-subtle"], "strokeWeight": 1,
            "layout": "horizontal", "padding": [0, 24, 0, 24], "crossAlign": "center"
        }
    })
    c1 = cmd("frame.create", {"parent": row["id"], "width": 310, "height": 42, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
    make_text(c1["id"], doc_name, font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=300)
    make_text(c1["id"], cp_name, font_size=11, fill=tokens["light/text-sec"], width=300)
    
    c2 = cmd("frame.create", {"parent": row["id"], "width": 175, "height": 30, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_badge(c2["id"], spark_info, spark_type, size="compact")
    
    c3 = cmd("frame.create", {"parent": row["id"], "width": 165, "height": 30, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_text(c3["id"], c_type_sum, font_size=11, font_style="Bold", fill=tokens["light/text-main"], width=155)
    
    c4 = cmd("frame.create", {"parent": row["id"], "width": 165, "height": 30, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_badge(c4["id"], r_score, r_type, size="compact")
    
    c5 = cmd("frame.create", {"parent": row["id"], "width": 275, "height": 34, "props": {"fills": [], "layout": "vertical", "mainAlign": "center"}})
    make_text(c5["id"], defects, font_size=11, fill=tokens["light/text-sec"], width=265)
    
    c6 = cmd("frame.create", {"parent": row["id"], "width": 120, "height": 30, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_text(c6["id"], st_text, font_size=11, font_style="Bold", fill=tokens[f"light/{st_type}-txt"])
    
    c7 = cmd("frame.create", {"parent": row["id"], "width": 110, "height": 32, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "crossAlign": "center"}})
    make_btn(c7["id"], btn_txt, btn_var, "light", "xs", width=95)


# ==============================================================================
# SCREEN 4: 04_Processing_Light (x=4500, y=0)
# ЖИВОЙ ПРОЦЕСС АНАЛИЗА: БЕЗ телеметрии!
# СЛЕВА: Открытый лист документа с живой подсветкой пунктов при сканировании.
# СПРАВА: Список обнаруженных проблем и дефектов в реальном времени.
# ==============================================================================
print("\n[4/8] Сборка экрана 04_Processing_Light (Процесс анализа: Документ слева + Проблемы справа)...")
f4 = cmd("frame.create", {
    "parent": p3_id, "name": "04_Processing_Light", "x": 4500, "y": 0, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f4_id = f4["id"]
make_app_navbar(f4_id, "Договоры", "Алексей Смирнов", "Юрист")

p4_body = cmd("frame.create", {
    "parent": f4_id, "name": "ProcessingBody", "x": 36, "y": 80, "width": 1368, "height": 875,
    "props": {"fills": [], "layout": "vertical", "gap": 14}
})

# TOP SCANNER STATUS CARD (Width 1368, Height 68)
scan_hdr = cmd("frame.create", {
    "parent": p4_body["id"], "width": 1368, "height": 68,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [12, 24, 12, 24], "gap": 6
    }
})
sh_top = cmd("frame.create", {"parent": scan_hdr["id"], "width": 1320, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
sh_tl = cmd("frame.create", {"parent": sh_top["id"], "width": 800, "height": 22, "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
make_text(sh_tl["id"], "Анализ документа: Договор_поставки_станков_№48-2026.docx", font_size=15, font_style="Bold", fill=tokens["light/text-main"])
make_badge(sh_tl["id"], "⚡ Идет глубокое ИИ-сканирование", "primary", size="compact")
make_text(sh_top["id"], "Проверено 68% (Страница 2 из 6) • Обнаружено 3 дефекта • ~10 сек до завершения", font_size=11, fill=tokens["light/text-sec"])

# Animated progress track
sh_tr = cmd("frame.create", {"parent": scan_hdr["id"], "width": 1320, "height": 6, "props": {"fill": tokens["light/card-tint"], "cornerRadius": 3}})
cmd("frame.create", {"parent": sh_tr["id"], "width": 900, "height": 6, "props": {"fill": tokens["brand/primary"], "cornerRadius": 3}})

# TWO-COLUMN SCANNER INTERFACE (Left: Document Sheet, Right: Real-Time Issues)
scan_split = cmd("frame.create", {"parent": p4_body["id"], "width": 1368, "height": 775, "props": {"fills": [], "layout": "horizontal", "gap": 18}})

# ==============================================================================
# LEFT: Real Document Sheet with Live Highlighting Clauses (Width 700)
# ==============================================================================
doc_sheet = cmd("frame.create", {
    "parent": scan_split["id"], "width": 700, "height": 775,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [20, 24, 20, 24], "gap": 10
    }
})

# Document Paper Header
d_p_hdr = cmd("frame.create", {"parent": doc_sheet["id"], "width": 652, "height": 30, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(d_p_hdr["id"], "📄 Текст договора (Страница 2 из 6) • Интерактивный лист", font_size=13, font_style="Bold", fill=tokens["light/text-main"])
make_badge(d_p_hdr["id"], "Сканирование в реальном времени", "blue", size="compact")

# Contract title snippet
make_text(doc_sheet["id"], "ДОГОВОР ПОСТАВКИ ОБОРУДОВАНИЯ № 48/2026", font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=652)
make_text(doc_sheet["id"], "3. ПОРЯДОК РАСЧЕТОВ И ЦЕНА ОБОРУДОВАНИЯ", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=652)
make_text(doc_sheet["id"], "3.1. Общая стоимость оборудования составляет 4 850 000 (четыре миллиона восемьсот пятьдесят тысяч) рублей, в т.ч. НДС 20%.", font_size=11, fill=tokens["light/text-main"], width=652)

# LIVE HIGHLIGHT 1: Clause 3.2 (Purple contradiction)
c32_box = cmd("frame.create", {
    "parent": doc_sheet["id"], "width": 652, "height": 105,
    "props": {
        "fill": tokens["light/contra-bg"], "stroke": tokens["light/contra-bdr"], "strokeWeight": 1.5,
        "cornerRadius": 8, "layout": "vertical", "padding": [10, 14, 10, 14], "gap": 4
    }
})
c32_h = cmd("frame.create", {"parent": c32_box["id"], "width": 624, "height": 20, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(c32_h["id"], "⚠️ Пункт 3.2 [НАЙДЕНО ЛОГИЧЕСКОЕ ПРОТИВОРЕЧИЕ]:", font_size=11, font_style="Bold", fill=tokens["light/contra-txt"])
make_badge(c32_h["id"], "Коллизия разделов", "contradiction", size="compact")
make_text(c32_box["id"], "«Оплата 100% стоимости оборудования производится Покупателем в течение 5 (пяти) банковских дней с даты выставления счета Поставщиком...»", font_size=11, font_style="Bold", fill=tokens["light/text-main"], width=624)
make_text(c32_box["id"], "⟳ Сопоставлено с п. 6.4: разрыв 25 дней! Требуется полная предоплата до сдачи-приемки и подписания Акта.", font_size=10, fill=tokens["light/contra-txt"], width=624)

# Contract snippet clause 6.4
make_text(doc_sheet["id"], "6. ПОРЯДОК СДАЧИ-ПРИЕМКИ ОБОРУДОВАНИЯ", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=652)
make_text(doc_sheet["id"], "6.4. Окончательный расчет производится Покупателем в течение 30 календарных дней строго после подписания двустороннего Акта сдачи-приемки.", font_size=11, fill=tokens["light/text-main"], width=652)

# LIVE HIGHLIGHT 2: Clause 7.3 (Red critical penalty)
c73_box = cmd("frame.create", {
    "parent": doc_sheet["id"], "width": 652, "height": 115,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1.5,
        "cornerRadius": 8, "layout": "vertical", "padding": [10, 14, 10, 14], "gap": 4
    }
})
c73_h = cmd("frame.create", {"parent": c73_box["id"], "width": 624, "height": 20, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(c73_h["id"], "🚨 Пункт 7.3 [НЕСОРАЗМЕРНАЯ НЕУСТОЙКА ПО СТ. 333 ГК РФ]:", font_size=11, font_style="Bold", fill=tokens["light/crit-txt"])
make_badge(c73_h["id"], "ст. 333 ГК РФ", "critical", size="compact")
make_text(c73_box["id"], "«В случае нарушения сроков поставки Поставщик уплачивает неустойку в размере 5% от суммы Договора за каждый день просрочки без ограничения предельной суммы...»", font_size=11, font_style="Bold", fill=tokens["light/text-main"], width=624)
make_text(c73_box["id"], "⚡ Превышение среднерыночной ставки более чем в 50 раз. За 20 дней сумма штрафа превысит стоимость договора (2 425 000 ₽)!", font_size=10, fill=tokens["light/crit-txt"], width=624)

# CURRENTLY SCANNING: Clause 9.1 (Blue active scanning pulse)
c91_box = cmd("frame.create", {
    "parent": doc_sheet["id"], "width": 652, "height": 95,
    "props": {
        "fill": tokens["light/blue-bg"], "stroke": tokens["light/blue-bdr"], "strokeWeight": 1.5,
        "cornerRadius": 8, "layout": "vertical", "padding": [10, 14, 10, 14], "gap": 4
    }
})
c91_h = cmd("frame.create", {"parent": c91_box["id"], "width": 624, "height": 20, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(c91_h["id"], "🔍 Пункт 9.1 [СКАНИРУЕТСЯ В ДАННЫЙ МОМЕНТ...]:", font_size=11, font_style="Bold", fill=tokens["light/blue-txt"])
make_badge(c91_h["id"], "В процессе (OCR + NLP)", "blue", size="compact")
make_text(c91_box["id"], "«9.1. Стороны освобождаются от ответственности за частичное или полное неисполнение обязательств при наступлении обстоятельств непреодолимой силы...»", font_size=11, fill=tokens["light/text-main"], width=624)
make_text(c91_box["id"], "⟳ Идет нормативная сверка оснований форс-мажора со ст. 401 ГК РФ и регламентом ТПП РФ...", font_size=10, fill=tokens["light/blue-txt"], width=624)

# Sheet bottom indicator
make_badge(doc_sheet["id"], "🔒 100% On-Premise: обработка в закрытом контуре по 152-ФЗ", "safe", size="regular")


# ==============================================================================
# RIGHT: Discovered Issues & Defects in Real-Time (Width 650)
# ==============================================================================
issues_col = cmd("frame.create", {
    "parent": scan_split["id"], "width": 650, "height": 775,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [20, 22, 20, 22], "gap": 12
    }
})

# Issues Header
i_hdr = cmd("frame.create", {"parent": issues_col["id"], "width": 606, "height": 28, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(i_hdr["id"], "Выявленные дефекты и риски договора (3):", font_size=14, font_style="Bold", fill=tokens["light/text-main"])
make_badge(i_hdr["id"], "Обновляется в реальном времени", "primary", size="compact")

# ISSUE 1: Critical Penalty
i1_card = cmd("frame.create", {
    "parent": issues_col["id"], "width": 606, "height": 130,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "vertical", "padding": [12, 16, 12, 16], "gap": 4
    }
})
i1_h = cmd("frame.create", {"parent": i1_card["id"], "width": 574, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(i1_h["id"], "🚨 Явно несоразмерная неустойка 5% в день (ст. 333 ГК РФ)", font_size=12, font_style="Bold", fill=tokens["light/crit-txt"])
make_badge(i1_h["id"], "Критический", "critical", size="compact")
make_text(i1_card["id"], "Раздел 7 • Пункт 7.3 • Финансовая ответственность Поставщика", font_size=10, font_style="Bold", fill=tokens["light/text-sec"])
make_text(i1_card["id"], "Ставка 5%/день превышает среднерыночную в 50 раз. Риск взыскания 2 425 000 ₽ при минимальной задержке. Судебный предиктор: вероятность снижения судом 84% по ст. 333 ГК РФ.", font_size=11, fill=tokens["light/text-sec"], width=574)
make_badge(i1_card["id"], "✓ ИИ подготовил безопасную замену: ставка 0.1%/день, предел Cap 10%", "safe", size="compact")

# ISSUE 2: Section Contradiction
i2_card = cmd("frame.create", {
    "parent": issues_col["id"], "width": 606, "height": 130,
    "props": {
        "fill": tokens["light/contra-bg"], "stroke": tokens["light/contra-bdr"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "vertical", "padding": [12, 16, 12, 16], "gap": 4
    }
})
i2_h = cmd("frame.create", {"parent": i2_card["id"], "width": 574, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(i2_h["id"], "⚠️ Взаимное противоречие условий оплаты и приемки", font_size=12, font_style="Bold", fill=tokens["light/contra-txt"])
make_badge(i2_h["id"], "Коллизия", "contradiction", size="compact")
make_text(i2_card["id"], "Коллизия разделов: Пункт 3.2 vs Пункт 6.4", font_size=10, font_style="Bold", fill=tokens["light/text-sec"])
make_text(i2_card["id"], "Пункт 3.2 обязывает оплатить счет за 5 дней до отгрузки, тогда как п. 6.4 устанавливает окончательный расчет строго через 30 дней после подписания Акта приема-передачи.", font_size=11, fill=tokens["light/text-sec"], width=574)
make_badge(i2_card["id"], "✓ ИИ предложил исключить предоплату: единый срок 15 дней после Акта", "safe", size="compact")

# ISSUE 3: Jurisdiction Warning
i3_card = cmd("frame.create", {
    "parent": issues_col["id"], "width": 606, "height": 120,
    "props": {
        "fill": tokens["light/warn-bg"], "stroke": tokens["light/warn-bdr"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "vertical", "padding": [12, 16, 12, 16], "gap": 4
    }
})
i3_h = cmd("frame.create", {"parent": i3_card["id"], "width": 574, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(i3_h["id"], "⚡ Неблагоприятная территориальная подсудность споров", font_size=12, font_style="Bold", fill=tokens["light/warn-txt"])
make_badge(i3_h["id"], "Предупреждение", "warning", size="compact")
make_text(i3_card["id"], "Раздел 11 • Пункт 11.2 • Порядок разрешения споров", font_size=10, font_style="Bold", fill=tokens["light/text-sec"])
make_text(i3_card["id"], "Подсудность споров установлена в Арбитражном суде по месту нахождения Поставщика. Риск командировочных и судебных расходов для компании.", font_size=11, fill=tokens["light/text-sec"], width=574)
make_badge(i3_card["id"], "✓ Рекомендовано изменить подсудность на Арбитражный суд г. Москвы", "safe", size="compact")

# Bottom Readiness & Action Card
bot_act = cmd("frame.create", {
    "parent": issues_col["id"], "width": 606, "height": 130,
    "props": {
        "fill": tokens["light/card-warm"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "vertical", "padding": [14, 16, 14, 16], "gap": 8
    }
})
make_text(bot_act["id"], "✨ Протокол разногласий сформирован на 85%:", font_size=12, font_style="Bold", fill=tokens["light/text-main"])
make_text(bot_act["id"], "Все найденные риски автоматически снабжены безопасными юридическими редакциями по корпоративному Playbook.", font_size=11, fill=tokens["light/text-sec"], width=574)
make_btn(bot_act["id"], "Перейти к детальному инспектору и протоколу разногласий →", "primary", "light", "md", width=574)


# ==============================================================================
# SCREEN 5: 05_Contract_Analysis_Light (x=0, y=1040)
# Детальный инспектор договора, Redline Diff, голосовая заметка, судебный предиктор
# ==============================================================================
print("\n[5/8] Сборка экрана 05_Contract_Analysis_Light (Детальный инспектор договора)...")
f5 = cmd("frame.create", {
    "parent": p3_id, "name": "05_Contract_Analysis_Light", "x": 0, "y": 1040, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f5_id = f5["id"]

# Document Sub-navbar
subnav = cmd("frame.create", {
    "parent": f5_id, "name": "SubNav", "x": 0, "y": 0, "width": 1440, "height": 60,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "layout": "horizontal", "padding": [0, 36, 0, 36], "mainAlign": "spaceBetween", "crossAlign": "center"
    }
})
sn_l = cmd("frame.create", {"parent": subnav["id"], "width": 520, "height": 36, "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
make_btn(sn_l["id"], "← Реестр", "secondary", "light", "sm", width=95)
make_text(sn_l["id"], "Договор №48-2026 (Поставка)", font_size=14, font_style="Bold", fill=tokens["light/text-main"], width=235)
make_badge(sn_l["id"], "Критический (78/100)", "critical", size="compact")

# Tabs
sn_tabs = cmd("frame.create", {"parent": subnav["id"], "width": 370, "height": 34, "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
for tname, is_act, tw in [
    ("Разметка", True, 85),
    ("Redline Diff", False, 95),
    ("Сущности", False, 80),
    ("Протокол", False, 85)
]:
    tb = cmd("frame.create", {
        "parent": sn_tabs["id"], "width": tw, "height": 28,
        "props": {
            "fill": tokens["brand/primary-light"] if is_act else "#00000000",
            "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"
        }
    })
    cmd("node.create", {"type": "text", "parent": tb["id"], "text": tname, "props": {"fontSize": 11, "fontStyle": "Bold" if is_act else "Regular", "fill": tokens["brand/primary"] if is_act else tokens["light/text-sec"]}})

sn_r = cmd("frame.create", {"parent": subnav["id"], "width": 340, "height": 36, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 10, "crossAlign": "center"}})
make_btn(sn_r["id"], "Экспорт в PDF", "secondary", "light", "sm", width=120)
make_btn(sn_r["id"], "Сформировать протокол", "primary", "light", "sm", width=195)

# Main container
a_body5 = cmd("frame.create", {
    "parent": f5_id, "name": "AnalysisBody", "x": 36, "y": 74, "width": 1368, "height": 890,
    "props": {"fills": [], "layout": "vertical", "gap": 12}
})

# EXECUTIVE SUMMARY BANNER
ex_banner = cmd("frame.create", {
    "parent": a_body5["id"], "width": 1368, "height": 72,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "horizontal", "padding": [0, 20, 0, 20], "crossAlign": "center", "gap": 16
    }
})
cmd("frame.create", {"parent": ex_banner["id"], "width": 4, "height": 50, "props": {"fill": tokens["light/crit-txt"], "cornerRadius": 2}})
make_badge(ex_banner["id"], "НЕ ПОДПИСЫВАТЬ", "critical", size="regular")
eb_txt = cmd("frame.create", {"parent": ex_banner["id"], "width": 1150, "height": 46, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
make_text(eb_txt["id"], "Резюме для руководства: Выявлена явно несоразмерная неустойка 5%/день (ст. 333 ГК РФ) и коллизия сроков оплаты", font_size=13, font_style="Bold", fill=tokens["light/crit-txt"], width=1140)
make_text(eb_txt["id"], "Сумма под риском штрафов: 2 425 000 руб. (50% от контракта) • Срок п. 3.2 (5 дней от счета) не совпадает с п. 6.4 (30 дней от Акта). Рекомендация: направить протокол разногласий.", font_size=11, fill=tokens["light/text-sec"], width=1140)

# TWO-COLUMN SPLIT
split_row5 = cmd("frame.create", {"parent": a_body5["id"], "width": 1368, "height": 790, "props": {"fills": [], "layout": "horizontal", "gap": 18}})

# LEFT COLUMN: Contract text with highlighted clauses + Voice note
c_left = cmd("frame.create", {
    "parent": split_row5["id"], "width": 670, "height": 790,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [16, 20, 16, 20], "gap": 10
    }
})
cl_hdr = cmd("frame.create", {"parent": c_left["id"], "width": 630, "height": 26, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(cl_hdr["id"], "Текст договора (Страница 2 из 6) • Интерактивная разметка", font_size=13, font_style="Bold", fill=tokens["light/text-main"])
make_badge(cl_hdr["id"], "Подсветка активна", "primary", size="compact")

make_text(c_left["id"], "3. ПОРЯДОК РАСЧЕТОВ И СТОИМОСТЬ ОБОРУДОВАНИЯ", font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=630)
make_text(c_left["id"], "3.1. Общая стоимость оборудования составляет 4 850 000 руб., в т.ч. НДС 20%.", font_size=11, fill=tokens["light/text-sec"], width=630)

# Highlight clause 3.2 (Purple contradiction)
c32 = cmd("frame.create", {
    "parent": c_left["id"], "width": 630, "height": 55,
    "props": {
        "fill": tokens["light/contra-bg"], "stroke": tokens["light/contra-bdr"], "strokeWeight": 1,
        "cornerRadius": 6, "layout": "vertical", "padding": [8, 12, 8, 12], "gap": 2
    }
})
make_text(c32["id"], "п. 3.2. Оплата производится Покупателем в течение 5 (пяти) банковских дней с даты счета Поставщика.", font_size=11, font_style="Bold", fill=tokens["light/contra-txt"], width=606)
make_text(c32["id"], "⚠ Логическая коллизия со сроком окончательного расчета в п. 6.4 (разрыв 25 дней)", font_size=10, fill=tokens["light/text-sec"], width=606)

make_text(c_left["id"], "4. УСЛОВИЯ И СРОКИ ПОСТАВКИ ТОВАРА", font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=630)
make_text(c_left["id"], "4.1. Поставка осуществляется в течение 20 рабочих дней с момента выплаты аванса.", font_size=11, fill=tokens["light/text-sec"], width=630)

# Highlight clause 6.4 (Purple counterpart contradiction)
c64 = cmd("frame.create", {
    "parent": c_left["id"], "width": 630, "height": 55,
    "props": {
        "fill": tokens["light/contra-bg"], "stroke": tokens["light/contra-bdr"], "strokeWeight": 1,
        "cornerRadius": 6, "layout": "vertical", "padding": [8, 12, 8, 12], "gap": 2
    }
})
make_text(c64["id"], "п. 6.4. Окончательный расчет осуществляется в течение 30 календарных дней после подписания Акта.", font_size=11, font_style="Bold", fill=tokens["light/contra-txt"], width=606)
make_text(c64["id"], "⚠ Противоречит п. 3.2, требующему оплату до поставки оборудования по счету", font_size=10, fill=tokens["light/text-sec"], width=606)

make_text(c_left["id"], "7. ОТВЕТСТВЕННОСТЬ СТОРОН", font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=630)

# Highlight clause 7.3 (Red critical penalty + Redline Diff)
c73 = cmd("frame.create", {
    "parent": c_left["id"], "width": 630, "height": 70,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1,
        "cornerRadius": 6, "layout": "vertical", "padding": [8, 12, 8, 12], "gap": 4
    }
})
make_text(c73["id"], "п. 7.3. В случае нарушения сроков поставки Поставщик уплачивает штраф 5% от суммы Договора за каждый день просрочки без ограничения предельной суммы.", font_size=11, font_style="Bold", fill=tokens["light/crit-txt"], width=606)
make_text(c73["id"], "🔴 Redline: [Исключить 5% без лимита] → [Заменить на 0.1%/день, предел Cap не более 10% по ст. 333 ГК РФ]", font_size=10, font_style="Bold", fill=tokens["light/crit-txt"], width=606)

# VOICE NOTE WIDGET (Voice player from Lawyer Alexey)
v_box = cmd("frame.create", {
    "parent": c_left["id"], "width": 630, "height": 68,
    "props": {
        "fill": tokens["light/card-warm"], "stroke": tokens["brand/primary"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "vertical", "padding": [8, 14, 8, 14], "gap": 4
    }
})
vh = cmd("frame.create", {"parent": v_box["id"], "width": 602, "height": 20, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(vh["id"], "🎙 Голосовая заметка: Алексей Смирнов (Ведущий юрист)", font_size=11, font_style="Bold", fill=tokens["brand/primary"])
make_text(vh["id"], "▶ 0:18 / 0:35 • Распознано ИИ", font_size=10, fill=tokens["light/text-sec"])
make_text(v_box["id"], "«Обязательно согласовать лимит неустойки 10% с финдиректором и привязать оплату исключительно к Акту приёмки, исключив оплату по счёту.»", font_size=11, fill=tokens["light/text-main"], width=602)


# RIGHT COLUMN: Risk Inspector + SPARK Diligence + Judicial Risk Predictor
c_right = cmd("frame.create", {
    "parent": split_row5["id"], "width": 680, "height": 790,
    "props": {"fills": [], "layout": "vertical", "gap": 12}
})

# COUNTERPARTY CARD (SPARK + Kad.Arbitr)
cp_card = cmd("frame.create", {
    "parent": c_right["id"], "width": 680, "height": 70,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "horizontal", "padding": [0, 18, 0, 18], "mainAlign": "spaceBetween", "crossAlign": "center"
    }
})
cp_info = cmd("frame.create", {"parent": cp_card["id"], "width": 460, "height": 44, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
make_text(cp_info["id"], "Контрагент: ООО «ПромМашСервис» (ИНН 7701234567)", font_size=12, font_style="Bold", fill=tokens["light/text-main"])
make_text(cp_info["id"], "СПАРК: 89/100 • 2 открытых судебных иска в Арбитражном суде г. Москвы на 1.4 млн ₽", font_size=11, fill=tokens["light/text-sec"])
make_badge(cp_card["id"], "КАД Арбитр: 2 иска", "warning", size="compact")

# Filter chips for risks
rf_row = cmd("frame.create", {"parent": c_right["id"], "width": 680, "height": 28, "props": {"fills": [], "layout": "horizontal", "gap": 8}})
make_badge(rf_row["id"], "Все замечания (5)", "primary", size="compact")
make_badge(rf_row["id"], "Критические риски (3)", "critical", size="compact")
make_badge(rf_row["id"], "Коллизии пунктов (2)", "contradiction", size="compact")

# RISK INSPECTOR CARD 1: Clause 7.3 Penalty
r_card1 = cmd("frame.create", {
    "parent": c_right["id"], "width": 680, "height": 330,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1.5,
        "cornerRadius": 10, "layout": "vertical", "padding": [16, 20, 16, 20], "gap": 8
    }
})
rc1_h = cmd("frame.create", {"parent": r_card1["id"], "width": 640, "height": 24, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_badge(rc1_h["id"], "КРИТИЧЕСКИЙ РИСК • п. 7.3", "critical", size="compact")
make_text(rc1_h["id"], "Оценка риска: 95/100", font_size=12, font_style="Bold", fill=tokens["light/crit-txt"])

make_text(r_card1["id"], "Несоразмерная неустойка (5%/день) без ограничения ответственности", font_size=13, font_style="Bold", fill=tokens["light/text-main"], width=640)
make_text(r_card1["id"], "Комментарий ИИ: Ставка 5%/день превышает среднерыночную ставку по ст. 395 ГК РФ более чем в 50 раз (ст. 333 ГК РФ, Постановление Пленума ВС РФ № 7). При просрочке на 20 дней штраф превысит сумму всего договора.", font_size=11, fill=tokens["light/text-sec"], width=640)

# JUDICIAL RISK PREDICTOR WIDGET
pred_box = cmd("frame.create", {
    "parent": r_card1["id"], "width": 640, "height": 34,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1,
        "cornerRadius": 6, "layout": "horizontal", "padding": [0, 14, 0, 14], "crossAlign": "center", "gap": 8
    }
})
make_text(pred_box["id"], "⚖️ Судебный предиктор: Вероятность снижения неустойки судом по ст. 333 ГК РФ — 84%", font_size=11, font_style="Bold", fill=tokens["light/crit-txt"])

# AI Safe replacement formula
safe_box = cmd("frame.create", {
    "parent": r_card1["id"], "width": 640, "height": 55,
    "props": {
        "fill": tokens["light/safe-bg"], "stroke": tokens["light/safe-bdr"], "strokeWeight": 1,
        "cornerRadius": 6, "layout": "vertical", "padding": [8, 12, 8, 12], "gap": 2
    }
})
make_text(safe_box["id"], "Безопасная редакция ИИ (для протокола разногласий):", font_size=10, font_style="Bold", fill=tokens["light/safe-txt"])
make_text(safe_box["id"], "«...пени в размере 0.1% от стоимости непоставленного Товара за каждый день просрочки, но не более 10% от общей суммы Договора.»", font_size=11, fill=tokens["light/text-main"], width=616)

# Action buttons
act_r1 = cmd("frame.create", {"parent": r_card1["id"], "width": 640, "height": 34, "props": {"fills": [], "layout": "horizontal", "gap": 10}})
make_btn(act_r1["id"], "Принять правку ИИ", "primary", "light", "sm", width=170)
make_btn(act_r1["id"], "Редактировать формулировку", "secondary", "light", "sm", width=240)
make_btn(act_r1["id"], "В протокол .DOCX", "secondary", "light", "sm", width=190)

# RISK INSPECTOR CARD 2: Clause 3.2 vs 6.4 Contradiction
r_card2 = cmd("frame.create", {
    "parent": c_right["id"], "width": 680, "height": 170,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/contra-bdr"], "strokeWeight": 1.5,
        "cornerRadius": 10, "layout": "vertical", "padding": [14, 18, 14, 18], "gap": 6
    }
})
rc2_h = cmd("frame.create", {"parent": r_card2["id"], "width": 644, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_badge(rc2_h["id"], "КОЛЛИЗИЯ ПУНКТОВ • п. 3.2 vs п. 6.4", "contradiction", size="compact")
make_text(rc2_h["id"], "Сроки и порядок оплаты", font_size=11, font_style="Bold", fill=tokens["light/contra-txt"])

make_text(r_card2["id"], "Внутреннее логическое противоречие: п. 3.2 требует оплату за 5 дней до отгрузки, а п. 6.4 устанавливает окончательный расчет через 30 дней после Акта.", font_size=11, font_style="Bold", fill=tokens["light/text-main"], width=644)
make_text(r_card2["id"], "Решение ИИ: Синхронизировать единый срок окончательного расчета: 15 банковских дней с момента подписания Акта приема-передачи оборудования.", font_size=11, fill=tokens["light/text-sec"], width=644)
make_btn(r_card2["id"], "Синхронизировать сроки в тексте договора →", "secondary", "light", "sm", width=644)


# ==============================================================================
# SCREEN 6: 06_Risk_Analytics_Light (x=1500, y=1040)
# Сводная аналитика юридического департамента, предотвращенные потери, графики
# ==============================================================================
print("\n[6/8] Сборка экрана 06_Risk_Analytics_Light (Аналитика рисков компании)...")
f6 = cmd("frame.create", {
    "parent": p3_id, "name": "06_Risk_Analytics_Light", "x": 1500, "y": 1040, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f6_id = f6["id"]
make_app_navbar(f6_id, "Аналитика рисков", "Ольга Николаева", "Руководитель")

body6 = cmd("frame.create", {"parent": f6_id, "name": "AnalyticsBody", "x": 36, "y": 84, "width": 1368, "height": 870, "props": {"fills": [], "layout": "vertical", "gap": 16}})

# Filter & Report Header
f6_bar = cmd("frame.create", {"parent": body6["id"], "width": 1368, "height": 45, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(f6_bar["id"], "Сводная аналитика рисков юридического департамента", font_size=20, font_style="Bold", fill=tokens["light/text-main"], width=700)
f6_r = cmd("frame.create", {"parent": f6_bar["id"], "width": 480, "height": 40, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 12, "crossAlign": "center"}})
make_btn(f6_r["id"], "Период: Октябрь 2026", "secondary", "light", "sm", width=180)
make_btn(f6_r["id"], "Экспорт отчета Совету директоров", "primary", "light", "sm", width=250)

# 4 KPI cards
kpi_row6 = cmd("frame.create", {"parent": body6["id"], "width": 1368, "height": 96, "props": {"fills": [], "layout": "horizontal", "gap": 16}})
kpis6 = [
    ("Сэкономлено рабочих часов", "142 часа", "Равносильно 0.9 ставки юриста", "safe", tokens["brand/primary"], "Эффективность"),
    ("Предотвращено штрафов", "18.4 млн ₽", "По 14 договорам с неограниченным cap", "critical", tokens["light/crit-txt"], "Защита активов"),
    ("Устранено логических коллизий", "29 коллизий", "Исключен риск судебных споров по срокам", "contradiction", tokens["light/contra-txt"], "Коллизии"),
    ("Согласовано без правок", "34% договоров", "Типовые формы без единого риска", "safe", tokens["light/safe-txt"], "Согласовано")
]
for kt, kv, ks, ktype, top_color, badge_text in kpis6:
    card = cmd("frame.create", {
        "parent": kpi_row6["id"], "width": 330, "height": 96,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "cornerRadius": 10, "layout": "vertical", "padding": [0, 18, 14, 18], "gap": 6
        }
    })
    cmd("frame.create", {"parent": card["id"], "width": 330, "height": 4, "props": {"fill": top_color, "cornerRadius": 2}})
    chdr = cmd("frame.create", {"parent": card["id"], "width": 294, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
    make_text(chdr["id"], kt, font_size=11, font_style="Bold", fill=tokens["light/text-sec"])
    make_badge(chdr["id"], badge_text, ktype, size="compact")
    make_text(card["id"], kv, font_size=20, font_style="Bold", fill=tokens["light/text-main"])
    make_text(card["id"], ks, font_size=11, fill=tokens["light/text-muted"])

# Two Infographic Blocks (670px left distribution, 680px right matrix + weekly volume)
f6_charts = cmd("frame.create", {"parent": body6["id"], "width": 1368, "height": 410, "props": {"fills": [], "layout": "horizontal", "gap": 18}})

# Left: Risk Categories Bar Chart
c_card1 = cmd("frame.create", {
    "parent": f6_charts["id"], "width": 670, "height": 410,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [20, 24, 20, 24], "gap": 14
    }
})
make_text(c_card1["id"], "Распределение выявленных рисков по категориям:", font_size=14, font_style="Bold", fill=tokens["light/text-main"], width=620)

cat_bars = [
    ("Неустойки и ответственность (ст. 333 ГК РФ)", "42% (62 случая)", 250, tokens["light/crit-txt"]),
    ("Логические противоречия сроков и оплат", "28% (41 случай)", 168, tokens["light/contra-txt"]),
    ("Неблагоприятная территориальная подсудность", "16% (24 случая)", 96, tokens["brand/primary"]),
    ("Одностороннее изменение цен и объемов", "9% (13 случаев)", 54, tokens["light/warn-txt"]),
    ("Нарушение конфиденциальности и коммерческой тайны", "5% (8 случаев)", 30, tokens["light/safe-txt"])
]
for cat_name, cat_val, bar_w, bar_c in cat_bars:
    crow = cmd("frame.create", {"parent": c_card1["id"], "width": 622, "height": 42, "props": {"fills": [], "layout": "vertical", "gap": 4}})
    ctx = cmd("frame.create", {"parent": crow["id"], "width": 622, "height": 18, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween"}})
    make_text(ctx["id"], cat_name, font_size=11, font_style="Bold", fill=tokens["light/text-main"])
    make_text(ctx["id"], cat_val, font_size=11, fill=tokens["light/text-sec"])
    tr = cmd("frame.create", {"parent": crow["id"], "width": 622, "height": 8, "props": {"fill": tokens["light/card-tint"], "cornerRadius": 4}})
    cmd("frame.create", {"parent": tr["id"], "width": bar_w * 2, "height": 8, "props": {"fill": bar_c, "cornerRadius": 4}})

# Right: Risk Heatmap by Contract Type + Weekly Column Chart
c_card2 = cmd("frame.create", {
    "parent": f6_charts["id"], "width": 680, "height": 410,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [20, 24, 20, 24], "gap": 14
    }
})
make_text(c_card2["id"], "Матрица рисков по типам договоров и недельная динамика:", font_size=14, font_style="Bold", fill=tokens["light/text-main"], width=630)

types_grid = cmd("frame.create", {"parent": c_card2["id"], "width": 632, "height": 65, "props": {"fills": [], "layout": "horizontal", "gap": 10}})
for c_title, r_rate, r_type in [
    ("Поставка", "78% риск", "critical"),
    ("Аренда", "65% риск", "warning"),
    ("Подряд", "45% риск", "warning"),
    ("Услуги", "22% риск", "safe"),
    ("NDA", "08% риск", "safe")
]:
    t_box = cmd("frame.create", {"parent": types_grid["id"], "width": 118, "height": 60, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "vertical", "padding": [8, 8, 8, 8], "mainAlign": "center", "crossAlign": "center", "gap": 4}})
    make_text(t_box["id"], c_title, font_size=11, font_style="Bold", fill=tokens["light/text-main"])
    make_badge(t_box["id"], r_rate, r_type, size="compact")

make_text(c_card2["id"], "Динамика проверок по дням недели (пик в четверг — 40 договоров):", font_size=11, font_style="Bold", fill=tokens["light/text-sec"])

chart_box = cmd("frame.create", {"parent": c_card2["id"], "width": 632, "height": 180, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceAround", "crossAlign": "max"}})
days = [("Пн", 28, 90), ("Вт", 36, 115), ("Ср", 32, 102), ("Чт", 40, 130), ("Пт", 24, 78), ("Сб", 6, 20), ("Вс", 2, 8)]
for dname, dcnt, dheight in days:
    col_f = cmd("frame.create", {"parent": chart_box["id"], "width": 60, "height": 160, "props": {"fills": [], "layout": "vertical", "mainAlign": "max", "crossAlign": "center", "gap": 6}})
    make_text(col_f["id"], str(dcnt), font_size=11, font_style="Bold", fill=tokens["brand/primary"])
    cmd("frame.create", {"parent": col_f["id"], "width": 46, "height": dheight, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4}})
    make_text(col_f["id"], dname, font_size=11, fill=tokens["light/text-sec"])

# Team Workload & Efficiency Table
t_card6 = cmd("frame.create", {
    "parent": body6["id"], "width": 1368, "height": 220,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "clip": True
    }
})
t_hdr6 = cmd("frame.create", {"parent": t_card6["id"], "width": 1368, "height": 40, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "layout": "horizontal", "padding": [0, 24, 0, 24], "crossAlign": "center"}})
make_text(t_hdr6["id"], "Сотрудник и специализация", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=350)
make_text(t_hdr6["id"], "Проверено договоров", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=250)
make_text(t_hdr6["id"], "Принято правок ИИ", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=250)
make_text(t_hdr6["id"], "Средняя оценка риска", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=250)
make_text(t_hdr6["id"], "Статус нагрузки юриста", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=220)

team_data = [
    ("Алексей Смирнов • Ведущий юрист (Поставка)", "74 договора", "92% правок принято", "Высокий риск (64/100)", "Оптимальная (3.2 ч/день)"),
    ("Елена Васильева • Юрист (Аренда и услуги)", "48 договоров", "88% правок принято", "Средний риск (38/100)", "Оптимальная (2.1 ч/день)"),
    ("Михаил Рогов • Младший юрист (NDA и подряд)", "26 договоров", "96% правок принято", "Низкий риск (18/100)", "Доступен для новых задач")
]
for t_name, t_cnt, t_acc, t_risk, t_load in team_data:
    trow = cmd("frame.create", {"parent": t_card6["id"], "width": 1368, "height": 52, "props": {"fills": [], "stroke": tokens["light/border-subtle"], "strokeWeight": 1, "layout": "horizontal", "padding": [0, 24, 0, 24], "crossAlign": "center"}})
    make_text(trow["id"], t_name, font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=350)
    make_text(trow["id"], t_cnt, font_size=12, fill=tokens["light/text-sec"], width=250)
    make_text(trow["id"], t_acc, font_size=12, font_style="Bold", fill=tokens["light/safe-txt"], width=250)
    make_text(trow["id"], t_risk, font_size=12, fill=tokens["light/text-sec"], width=250)
    make_text(trow["id"], t_load, font_size=12, fill=tokens["light/text-sec"], width=220)


# ==============================================================================
# SCREEN 7: 07_Corporate_Playbook_Light (x=3000, y=1040)
# Конструктор правил IF/THEN, корпоративные формулировки, история версий
# ==============================================================================
print("\n[7/8] Сборка экрана 07_Corporate_Playbook_Light (Корпоративный Playbook)...")
f7 = cmd("frame.create", {
    "parent": p3_id, "name": "07_Corporate_Playbook_Light", "x": 3000, "y": 1040, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f7_id = f7["id"]
make_app_navbar(f7_id, "Корпоративный Playbook", "Ольга Николаева", "Руководитель")

body7 = cmd("frame.create", {"parent": f7_id, "name": "PlaybookBody", "x": 36, "y": 84, "width": 1368, "height": 870, "props": {"fills": [], "layout": "vertical", "gap": 14}})

# Playbook Header with Actions
p_hdr = cmd("frame.create", {"parent": body7["id"], "width": 1368, "height": 45, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(p_hdr["id"], "Корпоративный Playbook (ООО «ТехноСнаб»)", font_size=20, font_style="Bold", fill=tokens["light/text-main"], width=520)
p_hdr_r = cmd("frame.create", {"parent": p_hdr["id"], "width": 720, "height": 40, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 14, "crossAlign": "center"}})
make_badge(p_hdr_r["id"], "Редакция 3.2 (Ольга Н.)", "primary", size="regular")
make_btn(p_hdr_r["id"], "+ Создать новое правило", "primary", "light", "sm", width=200)
make_btn(p_hdr_r["id"], "Импорт из шаблона", "secondary", "light", "sm", width=170)

# Playbook Info Callout
p_callout = cmd("frame.create", {
    "parent": body7["id"], "width": 1368, "height": 55,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "horizontal", "padding": [0, 20, 0, 20], "crossAlign": "center", "gap": 12
    }
})
make_text(p_callout["id"], "📌 Как Playbook управляет анализом ИИ:", font_size=12, font_style="Bold", fill=tokens["brand/primary"], width=280)
make_text(p_callout["id"], "Любое отклонение условий входящего договора от утвержденных лимитов помечается как риск, и ИИ мгновенно предлагает корпоративную формулировку для протокола разногласий.", font_size=11, fill=tokens["light/text-sec"], width=1020)

# 5 Visual Rule Cards with IF / THEN logic
rules = [
    ("RULE-01", "Ограничение размера неустойки за просрочку поставки", "Финансовая ответственность", "Критический",
     "ЕСЛИ (IF): Ставка неустойки > 0.1%/день ИЛИ совокупный предел ответственности (Cap) отсутствует либо > 10% от суммы договора.",
     "ТОГДА (THEN): Пометить как критический риск (ст. 333 ГК РФ) и заменить на корпоративный стандарт.",
     "Безопасная формулировка ИИ: «...не более 0.1% за каждый рабочий день просрочки, но не более 10% от общей суммы договора»", True),
    
    ("RULE-02", "Синхронизация сроков оплаты и исключение внутренних коллизий", "Логические противоречия", "Коллизия",
     "ЕСЛИ (IF): Требование оплаты выставленного счета до даты подписания Акта сдачи-приемки оборудования.",
     "ТОГДА (THEN): Зафиксировать логическую коллизию между разделами и исключить предоплату без Акта.",
     "Безопасная формулировка ИИ: «...в течение 15 банковских дней с момента подписания Сторонами Акта сдачи-приемки»", True),
    
    ("RULE-03", "Территориальная подсудность судебных споров", "Судебные риски", "Критический",
     "ЕСЛИ (IF): Подсудность споров установлена по месту нахождения Поставщика (вне г. Москвы).",
     "ТОГДА (THEN): Заменить на рассмотрение споров исключительно в Арбитражном суде г. Москвы.",
     "Безопасная формулировка ИИ: «...в Арбитражном суде г. Москвы в соответствии с законодательством РФ»", True),
    
    ("RULE-04", "Обязательный досудебный претензионный порядок", "Регламент споров", "Предупреждение",
     "ЕСЛИ (IF): Срок рассмотрения претензии > 15 календарных дней либо условие вовсе не урегулировано.",
     "ТОГДА (THEN): Установить обязательный 15-дневный срок ответа на претензию до обращения в суд.",
     "Безопасная формулировка ИИ: «...претензия рассматривается Стороной в течение 15 календарных дней с момента получения»", True),
    
    ("RULE-05", "Запрет на одностороннее расторжение без компенсации убытков", "Расторжение договора", "Предупреждение",
     "ЕСЛИ (IF): Контрагент имеет право расторгнуть контракт во внесудебном порядке без возмещения расходов.",
     "ТОГДА (THEN): Запретить немотивированный односторонний отказ контрагента.",
     "Безопасная формулировка ИИ: «...расторжение допускается только по взаимному соглашению либо решению суда»", False)
]

for r_id, r_title, r_cat, r_sev, r_if, r_then, r_safe, is_on in rules:
    rc = cmd("frame.create", {
        "parent": body7["id"], "width": 1368, "height": 135,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "cornerRadius": 10, "layout": "horizontal", "padding": [12, 20, 12, 20], "crossAlign": "center", "gap": 20
        }
    })
    # Toggle switch
    tog_box = cmd("frame.create", {"parent": rc["id"], "width": 55, "height": 50, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "crossAlign": "center", "gap": 4}})
    sw = cmd("frame.create", {
        "parent": tog_box["id"], "width": 44, "height": 24,
        "props": {
            "fill": tokens["brand/primary"] if is_on else tokens["light/border"],
            "cornerRadius": 12, "layout": "horizontal", "padding": [2, 2, 2, 2], "mainAlign": "max" if is_on else "min", "crossAlign": "center"
        }
    })
    cmd("frame.create", {"parent": sw["id"], "width": 20, "height": 20, "props": {"fill": "#FFFFFF", "cornerRadius": 10}})
    make_text(tog_box["id"], "ВКЛ" if is_on else "ВЫКЛ", font_size=10, font_style="Bold", fill=tokens["brand/primary"] if is_on else tokens["light/text-muted"])
    
    # Rule Content Box
    r_mid = cmd("frame.create", {"parent": rc["id"], "width": 1120, "height": 110, "props": {"fills": [], "layout": "vertical", "gap": 4}})
    r_hdr_row = cmd("frame.create", {"parent": r_mid["id"], "width": 1120, "height": 22, "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
    make_text(r_hdr_row["id"], r_id, font_size=12, font_style="Bold", fill=tokens["light/text-muted"])
    make_text(r_hdr_row["id"], r_title, font_size=13, font_style="Bold", fill=tokens["light/text-main"])
    make_badge(r_hdr_row["id"], r_cat, "primary", size="compact")
    b_type = "critical" if r_sev == "Критический" else ("contradiction" if r_sev == "Коллизия" else "warning")
    make_badge(r_hdr_row["id"], r_sev, b_type, size="compact")
    
    make_text(r_mid["id"], r_if, font_size=11, fill=tokens["light/text-sec"], width=1120)
    make_text(r_mid["id"], r_then, font_size=11, font_style="Bold", fill=tokens["light/text-main"], width=1120)
    make_text(r_mid["id"], r_safe, font_size=11, font_style="Bold", fill=tokens["brand/primary"], width=1120)
    
    # Edit Action
    make_btn(rc["id"], "Настроить", "secondary", "light", "sm", width=115)


# ==============================================================================
# SCREEN 8: 08_Team_Settings_Light (x=4500, y=1040)
# Команда, профиль юриста, интеграции с 1С/Диадок/СПАРК и комплаенс 152-ФЗ
# ==============================================================================
print("\n[8/8] Сборка экрана 08_Team_Settings_Light (Команда, Профили и Интеграции)...")
f8 = cmd("frame.create", {
    "parent": p3_id, "name": "08_Team_Settings_Light", "x": 4500, "y": 1040, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f8_id = f8["id"]
make_app_navbar(f8_id, "Команда", "Алексей Смирнов", "Юрист")

body8 = cmd("frame.create", {"parent": f8_id, "name": "TeamBody", "x": 36, "y": 84, "width": 1368, "height": 870, "props": {"fills": [], "layout": "horizontal", "gap": 24}})

# LEFT SIDEBAR: Current User Profile & Quotas (Card 380 x 870)
sb_left = cmd("frame.create", {
    "parent": body8["id"], "width": 380, "height": 870,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 12, "layout": "vertical", "padding": [24, 24, 24, 24], "gap": 16
    }
})

# User Avatar & Info
u_box = cmd("frame.create", {"parent": sb_left["id"], "width": 332, "height": 70, "props": {"fills": [], "layout": "horizontal", "gap": 16, "crossAlign": "center"}})
u_av = cmd("frame.create", {"parent": u_box["id"], "width": 64, "height": 64, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["brand/primary"], "strokeWeight": 2, "cornerRadius": 32, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": u_av["id"], "text": "АС", "props": {"fontSize": 20, "fontStyle": "Bold", "fill": tokens["brand/primary"]}})
u_txt = cmd("frame.create", {"parent": u_box["id"], "width": 240, "height": 55, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
make_text(u_txt["id"], "Алексей Смирнов", font_size=16, font_style="Bold", fill=tokens["light/text-main"])
make_text(u_txt["id"], "Ведущий юрисконсульт • ООО «ТехноСнаб»", font_size=11, fill=tokens["light/text-sec"])
make_badge(u_txt["id"], "Editor • Проверяющий юрист", "primary", size="compact")

# Persona Switcher for Live Prototype
make_text(sb_left["id"], "Переключить активный портрет (Тест интерфейса):", font_size=11, font_style="Bold", fill=tokens["light/text-sec"])
ps_box = cmd("frame.create", {"parent": sb_left["id"], "width": 332, "height": 34, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [2, 2, 2, 2], "gap": 2}})
p1 = cmd("frame.create", {"parent": ps_box["id"], "width": 108, "height": 28, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": p1["id"], "text": "Алексей (Юрист)", "props": {"fontSize": 10, "fontStyle": "Bold", "fill": "#FFFFFF"}})
p2 = cmd("frame.create", {"parent": ps_box["id"], "width": 108, "height": 28, "props": {"fills": [], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": p2["id"], "text": "Ольга (Руков.)", "props": {"fontSize": 10, "fill": tokens["light/text-sec"]}})
p3 = cmd("frame.create", {"parent": ps_box["id"], "width": 108, "height": 28, "props": {"fills": [], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": p3["id"], "text": "Дмитрий (Дир.)", "props": {"fontSize": 10, "fill": tokens["light/text-sec"]}})

# Corporate Subscription & Quota Box
sub_box = cmd("frame.create", {
    "parent": sb_left["id"], "width": 332, "height": 130,
    "props": {
        "fill": tokens["light/card-warm"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [14, 16, 14, 16], "gap": 8
    }
})
make_text(sub_box["id"], "Тариф: Корпоративный SaaS (On-Premise)", font_size=12, font_style="Bold", fill=tokens["light/text-main"])
make_text(sub_box["id"], "Использовано проверок: 148 из 500 в этом месяце", font_size=11, fill=tokens["light/text-sec"])
q_tr = cmd("frame.create", {"parent": sub_box["id"], "width": 300, "height": 6, "props": {"fill": tokens["light/border"], "cornerRadius": 3}})
cmd("frame.create", {"parent": q_tr["id"], "width": 88, "height": 6, "props": {"fill": tokens["brand/primary"], "cornerRadius": 3}})
make_text(sub_box["id"], "Действует до 31 декабря 2026 г. • 5 юристов в штате", font_size=10, fill=tokens["light/text-muted"])
make_btn(sub_box["id"], "Управление корпоративной подпиской", "secondary", "light", "xs", width=300)

# Notification Channels & Frequency
make_text(sb_left["id"], "Настройка каналов и частоты уведомлений:", font_size=12, font_style="Bold", fill=tokens["light/text-main"])
notifs = [
    ("Email: alexey.smirnov@technosnab.ru (мгновенно)", True),
    ("Telegram-бот @LexAI_Legal_Bot (при рисках > 80)", True),
    ("SMS-уведомления при судебных коллизиях", False),
    ("Еженедельный дайджест для руководства (пн, 09:00)", True)
]
for n_name, n_on in notifs:
    nrow = cmd("frame.create", {"parent": sb_left["id"], "width": 332, "height": 28, "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
    make_badge(nrow["id"], "✓ ВКЛ" if n_on else "ВЫКЛ", "safe" if n_on else "warning", size="compact")
    make_text(nrow["id"], n_name, font_size=11, fill=tokens["light/text-main"])


# RIGHT CONTENT: 3 Cards (Team Access, Integrations Hub, 152-FZ Compliance)
sb_right = cmd("frame.create", {"parent": body8["id"], "width": 964, "height": 870, "props": {"fills": [], "layout": "vertical", "gap": 16}})

# 1. Team Members & Roles (POA personas)
team_box = cmd("frame.create", {
    "parent": sb_right["id"], "width": 964, "height": 260,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "clip": True
    }
})
tb_hdr = cmd("frame.create", {"parent": team_box["id"], "width": 964, "height": 45, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "layout": "horizontal", "padding": [0, 20, 0, 20], "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(tb_hdr["id"], "Управление доступом команды (Портреты пользователей)", font_size=13, font_style="Bold", fill=tokens["light/text-main"])
make_btn(tb_hdr["id"], "+ Пригласить юриста", "primary", "light", "xs", width=160)

members = [
    ("Алексей Смирнов", "alexey.smirnov@technosnab.ru", "Практикующий юрист", "Editor / Аналитик", "safe", "Активен сейчас"),
    ("Ольга Николаева", "olga.nikolaeva@technosnab.ru", "Руководитель юротдела", "Admin / Playbook Lead", "safe", "Активен"),
    ("Дмитрий Ковалев", "dmitry.kovalev@technosnab.ru", "Закупки / Дирекция", "Viewer / Executive", "safe", "Активен"),
    ("Елена Васильева", "elena.vasilieva@technosnab.ru", "Юрисконсульт по аренде", "Editor / Аналитик", "safe", "Активен")
]
for m_name, m_mail, m_poa, m_role, m_st_t, m_st in members:
    mrow = cmd("frame.create", {"parent": team_box["id"], "width": 964, "height": 50, "props": {"fills": [], "stroke": tokens["light/border-subtle"], "strokeWeight": 1, "layout": "horizontal", "padding": [0, 20, 0, 20], "crossAlign": "center"}})
    m_info = cmd("frame.create", {"parent": mrow["id"], "width": 230, "height": 36, "props": {"fills": [], "layout": "vertical", "mainAlign": "center"}})
    make_text(m_info["id"], m_name, font_size=11, font_style="Bold", fill=tokens["light/text-main"])
    make_text(m_info["id"], m_mail, font_size=10, fill=tokens["light/text-muted"])
    
    make_text(mrow["id"], m_poa, font_size=11, fill=tokens["light/text-sec"], width=200)
    make_text(mrow["id"], m_role, font_size=11, font_style="Bold", fill=tokens["light/text-main"], width=180)
    
    st_b = cmd("frame.create", {"parent": mrow["id"], "width": 140, "height": 30, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_badge(st_b["id"], m_st, m_st_t, size="compact")
    
    make_btn(mrow["id"], "Права доступа", "secondary", "light", "xs", width=110)

# 2. Corporate Integrations Hub
int_card = cmd("frame.create", {
    "parent": sb_right["id"], "width": 964, "height": 260,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [16, 20, 16, 20], "gap": 10
    }
})
make_text(int_card["id"], "Интеграции с корпоративными СЭД и юридическими базами:", font_size=13, font_style="Bold", fill=tokens["light/text-main"])

integrations = [
    ("1С:Документооборот 3.0", "Автоматическая выгрузка договоров на проверку прямо из карточки документа", "safe", "Подключено"),
    ("Диадок (Контур.СЭД)", "Прямой импорт входящих пакетов документов от внешних контрагентов", "safe", "Подключено"),
    ("СПАРК / Мой Арбитр", "Подгрузка индексов благонадежности, банкротства и судебных споров", "safe", "Подключено"),
    ("GigaChat Enterprise On-Premise", "Шлюз локальной нейросети, развернутый внутри закрытого контура 152-ФЗ", "primary", "Активен")
]
for iname, idesc, itype, istatus in integrations:
    irow = cmd("frame.create", {"parent": int_card["id"], "width": 924, "height": 45, "props": {"fill": tokens["light/card-tint"], "cornerRadius": 6, "layout": "horizontal", "padding": [0, 16, 0, 16], "mainAlign": "spaceBetween", "crossAlign": "center"}})
    i_left = cmd("frame.create", {"parent": irow["id"], "width": 720, "height": 36, "props": {"fills": [], "layout": "vertical", "mainAlign": "center"}})
    make_text(i_left["id"], iname, font_size=11, font_style="Bold", fill=tokens["light/text-main"])
    make_text(i_left["id"], idesc, font_size=10, fill=tokens["light/text-sec"])
    make_badge(irow["id"], istatus, itype, size="compact")

# 3. Security & 152-FZ Compliance Card
sec_card = cmd("frame.create", {
    "parent": sb_right["id"], "width": 964, "height": 260,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [16, 20, 16, 20], "gap": 8
    }
})
make_text(sec_card["id"], "Безопасность, шифрование и аудит доступа (152-ФЗ):", font_size=13, font_style="Bold", fill=tokens["light/text-main"])

sec_items = [
    ("Изолированный контур обработки (On-Premise):", "Договоры обрабатываются в изолированной среде без сохранения в публичные облака и без обучения моделей на данных контрактов.", "ВКЛЮЧЕНО"),
    ("Журнал действий пользователей (Audit Log):", "Фиксируются все загрузки, скачивания, просмотры и принятые формулировки протоколов разногласий.", "ВЕДЕТСЯ"),
    ("Двухфакторная аутентификация (2FA & ГОСТ-шифрование):", "Обязательна для всех сотрудников юридического департамента и руководства.", "АКТИВНА")
]
for stitle, sdesc, sbadge in sec_items:
    srow = cmd("frame.create", {"parent": sec_card["id"], "width": 924, "height": 55, "props": {"fill": tokens["light/safe-bg"], "stroke": tokens["light/safe-bdr"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 16, 0, 16], "mainAlign": "spaceBetween", "crossAlign": "center"}})
    s_l = cmd("frame.create", {"parent": srow["id"], "width": 780, "height": 40, "props": {"fills": [], "layout": "vertical", "mainAlign": "center"}})
    make_text(s_l["id"], stitle, font_size=11, font_style="Bold", fill=tokens["light/safe-txt"])
    make_text(s_l["id"], sdesc, font_size=10, fill=tokens["light/text-sec"])
    make_badge(srow["id"], sbadge, "safe", size="compact")


# ==============================================================================
# SAVE & EXPORT ALL 8 SCREENS
# ==============================================================================
print("\n💾 Сохранение изменений в открытом проекте...")
save_res = cmd("file.save", {})
print(f"  Результат сохранения: {save_res}")

print("\n📸 Экспорт обновленных PNG рендеров всех 8 экранов...")
screens_to_export = [
    (f1_id, "screen_01_welcome_light.png"),
    (f2_id, "screen_02_auth_light.png"),
    (f3_id, "screen_03_dashboard_light.png"),
    (f4_id, "screen_04_processing_light.png"),
    (f5_id, "screen_05_analysis_light.png"),
    (f6_id, "screen_06_analytics_light.png"),
    (f7_id, "screen_07_playbook_light.png"),
    (f8_id, "screen_08_team_light.png")
]

for fid, fname in screens_to_export:
    out_p = os.path.join(EXPORT_DIR, fname)
    res = cmd("file.export", {"ids": [fid], "format": "png", "scale": 2, "path": out_p})
    if os.path.exists(out_p):
        print(f"  ✓ Экспортирован: {fname}")
    else:
        print(f"  ⚠ Ошибка экспорта {fname}: {res}")

print("\n✨ ВСЕ 8 ЭКРАНОВ РАСШИРЕННОГО ПРОТОТИПА УСПЕШНО СОЗДАНЫ И ЭКСПОРТИРОВАНЫ!")
s.close()
