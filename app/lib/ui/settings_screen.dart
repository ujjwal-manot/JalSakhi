import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../hal/device_manager.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _apiController = TextEditingController();
  bool _editingApi = false;

  @override
  void dispose() {
    _apiController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<DeviceManager>(
      builder: (context, manager, _) {
        return Scaffold(
          appBar: AppBar(title: const Text('Settings')),
          body: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Device Info
              _SectionHeader(title: 'Device'),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      _InfoRow(
                        label: 'Status',
                        value: manager.isConnected
                            ? 'Connected'
                            : 'Disconnected',
                        valueColor: manager.isConnected
                            ? const Color(0xFF4CAF50)
                            : const Color(0xFFD7263D),
                      ),
                      const Divider(color: Colors.white12),
                      _InfoRow(
                        label: 'Device Name',
                        value: manager.connectedDeviceName.isEmpty
                            ? 'None'
                            : manager.connectedDeviceName,
                      ),
                      const Divider(color: Colors.white12),
                      _InfoRow(
                        label: 'Mode',
                        value: manager.isDemoMode ? 'Demo' : 'Hardware',
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // Demo Mode
              _SectionHeader(title: 'Demo Mode'),
              Card(
                child: SwitchListTile(
                  title: const Text(
                    'Enable Demo Mode',
                    style: TextStyle(color: Colors.white),
                  ),
                  subtitle: const Text(
                    'Use simulated data without hardware',
                    style: TextStyle(color: Colors.white54, fontSize: 12),
                  ),
                  value: manager.isDemoMode,
                  onChanged: (value) => manager.setDemoMode(value),
                  activeColor: const Color(0xFF1B998B),
                ),
              ),

              const SizedBox(height: 24),

              // API Endpoint
              _SectionHeader(title: 'Cloud API'),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'API Endpoint',
                        style: TextStyle(color: Colors.white70, fontSize: 13),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _apiController,
                        style: const TextStyle(color: Colors.white),
                        decoration: InputDecoration(
                          hintText: 'https://api.example.com/v1',
                          hintStyle: const TextStyle(color: Colors.white24),
                          filled: true,
                          fillColor: const Color(0xFF0A1628),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: BorderSide.none,
                          ),
                          suffixIcon: IconButton(
                            icon: const Icon(Icons.save, color: Color(0xFF1B998B)),
                            onPressed: () {
                              // Save API endpoint (placeholder)
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('API endpoint saved'),
                                ),
                              );
                            },
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // About
              _SectionHeader(title: 'About'),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: const [
                      _InfoRow(label: 'App', value: 'JalSakhi'),
                      Divider(color: Colors.white12),
                      _InfoRow(label: 'Version', value: '1.0.0'),
                      Divider(color: Colors.white12),
                      _InfoRow(
                        label: 'Purpose',
                        value: 'Household water quality testing',
                      ),
                      Divider(color: Colors.white12),
                      _InfoRow(
                        label: 'Method',
                        value: 'Differential Pulse Voltammetry',
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 16),

              Center(
                child: Text(
                  'World Water Day 2026 Competition Entry',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.25),
                    fontSize: 12,
                  ),
                ),
              ),
              const SizedBox(height: 32),
            ],
          ),
        );
      },
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;

  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: const TextStyle(
          color: Color(0xFF1B998B),
          fontSize: 14,
          fontWeight: FontWeight.bold,
          letterSpacing: 1,
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  final Color? valueColor;

  const _InfoRow({
    required this.label,
    required this.value,
    this.valueColor,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(color: Colors.white54, fontSize: 14),
          ),
          Flexible(
            child: Text(
              value,
              style: TextStyle(
                color: valueColor ?? Colors.white,
                fontSize: 14,
              ),
              textAlign: TextAlign.end,
            ),
          ),
        ],
      ),
    );
  }
}
