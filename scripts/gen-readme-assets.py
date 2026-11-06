#!/usr/bin/env python3
"""README visuals for dsh-hs-classify — drawn from this plugin's real structure.

Two figures, both read off the shipped source and rule pack rather than a
generic pipeline template:

  hero 1440×576 (Pillow, four files: zh/en × light/dark)
      The ledger itself. The register header has no `tariffVersion`, row 1
      states a subheading of 847140 against a commodity code of 8471300000,
      row 2 repeats item number 1 and still carries a template placeholder.
      The code is then laid out as ten digit cells with four brackets — the
      chapter (2), heading (4) and subheading (6) are successive prefixes of
      the ten-digit code (HC-002), which is why the fifth digit is where the
      row breaks. Under it sit the two report channels: `issues[]` (four
      located differences) and `skipped[]` (HC-003, because the material has
      no `basis` column).

  flow 1100×660 (hand-written SVG, two files: light/dark)
      A staircase, not a row of boxes: the four levels of the code climb from
      chapter (2 digits) through heading (4) and subheading (6) to the full
      commodity code (10), with HC-002 on the three prefix levels and HC-001
      on the full code. The header field and the four non-code row fields sit
      in their own block; every item carries its outcome. The outcomes leave
      through two channels (`issues[]` and `skipped[]`) and are projected once
      by buildView() into markdown / reportJson. The quiet third outcome —
      executed, no difference, therefore in neither channel (HC-001) — is
      stated rather than hidden.

Sample values are taken from the repository's own contract and example:
  rules/hs-classify.yaml        HC-001 pattern ^[0-9]{10}$; HC-002 prefixOf
                                chapter/heading/subheading with digits 10;
                                HC-003 presence basis; HC-004 headerPresence
                                tariffVersion; HC-005 unique itemNo; HC-006
                                containsAny description
  src/model.ts                  column aliases (品名/商品编号/章/品目/子目…)
  src/shared/rows.ts            finding wording and the skipped reasons
  README.md                     the worked HC-002 example (847140 vs
                                8471300000, row 1, subheading)

Run:  python scripts/gen-readme-assets.py
Needs: Pillow, and the Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf /
       consolab.ttf. A missing font aborts instead of shipping tofu boxes.
"""
from __future__ import annotations

import math
import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

FONT_CJK = r"C:\Windows\Fonts\msyh.ttc"
FONT_CJK_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"
FONT_MONO_BOLD = r"C:\Windows\Fonts\consolab.ttf"
for _p in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO, FONT_MONO_BOLD):
    if not os.path.exists(_p):
        raise SystemExit(f"FATAL: font missing: {_p}")

RADIUS = 22
SHADOW = 26

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", card_edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent2="#16a34a",
        pill="#ece7f9", band="#f5f2fb", grid="#e7e4f0",
        mark="#b45309", mark_bg="#fdf3e9",
        shadow=(32, 26, 64), glow2="#7a68c9",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", card_edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent2="#3fb950",
        pill="#242d42", band="#202839", grid="#262f42",
        mark="#d9a441", mark_bg="#2a2216",
        shadow=(0, 0, 0), glow2="#8496f5",
    ),
}

FONT_FILES = {"cjk": FONT_CJK, "cjk_bold": FONT_CJK_BOLD,
              "mono": FONT_MONO, "mono_bold": FONT_MONO_BOLD}


def font(size: int, kind: str = "cjk_bold") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], size)


def hx(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(base)
    a, b = hx(c1), hx(c2)
    for y in range(h):
        t = 0.15 * (y / h) + 0.85 * (y / h) ** 1.35
        d.line([(0, y), (w, y)],
               fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color: tuple,
         alpha: int = 40) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(9, 0, -1):
        rr = r * i / 9
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (int(alpha * (1 - i / 10)),))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def card(img: Image.Image, box: tuple, s: dict, radius: int = RADIUS,
         shadow: int = SHADOW, fill: str | None = None) -> Image.Image:
    """A soft-shadowed rounded card on the gradient background."""
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -3):
        sd.rounded_rectangle([x0 - i // 5, y0 + i // 2, x1 + i // 5, y1 + i],
                             radius=radius + i // 5,
                             fill=s["shadow"] + (int(9 * (1 - i / shadow)),))
    base = Image.alpha_composite(img.convert("RGBA"),
                                 sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or s["card"]),
                        outline=hx(s["card_edge"]), width=2)
    return base.convert("RGB")


