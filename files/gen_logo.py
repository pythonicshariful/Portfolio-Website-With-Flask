#!/usr/bin/env python3
"""
Zeplo Studio - animated logo.

Concept: the Pixel Grid Z writes itself one cell at a time, in Z-stroke order
(top rail, diagonal, bottom rail). The leading cell lands in Grid Teal and
settles to Pixel Purple - a write head moving through the grid.

Outputs
  zeplo-mark-animated.svg      512x512, CSS-animated, loops forever
  zeplo-lockup-animated.svg    1200x400, mark + wordmark + tagline
  zeplo-mark-dark.gif / -light.gif
  zeplo-lockup-dark.gif / -light.gif
  zeplo-mark-static.svg        non-animated fallback (favicons, print)
"""
import os, math, subprocess

OUT = "/home/claude/logo"
os.makedirs(OUT, exist_ok=True)
os.makedirs(f"{OUT}/frames", exist_ok=True)

PURPLE  = "#5B3FF8"
TEAL    = "#00E5B0"
INK     = "#0A0A12"
PAPER   = "#F7F7FB"
GHOST_D = "#FFFFFF"
GHOST_L = "#14131F"

DISPLAY = "Space Grotesk, DejaVu Sans, sans-serif"
MONO    = "DM Mono, DejaVu Sans Mono, monospace"

# 5x5 Z, written in stroke order: top rail L>R, diagonal, bottom rail L>R
ORDER = ([(0, c) for c in range(5)]
         + [(1, 3), (2, 2), (3, 1)]
         + [(4, c) for c in range(5)])
ZSET = set(ORDER)

T      = 3.6      # loop length, seconds
STEP   = 0.09     # gap between cells lighting
FRAMES = 36       # gif frames
DELAY  = 10       # gif centiseconds per frame


# ------------------------------------------------------------------ geometry
def cells(x0, y0, size, gap):
    return {(r, c): (x0 + c * (size + gap), y0 + r * (size + gap))
            for r in range(5) for c in range(5)}


def ghost_grid(pos, size, colour, op=".07"):
    return "".join(
        f'<rect x="{pos[(r,c)][0]}" y="{pos[(r,c)][1]}" width="{size}" height="{size}" '
        f'rx="{size*0.16:.1f}" fill="{colour}" fill-opacity="{op}"/>'
        for r in range(5) for c in range(5))


# ------------------------------------------------------ animated SVG (CSS)
CSS = f"""
.cell {{
  transform-box: fill-box;
  transform-origin: center;
  animation: draw {T}s cubic-bezier(.22,1,.36,1) infinite;
  opacity: 0;
}}
@keyframes draw {{
  0%   {{ opacity: 0; transform: scale(.25); fill: {TEAL}; }}
  3%   {{ opacity: 1; transform: scale(1.22); fill: {TEAL}; }}
  8%   {{ opacity: 1; transform: scale(1);    fill: {PURPLE}; }}
  78%  {{ opacity: 1; transform: scale(1);    fill: {PURPLE}; }}
  86%  {{ opacity: 0; transform: scale(.25);  fill: {PURPLE}; }}
  100% {{ opacity: 0; transform: scale(.25);  fill: {PURPLE}; }}
}}
.word {{ animation: rise {T}s ease-out infinite; opacity: 0; }}
@keyframes rise {{
  0%,32%   {{ opacity: 0; transform: translateX(-14px); }}
  42%      {{ opacity: 1; transform: translateX(0); }}
  76%      {{ opacity: 1; transform: translateX(0); }}
  84%,100% {{ opacity: 0; transform: translateX(0); }}
}}
.tag {{ animation: rise {T}s ease-out infinite; animation-delay: .18s; opacity: 0;
        transform-box: fill-box; }}
@media (prefers-reduced-motion: reduce) {{
  .cell, .word, .tag {{ animation: none; opacity: 1; fill: {PURPLE}; }}
}}
"""


def animated_svg(w, h, x0, y0, size, gap, wordmark=False):
    pos = cells(x0, y0, size, gap)
    g = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}" font-family="{DISPLAY}">',
         f'<style>{CSS}</style>',
         f'<g id="ghost">{ghost_grid(pos, size, "#8B86A8", ".08")}</g>']
    for i, (r, c) in enumerate(ORDER):
        x, y = pos[(r, c)]
        g.append(f'<rect class="cell" x="{x}" y="{y}" width="{size}" height="{size}" '
                 f'rx="{size*0.16:.1f}" fill="{PURPLE}" style="animation-delay:{i*STEP:.2f}s"/>')
    if wordmark:
        g.append(f'<g class="word"><text x="{x0+5*size+4*gap+72}" y="{h*0.55:.0f}" '
                 f'font-size="96" font-weight="700" letter-spacing="-3" fill="{PURPLE}">'
                 f'zeplo <tspan fill="#8B86A8" font-weight="500">studio</tspan></text></g>')
        g.append(f'<g class="tag"><text x="{x0+5*size+4*gap+76}" y="{h*0.55+46:.0f}" '
                 f'font-family="{MONO}" font-size="25" letter-spacing="5.5" fill="{TEAL}">'
                 f'every pixel has a purpose</text></g>')
    g.append("</svg>")
    return "".join(g)


