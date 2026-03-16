import 'dart:async';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../hal/device_manager.dart';
import '../protocol/ble_protocol.dart';
import '../protocol/data_models.dart';
import '../signal/processing_pipeline.dart';
import 'results_panel.dart';
import 'scan_history.dart';
import 'settings_screen.dart';
import 'voltammogram_chart.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final List<DpvDataPoint> _liveDataPoints = [];
  ScanResult? _lastResult;
  List<ContaminantResult> _detectedPeaks = const [];
  bool _showResults = false;

  StreamSubscription<DpvDataPoint>? _dataPointSub;
  StreamSubscription<ScanResult?>? _scanCompleteSub;

  @override
  void initState() {
    super.initState();
    _subscribeToStreams();
  }

  void _subscribeToStreams() {
    final manager = context.read<DeviceManager>();

    _dataPointSub = manager.dataPoints.listen((point) {
      setState(() {
        _liveDataPoints.add(point);
      });
    });

    _scanCompleteSub = manager.scanComplete.listen((result) {
      if (result != null) {
        setState(() {
          _lastResult = result;
          _detectedPeaks = result.contaminants;
          _showResults = true;
        });
      } else {
        // Process locally if device didn't send full result
        _processLocally();
      }
    });
  }

  void _processLocally() {
    if (_liveDataPoints.isEmpty) return;

    final pipeline = const ProcessingPipeline();
    final processed = pipeline.process(List.unmodifiable(_liveDataPoints));

    final safety = _computeSafety(processed.contaminants);

    setState(() {
      _detectedPeaks = processed.contaminants;
      _lastResult = ScanResult(
        testId: 'LOCAL-${DateTime.now().millisecondsSinceEpoch}',
        timestamp: DateTime.now(),
        dataPoints: List.unmodifiable(_liveDataPoints),
        metadata: const ScanMetadata(),
        contaminants: processed.contaminants,
        overallSafety: safety,
      );
      _showResults = true;
    });
  }

  String _computeSafety(List<ContaminantResult> contaminants) {
    if (contaminants.isEmpty) return 'Safe';
    final maxRatio =
        contaminants.map((c) => c.ratio).reduce((a, b) => a > b ? a : b);
    if (maxRatio > 2.0) return 'Unsafe';
    if (maxRatio > 1.0) return 'Caution';
    return 'Safe';
  }

  void _startScan(DeviceManager manager) {
    setState(() {
      _liveDataPoints.clear();
      _detectedPeaks = const [];
      _showResults = false;
      _lastResult = null;
    });
    manager.startScan();
  }

  @override
  void dispose() {
    _dataPointSub?.cancel();
    _scanCompleteSub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<DeviceManager>(
      builder: (context, manager, _) {
        return Scaffold(
          appBar: AppBar(
            title: const Text('JalSakhi'),
            actions: [
              IconButton(
                icon: const Icon(Icons.history),
                tooltip: 'Scan History',
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const ScanHistoryScreen(),
                  ),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.settings),
                tooltip: 'Settings',
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const SettingsScreen(),
                  ),
                ),
              ),
            ],
          ),
          body: Column(
            children: [
              _ConnectionBar(manager: manager),
              Expanded(
                child: _showResults && _lastResult != null
                    ? _ResultsView(
                        result: _lastResult!,
                        dataPoints: _liveDataPoints,
                        detectedPeaks: _detectedPeaks,
                        onBack: () => setState(() => _showResults = false),
                      )
                    : _ScanView(
                        dataPoints: _liveDataPoints,
                        detectedPeaks: _detectedPeaks,
                        isScanning: manager.isScanning,
                      ),
              ),
            ],
          ),
          bottomNavigationBar: _BottomControls(
            manager: manager,
            isScanning: manager.isScanning,
            showResults: _showResults,
            onStartScan: () => _startScan(manager),
            onStartDemoClean: () {
              setState(() {
                _liveDataPoints.clear();
                _detectedPeaks = const [];
                _showResults = false;
              });
              manager.startDemoClean();
            },
            onStartDemoContaminated: () {
              setState(() {
                _liveDataPoints.clear();
                _detectedPeaks = const [];
                _showResults = false;
              });
              manager.startDemoContaminated();
            },
            onStop: () => manager.stop(),
          ),
        );
      },
    );
  }
}

class _ConnectionBar extends StatelessWidget {
  final DeviceManager manager;

  const _ConnectionBar({required this.manager});

