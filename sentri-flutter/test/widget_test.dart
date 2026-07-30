import 'package:flutter_test/flutter_test.dart';
import 'package:sentri_app/main.dart';

void main() {
  testWidgets('Sentri app renders splash', (tester) async {
    await tester.pumpWidget(const SentriApp());

    expect(find.text('Sentri'), findsOneWidget);
    expect(find.text('Quiet protection for every transfer'), findsOneWidget);
  });
}
