import 'package:flutter/material.dart';

class DemoDestination {
  final String sourceSmartWalletId;
  final String bankAccountId;

  const DemoDestination({
    required this.sourceSmartWalletId,
    required this.bankAccountId,
  });

  Map<String, dynamic> toJson() => {
        'sourceSmartWalletId': sourceSmartWalletId,
        'bankAccountId': bankAccountId,
      };
}

class DemoUser {
  final String id;
  final String name;
  final String firstName;
  final String cardName;
  final String cohortLabel;
  final DemoDestination destination;

  const DemoUser({
    required this.id,
    required this.name,
    required this.firstName,
    required this.cardName,
    required this.cohortLabel,
    required this.destination,
  });
}

class Recipient {
  final String id;
  final String backendRecipientId;
  final String name;
  final String initials;
  final String subtitle;
  final bool isNew;
  final int defaultAmount;

  const Recipient({
    required this.id,
    required this.backendRecipientId,
    required this.name,
    required this.initials,
    required this.subtitle,
    required this.defaultAmount,
    this.isNew = false,
  });
}

class AppData {
  static const users = [
    DemoUser(
      id: 'user_001',
      name: 'Jewel Abimbola',
      firstName: 'Jewel',
      cardName: 'JEWEL A.',
      cohortLabel: 'Intervene demo',
      destination: DemoDestination(
        sourceSmartWalletId: 'fd627349-2343-4489-ae9b-988d12efee32',
        bankAccountId: '9a6d486a-5593-45a8-ae00-2f158a594560',
      ),
    ),
    DemoUser(
      id: 'user_002',
      name: 'Bola Adeyemi',
      firstName: 'Bola',
      cardName: 'BOLA A.',
      cohortLabel: 'Silent-pass demo',
      destination: DemoDestination(
        sourceSmartWalletId: 'd177e7a6-f9a9-4ffe-b215-3bb854852e69',
        bankAccountId: '3ae60b09-b5e6-42ae-b10e-e6bc469338a5',
      ),
    ),
  ];

  static const recipients = [
    Recipient(
      id: 'eliana',
      backendRecipientId: 'user_001_landlord',
      name: 'Eliana Baron',
      initials: 'EB',
      subtitle: 'Sent 12 times',
      defaultAmount: 100,
    ),
    Recipient(
      id: 'ademide',
      backendRecipientId: 'user_001_colleague',
      name: 'Ademide Johnson',
      initials: 'AJ',
      subtitle: 'Sent 7 times',
      defaultAmount: 100,
    ),
    Recipient(
      id: 'marcus',
      backendRecipientId: 'user_001_advance_refund_agent',
      name: 'Marcus Webb',
      initials: 'MW',
      subtitle: 'Added today',
      defaultAmount: 450,
      isNew: true,
    ),
  ];

  static DemoUser userById(String id) =>
      users.firstWhere((user) => user.id == id);

  static Recipient recipientById(String id) =>
      recipients.firstWhere((recipient) => recipient.id == id);

  static String recipientBackendIdForUser(Recipient recipient, DemoUser user) {
    if (recipient.id == 'marcus') return '${user.id}_advance_refund_agent';
    final suffix = recipient.backendRecipientId.split('${user.id}_').last;
    if (recipient.id == 'eliana') return '${user.id}_landlord';
    if (recipient.id == 'ademide') return '${user.id}_colleague';
    return '${user.id}_$suffix';
  }
}

enum RootTab { home, card, insights, profile }

extension RootTabIcon on RootTab {
  IconData get icon {
    switch (this) {
      case RootTab.home:
        return Icons.home_rounded;
      case RootTab.card:
        return Icons.credit_card_rounded;
      case RootTab.insights:
        return Icons.insights_rounded;
      case RootTab.profile:
        return Icons.person_rounded;
    }
  }

  String get label {
    switch (this) {
      case RootTab.home:
        return 'Home';
      case RootTab.card:
        return 'Card';
      case RootTab.insights:
        return 'Insights';
      case RootTab.profile:
        return 'Profile';
    }
  }
}
