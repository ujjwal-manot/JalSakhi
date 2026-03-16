import 'dart:math';

/// Linear baseline estimation and subtraction.
///
/// Estimates a straight-line baseline from the first and last 10%
/// of the data, then subtracts it. Returns a new list.
class BaselineCorrector {
  const BaselineCorrector();

  /// Subtract a linear baseline from [data].
  ///
  /// Uses [voltages] to compute the slope. The baseline is estimated
  /// by averaging the first and last 10% of current values.
  /// Returns a new [List<double>].
  List<double> subtract(List<double> data, List<double> voltages) {
    if (data.length < 4) return List<double>.from(data);

    final n = data.length;
    final edgeCount = max(1, (n * 0.1).round());

    // Average of first 10% of points
    double startSum = 0;
    double startVSum = 0;
    for (int i = 0; i < edgeCount; i++) {
      startSum += data[i];
      startVSum += voltages[i];
    }
    final startAvg = startSum / edgeCount;
    final startVAvg = startVSum / edgeCount;

    // Average of last 10% of points
    double endSum = 0;
    double endVSum = 0;
    for (int i = n - edgeCount; i < n; i++) {
      endSum += data[i];
      endVSum += voltages[i];
    }
    final endAvg = endSum / edgeCount;
    final endVAvg = endVSum / edgeCount;

    // Linear baseline: y = slope * (v - startVAvg) + startAvg
    final dv = endVAvg - startVAvg;
    final slope = dv.abs() < 1e-12 ? 0.0 : (endAvg - startAvg) / dv;

    final result = <double>[];
    for (int i = 0; i < n; i++) {
      final baseline = startAvg + slope * (voltages[i] - startVAvg);
      result.add(data[i] - baseline);
    }

    return List<double>.unmodifiable(result);
  }
}
