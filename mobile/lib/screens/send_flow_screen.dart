import 'dart:ui';

import 'package:flutter/material.dart';

import '../api_client.dart';
import '../app_data.dart';
import '../design_system.dart';
import '../models.dart';
import '../widgets/sentri_mascot.dart';
import '../widgets/ui_components.dart';

class SendFlowScreen extends StatefulWidget {
  final DemoUser user;
  final bool sentriOn;
  final VoidCallback onCancelled;

  const SendFlowScreen({
    super.key,
    required this.user,
    required this.sentriOn,
    required this.onCancelled,
  });

  @override
  State<SendFlowScreen> createState() => _SendFlowScreenState();
}

class _SendFlowScreenState extends State<SendFlowScreen> {
  final _api = ApiClient();
  Recipient? _recipient;
  int _amount = 100;
  TransferResponse? _held;
  bool _submitting = false;
  bool _sheetOpen = false;
  String? _error;
  _SendStep _step = _SendStep.recipient;

  Future<void> _submitTransfer() async {
    if (_recipient == null) return;
    setState(() {
      _submitting = true;
      _error = null;
    });

    try {
      final recipient = _recipient!;
      final response = await _api.createTransfer(
        TransferRequest(
          userId: widget.user.id,
          amountKobo: _amount * 100,
          recipientId:
              AppData.recipientBackendIdForUser(recipient, widget.user),
          destination: widget.user.destination.toJson(),
          currency: 'NGN',
          crossBorder: recipient.isNew,
          memo: 'Transfer to ${recipient.name}',
        ),
      );
      if (!mounted) return;
      if (response.isHeld && widget.sentriOn) {
        setState(() {
          _held = response;
          _sheetOpen = true;
          _submitting = false;
        });
      } else {
        setState(() {
          _submitting = false;
          _step = _SendStep.success;
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _submitting = false;
        _error = _cleanError(e);
      });
    }
  }

  Future<void> _confirmHeld() async {
    final transferId = _held?.transferId;
    if (transferId == null) return;
    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      await _api.confirmTransfer(transferId);
      if (!mounted) return;
      setState(() {
        _submitting = false;
        _sheetOpen = false;
        _step = _SendStep.success;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _submitting = false;
        _error = _cleanError(e);
      });
    }
  }

  String _cleanError(Object error) {
    final text = error.toString();
    if (text.contains('BMONI_API_KEY not configured')) {
      return 'The backend evaluated the transfer, but live BMONI execution is not configured.';
    }
    return text.replaceFirst('Exception: ', '');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          AnimatedSwitcher(
              duration: const Duration(milliseconds: 240), child: _content()),
          if (_sheetOpen && _recipient != null)
            _SentriSheet(
              recipient: _recipient!,
              amount: _amount,
              explanation: _held?.explanation,
              loading: _submitting,
              error: _error,
              onClose: () => setState(() => _sheetOpen = false),
              onReview: () => setState(() {
                _sheetOpen = false;
                _step = _SendStep.reviewDetail;
              }),
              onGoAnyway: _confirmHeld,
            ),
        ],
      ),
    );
  }

  Widget _content() {
    switch (_step) {
      case _SendStep.recipient:
        return _RecipientStep(
          onBack: () => Navigator.pop(context),
          onPick: (recipient) => setState(() {
            _recipient = recipient;
            _amount = recipient.defaultAmount;
            _step = _SendStep.amount;
            _error = null;
          }),
        );
      case _SendStep.amount:
        return _AmountStep(
          recipient: _recipient!,
          amount: _amount,
          onBack: () => setState(() => _step = _SendStep.recipient),
          onAmount: (amount) => setState(() => _amount = amount),
          onContinue: () => setState(() => _step = _SendStep.review),
        );
      case _SendStep.review:
        return _ReviewStep(
          recipient: _recipient!,
          amount: _amount,
          loading: _submitting,
          error: _error,
          onBack: () => setState(() => _step = _SendStep.amount),
          onConfirm: _submitTransfer,
        );
      case _SendStep.reviewDetail:
        return _ReviewDetailStep(
          recipient: _recipient!,
          amount: _amount,
          loading: _submitting,
          error: _error,
          onBack: () => setState(() {
            _step = _SendStep.review;
            _sheetOpen = true;
          }),
          onCancel: () {
            widget.onCancelled();
            Navigator.pop(context);
          },
          onSendAnyway: _confirmHeld,
        );
      case _SendStep.success:
        return _SuccessStep(
          recipient: _recipient!,
          amount: _amount,
          onDone: () => Navigator.pop(context),
        );
    }
  }
}

