import 'package:flutter/material.dart';

class PasteLinkButton extends StatelessWidget {
  final VoidCallback onPressed;
  const PasteLinkButton({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.blue,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(25)),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      ),
      child: const Text("Paste your link",style: TextStyle(fontSize: 16,color: Colors.white),),
    );
  }
}
