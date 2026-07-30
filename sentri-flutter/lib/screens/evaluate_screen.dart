import 'package:flutter/material.dart';
import '../api_client.dart';
import '../models.dart';

/// POST /evaluate — the core Sentri scoring screen.
/// Lets you fill in a transaction event and see the full verdict.
class EvaluateScreen extends StatefulWidget {
  final String userId;
  final UserProfile profile;

  const EvaluateScreen({super.key, required this.userId, required this.profile});

  @override
  State<EvaluateScreen> createState() => _EvaluateScreenState();
}

class _EvaluateScreenState extends State<EvaluateScreen> {
  final _formKey = GlobalKey<FormState>();
  final _recipientCtrl = TextEditingController();
  final _amountCtrl = TextEditingController();
  final _memoCtrl = TextEditingController();
  final _api = ApiClient();

  String _currency = 'NGN';
  bool _crossBorder = false;
  bool _loading = false;
  List<String> _recipientSuggestions = [];

  EvaluateResult? _result;

  @override
  void dispose() {
    _recipientCtrl.dispose();
    _amountCtrl.dispose();
    _memoCtrl.dispose();
    super.dispose();
  }

  void _onRecipientChanged(String v) {
    if (v.isEmpty) { setState(() => _recipientSuggestions = []); return; }
    final matches = widget.profile.recipients.keys
        .where((k) => k.toLowerCase().contains(v.toLowerCase()))
        .take(6)
        .toList();
    setState(() => _recipientSuggestions = matches);
  }