_SCRATCH = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: int, kind: str) -> float:
    return _SCRATCH.textlength(text, font=font(size, kind))


def require_w(text: str, size: int, kind: str, max_w: float, what: str) -> None:
    """Fail loudly instead of shipping a clipped label."""
    w = measure(text, size, kind)
    if w > max_w + 0.4:
        raise SystemExit(f"FATAL: {what} overflows: {text!r} needs "
                         f"{w:.1f}px > {max_w}px")


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    size = start
    while size > minimum:
        if measure(text, size, kind) <= max_w:
            return size
        size -= 1
    raise SystemExit(f"FATAL: text does not fit {max_w}px at >= {minimum}px: "
                     f"{text!r}")


def fit_lines(lines: list[str], kind: str, max_w: float, start: int,
              minimum: int) -> int:
    return min(fit(t, kind, max_w, start, minimum) for t in lines)


def pill(img: Image.Image, xy: tuple[int, int], text: str, s: dict,
         size: int = 16, fg: str | None = None, bg: str | None = None,
         kind: str = "cjk_bold") -> tuple[int, int]:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    h = size + 20
    d.rounded_rectangle([x, y, x + w + 30, y + h], radius=h // 2,
                        fill=hx(bg or s["pill"]))
    d.text((x + 15, y + h / 2), text, font=f, fill=hx(fg or s["accent"]),
           anchor="lm")
    return int(x + w + 30), int(y + h)


def chip(img: Image.Image, xy: tuple[int, int], text: str, fg: str, bg: str,
         size: int = 11, kind: str = "cjk_bold", padx: int = 9,
         height: int = 20) -> int:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    d.rounded_rectangle([x, y, x + w + padx * 2, y + height],
                        radius=height // 2, fill=hx(bg))
    d.text((x + padx, y + height / 2), text, font=f, fill=hx(fg), anchor="lm")
    return int(w + padx * 2)


def dash_rect(d: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
              color: str, width: int = 2, dash: int = 7, gap: int = 5) -> None:
    x0, y0, x1, y1 = box
    for a, b in (((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)),
                 ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))):
        dist = math.hypot(b[0] - a[0], b[1] - a[1])
        n = int(dist // (dash + gap)) + 1
        for i in range(n):
            t0 = i * (dash + gap) / dist
            t1 = min((i * (dash + gap) + dash) / dist, 1.0)
            if t0 >= 1:
                break
            d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                    (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)],
                   fill=hx(color), width=width)