enum _SendStep { recipient, amount, review, reviewDetail, success }

class _RecipientStep extends StatelessWidget {
  final VoidCallback onBack;
  final ValueChanged<Recipient> onPick;

  const _RecipientStep({required this.onBack, required this.onPick});

  @override
  Widget build(BuildContext context) {
    return PrimaryScaffoldPadding(
      padding: const EdgeInsets.fromLTRB(20, 58, 20, 34),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        _Header(title: 'Send money', onBack: onBack),
        const SizedBox(height: 22),
        TextField(
          readOnly: true,
          decoration: InputDecoration(
            hintText: 'Search recipients',
            prefixIcon: Icon(Icons.search_rounded, color: SentriColors.muted3),
          ),
        ),
        const SizedBox(height: 24),
        const SectionHeader('Frequent'),
        const SizedBox(height: 6),
        _RecipientRow(
            recipient: AppData.recipients[0],
            onTap: () => onPick(AppData.recipients[0])),
        _RecipientRow(
            recipient: AppData.recipients[1],
            onTap: () => onPick(AppData.recipients[1])),
        const SizedBox(height: 18),
        const SectionHeader('New'),
        const SizedBox(height: 6),
        _RecipientRow(
            recipient: AppData.recipients[2],
            onTap: () => onPick(AppData.recipients[2])),
      ]),
    );
  }
}

class _AmountStep extends StatelessWidget {
  final Recipient recipient;
  final int amount;
  final VoidCallback onBack;
  final ValueChanged<int> onAmount;
  final VoidCallback onContinue;

  const _AmountStep({
    required this.recipient,
    required this.amount,
    required this.onBack,
    required this.onAmount,
    required this.onContinue,
  });

  @override
  Widget build(BuildContext context) {
    return PrimaryScaffoldPadding(
      padding: const EdgeInsets.fromLTRB(20, 58, 20, 34),
      child: Column(children: [
        _Header(title: 'Send money', onBack: onBack),
        const SizedBox(height: 18),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
              color: SentriColors.surface2,
              borderRadius: BorderRadius.circular(999)),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            RecipientAvatar(initials: recipient.initials, size: 24),
            const SizedBox(width: 8),
            Text('To ${recipient.name}',
                style: Theme.of(context)
                    .textTheme
                    .bodyLarge
                    ?.copyWith(fontSize: 13.5)),
          ]),
        ),
        const Spacer(),
        Text('₦$amount', style: monoStyle(size: 54, weight: FontWeight.w500)),
        const SizedBox(height: 28),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [50, 100, 250, 450]
              .map((value) => Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 5),
                    child: _AmountChip(
                        value: value,
                        selected: amount == value,
                        onTap: () => onAmount(value)),
                  ))
              .toList(),
        ),
        const Spacer(),
        ElevatedButton(onPressed: onContinue, child: const Text('Continue')),
      ]),
    );
  }
}

class _ReviewStep extends StatelessWidget {
  final Recipient recipient;
  final int amount;
  final bool loading;
  final String? error;
  final VoidCallback onBack;
  final VoidCallback onConfirm;

