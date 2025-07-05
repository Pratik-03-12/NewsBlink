import 'package:flutter/material.dart';
import 'package:newsblink/screens/homescreen.dart';
import 'package:newsblink/screens/newsummaryscreen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      initialRoute: '/',
      title: 'News Blink',
      //  home: NewsSummaryScreen(),
      routes: {'/': (context)=>const Homescreen(),
      '/newssummaryscreen': (context)=> const NewsSummaryScreen()
      }
    );
  }
}
