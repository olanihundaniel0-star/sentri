import 'package:flutter/material.dart';

import '../app_data.dart';
import '../design_system.dart';
import '../widgets/ui_components.dart';
import 'send_flow_screen.dart';

class DashboardScreen extends StatefulWidget {
  final DemoUser user;

  const DashboardScreen({super.key, required this.user});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  RootTab _tab = RootTab.home;
  bool _balanceHidden = false;
  bool _unread = true;
  bool _cardFrozen = false;
  bool _contactless = true;
  bool _onlinePay = true;
  bool _cvvShown = false;
  bool _sentriOn = true;
  bool _july = true;
  String? _toast;

  void _showToast(String message) {
    setState(() => _toast = message);
    Future<void>.delayed(const Duration(milliseconds: 2200), () {
      if (mounted && _toast == message) setState(() => _toast = null);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 220),
            child: _currentScreen(),
          ),
          Align(
            alignment: Alignment.bottomCenter,
            child: _BottomNav(
                tab: _tab, onChanged: (tab) => setState(() => _tab = tab)),
          ),
          if (_toast != null)
            Positioned(
              left: 24,
              right: 24,
              bottom: 98,
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 13),
                decoration: BoxDecoration(
                    color: SentriColors.ink,
                    borderRadius: BorderRadius.circular(14)),
                child: Text(_toast!,
                    textAlign: TextAlign.center,
                    style: Theme.of(context)
                        .textTheme
                        .bodyLarge
                        ?.copyWith(color: Colors.white, fontSize: 13.5)),
              ),
            ),
        ],
      ),
    );
  }

  Widget _currentScreen() {
    switch (_tab) {
      case RootTab.home:
        return _HomeTab(
          user: widget.user,
          unread: _unread,
          balanceHidden: _balanceHidden,
          onToggleBalance: () =>
              setState(() => _balanceHidden = !_balanceHidden),
          onOpenNotifications: () {
            setState(() => _unread = false);
            Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (_) => const _NotificationsScreen()));
          },
          onOpenTransactions: () => Navigator.push(context,
              MaterialPageRoute(builder: (_) => const _TransactionsScreen())),
          onSend: () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => SendFlowScreen(
                user: widget.user,
                sentriOn: _sentriOn,
                onCancelled: () => _showToast('Transfer cancelled'),
              ),
            ),
          ),
        );
      case RootTab.card:
        return _CardTab(
          frozen: _cardFrozen,
          contactless: _contactless,
          onlinePay: _onlinePay,
          cvvShown: _cvvShown,
          onFreeze: (v) => setState(() => _cardFrozen = v),
          onContactless: (v) => setState(() => _contactless = v),
          onOnlinePay: (v) => setState(() => _onlinePay = v),
          onCvv: () => setState(() => _cvvShown = !_cvvShown),
        );
      case RootTab.insights:
        return _InsightsTab(
            july: _july, onMonth: (v) => setState(() => _july = v));
      case RootTab.profile:
        return _ProfileTab(
          user: widget.user,
          sentriOn: _sentriOn,
          onSentri: (v) => setState(() => _sentriOn = v),
          onNotifications: () {
            setState(() => _unread = false);
            Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (_) => const _NotificationsScreen()));
          },
        );
    }
  }
}

class _HomeTab extends StatelessWidget {
  final DemoUser user;
  final bool unread;
  final bool balanceHidden;
  final VoidCallback onToggleBalance;
  final VoidCallback onOpenNotifications;
  final VoidCallback onOpenTransactions;
  final VoidCallback onSend;

  const _HomeTab({
    required this.user,
    required this.unread,
    required this.balanceHidden,
    required this.onToggleBalance,
    required this.onOpenNotifications,
    required this.onOpenTransactions,
    required this.onSend,
  });

