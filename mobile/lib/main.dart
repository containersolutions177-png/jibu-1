import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';
import 'dart:convert';

void main() => runApp(const JibuApp());

class JibuApp extends StatelessWidget {
  const JibuApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Jibu',
      theme: ThemeData(primarySwatch: Colors.green, useMaterial3: true),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final String apiUrl = "https://jibu-ten.vercel.app"; // ⚠️ CHANGE THIS TO YOUR VERCEL BACKEND
  List products = [];

  @override
  void initState() {
    super.initState();
    fetchProducts();
  }

  Future<void> fetchProducts() async {
    try {
      final res = await http.get(Uri.parse("$apiUrl/products"));
      setState(() => products = jsonDecode(res.body));
    } catch (e) {
      debugPrint("Error: $e");
    }
  }

  Future<void> makePayment(String provider, double amount, String name) async {
    try {
      final res = await http.post(
        Uri.parse("$apiUrl/checkout"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "provider": provider,
          "amount": amount,
          "currency": "ZAR",
          "item_name": name,
          "email": "test@jibu.app",
          "return_url": "https://jibu.app",
          "cancel_url": "https://jibu.app",
          "notify_url": "$apiUrl/webhook"
        })
      );
      final data = jsonDecode(res.body);
      if (data['payment_url'] != null) {
        await launchUrl(Uri.parse(data['payment_url']), mode: LaunchMode.externalApplication);
      }
    } catch (e) {
      debugPrint("Payment error: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Jibu Marketplace"), backgroundColor: Colors.green),
      body: ListView.builder(
        itemCount: products.length,
        itemBuilder: (context, index) {
          final p = products[index];
          return Card(
            margin: const EdgeInsets.all(10),
            child: Column(
              children: [
                Image.network(p['image_url'], height: 150, width: double.infinity, fit: BoxFit.cover),
                ListTile(
                  title: Text(p['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text("R${p['price']}"),
                  trailing: ElevatedButton(
                    child: const Text("Pay"),
                    onPressed: () => showDialog(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        title: const Text("Choose Gateway"),
                        content: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            ListTile(title: const Text("PayFast (ZAR)"), onTap: () { Navigator.pop(ctx); makePayment("payfast", p['price'], p['name']); }),
                            ListTile(title: const Text("Ozow (Instant EFT)"), onTap: () { Navigator.pop(ctx); makePayment("ozow", p['price'], p['name']); }),
                            ListTile(title: const Text("Stripe (Global)"), onTap: () { Navigator.pop(ctx); makePayment("stripe", p['price'], p['name']); }),
                          ],
                        ),
                      ),
                    ),
                  ),
                )
              ],
            ),
          );
        },
      ),
    );
  }
}
