import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';

import '../protocol/ble_protocol.dart';
import '../protocol/data_models.dart';
import 'demo_device.dart';

/// Hardware abstraction layer that manages device connections.
///
/// Supports both real BLE devices and a mock [DemoDevice] for
/// development without hardware.
class DeviceManager extends ChangeNotifier {
  final BleProtocol _bleProtocol = BleProtocol();
  DemoDevice? _demoDevice;

  bool _isDemoMode = false;
  bool _isScanning = false;
  BleConnectionState _connectionState = BleConnectionState.disconnected;
  String _connectedDeviceName = '';
  String _statusMessage = '';

  final _dataPointController = StreamController<DpvDataPoint>.broadcast();
  final _scanCompleteController = StreamController<ScanResult?>.broadcast();

  StreamSubscription<BleConnectionState>? _connectionSub;
  StreamSubscription<DpvDataPoint>? _dataPointSub;
  StreamSubscription<void>? _scanCompleteSub;
  StreamSubscription<String>? _statusSub;

  // --- Public getters ---

  bool get isDemoMode => _isDemoMode;
  bool get isScanning => _isScanning;
  bool get isConnected => _connectionState == BleConnectionState.connected;
  BleConnectionState get connectionState => _connectionState;
  String get connectedDeviceName => _connectedDeviceName;
  String get statusMessage => _statusMessage;

  Stream<DpvDataPoint> get dataPoints => _dataPointController.stream;
  Stream<ScanResult?> get scanComplete => _scanCompleteController.stream;

  // --- Demo mode ---

  void setDemoMode(bool enabled) {
    if (_isDemoMode == enabled) return;
    _isDemoMode = enabled;

    if (enabled) {
      _demoDevice = DemoDevice();
      _connectionState = BleConnectionState.connected;
      _connectedDeviceName = 'JalSakhi-DEMO';
      _subscribeToDemoDevice();
    } else {
      _demoDevice?.dispose();
      _demoDevice = null;
      _connectionState = BleConnectionState.disconnected;
      _connectedDeviceName = '';
    }
    notifyListeners();
  }

  void _subscribeToDemoDevice() {
    _dataPointSub?.cancel();
    _scanCompleteSub?.cancel();

    _dataPointSub = _demoDevice!.dataPoints.listen((point) {
      _dataPointController.add(point);
    });

    _scanCompleteSub = _demoDevice!.scanComplete.listen((result) {
      _isScanning = false;
      _scanCompleteController.add(result);
      notifyListeners();
    });
  }

  // --- BLE device scanning ---

  Stream<ScanResult_BLE> scanForDevices() {
    return FlutterBluePlus.onScanResults.map((results) {
      return results;
    }).expand((results) => results).where((r) {
      final name = r.device.platformName;
      return name.startsWith('JalSakhi');
    }).map((r) => ScanResult_BLE(
          device: r.device,
          name: r.device.platformName,
          rssi: r.rssi,
        ));
  }

  Future<void> startDeviceScan() async {
    await FlutterBluePlus.startScan(
      timeout: const Duration(seconds: 10),
      withNames: ['JalSakhi'],
    );
  }

  Future<void> stopDeviceScan() async {
    await FlutterBluePlus.stopScan();
  }

  // --- Connection management ---

  Future<void> connect(BluetoothDevice device) async {
    _connectionSub?.cancel();
    _dataPointSub?.cancel();
    _scanCompleteSub?.cancel();
    _statusSub?.cancel();

    _connectionSub = _bleProtocol.connectionState.listen((state) {
      _connectionState = state;
      if (state == BleConnectionState.connected) {
        _connectedDeviceName = device.platformName;
      } else if (state == BleConnectionState.disconnected) {
        _connectedDeviceName = '';
      }
      notifyListeners();
    });

    _dataPointSub = _bleProtocol.dataPoints.listen((point) {
      _dataPointController.add(point);
    });

    _scanCompleteSub = _bleProtocol.scanComplete.listen((_) {
      _isScanning = false;
      _scanCompleteController.add(null);
      notifyListeners();
    });

    _statusSub = _bleProtocol.status.listen((msg) {
      _statusMessage = msg;
      notifyListeners();
    });

    await _bleProtocol.connect(device);
  }

  Future<void> disconnect() async {
    if (_isDemoMode) {
      setDemoMode(false);
      return;
    }
    await _bleProtocol.disconnect();
  }

  // --- Scan commands ---

  Future<void> startScan() async {
    _isScanning = true;
    notifyListeners();

    if (_isDemoMode) {
      _demoDevice?.startScan();
    } else {
      await _bleProtocol.sendCommand(BleCommands.startScan);
    }
  }

  Future<void> startDemoClean() async {
    _isScanning = true;
    notifyListeners();

    if (_isDemoMode) {
      _demoDevice?.startDemoClean();
    } else {
      await _bleProtocol.sendCommand(BleCommands.demoClean);
    }
  }

  Future<void> startDemoContaminated() async {
    _isScanning = true;
    notifyListeners();

    if (_isDemoMode) {
      _demoDevice?.startDemoContaminated();
    } else {
      await _bleProtocol.sendCommand(BleCommands.demoContaminated);
    }
  }

  Future<void> stop() async {
    _isScanning = false;
    notifyListeners();

    if (_isDemoMode) {
      _demoDevice?.stop();
    } else {
      await _bleProtocol.sendCommand(BleCommands.stop);
    }
  }

  Future<void> calibrate() async {
    if (_isDemoMode) return;
    await _bleProtocol.sendCommand(BleCommands.calibrate);
  }

  @override
  void dispose() {
    _connectionSub?.cancel();
    _dataPointSub?.cancel();
    _scanCompleteSub?.cancel();
    _statusSub?.cancel();
    _demoDevice?.dispose();
    _bleProtocol.dispose();
    _dataPointController.close();
    _scanCompleteController.close();
    super.dispose();
  }
}

/// Lightweight scan result for device discovery UI.
@immutable
class ScanResult_BLE {
  final BluetoothDevice device;
  final String name;
  final int rssi;

  const ScanResult_BLE({
    required this.device,
    required this.name,
    required this.rssi,
  });
}
