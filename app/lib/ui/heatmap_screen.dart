/// Community contamination map screen.
///
/// Displays nearby test results from the API in a list/grid view,
/// color-coded by contamination level. Supports filtering by contaminant
/// and pull-to-refresh. Serves as a placeholder until full map integration.
import 'package:flutter/material.dart';

import '../protocol/api_client.dart';
import '../protocol/api_models.dart';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const _contaminantFilters = ['All', 'NH3', 'Pb', 'As', 'NO3', 'Fe'];

const _contaminantNames = {
  'NH3': 'Ammonia',
  'Pb': 'Lead',
  'As': 'Arsenic',
  'NO3': 'Nitrate',
  'Fe': 'Iron',
};

// ---------------------------------------------------------------------------
// Heatmap Screen
// ---------------------------------------------------------------------------

class HeatmapScreen extends StatefulWidget {
  final ApiClient apiClient;

  const HeatmapScreen({super.key, required this.apiClient});

  @override
  State<HeatmapScreen> createState() => _HeatmapScreenState();
}

class _HeatmapScreenState extends State<HeatmapScreen> {
  List<TestSummary> _tests = const [];
  List<AlertData> _alerts = const [];
  DistrictStats? _stats;
  bool _isLoading = false;
  String? _errorMessage;
  String _selectedFilter = 'All';
  DateTime? _lastUpdated;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final results = await Future.wait([
        widget.apiClient.getTests(limit: 50),
        widget.apiClient.getAlerts(),
        widget.apiClient.getStats(),
      ]);

      setState(() {
        _tests = results[0] as List<TestSummary>;
        _alerts = results[1] as List<AlertData>;
        _stats = results[2] as DistrictStats;
        _lastUpdated = DateTime.now();
        _isLoading = false;
      });
    } on ApiException catch (e) {
      setState(() {
        _errorMessage = e.message;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Could not load data. Please check your connection.';
        _isLoading = false;
      });
    }
  }

  List<TestSummary> get _filteredTests {
    if (_selectedFilter == 'All') return _tests;
    return _tests.where((t) {
      return t.contaminantReadings.any((c) => c.symbol == _selectedFilter);
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Community Map'),
        actions: [
          if (_lastUpdated != null)
            Center(
              child: Padding(
                padding: const EdgeInsets.only(right: 8),
                child: Text(
                  'Updated ${_formatTime(_lastUpdated!)}',
                  style: const TextStyle(
                    color: Colors.white38,
                    fontSize: 11,
                  ),
                ),
              ),
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: _buildBody(),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _tests.isEmpty) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(color: Color(0xFF1B998B)),
            SizedBox(height: 16),
            Text(
              'Loading community data...',
              style: TextStyle(color: Colors.white54),
            ),
          ],
        ),
      );
    }

    if (_errorMessage != null && _tests.isEmpty) {
      return _ErrorView(
        message: _errorMessage!,
        onRetry: _loadData,
      );
    }

    return CustomScrollView(
      slivers: [
        // Stats bar
        if (_stats != null) _buildStatsBar(),

        // Active alerts
        if (_alerts.isNotEmpty) _buildAlertsSection(),

        // Filter chips
        _buildFilterChips(),

        // Map placeholder
        _buildMapPlaceholder(),

        // Test results list
        if (_filteredTests.isEmpty)
          const SliverFillRemaining(
            child: Center(
              child: Text(
                'No test results found for this filter.',
                style: TextStyle(color: Colors.white54),
              ),
            ),
          )
        else
          _buildTestList(),

        // Bottom padding
        const SliverPadding(padding: EdgeInsets.only(bottom: 24)),
      ],
    );
  }

  SliverToBoxAdapter _buildStatsBar() {
    return SliverToBoxAdapter(
      child: Container(
        margin: const EdgeInsets.fromLTRB(16, 12, 16, 4),
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
        decoration: BoxDecoration(
          color: const Color(0xFF112240),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _StatChip(
              label: 'Tests',
              value: _stats!.totalTests.toString(),
              icon: Icons.science_outlined,
            ),
            _StatChip(
              label: 'Unsafe',
              value: _stats!.unsafeSources.toString(),
              icon: Icons.warning_amber,
              valueColor: _stats!.unsafeSources > 0
                  ? const Color(0xFFD7263D)
                  : const Color(0xFF4CAF50),
            ),
            _StatChip(
              label: 'Testers',
              value: _stats!.activeTesters.toString(),
              icon: Icons.people_outline,
            ),
          ],
        ),
      ),
    );
  }

  SliverToBoxAdapter _buildAlertsSection() {
    return SliverToBoxAdapter(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.fromLTRB(16, 12, 16, 8),
            child: Row(
              children: [
                Icon(Icons.notification_important,
                    color: Color(0xFFD7263D), size: 18),
                SizedBox(width: 6),
                Text(
                  'Active Alerts',
                  style: TextStyle(
                    color: Color(0xFFD7263D),
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          SizedBox(
            height: 80,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 12),
              itemCount: _alerts.length,
              itemBuilder: (context, index) =>
                  _AlertChip(alert: _alerts[index]),
            ),
          ),
        ],
      ),
    );
  }

  SliverToBoxAdapter _buildFilterChips() {
    return SliverToBoxAdapter(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
        child: Wrap(
          spacing: 8,
          children: _contaminantFilters.map((filter) {
            final isSelected = _selectedFilter == filter;
            return ChoiceChip(
              label: Text(
                filter == 'All'
                    ? 'All'
                    : _contaminantNames[filter] ?? filter,
                style: TextStyle(
                  fontSize: 12,
                  color: isSelected ? Colors.white : Colors.white54,
                ),
              ),
              selected: isSelected,
              selectedColor: const Color(0xFF1B998B),
              backgroundColor: const Color(0xFF112240),
              onSelected: (_) => setState(() => _selectedFilter = filter),
            );
          }).toList(),
        ),
      ),
    );
  }

  SliverToBoxAdapter _buildMapPlaceholder() {
    return SliverToBoxAdapter(
      child: Container(
        margin: const EdgeInsets.fromLTRB(16, 4, 16, 12),
        height: 120,
        decoration: BoxDecoration(
          color: const Color(0xFF112240),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: const Color(0xFF1B998B).withOpacity(0.3),
          ),
        ),
        child: const Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.map_outlined, color: Colors.white24, size: 36),
              SizedBox(height: 8),
              Text(
                'Interactive map coming soon',
                style: TextStyle(color: Colors.white38, fontSize: 13),
              ),
              Text(
                'Showing results as list below',
                style: TextStyle(color: Colors.white24, fontSize: 11),
              ),
            ],
          ),
        ),
      ),
    );
  }

  SliverList _buildTestList() {
    return SliverList(
      delegate: SliverChildBuilderDelegate(
        (context, index) {
          if (index == 0) {
            return Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
              child: Text(
                '${_filteredTests.length} nearby results',
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
            );
          }
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: _TestResultCard(test: _filteredTests[index - 1]),
          );
        },
        childCount: _filteredTests.length + 1,
      ),
    );
  }

  String _formatTime(DateTime dt) {
    return '${_pad(dt.hour)}:${_pad(dt.minute)}';
  }

  String _pad(int n) => n.toString().padLeft(2, '0');
}

