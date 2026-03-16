"""
JalSakhi — CNN Training Script

Trains the dual-head 1D-CNN on synthetic voltammogram data.

Usage:
  python train_cnn.py                              # Train with defaults
  python train_cnn.py --epochs 100 --batch 64      # Custom training
  python train_cnn.py --resume checkpoints/best.keras  # Resume from checkpoint
"""

import argparse
import time
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
import tensorflow as tf
from tensorflow import keras

from model import build_model, compile_model


def load_data(data_dir: Path, split: str) -> tuple[dict, dict]:
    """Load a dataset split and format for Keras."""
    path = data_dir / f"{split}.npz"
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}\n"
            "Run: python generate_dataset.py"
        )

    raw = np.load(path)
    voltammograms = raw["voltammograms"]
    # Add channel dimension: (N, 1000) -> (N, 1000, 1)
    voltammograms = voltammograms[..., np.newaxis]

    detection_labels = raw["labels_detection"].astype(np.float32)
    concentration_labels = raw["labels_concentration"]
    # Pack detection labels into concentration target for MaskedMSELoss:
    # y_true = [concentrations | detection_flags]
    concentration_with_mask = np.concatenate([concentration_labels, detection_labels], axis=-1)

    inputs = {
        "voltammogram": voltammograms,
        "metadata": raw["metadata"],
    }
    outputs = {
        "detection": detection_labels,
        "concentration": concentration_with_mask,
    }
    return inputs, outputs


def normalize_voltammograms(
    train_inputs: dict,
    val_inputs: dict,
    test_inputs: dict | None = None,
) -> tuple[dict, dict, dict | None, float, float]:
    """Z-score normalize voltammograms using train statistics."""
    v_train = train_inputs["voltammogram"]
    mean = v_train.mean()
    std = v_train.std() + 1e-8

    train_inputs = {**train_inputs, "voltammogram": (v_train - mean) / std}
    val_inputs = {**val_inputs, "voltammogram": (val_inputs["voltammogram"] - mean) / std}

    if test_inputs is not None:
        test_inputs = {**test_inputs, "voltammogram": (test_inputs["voltammogram"] - mean) / std}

    return train_inputs, val_inputs, test_inputs, float(mean), float(std)


def normalize_metadata(
    train_inputs: dict,
    val_inputs: dict,
    test_inputs: dict | None = None,
) -> tuple[dict, dict, dict | None, NDArray, NDArray]:
    """Z-score normalize metadata features using train statistics."""
    m_train = train_inputs["metadata"]
    meta_mean = m_train.mean(axis=0)
    meta_std = m_train.std(axis=0) + 1e-8

    train_inputs = {**train_inputs, "metadata": ((m_train - meta_mean) / meta_std).astype(np.float32)}
    val_inputs = {**val_inputs, "metadata": ((val_inputs["metadata"] - meta_mean) / meta_std).astype(np.float32)}

    if test_inputs is not None:
        test_inputs = {**test_inputs, "metadata": ((test_inputs["metadata"] - meta_mean) / meta_std).astype(np.float32)}

    return train_inputs, val_inputs, test_inputs, meta_mean, meta_std


