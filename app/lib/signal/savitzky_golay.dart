/// Savitzky-Golay smoothing filter (5-point, quadratic).
///
/// Uses coefficients [-3, 12, 17, 12, -3] / 35, ported from the
/// ESP32 firmware. Returns a new list; the input is never mutated.
class SavitzkyGolayFilter {
  static const List<int> _coefficients = [-3, 12, 17, 12, -3];
  static const int _norm = 35;
  static const int _halfWindow = 2;

  const SavitzkyGolayFilter();

  /// Apply the 5-point SG filter to [data].
  ///
  /// Edge points (first 2 and last 2) are copied unchanged.
  /// Returns a new [List<double>].
  List<double> apply(List<double> data) {
    if (data.length < _coefficients.length) {
      return List<double>.from(data);
    }

    final result = List<double>.filled(data.length, 0.0);

    // Copy edges unchanged
    for (int i = 0; i < _halfWindow; i++) {
      result[i] = data[i];
      result[data.length - 1 - i] = data[data.length - 1 - i];
    }

    // Apply convolution
    for (int i = _halfWindow; i < data.length - _halfWindow; i++) {
      double sum = 0;
      for (int j = 0; j < _coefficients.length; j++) {
        sum += _coefficients[j] * data[i - _halfWindow + j];
      }
      result[i] = sum / _norm;
    }

    return List<double>.unmodifiable(result);
  }
}
