#!/usr/bin/env python3
"""
LexAI — Pro Max Design System & Multi-Page UI Builder (FigCraft).
Built in accordance with UI/UX Pro Max and Design System Skill specifications:
- 3-Layer Token Engine (Primitive -> Semantic -> Component)
- Full Light & Dark Mode in Anthropic Warm Style
- Canonical sizing hierarchy (48/40/32px controls, 36/24/18/16/14/12px typography)
- Button States Matrix (Default, Hover, Active, Focus, Disabled)
- Form Input States (Default, Focus Ring, Error, Disabled)
- Semantic Status Badges & Vector Indicators (No emojis)
- 3 Separate Pages in FigCraft:
  Page 1: 🎨 Design System (Scale & Primitives)
  Page 2: 🌙 Screens — Dark Theme
  Page 3: ☀️ Screens — Light Theme
"""

import socket
import subprocess
import time
import json
import os
import sys

PORT = 9918
FIGCRAFT_BIN = "/Applications/FigCraft.app/Contents/MacOS/FigCraft"
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(WORKSPACE_DIR, "Legal_AI_Analyst.figcraft")
EXPORT_DIR = os.path.join(WORKSPACE_DIR, "renders")
os.makedirs(EXPORT_DIR, exist_ok=True)

print(f"🚀 Запуск FigCraft для генерации UI/UX Pro Max дизайн-системы (порт {PORT})...")
proc = subprocess.Popen([FIGCRAFT_BIN, "--control", str(PORT)])
time.sleep(2.0)

