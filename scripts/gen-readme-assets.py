#!/usr/bin/env python3
"""Generate README image assets for dsh-hs-classify (docs/assets/).

Outputs (idempotent overwrite):
  dsh-hs-classify-flow-light.svg / dsh-hs-classify-flow-dark.svg
      Hero pipeline diagram. Two hand-written SVG files (vector - never
      rasterized to webp). Every visible label is a command-surface token
      (`file`, `material`, `hs_classify`, `rules/hs-classify.yaml`, `HC-00N`,
      `issues[]`, config keys ...), so all five README languages share the
      same pair.

No evidence chart: this repository ships no benchmark/RESULTS.md or measured
dataset, and the family rule is to draw one only from real data. The old
single-theme `dsh-hs-classify-flow.svg` stays on disk so existing external
links keep resolving.

Run once:  python scripts/gen-readme-assets.py
Requires:  the bundled Python (Pillow build); CJK font is probed below.
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont  # noqa: F401  (bundled runtime)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# --- palette: PerryLink family (accent) + GitHub page backgrounds ----------
FAMILY = "#4B67B4"   # family accent (badges labelColor family uses #2B3245)
SKIN = {
    "light": dict(bg="#ffffff", box="#f6f8fa", border="#d0d7de",
                  text="#1f2328", sub="#57606a", accent="#4B67B4",
                  chip="#eef1f8"),
    "dark": dict(bg="#0d1117", box="#161b22", border="#30363d",
                 text="#f0f6fc", sub="#8b949e", accent="#8ea6e8",
                 chip="#1c2330"),
}
WEBP_QUALITY = 90  # no raster asset in this repo; kept for family parity

# --- CJK font probe: Chinese must never render as tofu boxes ----------------
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",      # Microsoft YaHei
    r"C:\Windows\Fonts\simhei.ttf",    # SimHei
    r"C:\Windows\Fonts\Deng.ttf",      # DengXian
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if FONT_PATH is None:
    sys.exit("FATAL: no CJK font found (looked for msyh.ttc, simhei.ttf, "
             "Deng.ttf, Noto Sans CJK, PingFang). Refusing to render Chinese "
             "as tofu boxes; install one of the probed fonts and re-run.")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


# ---------------------------------------------------------------------------
# Hero pipeline SVG (light + dark)
# ---------------------------------------------------------------------------
NODES = [
    ("file", ["material", "JSON · YAML"]),
    ("hs_classify", ["rows[]", "columns \u2192 fields"]),
    ("rules/", ["hs-classify.yaml", "HC-001 \u2026 HC-006"]),
    ("issues[]", ["skipped[]", "ruleId · row · field"]),
    ("markdown", ["reportJson", "findings · reasons"]),
]
RULES = ["HC-001", "HC-002", "HC-003", "HC-004", "HC-005", "HC-006"]
CONFIG_KEYS = ("rulesFile · disabledRules · onlyRules · skipNotes · "
               "timeoutMs")


def esc(value: str) -> str:
    return (value.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    w, h = 1200, 430
    nw, nh, gap, x0, y0 = 200, 132, 35, 30, 150
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="dsh-hs-classify pipeline">',
        '<title>dsh-hs-classify pipeline</title>',
        f'<rect width="{w}" height="{h}" rx="18" fill="{s["bg"]}"/>',
        f'<text x="60" y="62" fill="{s["text"]}" font-family="ui-sans-serif,'
        f'system-ui,sans-serif" font-size="30" font-weight="700">'
        'dsh-hs-classify</text>',
        f'<text x="60" y="94" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="15">hs_classify · tools:register · '
        'rules/hs-classify.yaml</text>',
        f'<line x1="60" y1="116" x2="1140" y2="116" stroke="{s["border"]}"/>',
    ]
    for i, (label, subs) in enumerate(NODES):
        x = x0 + i * (nw + gap)
        accent = s["accent"] if i in (1, 2) else s["border"]
        parts.append(
            f'<rect x="{x}" y="{y0}" width="{nw}" height="{nh}" rx="14" '
            f'fill="{s["box"]}" stroke="{accent}" stroke-width="2"/>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 42}" fill="{s["text"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="18" font-weight="700">{esc(label)}</text>')
        for j, sub in enumerate(subs):
            parts.append(
                f'<text x="{x + nw // 2}" y="{y0 + 74 + j * 24}" '
                f'fill="{s["sub"]}" text-anchor="middle" '
                f'font-family="ui-monospace,monospace" font-size="12">'
                f'{esc(sub)}</text>')
        if i < len(NODES) - 1:
            ax = x + nw + 5
            ay = y0 + nh // 2
            parts.append(
                f'<path d="M{ax} {ay}h{gap - 12}" stroke="{s["sub"]}" '
                'stroke-width="3"/>')
            parts.append(
                f'<path d="M{ax + gap - 14} {ay - 7}l10 7-10 7" fill="none" '
                f'stroke="{s["sub"]}" stroke-width="3" '
                'stroke-linecap="round" stroke-linejoin="round"/>')
    # rule-id chips
    chip_w, chip_h, chip_gap = 128, 30, 18
    total = len(RULES) * chip_w + (len(RULES) - 1) * chip_gap
    cx = (w - total) // 2
    for i, rule in enumerate(RULES):
        x = cx + i * (chip_w + chip_gap)
        parts.append(
            f'<rect x="{x}" y="306" width="{chip_w}" height="{chip_h}" '
            f'rx="8" fill="{s["chip"]}" stroke="{s["border"]}"/>')
        parts.append(
            f'<text x="{x + chip_w // 2}" y="326" fill="{s["text"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="14">{rule}</text>')
    # config-key band
    parts.append(
        f'<rect x="30" y="352" width="1140" height="38" rx="10" '
        f'fill="{s["box"]}" stroke="{s["border"]}"/>')
    parts.append(
        f'<text x="600" y="376" fill="{s["sub"]}" text-anchor="middle" '
        f'font-family="ui-monospace,monospace" font-size="14">'
        f'{esc(CONFIG_KEYS)}</text>')
    parts.append(
        f'<text x="60" y="416" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="13">PerryLink DSH plugin family · '
        'Apache-2.0</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        with open(os.path.join(OUT, f"dsh-hs-classify-flow-{skin}.svg"),
                  "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
    print("wrote 2 SVG assets to docs/assets/ (no evidence chart: "
          "no measured dataset in this repo)")


if __name__ == "__main__":
    main()
