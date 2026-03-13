"""
JalSakhi - Phone UI Mockup Generator
Creates a comparison image showing:
- Old keypad phone (can't run JalSakhi)
- Old smartphone with micro-USB (colorimetric mode only)
- Modern smartphone with USB-C/BLE (full mode)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Arc, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np
from PIL import Image
import io

# Colors
BG_DARK = '#0D1B2A'
BG_PANEL = '#112240'
TEAL = '#00A8B5'
ORANGE = '#FF6B35'
GREEN = '#2EA06A'
RED = '#E83E3E'
WHITE = '#FFFFFF'
GRAY = '#8CB4C9'
DARK_GRAY = '#2D2D2D'


def create_phone_comparison():
    """Create a wide image showing 3 phones side by side."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 7))
    fig.set_facecolor(BG_DARK)

    # ── PHONE 1: OLD KEYPAD PHONE ──
    ax = axes[0]
    ax.set_facecolor(BG_DARK)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 18)
    ax.axis('off')

    # Phone body (taller, thicker)
    phone = FancyBboxPatch((2, 1), 6, 15, boxstyle="round,pad=0.4",
                            facecolor='#2A2A2A', edgecolor='#555555', linewidth=2)
    ax.add_patch(phone)

    # Small screen
    screen = FancyBboxPatch((2.8, 9), 4.4, 5, boxstyle="round,pad=0.15",
                             facecolor='#1A3A1A', edgecolor='#444444', linewidth=1)
    ax.add_patch(screen)

    # Screen content - basic text
    ax.text(5, 13, 'Nokia', fontsize=10, color='#4A8A4A', ha='center',
           va='center', fontfamily='monospace')
    ax.text(5, 12, '12:30', fontsize=14, color='#6ACA6A', ha='center',
           va='center', fontfamily='monospace', fontweight='bold')
    ax.text(5, 10.5, 'Menu  Names', fontsize=7, color='#4A8A4A', ha='center',
           va='center', fontfamily='monospace')

    # Keypad
    keys = [
        ['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', '9'],
        ['*', '0', '#'],
    ]
    for row_i, row in enumerate(keys):
        for col_i, key in enumerate(row):
            x = 3.2 + col_i * 1.5
            y = 7.5 - row_i * 1.3
            circle = Circle((x, y), 0.45, facecolor='#3A3A3A', edgecolor='#555555', linewidth=1)
            ax.add_patch(circle)
            ax.text(x, y, key, fontsize=8, color='#888888', ha='center', va='center')

    # Call/End buttons
    circle_g = Circle((3.5, 8.5), 0.35, facecolor='#1A4A1A', edgecolor='#2A7A2A')
    ax.add_patch(circle_g)
    circle_r = Circle((6.5, 8.5), 0.35, facecolor='#4A1A1A', edgecolor='#7A2A2A')
    ax.add_patch(circle_r)

    # X mark - can't run JalSakhi
    ax.plot([2.5, 7.5], [3, 14], color=RED, linewidth=4, alpha=0.4)
    ax.plot([2.5, 7.5], [14, 3], color=RED, linewidth=4, alpha=0.4)

    # Label
    ax.text(5, 0.3, 'Basic Phone', fontsize=12, color='#666666', ha='center',
           va='bottom', fontweight='bold')

    # Status badge
    badge = FancyBboxPatch((1.5, 16.3), 7, 1.2, boxstyle="round,pad=0.2",
                            facecolor='#3A1A1A', edgecolor=RED, linewidth=1.5, alpha=0.9)
    ax.add_patch(badge)
    ax.text(5, 16.9, 'NOT COMPATIBLE', fontsize=10, color=RED,
           ha='center', va='center', fontweight='bold')

    # ── PHONE 2: OLD SMARTPHONE (MICRO USB) ──
    ax = axes[1]
    ax.set_facecolor(BG_DARK)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 18)
    ax.axis('off')

    # Phone body
    phone = FancyBboxPatch((1.5, 1.5), 7, 14.5, boxstyle="round,pad=0.3",
                            facecolor=DARK_GRAY, edgecolor='#555555', linewidth=2)
    ax.add_patch(phone)

    # Screen
    screen = FancyBboxPatch((1.9, 3), 6.2, 11.5, boxstyle="round,pad=0.1",
                             facecolor=BG_PANEL, edgecolor='#333333', linewidth=1)
    ax.add_patch(screen)

    # Home button
    circle_home = Circle((5, 2.2), 0.5, facecolor='#3A3A3A', edgecolor='#555555', linewidth=1)
    ax.add_patch(circle_home)

    # Screen content - JalSakhi colorimetric mode
    # Status bar
    ax.fill_between([2, 8], [14, 14], [14.3, 14.3], color='#1A3350')
    ax.text(3, 14.15, '10:45', fontsize=6, color=GRAY, ha='left')
    ax.text(7, 14.15, '78%', fontsize=6, color=GRAY, ha='right')

    # App header
    ax.fill_between([2, 8], [13.2, 13.2], [13.8, 13.8], color='#0D2B45')
    ax.text(5, 13.5, 'JalSakhi', fontsize=9, color=TEAL, ha='center', fontweight='bold')

    # Mode indicator
    ax.fill_between([2.5, 7.5], [12.5, 12.5], [12.9, 12.9], color=GREEN, alpha=0.2)
    ax.text(5, 12.7, 'COLORIMETRIC MODE', fontsize=7, color=GREEN, ha='center', fontweight='bold')

    # Camera viewfinder
    cam_box = FancyBboxPatch((2.5, 7.5), 5, 4.5, boxstyle="round,pad=0.1",
                              facecolor='#0A1628', edgecolor=TEAL, linewidth=1, alpha=0.8)
    ax.add_patch(cam_box)

    # Test strip representation in viewfinder
    strip = Rectangle((4, 8), 2, 3.5, facecolor='#EEEEEE', edgecolor='#999999', linewidth=1)
    ax.add_patch(strip)
    # Color pads on strip
    colors_strip = ['#4CAF50', '#FF9800', '#81C784', '#E8F5E9', '#FFF9C4']
    for i, c in enumerate(colors_strip):
        pad = Rectangle((4.3, 8.3 + i * 0.6), 1.4, 0.4, facecolor=c, edgecolor='#CCCCCC', linewidth=0.5)
        ax.add_patch(pad)

    # Calibration card corners
    for cx, cy in [(2.7, 7.7), (7.3, 7.7), (2.7, 11.8), (7.3, 11.8)]:
        ax.plot(cx, cy, 's', color=ORANGE, markersize=5)

    ax.text(5, 7.2, 'Align strip in frame', fontsize=6, color=TEAL, ha='center')

    # Capture button
    cap_btn = Circle((5, 5.5), 0.8, facecolor=TEAL, edgecolor=WHITE, linewidth=2)
    ax.add_patch(cap_btn)
    ax.text(5, 5.5, 'TAP', fontsize=7, color=WHITE, ha='center', va='center', fontweight='bold')

    # Result preview
    ax.text(3, 4.3, 'Last: Safe', fontsize=7, color=GREEN, ha='left', fontweight='bold')
    ax.text(7, 4.3, '30s ago', fontsize=6, color=GRAY, ha='right')

    # Bottom info
    ax.text(5, 3.3, 'Camera + Test Strips + AI', fontsize=6, color=GRAY, ha='center')

    # Label
    ax.text(5, 0.8, 'Older Smartphone', fontsize=12, color=GRAY, ha='center', fontweight='bold')
    ax.text(5, 0.2, '(Any phone with camera)', fontsize=8, color='#5A7A99', ha='center')

    # Status badge
    badge = FancyBboxPatch((0.8, 16.2), 8.4, 1.4, boxstyle="round,pad=0.2",
                            facecolor='#1A3A20', edgecolor=GREEN, linewidth=1.5, alpha=0.9)
    ax.add_patch(badge)
    ax.text(5, 16.9, 'COLORIMETRIC MODE', fontsize=10, color=GREEN,
           ha='center', va='center', fontweight='bold')
    ax.text(5, 16.4, 'Zero hardware needed', fontsize=7, color='#7BC67E', ha='center')

    # ── PHONE 3: MODERN SMARTPHONE (USB-C / BLE) ──
    ax = axes[2]
    ax.set_facecolor(BG_DARK)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 18)
    ax.axis('off')

    # Phone body (modern, thin bezels)
    phone = FancyBboxPatch((1.3, 1.5), 7.4, 15, boxstyle="round,pad=0.3",
                            facecolor='#1A1A1A', edgecolor='#444444', linewidth=2)
    ax.add_patch(phone)

    # Screen (edge-to-edge)
    screen = FancyBboxPatch((1.6, 1.8), 6.8, 14.2, boxstyle="round,pad=0.1",
                             facecolor=BG_PANEL, edgecolor='#222222', linewidth=1)
    ax.add_patch(screen)

    # Camera notch
    notch = Circle((5, 15.6), 0.15, facecolor='#333333', edgecolor='#444444')
    ax.add_patch(notch)

    # Screen content - JalSakhi full mode
    # Status bar
    ax.fill_between([1.8, 8.2], [15, 15], [15.3, 15.3], color='#0D2B45')
    ax.text(2.5, 15.15, '14:30', fontsize=6, color=GRAY)
    ax.text(7.5, 15.15, 'BLE', fontsize=6, color=TEAL, ha='right', fontweight='bold')

    # App header
    ax.fill_between([1.8, 8.2], [14.2, 14.2], [14.8, 14.8], color='#0D2B45')
    ax.text(5, 14.5, 'JalSakhi', fontsize=10, color=TEAL, ha='center', fontweight='bold')

    # BLE Connected indicator
    ax.fill_between([2, 8], [13.5, 13.5], [14, 14], color=TEAL, alpha=0.2)
    ax.text(5, 13.75, 'POTENTIOSTAT CONNECTED (BLE)', fontsize=6, color=TEAL,
           ha='center', fontweight='bold')

    # Real-time voltammogram
    x_volt = np.linspace(2.2, 7.8, 200)
    y_base = 10.5 + np.zeros_like(x_volt)
    y_sig = y_base.copy()
    # Peaks
    for pos, h in [(3.5, 1.5), (4.8, 2.2), (6.0, 1.0), (7.0, 0.8)]:
        y_sig += h * np.exp(-((x_volt - pos)**2) / 0.08)

    ax.plot(x_volt, y_sig, color=TEAL, linewidth=2)
    ax.fill_between(x_volt, y_base, y_sig, color=TEAL, alpha=0.1)

    # Peak labels
    ax.text(3.5, 12.3, 'Pb', fontsize=6, color='#9C27B0', ha='center', fontweight='bold')
    ax.text(4.8, 13, 'NH3', fontsize=6, color=ORANGE, ha='center', fontweight='bold')
    ax.text(6.0, 11.8, 'NO3', fontsize=6, color=GREEN, ha='center', fontweight='bold')
    ax.text(7.0, 11.5, 'Fe', fontsize=6, color=TEAL, ha='center', fontweight='bold')

    ax.text(5, 10, 'Real-time DPV Voltammogram', fontsize=6, color=GRAY, ha='center')

    # Results section
    ax.fill_between([2, 8], [5.5, 5.5], [9.5, 9.5], color='#0D2B45', alpha=0.8)

    # Safety badge
    badge_inner = FancyBboxPatch((2.5, 8.5), 5, 0.8, boxstyle="round,pad=0.1",
                                  facecolor=ORANGE, edgecolor=ORANGE, alpha=0.3)
    ax.add_patch(badge_inner)
    ax.text(5, 8.9, 'MODERATE RISK', fontsize=8, color=ORANGE, ha='center', fontweight='bold')

    # Contaminant list
    contams = [
        ('NH3', '1.8 mg/L', ORANGE),
        ('Pb', '12 ppb', RED),
        ('NO3', '32 mg/L', GREEN),
        ('Fe', '0.4 mg/L', TEAL),
    ]
    for i, (name, val, color) in enumerate(contams):
        y = 8.0 - i * 0.55
        ax.text(2.5, y, name, fontsize=7, color=GRAY, ha='left')
        ax.text(7.5, y, val, fontsize=7, color=color, ha='right', fontweight='bold')
        # Mini bar
        ax.fill_between([4, 6.5], [y-0.12, y-0.12], [y-0.02, y-0.02], color='#1B3A5C')

    # Treatment box
    treat_box = FancyBboxPatch((2, 4), 6, 1.3, boxstyle="round,pad=0.1",
                                facecolor='#1A3350', edgecolor=ORANGE, linewidth=1, alpha=0.8)
    ax.add_patch(treat_box)
    ax.text(5, 5, 'Treatment: Chlorination', fontsize=7, color=ORANGE,
           ha='center', fontweight='bold')
    ax.text(5, 4.5, 'Dose: 13.7 mg/L Cl2', fontsize=7, color=TEAL, ha='center')

    # Confidence & Mode
    ax.text(5, 3.2, 'Confidence: HIGH | 47s | Offline', fontsize=6, color=GREEN, ha='center')
    ax.text(5, 2.6, 'Electrochemical + Colorimetric', fontsize=6, color=GRAY, ha='center')

    # BLE dongle illustration
    dongle_box = FancyBboxPatch((6.5, 0.5), 3.2, 1.2, boxstyle="round,pad=0.2",
                                 facecolor='#1A3350', edgecolor=TEAL, linewidth=1)
    ax.add_patch(dongle_box)
    ax.text(8.1, 1.1, 'BLE Dongle', fontsize=6, color=TEAL, ha='center', fontweight='bold')
    ax.text(8.1, 0.7, 'INR 1,200', fontsize=6, color=GRAY, ha='center')

    # BLE signal waves
    for r in [0.3, 0.5, 0.7]:
        arc = Arc((6.5, 1.1), r*2, r*2, angle=0, theta1=-45, theta2=45,
                 color=TEAL, linewidth=1, alpha=0.5)
        ax.add_patch(arc)

    # Label
    ax.text(5, 0.8, 'Modern Smartphone', fontsize=12, color=WHITE, ha='center', fontweight='bold')
    ax.text(5, 0.2, '(BLE + Full Analysis)', fontsize=8, color=TEAL, ha='center')

    # Status badge
    badge = FancyBboxPatch((0.6, 16.7), 8.8, 1.4, boxstyle="round,pad=0.2",
                            facecolor='#0A2A3A', edgecolor=TEAL, linewidth=2, alpha=0.95)
    ax.add_patch(badge)
    ax.text(5, 17.4, 'FULL MODE', fontsize=11, color=TEAL,
           ha='center', va='center', fontweight='bold')
    ax.text(5, 16.9, 'Electrochemical + Colorimetric + AI', fontsize=7, color=GRAY, ha='center')

    # Title for the whole figure
    fig.suptitle('JalSakhi Works With What You Have', fontsize=18,
                color=WHITE, fontweight='bold', y=0.98)
    fig.text(0.5, 0.93, 'No expensive hardware required - any smartphone becomes a water lab',
            fontsize=10, color=GRAY, ha='center')

    # Arrows showing progression
    fig.text(0.35, 0.5, '>>>', fontsize=20, color=TEAL, ha='center', va='center',
            fontweight='bold', alpha=0.6)
    fig.text(0.67, 0.5, '>>>', fontsize=20, color=TEAL, ha='center', va='center',
            fontweight='bold', alpha=0.6)

    plt.tight_layout(rect=[0, 0.02, 1, 0.92])

    # Save
    out_path = "C:/Users/Ujjwal/JalSakhi/presentation/gifs/phone_comparison.png"
    fig.savefig(out_path, dpi=150, facecolor=BG_DARK, bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)
    print(f"Saved: {out_path}")

    # Also create an animated version showing the scanning
    create_phone_scanning_gif()