def static_svg(size_px=512):
    s, gap = 64, 16
    x0 = y0 = (size_px - (5 * s + 4 * gap)) / 2
    pos = cells(x0, y0, s, gap)
    body = "".join(
        f'<rect x="{pos[(r,c)][0]}" y="{pos[(r,c)][1]}" width="{s}" height="{s}" '
        f'rx="10" fill="{PURPLE}"/>' for (r, c) in ORDER)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size_px}" height="{size_px}" '
            f'viewBox="0 0 {size_px} {size_px}">{body}</svg>')


# ---------------------------------------------------------------- gif frames
def ease_out(t):
    return 1 - pow(1 - t, 3)


def frame_svg(f, w, h, x0, y0, size, gap, bg, ghost, wordmark=False):
    """One static frame at loop position f/FRAMES."""
    t = f / FRAMES * T
    pos = cells(x0, y0, size, gap)
    g = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}" font-family="{DISPLAY}">',
         f'<rect width="{w}" height="{h}" fill="{bg}"/>',
         ghost_grid(pos, size, ghost, ".08")]

    for i, (r, c) in enumerate(ORDER):
        d = i * STEP
        local = t - d
        cycle = T
        out_at = 0.86 * cycle - d * 0          # exit uses same stagger via d below
        # appear
        if local < 0:
            continue
        # exit window, staggered the same way as entry
        exit_start = 0.80 * T
        if t > exit_start + d * 0.5:
            k = min(1.0, (t - exit_start - d * 0.5) / 0.22)
            op = 1 - k
            sc = 1 - 0.75 * k
            col = PURPLE
        elif local < 0.11:
            k = ease_out(min(1.0, local / 0.11))
            op = k
            sc = 0.25 + 0.97 * k
            col = TEAL
        elif local < 0.30:
            k = (local - 0.11) / 0.19
            op = 1
            sc = 1.22 - 0.22 * k
            col = TEAL if k < 0.5 else PURPLE
        else:
            op, sc, col = 1, 1, PURPLE
        if op <= 0.01:
            continue
        x, y = pos[(r, c)]
        cx, cy = x + size / 2, y + size / 2
        g.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{size*0.16:.1f}" '
                 f'fill="{col}" fill-opacity="{op:.3f}" '
                 f'transform="translate({cx:.1f} {cy:.1f}) scale({sc:.3f}) translate({-cx:.1f} {-cy:.1f})"/>')

    if wordmark:
        wt = (t - 1.18) / 0.36
        wop = max(0.0, min(1.0, wt))
        if t > 0.80 * T:
            wop = max(0.0, 1 - (t - 0.80 * T) / 0.26)
        if wop > 0.01:
            dx = (1 - ease_out(min(1.0, max(0.0, wt)))) * -14
            wx = x0 + 5 * size + 4 * gap + 72
            g.append(f'<g opacity="{wop:.3f}" transform="translate({dx:.1f} 0)">'
                     f'<text x="{wx}" y="{h*0.55:.0f}" font-size="96" font-weight="700" '
                     f'letter-spacing="-3" fill="{PURPLE}">zeplo '
                     f'<tspan fill="#8B86A8" font-weight="500">studio</tspan></text>'
                     f'<text x="{wx+4}" y="{h*0.55+46:.0f}" font-family="{MONO}" font-size="25" '
                     f'letter-spacing="5.5" fill="{TEAL}">every pixel has a purpose</text></g>')
    g.append("</svg>")
    return "".join(g)


def build_gif(name, w, h, x0, y0, size, gap, bg, ghost, wordmark, scale):
    import cairosvg
    for f in range(FRAMES):
        svg = frame_svg(f, w, h, x0, y0, size, gap, bg, ghost, wordmark)
        cairosvg.svg2png(bytestring=svg.encode(),
                         write_to=f"{OUT}/frames/{name}_{f:03d}.png",
                         output_width=int(w * scale), output_height=int(h * scale))
    subprocess.run(
        f'convert -delay {DELAY} -loop 0 {OUT}/frames/{name}_*.png '
        f'-layers OptimizeTransparency {OUT}/{name}.gif',
        shell=True, check=True)
    subprocess.run(f'rm -f {OUT}/frames/{name}_*.png', shell=True)
    print("gif:", name)


if __name__ == "__main__":
    # animated SVGs
    open(f"{OUT}/zeplo-mark-animated.svg", "w").write(
        animated_svg(512, 512, 64, 64, 64, 16))
    open(f"{OUT}/zeplo-lockup-animated.svg", "w").write(
        animated_svg(1180, 400, 90, 92, 43, 11, wordmark=True))
    open(f"{OUT}/zeplo-mark-static.svg", "w").write(static_svg())
    print("svg: written")

    build_gif("zeplo-mark-dark",   512, 512, 64, 64, 64, 16, INK,   GHOST_D, False, 0.9)
    build_gif("zeplo-mark-light",  512, 512, 64, 64, 64, 16, PAPER, GHOST_L, False, 0.9)
    build_gif("zeplo-lockup-dark", 1180, 400, 90, 92, 43, 11, INK,  GHOST_D, True, 0.85)
    build_gif("zeplo-lockup-light",1180, 400, 90, 92, 43, 11, PAPER, GHOST_L, True, 0.85)
