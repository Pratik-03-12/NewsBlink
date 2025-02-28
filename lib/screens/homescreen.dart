
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:newsblink/widgets/paste_link_button.dart';

class Homescreen extends StatefulWidget {
  const Homescreen({super.key});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<Homescreen> {
  bool showTextField = false;
  String? errormessage;
  final TextEditingController _textEditingController = TextEditingController();

  bool isValidYouTubeLink(String url) {
    final RegExp youtubeRegExp = RegExp(
      r'^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/|v\/)|youtu\.be\/)[\w-]+(&\S*)?$',
      caseSensitive: false,
      multiLine: false,
    );
    return youtubeRegExp.hasMatch(url);
  }
  void navigateToNextPage() {
    String link = _textEditingController.text.trim();
    if (_textEditingController.text.isNotEmpty) {
      setState(()=>errormessage = null);
      Navigator.pushReplacementNamed(
        context,
        '/newssummaryscreen',
      );
    }
    else{
      setState(()=>errormessage = "Enter a valid Youtube Link");
    }
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: false,
      extendBodyBehindAppBar: true,
      appBar: AppBar(
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
      body: Stack(
        children: [
          Positioned.fill(
            child:
                Image.asset("assets/images/background.png", fit: BoxFit.cover),
          ),
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Padding(
                  padding: const EdgeInsets.only(
                      left: 10.0, top: 30.0, right: 0.0, bottom: 0.0),
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
                  Padding(padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: TextField(
                    controller: _textEditingController,

                    decoration: InputDecoration(
                      hintText: "Enter your Youtube link",
                      errorText: errormessage,
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10))
                    ),
                  ),
                  ),
                  const SizedBox(height: 10,),
                  ElevatedButton(onPressed: navigateToNextPage, child: const Text("Proceed"))
                ]
              ],
            ),
          )
        ],
      ),
    );
  }
}
