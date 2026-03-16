/// HTTP client for JalSakhi backend API communication.
///
/// Supports offline queueing, exponential backoff retries, and timeout handling.
/// All methods return immutable data classes.
import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:http/http.dart' as http;

import 'api_models.dart';
import 'data_models.dart';
import 'offline_queue.dart';

// ---------------------------------------------------------------------------
// Error types
// ---------------------------------------------------------------------------

/// User-friendly API error with optional HTTP status code.
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final String? detail;

  const ApiException({
    required this.message,
    this.statusCode,
    this.detail,
  });

  @override
  String toString() => 'ApiException($statusCode): $message';
}

// ---------------------------------------------------------------------------
// API Client
// ---------------------------------------------------------------------------

class ApiClient {
  final String baseUrl;
  final Duration timeout;
  final int maxRetries;
  final OfflineQueue? offlineQueue;
  final http.Client _httpClient;

  ApiClient({
    required this.baseUrl,
    this.timeout = const Duration(seconds: 10),
    this.maxRetries = 3,
    this.offlineQueue,
    http.Client? httpClient,
  }) : _httpClient = httpClient ?? http.Client();

  // -----------------------------------------------------------------------
  // Device registration
  // -----------------------------------------------------------------------

  /// Register a device with the backend.
  ///
  /// Throws [ApiException] on failure with user-friendly message.
  Future<DeviceResponse> registerDevice(
    String hardwareId,
    String firmwareVersion,
  ) async {
    final body = {
      'hardware_id': hardwareId,
      'firmware_version': firmwareVersion,
    };

    final response = await _post('/api/v1/devices/register', body);
    return DeviceResponse.fromJson(response);
  }

  // -----------------------------------------------------------------------
  // Test submission (with offline queue support)
  // -----------------------------------------------------------------------

  /// Submit a test result to the backend.
  ///
  /// If the network is unavailable and an [offlineQueue] is configured,
  /// the result is queued for later submission.
  Future<void> submitTest(ScanResult result) async {
    final body = _scanResultToSubmission(result);

    try {
      await _post('/api/v1/tests', body);
    } on ApiException catch (e) {
      if (_isNetworkError(e) && offlineQueue != null) {
        await offlineQueue!.enqueue(result);
        return;
      }
      rethrow;
    }
  }

  /// Convert a [ScanResult] to the backend TestSubmission JSON format.
  Map<String, dynamic> _scanResultToSubmission(ScanResult result) {
    return {
      'device_id': 1, // Default device; override after registration
      'timestamp': result.timestamp.toIso8601String(),
      'latitude': result.latitude ?? 0.0,
      'longitude': result.longitude ?? 0.0,
      'source_type': 'tap',
      'tester_name': 'JalSakhi User',
      'temperature': result.metadata.temperature,
      'ph': result.metadata.ph,
      'tds': result.metadata.tds,
      'raw_voltammogram': result.dataPoints
          .map((p) => [p.voltage, p.current])
          .toList(),
      'contaminant_readings': result.contaminants
          .map((c) => {
                'symbol': c.symbol,
                'value': c.value,
                'unit': c.unit,
                'confidence': c.confidence.toUpperCase(),
              })
          .toList(),
    };
  }

  // -----------------------------------------------------------------------
  // Query tests
  // -----------------------------------------------------------------------

  /// Query test results with optional geographic and time filters.
  Future<List<TestSummary>> getTests({
    LatLngBounds? bounds,
    DateTime? since,
    int limit = 100,
  }) async {
    final params = <String, String>{};

    if (bounds != null) {
      params['lat_min'] = bounds.latMin.toString();
      params['lat_max'] = bounds.latMax.toString();
      params['lng_min'] = bounds.lngMin.toString();
      params['lng_max'] = bounds.lngMax.toString();
    }
    if (since != null) {
      params['start'] = since.toIso8601String();
    }
    params['limit'] = limit.toString();

    final response = await _get('/api/v1/tests', params);
    final list = response as List<dynamic>;
    return List<TestSummary>.unmodifiable(
      list.map((j) => TestSummary.fromJson(j as Map<String, dynamic>)),
    );
  }

  // -----------------------------------------------------------------------
  // Heatmap
  // -----------------------------------------------------------------------

  /// Get heatmap data points for map rendering.
  Future<List<HeatmapPoint>> getHeatmap({
    String? contaminant,
    required LatLngBounds bounds,
  }) async {
    final params = <String, String>{
      'lat_min': bounds.latMin.toString(),
      'lat_max': bounds.latMax.toString(),
      'lng_min': bounds.lngMin.toString(),
      'lng_max': bounds.lngMax.toString(),
    };

    if (contaminant != null) {
      params['contaminant'] = contaminant;
    }

    final response = await _get('/api/v1/heatmap', params);
    final list = response as List<dynamic>;
    return List<HeatmapPoint>.unmodifiable(
      list.map((j) => HeatmapPoint.fromJson(j as Map<String, dynamic>)),
    );
  }

