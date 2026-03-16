import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

import '../protocol/data_models.dart';
import '../signal/peak_detector.dart';

/// Real-time animated voltammogram chart.
///
/// X-axis: voltage (-0.8V to +0.8V)
/// Y-axis: differential current (auto-scaled)
/// Marks detected contaminant peaks with colored dots and labels.
class VoltammogramChart extends StatelessWidget {
  final List<DpvDataPoint> dataPoints;
  final List<ContaminantResult> detectedPeaks;

  const VoltammogramChart({
    super.key,
    required this.dataPoints,
    this.detectedPeaks = const [],
  });

  @override
  Widget build(BuildContext context) {
    if (dataPoints.isEmpty) {
      return const Center(
        child: Text(
          'Waiting for data...',
          style: TextStyle(color: Colors.white54),
        ),
      );
    }

    final spots = dataPoints
        .map((p) => FlSpot(p.voltage, p.current))
        .toList();

    final minY = dataPoints
        .map((p) => p.current)
        .reduce((a, b) => a < b ? a : b);
    final maxY = dataPoints
        .map((p) => p.current)
        .reduce((a, b) => a > b ? a : b);
    final yPadding = (maxY - minY) * 0.1;

    return Padding(
      padding: const EdgeInsets.all(16),
      child: LineChart(
        LineChartData(
          minX: -0.8,
          maxX: 0.8,
          minY: minY - yPadding,
          maxY: maxY + yPadding,
          clipData: const FlClipData.all(),
          gridData: FlGridData(
            show: true,
            drawVerticalLine: true,
            horizontalInterval: _computeInterval(maxY - minY),
            verticalInterval: 0.2,
            getDrawingHorizontalLine: (_) => FlLine(
              color: Colors.white12,
              strokeWidth: 0.5,
            ),
            getDrawingVerticalLine: (_) => FlLine(
              color: Colors.white12,
              strokeWidth: 0.5,
            ),
          ),
          titlesData: FlTitlesData(
            topTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            rightTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            bottomTitles: AxisTitles(
              axisNameWidget: const Text(
                'Voltage (V)',
                style: TextStyle(color: Colors.white54, fontSize: 12),
              ),
              sideTitles: SideTitles(
                showTitles: true,
                interval: 0.4,
                getTitlesWidget: (value, _) => Text(
                  value.toStringAsFixed(1),
                  style: const TextStyle(color: Colors.white38, fontSize: 10),
                ),
              ),
            ),
            leftTitles: AxisTitles(
              axisNameWidget: const Text(
                'Current (uA)',
                style: TextStyle(color: Colors.white54, fontSize: 12),
              ),
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 44,
                interval: _computeInterval(maxY - minY),
                getTitlesWidget: (value, _) => Text(
                  value.toStringAsFixed(1),
                  style: const TextStyle(color: Colors.white38, fontSize: 10),
                ),
              ),
            ),
          ),
          borderData: FlBorderData(
            show: true,
            border: const Border(
              bottom: BorderSide(color: Colors.white24),
              left: BorderSide(color: Colors.white24),
            ),
          ),
          lineBarsData: [
            LineChartBarData(
              spots: spots,
              isCurved: true,
              curveSmoothness: 0.15,
              color: const Color(0xFF1B998B),
              barWidth: 2,
              isStrokeCapRound: true,
              dotData: const FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                color: const Color(0xFF1B998B).withOpacity(0.1),
              ),
            ),
          ],
          lineTouchData: LineTouchData(
            touchTooltipData: LineTouchTooltipData(
              getTooltipItems: (touchedSpots) {
                return touchedSpots.map((spot) {
                  return LineTooltipItem(
                    'V: ${spot.x.toStringAsFixed(3)}\n'
                    'I: ${spot.y.toStringAsFixed(2)} uA',
                    const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                    ),
                  );
                }).toList();
              },
            ),
          ),
          extraLinesData: ExtraLinesData(
            verticalLines: _buildPeakLines(),
          ),
        ),
        duration: const Duration(milliseconds: 150),
        curve: Curves.easeInOut,
      ),
    );
  }

  List<VerticalLine> _buildPeakLines() {
    return detectedPeaks.map((peak) {
      final dbEntry = PeakDetector.contaminantDatabase
          .where((e) => e.symbol == peak.symbol)
          .firstOrNull;
      final voltage = dbEntry?.peakVoltage ?? 0;
      final color = _colorForContaminant(peak);

      return VerticalLine(
        x: voltage,
        color: color.withOpacity(0.6),
        strokeWidth: 1.5,
        dashArray: [4, 4],
        label: VerticalLineLabel(
          show: true,
          alignment: Alignment.topCenter,
          style: TextStyle(
            color: color,
            fontSize: 10,
            fontWeight: FontWeight.bold,
          ),
          labelResolver: (_) => '${peak.symbol}\n${peak.value} ${peak.unit}',
        ),
      );
    }).toList();
  }

  Color _colorForContaminant(ContaminantResult c) {
    if (c.ratio > 2.0) return const Color(0xFFD7263D);
    if (c.ratio > 1.0) return const Color(0xFFFF9800);
    return const Color(0xFF4CAF50);
  }

  double _computeInterval(double range) {
    if (range <= 0) return 1;
    if (range < 2) return 0.5;
    if (range < 5) return 1;
    if (range < 20) return 5;
    return 10;
  }
}
