"""
JalSakhi - Clean, light-themed GIFs for PPT
1. Phone comparison GIF: Keypad phone (SMS results) + Smartphone (full app) side by side
2. Voltammogram scan animation (light theme)
3. Heatmap buildup animation (light theme)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Arc, Wedge
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as pe
from PIL import Image, ImageDraw, ImageFont
import io
import os

OUT_DIR = "C:/Users/Ujjwal/JalSakhi/presentation/gifs"
os.makedirs(OUT_DIR, exist_ok=True)

# ── LIGHT COLOR PALETTE ───────────────────────────────────
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
DARK = '#2C3E50'
GRAY = '#7F8C8D'
LIGHT_GRAY = '#BDC3C7'
VERY_LIGHT = '#ECF0F1'
PHONE_BODY = '#3C3C3C'
PHONE_LIGHT = '#E8E8E8'
SCREEN_BG = '#FAFCFE'


def fig_to_pil(fig, dpi=130):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none', pad_inches=0.15)
    buf.seek(0)
    img = Image.open(buf).copy()
    buf.close()
    return img


# ══════════════════════════════════════════════════════════
# GIF 1: TWO PHONES SIDE BY SIDE (Animated)
# Left: Keypad phone receiving SMS results
# Right: Smartphone showing full app
# ══════════════════════════════════════════════════════════

def draw_keypad_phone(ax, x_off, y_off, sms_lines=0, sms_text=None):
    """Draw a keypad phone at given offset."""
    pw, ph = 3.2, 6.5

    # Phone body - rounded dark rectangle
    body = FancyBboxPatch((x_off, y_off), pw, ph,
                           boxstyle="round,pad=0.25",
                           facecolor='#4A4A4A', edgecolor='#333333',
                           linewidth=2)
    ax.add_patch(body)

    # Inner bevel
    bevel = FancyBboxPatch((x_off + 0.08, y_off + 0.08), pw - 0.16, ph - 0.16,
                            boxstyle="round,pad=0.2",
                            facecolor='#555555', edgecolor='none')
    ax.add_patch(bevel)

    # Screen (smaller, top half)
    sx, sy = x_off + 0.4, y_off + 3.4
    sw, sh = pw - 0.8, 2.6
    screen = FancyBboxPatch((sx, sy), sw, sh,
                             boxstyle="round,pad=0.08",
                             facecolor='#C8E6C9', edgecolor='#888888',
                             linewidth=1)
    ax.add_patch(screen)

    # Screen content
    if sms_text and sms_lines > 0:
        # Show SMS arriving
        lines = sms_text[:sms_lines]
        for i, line in enumerate(lines):
            color = '#1B5E20'
            fs = 5.5
            if 'UNSAFE' in line or 'DO NOT' in line:
                color = '#B71C1C'
                fs = 6
            elif 'SAFE' in line and 'UNSAFE' not in line:
                color = '#1B5E20'
                fs = 6
            ax.text(sx + 0.15, sy + sh - 0.3 - i * 0.32, line,
                   fontsize=fs, color=color, fontfamily='monospace',
                   ha='left', va='top', clip_on=True)
    else:
        # Idle screen
        ax.text(sx + sw/2, sy + sh/2 + 0.3, '12:30',
               fontsize=12, color='#2E7D32', ha='center', va='center',
               fontfamily='monospace', fontweight='bold')
        ax.text(sx + sw/2, sy + sh/2 - 0.3, 'JalSakhi SMS',
               fontsize=5.5, color='#4CAF50', ha='center', va='center')

    # D-pad / navigation
    nav_cx, nav_cy = x_off + pw/2, y_off + 2.8
    # Center button
    center = Circle((nav_cx, nav_cy), 0.28, facecolor='#666666',
                    edgecolor='#555555', linewidth=1)
    ax.add_patch(center)
    # Arrow buttons
    for dx, dy in [(0, 0.4), (0, -0.4), (-0.4, 0), (0.4, 0)]:
        btn = Circle((nav_cx + dx, nav_cy + dy), 0.15,
                     facecolor='#5A5A5A', edgecolor='#4A4A4A', linewidth=0.5)
        ax.add_patch(btn)

    # Call/end buttons
    call = FancyBboxPatch((x_off + 0.4, y_off + 2.0), 0.9, 0.4,
                           boxstyle="round,pad=0.08",
                           facecolor='#2E7D32', edgecolor='#1B5E20', linewidth=1)
    ax.add_patch(call)
    end = FancyBboxPatch((x_off + pw - 1.3, y_off + 2.0), 0.9, 0.4,
                          boxstyle="round,pad=0.08",
                          facecolor='#C62828', edgecolor='#B71C1C', linewidth=1)
    ax.add_patch(end)

    # Keypad
    keys = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['*', '0', '#']]
    for ri, row in enumerate(keys):
        for ci, key in enumerate(row):
            kx = x_off + 0.45 + ci * 0.85
            ky = y_off + 1.5 - ri * 0.38
            btn = FancyBboxPatch((kx, ky), 0.6, 0.3,
                                  boxstyle="round,pad=0.05",
                                  facecolor='#5A5A5A', edgecolor='#4A4A4A',
                                  linewidth=0.5)
            ax.add_patch(btn)
            ax.text(kx + 0.3, ky + 0.15, key, fontsize=5, color='#CCC',
                   ha='center', va='center')

    # Speaker grille at top
    for i in range(5):
        ax.plot([x_off + pw/2 - 0.3 + i*0.15, x_off + pw/2 - 0.3 + i*0.15],
               [y_off + ph - 0.25, y_off + ph - 0.15], color='#666', linewidth=0.5)

    return sx, sy, sw, sh


def draw_smartphone(ax, x_off, y_off, phase='idle', progress=0.0, result_alpha=0.0):
    """Draw a modern smartphone at given offset."""
    pw, ph = 3.8, 7.2

    # Phone body
    body = FancyBboxPatch((x_off, y_off), pw, ph,
                           boxstyle="round,pad=0.2",
                           facecolor='#2C2C2C', edgecolor='#1A1A1A',
                           linewidth=2.5)
    ax.add_patch(body)

    # Screen (edge-to-edge, thin bezels)
    sx, sy = x_off + 0.18, y_off + 0.35
    sw, sh = pw - 0.36, ph - 0.55
    screen = FancyBboxPatch((sx, sy), sw, sh,
                             boxstyle="round,pad=0.06",
                             facecolor=SCREEN_BG, edgecolor='#CCCCCC',
                             linewidth=0.5)
    ax.add_patch(screen)

    # Camera notch
    notch = Circle((x_off + pw/2, y_off + ph - 0.28), 0.06,
                   facecolor='#444', edgecolor='#333')
    ax.add_patch(notch)

    # Status bar
    ax.fill_between([sx, sx + sw], [sy + sh - 0.22, sy + sh - 0.22],
                   [sy + sh, sy + sh], color='#F0F4F8', zorder=3)
    ax.text(sx + 0.15, sy + sh - 0.12, '2:30 PM', fontsize=4.5,
           color=DARK, ha='left', va='center', zorder=4)
    ax.text(sx + sw - 0.15, sy + sh - 0.12, '87%', fontsize=4.5,
           color=DARK, ha='right', va='center', zorder=4)

    # App header bar
    header_y = sy + sh - 0.55
    ax.fill_between([sx, sx + sw], [header_y, header_y],
                   [header_y + 0.33, header_y + 0.33], color=BLUE, zorder=3)
    ax.text(sx + sw/2, header_y + 0.17, 'JalSakhi', fontsize=7,
           color='white', ha='center', va='center', fontweight='bold', zorder=4)

    # BLE indicator
    if phase != 'idle':
        ble_y = header_y - 0.22
        ax.fill_between([sx + 0.1, sx + sw - 0.1], [ble_y, ble_y],
                       [ble_y + 0.18, ble_y + 0.18], color=TEAL_LIGHT, zorder=3)
        ax.text(sx + sw/2, ble_y + 0.09, 'Potentiostat Connected (BLE)',
               fontsize=4, color=TEAL, ha='center', va='center', fontweight='bold', zorder=4)

    content_top = header_y - 0.5

    if phase == 'scanning':
        # Voltammogram being drawn
        E = np.linspace(sx + 0.2, sx + sw - 0.2, 200)
        y_base = content_top - 1.5
        y_sig = np.full_like(E, y_base)
        for pos_frac, h in [(0.2, 0.6), (0.4, 0.9), (0.6, 0.5), (0.8, 0.35)]:
            pos = sx + 0.2 + (sw - 0.4) * pos_frac
            y_sig += h * np.exp(-((E - pos)**2) / (0.02 * sw**2))

        idx = max(1, int(progress * len(E)))
        ax.plot(E[:idx], y_sig[:idx], color=BLUE, linewidth=1.8, zorder=4)
        ax.fill_between(E[:idx], y_base, y_sig[:idx], color=BLUE_LIGHT, alpha=0.4, zorder=3)

        # Scan line
        ax.axvline(x=E[idx-1], ymin=0.3, ymax=0.75, color=ORANGE,
                  linewidth=0.8, alpha=0.6, linestyle='--', zorder=4)

        # Progress label
        prog_y = content_top - 3.2
        ax.fill_between([sx + 0.3, sx + sw - 0.3], [prog_y, prog_y],
                       [prog_y + 0.22, prog_y + 0.22], color=VERY_LIGHT, zorder=3)
        ax.fill_between([sx + 0.3, sx + 0.3 + (sw - 0.6)*progress],
                       [prog_y, prog_y], [prog_y + 0.22, prog_y + 0.22],
                       color=BLUE, alpha=0.7, zorder=4)
        ax.text(sx + sw/2, prog_y + 0.11, f'Scanning... {int(progress*100)}%',
               fontsize=5, color=DARK, ha='center', va='center', zorder=5)

        # Bottom info
        ax.text(sx + sw/2, prog_y - 0.3, 'Differential Pulse Voltammetry',
               fontsize=4.5, color=GRAY, ha='center', zorder=4)

    elif phase == 'result':
        # Show results card
        alpha = result_alpha

        # Safety badge
        badge_y = content_top - 0.1
        badge = FancyBboxPatch((sx + 0.3, badge_y - 0.35), sw - 0.6, 0.4,
                                boxstyle="round,pad=0.06",
                                facecolor=ORANGE_LIGHT, edgecolor=ORANGE,
                                linewidth=1, alpha=alpha, zorder=4)
        ax.add_patch(badge)
        ax.text(sx + sw/2, badge_y - 0.15, 'MODERATE RISK',
               fontsize=6.5, color=ORANGE, ha='center', va='center',
               fontweight='bold', alpha=alpha, zorder=5)

        # Contaminant rows
        contams = [
            ('NH3 (Ammonia)', '1.8 mg/L', ORANGE, 0.85),
            ('Pb (Lead)', '12 ppb', RED, 0.6),
            ('NO3 (Nitrate)', '32 mg/L', GREEN, 0.32),
            ('Fe (Iron)', '0.4 mg/L', BLUE, 0.67),
            ('F (Fluoride)', '0.7 mg/L', GREEN, 0.35),
        ]

        for i, (name, val, color, pct) in enumerate(contams):
            ry = badge_y - 0.7 - i * 0.55
            ax.text(sx + 0.3, ry, name, fontsize=4.5, color=GRAY,
                   ha='left', alpha=alpha, zorder=4)
            ax.text(sx + sw - 0.3, ry, val, fontsize=5, color=color,
                   ha='right', fontweight='bold', alpha=alpha, zorder=4)

            # Progress bar
            bar_y = ry - 0.15
            ax.fill_between([sx + 0.3, sx + sw - 0.3],
                           [bar_y, bar_y], [bar_y + 0.07, bar_y + 0.07],
                           color=VERY_LIGHT, alpha=alpha, zorder=3)
            bar_w = (sw - 0.6) * pct * alpha
            ax.fill_between([sx + 0.3, sx + 0.3 + bar_w],
                           [bar_y, bar_y], [bar_y + 0.07, bar_y + 0.07],
                           color=color, alpha=0.5 * alpha, zorder=4)

        # Treatment advisory box
        treat_y = badge_y - 4.0
        treat = FancyBboxPatch((sx + 0.2, treat_y), sw - 0.4, 0.7,
                                boxstyle="round,pad=0.06",
                                facecolor=ORANGE_LIGHT, edgecolor=ORANGE,
                                linewidth=0.8, alpha=alpha, zorder=4)
        ax.add_patch(treat)
        ax.text(sx + sw/2, treat_y + 0.45, 'Treatment: Chlorination',
               fontsize=5, color=ORANGE, ha='center', fontweight='bold',
               alpha=alpha, zorder=5)
        ax.text(sx + sw/2, treat_y + 0.2, 'Dose: 13.7 mg/L Cl2',
               fontsize=5, color=DARK, ha='center', alpha=alpha, zorder=5)

        # Confidence
        conf_y = treat_y - 0.3
        ax.text(sx + sw/2, conf_y, 'Confidence: HIGH  |  47s  |  Offline',
               fontsize=4, color=GREEN, ha='center', fontweight='bold',
               alpha=alpha, zorder=4)

    return sx, sy, sw, sh


def create_phone_comparison_gif():
    print("Creating phone comparison GIF...")

    # SMS text lines (appearing one by one)
    sms_lines = [
        "JalSakhi Alert",
        "Source: Borewell #3",
        "NH3: 1.8 mg/L",
        "Status: UNSAFE",
        "Pb: 12ppb Fe:0.4",
        "Treatment: Add 18",
        "drops bleach/liter",
        "Safe src: Sabour 2km",
    ]

    frames = []
    n_frames = 70

    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(11, 6.5))
        fig.set_facecolor(BG)
        ax.set_facecolor(BG)
        ax.set_xlim(-0.5, 15)
        ax.set_ylim(-0.8, 9)
        ax.axis('off')

        # Title
        ax.text(7.25, 8.5, 'JalSakhi Works For Everyone',
               fontsize=20, color=BLUE_DARK, ha='center', va='center',
               fontweight='bold')
        ax.text(7.25, 8.0, 'Water quality results on any phone - nobody is left behind',
               fontsize=10, color=GRAY, ha='center', va='center')

        # ── LEFT: KEYPAD PHONE ──
        kp_x, kp_y = 1.5, 0.8

        # Calculate SMS lines to show
        if frame < 10:
            sms_count = 0
        elif frame < 42:
            sms_count = min(len(sms_lines), (frame - 10) // 4 + 1)
        else:
            sms_count = len(sms_lines)

        draw_keypad_phone(ax, kp_x, kp_y,
                         sms_lines=sms_count,
                         sms_text=sms_lines)

        # SMS notification icon (blinking when receiving)
        if 10 <= frame < 42 and frame % 4 < 2:
            notif = FancyBboxPatch((kp_x + 2.2, kp_y + 5.8), 1.2, 0.35,
                                    boxstyle="round,pad=0.06",
                                    facecolor=GREEN, edgecolor=GREEN, alpha=0.9, zorder=10)
            ax.add_patch(notif)
            ax.text(kp_x + 2.8, kp_y + 5.97, 'SMS', fontsize=5.5,
                   color='white', ha='center', va='center', fontweight='bold', zorder=11)

        # Label
        ax.text(kp_x + 1.6, kp_y - 0.3, 'Basic / Keypad Phone',
               fontsize=11, color=DARK, ha='center', fontweight='bold')
        ax.text(kp_x + 1.6, kp_y - 0.65, 'Results via SMS',
               fontsize=8, color=TEAL, ha='center')

        # Feature list under keypad phone
        features_kp = ['SMS water quality alerts', 'Nearest safe source directions',
                       'Treatment dosage in text', 'Works without internet']
        for i, feat in enumerate(features_kp):
            if frame > 42:
                feat_alpha = min(1.0, (frame - 42 - i*2) / 4)
                if feat_alpha > 0:
                    ax.text(kp_x + 0.1, -0.1 - i * 0.32, feat,
                           fontsize=6.5, color=DARK, ha='left', alpha=max(0, feat_alpha))
                    ax.plot(kp_x - 0.1, -0.1 - i * 0.32, 'o', color=TEAL,
                           markersize=4, alpha=max(0, feat_alpha))

        # ── DIVIDER ──
        # "+" symbol between phones
        ax.text(7.25, 4.2, '+', fontsize=28, color=BLUE, ha='center',
               va='center', fontweight='bold', alpha=0.4)

        # Connecting line showing same data
        if frame > 45:
            conn_alpha = min(0.5, (frame - 45) / 8)
            ax.annotate('', xy=(9.0, 4.5), xytext=(5.5, 4.5),
                       arrowprops=dict(arrowstyle='<->', color=BLUE,
                                      lw=1.5, alpha=conn_alpha))
            ax.text(7.25, 4.85, 'Same test data', fontsize=7, color=BLUE,
                   ha='center', alpha=conn_alpha)

        # ── RIGHT: SMARTPHONE ──
        sp_x, sp_y = 9.0, 0.6

        # Phone phases
        if frame < 8:
            sp_phase = 'idle'
            sp_progress = 0
            sp_result = 0
        elif frame < 35:
            sp_phase = 'scanning'
            sp_progress = (frame - 8) / 27
            sp_result = 0
        elif frame < 42:
            sp_phase = 'scanning'
            sp_progress = 1.0
            sp_result = 0
        else:
            sp_phase = 'result'
            sp_progress = 1.0
            sp_result = min(1.0, (frame - 42) / 6)

        draw_smartphone(ax, sp_x, sp_y,
                       phase=sp_phase,
                       progress=sp_progress,
                       result_alpha=sp_result)

        # Label
        ax.text(sp_x + 1.9, sp_y - 0.3, 'Smartphone',
               fontsize=11, color=DARK, ha='center', fontweight='bold')
        ax.text(sp_x + 1.9, sp_y - 0.65, 'Full JalSakhi App',
               fontsize=8, color=BLUE, ha='center')

        # Feature list under smartphone
        features_sp = ['Real-time voltammogram display', 'AI-powered contaminant ID',
                       'Treatment dosage calculator', 'Uploads to community map']
        for i, feat in enumerate(features_sp):
            if frame > 42:
                feat_alpha = min(1.0, (frame - 42 - i*2) / 4)
                if feat_alpha > 0:
                    ax.text(sp_x + 0.1, -0.1 - i * 0.32, feat,
                           fontsize=6.5, color=DARK, ha='left', alpha=max(0, feat_alpha))
                    ax.plot(sp_x - 0.1, -0.1 - i * 0.32, 'o', color=BLUE,
                           markersize=4, alpha=max(0, feat_alpha))

        # Bottom tagline (appears at end)
        if frame > 55:
            tag_alpha = min(1.0, (frame - 55) / 5)
            tagline = FancyBboxPatch((2, -1.2), 11, 0.55,
                                     boxstyle="round,pad=0.08",
                                     facecolor=BLUE_LIGHT, edgecolor=BLUE,
                                     linewidth=1, alpha=tag_alpha * 0.7)
            ax.add_patch(tagline)
            ax.text(7.5, -0.93, 'Jal Sakhi tests the water. Everyone gets the result.',
                   fontsize=9, color=BLUE_DARK, ha='center', va='center',
                   fontweight='bold', alpha=tag_alpha)

        plt.tight_layout()
        frames.append(fig_to_pil(fig, dpi=120))
        plt.close(fig)

    durations = [120] * 55 + [150] * 15
    durations[-1] = 3000
    out = f"{OUT_DIR}/phones_side_by_side.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    print(f"  Saved: {out} ({len(frames)} frames)")


# ══════════════════════════════════════════════════════════
# GIF 2: VOLTAMMOGRAM SCAN (Light theme)
# ══════════════════════════════════════════════════════════

def create_voltammogram_gif():
    print("Creating voltammogram animation (light)...")

    E = np.linspace(-1.2, 0.6, 1000)
    peaks = [
        (-0.95, 18, 0.06, 'Lead (Pb)', '#8E44AD'),
        (-0.70, 25, 0.07, 'Arsenic (As)', RED),
        (-0.38, 35, 0.08, 'Ammonia (NH3)', ORANGE),
        (-0.05, 15, 0.06, 'Nitrate (NO3)', YELLOW),
        (0.25, 22, 0.07, 'Iron (Fe)', TEAL),
    ]

    baseline = 2 + 0.5 * E + 0.3 * np.sin(E * 3)
    np.random.seed(42)

    def full_signal():
        sig = baseline.copy()
        for pos, h, w, n, c in peaks:
            sig += h * np.exp(-((E - pos)**2) / (2*w**2))
        return sig

    fsig = full_signal()
    frames = []
    n_frames = 65
    scan_f = 48
    result_f = 17

    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(9, 4.5))
        fig.set_facecolor(BG)
        ax.set_facecolor(BG_SOFT)

        ax.spines['bottom'].set_color(LIGHT_GRAY)
        ax.spines['left'].set_color(LIGHT_GRAY)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors=GRAY, labelsize=8)
        ax.set_xlabel('Potential (V vs Ag/AgCl)', color=GRAY, fontsize=9)
        ax.set_ylabel('Current (uA)', color=GRAY, fontsize=9)
        ax.grid(True, alpha=0.2, color=LIGHT_GRAY, linestyle='-')

        if frame < scan_f:
            progress = (frame + 1) / scan_f
            idx = max(1, int(progress * len(E)))
            E_show = E[:idx]
            sig_show = baseline[:idx].copy()
            for pos, h, w, n, c in peaks:
                if E_show[-1] >= pos - 3*w:
                    sig_show += h * np.exp(-((E_show - pos)**2) / (2*w**2))

            noise = np.random.normal(0, 0.25, len(E_show))
            ax.plot(E_show, sig_show + noise, color=BLUE, linewidth=2)
            ax.fill_between(E_show, baseline[:idx], sig_show + noise,
                           color=BLUE_LIGHT, alpha=0.3)

            ax.axvline(x=E[idx-1], color=ORANGE, linewidth=1, alpha=0.5, linestyle='--')

            for pos, h, w, name, color in peaks:
                if E_show[-1] >= pos + 2*w:
                    peak_y = baseline[np.argmin(np.abs(E - pos))] + h
                    ax.annotate(name, xy=(pos, peak_y),
                               xytext=(pos, peak_y + 3),
                               fontsize=7.5, color=color, fontweight='bold',
                               ha='center',
                               arrowprops=dict(arrowstyle='->', color=color, lw=1.2))

            ax.set_title(f'Differential Pulse Voltammetry  -  Scanning {int(progress*100)}%',
                        color=DARK, fontsize=12, fontweight='bold', pad=10)

            ax.text(0.97, 0.93, f'E = {E[idx-1]:.2f} V',
                   transform=ax.transAxes, fontsize=9, color=ORANGE,
                   ha='right', va='top', fontfamily='monospace',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor=ORANGE_LIGHT,
                            edgecolor=ORANGE, alpha=0.9))

        else:
            noise = np.random.normal(0, 0.25, len(E))
            ax.plot(E, fsig + noise, color=BLUE, linewidth=2)

            for pos, h, w, name, color in peaks:
                peak_y = baseline[np.argmin(np.abs(E - pos))] + h
                ax.annotate(name, xy=(pos, peak_y),
                           xytext=(pos, peak_y + 3),
                           fontsize=8, color=color, fontweight='bold', ha='center',
                           arrowprops=dict(arrowstyle='->', color=color, lw=1.2))

                pe_E = E[(E > pos - 2.5*w) & (E < pos + 2.5*w)]
                pe_base = baseline[(E > pos - 2.5*w) & (E < pos + 2.5*w)]
                pe_sig = pe_base + h * np.exp(-((pe_E - pos)**2) / (2*w**2))
                ax.fill_between(pe_E, pe_base, pe_sig, alpha=0.15, color=color)

            ax.set_title('Scan Complete  -  5 Contaminants Identified',
                        color=GREEN, fontsize=12, fontweight='bold', pad=10)

            r_alpha = min(1.0, (frame - scan_f) / 5)
            results_text = "NH3: 1.8 mg/L  |  Pb: 12 ppb  |  As: 8 ppb\nNO3: 32 mg/L  |  Fe: 0.4 mg/L"
            ax.text(0.97, 0.93, results_text,
                   transform=ax.transAxes, fontsize=8, color=DARK,
                   ha='right', va='top', fontfamily='monospace', alpha=r_alpha,
                   bbox=dict(boxstyle='round,pad=0.4', facecolor=GREEN_LIGHT,
                            edgecolor=GREEN, alpha=0.85*r_alpha))

            ax.text(0.97, 0.73, 'Confidence: HIGH',
                   transform=ax.transAxes, fontsize=8, color=GREEN,
                   ha='right', va='top', fontweight='bold', alpha=r_alpha,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                            edgecolor=GREEN, alpha=0.7*r_alpha))

        ax.set_xlim(-1.3, 0.7)
        ax.set_ylim(-2, 48)

        # Branding
        ax.text(0.03, 0.93, 'JalSakhi', transform=ax.transAxes,
               fontsize=10, color=BLUE, fontweight='bold', va='top')

        plt.tight_layout()
        frames.append(fig_to_pil(fig, dpi=120))
        plt.close(fig)

    durations = [90] * scan_f + [180] * result_f
    durations[-1] = 2500
    out = f"{OUT_DIR}/voltammogram_light.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    print(f"  Saved: {out} ({len(frames)} frames)")


# ══════════════════════════════════════════════════════════
# GIF 3: HEATMAP BUILDUP (Light theme)
# ══════════════════════════════════════════════════════════

def create_heatmap_gif():
    print("Creating heatmap animation (light)...")

    np.random.seed(42)
    n_pts = 50
    lats = 25.25 + np.random.normal(0, 0.06, n_pts)
    lngs = 86.98 + np.random.normal(0, 0.1, n_pts)

    contam = np.random.uniform(0.05, 0.35, n_pts)
    hot1 = ((lats - 25.21)**2 + (lngs - 87.05)**2) < 0.003
    contam[hot1] = np.random.uniform(0.7, 1.0, hot1.sum())
    hot2 = ((lats - 25.32)**2 + (lngs - 87.08)**2) < 0.002
    contam[hot2] = np.random.uniform(0.5, 0.75, hot2.sum())

    frames = []
    n_frames = 50

    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list('contam',
        ['#FFFFFF', '#D5F5E3', '#82E0AA', '#F9E79F', '#F5B041', '#E74C3C', '#922B21'], N=256)

    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(8.5, 5.5))
        fig.set_facecolor(BG)
        ax.set_facecolor('#FAFCFE')

        n_vis = int(min(n_pts, max(1, (frame + 1) / 35 * n_pts))) if frame < 35 else n_pts

        # Heatmap interpolation
        if n_vis > 5 and frame >= 5:
            from scipy.ndimage import gaussian_filter
            grid_res = 80
            lat_g = np.linspace(lats.min() - 0.04, lats.max() + 0.04, grid_res)
            lng_g = np.linspace(lngs.min() - 0.06, lngs.max() + 0.06, grid_res)
            LNG, LAT = np.meshgrid(lng_g, lat_g)

            Z = np.zeros_like(LAT)
            for i in range(n_vis):
                d = np.sqrt((LAT - lats[i])**2 + (LNG - lngs[i])**2)
                d = np.maximum(d, 0.001)
                Z += contam[i] / d**2
            total_w = np.zeros_like(LAT)
            for i in range(n_vis):
                d = np.sqrt((LAT - lats[i])**2 + (LNG - lngs[i])**2)
                d = np.maximum(d, 0.001)
                total_w += 1.0 / d**2
            Z = Z / total_w
            Z = gaussian_filter(Z, sigma=2.5)

            ha = min(0.6, (frame - 5) / 12)
            ax.contourf(LNG, LAT, Z, levels=15, cmap=cmap, alpha=ha)
            ax.contour(LNG, LAT, Z, levels=[0.5], colors=[ORANGE], linewidths=1.5,
                      alpha=ha * 0.8, linestyles='--')

        # Plot points
        for i in range(n_vis):
            c = contam[i]
            if c < 0.3: color = GREEN
            elif c < 0.5: color = '#F1C40F'
            elif c < 0.7: color = ORANGE
            else: color = RED

            alpha = 1.0 if not (i >= n_vis - 2 and frame < 35) else 0.5
            ax.plot(lngs[i], lats[i], 'o', color=color, markersize=6,
                   alpha=alpha, markeredgecolor='white', markeredgewidth=0.8, zorder=5)

        ax.set_xlim(lngs.min() - 0.06, lngs.max() + 0.06)
        ax.set_ylim(lats.min() - 0.04, lats.max() + 0.04)
        ax.spines['bottom'].set_color(LIGHT_GRAY)
        ax.spines['left'].set_color(LIGHT_GRAY)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors=GRAY, labelsize=7)
        ax.set_xlabel('Longitude', color=GRAY, fontsize=8)
        ax.set_ylabel('Latitude', color=GRAY, fontsize=8)
        ax.grid(True, alpha=0.15, color=LIGHT_GRAY)

        if frame < 35:
            ax.set_title(f'Community Contamination Map  -  {n_vis}/{n_pts} sources tested',
                        color=DARK, fontsize=12, fontweight='bold', pad=10)
        else:
            ax.set_title(f'Bhagalpur District Water Intelligence  -  {n_pts} sources',
                        color=BLUE_DARK, fontsize=12, fontweight='bold', pad=10)

        # Legend
        legend_items = [('Safe', GREEN), ('Moderate', '#F1C40F'), ('Elevated', ORANGE), ('Critical', RED)]
        for i, (label, color) in enumerate(legend_items):
            ax.plot([], [], 'o', color=color, label=label, markersize=6)
        leg = ax.legend(loc='upper left', fontsize=7, framealpha=0.9,
                       edgecolor=LIGHT_GRAY, fancybox=True)
        leg.get_frame().set_facecolor(BG)

        if frame >= 35:
            sa = min(1.0, (frame - 35) / 5)
            stats = 'Sources > WHO limit: 18.4%\nHotspot: Sultanpur Block\nPrimary concern: Ammonia'
            ax.text(0.98, 0.65, stats, transform=ax.transAxes,
                   fontsize=7.5, color=DARK, ha='right', va='top', alpha=sa,
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                            edgecolor=ORANGE, alpha=0.9*sa))

            # WHO limit contour label
            if frame > 40:
                ax.text(0.98, 0.42, '--- WHO limit boundary',
                       transform=ax.transAxes, fontsize=6.5, color=ORANGE,
                       ha='right', alpha=min(1, (frame-40)/5))

        ax.text(0.02, 0.02, 'JalSakhi Community Intelligence',
               transform=ax.transAxes, fontsize=7, color=BLUE, alpha=0.6)

        plt.tight_layout()
        frames.append(fig_to_pil(fig, dpi=115))
        plt.close(fig)

    durations = [130] * 35 + [200] * 15
    durations[-1] = 3000
    out = f"{OUT_DIR}/heatmap_light.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    print(f"  Saved: {out} ({len(frames)} frames)")


# ── RUN ───────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 50)
    print("JalSakhi GIF Generator v2 (Light Theme)")
    print("=" * 50)
    create_phone_comparison_gif()
    create_voltammogram_gif()
    try:
        from scipy.ndimage import gaussian_filter
        create_heatmap_gif()
    except ImportError:
        print("  Skipping heatmap (install scipy)")
    print("\nDone! All GIFs in:", OUT_DIR)