  Future<void> _evaluate() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _loading = true; _result = null; _recipientSuggestions = []; });

    try {
      final amountKobo = (double.parse(_amountCtrl.text) * 100).round();
      final result = await _api.evaluate(
        userId: widget.userId,
        amountKobo: amountKobo,
        recipientId: _recipientCtrl.text.trim(),
        timestamp: DateTime.now().toUtc().toIso8601String(),
        currency: _currency,
        crossBorder: _crossBorder,
        memo: _memoCtrl.text.trim().isEmpty ? null : _memoCtrl.text.trim(),
      );
      setState(() { _result = result; _loading = false; });
    } catch (e) {
      setState(() => _loading = false);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$e'), backgroundColor: const Color(0xFFFF6B35)),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Evaluate Transaction'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          if (_result != null)
            TextButton(
              onPressed: () => setState(() => _result = null),
              child: const Text('Reset', style: TextStyle(color: Color(0xFF8A9BB5))),
            ),
        ],
      ),
      body: _result != null ? _verdictView() : _formView(),
    );
  }

  // ── Form ──────────────────────────────────────────────────────────────────

  Widget _formView() {
    return GestureDetector(
      onTap: () => setState(() => _recipientSuggestions = []),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            // Endpoint label
            _EndpointBadge('POST /evaluate · ${widget.userId}'),
            const SizedBox(height: 20),

            // Amount
            _FieldLabel('amount_kobo'),
            const SizedBox(height: 6),
            Row(children: [
              Expanded(
                child: TextFormField(
                  controller: _amountCtrl,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(
                    hintText: 'Amount in Naira',
                    prefixText: '₦  ',
                  ),
                  validator: (v) {
                    if (v == null || v.isEmpty) return 'Required';
                    if (double.tryParse(v) == null || double.parse(v) <= 0) return 'Invalid amount';
                    return null;
                  },
                ),
              ),
              const SizedBox(width: 10),
              _CurrencyPicker(
                value: _currency,
                onChanged: (c) => setState(() {
                  _currency = c;
                  if (c != 'NGN') _crossBorder = true;
                }),
              ),
            ]),
            const SizedBox(height: 16),

            // Recipient with autocomplete
            _FieldLabel('recipient_id'),
            const SizedBox(height: 6),
            TextFormField(
              controller: _recipientCtrl,
              onChanged: _onRecipientChanged,
              decoration: const InputDecoration(hintText: 'e.g. user_001_landlord'),
              validator: (v) => (v == null || v.trim().isEmpty) ? 'Required' : null,
            ),
            if (_recipientSuggestions.isNotEmpty)
              _Autocomplete(
                suggestions: _recipientSuggestions,
                profile: widget.profile,
                onSelect: (id) {
                  _recipientCtrl.text = id;
                  setState(() => _recipientSuggestions = []);
                },
              ),
            const SizedBox(height: 16),

            // Memo
            _FieldLabel('memo  (optional)'),
            const SizedBox(height: 6),
            TextFormField(
              controller: _memoCtrl,
              maxLength: 200,
              decoration: const InputDecoration(hintText: 'What\'s this for?', counterText: ''),
            ),
            const SizedBox(height: 16),

            // Flags row
            _FieldLabel('flags'),
            const SizedBox(height: 6),
            Card(
              child: SwitchListTile(
                dense: true,
                value: _crossBorder,
                onChanged: (v) => setState(() => _crossBorder = v),
                title: Text('cross_border', style: Theme.of(context).textTheme.bodyLarge!.copyWith(fontSize: 13)),
                subtitle: Text('Activates cross-border signal',
                    style: Theme.of(context).textTheme.bodyMedium!.copyWith(fontSize: 11)),
                activeColor: const Color(0xFF00D4AA),
                secondary: Icon(
                  Icons.public_rounded,
                  color: _crossBorder ? const Color(0xFFFF6B35) : const Color(0xFF8A9BB5),
                  size: 20,
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Quick-fill presets
            Text('Quick presets', style: Theme.of(context).textTheme.bodyMedium),
            const SizedBox(height: 8),
            _Presets(
              userId: widget.userId,
              profile: widget.profile,
              onSelect: (recipient, amount, currency, crossBorder) {
                _recipientCtrl.text = recipient;
                _amountCtrl.text = amount;
                setState(() {
                  _currency = currency;
                  _crossBorder = crossBorder;
                  _recipientSuggestions = [];
                });
              },
            ),
            const SizedBox(height: 28),

            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _loading ? null : _evaluate,
                icon: _loading
                    ? const SizedBox(width: 18, height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF0A0E1A)))
                    : const Icon(Icons.send_rounded, size: 18),
                label: Text(_loading ? 'Evaluating...' : 'Run Sentri Evaluation'),
              ),
            ),
          ]),
        ),
      ),
    );
  }

  // ── Verdict ───────────────────────────────────────────────────────────────

  Widget _verdictView() {
    final r = _result!;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        // Verdict banner
        _VerdictBanner(result: r),
        const SizedBox(height: 20),

        // Triggered reasons
        if (r.triggeredReasons.isNotEmpty) ...[
          _SectionLabel('triggered_reasons'),
          const SizedBox(height: 10),
          ...r.nonStructuralReasons.map((reason) => _ReasonRow(
                reason: reason,
                isStructural: false,
              )),
          ...r.structuralReasons.map((reason) => _ReasonRow(
                reason: reason,
                isStructural: true,
              )),
          const SizedBox(height: 20),
        ],

        // Explanation
        if (r.explanation != null) ...[
          Row(children: [
            _SectionLabel('explanation'),
            const SizedBox(width: 8),
            _SynthesizerBadge(r.synthesizerUsed),
          ]),
          const SizedBox(height: 10),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF1A2235),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFF253048)),
            ),
            child: Text(r.explanation!,
                style: Theme.of(context).textTheme.bodyLarge!.copyWith(height: 1.7)),
          ),
          const SizedBox(height: 20),
        ],

        // Structural signal note
        if (r.structuralReasons.isNotEmpty && r.isSilentPass) ...[
          _InfoNote(
            'Structural signals fired (${r.structuralReasons.join(', ')}) but cannot trigger INTERVENE alone. At least one non-structural signal (amount, time, or categorical) must also fire.',
          ),
          const SizedBox(height: 20),
        ],

        // Request echo
        _SectionLabel('request sent'),
        const SizedBox(height: 10),
        _RequestEcho(
          userId: widget.userId,
          recipientId: _recipientCtrl.text,
          amount: _amountCtrl.text,
          currency: _currency,
          crossBorder: _crossBorder,
          memo: _memoCtrl.text.trim().isEmpty ? null : _memoCtrl.text.trim(),
        ),
        const SizedBox(height: 28),

        SizedBox(
          width: double.infinity,
          child: OutlinedButton(
            onPressed: () => setState(() => _result = null),
            child: const Text('Evaluate another'),
          ),
        ),
      ]),
    );
  }
}

