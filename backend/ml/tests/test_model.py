"""Tests for the 1D-CNN model architecture."""

import numpy as np
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model import build_model, compile_model, VOLTAMMOGRAM_LENGTH, METADATA_LENGTH
from synthetic_gen import NUM_CONTAMINANTS


@pytest.fixture
def model():
    m = build_model()
    return compile_model(m)


class TestModelArchitecture:

    def test_model_builds_without_error(self):
        model = build_model()
        assert model is not None

    def test_input_shapes(self, model):
        inputs = model.input_shape
        # Should have two inputs
        assert isinstance(inputs, dict) or len(model.inputs) == 2

    def test_output_shapes(self, model):
        batch = 4
        v = np.random.randn(batch, VOLTAMMOGRAM_LENGTH, 1).astype(np.float32)
        m = np.random.randn(batch, METADATA_LENGTH).astype(np.float32)
        outputs = model.predict({"voltammogram": v, "metadata": m}, verbose=0)
        assert outputs["detection"].shape == (batch, NUM_CONTAMINANTS)
        assert outputs["concentration"].shape == (batch, NUM_CONTAMINANTS)

    def test_detection_output_range(self, model):
        """Detection head should output values in [0, 1] (sigmoid)."""
        v = np.random.randn(10, VOLTAMMOGRAM_LENGTH, 1).astype(np.float32)
        m = np.random.randn(10, METADATA_LENGTH).astype(np.float32)
        outputs = model.predict({"voltammogram": v, "metadata": m}, verbose=0)
        det = outputs["detection"]
        assert np.all(det >= 0.0), f"Min detection value: {det.min()}"
        assert np.all(det <= 1.0), f"Max detection value: {det.max()}"

    def test_concentration_output_non_negative(self, model):
        """Concentration head should output non-negative values (ReLU)."""
        v = np.random.randn(10, VOLTAMMOGRAM_LENGTH, 1).astype(np.float32)
        m = np.random.randn(10, METADATA_LENGTH).astype(np.float32)
        outputs = model.predict({"voltammogram": v, "metadata": m}, verbose=0)
        conc = outputs["concentration"]
        assert np.all(conc >= 0.0), f"Min concentration: {conc.min()}"

    def test_model_parameter_count_reasonable(self, model):
        """Model should be small enough for mobile deployment."""
        params = model.count_params()
        # Should be under 500K params for a lightweight model
        assert params < 500_000, f"Model has {params:,} params — too large for mobile"

    def test_estimated_tflite_size(self, model):
        """INT8 quantized model should be under 200 KB."""
        params = model.count_params()
        estimated_kb = params / 1024 + 10  # ~1 byte per param + overhead
        assert estimated_kb < 200, f"Estimated size {estimated_kb:.0f} KB exceeds 200 KB target"


class TestModelTraining:

    def test_loss_decreases_on_tiny_dataset(self, model):
        """Train for a few epochs on tiny data — loss should decrease."""
        n = 64
        v = np.random.randn(n, VOLTAMMOGRAM_LENGTH, 1).astype(np.float32)
        m = np.random.randn(n, METADATA_LENGTH).astype(np.float32)
        det = np.random.randint(0, 2, (n, NUM_CONTAMINANTS)).astype(np.float32)
        conc = np.random.rand(n, NUM_CONTAMINANTS).astype(np.float32) * det

        history = model.fit(
            {"voltammogram": v, "metadata": m},
            {"detection": det, "concentration": conc},
            epochs=5,
            batch_size=16,
            verbose=0,
        )

        losses = history.history["loss"]
        assert losses[-1] < losses[0], "Loss did not decrease after 5 epochs"
