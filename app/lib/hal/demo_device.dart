import 'dart:async';
import 'dart:math';

import '../protocol/data_models.dart';
import '../signal/processing_pipeline.dart';

/// Mock device that generates synthetic DPV data for development
/// without hardware. Simulates BLE delay between data points.
class DemoDevice {
  final _dataPointController = StreamController<DpvDataPoint>.broadcast();
  final _scanCompleteController = StreamController<ScanResult?>.broadcast();

  Timer? _scanTimer;
  bool _isScanning = false;
  List<DpvDataPoint> _collectedPoints = [];

  Stream<DpvDataPoint> get dataPoints => _dataPointController.stream;
  Stream<ScanResult?> get scanComplete => _scanCompleteController.stream;

  /// Start a scan generating clean water data.
  void startDemoClean() {
    _startGenerating(contaminated: false);
  }

  /// Start a scan generating contaminated water data.
  void startDemoContaminated() {
    _startGenerating(contaminated: true);
  }

  /// Start a generic scan (defaults to contaminated for demo value).
  void startScan() {
    _startGenerating(contaminated: true);
  }

  /// Stop the current scan.
  void stop() {
    _scanTimer?.cancel();
    _isScanning = false;
  }

  void _startGenerating({required bool contaminated}) {
    stop();
    _isScanning = true;
    _collectedPoints = [];

    final points = _generateVoltammogram(contaminated: contaminated);
    int index = 0;

    // Simulate BLE data streaming at ~50ms per point
    _scanTimer = Timer.periodic(const Duration(milliseconds: 50), (timer) {
      if (index >= points.length || !_isScanning) {
        timer.cancel();
        _isScanning = false;
        _onScanComplete();
        return;
      }

      final point = points[index];
      _collectedPoints = List.unmodifiable([..._collectedPoints, point]);
      _dataPointController.add(point);
      index++;
    });
  }

  void _onScanComplete() {
    if (_collectedPoints.isEmpty) {
      _scanCompleteController.add(null);
      return;
    }

    final pipeline = ProcessingPipeline();
    final processed = pipeline.process(_collectedPoints);

    final result = ScanResult(
      testId: 'DEMO-${DateTime.now().millisecondsSinceEpoch}',
      timestamp: DateTime.now(),
      dataPoints: _collectedPoints,
      metadata: const ScanMetadata(
        temperature: 25.0,
        ph: 7.2,
        tds: 340,
        technique: 'DPV',
      ),
      contaminants: processed.contaminants,
      overallSafety: _computeSafety(processed.contaminants),
    );

    _scanCompleteController.add(result);
  }

  /// Generate a synthetic DPV voltammogram.
  ///
  /// The waveform is a sum of Gaussian peaks at known contaminant
  /// potentials on top of a sloped baseline with noise.
  List<DpvDataPoint> _generateVoltammogram({required bool contaminated}) {
    final rng = Random(42);
    final points = <DpvDataPoint>[];

    const startV = -0.8;
    const endV = 0.8;
    const stepV = 0.005;
    final numPoints = ((endV - startV) / stepV).round();

    for (int i = 0; i <= numPoints; i++) {
      final v = startV + i * stepV;

      // Sloped baseline
      double current = 0.5 + 0.3 * v;

      if (contaminated) {
        // Lead peak at -0.45V
        current += _gaussianPeak(v, center: -0.45, height: 8.0, width: 0.04);
        // Arsenic peak at -0.15V
        current += _gaussianPeak(v, center: -0.15, height: 5.0, width: 0.04);
        // Iron peak at +0.05V
        current += _gaussianPeak(v, center: 0.05, height: 3.5, width: 0.05);
        // Ammonia peak at +0.25V
        current += _gaussianPeak(v, center: 0.25, height: 6.0, width: 0.04);
        // Nitrate peak at +0.45V
        current += _gaussianPeak(v, center: 0.45, height: 4.0, width: 0.04);
      }

      // Add noise (±0.15 uA)
      current += (rng.nextDouble() - 0.5) * 0.3;

      points.add(DpvDataPoint(voltage: v, current: current));
    }

    return List.unmodifiable(points);
  }

  double _gaussianPeak(
    double x, {
    required double center,
    required double height,
    required double width,
  }) {
    final exponent = -0.5 * pow((x - center) / width, 2);
    return height * exp(exponent);
  }

  String _computeSafety(List<ContaminantResult> contaminants) {
    if (contaminants.isEmpty) return 'Safe';

    final maxRatio =
        contaminants.map((c) => c.ratio).reduce((a, b) => a > b ? a : b);

    if (maxRatio > 2.0) return 'Unsafe';
    if (maxRatio > 1.0) return 'Caution';
    return 'Safe';
  }

  void dispose() {
    stop();
    _dataPointController.close();
    _scanCompleteController.close();
  }
}