// ── Sub-widgets ──────────────────────────────────────────────────────────────

class _EndpointBadge extends StatelessWidget {
  final String label;
  const _EndpointBadge(this.label);
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: const Color(0xFF00D4AA).withOpacity(0.08),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFF00D4AA).withOpacity(0.25)),
      ),
      child: Text(label,
          style: const TextStyle(color: Color(0xFF00D4AA), fontSize: 11, fontFamily: 'monospace')),
    );
  }
}

class _FieldLabel extends StatelessWidget {
  final String label;
  const _FieldLabel(this.label);
  @override
  Widget build(BuildContext context) {
    return Text(label,
        style: const TextStyle(
            color: Color(0xFF8A9BB5), fontSize: 11, fontWeight: FontWeight.w500));
  }
}

class _SectionLabel extends StatelessWidget {
  final String label;
  const _SectionLabel(this.label);
  @override
  Widget build(BuildContext context) {
    return Text(label,
        style: const TextStyle(
            color: Color(0xFF8A9BB5), fontSize: 11, fontWeight: FontWeight.w600,
            letterSpacing: 0.5));
  }
}

class _CurrencyPicker extends StatelessWidget {
  final String value;
  final ValueChanged<String> onChanged;
  const _CurrencyPicker({required this.value, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () async {
        final picked = await showModalBottomSheet<String>(
          context: context,
          backgroundColor: const Color(0xFF111827),
          shape: const RoundedRectangleBorder(
              borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
          builder: (_) => Padding(
            padding: const EdgeInsets.all(20),
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              Text('currency', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 12),
              ...['NGN', 'USD', 'GBP', 'EUR'].map((c) => ListTile(
                    title: Text(c),
                    trailing: value == c
                        ? const Icon(Icons.check, color: Color(0xFF00D4AA))
                        : null,
                    onTap: () => Navigator.pop(context, c),
                  )),
            ]),
          ),
        );
        if (picked != null) onChanged(picked);
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 16),
        decoration: BoxDecoration(
          color: const Color(0xFF1A2235),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFF253048)),
        ),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          Text(value,
              style: const TextStyle(
                  color: Color(0xFFE8EDF5), fontWeight: FontWeight.w600, fontSize: 14)),
          const SizedBox(width: 4),
          const Icon(Icons.expand_more, size: 16, color: Color(0xFF8A9BB5)),
        ]),
      ),
    );
  }
}

class _Autocomplete extends StatelessWidget {
  final List<String> suggestions;
  final UserProfile profile;
  final ValueChanged<String> onSelect;

  const _Autocomplete({required this.suggestions, required this.profile, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF1A2235),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF253048)),
      ),
      child: Column(
        children: suggestions.map((id) {
          final rollup = profile.recipients[id];
          return InkWell(
            onTap: () => onSelect(id),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              child: Row(children: [
                const Icon(Icons.history_rounded, size: 14, color: Color(0xFF8A9BB5)),
                const SizedBox(width: 10),
                Expanded(
                    child: Text(id,
                        style: Theme.of(context).textTheme.bodyLarge!.copyWith(fontSize: 13))),
                if (rollup != null)
                  Text('${rollup.count}x',
                      style: const TextStyle(color: Color(0xFF00D4AA), fontSize: 11)),
              ]),
            ),
          );
        }).toList(),
      ),
    );
  }
}

class _Presets extends StatelessWidget {
  final String userId;
  final UserProfile profile;
  final void Function(String recipient, String amount, String currency, bool crossBorder) onSelect;

