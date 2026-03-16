/// Multi-signal confidence scoring for contaminant detection.
///
/// Combines model probability, signal-to-noise ratio, and scan quality
/// into an overall confidence level: HIGH, MEDIUM, LOW, or RETEST.
import 'dart:math';

class ConfidenceScorer {
  // Thresholds for confidence buckets
  static const double _highThreshold = 0.75;
  static const double _mediumThreshold = 0.50;
  static const double _lowThreshold = 0.30;

  // Weight distribution for composite score
  static const double _modelWeight = 0.50;
  static const double _snrWeight = 0.30;
  static const double _qualityWeight = 0.20;

  const ConfidenceScorer._();

  /// Compute a confidence label from multiple detection signals.
  ///
  /// [modelProbability] - 0.0 to 1.0 from classifier sigmoid output.
  /// [signalToNoise] - SNR from scan quality analysis (higher is better).
  /// [scanQuality] - one of 'GOOD', 'MARGINAL', or 'REJECT'.
  ///
  /// Returns one of: 'HIGH', 'MEDIUM', 'LOW', or 'RETEST'.
  static String score({
    required double modelProbability,
    required double signalToNoise,
    required String scanQuality,
  }) {
    // Immediately flag rejected scans
    if (scanQuality == 'REJECT') {
      return 'RETEST';
    }

    final clampedProb = modelProbability.clamp(0.0, 1.0);
    final normalizedSnr = _normalizeSnr(signalToNoise);
    final qualityScore = _qualityToScore(scanQuality);

    final composite = (clampedProb * _modelWeight) +
        (normalizedSnr * _snrWeight) +
        (qualityScore * _qualityWeight);

    if (composite >= _highThreshold) return 'HIGH';
    if (composite >= _mediumThreshold) return 'MEDIUM';
    if (composite >= _lowThreshold) return 'LOW';
    return 'RETEST';
  }

  /// Normalize SNR to a 0-1 range using a sigmoid-like curve.
  ///
  /// SNR of 5 maps to ~0.5, SNR of 10+ maps to ~0.9+.
  static double _normalizeSnr(double snr) {
    if (snr <= 0) return 0.0;
    // Logistic function centered at SNR=5 with moderate steepness
    return 1.0 / (1.0 + exp(-0.5 * (snr - 5.0)));
  }

  /// Convert scan quality label to a numeric score.
  static double _qualityToScore(String quality) {
    switch (quality.toUpperCase()) {
      case 'GOOD':
        return 1.0;
      case 'MARGINAL':
        return 0.5;
      case 'REJECT':
        return 0.0;
      default:
        return 0.0;
    }
  }
}
