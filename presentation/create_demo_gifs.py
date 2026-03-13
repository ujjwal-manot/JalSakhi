"""
JalSakhi - Create animated demo GIFs for PPT embedding
1. Voltammogram animation (electrochemical scan)
2. Colorimetric analysis pipeline animation
3. Real-time classification result animation
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import matplotlib.patheffects as pe
from PIL import Image, ImageDraw, ImageFont
import io
import os

OUT_DIR = "C:/Users/Ujjwal/JalSakhi/presentation/gifs"
os.makedirs(OUT_DIR, exist_ok=True)

# ── COLOR SCHEME ──────────────────────────────────────────
BG_DARK = '#0D1B2A'
BG_PANEL = '#112240'
TEAL = '#00A8B5'
WATER_BLUE = '#1B6B93'
ORANGE = '#FF6B35'
GREEN = '#2EA06A'
RED = '#E83E3E'
YELLOW = '#FFD700'
WHITE = '#FFFFFF'
GRAY = '#8CB4C9'
DARK_TEXT = '#E0E0E0'


def fig_to_pil(fig, dpi=120):
    """Convert matplotlib figure to PIL Image."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none', pad_inches=0.1)
    buf.seek(0)
    img = Image.open(buf).copy()
    buf.close()
    return img


# ══════════════════════════════════════════════════════════
# GIF 1: ANIMATED VOLTAMMOGRAM
# Shows DPV scan with peaks appearing for contaminants
# ══════════════════════════════════════════════════════════
def create_voltammogram_gif():
    print("Creating voltammogram animation...")

    # Voltage range for DPV
    E = np.linspace(-1.2, 0.6, 1000)

    # Contaminant peaks (position, height, width, name, color)
    peaks = [
        (-0.95, 18, 0.06, 'Pb (Lead)', '#9C27B0'),
        (-0.70, 25, 0.07, 'As (Arsenic)', '#E83E3E'),
        (-0.38, 35, 0.08, 'NH3 (Ammonia)', ORANGE),
        (-0.05, 15, 0.06, 'NO3 (Nitrate)', YELLOW),
        (0.25, 22, 0.07, 'Fe (Iron)', TEAL),
    ]

    # Baseline (slight slope + noise seed)
    np.random.seed(42)
    baseline = 2 + 0.5 * E + 0.3 * np.sin(E * 3)

    # Full signal
    def get_signal(E, peaks_to_include):
        signal = baseline.copy()
        for pos, height, width, name, color in peaks[:peaks_to_include]:
            signal += height * np.exp(-((E - pos) ** 2) / (2 * width ** 2))
        return signal

    full_signal = get_signal(E, len(peaks))

    frames = []
    n_frames = 80
    scan_frames = 60  # frames for the scan sweep
    result_frames = 20  # frames for showing results

    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(8, 4.5))
        fig.set_facecolor(BG_DARK)
        ax.set_facecolor(BG_PANEL)

        # Style the axes
        ax.spines['bottom'].set_color(GRAY)
        ax.spines['left'].set_color(GRAY)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors=GRAY, labelsize=8)
        ax.set_xlabel('Potential (V vs Ag/AgCl)', color=GRAY, fontsize=9)
        ax.set_ylabel('Current (uA)', color=GRAY, fontsize=9)

        if frame < scan_frames:
            # Scanning phase - draw signal progressively
            progress = (frame + 1) / scan_frames
            idx = int(progress * len(E))

            # Draw completed part of scan
            E_show = E[:idx]
            # Calculate how many peaks are visible at this point
            signal_show = baseline[:idx].copy()
            for pos, height, width, name, color in peaks:
                if E_show[-1] >= pos - 3 * width:
                    signal_show += height * np.exp(-((E_show - pos) ** 2) / (2 * width ** 2))

            # Add subtle noise
            noise = np.random.normal(0, 0.3, len(E_show))
            signal_noisy = signal_show + noise

            ax.plot(E_show, signal_noisy, color=TEAL, linewidth=1.5, alpha=0.9)

            # Scan line indicator
            ax.axvline(x=E[idx-1], color=ORANGE, linewidth=1, alpha=0.6, linestyle='--')

            # Label detected peaks so far
            for pos, height, width, name, color in peaks:
                if E_show[-1] >= pos + 2 * width:
                    peak_y = baseline[np.argmin(np.abs(E - pos))] + height
                    ax.annotate(name, xy=(pos, peak_y + 1),
                               fontsize=7, color=color, fontweight='bold',
                               ha='center', va='bottom',
                               path_effects=[pe.withStroke(linewidth=2, foreground=BG_DARK)])
                    ax.plot(pos, peak_y, 'v', color=color, markersize=6, alpha=0.8)

            # Title with scan progress
            ax.set_title(f'Differential Pulse Voltammetry - Scanning... {int(progress*100)}%',
                        color=WHITE, fontsize=11, fontweight='bold', pad=10)

            # Voltage readout
            ax.text(0.98, 0.95, f'E = {E[idx-1]:.2f} V',
                   transform=ax.transAxes, fontsize=9, color=ORANGE,
                   ha='right', va='top', fontfamily='monospace',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor=BG_DARK, edgecolor=ORANGE, alpha=0.8))

        else:
            # Results phase - full scan + classification results
            noise = np.random.normal(0, 0.3, len(E))
            ax.plot(E, full_signal + noise, color=TEAL, linewidth=1.5, alpha=0.9)

            # Highlight all peaks
            for pos, height, width, name, color in peaks:
                peak_y = baseline[np.argmin(np.abs(E - pos))] + height
                ax.annotate(name, xy=(pos, peak_y + 1),
                           fontsize=8, color=color, fontweight='bold',
                           ha='center', va='bottom',
                           path_effects=[pe.withStroke(linewidth=2, foreground=BG_DARK)])
                ax.plot(pos, peak_y, 'v', color=color, markersize=7)

                # Shade peak area
                peak_E = E[(E > pos - 2.5*width) & (E < pos + 2.5*width)]
                peak_base = baseline[(E > pos - 2.5*width) & (E < pos + 2.5*width)]
                peak_sig = peak_base + height * np.exp(-((peak_E - pos) ** 2) / (2 * width ** 2))
                ax.fill_between(peak_E, peak_base, peak_sig, alpha=0.15, color=color)

            ax.set_title('Scan Complete - 5 Contaminants Detected',
                        color=GREEN, fontsize=11, fontweight='bold', pad=10)

            # Classification result box
            result_alpha = min(1.0, (frame - scan_frames) / 5)
            results_text = "NH3: 1.8 mg/L | Pb: 12 ppb | As: 8 ppb\nNO3: 32 mg/L | Fe: 0.4 mg/L"
            ax.text(0.98, 0.95, results_text,
                   transform=ax.transAxes, fontsize=8, color=WHITE,
                   ha='right', va='top', fontfamily='monospace', alpha=result_alpha,
                   bbox=dict(boxstyle='round,pad=0.4', facecolor=BG_DARK,
                            edgecolor=GREEN, alpha=0.8 * result_alpha))

            # Confidence badge
            ax.text(0.98, 0.72, 'Confidence: HIGH',
                   transform=ax.transAxes, fontsize=8, color=GREEN,
                   ha='right', va='top', fontweight='bold', alpha=result_alpha,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='#2EA06A22',
                            edgecolor=GREEN, alpha=0.6 * result_alpha))

        ax.set_xlim(-1.3, 0.7)
        ax.set_ylim(-2, 45)
        ax.grid(True, alpha=0.1, color=GRAY)

        # JalSakhi branding
        ax.text(0.02, 0.95, 'JalSakhi', transform=ax.transAxes,
               fontsize=10, color=TEAL, fontweight='bold', va='top',
               path_effects=[pe.withStroke(linewidth=2, foreground=BG_DARK)])

        plt.tight_layout()
        img = fig_to_pil(fig, dpi=120)
        frames.append(img)
        plt.close(fig)

    # Save GIF
    durations = [80] * scan_frames + [150] * result_frames
    durations[-1] = 2000  # Hold last frame
    frames[0].save(
        f"{OUT_DIR}/voltammogram_scan.gif",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"  Saved: {OUT_DIR}/voltammogram_scan.gif ({len(frames)} frames)")


