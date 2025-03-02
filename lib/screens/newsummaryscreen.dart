import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class NewsSummaryScreen extends StatefulWidget {
  const NewsSummaryScreen({super.key});

  @override
  State<NewsSummaryScreen> createState() => _NewsSummaryScreenState();
}

class _NewsSummaryScreenState extends State<NewsSummaryScreen> {
  String category = "Loading..";
  String summary = "Fetching Data...";

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: false,
      appBar: AppBar(
        toolbarHeight: 80,
        title: Padding(
          padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
          child: Text(
            "Your Result",
            style: GoogleFonts.poppins(
                color: Colors.white, fontWeight: FontWeight.bold, fontSize: 35),
          ),
        ),
        centerTitle: true,
        backgroundColor: Colors.deepPurple,
      ),
      body: Stack(
        children: [
          Positioned.fill(
            child: Opacity(
                opacity: 0.35,
                child: Image.asset(
                  "assets/images/bg3.png",
                )),
          ),
          SafeArea(
              child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(
                      Icons.arrow_back,
                      size: 28,
                      color: Colors.white,
                    )),
                const SizedBox(height: 20),
                _buildCategorySection(),
                const SizedBox(
                  height: 20,
                ),
                _buildSummarySection(),
                const Spacer(),
                Center(
                  child: ElevatedButton(
                      onPressed: () => Navigator.pop(context),
                      style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.deepPurple,
                          foregroundColor: Colors.white),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(
                            vertical: 10, horizontal: 16),
                        child: const Text(
                          "Back",
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 22,
                          ),
                        ),
                      )),
                )
              ],
            ),
          ))
        ],
      ),
    );
  }

  Widget _buildCategorySection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        /// Category Header (without _customHeader function)
        Container(
          padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
          decoration: BoxDecoration(
            color: Colors.deepPurple,
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Text(
            "Category",
            style: TextStyle(
                fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
          ),
        ),
        const SizedBox(height: 5),
        Text(category, style: const TextStyle(fontSize: 16)),
      ],
    );
  }

  Widget _buildSummarySection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
          decoration: BoxDecoration(
            color: Colors.deepPurple,
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Text(
            "Summary",
            style: TextStyle(
                fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
          ),
        ),
        const SizedBox(height: 5),
        Text(summary, style: const TextStyle(fontSize: 17)),
      ],
    );
  }
}