  @override
  Widget build(BuildContext context) {
    final isConnected = manager.isConnected;
    final color = isConnected
        ? const Color(0xFF4CAF50)
        : const Color(0xFFD7263D);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: color.withOpacity(0.15),
      child: Row(
        children: [
          Icon(
            isConnected ? Icons.bluetooth_connected : Icons.bluetooth_disabled,
            color: color,
            size: 18,
          ),
          const SizedBox(width: 8),
          Text(
            isConnected
                ? 'Connected: ${manager.connectedDeviceName}'
                : 'Disconnected',
            style: TextStyle(color: color, fontSize: 13),
          ),
          const Spacer(),
          if (!isConnected && !manager.isDemoMode)
            TextButton(
              onPressed: () => manager.setDemoMode(true),
              child: const Text(
                'Demo Mode',
                style: TextStyle(fontSize: 12),
              ),
            ),
          if (manager.isDemoMode)
            TextButton(
              onPressed: () => manager.setDemoMode(false),
              child: const Text(
                'Exit Demo',
                style: TextStyle(fontSize: 12, color: Colors.orangeAccent),
              ),
            ),
        ],
      ),
    );
  }
}

class _ScanView extends StatelessWidget {
  final List<DpvDataPoint> dataPoints;
  final List<ContaminantResult> detectedPeaks;
  final bool isScanning;

  const _ScanView({
    required this.dataPoints,
    required this.detectedPeaks,
    required this.isScanning,
  });

  @override
  Widget build(BuildContext context) {
    if (dataPoints.isEmpty && !isScanning) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.water_drop_outlined,
              size: 80,
              color: const Color(0xFF1B998B).withOpacity(0.4),
            ),
            const SizedBox(height: 16),
            const Text(
              'Ready to Test',
              style: TextStyle(
                color: Colors.white70,
                fontSize: 20,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Connect a device or enable Demo Mode\nthen start a scan.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white38, fontSize: 14),
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        if (isScanning)
          const Padding(
            padding: EdgeInsets.only(top: 8),
            child: LinearProgressIndicator(
              backgroundColor: Color(0xFF112240),
              color: Color(0xFF1B998B),
            ),
          ),
        Expanded(
          child: VoltammogramChart(
            dataPoints: dataPoints,
            detectedPeaks: detectedPeaks,
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            '${dataPoints.length} data points',
            style: const TextStyle(color: Colors.white38, fontSize: 12),
          ),
        ),
        const SizedBox(height: 8),
      ],
    );
  }
}

class _ResultsView extends StatelessWidget {
  final ScanResult result;
  final List<DpvDataPoint> dataPoints;
  final List<ContaminantResult> detectedPeaks;
  final VoidCallback onBack;

  const _ResultsView({
    required this.result,
    required this.dataPoints,
    required this.detectedPeaks,
    required this.onBack,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Mini chart
        SizedBox(
          height: 180,
          child: VoltammogramChart(
            dataPoints: dataPoints,
            detectedPeaks: detectedPeaks,
          ),
        ),
        // Back to chart button
        Align(
          alignment: Alignment.centerLeft,
          child: TextButton.icon(
            onPressed: onBack,
            icon: const Icon(Icons.arrow_back, size: 16),
            label: const Text('Back to Chart'),
          ),
        ),
        // Results
        Expanded(
          child: ResultsPanel(result: result),
        ),
      ],
    );
  }
}

class _BottomControls extends StatelessWidget {
  final DeviceManager manager;
  final bool isScanning;
  final bool showResults;
  final VoidCallback onStartScan;
  final VoidCallback onStartDemoClean;
  final VoidCallback onStartDemoContaminated;
  final VoidCallback onStop;

  const _BottomControls({
    required this.manager,
    required this.isScanning,
    required this.showResults,
    required this.onStartScan,
    required this.onStartDemoClean,
    required this.onStartDemoContaminated,
    required this.onStop,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      decoration: const BoxDecoration(
        color: Color(0xFF0A2463),
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      child: isScanning
          ? ElevatedButton.icon(
              onPressed: onStop,
              icon: const Icon(Icons.stop),
              label: const Text('Stop Scan'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFD7263D),
                minimumSize: const Size(double.infinity, 48),
              ),
            )
          : Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                ElevatedButton.icon(
                  onPressed: manager.isConnected ? onStartScan : null,
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('Start Scan'),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(double.infinity, 48),
                  ),
                ),
                if (manager.isDemoMode) ...[
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: onStartDemoClean,
                          style: OutlinedButton.styleFrom(
                            foregroundColor: const Color(0xFF4CAF50),
                            side: const BorderSide(
                              color: Color(0xFF4CAF50),
                              width: 0.5,
                            ),
                          ),
                          child: const Text('Demo: Clean'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: onStartDemoContaminated,
                          style: OutlinedButton.styleFrom(
                            foregroundColor: const Color(0xFFFF9800),
                            side: const BorderSide(
                              color: Color(0xFFFF9800),
                              width: 0.5,
                            ),
                          ),
                          child: const Text('Demo: Contaminated'),
                        ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
    );
  }
}
