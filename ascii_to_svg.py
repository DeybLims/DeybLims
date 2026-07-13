#!/usr/bin/env python3
"""Convert profile photo to Instagram-style ASCII portrait SVG banners."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).parent
IMAGE_PATH = ROOT / "profile.jpg"
ASCII_RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
PROFILE = {
    "name": "Dave Emanuel G. Lima",
    "role": "Full Stack Developer",
    "origin": "Philippines",
    "education": "B.S. CS — AI Major, WVSU",
    "focus": "ERP workflows · Next.js · Cloud",
    "portfolio": "davelims.vercel.app",
    "email": "daveemanuel.lima@wvsu.edu.ph",
    "github": "DeybLims",
    "status": "Open to remote & freelance",
    "languages": "TypeScript · Python · Dart · PHP",
    "toolchain": "VS Code · Git · Docker · Vercel",
    "currently": "ERP systems & AI-powered apps",
    "skills": [
        "React", "Next.js", "Node.js", "TypeScript", "Tailwind", "Python", "Docker",
        "Postgres", "AWS", "Git", "Figma", "Flutter", "Laravel", "Flask", "Firebase",
        "Vercel", "ERPNext", "Frappe",
    ],
    "status_items": [
        ("GitHub", "active"),
        ("VS Code", "running"),
        ("Docker", "ready"),
        ("Deploy", "online"),
    ],
}


FRAME_X, FRAME_Y, FRAME_W, FRAME_H = 64, 88, 368, 430
ASCII_COLS = 62
ASCII_ROWS = 58


def image_to_ascii(path: Path, cols: int = ASCII_COLS, rows: int = ASCII_ROWS, contrast: float = 1.55) -> list[str]:
    img = Image.open(path).convert("L")
    w, h = img.size
    target_aspect = rows / cols
    src_aspect = h / w
    if src_aspect > target_aspect:
        new_h = int(w * target_aspect)
        top = max(0, (h - new_h) // 2 - int(new_h * 0.05))
        img = img.crop((0, top, w, min(h, top + new_h)))
    else:
        new_w = int(h / target_aspect)
        left = max(0, (w - new_w) // 2 - int(new_w * 0.02))
        img = img.crop((left, 0, left + new_w, h))
    zoom = 1.08
    zw, zh = img.size
    margin_w = int(zw * (zoom - 1) / 2)
    margin_h = int(zh * (zoom - 1) / 2)
    img = img.crop((margin_w, margin_h, zw - margin_w, zh - margin_h))
    img = ImageOps.autocontrast(img)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = img.resize((cols, rows), Image.Resampling.LANCZOS)
    pixels = img.load()
    lines: list[str] = []
    for y in range(rows):
        row = []
        for x in range(cols):
            lum = pixels[x, y]
            idx = int(lum / 255 * (len(ASCII_RAMP) - 1))
            row.append(ASCII_RAMP[idx])
        lines.append("".join(row))
    return lines


def ascii_layout(lines: list[str]) -> tuple[float, float, int, float]:
    rows = len(lines)
    line_h = FRAME_H / rows
    font_size = line_h * 0.82
    x = FRAME_X
    y0 = FRAME_Y + font_size
    return font_size, line_h, x, y0


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def ascii_svg_block(lines: list[str], x: int, y0: int, line_h: float, font_size: float, fill: str) -> str:
    out = [
        "      <text font-family=\"ui-monospace,SFMono-Regular,Menlo,Consolas,monospace\" "
        f'font-size="{font_size:.2f}" fill="{fill}" xml:space="preserve">'
    ]
    for i, line in enumerate(lines):
        line = line.ljust(ASCII_COLS)[:ASCII_COLS]
        y = y0 + i * line_h
        out.append(
            f'        <tspan x="{x}" y="{y:.1f}" textLength="{FRAME_W}" '
            f'lengthAdjust="spacingAndGlyphs">{esc(line)}</tspan>'
        )
    out.append("      </text>")
    return "\n".join(out)


def pill_rows(skills: list[str], start_y: int, theme: dict, max_x: int = 1105) -> tuple[str, int]:
    chunks: list[str] = []
    x = 488
    y = start_y
    row_h = 28
    for skill in skills:
        w = max(50, len(skill) * 7 + 20)
        if x + w > max_x:
            x = 488
            y += row_h
        chunks.append(
            f"""    <g>
      <rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="{theme['pill_fill']}" stroke="{theme['pill_stroke']}" stroke-width="1"/>
      <text x="{x + w // 2}" y="{y + 15}" text-anchor="middle" font-family="ui-sans-serif,sans-serif" font-size="10" fill="{theme['pill_text']}">{esc(skill)}</text>
    </g>"""
        )
        x += w + 6
    return "\n".join(chunks), y + row_h


def profile_columns(theme: dict) -> str:
    left = [
        ("Subject", PROFILE["name"], theme["value"]),
        ("Role", PROFILE["role"], theme["accent_text"]),
        ("Origin", PROFILE["origin"], theme["value"]),
        ("Education", PROFILE["education"], theme["value"]),
    ]
    right = [
        ("Focus", PROFILE["focus"], theme["value"]),
        ("Status", "Open to work", theme["success"]),
        ("Languages", "TS · Python · Dart", theme["value"]),
        ("ToolChain", "VS Code · Git · Docker", theme["value"]),
    ]
    lines: list[str] = []
    y = 252
    for i in range(4):
        l_label, l_val, l_color = left[i]
        r_label, r_val, r_color = right[i]
        lines.append(
            f'      <text x="488" y="{y}" font-family="ui-monospace,monospace" font-size="11" fill="{theme["muted"]}">'
            f'<tspan fill="{theme["label"]}" font-weight="600">{esc(l_label):<11}</tspan>'
            f'<tspan fill="{l_color}">{esc(l_val)}</tspan></text>'
        )
        lines.append(
            f'      <text x="800" y="{y}" font-family="ui-monospace,monospace" font-size="11" fill="{theme["muted"]}">'
            f'<tspan fill="{theme["label"]}" font-weight="600">{esc(r_label):<11}</tspan>'
            f'<tspan fill="{r_color}">{esc(r_val)}</tspan></text>'
        )
        y += 22
    return "\n".join(lines)


def status_panel(theme: dict) -> str:
    items = []
    x = 488
    for label, state in PROFILE["status_items"]:
        items.append(
            f"""      <g>
        <circle cx="{x + 6}" cy="374" r="4" fill="{theme['success_dot']}"/>
        <text x="{x + 16}" y="378" font-family="ui-monospace,monospace" font-size="10" fill="{theme['muted']}">{esc(label)}</text>
        <text x="{x + 72}" y="378" font-family="ui-monospace,monospace" font-size="10" fill="{theme['success']}">{esc(state)}</text>
      </g>"""
        )
        x += 148
    return "\n".join(items)


def terminal_footer(theme: dict, y: int) -> str:
    return f"""    <rect x="480" y="{y}" width="648" height="24" rx="8" fill="{theme['chrome']}" fill-opacity="0.95"/>
    <text x="492" y="{y + 16}" font-family="ui-monospace,monospace" font-size="10" fill="{theme['muted']}">deyb@github</text>
    <text x="572" y="{y + 16}" font-family="ui-monospace,monospace" font-size="10" fill="{theme['label']}">~</text>
    <text x="584" y="{y + 16}" font-family="ui-monospace,monospace" font-size="10" fill="{theme['value']}">git commit -m &quot;ready to deploy&quot;</text>
    <rect x="838" y="{y + 8}" width="7" height="10" rx="1" fill="{theme['accent_text']}" opacity="0.9"/>"""


def build_svg(theme: dict, ascii_lines: list[str]) -> str:
    font_size, line_h, ascii_x, ascii_y0 = ascii_layout(ascii_lines)
    ascii_block = ascii_svg_block(ascii_lines, ascii_x, ascii_y0, line_h, font_size, theme["ascii_fill"])
    profile_block = profile_columns(theme)
    status_block = status_panel(theme)

    pills_y = 406
    pills, pills_end = pill_rows(PROFILE["skills"], pills_y, theme)
    connect_y = max(pills_end + 12, 488)
    footer_y = 538

    connect_lines = [
        f'      <text x="488" y="{connect_y + 18}" font-family="ui-monospace,monospace" font-size="10" fill="{theme["muted"]}">'
        f'<tspan fill="{theme["label"]}" font-weight="600">Portfolio  </tspan>'
        f'<tspan fill="{theme["link"]}">{esc(PROFILE["portfolio"])}</tspan></text>',
        f'      <text x="488" y="{connect_y + 34}" font-family="ui-monospace,monospace" font-size="10" fill="{theme["muted"]}">'
        f'<tspan fill="{theme["label"]}" font-weight="600">Email      </tspan>'
        f'<tspan fill="{theme["link"]}">{esc(PROFILE["email"])}</tspan></text>',
        f'      <text x="488" y="{connect_y + 50}" font-family="ui-monospace,monospace" font-size="10" fill="{theme["muted"]}">'
        f'<tspan fill="{theme["label"]}" font-weight="600">GitHub     </tspan>'
        f'<tspan fill="{theme["link"]}">github.com/{esc(PROFILE["github"])}</tspan></text>',
    ]
    footer = terminal_footer(theme, footer_y)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610" role="img" aria-label="{esc(PROFILE['name'])} — Software Engineer">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{theme['bg1']}"/>
      <stop offset="50%" stop-color="{theme['bg2']}"/>
      <stop offset="100%" stop-color="{theme['bg1']}"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{theme['accent1']}"/>
      <stop offset="50%" stop-color="{theme['accent2']}"/>
      <stop offset="100%" stop-color="{theme['accent3']}"/>
    </linearGradient>
    <linearGradient id="borderShimmer" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{theme['shimmer_a']}"/>
      <stop offset="50%" stop-color="{theme['shimmer_b']}"/>
      <stop offset="100%" stop-color="{theme['shimmer_a']}"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="-1180 0;1180 0;-1180 0" dur="6s" repeatCount="indefinite"/>
    </linearGradient>
    <filter id="asciiGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1.8" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="pillGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="1.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="gridPattern" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M24 0H0V24" fill="none" stroke="{theme['grid']}" stroke-width="0.5" opacity="0.35"/>
    </pattern>
    <clipPath id="cardClip"><rect x="20" y="20" width="1140" height="570" rx="24"/></clipPath>
    <clipPath id="asciiClip"><rect x="48" y="48" width="400" height="514" rx="16"/></clipPath>
    <clipPath id="termClip"><rect x="468" y="48" width="672" height="514" rx="16"/></clipPath>
    <clipPath id="asciiFrame"><rect x="{FRAME_X}" y="{FRAME_Y}" width="{FRAME_W}" height="{FRAME_H}" rx="12"/></clipPath>
  </defs>

  <rect width="1180" height="610" fill="url(#bgGrad)"/>
  <rect width="1180" height="610" fill="{theme['glow']}" opacity="0.35"/>

  <g clip-path="url(#cardClip)">
    <rect x="20" y="20" width="1140" height="570" rx="24" fill="{theme['panel']}" fill-opacity="0.92"/>
    <rect x="20" y="20" width="1140" height="570" rx="24" fill="none" stroke="{theme['border']}" stroke-width="1"/>
    <rect x="20" y="20" width="1140" height="570" rx="24" fill="none" stroke="url(#borderShimmer)" stroke-width="1.2" opacity="0.8"/>
  </g>

  <g clip-path="url(#asciiClip)">
    <rect x="48" y="48" width="400" height="514" rx="16" fill="{theme['subpanel']}" fill-opacity="0.85"/>
    <rect x="48" y="48" width="400" height="514" rx="16" fill="none" stroke="{theme['border']}" stroke-width="1"/>
    <rect x="48" y="48" width="400" height="36" rx="16" fill="{theme['chrome']}" fill-opacity="0.95"/>
    <rect x="48" y="68" width="400" height="16" fill="{theme['chrome']}" fill-opacity="0.95"/>
    <circle cx="72" cy="66" r="4.5" fill="#EF4444" opacity="0.8"/>
    <circle cx="88" cy="66" r="4.5" fill="#F59E0B" opacity="0.8"/>
    <circle cx="104" cy="66" r="4.5" fill="#10B981" opacity="0.8"/>
    <text x="120" y="70" font-family="ui-monospace,monospace" font-size="10" fill="{theme['muted']}">~/portrait — ascii render</text>
    <g clip-path="url(#asciiFrame)" filter="url(#asciiGlow)">
{ascii_block}
    </g>
    <rect x="{FRAME_X}" y="{FRAME_Y}" width="{FRAME_W}" height="{FRAME_H}" rx="12" fill="none" stroke="{theme['ascii_stroke']}" stroke-width="1.2"/>
    <rect x="{FRAME_X}" y="{FRAME_Y}" width="{FRAME_W}" height="2" fill="{theme['scanline']}" opacity="0.35">
      <animate attributeName="y" values="{FRAME_Y};{FRAME_Y + FRAME_H};{FRAME_Y}" dur="4.5s" repeatCount="indefinite"/>
    </rect>
  </g>

  <g clip-path="url(#termClip)">
    <rect x="468" y="48" width="672" height="514" rx="16" fill="{theme['subpanel']}" fill-opacity="0.9"/>
    <rect x="468" y="48" width="672" height="514" rx="16" fill="url(#gridPattern)" opacity="0.45"/>
    <rect x="468" y="48" width="672" height="514" rx="16" fill="none" stroke="{theme['border']}" stroke-width="1"/>
    <rect x="468" y="48" width="672" height="36" rx="16" fill="{theme['chrome']}" fill-opacity="0.95"/>
    <rect x="468" y="68" width="672" height="16" fill="{theme['chrome']}" fill-opacity="0.95"/>
    <circle cx="492" cy="66" r="5" fill="#EF4444" opacity="0.8"/>
    <circle cx="512" cy="66" r="5" fill="#F59E0B" opacity="0.8"/>
    <circle cx="532" cy="66" r="5" fill="#10B981" opacity="0.8"/>
    <text x="550" y="70" font-family="ui-monospace,monospace" font-size="11" fill="{theme['muted']}">deyb@github — zsh</text>

    <text x="488" y="112" font-family="ui-monospace,monospace" font-size="13" fill="{theme['muted']}">Hi &#x1F44B;</text>
    <text x="488" y="142" font-family="ui-sans-serif,system-ui,sans-serif" font-size="22" font-weight="600" fill="{theme['value']}">I'm {esc(PROFILE['name'])}</text>
    <text x="488" y="172" font-family="ui-monospace,monospace" font-size="14" fill="url(#accentGrad)">{esc(PROFILE['role'])}</text>
    <text x="488" y="196" font-family="ui-monospace,monospace" font-size="10" fill="{theme['muted']}">// building {esc(PROFILE['currently'])}</text>

    <text x="488" y="222" font-family="ui-monospace,monospace" font-size="10" font-weight="600" fill="{theme['muted']}" letter-spacing="1.2">PROFILE DATA</text>
    <line x1="488" y1="228" x2="1120" y2="228" stroke="{theme['border']}" stroke-width="1"/>
    <g>
{profile_block}
    </g>

    <text x="488" y="358" font-family="ui-monospace,monospace" font-size="10" font-weight="600" fill="{theme['muted']}" letter-spacing="1.2">LIVE STATUS</text>
    <line x1="488" y1="364" x2="1120" y2="364" stroke="{theme['border']}" stroke-width="1"/>
    <g>
{status_block}
    </g>

    <text x="488" y="398" font-family="ui-monospace,monospace" font-size="10" font-weight="600" fill="{theme['muted']}" letter-spacing="1.2">TECH STACK</text>
    <line x1="488" y1="404" x2="1120" y2="404" stroke="{theme['border']}" stroke-width="1"/>
  </g>

  <g filter="url(#pillGlow)">
{pills}
  </g>

  <g>
    <text x="488" y="{connect_y}" font-family="ui-monospace,monospace" font-size="10" font-weight="600" fill="{theme['muted']}" letter-spacing="1.2">CONNECT</text>
    <line x1="488" y1="{connect_y + 6}" x2="1120" y2="{connect_y + 6}" stroke="{theme['border']}" stroke-width="1"/>
    <g>
{chr(10).join(connect_lines)}
    </g>
{footer}
  </g>
</svg>
'''


DARK = {
    "bg1": "#030712", "bg2": "#0a0f1e", "panel": "#0F172A", "subpanel": "#0F172A",
    "chrome": "#0a0f1e", "border": "rgba(255,255,255,0.08)", "muted": "#94A3B8",
    "value": "#F8FAFC", "label": "#22D3EE", "accent_text": "#22D3EE", "link": "#22D3EE",
    "success": "#10B981", "success_dot": "#34D399", "grid": "rgba(34,211,238,0.12)",
    "ascii_fill": "#67E8F9", "ascii_stroke": "rgba(34,211,238,0.35)", "scanline": "#22D3EE",
    "accent1": "#7C3AED", "accent2": "#22D3EE", "accent3": "#10B981",
    "shimmer_a": "rgba(255,255,255,0.02)", "shimmer_b": "rgba(34,211,238,0.35)",
    "glow": "rgba(37,99,235,0.15)", "pill_fill": "#0F172A", "pill_stroke": "rgba(124,58,237,0.45)",
    "pill_text": "#F8FAFC",
}

LIGHT = {
    "bg1": "#FFFFFF", "bg2": "#F8FAFC", "panel": "#F8FAFC", "subpanel": "#FFFFFF",
    "chrome": "#F1F5F9", "border": "rgba(15,23,42,0.08)", "muted": "#475569",
    "value": "#0F172A", "label": "#2563EB", "accent_text": "#06B6D4", "link": "#2563EB",
    "success": "#059669", "success_dot": "#10B981", "grid": "rgba(37,99,235,0.08)",
    "ascii_fill": "#0891B2", "ascii_stroke": "rgba(37,99,235,0.25)", "scanline": "#06B6D4",
    "accent1": "#2563EB", "accent2": "#06B6D4", "accent3": "#10B981",
    "shimmer_a": "rgba(15,23,42,0.02)", "shimmer_b": "rgba(37,99,235,0.2)",
    "glow": "rgba(37,99,235,0.08)", "pill_fill": "#FFFFFF", "pill_stroke": "rgba(37,99,235,0.3)",
    "pill_text": "#0F172A",
}


def main() -> None:
    if not IMAGE_PATH.exists():
        raise SystemExit(f"Missing {IMAGE_PATH}")
    ascii_lines = image_to_ascii(IMAGE_PATH)
    font_size, _, _, _ = ascii_layout(ascii_lines)
    (ROOT / "dark.svg").write_text(build_svg(DARK, ascii_lines), encoding="utf-8")
    (ROOT / "light.svg").write_text(build_svg(LIGHT, ascii_lines), encoding="utf-8")
    deyb = ROOT.parent / "DeybLims"
    if deyb.exists():
        (deyb / "dark.svg").write_text((ROOT / "dark.svg").read_text(encoding="utf-8"), encoding="utf-8")
        (deyb / "light.svg").write_text((ROOT / "light.svg").read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Generated banners: {len(ascii_lines)} rows x {max(len(l) for l in ascii_lines)} cols, font {font_size:.1f}px")


if __name__ == "__main__":
    main()
