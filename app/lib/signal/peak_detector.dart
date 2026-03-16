import 'package:flutter/foundation.dart';

import '../protocol/data_models.dart';

/// Known contaminant peak voltages and calibration data.
@immutable
class ContaminantEntry {
  final String symbol;
  final String name;
  final double peakVoltage;
  final double sensitivity; // uA per ppm (or ppb)
  final String unit;
  final double whoLimit;

  const ContaminantEntry({
    required this.symbol,
    required this.name,
    required this.peakVoltage,
    required this.sensitivity,
    required this.unit,
    required this.whoLimit,
  });
}

/// Peak detection with contaminant matching.
///
/// Finds local maxima using first-derivative zero-crossing, then
/// matches them to known contaminants within +/- 50 mV tolerance.
class PeakDetector {
  static const double _toleranceV = 0.050; // 50 mV

  static const List<ContaminantEntry> contaminantDatabase = [
    ContaminantEntry(
      symbol: 'NH3',
      name: 'Ammonia',
      peakVoltage: 0.25,
      sensitivity: 2.0,
      unit: 'mg/L',
      whoLimit: 1.5,
    ),
    ContaminantEntry(
      symbol: 'Pb',
      name: 'Lead',
      peakVoltage: -0.45,
      sensitivity: 0.8,
      unit: 'ppb',
      whoLimit: 10.0,
    ),
    ContaminantEntry(
      symbol: 'As',
      name: 'Arsenic',
      peakVoltage: -0.15,
      sensitivity: 0.6,
      unit: 'ppb',
      whoLimit: 10.0,
    ),
    ContaminantEntry(
      symbol: 'NO3',
      name: 'Nitrate',
      peakVoltage: 0.45,
      sensitivity: 1.5,
      unit: 'mg/L',
      whoLimit: 50.0,
    ),
    ContaminantEntry(
      symbol: 'Fe',
      name: 'Iron',
      peakVoltage: 0.05,
      sensitivity: 1.2,
      unit: 'mg/L',
      whoLimit: 0.3,
    ),
  ];

  const PeakDetector();

  /// Detect peaks and match to contaminants.
  ///
  /// [voltages] and [currents] are the baseline-subtracted signal.
  /// Returns a list of [ContaminantResult] for matched peaks.
  List<ContaminantResult> detect(
    List<double> voltages,
    List<double> currents,
  ) {
    if (voltages.length < 5) return const [];

    final peaks = _findLocalMaxima(voltages, currents);
    final results = <ContaminantResult>[];

    for (final peak in peaks) {
      final match = _matchContaminant(peak.voltage);
      if (match == null) continue;

      final concentration = peak.current / match.sensitivity;
      if (concentration < 0) continue;

      final confidence = _estimateConfidence(peak.current, concentration);

      results.add(ContaminantResult(
        symbol: match.symbol,
        name: match.name,
        value: double.parse(concentration.toStringAsFixed(2)),
        unit: match.unit,
        whoLimit: match.whoLimit,
        confidence: confidence,
      ));
    }

    return List<ContaminantResult>.unmodifiable(results);
  }

  List<_Peak> _findLocalMaxima(
    List<double> voltages,
    List<double> currents,
  ) {
    final peaks = <_Peak>[];

    // First derivative zero-crossing (positive to negative = maximum)
    for (int i = 2; i < currents.length - 2; i++) {
      final dLeft = currents[i] - currents[i - 1];
      final dRight = currents[i + 1] - currents[i];

      // Zero-crossing: derivative goes from positive to negative
      if (dLeft > 0 && dRight < 0 && currents[i] > 0.5) {
        peaks.add(_Peak(voltage: voltages[i], current: currents[i]));
      }
    }

    return peaks;
  }

  ContaminantEntry? _matchContaminant(double peakVoltage) {
    for (final entry in contaminantDatabase) {
      if ((peakVoltage - entry.peakVoltage).abs() <= _toleranceV) {
        return entry;
      }
    }
    return null;
  }

  String _estimateConfidence(double peakHeight, double concentration) {
    if (peakHeight > 5.0) return 'High';
    if (peakHeight > 2.0) return 'Medium';
    return 'Low';
  }
}

@immutable
class _Peak {
  final double voltage;
  final double current;

  const _Peak({required this.voltage, required this.current});
}