def main() -> None:
    parser = argparse.ArgumentParser(description="Train JalSakhi contaminant detection CNN")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--det-weight", type=float, default=1.0, help="Detection loss weight")
    parser.add_argument("--conc-weight", type=float, default=0.5, help="Concentration loss weight")
    parser.add_argument("--patience", type=int, default=10, help="Early stopping patience")
    parser.add_argument("--resume", type=str, default=None, help="Path to checkpoint to resume from")
    parser.add_argument("--data-dir", type=str, default=None)
    parser.add_argument("--output-dir", type=str, default=None)
    args = parser.parse_args()

    # Validate bounds
    if not (1 <= args.epochs <= 1000):
        parser.error(f"--epochs must be between 1 and 1000 (got {args.epochs})")
    if not (1 <= args.batch <= 512):
        parser.error(f"--batch must be between 1 and 512 (got {args.batch})")
    if not (1e-6 <= args.lr <= 1.0):
        parser.error(f"--lr must be between 1e-6 and 1.0 (got {args.lr})")

    project_root = Path(__file__).resolve().parent.parent.parent
    data_dir = Path(args.data_dir) if args.data_dir else project_root / "data" / "training"
    output_dir = Path(args.output_dir) if args.output_dir else project_root / "backend" / "ml" / "checkpoints"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print("Loading datasets...")
    train_inputs, train_outputs = load_data(data_dir, "train")
    val_inputs, val_outputs = load_data(data_dir, "val")

    n_train = train_inputs["voltammogram"].shape[0]
    n_val = val_inputs["voltammogram"].shape[0]
    print(f"  Train: {n_train:,} samples")
    print(f"  Val:   {n_val:,} samples")

    # Normalize voltammograms
    print("Normalizing voltammograms...")
    train_inputs, val_inputs, _, v_mean, v_std = normalize_voltammograms(
        train_inputs, val_inputs
    )
    print(f"  Voltammogram — Mean: {v_mean:.4f}, Std: {v_std:.4f}")

    # Normalize metadata
    print("Normalizing metadata...")
    train_inputs, val_inputs, _, meta_mean, meta_std = normalize_metadata(
        train_inputs, val_inputs
    )
    print(f"  Metadata — Means: {meta_mean.round(2)}")

    # Save normalization stats for inference (single source of truth)
    np.savez(output_dir / "norm_stats.npz", mean=v_mean, std=v_std,
             meta_mean=meta_mean, meta_std=meta_std)

    # Build model
    if args.resume:
        print(f"Resuming from {args.resume}...")
        model = keras.models.load_model(args.resume)
    else:
        print("Building model...")
        model = build_model()

    model = compile_model(
        model,
        learning_rate=args.lr,
        detection_loss_weight=args.det_weight,
        concentration_loss_weight=args.conc_weight,
    )

    total_params = model.count_params()
    print(f"  Parameters: {total_params:,}")

    # Callbacks
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            str(output_dir / "best.keras"),
            monitor="val_loss",
            save_best_only=True,
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=args.patience,
            restore_best_weights=True,
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1,
        ),
        keras.callbacks.TensorBoard(
            log_dir=str(output_dir / "logs"),
            histogram_freq=1,
        ),
    ]

    # Train
    print(f"\nTraining for up to {args.epochs} epochs (patience={args.patience})...")
    print(f"  Batch size: {args.batch}")
    print(f"  Learning rate: {args.lr}")
    print(f"  Loss weights: detection={args.det_weight}, concentration={args.conc_weight}")
    print()

    t0 = time.time()
    history = model.fit(
        train_inputs,
        train_outputs,
        validation_data=(val_inputs, val_outputs),
        epochs=args.epochs,
        batch_size=args.batch,
        callbacks=callbacks,
        verbose=1,
    )
    elapsed = time.time() - t0

    # Results
    best_epoch = np.argmin(history.history["val_loss"]) + 1
    best_val_loss = min(history.history["val_loss"])

    print(f"\n{'=' * 50}")
    print(f"  Training complete in {elapsed:.0f}s")
    print(f"  Best epoch: {best_epoch}")
    print(f"  Best val_loss: {best_val_loss:.4f}")
    print(f"  Best val_detection_acc: {history.history['val_detection_acc'][best_epoch - 1]:.4f}")
    print(f"  Best val_detection_auc: {history.history['val_detection_auc'][best_epoch - 1]:.4f}")
    print(f"  Best val_concentration_mae: {history.history['val_concentration_mae'][best_epoch - 1]:.4f}")
    print(f"{'=' * 50}")

    # Save final model
    model.save(str(output_dir / "final.keras"))
    print(f"\nModel saved to {output_dir}")

    # Save training history
    np.savez(
        output_dir / "history.npz",
        **{k: np.array(v) for k, v in history.history.items()},
    )


if __name__ == "__main__":
    main()