# ══════════════════════════════════════════════════════════
# GIF 2: REAL-TIME CLASSIFICATION RESULT
# Phone-style UI showing test result appearing
# ══════════════════════════════════════════════════════════
def create_classification_gif():
    print("Creating classification result animation...")

    frames = []
    n_frames = 45

    # Phases: scanning (15), processing (10), result reveal (10), hold (10)
    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(4, 7))
        fig.set_facecolor(BG_DARK)
        ax.set_facecolor(BG_DARK)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 17)
        ax.axis('off')

        # Phone frame
        phone = FancyBboxPatch((0.5, 0.5), 9, 16, boxstyle="round,pad=0.3",
                                facecolor=BG_PANEL, edgecolor=GRAY, linewidth=2)
        ax.add_patch(phone)

        # Status bar
        ax.fill_between([0.5, 9.5], [16.2, 16.2], [16.5, 16.5], color=BG_PANEL)
        ax.text(5, 16.35, 'JalSakhi', fontsize=8, color=TEAL,
               ha='center', va='center', fontweight='bold')

        # Header
        ax.fill_between([0.8, 9.2], [15, 15], [15.8, 15.8], color=WATER_BLUE, alpha=0.3)
        ax.text(5, 15.4, 'Water Quality Test', fontsize=10, color=WHITE,
               ha='center', va='center', fontweight='bold')

        if frame < 15:
            # Scanning phase
            progress = (frame + 1) / 15

            # Mini voltammogram being drawn
            x_volt = np.linspace(1.5, 8.5, 200)
            y_base = 11 + 0.3 * np.sin(x_volt)
            idx = int(progress * len(x_volt))

            # Add peaks progressively
            y_sig = y_base.copy()
            peak_positions = [3.0, 4.5, 6.0, 7.5]
            peak_heights = [1.5, 2.0, 1.2, 0.8]
            for pp, ph in zip(peak_positions, peak_heights):
                y_sig += ph * np.exp(-((x_volt - pp)**2) / 0.15)

            ax.plot(x_volt[:idx], y_sig[:idx], color=TEAL, linewidth=2)
            ax.axvline(x=x_volt[max(0,idx-1)], color=ORANGE, linewidth=1, alpha=0.5,
                      ymin=0.55, ymax=0.85, linestyle='--')

            # Scanning box
            ax.fill_between([1, 9], [9.5, 9.5], [10.5, 10.5], color=BG_DARK, alpha=0.8)
            ax.text(5, 10, f'Scanning... {int(progress*100)}%', fontsize=11, color=ORANGE,
                   ha='center', va='center', fontweight='bold')

            # Progress bar
            ax.fill_between([1.5, 8.5], [9.6, 9.6], [9.8, 9.8], color='#1B3A5C')
            ax.fill_between([1.5, 1.5 + 7*progress], [9.6, 9.6], [9.8, 9.8], color=TEAL)

            # Electrode status
            ax.text(5, 8.5, 'Electrode: Connected', fontsize=7, color=GREEN, ha='center')
            ax.text(5, 8.0, 'Mode: Differential Pulse Voltammetry', fontsize=6, color=GRAY, ha='center')
            ax.text(5, 7.5, f'Temperature: 27.3 C', fontsize=6, color=GRAY, ha='center')

        elif frame < 25:
            # Processing phase
            proc_frame = frame - 15

            # Show completed voltammogram
            x_volt = np.linspace(1.5, 8.5, 200)
            y_base = 11 + 0.3 * np.sin(x_volt)
            y_sig = y_base.copy()
            for pp, ph in zip([3.0, 4.5, 6.0, 7.5], [1.5, 2.0, 1.2, 0.8]):
                y_sig += ph * np.exp(-((x_volt - pp)**2) / 0.15)
            ax.plot(x_volt, y_sig, color=TEAL, linewidth=2, alpha=0.5)

            # Processing steps
            steps = [
                'Baseline correction...',
                'Peak detection...',
                'Feature extraction...',
                'CNN classification...',
                'Confidence scoring...',
            ]
            current_step = min(proc_frame // 2, len(steps) - 1)

            ax.fill_between([1, 9], [7, 7], [10.5, 10.5], color=BG_DARK, alpha=0.9)
            ax.text(5, 10, 'Analyzing...', fontsize=12, color=TEAL,
                   ha='center', va='center', fontweight='bold')

            for i, step in enumerate(steps):
                y = 9.2 - i * 0.5
                if i < current_step:
                    ax.text(2, y, 'OK', fontsize=7, color=GREEN, ha='center', fontweight='bold')
                    ax.text(3, y, step.replace('...', ''), fontsize=7, color=GREEN, ha='left')
                elif i == current_step:
                    ax.text(2, y, '...', fontsize=7, color=ORANGE, ha='center', fontweight='bold')
                    ax.text(3, y, step, fontsize=7, color=ORANGE, ha='left')
                else:
                    ax.text(3, y, step, fontsize=7, color='#3A5A7C', ha='left')

        else:
            # Result reveal phase
            reveal = min(1.0, (frame - 25) / 5)

            # Completed voltammogram (dimmed)
            x_volt = np.linspace(1.5, 8.5, 200)
            y_base = 12 + 0.2 * np.sin(x_volt)
            y_sig = y_base.copy()
            for pp, ph in zip([3.0, 4.5, 6.0, 7.5], [1.2, 1.6, 0.9, 0.6]):
                y_sig += ph * np.exp(-((x_volt - pp)**2) / 0.15)
            ax.plot(x_volt, y_sig, color=TEAL, linewidth=1.5, alpha=0.3)

            # RESULT CARD
            result_box = FancyBboxPatch((1, 1.5), 8, 12.5, boxstyle="round,pad=0.3",
                                         facecolor=BG_DARK, edgecolor=ORANGE,
                                         linewidth=2, alpha=reveal)
            ax.add_patch(result_box)

            if reveal > 0.3:
                # Safety badge
                badge_color = ORANGE
                ax.fill_between([2.5, 7.5], [12.5, 12.5], [13.3, 13.3],
                               color=badge_color, alpha=0.2 * reveal)
                ax.text(5, 12.9, 'MODERATE RISK', fontsize=12, color=badge_color,
                       ha='center', va='center', fontweight='bold', alpha=reveal)

            if reveal > 0.5:
                # Contaminant results
                contams = [
                    ('NH3 (Ammonia)', '1.8 mg/L', ORANGE, 'WHO: 0.5', 0.9),
                    ('Pb (Lead)', '12 ppb', RED, 'WHO: 10', 0.6),
                    ('NO3 (Nitrate)', '32 mg/L', GREEN, 'WHO: 50', 0.32),
                    ('Fe (Iron)', '0.4 mg/L', YELLOW, 'WHO: 0.3', 0.67),
                    ('As (Arsenic)', '8 ppb', GREEN, 'WHO: 10', 0.4),
                ]

                for i, (name, value, color, limit, pct) in enumerate(contams):
                    y = 11.5 - i * 1.2
                    ax.text(1.5, y, name, fontsize=7, color=GRAY, ha='left', alpha=reveal)
                    ax.text(8.5, y, value, fontsize=8, color=color, ha='right',
                           fontweight='bold', alpha=reveal)
                    ax.text(8.5, y - 0.35, limit, fontsize=5, color='#5A7A99',
                           ha='right', alpha=reveal)

                    # Bar
                    ax.fill_between([1.5, 6.5], [y-0.55, y-0.55], [y-0.4, y-0.4],
                                   color='#1B3A5C', alpha=reveal)
                    ax.fill_between([1.5, 1.5 + 5*pct], [y-0.55, y-0.55], [y-0.4, y-0.4],
                                   color=color, alpha=0.6*reveal)

            if reveal > 0.8:
                # Treatment advisory
                ax.fill_between([1.3, 8.7], [2.0, 2.0], [4.0, 4.0],
                               color='#1A3350', alpha=reveal)
                ax.text(5, 3.6, 'Treatment Advisory', fontsize=8, color=ORANGE,
                       ha='center', fontweight='bold', alpha=reveal)
                ax.text(5, 3.0, 'Breakpoint chlorination recommended', fontsize=7,
                       color=DARK_TEXT, ha='center', alpha=reveal)
                ax.text(5, 2.5, 'Dose: 13.7 mg/L Cl2 for NH3 removal', fontsize=7,
                       color=TEAL, ha='center', fontweight='bold', alpha=reveal)

                # Confidence
                ax.text(5, 1.2, 'Confidence: HIGH | Time: 47s | Offline',
                       fontsize=6, color=GREEN, ha='center', alpha=reveal)

        plt.tight_layout()
        img = fig_to_pil(fig, dpi=100)
        frames.append(img)
        plt.close(fig)

    # Save GIF
    durations = [100] * 15 + [200] * 10 + [120] * 10 + [200] * 10
    durations[-1] = 3000  # Hold last frame
    frames[0].save(
        f"{OUT_DIR}/phone_classification.gif",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"  Saved: {OUT_DIR}/phone_classification.gif ({len(frames)} frames)")


# ══════════════════════════════════════════════════════════
# GIF 3: HEATMAP BUILDING UP
# Shows contamination data points appearing and heatmap forming
# ══════════════════════════════════════════════════════════
def create_heatmap_gif():
    print("Creating heatmap buildup animation...")

    np.random.seed(42)

    # Generate test points around Bhagalpur
    n_points = 50
    center_lat, center_lng = 25.25, 86.98

    lats = center_lat + np.random.normal(0, 0.06, n_points)
    lngs = center_lng + np.random.normal(0, 0.1, n_points)

    # Contamination levels with a hotspot
    contamination = np.random.uniform(0.1, 0.4, n_points)
    # Create hotspot
    hotspot_mask = ((lats - 25.21)**2 + (lngs - 87.05)**2) < 0.003
    contamination[hotspot_mask] = np.random.uniform(0.7, 1.0, hotspot_mask.sum())
    # Secondary hotspot
    hotspot2 = ((lats - 25.32)**2 + (lngs - 87.08)**2) < 0.002
    contamination[hotspot2] = np.random.uniform(0.5, 0.8, hotspot2.sum())

    frames = []
    n_frames = 50

    for frame in range(n_frames):
        fig, ax = plt.subplots(1, 1, figsize=(8, 5))
        fig.set_facecolor(BG_DARK)
        ax.set_facecolor('#0A1628')

        # How many points visible
        if frame < 35:
            n_visible = int((frame + 1) / 35 * n_points)
        else:
            n_visible = n_points

        vis_lats = lats[:n_visible]
        vis_lngs = lngs[:n_visible]
        vis_contam = contamination[:n_visible]

        # Draw heatmap using scatter with interpolation effect
        if n_visible > 3 and frame >= 5:
            # Create a grid for interpolation
            from scipy.ndimage import gaussian_filter
            grid_res = 100
            lat_grid = np.linspace(lats.min() - 0.05, lats.max() + 0.05, grid_res)
            lng_grid = np.linspace(lngs.min() - 0.05, lngs.max() + 0.05, grid_res)
            LNG, LAT = np.meshgrid(lng_grid, lat_grid)

            # Simple IDW interpolation
            Z = np.zeros_like(LAT)
            for i in range(n_visible):
                dist = np.sqrt((LAT - vis_lats[i])**2 + (LNG - vis_lngs[i])**2)
                dist = np.maximum(dist, 0.001)
                Z += vis_contam[i] / (dist**2)

            Z = Z / (np.sum(1.0 / np.maximum(
                np.sqrt((LAT[:,:,None] - vis_lats[None,None,:])**2 +
                        (LNG[:,:,None] - vis_lngs[None,None,:])**2), 0.001)**2, axis=2))

            Z = gaussian_filter(Z, sigma=3)

            # Custom colormap
            from matplotlib.colors import LinearSegmentedColormap
            colors_list = ['#0A1628', '#2EA06A', '#7BC67E', '#FFD700', '#FF6B35', '#E83E3E', '#B71C1C']
            cmap = LinearSegmentedColormap.from_list('contam', colors_list, N=256)

            heatmap_alpha = min(0.7, (frame - 5) / 15)
            ax.contourf(LNG, LAT, Z, levels=20, cmap=cmap, alpha=heatmap_alpha)

        # Plot test points
        for i in range(n_visible):
            c = vis_contam[i]
            if c < 0.3:
                color = GREEN
            elif c < 0.5:
                color = YELLOW
            elif c < 0.7:
                color = ORANGE
            else:
                color = RED

            # Fade in effect for newest points
            point_alpha = 1.0
            if i >= n_visible - 3 and frame < 35:
                point_alpha = 0.5

            ax.plot(vis_lngs[i], vis_lats[i], 'o', color=color,
                   markersize=5, alpha=point_alpha,
                   markeredgecolor=BG_DARK, markeredgewidth=0.5)

        # Style
        ax.set_xlim(lngs.min() - 0.08, lngs.max() + 0.08)
        ax.set_ylim(lats.min() - 0.05, lats.max() + 0.05)
        ax.spines['bottom'].set_color('#1B3A5C')
        ax.spines['left'].set_color('#1B3A5C')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors='#5A7A99', labelsize=7)
        ax.set_xlabel('Longitude', color='#5A7A99', fontsize=8)
        ax.set_ylabel('Latitude', color='#5A7A99', fontsize=8)
        ax.grid(True, alpha=0.08, color='#1B3A5C')

        # Title
        if frame < 35:
            ax.set_title(f'Building Contamination Map - {n_visible}/{n_points} test points',
                        color=WHITE, fontsize=11, fontweight='bold', pad=10)
        else:
            ax.set_title(f'District Contamination Intelligence - {n_points} sources mapped',
                        color=TEAL, fontsize=11, fontweight='bold', pad=10)

        # Legend
        legend_x, legend_y = 0.02, 0.95
        legend_items = [('Safe', GREEN), ('Moderate', YELLOW), ('Elevated', ORANGE), ('Critical', RED)]
        for i, (label, color) in enumerate(legend_items):
            ax.text(legend_x, legend_y - i * 0.07, f'  {label}', transform=ax.transAxes,
                   fontsize=7, color=color, va='top',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor=BG_DARK, alpha=0.7, edgecolor='none'))

        # Stats overlay (appears after map is built)
        if frame >= 35:
            stats_alpha = min(1.0, (frame - 35) / 5)
            stats_text = f'Sources > WHO: 18.4%\nHotspot: Sultanpur Block\nPrimary: Ammonia (NH3)\nKriging confidence: 94%'
            ax.text(0.98, 0.95, stats_text, transform=ax.transAxes,
                   fontsize=7, color=WHITE, ha='right', va='top',
                   fontfamily='monospace', alpha=stats_alpha,
                   bbox=dict(boxstyle='round,pad=0.4', facecolor=BG_DARK,
                            edgecolor=TEAL, alpha=0.8 * stats_alpha))

        # JalSakhi branding
        ax.text(0.98, 0.05, 'JalSakhi Community Intelligence',
               transform=ax.transAxes, fontsize=7, color=TEAL,
               ha='right', va='bottom', alpha=0.7)

        plt.tight_layout()
        img = fig_to_pil(fig, dpi=110)
        frames.append(img)
        plt.close(fig)

    # Save GIF
    durations = [120] * 35 + [200] * 15
    durations[-1] = 3000
    frames[0].save(
        f"{OUT_DIR}/heatmap_buildup.gif",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"  Saved: {OUT_DIR}/heatmap_buildup.gif ({len(frames)} frames)")


# ── RUN ALL ───────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 50)
    print("JalSakhi Demo GIF Generator")
    print("=" * 50)

    create_voltammogram_gif()
    create_classification_gif()

    try:
        from scipy.ndimage import gaussian_filter
        create_heatmap_gif()
    except ImportError:
        print("  Skipping heatmap GIF (scipy not available)")
        print("  Install scipy: pip install scipy")

    print("\nAll GIFs created in:", OUT_DIR)
    print("Embed these in your PPT slides for auto-playing animations!")
