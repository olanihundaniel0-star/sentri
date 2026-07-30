import 'package:flutter/material.dart';

import '../design_system.dart';

class FactMarker extends StatelessWidget {
  const FactMarker({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 18,
      height: 18,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: SentriColors.brand.withOpacity(0.08),
        border:
            Border.all(color: SentriColors.brand.withOpacity(0.35), width: 1.5),
      ),
      child: Center(
        child: Container(
          width: 8,
          height: 8,
          decoration: const BoxDecoration(
              shape: BoxShape.circle, color: SentriColors.brand),
        ),
      ),
    );
  }
}

class FactRow extends StatelessWidget {
  final String text;

  const FactRow(this.text, {super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 14),
      decoration: BoxDecoration(
        color: SentriColors.surface2,
        borderRadius: BorderRadius.circular(SentriRadii.card),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const FactMarker(),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              text,
              style: Theme.of(context)
                  .textTheme
                  .bodyLarge
                  ?.copyWith(fontSize: 13.5),
            ),
          ),
        ],
      ),
    );
  }
}

class PressableScale extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final double pressedScale;
  final BorderRadius? borderRadius;

  const PressableScale({
    super.key,
    required this.child,
    this.onTap,
    this.pressedScale = 0.98,
    this.borderRadius,
  });

  @override
  State<PressableScale> createState() => _PressableScaleState();
}

class _PressableScaleState extends State<PressableScale> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onTap,
      onTapDown: (_) => setState(() => _pressed = true),
      onTapCancel: () => setState(() => _pressed = false),
      onTapUp: (_) => setState(() => _pressed = false),
      child: AnimatedScale(
        scale: _pressed ? widget.pressedScale : 1,
        duration: const Duration(milliseconds: 90),
        child: widget.child,
      ),
    );
  }
}

class CircleIconButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  final Color background;
  final Color color;

  const CircleIconButton({
    super.key,
    required this.icon,
    required this.onTap,
    this.background = SentriColors.surface2,
    this.color = SentriColors.ink,
  });

  @override
  Widget build(BuildContext context) {
    return PressableScale(
      pressedScale: 0.9,
      onTap: onTap,
      child: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(color: background, shape: BoxShape.circle),
        child: Icon(icon, color: color, size: 20),
      ),
    );
  }
}

class SectionHeader extends StatelessWidget {
  final String text;

  const SectionHeader(this.text, {super.key});

  @override
  Widget build(BuildContext context) {
    return Text(
      text.toUpperCase(),
      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: SentriColors.muted2,
            fontSize: 12.5,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.4,
          ),
    );
  }
}

class RecipientAvatar extends StatelessWidget {
  final String initials;
  final double size;

  const RecipientAvatar({super.key, required this.initials, this.size = 44});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: const BoxDecoration(
          shape: BoxShape.circle, color: SentriColors.brandTint3),
      child: Center(
        child: Text(
          initials,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: SentriColors.brand,
                fontSize: size * 0.34,
              ),
        ),
      ),
    );
  }
}

class SentriSwitch extends StatelessWidget {
  final bool value;
  final ValueChanged<bool> onChanged;

  const SentriSwitch({super.key, required this.value, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => onChanged(!value),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        curve: Curves.easeInOut,
        width: 46,
        height: 27,
        padding: const EdgeInsets.all(3),
        decoration: BoxDecoration(
          color: value ? SentriColors.brand : const Color(0xFFE2E2E8),
          borderRadius: BorderRadius.circular(999),
        ),
        child: AnimatedAlign(
          duration: const Duration(milliseconds: 180),
          curve: Curves.easeInOut,
          alignment: value ? Alignment.centerRight : Alignment.centerLeft,
          child: Container(
            width: 21,
            height: 21,
            decoration: const BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                    color: Color(0x38000000),
                    offset: Offset(0, 1),
                    blurRadius: 3),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class PrimaryScaffoldPadding extends StatelessWidget {
  final Widget child;
  final EdgeInsets padding;

  const PrimaryScaffoldPadding({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.fromLTRB(20, 56, 20, 34),
  });

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      bottom: false,
      child: Padding(padding: padding, child: child),
    );
  }
}
