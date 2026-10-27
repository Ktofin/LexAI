#!/usr/bin/env python3
"""
LexAI — Live Container Revamp in Open FigCraft.
Connects directly to the user's open FigCraft on port 9897.
Replaces uniform generic cards with 5 distinct, purposeful container archetypes:
1. Stat / KPI Metric Card (3px colored top bar, hero number, trend pill)
2. Interactive Dropzone Upload (dashed border, format chips, centered drop target)
3. High-Priority Risk Alert (4px solid crimson left stripe, score gauge, legal basis)
4. AI Recommendation Quote Box (3px solid terracotta left stripe, diff quotation)
5. Logic Contradiction Dual Card (3px solid amethyst left stripe, ⇄ clause comparison)
"""

import socket
import json
import os
import sys

PORT = 9897
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(WORKSPACE_DIR, "Legal_AI_Analyst.figcraft")
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
    s.settimeout(12.0)
    while True:
        chunk = s.recv(16384)
        if not chunk: break
        buf += chunk
        if b"\n" in buf: break
    res = json.loads(buf.decode("utf-8"))
    if "error" in res and res["error"]:
        print(f"⚠️ Ошибка в {action}: {res['error']}")
    return res.get("result")

# 1. RETRIEVE EXISTING VARIABLES & PAGES
tokens = {
    "brand/primary": "#D97757",
    "brand/primary-hover": "#C26546",
    "brand/primary-active": "#AC5437",
    "dark/bg": "#141413",
    "dark/card": "#1C1C1A",
    "dark/card-subtle": "#232321",
    "dark/border": "#2E2E2A",
    "dark/text-main": "#FAF9F5",
    "dark/text-sec": "#B0AEA5",
    "dark/text-muted": "#73726C",
    "dark/brand-tint": "#2A1E19",
    "dark/brand-bdr": "#593627",
    "dark/crit-bg": "#2C1819",
    "dark/crit-bdr": "#5E2729",
    "dark/crit-txt": "#FF8587",
    "dark/contra-bg": "#231F33",
    "dark/contra-bdr": "#47396B",
    "dark/contra-txt": "#BDB4FE",
    "dark/warn-bg": "#2B2013",
    "dark/warn-bdr": "#573D1E",
    "dark/warn-txt": "#F6BF66",
    "dark/safe-bg": "#15241B",
    "dark/safe-bdr": "#274834",
    "dark/safe-txt": "#72D59A",
    "light/bg": "#FAF9F5",
    "light/card": "#FFFFFF",
    "light/card-subtle": "#F4F3ED",
    "light/border": "#E5E3D8",
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

# Helpers
def make_btn(parent, text, variant="primary", theme="dark", size="md", width=None, state="default", **kwargs):
    t_pre = "dark" if theme == "dark" else "light"
    cfg = {
        "lg": {"h": 48, "font": 16, "px": 24, "py": 12, "r": 8},
        "md": {"h": 40, "font": 14, "px": 18, "py": 10, "r": 6},
        "sm": {"h": 32, "font": 12, "px": 14, "py": 6,  "r": 6}
    }.get(size, {"h": 40, "font": 14, "px": 18, "py": 10, "r": 6})

    bg, stroke, stroke_w, txt_c, opacity = None, None, 0, tokens[f"{t_pre}/text-main"], 1.0
    if variant == "primary":
        bg = tokens["brand/primary"]
        txt_c = "#FFFFFF"
        if state == "hover": bg = tokens["brand/primary-hover"]
        elif state == "active": bg = tokens["brand/primary-active"]
        elif state == "disabled": opacity = 0.45
        elif state == "focus": stroke, stroke_w = tokens[f"{t_pre}/text-main"], 2
    elif variant == "secondary":
        bg, stroke, stroke_w = tokens[f"{t_pre}/card"], tokens[f"{t_pre}/border"], 1
        txt_c = tokens[f"{t_pre}/text-main"]
        if state == "hover": bg = tokens[f"{t_pre}/card-subtle"]
        elif state == "disabled": opacity = 0.45
        elif state == "focus": stroke, stroke_w = tokens["brand/primary"], 2
    elif variant == "outline":
        stroke, stroke_w, txt_c = tokens[f"{t_pre}/border"], 1, tokens[f"{t_pre}/text-main"]
        if state == "disabled": opacity = 0.45
    elif variant == "danger":
        bg, stroke, stroke_w, txt_c = tokens[f"{t_pre}/crit-bg"], tokens[f"{t_pre}/crit-bdr"], 1, tokens[f"{t_pre}/crit-txt"]
        if state == "disabled": opacity = 0.45
    elif variant == "success":
        bg, stroke, stroke_w, txt_c = tokens[f"{t_pre}/safe-bg"], tokens[f"{t_pre}/safe-bdr"], 1, tokens[f"{t_pre}/safe-txt"]
        if state == "disabled": opacity = 0.45
    elif variant == "ghost":
        txt_c = tokens[f"{t_pre}/text-sec"]
        if state == "hover": bg, txt_c = tokens[f"{t_pre}/card-subtle"], tokens[f"{t_pre}/text-main"]
        elif state == "disabled": opacity = 0.45

    props = {"layout": "horizontal", "mainAlign": "center", "crossAlign": "center", "padding": [cfg["py"], cfg["px"], cfg["py"], cfg["px"]], "cornerRadius": cfg["r"], "opacity": opacity}
    if bg: props["fill"] = bg
    else: props["fills"] = []
    if stroke and stroke_w > 0: props["stroke"], props["strokeWeight"] = stroke, stroke_w

    f_args = {"parent": parent, "height": cfg["h"], "props": props}
    if width: f_args["width"] = width
    else: f_args["props"]["sizingH"] = "hug"

    b = cmd("frame.create", f_args)
    if variant == "primary" and state == "default" and "brand/primary" in var_ids:
        bind(b["id"], "fill", "brand/primary")
    cmd("node.create", {"type": "text", "parent": b["id"], "text": text, "props": {"fontSize": cfg["font"], "fontStyle": "Bold", "fill": txt_c}})
    return b["id"]

def make_badge(parent, text, btype="safe", theme="dark", size="regular", **kwargs):
    t_pre = "dark" if theme == "dark" else "light"
    cfg = {"regular": {"h": 26, "font": 12, "px": 10, "dot": 6}, "compact": {"h": 20, "font": 10, "px": 7, "dot": 5}}.get(size, {"h": 26, "font": 12, "px": 10, "dot": 6})
    mapping = {
        "critical": (tokens[f"{t_pre}/crit-bg"], tokens[f"{t_pre}/crit-bdr"], tokens[f"{t_pre}/crit-txt"]),
        "contradiction": (tokens[f"{t_pre}/contra-bg"], tokens[f"{t_pre}/contra-bdr"], tokens[f"{t_pre}/contra-txt"]),
        "warning": (tokens[f"{t_pre}/warn-bg"], tokens[f"{t_pre}/warn-bdr"], tokens[f"{t_pre}/warn-txt"]),
        "safe": (tokens[f"{t_pre}/safe-bg"], tokens[f"{t_pre}/safe-bdr"], tokens[f"{t_pre}/safe-txt"]),
        "primary": (tokens[f"{t_pre}/brand-tint"], tokens[f"{t_pre}/brand-bdr"], tokens["brand/primary"])
    }
    bg, bdr, txt_c = mapping.get(btype, mapping["safe"])
    badge = cmd("frame.create", {
        "parent": parent, "height": cfg["h"],
        "props": {"fill": bg, "stroke": bdr, "strokeWeight": 1, "cornerRadius": 100, "layout": "horizontal", "padding": [0, cfg["px"], 0, cfg["px"]], "gap": 6, "crossAlign": "center", "sizingH": "hug"}
    })
    cmd("frame.create", {"parent": badge["id"], "width": cfg["dot"], "height": cfg["dot"], "props": {"fill": txt_c, "cornerRadius": cfg["dot"] // 2}})
    cmd("node.create", {"type": "text", "parent": badge["id"], "text": text, "props": {"fontSize": cfg["font"], "fontStyle": "Bold", "fill": txt_c}})
    return badge["id"]

# =============================================================================
# DELETE PREVIOUS ARTBOARDS ON THE 3 PAGES
# =============================================================================
print("Очистка старых макетов на страницах...")
for pid in [1, 2, 3]:
    p_info = cmd("node.get", {"id": pid})
    if p_info and "children" in p_info:
        child_ids = [c["id"] for c in p_info["children"]]
        if child_ids:
            cmd("edit.delete", {"ids": child_ids})
            print(f"  Удалены старые элементы на странице {pid}: {child_ids}")

# =============================================================================
# BUILD PAGE 1: 🎨 DESIGN SYSTEM (FEATURING 5 DISTINCT CONTAINER ARCHETYPES)
# =============================================================================
print("\nСборка Page 1: Дизайн-система с разнообразными типами контейнеров...")
cmd("page.select", {"index": 0})

def build_canonical_ds_board(theme="dark", x_pos=0):
    t_pre = "dark" if theme == "dark" else "light"
    bg_c = tokens[f"{t_pre}/bg"]
    card_c = tokens[f"{t_pre}/card"]
    bdr_c = tokens[f"{t_pre}/border"]
    txt_m = tokens[f"{t_pre}/text-main"]
    txt_s = tokens[f"{t_pre}/text-sec"]
    txt_mu = tokens[f"{t_pre}/text-muted"]

    title_suffix = "DARK MODE (Warm Obsidian #141413)" if theme == "dark" else "LIGHT MODE (Warm Linen #FAF9F5)"

    board = cmd("frame.create", {
        "name": f"DS_{theme.upper()}_CANONICAL",
        "x": x_pos, "y": 0, "width": 1400, "height": 1820,
        "props": {"fill": bg_c, "cornerRadius": 16, "clip": True}
    })
    b_id = board["id"]

    # Header
    hdr = cmd("frame.create", {"parent": b_id, "x": 40, "y": 40, "width": 1320, "height": 75, "props": {"fills": [], "layout": "vertical", "gap": 6}})
    cmd("node.create", {"type": "text", "parent": hdr["id"], "text": f"LexAI Design System — {title_suffix}", "props": {"fontSize": 24, "fontStyle": "Bold", "fill": txt_m}})
    cmd("node.create", {"type": "text", "parent": hdr["id"], "text": "UI/UX Pro Max Architecture • Distinct Container Archetypes • Sizing Scale Ladder (48/40/32px)", "props": {"fontSize": 13, "fill": txt_s}})

    # Section 1: Typography
    s_typo = cmd("frame.create", {"parent": b_id, "x": 40, "y": 130, "width": 1320, "height": 260, "props": {"fill": card_c, "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 10}})
    cmd("node.create", {"type": "text", "parent": s_typo["id"], "text": "1. Typography Scale Hierarchy (High Contrast)", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": txt_m}})
    t_scale_row = cmd("frame.create", {"parent": s_typo["id"], "width": 1280, "height": 195, "props": {"fills": [], "layout": "vertical", "gap": 8, "sizingH": "fill"}})
    for tag, fsize, fweight, desc, sample in [
        ("Display", 36, "Bold", "36px / Bold — Hero & Key Promos", "AI-Powered Legal Risk Intelligence"),
        ("Heading 1", 24, "Bold", "24px / Bold — Section Headers", "Реестр договоров и выявление правовых коллизий"),
        ("Heading 2", 18, "Bold", "18px / Bold — Cards & Modals", "Инспектор рисков и рекомендации ИИ"),
        ("Body Base", 16, "Regular", "16px / Regular — Contract Content", "В случае нарушения сроков поставки Поставщик уплачивает штраф..."),
        ("Small / UI", 14, "Regular", "14px / Regular — Table & UI Controls", "ООО «ПромМашСервис» • Договор поставки №48-2026"),
        ("Caption", 12, "Regular", "12px / Regular — Meta & Labels", "Статья 333 ГК РФ • Превышение ставки в 50 раз")
    ]:
        tr = cmd("frame.create", {"parent": t_scale_row["id"], "width": 1280, "height": 24, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center", "sizingH": "fill"}})
        cmd("node.create", {"type": "text", "parent": tr["id"], "text": f"{tag} ({desc})", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": txt_mu, "width": 320}})
        cmd("node.create", {"type": "text", "parent": tr["id"], "text": sample, "props": {"fontSize": min(fsize, 18), "fontStyle": fweight, "fill": txt_m}})

    # Section 2: Colors & Roles
    s_colors = cmd("frame.create", {"parent": b_id, "x": 40, "y": 410, "width": 1320, "height": 160, "props": {"fill": card_c, "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 12}})
    cmd("node.create", {"type": "text", "parent": s_colors["id"], "text": "2. Color Tokens & Semantic Risk Roles", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": txt_m}})
    c_row = cmd("frame.create", {"parent": s_colors["id"], "width": 1280, "height": 85, "props": {"fills": [], "layout": "horizontal", "gap": 12, "sizingH": "fill"}})
    for c_label, c_hex, c_role, c_contrast in [
        ("Brand Accent", tokens["brand/primary"], "brand/primary", "AA+"),
        ("Surface Bg", bg_c, f"{t_pre}/bg", "Base"),
        ("Card Surface", card_c, f"{t_pre}/card", "Base"),
        ("Border Line", bdr_c, f"{t_pre}/border", "1px"),
        ("Critical Risk", tokens[f"{t_pre}/crit-txt"], "Критические риски", "95/100"),
        ("Contradiction", tokens[f"{t_pre}/contra-txt"], "Коллизии пунктов", "п.3 vs п.6"),
        ("Warning Note", tokens[f"{t_pre}/warn-txt"], "Предупреждения", "Сроки"),
        ("Compliant Safe", tokens[f"{t_pre}/safe-txt"], "Полное соответствие", "100%")
    ]:
        sw = cmd("frame.create", {"parent": c_row["id"], "width": 148, "height": 85, "props": {"fill": tokens[f"{t_pre}/card-subtle"], "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 8, "layout": "vertical", "padding": 8, "gap": 4, "sizingH": "fill"}})
        cmd("frame.create", {"parent": sw["id"], "width": 132, "height": 26, "props": {"fill": c_hex, "cornerRadius": 4, "sizingH": "fill"}})
        cmd("node.create", {"type": "text", "parent": sw["id"], "text": c_label, "props": {"fontSize": 11, "fontStyle": "Bold", "fill": txt_m}})
        cmd("node.create", {"type": "text", "parent": sw["id"], "text": f"{c_hex} • {c_contrast}", "props": {"fontSize": 10, "fill": txt_s}})

    # Section 3: Buttons Matrix
    s_btns = cmd("frame.create", {"parent": b_id, "x": 40, "y": 590, "width": 1320, "height": 340, "props": {"fill": card_c, "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 12}})
    cmd("node.create", {"type": "text", "parent": s_btns["id"], "text": "3. Buttons Ladder & Interactive States Matrix (48px / 40px / 32px)", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": txt_m}})
    
    r_sizes = cmd("frame.create", {"parent": s_btns["id"], "width": 1280, "height": 52, "props": {"fills": [], "layout": "horizontal", "gap": 16, "crossAlign": "center"}})
    make_btn(r_sizes["id"], "Large CTA (48px / Font 16px)", "primary", theme, "lg")
    make_btn(r_sizes["id"], "Medium (40px / Font 14px)", "primary", theme, "md")
    make_btn(r_sizes["id"], "Small (32px / Font 12px)", "primary", theme, "sm")

    r_states = cmd("frame.create", {"parent": s_btns["id"], "width": 1280, "height": 44, "props": {"fills": [], "layout": "horizontal", "gap": 14, "crossAlign": "center"}})
    make_btn(r_states["id"], "Default State", "primary", theme, "md", state="default")
    make_btn(r_states["id"], "Hover State", "primary", theme, "md", state="hover")
    make_btn(r_states["id"], "Active / Pressed", "primary", theme, "md", state="active")
    make_btn(r_states["id"], "Focus (2px Ring)", "primary", theme, "md", state="focus")
    make_btn(r_states["id"], "Disabled", "primary", theme, "md", state="disabled")

    r_vars = cmd("frame.create", {"parent": s_btns["id"], "width": 1280, "height": 44, "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
    make_btn(r_vars["id"], "Primary Action", "primary", theme, "md")
    make_btn(r_vars["id"], "Secondary Action", "secondary", theme, "md")
    make_btn(r_vars["id"], "Outline Action", "outline", theme, "md")
    make_btn(r_vars["id"], "Danger / Reject", "danger", theme, "md")
    make_btn(r_vars["id"], "Success / Approve", "success", theme, "md")
    make_btn(r_vars["id"], "Ghost Action", "ghost", theme, "md")

    # Section 4: Form Inputs
    s_inputs = cmd("frame.create", {"parent": b_id, "x": 40, "y": 950, "width": 1320, "height": 220, "props": {"fill": card_c, "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 12}})
    cmd("node.create", {"type": "text", "parent": s_inputs["id"], "text": "4. Form Inputs Scale & Controls", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": txt_m}})
    r_inps = cmd("frame.create", {"parent": s_inputs["id"], "width": 1280, "height": 52, "props": {"fills": [], "layout": "horizontal", "gap": 16, "crossAlign": "center"}})
    
    inp_lg = cmd("frame.create", {"parent": r_inps["id"], "width": 380, "height": 48, "props": {"fill": tokens[f"{t_pre}/card-subtle"], "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 8, "layout": "horizontal", "padding": [0, 16, 0, 16], "crossAlign": "center"}})
    cmd("node.create", {"type": "text", "parent": inp_lg["id"], "text": "Large Input (48px) — Поиск договоров...", "props": {"fontSize": 14, "fill": txt_s}})
    
    inp_md = cmd("frame.create", {"parent": r_inps["id"], "width": 380, "height": 40, "props": {"fill": tokens[f"{t_pre}/card-subtle"], "stroke": tokens["brand/primary"], "strokeWeight": 2, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 14, 0, 14], "crossAlign": "center"}})
    cmd("node.create", {"type": "text", "parent": inp_md["id"], "text": "Medium Focus (40px) — Активный ввод |", "props": {"fontSize": 13, "fill": txt_m}})

    inp_sm = cmd("frame.create", {"parent": r_inps["id"], "width": 380, "height": 32, "props": {"fill": tokens[f"{t_pre}/card-subtle"], "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 12, 0, 12], "crossAlign": "center"}})
    cmd("node.create", {"type": "text", "parent": inp_sm["id"], "text": "Small Input (32px) — Фильтр по дате", "props": {"fontSize": 12, "fill": txt_s}})

    # Controls Row
    r_ctrl = cmd("frame.create", {"parent": s_inputs["id"], "width": 1280, "height": 50, "props": {"fills": [], "layout": "horizontal", "gap": 24, "crossAlign": "center"}})
    sw_wrap = cmd("frame.create", {"parent": r_ctrl["id"], "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
    sw_bg = cmd("frame.create", {"parent": sw_wrap["id"], "width": 44, "height": 24, "props": {"fill": tokens["brand/primary"], "cornerRadius": 12, "layout": "horizontal", "padding": 3, "mainAlign": "max", "crossAlign": "center"}})
    cmd("frame.create", {"parent": sw_bg["id"], "width": 18, "height": 18, "props": {"fill": "#FFFFFF", "cornerRadius": 9}})
    cmd("node.create", {"type": "text", "parent": sw_wrap["id"], "text": "Автоматическая замена формулировок ИИ", "props": {"fontSize": 13, "fill": txt_m}})

    cb_wrap = cmd("frame.create", {"parent": r_ctrl["id"], "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
    cb_box = cmd("frame.create", {"parent": cb_wrap["id"], "width": 20, "height": 20, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
    cmd("node.create", {"type": "text", "parent": cb_box["id"], "text": "✓", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": "#FFFFFF"}})
    cmd("node.create", {"type": "text", "parent": cb_wrap["id"], "text": "Проверка по ст. 333 ГК РФ", "props": {"fontSize": 13, "fill": txt_m}})

    # Section 5: Badges
    s_badges = cmd("frame.create", {"parent": b_id, "x": 40, "y": 1190, "width": 1320, "height": 150, "props": {"fill": card_c, "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 12}})
    cmd("node.create", {"type": "text", "parent": s_badges["id"], "text": "5. Status Indicators & Badges Scale (No Emojis)", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": txt_m}})
    b_row1 = cmd("frame.create", {"parent": s_badges["id"], "width": 1280, "height": 28, "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
    make_badge(b_row1["id"], "Критический риск (78/100)", "critical", theme, "regular")
    make_badge(b_row1["id"], "Коллизия пунктов", "contradiction", theme, "regular")
    make_badge(b_row1["id"], "Требует внимания", "warning", theme, "regular")
    make_badge(b_row1["id"], "Полное соответствие", "safe", theme, "regular")

    # =========================================================================
    # SECTION 6: THE 5 DISTINCT CONTAINER ARCHETYPES (REDESIGNED!)
    # =========================================================================
    s_cont = cmd("frame.create", {"parent": b_id, "x": 40, "y": 1360, "width": 1320, "height": 420, "props": {"fill": card_c, "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 16}})
    cmd("node.create", {"type": "text", "parent": s_cont["id"], "text": "6. Specialized Container & Card Primitives (5 Distinct Functional Archetypes)", "props": {"fontSize": 15, "fontStyle": "Bold", "fill": txt_m}})

    # Top Row: Archetype 1 (Stat Metric) & Archetype 2 (Risk Alert) & Archetype 3 (Contradiction)
    c_row_top = cmd("frame.create", {"parent": s_cont["id"], "width": 1280, "height": 160, "props": {"fills": [], "layout": "horizontal", "gap": 16, "sizingH": "fill"}})

    # 1. STAT / METRIC KPI CONTAINER (Distinct: 3px Top Colored Bar + Hero Number)
    c_stat = cmd("frame.create", {
        "parent": c_row_top["id"], "width": 380, "height": 160,
        "props": {
            "fill": tokens[f"{t_pre}/card-subtle"],
            "stroke": bdr_c, "strokeWeight": 1,
            "strokeTopWeight": 3,
            "cornerRadius": 10,
            "layout": "vertical", "padding": 16, "gap": 8, "sizingH": "fill"
        }
    })
    cmd("variable.bind", {"ids": [c_stat["id"]], "field": "stroke", "variable": var_ids["brand/primary"]}) if "brand/primary" in var_ids else None
    
    st_head = cmd("frame.create", {"parent": c_stat["id"], "width": 348, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
    cmd("node.create", {"type": "text", "parent": st_head["id"], "text": "АРХЕТИП 1: МЕТРИКА / KPI", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": txt_s}})
    make_badge(st_head["id"], "+18 за неделю", "safe", theme, "compact")
    cmd("node.create", {"type": "text", "parent": c_stat["id"], "text": "148 договоров", "props": {"fontSize": 26, "fontStyle": "Bold", "fill": tokens["brand/primary"]}})
    cmd("node.create", {"type": "text", "parent": c_stat["id"], "text": "Контейнер с 3px акцентной верхней полосой и крупным числом", "props": {"fontSize": 11, "fill": txt_mu}})

    # 2. HIGH-PRIORITY RISK ALERT CARD (Distinct: 4px Left Crimson Stripe + Threat Gauge)
    c_risk = cmd("frame.create", {
        "parent": c_row_top["id"], "width": 430, "height": 160,
        "props": {
            "fill": tokens[f"{t_pre}/crit-bg"],
            "stroke": tokens[f"{t_pre}/crit-bdr"], "strokeWeight": 1,
            "strokeLeftWeight": 4,
            "cornerRadius": 10,
            "layout": "vertical", "padding": 16, "gap": 6, "sizingH": "fill"
        }
    })
    rk_head = cmd("frame.create", {"parent": c_risk["id"], "width": 398, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
    make_badge(rk_head["id"], "КРИТИЧЕСКИЙ РИСК", "critical", theme, "compact")
    cmd("node.create", {"type": "text", "parent": rk_head["id"], "text": "Оценка: 95/100", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/crit-txt"]}})
    cmd("node.create", {"type": "text", "parent": c_risk["id"], "text": "АРХЕТИП 2: Карточка критической угрозы", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": txt_m}})
    cmd("node.create", {"type": "text", "parent": c_risk["id"], "text": "Выделенный левый бордер 4px, тревожный фон, ссылка на норму права (ст. 333 ГК РФ)", "props": {"fontSize": 11, "fill": txt_s}})

    # 3. LOGIC CONTRADICTION COMPARISON (Distinct: 3px Left Amethyst Stripe + Dual Item Diff)
    c_contra = cmd("frame.create", {
        "parent": c_row_top["id"], "width": 430, "height": 160,
        "props": {
            "fill": tokens[f"{t_pre}/contra-bg"],
            "stroke": tokens[f"{t_pre}/contra-bdr"], "strokeWeight": 1,
            "strokeLeftWeight": 3,
            "cornerRadius": 10,
            "layout": "vertical", "padding": 16, "gap": 6, "sizingH": "fill"
        }
    })
    co_head = cmd("frame.create", {"parent": c_contra["id"], "width": 398, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
    make_badge(co_head["id"], "КОЛЛИЗИЯ ПУНКТОВ", "contradiction", theme, "compact")
    cmd("node.create", {"type": "text", "parent": co_head["id"], "text": "Расхождение 25 дней", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/contra-txt"]}})
    cmd("node.create", {"type": "text", "parent": c_contra["id"], "text": "АРХЕТИП 3: Блок внутреннего противоречия", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": txt_m}})
    cmd("node.create", {"type": "text", "parent": c_contra["id"], "text": "п. 3.2 (оплата 5 дней) ⇄ п. 6.4 (оплата 30 дней) — прямое смысловое несоответствие", "props": {"fontSize": 11, "fill": txt_s}})

    # Bottom Row: Archetype 4 (AI Diff Quote) & Archetype 5 (Dropzone)
    c_row_bot = cmd("frame.create", {"parent": s_cont["id"], "width": 1280, "height": 170, "props": {"fills": [], "layout": "horizontal", "gap": 16, "sizingH": "fill"}})

    # 4. AI RECOMMENDATION QUOTE BOX (Distinct: 3px Left Terracotta Stripe + Quote Block)
    c_ai = cmd("frame.create", {
        "parent": c_row_bot["id"], "width": 630, "height": 170,
        "props": {
            "fill": tokens[f"{t_pre}/brand-tint"],
            "stroke": tokens[f"{t_pre}/brand-bdr"], "strokeWeight": 1,
            "strokeLeftWeight": 3,
            "cornerRadius": 10,
            "layout": "vertical", "padding": 16, "gap": 8, "sizingH": "fill"
        }
    })
    ai_h = cmd("frame.create", {"parent": c_ai["id"], "width": 598, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
    cmd("node.create", {"type": "text", "parent": ai_h["id"], "text": "АРХЕТИП 4: БЕЗОПАСНАЯ РЕДАКЦИЯ ИИ (DIFF QUOTE)", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": tokens["brand/primary"]}})
    make_badge(ai_h["id"], "Готово к протоколу", "primary", theme, "compact")
    
    q_box = cmd("frame.create", {"parent": c_ai["id"], "width": 598, "height": 50, "props": {"fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeWeight": 1, "cornerRadius": 6, "layout": "vertical", "padding": 10, "sizingH": "fill"}})
    cmd("node.create", {"type": "text", "parent": q_box["id"], "text": "«...пеня в размере 0.1% от стоимости непоставленного Товара, но не более 10%...»", "props": {"fontSize": 11, "fill": txt_m}})
    
    ai_acts = cmd("frame.create", {"parent": c_ai["id"], "width": 598, "height": 32, "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center", "sizingH": "fill"}})
    make_btn(ai_acts["id"], "Принять правку", "primary", theme, "sm", width=140)
    make_btn(ai_acts["id"], "Редактировать", "secondary", theme, "sm", width=120)

    # 5. INTERACTIVE DROPZONE CONTAINER (Distinct: 1.5px Dashed Border + File Chips)
    c_dz = cmd("frame.create", {
        "parent": c_row_bot["id"], "width": 630, "height": 170,
        "props": {
            "fill": tokens[f"{t_pre}/card-subtle"],
            "stroke": tokens[f"{t_pre}/brand-bdr"], "strokeWeight": 1.5,
            "cornerRadius": 10,
            "layout": "vertical", "mainAlign": "center", "crossAlign": "center", "padding": 16, "gap": 8, "sizingH": "fill"
        }
    })
    cmd("node.create", {"type": "text", "parent": c_dz["id"], "text": "АРХЕТИП 5: ИНТЕРАКТИВНАЯ ЗОНА ЗАГРУЗКИ", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": tokens["brand/primary"]}})
    cmd("node.create", {"type": "text", "parent": c_dz["id"], "text": "Перетащите договор для комплексной правовой проверки", "props": {"fontSize": 12, "fill": txt_s}})
    
    chips_row = cmd("frame.create", {"parent": c_dz["id"], "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
    for chip in [".PDF", ".DOCX", "до 50 МБ"]:
        cp = cmd("frame.create", {"parent": chips_row["id"], "props": {"fill": tokens[f"{t_pre}/card"], "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 4, "layout": "horizontal", "padding": [3, 8, 3, 8], "sizingH": "hug"}})
        cmd("node.create", {"type": "text", "parent": cp["id"], "text": chip, "props": {"fontSize": 10, "fontStyle": "Bold", "fill": txt_s}})

    return b_id

dark_ds_id = build_canonical_ds_board("dark", 0)
light_ds_id = build_canonical_ds_board("light", 1460)

# =============================================================================
# BUILD PAGE 2: 🌙 SCREENS — DARK THEME (WITH DISTINCT CONTAINERS)
# =============================================================================
print("\nСборка Page 2: Экраны в темной теме с обновленными контейнерами...")
cmd("page.select", {"index": 1})

def make_screen_navbar(parent, active_tab="Договоры", theme="dark"):
    t_pre = "dark" if theme == "dark" else "light"
    nav = cmd("frame.create", {
        "parent": parent, "name": "Navbar", "x": 0, "y": 0, "width": 1440, "height": 64,
        "props": {
            "fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeBottomWeight": 1,
            "layout": "horizontal", "padding": [0, 36, 0, 36], "mainAlign": "spaceBetween", "crossAlign": "center"
        }
    })
    n_l = cmd("frame.create", {"parent": nav["id"], "props": {"fills": [], "layout": "horizontal", "gap": 36, "crossAlign": "center"}})
    
    brand_box = cmd("frame.create", {"parent": n_l["id"], "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
    mark = cmd("frame.create", {"parent": brand_box["id"], "width": 18, "height": 18, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
    cmd("node.create", {"type": "text", "parent": mark["id"], "text": "§", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": "#FFFFFF"}})
    cmd("node.create", {"type": "text", "parent": brand_box["id"], "text": "LexAI Legal", "props": {"fontSize": 18, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
    
    n_links = cmd("frame.create", {"parent": n_l["id"], "props": {"fills": [], "layout": "horizontal", "gap": 24, "crossAlign": "center"}})
    for t in ["Договоры", "Аналитика рисков", "Корпоративный Playbook", "Команда"]:
        is_act = (t == active_tab)
        clr = tokens["brand/primary"] if is_act else tokens[f"{t_pre}/text-sec"]
        cmd("node.create", {"type": "text", "parent": n_links["id"], "text": t, "props": {"fontSize": 13, "fontStyle": "Bold" if is_act else "Regular", "fill": clr}})

    n_r = cmd("frame.create", {"parent": nav["id"], "props": {"fills": [], "layout": "horizontal", "gap": 16, "crossAlign": "center"}})
    cmd("node.create", {"type": "text", "parent": n_r["id"], "text": "Алексей Смирнов", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
    av = cmd("frame.create", {"parent": n_r["id"], "width": 34, "height": 34, "props": {"fill": tokens[f"{t_pre}/brand-tint"], "stroke": tokens[f"{t_pre}/brand-bdr"], "strokeWeight": 1, "cornerRadius": 17, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
    cmd("node.create", {"type": "text", "parent": av["id"], "text": "АС", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens["brand/primary"]}})
    return nav["id"]

def build_screen_dashboard(x=0, theme="dark"):
    t_pre = "dark" if theme == "dark" else "light"
    name_sfx = "Dark" if theme == "dark" else "Light"
    f_dash = cmd("frame.create", {"name": f"02_Dashboard_{name_sfx}", "x": x, "y": 0, "width": 1440, "height": 960, "props": {"fill": tokens[f"{t_pre}/bg"], "cornerRadius": 16, "clip": True}})
    fd_id = f_dash["id"]
    make_screen_navbar(fd_id, "Договоры", theme)

    d_body = cmd("frame.create", {"parent": fd_id, "x": 36, "y": 88, "width": 1368, "height": 840, "props": {"fills": [], "layout": "vertical", "gap": 20, "sizingH": "fixed"}})
    
    # 1. KPI ROW: DISTINCT METRIC CARDS WITH 3PX COLORED TOP BARS!
    k_row = cmd("frame.create", {"parent": d_body["id"], "width": 1368, "height": 95, "props": {"fills": [], "layout": "horizontal", "gap": 16, "sizingH": "fill"}})
    for kt, kv, ks, ktype, top_color, badge_text in [
        ("Проверено договоров", "148 шт.", "+18 за неделю", "safe", tokens["brand/primary"], "В норме"),
        ("Критических рисков", "38 условий", "Штрафы и неустойки", "critical", tokens[f"{t_pre}/crit-txt"], "Внимание"),
        ("Логических коллизий", "19 коллизий", "Несовпадение сроков", "contradiction", tokens[f"{t_pre}/contra-txt"], "Коллизии"),
        ("Среднее время анализа", "1 мин 18 сек", "Норматив < 2 мин", "safe", tokens[f"{t_pre}/safe-txt"], "Отлично")
    ]:
        kc = cmd("frame.create", {
            "parent": k_row["id"], "width": 330, "height": 95,
            "props": {
                "fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeWeight": 1,
                "strokeTopWeight": 3,
                "cornerRadius": 10, "layout": "vertical", "padding": [12, 16, 12, 16], "gap": 4, "sizingH": "fill"
            }
        })
        kc_top = cmd("frame.create", {"parent": kc["id"], "width": 298, "height": 18, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
        cmd("node.create", {"type": "text", "parent": kc_top["id"], "text": kt, "props": {"fontSize": 11, "fill": tokens[f"{t_pre}/text-sec"]}})
        make_badge(kc_top["id"], badge_text, ktype, theme, "compact")
        cmd("node.create", {"type": "text", "parent": kc["id"], "text": kv, "props": {"fontSize": 20, "fontStyle": "Bold", "fill": top_color}})
        cmd("node.create", {"type": "text", "parent": kc["id"], "text": ks, "props": {"fontSize": 11, "fill": tokens[f"{t_pre}/text-muted"]}})

    # 2. DROPZONE CONTAINER: DISTINCT DASHED BORDER & CENTERED TARGET
    up = cmd("frame.create", {
        "parent": d_body["id"], "width": 1368, "height": 175,
        "props": {
            "fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeWeight": 1,
            "cornerRadius": 12, "layout": "vertical", "padding": 18, "gap": 12, "sizingH": "fill"
        }
    })
    cmd("node.create", {"type": "text", "parent": up["id"], "text": "Быстрая загрузка договора на проверку", "props": {"fontSize": 15, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
    
    dz = cmd("frame.create", {
        "parent": up["id"], "width": 1332, "height": 72,
        "props": {
            "fill": tokens[f"{t_pre}/card-subtle"], "stroke": tokens[f"{t_pre}/brand-bdr"], "strokeWeight": 1.5,
            "cornerRadius": 8, "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "padding": [0, 24, 0, 24], "sizingH": "fill"
        }
    })
    dz_l = cmd("frame.create", {"parent": dz["id"], "props": {"fills": [], "layout": "vertical", "gap": 3}})
    cmd("node.create", {"type": "text", "parent": dz_l["id"], "text": "Перетащите файл договора для извлечения текста и проверки коллизий", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": tokens["brand/primary"]}})
    
    chips = cmd("frame.create", {"parent": dz_l["id"], "props": {"fills": [], "layout": "horizontal", "gap": 6, "crossAlign": "center"}})
    for c_txt in [".PDF", ".DOCX", "до 50 МБ"]:
        cp = cmd("frame.create", {"parent": chips["id"], "props": {"fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeWeight": 1, "cornerRadius": 4, "padding": [2, 6, 2, 6], "sizingH": "hug"}})
        cmd("node.create", {"type": "text", "parent": cp["id"], "text": c_txt, "props": {"fontSize": 10, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-sec"]}})

    dz_r = cmd("frame.create", {"parent": dz["id"], "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
    make_btn(dz_r["id"], "Запустить анализ ИИ", "primary", theme, "md", width=180)
    make_btn(dz_r["id"], "Выбрать файл", "secondary", theme, "md", width=130)

    # 3. REGISTRY TABLE CONTAINER: STRUCTURED TABLE CARD
    t_card = cmd("frame.create", {
        "parent": d_body["id"], "width": 1368, "height": 490,
        "props": {
            "fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeWeight": 1,
            "cornerRadius": 12, "layout": "vertical", "padding": 18, "gap": 10, "sizingH": "fill"
        }
    })
    t_hdr = cmd("frame.create", {"parent": t_card["id"], "width": 1332, "height": 28, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
    cmd("node.create", {"type": "text", "parent": t_hdr["id"], "text": "Реестр проверенных договоров", "props": {"fontSize": 15, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
    make_badge(t_hdr["id"], "Всего 148 документов", "safe", theme, "compact")

    t_th = cmd("frame.create", {"parent": t_card["id"], "width": 1332, "height": 34, "props": {"fill": tokens[f"{t_pre}/card-subtle"], "cornerRadius": 6, "layout": "horizontal", "padding": [0, 16, 0, 16], "crossAlign": "center", "sizingH": "fill"}})
    for tt, tw in [("Документ и контрагент", 380), ("Тип договора", 160), ("Уровень риска", 180), ("Выявленные замечания", 260), ("Статус проверки", 150), ("Действие", 150)]:
        cmd("node.create", {"type": "text", "parent": t_th["id"], "text": tt, "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-sec"], "width": tw}})

    for fname, counterpart, dtype, rlevel, rtype, problems, status, action_text, btn_style in [
        ("Договор_поставки_станков_№48-2026.docx", "ООО «ПромМашСервис»", "Поставка оборудования", "Критический (78%)", "critical", "3 риска • 2 коллизии сроков", "Требует правок", "Открыть отчет", "primary"),
        ("NDA_Соглашение_о_конфиденциальности.pdf", "ООО «ТехноПарк Групп»", "NDA / Соглашение", "Безопасно (12%)", "safe", "0 рисков • Соответствие норме", "Согласовано", "Скачать резюме", "secondary"),
        ("Договор_оказания_маркетинговых_услуг.docx", "ИП Соколов В.А.", "Возмездное оказание услуг", "Средний риск (42%)", "warning", "1 риск: короткий срок претензий", "На согласовании", "Смотреть правки", "primary"),
        ("Аренда_складского_помещения_Б-4.pdf", "АО «СеверЛогистик»", "Аренда коммерч. недвиж.", "Критический (65%)", "critical", "2 риска: скрытая индексация 25%", "Отклонено ИИ", "Открыть отчет", "primary"),
        ("Лицензионный_договор_ПО_v2.docx", "ООО «СофтЛаб Технологии»", "Лицензионный договор", "Безопасно (08%)", "safe", "0 рисков • Стандартная форма", "Готово к подписи", "Скачать резюме", "secondary")
    ]:
        tr = cmd("frame.create", {"parent": t_card["id"], "width": 1332, "height": 52, "props": {"fills": [], "stroke": tokens[f"{t_pre}/border"], "strokeBottomWeight": 1, "layout": "horizontal", "padding": [0, 16, 0, 16], "crossAlign": "center", "sizingH": "fill"}})
        dc = cmd("frame.create", {"parent": tr["id"], "width": 380, "height": 45, "props": {"fills": [], "layout": "vertical", "mainAlign": "center", "gap": 2}})
        cmd("node.create", {"type": "text", "parent": dc["id"], "text": fname, "props": {"fontSize": 13, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
        cmd("node.create", {"type": "text", "parent": dc["id"], "text": counterpart, "props": {"fontSize": 11, "fill": tokens[f"{t_pre}/text-muted"]}})
        cmd("node.create", {"type": "text", "parent": tr["id"], "text": dtype, "props": {"fontSize": 12, "fill": tokens[f"{t_pre}/text-sec"], "width": 160}})
        rc = cmd("frame.create", {"parent": tr["id"], "width": 180, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
        make_badge(rc["id"], rlevel, rtype, theme, "compact")
        cmd("node.create", {"type": "text", "parent": tr["id"], "text": problems, "props": {"fontSize": 12, "fill": tokens[f"{t_pre}/text-sec"], "width": 260}})
        cmd("node.create", {"type": "text", "parent": tr["id"], "text": status, "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"], "width": 150}})
        ac = cmd("frame.create", {"parent": tr["id"], "width": 150, "props": {"fills": [], "layout": "horizontal", "crossAlign": "center"}})
        make_btn(ac["id"], action_text, btn_style, theme, "sm", width=125)

    return fd_id

def build_screen_analysis(x=1500, theme="dark"):
    t_pre = "dark" if theme == "dark" else "light"
    name_sfx = "Dark" if theme == "dark" else "Light"
    f_anal = cmd("frame.create", {"name": f"04_Contract_Analysis_{name_sfx}", "x": x, "y": 0, "width": 1440, "height": 960, "props": {"fill": tokens[f"{t_pre}/bg"], "cornerRadius": 16, "clip": True}})
    fa_id = f_anal["id"]
    
    v_nav = cmd("frame.create", {"parent": fa_id, "x": 0, "y": 0, "width": 1440, "height": 64, "props": {"fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeBottomWeight": 1, "layout": "horizontal", "padding": [0, 32, 0, 32], "mainAlign": "spaceBetween", "crossAlign": "center"}})
    vn_l = cmd("frame.create", {"parent": v_nav["id"], "props": {"fills": [], "layout": "horizontal", "gap": 16, "crossAlign": "center"}})
    make_btn(vn_l["id"], "← К договорам", "secondary", theme, "sm", width=110)
    cmd("node.create", {"type": "text", "parent": vn_l["id"], "text": "Договор_поставки_станков_№48-2026.docx", "props": {"fontSize": 15, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
    make_badge(vn_l["id"], "Критический риск (78/100)", "critical", theme, "regular")
    
    vn_r = cmd("frame.create", {"parent": v_nav["id"], "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
    make_btn(vn_r["id"], "Экспорт в PDF", "secondary", theme, "sm", width=110)
    make_btn(vn_r["id"], "Сгенерировать протокол разногласий", "primary", theme, "sm", width=250)

    # 1. RISK BANNER: DISTINCT 4PX CRIMSON STRIPE
    ex_b = cmd("frame.create", {
        "parent": fa_id, "x": 32, "y": 80, "width": 1376, "height": 68,
        "props": {
            "fill": tokens[f"{t_pre}/crit-bg"], "stroke": tokens[f"{t_pre}/crit-bdr"], "strokeWeight": 1,
            "strokeLeftWeight": 4,
            "cornerRadius": 10, "layout": "horizontal", "padding": [12, 18, 12, 18], "crossAlign": "center", "gap": 14
        }
    })
    make_badge(ex_b["id"], "КРИТИЧЕСКИЙ РИСК", "critical", theme, "compact")
    ex_txt = cmd("frame.create", {"parent": ex_b["id"], "width": 1180, "height": 44, "props": {"fills": [], "layout": "vertical", "gap": 2, "sizingH": "fill"}})
    cmd("node.create", {"type": "text", "parent": ex_txt["id"], "text": "Резюме ИИ-аналитика: Не рекомендуется к подписанию без протокола разногласий", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/crit-txt"]}})
    cmd("node.create", {"type": "text", "parent": ex_txt["id"], "text": "Выявлена скрытая неустойка 5%/день в п. 7.3 без ограничения ответственности и противоречие сроков оплаты между п. 3.2 (5 дней) и п. 6.4 (30 дней).", "props": {"fontSize": 11, "fill": tokens[f"{t_pre}/text-sec"]}})

    sp = cmd("frame.create", {"parent": fa_id, "x": 32, "y": 160, "width": 1376, "height": 770, "props": {"fills": [], "layout": "horizontal", "gap": 18, "sizingH": "fixed"}})
    
    # 2. DOCUMENT CLAUSE VIEWER (LEFT)
    dv = cmd("frame.create", {"parent": sp["id"], "width": 640, "height": 770, "props": {"fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 12, "sizingH": "fixed"}})
    dv_h = cmd("frame.create", {"parent": dv["id"], "width": 600, "height": 26, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
    cmd("node.create", {"type": "text", "parent": dv_h["id"], "text": "Текст договора (Страница 2 из 6)", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
    make_badge(dv_h["id"], "Подсветка активна", "primary", theme, "compact")

    db = cmd("frame.create", {"parent": dv["id"], "width": 600, "height": 690, "props": {"fills": [], "layout": "vertical", "gap": 12, "sizingH": "fill"}})
    cmd("node.create", {"type": "text", "parent": db["id"], "text": "3. ПОРЯДОК РАСЧЕТОВ И СТОИМОСТЬ", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
    cmd("node.create", {"type": "text", "parent": db["id"], "text": "3.1. Общая стоимость оборудования составляет 4 850 000 руб., вкл. НДС 20%.", "props": {"fontSize": 12, "fill": tokens[f"{t_pre}/text-sec"]}})

    # Clause 3.2: Amethyst Left Stripe
    p32 = cmd("frame.create", {
        "parent": db["id"], "width": 600, "height": 55,
        "props": {
            "fill": tokens[f"{t_pre}/contra-bg"], "stroke": tokens[f"{t_pre}/contra-bdr"], "strokeWeight": 1,
            "strokeLeftWeight": 3,
            "cornerRadius": 6, "layout": "vertical", "padding": 8, "sizingH": "fill"
        }
    })
    cmd("node.create", {"type": "text", "parent": p32["id"], "text": "п. 3.2. Оплата производится Покупателем в течение 5 (пяти) банковских дней с даты счета Поставщика.", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/contra-txt"]}})

    cmd("node.create", {"type": "text", "parent": db["id"], "text": "4. УСЛОВИЯ И СРОКИ ПОСТАВКИ ТОВАРА\n4.1. Поставка осуществляется в течение 20 рабочих дней с момента аванса.", "props": {"fontSize": 12, "fill": tokens[f"{t_pre}/text-sec"]}})

    # Clause 6.4: Amethyst Left Stripe
    p64 = cmd("frame.create", {
        "parent": db["id"], "width": 600, "height": 60,
        "props": {
            "fill": tokens[f"{t_pre}/contra-bg"], "stroke": tokens[f"{t_pre}/contra-bdr"], "strokeWeight": 1,
            "strokeLeftWeight": 3,
            "cornerRadius": 6, "layout": "vertical", "padding": 8, "sizingH": "fill"
        }
    })
    cmd("node.create", {"type": "text", "parent": p64["id"], "text": "п. 6.4. Окончательный расчет осуществляется в течение 30 календарных дней после подписания Акта.", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/contra-txt"]}})

    cmd("node.create", {"type": "text", "parent": db["id"], "text": "7. ОТВЕТСТВЕННОСТЬ СТОРОН", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})

    # Clause 7.3: Crimson Left Stripe
    p73 = cmd("frame.create", {
        "parent": db["id"], "width": 600, "height": 80,
        "props": {
            "fill": tokens[f"{t_pre}/crit-bg"], "stroke": tokens[f"{t_pre}/crit-bdr"], "strokeWeight": 1,
            "strokeLeftWeight": 4,
            "cornerRadius": 6, "layout": "vertical", "padding": 8, "sizingH": "fill"
        }
    })
    cmd("node.create", {"type": "text", "parent": p73["id"], "text": "п. 7.3. В случае нарушения сроков поставки Поставщик уплачивает штраф 5% от суммы Договора за каждый день просрочки без ограничения предельной суммы.", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/crit-txt"]}})

    # 3. AI RISK INSPECTOR (RIGHT)
    insp = cmd("frame.create", {"parent": sp["id"], "width": 718, "height": 770, "props": {"fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 18, "gap": 14, "sizingH": "fixed"}})
    cmd("node.create", {"type": "text", "parent": insp["id"], "text": "Инспектор рисков и рекомендации ИИ", "props": {"fontSize": 15, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
    
    t_tabs = cmd("frame.create", {"parent": insp["id"], "width": 682, "height": 32, "props": {"fills": [], "layout": "horizontal", "gap": 8, "sizingH": "fill"}})
    make_badge(t_tabs["id"], "Все замечания (5)", "primary", theme, "regular")
    make_badge(t_tabs["id"], "Критические риски (3)", "critical", theme, "regular")
    make_badge(t_tabs["id"], "Коллизии пунктов (2)", "contradiction", theme, "regular")

    # Card 1: Critical Risk with 4px Crimson Left Stripe
    rc1 = cmd("frame.create", {
        "parent": insp["id"], "width": 682, "height": 280,
        "props": {
            "fill": tokens[f"{t_pre}/card-subtle"], "stroke": tokens[f"{t_pre}/crit-bdr"], "strokeWeight": 1,
            "strokeLeftWeight": 4,
            "cornerRadius": 10, "layout": "vertical", "padding": 14, "gap": 8, "sizingH": "fill"
        }
    })
    rc1_h = cmd("frame.create", {"parent": rc1["id"], "width": 654, "height": 24, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
    make_badge(rc1_h["id"], "КРИТИЧЕСКИЙ РИСК • п. 7.3", "critical", theme, "compact")
    cmd("node.create", {"type": "text", "parent": rc1_h["id"], "text": "Оценка риска: 95/100", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/crit-txt"]}})
    cmd("node.create", {"type": "text", "parent": rc1["id"], "text": "Несоразмерная неустойка (5%/день) без ограничения совокупной ответственности", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
    cmd("node.create", {"type": "text", "parent": rc1["id"], "text": "Комментарий: Ставка 5%/день превышает среднерыночную в 50 раз (ст. 333 ГК РФ). При просрочке на 20 дней штраф превысит сумму всего оборудования.", "props": {"fontSize": 11, "fill": tokens[f"{t_pre}/text-sec"]}})
    
    # AI Safe Recommendation Quote Box with 3px Terracotta Left Stripe
    ai_box = cmd("frame.create", {
        "parent": rc1["id"], "width": 654, "height": 75,
        "props": {
            "fill": tokens[f"{t_pre}/brand-tint"], "stroke": tokens[f"{t_pre}/brand-bdr"], "strokeWeight": 1,
            "strokeLeftWeight": 3,
            "cornerRadius": 6, "layout": "vertical", "padding": 8, "gap": 3, "sizingH": "fill"
        }
    })
    cmd("node.create", {"type": "text", "parent": ai_box["id"], "text": "Безопасная редакция ИИ (рекомендуется для протокола разногласий):", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": tokens["brand/primary"]}})
    cmd("node.create", {"type": "text", "parent": ai_box["id"], "text": "«...пеня в размере 0.1% от стоимости непоставленного Товара за каждый день просрочки, но не более 10% от общей суммы Договора.»", "props": {"fontSize": 11, "fill": tokens[f"{t_pre}/text-main"]}})

    r_acts = cmd("frame.create", {"parent": rc1["id"], "width": 654, "height": 34, "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center", "sizingH": "fill"}})
    make_btn(r_acts["id"], "Принять правку ИИ", "primary", theme, "sm", width=160)
    make_btn(r_acts["id"], "Редактировать", "secondary", theme, "sm", width=120)
    make_btn(r_acts["id"], "Отклонить", "danger", theme, "sm", width=100)

    # Card 2: Logic Contradiction with 3px Amethyst Left Stripe
    rc2 = cmd("frame.create", {
        "parent": insp["id"], "width": 682, "height": 140,
        "props": {
            "fill": tokens[f"{t_pre}/contra-bg"], "stroke": tokens[f"{t_pre}/contra-bdr"], "strokeWeight": 1,
            "strokeLeftWeight": 3,
            "cornerRadius": 10, "layout": "vertical", "padding": 12, "gap": 6, "sizingH": "fill"
        }
    })
    rc2_h = cmd("frame.create", {"parent": rc2["id"], "width": 654, "height": 22, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
    make_badge(rc2_h["id"], "КОЛЛИЗИЯ ПУНКТОВ • п. 3.2 vs п. 6.4", "contradiction", theme, "compact")
    cmd("node.create", {"type": "text", "parent": rc2_h["id"], "text": "Сроки оплаты", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/contra-txt"]}})
    cmd("node.create", {"type": "text", "parent": rc2["id"], "text": "Внутреннее противоречие: п. 3.2 требует оплату за 5 дней, а п. 6.4 указывает срок 30 дней", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
    cmd("node.create", {"type": "text", "parent": rc2["id"], "text": "Рекомендация: Унифицировать срок расчета до 15 календарных дней в обоих пунктах.", "props": {"fontSize": 11, "fill": tokens[f"{t_pre}/text-sec"]}})

    return fa_id

# Build Screens on Page 2 and Page 3
fdd_id = build_screen_dashboard(0, "dark")
fad_id = build_screen_analysis(1500, "dark")

print("\nСборка Page 3: Экраны в светлой теме с обновленными контейнерами...")
cmd("page.select", {"index": 2})
fdl_id = build_screen_dashboard(0, "light")
fal_id = build_screen_analysis(1500, "light")

# SAVE DIRECTLY IN OPEN FIGCRAFT
print("\n💾 Сохранение изменений в открытом проекте...")
save_res = cmd("file.save", {})
print("  Результат сохранения:", save_res)

# EXPORT HIGH-RES PNG RENDERS
print("\nЭкспорт обновленных PNG рендеров...")
exports = [
    ("ds_canonical_dark.png", dark_ds_id),
    ("ds_canonical_light.png", light_ds_id),
    ("screen_dashboard_dark.png", fdd_id),
    ("screen_analysis_dark.png", fad_id),
    ("screen_dashboard_light.png", fdl_id),
    ("screen_analysis_light.png", fal_id)
]
for fn, fid in exports:
    p = os.path.join(EXPORT_DIR, fn)
    cmd("file.export", {"ids": [fid], "format": "png", "scale": 2, "path": p})
    print(f"  ✓ Экспортирован: {fn}")

s.close()
print("\n✨ ВСЕ КОНТЕЙНЕРЫ УСПЕШНО ОБНОВЛЕНЫ ПРЯМО В ОТКРЫТОМ FIGCRAFT БЕЗ ПЕРЕЗАПУСКА!")
