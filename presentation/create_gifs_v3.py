"""
JalSakhi - Competition-Grade Animated GIFs v3
==============================================
1. Phone comparison GIF: Realistic keypad + smartphone side by side
2. Voltammogram scan animation: Smooth DPV with pop-in labels
3. Heatmap buildup animation: Ripple effects, contour lines, village labels
4. Treatment advisory flow: AI-driven recommendation system

All GIFs use professional color palette, anti-aliased rendering,
smooth easing, and high resolution for PowerPoint embedding.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Arc, Wedge, Ellipse, PathPatch
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as pe
import matplotlib.path as mpath
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import os
import math

OUT_DIR = "C:/Users/Ujjwal/JalSakhi/presentation/gifs"
os.makedirs(OUT_DIR, exist_ok=True)

# ── FONT SETUP ────────────────────────────────────────────
# Windows font fallback chain
FONT_SANS = 'Segoe UI'
FONT_MONO = 'Consolas'

for candidate in ['Segoe UI', 'DejaVu Sans', 'Arial', 'Calibri']:
    try:
        import matplotlib.font_manager as fm
        if any(f.name == candidate for f in fm.fontManager.ttflist):
            FONT_SANS = candidate
            break
    except:
        pass

for candidate in ['Consolas', 'DejaVu Sans Mono', 'Courier New']:
    try:
        if any(f.name == candidate for f in fm.fontManager.ttflist):
            FONT_MONO = candidate
            break
    except:
        pass

plt.rcParams['font.family'] = FONT_SANS
plt.rcParams['font.sans-serif'] = [FONT_SANS, 'DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

print(f"  Using fonts: {FONT_SANS} / {FONT_MONO}")

# ── COLOR PALETTE ─────────────────────────────────────────
BG = '#FFFFFF'
BG_SOFT = '#F7FAFE'
BG_CARD = '#F0F6FC'
BLUE = '#2B7CD4'
BLUE_LIGHT = '#D6E9F8'
BLUE_DARK = '#1A5276'
TEAL = '#0CA4A5'
TEAL_LIGHT = '#D4F1F0'
GREEN = '#27AE60'
GREEN_LIGHT = '#D5F5E3'
ORANGE = '#E67E22'
ORANGE_LIGHT = '#FDEBD0'
RED = '#E74C3C'
RED_LIGHT = '#FADBD8'
YELLOW = '#F1C40F'
YELLOW_LIGHT = '#FCF3CF'
PURPLE = '#8E44AD'
PURPLE_LIGHT = '#E8DAEF'
DARK = '#2C3E50'
GRAY = '#7F8C8D'
LIGHT_GRAY = '#BDC3C7'
VERY_LIGHT = '#ECF0F1'
PHONE_BODY_DARK = '#2A2A2E'
PHONE_BODY_BEZEL = '#1A1A1E'
SCREEN_BG = '#FAFCFE'


# ── EASING FUNCTIONS ──────────────────────────────────────
def ease_out_cubic(t):
    """Decelerate smoothly."""
    return 1 - (1 - t) ** 3

def ease_in_out_cubic(t):
    """Smooth S-curve."""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - (-2 * t + 2) ** 3 / 2

def ease_out_back(t):
    """Overshoot then settle (pop-in effect)."""
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def ease_out_elastic(t):
    """Elastic bounce for pop-in."""
    if t == 0 or t == 1:
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1

def lerp(a, b, t):
    """Linear interpolation."""
    return a + (b - a) * max(0, min(1, t))


def fig_to_pil(fig, dpi=150):
    """Convert matplotlib figure to PIL Image with high quality."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none', pad_inches=0.12)
    buf.seek(0)
    img = Image.open(buf).copy()
    buf.close()
    return img


def add_drop_shadow(img, offset=(4, 4), blur_radius=8, shadow_color=(0, 0, 0, 40)):
    """Add subtle drop shadow to an image (for cards)."""
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    # Create shadow only on non-transparent areas
    return img  # Simplified for GIF compatibility


# ══════════════════════════════════════════════════════════
# GIF 1: TWO PHONES SIDE BY SIDE (Realistic, Animated)
# ══════════════════════════════════════════════════════════

def draw_rounded_rect(ax, x, y, w, h, radius=0.15, **kwargs):
    """Draw a properly rounded rectangle using a path."""
    verts = []
    codes = []
    # Build rounded rectangle path
    r = min(radius, w/2, h/2)
    # Bottom-left
    verts += [(x + r, y), (x, y), (x, y + r)]
    codes += [mpath.Path.MOVETO, mpath.Path.CURVE3, mpath.Path.CURVE3]
    # Left side up
    verts += [(x, y + h - r)]
    codes += [mpath.Path.LINETO]
    # Top-left
    verts += [(x, y + h), (x + r, y + h)]
    codes += [mpath.Path.CURVE3, mpath.Path.CURVE3]
    # Top side right
    verts += [(x + w - r, y + h)]
    codes += [mpath.Path.LINETO]
    # Top-right
    verts += [(x + w, y + h), (x + w, y + h - r)]
    codes += [mpath.Path.CURVE3, mpath.Path.CURVE3]
    # Right side down
    verts += [(x + w, y + r)]
    codes += [mpath.Path.LINETO]
    # Bottom-right
    verts += [(x + w, y), (x + w - r, y)]
    codes += [mpath.Path.CURVE3, mpath.Path.CURVE3]
    # Close
    verts += [(x + r, y)]
    codes += [mpath.Path.CLOSEPOLY]

    path = mpath.Path(verts, codes)
    patch = PathPatch(path, **kwargs)
    ax.add_patch(patch)
    return patch


def draw_keypad_phone_v3(ax, x_off, y_off, sms_progress=0.0, sms_text_full="", frame=0):
    """Draw a realistic keypad phone with letter-by-letter SMS."""
    pw, ph = 3.0, 6.2

    # Phone body with shadow effect
    shadow = FancyBboxPatch((x_off + 0.06, y_off - 0.06), pw, ph,
                             boxstyle="round,pad=0.22",
                             facecolor='#00000015', edgecolor='none', zorder=1)
    ax.add_patch(shadow)

    # Main body
    draw_rounded_rect(ax, x_off, y_off, pw, ph, radius=0.25,
                      facecolor='#3C3C40', edgecolor='#2A2A2E', linewidth=2.5, zorder=2)

    # Inner bevel (subtle gradient effect)
    draw_rounded_rect(ax, x_off + 0.06, y_off + 0.06, pw - 0.12, ph - 0.12, radius=0.2,
                      facecolor='#4A4A4E', edgecolor='none', zorder=2.1)

    # Speaker grille (realistic dots pattern)
    for i in range(7):
        for j in range(2):
            cx = x_off + pw/2 - 0.27 + i * 0.09
            cy = y_off + ph - 0.22 + j * 0.07
            dot = Circle((cx, cy), 0.02, facecolor='#555', edgecolor='none', zorder=3)
            ax.add_patch(dot)

    # Brand name
    ax.text(x_off + pw/2, y_off + ph - 0.42, 'NOKIA', fontsize=4.5,
            color='#888', ha='center', va='center', fontweight='bold',
            fontfamily=FONT_SANS, zorder=3)

    # Screen area - green-tinted LCD
    sx, sy = x_off + 0.35, y_off + 3.5
    sw, sh = pw - 0.7, 2.25
    # Screen bezel
    draw_rounded_rect(ax, sx - 0.05, sy - 0.05, sw + 0.1, sh + 0.1, radius=0.08,
                      facecolor='#555', edgecolor='#444', linewidth=1, zorder=2.5)
    # Screen itself
    draw_rounded_rect(ax, sx, sy, sw, sh, radius=0.06,
                      facecolor='#B8D8B0', edgecolor='#90B888', linewidth=0.5, zorder=3)

    # Screen content
    if sms_progress > 0 and sms_text_full:
        total_chars = len(sms_text_full)
        chars_shown = int(sms_progress * total_chars)
        visible_text = sms_text_full[:chars_shown]
        lines = visible_text.split('\n')

        for i, line in enumerate(lines):
            if i > 7:
                break
            y_pos = sy + sh - 0.22 - i * 0.28
            if y_pos < sy + 0.1:
                break
            color = '#1B5E20'
            fs = 5.0
            if 'UNSAFE' in line or 'DO NOT' in line:
                color = '#8B0000'
                fs = 5.2
            elif line.startswith('SAFE') or line == 'Status: SAFE':
                color = '#1B5E20'
                fs = 5.2
            ax.text(sx + 0.1, y_pos, line,
                    fontsize=fs, color=color, fontfamily=FONT_MONO,
                    ha='left', va='top', clip_on=True, zorder=4)

        # Blinking cursor at end
        if chars_shown < total_chars and frame % 6 < 3:
            cursor_line = len(lines) - 1
            cursor_x = sx + 0.1 + len(lines[-1]) * 0.067
            cursor_y = sy + sh - 0.22 - cursor_line * 0.28
            ax.plot([cursor_x, cursor_x], [cursor_y - 0.15, cursor_y + 0.02],
                    color='#1B5E20', linewidth=1.5, zorder=4)
    else:
        # Idle screen
        ax.text(sx + sw/2, sy + sh/2 + 0.4, '12:30',
                fontsize=14, color='#2E7D32', ha='center', va='center',
                fontfamily=FONT_MONO, fontweight='bold', zorder=4)
        ax.text(sx + sw/2, sy + sh/2 - 0.15, 'JalSakhi SMS',
                fontsize=5.5, color='#4CAF50', ha='center', va='center', zorder=4)
        # Signal bars
        for i in range(4):
            bar_h = 0.06 + i * 0.04
            ax.add_patch(Rectangle((sx + sw - 0.5 + i * 0.1, sy + sh - 0.1 - bar_h),
                                   0.06, bar_h, facecolor='#2E7D32', zorder=4))

    # D-pad area
    nav_cx, nav_cy = x_off + pw/2, y_off + 2.95

    # D-pad ring
    ring = Circle((nav_cx, nav_cy), 0.42, facecolor='#555',
                  edgecolor='#444', linewidth=1.5, zorder=3)
    ax.add_patch(ring)
    # Center button
    center = Circle((nav_cx, nav_cy), 0.18, facecolor='#6A6A6E',
                     edgecolor='#555', linewidth=1, zorder=3.1)
    ax.add_patch(center)
    # Arrow indicators
    arrows = [(0, 0.3, '^'), (0, -0.3, 'v'), (-0.3, 0, '<'), (0.3, 0, '>')]
    for dx, dy, marker in arrows:
        ax.plot(nav_cx + dx, nav_cy + dy, marker=marker, color='#888',
                markersize=3, zorder=3.2)

    # Call / End buttons
    call_btn = FancyBboxPatch((x_off + 0.3, y_off + 2.18), 0.9, 0.4,
                               boxstyle="round,pad=0.08",
                               facecolor='#2E7D32', edgecolor='#1B5E20',
                               linewidth=1, zorder=3)
    ax.add_patch(call_btn)
    ax.text(x_off + 0.75, y_off + 2.38, 'CALL', fontsize=4,
            color='white', ha='center', va='center', fontweight='bold', zorder=4)

    end_btn = FancyBboxPatch((x_off + pw - 1.2, y_off + 2.18), 0.9, 0.4,
                              boxstyle="round,pad=0.08",
                              facecolor='#C62828', edgecolor='#B71C1C',
                              linewidth=1, zorder=3)
    ax.add_patch(end_btn)
    ax.text(x_off + pw - 0.75, y_off + 2.38, 'END', fontsize=4,
            color='white', ha='center', va='center', fontweight='bold', zorder=4)

    # Keypad with T9 labels
    keys = [
        [('1', ''), ('2', 'ABC'), ('3', 'DEF')],
        [('4', 'GHI'), ('5', 'JKL'), ('6', 'MNO')],
        [('7', 'PQRS'), ('8', 'TUV'), ('9', 'WXYZ')],
        [('*', ''), ('0', '+'), ('#', '')]
    ]

    for ri, row in enumerate(keys):
        for ci, (key, sub) in enumerate(row):
            kx = x_off + 0.32 + ci * 0.82
            ky = y_off + 1.65 - ri * 0.42
            btn = FancyBboxPatch((kx, ky), 0.6, 0.34,
                                  boxstyle="round,pad=0.04",
                                  facecolor='#505054', edgecolor='#3A3A3E',
                                  linewidth=0.5, zorder=3)
            ax.add_patch(btn)
            ax.text(kx + 0.3, ky + 0.22, key, fontsize=6, color='#DDD',
                    ha='center', va='center', fontweight='bold', zorder=4)
            if sub:
                ax.text(kx + 0.3, ky + 0.08, sub, fontsize=2.8, color='#999',
                        ha='center', va='center', zorder=4)

    return sx, sy, sw, sh


