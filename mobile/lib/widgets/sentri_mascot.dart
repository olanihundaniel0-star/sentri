import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';

class SentriMascot extends StatefulWidget {
  /// Size of the backdrop stage (rings / glow / scan arc live inside this box).
  final double size;

  /// Size of the mascot orb itself. Defaults to [size] (used by the splash,
  /// where the orb fills its stage). The Sentri-check sheet uses a smaller
  /// orb inside a larger stage, so it passes both.
  final double? mascotSize;
  final bool interactive;

  /// Idle/splash backdrop: two staggered soft rings + a breathing glow.
  final bool rings;

  /// "Sentri in action" backdrop: three tightly-staggered brand-colour
  /// sonar rings, a rotating scan arc, and a static glow — the distinct
  /// treatment for the moment Sentri is actively checking a transfer.
  final bool checking;

  const SentriMascot({
    super.key,
    this.size = 212,
    this.mascotSize,
    this.interactive = false,
    this.rings = true,
    this.checking = false,
  });

  @override
  State<SentriMascot> createState() => _SentriMascotState();
}

class _SentriMascotState extends State<SentriMascot>
    with TickerProviderStateMixin {
  late final AnimationController _float;
  late final AnimationController _blink;
  Offset _aim = Offset.zero;
  double _near = 0;

  @override
  void initState() {
    super.initState();
    _float =
        AnimationController(vsync: this, duration: const Duration(seconds: 5))
          ..repeat();
    _blink = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 4600))
      ..repeat();
  }

  @override
  void dispose() {
    _float.dispose();
    _blink.dispose();
    super.dispose();
  }

  void _track(Offset localPosition) {
    if (!widget.interactive) return;
    final center = Offset(widget.size / 2, widget.size / 2);
    final delta = localPosition - center;
    final distance = delta.distance;
    setState(() {
      _aim = Offset(
        (delta.dx / 300).clamp(-1.0, 1.0).toDouble(),
        (delta.dy / 300).clamp(-1.0, 1.0).toDouble(),
      );
      _near = math.max(0.0, 1 - distance / 340);
    });
  }

  @override
  Widget build(BuildContext context) {
    final svgSize = widget.mascotSize ?? widget.size;
    return Listener(
      onPointerHover: (event) => _track(event.localPosition),
      onPointerMove: (event) => _track(event.localPosition),
      child: SizedBox(
        width: widget.size,
        height: widget.size,
        child: Stack(
          alignment: Alignment.center,
          children: [
            if (widget.checking) ..._checkingBackdrop(),
            if (widget.rings && !widget.checking) ..._idleBackdrop(),
            AnimatedBuilder(
              animation: Listenable.merge([_float, _blink]),
              builder: (_, __) {
                final bob = math.sin(_float.value * math.pi * 2) * -7;
                final blinkWindow = _blink.value > 0.90 && _blink.value < 1.0;
                final blinkProgress =
                    ((_blink.value - 0.90) / 0.10).clamp(0.0, 1.0);
                final blink = blinkWindow
                    ? 1 - math.sin(blinkProgress * math.pi) * 0.95
                    : 1.0;
                return Transform.translate(
                  offset: Offset(-_aim.dx * 3, bob - _aim.dy * 3),
                  child: Transform.rotate(
                    angle: _aim.dx * math.pi / 112,
                    child: CustomPaint(
                      size: Size.square(svgSize),
                      painter: _MascotPainter(
                        irisOffset: _aim * 5,
                        pupilOffset: _aim * 8,
                        pupilScale: 1 + _near * 0.22,
                        blinkScale: blink,
                      ),
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _idleBackdrop() {
    return [
      _PulseRing(size: widget.size * 1.123, delay: Duration.zero),
      _PulseRing(
          size: widget.size * 1.123,
          delay: const Duration(milliseconds: 1800)),
      AnimatedBuilder(
        animation: _float,
        builder: (_, __) {
          final t = math.sin(_float.value * math.pi * 2);
          return Transform.scale(
            scale: 1 + t * 0.03,
            child: Container(
              width: widget.size * 0.99,
              height: widget.size * 0.99,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    const Color(0xFFA83CD8).withOpacity(0.24),
                    const Color(0x00A83CD8),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    ];
  }

  List<Widget> _checkingBackdrop() {
    final stage = widget.size;
    return [
      Container(
        width: stage,
        height: stage,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: RadialGradient(
            colors: [
              const Color(0xFF7E01AF).withOpacity(0.10),
              const Color(0x007E01AF),
            ],
          ),
        ),
      ),
      _ScanArc(size: stage * (220 / 260)),
      for (final delaySeconds in const [0, 1, 2])
        _PulseRing(
          size: stage * (190 / 260),
          delay: Duration(seconds: delaySeconds),
          duration: const Duration(seconds: 3),
          color: const Color(0xFF7E01AF),
          borderWidth: 1.5,
          maxOpacity: 0.45,
        ),
    ];
  }
}

class _PulseRing extends StatefulWidget {
  final double size;
  final Duration delay;
  final Duration duration;
  final Color color;
  final double borderWidth;
  final double maxOpacity;

  const _PulseRing({
    required this.size,
    required this.delay,
    this.duration = const Duration(milliseconds: 3600),
    this.color = const Color(0xFFA83CD8),
    this.borderWidth = 1,
    this.maxOpacity = 0.38,
  });

  @override
  State<_PulseRing> createState() => _PulseRingState();
}

class _PulseRingState extends State<_PulseRing>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  Timer? _startTimer;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: widget.duration);
    _startTimer = Timer(widget.delay, () {
      if (mounted) _controller.repeat();
    });
  }

  @override
  void dispose() {
    _startTimer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (_, __) {
        final scale = 0.6 + _controller.value * 0.9;
        final opacity = (widget.maxOpacity * (1 - _controller.value * 1.4))
            .clamp(0.0, widget.maxOpacity)
            .toDouble();
        return Transform.scale(
          scale: scale,
          child: Opacity(
            opacity: opacity,
            child: Container(
              width: widget.size,
              height: widget.size,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                    color: widget.color.withOpacity(0.7),
                    width: widget.borderWidth),
              ),
            ),
          ),
        );
      },
    );
  }
}

/// The rotating "scan arc" shown behind the mascot while Sentri is actively
/// checking a transfer — a thin ring with one brighter leading edge,
/// spinning slowly (7s/turn), distinct from the idle splash rings.
class _ScanArc extends StatefulWidget {
  final double size;

  const _ScanArc({required this.size});

  @override
  State<_ScanArc> createState() => _ScanArcState();
}

class _ScanArcState extends State<_ScanArc>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller =
        AnimationController(vsync: this, duration: const Duration(seconds: 7))
          ..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (_, __) => Transform.rotate(
        angle: _controller.value * 2 * math.pi,
        child: CustomPaint(
          size: Size.square(widget.size),
          painter: _ScanArcPainter(),
        ),
      ),
    );
  }
}

class _ScanArcPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final center = size.center(Offset.zero);
    final radius = size.width / 2;
    final rect = Rect.fromCircle(center: center, radius: radius);

    canvas.drawCircle(
      center,
      radius,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1
        ..color = const Color(0xFF7E01AF).withOpacity(0.16),
    );

    canvas.drawArc(
      rect,
      -math.pi / 2 - 0.45,
      0.9,
      false,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1
        ..strokeCap = StrokeCap.round
        ..color = const Color(0xFF7E01AF).withOpacity(0.4),
    );
  }

  @override
  bool shouldRepaint(covariant _ScanArcPainter oldDelegate) => false;
}

class _MascotPainter extends CustomPainter {
  final Offset irisOffset;
  final Offset pupilOffset;
  final double pupilScale;
  final double blinkScale;

  _MascotPainter({
    required this.irisOffset,
    required this.pupilOffset,
    required this.pupilScale,
    required this.blinkScale,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final s = size.width / 200;
    canvas.save();
    canvas.scale(s);

    final shadow = Paint()..color = const Color(0xBF0A040F);
    canvas.drawOval(
        Rect.fromCenter(center: const Offset(100, 184), width: 92, height: 14),
        shadow);

    final facets = [
      (
        [
          const Offset(100, 20),
          const Offset(132, 37),
          const Offset(118, 82),
          const Offset(100, 68)
        ],
        const Color(0xFFC069E8)
      ),
      (
        [
          const Offset(132, 37),
          const Offset(169, 70),
          const Offset(130, 96),
          const Offset(118, 82)
        ],
        const Color(0xFFB954E2)
      ),
      (
        [
          const Offset(169, 70),
          const Offset(178, 114),
          const Offset(132, 116),
          const Offset(130, 96)
        ],
        const Color(0xFFA83CD8)
      ),
      (
        [
          const Offset(178, 114),
          const Offset(150, 160),
          const Offset(120, 132),
          const Offset(132, 116)
        ],
        const Color(0xFF9B28C4)
      ),
      (
        [
          const Offset(150, 160),
          const Offset(100, 176),
          const Offset(100, 137),
          const Offset(120, 132)
        ],
        const Color(0xFF8F14BF)
      ),
      (
        [
          const Offset(100, 176),
          const Offset(50, 160),
          const Offset(80, 132),
          const Offset(100, 137)
        ],
        const Color(0xFF7E01AF)
      ),
      (
        [
          const Offset(50, 160),
          const Offset(22, 114),
          const Offset(68, 116),
          const Offset(80, 132)
        ],
        const Color(0xFF7405A3)
      ),
      (
        [
          const Offset(22, 114),
          const Offset(31, 70),
          const Offset(70, 96),
          const Offset(68, 116)
        ],
        const Color(0xFF63018F)
      ),
      (
        [
          const Offset(31, 70),
          const Offset(68, 37),
          const Offset(82, 82),
          const Offset(70, 96)
        ],
        const Color(0xFF5F0186)
      ),
      (
        [
          const Offset(68, 37),
          const Offset(100, 20),
          const Offset(100, 68),
          const Offset(82, 82)
        ],
        const Color(0xFF520178)
      ),
      (
        [
          const Offset(82, 82),
          const Offset(100, 68),
          const Offset(118, 82),
          const Offset(130, 96),
          const Offset(132, 116),
          const Offset(120, 132),
          const Offset(100, 137),
          const Offset(80, 132),
          const Offset(68, 116),
          const Offset(70, 96),
        ],
        const Color(0xFF4D016D)
      ),
    ];

    for (final facet in facets) {
      final path = Path()..addPolygon(facet.$1, true);
      canvas.drawPath(path, Paint()..color = facet.$2);
    }

    canvas.drawCircle(
        const Offset(100, 100), 38, Paint()..color = const Color(0xFF1D0A26));
    canvas.drawCircle(
        const Offset(100, 100), 30, Paint()..color = const Color(0xFF120616));
    canvas.drawCircle(
      const Offset(100, 100),
      27,
      Paint()
        ..shader = const RadialGradient(
          center: Alignment(0, -0.2),
          colors: [Color(0xFF3A1049), Color(0xFF170A1E)],
        ).createShader(
            Rect.fromCircle(center: const Offset(100, 100), radius: 27)),
    );

    canvas.save();
    canvas.translate(100, 100);
    canvas.scale(1, blinkScale);
    canvas.translate(irisOffset.dx, irisOffset.dy);
    canvas.drawCircle(
      Offset.zero,
      18,
      Paint()
        ..shader = const RadialGradient(
          center: Alignment(-0.25, -0.35),
          colors: [
            Color(0xFFF6DCFF),
            Color(0xFFC471EA),
            Color(0xFF8F14BF),
            Color(0xFF40015A)
          ],
          stops: [0, 0.30, 0.64, 1],
        ).createShader(Rect.fromCircle(center: Offset.zero, radius: 18)),
    );
    canvas.save();
    canvas.translate(pupilOffset.dx, pupilOffset.dy);
    canvas.scale(pupilScale);
    canvas.drawCircle(
        Offset.zero, 9.5, Paint()..color = const Color(0xFF150818));
    canvas.drawCircle(const Offset(-4.6, -5.2), 3.5,
        Paint()..color = Colors.white.withOpacity(0.92));
    canvas.restore();
    canvas.restore();
    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant _MascotPainter oldDelegate) {
    return oldDelegate.irisOffset != irisOffset ||
        oldDelegate.pupilOffset != pupilOffset ||
        oldDelegate.pupilScale != pupilScale ||
        oldDelegate.blinkScale != blinkScale;
  }
}
