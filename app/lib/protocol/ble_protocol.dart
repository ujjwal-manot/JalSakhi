import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:flutter_blue_plus/flutter_blue_plus.dart';

import 'data_models.dart';

/// BLE UUIDs matching the ESP32 firmware.
class BleUuids {
  static const serviceUuid = '4fafc201-1fb5-459e-8fcc-c5c9c331914b';
  static const txCharUuid = 'beb5483e-36e1-4688-b7f5-ea07361b26a8';
  static const rxCharUuid = '6e400002-b5a3-f393-e0a9-e50e24dcca9e';
}

/// Commands the app can send to the ESP32.
class BleCommands {
  static const startScan = 'START_SCAN\n';
  static const demoClean = 'DEMO_CLEAN\n';
  static const demoContaminated = 'DEMO_CONTAMINATED\n';
  static const stop = 'STOP\n';
  static const calibrate = 'CALIBRATE\n';
}

/// Connection states exposed by the protocol layer.
enum BleConnectionState {
  disconnected,
  connecting,
  connected,
  disconnecting,
}

/// Handles BLE communication with the JalSakhi ESP32 potentiostat.
class BleProtocol {
  BluetoothDevice? _device;
  BluetoothCharacteristic? _txChar;
  BluetoothCharacteristic? _rxChar;
  StreamSubscription<List<int>>? _notifySub;
  StreamSubscription<BluetoothConnectionState>? _connectionSub;

  final _connectionStateController =
      StreamController<BleConnectionState>.broadcast();
  final _dataPointController = StreamController<DpvDataPoint>.broadcast();
  final _scanCompleteController = StreamController<void>.broadcast();
  final _statusController = StreamController<String>.broadcast();
  final _metadataController = StreamController<ScanMetadata>.broadcast();

  String _lineBuffer = '';
  int _reconnectAttempts = 0;
  static const _maxReconnectAttempts = 5;
  bool _shouldReconnect = false;

  /// Stream of connection state changes.
  Stream<BleConnectionState> get connectionState =>
      _connectionStateController.stream;

  /// Stream of incoming DPV data points.
  Stream<DpvDataPoint> get dataPoints => _dataPointController.stream;

  /// Fires when a scan completes.
  Stream<void> get scanComplete => _scanCompleteController.stream;

  /// Stream of status messages from the device.
  Stream<String> get status => _statusController.stream;

  /// Stream of metadata received from device.
  Stream<ScanMetadata> get metadata => _metadataController.stream;

  /// Connect to a discovered BLE device.
  Future<void> connect(BluetoothDevice device) async {
    _device = device;
    _shouldReconnect = true;
    _reconnectAttempts = 0;
    _connectionStateController.add(BleConnectionState.connecting);

    try {
      await device.connect(autoConnect: false, timeout: const Duration(seconds: 10));
      await _discoverAndSubscribe(device);
      _reconnectAttempts = 0;
      _connectionStateController.add(BleConnectionState.connected);

      _connectionSub = device.connectionState.listen((state) {
        if (state == BluetoothConnectionState.disconnected) {
          _connectionStateController.add(BleConnectionState.disconnected);
          _attemptReconnect();
        }
      });
    } catch (e) {
      _connectionStateController.add(BleConnectionState.disconnected);
      _attemptReconnect();
    }
  }

  Future<void> _discoverAndSubscribe(BluetoothDevice device) async {
    final services = await device.discoverServices();
    final service = services.firstWhere(
      (s) => s.uuid.toString().toLowerCase() == BleUuids.serviceUuid,
      orElse: () => throw Exception('JalSakhi BLE service not found'),
    );

    _txChar = service.characteristics.firstWhere(
      (c) => c.uuid.toString().toLowerCase() == BleUuids.txCharUuid,
      orElse: () => throw Exception('TX characteristic not found'),
    );

    _rxChar = service.characteristics.firstWhere(
      (c) => c.uuid.toString().toLowerCase() == BleUuids.rxCharUuid,
      orElse: () => throw Exception('RX characteristic not found'),
    );

    await _txChar!.setNotifyValue(true);
    _notifySub = _txChar!.onValueReceived.listen(_onDataReceived);
  }