def draw_smartphone_v3(ax, x_off, y_off, phase='idle', progress=0.0, result_alpha=0.0, ble_pulse=0.0):
    """Draw a realistic modern smartphone with app UI."""
    pw, ph = 3.6, 7.0

    # Shadow
    shadow = FancyBboxPatch((x_off + 0.06, y_off - 0.06), pw, ph,
                             boxstyle="round,pad=0.18",
                             facecolor='#00000018', edgecolor='none', zorder=1)
    ax.add_patch(shadow)

    # Phone body
    draw_rounded_rect(ax, x_off, y_off, pw, ph, radius=0.28,
                      facecolor=PHONE_BODY_DARK, edgecolor=PHONE_BODY_BEZEL,
                      linewidth=2.5, zorder=2)

    # Side buttons (volume, power)
    ax.add_patch(Rectangle((x_off - 0.04, y_off + ph - 2.2), 0.04, 0.5,
                            facecolor='#333', edgecolor='none', zorder=2))
    ax.add_patch(Rectangle((x_off - 0.04, y_off + ph - 2.9), 0.04, 0.5,
                            facecolor='#333', edgecolor='none', zorder=2))
    ax.add_patch(Rectangle((x_off + pw, y_off + ph - 2.5), 0.04, 0.6,
                            facecolor='#333', edgecolor='none', zorder=2))

    # Screen (edge-to-edge with thin bezels)
    sx, sy = x_off + 0.14, y_off + 0.22
    sw, sh = pw - 0.28, ph - 0.40
    draw_rounded_rect(ax, sx, sy, sw, sh, radius=0.16,
                      facecolor=SCREEN_BG, edgecolor='#DDD', linewidth=0.5, zorder=3)

    # Camera punch-hole
    cam = Circle((x_off + pw/2, y_off + ph - 0.30), 0.05,
                  facecolor='#333', edgecolor='#222', linewidth=0.5, zorder=4)
    ax.add_patch(cam)

    # Status bar
    sbar_y = sy + sh - 0.20
    ax.fill_between([sx, sx + sw], [sbar_y], [sy + sh], color='#F0F4F8', zorder=4)
    ax.text(sx + 0.12, sbar_y + 0.10, '2:30 PM', fontsize=4.2,
            color=DARK, ha='left', va='center', fontfamily=FONT_SANS, zorder=5)
    # Battery icon
    ax.add_patch(Rectangle((sx + sw - 0.55, sbar_y + 0.04), 0.35, 0.12,
                            facecolor=GREEN, edgecolor=GRAY, linewidth=0.3, zorder=5))
    ax.text(sx + sw - 0.12, sbar_y + 0.10, '87%', fontsize=3.5,
            color=DARK, ha='right', va='center', zorder=5)
    # WiFi/BLE indicators
    if phase != 'idle':
        ax.text(sx + sw - 0.75, sbar_y + 0.10, 'BLE', fontsize=3.5,
                color=BLUE, ha='right', va='center', fontweight='bold', zorder=5)

    # App header bar
    header_y = sbar_y - 0.38
    header_h = 0.38
    ax.fill_between([sx, sx + sw], [header_y], [header_y + header_h],
                    color=BLUE, zorder=4)

    # Water drop icon (simple)
    drop_x = sx + 0.3
    drop_y = header_y + header_h/2
    ax.plot(drop_x, drop_y + 0.06, 'v', color='white', markersize=5, zorder=5)

    ax.text(sx + 0.55, header_y + header_h/2, 'JalSakhi', fontsize=8,
            color='white', ha='left', va='center', fontweight='bold',
            fontfamily=FONT_SANS, zorder=5)

    # BLE connection status bar
    if phase != 'idle':
        ble_y = header_y - 0.20
        ble_color = TEAL_LIGHT
        pulse_extra = abs(math.sin(ble_pulse * math.pi)) * 0.15 if ble_pulse > 0 else 0
        ax.fill_between([sx + 0.08, sx + sw - 0.08], [ble_y], [ble_y + 0.18],
                        color=ble_color, alpha=0.7 + pulse_extra, zorder=4)

        # BLE icon (zigzag)
        bx = sx + 0.25
        by = ble_y + 0.09
        ax.plot([bx, bx + 0.06, bx - 0.04, bx + 0.06, bx],
                [by - 0.05, by, by, by, by + 0.05],
                color=TEAL, linewidth=1, zorder=5)

        ax.text(sx + sw/2, ble_y + 0.09, 'Potentiostat Connected',
                fontsize=4, color=TEAL, ha='center', va='center',
                fontweight='bold', zorder=5)

    content_top = header_y - (0.45 if phase != 'idle' else 0.25)

    if phase == 'scanning':
        # Smooth voltammogram
        n_plot_pts = 300
        E_plot = np.linspace(sx + 0.15, sx + sw - 0.15, n_plot_pts)
        y_base = content_top - 1.4
        y_sig = np.full_like(E_plot, y_base)

        peak_params = [
            (0.18, 0.50, 0.04), (0.38, 0.80, 0.05),
            (0.58, 0.45, 0.04), (0.78, 0.30, 0.03),
        ]
        for pos_frac, h, w in peak_params:
            pos = sx + 0.15 + (sw - 0.3) * pos_frac
            y_sig += h * np.exp(-((E_plot - pos)**2) / (2 * (w * sw)**2))

        # Smooth progress with easing
        smooth_prog = ease_out_cubic(progress)
        idx = max(1, int(smooth_prog * len(E_plot)))

        # Anti-aliased line
        ax.plot(E_plot[:idx], y_sig[:idx], color=BLUE, linewidth=2.0,
                solid_capstyle='round', antialiased=True, zorder=5)
        ax.fill_between(E_plot[:idx], y_base, y_sig[:idx],
                        color=BLUE_LIGHT, alpha=0.35, zorder=4)

        # Animated scan line
        scan_x = E_plot[idx-1]
        ax.axvline(x=scan_x, ymin=0.28, ymax=0.68, color=ORANGE,
                   linewidth=1, alpha=0.6, linestyle='--', zorder=5)

        # Scan dot
        ax.plot(scan_x, y_sig[idx-1], 'o', color=ORANGE, markersize=5,
                markeredgecolor='white', markeredgewidth=1, zorder=6)

        # Progress bar
        prog_y = content_top - 3.0
        # Background
        draw_rounded_rect(ax, sx + 0.2, prog_y, sw - 0.4, 0.22, radius=0.05,
                          facecolor=VERY_LIGHT, edgecolor='none', zorder=4)
        # Fill
        bar_width = (sw - 0.44) * smooth_prog
        if bar_width > 0.02:
            draw_rounded_rect(ax, sx + 0.22, prog_y + 0.02, bar_width, 0.18, radius=0.04,
                              facecolor=BLUE, edgecolor='none', alpha=0.8, zorder=5)
        ax.text(sx + sw/2, prog_y + 0.11, f'Scanning... {int(progress*100)}%',
                fontsize=4.5, color=DARK, ha='center', va='center',
                fontfamily=FONT_SANS, zorder=6)

        # Method label
        ax.text(sx + sw/2, prog_y - 0.2, 'Differential Pulse Voltammetry',
                fontsize=4, color=GRAY, ha='center', zorder=5)
        ax.text(sx + sw/2, prog_y - 0.4, '47 seconds | 5 contaminants',
                fontsize=3.5, color=LIGHT_GRAY, ha='center', zorder=5)

    elif phase == 'result':
        alpha = ease_out_cubic(result_alpha)

        # Safety badge with icon
        badge_y = content_top - 0.08
        badge = FancyBboxPatch((sx + 0.2, badge_y - 0.38), sw - 0.4, 0.42,
                                boxstyle="round,pad=0.06",
                                facecolor=ORANGE_LIGHT, edgecolor=ORANGE,
                                linewidth=1.2, alpha=alpha, zorder=5)
        ax.add_patch(badge)

        # Warning triangle icon
        ax.text(sx + 0.42, badge_y - 0.17, '!',
                fontsize=7, color=ORANGE, ha='center', va='center',
                fontweight='bold', alpha=alpha, zorder=6)
        ax.text(sx + sw/2 + 0.1, badge_y - 0.17, 'MODERATE RISK',
                fontsize=7, color=ORANGE, ha='center', va='center',
                fontweight='bold', alpha=alpha, fontfamily=FONT_SANS, zorder=6)

        # Contaminant results
        contams = [
            ('NH\u2083 Ammonia', '1.8 mg/L', ORANGE, 0.85, 'WHO: 1.5'),
            ('Pb Lead', '12 ppb', RED, 0.60, 'WHO: 10'),
            ('NO\u2083 Nitrate', '32 mg/L', GREEN, 0.32, 'WHO: 50'),
            ('Fe Iron', '0.4 mg/L', BLUE, 0.67, 'WHO: 0.3'),
            ('F Fluoride', '0.7 mg/L', GREEN, 0.35, 'WHO: 1.5'),
        ]

        for i, (name, val, color, pct, who) in enumerate(contams):
            # Staggered fade-in
            item_alpha = ease_out_cubic(max(0, min(1, (result_alpha - i * 0.08) / 0.5)))
            ry = badge_y - 0.68 - i * 0.52
            ax.text(sx + 0.22, ry, name, fontsize=4.2, color=GRAY,
                    ha='left', alpha=item_alpha, fontfamily=FONT_SANS, zorder=5)
            ax.text(sx + sw - 0.22, ry, val, fontsize=4.8, color=color,
                    ha='right', fontweight='bold', alpha=item_alpha, zorder=5)
            ax.text(sx + sw - 0.22, ry - 0.14, who, fontsize=3, color=LIGHT_GRAY,
                    ha='right', alpha=item_alpha * 0.7, zorder=5)

            # Progress bar
            bar_y = ry - 0.12
            # bg
            ax.fill_between([sx + 0.22, sx + sw - 0.22],
                            [bar_y], [bar_y + 0.06],
                            color=VERY_LIGHT, alpha=item_alpha, zorder=4)
            # fill
            bar_w = (sw - 0.44) * pct * item_alpha
            if bar_w > 0:
                ax.fill_between([sx + 0.22, sx + 0.22 + bar_w],
                                [bar_y], [bar_y + 0.06],
                                color=color, alpha=0.45 * item_alpha, zorder=5)
            # WHO limit marker
            who_x = sx + 0.22 + (sw - 0.44) * min(1.0, pct * 1.2)  # approximate
            ax.plot([who_x], [bar_y + 0.03], '|', color='#333',
                    markersize=4, alpha=item_alpha * 0.5, zorder=6)

        # Treatment box
        treat_y = badge_y - 3.5
        treat_alpha = ease_out_cubic(max(0, min(1, (result_alpha - 0.5) / 0.4)))
        treat = FancyBboxPatch((sx + 0.15, treat_y), sw - 0.3, 0.65,
                                boxstyle="round,pad=0.06",
                                facecolor=ORANGE_LIGHT, edgecolor=ORANGE,
                                linewidth=0.8, alpha=treat_alpha, zorder=5)
        ax.add_patch(treat)
        ax.text(sx + sw/2, treat_y + 0.42, 'Rx: Chlorination',
                fontsize=5, color=ORANGE, ha='center', fontweight='bold',
                alpha=treat_alpha, fontfamily=FONT_SANS, zorder=6)
        ax.text(sx + sw/2, treat_y + 0.2, 'Dose: 13.7 mg/L Cl\u2082',
                fontsize=4.5, color=DARK, ha='center', alpha=treat_alpha, zorder=6)

        # Footer stats
        conf_y = treat_y - 0.22
        ax.text(sx + sw/2, conf_y, 'HIGH confidence  |  47s  |  Offline',
                fontsize=3.5, color=GREEN, ha='center', fontweight='bold',
                alpha=treat_alpha, zorder=5)

    # Bottom navigation bar
    nav_y = sy + 0.05
    ax.fill_between([sx, sx + sw], [nav_y], [nav_y + 0.22], color='#F5F5F5', zorder=4)
    # Nav icons (simplified)
    nav_icons = ['Home', 'Test', 'Map', 'Settings']
    for i, label in enumerate(nav_icons):
        nx = sx + (i + 0.5) * sw / 4
        ax.text(nx, nav_y + 0.11, label, fontsize=3, color=GRAY if i != 1 else BLUE,
                ha='center', va='center', fontweight='bold' if i == 1 else 'normal', zorder=5)

    return sx, sy, sw, sh


