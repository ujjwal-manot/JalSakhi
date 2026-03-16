"""
JalSakhi — Voltammogram Visualization & Validation

Plots sample voltammograms, verifies peak positions, checks label distributions.
Run after generate_dataset.py to sanity-check training data.

Usage:
  python visualize_data.py                      # Visualize train split
  python visualize_data.py --split test          # Visualize test split
  python visualize_data.py --save plots/         # Save instead of showing
"""

import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from synthetic_gen import CONTAMINANTS, NUM_CONTAMINANTS, GeneratorConfig


def load_split(data_dir: Path, split: str) -> dict[str, np.ndarray]:
    """Load a dataset split from .npz file."""
    path = data_dir / f"{split}.npz"
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}\nRun generate_dataset.py first.")
    data = np.load(path)
    return {k: data[k] for k in data.files}


def plot_sample_voltammograms(data: dict, config: GeneratorConfig, n: int = 12) -> plt.Figure:
    """Plot a grid of sample voltammograms with contaminant labels."""
    fig, axes = plt.subplots(3, 4, figsize=(16, 10))
    fig.suptitle("Sample Voltammograms", fontsize=14, fontweight="bold")

    voltages = np.linspace(config.v_start, config.v_end, config.num_points)
    indices = np.random.choice(len(data["voltammograms"]), n, replace=False)

    for ax, idx in zip(axes.flat, indices):
        v = data["voltammograms"][idx]
        det = data["labels_detection"][idx]
        conc = data["labels_concentration"][idx]

        ax.plot(voltages, v, color="#0A2463", linewidth=0.8)

        # Mark detected contaminant peaks
        present = []
        for i, c in enumerate(CONTAMINANTS):
            if det[i]:
                ax.axvline(c.peak_potential_v, color="#D7263D", alpha=0.3, linestyle="--", linewidth=0.7)
                present.append(f"{c.symbol}={conc[i]:.1f}{c.unit}")

        label = ", ".join(present) if present else "Clean"
        ax.set_title(label, fontsize=8, color="#D7263D" if present else "#10B981")
        ax.set_xlabel("V", fontsize=7)
        ax.set_ylabel("μA", fontsize=7)
        ax.tick_params(labelsize=6)

    fig.tight_layout()
    return fig


def plot_peak_position_verification(data: dict, config: GeneratorConfig) -> plt.Figure:
    """Verify that peaks appear at expected voltages for each contaminant."""
    fig, axes = plt.subplots(1, NUM_CONTAMINANTS, figsize=(18, 4))
    fig.suptitle("Peak Position Verification — Overlay of 50 samples per contaminant", fontsize=12, fontweight="bold")

    voltages = np.linspace(config.v_start, config.v_end, config.num_points)

    for i, (ax, c) in enumerate(zip(axes, CONTAMINANTS)):
        mask = data["labels_detection"][:, i] == 1
        indices = np.where(mask)[0]
        if len(indices) == 0:
            ax.set_title(f"{c.symbol} — no samples")
            continue

        sample_indices = np.random.choice(indices, min(50, len(indices)), replace=False)
        for idx in sample_indices:
            ax.plot(voltages, data["voltammograms"][idx], alpha=0.15, linewidth=0.5, color="#0A2463")

        ax.axvline(c.peak_potential_v, color="#D7263D", linewidth=2, label=f"Expected Ep={c.peak_potential_v}V")
        ax.set_title(f"{c.symbol} ({c.name})", fontsize=10, fontweight="bold")
        ax.set_xlabel("V", fontsize=8)
        ax.legend(fontsize=7, loc="upper left")
        ax.tick_params(labelsize=6)

    fig.tight_layout()
    return fig