  void _onDataReceived(List<int> data) {
    _lineBuffer += utf8.decode(data, allowMalformed: true);

    while (_lineBuffer.contains('\n')) {
      final newlineIndex = _lineBuffer.indexOf('\n');
      final line = _lineBuffer.substring(0, newlineIndex).trim();
      _lineBuffer = _lineBuffer.substring(newlineIndex + 1);

      if (line.isNotEmpty) {
        _parseLine(line);
      }
    }
  }

  void _parseLine(String line) {
    // Data point: V:<float>,I:<float>
    if (line.startsWith('V:')) {
      final point = _parseDataPoint(line);
      if (point != null) {
        _dataPointController.add(point);
      }
      return;
    }

    // Metadata: META:temp=<float>,ph=<float>,tds=<float>
    if (line.startsWith('META:')) {
      final meta = _parseMetadata(line.substring(5));
      if (meta != null) {
        _metadataController.add(meta);
      }
      return;
    }

    // Scan complete
    if (line == 'SCAN_COMPLETE') {
      _scanCompleteController.add(null);
      return;
    }

    // Status message
    if (line.startsWith('STATUS:')) {
      _statusController.add(line.substring(7));
      return;
    }
  }

  DpvDataPoint? _parseDataPoint(String line) {
    try {
      final parts = line.split(',');
      final voltage =
          double.parse(parts[0].substring(2)); // after "V:"
      final current =
          double.parse(parts[1].substring(2)); // after "I:"
      return DpvDataPoint(voltage: voltage, current: current);
    } catch (_) {
      return null;
    }
  }

  ScanMetadata? _parseMetadata(String raw) {
    try {
      final pairs = raw.split(',');
      double? temp, ph, tds;
      for (final pair in pairs) {
        final kv = pair.split('=');
        if (kv.length != 2) continue;
        final key = kv[0].trim();
        final val = double.tryParse(kv[1].trim());
        switch (key) {
          case 'temp':
            temp = val;
          case 'ph':
            ph = val;
          case 'tds':
            tds = val;
        }
      }
      return ScanMetadata(temperature: temp, ph: ph, tds: tds);
    } catch (_) {
      return null;
    }
  }

  /// Send a command string to the device.
  Future<void> sendCommand(String command) async {
    if (_rxChar == null) {
      throw Exception('Not connected to device');
    }
    await _rxChar!.write(utf8.encode(command), withoutResponse: false);
  }

  /// Disconnect from the device.
  Future<void> disconnect() async {
    _shouldReconnect = false;
    _connectionStateController.add(BleConnectionState.disconnecting);
    await _notifySub?.cancel();
    await _connectionSub?.cancel();
    _notifySub = null;
    _connectionSub = null;
    await _device?.disconnect();
    _device = null;
    _txChar = null;
    _rxChar = null;
    _lineBuffer = '';
    _connectionStateController.add(BleConnectionState.disconnected);
  }

  void _attemptReconnect() {
    if (!_shouldReconnect) return;
    if (_reconnectAttempts >= _maxReconnectAttempts) {
      _statusController.add('Reconnection failed after $_maxReconnectAttempts attempts');
      return;
    }

    _reconnectAttempts++;
    final delay = Duration(
      milliseconds: min(1000 * pow(2, _reconnectAttempts).toInt(), 30000),
    );

    Future.delayed(delay, () async {
      if (!_shouldReconnect || _device == null) return;
      _connectionStateController.add(BleConnectionState.connecting);
      try {
        await _device!.connect(autoConnect: false, timeout: const Duration(seconds: 10));
        await _discoverAndSubscribe(_device!);
        _reconnectAttempts = 0;
        _connectionStateController.add(BleConnectionState.connected);
      } catch (_) {
        _connectionStateController.add(BleConnectionState.disconnected);
        _attemptReconnect();
      }
    });
  }

  /// Clean up all resources.
  void dispose() {
    _shouldReconnect = false;
    _notifySub?.cancel();
    _connectionSub?.cancel();
    _connectionStateController.close();
    _dataPointController.close();
    _scanCompleteController.close();
    _statusController.close();
    _metadataController.close();
  }
}