# --------------------------------------------------------------------------- hero
# Values below are the real contract's own example, not invented data:
# row 1's subheading 847140 against code 8471300000, row 2's repeated item
# number 1 and 【待补充】 placeholder, and a header with no tariffVersion.
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 核对器",
        value=["十位编号拆成四级前缀，", "差异落到第几行、哪一栏。"],
        sub="只核对编号的结构自洽；不查税则、不下归类结论。",
        meta="HC-001..HC-006 · 规则库即数据 · skipped 逐条说明",
        foot="Apache-2.0 · PerryLink DSH plugin family",
        reg_title="台账 · 一行一项",
        reg_chip="只读原件",
        reg_head="表头：未声明 tariffVersion",
        headers=["品名", "章", "品目", "子目", "商品编号"],
        row1=["便携式自动数据处理设备", "84", "8471", "847140", "8471300000"],
        row2=["【待补充】", "84", "8471", "847130", "8471300000"],
        reg_note="列名忽略大小写、空格与下划线；原件永不修改",
        digits_title="商品编号 8471300000 · 十位数字",
        digits_chip="HC-001",
        brackets=["章 2 位", "品目 4 位", "子目 6 位 · 847140", "编号 10 位"],
        chan_issue="issues[] 4 条",
        chan_issue_line="HC-002 · 第 1 行 · subheading",
        chan_issue_detail="847140 不是 8471300000 的前缀",
        chan_skip="skipped[] 1 条",
        chan_skip_line="HC-003 · 材料没有「basis」列",
        chan_note="空 issues ≠ 没问题：先读 skipped",
        chan_verdict="结论留给审核人",
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · checker",
        value=["Ten digits, four prefix levels:", "each gap lands on a row and a cell"],
        sub="Structure only: no tariff lookup, no classification verdict.",
        meta="HC-001..HC-006 · rules are data · every skip explained",
        foot="Apache-2.0 · PerryLink DSH plugin family",
        reg_title="Register · one row per item",
        reg_chip="read-only",
        reg_head="Header: no tariffVersion declared",
        headers=["Item name", "Ch.", "Heading", "Subhead.", "Commodity code"],
        row1=["Portable ADP machine", "84", "8471", "847140", "8471300000"],
        row2=["[TBD]", "84", "8471", "847130", "8471300000"],
        reg_note="Column names ignore case and spacing; the original is never edited",
        digits_title="Commodity code 8471300000 · ten digits",
        digits_chip="HC-001",
        brackets=["Chapter · 2", "Heading · 4", "Subheading · 6 · 847140", "Code · 10"],
        chan_issue="issues[] 4",
        chan_issue_line="HC-002 · row 1 · subheading",
        chan_issue_detail="847140 is not a prefix of 8471300000",
        chan_skip="skipped[] 1",
        chan_skip_line="HC-003 · no basis column",
        chan_note="empty issues != no problem: read skipped",
        chan_verdict="verdict stays with the reviewer",
    ),
}


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    H = HERO[lang]
    W, HT = 1440, 576
    img = gradient(W, HT, s["bg_from"], s["bg_to"])
    img = glow(img, 1180, 30, 420, hx(s["accent"]),
               24 if skin == "light" else 38)
    img = glow(img, 90, 580, 300, hx(s["glow2"]),
               10 if skin == "light" else 16)

    d = ImageDraw.Draw(img)
    m = 64
    col_w = 596

    # ---- left column: kicker / title / value / sub / meta / footer ----------
    pill(img, (m, 54), H["kicker"], s, size=17)
    d = ImageDraw.Draw(img)

    title = "dsh-hs-classify"
    title_size = fit(title, "mono_bold", col_w, 58, 48)
    d.text((m - 2, 114), title, font=font(title_size, "mono_bold"),
           fill=hx(s["text"]))

    value_size = fit_lines(H["value"], "cjk_bold", col_w, 40, 33)
    for i, line in enumerate(H["value"]):
        require_w(line, value_size, "cjk_bold", col_w, "hero value")
        d.text((m, 204 + i * 54), line, font=font(value_size, "cjk_bold"),
               fill=hx(s["text"]))

    require_w(H["sub"], 20, "cjk", col_w, "hero sub")
    d.text((m + 1, 334), H["sub"], font=font(20, "cjk"), fill=hx(s["sub"]))

    require_w(H["meta"], 17, "cjk", col_w, "hero meta")
    require_w(H["foot"], 16, "cjk", col_w, "hero footer")
    d.text((m + 1, 412), H["meta"], font=font(17, "cjk"), fill=hx(s["faint"]))
    d.line([m + 1, 468, m + col_w - 4, 468], fill=hx(s["grid"]), width=2)
    d.text((m + 1, 482), H["foot"], font=font(16, "cjk"), fill=hx(s["faint"]))

    # ---- right: the register card -------------------------------------------
    img = card(img, (700, 40, 1376, 254), s, radius=RADIUS, shadow=SHADOW)
    d = ImageDraw.Draw(img)
    d.text((724, 58), H["reg_title"], font=font(17, "cjk_bold"),
           fill=hx(s["accent"]))
    cw = measure(H["reg_chip"], 11, "cjk")
    chip(img, (1352 - int(cw) - 18, 54), H["reg_chip"], s["accent"], s["pill"],
         size=11)
    d = ImageDraw.Draw(img)
    d.text((724, 90), H["reg_head"], font=font(12.5, "cjk"), fill=hx(s["mark"]))
    require_w(H["reg_head"], 12.5, "cjk", 560, "register header")

    xs = [724, 928, 978, 1046, 1132]
    widths = [196, 44, 64, 78, 170]
    top = 118
    d.rounded_rectangle([716, top, 1310, top + 28], radius=8,
                        fill=hx(s["band"]))
    for i, head in enumerate(H["headers"]):
        hs = 11.5
        require_w(head, hs, "cjk_bold", widths[i] - 8, "table header")
        d.text((xs[i] + 8, top + 7), head, font=font(hs, "cjk_bold"),
               fill=hx(s["sub"]))

    row_h = 34
    for r, row in enumerate((H["row1"], H["row2"])):
        ry = top + 28 + r * row_h
        for i, value in enumerate(row):
            if i == 0:
                f = font(12.5, "cjk")
                kind, size = "cjk", 12.5
            else:
                f = font(12.5, "mono")
                kind, size = "mono", 12.5
            fill = s["text"]
            if r == 0 and i == 3:
                fill = s["mark"]
            if r == 1 and i == 0:
                fill = s["mark"]
            require_w(value, size, kind, widths[i] - 10, "table cell")
            d.text((xs[i] + 8, ry + 10), value, font=f, fill=hx(fill))
        if r == 0:
            d.line([724, ry + row_h, 1300, ry + row_h], fill=hx(s["grid"]),
                   width=1)

    # the mismatching subheading cell, ringed
    cell = (1038, top + 32, 1128, top + 28 + row_h - 2)
    d.rounded_rectangle(cell, radius=8, fill=hx(s["mark_bg"]))
    dash_rect(d, cell, s["mark"], width=2, dash=6, gap=4)
    d.text((xs[3] + 8, top + 38), H["row1"][3], font=font(12.5, "mono"),
           fill=hx(s["mark"]))

    require_w(H["reg_note"], 11.5, "cjk", 620, "register note")
    d.text((724, 224), H["reg_note"], font=font(11.5, "cjk"),
           fill=hx(s["faint"]))

    # ---- right: the ten-digit strip with four prefix brackets ----------------
    img = card(img, (700, 266, 1376, 462), s, radius=RADIUS, shadow=SHADOW)
    d = ImageDraw.Draw(img)
    d.text((724, 282), H["digits_title"], font=font(13.5, "cjk_bold"),
           fill=hx(s["accent"]))
    require_w(H["digits_title"], 13.5, "cjk_bold", 530, "digits title")
    chip(img, (1352 - 8 - 48, 278), H["digits_chip"], s["accent"], s["pill"],
         size=11, height=19)
    d = ImageDraw.Draw(img)

    digit = "8471300000"
    cw_, gap_, cell_h = 52, 5, 56
    x0, y0 = 724, 318
    cs = [x0 + i * (cw_ + gap_) for i in range(10)]
    for i, ch in enumerate(digit):
        bad = (i == 4)
        box = (cs[i], y0, cs[i] + cw_, y0 + cell_h)
        d.rounded_rectangle(box, radius=9,
                            fill=hx(s["mark_bg"] if bad else s["band"]),
                            outline=hx(s["mark"] if bad else s["grid"]),
                            width=2 if bad else 1)
        d.text((cs[i] + cw_ / 2, y0 + cell_h / 2), ch,
               font=font(24, "mono_bold"),
               fill=hx(s["mark"] if bad else s["text"]), anchor="mm")
    # caret under the digit where the stated subheading diverges
    cx = cs[4] + cw_ / 2
    d.polygon([(cx - 6, 378), (cx + 6, 378), (cx, 384)], fill=hx(s["mark"]))

    spans = [2, 4, 6, 10]
    ys = [390, 409, 428, 447]
    for i, (span, by, label) in enumerate(zip(spans, ys, H["brackets"])):
        end = cs[span - 1] + cw_
        col = s["mark"] if i == 2 else s["accent"]
        d.line([cs[0], by, end, by], fill=hx(col), width=2)
        d.line([cs[0], by - 4, cs[0], by + 4], fill=hx(col), width=2)
        d.line([end, by - 4, end, by + 4], fill=hx(col), width=2)
        require_w(label, 11.5, "cjk", 1358 - (end + 8), "bracket label")
        d.text((end + 8, by - 8), label, font=font(11.5, "cjk"), fill=hx(col))

    # ---- right: the two report channels -------------------------------------
    img = card(img, (700, 474, 1376, 546), s, radius=18, shadow=18)
    d = ImageDraw.Draw(img)
    d.line([1020, 486, 1020, 534], fill=hx(s["grid"]), width=1)
    d.text((724, 486), H["chan_issue"], font=font(13, "cjk_bold"),
           fill=hx(s["accent"]))
    d.text((724, 506), H["chan_issue_line"], font=font(11, "cjk"),
           fill=hx(s["sub"]))
    d.text((724, 524), H["chan_issue_detail"], font=font(11.5, "cjk"),
           fill=hx(s["mark"]))
    for key, size, kind in (("chan_issue_line", 11, "cjk"),
                            ("chan_issue_detail", 11.5, "cjk")):
        require_w(H[key], size, kind, 280, f"channel {key}")

    d.text((1040, 486), H["chan_skip"], font=font(13, "cjk_bold"),
           fill=hx(s["sub"]))
    d.text((1040, 506), H["chan_skip_line"], font=font(11, "cjk"),
           fill=hx(s["sub"]))
    require_w(H["chan_skip_line"], 11, "cjk", 300, "skip channel line")
    require_w(H["chan_verdict"], 11.5, "cjk_bold", 312, "verdict")
    vw = measure(H["chan_verdict"], 11.5, "cjk_bold")
    d.text((1352 - vw, 524), H["chan_verdict"], font=font(11.5, "cjk_bold"),
           fill=hx(s["accent2"]))

    name = f"dsh-hs-classify-hero-{lang}-{skin}.webp"
    img.save(os.path.join(OUT, name), "WEBP", quality=92, method=6)
    print(f"wrote {name} ({W}×{HT})")