  const _Presets({required this.userId, required this.profile, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    // Pick a known recipient (highest count = most familiar)
    final sorted = profile.recipients.entries.toList()
      ..sort((a, b) => b.value.count.compareTo(a.value.count));
    final familiar = sorted.isNotEmpty ? sorted.first.key : '${userId}_landlord';
    final unfamiliar = '${userId}_advance_refund_agent';
    final meanNaira = (profile.globalMeanKobo / 100).round();
    final highAmount = (meanNaira * 10).toString();
    final normalAmount = meanNaira.toString();

    final presets = [
      _Preset(
        label: 'Normal',
        description: 'Familiar recipient, avg amount',
        recipient: familiar,
        amount: normalAmount,
        currency: 'NGN',
        crossBorder: false,
        color: const Color(0xFF00D4AA),
        icon: Icons.check_circle_outline_rounded,
      ),
      _Preset(
        label: 'Anomalous',
        description: 'Unknown recipient, 10× amount, 3am',
        recipient: unfamiliar,
        amount: highAmount,
        currency: 'USD',
        crossBorder: true,
        color: const Color(0xFFFF6B35),
        icon: Icons.warning_amber_rounded,
      ),
      _Preset(
        label: 'High amount',
        description: 'Same recipient, 10× amount',
        recipient: familiar,
        amount: highAmount,
        currency: 'NGN',
        crossBorder: false,
        color: const Color(0xFFFFC107),
        icon: Icons.trending_up_rounded,
      ),
      _Preset(
        label: 'New currency',
        description: 'Familiar recipient, foreign currency',
        recipient: familiar,
        amount: normalAmount,
        currency: 'USD',
        crossBorder: true,
        color: const Color(0xFF7C83FD),
        icon: Icons.currency_exchange_rounded,
      ),
    ];

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: presets
          .map((p) => GestureDetector(
                onTap: () => onSelect(p.recipient, p.amount, p.currency, p.crossBorder),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: p.color.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: p.color.withOpacity(0.25)),
                  ),
                  child: Row(mainAxisSize: MainAxisSize.min, children: [
                    Icon(p.icon, color: p.color, size: 14),
                    const SizedBox(width: 6),
                    Text(p.label,
                        style: TextStyle(
                            color: p.color, fontSize: 12, fontWeight: FontWeight.w600)),
                  ]),
                ),
              ))
          .toList(),
    );
  }
}

class _Preset {
  final String label, description, recipient, amount, currency;
  final bool crossBorder;
  final Color color;
  final IconData icon;
  const _Preset({
    required this.label,
    required this.description,
    required this.recipient,
    required this.amount,
    required this.currency,
    required this.crossBorder,
    required this.color,
    required this.icon,
  });
}

class _VerdictBanner extends StatelessWidget {
  final EvaluateResult result;
  const _VerdictBanner({required this.result});

  @override
  Widget build(BuildContext context) {
    final isPass = result.isSilentPass;
    final color = isPass ? const Color(0xFF00D4AA) : const Color(0xFFFF6B35);
    final label = isPass ? 'SILENT_PASS' : 'INTERVENE';
    final icon = isPass ? Icons.verified_rounded : Icons.warning_amber_rounded;
    final desc = isPass
        ? 'No non-structural signals fired. Transfer would proceed immediately.'
        : 'At least one non-structural signal fired. User would see this explanation before confirming.';

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: color.withOpacity(0.08),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: color.withOpacity(0.35)),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(width: 10),
          Text('verdict',
              style: const TextStyle(color: Color(0xFF8A9BB5), fontSize: 11, fontWeight: FontWeight.w500)),
        ]),
        const SizedBox(height: 8),
        Text(label,
            style: TextStyle(color: color, fontSize: 26, fontWeight: FontWeight.w700,
                letterSpacing: 1)),
        const SizedBox(height: 8),
        Text(desc, style: Theme.of(context).textTheme.bodyMedium!.copyWith(height: 1.5)),
      ]),
    );
  }
}

