"""
JalSakhi — Autoencoder Anomaly Detector for Interference Detection

Trains a 1D convolutional autoencoder on known voltammogram patterns.
High reconstruction error flags unknown matrix interference, preventing
false safety signals from novel contaminant combinations.

Usage:
  python anomaly.py train                       # Train autoencoder
  python anomaly.py evaluate                    # Evaluate on test set
  python anomaly.py export                      # Export to TFLite
"""

import argparse
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


VOLTAMMOGRAM_LENGTH = 1000
LATENT_DIM = 32


def build_autoencoder(
    input_length: int = VOLTAMMOGRAM_LENGTH,
    latent_dim: int = LATENT_DIM,
) -> keras.Model:
    """Build 1D convolutional autoencoder for voltammogram reconstruction."""

    # Encoder
    encoder_input = layers.Input(shape=(input_length, 1), name="encoder_input")

    x = layers.Conv1D(32, kernel_size=7, strides=2, padding="same", activation="relu")(encoder_input)
    x = layers.Conv1D(64, kernel_size=5, strides=2, padding="same", activation="relu")(x)
    x = layers.Conv1D(64, kernel_size=3, strides=2, padding="same", activation="relu")(x)
    x = layers.GlobalAveragePooling1D()(x)
    latent = layers.Dense(latent_dim, activation="relu", name="latent")(x)

    # Decoder
    x = layers.Dense(125 * 64, activation="relu")(latent)
    x = layers.Reshape((125, 64))(x)
    x = layers.Conv1DTranspose(64, kernel_size=3, strides=2, padding="same", activation="relu")(x)
    x = layers.Conv1DTranspose(32, kernel_size=5, strides=2, padding="same", activation="relu")(x)
    x = layers.Conv1DTranspose(1, kernel_size=7, strides=2, padding="same", activation="linear")(x)

    # Crop to exact input length — Conv1DTranspose with strides may overshoot
    # 125 * 2 * 2 * 2 = 1000, so no cropping needed with input_length=1000
    # For safety, add a Cropping1D to trim any excess
    decoder_output = layers.Cropping1D(cropping=(0, 0), name="crop")(x)

    model = keras.Model(encoder_input, decoder_output, name="jalsakhi_anomaly_autoencoder")
    return model


def train_autoencoder(data_dir: Path, output_dir: Path, epochs: int = 30, batch_size: int = 64) -> None:
    """Train autoencoder on training voltammograms."""
    print("Loading training data...")
    raw = np.load(data_dir / "train.npz")
    voltammograms = raw["voltammograms"]

    # Use shared normalization stats if available (single source of truth with CNN)
    shared_norm_path = output_dir / "norm_stats.npz"
    if shared_norm_path.exists():
        norm = np.load(shared_norm_path)
        v_mean = float(norm["mean"])
        v_std = float(norm["std"])
        print(f"  Using shared norm stats from {shared_norm_path}")
    else:
        v_mean = float(voltammograms.mean())
        v_std = float(voltammograms.std() + 1e-8)
        print("  Warning: No shared norm_stats.npz found, computing from data")

    voltammograms = ((voltammograms - v_mean) / v_std).astype(np.float32)
    voltammograms = voltammograms[..., np.newaxis]  # (N, 1000, 1)

    # Validation
    raw_val = np.load(data_dir / "val.npz")
    val_v = ((raw_val["voltammograms"] - v_mean) / v_std).astype(np.float32)[..., np.newaxis]

    print(f"  Train: {voltammograms.shape[0]:,} samples")
    print(f"  Val:   {val_v.shape[0]:,} samples")

    # Build and compile
    model = build_autoencoder()
    model.compile(optimizer=keras.optimizers.Adam(1e-3), loss="mse")
    model.summary()

    output_dir.mkdir(parents=True, exist_ok=True)

    callbacks = [
        keras.callbacks.ModelCheckpoint(
            str(output_dir / "anomaly_best.keras"),
            monitor="val_loss", save_best_only=True, verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=8, restore_best_weights=True, verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=4, verbose=1,
        ),
    ]

    model.fit(
        voltammograms, voltammograms,  # Input = target (autoencoder)
        validation_data=(val_v, val_v),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1,
    )

    model.save(str(output_dir / "anomaly_final.keras"))

    # Save normalization stats
    np.savez(output_dir / "anomaly_norm_stats.npz", mean=v_mean, std=v_std)
    print(f"\nAutoencoder saved to {output_dir}")


def evaluate_autoencoder(data_dir: Path, model_dir: Path) -> None:
    """Evaluate reconstruction error distribution on test set."""
    model = keras.models.load_model(model_dir / "anomaly_best.keras")
    norm = np.load(model_dir / "anomaly_norm_stats.npz")
    v_mean, v_std = float(norm["mean"]), float(norm["std"])

    raw = np.load(data_dir / "test.npz")
    voltammograms = ((raw["voltammograms"] - v_mean) / v_std).astype(np.float32)[..., np.newaxis]

    reconstructed = model.predict(voltammograms, batch_size=64, verbose=0)
    mse_per_sample = np.mean((voltammograms - reconstructed) ** 2, axis=(1, 2))

    p50 = np.percentile(mse_per_sample, 50)
    p90 = np.percentile(mse_per_sample, 90)
    p95 = np.percentile(mse_per_sample, 95)
    p99 = np.percentile(mse_per_sample, 99)

    print(f"\nReconstruction error distribution (MSE):")
    print(f"  Median: {p50:.6f}")
    print(f"  P90:    {p90:.6f}")
    print(f"  P95:    {p95:.6f}")
    print(f"  P99:    {p99:.6f}")
    print(f"\nSuggested threshold (P95): {p95:.6f}")
    print(f"Samples flagged at P95: {int(np.sum(mse_per_sample > p95)):,} / {len(mse_per_sample):,}")

    # Save threshold
    np.savez(model_dir / "anomaly_threshold.npz", threshold=p95)


def export_autoencoder(model_dir: Path, output_path: Path) -> None:
    """Export autoencoder to TFLite."""
    model = keras.models.load_model(model_dir / "anomaly_best.keras")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(tflite_model)
    print(f"Autoencoder TFLite saved to {output_path} ({len(tflite_model) / 1024:.1f} KB)")


def main() -> None:
    parser = argparse.ArgumentParser(description="JalSakhi anomaly detection autoencoder")
    parser.add_argument("action", choices=["train", "evaluate", "export"])
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch", type=int, default=64)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent
    data_dir = project_root / "data" / "training"
    model_dir = Path(__file__).resolve().parent / "checkpoints"

    if args.action == "train":
        train_autoencoder(data_dir, model_dir, args.epochs, args.batch)
    elif args.action == "evaluate":
        evaluate_autoencoder(data_dir, model_dir)
    elif args.action == "export":
        output_path = project_root / "app" / "assets" / "models" / "anomaly_autoencoder.tflite"
        export_autoencoder(model_dir, output_path)


if __name__ == "__main__":
    main()