def draw_ble_waves(ax, x1, y1, x2, y2, progress, frame):
    """Draw animated BLE connection waves between two points."""
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    n_waves = 3
    for i in range(n_waves):
        wave_phase = (frame * 0.15 + i * 0.33) % 1.0
        wave_alpha = (1 - wave_phase) * 0.4 * progress
        wave_r = 0.2 + wave_phase * 0.6

        # Waves from left phone
        left_cx = x1 + (cx - x1) * 0.3
        arc_l = Arc((left_cx, cy), wave_r, wave_r * 1.5, angle=0,
                     theta1=-60, theta2=60, color=TEAL,
                     linewidth=1.5, alpha=wave_alpha, zorder=8)
        ax.add_patch(arc_l)

        # Waves from right phone
        right_cx = x2 - (x2 - cx) * 0.3
        arc_r = Arc((right_cx, cy), wave_r, wave_r * 1.5, angle=180,
                     theta1=-60, theta2=60, color=BLUE,
                     linewidth=1.5, alpha=wave_alpha, zorder=8)
        ax.add_patch(arc_r)

    # Central BLE icon
    ble_alpha = 0.3 + 0.3 * abs(math.sin(frame * 0.2))
    ble_size = 0.15 + 0.03 * abs(math.sin(frame * 0.15))
    ax.text(cx, cy, 'BLE', fontsize=6, color=BLUE, ha='center', va='center',
            fontweight='bold', alpha=ble_alpha * progress,
            bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                     edgecolor=BLUE, alpha=0.6 * progress),
            zorder=9)