  @override
  Widget build(BuildContext context) {
    return PrimaryScaffoldPadding(
      padding: const EdgeInsets.fromLTRB(20, 56, 20, 108),
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Good Morning,',
                          style: Theme.of(context)
                              .textTheme
                              .bodyMedium
                              ?.copyWith(fontSize: 13)),
                      Text(user.firstName,
                          style: Theme.of(context)
                              .textTheme
                              .titleLarge
                              ?.copyWith(fontWeight: FontWeight.w700)),
                    ]),
              ),
              PressableScale(
                onTap: onOpenNotifications,
                pressedScale: 0.9,
                child: Stack(
                  clipBehavior: Clip.none,
                  children: [
                    const Icon(Icons.notifications_none_rounded,
                        size: 24, color: SentriColors.ink),
                    if (unread)
                      Positioned(
                        right: -7,
                        top: -8,
                        child: Container(
                          width: 18,
                          height: 18,
                          decoration: BoxDecoration(
                              color: SentriColors.brand,
                              shape: BoxShape.circle,
                              border:
                                  Border.all(color: Colors.white, width: 2)),
                          child: Center(
                              child: Text('1',
                                  style: Theme.of(context)
                                      .textTheme
                                      .bodyMedium
                                      ?.copyWith(
                                          color: Colors.white,
                                          fontSize: 9,
                                          height: 1))),
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          _BankCard(
              user: user, hidden: balanceHidden, onToggle: onToggleBalance),
          const SizedBox(height: 18),
          Row(
            children: [
              _ActionCard(
                  icon: Icons.arrow_upward_rounded,
                  label: 'Send',
                  color: SentriColors.green,
                  tint: SentriColors.greenTint,
                  onTap: onSend),
              const SizedBox(width: 12),
              _ActionCard(
                  icon: Icons.add_card_rounded,
                  label: 'Fund',
                  color: SentriColors.amber,
                  tint: SentriColors.amberTint,
                  onTap: () {}),
              const SizedBox(width: 12),
              _ActionCard(
                  icon: Icons.swap_horiz_rounded,
                  label: 'Swap',
                  color: SentriColors.green,
                  tint: SentriColors.greenTint,
                  onTap: () {}),
            ],
          ),
          const SizedBox(height: 22),
          Row(
            children: [
              Expanded(
                  child: Text('Recent Transactions',
                      style: Theme.of(context).textTheme.titleMedium)),
              TextButton(
                  onPressed: onOpenTransactions,
                  child: const Text('See all ›',
                      style: TextStyle(color: SentriColors.brand))),
            ],
          ),
          const SizedBox(height: 8),
          _TransactionCard(rows: const [
            _TxData(
                'Eliana Baron', 'Money Out', '-₦245.00', '10/06/2026 12:45'),
            _TxData(
                'Ademide Johnson', 'Money In', '+₦245.00', '09/06/2026 08:12'),
          ]),
        ],
      ),
    );
  }
}

class _BankCard extends StatelessWidget {
  final DemoUser user;
  final bool hidden;
  final VoidCallback onToggle;

  const _BankCard(
      {required this.user, required this.hidden, required this.onToggle});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(SentriRadii.bankCard),
        gradient: const LinearGradient(colors: [
          SentriColors.cardPlum1,
          SentriColors.cardPlum2,
          SentriColors.cardPlum3
        ], begin: Alignment.topLeft, end: Alignment.bottomRight),
        boxShadow: [
          BoxShadow(
              color: SentriColors.cardPlum1.withOpacity(0.26),
              offset: const Offset(0, 14),
              blurRadius: 26)
        ],
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Expanded(
              child: Text('Available balance:',
                  style: Theme.of(context)
                      .textTheme
                      .bodyMedium
                      ?.copyWith(color: Colors.white.withOpacity(0.62)))),
          CircleIconButton(
              icon: hidden
                  ? Icons.visibility_off_rounded
                  : Icons.visibility_rounded,
              onTap: onToggle,
              background: Colors.white.withOpacity(0.13),
              color: Colors.white),
        ]),
        const SizedBox(height: 8),
        Text(hidden ? '₦••••••' : '₦2,406.85',
            style: monoStyle(
                size: 30, color: Colors.white, weight: FontWeight.w600)),
        const SizedBox(height: 28),
        Text('**** **** **** 7068',
            style: monoStyle(
                size: 15,
                color: Colors.white.withOpacity(0.82),
                weight: FontWeight.w500)),
        const SizedBox(height: 18),
        Row(children: [
          Expanded(
              child: Text(user.cardName,
                  style: monoStyle(
                      size: 12.5,
                      color: Colors.white.withOpacity(0.68),
                      weight: FontWeight.w500))),
          Text('09/29',
              style: monoStyle(
                  size: 12.5,
                  color: Colors.white.withOpacity(0.68),
                  weight: FontWeight.w500)),
        ]),
      ]),
    );
  }
}

class _ActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final Color tint;
  final VoidCallback onTap;

  const _ActionCard(
      {required this.icon,
      required this.label,
      required this.color,
      required this.tint,
      required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: PressableScale(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 16),
          decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: softShadow),
          child: Column(children: [
            Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(color: tint, shape: BoxShape.circle),
                child: Icon(icon, color: color, size: 22)),
            const SizedBox(height: 9),
            Text(label,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: SentriColors.ink,
                    fontWeight: FontWeight.w500,
                    fontSize: 13)),
          ]),
        ),
      ),
    );
  }
}

