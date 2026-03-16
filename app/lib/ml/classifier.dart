/// TFLite inference wrapper for contaminant classification.
///
/// Provides a FALLBACK mode using the signal processing peak detector
/// when the TFLite model is not available, so the app works without
/// a trained model.
import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

import '../protocol/data_models.dart';
import '../signal/processing_pipeline.dart';
import 'confidence.dart';

// ---------------------------------------------------------------------------
// Classification result
// ---------------------------------------------------------------------------

@immutable
class ClassificationResult {
  final List<ContaminantResult> contaminants;
  final String inferenceMode; // 'tflite' or 'fallback'
  final Duration inferenceTime;

  const ClassificationResult({
    required this.contaminants,
    required this.inferenceMode,
    required this.inferenceTime,
  });

  @override
  String toString() =>
      'ClassificationResult(mode=$inferenceMode, '
      '${contaminants.length} contaminants, ${inferenceTime.inMilliseconds}ms)';
}

// ---------------------------------------------------------------------------
// Classifier
// ---------------------------------------------------------------------------

/// Contaminant classifier with TFLite inference and signal processing fallback.
///
/// Call [loadModel] to attempt loading the TFLite model from assets.
/// If the model is unavailable, [classify] automatically falls back to
/// the signal processing pipeline (peak detection).
class ContaminantClassifier {
  static const String _modelAssetPath = 'assets/models/contaminant_model.tflite';

  bool _modelLoaded = false;
  // Interpreter placeholder: will be a tflite.Interpreter when model is trained
  // and tflite_flutter dependency is added.
  dynamic _interpreter;

  final ProcessingPipeline _pipeline;

  ContaminantClassifier({
    ProcessingPipeline pipeline = const ProcessingPipeline(),
  }) : _pipeline = pipeline;

  /// Whether the TFLite model is loaded and ready for inference.
  bool get isReady => _modelLoaded;

  /// Whether the classifier is using fallback mode (peak detection).
  bool get isFallbackMode => !_modelLoaded;

  /// Attempt to load the TFLite model from assets.
  ///
  /// If the model file is not found or cannot be loaded, the classifier
  /// will operate in fallback mode using peak detection.
  /// This method never throws; it silently falls back on failure.
  Future<void> loadModel() async {
    try {
      // Verify the asset exists
      await rootBundle.load(_modelAssetPath);

      // TODO: Initialize tflite.Interpreter when model is trained
      // _interpreter = await tflite.Interpreter.fromAsset(_modelAssetPath);
      // _modelLoaded = true;

      // For now, the model file exists but we lack tflite_flutter,
      // so we stay in fallback mode.
      debugPrint('ContaminantClassifier: model asset found, '
          'but TFLite runtime not yet integrated. Using fallback mode.');
      _modelLoaded = false;
    } catch (e) {
      debugPrint('ContaminantClassifier: model not available ($e). '
          'Using fallback peak detection.');
      _modelLoaded = false;
    }
  }

  /// Run inference on a voltammogram.
  ///
  /// Uses TFLite model if loaded, otherwise falls back to signal processing
  /// peak detection from [ProcessingPipeline].
  Future<ClassificationResult> classify(
    List<DpvDataPoint> dataPoints,
    ScanMetadata metadata,
  ) async {
    if (dataPoints.isEmpty) {
      return const ClassificationResult(
        contaminants: [],
        inferenceMode: 'fallback',
        inferenceTime: Duration.zero,
      );
    }

    final stopwatch = Stopwatch()..start();

    if (_modelLoaded && _interpreter != null) {
      return _classifyWithModel(dataPoints, metadata, stopwatch);
    }

    return _classifyWithFallback(dataPoints, metadata, stopwatch);
  }