def plot_label_distributions(data: dict) -> plt.Figure:
    """Plot contaminant detection frequency and concentration distributions."""
    fig = plt.figure(figsize=(14, 8))
    gs = gridspec.GridSpec(2, NUM_CONTAMINANTS, figure=fig)
    fig.suptitle("Label Distributions", fontsize=14, fontweight="bold")

    det = data["labels_detection"]
    conc = data["labels_concentration"]

    # Row 1: Detection frequency
    ax_bar = fig.add_subplot(gs[0, :])
    counts = det.sum(axis=0)
    total = len(det)
    colors = ["#1B998B", "#E8AA14", "#D7263D", "#0A2463", "#F97316"]
    bars = ax_bar.bar(
        [c.symbol for c in CONTAMINANTS], counts,
        color=colors[:NUM_CONTAMINANTS], alpha=0.8
    )
    for bar, count in zip(bars, counts):
        ax_bar.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + total * 0.005,
                    f"{count:,}\n({100 * count / total:.1f}%)", ha="center", fontsize=9)
    ax_bar.set_ylabel("Number of samples")
    ax_bar.set_title("Detection Frequency", fontsize=11)

    # Row 2: Concentration histograms
    for i, c in enumerate(CONTAMINANTS):
        ax = fig.add_subplot(gs[1, i])
        mask = det[:, i] == 1
        if mask.any():
            values = conc[mask, i]
            ax.hist(values, bins=30, color=colors[i], alpha=0.7, edgecolor="white")
            ax.axvline(c.who_limit, color="#D7263D", linewidth=1.5, linestyle="--", label=f"WHO={c.who_limit}")
            ax.legend(fontsize=7)
        ax.set_title(f"{c.symbol} ({c.unit})", fontsize=9)
        ax.tick_params(labelsize=6)
        ax.set_xlabel(c.unit, fontsize=7)

    fig.tight_layout()
    return fig


def plot_multi_label_distribution(data: dict) -> plt.Figure:
    """Plot distribution of number of simultaneous contaminants."""
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.suptitle("Multi-Contaminant Distribution", fontsize=14, fontweight="bold")

    n_contaminants = data["labels_detection"].sum(axis=1)
    unique, counts = np.unique(n_contaminants, return_counts=True)
    total = len(n_contaminants)

    colors_map = {0: "#10B981", 1: "#1B998B", 2: "#E8AA14", 3: "#F97316", 4: "#D7263D"}
    bar_colors = [colors_map.get(u, "#0A2463") for u in unique]

    bars = ax.bar(unique, counts, color=bar_colors, alpha=0.8, edgecolor="white")
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + total * 0.005,
                f"{count:,}\n({100 * count / total:.1f}%)", ha="center", fontsize=10)

    ax.set_xlabel("Number of contaminants present")
    ax.set_ylabel("Number of samples")
    ax.set_xticks(unique)
    ax.set_xticklabels([f"{u} ({'Clean' if u == 0 else f'{u} contaminant' + ('s' if u > 1 else '')})" for u in unique])

    fig.tight_layout()
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualize synthetic voltammogram data")
    parser.add_argument("--split", default="train", choices=["train", "val", "test"])
    parser.add_argument("--save", default=None, help="Directory to save plots (instead of showing)")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent
    data_dir = project_root / "data" / "training"
    config = GeneratorConfig()

    print(f"Loading {args.split} split...")
    data = load_split(data_dir, args.split)
    print(f"  Loaded {len(data['voltammograms']):,} samples")

    rng = np.random.default_rng(42)
    # Seed numpy's legacy RNG for matplotlib internals that use it
    np.random.seed(42)

    figs = [
        ("sample_voltammograms", plot_sample_voltammograms(data, config)),
        ("peak_verification", plot_peak_position_verification(data, config)),
        ("label_distributions", plot_label_distributions(data)),
        ("multi_label_distribution", plot_multi_label_distribution(data)),
    ]

    if args.save:
        save_dir = Path(args.save)
        save_dir.mkdir(parents=True, exist_ok=True)
        for name, fig in figs:
            path = save_dir / f"{name}.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            print(f"  Saved {path}")
        plt.close("all")
    else:
        plt.show()


if __name__ == "__main__":
    main()