class _TransactionCard extends StatelessWidget {
  final List<_TxData> rows;

  const _TransactionCard({required this.rows});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: softShadow),
      child: Column(
        children: [
          for (int i = 0; i < rows.length; i++) ...[
            _TxRow(data: rows[i]),
            if (i != rows.length - 1)
              const Divider(height: 1, indent: 16, endIndent: 16),
          ],
        ],
      ),
    );
  }
}

class _TxData {
  final String name;
  final String type;
  final String amount;
  final String timestamp;
  const _TxData(this.name, this.type, this.amount, this.timestamp);
}

class _TxRow extends StatelessWidget {
  final _TxData data;

  const _TxRow({required this.data});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(children: [
        Expanded(
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(data.name,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: SentriColors.ink,
                  fontWeight: FontWeight.w500,
                  fontSize: 15)),
          const SizedBox(height: 3),
          Text(data.type,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: SentriColors.brand,
                  fontWeight: FontWeight.w500,
                  fontSize: 11.5)),
        ])),
        Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
          Text(data.amount, style: monoStyle(size: 15)),
          const SizedBox(height: 3),
          Text(data.timestamp,
              style: Theme.of(context)
                  .textTheme
                  .bodyMedium
                  ?.copyWith(color: SentriColors.muted3, fontSize: 10.5)),
        ]),
      ]),
    );
  }
}

class _BottomNav extends StatelessWidget {
  final RootTab tab;
  final ValueChanged<RootTab> onChanged;

  const _BottomNav({required this.tab, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Container(
        margin: const EdgeInsets.fromLTRB(18, 0, 18, 26),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        decoration: BoxDecoration(
            color: SentriColors.brand,
            borderRadius: BorderRadius.circular(999),
            boxShadow: [
              BoxShadow(
                  color: SentriColors.brand.withOpacity(0.28),
                  offset: const Offset(0, 10),
                  blurRadius: 22)
            ]),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: RootTab.values.map((item) {
            final active = item == tab;
            return PressableScale(
              pressedScale: 0.9,
              onTap: () => onChanged(item),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 180),
                height: 42,
                padding: EdgeInsets.symmetric(horizontal: active ? 15 : 11),
                decoration: BoxDecoration(
                    color: active ? Colors.white : Colors.transparent,
                    borderRadius: BorderRadius.circular(999)),
                child: Row(
                  children: [
                    Icon(item.icon,
                        color: active
                            ? SentriColors.brand
                            : Colors.white.withOpacity(0.92),
                        size: 20),
                    if (active) ...[
                      const SizedBox(width: 7),
                      Text(item.label,
                          style: Theme.of(context)
                              .textTheme
                              .bodyLarge
                              ?.copyWith(
                                  color: SentriColors.brand,
                                  fontWeight: FontWeight.w600,
                                  fontSize: 13)),
                    ],
                  ],
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }
}

class _CardTab extends StatelessWidget {
  final bool frozen;
  final bool contactless;
  final bool onlinePay;
  final bool cvvShown;
  final ValueChanged<bool> onFreeze;
  final ValueChanged<bool> onContactless;
  final ValueChanged<bool> onOnlinePay;
  final VoidCallback onCvv;

  const _CardTab(
      {required this.frozen,
      required this.contactless,
      required this.onlinePay,
      required this.cvvShown,
      required this.onFreeze,
      required this.onContactless,
      required this.onOnlinePay,
      required this.onCvv});

  @override
  Widget build(BuildContext context) {
    return PrimaryScaffoldPadding(
      padding: const EdgeInsets.fromLTRB(20, 56, 20, 108),
      child: ListView(padding: EdgeInsets.zero, children: [
        Text('My Card', style: Theme.of(context).textTheme.headlineMedium),
        const SizedBox(height: 18),
        Opacity(opacity: frozen ? 0.55 : 1, child: const _LargeCard()),
        const SizedBox(height: 20),
        _SettingsCard(children: [
          _SwitchRow(
              'Freeze card', 'Blocks new payments instantly', frozen, onFreeze),
          _SwitchRow('Contactless payments', null, contactless, onContactless),
          _SwitchRow('Online payments', null, onlinePay, onOnlinePay),
        ]),
        const SizedBox(height: 18),
        _SettingsCard(children: [
          _DetailRow('Card number', '**** **** **** 7068'),
          _DetailRow('CVV', cvvShown ? '481' : '•••',
              action: cvvShown ? 'Hide' : 'Show', onAction: onCvv),
        ]),
        const SizedBox(height: 18),
        _LimitCard(),
      ]),
    );
  }
}

class _LargeCard extends StatelessWidget {
  const _LargeCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 220,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(22),
          gradient: const LinearGradient(colors: [
            SentriColors.cardPlum1,
            SentriColors.cardPlum2,
            SentriColors.cardPlum3
          ]),
          boxShadow: softShadow),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Text('Sentri',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(color: Colors.white)),
          const Spacer(),
          const Icon(Icons.contactless_rounded, color: Colors.white70),
        ]),
        const Spacer(),
        Container(
            width: 44,
            height: 32,
            decoration: BoxDecoration(
                color: const Color(0xFFD8B75F),
                borderRadius: BorderRadius.circular(7))),
        const SizedBox(height: 20),
        Text('**** **** **** 7068',
            style: monoStyle(
                size: 17, color: Colors.white, weight: FontWeight.w500)),
        const SizedBox(height: 16),
        Row(children: [
          Expanded(
              child: Text('CARD HOLDER\nJEWEL A.',
                  style: monoStyle(
                      size: 11,
                      color: Colors.white70,
                      weight: FontWeight.w500,
                      height: 1.5))),
          Text('EXPIRES\n09/29',
              style: monoStyle(
                  size: 11,
                  color: Colors.white70,
                  weight: FontWeight.w500,
                  height: 1.5)),
        ]),
      ]),
    );
  }
}

