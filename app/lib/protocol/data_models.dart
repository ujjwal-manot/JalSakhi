import 'package:flutter/foundation.dart';

@immutable
class DpvDataPoint {
  final double voltage;
  final double current;

  const DpvDataPoint({
    required this.voltage,
    required this.current,
  });

  Map<String, dynamic> toJson() => {
        'voltage': voltage,
        'current': current,
      };

  factory DpvDataPoint.fromJson(Map<String, dynamic> json) => DpvDataPoint(
        voltage: (json['voltage'] as num).toDouble(),
        current: (json['current'] as num).toDouble(),
      );

  @override
  String toString() => 'DpvDataPoint(V=$voltage, I=$current)';
}

@immutable
class ScanMetadata {
  final double? temperature;
  final double? ph;
  final double? tds;
  final String technique;

  const ScanMetadata({
    this.temperature,
    this.ph,
    this.tds,
    this.technique = 'DPV',
  });

  Map<String, dynamic> toJson() => {
        'temperature': temperature,
        'ph': ph,
        'tds': tds,
        'technique': technique,
      };

  factory ScanMetadata.fromJson(Map<String, dynamic> json) => ScanMetadata(
        temperature: (json['temperature'] as num?)?.toDouble(),
        ph: (json['ph'] as num?)?.toDouble(),
        tds: (json['tds'] as num?)?.toDouble(),
        technique: json['technique'] as String? ?? 'DPV',
      );
}

@immutable
class ContaminantResult {
  final String symbol;
  final String name;
  final double value;
  final String unit;
  final double whoLimit;
  final String confidence;

  const ContaminantResult({
    required this.symbol,
    required this.name,
    required this.value,
    required this.unit,
    required this.whoLimit,
    required this.confidence,
  });

  bool get exceedsLimit => value > whoLimit;

  double get ratio => whoLimit > 0 ? value / whoLimit : 0;

  Map<String, dynamic> toJson() => {
        'symbol': symbol,
        'name': name,
        'value': value,
        'unit': unit,
        'whoLimit': whoLimit,
        'confidence': confidence,
      };

  factory ContaminantResult.fromJson(Map<String, dynamic> json) =>
      ContaminantResult(
        symbol: json['symbol'] as String,
        name: json['name'] as String,
        value: (json['value'] as num).toDouble(),
        unit: json['unit'] as String,
        whoLimit: (json['whoLimit'] as num).toDouble(),
        confidence: json['confidence'] as String,
      );

  @override
  String toString() =>
      'ContaminantResult($symbol: $value $unit, WHO: $whoLimit)';
}

@immutable
class ScanResult {
  final String testId;
  final DateTime timestamp;
  final List<DpvDataPoint> dataPoints;
  final ScanMetadata metadata;
  final List<ContaminantResult> contaminants;
  final double? latitude;
  final double? longitude;
  final String overallSafety;

  const ScanResult({
    required this.testId,
    required this.timestamp,
    required this.dataPoints,
    required this.metadata,
    required this.contaminants,
    this.latitude,
    this.longitude,
    required this.overallSafety,
  });

  Map<String, dynamic> toJson() => {
        'testId': testId,
        'timestamp': timestamp.toIso8601String(),
        'dataPoints': dataPoints.map((p) => p.toJson()).toList(),
        'metadata': metadata.toJson(),
        'contaminants': contaminants.map((c) => c.toJson()).toList(),
        'latitude': latitude,
        'longitude': longitude,
        'overallSafety': overallSafety,
      };

  factory ScanResult.fromJson(Map<String, dynamic> json) => ScanResult(
        testId: json['testId'] as String,
        timestamp: DateTime.parse(json['timestamp'] as String),
        dataPoints: (json['dataPoints'] as List)
            .map((p) => DpvDataPoint.fromJson(p as Map<String, dynamic>))
            .toList(),
        metadata:
            ScanMetadata.fromJson(json['metadata'] as Map<String, dynamic>),
        contaminants: (json['contaminants'] as List)
            .map((c) => ContaminantResult.fromJson(c as Map<String, dynamic>))
            .toList(),
        latitude: (json['latitude'] as num?)?.toDouble(),
        longitude: (json['longitude'] as num?)?.toDouble(),
        overallSafety: json['overallSafety'] as String,
      );

  @override
  String toString() =>
      'ScanResult($testId, safety=$overallSafety, '
      '${contaminants.length} contaminants)';
}
