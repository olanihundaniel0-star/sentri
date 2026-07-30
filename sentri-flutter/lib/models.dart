/// Transaction from behavioral history
class Transaction {
  final int amountKobo;
  final DateTime timestamp;
  final String recipientId;
  final String currency;
  final String? memo;

  Transaction({
    required this.amountKobo,
    required this.timestamp,
    required this.recipientId,
    required this.currency,
    this.memo,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      amountKobo: json['amount_kobo'] as int,
      timestamp: DateTime.parse(json['timestamp'] as String),
      recipientId: json['recipient_id'] as String,
      currency: json['currency'] as String? ?? 'NGN',
      memo: json['memo'] as String?,
    );
  }

  String get displayAmount {
    final naira = amountKobo ~/ 100;
    final kobo = amountKobo % 100;
    final formatted = naira.toString().replaceAllMapped(
        RegExp(r'\B(?=(\d{3})+(?!\d))'), (_) => ',');
    return kobo == 0 ? '₦$formatted' : '₦$formatted.${kobo.toString().padLeft(2, '0')}';
  }
}

/// Recipient rollup from /debug/profile
class RecipientRollup {
  final String recipientId;
  final int count;
  final double meanKobo;
  final double stdKobo;
  final int minKobo;
  final int maxKobo;
  final DateTime firstSeen;
  final DateTime lastSeen;
  final int totalVolumeKobo;
  final List<Transaction> transactions;

  RecipientRollup({
    required this.recipientId,
    required this.count,
    required this.meanKobo,
    required this.stdKobo,
    required this.minKobo,
    required this.maxKobo,
    required this.firstSeen,
    required this.lastSeen,
    required this.totalVolumeKobo,
    required this.transactions,
  });

  factory RecipientRollup.fromJson(Map<String, dynamic> json) {
    return RecipientRollup(
      recipientId: json['recipient_id'] as String,
      count: json['count'] as int,
      meanKobo: (json['mean_kobo'] as num).toDouble(),
      stdKobo: (json['std_kobo'] as num).toDouble(),
      minKobo: json['min_kobo'] as int,
      maxKobo: json['max_kobo'] as int,
      firstSeen: DateTime.parse(json['first_seen'] as String),
      lastSeen: DateTime.parse(json['last_seen'] as String),
      totalVolumeKobo: json['total_volume_kobo'] as int,
      transactions: (json['transactions'] as List)
          .map((e) => Transaction.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

/// Full profile from /debug/profile/{user_id}
class UserProfile {
  final String userId;
  final Map<String, RecipientRollup> recipients;
  final double globalMeanKobo;
  final double globalStdKobo;
  final List<int> hourHistogram;
  final List<String> currenciesSeen;

  UserProfile({
    required this.userId,
    required this.recipients,
    required this.globalMeanKobo,
    required this.globalStdKobo,
    required this.hourHistogram,
    required this.currenciesSeen,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    final recipientsMap = (json['recipients'] as Map<String, dynamic>).map(
      (k, v) => MapEntry(k, RecipientRollup.fromJson(v as Map<String, dynamic>)),
    );
    return UserProfile(
      userId: json['user_id'] as String,
      recipients: recipientsMap,
      globalMeanKobo: (json['global_mean_kobo'] as num).toDouble(),
      globalStdKobo: (json['global_std_kobo'] as num).toDouble(),
      hourHistogram: (json['hour_histogram'] as List).cast<int>(),
      currenciesSeen: (json['currencies_seen'] as List).cast<String>(),
    );
  }

  List<Transaction> get allTransactions {
    final all = <Transaction>[];
    for (final r in recipients.values) {
      all.addAll(r.transactions);
    }
    all.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    return all;
  }
}

/// Verdict from POST /evaluate
/// kind: "silent_pass" | "intervene"
/// synthesizer_used: "claude" | "template" | "none"
class EvaluateResult {
  final String kind; // "silent_pass" | "intervene"
  final String? explanation;
  final List<String> triggeredReasons;
  final String synthesizerUsed; // "claude" | "template" | "none"

  EvaluateResult({
    required this.kind,
    this.explanation,
    this.triggeredReasons = const [],
    required this.synthesizerUsed,
  });

  factory EvaluateResult.fromJson(Map<String, dynamic> json) {
    return EvaluateResult(
      kind: json['kind'] as String,
      explanation: json['explanation'] as String?,
      triggeredReasons: (json['triggered_reasons'] as List?)?.cast<String>() ?? [],
      synthesizerUsed: json['synthesizer_used'] as String? ?? 'none',
    );
  }

  bool get isSilentPass => kind == 'silent_pass';
  bool get isIntervene => kind == 'intervene';

  // Structural reasons cannot trigger INTERVENE alone
  static const _structural = {'recipient_familiarity', 'graph_proximity'};
  List<String> get structuralReasons =>
      triggeredReasons.where((r) => _structural.contains(r)).toList();
  List<String> get nonStructuralReasons =>
      triggeredReasons.where((r) => !_structural.contains(r)).toList();
}