class _InsightsTab extends StatelessWidget {
  final bool july;
  final ValueChanged<bool> onMonth;

  const _InsightsTab({required this.july, required this.onMonth});

  @override
  Widget build(BuildContext context) {
    final bars =
        july ? [42, 68, 55, 88, 74, 96, 60] : [58, 44, 72, 50, 66, 38, 80];
    final cats = july
        ? ['₦920.00', '₦412.30', '₦318.00', '₦192.00']
        : ['₦760.00', '₦402.00', '₦286.00', '₦162.00'];
    return PrimaryScaffoldPadding(
      padding: const EdgeInsets.fromLTRB(20, 56, 20, 108),
      child: ListView(padding: EdgeInsets.zero, children: [
        Text('Insights', style: Theme.of(context).textTheme.headlineMedium),
        const SizedBox(height: 18),
        Row(children: [
          _MonthChip(
              label: 'June', selected: !july, onTap: () => onMonth(false)),
          const SizedBox(width: 10),
          _MonthChip(label: 'July', selected: july, onTap: () => onMonth(true)),
        ]),
        const SizedBox(height: 20),
        Text(july ? '₦1,842.30' : '₦1,610.00', style: monoStyle(size: 32)),
        Text(july ? 'vs ₦1,610.00 in June' : 'vs ₦1,488.00 in May',
            style: Theme.of(context).textTheme.bodyMedium),
        const SizedBox(height: 18),
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: softShadow),
          child: SizedBox(height: 132, child: _Bars(values: bars)),
        ),
        const SizedBox(height: 20),
        Text('Where it went', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 12),
        _SettingsCard(children: [
          _DetailRow('Transfers', cats[0]),
          _DetailRow('Bills', cats[1]),
          _DetailRow('Groceries', cats[2]),
          _DetailRow('Subscriptions', cats[3]),
        ]),
      ]),
    );
  }
}

class _ProfileTab extends StatelessWidget {
  final DemoUser user;
  final bool sentriOn;
  final ValueChanged<bool> onSentri;
  final VoidCallback onNotifications;

  const _ProfileTab(
      {required this.user,
      required this.sentriOn,
      required this.onSentri,
      required this.onNotifications});