  const _ReviewStep({
    required this.recipient,
    required this.amount,
    required this.loading,
    required this.error,
    required this.onBack,
    required this.onConfirm,
  });

  @override
  Widget build(BuildContext context) {
    return PrimaryScaffoldPadding(
      padding: const EdgeInsets.fromLTRB(20, 58, 20, 34),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        _Header(title: 'Review transfer', onBack: onBack),
        const SizedBox(height: 24),
        _SummaryTile(recipient: recipient, amount: amount),
        const SizedBox(height: 18),
        _DetailCard(rows: [
          const ('Arrives', 'Within minutes'),
          const ('Fee', 'Free'),
          ('Total', '₦$amount.00'),
        ]),
        if (error != null) ...[
          const SizedBox(height: 14),
          _ErrorBox(error!),
        ],
        const Spacer(),
        ElevatedButton(
          onPressed: loading ? null : onConfirm,
          child: Text(loading ? 'Running Sentri check...' : 'Confirm transfer'),
        ),
      ]),
    );
  }
}

class _SentriSheet extends StatelessWidget {
  final Recipient recipient;
  final int amount;
  final String? explanation;
  final bool loading;
  final String? error;
  final VoidCallback onClose;
  final VoidCallback onReview;
  final VoidCallback onGoAnyway;

  const _SentriSheet({
    required this.recipient,
    required this.amount,
    required this.explanation,
    required this.loading,
    required this.error,
    required this.onClose,
    required this.onReview,
    required this.onGoAnyway,
  });

  @override
  Widget build(BuildContext context) {
    return Positioned.fill(
      child: Stack(children: [
        GestureDetector(
          onTap: onClose,
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 2, sigmaY: 2),
            child: Container(color: const Color(0x99404950)),
          ),
        ),
        Align(
          alignment: Alignment.bottomCenter,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 320),
            curve: Curves.easeOut,
            constraints: BoxConstraints(
                maxHeight: MediaQuery.of(context).size.height * 0.92),
            padding: const EdgeInsets.fromLTRB(26, 14, 26, 34),
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(
                  top: Radius.circular(SentriRadii.sheet)),
              boxShadow: [
                BoxShadow(
                    color: Color(0x40000000),
                    offset: Offset(0, -20),
                    blurRadius: 50)
              ],
            ),
            child: SingleChildScrollView(
              child: Column(children: [
                Container(
                    width: 36,
                    height: 4,
                    decoration: BoxDecoration(
                        color: const Color(0xFFD8D8DC),
                        borderRadius: BorderRadius.circular(999))),
                const SizedBox(height: 18),
                Text('SENTRI CHECK',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: SentriColors.brand,
                        fontSize: 11.5,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 1.4)),
                const SizedBox(height: 14),
                const SizedBox(
                    width: 260,
                    height: 260,
                    child: SentriMascot(size: 150, rings: true)),
                Text("You've never sent to ${recipient.name} before.",
                    textAlign: TextAlign.center,
                    style: Theme.of(context)
                        .textTheme
                        .headlineMedium
                        ?.copyWith(fontSize: 21, height: 1.35)),
                const SizedBox(height: 18),
                FactRow(explanation?.isNotEmpty == true
                    ? explanation!
                    : 'This transfer is different from your usual pattern.'),
                const SizedBox(height: 10),
                const FactRow(
                    'Sentri never blocks a transfer. You can review it or go on anyway.'),
                if (error != null) ...[
                  const SizedBox(height: 10),
                  _ErrorBox(error!),
                ],
                const SizedBox(height: 18),
                ElevatedButton(
                    onPressed: loading ? null : onReview,
                    child: const Text('I want to review')),
                const SizedBox(height: 10),
                OutlinedButton(
                    onPressed: loading ? null : onGoAnyway,
                    child: Text(loading ? 'Sending...' : 'Go on anyway')),
                const SizedBox(height: 14),
                Text(
                    'Sentri never blocks a transfer — this is just information.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context)
                        .textTheme
                        .bodyMedium
                        ?.copyWith(fontSize: 12)),
              ]),
            ),
          ),
        ),
      ]),
    );
  }
}