try:
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

    # 1. SETUP 3 MULTI-PAGES
    print("Создание 3 независимых страниц...")
    cmd("page.rename", {"name": "🎨 Design System (Scale & Primitives)"})
    cmd("page.add", {"name": "🌙 Screens — Dark Theme"})
    cmd("page.add", {"name": "☀️ Screens — Light Theme"})

    # 2. DESIGN TOKENS (Anthropic Warm Obsidian & Warm Linen)
    tokens = {
        # Brand Accent (Variable)
        "brand/primary": "#D97757",
        "brand/primary-hover": "#C26546",
        "brand/primary-active": "#AC5437",

        # Dark Mode Tokens (Warm Obsidian #141413)
        "dark/bg": "#141413",
        "dark/card": "#1C1C1A",
        "dark/card-subtle": "#232321",
        "dark/border": "#2E2E2A",
        "dark/border-focus": "#D97757",
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

        # Light Mode Tokens (Warm Linen #FAF9F5)
        "light/bg": "#FAF9F5",
        "light/card": "#FFFFFF",
        "light/card-subtle": "#F4F3ED",
        "light/border": "#E5E3D8",
        "light/border-focus": "#D97757",
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

    print("Регистрация глобальных переменных...")
    coll = cmd("variable.createCollection", {"name": "LexAI Tokens"})
    coll_id = coll["id"] if (coll and "id" in coll) else "c1"
    var_ids = {}
    for name, val in tokens.items():
        v = cmd("variable.create", {"collection": coll_id, "name": name, "type": "color", "value": val})
        if v and "id" in v:
            var_ids[name] = v["id"]

    def bind(node_id, field, var_name):
        if var_name in var_ids:
            cmd("variable.bind", {"ids": [node_id], "field": field, "variable": var_ids[var_name]})

    # UI HELPER: BUTTON COMPONENT
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
            if state == "hover":
                bg = tokens["brand/primary-hover"]
            elif state == "active":
                bg = tokens["brand/primary-active"]
            elif state == "disabled":
                opacity = 0.45
            elif state == "focus":
                stroke = tokens[f"{t_pre}/text-main"]
                stroke_w = 2
        elif variant == "secondary":
            bg = tokens[f"{t_pre}/card"]
            stroke = tokens[f"{t_pre}/border"]
            stroke_w = 1
            txt_c = tokens[f"{t_pre}/text-main"]
            if state == "hover":
                bg = tokens[f"{t_pre}/card-subtle"]
            elif state == "disabled":
                opacity = 0.45
            elif state == "focus":
                stroke = tokens["brand/primary"]
                stroke_w = 2
        elif variant == "outline":
            bg = None
            stroke = tokens[f"{t_pre}/border"]
            stroke_w = 1
            txt_c = tokens[f"{t_pre}/text-main"]
            if state == "disabled": opacity = 0.45
        elif variant == "danger":
            bg = tokens[f"{t_pre}/crit-bg"]
            stroke = tokens[f"{t_pre}/crit-bdr"]
            stroke_w = 1
            txt_c = tokens[f"{t_pre}/crit-txt"]
            if state == "disabled": opacity = 0.45
        elif variant == "success":
            bg = tokens[f"{t_pre}/safe-bg"]
            stroke = tokens[f"{t_pre}/safe-bdr"]
            stroke_w = 1
            txt_c = tokens[f"{t_pre}/safe-txt"]
            if state == "disabled": opacity = 0.45
        elif variant == "ghost":
            bg = None
            txt_c = tokens[f"{t_pre}/text-sec"]
            if state == "hover":
                bg = tokens[f"{t_pre}/card-subtle"]
                txt_c = tokens[f"{t_pre}/text-main"]
            elif state == "disabled": opacity = 0.45

        props = {
            "layout": "horizontal",
            "mainAlign": "center",
            "crossAlign": "center",
            "padding": [cfg["py"], cfg["px"], cfg["py"], cfg["px"]],
            "cornerRadius": cfg["r"],
            "opacity": opacity
        }
        if bg: props["fill"] = bg
        else: props["fills"] = []
        if stroke and stroke_w > 0:
            props["stroke"] = stroke
            props["strokeWeight"] = stroke_w

        f_args = {"parent": parent, "height": cfg["h"], "props": props}
        if width: f_args["width"] = width
        else: f_args["props"]["sizingH"] = "hug"

        b = cmd("frame.create", f_args)
        if variant == "primary" and state == "default" and "brand/primary" in var_ids:
            bind(b["id"], "fill", "brand/primary")
        t_props = {"fontSize": cfg["font"], "fontStyle": "Bold", "fill": txt_c}
        cmd("node.create", {"type": "text", "parent": b["id"], "text": text, "props": t_props})
        return b["id"]

    # UI HELPER: STATUS BADGE
    def make_badge(parent, text, btype="safe", theme="dark", size="regular", **kwargs):
        t_pre = "dark" if theme == "dark" else "light"
        cfg = {
            "regular": {"h": 26, "font": 12, "px": 10, "dot": 6},
            "compact": {"h": 20, "font": 10, "px": 7, "dot": 5}
        }.get(size, {"h": 26, "font": 12, "px": 10, "dot": 6})

        mapping = {
            "critical": (tokens[f"{t_pre}/crit-bg"], tokens[f"{t_pre}/crit-bdr"], tokens[f"{t_pre}/crit-txt"]),
            "contradiction": (tokens[f"{t_pre}/contra-bg"], tokens[f"{t_pre}/contra-bdr"], tokens[f"{t_pre}/contra-txt"]),
            "warning": (tokens[f"{t_pre}/warn-bg"], tokens[f"{t_pre}/warn-bdr"], tokens[f"{t_pre}/warn-txt"]),
            "safe": (tokens[f"{t_pre}/safe-bg"], tokens[f"{t_pre}/safe-bdr"], tokens[f"{t_pre}/safe-txt"]),
            "primary": (tokens[f"{t_pre}/brand-tint"], tokens[f"{t_pre}/brand-bdr"], tokens["brand/primary"])
        }
        bg, bdr, txt_c = mapping.get(btype, mapping["safe"])

        badge = cmd("frame.create", {
            "parent": parent,
            "height": cfg["h"],
            "props": {
                "fill": bg,
                "stroke": bdr,
                "strokeWeight": 1,
                "cornerRadius": 100,
                "layout": "horizontal",
                "padding": [0, cfg["px"], 0, cfg["px"]],
                "gap": 6,
                "crossAlign": "center",
                "sizingH": "hug"
            }
        })
        # Clean geometric indicator dot (no emojis!)
        dot = cmd("frame.create", {
            "parent": badge["id"],
            "width": cfg["dot"],
            "height": cfg["dot"],
            "props": {"fill": txt_c, "cornerRadius": cfg["dot"] // 2}
        })
        cmd("node.create", {
            "type": "text",
            "parent": badge["id"],
            "text": text,
            "props": {"fontSize": cfg["font"], "fontStyle": "Bold", "fill": txt_c}
        })
        return badge["id"]

    # =========================================================================
    # BUILD PAGE 1: 🎨 DESIGN SYSTEM (SCALE & PRIMITIVES)
    # =========================================================================
    print("Генерация Page 1: Каноническая дизайн-система...")
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
            "x": x_pos,
            "y": 0,
            "width": 1400,
            "height": 1720,
            "props": {"fill": bg_c, "cornerRadius": 16, "clip": True}
        })
        b_id = board["id"]

        # HEADER
        hdr = cmd("frame.create", {"parent": b_id, "x": 40, "y": 40, "width": 1320, "height": 75, "props": {"fills": [], "layout": "vertical", "gap": 6}})
        cmd("node.create", {"type": "text", "parent": hdr["id"], "text": f"LexAI Design System — {title_suffix}", "props": {"fontSize": 24, "fontStyle": "Bold", "fill": txt_m}})
        cmd("node.create", {"type": "text", "parent": hdr["id"], "text": "UI/UX Pro Max Architecture • 3-Layer Token Engine • Strict Scale Ladder (48/40/32px Controls, 36/24/18/16/14/12px Typography)", "props": {"fontSize": 13, "fill": txt_s}})

        # SECTION 1: TYPOGRAPHY SCALE (DISPLAY 36, H1 24, H2 18, BODY 16, SMALL 14, CAPTION 12)
        s_typo = cmd("frame.create", {"parent": b_id, "x": 40, "y": 130, "width": 1320, "height": 260, "props": {"fill": card_c, "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 10}})
        cmd("node.create", {"type": "text", "parent": s_typo["id"], "text": "1. Typography Scale Hierarchy", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": txt_m}})
        
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

        # SECTION 2: 3-LAYER COLOR TOKENS & CONTRAST
        s_colors = cmd("frame.create", {"parent": b_id, "x": 40, "y": 410, "width": 1320, "height": 160, "props": {"fill": card_c, "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 12}})
        cmd("node.create", {"type": "text", "parent": s_colors["id"], "text": "2. Color Tokens & Semantic Risk Roles (WCAG Contrast Verified)", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": txt_m}})
        
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
            c_chip = cmd("frame.create", {"parent": sw["id"], "width": 132, "height": 26, "props": {"fill": c_hex, "cornerRadius": 4, "sizingH": "fill"}})
            cmd("node.create", {"type": "text", "parent": sw["id"], "text": c_label, "props": {"fontSize": 11, "fontStyle": "Bold", "fill": txt_m}})
            cmd("node.create", {"type": "text", "parent": sw["id"], "text": f"{c_hex} • {c_contrast}", "props": {"fontSize": 10, "fill": txt_s}})

        # SECTION 3: BUTTONS MATRIX — SIZES & INTERACTIVE STATES (UI/UX PRO MAX SPEC)
        s_btns = cmd("frame.create", {"parent": b_id, "x": 40, "y": 590, "width": 1320, "height": 380, "props": {"fill": card_c, "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 14}})
        cmd("node.create", {"type": "text", "parent": s_btns["id"], "text": "3. Button Sizing Ladder & Interactive States Matrix", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": txt_m}})

        # Row 1: Sizes Ladder (48px Large, 40px Medium, 32px Small)
        cmd("node.create", {"type": "text", "parent": s_btns["id"], "text": "• SIZING LADDER (Large: 48px / Medium: 40px / Small: 32px)", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": txt_s}})
        row_sizes = cmd("frame.create", {"parent": s_btns["id"], "width": 1280, "height": 52, "props": {"fills": [], "layout": "horizontal", "gap": 16, "crossAlign": "center"}})
        make_btn(row_sizes["id"], "Large CTA (48px / Font 16px)", "primary", theme, "lg")
        make_btn(row_sizes["id"], "Medium Standard (40px / Font 14px)", "primary", theme, "md")
        make_btn(row_sizes["id"], "Small Compact (32px / Font 12px)", "primary", theme, "sm")

        # Row 2: Interactive States (Default, Hover, Active, Focus Ring 2px, Disabled)
        cmd("node.create", {"type": "text", "parent": s_btns["id"], "text": "• INTERACTIVE STATES (Default, Hover, Active, Focus Ring WCAG AAA, Disabled)", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": txt_s}})
        row_states = cmd("frame.create", {"parent": s_btns["id"], "width": 1280, "height": 44, "props": {"fills": [], "layout": "horizontal", "gap": 14, "crossAlign": "center"}})
        make_btn(row_states["id"], "Default State", "primary", theme, "md", state="default")
        make_btn(row_states["id"], "Hover State", "primary", theme, "md", state="hover")
        make_btn(row_states["id"], "Active / Pressed", "primary", theme, "md", state="active")
        make_btn(row_states["id"], "Focus (2px Ring)", "primary", theme, "md", state="focus")
        make_btn(row_states["id"], "Disabled State", "primary", theme, "md", state="disabled")

        # Row 3: Variants Ladder (Primary, Secondary, Outline, Danger, Success, Ghost)
        cmd("node.create", {"type": "text", "parent": s_btns["id"], "text": "• VARIANTS SPECTRUM (Primary, Secondary, Outline, Danger, Success, Ghost)", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": txt_s}})
        row_variants = cmd("frame.create", {"parent": s_btns["id"], "width": 1280, "height": 44, "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
        make_btn(row_variants["id"], "Primary Action", "primary", theme, "md")
        make_btn(row_variants["id"], "Secondary Action", "secondary", theme, "md")
        make_btn(row_variants["id"], "Outline Action", "outline", theme, "md")
        make_btn(row_variants["id"], "Danger / Reject", "danger", theme, "md")
        make_btn(row_variants["id"], "Success / Approve", "success", theme, "md")
        make_btn(row_variants["id"], "Ghost Action", "ghost", theme, "md")

        # SECTION 4: FORM INPUTS SCALE & INTERACTIVE STATES
        s_inputs = cmd("frame.create", {"parent": b_id, "x": 40, "y": 990, "width": 1320, "height": 250, "props": {"fill": card_c, "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 12}})
        cmd("node.create", {"type": "text", "parent": s_inputs["id"], "text": "4. Form Inputs Scale & Validation States (48px, 40px, 32px)", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": txt_m}})
        
        row_inp_sizes = cmd("frame.create", {"parent": s_inputs["id"], "width": 1280, "height": 52, "props": {"fills": [], "layout": "horizontal", "gap": 16, "crossAlign": "center"}})
        
        # 48px Input
        inp_lg = cmd("frame.create", {"parent": row_inp_sizes["id"], "width": 380, "height": 48, "props": {"fill": tokens[f"{t_pre}/card-subtle"], "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 8, "layout": "horizontal", "padding": [0, 16, 0, 16], "crossAlign": "center"}})
        cmd("node.create", {"type": "text", "parent": inp_lg["id"], "text": "Large Input (48px / Font 15px) — Поиск договоров...", "props": {"fontSize": 14, "fill": txt_s}})
        
        # 40px Input (Focus State with 2px Ring)
        inp_md = cmd("frame.create", {"parent": row_inp_sizes["id"], "width": 380, "height": 40, "props": {"fill": tokens[f"{t_pre}/card-subtle"], "stroke": tokens["brand/primary"], "strokeWeight": 2, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 14, 0, 14], "crossAlign": "center"}})
        cmd("node.create", {"type": "text", "parent": inp_md["id"], "text": "Medium Focus State (40px) — Активный ввод |", "props": {"fontSize": 13, "fill": txt_m}})

        # 32px Input
        inp_sm = cmd("frame.create", {"parent": row_inp_sizes["id"], "width": 380, "height": 32, "props": {"fill": tokens[f"{t_pre}/card-subtle"], "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 12, 0, 12], "crossAlign": "center"}})
        cmd("node.create", {"type": "text", "parent": inp_sm["id"], "text": "Small Input (32px) — Фильтр по дате", "props": {"fontSize": 12, "fill": txt_s}})

        # Controls Row (Error State, Switch, Checkbox)
        row_ctrls = cmd("frame.create", {"parent": s_inputs["id"], "width": 1280, "height": 55, "props": {"fills": [], "layout": "horizontal", "gap": 24, "crossAlign": "center"}})
        
        # Error Input
        inp_err_box = cmd("frame.create", {"parent": row_ctrls["id"], "width": 380, "height": 55, "props": {"fills": [], "layout": "vertical", "gap": 3}})
        inp_err = cmd("frame.create", {"parent": inp_err_box["id"], "width": 380, "height": 34, "props": {"fill": tokens[f"{t_pre}/crit-bg"], "stroke": tokens[f"{t_pre}/crit-bdr"], "strokeWeight": 1, "cornerRadius": 6, "layout": "horizontal", "padding": [0, 12, 0, 12], "crossAlign": "center"}})
        cmd("node.create", {"type": "text", "parent": inp_err["id"], "text": "Ошибочное значение неустойки", "props": {"fontSize": 12, "fill": tokens[f"{t_pre}/crit-txt"]}})
        cmd("node.create", {"type": "text", "parent": inp_err_box["id"], "text": "Недопустимый формат: ставка не может быть выше 10%", "props": {"fontSize": 10, "fill": tokens[f"{t_pre}/crit-txt"]}})

        # Toggle Switch (Interactive UI Spec)
        sw_wrap = cmd("frame.create", {"parent": row_ctrls["id"], "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center"}})
        sw_bg = cmd("frame.create", {"parent": sw_wrap["id"], "width": 44, "height": 24, "props": {"fill": tokens["brand/primary"], "cornerRadius": 12, "layout": "horizontal", "padding": 3, "mainAlign": "max", "crossAlign": "center"}})
        cmd("frame.create", {"parent": sw_bg["id"], "width": 18, "height": 18, "props": {"fill": "#FFFFFF", "cornerRadius": 9}})
        cmd("node.create", {"type": "text", "parent": sw_wrap["id"], "text": "Автоматическая замена формулировок ИИ", "props": {"fontSize": 13, "fill": txt_m}})

        # Checkbox
        cb_wrap = cmd("frame.create", {"parent": row_ctrls["id"], "props": {"fills": [], "layout": "horizontal", "gap": 8, "crossAlign": "center"}})
        cb_box = cmd("frame.create", {"parent": cb_wrap["id"], "width": 20, "height": 20, "props": {"fill": tokens["brand/primary"], "cornerRadius": 4, "layout": "horizontal", "mainAlign": "center", "crossAlign": "center"}})
        cmd("node.create", {"type": "text", "parent": cb_box["id"], "text": "✓", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": "#FFFFFF"}})
        cmd("node.create", {"type": "text", "parent": cb_wrap["id"], "text": "Проверка по ст. 333 ГК РФ", "props": {"fontSize": 13, "fill": txt_m}})

        # SECTION 5: STATUS BADGES LADDER (REGULAR 26px & COMPACT 20px)
        s_badges = cmd("frame.create", {"parent": b_id, "x": 40, "y": 1260, "width": 1320, "height": 170, "props": {"fill": card_c, "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 12}})
        cmd("node.create", {"type": "text", "parent": s_badges["id"], "text": "5. Status Indicators & Badges Scale (Regular 26px / Compact 20px — No Emojis)", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": txt_m}})
        
        b_row_reg = cmd("frame.create", {"parent": s_badges["id"], "width": 1280, "height": 30, "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
        cmd("node.create", {"type": "text", "parent": b_row_reg["id"], "text": "Regular (26px):", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": txt_mu, "width": 120}})
        make_badge(b_row_reg["id"], "Критический риск (78/100)", "critical", theme, "regular")
        make_badge(b_row_reg["id"], "Коллизия пунктов", "contradiction", theme, "regular")
        make_badge(b_row_reg["id"], "Требует внимания", "warning", theme, "regular")
        make_badge(b_row_reg["id"], "Полное соответствие", "safe", theme, "regular")
        make_badge(b_row_reg["id"], "Активный анализ ИИ", "primary", theme, "regular")

        b_row_comp = cmd("frame.create", {"parent": s_badges["id"], "width": 1280, "height": 24, "props": {"fills": [], "layout": "horizontal", "gap": 12, "crossAlign": "center"}})
        cmd("node.create", {"type": "text", "parent": b_row_comp["id"], "text": "Compact (20px):", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": txt_mu, "width": 120}})
        make_badge(b_row_comp["id"], "Критический (95%)", "critical", theme, "compact")
        make_badge(b_row_comp["id"], "Коллизия", "contradiction", theme, "compact")
        make_badge(b_row_comp["id"], "Внимание", "warning", theme, "compact")
        make_badge(b_row_comp["id"], "Норма", "safe", theme, "compact")

        # SECTION 6: BASIC CARD PRIMITIVES (CLEAN UNCOMPLICATED CONTAINERS)
        s_card = cmd("frame.create", {"parent": b_id, "x": 40, "y": 1450, "width": 1320, "height": 220, "props": {"fill": card_c, "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 12}})
        cmd("node.create", {"type": "text", "parent": s_card["id"], "text": "6. Standard Container & Card Primitives (Radius 12px, 1px Border, Subtle Elevation)", "props": {"fontSize": 14, "fontStyle": "Bold", "fill": txt_m}})
        
        cards_row = cmd("frame.create", {"parent": s_card["id"], "width": 1280, "height": 130, "props": {"fills": [], "layout": "horizontal", "gap": 16, "sizingH": "fill"}})
        for cd_title, cd_desc, cd_badge in [
            ("Standard Card", "Базовый контейнер со скруглением 12px, паддингом 16px и обводкой 1px.", "UI Container"),
            ("Elevated Subtle Card", "Карточка второго уровня вложенности для внутренних списков и таблиц реестра.", "Subtle Surface"),
            ("AI Highlight Banner", "Контейнер с мягким семантическим фоном для подсветки результатов работы ИИ.", "Intelligence Box")
        ]:
            card_p = cmd("frame.create", {"parent": cards_row["id"], "width": 416, "height": 130, "props": {"fill": tokens[f"{t_pre}/card-subtle"], "stroke": bdr_c, "strokeWeight": 1, "cornerRadius": 10, "layout": "vertical", "padding": [16, 18, 16, 18], "gap": 8, "sizingH": "fill"}})
            c_top = cmd("frame.create", {"parent": card_p["id"], "width": 380, "height": 24, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
            cmd("node.create", {"type": "text", "parent": c_top["id"], "text": cd_title, "props": {"fontSize": 13, "fontStyle": "Bold", "fill": txt_m}})
            make_badge(c_top["id"], cd_badge, "primary", theme, "compact")
            cmd("node.create", {"type": "text", "parent": card_p["id"], "text": cd_desc, "props": {"fontSize": 12, "fill": txt_s}})

        return b_id

    dark_ds_id = build_canonical_ds_board("dark", 0)
    light_ds_id = build_canonical_ds_board("light", 1460)

    # UI HELPER: SCREEN NAVBAR (CLEAN VECTOR LOGO, NO EMOJIS)
    def make_screen_navbar(parent, active_tab="Договоры", theme="dark"):
        t_pre = "dark" if theme == "dark" else "light"
        nav = cmd("frame.create", {
            "parent": parent,
            "name": "Navbar",
            "x": 0, "y": 0, "width": 1440, "height": 64,
            "props": {
                "fill": tokens[f"{t_pre}/card"],
                "stroke": tokens[f"{t_pre}/border"],
                "strokeBottomWeight": 1,
                "layout": "horizontal",
                "padding": [0, 36, 0, 36],
                "mainAlign": "spaceBetween",
                "crossAlign": "center"
            }
        })
        n_l = cmd("frame.create", {"parent": nav["id"], "props": {"fills": [], "layout": "horizontal", "gap": 36, "crossAlign": "center"}})
        
        # Clean Geometric Mark + Brand
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

    # UI HELPER: SCREEN 02 DASHBOARD (CLEAN UI/UX PRO MAX SPEC)
    def build_screen_dashboard(x=0, theme="dark"):
        t_pre = "dark" if theme == "dark" else "light"
        name_sfx = "Dark" if theme == "dark" else "Light"
        f_dash = cmd("frame.create", {"name": f"02_Dashboard_{name_sfx}", "x": x, "y": 0, "width": 1440, "height": 960, "props": {"fill": tokens[f"{t_pre}/bg"], "cornerRadius": 16, "clip": True}})
        fd_id = f_dash["id"]
        make_screen_navbar(fd_id, "Договоры", theme)

        d_body = cmd("frame.create", {"parent": fd_id, "x": 36, "y": 88, "width": 1368, "height": 840, "props": {"fills": [], "layout": "vertical", "gap": 20, "sizingH": "fixed"}})
        
        # KPI Row
        k_row = cmd("frame.create", {"parent": d_body["id"], "width": 1368, "height": 90, "props": {"fills": [], "layout": "horizontal", "gap": 16, "sizingH": "fill"}})
        for kt, kv, ks, ktype in [
            ("Проверено договоров", "148 шт.", "+18 за неделю", "safe"),
            ("Критических рисков", "38 условий", "Штрафы и ответственность", "critical"),
            ("Логических коллизий", "19 коллизий", "Несовпадение сроков", "contradiction"),
            ("Среднее время анализа", "1 мин 18 сек", "Норматив < 2 мин выполнен", "safe")
        ]:
            kc = cmd("frame.create", {"parent": k_row["id"], "width": 330, "height": 90, "props": {"fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeWeight": 1, "cornerRadius": 10, "layout": "vertical", "padding": [12, 16, 12, 16], "gap": 4, "sizingH": "fill"}})
            cmd("node.create", {"type": "text", "parent": kc["id"], "text": kt, "props": {"fontSize": 11, "fill": tokens[f"{t_pre}/text-sec"]}})
            clr = tokens["brand/primary"] if ktype == "safe" else (tokens[f"{t_pre}/crit-txt"] if ktype == "critical" else tokens[f"{t_pre}/contra-txt"])
            cmd("node.create", {"type": "text", "parent": kc["id"], "text": kv, "props": {"fontSize": 18, "fontStyle": "Bold", "fill": clr}})
            cmd("node.create", {"type": "text", "parent": kc["id"], "text": ks, "props": {"fontSize": 11, "fill": tokens[f"{t_pre}/text-muted"]}})

        # Upload Dropzone Card
        up = cmd("frame.create", {"parent": d_body["id"], "width": 1368, "height": 180, "props": {"fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 18, "gap": 12, "sizingH": "fill"}})
        cmd("node.create", {"type": "text", "parent": up["id"], "text": "Быстрая загрузка договора на проверку", "props": {"fontSize": 15, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
        
        dz = cmd("frame.create", {"parent": up["id"], "width": 1332, "height": 75, "props": {"fill": tokens[f"{t_pre}/card-subtle"], "stroke": tokens[f"{t_pre}/brand-bdr"], "strokeWeight": 1.5, "cornerRadius": 8, "layout": "vertical", "mainAlign": "center", "crossAlign": "center", "gap": 3, "sizingH": "fill"}})
        cmd("node.create", {"type": "text", "parent": dz["id"], "text": "Перетащите файл договора (PDF, DOCX до 50 МБ)", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": tokens["brand/primary"]}})
        cmd("node.create", {"type": "text", "parent": dz["id"], "text": "ИИ выполнит извлечение текста, проверку противоречий и сформирует альтернативные безопасные формулировки", "props": {"fontSize": 11, "fill": tokens[f"{t_pre}/text-sec"]}})
        
        up_acts = cmd("frame.create", {"parent": up["id"], "width": 1332, "height": 38, "props": {"fills": [], "layout": "horizontal", "gap": 14, "crossAlign": "center"}})
        make_btn(up_acts["id"], "Запустить анализ ИИ", "primary", theme, "md", width=190)
        make_btn(up_acts["id"], "Выбрать файл", "secondary", theme, "md", width=140)
        cmd("node.create", {"type": "text", "parent": up_acts["id"], "text": "Профиль: Строгий Playbook • База знаний: ГК РФ 2026", "props": {"fontSize": 12, "fill": tokens[f"{t_pre}/text-muted"]}})

        # Contracts Registry Table Card
        t_card = cmd("frame.create", {"parent": d_body["id"], "width": 1368, "height": 490, "props": {"fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 18, "gap": 10, "sizingH": "fill"}})
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

    # UI HELPER: SCREEN 04 CONTRACT ANALYSIS & AI INSPECTOR
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

        # Risk Banner (No emojis, clean vector alert pill)
        ex_b = cmd("frame.create", {"parent": fa_id, "x": 32, "y": 80, "width": 1376, "height": 68, "props": {"fill": tokens[f"{t_pre}/crit-bg"], "stroke": tokens[f"{t_pre}/crit-bdr"], "strokeWeight": 1, "cornerRadius": 10, "layout": "horizontal", "padding": [12, 18, 12, 18], "crossAlign": "center", "gap": 14}})
        make_badge(ex_b["id"], "КРИТИЧЕСКИЙ РИСК", "critical", theme, "compact")
        
        ex_txt = cmd("frame.create", {"parent": ex_b["id"], "width": 1180, "height": 44, "props": {"fills": [], "layout": "vertical", "gap": 2, "sizingH": "fill"}})
        cmd("node.create", {"type": "text", "parent": ex_txt["id"], "text": "Резюме ИИ-аналитика: Не рекомендуется к подписанию без протокола разногласий", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/crit-txt"]}})
        cmd("node.create", {"type": "text", "parent": ex_txt["id"], "text": "Выявлена скрытая неустойка 5%/день в п. 7.3 без ограничения ответственности и противоречие сроков оплаты между п. 3.2 (5 дней) и п. 6.4 (30 дней).", "props": {"fontSize": 11, "fill": tokens[f"{t_pre}/text-sec"]}})

        sp = cmd("frame.create", {"parent": fa_id, "x": 32, "y": 160, "width": 1376, "height": 770, "props": {"fills": [], "layout": "horizontal", "gap": 18, "sizingH": "fixed"}})
        
        # Left Panel: Document Clause Viewer
        dv = cmd("frame.create", {"parent": sp["id"], "width": 640, "height": 770, "props": {"fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 20, "gap": 12, "sizingH": "fixed"}})
        dv_h = cmd("frame.create", {"parent": dv["id"], "width": 600, "height": 26, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
        cmd("node.create", {"type": "text", "parent": dv_h["id"], "text": "Текст договора (Страница 2 из 6)", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
        make_badge(dv_h["id"], "Подсветка активна", "primary", theme, "compact")

        db = cmd("frame.create", {"parent": dv["id"], "width": 600, "height": 690, "props": {"fills": [], "layout": "vertical", "gap": 12, "sizingH": "fill"}})
        cmd("node.create", {"type": "text", "parent": db["id"], "text": "3. ПОРЯДОК РАСЧЕТОВ И СТОИМОСТЬ", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
        cmd("node.create", {"type": "text", "parent": db["id"], "text": "3.1. Общая стоимость оборудования составляет 4 850 000 руб., вкл. НДС 20%.", "props": {"fontSize": 12, "fill": tokens[f"{t_pre}/text-sec"]}})

        p32 = cmd("frame.create", {"parent": db["id"], "width": 600, "height": 55, "props": {"fill": tokens[f"{t_pre}/contra-bg"], "stroke": tokens[f"{t_pre}/contra-bdr"], "strokeWeight": 1, "cornerRadius": 6, "layout": "vertical", "padding": 8, "sizingH": "fill"}})
        cmd("node.create", {"type": "text", "parent": p32["id"], "text": "п. 3.2. Оплата производится Покупателем в течение 5 (пяти) банковских дней с даты счета Поставщика.", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/contra-txt"]}})

        cmd("node.create", {"type": "text", "parent": db["id"], "text": "4. УСЛОВИЯ И СРОКИ ПОСТАВКИ ТОВАРА\n4.1. Поставка осуществляется в течение 20 рабочих дней с момента аванса.", "props": {"fontSize": 12, "fill": tokens[f"{t_pre}/text-sec"]}})

        p64 = cmd("frame.create", {"parent": db["id"], "width": 600, "height": 60, "props": {"fill": tokens[f"{t_pre}/contra-bg"], "stroke": tokens[f"{t_pre}/contra-bdr"], "strokeWeight": 1, "cornerRadius": 6, "layout": "vertical", "padding": 8, "sizingH": "fill"}})
        cmd("node.create", {"type": "text", "parent": p64["id"], "text": "п. 6.4. Окончательный расчет осуществляется в течение 30 календарных дней после подписания Акта.", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/contra-txt"]}})

        cmd("node.create", {"type": "text", "parent": db["id"], "text": "7. ОТВЕТСТВЕННОСТЬ СТОРОН", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})

        p73 = cmd("frame.create", {"parent": db["id"], "width": 600, "height": 80, "props": {"fill": tokens[f"{t_pre}/crit-bg"], "stroke": tokens[f"{t_pre}/crit-bdr"], "strokeWeight": 1, "cornerRadius": 6, "layout": "vertical", "padding": 8, "sizingH": "fill"}})
        cmd("node.create", {"type": "text", "parent": p73["id"], "text": "п. 7.3. В случае нарушения сроков поставки Поставщик уплачивает штраф 5% от суммы Договора за каждый день просрочки без ограничения предельной суммы.", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/crit-txt"]}})

        # Right Panel: AI Risk Inspector
        insp = cmd("frame.create", {"parent": sp["id"], "width": 718, "height": 770, "props": {"fill": tokens[f"{t_pre}/card"], "stroke": tokens[f"{t_pre}/border"], "strokeWeight": 1, "cornerRadius": 12, "layout": "vertical", "padding": 18, "gap": 14, "sizingH": "fixed"}})
        cmd("node.create", {"type": "text", "parent": insp["id"], "text": "Инспектор рисков и рекомендации ИИ", "props": {"fontSize": 15, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
        
        t_tabs = cmd("frame.create", {"parent": insp["id"], "width": 682, "height": 32, "props": {"fills": [], "layout": "horizontal", "gap": 8, "sizingH": "fill"}})
        make_badge(t_tabs["id"], "Все замечания (5)", "primary", theme, "regular")
        make_badge(t_tabs["id"], "Критические риски (3)", "critical", theme, "regular")
        make_badge(t_tabs["id"], "Коллизии пунктов (2)", "contradiction", theme, "regular")

        rc1 = cmd("frame.create", {"parent": insp["id"], "width": 682, "height": 270, "props": {"fill": tokens[f"{t_pre}/card-subtle"], "stroke": tokens[f"{t_pre}/crit-bdr"], "strokeWeight": 1.5, "cornerRadius": 10, "layout": "vertical", "padding": 14, "gap": 8, "sizingH": "fill"}})
        rc1_h = cmd("frame.create", {"parent": rc1["id"], "width": 654, "height": 24, "props": {"fills": [], "layout": "horizontal", "mainAlign": "spaceBetween", "crossAlign": "center", "sizingH": "fill"}})
        make_badge(rc1_h["id"], "КРИТИЧЕСКИЙ РИСК • п. 7.3", "critical", theme, "compact")
        cmd("node.create", {"type": "text", "parent": rc1_h["id"], "text": "Оценка риска: 95/100", "props": {"fontSize": 12, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/crit-txt"]}})
        cmd("node.create", {"type": "text", "parent": rc1["id"], "text": "Несоразмерная неустойка (5%/день) без ограничения совокупной ответственности", "props": {"fontSize": 13, "fontStyle": "Bold", "fill": tokens[f"{t_pre}/text-main"]}})
        cmd("node.create", {"type": "text", "parent": rc1["id"], "text": "Комментарий: Ставка 5%/день превышает среднерыночную в 50 раз (ст. 333 ГК РФ). При просрочке на 20 дней штраф превысит сумму всего оборудования.", "props": {"fontSize": 11, "fill": tokens[f"{t_pre}/text-sec"]}})
        
        ai_box = cmd("frame.create", {"parent": rc1["id"], "width": 654, "height": 75, "props": {"fill": tokens[f"{t_pre}/brand-tint"], "stroke": tokens[f"{t_pre}/brand-bdr"], "strokeWeight": 1, "cornerRadius": 6, "layout": "vertical", "padding": 8, "gap": 3, "sizingH": "fill"}})
        cmd("node.create", {"type": "text", "parent": ai_box["id"], "text": "Безопасная редакция ИИ (рекомендуется для протокола разногласий):", "props": {"fontSize": 11, "fontStyle": "Bold", "fill": tokens["brand/primary"]}})
        cmd("node.create", {"type": "text", "parent": ai_box["id"], "text": "«...пеня в размере 0.1% от стоимости непоставленного Товара за каждый день просрочки, но не более 10% от общей суммы Договора.»", "props": {"fontSize": 11, "fill": tokens[f"{t_pre}/text-main"]}})

        r_acts = cmd("frame.create", {"parent": rc1["id"], "width": 654, "height": 34, "props": {"fills": [], "layout": "horizontal", "gap": 10, "crossAlign": "center", "sizingH": "fill"}})
        make_btn(r_acts["id"], "Принять правку ИИ", "primary", theme, "sm", width=160)
        make_btn(r_acts["id"], "Редактировать", "secondary", theme, "sm", width=120)
        make_btn(r_acts["id"], "Отклонить", "danger", theme, "sm", width=100)
        
        return fa_id

    # BUILD PAGE 2: 🌙 SCREENS — DARK THEME
    print("Генерация Page 2: Экраны (Dark Theme)...")
    cmd("page.select", {"index": 1})
    fdd_id = build_screen_dashboard(0, "dark")
    fad_id = build_screen_analysis(1500, "dark")

    # BUILD PAGE 3: ☀️ SCREENS — LIGHT THEME
    print("Генерация Page 3: Экраны (Light Theme)...")
    cmd("page.select", {"index": 2})
    fdl_id = build_screen_dashboard(0, "light")
    fal_id = build_screen_analysis(1500, "light")

    # SAVE AND EXPORT
    print(f"Сохранение проекта в {SAVE_PATH}...")
    cmd("file.saveAs", {"path": SAVE_PATH})

    print("Экспорт PNG рендеров высокого разрешения...")
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

    print("\n✨ UI/UX PRO MAX ДИЗАЙН-СИСТЕМА И МАКЕТЫ УСПЕШНО СОБРАНЫ!")

finally:
    proc.terminate()
