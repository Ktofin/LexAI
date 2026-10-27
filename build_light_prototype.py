#!/usr/bin/env python3
"""
LexAI — Complete Light Theme Website Prototype in Open FigCraft.
Builds the full end-to-end interactive product prototype across all 7 screens:
Row 1 (Primary Document Lifecycle):
  - 01_Onboarding_Auth_Light (x=0, y=0)
  - 02_Dashboard_Light (x=1500, y=0)
  - 03_Processing_Light (x=3000, y=0)
  - 04_Contract_Analysis_Light (x=4500, y=0)
Row 2 (Management & Configuration Tabs):
  - 05_Risk_Analytics_Light (x=0, y=1040)
  - 06_Corporate_Playbook_Light (x=1500, y=1040)
  - 07_Team_Settings_Light (x=3000, y=1040)

Features:
- Anthropic Warm Linen (#FAF9F5, #FFFFFF, #E5E3D8, Terracotta #D97757)
- 5 Distinct Container Archetypes (Top colored bars, risk alert stripes, contradiction diffs, AI quote boxes, dropzones)
- Guaranteed NO text overflow / clipping (textAutoResize: "height", explicit wrapping widths)
- Dynamic button sizing with comfortable padding
- Updates live directly in the open FigCraft on port 9897
"""

import socket
import json
import os
import sys

PORT = 9897
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(WORKSPACE_DIR, "renders")
os.makedirs(EXPORT_DIR, exist_ok=True)

print(f"🔄 Подключение к открытому FigCraft на порту {PORT}...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", PORT))
seq = 0

def cmd(action, params={}):
    global seq
    seq += 1
    req = json.dumps({"id": seq, "method": "engine.execute", "params": {"command": action, "params": params}}) + "\n"
    s.sendall(req.encode("utf-8"))
    buf = b""
    s.settimeout(20.0)
    while True:
        chunk = s.recv(16384)
        if not chunk: break
        buf += chunk
        if b"\n" in buf: break
    res = json.loads(buf.decode("utf-8"))
    if "error" in res and res["error"]:
        print(f"⚠️ Ошибка в {action}: {res['error']}")
    return res.get("result")