def create_phone_comparison_gif():
    print("Creating phone comparison GIF (v3)...")

    sms_text = (
        "JalSakhi Alert\n"
        "Src: Borewell #3\n"
        "NH3: 1.8 mg/L\n"
        "Status: UNSAFE\n"
        "Pb: 12ppb Fe:0.4\n"
        "Add 18 drops\n"
        "bleach per liter\n"
        "Safe: Sabour 2km"
    )

    frames = []
    n_frames = 85

    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(12, 7))
        fig.set_facecolor(BG)
        ax.set_facecolor(BG)
        ax.set_xlim(-0.5, 15.5)
        ax.set_ylim(-1.2, 9.5)
        ax.axis('off')
        ax.set_aspect('equal')

        # Title with fade-in
        title_alpha = ease_out_cubic(min(1.0, frame / 8))
        ax.text(7.75, 9.0, 'JalSakhi Works For Everyone',
                fontsize=22, color=BLUE_DARK, ha='center', va='center',
                fontweight='bold', fontfamily=FONT_SANS, alpha=title_alpha)
        ax.text(7.75, 8.45, 'Water quality results on any phone - nobody left behind',
                fontsize=10.5, color=GRAY, ha='center', va='center',
                fontfamily=FONT_SANS, alpha=title_alpha)

        # ── LEFT: KEYPAD PHONE ──
        kp_x, kp_y = 1.8, 1.2

        # SMS progress: letter by letter
        if frame < 12:
            sms_prog = 0
        elif frame < 55:
            sms_prog = ease_out_cubic((frame - 12) / 43)
        else:
            sms_prog = 1.0

        draw_keypad_phone_v3(ax, kp_x, kp_y, sms_progress=sms_prog,
                             sms_text_full=sms_text, frame=frame)

        # SMS notification badge
        if 12 <= frame < 55:
            pulse = abs(math.sin(frame * 0.3))
            notif_alpha = 0.7 + 0.3 * pulse
            notif = FancyBboxPatch((kp_x + 2.0, kp_y + 5.5), 1.3, 0.35,
                                    boxstyle="round,pad=0.06",
                                    facecolor=GREEN, edgecolor='white',
                                    linewidth=1, alpha=notif_alpha, zorder=10)
            ax.add_patch(notif)
            ax.text(kp_x + 2.65, kp_y + 5.67, 'New SMS',
                    fontsize=4.5, color='white', ha='center', va='center',
                    fontweight='bold', alpha=notif_alpha, zorder=11)

        # Label
        label_alpha = ease_out_cubic(min(1.0, frame / 10))
        ax.text(kp_x + 1.5, kp_y - 0.35, 'Basic / Keypad Phone',
                fontsize=11, color=DARK, ha='center', fontweight='bold',
                fontfamily=FONT_SANS, alpha=label_alpha)
        ax.text(kp_x + 1.5, kp_y - 0.72, 'Results via SMS',
                fontsize=8.5, color=TEAL, ha='center',
                fontfamily=FONT_SANS, alpha=label_alpha)

        # Feature list (staggered)
        features_kp = [
            'SMS water quality alerts',
            'Nearest safe source directions',
            'Treatment dosage in text',
            'Works without internet'
        ]
        if frame > 55:
            for i, feat in enumerate(features_kp):
                feat_t = max(0, min(1, (frame - 55 - i * 2) / 5))
                feat_alpha = ease_out_cubic(feat_t)
                if feat_alpha > 0.01:
                    fy = -0.05 - i * 0.32
                    # Bullet
                    bullet = Circle((kp_x - 0.05, fy), 0.06,
                                    facecolor=TEAL, alpha=feat_alpha, zorder=5)
                    ax.add_patch(bullet)
                    ax.text(kp_x + 0.15, fy, feat, fontsize=6.5, color=DARK,
                            ha='left', va='center', alpha=feat_alpha,
                            fontfamily=FONT_SANS)

        # ── CENTER: BLE Connection ──
        center_x = 7.75
        ax.text(center_x, 4.5, '+', fontsize=30, color=BLUE, ha='center',
                va='center', fontweight='bold', alpha=0.3)

        # BLE waves animation
        if frame > 8:
            ble_prog = ease_out_cubic(min(1, (frame - 8) / 10))
            draw_ble_waves(ax, kp_x + 3.0, 4.5, 10.2, 4.5, ble_prog, frame)

        # "Same test data" connector
        if frame > 55:
            conn_alpha = ease_out_cubic(min(1, (frame - 55) / 8)) * 0.6
            ax.annotate('', xy=(10.0, 4.5), xytext=(5.5, 4.5),
                        arrowprops=dict(arrowstyle='<->', color=BLUE,
                                       lw=1.8, alpha=conn_alpha))
            ax.text(center_x, 4.95, 'Same test data', fontsize=7.5, color=BLUE,
                    ha='center', alpha=conn_alpha, fontfamily=FONT_SANS,
                    fontweight='bold')

        # ── RIGHT: SMARTPHONE ──
        sp_x, sp_y = 10.2, 1.0

        if frame < 8:
            sp_phase = 'idle'
            sp_progress = 0
            sp_result = 0
        elif frame < 42:
            sp_phase = 'scanning'
            sp_progress = (frame - 8) / 34
            sp_result = 0
        elif frame < 50:
            sp_phase = 'scanning'
            sp_progress = 1.0
            sp_result = 0
        else:
            sp_phase = 'result'
            sp_progress = 1.0
            sp_result = min(1.0, (frame - 50) / 10)

        draw_smartphone_v3(ax, sp_x, sp_y,
                           phase=sp_phase,
                           progress=sp_progress,
                           result_alpha=sp_result,
                           ble_pulse=frame * 0.1)

        # Label
        ax.text(sp_x + 1.8, sp_y - 0.35, 'Smartphone',
                fontsize=11, color=DARK, ha='center', fontweight='bold',
                fontfamily=FONT_SANS, alpha=label_alpha)
        ax.text(sp_x + 1.8, sp_y - 0.72, 'Full JalSakhi App',
                fontsize=8.5, color=BLUE, ha='center',
                fontfamily=FONT_SANS, alpha=label_alpha)

        # Feature list
        features_sp = [
            'Real-time voltammogram display',
            'AI-powered contaminant ID',
            'Treatment dosage calculator',
            'Uploads to community map'
        ]
        if frame > 55:
            for i, feat in enumerate(features_sp):
                feat_t = max(0, min(1, (frame - 55 - i * 2) / 5))
                feat_alpha = ease_out_cubic(feat_t)
                if feat_alpha > 0.01:
                    fy = -0.05 - i * 0.32
                    bullet = Circle((sp_x - 0.05, fy), 0.06,
                                    facecolor=BLUE, alpha=feat_alpha, zorder=5)
                    ax.add_patch(bullet)
                    ax.text(sp_x + 0.15, fy, feat, fontsize=6.5, color=DARK,
                            ha='left', va='center', alpha=feat_alpha,
                            fontfamily=FONT_SANS)

        # Bottom tagline
        if frame > 68:
            tag_t = max(0, min(1, (frame - 68) / 8))
            tag_alpha = ease_out_cubic(tag_t)
            tagline = FancyBboxPatch((2.5, -1.3), 10.5, 0.55,
                                     boxstyle="round,pad=0.08",
                                     facecolor=BLUE_LIGHT, edgecolor=BLUE,
                                     linewidth=1.2, alpha=tag_alpha * 0.8, zorder=8)
            ax.add_patch(tagline)
            ax.text(7.75, -1.03, 'Jal Sakhi tests the water. Everyone gets the result.',
                    fontsize=10, color=BLUE_DARK, ha='center', va='center',
                    fontweight='bold', alpha=tag_alpha, fontfamily=FONT_SANS, zorder=9)

        plt.tight_layout()
        frames.append(fig_to_pil(fig, dpi=130))
        plt.close(fig)

    # Smooth duration curve
    durations = []
    for i in range(n_frames):
        if i < 65:
            durations.append(100)
        elif i < 80:
            durations.append(140)
        else:
            durations.append(160)
    durations[-1] = 3500  # Hold last frame

    out = f"{OUT_DIR}/phones_side_by_side.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    print(f"  Saved: {out} ({len(frames)} frames)")


# ══════════════════════════════════════════════════════════
# GIF 2: VOLTAMMOGRAM SCAN (Professional, Anti-aliased)
# ══════════════════════════════════════════════════════════