# --------------------------------------------------------------------------- flow
FLOW = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        panel="#ffffff", edge="#e6e2ef", band="#f5f2fb", band_alt="#faf8fe",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent2="#16a34a", mark="#b45309",
        mark_bg="#fdf3e9", rule="#dcd8ea", chip="#ece7f9",
        shadow="0.10",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        panel="#1b2231", edge="#2e374b", band="#202839", band_alt="#1e2534",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent2="#3fb950", mark="#d9a441",
        mark_bg="#2a2216", rule="#2b3348", chip="#242d42",
        shadow="0.45",
    ),
}

FONT_CSS_CJK = ("'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',"
                "'Source Han Sans SC',sans-serif")
FONT_CSS_MONO = ("'Consolas','SFMono-Regular','Menlo',ui-monospace,monospace")

# level, canonical field, stated value, digits covered, rule, ok?
LEVELS = [
    ("商品编号", "hsCode", "8471300000", "10 位", "HC-001", True),
    ("子目", "subheading", "847140", "前 6 位", "HC-002", False),
    ("品目", "heading", "8471", "前 4 位", "HC-002", True),
    ("章", "chapter", "84", "前 2 位", "HC-002", True),
]

# rule id, where it reads, what it found, channel ("issue" / "skip")
OTHER_CHECKS = [
    ("HC-004", "tariffVersion 未声明", "issue"),
    ("HC-005", "itemNo 重复「1」", "issue"),
    ("HC-006", "description 残留「【」", "issue"),
    ("HC-003", "basis 整列缺失", "skip"),
]