# Design Tokens (Anthropic Warm Linen & Terracotta Palette)
tokens = {
    "brand/primary": "#D97757",
    "brand/primary-hover": "#C26546",
    "brand/primary-active": "#AC5437",
    
    "light/bg": "#FAF9F5",
    "light/card": "#FFFFFF",
    "light/card-subtle": "#F4F3ED",
    "light/border": "#E5E3D8",
    "light/border-strong": "#CCC8BC",
    "light/text-main": "#141413",
    "light/text-sec": "#615F59",
    "light/text-muted": "#8C8A82",
    "light/brand-tint": "#FDF5F2",
    "light/brand-bdr": "#F5D0C5",
    
    "light/crit-bg": "#FDF2F2",
    "light/crit-bdr": "#F8B4B4",
    "light/crit-txt": "#C81E1E",
    
    "light/contra-bg": "#F5F3FF",
    "light/contra-bdr": "#DDD6FE",
    "light/contra-txt": "#6D28D9",
    
    "light/warn-bg": "#FFFBEB",
    "light/warn-bdr": "#FDE68A",
    "light/warn-txt": "#B45309",
    
    "light/safe-bg": "#F0FDF4",
    "light/safe-bdr": "#BBF7D0",
    "light/safe-txt": "#15803D",
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

# ROBUST TEXT CREATOR WITH WRAPPING SUPPORT
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

# ROBUST BUTTON CREATOR (NEVER CLIPS TEXT)
def make_btn(parent, text, variant="primary", theme="light", size="md", width=None, state="default", **kwargs):
    t_pre = "light"
    cfg = {
        "lg": {"h": 48, "font": 16, "px": 24, "py": 12, "r": 8},
        "md": {"h": 40, "font": 14, "px": 18, "py": 10, "r": 6},
        "sm": {"h": 32, "font": 12, "px": 14, "py": 6,  "r": 6}
    }.get(size, {"h": 40, "font": 14, "px": 18, "py": 10, "r": 6})

    min_required_w = int(len(text) * cfg["font"] * 0.72 + 2 * cfg["px"])
    actual_w = max(width, min_required_w) if width else None

    bg, stroke, stroke_w, txt_c, opacity = None, None, 0, tokens[f"{t_pre}/text-main"], 1.0
    if variant == "primary":
        bg = tokens["brand/primary"]
        txt_c = "#FFFFFF"
        if state == "hover": bg = tokens["brand/primary-hover"]
        elif state == "active": bg = tokens["brand/primary-active"]
        elif state == "disabled": opacity = 0.45
    elif variant == "secondary":
        bg, stroke, stroke_w = tokens[f"{t_pre}/card"], tokens[f"{t_pre}/border"], 1
        txt_c = tokens[f"{t_pre}/text-main"]
        if state == "hover": bg = tokens[f"{t_pre}/card-subtle"]
        elif state == "disabled": opacity = 0.45
    elif variant == "outline":
        stroke, stroke_w, txt_c = tokens[f"{t_pre}/border"], 1, tokens[f"{t_pre}/text-main"]
        if state == "disabled": opacity = 0.45
    elif variant == "danger":
        bg, stroke, stroke_w, txt_c = tokens[f"{t_pre}/crit-bg"], tokens[f"{t_pre}/crit-bdr"], 1, tokens[f"{t_pre}/crit-txt"]
    elif variant == "success":
        bg, stroke, stroke_w, txt_c = tokens[f"{t_pre}/safe-bg"], tokens[f"{t_pre}/safe-bdr"], 1, tokens[f"{t_pre}/safe-txt"]
    elif variant == "ghost":
        txt_c = tokens[f"{t_pre}/text-sec"]
        if state == "hover": bg, txt_c = tokens[f"{t_pre}/card-subtle"], tokens[f"{t_pre}/text-main"]

    props = {
        "layout": "horizontal", "mainAlign": "center", "crossAlign": "center",
        "padding": [cfg["py"], cfg["px"], cfg["py"], cfg["px"]],
        "cornerRadius": cfg["r"], "opacity": opacity
    }
    if bg: props["fill"] = bg
    else: props["fills"] = []
    if stroke and stroke_w > 0: props["stroke"], props["strokeWeight"] = stroke, stroke_w

    f_args = {"parent": parent, "height": cfg["h"], "props": props}
    if actual_w: f_args["width"] = actual_w
    else: f_args["props"]["sizingH"] = "hug"

    b = cmd("frame.create", f_args)
    if variant == "primary" and state == "default" and "brand/primary" in var_ids:
        bind(b["id"], "fill", "brand/primary")
    cmd("node.create", {"type": "text", "parent": b["id"], "text": text, "props": {"fontSize": cfg["font"], "fontStyle": "Bold", "fill": txt_c}})
    return b["id"]

# ROBUST STATUS BADGE (HUGS TEXT BEAUTIFULLY)
def make_badge(parent, text, btype="safe", theme="light", size="regular", **kwargs):
    t_pre = "light"
    cfg = {"regular": {"h": 26, "font": 12, "px": 12, "dot": 6}, "compact": {"h": 20, "font": 10, "px": 8, "dot": 5}}.get(size, {"h": 26, "font": 12, "px": 12, "dot": 6})
    mapping = {
        "critical": (tokens[f"{t_pre}/crit-bg"], tokens[f"{t_pre}/crit-bdr"], tokens[f"{t_pre}/crit-txt"]),
        "contradiction": (tokens[f"{t_pre}/contra-bg"], tokens[f"{t_pre}/contra-bdr"], tokens[f"{t_pre}/contra-txt"]),
        "warning": (tokens[f"{t_pre}/warn-bg"], tokens[f"{t_pre}/warn-bdr"], tokens[f"{t_pre}/warn-txt"]),
        "safe": (tokens[f"{t_pre}/safe-bg"], tokens[f"{t_pre}/safe-bdr"], tokens[f"{t_pre}/safe-txt"]),
        "primary": (tokens[f"{t_pre}/brand-tint"], tokens[f"{t_pre}/brand-bdr"], tokens["brand/primary"])
    }
    bg, bdr, txt_c = mapping.get(btype, mapping["safe"])
    min_badge_w = int(len(text) * cfg["font"] * 0.72 + 2 * cfg["px"] + cfg["dot"] + 8)
    badge = cmd("frame.create", {
        "parent": parent, "height": cfg["h"], "width": min_badge_w,
        "props": {"fill": bg, "stroke": bdr, "strokeWeight": 1, "cornerRadius": 100, "layout": "horizontal", "padding": [0, cfg["px"], 0, cfg["px"]], "gap": 6, "crossAlign": "center", "sizingH": "hug"}
    })
    cmd("frame.create", {"parent": badge["id"], "width": cfg["dot"], "height": cfg["dot"], "props": {"fill": txt_c, "cornerRadius": cfg["dot"] // 2}})
    cmd("node.create", {"type": "text", "parent": badge["id"], "text": text, "props": {"fontSize": cfg["font"], "fontStyle": "Bold", "fill": txt_c}})
    return badge["id"]

# UNIFIED APP NAVBAR
def make_app_navbar(parent, active_tab="Договоры"):
    t_pre = "light"
    nav = cmd("frame.create", {
        "parent": parent, "name": "Navbar", "x": 0, "y": 0, "width": 1440, "height": 64,
        "props": {
            "fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeBottomWeight": 1,
            "layout": "horizontal", "padding": [0, 36, 0, 36], "mainAlign": "spaceBetween", "crossAlign": "center"
        }
    })
    n_l = cmd("frame.create", {"parent": nav["id"], "props": {"fills": [], "layout": "horizontal", "gap": 36, "crossAlign": "center"}})
    
    brand_box = cmd("frame.create", {"parent": n_l["id"], "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
    mark = cmd("frame.create", {"parent": brand_box["id"], "width": 20, "height": 20, "props": {"fill": tokens["brand/primary"], "cornerRadius": 5, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
    cmd("node.create", {"type": "text", "parent": mark["id"], "text": "§", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": "#FFFFFF"}})
    make_text(brand_box["id"], "LexAI Legal", font_size=18, font_style="Bold", fill=tokens[f"{t_pre}/text-main"])
    
    n_links = cmd("frame.create", {"parent": n_l["id"], "props": {"fills": [], "layout": "horizontal", "gap": 24, "crossAlign": "center"}})
    for t in ["Договоры", "Аналитика рисков", "Корпоративный Playbook", "Команда"]:
        is_act = (t == active_tab)
        clr = tokens["brand/primary"] if is_act else tokens[f"{t_pre}/text-sec"]
        make_text(n_links["id"], t, font_size=13, font_style="Bold" if is_act else "Regular", fill=clr)

    n_r = cmd("frame.create", {"parent": nav["id"], "props": {"fills": [], "layout": "horizontal", "gap": 16, "crossAlign": "center"}})
    make_text(n_r["id"], "Алексей Смирнов", font_size=13, font_style="Bold", fill=tokens[f"{t_pre}/text-main"])
    av = cmd("frame.create", {"parent": n_r["id"], "width": 34, "height": 34, "props": {"fill": tokens[f"{t_pre}/brand-tint"], "stroke": tokens[f"{t_pre}/brand-bdr"], "strokeWeight": 1, "cornerRadius": 17, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
    make_text(av["id"], "АС", font_size=12, font_style="Bold", fill=tokens["brand/primary"])
    return nav["id"]

# =============================================================================
# CLEAN UP PAGE 3 PREVIOUS SCREENS
# =============================================================================
print("Очистка старых экранов на Page 3 (☀️ Screens — Light Theme)...")
p3_info = cmd("node.get", {"id": 3})
if p3_info and "children" in p3_info:
    old_ids = [c["id"] for c in p3_info["children"]]
    if old_ids:
        cmd("edit.delete", {"ids": old_ids})
        print(f"  Удалено старых узлов: {len(old_ids)}")

cmd("page.select", {"index": 2})

# =============================================================================
# SCREEN 1: 01_Onboarding_Auth_Light (x=0, y=0)
# =============================================================================
print("\n[1/7] Сборка экрана 01_Onboarding_Auth_Light (Приветствие и Вход)...")
f1 = cmd("frame.create", {"name": "01_Onboarding_Auth_Light", "x": 0, "y": 0, "width": 1440, "height": 960, "props": {"fill": tokens["light/bg"], "cornerRadius": 16, "clip": True}})
f1_id = f1["id"]

# Onboarding Landing Navbar
nav1 = cmd("frame.create", {
    "parent": f1_id, "name": "LandingNavbar", "x": 0, "y": 0, "width": 1440, "height": 64,
    "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeBottomWeight": 1, "layout": "horizontal", "padding": [0, 48, 0, 48], "mainAlign": "spaceBetween", "crossAlign": "center"}
})
nav1_l = cmd("frame.create", {"parent": nav1["id"], "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
mark1 = cmd("frame.create", {"parent": nav1_l["id"], "width": 22, "height": 22, "props": {"fill": tokens["brand/primary"], "cornerRadius": 5, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": mark1["id"], "text": "§", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": "#FFFFFF"}})
make_text(nav1_l["id"], "LexAI Legal", font_size=19, font_style="Bold", fill=tokens["light/text-main"])
make_badge(nav1_l["id"], "On-Premise Edition", "primary", size="compact")

nav1_links = cmd("frame.create", {"parent": nav1["id"], "props": {"fills": [], "layout": "horizontal", "gap": 28, "crossAlign": "center"}})
for nl in ["Возможности", "Безопасность (152-ФЗ)", "Корпоративный Playbook", "Тарифы"]:
    make_text(nav1_links["id"], nl, font_size=13, fill=tokens["light/text-sec"])

nav1_r = cmd("frame.create", {"parent": nav1["id"], "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
make_btn(nav1_r["id"], "Демо-тест без входа", "secondary", "light", "sm", width=170)
make_btn(nav1_r["id"], "Войти в систему →", "primary", "light", "sm", width=160)

# Hero 2-Column Split
hero_split = cmd("frame.create", {"parent": f1_id, "x": 48, "y": 92, "width": 1344, "height": 830, "props": {"fills": [], "layout": "horizontal", "gap": 48, "crossAlign": "center"}})

# Left Hero Column (720px)
h_left = cmd("frame.create", {"parent": hero_split["id"], "width": 730, "height": 800, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 20}})
make_badge(h_left["id"], "ВЕРСИЯ 2.4: АВТОМАТИЧЕСКИЙ ПОИСК КОЛЛИЗИЙ И СТ. 333 ГК РФ", "primary", size="regular")
make_text(h_left["id"], "Интеллектуальная проверка договоров на риски и противоречия за 1.5 минуты", font_size=32, font_style="Bold", fill=tokens["light/text-main"], width=720)
make_text(h_left["id"], "ИИ-ассистент юриста и руководителя. Находит нестыковки сроков, скрытые штрафы, неограниченную ответственность и готовит готовый протокол разногласий по ст. ГК РФ.", font_size=15, fill=tokens["light/text-sec"], width=710)

# 3 Value Proposition Cards (Archetype 4 inspired)
val_box = cmd("frame.create", {"parent": h_left["id"], "width": 730, "height": 280, "props": {"fills": [], "layout": "vertical", "gap": 12}})
for v_tag, v_title, v_desc, v_bdr in [
    ("СКОРОСТЬ", "Анализ за 90 сек вместо 3 часов ручной вычитки", "Экономия до 85% рабочего времени юриста на типовых договорах поставки, подряда, аренды и оказания услуг.", tokens["brand/primary"]),
    ("КОЛЛИЗИИ", "Поиск взаимных противоречий между пунктами договора", "Уникальный алгоритм сопоставляет сроки оплаты (п. 3.2) и графики поставки (п. 6.4) внутри единого документа.", tokens["light/contra-txt"]),
    ("БЕЗОПАСНОСТЬ", "100% On-Premise изоляция данных и соответствие 152-ФЗ", "Данные контрактов не передаются в публичные нейросети, не индексируются и не используются для обучения.", tokens["light/safe-txt"])
]:
    vc = cmd("frame.create", {
        "parent": val_box["id"], "width": 730, "height": 76,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "strokeLeftWeight": 4, "cornerRadius": 8, "layout": "vertical", "padding": [12, 18, 12, 18], "gap": 3
        }
    })
    vc_top = cmd("frame.create", {"parent": vc["id"], "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
    make_text(vc_top["id"], v_title, font_size=13, font_style="Bold", fill=tokens["light/text-main"])
    make_text(vc["id"], v_desc, font_size=11, fill=tokens["light/text-sec"], width=680)

# Social Proof Footnote
sp_box = cmd("frame.create", {"parent": h_left["id"], "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
make_text(sp_box["id"], "Доверяют юрдепартаменты 140+ компаний РФ:", font_size=12, fill=tokens["light/text-muted"])
for c_name in ["ООО «ПромМашСервис»", "АО «СеверЛогистик»", "ТехноПарк Групп"]:
    cp = cmd("frame.create", {"parent": sp_box["id"], "props": {"fill": tokens["light/card-subtle"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 4, "padding": [3, 8, 3, 8]}})
    make_text(cp["id"], c_name, font_size=11, font_style="Bold", fill=tokens["light/text-sec"])

# Right Auth & Fast Test Card (560px)
h_right = cmd("frame.create", {
    "parent": hero_split["id"], "width": 560, "height": 720,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 16, "layout": "vertical", "padding": 36, "gap": 18, "mainAlign": "center"
    }
})
make_text(h_right["id"], "Вход в систему LexAI", font_size=22, font_style="Bold", fill=tokens["light/text-main"])
make_text(h_right["id"], "Войдите в защищенный корпоративный контур вашей организации", font_size=13, fill=tokens["light/text-sec"])

# Role Selector Tabs
role_row = cmd("frame.create", {"parent": h_right["id"], "width": 488, "height": 38, "props": {"fill": tokens["light/card-subtle"], "cornerRadius": 8, "layout": "horizontal", "padding": 3, "gap": 4}})
r_act = cmd("frame.create", {"parent": role_row["id"], "width": 238, "height": 32, "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
make_text(r_act["id"], "Юрист / Комплаенс", font_size=12, font_style="Bold", fill=tokens["brand/primary"])
r_inact = cmd("frame.create", {"parent": role_row["id"], "width": 238, "height": 32, "props": {"fills": [], "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
make_text(r_inact["id"], "Руководитель / Директор", font_size=12, fill=tokens["light/text-sec"])

# Form Fields
for lbl, val in [("Рабочий Email юриста", "alexey.smirnov@technosnab.ru"), ("Пароль", "••••••••••••••••")]:
    ib = cmd("frame.create", {"parent": h_right["id"], "width": 488, "height": 64, "props": {"fills": [], "layout": "vertical", "gap": 6}})
    make_text(ib["id"], lbl, font_size=12, font_style="Bold", fill=tokens["light/text-main"])
    inp = cmd("frame.create", {"parent": ib["id"], "width": 488, "height": 40, "props": {"fill": tokens["light/card-subtle"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 8, "layout": "horizontal", "padding": [0, 14, 0, 14], "crossAlign": "center"}})
    make_text(inp["id"], val, font_size=13, fill=tokens["light/text-main"] if "@" in val else tokens["light/text-muted"])

make_btn(h_right["id"], "Войти в систему →", "primary", "light", "md", width=488)
make_btn(h_right["id"], "Войти через Корпоративный SSO / Госуслуги", "secondary", "light", "md", width=488)

div_or = cmd("frame.create", {"parent": h_right["id"], "width": 488, "height": 1, "props": {"fill": tokens["light/border"]}})

# Fast Test Dropzone in Auth Card
test_dz = cmd("frame.create", {
    "parent": h_right["id"], "width": 488, "height": 85,
    "props": {
        "fill": tokens["light/brand-tint"], "stroke": tokens["light/brand-bdr"], "strokeWeight": 1.5,
        "cornerRadius": 8, "layout": "vertical", "mainAlign": "center", "crossAlign": "center", "padding": 12, "gap": 4
    }
})
make_text(test_dz["id"], "Или перетащите договор сюда для экспресс-проверки", font_size=12, font_style="Bold", fill=tokens["brand/primary"])
make_text(test_dz["id"], "Бесплатный демо-анализ первых 3 страниц без регистрации (.PDF, .DOCX)", font_size=11, fill=tokens["light/text-sec"])


# =============================================================================
# SCREEN 2: 02_Dashboard_Light (x=1500, y=0)
# =============================================================================
print("\n[2/7] Сборка экрана 02_Dashboard_Light (Главная / Реестр договоров)...")
f2 = cmd("frame.create", {"name": "02_Dashboard_Light", "x": 1500, "y": 0, "width": 1440, "height": 960, "props": {"fill": tokens["light/bg"], "cornerRadius": 16, "clip": True}})
f2_id = f2["id"]
make_app_navbar(f2_id, "Договоры")

d_body = cmd("frame.create", {"parent": f2_id, "x": 36, "y": 88, "width": 1368, "height": 840, "props": {"fills": [], "layout": "vertical", "gap": 20, "sizingH": "fixed"}})

# KPI Row with Top Color Bars (Archetype 1)
k_row = cmd("frame.create", {"parent": d_body["id"], "width": 1368, "height": 95, "props": {"fills": [], "layout": "horizontal", "gap": 16, "sizingH": "fill"}})
for kt, kv, ks, ktype, top_color, badge_text in [
    ("Проверено договоров", "148 шт.", "+18 за неделю", "safe", tokens["brand/primary"], "В норме"),
    ("Критических рисков", "38 условий", "Штрафы и неустойки", "critical", tokens["light/crit-txt"], "Внимание"),
    ("Логических коллизий", "19 коллизий", "Несовпадение сроков", "contradiction", tokens["light/contra-txt"], "Коллизии"),
    ("Среднее время анализа", "1 мин 18 сек", "Норматив < 2 мин", "safe", tokens["light/safe-txt"], "Отлично")
]:
    kc = cmd("frame.create", {
        "parent": k_row["id"], "width": 330, "height": 95,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "strokeTopWeight": 3, "cornerRadius": 10, "layout": "vertical", "padding": [12, 16, 12, 16], "gap": 4, "sizingH": "fill"
        }
    })
    kc_top = cmd("frame.create", {"parent": kc["id"], "width": 298, "height": 18, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
    make_text(kc_top["id"], kt, font_size=11, fill=tokens["light/text-sec"])
    make_badge(kc_top["id"], badge_text, ktype, "light", "compact")
    make_text(kc["id"], kv, font_size=20, font_style="Bold", fill=top_color)
    make_text(kc["id"], ks, font_size=11, fill=tokens["light/text-muted"])

# Dropzone Container (Archetype 5)
up = cmd("frame.create", {
    "parent": d_body["id"], "width": 1368, "height": 175,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 12, "layout": "vertical", "padding": 18, "gap": 12, "sizingH": "fill"
    }
})
make_text(up["id"], "Быстрая загрузка договора на проверку", font_size=15, font_style="Bold", fill=tokens["light/text-main"])

dz = cmd("frame.create", {
    "parent": up["id"], "width": 1332, "height": 72,
    "props": {
        "fill": tokens["light/card-subtle"], "stroke": tokens["light/brand-bdr"], "strokeWeight": 1.5,
        "cornerRadius": 8, "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "padding": [0, 24, 0, 24], "sizingH": "fill"
    }
})
dz_l = cmd("frame.create", {"parent": dz["id"], "props": {"fills": [], "layout": "vertical", "gap": 3}})
make_text(dz_l["id"], "Перетащите файл договора для извлечения текста и проверки коллизий", font_size=13, font_style="Bold", fill=tokens["brand/primary"])

chips = cmd("frame.create", {"parent": dz_l["id"], "props": {"fills": [], "layout": "horizontal", "gap": 6, "crossAlign": "center", "sizingH": "hug"}})
for c_txt in [".PDF", ".DOCX", "до 50 МБ"]:
    cp = cmd("frame.create", {"parent": chips["id"], "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 4, "padding": [2, 6, 2, 6], "sizingH": "hug"}})
    make_text(cp["id"], c_txt, font_size=10, font_style="Bold", fill=tokens["light/text-sec"])

dz_r = cmd("frame.create", {"parent": dz["id"], "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
make_btn(dz_r["id"], "Запустить анализ ИИ", "primary", "light", "md", width=180)
make_btn(dz_r["id"], "Выбрать файл", "secondary", "light", "md", width=130)

# Registry Table Container
t_card = cmd("frame.create", {
    "parent": d_body["id"], "width": 1368, "height": 490,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 12, "layout": "vertical", "padding": 18, "gap": 10, "sizingH": "fill"
    }
})
t_hdr = cmd("frame.create", {"parent": t_card["id"], "width": 1332, "height": 28, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
make_text(t_hdr["id"], "Реестр проверенных договоров", font_size=15, font_style="Bold", fill=tokens["light/text-main"])
make_badge(t_hdr["id"], "Всего 148 документов", "safe", "light", "compact")

t_th = cmd("frame.create", {"parent": t_card["id"], "width": 1332, "height": 34, "props": {"fill": tokens["light/card-subtle"], "cornerRadius": 6, "layout": "horizontal", "padding": [0, 16, 0, 16], "crossAlign": "center", "sizingH": "fill"}})
for tt, tw in [("Документ и контрагент", 380), ("Тип договора", 160), ("Уровень риска", 180), ("Выявленные замечания", 260), ("Статус проверки", 150), ("Действие", 150)]:
    make_text(t_th["id"], tt, font_size=12, font_style="Bold", fill=tokens["light/text-sec"], width=tw)

for fname, counterpart, dtype, rlevel, rtype, problems, status, action_text, btn_style in [
    ("Договор_поставки_станков_№48-2026.docx", "ООО «ПромМашСервис»", "Поставка оборудования", "Критический (78%)", "critical", "3 риска • 2 коллизии сроков", "Требует правок", "Открыть отчет", "primary"),
    ("NDA_Соглашение_о_конфиденциальности.pdf", "ООО «ТехноПарк Групп»", "NDA / Соглашение", "Безопасно (12%)", "safe", "0 рисков • Соответствие норме", "Согласовано", "Скачать резюме", "secondary"),
    ("Договор_оказания_маркетинговых_услуг.docx", "ИП Соколов В.А.", "Возмездное оказание услуг", "Средний риск (42%)", "warning", "1 риск: короткий срок претензий", "На согласовании", "Смотреть правки", "primary"),
    ("Аренда_складского_помещения_Б-4.pdf", "АО «СеверЛогистик»", "Аренда коммерч. недвиж.", "Критический (65%)", "critical", "2 риска: скрытая индексация 25%", "Отклонено ИИ", "Открыть отчет", "primary"),
    ("Лицензионный_договор_ПО_v2.docx", "ООО «СофтЛаб Технологии»", "Лицензионный договор", "Безопасно (08%)", "safe", "0 рисков • Стандартная форма", "Готово к подписи", "Скачать резюме", "secondary")
]:
    tr = cmd("frame.create", {"parent": t_card["id"], "width": 1332, "height": 52, "props": {"fills": [], "stroke": tokens["light/border"], "strokeBottomWeight": 1, "layout": "horizontal", "padding": [0, 16, 0, 16], "crossAlign": "center", "sizingH": "fill"}})
    dc = cmd("frame.create", {"parent": tr["id"], "width": 380, "height": 45, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
    make_text(dc["id"], fname, font_size=13, font_style="Bold", fill=tokens["light/text-main"], width=360)
    make_text(dc["id"], counterpart, font_size=11, fill=tokens["light/text-muted"], width=360)
    make_text(tr["id"], dtype, font_size=12, fill=tokens["light/text-sec"], width=160)
    rc = cmd("frame.create", {"parent": tr["id"], "width": 180, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_badge(rc["id"], rlevel, rtype, "light", "compact")
    make_text(tr["id"], problems, font_size=12, fill=tokens["light/text-sec"], width=260)
    make_text(tr["id"], status, font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=150)
    ac = cmd("frame.create", {"parent": tr["id"], "width": 150, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_btn(ac["id"], action_text, btn_style, "light", "sm", width=135)


# =============================================================================
# SCREEN 3: 03_Processing_Light (x=3000, y=0)
# =============================================================================
print("\n[3/7] Сборка экрана 03_Processing_Light (Процесс анализа документа в реальном времени)...")
f3 = cmd("frame.create", {"name": "03_Processing_Light", "x": 3000, "y": 0, "width": 1440, "height": 960, "props": {"fill": tokens["light/bg"], "cornerRadius": 16, "clip": True}})
f3_id = f3["id"]
make_app_navbar(f3_id, "Договоры")

proc_center = cmd("frame.create", {
    "parent": f3_id, "x": 270, "y": 95, "width": 900, "height": 800,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 16, "layout": "vertical", "padding": 40, "gap": 22, "mainAlign": "center", "crossAlign": "center"
    }
})

# Pulsing Engine Icon Box
loader_icon = cmd("frame.create", {"parent": proc_center["id"], "width": 68, "height": 68, "props": {"fill": tokens["light/brand-tint"], "stroke": tokens["light/brand-bdr"], "strokeWeight": 2, "cornerRadius": 34, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
cmd("node.create", {"type": "text", "parent": loader_icon["id"], "text": "⚡", "props": {"fontSize": 30, "fill": tokens["brand/primary"]}})

make_text(proc_center["id"], "Выполняется глубокий ИИ-анализ договора...", font_size=22, font_style="Bold", fill=tokens["light/text-main"])
make_text(proc_center["id"], "Документ: Договор_поставки_станков_№48-2026.docx (8 страниц, 4 850 000 руб.)", font_size=13, fill=tokens["light/text-sec"])

# Progress Bar Container
pbar_wrap = cmd("frame.create", {"parent": proc_center["id"], "width": 820, "height": 10, "props": {"fill": tokens["light/border"], "cornerRadius": 5}})
pbar_fill = cmd("frame.create", {"parent": pbar_wrap["id"], "width": 672, "height": 10, "props": {"fill": tokens["brand/primary"], "cornerRadius": 5}})
if "brand/primary" in var_ids: bind(pbar_fill["id"], "fill", "brand/primary")

make_text(proc_center["id"], "Прогресс проверки: 82% • Расчетное время завершения: ~12 секунд", font_size=12, font_style="Bold", fill=tokens["brand/primary"])

# Stepper Timeline Items
steps_box = cmd("frame.create", {"parent": proc_center["id"], "width": 820, "height": 330, "props": {"fills": [], "layout": "vertical", "gap": 10}})
for s_icon, s_title, s_detail, s_badge, s_btype in [
    ("✓", "Извлечение текста, таблиц и реквизитов сторон", "Распознано 1 420 слов, 8 разделов, 2 подписанта", "Завершено", "safe"),
    ("✓", "Классификация договора и нормативный анализ ст. ГК РФ", "Сопоставление со ст. 333, 401, 421 ГК РФ (неустойка, форс-мажор)", "Завершено", "safe"),
    ("✓", "Проверка соответствия корпоративному Playbook ООО «ТехноСнаб»", "Выявлено 3 отклонения от утвержденных лимитов компании", "3 риска", "critical"),
    ("⟳", "Поиск логических противоречий между условиями договора", "Анализ конфликта сроков: п. 3.2 (5 дней) vs п. 6.4 (30 дней)...", "В процессе", "primary"),
    ("⏳", "Генерация юридически безопасных альтернативных формулировок", "Подготовка правок и редакции для протокола разногласий", "В очереди", "warning")
]:
    sitem = cmd("frame.create", {
        "parent": steps_box["id"], "width": 820, "height": 56,
        "props": {
            "fill": tokens["light/card-subtle"] if s_badge != "В процессе" else tokens["light/brand-tint"],
            "stroke": tokens["light/brand-bdr"] if s_badge == "В процессе" else tokens["light/border"],
            "strokeWeight": 1, "cornerRadius": 8, "layout": "horizontal", "padding": [0, 18, 0, 18], "crossAlign": "center", "gap": 14
        }
    })
    cmd("node.create", {"type": "text", "parent": sitem["id"], "text": s_icon, "props": {"fontSize": 14, "fontStyle": "Bold", "fill": tokens["brand/primary"] if s_badge == "В процессе" else (tokens["light/safe-txt"] if s_btype == "safe" else tokens["light/text-muted"])}})
    st_col = cmd("frame.create", {"parent": sitem["id"], "width": 620, "height": 42, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
    make_text(st_col["id"], s_title, font_size=12, font_style="Bold", fill=tokens["light/text-main"])
    make_text(st_col["id"], s_detail, font_size=11, fill=tokens["light/text-sec"])
    make_badge(sitem["id"], s_badge, s_btype, "light", "compact")

# Cancel Action & Security Pill
make_btn(proc_center["id"], "Отменить проверку", "ghost", "light", "sm", width=170)
make_badge(proc_center["id"], "🔒 Изолированный локальный контур (152-ФЗ)", "safe", "light", "compact")


# =============================================================================
# SCREEN 4: 04_Contract_Analysis_Light (x=4500, y=0)
# =============================================================================
print("\n[4/7] Сборка экрана 04_Contract_Analysis_Light (Детальный инспектор договора)...")
f4 = cmd("frame.create", {"name": "04_Contract_Analysis_Light", "x": 4500, "y": 0, "width": 1440, "height": 960, "props": {"fill": tokens["light/bg"], "cornerRadius": 16, "clip": True}})
f4_id = f4["id"]

# Sub-Navbar
v_nav = cmd("frame.create", {"parent": f4_id, "x": 0, "y": 0, "width": 1440, "height": 64, "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeBottomWeight": 1, "layout": "horizontal", "padding": [0, 32, 0, 32], "mainAlign": "spaceBetween", "crossAlign": "center"}})
vn_l = cmd("frame.create", {"parent": v_nav["id"], "props": {"fills": [], "layout": "horizontal", "gap": 16, "crossAlign": "center"}})
make_btn(vn_l["id"], "← К договорам", "secondary", "light", "sm", width=125)
make_text(vn_l["id"], "Договор_поставки_станков_№48-2026.docx", font_size=15, font_style="Bold", fill=tokens["light/text-main"])
make_badge(vn_l["id"], "Критический риск (78/100)", "critical", "light", "regular")

vn_r = cmd("frame.create", {"parent": v_nav["id"], "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
make_btn(vn_r["id"], "Экспорт в PDF", "secondary", "light", "sm", width=120)
make_btn(vn_r["id"], "Сформировать протокол", "primary", "light", "sm", width=200)

# Risk Executive Banner (Resilient multi-line height 80px)
ex_b = cmd("frame.create", {
    "parent": f4_id, "x": 32, "y": 80, "width": 1376, "height": 80,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1,
        "strokeLeftWeight": 4, "cornerRadius": 10,
        "layout": "horizontal", "padding": [14, 20, 14, 20], "crossAlign": "center", "gap": 16
    }
})
make_badge(ex_b["id"], "КРИТИЧЕСКИЙ РИСК", "critical", "light", "compact")
ex_txt = cmd("frame.create", {"parent": ex_b["id"], "width": 1150, "height": 52, "props": {"fills": [], "layout": "vertical", "gap": 3, "sizingH": "fill"}})
make_text(ex_txt["id"], "Резюме ИИ-аналитика: Не рекомендуется к подписанию без протокола разногласий", font_size=13, font_style="Bold", fill=tokens["light/crit-txt"], width=1140)
make_text(ex_txt["id"], "Выявлена скрытая неустойка 5%/день в п. 7.3 без ограничения ответственности и противоречие сроков оплаты между п. 3.2 (5 дней) и п. 6.4 (30 дней).", font_size=11, fill=tokens["light/text-sec"], width=1140)

sp = cmd("frame.create", {"parent": f4_id, "x": 32, "y": 172, "width": 1376, "height": 760, "props": {"fills": [], "layout": "horizontal", "gap": 18, "sizingH": "fixed"}})

# Left: Document Clause Viewer (Wrapped Clauses)
dv = cmd("frame.create", {"parent": sp["id"], "width": 640, "height": 760, "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 12, "sizingH": "fixed"}})
dv_h = cmd("frame.create", {"parent": dv["id"], "width": 600, "height": 26, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
make_text(dv_h["id"], "Текст договора (Страница 2 из 6)", font_size=13, font_style="Bold", fill=tokens["light/text-main"])
make_badge(dv_h["id"], "Подсветка активна", "primary", "light", "compact")

db = cmd("frame.create", {"parent": dv["id"], "width": 600, "height": 680, "props": {"fills": [], "layout": "vertical", "gap": 12, "sizingH": "fill"}})
make_text(db["id"], "3. ПОРЯДОК РАСЧЕТОВ И СТОИМОСТЬ", font_size=12, font_style="Bold", fill=tokens["light/text-main"])
make_text(db["id"], "3.1. Общая стоимость оборудования составляет 4 850 000 руб., вкл. НДС 20%.", font_size=12, fill=tokens["light/text-sec"], width=570)

# Clause 3.2 (Wrapped onto 2 lines, height 65)
p32 = cmd("frame.create", {
    "parent": db["id"], "width": 600, "height": 65,
    "props": {
        "fill": tokens["light/contra-bg"], "stroke": tokens["light/contra-bdr"], "strokeWeight": 1,
        "strokeLeftWeight": 3, "cornerRadius": 6,
        "layout": "vertical", "padding": [10, 12, 10, 12], "sizingH": "fill"
    }
})
make_text(p32["id"], "п. 3.2. Оплата производится Покупателем в течение 5 (пяти) банковских дней с даты счета Поставщика.", font_size=12, font_style="Bold", fill=tokens["light/contra-txt"], width=560)

make_text(db["id"], "4. УСЛОВИЯ И СРОКИ ПОСТАВКИ ТОВАРА\n4.1. Поставка осуществляется в течение 20 рабочих дней с момента аванса.", font_size=12, fill=tokens["light/text-sec"], width=570)

# Clause 6.4 (Wrapped onto 2 lines, height 65)
p64 = cmd("frame.create", {
    "parent": db["id"], "width": 600, "height": 65,
    "props": {
        "fill": tokens["light/contra-bg"], "stroke": tokens["light/contra-bdr"], "strokeWeight": 1,
        "strokeLeftWeight": 3, "cornerRadius": 6,
        "layout": "vertical", "padding": [10, 12, 10, 12], "sizingH": "fill"
    }
})
make_text(p64["id"], "п. 6.4. Окончательный расчет осуществляется в течение 30 календарных дней после подписания Акта.", font_size=12, font_style="Bold", fill=tokens["light/contra-txt"], width=560)

make_text(db["id"], "7. ОТВЕТСТВЕННОСТЬ СТОРОН", font_size=12, font_style="Bold", fill=tokens["light/text-main"])

# Clause 7.3 (Wrapped onto 3 lines, height 85)
p73 = cmd("frame.create", {
    "parent": db["id"], "width": 600, "height": 85,
    "props": {
        "fill": tokens["light/crit-bg"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1,
        "strokeLeftWeight": 4, "cornerRadius": 6,
        "layout": "vertical", "padding": [10, 12, 10, 12], "sizingH": "fill"
    }
})
make_text(p73["id"], "п. 7.3. В случае нарушения сроков поставки Поставщик уплачивает штраф 5% от суммы Договора за каждый день просрочки без ограничения предельной суммы.", font_size=12, font_style="Bold", fill=tokens["light/crit-txt"], width=560)

# Right: AI Inspector
insp = cmd("frame.create", {"parent": sp["id"], "width": 718, "height": 760, "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 18, "gap": 14, "sizingH": "fixed"}})
make_text(insp["id"], "Инспектор рисков и рекомендации ИИ", font_size=15, font_style="Bold", fill=tokens["light/text-main"])

t_tabs = cmd("frame.create", {"parent": insp["id"], "width": 682, "height": 32, "props": {"fills": [], "layout": "horizontal", "gap": 8, "sizingH": "fill"}})
make_badge(t_tabs["id"], "Все замечания (5)", "primary", "light", "regular")
make_badge(t_tabs["id"], "Критические риски (3)", "critical", "light", "regular")
make_badge(t_tabs["id"], "Коллизии пунктов (2)", "contradiction", "light", "regular")

# Risk Card 1 (Height 305px to comfortably fit all 2-line wraps)
rc1 = cmd("frame.create", {
    "parent": insp["id"], "width": 682, "height": 305,
    "props": {
        "fill": tokens["light/card-subtle"], "stroke": tokens["light/crit-bdr"], "strokeWeight": 1,
        "strokeLeftWeight": 4, "cornerRadius": 10,
        "layout": "vertical", "padding": 14, "gap": 8, "sizingH": "fill"
    }
})
rc1_h = cmd("frame.create", {"parent": rc1["id"], "width": 654, "height": 24, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
make_badge(rc1_h["id"], "КРИТИЧЕСКИЙ РИСК • п. 7.3", "critical", "light", "compact")
make_text(rc1_h["id"], "Оценка риска: 95/100", font_size=12, font_style="Bold", fill=tokens["light/crit-txt"])
make_text(rc1["id"], "Несоразмерная неустойка (5%/день) без ограничения ответственности", font_size=13, font_style="Bold", fill=tokens["light/text-main"], width=640)
make_text(rc1["id"], "Комментарий: Ставка 5%/день превышает среднерыночную в 50 раз (ст. 333 ГК РФ). При просрочке на 20 дней штраф превысит сумму всего оборудования.", font_size=11, fill=tokens["light/text-sec"], width=640)

# AI Safe Clause Quote Box (Height 85px)
ai_box = cmd("frame.create", {
    "parent": rc1["id"], "width": 654, "height": 85,
    "props": {
        "fill": tokens["light/brand-tint"], "stroke": tokens["light/brand-bdr"], "strokeWeight": 1,
        "strokeLeftWeight": 3, "cornerRadius": 6,
        "layout": "vertical", "padding": [8, 12, 8, 12], "gap": 4, "sizingH": "fill"
    }
})
make_text(ai_box["id"], "Безопасная редакция ИИ (для протокола разногласий):", font_size=11, font_style="Bold", fill=tokens["brand/primary"], width=620)
make_text(ai_box["id"], "«...пеня в размере 0.1% от стоимости непоставленного Товара за каждый день просрочки, но не более 10% от общей суммы Договора.»", font_size=11, fill=tokens["light/text-main"], width=620)

r_acts = cmd("frame.create", {"parent": rc1["id"], "width": 654, "height": 34, "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center", "sizingH": "fill"}})
make_btn(r_acts["id"], "Принять правку ИИ", "primary", "light", "sm", width=160)
make_btn(r_acts["id"], "Редактировать", "secondary", "light", "sm", width=125)
make_btn(r_acts["id"], "Отклонить", "danger", "light", "sm", width=100)

# Risk Card 2 (Contradiction, Height 155px)
rc2 = cmd("frame.create", {
    "parent": insp["id"], "width": 682, "height": 155,
    "props": {
        "fill": tokens["light/contra-bg"], "stroke": tokens["light/contra-bdr"], "strokeWeight": 1,
        "strokeLeftWeight": 3, "cornerRadius": 10,
        "layout": "vertical", "padding": 12, "gap": 6, "sizingH": "fill"
    }
})
rc2_h = cmd("frame.create", {"parent": rc2["id"], "width": 654, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
make_badge(rc2_h["id"], "КОЛЛИЗИЯ ПУНКТОВ • п. 3.2 vs п. 6.4", "contradiction", "light", "compact")
make_text(rc2_h["id"], "Сроки оплаты", font_size=11, font_style="Bold", fill=tokens["light/contra-txt"])
make_text(rc2["id"], "Внутреннее противоречие: п. 3.2 требует оплату за 5 дней, а п. 6.4 указывает 30 дней", font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=640)
make_text(rc2["id"], "Рекомендация: Синхронизировать единый срок окончательного расчета до 15 календарных дней.", font_size=11, fill=tokens["light/text-sec"], width=640)


# =============================================================================
# SCREEN 5: 05_Risk_Analytics_Light (x=0, y=1040)
# =============================================================================
print("\n[5/7] Сборка экрана 05_Risk_Analytics_Light (Аналитика рисков компании)...")
f5 = cmd("frame.create", {"name": "05_Risk_Analytics_Light", "x": 0, "y": 1040, "width": 1440, "height": 960, "props": {"fill": tokens["light/bg"], "cornerRadius": 16, "clip": True}})
f5_id = f5["id"]
make_app_navbar(f5_id, "Аналитика рисков")

body5 = cmd("frame.create", {"parent": f5_id, "name": "AnalyticsBody", "x": 36, "y": 88, "width": 1368, "height": 840, "props": {"fills": [], "layout": "vertical", "gap": 18, "sizingH": "fixed"}})

# Filter & Report Header
f5_bar = cmd("frame.create", {"parent": body5["id"], "width": 1368, "height": 45, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
make_text(f5_bar["id"], "Сводная аналитика рисков юридического департамента", font_size=18, font_style="Bold", fill=tokens["light/text-main"])
f5_r = cmd("frame.create", {"parent": f5_bar["id"], "props": {"fills": [], "layout": "horizontal", "gap": 10}})
make_btn(f5_r["id"], "Период: Октябрь 2026", "secondary", "light", "sm", width=180)
make_btn(f5_r["id"], "Экспорт отчета руководству", "primary", "light", "sm", width=220)

# 4 KPI cards (Archetype 1)
kpi_row5 = cmd("frame.create", {"parent": body5["id"], "width": 1368, "height": 95, "props": {"fills": [], "layout": "horizontal", "gap": 16, "sizingH": "fill"}})
for kt, kv, ks, ktype, top_color, badge_text in [
    ("Сэкономлено рабочих часов", "142 часа", "Равносильно 0.9 ставки юриста", "safe", tokens["brand/primary"], "Эффективность"),
    ("Предотвращено штрафов", "18.4 млн ₽", "По 14 договорам с неограниченным cap", "critical", tokens["light/crit-txt"], "Защита активов"),
    ("Устранено логических коллизий", "29 коллизий", "Исключен риск судебных споров по срокам", "contradiction", tokens["light/contra-txt"], "Коллизии"),
    ("Договоров без замечаний", "34% от общего числа", "Согласованы с первого раза без разногласий", "safe", tokens["light/safe-txt"], "Согласовано")
]:
    kc = cmd("frame.create", {
        "parent": kpi_row5["id"], "width": 330, "height": 95,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "strokeTopWeight": 3, "cornerRadius": 10, "layout": "vertical", "padding": [12, 16, 12, 16], "gap": 4, "sizingH": "fill"
        }
    })
    kc_top = cmd("frame.create", {"parent": kc["id"], "width": 298, "height": 18, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
    make_text(kc_top["id"], kt, font_size=11, fill=tokens["light/text-sec"])
    make_badge(kc_top["id"], badge_text, ktype, "light", "compact")
    make_text(kc["id"], kv, font_size=20, font_style="Bold", fill=top_color)
    make_text(kc["id"], ks, font_size=11, fill=tokens["light/text-muted"])

# 2 Charts Split row
charts_row = cmd("frame.create", {"parent": body5["id"], "width": 1368, "height": 380, "props": {"fills": [], "layout": "horizontal", "gap": 18, "sizingH": "fill"}})

# Left Chart: Risk Distribution by Category
c1 = cmd("frame.create", {
    "parent": charts_row["id"], "width": 675, "height": 380,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 16, "sizingH": "fill"
    }
})
make_text(c1["id"], "Распределение выявленных рисков по категориям", font_size=15, font_style="Bold", fill=tokens["light/text-main"])
bars_box = cmd("frame.create", {"parent": c1["id"], "width": 635, "height": 280, "props": {"fills": [], "layout": "vertical", "gap": 14}})
for cat_name, cat_pct, cat_count, cat_clr in [
    ("Неустойки и неограниченная ответственность (ст. 333 ГК РФ)", 42, "62 случая", tokens["light/crit-txt"]),
    ("Логические противоречия сроков и условий оплаты", 28, "41 случай", tokens["light/contra-txt"]),
    ("Неблагоприятная территориальная подсудность контрагента", 16, "24 случая", tokens["light/warn-txt"]),
    ("Одностороннее изменение цен и объемов поставки", 9, "13 случаев", tokens["light/warn-txt"]),
    ("Нарушение правил конфиденциальности и NDA", 5, "8 случаев", tokens["brand/primary"])
]:
    brow = cmd("frame.create", {"parent": bars_box["id"], "width": 635, "height": 40, "props": {"fills": [], "layout": "vertical", "gap": 4}})
    blbl = cmd("frame.create", {"parent": brow["id"], "width": 635, "height": 16, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween"}})
    make_text(blbl["id"], cat_name, font_size=12, font_style="Bold", fill=tokens["light/text-main"])
    make_text(blbl["id"], f"{cat_pct}% ({cat_count})", font_size=12, fill=tokens["light/text-sec"])
    bg_bar = cmd("frame.create", {"parent": brow["id"], "width": 635, "height": 8, "props": {"fill": tokens["light/card-subtle"], "cornerRadius": 4}})
    cmd("frame.create", {"parent": bg_bar["id"], "width": int(635 * cat_pct / 100), "height": 8, "props": {"fill": cat_clr, "cornerRadius": 4}})

# Right Chart: Weekly Volume & Speed
c2 = cmd("frame.create", {
    "parent": charts_row["id"], "width": 675, "height": 380,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 16, "sizingH": "fill"
    }
})
make_text(c2["id"], "Динамика проверок по дням недели и нагрузка юристов", font_size=15, font_style="Bold", fill=tokens["light/text-main"])
week_cols = cmd("frame.create", {"parent": c2["id"], "width": 635, "height": 220, "props": {"fills": [], "layout": "horizontal", "gap": 22, "mainAlign": "center", "crossAlign": "max"}})
for day_name, d_count, d_h in [("Пн", 28, 140), ("Вт", 36, 180), ("Ср", 32, 160), ("Чт", 40, 200), ("Пт", 24, 120), ("Сб", 6, 30), ("Вс", 2, 10)]:
    dcol = cmd("frame.create", {"parent": week_cols["id"], "width": 65, "height": 210, "props": {"fills": [], "layout": "vertical", "crossAlign": "center", "gap": 8, "mainAlign": "max"}})
    make_text(dcol["id"], str(d_count), font_size=12, font_style="Bold", fill=tokens["brand/primary"])
    bar_pillar = cmd("frame.create", {"parent": dcol["id"], "width": 44, "height": d_h, "props": {"fill": tokens["brand/primary"], "cornerRadius": [6, 6, 0, 0]}})
    if "brand/primary" in var_ids: bind(bar_pillar["id"], "fill", "brand/primary")
    make_text(dcol["id"], day_name, font_size=12, fill=tokens["light/text-sec"])

make_text(c2["id"], "Пиковая нагрузка: Четверг (40 договоров). Среднее время проверки стабильно < 1.4 мин.", font_size=12, fill=tokens["light/text-muted"])

# Bottom Table: Lawyers Workload
low_table = cmd("frame.create", {
    "parent": body5["id"], "width": 1368, "height": 260,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 12, "layout": "vertical", "padding": 18, "gap": 8, "sizingH": "fill"
    }
})
make_text(low_table["id"], "Эффективность команды юристов за текущий месяц", font_size=15, font_style="Bold", fill=tokens["light/text-main"])
lt_h = cmd("frame.create", {"parent": low_table["id"], "width": 1332, "height": 32, "props": {"fill": tokens["light/card-subtle"], "cornerRadius": 6, "layout": "horizontal", "padding": [0, 16, 0, 16], "crossAlign": "center"}})
for lt_t, lt_w in [("Сотрудник", 300), ("Роль", 200), ("Проверено договоров", 220), ("Принято правок ИИ", 220), ("Средняя оценка риска", 200), ("Статус нагрузки", 180)]:
    make_text(lt_h["id"], lt_t, font_size=12, font_style="Bold", fill=tokens["light/text-sec"], width=lt_w)

for emp_name, emp_role, emp_cnt, emp_accepted, emp_score, emp_status in [
    ("Алексей Смирнов", "Ведущий юрист (Поставки)", "74 договора", "92% правок принято", "Высокий риск (64%)", "Оптимальная (3.2 ч/день)"),
    ("Елена Васильева", "Юрист (Аренда и услуги)", "48 договоров", "88% правок принято", "Средний риск (38%)", "Оптимальная (2.1 ч/день)"),
    ("Михаил Рогов", "Младший юрист (NDA)", "26 договоров", "96% правок принято", "Низкий риск (18%)", "Доступен для задач")
]:
    ltr = cmd("frame.create", {"parent": low_table["id"], "width": 1332, "height": 45, "props": {"fills": [], "stroke": tokens["light/border"], "strokeBottomWeight": 1, "layout": "horizontal", "padding": [0, 16, 0, 16], "crossAlign": "center"}})
    make_text(ltr["id"], emp_name, font_size=13, font_style="Bold", fill=tokens["light/text-main"], width=300)
    make_text(ltr["id"], emp_role, font_size=12, fill=tokens["light/text-sec"], width=200)
    make_text(ltr["id"], emp_cnt, font_size=12, fill=tokens["light/text-main"], width=220)
    make_text(ltr["id"], emp_accepted, font_size=12, font_style="Bold", fill=tokens["light/safe-txt"], width=220)
    make_text(ltr["id"], emp_score, font_size=12, fill=tokens["light/text-sec"], width=200)
    make_text(ltr["id"], emp_status, font_size=12, fill=tokens["light/text-muted"], width=180)


# =============================================================================
# SCREEN 6: 06_Corporate_Playbook_Light (x=1500, y=1040)
# =============================================================================
print("\n[6/7] Сборка экрана 06_Corporate_Playbook_Light (Корпоративный Playbook)...")
f6 = cmd("frame.create", {"name": "06_Corporate_Playbook_Light", "x": 1500, "y": 1040, "width": 1440, "height": 960, "props": {"fill": tokens["light/bg"], "cornerRadius": 16, "clip": True}})
f6_id = f6["id"]
make_app_navbar(f6_id, "Корпоративный Playbook")

body6 = cmd("frame.create", {"parent": f6_id, "name": "PlaybookBody", "x": 36, "y": 88, "width": 1368, "height": 840, "props": {"fills": [], "layout": "vertical", "gap": 16, "sizingH": "fixed"}})

# Playbook Header with Actions
p_hdr = cmd("frame.create", {"parent": body6["id"], "width": 1368, "height": 45, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
make_text(p_hdr["id"], "Корпоративный Playbook: Правила и пороги проверки (ООО «ТехноСнаб»)", font_size=18, font_style="Bold", fill=tokens["light/text-main"])
p_hdr_r = cmd("frame.create", {"parent": p_hdr["id"], "props": {"fills": [], "layout": "horizontal", "gap": 12}})
make_btn(p_hdr_r["id"], "+ Создать новое правило", "primary", "light", "sm", width=195)
make_btn(p_hdr_r["id"], "Импорт из типового шаблона", "secondary", "light", "sm", width=220)

# Playbook Info Callout
p_callout = cmd("frame.create", {
    "parent": body6["id"], "width": 1368, "height": 68,
    "props": {
        "fill": tokens["light/brand-tint"], "stroke": tokens["light/brand-bdr"], "strokeWeight": 1,
        "strokeLeftWeight": 4, "cornerRadius": 8, "layout": "vertical", "padding": [12, 18, 12, 18], "gap": 3, "sizingH": "fill"
    }
})
make_text(p_callout["id"], "📌 Как Playbook управляет ИИ-анализом:", font_size=13, font_style="Bold", fill=tokens["brand/primary"])
make_text(p_callout["id"], "Любое отклонение входящего договора от утвержденных ниже порогов автоматически помечается как критический риск или предупреждение. ИИ автоматически предлагает корпоративную формулировку компании.", font_size=12, fill=tokens["light/text-sec"])

# Rules Cards List (Archetype 2/3/4 hybrids)
rules_container = cmd("frame.create", {"parent": body6["id"], "width": 1368, "height": 690, "props": {"fills": [], "layout": "vertical", "gap": 12, "sizingH": "fill"}})

rules_data = [
    ("RULE-01", "Ограничение размера неустойки за просрочку поставки", "Финансовая ответственность", "Пеня не более 0.1% в день, совокупный предел ответственности (Cap) строго не более 10% от суммы договора.", "«...не более 0.1% за каждый рабочий день просрочки, но не более 10% от общей суммы договора»", True, "critical", tokens["light/crit-txt"]),
    ("RULE-02", "Синхронизация сроков оплаты и исключение внутренних коллизий", "Логические противоречия", "Единый срок оплаты: не менее 15 банковских дней с момента подписания Акта приема-передачи (исключить оплату от счета).", "«...в течение 15 банковских дней с момента подписания Сторонами Акта сдачи-приемки»", True, "contradiction", tokens["light/contra-txt"]),
    ("RULE-03", "Территориальная подсудность споров", "Судебные риски", "Все споры подлежат рассмотрению исключительно в Арбитражном суде по месту нахождения Покупателя (г. Москва).", "«...в Арбитражном суде г. Москвы в соответствии с законодательством РФ»", True, "critical", tokens["light/crit-txt"]),
    ("RULE-04", "Обязательный досудебный претензионный порядок", "Регламент споров", "Срок рассмотрения претензии контрагентом должен составлять не более 15 календарных дней.", "«...претензия рассматривается Стороной в течение 15 календарных дней с момента получения»", True, "warning", tokens["light/warn-txt"]),
    ("RULE-05", "Запрет на одностороннее расторжение без компенсации", "Расторжение договора", "Контрагент не имеет права расторгнуть контракт во внесудебном порядке без возмещения документально подтвержденных убытков.", "«...расторжение допускается только по взаимному соглашению либо решению суда»", False, "warning", tokens["light/text-muted"])
]

for rid, rname, rcat, rcond, rsafe, ris_active, rbadge_type, rstripe_clr in rules_data:
    rcard = cmd("frame.create", {
        "parent": rules_container["id"], "name": f"Rule_{rid}", "width": 1368, "height": 118,
        "props": {
            "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
            "strokeLeftWeight": 4, "cornerRadius": 10, "layout": "horizontal", "padding": 16, "gap": 16, "crossAlign": "center", "sizingH": "fill"
        }
    })
    
    # Left Status Toggle
    t_col = cmd("frame.create", {"parent": rcard["id"], "width": 50, "height": 80, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "crossAlign": "center", "gap": 6}})
    tog_bg = cmd("frame.create", {
        "parent": t_col["id"], "width": 40, "height": 22,
        "props": {
            "fill": tokens["brand/primary"] if ris_active else tokens["light/card-subtle"],
            "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 11,
            "layout": "horizontal", "padding": 2, "mainAlign": "max" if ris_active else "min"
        }
    })
    cmd("frame.create", {"parent": tog_bg["id"], "width": 18, "height": 18, "props": {"fill": "#FFFFFF", "cornerRadius": 9}})
    make_text(t_col["id"], "ВКЛ" if ris_active else "ВЫКЛ", font_size=10, font_style="Bold", fill=tokens["brand/primary"] if ris_active else tokens["light/text-muted"])

    # Middle Content with clean wrapping
    m_col = cmd("frame.create", {"parent": rcard["id"], "width": 1080, "height": 88, "props": {"fills": [], "layout": "vertical", "gap": 4, "sizingH": "fill"}})
    m_top = cmd("frame.create", {"parent": m_col["id"], "width": 1080, "height": 24, "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
    make_text(m_top["id"], rid, font_size=12, font_style="Bold", fill=tokens["light/text-muted"])
    make_text(m_top["id"], rname, font_size=14, font_style="Bold", fill=tokens["light/text-main"])
    make_badge(m_top["id"], rcat, "primary", "light", "compact")
    make_badge(m_top["id"], "Критический" if rbadge_type == "critical" else ("Коллизия" if rbadge_type == "contradiction" else "Предупреждение"), rbadge_type, "light", "compact")

    make_text(m_col["id"], f"Условие правила: {rcond}", font_size=12, fill=tokens["light/text-sec"], width=1060)
    make_text(m_col["id"], f"Безопасная формулировка ИИ: {rsafe}", font_size=12, font_style="Bold", fill=tokens["brand/primary"], width=1060)

    # Right Action
    r_act = cmd("frame.create", {"parent": rcard["id"], "width": 150, "height": 80, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "crossAlign": "center", "gap": 8}})
    make_btn(r_act["id"], "Редактировать", "secondary", "light", "sm", width=135)


# =============================================================================
# SCREEN 7: 07_Team_Settings_Light (x=3000, y=1040)
# =============================================================================
print("\n[7/7] Сборка экрана 07_Team_Settings_Light (Команда и настройки)...")
f7 = cmd("frame.create", {"name": "07_Team_Settings_Light", "x": 3000, "y": 1040, "width": 1440, "height": 960, "props": {"fill": tokens["light/bg"], "cornerRadius": 16, "clip": True}})
f7_id = f7["id"]
make_app_navbar(f7_id, "Команда")

body7 = cmd("frame.create", {"parent": f7_id, "name": "ProfileBody", "x": 36, "y": 88, "width": 1368, "height": 840, "props": {"fills": [], "layout": "horizontal", "gap": 24, "sizingH": "fixed"}})

# Left Profile & Subscription Column (420px)
left_p = cmd("frame.create", {
    "parent": body7["id"], "width": 420, "height": 830,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 12, "layout": "vertical", "padding": 28, "gap": 18, "sizingH": "fixed"
    }
})

av_big = cmd("frame.create", {"parent": left_p["id"], "width": 76, "height": 76, "props": {"fill": tokens["light/brand-tint"], "stroke": tokens["light/brand-bdr"], "strokeWeight": 2, "cornerRadius": 38, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
make_text(av_big["id"], "АС", font_size=26, font_style="Bold", fill=tokens["brand/primary"])

make_text(left_p["id"], "Алексей Смирнов", font_size=20, font_style="Bold", fill=tokens["light/text-main"])
make_text(left_p["id"], "Ведущий юрисконсульт • ООО «ТехноСнаб»", font_size=13, fill=tokens["light/text-sec"])
make_badge(left_p["id"], "Роль: Проверяющий юрист (Editor)", "primary", "light", "regular")

cmd("frame.create", {"parent": left_p["id"], "width": 364, "height": 1, "props": {"fill": tokens["light/border"]}})

# Subscription Card
sub_box = cmd("frame.create", {
    "parent": left_p["id"], "width": 364, "height": 170,
    "props": {
        "fill": tokens["light/card-subtle"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": 16, "gap": 10
    }
})
make_text(sub_box["id"], "Тариф: Корпоративный SaaS", font_size=14, font_style="Bold", fill=tokens["light/text-main"])
make_text(sub_box["id"], "Использовано проверок: 148 из 500 в текущем месяце", font_size=12, fill=tokens["light/text-sec"])
sbar_bg = cmd("frame.create", {"parent": sub_box["id"], "width": 332, "height": 8, "props": {"fill": tokens["light/border"], "cornerRadius": 4}})
sbar_f = cmd("frame.create", {"parent": sbar_bg["id"], "width": int(332 * 148 / 500), "height": 8, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4}})
if "brand/primary" in var_ids: bind(sbar_f["id"], "fill", "brand/primary")

make_text(sub_box["id"], "Действует до 31 декабря 2026 г. • 5 рабочих мест юристов", font_size=11, fill=tokens["light/text-muted"])
make_btn(sub_box["id"], "Управление подпиской", "secondary", "light", "sm", width=332)

# Notifications Checkboxes
make_text(left_p["id"], "Уведомления и алерты:", font_size=14, font_style="Bold", fill=tokens["light/text-main"])
for n_txt in ["Email-уведомление сразу по готовности отчета", "SMS при обнаружении критического риска (>90%)", "Еженедельный сводный дайджест для руководства"]:
    nrow = cmd("frame.create", {"parent": left_p["id"], "width": 364, "height": 24, "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
    chk = cmd("frame.create", {"parent": nrow["id"], "width": 18, "height": 18, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
    cmd("node.create", {"type": "text", "parent": chk["id"], "text": "✓", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": "#FFFFFF"}})
    make_text(nrow["id"], n_txt, font_size=11, fill=tokens["light/text-sec"], width=330)

# Right Team & Access Control Column (924px)
right_p = cmd("frame.create", {
    "parent": body7["id"], "width": 924, "height": 830,
    "props": {
        "fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 12, "layout": "vertical", "padding": 28, "gap": 18, "sizingH": "fill"
    }
})

tp_hdr = cmd("frame.create", {"parent": right_p["id"], "width": 868, "height": 36, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
make_text(tp_hdr["id"], "Управление доступом команды (Портреты пользователей)", font_size=16, font_style="Bold", fill=tokens["light/text-main"])
make_btn(tp_hdr["id"], "+ Пригласить юриста", "primary", "light", "sm", width=180)

# Team Table
t_team = cmd("frame.create", {"parent": right_p["id"], "width": 868, "height": 310, "props": {"fills": [], "layout": "vertical", "gap": 8, "sizingH": "fill"}})
t_th7 = cmd("frame.create", {"parent": t_team["id"], "width": 868, "height": 32, "props": {"fill": tokens["light/card-subtle"], "cornerRadius": 6, "layout": "horizontal", "padding": [0, 16, 0, 16], "crossAlign": "center"}})
for tt_t, tt_w in [("Сотрудник", 260), ("Портрет из отчета", 180), ("Роль в системе", 180), ("Статус доступа", 140), ("Действие", 100)]:
    make_text(t_th7["id"], tt_t, font_size=12, font_style="Bold", fill=tokens["light/text-sec"], width=tt_w)

team_members = [
    ("Алексей Смирнов", "alexey.smirnov@technosnab.ru", "Алексей (50% ЦА) — практикующий юрист", "Editor / Аналитик", "Активен сейчас", "primary"),
    ("Ольга Николаева", "olga.nikolaeva@technosnab.ru", "Ольга (25% ЦА) — руководитель отдела", "Admin / Playbook Lead", "Активен", "secondary"),
    ("Дмитрий Ковалев", "dmitry.kovalev@technosnab.ru", "Дмитрий (25% ЦА) — закупки / директор", "Viewer / Executive", "Активен", "secondary"),
    ("Елена Васильева", "elena.vasilieva@technosnab.ru", "Юрисконсульт по недвижимости", "Editor / Аналитик", "Активен", "secondary")
]

for m_name, m_email, m_persona, m_role, m_status, m_btn in team_members:
    tm_row = cmd("frame.create", {"parent": t_team["id"], "width": 868, "height": 55, "props": {"fills": [], "stroke": tokens["light/border"], "strokeBottomWeight": 1, "layout": "horizontal", "padding": [0, 16, 0, 16], "crossAlign": "center"}})
    m_col = cmd("frame.create", {"parent": tm_row["id"], "width": 260, "height": 45, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
    make_text(m_col["id"], m_name, font_size=13, font_style="Bold", fill=tokens["light/text-main"])
    make_text(m_col["id"], m_email, font_size=11, fill=tokens["light/text-muted"])
    make_text(tm_row["id"], m_persona, font_size=12, fill=tokens["light/text-sec"], width=180)
    make_text(tm_row["id"], m_role, font_size=12, font_style="Bold", fill=tokens["light/text-main"], width=180)
    st_box = cmd("frame.create", {"parent": tm_row["id"], "width": 140, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_badge(st_box["id"], m_status, "safe", "light", "compact")
    act_box = cmd("frame.create", {"parent": tm_row["id"], "width": 100, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
    make_btn(act_box["id"], "Права", "secondary", "light", "sm", width=80)

# Security & Audit Log Card
sec_box = cmd("frame.create", {
    "parent": right_p["id"], "width": 868, "height": 260,
    "props": {
        "fill": tokens["light/card-subtle"], "stroke": tokens["light/border"], "strokeWeight": 1,
        "cornerRadius": 10, "layout": "vertical", "padding": 18, "gap": 10, "sizingH": "fill"
    }
})
make_text(sec_box["id"], "Безопасность и аудит доступа (Соответствие 152-ФЗ):", font_size=14, font_style="Bold", fill=tokens["light/text-main"])

sec_items = [
    ("Изолированный контур обработки", "Договоры обрабатываются в изолированной среде без сохранения в публичные облака.", "ВКЛЮЧЕНО"),
    ("Журнал действий пользователей (Audit Log)", "Фиксируются все загрузки, скачивания и принятые формулировки.", "ВЕДЕТСЯ"),
    ("Двухфакторная аутентификация (2FA)", "Обязательна для всех сотрудников юридического департамента.", "АКТИВНА")
]
for st, sd, ss in sec_items:
    srow = cmd("frame.create", {"parent": sec_box["id"], "width": 832, "height": 45, "props": {"fill": tokens["light/card"], "stroke": tokens["light/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 16, 0, 16], "crossAlign": "center", "mainAlign": "spaceBetween"}})
    sc_col = cmd("frame.create", {"parent": srow["id"], "props": {"fills": [], "layout": "vertical", "gap": 2}})
    make_text(sc_col["id"], st, font_size=12, font_style="Bold", fill=tokens["light/text-main"])
    make_text(sc_col["id"], sd, font_size=11, fill=tokens["light/text-sec"])
    make_badge(srow["id"], ss, "safe", "light", "compact")


# =============================================================================
# SAVE DIRECTLY IN OPEN FIGCRAFT
# =============================================================================
print("\n💾 Сохранение изменений в открытом проекте...")
save_res = cmd("file.save", {})
print("  Результат сохранения:", save_res)

# =============================================================================
# EXPORT HIGH-RES PNG RENDERS
# =============================================================================
print("\n📸 Экспорт обновленных PNG рендеров всех 7 экранов...")
exports = [
    ("screen_01_onboarding_light.png", f1_id),
    ("screen_02_dashboard_light.png", f2_id),
    ("screen_03_processing_light.png", f3_id),
    ("screen_04_analysis_light.png", f4_id),
    ("screen_05_analytics_light.png", f5_id),
    ("screen_06_playbook_light.png", f6_id),
    ("screen_07_team_light.png", f7_id)
]
for fn, fid in exports:
    p = os.path.join(EXPORT_DIR, fn)
    cmd("file.export", {"ids": [fid], "format": "png", "scale": 2, "path": p})
    print(f"  ✓ Экспортирован: {fn}")

s.close()
print("\n✨ ВСЕ 7 ЭКРАНОВ ПРОТОТИПА В СВЕТЛОЙ ТЕМЕ УСПЕШНО СОЗДАНЫ И ЭКСПОРТИРОВАНЫ!")
