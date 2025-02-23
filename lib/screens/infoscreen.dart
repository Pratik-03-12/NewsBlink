import 'package:flutter/material.dart';

class infoScreen extends StatelessWidget {
  const infoScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("This shows the information")),
      body: Center(child: const Text("You entered: "),),
    );
  }
}