// ---------------------------------------------------------------------------
// Sub-widgets
// ---------------------------------------------------------------------------

class _ErrorView extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _ErrorView({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off, color: Colors.white38, size: 48),
            const SizedBox(height: 16),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.white54, fontSize: 14),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh, size: 18),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatChip extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color? valueColor;

  const _StatChip({
    required this.label,
    required this.value,
    required this.icon,
    this.valueColor,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: Colors.white38, size: 18),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            color: valueColor ?? Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(color: Colors.white38, fontSize: 11),
        ),
      ],
    );
  }
}

class _AlertChip extends StatelessWidget {
  final AlertData alert;

  const _AlertChip({required this.alert});

  @override
  Widget build(BuildContext context) {
    final isCritical = alert.severity == 'critical';
    final color = isCritical
        ? const Color(0xFFD7263D)
        : const Color(0xFFFF9800);

    return Container(
      width: 200,
      margin: const EdgeInsets.symmetric(horizontal: 4),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Icon(
                isCritical ? Icons.dangerous : Icons.warning_amber,
                color: color,
                size: 14,
              ),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  alert.locationName,
                  style: TextStyle(
                    color: color,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            '${_contaminantNames[alert.contaminant] ?? alert.contaminant}: '
            '${alert.value} (${alert.severity})',
            style: const TextStyle(color: Colors.white54, fontSize: 11),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

class _TestResultCard extends StatelessWidget {
  final TestSummary test;

  const _TestResultCard({required this.test});

  @override
  Widget build(BuildContext context) {
    final safety = test.overallSafety;
    final (color, icon) = switch (safety) {
      'Safe' => (const Color(0xFF4CAF50), Icons.check_circle_outline),
      'Caution' => (const Color(0xFFFF9800), Icons.warning_amber),
      'Unsafe' => (const Color(0xFFD7263D), Icons.dangerous),
      _ => (Colors.grey, Icons.help_outline),
    };

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            // Safety indicator
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: color, size: 22),
            ),
            const SizedBox(width: 12),
            // Details
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${test.sourceType.toUpperCase()} - ${_formatDate(test.timestamp)}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 2),
                  if (test.contaminantReadings.isNotEmpty)
                    Text(
                      test.contaminantReadings
                          .map((c) => '${c.symbol}: ${c.value} ${c.unit}')
                          .join(', '),
                      style:
                          const TextStyle(color: Colors.white54, fontSize: 11),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  const SizedBox(height: 2),
                  Text(
                    'by ${test.testerName}',
                    style:
                        const TextStyle(color: Colors.white30, fontSize: 10),
                  ),
                ],
              ),
            ),
            // Confidence / safety badge
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                safety,
                style: TextStyle(
                  color: color,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime dt) {
    return '${dt.year}-${_pad(dt.month)}-${_pad(dt.day)} '
        '${_pad(dt.hour)}:${_pad(dt.minute)}';
  }

  String _pad(int n) => n.toString().padLeft(2, '0');
}