class _ReviewDetailStep extends StatelessWidget {
  final Recipient recipient;
  final int amount;
  final bool loading;
  final String? error;
  final VoidCallback onBack;
  final VoidCallback onCancel;
  final VoidCallback onSendAnyway;

  const _ReviewDetailStep({
    required this.recipient,
    required this.amount,
    required this.loading,
    required this.error,
    required this.onBack,
    required this.onCancel,
    required this.onSendAnyway,
  });

  @override
  Widget build(BuildContext context) {
    return PrimaryScaffoldPadding(
      padding: const EdgeInsets.fromLTRB(20, 58, 20, 34),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        _Header(title: 'Review details', onBack: onBack),
        const SizedBox(height: 22),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: softShadow),
          child: Row(children: [
            RecipientAvatar(initials: recipient.initials, size: 52),
            const SizedBox(width: 13),
            Expanded(
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                  Row(children: [
                    Text(recipient.name,
                        style: Theme.of(context).textTheme.titleMedium),
                    if (recipient.isNew) ...[
                      const SizedBox(width: 7),
                      const _NewPill()
                    ],
                  ]),
                  Text('•••• 8823 · Added today',
                      style: monoStyle(
                          size: 12.5,
                          color: SentriColors.muted2,
                          weight: FontWeight.w500)),
                ])),
          ]),
        ),
        const SizedBox(height: 18),
        Text('How this compares',
            style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 10),
        _DetailCard(rows: [
          const ('Typical new-recipient amount', '₦50–₦100'),
          ('This transfer', '₦$amount.00'),
          const ('Typical device', 'This iPhone'),
          const ('Recipient location', 'Out of state'),
          const ('Account age', 'Opened 6 days ago'),
        ]),
        if (error != null) ...[
          const SizedBox(height: 14),
          _ErrorBox(error!),
        ],
        const Spacer(),
        ElevatedButton(
            onPressed: loading ? null : onCancel,
            child: const Text('Cancel transfer')),
        const SizedBox(height: 10),
        OutlinedButton(
            onPressed: loading ? null : onSendAnyway,
            child: Text(loading ? 'Sending...' : 'Send anyway')),
      ]),
    );
  }
}

class _SuccessStep extends StatelessWidget {
  final Recipient recipient;
  final int amount;
  final VoidCallback onDone;

  const _SuccessStep(
      {required this.recipient, required this.amount, required this.onDone});

  @override
  Widget build(BuildContext context) {
    return PrimaryScaffoldPadding(
      child: Column(children: [
        const Spacer(),
        Container(
            width: 76,
            height: 76,
            decoration: const BoxDecoration(
                shape: BoxShape.circle, color: SentriColors.brand),
            child:
                const Icon(Icons.check_rounded, color: Colors.white, size: 40)),
        const SizedBox(height: 22),
        Text('Transfer sent',
            style: Theme.of(context).textTheme.headlineMedium),
        const SizedBox(height: 8),
        Text('You sent ₦$amount.00 to ${recipient.name}',
            style: Theme.of(context)
                .textTheme
                .bodyLarge
                ?.copyWith(color: SentriColors.muted1, fontSize: 14.5)),
        const SizedBox(height: 26),
        _DetailCard(rows: [
          ('Recipient', recipient.name),
          ('Amount', '₦$amount.00'),
          ('Date', '30/07/2026'),
        ]),
        const Spacer(),
        ElevatedButton(onPressed: onDone, child: const Text('Done')),
      ]),
    );
  }
}

class _Header extends StatelessWidget {
  final String title;
  final VoidCallback onBack;

  const _Header({required this.title, required this.onBack});

