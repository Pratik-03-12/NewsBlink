import 'package:flutter/material.dart';
import 'package:newsblink/screens/infoscreen.dart';
import 'package:newsblink/widgets/paste_link_button.dart';
// import '../utils/app_colors.dart';

class Homescreen extends StatefulWidget {
  const Homescreen({super.key});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<Homescreen> {
  bool showTextField = false;
  final TextEditingController linkController = TextEditingController();

  void navigateToNextPage() {
    if (linkController.text.isNotEmpty) {
      Navigator.pushReplacementNamed(
        context,
        '/infoscreen'
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          Positioned.fill(
            child: Image.asset('assets/background.png', fit: BoxFit.cover),
          ),
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Image.asset('assets/illustration.png', height: 250),
                const SizedBox(height: 20),
                const Text("NEWSBLINK", style: TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold, letterSpacing: 2)),
                const SizedBox(height: 10),
                const Text("Get Started", style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Colors.white)),
                const SizedBox(height: 10),
                const Text(
                  "Stay informed in a snap – get your news\ncategory and summary instantly!",
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 14, color: Colors.white70),
                ),
                const SizedBox(height: 20),

                // "Paste your Link" Button
                PasteLinkButton(onPressed: () {
                  setState(() {
                    showTextField = !showTextField;
                  });
                }),

                if (showTextField) ...[
                  const SizedBox(height: 15),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: TextField(
                      controller: linkController,
                      decoration: InputDecoration(
                        hintText: "Enter YouTube Link",
                        filled: true,
                        fillColor: Colors.white,
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  ElevatedButton(
                    onPressed: navigateToNextPage,
                    child: const Text("Next"),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