  // -----------------------------------------------------------------------
  // Alerts
  // -----------------------------------------------------------------------

  /// Get all active (unresolved) alerts.
  Future<List<AlertData>> getAlerts() async {
    final response = await _get('/api/v1/alerts', {});
    final list = response as List<dynamic>;
    return List<AlertData>.unmodifiable(
      list.map((j) => AlertData.fromJson(j as Map<String, dynamic>)),
    );
  }

  // -----------------------------------------------------------------------
  // Stats
  // -----------------------------------------------------------------------

  /// Get district overview statistics.
  Future<DistrictStats> getStats() async {
    final response = await _get('/api/v1/stats', {});
    return DistrictStats.fromJson(response as Map<String, dynamic>);
  }

  // -----------------------------------------------------------------------
  // HTTP helpers with retry and error handling
  // -----------------------------------------------------------------------

  /// Execute a GET request with retry and exponential backoff.
  Future<dynamic> _get(
    String path,
    Map<String, String> queryParams,
  ) async {
    return _withRetry(() async {
      final uri = Uri.parse('$baseUrl$path').replace(
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );

      final response = await _httpClient.get(
        uri,
        headers: _defaultHeaders(),
      ).timeout(timeout);

      return _handleResponse(response);
    });
  }

  /// Execute a POST request with retry and exponential backoff.
  Future<dynamic> _post(
    String path,
    Map<String, dynamic> body,
  ) async {
    return _withRetry(() async {
      final uri = Uri.parse('$baseUrl$path');

      final response = await _httpClient.post(
        uri,
        headers: _defaultHeaders(),
        body: jsonEncode(body),
      ).timeout(timeout);

      return _handleResponse(response);
    });
  }

  /// Default request headers.
  Map<String, String> _defaultHeaders() => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

  /// Parse response body and throw on error status codes.
  dynamic _handleResponse(http.Response response) {
    final body = response.body.isNotEmpty ? jsonDecode(response.body) : null;

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return body;
    }

    final detail = body is Map ? body['detail'] as String? : null;
    final message = _userFriendlyMessage(response.statusCode, detail);

    throw ApiException(
      message: message,
      statusCode: response.statusCode,
      detail: detail,
    );
  }

  /// Retry a request with exponential backoff on transient failures.
  Future<T> _withRetry<T>(Future<T> Function() action) async {
    int attempt = 0;

    while (true) {
      try {
        return await action();
      } on ApiException catch (e) {
        if (!_isRetryable(e) || attempt >= maxRetries - 1) rethrow;
        attempt++;
        final delay = Duration(
          milliseconds: min(1000 * pow(2, attempt).toInt(), 8000),
        );
        await Future<void>.delayed(delay);
      } on TimeoutException {
        if (attempt >= maxRetries - 1) {
          throw const ApiException(
            message: 'Request timed out. Please check your connection and try again.',
          );
        }
        attempt++;
        final delay = Duration(
          milliseconds: min(1000 * pow(2, attempt).toInt(), 8000),
        );
        await Future<void>.delayed(delay);
      } catch (e) {
        // Network errors (SocketException, etc.)
        if (attempt >= maxRetries - 1) {
          throw ApiException(
            message: 'Could not connect to server. Please check your internet connection.',
            detail: e.toString(),
          );
        }
        attempt++;
        final delay = Duration(
          milliseconds: min(1000 * pow(2, attempt).toInt(), 8000),
        );
        await Future<void>.delayed(delay);
      }
    }
  }

  /// Whether an error is transient and worth retrying.
  bool _isRetryable(ApiException e) {
    if (e.statusCode == null) return true; // Network error
    return e.statusCode! >= 500 || e.statusCode == 429;
  }

  /// Whether an error indicates network unavailability.
  bool _isNetworkError(ApiException e) {
    return e.statusCode == null;
  }

  /// Map HTTP status codes to user-friendly messages.
  String _userFriendlyMessage(int statusCode, String? detail) {
    switch (statusCode) {
      case 400:
        return detail ?? 'Invalid request. Please check your input.';
      case 401:
        return 'Authentication required. Please log in again.';
      case 403:
        return 'Access denied. You do not have permission for this action.';
      case 404:
        return detail ?? 'The requested resource was not found.';
      case 409:
        return detail ?? 'This item already exists.';
      case 422:
        return detail ?? 'Invalid data submitted. Please check your input.';
      case 429:
        return 'Too many requests. Please wait a moment and try again.';
      case >= 500:
        return 'Server error. Please try again later.';
      default:
        return detail ?? 'An unexpected error occurred (HTTP $statusCode).';
    }
  }

  /// Release resources.
  void dispose() {
    _httpClient.close();
  }
}
