import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';

import '../protocol/data_models.dart';
import 'results_panel.dart';

/// Local scan history backed by Hive.
class ScanHistoryScreen extends StatelessWidget {
  const ScanHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scan History')),
      body: ValueListenableBuilder<Box<Map>>(
        valueListenable: Hive.box<Map>('scan_history').listenable(),
        builder: (context, box, _) {
          if (box.isEmpty) {
            return const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.history, size: 64, color: Colors.white24),
                  SizedBox(height: 16),
                  Text(
                    'No scan history yet',
                    style: TextStyle(color: Colors.white54, fontSize: 16),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Completed scans will appear here.',
                    style: TextStyle(color: Colors.white38, fontSize: 13),
                  ),
                ],
              ),
            );
          }

          // Sort by timestamp (newest first)
          final entries = box.toMap().entries.toList()
            ..sort((a, b) {
              final aTime = a.value['timestamp'] as String? ?? '';
              final bTime = b.value['timestamp'] as String? ?? '';
              return bTime.compareTo(aTime);
            });

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: entries.length,
            itemBuilder: (context, index) {
              final entry = entries[index];
              final data = Map<String, dynamic>.from(entry.value);

              return _HistoryListItem(
                data: data,
                onTap: () => _openDetail(context, data),
                onDelete: () => box.delete(entry.key),
              );
            },
          );
        },
      ),
    );
  }

  void _openDetail(BuildContext context, Map<String, dynamic> data) {
    try {
      final result = ScanResult.fromJson(data);
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => _HistoryDetailScreen(result: result),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to load scan data: $e'),
          backgroundColor: const Color(0xFFD7263D),
        ),
      );
    }
  }
}

class _HistoryListItem extends StatelessWidget {
  final Map<String, dynamic> data;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  const _HistoryListItem({
    required this.data,
    required this.onTap,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final safety = data['overallSafety'] as String? ?? 'Unknown';
    final timestamp = DateTime.tryParse(data['timestamp'] as String? ?? '');
    final testId = data['testId'] as String? ?? 'Unknown';
    final contaminantCount =
        (data['contaminants'] as List?)?.length ?? 0;

    final safetyColor = switch (safety) {
      'Safe' => const Color(0xFF4CAF50),
      'Caution' => const Color(0xFFFF9800),
      'Unsafe' => const Color(0xFFD7263D),
      _ => Colors.grey,
    };

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        onTap: onTap,
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: safetyColor.withOpacity(0.15),
            borderRadius: BorderRadius.circular(10),
          ),
          alignment: Alignment.center,
          child: Icon(
            safety == 'Safe'
                ? Icons.check_circle
                : safety == 'Unsafe'
                    ? Icons.dangerous
                    : Icons.warning,
            color: safetyColor,
            size: 22,
          ),
        ),
        title: Text(
          safety,
          style: TextStyle(
            color: safetyColor,
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Text(
          '${_formatDate(timestamp)} | $contaminantCount contaminant(s)',
          style: const TextStyle(color: Colors.white54, fontSize: 12),
        ),
        trailing: IconButton(
          icon: const Icon(Icons.delete_outline, color: Colors.white24),
          onPressed: onDelete,
        ),
      ),
    );
  }

  String _formatDate(DateTime? dt) {
    if (dt == null) return 'Unknown date';
    return '${dt.year}-${_pad(dt.month)}-${_pad(dt.day)} '
        '${_pad(dt.hour)}:${_pad(dt.minute)}';
  }

  String _pad(int n) => n.toString().padLeft(2, '0');
}

class _HistoryDetailScreen extends StatelessWidget {
  final ScanResult result;

  const _HistoryDetailScreen({required this.result});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Scan ${result.testId}'),
      ),
      body: ResultsPanel(result: result),
    );
  }
}

/// Saves a [ScanResult] to the Hive scan history box.
Future<void> saveScanResult(ScanResult result) async {
  final box = Hive.box<Map>('scan_history');
  await box.put(result.testId, result.toJson());
}
