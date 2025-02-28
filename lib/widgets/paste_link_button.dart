import 'package:flutter/material.dart';

class PasteLinkButton extends StatefulWidget {
  final VoidCallback onPressed;
  const PasteLinkButton({super.key, required this.onPressed});

  @override
  _PasteLinkButtonState createState() => _PasteLinkButtonState();
}

class _PasteLinkButtonState extends State<PasteLinkButton> {
  bool isHovered = false;
  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: ElevatedButton.icon(
        onPressed: widget.onPressed,
        icon: const Icon(
          Icons.paste,
          color: Colors.white,
        ),
        label: const Text("Paste your Link"),
        style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blueAccent,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(150)),
            textStyle:
                const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
      ),
    );
  }
}
