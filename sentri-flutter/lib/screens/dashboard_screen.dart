import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:shimmer/shimmer.dart';
import '../api_client.dart';
import '../config.dart';
import '../models.dart';
import 'evaluate_screen.dart';

class DashboardScreen extends StatefulWidget {
  final String userId;
  const DashboardScreen({super.key, required this.userId});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final _api = ApiClient();
  UserProfile? _profile;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final p = await _api.getProfile(widget.userId);
      setState(() { _profile = p; _loading = false; });
    } catch (e) {
      setState(() { _error = e.toString(); _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    final meta = Config.userMeta[widget.userId]!;
    return Scaffold(
      appBar: AppBar(
        title: Text(meta.name),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: _loading
          ? _shimmer()
          : _error != null
              ? _errorView()
              : _body(meta),
      floatingActionButton: _profile == null
          ? null
          : FloatingActionButton.extended(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => EvaluateScreen(userId: widget.userId, profile: _profile!),
                ),
              ),
              backgroundColor: const Color(0xFF00D4AA),
              foregroundColor: const Color(0xFF0A0E1A),
              icon: const Icon(Icons.play_circle_outline_rounded),
              label: const Text('Evaluate Transaction'),
            ),
    );
  }

  Widget _body(UserMeta meta) {
    final p = _profile!;
    final fmt = NumberFormat('#,###');
    final meanNaira = (p.globalMeanKobo / 100).round();
    final stdNaira = (p.globalStdKobo / 100).round();
    final txList = p.allTransactions;

    return RefreshIndicator(
      onRefresh: _load,
      color: const Color(0xFF00D4AA),
      child: ListView(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 120),
        children: [
          // Cohort badge
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: meta.color.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(meta.icon, color: meta.color, size: 14),
                    const SizedBox(width: 6),
                    Text(meta.cohortLabel,
                        style: TextStyle(color: meta.color, fontSize: 12, fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Stats row
          Row(children: [
            _StatTile('Avg transfer', '₦${fmt.format(meanNaira)}', Icons.attach_money_rounded, const Color(0xFF00D4AA)),
            const SizedBox(width: 10),
            _StatTile('Std dev', '₦${fmt.format(stdNaira)}', Icons.show_chart_rounded, const Color(0xFF7C83FD)),
            const SizedBox(width: 10),
            _StatTile('Recipients', '${p.recipients.length}', Icons.people_outline_rounded, const Color(0xFFFFC107)),
          ]),
          const SizedBox(height: 10),
          Row(children: [
            _StatTile('Currencies', p.currenciesSeen.join(', '), Icons.currency_exchange_rounded, const Color(0xFFFF6B35)),
            const SizedBox(width: 10),
            _StatTile('Transactions', '${txList.length}', Icons.receipt_long_rounded, const Color(0xFF00D4AA)),
            const SizedBox(width: 10),
            _StatTile('Typical hour', _typicalHour(p.hourHistogram), Icons.access_time_rounded, const Color(0xFF7C83FD)),
          ]),
          const SizedBox(height: 20),

          // Hour histogram
          Text('Activity by hour (WAT)', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 10),
          _HourBar(histogram: p.hourHistogram),
          const SizedBox(height: 20),

          // Transaction history
          Text('Transaction history', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 10),
          ...txList.take(30).map((tx) => _TxRow(tx: tx)),
          if (txList.length > 30)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text('+ ${txList.length - 30} more',
                  style: Theme.of(context).textTheme.bodyMedium, textAlign: TextAlign.center),
            ),
        ],
      ),
    );
  }

  String _typicalHour(List<int> hist) {
    if (hist.every((h) => h == 0)) return '—';
    int peak = 0;
    for (int i = 0; i < hist.length; i++) {
      if (hist[i] > hist[peak]) peak = i;
    }
    final period = peak < 12 ? 'am' : 'pm';
    final h = peak % 12 == 0 ? 12 : peak % 12;
    return '$h$period';
  }

  Widget _shimmer() {
    return Shimmer.fromColors(
      baseColor: const Color(0xFF1A2235),
      highlightColor: const Color(0xFF253048),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: 6,
        itemBuilder: (_, __) => Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Container(height: 60, decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12))),
        ),
      ),
    );
  }

  Widget _errorView() {
    return Center(
      child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
        const Icon(Icons.wifi_off_rounded, size: 40, color: Color(0xFF8A9BB5)),
        const SizedBox(height: 12),
        Text('Could not reach backend', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 20),
        ElevatedButton(onPressed: _load, child: const Text('Retry')),
      ]),
    );
  }
}

class _StatTile extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const _StatTile(this.label, this.value, this.icon, this.color);

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Icon(icon, color: color, size: 16),
            const SizedBox(height: 6),
            Text(value,
                style: Theme.of(context).textTheme.titleMedium!.copyWith(color: color, fontSize: 13),
                maxLines: 1,
                overflow: TextOverflow.ellipsis),
            const SizedBox(height: 2),
            Text(label, style: Theme.of(context).textTheme.bodyMedium!.copyWith(fontSize: 10)),
          ]),
        ),
      ),
    );
  }
}

class _HourBar extends StatelessWidget {
  final List<int> histogram;
  const _HourBar({required this.histogram});

  @override
  Widget build(BuildContext context) {
    if (histogram.isEmpty) return const SizedBox();
    final max = histogram.reduce((a, b) => a > b ? a : b);
    if (max == 0) return const SizedBox();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          SizedBox(
            height: 60,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: List.generate(24, (i) {
                final ratio = histogram[i] / max;
                final isActive = ratio > 0.5;
                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 1),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Flexible(
                          child: FractionallySizedBox(
                            heightFactor: ratio.clamp(0.05, 1.0),
                            child: Container(
                              decoration: BoxDecoration(
                                color: isActive ? const Color(0xFF00D4AA) : const Color(0xFF253048),
                                borderRadius: const BorderRadius.vertical(top: Radius.circular(2)),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }),
            ),
          ),
          const SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: ['0h', '6h', '12h', '18h', '23h']
                .map((l) => Text(l, style: const TextStyle(color: Color(0xFF8A9BB5), fontSize: 10)))
                .toList(),
          ),
        ]),
      ),
    );
  }
}

class _TxRow extends StatelessWidget {
  final Transaction tx;
  const _TxRow({required this.tx});

  @override
  Widget build(BuildContext context) {
    final label = tx.recipientId.split('_').skip(2).join(' ').trim();
    final date = DateFormat('MMM d · HH:mm').format(tx.timestamp.toLocal());
    return Card(
      margin: const EdgeInsets.only(bottom: 6),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Row(children: [
          Expanded(child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label.isEmpty ? tx.recipientId : label,
                  style: Theme.of(context).textTheme.bodyLarge!.copyWith(fontSize: 13),
                  maxLines: 1, overflow: TextOverflow.ellipsis),
              const SizedBox(height: 2),
              Text(date, style: Theme.of(context).textTheme.bodyMedium!.copyWith(fontSize: 11)),
            ],
          )),
          Text(tx.displayAmount,
              style: Theme.of(context).textTheme.bodyLarge!.copyWith(fontWeight: FontWeight.w700)),
          const SizedBox(width: 6),
          Text(tx.currency,
              style: Theme.of(context).textTheme.bodyMedium!.copyWith(fontSize: 10)),
        ]),
      ),
    );
  }
}
