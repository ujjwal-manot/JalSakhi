"""
JalSakhi — Dataset Generation Script

Generates train/val/test splits of synthetic voltammograms for CNN training.

Usage:
  python generate_dataset.py                    # Default: 50k/10k/10k
  python generate_dataset.py --train 100000     # Custom train size
  python generate_dataset.py --output ../data   # Custom output dir
"""

import argparse
import sys
import time
from pathlib import Path

import numpy as np

from synthetic_gen import GeneratorConfig, generate_dataset, NUM_CONTAMINANTS, CONTAMINANTS


def print_dataset_stats(data: dict[str, np.ndarray], split_name: str) -> None:
    """Print summary statistics for a generated dataset split."""
    n = data["voltammograms"].shape[0]
    det = data["labels_detection"]
    conc = data["labels_concentration"]

    print(f"\n{'=' * 50}")
    print(f"  {split_name} split: {n:,} samples")
    print(f"{'=' * 50}")

    # Clean vs contaminated
    has_any = det.any(axis=1)
    n_clean = int((~has_any).sum())
    n_contaminated = int(has_any.sum())
    print(f"  Clean:        {n_clean:>6,} ({100 * n_clean / n:.1f}%)")
    print(f"  Contaminated: {n_contaminated:>6,} ({100 * n_contaminated / n:.1f}%)")

    # Per-contaminant stats
    print(f"\n  {'Contaminant':<12} {'Present':>8} {'Pct':>6} {'Mean Conc':>10} {'Max Conc':>10} {'Unit':<6}")
    print(f"  {'-' * 58}")
    for i, c in enumerate(CONTAMINANTS):
        mask = det[:, i] == 1
        count = int(mask.sum())
        pct = 100 * count / n
        if count > 0:
            mean_c = float(conc[mask, i].mean())
            max_c = float(conc[mask, i].max())
        else:
            mean_c = max_c = 0.0
        print(f"  {c.symbol:<12} {count:>8,} {pct:>5.1f}% {mean_c:>10.2f} {max_c:>10.2f} {c.unit:<6}")

    # Multi-label distribution
    n_contaminants = det.sum(axis=1)
    print(f"\n  Contaminants per sample:")
    for k in range(NUM_CONTAMINANTS + 1):
        count = int((n_contaminants == k).sum())
        if count > 0:
            print(f"    {k}: {count:>6,} ({100 * count / n:.1f}%)")

    # Metadata ranges
    meta = data["metadata"]
    labels = ["Temp(°C)", "pH", "TDS(mg/L)", "SNR(dB)", "Baseline", "WaterType", "ScanRate", "ElBatch"]
    print(f"\n  Metadata ranges:")
    for j, label in enumerate(labels):
        print(f"    {label:<12}: [{meta[:, j].min():.1f}, {meta[:, j].max():.1f}]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic voltammogram datasets")
    parser.add_argument("--train", type=int, default=50000, help="Training samples (default: 50000)")
    parser.add_argument("--val", type=int, default=10000, help="Validation samples (default: 10000)")
    parser.add_argument("--test", type=int, default=10000, help="Test samples (default: 10000)")
    parser.add_argument("--output", type=str, default=None, help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    # Validate bounds to prevent OOM
    for name in ("train", "val", "test"):
        val = getattr(args, name)
        if not (10 <= val <= 500_000):
            parser.error(f"--{name} must be between 10 and 500,000 (got {val})")

    # Determine output paths
    project_root = Path(__file__).resolve().parent.parent.parent
    if args.output:
        out_dir = Path(args.output)
    else:
        out_dir = project_root / "data"

    synthetic_dir = out_dir / "synthetic"
    training_dir = out_dir / "training"
    synthetic_dir.mkdir(parents=True, exist_ok=True)
    training_dir.mkdir(parents=True, exist_ok=True)

    config = GeneratorConfig()

    splits = [
        ("train", args.train, args.seed),
        ("val", args.val, args.seed + 1000),
        ("test", args.test, args.seed + 2000),
    ]

    for split_name, n_samples, seed in splits:
        print(f"\nGenerating {split_name} split ({n_samples:,} samples)...")
        t0 = time.time()
        data = generate_dataset(n_samples, config, seed)
        elapsed = time.time() - t0
        print(f"  Generated in {elapsed:.1f}s ({n_samples / elapsed:.0f} samples/sec)")

        # Save
        out_path = training_dir / f"{split_name}.npz"
        np.savez_compressed(
            out_path,
            voltammograms=data["voltammograms"],
            labels_detection=data["labels_detection"],
            labels_concentration=data["labels_concentration"],
            metadata=data["metadata"],
        )
        size_mb = out_path.stat().st_size / (1024 * 1024)
        print(f"  Saved to {out_path} ({size_mb:.1f} MB)")

        print_dataset_stats(data, split_name)

    print(f"\nDataset generation complete.")
    print(f"Files saved to: {training_dir}")


if __name__ == "__main__":
    main()
