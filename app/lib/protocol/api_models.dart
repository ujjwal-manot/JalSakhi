/// Data classes for API communication, matching backend Pydantic schemas.
///
/// All classes are immutable with const constructors where possible.
import 'package:flutter/foundation.dart';

import 'data_models.dart';

// ---------------------------------------------------------------------------
// Device
// ---------------------------------------------------------------------------

@immutable
class DeviceResponse {
  final int id;
  final String hardwareId;
  final String firmwareVersion;
  final DateTime registeredAt;

  const DeviceResponse({
    required this.id,
    required this.hardwareId,
    required this.firmwareVersion,
    required this.registeredAt,
  });

  factory DeviceResponse.fromJson(Map<String, dynamic> json) =>
      DeviceResponse(
        id: json['id'] as int,
        hardwareId: json['hardware_id'] as String,
        firmwareVersion: json['firmware_version'] as String,
        registeredAt: DateTime.parse(json['registered_at'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'hardware_id': hardwareId,
        'firmware_version': firmwareVersion,
        'registered_at': registeredAt.toIso8601String(),
      };

  @override
  String toString() =>
      'DeviceResponse(id=$id, hw=$hardwareId, fw=$firmwareVersion)';
}

// ---------------------------------------------------------------------------
// Heatmap
// ---------------------------------------------------------------------------

@immutable
class HeatmapPoint {
  final double latitude;
  final double longitude;
  final String contaminant;
  final double value;
  final String unit;
  final bool exceedsWhoLimit;
  final String sourceType;
  final DateTime timestamp;

  const HeatmapPoint({
    required this.latitude,
    required this.longitude,
    required this.contaminant,
    required this.value,
    required this.unit,
    required this.exceedsWhoLimit,
    required this.sourceType,
    required this.timestamp,
  });

  factory HeatmapPoint.fromJson(Map<String, dynamic> json) => HeatmapPoint(
        latitude: (json['latitude'] as num).toDouble(),
        longitude: (json['longitude'] as num).toDouble(),
        contaminant: json['contaminant'] as String,
        value: (json['value'] as num).toDouble(),
        unit: json['unit'] as String,
        exceedsWhoLimit: json['exceeds_who_limit'] as bool,
        sourceType: json['source_type'] as String,
        timestamp: DateTime.parse(json['timestamp'] as String),
      );

  Map<String, dynamic> toJson() => {
        'latitude': latitude,
        'longitude': longitude,
        'contaminant': contaminant,
        'value': value,
        'unit': unit,
        'exceeds_who_limit': exceedsWhoLimit,
        'source_type': sourceType,
        'timestamp': timestamp.toIso8601String(),
      };
}

// ---------------------------------------------------------------------------
// Alert
// ---------------------------------------------------------------------------

@immutable
class AlertData {
  final int id;
  final String locationName;
  final double latitude;
  final double longitude;
  final String contaminant;
  final double value;
  final String severity;
  final String message;
  final DateTime createdAt;
  final DateTime? resolvedAt;

  const AlertData({
    required this.id,
    required this.locationName,
    required this.latitude,
    required this.longitude,
    required this.contaminant,
    required this.value,
    required this.severity,
    required this.message,
    required this.createdAt,
    this.resolvedAt,
  });

  factory AlertData.fromJson(Map<String, dynamic> json) => AlertData(
        id: json['id'] as int,
        locationName: json['location_name'] as String,
        latitude: (json['latitude'] as num).toDouble(),
        longitude: (json['longitude'] as num).toDouble(),
        contaminant: json['contaminant'] as String,
        value: (json['value'] as num).toDouble(),
        severity: json['severity'] as String,
        message: json['message'] as String,
        createdAt: DateTime.parse(json['created_at'] as String),
        resolvedAt: json['resolved_at'] != null
            ? DateTime.parse(json['resolved_at'] as String)
            : null,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'location_name': locationName,
        'latitude': latitude,
        'longitude': longitude,
        'contaminant': contaminant,
        'value': value,
        'severity': severity,
        'message': message,
        'created_at': createdAt.toIso8601String(),
        'resolved_at': resolvedAt?.toIso8601String(),
      };
}

// ---------------------------------------------------------------------------
// District Stats
// ---------------------------------------------------------------------------

@immutable
class DistrictStats {
  final int totalTests;
  final int unsafeSources;
  final int activeTesters;

  const DistrictStats({
    required this.totalTests,
    required this.unsafeSources,
    required this.activeTesters,
  });

  factory DistrictStats.fromJson(Map<String, dynamic> json) => DistrictStats(
        totalTests: json['total_tests'] as int,
        unsafeSources: json['unsafe_sources'] as int,
        activeTesters: json['active_testers'] as int,
      );

  Map<String, dynamic> toJson() => {
        'total_tests': totalTests,
        'unsafe_sources': unsafeSources,
        'active_testers': activeTesters,
      };
}

// ---------------------------------------------------------------------------
// Test Summary (from GET /api/v1/tests)
// ---------------------------------------------------------------------------

@immutable
class TestSummary {
  final int id;
  final int deviceId;
  final DateTime timestamp;
  final double latitude;
  final double longitude;
  final String sourceType;
  final String testerName;
  final double? temperature;
  final double? ph;
  final double? tds;
  final DateTime createdAt;
  final List<ContaminantResult> contaminantReadings;

  const TestSummary({
    required this.id,
    required this.deviceId,
    required this.timestamp,
    required this.latitude,
    required this.longitude,
    required this.sourceType,
    required this.testerName,
    this.temperature,
    this.ph,
    this.tds,
    required this.createdAt,
    required this.contaminantReadings,
  });

  /// Derive overall safety from contaminant readings.
  String get overallSafety {
    if (contaminantReadings.isEmpty) return 'Safe';
    final maxRatio = contaminantReadings
        .map((c) => c.ratio)
        .reduce((a, b) => a > b ? a : b);
    if (maxRatio > 2.0) return 'Unsafe';
    if (maxRatio > 1.0) return 'Caution';
    return 'Safe';
  }

  factory TestSummary.fromJson(Map<String, dynamic> json) {
    final readings = (json['contaminant_readings'] as List? ?? [])
        .map((r) => _contaminantFromApiJson(r as Map<String, dynamic>))
        .toList();

    return TestSummary(
      id: json['id'] as int,
      deviceId: json['device_id'] as int,
      timestamp: DateTime.parse(json['timestamp'] as String),
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      sourceType: json['source_type'] as String,
      testerName: json['tester_name'] as String,
      temperature: (json['temperature'] as num?)?.toDouble(),
      ph: (json['ph'] as num?)?.toDouble(),
      tds: (json['tds'] as num?)?.toDouble(),
      createdAt: DateTime.parse(json['created_at'] as String),
      contaminantReadings: List<ContaminantResult>.unmodifiable(readings),
    );
  }
}

/// Convert backend contaminant reading JSON to app ContaminantResult.
///
/// The backend uses snake_case keys and includes `exceeds_who_limit`,
/// while the app model uses camelCase.
ContaminantResult _contaminantFromApiJson(Map<String, dynamic> json) {
  // Map backend schema to app data model
  const whoLimits = {
    'NH3': 0.5,
    'Pb': 10.0,
    'As': 10.0,
    'NO3': 50.0,
    'Fe': 0.3,
  };

  const nameMap = {
    'NH3': 'Ammonia',
    'Pb': 'Lead',
    'As': 'Arsenic',
    'NO3': 'Nitrate',
    'Fe': 'Iron',
  };

  final symbol = json['symbol'] as String;

  return ContaminantResult(
    symbol: symbol,
    name: nameMap[symbol] ?? symbol,
    value: (json['value'] as num).toDouble(),
    unit: json['unit'] as String,
    whoLimit: whoLimits[symbol] ?? 0.0,
    confidence: json['confidence'] as String,
  );
}

// ---------------------------------------------------------------------------
// Lat/Lng bounds for queries
// ---------------------------------------------------------------------------

@immutable
class LatLngBounds {
  final double latMin;
  final double latMax;
  final double lngMin;
  final double lngMax;

  const LatLngBounds({
    required this.latMin,
    required this.latMax,
    required this.lngMin,
    required this.lngMax,
  });
}