  @override
  Widget build(BuildContext context) {
    return Row(children: [
      CircleIconButton(icon: Icons.chevron_left_rounded, onTap: onBack),
      const SizedBox(width: 14),
      Text(title, style: Theme.of(context).textTheme.titleLarge),
    ]);
  }
}

class _RecipientRow extends StatelessWidget {
  final Recipient recipient;
  final VoidCallback onTap;

  const _RecipientRow({required this.recipient, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return PressableScale(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 11),
        decoration: BoxDecoration(borderRadius: BorderRadius.circular(16)),
        child: Row(children: [
          RecipientAvatar(initials: recipient.initials),
          const SizedBox(width: 13),
          Expanded(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                Row(children: [
                  Text(recipient.name,
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: SentriColors.ink,
                          fontSize: 15.5,
                          fontWeight: FontWeight.w500)),
                  if (recipient.isNew) ...[
                    const SizedBox(width: 7),
                    const _NewPill()
                  ],
                ]),
                Text(recipient.subtitle,
                    style: Theme.of(context).textTheme.bodyMedium),
              ])),
        ]),
      ),
    );
  }
}

class _AmountChip extends StatelessWidget {
  final int value;
  final bool selected;
  final VoidCallback onTap;

  const _AmountChip(
      {required this.value, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return PressableScale(
      onTap: onTap,
      child: Container(
        width: 72,
        padding: const EdgeInsets.symmetric(vertical: 13),
        decoration: BoxDecoration(
          color: selected ? SentriColors.brand : Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
              color: selected ? SentriColors.brand : SentriColors.brandTint3,
              width: 1.5),
        ),
        child: Text(
          '₦$value',
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: selected ? Colors.white : SentriColors.brand,
              fontWeight: FontWeight.w600,
              fontSize: 15),
        ),
      ),
    );
  }
}

class _SummaryTile extends StatelessWidget {
  final Recipient recipient;
  final int amount;

  const _SummaryTile({required this.recipient, required this.amount});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
          color: SentriColors.surface2,
          borderRadius: BorderRadius.circular(20)),
      child: Column(children: [
        RecipientAvatar(initials: recipient.initials, size: 56),
        const SizedBox(height: 10),
        Text(recipient.name,
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(fontSize: 17)),
        const SizedBox(height: 8),
        Text('₦$amount.00',
            style: monoStyle(size: 30, weight: FontWeight.w500)),
      ]),
    );
  }
}

class _DetailCard extends StatelessWidget {
  final List<(String, String)> rows;

  const _DetailCard({required this.rows});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: softShadow),
      child: Column(
        children: [
          for (int i = 0; i < rows.length; i++) ...[
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 13),
              child: Row(children: [
                Expanded(
                    child: Text(rows[i].$1,
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: i == rows.length - 1
                                ? SentriColors.ink
                                : SentriColors.muted1,
                            fontWeight: i == rows.length - 1
                                ? FontWeight.w600
                                : FontWeight.w400))),
                Text(rows[i].$2,
                    style: monoStyle(
                        size: 14,
                        weight: i == rows.length - 1
                            ? FontWeight.w700
                            : FontWeight.w500)),
              ]),
            ),
            if (i != rows.length - 1) const Divider(height: 1),
          ],
        ],
      ),
    );
  }
}

class _ErrorBox extends StatelessWidget {
  final String message;

  const _ErrorBox(this.message);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
          color: SentriColors.amberTint,
          borderRadius: BorderRadius.circular(14)),
      child: Text(message,
          style: Theme.of(context)
              .textTheme
              .bodyMedium
              ?.copyWith(color: SentriColors.inkSecondary)),
    );
  }
}

class _NewPill extends StatelessWidget {
  const _NewPill();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
          color: SentriColors.brandTint2,
          borderRadius: BorderRadius.circular(999)),
      child: Text('New',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: SentriColors.brand,
              fontSize: 10,
              fontWeight: FontWeight.w600)),
    );
  }
}