def create_phone_scanning_gif():
    """Create an animated GIF of the modern phone doing a live scan."""
    print("Creating phone scanning GIF...")

    frames = []
    n_frames = 60

    for frame_i in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(4.5, 8))
        fig.set_facecolor(BG_DARK)
        ax.set_facecolor(BG_DARK)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 18)
        ax.axis('off')

        # Modern phone body
        phone = FancyBboxPatch((1, 0.8), 8, 16, boxstyle="round,pad=0.35",
                                facecolor='#1A1A1A', edgecolor='#444444', linewidth=2.5)
        ax.add_patch(phone)

        # Screen
        screen = FancyBboxPatch((1.4, 1.2), 7.2, 15, boxstyle="round,pad=0.15",
                                 facecolor=BG_PANEL, edgecolor='#222222', linewidth=1)
        ax.add_patch(screen)

        # Camera notch
        notch = Circle((5, 15.8), 0.12, facecolor='#333333')
        ax.add_patch(notch)

        # Status bar
        ax.fill_between([1.5, 8.5], [15.5, 15.5], [15.8, 15.8], color='#0D2B45')
        ax.text(2.2, 15.65, '14:30', fontsize=6, color=GRAY)

        # BLE indicator (blinking)
        ble_alpha = 0.5 + 0.5 * np.sin(frame_i * 0.3)
        ax.text(7.8, 15.65, 'BLE', fontsize=5, color=TEAL, ha='right',
               fontweight='bold', alpha=ble_alpha)

        # App header
        ax.fill_between([1.5, 8.5], [14.7, 14.7], [15.3, 15.3], color='#0D2B45')
        ax.text(5, 15.0, 'JalSakhi', fontsize=11, color=TEAL, ha='center', fontweight='bold')

        progress = frame_i / n_frames

        if frame_i < 35:
            # SCANNING PHASE
            scan_progress = frame_i / 35

            # Connected badge
            ax.fill_between([2, 8], [14, 14], [14.4, 14.4], color=TEAL, alpha=0.15)
            ax.text(5, 14.2, 'SCANNING... ' + str(int(scan_progress * 100)) + '%',
                   fontsize=7, color=TEAL, ha='center', fontweight='bold')

            # Voltammogram drawing progressively
            E = np.linspace(1.8, 8.2, 300)
            y_base = 10 + np.zeros_like(E)
            y_sig = y_base.copy()

            peaks_data = [
                (3.2, 1.8, 0.08, 'Pb', '#9C27B0'),
                (4.5, 2.5, 0.09, 'NH3', ORANGE),
                (5.8, 1.3, 0.07, 'NO3', GREEN),
                (7.0, 1.0, 0.08, 'Fe', TEAL),
            ]
            for pos, h, w, name, color in peaks_data:
                y_sig += h * np.exp(-((E - pos)**2) / (2 * w**2))

            idx = int(scan_progress * len(E))
            noise = np.random.normal(0, 0.05, idx)

            ax.plot(E[:idx], y_sig[:idx] + noise, color=TEAL, linewidth=2)

            # Scan line
            if idx > 0:
                ax.axvline(x=E[idx-1], color=ORANGE, linewidth=1, alpha=0.5,
                          ymin=0.5, ymax=0.8, linestyle='--')

            # Detected peaks so far
            for pos, h, w, name, color in peaks_data:
                if idx > 0 and E[idx-1] > pos + 2*w:
                    peak_y = 10 + h
                    ax.text(pos, peak_y + 0.5, name, fontsize=7, color=color,
                           ha='center', fontweight='bold',
                           path_effects=[pe.withStroke(linewidth=2, foreground=BG_PANEL)])

            # Axis labels
            ax.text(5, 8.8, 'Potential (V)', fontsize=6, color='#5A7A99', ha='center')
            ax.text(1.6, 11, 'I', fontsize=7, color='#5A7A99', rotation=90)

            # Progress bar
            ax.fill_between([2, 8], [8.2, 8.2], [8.4, 8.4], color='#1B3A5C')
            ax.fill_between([2, 2 + 6*scan_progress], [8.2, 8.2], [8.4, 8.4], color=TEAL)

            # Info box
            ax.fill_between([2, 8], [5, 5], [7.8, 7.8], color='#0D2B45', alpha=0.8)
            ax.text(5, 7.3, 'Electrode: Connected', fontsize=7, color=GREEN, ha='center')
            ax.text(5, 6.7, 'Mode: DPV', fontsize=7, color=GRAY, ha='center')
            ax.text(5, 6.1, f'E = {-1.2 + scan_progress * 1.8:.2f} V', fontsize=8,
                   color=ORANGE, ha='center', fontfamily='monospace')
            ax.text(5, 5.4, f'Temp: 27.3 C', fontsize=7, color=GRAY, ha='center')

            # Bottom - electrode illustration
            ax.fill_between([3, 7], [2, 2], [4.5, 4.5], color='#0A1628', alpha=0.5)
            # Water sample
            ax.fill_between([3.5, 6.5], [2, 2], [3.2, 3.2], color='#1B6B93', alpha=0.3)
            ax.text(5, 2.6, '~ water ~', fontsize=6, color=TEAL, ha='center', alpha=0.5)
            # Electrode
            ax.plot([5, 5], [3.2, 4.2], color='#AAAAAA', linewidth=3)
            ax.plot([4, 4], [3.2, 4.0], color='#888888', linewidth=2)
            ax.plot([6, 6], [3.2, 4.0], color='#888888', linewidth=2)
            ax.text(5, 4.4, 'WE', fontsize=5, color=GRAY, ha='center')
            ax.text(4, 4.2, 'RE', fontsize=5, color=GRAY, ha='center')
            ax.text(6, 4.2, 'CE', fontsize=5, color=GRAY, ha='center')
            ax.text(5, 1.5, 'Dip electrode in sample', fontsize=6, color=GRAY, ha='center')

        elif frame_i < 45:
            # PROCESSING PHASE
            proc = frame_i - 35

            # Full voltammogram (dimmed)
            E = np.linspace(1.8, 8.2, 300)
            y_base = 10 + np.zeros_like(E)
            y_sig = y_base.copy()
            for pos, h, w in [(3.2, 1.8, 0.08), (4.5, 2.5, 0.09), (5.8, 1.3, 0.07), (7.0, 1.0, 0.08)]:
                y_sig += h * np.exp(-((E - pos)**2) / (2 * w**2))
            ax.plot(E, y_sig, color=TEAL, linewidth=1.5, alpha=0.3)

            ax.fill_between([1.5, 8.5], [5, 5], [14, 14], color=BG_PANEL, alpha=0.9)

            ax.text(5, 13, 'Analyzing...', fontsize=14, color=TEAL, ha='center', fontweight='bold')

            # Processing steps
            steps = ['Baseline correction', 'Peak detection', 'Feature extraction',
                    'CNN classification', 'Confidence scoring']
            current = min(proc, len(steps) - 1)
            for i, step in enumerate(steps):
                y = 11.5 - i * 0.8
                if i < current:
                    ax.text(3, y, 'OK', fontsize=7, color=GREEN, ha='center', fontweight='bold')
                    ax.text(4, y, step, fontsize=7, color=GREEN, ha='left')
                elif i == current:
                    ax.text(3, y, '>>', fontsize=7, color=ORANGE, ha='center')
                    ax.text(4, y, step + '...', fontsize=7, color=ORANGE, ha='left')
                else:
                    ax.text(4, y, step, fontsize=7, color='#3A5A7C', ha='left')

            # Spinner animation
            angle = frame_i * 30
            for a_offset in range(0, 360, 45):
                a = np.radians(angle + a_offset)
                alpha = 0.2 + 0.8 * ((a_offset / 360) ** 0.5)
                ax.plot(5 + 0.5*np.cos(a), 7 + 0.5*np.sin(a), 'o',
                       color=TEAL, markersize=3, alpha=alpha)

        else:
            # RESULT PHASE
            reveal = min(1.0, (frame_i - 45) / 5)

            # Small voltammogram at top
            E = np.linspace(2, 8, 200)
            y_base = 13.5 + np.zeros_like(E)
            y_sig = y_base.copy()
            for pos, h, w in [(3.2, 0.6, 0.08), (4.5, 0.8, 0.09), (5.8, 0.4, 0.07), (7.0, 0.3, 0.08)]:
                y_sig += h * np.exp(-((E - pos)**2) / (2 * w**2))
            ax.plot(E, y_sig, color=TEAL, linewidth=1.5, alpha=0.4)

            # Safety badge
            badge_color = ORANGE
            badge_bg = FancyBboxPatch((2, 12), 6, 1.2, boxstyle="round,pad=0.15",
                                      facecolor=ORANGE, edgecolor=ORANGE,
                                      alpha=0.2 * reveal)
            ax.add_patch(badge_bg)
            ax.text(5, 12.6, 'MODERATE RISK', fontsize=12, color=ORANGE,
                   ha='center', fontweight='bold', alpha=reveal)

            # Contaminant results
            contams = [
                ('NH3 (Ammonia)', '1.8 mg/L', 'WHO: 0.5', ORANGE, 0.85),
                ('Pb (Lead)', '12 ppb', 'WHO: 10', RED, 0.6),
                ('NO3 (Nitrate)', '32 mg/L', 'WHO: 50', GREEN, 0.32),
                ('Fe (Iron)', '0.4 mg/L', 'WHO: 0.3', TEAL, 0.67),
                ('As (Arsenic)', '< 5 ppb', 'WHO: 10', GREEN, 0.25),
            ]

            for i, (name, val, limit, color, pct) in enumerate(contams):
                y = 11.0 - i * 1.3
                ax.text(2.2, y, name, fontsize=7, color=GRAY, ha='left', alpha=reveal)
                ax.text(7.8, y, val, fontsize=8, color=color, ha='right',
                       fontweight='bold', alpha=reveal)
                ax.text(7.8, y - 0.4, limit, fontsize=5, color='#5A7A99',
                       ha='right', alpha=reveal)
                # Bar
                ax.fill_between([2.2, 6.5], [y-0.6, y-0.6], [y-0.45, y-0.45],
                               color='#1B3A5C', alpha=reveal)
                bar_end = 2.2 + 4.3 * pct * reveal
                ax.fill_between([2.2, bar_end], [y-0.6, y-0.6], [y-0.45, y-0.45],
                               color=color, alpha=0.6 * reveal)

            # Treatment advisory
            if reveal > 0.5:
                treat = FancyBboxPatch((2, 2.8), 6, 1.5, boxstyle="round,pad=0.15",
                                       facecolor='#1A3350', edgecolor=ORANGE,
                                       linewidth=1, alpha=reveal)
                ax.add_patch(treat)
                ax.text(5, 3.9, 'Breakpoint Chlorination', fontsize=8, color=ORANGE,
                       ha='center', fontweight='bold', alpha=reveal)
                ax.text(5, 3.3, 'Dose: 13.7 mg/L Cl2', fontsize=8, color=TEAL,
                       ha='center', alpha=reveal)

            # Confidence & timing
            if reveal > 0.7:
                ax.text(5, 2.2, 'Confidence: HIGH', fontsize=7, color=GREEN,
                       ha='center', fontweight='bold', alpha=reveal)
                ax.text(5, 1.7, 'Time: 47s | Offline | BLE', fontsize=6,
                       color=GRAY, ha='center', alpha=reveal)

        plt.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, facecolor=BG_DARK,
                   bbox_inches='tight', pad_inches=0.05)
        buf.seek(0)
        img = Image.open(buf).copy()
        buf.close()
        frames.append(img)
        plt.close(fig)

    # Save GIF
    durations = [100] * 35 + [250] * 10 + [150] * 15
    durations[-1] = 3000
    out_path = "C:/Users/Ujjwal/JalSakhi/presentation/gifs/phone_live_scan.gif"
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"Saved: {out_path} ({len(frames)} frames)")


if __name__ == '__main__':
    print("=" * 50)
    print("JalSakhi Phone Mockup Generator")
    print("=" * 50)
    create_phone_comparison()
    print("\nDone! Files in presentation/gifs/")
