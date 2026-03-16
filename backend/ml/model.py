"""
JalSakhi — 1D-CNN Dual-Head Contaminant Detection Model

Architecture:
  Voltammogram (1000,1) ──→ Conv1D stack ──→ GAP ──┐
                                                     ├── Dense(64) ──→ Detection Head (sigmoid)
  Metadata (8,) ──────────→ Dense stack ───────────┘                └→ Concentration Head (ReLU)

Detection head: multi-label binary classification (which contaminants present)
Concentration head: regression (how much of each, masked to detected only)

Target: INT8 TFLite < 200 KB, < 50ms inference on mobile.
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from synthetic_gen import NUM_CONTAMINANTS

VOLTAMMOGRAM_LENGTH = 1000
METADATA_LENGTH = 8


def build_model(
    num_contaminants: int = NUM_CONTAMINANTS,
    voltammogram_length: int = VOLTAMMOGRAM_LENGTH,
    metadata_length: int = METADATA_LENGTH,
    dropout_rate: float = 0.3,
) -> keras.Model:
    """
    Build the dual-head 1D-CNN for contaminant detection and quantification.

    Returns a compiled Keras model with two outputs:
      - 'detection': (batch, num_contaminants) sigmoid probabilities
      - 'concentration': (batch, num_contaminants) predicted concentrations
    """

    # === Voltammogram branch ===
    volt_input = layers.Input(shape=(voltammogram_length, 1), name="voltammogram")

    x = layers.Conv1D(32, kernel_size=7, padding="same", name="conv1")(volt_input)
    x = layers.BatchNormalization(name="bn1")(x)
    x = layers.ReLU(name="relu1")(x)
    x = layers.MaxPooling1D(pool_size=4, name="pool1")(x)

    x = layers.Conv1D(64, kernel_size=5, padding="same", name="conv2")(x)
    x = layers.BatchNormalization(name="bn2")(x)
    x = layers.ReLU(name="relu2")(x)
    x = layers.MaxPooling1D(pool_size=4, name="pool2")(x)

    x = layers.Conv1D(128, kernel_size=3, padding="same", name="conv3")(x)
    x = layers.BatchNormalization(name="bn3")(x)
    x = layers.ReLU(name="relu3")(x)
    x = layers.MaxPooling1D(pool_size=4, name="pool3")(x)

    x = layers.Conv1D(128, kernel_size=3, padding="same", name="conv4")(x)
    x = layers.BatchNormalization(name="bn4")(x)
    x = layers.ReLU(name="relu4")(x)
    x = layers.GlobalAveragePooling1D(name="gap")(x)

    # === Metadata branch ===
    meta_input = layers.Input(shape=(metadata_length,), name="metadata")

    m = layers.Dense(16, activation="relu", name="meta_dense1")(meta_input)
    m = layers.Dense(16, activation="relu", name="meta_dense2")(m)

    # === Fusion ===
    fused = layers.Concatenate(name="fusion")([x, m])
    fused = layers.Dense(64, activation="relu", name="shared_dense")(fused)
    fused = layers.Dropout(dropout_rate, name="dropout")(fused)

    # === Detection head (multi-label sigmoid) ===
    detection = layers.Dense(
        num_contaminants, activation="sigmoid", name="detection"
    )(fused)

    # === Concentration head (regression, ReLU for non-negative) ===
    concentration = layers.Dense(
        num_contaminants, activation="relu", name="concentration"
    )(fused)

    model = keras.Model(
        inputs={"voltammogram": volt_input, "metadata": meta_input},
        outputs={"detection": detection, "concentration": concentration},
        name="jalsakhi_contaminant_cnn",
    )

    return model


class MaskedMSELoss(keras.losses.Loss):
    """
    MSE loss masked to only penalize detected contaminants.

    Expects y_true to be structured as:
      y_true[:, :NUM_CONTAMINANTS] = concentrations
      y_true[:, NUM_CONTAMINANTS:] = detection labels (0 or 1)
    """

    def call(self, y_true: tf.Tensor, y_pred: tf.Tensor) -> tf.Tensor:
        n = tf.shape(y_pred)[-1]
        true_conc = y_true[:, :n]
        mask = y_true[:, n:]
        mask = tf.cast(mask > 0.5, tf.float32)
        squared_error = tf.square(true_conc - y_pred)
        masked_error = squared_error * mask
        n_detected = tf.maximum(tf.reduce_sum(mask, axis=-1), 1.0)
        return tf.reduce_mean(tf.reduce_sum(masked_error, axis=-1) / n_detected)


def compile_model(
    model: keras.Model,
    learning_rate: float = 1e-3,
    detection_loss_weight: float = 1.0,
    concentration_loss_weight: float = 0.5,
    use_masked_concentration_loss: bool = True,
) -> keras.Model:
    """Compile model with dual losses and Adam optimizer.

    Note: This mutates and returns the same model object (Keras compile is in-place).
    """
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)

    concentration_loss = MaskedMSELoss() if use_masked_concentration_loss else keras.losses.MeanSquaredError()

    model.compile(
        optimizer=optimizer,
        loss={
            "detection": keras.losses.BinaryCrossentropy(),
            "concentration": concentration_loss,
        },
        loss_weights={
            "detection": detection_loss_weight,
            "concentration": concentration_loss_weight,
        },
        metrics={
            "detection": [
                keras.metrics.BinaryAccuracy(name="acc"),
                keras.metrics.AUC(name="auc", multi_label=True),
            ],
            "concentration": [
                keras.metrics.MeanAbsoluteError(name="mae"),
            ],
        },
    )
    return model


def get_model_summary(model: keras.Model) -> str:
    """Return model summary as string."""
    lines = []
    model.summary(print_fn=lambda line: lines.append(line))
    return "\n".join(lines)


if __name__ == "__main__":
    model = build_model()
    model = compile_model(model)
    print(get_model_summary(model))

    # Estimate model size
    total_params = model.count_params()
    # INT8 quantized: ~1 byte per param + overhead
    estimated_tflite_kb = total_params / 1024 + 10
    print(f"\nTotal parameters: {total_params:,}")
    print(f"Estimated TFLite size (INT8): ~{estimated_tflite_kb:.0f} KB")
