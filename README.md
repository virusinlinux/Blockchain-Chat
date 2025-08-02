Blockchain Chat: Decentralized Bluetooth Messaging
Overview
Blockchain Chat is a revolutionary decentralized messaging application that leverages blockchain technology and Bluetooth Low Energy (BLE) to enable secure, serverless communication between devices without an internet connection. Built with Python and Kivy, this app creates a mesh network where messages are stored in an immutable blockchain, ensuring tamper-proof communication with end-to-end encryption.

🌟 Key Features
🔐 Security & Privacy
End-to-End Encryption: All messages are encrypted using RSA/AES hybrid encryption.

Blockchain Verification: Each message is stored as a block in a blockchain, ensuring integrity.

Decentralized Identity: Unique device IDs with public key cryptography for secure authentication.

Disappearing Messages: Self-destructing messages with customizable timers.

📱 Core Functionality
Bluetooth Mesh Networking: Device-to-device communication without the internet.

Offline Messaging: Store-and-forward functionality for delayed message delivery.

Group Chat: Create and join groups for multi-device communication.

File Sharing: Send images and files between connected devices.

Favorites System: Mark frequently contacted devices for quick access.

🎨 User Experience
Intuitive UI: Clean, modern interface with smooth animations.

Cross-Platform: Works on Windows, Android, and other supported platforms.

Onboarding Tutorial: A friendly setup wizard for new users.

QR Code Pairing: Secure device pairing using QR codes.

Real-time Status: Live connection status and message delivery indicators.

🛠 Technology Stack
Frontend: Kivy (Python UI framework)

Backend: Python with asyncio for asynchronous operations

Bluetooth: Bleak library for cross-platform BLE communication

Cryptography: Cryptography library for encryption and digital signatures

Blockchain: Custom blockchain implementation for message integrity

Storage: JSONStore for local data persistence

QR Codes: qrcode library for device pairing

📦 Installation & Setup
Prerequisites
Python 3.8 or higher

A Bluetooth-capable device

Required permissions for Bluetooth access

Install Dependencies
Bash

pip install kivy bleak cryptography qrcode[pil]
Run the Application
Bash

git clone https://github.com/yourusername/blockchain-chat.git
cd blockchain-chat
python main.py
For Android Deployment
Install Buildozer:

Bash

pip install buildozer
Initialize Buildozer:

Bash

buildozer init
Configure buildozer.spec (see example in the repository).

Build APK:

Bash

buildozer -v android debug
Install on Android device:

Bash

buildozer android deploy
🚀 How It Works
Device Discovery: The app scans for nearby devices running Blockchain Chat.

Secure Pairing: Devices exchange public keys for encrypted communication.

Blockchain Messaging: Messages are stored as blocks in a distributed blockchain.

Mesh Networking: Messages can hop between devices to reach recipients out of range.

End-to-End Encryption: All communication is encrypted using hybrid RSA/AES encryption.

📁 Project Structure
blockchain-chat/
├── main.py                 # Main application entry point
├── blockchain_chat.json    # Local storage for contacts and groups
├── buildozer.spec         # Buildozer configuration for Android
├── assets/                 # Images and resources (if any)
├── README.md              # This file
└── LICENSE                # MIT License
📱 Screenshots
Main Chat Interface	Device Discovery	Settings Screen

Export to Sheets
Note: The images above are placeholders. Replace them with actual screenshots of your application.

🔮 Future Enhancements
Complete file sharing implementation

Voice and video messaging

Blockchain-based smart contracts for advanced features

Wallet integration for cryptocurrency transactions

Enhanced group management features

Dark mode implementation

Message search functionality

Backup and restore for chat history

🤝 Contributing
We welcome contributions to improve Blockchain Chat! Please follow these steps:

Fork the repository.

Create a feature branch (git checkout -b feature/amazing-feature).

Commit your changes (git commit -m 'Add amazing feature').

Push to the branch (git push origin feature/amazing-feature).

Open a Pull Request.

Development Guidelines
Follow PEP 8 style guidelines.

Add comments for complex functionality.

Write unit tests for new features.

Update documentation as needed.

📄 License
This project is licensed under the MIT License—see the LICENSE file for details.

🙏 Acknowledgments
Inspired by decentralized messaging concepts from BitChat and Secretum.

Built with open-source libraries: Kivy, Bleak, Cryptography, and QRCode.

Thanks to all contributors who have helped improve this project.

📞 Support
If you encounter any issues or have questions, please:

Check the Issues page.

Create a new issue with detailed information.

Join our community discussions.