class _ReasonRow extends StatelessWidget {
  final String reason;
  final bool isStructural;
  const _ReasonRow({required this.reason, required this.isStructural});

  static const _descriptions = {
    'recipient_familiarity': 'Familiarity score below threshold — new or rarely used recipient',
    'graph_proximity': 'Recipient not in social graph (direct or FOF)',
    'amount_z_recipient': '|z-score| vs this recipient\'s history exceeds threshold',
    'amount_z_global': '|z-score| vs all history exceeds threshold (global fallback)',
    'amount_drift': 'Recent 30-day volatility > 2× prior 31–90-day volatility',
    'hour_deviation': 'Circular hour deviation from historical pattern exceeds threshold',
    'currency_novelty': 'Currency never seen in user\'s transaction history',
    'cross_border': 'cross_border flag was set to true on the request',
  };

  @override
  Widget build(BuildContext context) {
    final color = isStructural ? const Color(0xFFFFC107) : const Color(0xFFFF6B35);
    final desc = _descriptions[reason] ?? reason;
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.07),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withOpacity(0.25)),
      ),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Icon(Icons.flag_rounded, color: color, size: 15),
        const SizedBox(width: 10),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Text(reason,
                style: TextStyle(
                    color: color, fontSize: 12, fontWeight: FontWeight.w700,
                    fontFamily: 'monospace')),
            if (isStructural) ...[
              const SizedBox(width: 8),
              Text('structural',
                  style: TextStyle(
                      color: color.withOpacity(0.6), fontSize: 10)),
            ],
          ]),
          const SizedBox(height: 3),
          Text(desc, style: Theme.of(context).textTheme.bodyMedium!.copyWith(fontSize: 12, height: 1.5)),
        ])),
      ]),
    );
  }
}

class _SynthesizerBadge extends StatelessWidget {
  final String synthesizer;
  const _SynthesizerBadge(this.synthesizer);
  @override
  Widget build(BuildContext context) {
    final isLLM = synthesizer == 'claude';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
      decoration: BoxDecoration(
        color: isLLM ? const Color(0xFF7C83FD).withOpacity(0.12) : const Color(0xFF253048),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        isLLM ? '✦ claude' : synthesizer,
        style: TextStyle(
            color: isLLM ? const Color(0xFF7C83FD) : const Color(0xFF8A9BB5),
            fontSize: 10,
            fontWeight: FontWeight.w600),
      ),
    );
  }
}

class _InfoNote extends StatelessWidget {
  final String text;
  const _InfoNote(this.text);
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF1A2235),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF253048)),
      ),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Icon(Icons.info_outline_rounded, size: 15, color: Color(0xFF8A9BB5)),
        const SizedBox(width: 8),
        Expanded(
            child: Text(text,
                style: Theme.of(context).textTheme.bodyMedium!.copyWith(fontSize: 12, height: 1.5))),
      ]),
    );
  }
}

class _RequestEcho extends StatelessWidget {
  final String userId, recipientId, amount, currency;
  final bool crossBorder;
  final String? memo;

  const _RequestEcho({
    required this.userId,
    required this.recipientId,
    required this.amount,
    required this.currency,
    required this.crossBorder,
    this.memo,
  });

  @override
  Widget build(BuildContext context) {
    final kobo = (double.tryParse(amount) ?? 0) * 100;
    final lines = [
      '  "user_id": "$userId"',
      '  "recipient_id": "$recipientId"',
      '  "amount_kobo": ${kobo.round()}',
      '  "currency": "$currency"',
      '  "cross_border": $crossBorder',
      if (memo != null) '  "memo": "$memo"',
    ];
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0E1A),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF1E2D45)),
      ),
      child: Text(
        '{\n${lines.join(',\n')}\n}',
        style: const TextStyle(fontFamily: 'monospace', fontSize: 11,
            color: Color(0xFF8A9BB5), height: 1.7),
      ),
    );
  }
}
