import 'package:flutter/material.dart';

import '../protocol/data_models.dart';
import 'treatment_advisory.dart';

/// Displays scan results: overall safety, contaminant cards, treatment advisory.
class ResultsPanel extends StatelessWidget {
  final ScanResult result;

  const ResultsPanel({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final advisory = generateAdvisory(result.contaminants);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _SafetyBadge(safety: result.overallSafety),
          const SizedBox(height: 16),
          _AdvisoryCard(advisory: advisory),
          const SizedBox(height: 16),
          if (result.contaminants.isNotEmpty) ...[
            const Text(
              'Detected Contaminants',
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            ...result.contaminants.map(
              (c) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: _ContaminantCard(contaminant: c),
              ),
            ),
          ] else
            const Card(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Center(
                  child: Text(
                    'No contaminants detected above threshold',
                    style: TextStyle(color: Colors.white70, fontSize: 16),
                  ),
                ),
              ),
            ),
          const SizedBox(height: 8),
          Text(
            'Test ID: ${result.testId}',
            style: const TextStyle(color: Colors.white38, fontSize: 12),
          ),
          Text(
            'Time: ${_formatTimestamp(result.timestamp)}',
            style: const TextStyle(color: Colors.white38, fontSize: 12),
          ),
        ],
      ),
    );
  }

  String _formatTimestamp(DateTime dt) {
    return '${dt.year}-${_pad(dt.month)}-${_pad(dt.day)} '
        '${_pad(dt.hour)}:${_pad(dt.minute)}:${_pad(dt.second)}';
  }

  String _pad(int n) => n.toString().padLeft(2, '0');
}

class _SafetyBadge extends StatelessWidget {
  final String safety;

  const _SafetyBadge({required this.safety});

  @override
  Widget build(BuildContext context) {
    final (color, icon) = switch (safety) {
      'Safe' => (const Color(0xFF4CAF50), Icons.check_circle),
      'Caution' => (const Color(0xFFFF9800), Icons.warning_rounded),
      'Unsafe' => (const Color(0xFFD7263D), Icons.dangerous),
      _ => (Colors.grey, Icons.help_outline),
    };

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 24),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.4), width: 1.5),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(width: 12),
          Text(
            safety.toUpperCase(),
            style: TextStyle(
              color: color,
              fontSize: 28,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
            ),
          ),
        ],
      ),
    );
  }
}

class _AdvisoryCard extends StatelessWidget {
  final TreatmentAdvisory advisory;

  const _AdvisoryCard({required this.advisory});

  @override
  Widget build(BuildContext context) {
    final color = switch (advisory.severity) {
      AdvisorySeverity.critical => const Color(0xFFD7263D),
      AdvisorySeverity.severe => const Color(0xFFFF5722),
      AdvisorySeverity.moderate => const Color(0xFFFF9800),
      AdvisorySeverity.safe => const Color(0xFF4CAF50),
    };

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.medical_services, color: color, size: 20),
                const SizedBox(width: 8),
                Text(
                  'Treatment Advisory',
                  style: TextStyle(
                    color: color,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              advisory.title,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              advisory.description,
              style: const TextStyle(color: Colors.white70, fontSize: 13),
            ),
            const SizedBox(height: 12),
            ...advisory.actions.map(
              (action) => Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.arrow_right, color: color, size: 18),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        action,
                        style: const TextStyle(
                          color: Colors.white60,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ContaminantCard extends StatelessWidget {
  final ContaminantResult contaminant;

  const _ContaminantCard({required this.contaminant});

  @override
  Widget build(BuildContext context) {
    final color = _statusColor(contaminant);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            // Symbol badge
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: color.withOpacity(0.4)),
              ),
              alignment: Alignment.center,
              child: Text(
                contaminant.symbol,
                style: TextStyle(
                  color: color,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(width: 14),
            // Details
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    contaminant.name,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '${contaminant.value} ${contaminant.unit}',
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    contaminant.exceedsLimit
                        ? '${contaminant.ratio.toStringAsFixed(1)}x WHO limit'
                        : 'Within WHO limit',
                    style: TextStyle(
                      color: color,
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
            // Confidence badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.08),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                contaminant.confidence,
                style: const TextStyle(
                  color: Colors.white54,
                  fontSize: 11,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _statusColor(ContaminantResult c) {
    if (c.ratio > 2.0) return const Color(0xFFD7263D);
    if (c.ratio > 1.0) return const Color(0xFFFF9800);
    return const Color(0xFF4CAF50);
  }
}
