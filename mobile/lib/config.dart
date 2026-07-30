import 'package:flutter/material.dart';

class UserMeta {
  final String name;
  final String cohortLabel;
  final String description;
  final Color color;
  final IconData icon;

  const UserMeta({
    required this.name,
    required this.cohortLabel,
    required this.description,
    required this.color,
    required this.icon,
  });
}

class Config {
  /// Backend base URL. Override at build/run time so a physical device can
  /// reach the backend over the LAN instead of the Android-emulator-only
  /// `10.0.2.2` alias, e.g.:
  ///   flutter run --dart-define=API_BASE_URL=http://192.168.1.23:8000
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  static const List<String> demoUsers = ['user_001', 'user_002'];

  static const Map<String, UserMeta> userMeta = {
    'user_001': UserMeta(
      name: 'User 001',
      cohortLabel: 'Cohort A · Anomalous',
      description: 'Triggers INTERVENE',
      color: Color(0xFFFF6B35),
      icon: Icons.warning_amber_rounded,
    ),
    'user_002': UserMeta(
      name: 'User 002',
      cohortLabel: 'Cohort D · Normal',
      description: 'Triggers SILENT_PASS',
      color: Color(0xFF00D4AA),
      icon: Icons.check_circle_rounded,
    ),
  };
}
