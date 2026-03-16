import 'package:flutter/foundation.dart';

import '../protocol/data_models.dart';
import 'baseline.dart';
import 'peak_detector.dart';
import 'savitzky_golay.dart';

/// Result of the signal processing pipeline.
@immutable
class ProcessedResult {
  final List<double> smoothedCurrents;
  final List<double> baselineCorrectedCurrents;
  final List<double> voltages;
  final List<ContaminantResult> contaminants;

  const ProcessedResult({
    required this.smoothedCurrents,
    required this.baselineCorrectedCurrents,
    required this.voltages,
    required this.contaminants,
  });
}

/// Orchestrates the signal processing pipeline:
/// raw data -> SG smoothing -> baseline subtraction -> peak detection.
///
/// All operations are immutable; no input data is modified.
class ProcessingPipeline {
  final SavitzkyGolayFilter _sgFilter;
  final BaselineCorrector _baselineCorrector;
  final PeakDetector _peakDetector;

  const ProcessingPipeline({
    SavitzkyGolayFilter sgFilter = const SavitzkyGolayFilter(),
    BaselineCorrector baselineCorrector = const BaselineCorrector(),
    PeakDetector peakDetector = const PeakDetector(),
  })  : _sgFilter = sgFilter,
        _baselineCorrector = baselineCorrector,
        _peakDetector = peakDetector;

  /// Process raw DPV data points through the full pipeline.
  ProcessedResult process(List<DpvDataPoint> rawData) {
    if (rawData.isEmpty) {
      return const ProcessedResult(
        smoothedCurrents: [],
        baselineCorrectedCurrents: [],
        voltages: [],
        contaminants: [],
      );
    }

    // Extract voltage and current arrays
    final voltages = rawData.map((p) => p.voltage).toList();
    final currents = rawData.map((p) => p.current).toList();

    // Step 1: Savitzky-Golay smoothing
    final smoothed = _sgFilter.apply(currents);

    // Step 2: Baseline subtraction
    final corrected = _baselineCorrector.subtract(smoothed, voltages);

    // Step 3: Peak detection and contaminant matching
    final contaminants = _peakDetector.detect(voltages, corrected);

    return ProcessedResult(
      smoothedCurrents: smoothed,
      baselineCorrectedCurrents: corrected,
      voltages: List<double>.unmodifiable(voltages),
      contaminants: contaminants,
    );
  }
}
