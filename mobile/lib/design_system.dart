import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class SentriColors {
  static const brand = Color(0xFF7E01AF);
  static const brandHover = Color(0xFF6D0197);
  static const brandPressed = Color(0xFF5C0180);
  static const brandTint1 = Color(0xFFF6ECFA);
  static const brandTint2 = Color(0xFFF0DFF8);
  static const brandTint3 = Color(0xFFECD9F2);
  static const brandBorder = Color(0xFFD9B3E6);
  static const cardPlum1 = Color(0xFF2B0733);
  static const cardPlum2 = Color(0xFF3C0A49);
  static const cardPlum3 = Color(0xFF520F63);
  static const ink = Color(0xFF1E1E2F);
  static const inkSecondary = Color(0xFF3E3E3E);
  static const muted1 = Color(0xFF717171);
  static const muted2 = Color(0xFF818181);
  static const muted3 = Color(0xFFBABABA);
  static const surface = Color(0xFFFFFFFF);
  static const surface2 = Color(0xFFF9F9F9);
  static const green = Color(0xFF1C9D55);
  static const greenTint = Color(0xFFE6F6EC);
  static const amber = Color(0xFFE09A24);
  static const amberTint = Color(0xFFFDF3E3);
  static const divider = Color(0x0F1E1E2F);
}

class SentriRadii {
  static const chip = 14.0;
  static const card = 16.0;
  static const tile = 20.0;
  static const bankCard = 22.0;
  static const sheet = 40.0;
}

ThemeData buildSentriTheme() {
  final base = ThemeData.light(useMaterial3: true);
  final outfit = GoogleFonts.outfitTextTheme(base.textTheme);

  return base.copyWith(
    scaffoldBackgroundColor: SentriColors.surface,
    colorScheme: const ColorScheme.light(
      primary: SentriColors.brand,
      secondary: SentriColors.brandTint3,
      surface: SentriColors.surface,
      onPrimary: Colors.white,
      onSurface: SentriColors.ink,
      error: SentriColors.brandPressed,
    ),
    textTheme: outfit.copyWith(
      displayLarge: GoogleFonts.outfit(
        color: SentriColors.ink,
        fontSize: 30,
        fontWeight: FontWeight.w700,
        height: 1.1,
      ),
      headlineLarge: GoogleFonts.outfit(
        color: SentriColors.ink,
        fontSize: 25,
        fontWeight: FontWeight.w700,
        height: 1.2,
      ),
      headlineMedium: GoogleFonts.outfit(
        color: SentriColors.ink,
        fontSize: 22,
        fontWeight: FontWeight.w700,
      ),
      titleLarge: GoogleFonts.outfit(
        color: SentriColors.ink,
        fontSize: 19,
        fontWeight: FontWeight.w600,
      ),
      titleMedium: GoogleFonts.outfit(
        color: SentriColors.ink,
        fontSize: 16.5,
        fontWeight: FontWeight.w600,
      ),
      bodyLarge: GoogleFonts.outfit(
        color: SentriColors.inkSecondary,
        fontSize: 14,
        height: 1.5,
      ),
      bodyMedium: GoogleFonts.outfit(
        color: SentriColors.muted2,
        fontSize: 12.5,
        height: 1.4,
      ),
      labelLarge: GoogleFonts.outfit(
        color: Colors.white,
        fontSize: 15.5,
        fontWeight: FontWeight.w600,
      ),
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: SentriColors.surface,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: GoogleFonts.outfit(
        color: SentriColors.ink,
        fontSize: 19,
        fontWeight: FontWeight.w600,
      ),
      iconTheme: const IconThemeData(color: SentriColors.ink),
    ),
    cardTheme: CardThemeData(
      color: SentriColors.surface,
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(SentriRadii.card)),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: SentriColors.surface2,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(SentriRadii.card),
        borderSide: BorderSide.none,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(SentriRadii.card),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(SentriRadii.card),
        borderSide:
            const BorderSide(color: SentriColors.brandBorder, width: 1.5),
      ),
      hintStyle: GoogleFonts.outfit(color: SentriColors.muted3, fontSize: 14),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 15),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: SentriColors.brand,
        foregroundColor: Colors.white,
        disabledBackgroundColor: const Color(0xFFE2E2E8),
        disabledForegroundColor: SentriColors.muted3,
        minimumSize: const Size(double.infinity, 54),
        elevation: 0,
        shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(SentriRadii.card)),
        textStyle:
            GoogleFonts.outfit(fontSize: 15.5, fontWeight: FontWeight.w600),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: ButtonStyle(
        foregroundColor: WidgetStateProperty.resolveWith((states) =>
            states.contains(WidgetState.disabled)
                ? SentriColors.muted3
                : SentriColors.brand),
        side: WidgetStateProperty.resolveWith((states) => BorderSide(
            color: states.contains(WidgetState.disabled)
                ? const Color(0xFFE2E2E8)
                : SentriColors.brandBorder,
            width: 1.5)),
        minimumSize:
            const WidgetStatePropertyAll(Size(double.infinity, 54)),
        shape: WidgetStatePropertyAll(RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(SentriRadii.card))),
        textStyle: WidgetStatePropertyAll(
            GoogleFonts.outfit(fontSize: 15.5, fontWeight: FontWeight.w600)),
      ),
    ),
    dividerTheme:
        const DividerThemeData(color: SentriColors.divider, thickness: 1),
  );
}

TextStyle monoStyle({
  double size = 15,
  FontWeight weight = FontWeight.w600,
  Color color = SentriColors.ink,
  double? height,
}) {
  return TextStyle(
    fontFamily: 'Cascadia Mono',
    fontFamilyFallback: const ['Cascadia Code', 'Consolas', 'monospace'],
    fontSize: size,
    fontWeight: weight,
    color: color,
    height: height,
  );
}

List<BoxShadow> get softShadow => [
      BoxShadow(
        color: SentriColors.ink.withOpacity(0.05),
        offset: const Offset(0, 1),
        blurRadius: 2,
      ),
      BoxShadow(
        color: SentriColors.ink.withOpacity(0.06),
        offset: const Offset(0, 3),
        blurRadius: 12,
      ),
    ];