ISSUES = [
    ("HC-002", "第 1 行 · subheading", "847140 不是 8471300000 的前缀"),
    ("HC-004", "表头 · tariffVersion", "表头缺少 tariffVersion"),
    ("HC-005", "第 2 行 · itemNo", "「1」与第 1 行重复"),
    ("HC-006", "第 2 行 · description", "残留占位符「【」"),
]


class Svg:
    """Tiny SVG writer that measures every label before it is emitted."""

    def __init__(self) -> None:
        self.parts: list[str] = []
        self.overflows: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def text(self, x: float, y: float, content: str, size: float, fill: str, *,
             anchor: str = "start", weight: int | None = None,
             mono: bool = False, max_w: float | None = None,
             opacity: float | None = None) -> None:
        kind = ("mono" if mono else "cjk") + ("_bold" if weight else "")
        if mono and weight:
            kind = "mono_bold"
        if max_w is not None:
            w = measure(content, size, kind)
            if w > max_w + 0.4:
                self.overflows.append(
                    f"{content!r} needs {w:.1f}px > {max_w}px")
        family = FONT_CSS_MONO if mono else FONT_CSS_CJK
        attrs = [f'x="{x}"', f'y="{y}"', f'fill="{fill}"',
                 f'font-family="{family}"', f'font-size="{size}"']
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if weight:
            attrs.append(f'font-weight="{weight}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<text {" ".join(attrs)}>{escape(content)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, *, fill: str,
             rx: float = 0, stroke: str | None = None, sw: float = 1.5,
             shadow: bool = False, dash: str | None = None,
             opacity: float | None = None) -> None:
        attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"']
        if rx:
            attrs.append(f'rx="{rx}"')
        attrs.append(f'fill="{fill}"')
        if stroke:
            attrs.append(f'stroke="{stroke}"')
            attrs.append(f'stroke-width="{sw}"')
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        if shadow:
            attrs.append('filter="url(#soft)"')
        self.add(f'<rect {" ".join(attrs)}/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, *, stroke: str,
             sw: float = 1.5, dash: str | None = None,
             marker: str | None = None, opacity: float | None = None) -> None:
        attrs = [f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
                 f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<line {" ".join(attrs)}/>')

    def path(self, d: str, *, stroke: str, sw: float = 1.5,
             marker: str | None = None, dash: str | None = None,
             fill: str = "none", opacity: float | None = None) -> None:
        attrs = [f'd="{d}"', f'fill="{fill}"', f'stroke="{stroke}"',
                 f'stroke-width="{sw}"', 'stroke-linecap="round"',
                 'stroke-linejoin="round"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<path {" ".join(attrs)}/>')

    def dot(self, cx: float, cy: float, r: float, fill: str,
            opacity: float | None = None) -> None:
        extra = '' if opacity is None else f' opacity="{opacity}"'
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{extra}/>')

    def chip(self, x: float, y: float, label: str, fg: str, bg: str,
             *, size: float = 11, pad: float = 8, height: float = 18,
             mono: bool = False, weight: int | None = None,
             anchor_right: bool = False) -> float:
        kind = ("mono" if mono else "cjk") + ("_bold" if weight else "")
        if mono and weight:
            kind = "mono_bold"
        w = measure(label, size, kind) + pad * 2
        bx = x - w if anchor_right else x
        self.rect(bx, y, w, height, fill=bg, rx=height / 2)
        self.text(bx + pad, y + height / 2 + size * 0.34, label, size, fg,
                  weight=weight, mono=mono)
        return w

    def svg(self, w: int, h: int, label: str) -> str:
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
                f'height="{h}" viewBox="0 0 {w} {h}" role="img" '
                f'aria-label="{escape(label)}">')
        return "\n".join([head, *self.parts, "</svg>"]) + "\n"


