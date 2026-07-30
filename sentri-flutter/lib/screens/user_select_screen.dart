import 'package:flutter/material.dart';
import '../api_client.dart';
import '../config.dart';
import 'dashboard_screen.dart';

class UserSelectScreen extends StatefulWidget {
  const UserSelectScreen({super.key});

  @override
  State<UserSelectScreen> createState() => _UserSelectScreenState();
}

class _UserSelectScreenState extends State<UserSelectScreen> {
  bool _backendOnline = false;
  bool _checking = true;

  @override
  void initState() {
    super.initState();
    _checkBackend();
  }

  Future<void> _checkBackend() async {
    setState(() => _checking = true);
    final ok = await ApiClient().checkHealth();
    setState(() {
      _backendOnline = ok;
      _checking = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 24),
              // Logo
              Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF00D4AA), Color(0xFF0099FF)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(Icons.shield_rounded, color: Colors.white, size: 24),
                  ),
                  const SizedBox(width: 12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Sentri', style: Theme.of(context).textTheme.displayMedium),
                      Text('AI security coprocessor',
                          style: Theme.of(context).textTheme.bodyMedium),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Backend status
              GestureDetector(
                onTap: _checkBackend,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: _checking
                        ? const Color(0xFF1A2235)
                        : _backendOnline
                            ? const Color(0xFF00D4AA).withOpacity(0.08)
                            : const Color(0xFFFF6B35).withOpacity(0.08),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: _checking
                          ? const Color(0xFF253048)
                          : _backendOnline
                              ? const Color(0xFF00D4AA).withOpacity(0.3)
                              : const Color(0xFFFF6B35).withOpacity(0.3),
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      _checking
                          ? const SizedBox(
                              width: 10,
                              height: 10,
                              child: CircularProgressIndicator(strokeWidth: 1.5),
                            )
                          : Container(
                              width: 8,
                              height: 8,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: _backendOnline
                                    ? const Color(0xFF00D4AA)
                                    : const Color(0xFFFF6B35),
                              ),
                            ),
                      const SizedBox(width: 8),
                      Text(
                        _checking
                            ? 'Checking backend...'
                            : _backendOnline
                                ? 'Backend online · localhost:8000'
                                : 'Backend offline — tap to retry',
                        style: Theme.of(context).textTheme.bodyMedium!.copyWith(
                              fontSize: 12,
                              color: _backendOnline
                                  ? const Color(0xFF00D4AA)
                                  : const Color(0xFFFF6B35),
                            ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 40),

              Text('Select User', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8),
              Text(
                'Each user has a distinct behavioral profile. Sentri scores transactions against that history.',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 20),

              Expanded(
                child: ListView.separated(
                  itemCount: Config.demoUsers.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (context, i) {
                    final userId = Config.demoUsers[i];
                    final meta = Config.userMeta[userId]!;
                    return _UserCard(
                      userId: userId,
                      meta: meta,
                      onTap: () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => DashboardScreen(userId: userId),
                        ),
                      ),
                    );
                  },
                ),
              ),

              // What Sentri checks
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xFF1A2235),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF253048)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('What Sentri checks on every transaction',
                        style: Theme.of(context).textTheme.bodyMedium!.copyWith(
                              color: const Color(0xFFE8EDF5),
                              fontWeight: FontWeight.w600,
                              fontSize: 12,
                            )),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: const [
                        _SignalTag('Recipient familiarity'),
                        _SignalTag('Graph proximity'),
                        _SignalTag('Amount z-score'),
                        _SignalTag('Hour deviation'),
                        _SignalTag('Currency novelty'),
                        _SignalTag('Cross-border'),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _UserCard extends StatelessWidget {
  final String userId;
  final UserMeta meta;
  final VoidCallback onTap;

  const _UserCard({required this.userId, required this.meta, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Row(
            children: [
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: meta.color.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(meta.icon, color: meta.color, size: 26),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(meta.name, style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 3),
                    Text(userId, style: Theme.of(context).textTheme.bodyMedium),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: meta.color.withOpacity(0.12),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            meta.cohortLabel,
                            style: TextStyle(
                                color: meta.color, fontSize: 11, fontWeight: FontWeight.w600),
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(meta.description,
                            style:
                                Theme.of(context).textTheme.bodyMedium!.copyWith(fontSize: 11)),
                      ],
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right_rounded, color: Color(0xFF8A9BB5)),
            ],
          ),
        ),
      ),
    );
  }
}

class _SignalTag extends StatelessWidget {
  final String label;
  const _SignalTag(this.label);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF253048),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(label,
          style: Theme.of(context).textTheme.bodyMedium!.copyWith(fontSize: 10)),
    );
  }
}
