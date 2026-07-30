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
  static const String baseUrl = 'http://10.0.2.2:8000';

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
