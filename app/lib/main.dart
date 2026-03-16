import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:provider/provider.dart';

import 'hal/device_manager.dart';
import 'ui/home_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Hive.initFlutter();
  await Hive.openBox<Map>('scan_history');

  runApp(const JalSakhiApp());
}

class JalSakhiApp extends StatelessWidget {
  const JalSakhiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<DeviceManager>(
      create: (_) => DeviceManager(),
      child: MaterialApp(
        title: 'JalSakhi',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF0A2463),
            primary: const Color(0xFF0A2463),
            secondary: const Color(0xFF1B998B),
            error: const Color(0xFFD7263D),
            brightness: Brightness.dark,
          ),
          scaffoldBackgroundColor: const Color(0xFF0A1628),
          appBarTheme: const AppBarTheme(
            backgroundColor: Color(0xFF0A2463),
            foregroundColor: Colors.white,
            elevation: 0,
          ),
          cardTheme: CardTheme(
            color: const Color(0xFF112240),
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          elevatedButtonTheme: ElevatedButtonThemeData(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1B998B),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ),
        home: const HomeScreen(),
      ),
    );
  }
}
