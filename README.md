# 🎮 Dev Console

> **A Premium Real-Time Multiplayer Web Gaming & TV Console Platform**

Dev Console transforms any PC or Smart TV display into a multiplayer party console, enabling players to join seamlessly from their mobile phones as responsive gamepads using QR codes or room codes.

---

## 🌟 Included Games

### 1. ⚽ DevGoal!
- **Genre**: 3D Fast-Paced Arcade Football
- **Engine**: Three.js (WebGL), Procedural Stadium Shader Engine
- **Features**:
  - Full-field customizable mowing stripes and grass shaders
  - Multi-touch mobile controller with analog virtual joystick, charged shot mechanics, slide tackles, and sprint dashes
  - Goal net physics detection, dynamic camera tracking, player offscreen chevrons, and celebratory fireworks

### 2. 🚀 Spacess
- **Genre**: 2D Sci-Fi Cosmic Table Tennis Arcade (2 to 6 Players)
- **Engine**: HTML5 Canvas 2D Engine with procedural starfields & plasma physics
- **Features**:
  - Alien Saucer UFO Spaceships with dynamic team orientation
  - 3-Player Solo Giant Spaceship auto-balancing (double size & shield aura for solo player against 2 opponents)
  - Plasma ball rallies with deflection physics and random horizontal serves
  - Goal line scoring and celebration banners

---

## ✨ Console & Platform Features

- 📱 **Seamless Multi-Device Architecture**: Dual-mode Web interface (TV / Main Screen display mode + Mobile Phone Controller mode).
- 📡 **Real-Time Low Latency Networking**: Powered by Flask-SocketIO and WebSocket events.
- 🎛️ **Universal TV Remote & Keyboard Controls**: Navigate menus using WASD / Arrow keys on PC or the built-in Mobile D-Pad Remote.
- 🎨 **In-Game Shaders & Atmosphere Customization**: Real-time grass color pickers, sky domes, lighting intensity, and pattern controls.
- 🔄 **Auto-Balancing Teams & Player Management**: Automatic team distribution and admin player kick/pause controls.
- 🔊 **Web Audio Synthesizer**: Custom sound engine with kicks, passes, whistles, and goal anthems.

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.9+
- Modern Web Browser (Chrome, Edge, Safari, Firefox)

### Installation

1. **Clone the repository**:
   `ash
   git clone https://github.com/<your-username>/Dev-Console.git
   cd Dev-Console
   `

2. **Install dependencies**:
   `ash
   pip install -r requirements.txt
   `

3. **Start the server**:
   `ash
   python app.py
   `

4. **Connect & Play**:
   - **Main Display**: Open http://localhost:5000 on your PC or TV browser and choose **TV / MAIN SCREEN**.
   - **Players / Controllers**: Scan the QR code or visit http://<your-local-ip>:5000 on mobile devices and enter the 3-digit room code!

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Flask-SocketIO, Eventlet
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **3D Graphics & Physics**: Three.js (r128), GLTFLoader, SkeletonUtils
- **Audio**: Web Audio API (Procedural Synthesizer)

---

## 👨‍💻 Author

Developed by **SwarajDev**