def create_voltammogram_gif():
    print("Creating voltammogram animation (v3)...")

    E = np.linspace(-1.2, 0.6, 1200)  # Higher resolution

    # More realistic DPV peaks (sharper, realistic positions)
    peaks = [
        (-0.95, 20, 0.045, 'Lead (Pb)', PURPLE, '12 ppb', 'WHO: 10 ppb'),
        (-0.70, 28, 0.055, 'Arsenic (As)', RED, '8 ppb', 'WHO: 10 ppb'),
        (-0.35, 38, 0.065, 'Ammonia (NH\u2083)', ORANGE, '1.8 mg/L', 'WHO: 1.5'),
        (-0.02, 16, 0.050, 'Nitrate (NO\u2083)', YELLOW, '32 mg/L', 'WHO: 50'),
        (0.28, 24, 0.055, 'Iron (Fe)', TEAL, '0.4 mg/L', 'WHO: 0.3'),
    ]

    # Realistic baseline with slight slope
    baseline = 2.5 + 0.6 * E + 0.15 * np.sin(E * 2.5) + 0.08 * np.cos(E * 5)

    np.random.seed(42)

    def full_signal():
        sig = baseline.copy()
        for pos, h, w, *_ in peaks:
            sig += h * np.exp(-((E - pos)**2) / (2*w**2))
        return sig

    fsig = full_signal()
    frames = []
    n_frames = 80
    scan_frames = 55
    result_frames = 25

    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(10, 5.5))
        fig.set_facecolor(BG)
        ax.set_facecolor(BG_SOFT)

        # Clean axes
        ax.spines['bottom'].set_color(LIGHT_GRAY)
        ax.spines['left'].set_color(LIGHT_GRAY)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors=GRAY, labelsize=8)
        ax.set_xlabel('Potential (V vs Ag/AgCl)', color=GRAY, fontsize=10,
                       fontfamily=FONT_SANS)
        ax.set_ylabel('Current (\u00b5A)', color=GRAY, fontsize=10,
                       fontfamily=FONT_SANS)
        ax.grid(True, alpha=0.15, color=LIGHT_GRAY, linestyle='-')

        if frame < scan_frames:
            # Scanning phase
            raw_progress = (frame + 1) / scan_frames
            progress = ease_in_out_cubic(raw_progress)
            idx = max(1, int(progress * len(E)))
            E_show = E[:idx]
            sig_show = baseline[:idx].copy()

            for pos, h, w, *_ in peaks:
                if E_show[-1] >= pos - 3.5 * w:
                    sig_show += h * np.exp(-((E_show - pos)**2) / (2*w**2))

            # Subtle noise for realism
            noise = np.random.normal(0, 0.18, len(E_show))

            # Anti-aliased smooth line
            ax.plot(E_show, sig_show + noise, color=BLUE, linewidth=2.2,
                    solid_capstyle='round', antialiased=True, zorder=5)
            ax.fill_between(E_show, baseline[:idx], sig_show + noise,
                            color=BLUE_LIGHT, alpha=0.25, zorder=3)

            # Scan line
            ax.axvline(x=E[idx-1], color=ORANGE, linewidth=1.2,
                       alpha=0.5, linestyle='--', zorder=4)

            # Scan dot
            ax.plot(E[idx-1], sig_show[-1] + noise[-1], 'o', color=ORANGE,
                    markersize=7, markeredgecolor='white', markeredgewidth=1.5,
                    zorder=6)

            # Pop-in peak labels (appear as scan passes each peak)
            for pos, h, w, name, color, conc, who in peaks:
                if E_show[-1] >= pos + 2.5 * w:
                    # Calculate pop-in progress
                    label_progress = min(1.0, (E_show[-1] - (pos + 2.5*w)) / (0.15))
                    scale = ease_out_back(label_progress)

                    peak_y = baseline[np.argmin(np.abs(E - pos))] + h
                    label_fs = 8 * scale

                    if label_fs > 1:
                        ax.annotate(name, xy=(pos, peak_y + noise[min(len(noise)-1, np.argmin(np.abs(E_show - pos)))]),
                                    xytext=(pos, peak_y + 4 * scale),
                                    fontsize=label_fs, color=color, fontweight='bold',
                                    ha='center', fontfamily=FONT_SANS,
                                    alpha=min(1, label_progress * 1.2),
                                    arrowprops=dict(arrowstyle='->', color=color,
                                                   lw=1.2 * scale,
                                                   alpha=min(1, label_progress)),
                                    zorder=7)

            # Title with progress
            ax.set_title(f'Differential Pulse Voltammetry  \u2014  Scanning {int(raw_progress*100)}%',
                         color=DARK, fontsize=13, fontweight='bold', pad=12,
                         fontfamily=FONT_SANS)

            # Voltage readout
            ax.text(0.97, 0.94, f'E = {E[idx-1]:.2f} V',
                    transform=ax.transAxes, fontsize=10, color=ORANGE,
                    ha='right', va='top', fontfamily=FONT_MONO,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=ORANGE_LIGHT,
                             edgecolor=ORANGE, alpha=0.9))

            # Progress bar at bottom
            prog_bar_y = -1.5
            ax.fill_between([-1.3, 0.7], [prog_bar_y], [prog_bar_y + 0.8],
                            color=VERY_LIGHT, alpha=0.5, zorder=2)
            ax.fill_between([-1.3, -1.3 + 2.0 * raw_progress],
                            [prog_bar_y + 0.1], [prog_bar_y + 0.7],
                            color=BLUE, alpha=0.15, zorder=2.5)

            # Device icon (small inset)
            dev_x, dev_y = -1.1, 42
            dev_box = FancyBboxPatch((dev_x, dev_y), 0.55, 4,
                                      boxstyle="round,pad=0.06",
                                      facecolor=BG_CARD, edgecolor=LIGHT_GRAY,
                                      linewidth=0.8, zorder=4)
            ax.add_patch(dev_box)
            # Pulsing dot on device
            pulse = abs(math.sin(frame * 0.3))
            ax.plot(dev_x + 0.275, dev_y + 2, 'o', color=GREEN,
                    markersize=4 + 2 * pulse, alpha=0.5 + 0.3 * pulse, zorder=5)
            ax.text(dev_x + 0.275, dev_y + 0.5, 'JalSakhi\nDevice',
                    fontsize=4, color=GRAY, ha='center', va='center', zorder=5)

        else:
            # Results phase
            r_progress = (frame - scan_frames) / result_frames
            noise = np.random.normal(0, 0.18, len(E))
            ax.plot(E, fsig + noise, color=BLUE, linewidth=2.2,
                    solid_capstyle='round', antialiased=True, zorder=5)

            # Color-coded peak fills
            for pos, h, w, name, color, conc, who in peaks:
                peak_y = baseline[np.argmin(np.abs(E - pos))] + h

                # Peak region fill
                pe_mask = (E > pos - 2.8*w) & (E < pos + 2.8*w)
                pe_E = E[pe_mask]
                pe_base = baseline[pe_mask]
                pe_sig = pe_base + h * np.exp(-((pe_E - pos)**2) / (2*w**2))
                fill_alpha = ease_out_cubic(min(1, r_progress * 2)) * 0.2
                ax.fill_between(pe_E, pe_base, pe_sig, alpha=fill_alpha,
                                color=color, zorder=4)

                # Labels with concentrations
                label_alpha = ease_out_cubic(min(1, r_progress * 1.5))
                ax.annotate(f'{name}\n{conc}', xy=(pos, peak_y),
                            xytext=(pos, peak_y + 4),
                            fontsize=8, color=color, fontweight='bold',
                            ha='center', fontfamily=FONT_SANS,
                            alpha=label_alpha,
                            arrowprops=dict(arrowstyle='->', color=color,
                                           lw=1.2, alpha=label_alpha),
                            zorder=7)

            ax.set_title('Scan Complete  \u2014  5 Contaminants Identified',
                         color=GREEN, fontsize=13, fontweight='bold', pad=12,
                         fontfamily=FONT_SANS)

            # Results summary box (fades in)
            r_alpha = ease_out_cubic(min(1, (r_progress - 0.2) / 0.5))
            if r_alpha > 0.01:
                results_text = (
                    "NH\u2083: 1.8 mg/L  |  Pb: 12 ppb  |  As: 8 ppb\n"
                    "NO\u2083: 32 mg/L   |  Fe: 0.4 mg/L"
                )
                ax.text(0.97, 0.94, results_text,
                        transform=ax.transAxes, fontsize=8.5, color=DARK,
                        ha='right', va='top', fontfamily=FONT_MONO, alpha=r_alpha,
                        bbox=dict(boxstyle='round,pad=0.4', facecolor=GREEN_LIGHT,
                                 edgecolor=GREEN, alpha=0.85*r_alpha))

                ax.text(0.97, 0.76, 'Confidence: HIGH  |  47s scan',
                        transform=ax.transAxes, fontsize=8, color=GREEN,
                        ha='right', va='top', fontweight='bold', alpha=r_alpha,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                 edgecolor=GREEN, alpha=0.7*r_alpha))

            # WHO limit markers (dashed lines for exceeded contaminants)
            who_alpha = ease_out_cubic(min(1, (r_progress - 0.4) / 0.4))
            if who_alpha > 0.01:
                # Show WHO limits for exceeded contaminants
                for pos, h, w, name, color, conc, who_text in peaks:
                    if color in [RED, ORANGE]:  # Exceeded
                        peak_baseline = baseline[np.argmin(np.abs(E - pos))]
                        who_y = peak_baseline + h * 0.75  # Approximate WHO level line
                        ax.plot([pos - 3*w, pos + 3*w], [who_y, who_y],
                                '--', color=color, linewidth=1, alpha=who_alpha * 0.6,
                                zorder=6)

        ax.set_xlim(-1.3, 0.7)
        ax.set_ylim(-2, 52)

        # Branding
        ax.text(0.03, 0.94, 'JalSakhi', transform=ax.transAxes,
                fontsize=11, color=BLUE, fontweight='bold', va='top',
                fontfamily=FONT_SANS)
        ax.text(0.03, 0.88, 'Water Quality Analyzer', transform=ax.transAxes,
                fontsize=7, color=LIGHT_GRAY, va='top', fontfamily=FONT_SANS)

        plt.tight_layout()
        frames.append(fig_to_pil(fig, dpi=140))
        plt.close(fig)

    # Duration: faster during scan, slower for results
    durations = []
    for i in range(n_frames):
        if i < scan_frames:
            durations.append(80)
        elif i < n_frames - 3:
            durations.append(160)
        else:
            durations.append(200)
    durations[-1] = 3000

    out = f"{OUT_DIR}/voltammogram_light.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    print(f"  Saved: {out} ({len(frames)} frames)")


# ══════════════════════════════════════════════════════════
# GIF 3: HEATMAP BUILDUP (District map, ripples, villages)
# ══════════════════════════════════════════════════════════