  @override
  Widget build(BuildContext context) {
    return PrimaryScaffoldPadding(
      padding: const EdgeInsets.fromLTRB(20, 56, 20, 108),
      child: ListView(padding: EdgeInsets.zero, children: [
        Text('Profile', style: Theme.of(context).textTheme.headlineMedium),
        const SizedBox(height: 18),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(22),
              boxShadow: softShadow),
          child: Row(children: [
            const RecipientAvatar(initials: 'JA', size: 58),
            const SizedBox(width: 14),
            Expanded(
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                  Row(children: [
                    Text(user.name,
                        style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(width: 8),
                    const _Pill('Verified'),
                  ]),
                  Text('${user.id}@sentri.demo',
                      style: Theme.of(context).textTheme.bodyMedium),
                ])),
          ]),
        ),
        const SizedBox(height: 20),
        const SectionHeader('Sentri protection'),
        const SizedBox(height: 8),
        _SettingsCard(children: [
          _SwitchRow(
              'Speak up before I send',
              'Sentri shows what it noticed when a transfer breaks your pattern',
              sentriOn,
              onSentri),
          const _DetailRow('What Sentri knows about me', '›'),
        ]),
        const SizedBox(height: 18),
        _SettingsCard(children: [
          const _DetailRow('Personal details', '›'),
          const _DetailRow('Security & login', '›'),
          const _DetailRow('Payment limits', '›'),
          _DetailRow('Notifications', '›', onAction: onNotifications),
        ]),
        const SizedBox(height: 18),
        const _SettingsCard(children: [
          _DetailRow('Help & support', '›'),
          _DetailRow('Log out', ''),
        ]),
      ]),
    );
  }
}

class _SettingsCard extends StatelessWidget {
  final List<Widget> children;
  const _SettingsCard({required this.children});
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: softShadow),
      child: Column(children: [
        for (int i = 0; i < children.length; i++) ...[
          children[i],
          if (i != children.length - 1)
            const Divider(height: 1, indent: 16, endIndent: 16),
        ],
      ]),
    );
  }
}

class _SwitchRow extends StatelessWidget {
  final String title;
  final String? subtitle;
  final bool value;
  final ValueChanged<bool> onChanged;
  const _SwitchRow(this.title, this.subtitle, this.value, this.onChanged);
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      child: Row(children: [
        Expanded(
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: SentriColors.ink, fontWeight: FontWeight.w500)),
          if (subtitle != null)
            Text(subtitle!, style: Theme.of(context).textTheme.bodyMedium),
        ])),
        SentriSwitch(value: value, onChanged: onChanged),
      ]),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String title;
  final String detail;
  final String? action;
  final VoidCallback? onAction;
  const _DetailRow(this.title, this.detail, {this.action, this.onAction});
  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onAction,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 15),
        child: Row(children: [
          Expanded(
              child: Text(title,
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: SentriColors.ink, fontWeight: FontWeight.w500))),
          if (action != null)
            Text(action!,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: SentriColors.brand, fontWeight: FontWeight.w600))
          else
            Text(detail,
                style: monoStyle(
                    size: 13,
                    color: SentriColors.inkSecondary,
                    weight: FontWeight.w500)),
        ]),
      ),
    );
  }
}

class _LimitCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: softShadow),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Expanded(
              child: Text('Monthly spend limit',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: SentriColors.ink, fontWeight: FontWeight.w500))),
          Text('₦1,240.00 of ₦2,000.00',
              style: monoStyle(size: 12.5, color: SentriColors.muted1)),
        ]),
        const SizedBox(height: 12),
        ClipRRect(
          borderRadius: BorderRadius.circular(999),
          child: LinearProgressIndicator(
              value: 0.62,
              minHeight: 8,
              color: SentriColors.brand,
              backgroundColor: SentriColors.brandTint2),
        ),
      ]),
    );
  }
}

class _MonthChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;
  const _MonthChip(
      {required this.label, required this.selected, required this.onTap});
  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: PressableScale(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 11),
          decoration: BoxDecoration(
              color: selected ? SentriColors.brand : Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                  color:
                      selected ? SentriColors.brand : SentriColors.brandTint3,
                  width: 1.5)),
          child: Text(label,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: selected ? Colors.white : SentriColors.brand,
                  fontWeight: FontWeight.w600,
                  fontSize: 13.5)),
        ),
      ),
    );
  }
}

class _Bars extends StatelessWidget {
  final List<int> values;
  const _Bars({required this.values});
  @override
  Widget build(BuildContext context) {
    final peak = values.reduce((a, b) => a > b ? a : b);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: List.generate(values.length, (i) {
        return Expanded(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 5),
            child: FractionallySizedBox(
              heightFactor: values[i] / 100,
              alignment: Alignment.bottomCenter,
              child: Container(
                  decoration: BoxDecoration(
                      color: values[i] == peak
                          ? SentriColors.brand
                          : SentriColors.brandTint3,
                      borderRadius: BorderRadius.circular(9))),
            ),
          ),
        );
      }),
    );
  }
}

