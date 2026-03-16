"""
JalSakhi — TFLite Export with INT8 Quantization

Converts trained Keras model to TFLite for on-device inference.
Target: < 200 KB, < 50ms inference on mid-range phone.

Usage:
  python export_tflite.py                          # Export best checkpoint
  python export_tflite.py --model checkpoints/final.keras --float16
"""

import argparse
import time
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow import keras


def representative_dataset_gen(data_dir: Path, n_samples: int = 200):
    """Generator for INT8 calibration using representative training samples."""
    raw = np.load(data_dir / "train.npz")
    voltammograms = raw["voltammograms"]
    metadata = raw["metadata"]

    # Load normalization stats
    checkpoint_dir = Path(__file__).resolve().parent / "checkpoints"
    norm = np.load(checkpoint_dir / "norm_stats.npz")
    v_mean, v_std = float(norm["mean"]), float(norm["std"])

    indices = np.random.default_rng(42).choice(len(voltammograms), n_samples, replace=False)

    for idx in indices:
        v = ((voltammograms[idx] - v_mean) / v_std).astype(np.float32)
        v = v[np.newaxis, :, np.newaxis]  # (1, 1000, 1)
        m = metadata[idx][np.newaxis, :].astype(np.float32)  # (1, 8)
        yield {"voltammogram": v, "metadata": m}


def export_model(
    model_path: Path,
    output_path: Path,
    data_dir: Path,
    quantization: str = "int8",
) -> int:
    """
    Export Keras model to TFLite with specified quantization.

    Args:
        quantization: "none", "float16", "int8", or "dynamic"

    Returns:
        File size in bytes.
    """
    print(f"Loading model from {model_path}...")
    model = keras.models.load_model(model_path)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    if quantization == "int8":
        print("Applying INT8 quantization with representative dataset...")
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.representative_dataset = lambda: representative_dataset_gen(data_dir)
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        converter.inference_input_type = tf.float32  # Keep float I/O for easier integration
        converter.inference_output_type = tf.float32

    elif quantization == "float16":
        print("Applying float16 quantization...")
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]

    elif quantization == "dynamic":
        print("Applying dynamic range quantization...")
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

    elif quantization == "none":
        print("No quantization (float32)...")

    else:
        raise ValueError(f"Unknown quantization: {quantization}")

    print("Converting...")
    tflite_model = converter.convert()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(tflite_model)
    size_bytes = len(tflite_model)

    print(f"Saved to {output_path}")
    print(f"Size: {size_bytes:,} bytes ({size_bytes / 1024:.1f} KB)")

    return size_bytes


def validate_tflite(
    tflite_path: Path,
    data_dir: Path,
    n_samples: int = 100,
) -> None:
    """Run inference on TFLite model and report basic metrics."""
    print(f"\nValidating {tflite_path}...")

    interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print(f"  Inputs: {[(d['name'], d['shape'].tolist(), d['dtype'].__name__) for d in input_details]}")
    print(f"  Outputs: {[(d['name'], d['shape'].tolist(), d['dtype'].__name__) for d in output_details]}")

    # Load test data
    raw = np.load(data_dir / "test.npz")
    checkpoint_dir = Path(__file__).resolve().parent / "checkpoints"
    norm = np.load(checkpoint_dir / "norm_stats.npz")
    v_mean, v_std = float(norm["mean"]), float(norm["std"])

    indices = np.random.default_rng(123).choice(len(raw["voltammograms"]), n_samples, replace=False)

    correct = 0
    total = 0
    times = []

    for idx in indices:
        v = ((raw["voltammograms"][idx] - v_mean) / v_std).astype(np.float32)
        v = v[np.newaxis, :, np.newaxis]
        m = raw["metadata"][idx][np.newaxis, :].astype(np.float32)

        # Set inputs (order may vary)
        for detail in input_details:
            if "voltammogram" in detail["name"]:
                interpreter.set_tensor(detail["index"], v)
            elif "metadata" in detail["name"]:
                interpreter.set_tensor(detail["index"], m)

        t0 = time.perf_counter()
        interpreter.invoke()
        times.append((time.perf_counter() - t0) * 1000)

        # Get outputs
        pred_det = None
        for detail in output_details:
            if "detection" in detail["name"]:
                pred_det = interpreter.get_tensor(detail["index"])[0]
        if pred_det is None:
            raise RuntimeError(
                f"Could not find 'detection' output in TFLite model. "
                f"Available outputs: {[d['name'] for d in output_details]}"
            )

        # Check detection accuracy (threshold 0.5)
        true_det = raw["labels_detection"][idx]
        pred_binary = (pred_det > 0.5).astype(np.int8)
        correct += int((pred_binary == true_det).all())
        total += 1

    accuracy = correct / total
    avg_time = np.mean(times)
    p95_time = np.percentile(times, 95)

    print(f"\n  Exact-match accuracy: {accuracy:.1%} ({correct}/{total})")
    print(f"  Inference time: avg={avg_time:.1f}ms, p95={p95_time:.1f}ms")
    target = "PASS" if avg_time < 50 else "FAIL"
    print(f"  Latency target (<50ms): {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export JalSakhi model to TFLite")
    parser.add_argument("--model", type=str, default=None, help="Path to .keras model")
    parser.add_argument("--output", type=str, default=None, help="Output .tflite path")
    parser.add_argument("--quantization", choices=["int8", "float16", "dynamic", "none"], default="int8")
    parser.add_argument("--skip-validation", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent
    checkpoint_dir = Path(__file__).resolve().parent / "checkpoints"
    data_dir = project_root / "data" / "training"

    model_path = Path(args.model) if args.model else checkpoint_dir / "best.keras"
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = project_root / "app" / "assets" / "models" / "voltammogram_cnn.tflite"

    size = export_model(model_path, output_path, data_dir, args.quantization)

    if size > 200 * 1024:
        print(f"\nWARNING: Model size ({size / 1024:.0f} KB) exceeds 200 KB target!")
        print("Consider: --quantization int8 or reducing model capacity")

    if not args.skip_validation:
        validate_tflite(output_path, data_dir)


if __name__ == "__main__":
    main()
