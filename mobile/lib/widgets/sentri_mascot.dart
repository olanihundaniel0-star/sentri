import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';

class SentriMascot extends StatefulWidget {
  final double size;
  final bool interactive;
  final bool rings;

  const SentriMascot({
    super.key,
    this.size = 212,
    this.interactive = false,
    this.rings = true,
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
    return Listener(
      onPointerHover: (event) => _track(event.localPosition),
      onPointerMove: (event) => _track(event.localPosition),
      child: SizedBox(
        width: widget.size,
        height: widget.size,
        child: Stack(
          alignment: Alignment.center,
          children: [
            if (widget.rings) ...[
              _PulseRing(size: widget.size * 1.12, delay: Duration.zero),
              _PulseRing(
                  size: widget.size * 1.12,
                  delay: const Duration(milliseconds: 1500)),
              AnimatedBuilder(
                animation: _float,
                builder: (_, __) {
                  final t = math.sin(_float.value * math.pi * 2);
                  return Transform.scale(
                    scale: 1 + t * 0.03,
                    child: Container(
                      width: widget.size * 0.98,
                      height: widget.size * 0.98,
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
            ],
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
                      size: Size.square(widget.size),
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
}

class _PulseRing extends StatefulWidget {
  final double size;
  final Duration delay;

  const _PulseRing({required this.size, required this.delay});

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
    _controller =
        AnimationController(vsync: this, duration: const Duration(seconds: 3));
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
        final opacity =
            (0.6 * (1 - _controller.value * 1.4)).clamp(0.0, 0.6).toDouble();
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
                    color: const Color(0xFFA83CD8).withOpacity(0.38)),
              ),
            ),
          ),
        );
      },
    );
  }
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