def create_heatmap_gif():
    print("Creating heatmap animation (v3)...")

    np.random.seed(42)

    # Village/location data (realistic Bhagalpur-area names)
    villages = [
        ('Sabour', 25.245, 86.98, 0.15),
        ('Sultanpur', 25.21, 87.05, 0.85),
        ('Nathnagar', 25.26, 87.01, 0.35),
        ('Barari', 25.30, 86.95, 0.20),
        ('Kahalgaon', 25.28, 87.12, 0.45),
        ('Pirpainti', 25.32, 87.08, 0.72),
        ('Gopalpur', 25.22, 86.92, 0.55),
        ('Champanagar', 25.19, 86.99, 0.90),
        ('Jagdishpur', 25.35, 87.02, 0.25),
        ('Naugachia', 25.38, 86.96, 0.30),
        ('Bihpur', 25.24, 87.10, 0.62),
        ('Ismailpur', 25.33, 87.15, 0.40),
    ]

    # Additional random test points
    n_extra = 38
    extra_lats = 25.25 + np.random.normal(0, 0.06, n_extra)
    extra_lngs = 86.98 + np.random.normal(0, 0.08, n_extra)
    extra_contam = np.random.uniform(0.05, 0.45, n_extra)

    # Create hotspots
    for i in range(n_extra):
        d1 = np.sqrt((extra_lats[i] - 25.21)**2 + (extra_lngs[i] - 87.05)**2)
        d2 = np.sqrt((extra_lats[i] - 25.19)**2 + (extra_lngs[i] - 86.99)**2)
        if d1 < 0.05:
            extra_contam[i] = np.random.uniform(0.65, 0.95)
        elif d2 < 0.04:
            extra_contam[i] = np.random.uniform(0.60, 0.90)

    # Combine all points
    all_lats = np.concatenate([[v[1] for v in villages], extra_lats])
    all_lngs = np.concatenate([[v[2] for v in villages], extra_lngs])
    all_contam = np.concatenate([[v[3] for v in villages], extra_contam])
    n_pts = len(all_lats)

    # District boundary (approximate polygon)
    boundary_lats = [25.15, 25.18, 25.22, 25.28, 25.35, 25.40, 25.42,
                     25.40, 25.38, 25.35, 25.30, 25.22, 25.17, 25.15]
    boundary_lngs = [86.88, 86.84, 86.82, 86.84, 86.88, 86.93, 87.00,
                     87.10, 87.16, 87.20, 87.18, 87.14, 87.05, 86.88]

    # Custom colormap: green -> yellow -> orange -> red
    cmap = LinearSegmentedColormap.from_list('water_quality',
        [(0, GREEN), (0.35, '#82E0AA'), (0.5, YELLOW),
         (0.7, ORANGE), (0.85, RED), (1.0, '#922B21')], N=256)

    from scipy.ndimage import gaussian_filter

    frames = []
    n_frames = 65

    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(10, 6.5))
        fig.set_facecolor(BG)
        ax.set_facecolor('#FAFCFE')

        # Number of visible points
        if frame < 40:
            n_vis = int(min(n_pts, max(1, ease_out_cubic((frame + 1) / 40) * n_pts)))
        else:
            n_vis = n_pts

        # District boundary (fades in)
        boundary_alpha = ease_out_cubic(min(1, frame / 15)) * 0.4
        ax.plot(boundary_lngs, boundary_lats, '-', color=BLUE_DARK,
                linewidth=1.5, alpha=boundary_alpha, zorder=2)
        ax.fill(boundary_lngs, boundary_lats, color=BG_CARD, alpha=boundary_alpha * 0.3, zorder=1)

        # Heatmap interpolation (builds up smoothly)
        if n_vis > 8 and frame >= 8:
            grid_res = 100
            lat_g = np.linspace(all_lats.min() - 0.04, all_lats.max() + 0.04, grid_res)
            lng_g = np.linspace(all_lngs.min() - 0.06, all_lngs.max() + 0.06, grid_res)
            LNG, LAT = np.meshgrid(lng_g, lat_g)

            Z = np.zeros_like(LAT)
            W = np.zeros_like(LAT)
            for i in range(n_vis):
                d = np.sqrt((LAT - all_lats[i])**2 + (LNG - all_lngs[i])**2)
                d = np.maximum(d, 0.001)
                weight = 1.0 / d**2.5
                Z += all_contam[i] * weight
                W += weight
            Z = Z / W

            # Smooth interpolation
            sigma = max(1.5, 3.5 - frame * 0.03)  # Gets sharper over time
            Z = gaussian_filter(Z, sigma=sigma)

            # Heatmap alpha builds up
            heat_alpha = ease_out_cubic(min(0.55, (frame - 8) / 20))
            ax.contourf(LNG, LAT, Z, levels=20, cmap=cmap, alpha=heat_alpha, zorder=2)

            # WHO limit contour line
            if frame > 20:
                contour_alpha = ease_out_cubic(min(1, (frame - 20) / 10)) * 0.7
                try:
                    cs = ax.contour(LNG, LAT, Z, levels=[0.5], colors=[RED],
                                    linewidths=2, alpha=contour_alpha, linestyles='--', zorder=3)
                    if frame > 30:
                        ax.clabel(cs, fmt='WHO Limit', fontsize=6, colors=[RED])
                except:
                    pass

        # Plot test points with ripple effect
        for i in range(n_vis):
            c = all_contam[i]
            if c < 0.3:
                color = GREEN
            elif c < 0.5:
                color = YELLOW
            elif c < 0.7:
                color = ORANGE
            else:
                color = RED

            # Ripple effect for newly appearing points
            is_new = (i >= n_vis - 3) and frame < 40
            if is_new and frame > 2:
                # Expanding ripple
                ripple_phase = ((frame * 0.2) % 1.0)
                ripple_r = 0.005 + ripple_phase * 0.015
                ripple = Circle((all_lngs[i], all_lats[i]), ripple_r,
                                facecolor='none', edgecolor=color,
                                linewidth=1.5, alpha=(1 - ripple_phase) * 0.6, zorder=4)
                ax.add_patch(ripple)

            # Main point
            point_alpha = 0.5 if is_new else 0.85
            ax.plot(all_lngs[i], all_lats[i], 'o', color=color,
                    markersize=5 + c * 3, alpha=point_alpha,
                    markeredgecolor='white', markeredgewidth=0.8, zorder=5)

        # Village labels (appear gradually)
        if frame > 15:
            for j, (name, lat, lng, _) in enumerate(villages):
                label_t = max(0, min(1, (frame - 15 - j * 1.5) / 5))
                label_alpha = ease_out_cubic(label_t)
                if label_alpha > 0.05:
                    ax.text(lng + 0.008, lat + 0.008, name,
                            fontsize=5.5, color=DARK, alpha=label_alpha * 0.8,
                            fontfamily=FONT_SANS, fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                                     edgecolor=LIGHT_GRAY, alpha=label_alpha * 0.5),
                            zorder=6)

        # Axes styling
        ax.set_xlim(all_lngs.min() - 0.06, all_lngs.max() + 0.08)
        ax.set_ylim(all_lats.min() - 0.04, all_lats.max() + 0.04)
        ax.spines['bottom'].set_color(LIGHT_GRAY)
        ax.spines['left'].set_color(LIGHT_GRAY)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors=GRAY, labelsize=7)
        ax.set_xlabel('Longitude', color=GRAY, fontsize=9, fontfamily=FONT_SANS)
        ax.set_ylabel('Latitude', color=GRAY, fontsize=9, fontfamily=FONT_SANS)
        ax.grid(True, alpha=0.1, color=LIGHT_GRAY)

        # Title
        if frame < 40:
            ax.set_title(f'Community Water Map  \u2014  {n_vis}/{n_pts} sources tested',
                         color=DARK, fontsize=13, fontweight='bold', pad=12,
                         fontfamily=FONT_SANS)
        else:
            ax.set_title(f'Bhagalpur District Water Intelligence  \u2014  {n_pts} sources',
                         color=BLUE_DARK, fontsize=13, fontweight='bold', pad=12,
                         fontfamily=FONT_SANS)

        # Legend (builds as points appear)
        legend_items = [
            ('Safe (<0.3)', GREEN),
            ('Moderate (0.3-0.5)', YELLOW),
            ('Elevated (0.5-0.7)', ORANGE),
            ('Critical (>0.7)', RED)
        ]
        legend_alpha = ease_out_cubic(min(1, frame / 20))
        for i, (label, color) in enumerate(legend_items):
            show = (frame > i * 5)
            if show:
                ax.plot([], [], 'o', color=color, label=label, markersize=7)
        if frame > 0:
            leg = ax.legend(loc='upper left', fontsize=7, framealpha=0.9 * legend_alpha,
                            edgecolor=LIGHT_GRAY, fancybox=True)
            leg.get_frame().set_facecolor(BG)

        # Stats panel (appears at end)
        if frame >= 40:
            sa = ease_out_cubic(min(1, (frame - 40) / 8))

            # Stats box
            stats_lines = [
                f'Sources > WHO limit: 18.4%',
                f'Hotspot: Sultanpur Block',
                f'Primary: Ammonia, Lead',
                f'Action: 12 hotspots flagged'
            ]
            stats_text = '\n'.join(stats_lines)
            ax.text(0.98, 0.68, stats_text, transform=ax.transAxes,
                    fontsize=7.5, color=DARK, ha='right', va='top', alpha=sa,
                    fontfamily=FONT_SANS,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                             edgecolor=ORANGE, alpha=0.92*sa, linewidth=1.2))

        # Final frame summary
        if frame >= 55:
            final_alpha = ease_out_cubic(min(1, (frame - 55) / 6))
            ax.text(0.98, 0.38, '12 Hotspots Identified\nEmergency alerts sent',
                    transform=ax.transAxes, fontsize=9, color=RED,
                    ha='right', va='top', fontweight='bold', alpha=final_alpha,
                    fontfamily=FONT_SANS,
                    bbox=dict(boxstyle='round,pad=0.4', facecolor=RED_LIGHT,
                             edgecolor=RED, alpha=0.85*final_alpha))

            # WHO limit label
            ax.text(0.98, 0.22, '--- WHO limit boundary',
                    transform=ax.transAxes, fontsize=6.5, color=RED,
                    ha='right', alpha=final_alpha * 0.7, fontfamily=FONT_SANS)

        # Branding
        ax.text(0.02, 0.02, 'JalSakhi Community Intelligence',
                transform=ax.transAxes, fontsize=7, color=BLUE, alpha=0.5,
                fontfamily=FONT_SANS)

        plt.tight_layout()
        frames.append(fig_to_pil(fig, dpi=130))
        plt.close(fig)

    durations = []
    for i in range(n_frames):
        if i < 40:
            durations.append(110)
        elif i < 58:
            durations.append(180)
        else:
            durations.append(200)
    durations[-1] = 3500

    out = f"{OUT_DIR}/heatmap_light.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    print(f"  Saved: {out} ({len(frames)} frames)")


# ══════════════════════════════════════════════════════════
# GIF 4: TREATMENT ADVISORY FLOW (NEW)
# ══════════════════════════════════════════════════════════

