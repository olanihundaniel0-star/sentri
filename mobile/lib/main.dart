import 'package:flutter/material.dart';

import 'design_system.dart';
import 'screens/user_select_screen.dart';

void main() {
  runApp(const SentriApp());
}

class SentriApp extends StatelessWidget {
  const SentriApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sentri',
      debugShowCheckedModeBanner: false,
      theme: buildSentriTheme(),
      home: const UserSelectScreen(),
    );
  }
}
