#!/usr/bin/env python3
"""
LexAI Legal — Complete Rich Interactive Light Theme Prototype in Open FigCraft.
Directly implements:
- Full Story Mapping & Mind Map from user's report (image4.jpeg / Miro)
- 3 User Personas: Alexey (50% Lawyer), Olga (25% Head of Legal), Dmitry (25% Executive / Procurement)
- Rich domain workflows:
  * Guest test mode, Document type selectors, Analysis parameter checkboxes
  * GigaChat Enterprise + Civil Code logic validator
  * Entity extraction (Amounts, Dates, Parties, Terms)
  * Redline Diff view (strike-through original vs green corporate safe replacement)
  * Judicial Risk Predictor (84% win chance by ст. 333 ГК РФ)
  * Voice Note player (Alexey's audio note to clause)
  * SPARK / Kad.Arbitr counterparty diligence card
  * Executive Summary banner for directors
  * Corporate Playbook with visual IF/THEN condition builder
  * System integrations: 1C:Документооборот, Диадок СЭД, СПАРК, Telegram bot
- Beautiful Anthropic Warm Linen (#FAF9F5, #FFFFFF, #E5E3D8, Terracotta #D97757) aesthetic.
- Zero text clipping, zero default 100x100 squishes.
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
        "lg": {"h": 46, "font": 15, "px": 22, "py": 12, "r": 8},
        "md": {"h": 38, "font": 13, "px": 16, "py": 9, "r": 6},
        "sm": {"h": 30, "font": 12, "px": 12, "py": 5, "r": 6},
        "xs": {"h": 24, "font": 11, "px": 8,  "py": 3, "r": 4}
    }.get(size, {"h": 38, "font": 13, "px": 16, "py": 9, "r": 6})

    min_required_w = int(len(text) * cfg["font"] * 0.72 + 2 * cfg["px"])
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
    min_badge_w = int(len(text) * cfg["font"] * 0.72 + 2 * cfg["px"] + cfg["dot"] + 8)
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

cmd("page.select", {"index": 2})
p3_id = 3

# ==============================================================================
# SCREEN 1: 01_Onboarding_Auth_Light (x=0, y=0)
# Полноценный LegalTech портал: выбор типа договора, параметры проверки, 3 персоны входа
# ==============================================================================
print("\n[1/7] Сборка экрана 01_Onboarding_Auth_Light (Приветствие, Конфигуратор & Вход)...")
f1 = cmd("frame.create", {
    "parent": p3_id, "name": "01_Onboarding_Auth_Light", "x": 0, "y": 0, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f1_id = f1["id"]

# Navbar 1
nav1 = cmd("frame.create", {
    "parent": f1_id, "name": "LandingNavbar", "x": 0, "y": 0, "width": 1440, "height": 64,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "layout": "horizontal", "padding": [0, 36, 0, 36], "mainAlign": "spaceBetween", "crossAlign": "center"
    }
})
nav1_l = cmd("frame.create", {"parent": nav1["id"], "width": 380, "height": 36, "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
mark1 = cmd("frame.create", {"parent": nav1_l["id"], "width": 24, "height": 24, "props": {"fill": tokens["brand/primary"], "cornerRadius": 6, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": mark1["id"], "text": "§", "props": {"fontSize": 15, "fontStyle": "Bold", "fill": "#FFFFFF"}})
make_text(nav1_l["id"], "LexAI Legal", font_size=19, font_style="Bold", fill=tokens["light/text-main"], width=130)
make_badge(nav1_l["id"], "On-Premise 152-ФЗ", "primary", size="compact")

nav1_links = cmd("frame.create", {"parent": nav1["id"], "width": 580, "height": 30, "props": {"fills": [], "layout": "horizontal", "gap": 28, "crossAlign": "center"}})
for nl, nlw in [("Возможности", 100), ("Интеграции (1С, СПАРК)", 160), ("Корпоративный Playbook", 170), ("Тарифы", 65)]:
    make_text(nav1_links["id"], nl, font_size=13, fill=tokens["light/text-sec"], width=nlw)

nav1_r = cmd("frame.create", {"parent": nav1["id"], "width": 400, "height": 40, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 12, "crossAlign": "center"}})
make_btn(nav1_r["id"], "Гостевой экспресс-тест", "secondary", "light", "sm", width=180)
make_btn(nav1_r["id"], "Войти в систему →", "primary", "light", "sm", width=165)

# Main Hero Split Layout
hero = cmd("frame.create", {
    "parent": f1_id, "name": "HeroLayout", "x": 36, "y": 88, "width": 1368, "height": 860,
    "props": {"fills": [], "layout": "horizontal", "gap": 36}
})

# LEFT COLUMN: Title, Interactive Configurator & Dropzone (Width 820px)
h_left = cmd("frame.create", {"parent": hero["id"], "width": 820, "height": 860, "props": {"fills": [], "layout": "vertical", "gap": 16}})

# Live status pill
make_badge(h_left["id"], "GigaChat Enterprise • Логический аудит коллизий по ГК РФ", "primary", size="regular")

# Main Title & Subtitle
make_text(h_left["id"], "Интеллектуальная проверка договоров на риски и коллизии за 90 секунд", font_size=28, font_style="Bold", fill=tokens["light/text-main"], width=820)
make_text(h_left["id"], "ИИ-ассистент юриста и руководителя: сопоставляет разделы документа, выявляет скрытые штрафы, несоразмерную неустойку и готовит юридически безопасный протокол разногласий.", font_size=14, fill=tokens["light/text-sec"], width=820)

# INTERACTIVE CONFIGURATOR CARD (Card 820 x 470)
cfg_card = cmd("frame.create", {
    "parent": h_left["id"], "width": 820, "height": 470,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 12, "layout": "vertical", "padding": [20, 24, 20, 24], "gap": 14
    }
})

# Section 1: Choose Contract Type
make_text(cfg_card["id"], "1. Выберите тип входящего договора:", font_size=13, font_style="Bold", fill=tokens["light/text-main"], width=770)
types_row = cmd("frame.create", {"parent": cfg_card["id"], "width": 770, "height": 34, "props": {"fills": [], "layout": "horizontal", "gap": 10}})
ctypes = [
    ("✓ Поставка оборудования", True, 175),
    ("Аренда коммерч.", False, 135),
    ("Подряд и проект.", False, 135),
    ("Оказание услуг", False, 125),
    ("NDA / Конфид.", False, 120)
]
for ct_name, is_act, cw in ctypes:
    cb = cmd("frame.create", {
        "parent": types_row["id"], "width": cw, "height": 32,
        "props": {
            "fill": tokens["brand/primary"] if is_act else tokens["light/card-tint"],
            "stroke": tokens["brand/primary"] if is_act else tokens["light/border"],
            "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"
        }
    })
    cmd("node.create", {"type": "text", "parent": cb["id"], "text": ct_name, "props": {"fontSize": 12, "fontStyle": "Bold" if is_act else "Regular", "fill": "#FFFFFF" if is_act else tokens["light/text-main"]}})

# Section 2: Analysis Parameters (Checkboxes)
make_text(cfg_card["id"], "2. Настройте параметры анализа (ИИ + Корпоративный Playbook):", font_size=13, font_style="Bold", fill=tokens["light/text-main"], width=770)
params_grid = cmd("frame.create", {"parent": cfg_card["id"], "width": 770, "height": 60, "props": {"fills": [], "layout": "horizontal", "gap": 14}})
p_col1 = cmd("frame.create", {"parent": params_grid["id"], "width": 375, "height": 60, "props": {"fills": [], "layout": "vertical", "gap": 8}})
p_col2 = cmd("frame.create", {"parent": params_grid["id"], "width": 375, "height": 60, "props": {"fills": [], "layout": "vertical", "gap": 8}})

for p_text, p_col in [
    ("☑ Проверка неустоек и штрафов (ст. 333 ГК РФ)", p_col1),
    ("☑ Сверка с корпоративным Playbook ООО «ТехноСнаб»", p_col1),
    ("☑ Поиск внутренних коллизий сроков и оплат", p_col2),
    ("☑ Извлечение сущностей (суммы, даты, реквизиты)", p_col2)
]:
    p_box = cmd("frame.create", {"parent": p_col["id"], "width": 375, "height": 26, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border-subtle"], "strokeWeight": 1, "cornerRadius": 4, "layout": "horizontal", "padding": [0, 10, 0, 10], "crossAlign": "center"}})
    make_text(p_box["id"], p_text, font_size=11, font_style="Bold", fill=tokens["light/text-main"], width=355)

# Section 3: Dropzone
make_text(cfg_card["id"], "3. Загрузите файл документа (PDF, DOCX) или пакет файлов:", font_size=13, font_style="Bold", fill=tokens["light/text-main"], width=770)
h_dz = cmd("frame.create", {
    "parent": cfg_card["id"], "width": 770, "height": 135,
    "props": {
        "fill": tokens["light/card-warm"], "stroke": tokens["brand/primary"], "strokeWeight": 1.5,
        "cornerRadius": 8, "layout": "vertical", "mainAlign": "center", "crossAlign": "center", "padding": [14, 20, 14, 20], "gap": 8
    }
})
make_text(h_dz["id"], "📁 Перетащите договор (.pdf, .docx до 50 МБ) или выберите на компьютере", font_size=14, font_style="Bold", fill=tokens["brand/primary"])
make_text(h_dz["id"], "Поддерживается пакетная загрузка до 10 договоров • Двуязычные договоры (RU / EN) • OCR сканов", font_size=11, fill=tokens["light/text-sec"])

dz_btns = cmd("frame.create", {"parent": h_dz["id"], "width": 420, "height": 34, "props": {"fills": [], "layout": "horizontal", "gap": 12, "mainAlign": "center"}})
make_btn(dz_btns["id"], "Запустить глубокий анализ", "primary", "light", "sm", width=210)
make_btn(dz_btns["id"], "Выбрать файл с диска", "secondary", "light", "sm", width=180)

# Social Proof & Integration badges
proof_box = cmd("frame.create", {"parent": h_left["id"], "width": 820, "height": 38, "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
make_text(proof_box["id"], "Интеграции:", font_size=12, font_style="Bold", fill=tokens["light/text-muted"], width=80)
for int_name in ["1С:Документооборот", "Диадок СЭД", "СПАРК / Мой Арбитр", "GigaChat API"]:
    ib = cmd("frame.create", {"parent": proof_box["id"], "width": 150, "height": 26, "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
    make_text(ib["id"], int_name, font_size=11, font_style="Bold", fill=tokens["light/text-sec"])

# RIGHT COLUMN: Multi-Persona Auth & Guest Mode Showcase (Width 510px)
h_right = cmd("frame.create", {"parent": hero["id"], "width": 510, "height": 860, "props": {"fills": [], "layout": "vertical", "gap": 18}})

# AUTH CARD WITH 3 PERSONAS
auth_card = cmd("frame.create", {
    "parent": h_right["id"], "width": 510, "height": 550,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 12, "layout": "vertical", "padding": [28, 28, 28, 28], "gap": 14
    }
})

make_text(auth_card["id"], "Вход в систему LexAI", font_size=20, font_style="Bold", fill=tokens["light/text-main"], width=450)
make_text(auth_card["id"], "Выберите портрет пользователя (из отчета POA) для тестирования:", font_size=12, fill=tokens["light/text-sec"], width=450)

# Persona Switcher (3 Tabs: Alexey 50%, Olga 25%, Dmitry 25%)
persona_box = cmd("frame.create", {
    "parent": auth_card["id"], "width": 454, "height": 44,
    "props": {"fill": tokens["light/card-tint"], "cornerRadius": 8, "layout": "horizontal", "padding": [4, 4, 4, 4], "gap": 4}
})
for p_title, p_sub, is_active, pw in [
    ("Алексей (50%)", "Юрист", True, 150),
    ("Ольга (25%)", "Руководитель", False, 146),
    ("Дмитрий (25%)", "Закупки/Директор", False, 150)
]:
    pb = cmd("frame.create", {
        "parent": persona_box["id"], "width": pw, "height": 36,
        "props": {
            "fill": tokens["light/card"] if is_active else "#00000000",
            "stroke": tokens["brand/primary"] if is_active else "#00000000",
            "strokeWeight": 1 if is_active else 0,
            "cornerRadius": 6, "layout": "vertical", "mainAlign": "center", "crossAlign": "center"
        }
    })
    cmd("node.create", {"type": "text", "parent": pb["id"], "text": p_title, "props": {"fontSize": 11, "fontStyle": "Bold", "fill": tokens["brand/primary"] if is_active else tokens["light/text-sec"]}})
    cmd("node.create", {"type": "text", "parent": pb["id"], "text": p_sub, "props": {"fontSize": 9, "fill": tokens["light/text-muted"]}})

# Input 1: Work Email
make_text(auth_card["id"], "Корпоративный Email:", font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=450)
inp1 = cmd("frame.create", {"parent": auth_card["id"], "width": 454, "height": 40, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 14, 0, 14], "crossAlign": "center"}})
make_text(inp1["id"], "alexey.smirnov@technosnab.ru", font_size=13, fill=tokens["light/text-main"])

# Input 2: Password
make_text(auth_card["id"], "Пароль учетной записи:", font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=450)
inp2 = cmd("frame.create", {"parent": auth_card["id"], "width": 454, "height": 40, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 14, 0, 14], "crossAlign": "center"}})
make_text(inp2["id"], "••••••••••••••••••••", font_size=14, fill=tokens["light/text-muted"])

# 2FA checkbox
chk_row = cmd("frame.create", {"parent": auth_card["id"], "width": 454, "height": 22, "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
make_badge(chk_row["id"], "2FA ГОСТ", "safe", size="compact")
make_text(chk_row["id"], "Безопасная сессия на доверенном рабочем месте юриста", font_size=11, fill=tokens["light/text-sec"])

# Action Buttons
make_btn(auth_card["id"], "Войти в рабочий кабинет →", "primary", "light", "md", width=454)
make_btn(auth_card["id"], "Вход через Корпоративный SSO / Госуслуги (ЕСИА)", "secondary", "light", "md", width=454)

# GUEST EXECUTIVE SUMMARY CARD (From Story Map MVP)
guest_card = cmd("frame.create", {
    "parent": h_right["id"], "width": 510, "height": 130,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [14, 18, 14, 18], "gap": 6
    }
})
make_text(guest_card["id"], "💼 Экспресс-проверка для руководителя (Дмитрия):", font_size=13, font_style="Bold", fill=tokens["light/crit-txt"], width=470)
make_text(guest_card["id"], "Проверьте договор без авторизации: получите 1-страничное Executive Summary с вердиктом (подписывать или отклонять) и расчетом финансовых рисков по ст. 333 ГК РФ.", font_size=11, fill=tokens["light/text-sec"], width=470)
make_btn(guest_card["id"], "Попробовать демо без регистрации (3 страницы) →", "danger", "light", "xs", width=470)


# ==============================================================================
# SCREEN 2: 02_Dashboard_Light (x=1500, y=0)
# Рабочий стол юриста: реестр договоров, СПАРК-рейтинг, фильтры, пакетная загрузка
# ==============================================================================
print("\n[2/7] Сборка экрана 02_Dashboard_Light (Главная / Реестр договоров)...")
f2 = cmd("frame.create", {
    "parent": p3_id, "name": "02_Dashboard_Light", "x": 1500, "y": 0, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f2_id = f2["id"]
make_app_navbar(f2_id, "Договоры", "Алексей Смирнов", "Юрист")

d_body = cmd("frame.create", {
    "parent": f2_id, "name": "DashboardBody", "x": 36, "y": 84, "width": 1368, "height": 870,
    "props": {"fills": [], "layout": "vertical", "gap": 16}
})

# TOP COMMAND BAR (Mode switcher, Search & Upload actions)
cmd_bar = cmd("frame.create", {
    "parent": d_body["id"], "width": 1368, "height": 44,
    "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}
})
# Left side of command bar: Title & Persona Mode Switcher
cmd_l = cmd("frame.create", {"parent": cmd_bar["id"], "width": 630, "height": 40, "props": {"fills": [], "layout": "horizontal", "gap": 16, "crossAlign": "center"}})
make_text(cmd_l["id"], "Реестр договоров и аудит", font_size=20, font_style="Bold", fill=tokens["light/text-main"], width=270)
# Mode Switcher
mode_box = cmd("frame.create", {"parent": cmd_l["id"], "width": 340, "height": 34, "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [2, 2, 2, 2], "gap": 2}})
m_b1 = cmd("frame.create", {"parent": mode_box["id"], "width": 166, "height": 28, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": m_b1["id"], "text": "Вид юриста (детальный)", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": "#FFFFFF"}})
m_b2 = cmd("frame.create", {"parent": mode_box["id"], "width": 166, "height": 28, "props": {"fills": [], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": m_b2["id"], "text": "Вид директора (Executive)", "props": {"fontSize": 11, "fill": tokens["light/text-sec"]}})

# Right side: Search & Batch actions
cmd_r = cmd("frame.create", {"parent": cmd_bar["id"], "width": 720, "height": 40, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 12, "crossAlign": "center"}})
s_inp = cmd("frame.create", {"parent": cmd_r["id"], "width": 260, "height": 36, "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 14, 0, 14], "crossAlign": "center"}})
make_text(s_inp["id"], "🔍 Поиск контрагента, ИНН...", font_size=11, fill=tokens["light/text-muted"])
make_btn(cmd_r["id"], "+ Пакетная загрузка", "secondary", "light", "sm", width=180)
make_btn(cmd_r["id"], "Загрузить договор", "primary", "light", "sm", width=160)

# 4 KPI CARDS (Archetype 1: Top color bars)
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
    # Top color stripe
    cmd("frame.create", {"parent": card["id"], "width": 330, "height": 4, "props": {"fill": top_color, "cornerRadius": 2}})
    # Header row
    chdr = cmd("frame.create", {"parent": card["id"], "width": 294, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
    make_text(chdr["id"], kt, font_size=11, font_style="Bold", fill=tokens["light/text-sec"])
    make_badge(chdr["id"], badge_text, ktype, size="compact")
    # Value
    make_text(card["id"], kv, font_size=20, font_style="Bold", fill=tokens["light/text-main"])
    # Subtitle
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

# REGISTRY TABLE CONTAINER (Card 1368 x 640)
t_card = cmd("frame.create", {
    "parent": d_body["id"], "width": 1368, "height": 640,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "clip": True
    }
})

# Table Header (Height 42)
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

# 5 Rich Contract Rows
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
    # Col 1: Doc & Counterparty
    c1 = cmd("frame.create", {"parent": row["id"], "width": 310, "height": 42, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
    make_text(c1["id"], doc_name, font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=300)
    make_text(c1["id"], cp_name, font_size=11, fill=tokens["light/text-sec"], width=300)
    
    # Col 2: SPARK
    c2 = cmd("frame.create", {"parent": row["id"], "width": 175, "height": 30, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_badge(c2["id"], spark_info, spark_type, size="compact")
    
    # Col 3: Type & Sum
    c3 = cmd("frame.create", {"parent": row["id"], "width": 165, "height": 30, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_text(c3["id"], c_type_sum, font_size=11, font_style="Bold", fill=tokens["light/text-main"], width=155)
    
    # Col 4: Risk score
    c4 = cmd("frame.create", {"parent": row["id"], "width": 165, "height": 30, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_badge(c4["id"], r_score, r_type, size="compact")
    
    # Col 5: Defects description
    c5 = cmd("frame.create", {"parent": row["id"], "width": 275, "height": 34, "props": {"fills": [], "layout": "vertical", "mainAlign": "center"}})
    make_text(c5["id"], defects, font_size=11, fill=tokens["light/text-sec"], width=265)
    
    # Col 6: Status
    c6 = cmd("frame.create", {"parent": row["id"], "width": 120, "height": 30, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_text(c6["id"], st_text, font_size=11, font_style="Bold", fill=tokens[f"light/{st_type}-txt"])
    
    # Col 7: Action Button
    c7 = cmd("frame.create", {"parent": row["id"], "width": 110, "height": 32, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "crossAlign": "center"}})
    make_btn(c7["id"], btn_txt, btn_var, "light", "xs", width=95)


# ==============================================================================
# SCREEN 3: 03_Processing_Light (x=3000, y=0)
# Центр глубокого анализа: степпер, лог событий ИИ, извлечение сущностей на лету
# ==============================================================================
print("\n[3/7] Сборка экрана 03_Processing_Light (Процесс анализа документа в реальном времени)...")
f3 = cmd("frame.create", {
    "parent": p3_id, "name": "03_Processing_Light", "x": 3000, "y": 0, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f3_id = f3["id"]
make_app_navbar(f3_id, "Договоры", "Алексей Смирнов", "Юрист")

p_body = cmd("frame.create", {
    "parent": f3_id, "name": "ProcessingBody", "x": 36, "y": 84, "width": 1368, "height": 870,
    "props": {"fills": [], "layout": "vertical", "gap": 16}
})

# Header info card
doc_info_card = cmd("frame.create", {
    "parent": p_body["id"], "width": 1368, "height": 72,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "horizontal", "padding": [0, 24, 0, 24], "mainAlign": "spaceBetween", "crossAlign": "center"
    }
})
di_l = cmd("frame.create", {"parent": doc_info_card["id"], "width": 800, "height": 46, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
make_text(di_l["id"], "Выполняется глубокий ИИ-анализ: Договор_поставки_станков_№48-2026.docx", font_size=16, font_style="Bold", fill=tokens["light/text-main"], width=780)
make_text(di_l["id"], "8 страниц • 1 420 слов • Контрагент: ООО «ПромМашСервис» • Сумма: 4 850 000 руб.", font_size=12, fill=tokens["light/text-sec"], width=780)

di_r = cmd("frame.create", {"parent": doc_info_card["id"], "width": 450, "height": 40, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 12, "crossAlign": "center"}})
make_badge(di_r["id"], "GigaChat Enterprise + ГК РФ", "primary", size="regular")
make_btn(di_r["id"], "Отменить проверку", "secondary", "light", "sm", width=160)

# Progress bar block
prg_card = cmd("frame.create", {
    "parent": p_body["id"], "width": 1368, "height": 60,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [12, 24, 12, 24], "gap": 8
    }
})
prg_txt_row = cmd("frame.create", {"parent": prg_card["id"], "width": 1320, "height": 18, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(prg_txt_row["id"], "Прогресс проверки: 82% • Этап 4 из 5 (Сопоставление коллизий разделов)", font_size=12, font_style="Bold", fill=tokens["brand/primary"])
make_text(prg_txt_row["id"], "Расчетное время завершения: ~12 секунд", font_size=11, fill=tokens["light/text-sec"])

# Track & Fill
prg_track = cmd("frame.create", {"parent": prg_card["id"], "width": 1320, "height": 8, "props": {"fill": tokens["light/card-tint"], "cornerRadius": 4}})
cmd("frame.create", {"parent": prg_track["id"], "width": 1082, "height": 8, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4}})

# TWO-COLUMN SCANNER INTERFACE (660px left stepper, 690px right intelligence)
scan_split = cmd("frame.create", {"parent": p_body["id"], "width": 1368, "height": 700, "props": {"fills": [], "layout": "horizontal", "gap": 18}})

# LEFT: 5 Pipeline Steps (Width 660)
scan_l = cmd("frame.create", {"parent": scan_split["id"], "width": 660, "height": 700, "props": {"fills": [], "layout": "vertical", "gap": 12}})
make_text(scan_l["id"], "Этапы пайплайна юридического анализа:", font_size=14, font_style="Bold", fill=tokens["light/text-main"], width=660)

steps = [
    ("✓ 1. Извлечение текста и OCR таблиц", "Распознано 1 420 слов, 8 разделов, реквизиты сторон, 2 подписанта", "safe", "Завершено (0.8с)"),
    ("✓ 2. Нормативный аудит по ст. 333, 401, 421 ГК РФ", "Сопоставление условий неустойки, форс-мажора и соразмерности", "safe", "Завершено (1.2с)"),
    ("✓ 3. Сверка с корпоративным Playbook ООО «ТехноСнаб»", "Выявлено 3 отклонения от утвержденных лимитов ответственности", "critical", "3 риска"),
    ("⟳ 4. Поиск логических противоречий между разделами", "Идет сопоставление: п. 3.2 (оплата 5 дней) vs п. 6.4 (поставка 30 дней)...", "contradiction", "В процессе..."),
    ("⏳ 5. Генерация протокола разногласий и альтернатив", "Формирование юридически безопасных формулировок для юриста", "warning", "В очереди")
]

for st_title, st_desc, st_type, st_badge in steps:
    st_card = cmd("frame.create", {
        "parent": scan_l["id"], "width": 660, "height": 95,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"] if st_type != "contradiction" else tokens["light/contra-bdr"],
            "strokeWeight": 1.5 if st_type == "contradiction" else 1, "cornerRadius": 8, "layout": "vertical", "padding": [12, 16, 12, 16], "gap": 4
        }
    })
    s_hdr = cmd("frame.create", {"parent": st_card["id"], "width": 628, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
    make_text(s_hdr["id"], st_title, font_size=12, font_style="Bold", fill=tokens["light/text-main"] if st_type != "contradiction" else tokens["light/contra-txt"])
    make_badge(s_hdr["id"], st_badge, st_type, size="compact")
    make_text(st_card["id"], st_desc, font_size=11, fill=tokens["light/text-sec"], width=628)

# Security pill
make_badge(scan_l["id"], "🔒 100% On-Premise изоляция: данные не покидают закрытый периметр компании", "safe", size="regular")

# RIGHT: Entity Extraction & AI Stream Terminal (Width 690)
scan_r = cmd("frame.create", {"parent": scan_split["id"], "width": 690, "height": 700, "props": {"fills": [], "layout": "vertical", "gap": 14}})

# ENTITY MAP CARD
ent_card = cmd("frame.create", {
    "parent": scan_r["id"], "width": 690, "height": 280,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [16, 18, 16, 18], "gap": 10
    }
})
eh = cmd("frame.create", {"parent": ent_card["id"], "width": 654, "height": 24, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(eh["id"], "Карта извлеченных сущностей (Entity Extraction):", font_size=13, font_style="Bold", fill=tokens["light/text-main"])
make_badge(eh["id"], "Извлечено 18 сущностей", "blue", size="compact")

entities = [
    ("Стороны договора:", "Покупатель: ООО «ТехноСнаб» | Поставщик: ООО «ПромМашСервис» (ИНН 7701234567)"),
    ("Сумма и валюта:", "4 850 000 руб., в т.ч. НДС 20% • Аванс: 30% (1 455 000 руб.)"),
    ("Срок оплаты (п. 3.2):", "5 банковских дней с даты выставления счета Поставщика (ДО приемки)"),
    ("Срок поставки (п. 6.4):", "30 календарных дней с момента аванса • Окончательный расчет после Акта"),
    ("Штрафные санкции (п. 7.3):", "Пени 5% в день без ограничения Cap (Кабальное условие по ст. 333 ГК РФ)")
]
for elab, evalue in entities:
    erow = cmd("frame.create", {"parent": ent_card["id"], "width": 654, "height": 34, "props": {"fill": tokens["light/card-tint"], "cornerRadius": 4, "layout": "horizontal", "padding": [0, 10, 0, 10], "crossAlign": "center"}})
    make_text(erow["id"], elab, font_size=11, font_style="Bold", fill=tokens["light/text-main"], width=190)
    make_text(erow["id"], evalue, font_size=11, fill=tokens["light/text-sec"], width=440)

# LIVE AI EVENT LOG CONSOLE
log_card = cmd("frame.create", {
    "parent": scan_r["id"], "width": 690, "height": 330,
    "props": {
        "fill": "#1E1E1E", "stroke": "#333333", "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [14, 16, 14, 16], "gap": 6
    }
})
lh = cmd("frame.create", {"parent": log_card["id"], "width": 658, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(lh["id"], "GigaChat AI Live Stream Engine (Телеметрия)", font_size=11, font_style="Bold", fill="#D4D4D4")
make_text(lh["id"], "● LIVE", font_size=10, font_style="Bold", fill="#4ADE80")

logs = [
    "[19:42:01.012] INFO: Загрузка файла Договор_поставки_станков_№48-2026.docx завершена.",
    "[19:42:01.840] OCR: Извлечено 1 420 токенов, структура документа верифицирована.",
    "[19:42:02.320] SPARK API: Проверка ИНН 7701234567. Индекс благонадежности: 89/100.",
    "[19:42:03.110] PLAYBOOK: Найдено 3 несоответствия регламенту ООО «ТехноСнаб».",
    "[19:42:04.450] ВНИМАНИЕ: п. 7.3 содержит неустойку 5%/день. Превышение ст. 333 ГК РФ в 50 раз!",
    "[19:42:06.120] КОЛЛИЗИЯ: Срок п. 3.2 (5 дней от счета) противоречит п. 6.4 (30 дней от Акта).",
    "[19:42:07.500] NLP: Генерация безопасной редакции п. 7.3 для протокола разногласий...",
    "[19:42:08.200] STREAM: Подготовка финального отчета и расчет вероятности снижения неустойки судом (84%)."
]
for lmsg in logs:
    col = "#4ADE80" if "INFO" in lmsg or "OCR" in lmsg else ("#F87171" if "ВНИМАНИЕ" in lmsg else ("#C084FC" if "КОЛЛИЗИЯ" in lmsg else "#D4D4D4"))
    cmd("node.create", {"type": "text", "parent": log_card["id"], "text": lmsg, "props": {"fontSize": 10, "fontFamily": "Menlo", "fill": col}})


# ==============================================================================
# SCREEN 4: 04_Contract_Analysis_Light (x=4500, y=0)
# Флагманский инспектор: Redline Diff, судебный предиктор, СПАРК, голосовая заметка
# ==============================================================================
print("\n[4/7] Сборка экрана 04_Contract_Analysis_Light (Детальный инспектор договора)...")
f4 = cmd("frame.create", {
    "parent": p3_id, "name": "04_Contract_Analysis_Light", "x": 4500, "y": 0, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f4_id = f4["id"]

# Document Sub-navbar
subnav = cmd("frame.create", {
    "parent": f4_id, "name": "SubNav", "x": 0, "y": 0, "width": 1440, "height": 60,
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
a_body = cmd("frame.create", {
    "parent": f4_id, "name": "AnalysisBody", "x": 36, "y": 74, "width": 1368, "height": 890,
    "props": {"fills": [], "layout": "vertical", "gap": 12}
})

# EXECUTIVE SUMMARY BANNER (Archetype 2)
ex_banner = cmd("frame.create", {
    "parent": a_body["id"], "width": 1368, "height": 72,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "horizontal", "padding": [0, 20, 0, 20], "crossAlign": "center", "gap": 16
    }
})
# 4px red strip
cmd("frame.create", {"parent": ex_banner["id"], "width": 4, "height": 50, "props": {"fill": tokens["light/crit-txt"], "cornerRadius": 2}})
make_badge(ex_banner["id"], "НЕ ПОДПИСЫВАТЬ", "critical", size="regular")
eb_txt = cmd("frame.create", {"parent": ex_banner["id"], "width": 1150, "height": 46, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
make_text(eb_txt["id"], "Резюме для руководства (Дмитрия / Ольги): Выявлена кабальная неустойка 5%/день и критическая коллизия сроков оплаты", font_size=13, font_style="Bold", fill=tokens["light/crit-txt"], width=1140)
make_text(eb_txt["id"], "Сумма под риском штрафов: 2 425 000 руб. (50% от контракта) • Срок п. 3.2 (5 дней от счета) не совпадает с п. 6.4 (30 дней от Акта). Рекомендация: направить протокол разногласий.", font_size=11, fill=tokens["light/text-sec"], width=1140)

# TWO-COLUMN SPLIT (670px Left Contract Text + Voice Note, 680px Right Inspector + SPARK)
split_row = cmd("frame.create", {"parent": a_body["id"], "width": 1368, "height": 790, "props": {"fills": [], "layout": "horizontal", "gap": 18}})

# LEFT COLUMN: Contract text with highlighted clauses + Voice note
c_left = cmd("frame.create", {
    "parent": split_row["id"], "width": 670, "height": 790,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [16, 20, 16, 20], "gap": 10
    }
})
cl_hdr = cmd("frame.create", {"parent": c_left["id"], "width": 630, "height": 26, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(cl_hdr["id"], "Текст договора (Страница 2 из 6) • Интерактивная разметка", font_size=13, font_style="Bold", fill=tokens["light/text-main"])
make_badge(cl_hdr["id"], "Подсветка активна", "primary", size="compact")

# Contract body clauses
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
make_text(c32["id"], "⚠️ Логическая коллизия со сроком окончательного расчета в п. 6.4 (разрыв 25 дней)", font_size=10, fill=tokens["light/text-sec"], width=606)

make_text(c_left["id"], "4. УСЛОВИЯ И СРОКИ ПОСТАВКИ ТОВАРА", font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=630)
make_text(c_left["id"], "4.1. Поставка осуществляется в течение 20 рабочих дней с момента выплаты аванса.", font_size=11, fill=tokens["light/text-sec"], width=630)

# Highlight clause 6.4 (Purple contradiction)
c64 = cmd("frame.create", {
    "parent": c_left["id"], "width": 630, "height": 55,
    "props": {
        "fill": tokens["light/contra-bg"], "stroke": tokens["light/contra-bdr"], "strokeWeight": 1,
        "cornerRadius": 6, "layout": "vertical", "padding": [8, 12, 8, 12], "gap": 2
    }
})
make_text(c64["id"], "п. 6.4. Окончательный расчет осуществляется в течение 30 календарных дней после подписания Акта.", font_size=11, font_style="Bold", fill=tokens["light/contra-txt"], width=606)
make_text(c64["id"], "⚠️ Противоречит п. 3.2, требующему оплату до поставки оборудования по счету", font_size=10, fill=tokens["light/text-sec"], width=606)

make_text(c_left["id"], "7. ОТВЕТСТВЕННОСТЬ СТОРОН", font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=630)

# Highlight clause 7.3 (Red critical with Redline diff strike)
c73 = cmd("frame.create", {
    "parent": c_left["id"], "width": 630, "height": 72,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1,
        "cornerRadius": 6, "layout": "vertical", "padding": [8, 12, 8, 12], "gap": 3
    }
})
make_text(c73["id"], "п. 7.3. В случае нарушения сроков поставки Поставщик уплачивает штраф 5% от суммы Договора за каждый день просрочки без ограничения предельной суммы.", font_size=11, font_style="Bold", fill=tokens["light/crit-txt"], width=606)
make_text(c73["id"], "🛑 Redline: [Исключить 5% без лимита] → [Заменить на 0.1%/день, предел Cap не более 10% по ст. 333 ГК РФ]", font_size=10, font_style="Bold", fill=tokens["brand/primary"], width=606)

# VOICE NOTE WIDGET (From Story Map backlog: Голосовой ввод заметок)
vn_card = cmd("frame.create", {
    "parent": c_left["id"], "width": 630, "height": 74,
    "props": {
        "fill": tokens["light/card-warm"], "stroke": tokens["brand/primary"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "vertical", "padding": [8, 12, 8, 12], "gap": 4
    }
})
vnh = cmd("frame.create", {"parent": vn_card["id"], "width": 606, "height": 20, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(vnh["id"], "🎙 Голосовая заметка: Алексей Смирнов (Ведущий юрист)", font_size=11, font_style="Bold", fill=tokens["brand/primary"])
make_text(vnh["id"], "▶ 0:18 / 0:35 • Распознано ИИ", font_size=10, fill=tokens["light/text-sec"])
make_text(vn_card["id"], "«Обязательно согласовать лимит неустойки 10% с финдиректором и привязать оплату исключительно к Акту приемки, исключив оплату по счету.»", font_size=10, fill=tokens["light/text-main"], width=606)


# RIGHT COLUMN: AI Risk Inspector, SPARK counterparty, Judicial Predictor
c_right = cmd("frame.create", {
    "parent": split_row["id"], "width": 680, "height": 790,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [16, 20, 16, 20], "gap": 10
    }
})

# Counterparty Intelligence widget (СПАРК / Мой Арбитр)
spark_card = cmd("frame.create", {
    "parent": c_right["id"], "width": 640, "height": 48,
    "props": {
        "fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 6, "layout": "horizontal", "padding": [0, 14, 0, 14], "mainAlign": "spaceBetween", "crossAlign": "center"
    }
})
sp_l = cmd("frame.create", {"parent": spark_card["id"], "width": 460, "height": 36, "props": {"fills": [], "layout": "vertical", "mainAlign": "center"}})
make_text(sp_l["id"], "Контрагент: ООО «ПромМашСервис» (ИНН 7701234567)", font_size=11, font_style="Bold", fill=tokens["light/text-main"])
make_text(sp_l["id"], "СПАРК: 89/100 • 2 открытых судебных иска в Арбитражном суде г. Москвы на 1.4 млн ₽", font_size=10, fill=tokens["light/text-sec"])
make_badge(spark_card["id"], "Кадастр: 2 иска", "warning", size="compact")

# Filter chips in Inspector
cr_hdr = cmd("frame.create", {"parent": c_right["id"], "width": 640, "height": 30, "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
make_badge(cr_hdr["id"], "Все замечания (5)", "primary", size="compact")
make_badge(cr_hdr["id"], "Критические риски (3)", "critical", size="compact")
make_badge(cr_hdr["id"], "Коллизии пунктов (2)", "contradiction", size="compact")

# DETAILED RISK CARD: Clause 7.3 (ст. 333 ГК РФ)
rcard1 = cmd("frame.create", {
    "parent": c_right["id"], "width": 640, "height": 260,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1.5,
        "cornerRadius": 8, "layout": "vertical", "padding": [12, 14, 12, 14], "gap": 8
    }
})
r1_hdr = cmd("frame.create", {"parent": rcard1["id"], "width": 612, "height": 24, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_badge(r1_hdr["id"], "КРИТИЧЕСКИЙ РИСК • п. 7.3", "critical", size="compact")
make_text(r1_hdr["id"], "Оценка риска: 95/100", font_size=12, font_style="Bold", fill=tokens["light/crit-txt"])

make_text(rcard1["id"], "Несоразмерная неустойка (5%/день) без ограничения ответственности", font_size=13, font_style="Bold", fill=tokens["light/text-main"], width=612)
make_text(rcard1["id"], "Комментарий ИИ: Ставка 5%/день превышает среднерыночную ставку по ст. 395 ГК РФ более чем в 50 раз (ст. 333 ГК РФ, Постановление Пленума ВС РФ № 7). При просрочке на 20 дней штраф превысит сумму всего договора.", font_size=11, fill=tokens["light/text-sec"], width=612)

# Judicial Risk Predictor pill
j_pill = cmd("frame.create", {"parent": rcard1["id"], "width": 612, "height": 24, "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 4, "layout": "horizontal", "padding": [0, 8, 0, 8], "crossAlign": "center"}})
make_text(j_pill["id"], "⚖️ Судебный предиктор: Вероятность снижения неустойки судом по ст. 333 ГК РФ — 84%", font_size=10, font_style="Bold", fill=tokens["brand/primary"])

# AI Quote Box (Archetype 4)
quote_box = cmd("frame.create", {
    "parent": rcard1["id"], "width": 612, "height": 55,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["brand/primary"], "strokeWeight": 1,
        "cornerRadius": 6, "layout": "vertical", "padding": [6, 12, 6, 12], "gap": 2
    }
})
make_text(quote_box["id"], "Безопасная редакция ИИ (для протокола разногласий):", font_size=10, font_style="Bold", fill=tokens["brand/primary"])
make_text(quote_box["id"], "«...пени в размере 0.1% от стоимости непоставленного Товара за каждый день просрочки, но не более 10% от общей суммы Договора.»", font_size=10, fill=tokens["light/text-main"], width=588)

# Action Buttons
r1_btns = cmd("frame.create", {"parent": rcard1["id"], "width": 612, "height": 34, "props": {"fills": [], "layout": "horizontal", "gap": 10}})
make_btn(r1_btns["id"], "Принять правку ИИ", "primary", "light", "sm", width=175)
make_btn(r1_btns["id"], "Редактировать формулировку", "secondary", "light", "sm", width=225)
make_btn(r1_btns["id"], "В протокол .DOCX", "secondary", "light", "sm", width=180)

# DETAILED CONTRADICTION CARD: Clauses 3.2 vs 6.4
rcard2 = cmd("frame.create", {
    "parent": c_right["id"], "width": 640, "height": 130,
    "props": {
        "fill": tokens["light/contra-bg"], "stroke": tokens["light/contra-bdr"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "vertical", "padding": [12, 14, 12, 14], "gap": 4
    }
})
r2_hdr = cmd("frame.create", {"parent": rcard2["id"], "width": 612, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_badge(r2_hdr["id"], "КОЛЛИЗИЯ ПУНКТОВ • п. 3.2 vs п. 6.4", "contradiction", size="compact")
make_text(r2_hdr["id"], "Сроки и порядок оплаты", font_size=11, font_style="Bold", fill=tokens["light/contra-txt"])
make_text(rcard2["id"], "Внутреннее логическое противоречие: п. 3.2 требует оплату за 5 дней до отгрузки, а п. 6.4 устанавливает окончательный расчет через 30 дней после Акта.", font_size=11, font_style="Bold", fill=tokens["light/text-main"], width=612)
make_text(rcard2["id"], "Решение ИИ: Синхронизировать единый срок окончательного расчета: 15 банковских дней с момента подписания Акта приема-передачи оборудования.", font_size=10, fill=tokens["light/text-sec"], width=612)
make_btn(rcard2["id"], "Синхронизировать сроки в тексте договора →", "secondary", "light", "xs", width=612)


# ==============================================================================
# SCREEN 5: 05_Risk_Analytics_Light (x=0, y=1040)
# Сводная аналитика рисков, матрица рисков по типам, отчет для руководства
# ==============================================================================
print("\n[5/7] Сборка экрана 05_Risk_Analytics_Light (Аналитика рисков компании)...")
f5 = cmd("frame.create", {
    "parent": p3_id, "name": "05_Risk_Analytics_Light", "x": 0, "y": 1040, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f5_id = f5["id"]
make_app_navbar(f5_id, "Аналитика рисков", "Ольга Николаева", "Руководитель")

body5 = cmd("frame.create", {"parent": f5_id, "name": "AnalyticsBody", "x": 36, "y": 84, "width": 1368, "height": 870, "props": {"fills": [], "layout": "vertical", "gap": 16}})

# Filter & Report Header
f5_bar = cmd("frame.create", {"parent": body5["id"], "width": 1368, "height": 45, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(f5_bar["id"], "Сводная аналитика рисков юридического департамента", font_size=20, font_style="Bold", fill=tokens["light/text-main"], width=700)
f5_r = cmd("frame.create", {"parent": f5_bar["id"], "width": 480, "height": 40, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 12, "crossAlign": "center"}})
make_btn(f5_r["id"], "Период: Октябрь 2026", "secondary", "light", "sm", width=180)
make_btn(f5_r["id"], "Экспорт отчета Совету директоров", "primary", "light", "sm", width=250)

# 4 KPI cards
kpi_row5 = cmd("frame.create", {"parent": body5["id"], "width": 1368, "height": 96, "props": {"fills": [], "layout": "horizontal", "gap": 16}})
kpis5 = [
    ("Сэкономлено рабочих часов", "142 часа", "Равносильно 0.9 ставки юриста", "safe", tokens["brand/primary"], "Эффективность"),
    ("Предотвращено штрафов", "18.4 млн ₽", "По 14 договорам с неограниченным cap", "critical", tokens["light/crit-txt"], "Защита активов"),
    ("Устранено логических коллизий", "29 коллизий", "Исключен риск судебных споров по срокам", "contradiction", tokens["light/contra-txt"], "Коллизии"),
    ("Согласовано без правок", "34% договоров", "Типовые формы без единого риска", "safe", tokens["light/safe-txt"], "Согласовано")
]
for kt, kv, ks, ktype, top_color, badge_text in kpis5:
    card = cmd("frame.create", {
        "parent": kpi_row5["id"], "width": 330, "height": 96,
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
f5_charts = cmd("frame.create", {"parent": body5["id"], "width": 1368, "height": 410, "props": {"fills": [], "layout": "horizontal", "gap": 18}})

# Left: Risk Categories Bar Chart
c_card1 = cmd("frame.create", {
    "parent": f5_charts["id"], "width": 670, "height": 410,
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
    "parent": f5_charts["id"], "width": 680, "height": 410,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [20, 24, 20, 24], "gap": 12
    }
})
make_text(c_card2["id"], "Матрица рисков по типам договоров и недельная динамика:", font_size=14, font_style="Bold", fill=tokens["light/text-main"], width=630)

# Heatmap pills
hm_box = cmd("frame.create", {"parent": c_card2["id"], "width": 632, "height": 60, "props": {"fills": [], "layout": "horizontal", "gap": 8}})
hm_types = [
    ("Поставка", "78% риск", "critical", 120),
    ("Аренда", "65% риск", "warning", 115),
    ("Подряд", "45% риск", "warning", 115),
    ("Услуги", "22% риск", "safe", 115),
    ("NDA", "08% риск", "safe", 125)
]
for ht_name, ht_risk, ht_type, hw in hm_types:
    hb = cmd("frame.create", {"parent": hm_box["id"], "width": hw, "height": 55, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "vertical", "mainAlign": "center", "crossAlign": "center", "gap": 4}})
    cmd("node.create", {"type": "text", "parent": hb["id"], "text": ht_name, "props": {"fontSize": 11, "fontStyle": "Bold", "fill": tokens["light/text-main"]}})
    make_badge(hb["id"], ht_risk, ht_type, size="compact")

# Column Chart: Days of Week
make_text(c_card2["id"], "Динамика проверок по дням недели (пик в четверг — 40 договоров):", font_size=12, font_style="Bold", fill=tokens["light/text-sec"], width=630)
col_chart = cmd("frame.create", {"parent": c_card2["id"], "width": 632, "height": 190, "props": {"fills": [], "layout": "horizontal", "gap": 22, "crossAlign": "max", "padding": [0, 20, 0, 20]}})
days_data = [("Пн", 28, 90), ("Вт", 36, 120), ("Ср", 32, 105), ("Чт", 40, 140), ("Пт", 24, 80), ("Сб", 6, 25), ("Вс", 2, 12)]
for d_name, d_cnt, col_h in days_data:
    d_col = cmd("frame.create", {"parent": col_chart["id"], "width": 60, "height": col_h + 35, "props": {"fills": [], "layout": "vertical", "crossAlign": "center", "gap": 4}})
    make_text(d_col["id"], str(d_cnt), font_size=10, font_style="Bold", fill=tokens["brand/primary"])
    cmd("frame.create", {"parent": d_col["id"], "width": 44, "height": col_h, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4}})
    make_text(d_col["id"], d_name, font_size=11, fill=tokens["light/text-sec"])

# Team Productivity Table
t_perf = cmd("frame.create", {
    "parent": body5["id"], "width": 1368, "height": 220,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "clip": True
    }
})
tp_hdr = cmd("frame.create", {"parent": t_perf["id"], "width": 1368, "height": 38, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "layout": "horizontal", "padding": [0, 24, 0, 24], "crossAlign": "center"}})
make_text(tp_hdr["id"], "Сотрудник и специализация", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=320)
make_text(tp_hdr["id"], "Проверено договоров", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=240)
make_text(tp_hdr["id"], "Принято правок ИИ", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=240)
make_text(tp_hdr["id"], "Средняя оценка риска", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=240)
make_text(tp_hdr["id"], "Статус нагрузки юриста", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=240)

team_stats = [
    ("Алексей Смирнов • Ведущий юрист (Поставка)", "74 договора", "92% правок принято", "Высокий риск (64/100)", "Оптимальная (3.2 ч/день)"),
    ("Елена Васильева • Юрист (Аренда и услуги)", "48 договоров", "88% правок принято", "Средний риск (38/100)", "Оптимальная (2.1 ч/день)"),
    ("Михаил Рогов • Младший юрист (NDA и подряд)", "26 договоров", "96% правок принято", "Низкий риск (18/100)", "Доступен для новых задач")
]
for t_name, t_cnt, t_app, t_risk, t_load in team_stats:
    trow = cmd("frame.create", {"parent": t_perf["id"], "width": 1368, "height": 55, "props": {"fills": [], "stroke": tokens["light/border-subtle"], "strokeWeight": 1, "layout": "horizontal", "padding": [0, 24, 0, 24], "crossAlign": "center"}})
    make_text(trow["id"], t_name, font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=320)
    make_text(trow["id"], t_cnt, font_size=12, fill=tokens["light/text-main"], width=240)
    make_text(trow["id"], t_app, font_size=12, font_style="Bold", fill=tokens["light/safe-txt"], width=240)
    make_text(trow["id"], t_risk, font_size=12, fill=tokens["light/text-sec"], width=240)
    make_text(trow["id"], t_load, font_size=12, fill=tokens["light/text-sec"], width=240)


# ==============================================================================
# SCREEN 6: 06_Corporate_Playbook_Light (x=1500, y=1040)
# Конструктор правил IF/THEN, корпоративные формулировки, история версий
# ==============================================================================
print("\n[6/7] Сборка экрана 06_Corporate_Playbook_Light (Корпоративный Playbook)...")
f6 = cmd("frame.create", {
    "parent": p3_id, "name": "06_Corporate_Playbook_Light", "x": 1500, "y": 1040, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f6_id = f6["id"]
make_app_navbar(f6_id, "Корпоративный Playbook", "Ольга Николаева", "Руководитель")

body6 = cmd("frame.create", {"parent": f6_id, "name": "PlaybookBody", "x": 36, "y": 84, "width": 1368, "height": 870, "props": {"fills": [], "layout": "vertical", "gap": 14}})

# Playbook Header with Actions
p_hdr = cmd("frame.create", {"parent": body6["id"], "width": 1368, "height": 45, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(p_hdr["id"], "Корпоративный Playbook (ООО «ТехноСнаб»)", font_size=20, font_style="Bold", fill=tokens["light/text-main"], width=520)
p_hdr_r = cmd("frame.create", {"parent": p_hdr["id"], "width": 720, "height": 40, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "gap": 14, "crossAlign": "center"}})
make_badge(p_hdr_r["id"], "Редакция 3.2 (Ольга Н.)", "primary", size="regular")
make_btn(p_hdr_r["id"], "+ Создать новое правило", "primary", "light", "sm", width=200)
make_btn(p_hdr_r["id"], "Импорт из шаблона", "secondary", "light", "sm", width=170)

# Playbook Info Callout
p_callout = cmd("frame.create", {
    "parent": body6["id"], "width": 1368, "height": 55,
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
        "parent": body6["id"], "width": 1368, "height": 135,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "cornerRadius": 10, "layout": "horizontal", "padding": [12, 20, 12, 20], "crossAlign": "center", "gap": 20
        }
    })
    # Toggle switch
    tog = cmd("frame.create", {"parent": rc["id"], "width": 55, "height": 50, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "crossAlign": "center", "gap": 4}})
    t_track = cmd("frame.create", {"parent": tog["id"], "width": 42, "height": 22, "props": {"fill": tokens["brand/primary"] if is_on else tokens["light/border"], "cornerRadius": 11, "layout": "horizontal", "padding": [2, 2, 2, 2], "mainAlign": "max" if is_on else "min"}})
    cmd("frame.create", {"parent": t_track["id"], "width": 18, "height": 18, "props": {"fill": "#FFFFFF", "cornerRadius": 9}})
    make_text(tog["id"], "ВКЛ" if is_on else "ВЫКЛ", font_size=10, font_style="Bold", fill=tokens["brand/primary"] if is_on else tokens["light/text-muted"])
    
    # Rule Content
    r_body = cmd("frame.create", {"parent": rc["id"], "width": 1100, "height": 110, "props": {"fills": [], "layout": "vertical", "gap": 4}})
    
    # Header row
    rhdr = cmd("frame.create", {"parent": r_body["id"], "width": 1100, "height": 22, "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
    make_text(rhdr["id"], r_id, font_size=12, font_style="Bold", fill=tokens["light/text-muted"], width=65)
    make_text(rhdr["id"], r_title, font_size=13, font_style="Bold", fill=tokens["light/text-main"], width=520)
    make_badge(rhdr["id"], r_cat, "primary", size="compact")
    sev_type = "critical" if r_sev == "Критический" else ("contradiction" if r_sev == "Коллизия" else "warning")
    make_badge(rhdr["id"], r_sev, sev_type, size="compact")
    
    # IF / THEN Logic lines
    make_text(r_body["id"], r_if, font_size=11, fill=tokens["light/text-sec"], width=1100)
    make_text(r_body["id"], r_then, font_size=11, font_style="Bold", fill=tokens["light/text-main"], width=1100)
    make_text(r_body["id"], r_safe, font_size=11, font_style="Bold", fill=tokens["brand/primary"], width=1100)
    
    # Edit Action
    r_act = cmd("frame.create", {"parent": rc["id"], "width": 130, "height": 40, "props": {"fills": [], "layout": "horizontal", "mainAlign": "max", "crossAlign": "center"}})
    make_btn(r_act["id"], "Настроить", "secondary", "light", "sm", width=120)


# ==============================================================================
# SCREEN 7: 07_Team_Settings_Light (x=3000, y=1040)
# Центр управления: 3 профиля (Алексей, Ольга, Дмитрий), интеграции СЭД и 152-ФЗ
# ==============================================================================
print("\n[7/7] Сборка экрана 07_Team_Settings_Light (Команда, Профили и Интеграции)...")
f7 = cmd("frame.create", {
    "parent": p3_id, "name": "07_Team_Settings_Light", "x": 3000, "y": 1040, "width": 1440, "height": 980,
    "props": {"fill": tokens["light/bg"], "clip": True}
})
f7_id = f7["id"]
make_app_navbar(f7_id, "Команда", "Алексей Смирнов", "Юрист")

body7 = cmd("frame.create", {"parent": f7_id, "name": "TeamBody", "x": 36, "y": 84, "width": 1368, "height": 870, "props": {"fills": [], "layout": "horizontal", "gap": 24}})

# LEFT SIDEBAR: Current Profile, Persona Switcher & Notifications (Width 400)
sb_left = cmd("frame.create", {
    "parent": body7["id"], "width": 400, "height": 870,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": [24, 24, 24, 24], "gap": 16
    }
})

# Big Avatar & Info
av_card = cmd("frame.create", {"parent": sb_left["id"], "width": 352, "height": 80, "props": {"fills": [], "layout": "horizontal", "gap": 16, "crossAlign": "center"}})
av_big = cmd("frame.create", {"parent": av_card["id"], "width": 64, "height": 64, "props": {"fill": tokens["brand/primary-light"], "stroke": tokens["brand/primary"], "strokeWeight": 2, "cornerRadius": 32, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": av_big["id"], "text": "АС", "props": {"fontSize": 20, "fontStyle": "Bold", "fill": tokens["brand/primary"]}})

av_info = cmd("frame.create", {"parent": av_card["id"], "width": 260, "height": 60, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
make_text(av_info["id"], "Алексей Смирнов", font_size=18, font_style="Bold", fill=tokens["light/text-main"])
make_text(av_info["id"], "Ведущий юрисконсульт • ООО «ТехноСнаб»", font_size=11, fill=tokens["light/text-sec"])
make_badge(av_info["id"], "Editor • Проверяющий юрист", "primary", size="compact")

# Persona switcher on profile
make_text(sb_left["id"], "Переключить активный портрет (Тест интерфейса):", font_size=11, font_style="Bold", fill=tokens["light/text-muted"])
p_sw = cmd("frame.create", {"parent": sb_left["id"], "width": 352, "height": 34, "props": {"fill": tokens["light/card-tint"], "cornerRadius": 6, "layout": "horizontal", "padding": [2, 2, 2, 2], "gap": 2}})
ps_1 = cmd("frame.create", {"parent": p_sw["id"], "width": 115, "height": 30, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": ps_1["id"], "text": "Алексей (Юрист)", "props": {"fontSize": 10, "fontStyle": "Bold", "fill": "#FFFFFF"}})
ps_2 = cmd("frame.create", {"parent": p_sw["id"], "width": 115, "height": 30, "props": {"fills": [], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": ps_2["id"], "text": "Ольга (Руков.)", "props": {"fontSize": 10, "fill": tokens["light/text-sec"]}})
ps_3 = cmd("frame.create", {"parent": p_sw["id"], "width": 115, "height": 30, "props": {"fills": [], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": ps_3["id"], "text": "Дмитрий (Дир.)", "props": {"fontSize": 10, "fill": tokens["light/text-sec"]}})

# Subscription quota widget
sub_w = cmd("frame.create", {
    "parent": sb_left["id"], "width": 352, "height": 130,
    "props": {
        "fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 8, "layout": "vertical", "padding": [14, 16, 14, 16], "gap": 8
    }
})
make_text(sub_w["id"], "Тариф: Корпоративный SaaS (On-Premise)", font_size=12, font_style="Bold", fill=tokens["light/text-main"])
make_text(sub_w["id"], "Использовано проверок: 148 из 500 в этом месяце", font_size=11, fill=tokens["light/text-sec"])
# Progress
s_tr = cmd("frame.create", {"parent": sub_w["id"], "width": 320, "height": 6, "props": {"fill": tokens["light/border"], "cornerRadius": 3}})
cmd("frame.create", {"parent": s_tr["id"], "width": 95, "height": 6, "props": {"fill": tokens["brand/primary"], "cornerRadius": 3}})
make_text(sub_w["id"], "Действует до 31 декабря 2026 г. • 5 юристов в штате", font_size=10, fill=tokens["light/text-muted"])
make_btn(sub_w["id"], "Управление корпоративной подпиской", "secondary", "light", "xs", width=320)

# Notification Channels & Periods (From Story Map)
make_text(sb_left["id"], "Настройка каналов и частоты уведомлений:", font_size=12, font_style="Bold", fill=tokens["light/text-main"])
notifs = [
    ("Email: alexey.smirnov@technosnab.ru (мгновенно)", True),
    ("Telegram-бот @LexAI_Legal_Bot (при рисках > 80)", True),
    ("SMS-алерт при судебных коллизиях", False),
    ("Еженедельный дайджест для руководства (пн, 09:00)", True)
]
for n_txt, n_chk in notifs:
    nrow = cmd("frame.create", {"parent": sb_left["id"], "width": 352, "height": 24, "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
    make_badge(nrow["id"], "✓ ВКЛ" if n_chk else "ВЫКЛ", "safe" if n_chk else "warning", size="compact")
    make_text(nrow["id"], n_txt, font_size=11, fill=tokens["light/text-main"])


# RIGHT CONTENT: Team Matrix, Integrations Hub & 152-FZ Compliance (Width 944)
sb_right = cmd("frame.create", {"parent": body7["id"], "width": 944, "height": 870, "props": {"fills": [], "layout": "vertical", "gap": 16}})

# 1. Team Access Table
team_box = cmd("frame.create", {
    "parent": sb_right["id"], "width": 944, "height": 290,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "clip": True
    }
})
tb_hdr = cmd("frame.create", {"parent": team_box["id"], "width": 944, "height": 45, "props": {"fill": tokens["light/card-tint"], "stroke": tokens["light/border"], "strokeWeight": 1, "layout": "horizontal", "padding": [0, 20, 0, 20], "mainAlign": "spaceBetween", "crossAlign": "center"}})
make_text(tb_hdr["id"], "Управление доступом команды (Портреты пользователей)", font_size=13, font_style="Bold", fill=tokens["light/text-main"])
make_btn(tb_hdr["id"], "+ Пригласить юриста", "primary", "light", "xs", width=160)

# Table column names
th_row = cmd("frame.create", {"parent": team_box["id"], "width": 944, "height": 32, "props": {"fills": [], "stroke": tokens["light/border-subtle"], "strokeWeight": 1, "layout": "horizontal", "padding": [0, 20, 0, 20], "crossAlign": "center"}})
make_text(th_row["id"], "Сотрудник", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=220)
make_text(th_row["id"], "Портрет из отчета", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=200)
make_text(th_row["id"], "Роль в системе", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=170)
make_text(th_row["id"], "Статус", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=140)
make_text(th_row["id"], "Действие", font_size=11, font_style="Bold", fill=tokens["light/text-sec"], width=130)

members = [
    ("Алексей Смирнов", "alexey.smirnov@technosnab.ru", "Алексей (50%) — юрист", "Editor / Аналитик", "safe", "Активен сейчас"),
    ("Ольга Николаева", "olga.nikolaeva@technosnab.ru", "Ольга (25%) — рук. отдела", "Admin / Playbook Lead", "safe", "Активен"),
    ("Дмитрий Ковалев", "dmitry.kovalev@technosnab.ru", "Дмитрий (25%) — закупки", "Viewer / Executive", "safe", "Активен"),
    ("Елена Васильева", "elena.vasilieva@technosnab.ru", "Юрисконсульт по аренде", "Editor / Аналитик", "safe", "Активен")
]
for m_name, m_mail, m_poa, m_role, m_st_t, m_st in members:
    mrow = cmd("frame.create", {"parent": team_box["id"], "width": 944, "height": 50, "props": {"fills": [], "stroke": tokens["light/border-subtle"], "strokeWeight": 1, "layout": "horizontal", "padding": [0, 20, 0, 20], "crossAlign": "center"}})
    m_info = cmd("frame.create", {"parent": mrow["id"], "width": 220, "height": 36, "props": {"fills": [], "layout": "vertical", "mainAlign": "center"}})
    make_text(m_info["id"], m_name, font_size=11, font_style="Bold", fill=tokens["light/text-main"])
    make_text(m_info["id"], m_mail, font_size=10, fill=tokens["light/text-muted"])
    
    make_text(mrow["id"], m_poa, font_size=11, fill=tokens["light/text-sec"], width=200)
    make_text(mrow["id"], m_role, font_size=11, font_style="Bold", fill=tokens["light/text-main"], width=170)
    
    st_b = cmd("frame.create", {"parent": mrow["id"], "width": 140, "height": 30, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_badge(st_b["id"], m_st, m_st_t, size="compact")
    
    make_btn(mrow["id"], "Права доступа", "secondary", "light", "xs", width=110)

# 2. Corporate Integrations Hub (СЭД, Диадок, 1С, СПАРК)
int_card = cmd("frame.create", {
    "parent": sb_right["id"], "width": 944, "height": 260,
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
    irow = cmd("frame.create", {"parent": int_card["id"], "width": 904, "height": 45, "props": {"fill": tokens["light/card-tint"], "cornerRadius": 6, "layout": "horizontal", "padding": [0, 16, 0, 16], "mainAlign": "spaceBetween", "crossAlign": "center"}})
    i_left = cmd("frame.create", {"parent": irow["id"], "width": 700, "height": 36, "props": {"fills": [], "layout": "vertical", "mainAlign": "center"}})
    make_text(i_left["id"], iname, font_size=11, font_style="Bold", fill=tokens["light/text-main"])
    make_text(i_left["id"], idesc, font_size=10, fill=tokens["light/text-sec"])
    make_badge(irow["id"], istatus, itype, size="compact")

# 3. Security & 152-FZ Compliance Card
sec_card = cmd("frame.create", {
    "parent": sb_right["id"], "width": 944, "height": 260,
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
    sc = cmd("frame.create", {"parent": sec_card["id"], "width": 904, "height": 55, "props": {"fill": tokens["light/safe-bg"], "stroke": tokens["light/safe-bdr"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 16, 0, 16], "mainAlign": "spaceBetween", "crossAlign": "center"}})
    sc_col = cmd("frame.create", {"parent": sc["id"], "width": 740, "height": 40, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
    make_text(sc_col["id"], stitle, font_size=11, font_style="Bold", fill=tokens["light/safe-txt"])
    make_text(sc_col["id"], sdesc, font_size=10, fill=tokens["light/text-sec"])
    make_badge(sc["id"], sbadge, "safe", size="compact")


# ==============================================================================
# SAVE & EXPORT
# ==============================================================================
print("\n💾 Сохранение изменений в открытом проекте...")
res_save = cmd("file.save", {})
print(f"  Результат сохранения: {res_save}")

print("\n📸 Экспорт обновленных PNG рендеров всех 7 экранов...")
render_targets = [
    ("screen_01_onboarding_light.png", f1_id),
    ("screen_02_dashboard_light.png", f2_id),
    ("screen_03_processing_light.png", f3_id),
    ("screen_04_analysis_light.png", f4_id),
    ("screen_05_analytics_light.png", f5_id),
    ("screen_06_playbook_light.png", f6_id),
    ("screen_07_team_light.png", f7_id),
]

for fname, fid in render_targets:
    out_p = os.path.join(EXPORT_DIR, fname)
    cmd("file.export", {"ids": [fid], "format": "png", "scale": 2, "path": out_p})
    print(f"  ✓ Экспортирован: {fname}")

s.close()
print("\n✨ ВСЕ 7 ЭКРАНОВ РАСШИРЕННОГО ПРОТОТИПА УСПЕШНО СОЗДАНЫ И ЭКСПОРТИРОВАНЫ!")
