/// Offline-first submission queue backed by Hive.
///
/// Queues [ScanResult] objects when the network is unavailable,
/// then syncs them when connectivity returns.
import 'dart:async';
import 'dart:convert';

import 'package:hive/hive.dart';

import 'api_client.dart';
import 'data_models.dart';

// ---------------------------------------------------------------------------
// Sync report
// ---------------------------------------------------------------------------

/// Report returned after a sync attempt.
class SyncReport {
  final int submitted;
  final int failed;
  final int remaining;
  final List<String> errors;

  const SyncReport({
    required this.submitted,
    required this.failed,
    required this.remaining,
    required this.errors,
  });

  bool get isFullySync => remaining == 0;

  @override
  String toString() =>
      'SyncReport(submitted=$submitted, failed=$failed, remaining=$remaining)';
}

// ---------------------------------------------------------------------------
// Offline queue
// ---------------------------------------------------------------------------

/// Hive-backed offline queue for pending test submissions.
///
/// Each entry is stored as a JSON string keyed by its test ID.
class OfflineQueue {
  static const String _boxName = 'offline_queue';

  Box<String>? _box;
  Timer? _syncTimer;

  /// Open the Hive box. Must be called before any other method.
  Future<void> init() async {
    _box = await Hive.openBox<String>(_boxName);
  }

  /// Queue a test result for later submission.
  ///
  /// Stores the full [ScanResult] as JSON in Hive.
  Future<void> enqueue(ScanResult result) async {
    _ensureInitialized();
    final json = jsonEncode(result.toJson());
    await _box!.put(result.testId, json);
  }

  /// Try to submit all queued results to the backend.
  ///
  /// Returns a [SyncReport] describing what happened.
  /// Failed items remain in the queue for the next attempt.
  Future<SyncReport> syncAll(ApiClient client) async {
    _ensureInitialized();

    if (_box!.isEmpty) {
      return const SyncReport(
        submitted: 0,
        failed: 0,
        remaining: 0,
        errors: [],
      );
    }

    int submitted = 0;
    int failed = 0;
    final errors = <String>[];
    final keysToRemove = <String>[];

    // Iterate over a snapshot of keys to avoid modification during iteration
    final keys = List<String>.from(_box!.keys.cast<String>());

    for (final key in keys) {
      final jsonStr = _box!.get(key);
      if (jsonStr == null) continue;

      try {
        final map = jsonDecode(jsonStr) as Map<String, dynamic>;
        final result = ScanResult.fromJson(map);
        await client.submitTest(result);
        keysToRemove.add(key);
        submitted++;
      } on ApiException catch (e) {
        failed++;
        errors.add('${key}: ${e.message}');
      } catch (e) {
        failed++;
        errors.add('${key}: $e');
      }
    }

    // Remove successfully submitted entries
    for (final key in keysToRemove) {
      await _box!.delete(key);
    }

    return SyncReport(
      submitted: submitted,
      failed: failed,
      remaining: _box!.length,
      errors: List<String>.unmodifiable(errors),
    );
  }

  /// Number of pending (not yet submitted) test results.
  int get pendingCount {
    _ensureInitialized();
    return _box!.length;
  }

  /// Whether there are pending items to sync.
  bool get hasPending {
    _ensureInitialized();
    return _box!.isNotEmpty;
  }

  /// Start a periodic sync timer that attempts to flush the queue.
  ///
  /// Calls [syncAll] every [interval] while there are pending items.
  void startPeriodicSync(
    ApiClient client, {
    Duration interval = const Duration(minutes: 2),
  }) {
    _syncTimer?.cancel();
    _syncTimer = Timer.periodic(interval, (_) async {
      if (hasPending) {
        await syncAll(client);
      }
    });
  }

  /// Stop the periodic sync timer.
  void stopPeriodicSync() {
    _syncTimer?.cancel();
    _syncTimer = null;
  }

  /// Remove a specific pending item by test ID.
  Future<void> remove(String testId) async {
    _ensureInitialized();
    await _box!.delete(testId);
  }

  /// Clear all pending items.
  Future<void> clear() async {
    _ensureInitialized();
    await _box!.clear();
  }

  /// Ensure the Hive box has been initialized.
  void _ensureInitialized() {
    if (_box == null || !_box!.isOpen) {
      throw StateError(
        'OfflineQueue not initialized. Call init() before using the queue.',
      );
    }
  }

  /// Release resources.
  void dispose() {
    stopPeriodicSync();
    _box?.close();
  }
}