def create_treatment_advisory_gif():
    print("Creating treatment advisory GIF (v3)...")

    frames = []
    n_frames = 90

    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        fig.set_facecolor(BG)
        ax.set_facecolor(BG)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6.5)
        ax.axis('off')
        ax.set_aspect('equal')

        # Determine phase
        # Phase 1: 0-20  -> Water sample tested, results appear
        # Phase 2: 20-38 -> AI analyzes contaminants
        # Phase 3: 38-60 -> Treatment recommendation card
        # Phase 4: 60-90 -> Community map with safe source

        # Header (always visible)
        header_alpha = ease_out_cubic(min(1, frame / 5))
        ax.text(5, 6.2, 'JalSakhi Treatment Advisory System',
                fontsize=18, color=BLUE_DARK, ha='center', va='center',
                fontweight='bold', fontfamily=FONT_SANS, alpha=header_alpha)

        # Phase indicator dots
        phases_labels = ['Sample', 'Analysis', 'Treatment', 'Action']
        for i, label in enumerate(phases_labels):
            px = 2.5 + i * 1.67
            current_phase = 0
            if frame >= 60:
                current_phase = 3
            elif frame >= 38:
                current_phase = 2
            elif frame >= 20:
                current_phase = 1

            dot_color = BLUE if i <= current_phase else LIGHT_GRAY
            dot_size = 0.12 if i == current_phase else 0.08

            dot = Circle((px, 5.75), dot_size, facecolor=dot_color,
                          edgecolor='white' if i <= current_phase else LIGHT_GRAY,
                          linewidth=1, zorder=5, alpha=header_alpha)
            ax.add_patch(dot)
            ax.text(px, 5.55, label, fontsize=6, color=dot_color,
                    ha='center', va='center', fontfamily=FONT_SANS,
                    alpha=header_alpha, fontweight='bold' if i == current_phase else 'normal')

            # Connecting line
            if i < 3:
                line_color = BLUE if i < current_phase else LIGHT_GRAY
                ax.plot([px + 0.15, px + 1.52], [5.75, 5.75], '-',
                        color=line_color, linewidth=1.5, alpha=header_alpha * 0.5, zorder=4)

        # ── PHASE 1: Sample Results ──
        if frame < 30:
            phase1_alpha = ease_out_cubic(min(1, frame / 8))

            # Test tube / sample icon
            sample_x, sample_y = 1.5, 3.8
            # Beaker shape
            ax.add_patch(FancyBboxPatch((sample_x - 0.4, sample_y - 0.8), 0.8, 1.2,
                                         boxstyle="round,pad=0.08",
                                         facecolor=BLUE_LIGHT, edgecolor=BLUE,
                                         linewidth=1.5, alpha=phase1_alpha, zorder=3))
            # Water level (animated)
            water_h = 0.6 + 0.1 * math.sin(frame * 0.3)
            ax.fill_between([sample_x - 0.3, sample_x + 0.3],
                            [sample_y - 0.7], [sample_y - 0.7 + water_h],
                            color=BLUE, alpha=phase1_alpha * 0.3, zorder=4)
            ax.text(sample_x, sample_y + 0.65, 'Sample\nTested',
                    fontsize=7, color=BLUE_DARK, ha='center', va='center',
                    fontfamily=FONT_SANS, fontweight='bold', alpha=phase1_alpha)

            # Results card appearing
            if frame > 5:
                card_alpha = ease_out_cubic(min(1, (frame - 5) / 8))

                # Results card
                card_x, card_y = 3.2, 1.8
                card_w, card_h = 3.6, 3.5
                card = FancyBboxPatch((card_x, card_y), card_w, card_h,
                                      boxstyle="round,pad=0.12",
                                      facecolor='white', edgecolor=LIGHT_GRAY,
                                      linewidth=1.5, alpha=card_alpha, zorder=3)
                ax.add_patch(card)

                # Card header
                ax.fill_between([card_x, card_x + card_w],
                                [card_y + card_h - 0.5], [card_y + card_h],
                                color=BLUE_LIGHT, alpha=card_alpha * 0.6, zorder=4)
                ax.text(card_x + card_w/2, card_y + card_h - 0.25,
                        'Test Results  \u2014  Borewell #3',
                        fontsize=8, color=BLUE_DARK, ha='center', va='center',
                        fontweight='bold', fontfamily=FONT_SANS, alpha=card_alpha, zorder=5)

                # Results rows (staggered appearance)
                results = [
                    ('Ammonia (NH\u2083)', '1.8 mg/L', 'WHO: 1.5', ORANGE, True),
                    ('Lead (Pb)', '15 ppb', 'WHO: 10 ppb', RED, True),
                    ('Nitrate (NO\u2083)', '32 mg/L', 'WHO: 50', GREEN, False),
                    ('Iron (Fe)', '0.4 mg/L', 'WHO: 0.3', ORANGE, True),
                    ('Fluoride (F)', '0.7 mg/L', 'WHO: 1.5', GREEN, False),
                ]

                for i, (name, val, who, color, exceeded) in enumerate(results):
                    row_t = max(0, min(1, (frame - 8 - i * 1.5) / 4))
                    row_alpha = ease_out_cubic(row_t) * card_alpha
                    if row_alpha > 0.02:
                        ry = card_y + card_h - 0.9 - i * 0.55

                        # Status indicator
                        indicator = Circle((card_x + 0.3, ry + 0.1), 0.06,
                                           facecolor=color, alpha=row_alpha, zorder=5)
                        ax.add_patch(indicator)

                        ax.text(card_x + 0.5, ry + 0.1, name, fontsize=6.5,
                                color=DARK, ha='left', va='center', alpha=row_alpha,
                                fontfamily=FONT_SANS, zorder=5)
                        ax.text(card_x + card_w - 0.2, ry + 0.1, val,
                                fontsize=7, color=color, ha='right', va='center',
                                fontweight='bold', alpha=row_alpha, zorder=5)
                        ax.text(card_x + card_w - 0.2, ry - 0.12, who,
                                fontsize=4.5, color=LIGHT_GRAY, ha='right',
                                va='center', alpha=row_alpha * 0.7, zorder=5)

                        # Exceeded marker
                        if exceeded and row_alpha > 0.5:
                            ax.text(card_x + card_w - 0.05, ry + 0.1, '!',
                                    fontsize=8, color=color, ha='left', va='center',
                                    fontweight='bold', alpha=row_alpha * 0.8, zorder=5)

                # Arrow to next phase
                if frame > 18:
                    arrow_alpha = ease_out_cubic(min(1, (frame - 18) / 5)) * 0.6
                    ax.annotate('', xy=(7.8, 3.5), xytext=(7.0, 3.5),
                                arrowprops=dict(arrowstyle='->', color=BLUE,
                                               lw=2, alpha=arrow_alpha), zorder=6)

        # ── PHASE 2: AI Analysis ──
        if 15 <= frame < 50:
            phase2_t = max(0, min(1, (frame - 15) / 8))
            phase2_alpha = ease_out_cubic(phase2_t)

            # AI brain / analysis icon
            ai_x, ai_y = 8.5, 3.8
            # Gear/brain circle
            pulse = abs(math.sin(frame * 0.25))
            gear_r = 0.5 + 0.05 * pulse
            gear = Circle((ai_x, ai_y), gear_r,
                           facecolor=TEAL_LIGHT, edgecolor=TEAL,
                           linewidth=2, alpha=phase2_alpha, zorder=3)
            ax.add_patch(gear)
            ax.text(ai_x, ai_y + 0.05, 'AI', fontsize=14, color=TEAL,
                    ha='center', va='center', fontweight='bold',
                    alpha=phase2_alpha, zorder=4)
            ax.text(ai_x, ai_y - 0.25, 'ML', fontsize=6, color=TEAL,
                    ha='center', va='center', alpha=phase2_alpha * 0.6, zorder=4)

            # Processing text
            if frame >= 20 and frame < 38:
                proc_texts = [
                    'Analyzing contaminant levels...',
                    'Checking WHO/BIS standards...',
                    'Calculating treatment doses...',
                    'Finding nearest safe source...'
                ]
                proc_idx = min(len(proc_texts) - 1, (frame - 20) // 5)
                dots = '.' * ((frame % 4) + 1)
                ax.text(ai_x, ai_y - 0.7, proc_texts[proc_idx],
                        fontsize=5.5, color=TEAL, ha='center',
                        fontfamily=FONT_SANS, alpha=phase2_alpha * 0.8, zorder=4)

                # Spinning dots around the circle
                for dot_i in range(6):
                    angle = frame * 0.15 + dot_i * math.pi / 3
                    dx = math.cos(angle) * 0.7
                    dy = math.sin(angle) * 0.7
                    dot = Circle((ai_x + dx, ai_y + dy), 0.04,
                                  facecolor=TEAL, alpha=phase2_alpha * 0.4, zorder=4)
                    ax.add_patch(dot)

        # ── PHASE 3: Treatment Recommendation ──
        if frame >= 30:
            phase3_t = max(0, min(1, (frame - 30) / 10))
            phase3_alpha = ease_out_cubic(phase3_t)

            # Treatment card
            tc_x, tc_y = 0.5, 0.3
            tc_w, tc_h = 4.8, 4.5

            # Card slides up
            slide_offset = (1 - phase3_alpha) * 1.5
            tc_y_actual = tc_y - slide_offset

            if phase3_alpha > 0.05:
                # Shadow
                shadow = FancyBboxPatch((tc_x + 0.05, tc_y_actual - 0.05), tc_w, tc_h,
                                         boxstyle="round,pad=0.12",
                                         facecolor='#00000010', edgecolor='none',
                                         alpha=phase3_alpha, zorder=2)
                ax.add_patch(shadow)

                card = FancyBboxPatch((tc_x, tc_y_actual), tc_w, tc_h,
                                      boxstyle="round,pad=0.12",
                                      facecolor='white', edgecolor=TEAL,
                                      linewidth=2, alpha=phase3_alpha, zorder=3)
                ax.add_patch(card)

                # Card header
                ax.fill_between([tc_x + 0.12, tc_x + tc_w - 0.12],
                                [tc_y_actual + tc_h - 0.55], [tc_y_actual + tc_h - 0.12],
                                color=TEAL, alpha=phase3_alpha * 0.9, zorder=4)
                ax.text(tc_x + tc_w/2, tc_y_actual + tc_h - 0.35,
                        'Treatment Recommendation',
                        fontsize=10, color='white', ha='center', va='center',
                        fontweight='bold', fontfamily=FONT_SANS,
                        alpha=phase3_alpha, zorder=5)

                # Treatment items
                treatments = [
                    ('Ammonia: 1.8 mg/L', 'Add 2.5 ml bleach per liter',
                     'Chlorination neutralizes NH\u2083', ORANGE, 'Rx'),
                    ('Lead: 15 ppb', 'Use nearest safe source',
                     'Sabour borewell (1.2 km away)', RED, 'Go'),
                    ('Iron: 0.4 mg/L', 'Let water stand 30 min, filter',
                     'Oxidation + cloth filtration', ORANGE, 'DIY'),
                ]

                for i, (contam, action, detail, color, badge_text) in enumerate(treatments):
                    item_t = max(0, min(1, (frame - 35 - i * 4) / 6))
                    item_alpha = ease_out_cubic(item_t) * phase3_alpha

                    if item_alpha > 0.03:
                        iy = tc_y_actual + tc_h - 1.2 - i * 1.25

                        # Item card
                        item_card = FancyBboxPatch((tc_x + 0.2, iy - 0.15), tc_w - 0.4, 1.0,
                                                    boxstyle="round,pad=0.08",
                                                    facecolor=BG_CARD, edgecolor=LIGHT_GRAY,
                                                    linewidth=0.8, alpha=item_alpha, zorder=4)
                        ax.add_patch(item_card)

                        # Badge
                        badge = FancyBboxPatch((tc_x + 0.35, iy + 0.5), 0.5, 0.28,
                                               boxstyle="round,pad=0.04",
                                               facecolor=color, edgecolor='none',
                                               alpha=item_alpha, zorder=5)
                        ax.add_patch(badge)
                        ax.text(tc_x + 0.6, iy + 0.64, badge_text,
                                fontsize=5, color='white', ha='center', va='center',
                                fontweight='bold', alpha=item_alpha, zorder=6)

                        # Contaminant
                        ax.text(tc_x + 1.0, iy + 0.64, contam,
                                fontsize=7, color=color, ha='left', va='center',
                                fontweight='bold', fontfamily=FONT_SANS,
                                alpha=item_alpha, zorder=5)

                        # Arrow
                        ax.text(tc_x + tc_w/2, iy + 0.38, '\u2192  ' + action,
                                fontsize=7, color=DARK, ha='center', va='center',
                                fontfamily=FONT_SANS, fontweight='bold',
                                alpha=item_alpha, zorder=5)

                        # Detail
                        ax.text(tc_x + tc_w/2, iy + 0.12, detail,
                                fontsize=5.5, color=GRAY, ha='center', va='center',
                                fontfamily=FONT_SANS, alpha=item_alpha * 0.8, zorder=5)

        # ── PHASE 4: Community Map ──
        if frame >= 55:
            phase4_t = max(0, min(1, (frame - 55) / 10))
            phase4_alpha = ease_out_cubic(phase4_t)

            # Map card (right side)
            mc_x, mc_y = 5.5, 0.3
            mc_w, mc_h = 4.3, 4.5

            slide_offset = (1 - phase4_alpha) * 1.5

            if phase4_alpha > 0.05:
                mc_y_actual = mc_y - slide_offset

                # Shadow
                shadow = FancyBboxPatch((mc_x + 0.05, mc_y_actual - 0.05), mc_w, mc_h,
                                         boxstyle="round,pad=0.12",
                                         facecolor='#00000010', edgecolor='none',
                                         alpha=phase4_alpha, zorder=2)
                ax.add_patch(shadow)

                card = FancyBboxPatch((mc_x, mc_y_actual), mc_w, mc_h,
                                      boxstyle="round,pad=0.12",
                                      facecolor='white', edgecolor=GREEN,
                                      linewidth=2, alpha=phase4_alpha, zorder=3)
                ax.add_patch(card)

                # Map header
                ax.fill_between([mc_x + 0.12, mc_x + mc_w - 0.12],
                                [mc_y_actual + mc_h - 0.55], [mc_y_actual + mc_h - 0.12],
                                color=GREEN, alpha=phase4_alpha * 0.9, zorder=4)
                ax.text(mc_x + mc_w/2, mc_y_actual + mc_h - 0.35,
                        'Nearest Safe Source',
                        fontsize=10, color='white', ha='center', va='center',
                        fontweight='bold', fontfamily=FONT_SANS,
                        alpha=phase4_alpha, zorder=5)

                # Simplified map area
                map_x = mc_x + 0.3
                map_y = mc_y_actual + 0.5
                map_w = mc_w - 0.6
                map_h = mc_h - 1.8

                # Map background
                map_bg = FancyBboxPatch((map_x, map_y), map_w, map_h,
                                         boxstyle="round,pad=0.06",
                                         facecolor='#E8F5E9', edgecolor=LIGHT_GRAY,
                                         linewidth=0.8, alpha=phase4_alpha, zorder=4)
                ax.add_patch(map_bg)

                # Roads (simple grid)
                road_alpha = phase4_alpha * 0.3
                for ry in np.linspace(map_y + 0.3, map_y + map_h - 0.3, 4):
                    ax.plot([map_x + 0.1, map_x + map_w - 0.1], [ry, ry],
                            '-', color=LIGHT_GRAY, linewidth=0.8, alpha=road_alpha, zorder=4.5)
                for rx in np.linspace(map_x + 0.3, map_x + map_w - 0.3, 3):
                    ax.plot([rx, rx], [map_y + 0.1, map_y + map_h - 0.1],
                            '-', color=LIGHT_GRAY, linewidth=0.8, alpha=road_alpha, zorder=4.5)

                # Current location (red pin)
                cur_x, cur_y = map_x + map_w * 0.3, map_y + map_h * 0.4
                ax.plot(cur_x, cur_y, 'v', color=RED, markersize=12,
                        markeredgecolor='white', markeredgewidth=1.5,
                        alpha=phase4_alpha, zorder=6)
                ax.text(cur_x, cur_y - 0.2, 'You\n(Borewell #3)',
                        fontsize=5, color=RED, ha='center', va='top',
                        fontweight='bold', alpha=phase4_alpha, zorder=6)

                # Safe source (green pin)
                safe_x, safe_y = map_x + map_w * 0.75, map_y + map_h * 0.7
                # Pulsing green
                pulse = abs(math.sin(frame * 0.2))
                ax.plot(safe_x, safe_y, 'v', color=GREEN,
                        markersize=12 + 2 * pulse,
                        markeredgecolor='white', markeredgewidth=1.5,
                        alpha=phase4_alpha, zorder=6)
                ax.text(safe_x, safe_y + 0.18, 'Sabour Borewell',
                        fontsize=5.5, color=GREEN, ha='center', va='bottom',
                        fontweight='bold', alpha=phase4_alpha, zorder=6,
                        bbox=dict(boxstyle='round,pad=0.1', facecolor='white',
                                 edgecolor=GREEN, alpha=phase4_alpha * 0.8))

                # Walking path (dashed)
                if frame > 60:
                    path_t = max(0, min(1, (frame - 60) / 8))
                    path_alpha = ease_out_cubic(path_t) * phase4_alpha

                    # Curved path between locations
                    path_xs = np.linspace(cur_x, safe_x, 20)
                    path_ys = np.linspace(cur_y, safe_y, 20)
                    path_ys += 0.15 * np.sin(np.linspace(0, math.pi, 20))

                    ax.plot(path_xs, path_ys, '--', color=BLUE, linewidth=2,
                            alpha=path_alpha, zorder=5.5)

                    # Distance label
                    mid_x = (cur_x + safe_x) / 2
                    mid_y = (cur_y + safe_y) / 2 + 0.2
                    ax.text(mid_x, mid_y, '1.2 km\n~15 min walk',
                            fontsize=6, color=BLUE, ha='center', va='center',
                            fontweight='bold', alpha=path_alpha,
                            fontfamily=FONT_SANS, zorder=6,
                            bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                                     edgecolor=BLUE, alpha=path_alpha * 0.7))

                # Safe source info
                info_y = mc_y_actual + 0.15
                ax.text(mc_x + mc_w/2, info_y + 0.18,
                        'Pb: <1 ppb | NH\u2083: 0.2 mg/L | Safe',
                        fontsize=5.5, color=GREEN, ha='center', va='center',
                        fontweight='bold', alpha=phase4_alpha * 0.8,
                        fontfamily=FONT_SANS, zorder=5)

        # Branding
        ax.text(0.3, 0.1, 'JalSakhi', fontsize=8, color=BLUE, alpha=0.4,
                fontfamily=FONT_SANS, fontweight='bold')

        plt.tight_layout()
        frames.append(fig_to_pil(fig, dpi=135))
        plt.close(fig)

    # Durations
    durations = []
    for i in range(n_frames):
        if i < 20:
            durations.append(120)
        elif i < 38:
            durations.append(100)
        elif i < 60:
            durations.append(140)
        elif i < 85:
            durations.append(150)
        else:
            durations.append(180)
    durations[-1] = 4000

    out = f"{OUT_DIR}/treatment_advisory.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    print(f"  Saved: {out} ({len(frames)} frames)")


# ── RUN ───────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 55)
    print("  JalSakhi GIF Generator v3 (Competition Grade)")
    print("=" * 55)

    create_phone_comparison_gif()
    create_voltammogram_gif()

    try:
        from scipy.ndimage import gaussian_filter
        create_heatmap_gif()
    except ImportError:
        print("  [WARN] Skipping heatmap (install scipy: pip install scipy)")

    create_treatment_advisory_gif()

    print()
    print("=" * 55)
    print(f"  All GIFs saved to: {OUT_DIR}")
    print("=" * 55)

    # Print file sizes
    for f in ['phones_side_by_side.gif', 'voltammogram_light.gif',
              'heatmap_light.gif', 'treatment_advisory.gif']:
        path = os.path.join(OUT_DIR, f)
        if os.path.exists(path):
            size_kb = os.path.getsize(path) / 1024
            print(f"  {f}: {size_kb:.0f} KB")
