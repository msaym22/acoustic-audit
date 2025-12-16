import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:sound_stream/sound_stream.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:quran/quran.dart' as quran;
import 'package:audioplayers/audioplayers.dart';

void main() {
  runApp(const QuranAIApp());
}

class QuranAIApp extends StatelessWidget {
  const QuranAIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.teal),
      home: const ReciteScreen(),
    );
  }
}

class ReciteScreen extends StatefulWidget {
  const ReciteScreen({super.key});

  @override
  State<ReciteScreen> createState() => _ReciteScreenState();
}

class _ReciteScreenState extends State<ReciteScreen> {
  // --- CONNECTION SETTINGS ---
  // If using Android Emulator, use '10.0.2.2'. 
  // If using Real Phone, use your PC's IP address (e.g., '192.168.1.5')
  final TextEditingController _ipController = TextEditingController(text: "192.168.1.X"); 
  
  final RecorderStream _recorder = RecorderStream();
  WebSocketChannel? _channel;
  StreamSubscription? _audioSubscription;
  final AudioPlayer _audioPlayer = AudioPlayer();

  bool _isConnected = false;
  String _statusText = "Not Connected";
  int _currentSurah = 1; // Default: Al-Fatiha
  String _fullSurahText = "";
  
  // MISTAKE LOGIC
  List<int> _mistakeIndices = []; // Characters to highlight RED
  String _feedbackMode = "highlight"; // Options: highlight, beep, strict

  @override
  void initState() {
    super.initState();
    _initRecorder();
    _loadSurahText();
  }

  Future<void> _initRecorder() async {
    await _recorder.initialize();
  }

  void _loadSurahText() {
    String text = "";
    int count = quran.getVerseCount(_currentSurah);
    for (int i = 1; i <= count; i++) {
      text += "${quran.getVerse(_currentSurah, i)} ";
    }
    setState(() {
      _fullSurahText = text;
    });
  }

  // --- CONNECT & START LISTENING ---
  Future<void> _toggleConnection() async {
    if (_isConnected) {
      _disconnect();
    } else {
      await _connect();
    }
  }

  Future<void> _connect() async {
    // 1. Permission Check
    var status = await Permission.microphone.request();
    if (status != PermissionStatus.granted) {
      setState(() => _statusText = "Mic Permission Denied");
      return;
    }

    try {
      setState(() => _statusText = "Connecting...");
      
      // 2. Open WebSocket
      final wsUrl = Uri.parse("ws://${_ipController.text}:8000/ws/recite");
      _channel = WebSocketChannel.connect(wsUrl);
      await _channel!.ready;

      // 3. Send Config
      _channel!.sink.add(jsonEncode({"mode": _feedbackMode}));

      // 4. Listen to Server Responses
      _channel!.stream.listen((message) {
        _handleServerMessage(message);
      }, onError: (error) {
        _disconnect();
        setState(() => _statusText = "Connection Error: $error");
      }, onDone: () {
        _disconnect();
        setState(() => _statusText = "Disconnected by Server");
      });

      // 5. Start Audio Stream
      _audioSubscription = _recorder.audioStream.listen((data) {
        if (_channel != null) {
          _channel!.sink.add(data);
        }
      });
      await _recorder.start();

      setState(() {
        _isConnected = true;
        _statusText = "Listening... (Start Reciting Anywhere)";
      });

    } catch (e) {
      setState(() => _statusText = "Failed: $e");
    }
  }

  void _disconnect() async {
    await _recorder.stop();
    _audioSubscription?.cancel();
    _channel?.sink.close();
    setState(() {
      _isConnected = false;
      _statusText = "Stopped";
    });
  }

  // --- HANDLE AI FEEDBACK ---
  void _handleServerMessage(dynamic message) {
    final data = jsonDecode(message);
    
    if (data['type'] == 'info') {
      setState(() => _statusText = data['message']);
    } 
    else if (data['type'] == 'mistake') {
      // Logic: Highlight the mistake
      setState(() {
        _mistakeIndices.add(data['index']);
        _statusText = "Mistake Detected!";
      });

      // Logic: Beep if enabled
      if (data['action'] == 'beep') {
         _audioPlayer.play(AssetSource('beep.mp3')); // Make sure to add beep.mp3 to assets
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Quran AI Evaluator")),
      body: Column(
        children: [
          // IP Address Input (Vital for connecting to your PC)
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _ipController,
              decoration: const InputDecoration(
                labelText: "Server IP (e.g., 192.168.1.5)",
                border: OutlineInputBorder(),
              ),
            ),
          ),
          
          // Status Bar
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            color: _isConnected ? Colors.green[100] : Colors.grey[200],
            child: Text(
              _statusText, 
              textAlign: TextAlign.center,
              style: TextStyle(fontWeight: FontWeight.bold, color: _isConnected ? Colors.green[800] : Colors.black),
            ),
          ),

          // Quran Display
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: RichText(
                textDirection: TextDirection.rtl,
                text: _buildQuranText(),
              ),
            ),
          ),

          // Control Button
          Padding(
            padding: const EdgeInsets.all(20),
            child: FloatingActionButton.extended(
              onPressed: _toggleConnection,
              backgroundColor: _isConnected ? Colors.red : Colors.teal,
              icon: Icon(_isConnected ? Icons.stop : Icons.mic),
              label: Text(_isConnected ? "Stop Session" : "Start Listening"),
            ),
          ),
        ],
      ),
    );
  }

  TextSpan _buildQuranText() {
    List<TextSpan> spans = [];
    // Simple logic: If index is in mistake list, color Red.
    for (int i = 0; i < _fullSurahText.length; i++) {
      bool isError = _mistakeIndices.contains(i);
      spans.add(TextSpan(
        text: _fullSurahText[i],
        style: TextStyle(
          fontFamily: "Amiri", // Standard Arabic Font
          fontSize: 28,
          color: isError ? Colors.red : Colors.black,
          backgroundColor: isError ? Colors.yellow[200] : null,
        ),
      ));
    }
    return TextSpan(children: spans);
  }
}