  /// TFLite model inference (placeholder for when model is trained).
  Future<ClassificationResult> _classifyWithModel(
    List<DpvDataPoint> dataPoints,
    ScanMetadata metadata,
    Stopwatch stopwatch,
  ) async {
    // TODO: Implement when TFLite model is trained
    //
    // Expected flow:
    // 1. Normalize voltage/current arrays to fixed-length input tensor
    // 2. Run _interpreter.run(inputTensor, outputTensor)
    // 3. Parse sigmoid outputs as per-contaminant probabilities
    // 4. Apply confidence scoring via ConfidenceScorer
    // 5. Build ContaminantResult list
    //
    // For now, fall back to peak detection
    return _classifyWithFallback(dataPoints, metadata, stopwatch);
  }

  /// Fallback classification using signal processing peak detection.
  Future<ClassificationResult> _classifyWithFallback(
    List<DpvDataPoint> dataPoints,
    ScanMetadata metadata,
    Stopwatch stopwatch,
  ) async {
    // Run on a separate isolate for large datasets via compute
    final processed = await compute(
      _processDataPoints,
      dataPoints,
    );

    // Re-score confidence using the multi-signal scorer
    final rescored = processed.map((c) {
      final snr = _estimateSignalToNoise(dataPoints);
      final scanQuality = _assessScanQuality(dataPoints, snr);

      final newConfidence = ConfidenceScorer.score(
        modelProbability: _confidenceToProb(c.confidence),
        signalToNoise: snr,
        scanQuality: scanQuality,
      );

      return ContaminantResult(
        symbol: c.symbol,
        name: c.name,
        value: c.value,
        unit: c.unit,
        whoLimit: c.whoLimit,
        confidence: newConfidence,
      );
    }).toList();

    stopwatch.stop();

    return ClassificationResult(
      contaminants: List<ContaminantResult>.unmodifiable(rescored),
      inferenceMode: 'fallback',
      inferenceTime: stopwatch.elapsed,
    );
  }

  /// Estimate signal-to-noise ratio from raw data points.
  double _estimateSignalToNoise(List<DpvDataPoint> dataPoints) {
    if (dataPoints.length < 10) return 0.0;

    final currents = dataPoints.map((p) => p.current).toList();
    final mean = currents.reduce((a, b) => a + b) / currents.length;
    final variance = currents
            .map((c) => (c - mean) * (c - mean))
            .reduce((a, b) => a + b) /
        currents.length;
    final stdDev = _sqrt(variance);

    if (stdDev == 0) return 0.0;

    final maxCurrent = currents.reduce((a, b) => a > b ? a : b);
    return maxCurrent / stdDev;
  }

  /// Assess scan quality based on data point count and SNR.
  String _assessScanQuality(List<DpvDataPoint> dataPoints, double snr) {
    if (dataPoints.length < 20 || snr < 2.0) return 'REJECT';
    if (dataPoints.length < 50 || snr < 5.0) return 'MARGINAL';
    return 'GOOD';
  }

  /// Map string confidence labels to probabilities.
  double _confidenceToProb(String confidence) {
    switch (confidence.toUpperCase()) {
      case 'HIGH':
        return 0.9;
      case 'MEDIUM':
        return 0.7;
      case 'LOW':
        return 0.4;
      default:
        return 0.3;
    }
  }

  /// Simple square root without importing dart:math in top-level isolate.
  static double _sqrt(double x) {
    if (x <= 0) return 0.0;
    double guess = x / 2;
    for (int i = 0; i < 20; i++) {
      guess = (guess + x / guess) / 2;
    }
    return guess;
  }

  /// Release resources.
  void dispose() {
    _interpreter?.close();
    _interpreter = null;
    _modelLoaded = false;
  }
}

/// Top-level function for compute() isolate.
///
/// Runs the signal processing pipeline on raw data points.
List<ContaminantResult> _processDataPoints(List<DpvDataPoint> dataPoints) {
  const pipeline = ProcessingPipeline();
  final result = pipeline.process(dataPoints);
  return result.contaminants;
}
