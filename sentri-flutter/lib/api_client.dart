import 'dart:convert';
import 'package:http/http.dart' as http;
import 'config.dart';
import 'models.dart';

class ApiClient {
  final String baseUrl;

  ApiClient({String? baseUrl}) : baseUrl = baseUrl ?? Config.baseUrl;

  /// GET /debug/health
  Future<bool> checkHealth() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/debug/health'));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// GET /debug/profile/{user_id}
  Future<UserProfile> getProfile(String userId) async {
    final res = await http.get(Uri.parse('$baseUrl/debug/profile/$userId'));
    if (res.statusCode == 200) {
      return UserProfile.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
    }
    throw Exception('Failed to load profile: ${res.statusCode}');
  }

  /// POST /evaluate — the core Sentri scoring endpoint
  Future<EvaluateResult> evaluate({
    required String userId,
    required int amountKobo,
    required String recipientId,
    required String timestamp,
    String currency = 'NGN',
    bool crossBorder = false,
    String? memo,
    String language = 'en',
  }) async {
    final body = jsonEncode({
      'user_id': userId,
      'amount_kobo': amountKobo,
      'timestamp': timestamp,
      'recipient_id': recipientId,
      'currency': currency,
      'cross_border': crossBorder,
      'memo': memo,
      'language': language,
    });

    final res = await http.post(
      Uri.parse('$baseUrl/evaluate'),
      headers: {'Content-Type': 'application/json'},
      body: body,
    );

    if (res.statusCode == 200) {
      return EvaluateResult.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
    }
    throw Exception('Evaluate failed: ${res.statusCode} ${res.body}');
  }
}
