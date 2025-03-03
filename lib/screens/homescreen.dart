import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:newsblink/screens/newsummaryscreen.dart';
import 'package:newsblink/widgets/paste_link_button.dart';
import 'package:http/http.dart' as http;

class Homescreen extends StatefulWidget {
  const Homescreen({super.key});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<Homescreen> {
  bool showTextField = false;
  String? errormessage;
  bool _isLoading = false;
  final TextEditingController _textEditingController = TextEditingController();

  bool isValidYouTubeLink(String url) {
    final RegExp youtubeRegExp = RegExp(
      r'^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/|v\/)|youtu\.be\/)[\w-]+(&\S*)?$',
      caseSensitive: false,
      multiLine: false,
    );
    return youtubeRegExp.hasMatch(url);
  }
  Future<Map<String, dynamic>?> processVideo(String videoUrl) async {
    final url = Uri.parse("http://10.0.2.2:8000/process_video");  // Replace with your backend URL

    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json","server": "uvicorn"},
        body: jsonEncode({"url": videoUrl}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);  // Return response as Map
      } else {
        print("Error: ${response.body}");
        return null;
      }
    } catch (e) {
      print("Exception: $e");
      return null;
    }
  }

  void navigateToNextPage() async {
    String link = _textEditingController.text.trim();

    if (link.isNotEmpty && isValidYouTubeLink(link)) {
      setState(() => errormessage = null);

      final response = await processVideo(link);  // API call to backend

      if (response != null) {
        // Navigate with fetched data
        Navigator.pushNamed(
          context,
          '/newssummaryscreen',
          arguments: {
            'category': response['category'] ?? "Unknown Category",
            'summary': response['summary'] ?? "No Summary Available",
          },
        );
      } else {
        setState(() => errormessage = "Failed to fetch data from server.");
      }
    } else {
      setState(() => errormessage = "Enter a valid YouTube link.");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: false,
      extendBodyBehindAppBar: true,
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(70),
        child: AppBar(
          toolbarHeight: 70,
          title: Padding(
            padding: const EdgeInsets.only(top: 15.0),
            child: Text("NEWSBLINK",
                style: GoogleFonts.poppins(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 38,
                  // fontStyle: FontStyle.italic
                )),
          ),
          centerTitle: true,
          backgroundColor: Colors.transparent,
          elevation: 0,
        ),
      ),
      body: Stack(
        children: [
          Positioned.fill(
            child:
                Image.asset("assets/images/background.png", fit: BoxFit.cover),
          ),
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              // crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // const SizedBox(height: 10,),
                Padding(
                  padding: const EdgeInsets.only(
                      left: 10.0, top: 50.0, right: 0.0, bottom: 0.0),
                  child: Image.asset(
                    'assets/images/bg.png',
                    height: 380,
                  ),
                ),
                // const SizedBox(height: 8),
                Text(
                  "Get Started",
                  style: GoogleFonts.robotoFlex(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 2,
                      fontSize: 52),
                ),
                const SizedBox(height: 10),
                Text(
                  "Stay informed in a snap – get your news\ncategory and summary instantly!",
                  textAlign: TextAlign.center,
                  style: GoogleFonts.arvo(fontSize: 16, color: Colors.white),
                ),
                const SizedBox(height: 30),
                Padding(
                  padding: const EdgeInsets.all(10.0),
                  child: PasteLinkButton(onPressed: () {
                    setState(() {
                      showTextField = !showTextField;
                    });
                  }),
                ),
                if (showTextField) ...[
                  const SizedBox(
                    height: 15,
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: TextField(
                      controller: _textEditingController,
                      decoration: InputDecoration(
                          hintText: "Enter your Youtube link",
                          errorText: errormessage,
                          filled: true,
                          fillColor: Colors.white,
                          border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(10))),
                    ),
                  ),
                  const SizedBox(
                    height: 10,
                  ),
                  ElevatedButton(
                      onPressed: navigateToNextPage,
                      child: _isLoading?CircularProgressIndicator(color: Colors.white,):Text("Proceed"),)
                ]
              ],
            ),
          )
        ],
      ),
    );
  }
}
