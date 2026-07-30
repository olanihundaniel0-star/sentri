import 'dart:async';

import 'package:flutter/material.dart';

import '../api_client.dart';
import '../app_data.dart';
import '../design_system.dart';
import '../widgets/sentri_mascot.dart';
import '../widgets/ui_components.dart';
import 'dashboard_screen.dart';

class UserSelectScreen extends StatefulWidget {
  const UserSelectScreen({super.key});

  @override
  State<UserSelectScreen> createState() => _UserSelectScreenState();
}

class _UserSelectScreenState extends State<UserSelectScreen> {
  bool _showSplash = true;
  bool _backendOnline = false;
  bool _checking = true;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _checkBackend();
    _timer = Timer(const Duration(milliseconds: 4200), _skipSplash);
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _checkBackend() async {
    setState(() => _checking = true);
    final ok = await ApiClient().checkHealth();
    if (!mounted) return;
    setState(() {
      _backendOnline = ok;
      _checking = false;
    });
  }

  void _skipSplash() {
    if (mounted && _showSplash) setState(() => _showSplash = false);
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 420),
      child: _showSplash
          ? _Splash(onSkip: _skipSplash)
          : _Explainer(
              onRetry: _checkBackend,
              checking: _checking,
              backendOnline: _backendOnline),
    );
  }
}

class _Splash extends StatelessWidget {
  final VoidCallback onSkip;

  const _Splash({required this.onSkip});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onSkip,
      child: Scaffold(
        body: Container(
          decoration: const BoxDecoration(
            gradient: RadialGradient(
              center: Alignment(0, -0.2),
              radius: 0.85,
              colors: [Color(0xFF2A1236), Color(0xFF170C1F), Color(0xFF0E0713)],
              stops: [0, 0.52, 1],
            ),
          ),
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const SentriMascot(interactive: true),
                const SizedBox(height: 26),
                Text(
                  'Sentri',
                  style: Theme.of(context).textTheme.displayLarge?.copyWith(
                        color: Colors.white,
                        fontSize: 31,
                        letterSpacing: -0.5,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Quiet protection for every transfer',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: Colors.white.withOpacity(0.62),
                      ),
                ),
                const SizedBox(height: 22),
                Text(
                  'Move your finger — Sentri follows',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.white.withOpacity(0.34),
                        fontSize: 11.5,
                        letterSpacing: 0.3,
                      ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _Explainer extends StatelessWidget {
  final VoidCallback onRetry;
  final bool checking;
  final bool backendOnline;

  const _Explainer({
    required this.onRetry,
    required this.checking,
    required this.backendOnline,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: PrimaryScaffoldPadding(
        padding: const EdgeInsets.fromLTRB(20, 72, 20, 34),
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  children: [
                    SizedBox(
                      width: 100,
                      height: 100,
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          Container(
                            width: 100,
                            height: 100,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(
                                  color: SentriColors.brand.withOpacity(0.45),
                                  width: 1.5),
                            ),
                          ),
                          Container(
                            width: 46,
                            height: 46,
                            decoration: const BoxDecoration(
                              shape: BoxShape.circle,
                              gradient: RadialGradient(
                                center: Alignment(-0.3, -0.4),
                                colors: [
                                  Color(0xFF9A1FC9),
                                  SentriColors.brand,
                                  Color(0xFF63018F)
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 26),
                    Text('Meet Sentri.',
                        style: Theme.of(context).textTheme.headlineLarge),
                    const SizedBox(height: 12),
                    ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 300),
                      child: Text(
                        'Sentri quietly learns how you usually send money — who to, how much, how often. If a transfer breaks that pattern, it says something before you send it.',
                        textAlign: TextAlign.center,
                        style: Theme.of(context)
                            .textTheme
                            .bodyLarge
                            ?.copyWith(fontSize: 15, height: 1.55),
                      ),
                    ),
                    const SizedBox(height: 26),
                    const FactRow('Learns your normal transfer pattern'),
                    const SizedBox(height: 11),
                    const FactRow('Speaks up only when something is different'),
                    const SizedBox(height: 11),
                    const FactRow(
                        'Always your call — Sentri explains, you decide'),
                    const SizedBox(height: 22),
                    _BackendPill(
                        checking: checking,
                        online: backendOnline,
                        onRetry: onRetry),
                  ],
                ),
              ),
            ),
            Column(
              children: [
                ElevatedButton(
                  onPressed: () {
                    Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                          builder: (_) =>
                              DashboardScreen(user: AppData.users.first)),
                    );
                  },
                  child: const Text('Get started'),
                ),
                const SizedBox(height: 12),
                TextButton(
                  onPressed: () => _chooseUser(context),
                  child: const Text('Switch demo user',
                      style: TextStyle(color: SentriColors.brand)),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _chooseUser(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: SentriColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius:
            BorderRadius.vertical(top: Radius.circular(SentriRadii.sheet)),
      ),
      builder: (_) => Padding(
        padding: const EdgeInsets.fromLTRB(20, 14, 20, 34),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                  width: 36,
                  height: 4,
                  decoration: BoxDecoration(
                      color: const Color(0xFFD8D8DC),
                      borderRadius: BorderRadius.circular(999))),
            ),
            const SizedBox(height: 20),
            Text('Choose demo profile',
                style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 12),
            ...AppData.users.map((user) => Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: PressableScale(
                    onTap: () {
                      Navigator.pop(context);
                      Navigator.pushReplacement(
                          context,
                          MaterialPageRoute(
                              builder: (_) => DashboardScreen(user: user)));
                    },
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                          color: SentriColors.surface2,
                          borderRadius: BorderRadius.circular(16)),
                      child: Row(
                        children: [
                          const RecipientAvatar(initials: 'JA'),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(user.name,
                                    style: Theme.of(context)
                                        .textTheme
                                        .titleMedium),
                                Text('${user.id} · ${user.cohortLabel}',
                                    style:
                                        Theme.of(context).textTheme.bodyMedium),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                )),
          ],
        ),
      ),
    );
  }
}

class _BackendPill extends StatelessWidget {
  final bool checking;
  final bool online;
  final VoidCallback onRetry;

  const _BackendPill(
      {required this.checking, required this.online, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    final color = checking
        ? SentriColors.muted2
        : (online ? SentriColors.green : SentriColors.amber);
    return PressableScale(
      onTap: onRetry,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.09),
          borderRadius: BorderRadius.circular(999),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
                width: 8,
                height: 8,
                decoration:
                    BoxDecoration(color: color, shape: BoxShape.circle)),
            const SizedBox(width: 8),
            Text(
              checking
                  ? 'Checking backend'
                  : (online
                      ? 'Backend online'
                      : 'Backend offline · tap to retry'),
              style: Theme.of(context)
                  .textTheme
                  .bodyMedium
                  ?.copyWith(color: color, fontWeight: FontWeight.w600),
            ),
          ],
        ),
      ),
    );
  }
}