class _Pill extends StatelessWidget {
  final String text;
  const _Pill(this.text);
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
          color: SentriColors.brandTint2,
          borderRadius: BorderRadius.circular(999)),
      child: Text(text,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: SentriColors.brand,
              fontSize: 10,
              fontWeight: FontWeight.w600)),
    );
  }
}

class _NotificationsScreen extends StatelessWidget {
  const _NotificationsScreen();
  @override
  Widget build(BuildContext context) {
    return _PushedListScreen(title: 'Notifications', children: const [
      _NotificationRow(
        unread: true,
        title: 'Sentri looked at a transfer',
        body:
            "You've never sent to Marcus Webb before. You chose to review it.",
        timestamp: '2 hours ago',
      ),
      SizedBox(height: 11),
      _NotificationRow(
        markerColor: SentriColors.green,
        markerTint: SentriColors.greenTint,
        title: 'Money in from Ademide Johnson',
        amount: '+₦245.00',
        timestamp: 'Yesterday',
      ),
      SizedBox(height: 11),
      _NotificationRow(
        markerColor: SentriColors.amber,
        markerTint: SentriColors.amberTint,
        title: 'Your July statement is ready',
        timestamp: 'Jul 28',
      ),
    ]);
  }
}

class _NotificationRow extends StatelessWidget {
  final bool unread;
  final String title;
  final String? body;
  final String? amount;
  final String timestamp;
  final Color markerColor;
  final Color markerTint;

  const _NotificationRow({
    this.unread = false,
    required this.title,
    this.body,
    this.amount,
    required this.timestamp,
    this.markerColor = SentriColors.brand,
    this.markerTint = SentriColors.surface2,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 15),
      decoration: BoxDecoration(
        color: unread ? const Color(0xFFFAF4FD) : SentriColors.surface2,
        borderRadius: BorderRadius.circular(16),
        border: unread ? Border.all(color: SentriColors.brandTint2) : null,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (unread)
            const FactMarker()
          else
            Container(
              width: 18,
              height: 18,
              decoration: BoxDecoration(color: markerTint, shape: BoxShape.circle),
              child: Center(
                child: Container(
                  width: 8,
                  height: 8,
                  decoration:
                      BoxDecoration(color: markerColor, shape: BoxShape.circle),
                ),
              ),
            ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: SentriColors.ink,
                        fontWeight: unread ? FontWeight.w600 : FontWeight.w500,
                        fontSize: 14.5)),
                if (body != null) ...[
                  const SizedBox(height: 3),
                  Text(body!,
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          fontSize: 13, height: 1.5)),
                ],
                if (amount != null) ...[
                  const SizedBox(height: 3),
                  Text(amount!,
                      style: monoStyle(
                          size: 13,
                          color: SentriColors.inkSecondary,
                          weight: FontWeight.w400)),
                ],
                const SizedBox(height: 6),
                Text(timestamp,
                    style: Theme.of(context)
                        .textTheme
                        .bodyMedium
                        ?.copyWith(color: SentriColors.muted3, fontSize: 11)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _TransactionsScreen extends StatelessWidget {
  const _TransactionsScreen();
  @override
  Widget build(BuildContext context) {
    return const _PushedListScreen(title: 'Transactions', children: [
      SectionHeader('July 2026'),
      SizedBox(height: 10),
      _TransactionCard(rows: [
        _TxData('Eliana Baron', 'Money Out', '-₦245.00', '10/06/2026 12:45'),
        _TxData('Ademide Johnson', 'Money In', '+₦245.00', '09/06/2026 08:12'),
        _TxData('Netflix', 'Subscription', '-₦15.99', '08/06/2026 21:00'),
        _TxData('Bolagun Ahmed', 'Money Out', '-₦100.00', '05/06/2026 16:24'),
        _TxData('Payroll Inc', 'Money In', '+₦2,400.00', '01/06/2026 09:00'),
      ]),
    ]);
  }
}

class _PushedListScreen extends StatelessWidget {
  final String title;
  final List<Widget> children;
  const _PushedListScreen({required this.title, required this.children});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: PrimaryScaffoldPadding(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            CircleIconButton(
                icon: Icons.chevron_left_rounded,
                onTap: () => Navigator.pop(context)),
            const SizedBox(width: 14),
            Text(title, style: Theme.of(context).textTheme.titleLarge),
          ]),
          const SizedBox(height: 22),
          Expanded(
              child: ListView(padding: EdgeInsets.zero, children: children)),
        ]),
      ),
    );
  }
}