def flow_svg(skin: str) -> str:
    s = FLOW[skin]
    W, H = 1100, 660
    v = Svg()

    v.add("<defs>")
    v.add(f'<linearGradient id="bg" x1="0" y1="0" x2="0.3" y2="1">'
          f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
          f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    v.add(f'<filter id="soft" x="-30%" y="-30%" width="160%" height="170%">'
          f'<feDropShadow dx="0" dy="7" stdDeviation="9" '
          f'flood-color="#16122c" flood-opacity="{s["shadow"]}"/></filter>')
    v.add('<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
          'markerWidth="5.6" markerHeight="5.6" orient="auto-start-reverse">'
          f'<path d="M0 0 L10 5 L0 10 z" fill="{s["accent"]}"/></marker>')
    v.add("</defs>")
    v.add(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

    # ---- header -------------------------------------------------------------
    v.text(44, 52, "dsh-hs-classify", 24, s["text"], weight=700, mono=True,
           max_w=260)
    v.text(272, 52, "十位编号的四级前缀 · 两条出口", 23, s["text"], weight=700,
           max_w=560)
    v.chip(1056, 34, "规则库 v2026.1 · HC-001…HC-006", s["accent"], s["band"],
           size=11.5, pad=11, height=24, anchor_right=True)
    v.text(44, 84,
           "一份台账 = 表头 + 每行若干栏；十位编号拆成 2 / 4 / 6 / 10 四级前缀。"
           "能执行的检查出差异，不能执行的出原因。",
           14, s["sub"], max_w=1012)
    v.line(44, 100, 1056, 100, stroke=s["rule"], sw=1)

    # ---- left: the material (header + two rows) -----------------------------
    v.rect(44, 112, 286, 244, fill=s["panel"], rx=20, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(62, 130, "材料 · 一份台账", 13, s["accent"], weight=700, max_w=250)
    v.text(62, 150, "file | material · JSON / YAML", 11, s["faint"], mono=True,
           max_w=250)
    v.line(62, 166, 312, 166, stroke=s["rule"], sw=1)

    v.text(62, 180, "表头 header", 11, s["faint"], max_w=120)
    v.text(62, 200, "tariffVersion", 11.5, s["text"], mono=True, max_w=100)
    v.text(160, 200, "未声明", 11.5, s["mark"], weight=700, max_w=50)

    v.text(62, 224, "行 rows[] · 2 行", 11, s["faint"], max_w=150)
    v.text(62, 242, "1 · 便携式自动数据处理设备", 12, s["text"], max_w=250)
    v.text(62, 260, "子目 847140 · 编号 8471300000", 11, s["sub"], mono=True,
           max_w=250)
    v.text(62, 282, "1 · 【待补充】", 12, s["text"], max_w=150)
    v.text(62, 300, "子目 847130 · 编号 8471300000", 11, s["sub"], mono=True,
           max_w=250)

    v.text(62, 324, "无「归类依据 basis」列", 11, s["mark"], weight=700,
           max_w=210)
    v.text(62, 342, "列名归一 · 大小写不敏感", 11, s["faint"], max_w=250)

    # ---- left: the header field and the non-code row fields ------------------
    v.rect(44, 372, 286, 148, fill=s["panel"], rx=20, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(62, 390, "表头 / 行级其它栏", 13, s["accent"], weight=700, max_w=250)
    v.text(62, 408, "每条规则各读自己那一栏", 11, s["faint"], max_w=250)
    for i, (rid, detail, channel) in enumerate(OTHER_CHECKS):
        ry = 430 + i * 22
        v.text(62, ry, rid, 12, s["text"], weight=700, mono=True, max_w=50)
        v.text(116, ry, detail, 11, s["sub"], max_w=175)
        v.dot(304, ry + 4, 3.4,
              s["mark"] if channel == "issue" else s["faint"])

    # ---- centre: the staircase of four prefix levels ------------------------
    v.rect(344, 112, 410, 408, fill=s["panel"], rx=20, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(362, 130, "编号层级 · 由粗到细", 13, s["accent"], weight=700,
           max_w=374)
    v.text(362, 150, "HC-001 看形式 · HC-002 看逐级前缀", 11, s["faint"],
           max_w=374)

    bar_x = 362
    bar_ws = [374, 328, 282, 236]  # top (code) widest, bottom (chapter) shortest
    bar_ys = [172, 238, 304, 370]
    for i, ((name, field, stated, span, rule, ok), bw, by) in enumerate(
            zip(LEVELS, bar_ws, bar_ys)):
        fill = s["panel"] if ok else s["mark_bg"]
        stroke = s["edge"] if ok else s["mark"]
        v.rect(bar_x, by, bw, 54, fill=fill, rx=12, stroke=stroke,
               sw=2 if not ok else 1.4)
        v.text(bar_x + 14, by + 18, name, 12.5, s["text"], weight=700,
               max_w=80)
        v.text(bar_x + 14 + measure(name, 12.5, "cjk_bold") + 6, by + 18,
               field, 11, s["faint"], mono=True, max_w=90)
        v.chip(bar_x + bw - 10, by + 7, rule, s["mark"] if not ok else s["accent"],
               s["chip"], size=11, pad=6, height=16, weight=700,
               anchor_right=True)

        # the value with its fifth digit marked where the levels diverge
        value_x = bar_x + 14
        v.text(value_x, by + 42, stated, 17, s["mark"] if not ok else s["text"],
               weight=700, mono=True, max_w=150)
        if i <= 1:
            cw = measure("0", 17, "mono_bold")
            v.line(value_x + 4 * cw - 1, by + 47,
                   value_x + 5 * cw - 1, by + 47,
                   stroke=s["mark"], sw=2)
        v.text(bar_x + 120, by + 42, span, 11, s["sub"], max_w=80)

    # the finding, stated under the ladder
    v.text(362, 438,
           "第 1 行：子目 847140 不是 8471300000 的前缀", 12, s["mark"],
           weight=700, max_w=374)
    v.text(362, 458,
           "第 5 位起不同（3 vs 4）；只核对前缀关系与位数递增。",
           11, s["sub"], max_w=374)
    v.text(362, 478,
           "行 2 的 847130 是前缀；位数 2 / 4 / 6 / 10 逐级递增。",
           11, s["faint"], max_w=374)
    v.text(362, 498, "换年度税则只改规则库的 pattern，不改代码。", 11,
           s["faint"], max_w=374)

    # ---- right: issues[] -----------------------------------------------------
    v.rect(772, 112, 284, 286, fill=s["panel"], rx=20, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(790, 130, "issues[]", 14, s["accent"], weight=700, mono=True,
           max_w=150)
    v.chip(1056 - 18, 126, "4 条", s["accent"], s["band"], size=11, pad=8,
           height=19, anchor_right=True)
    v.text(790, 150, "差异：行号 + 栏名 + 应填", 11, s["faint"], max_w=250)
    for i, (rid, locator, detail) in enumerate(ISSUES):
        ry = 176 + i * 50
        v.text(790, ry, rid, 12, s["accent"], weight=700, mono=True, max_w=50)
        v.text(842, ry, locator, 11.5, s["sub"], max_w=190)
        v.text(790, ry + 20, detail, 12, s["text"], max_w=245)
    v.text(790, 378, "found / expected / fix 三项都写", 11, s["faint"],
           max_w=165)
    v.text(1038, 378, "结论留给审核人", 11, s["accent2"], weight=700,
           anchor="end", max_w=110)

    # ---- right: skipped[] ----------------------------------------------------
    v.rect(772, 414, 284, 112, fill=s["panel"], rx=20, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(790, 432, "skipped[]", 14, s["sub"], weight=700, mono=True,
           max_w=150)
    v.chip(1056 - 18, 428, "1 条", s["sub"], s["band"], size=11, pad=8,
           height=19, anchor_right=True)
    v.text(790, 452, "未执行：规则 + 原因", 11, s["faint"], max_w=250)
    v.text(790, 472, "HC-003 · 材料没有「basis」列", 12, s["text"], max_w=250)
    v.text(790, 490, "空 issues ≠ 没问题：先读 skipped", 11, s["sub"],
           max_w=250)
    v.text(790, 508, "HC-001 已执行、无差异 → 不入任何通道", 11, s["faint"],
           max_w=250)

    # ---- right: the projection ----------------------------------------------
    v.rect(772, 538, 284, 68, fill=s["panel"], rx=16, stroke=s["accent"],
           sw=1.5, shadow=True)
    v.text(790, 554, "buildView() → markdown", 13, s["accent"], weight=700,
           mono=True, max_w=250)
    v.text(790, 574, "reportJson · summary · counts", 11, s["sub"], mono=True,
           max_w=250)
    v.text(790, 592, "同一次运行的投影；结论不在里面", 11, s["faint"],
           max_w=250)

    # merge rail: both channels leave into the same projection
    v.path("M1056 398 H1068 V560 H1056", stroke=s["accent"], sw=1.4,
           marker="arr")
    v.path("M1056 480 H1068", stroke=s["accent"], sw=1.4)

    # ---- bottom: how to read the two channels --------------------------------
    v.dot(48, 552, 4, s["mark"])
    v.text(58, 548, "issues[] 有差异", 11, s["sub"], max_w=120)
    v.dot(178, 552, 4, s["faint"])
    v.text(188, 548, "skipped[] 未执行", 11, s["sub"], max_w=120)
    v.text(44, 576, "执行过、无差异的规则不出现在任何通道（如 HC-001）。",
           11, s["faint"], max_w=330)
    v.text(44, 596, "只读材料 · 无网络 · 不调用模型 · 不改原件", 11,
           s["faint"], max_w=330)

    # ---- footer --------------------------------------------------------------
    v.line(44, 620, 1056, 620, stroke=s["rule"], sw=1)
    v.text(44, 636,
           "PerryLink DSH plugin family · Apache-2.0 · 配图由 "
           "scripts/gen-readme-assets.py 生成",
           11, s["faint"], max_w=700)
    v.text(1056, 636, "规则库即数据：换 yaml 即换规则集", 11, s["faint"],
           anchor="end", max_w=260)

    if v.overflows:
        raise SystemExit("FATAL: SVG label overflow:\n  " +
                         "\n  ".join(v.overflows))
    return v.svg(W, H, "dsh-hs-classify 结构图：台账的十位编号拆成 2 / 4 / 6 / 10 "
                       "四级前缀阶梯；六条规则各读一栏，差异进 issues[]、"
                       "未执行进 skipped[]，最后由 buildView() 投影成报告")


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        for lang in ("zh", "en"):
            hero(lang, skin)
        name = f"dsh-hs-classify-flow-v5-{skin}.svg"
        with open(os.path.join(OUT, name), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote {name} (1100×660)")


if __name__ == "__main__":
    main()
