# 🚀 Blockchain Chat  
*The future of messaging — decentralized, offline, and secure.*  

![Made with Blockchain Vibes](https://img.shields.io/badge/decentralized-🚀-blue) ![MIT License](https://img.shields.io/badge/license-MIT-green)

## 🔮 What It Is  
Blockchain Chat turns nearby devices into a secure, self-healing messaging network—no central servers, no corporate eavesdropping, just peer-to-peer trust. Built with blockchain-backed immutability, Bluetooth mesh for offline reach, and wallet-based identity.

## ✨ Core Pillars of Trust & Functionality

- 🔐 **Security & Privacy**  
  End-to-end encryption + on-device blockchain ensures messages are tamper-proof and private.

- 📱 **Offline Mesh Networking**  
  Communicate over Bluetooth Low Energy (BLE) with automatic multi-hop relay when direct reach fails.

- 🎨 **UX That Doesn’t Suck**  
  Clean interfaces, QR key pairing, status indicators—secure messaging made frictionless.

## 🛠️ Tech Stack Snapshot  
The app blends real-time local communication with cryptographic integrity:

- **Python & Asyncio** – async core for non-blocking device I/O  
- **Kivy** – cross-platform frontend/UI  
- **Bleak** – BLE scanning, discovery, and mesh communication  
- **Custom Blockchain Layer** – per-device chain for signed & encrypted messages  
- **Cryptography** – key exchange, message signing, and encryption  

*(In the web UI version, this is visualized as a doughnut chart showing relative components.)*

## 🧠 How It Works

1. **Device Discovery**  
   Devices scan nearby via BLE and detect running instances.

2. **Secure Pairing**  
   Public keys are exchanged through QR codes to bootstrap encrypted sessions.

3. **Blockchain Messaging**  
   Messages are signed, encrypted, and appended to a local distributed blockchain for auditability and integrity.

4. **Mesh Routing**  
   If a recipient is out of range, trusted intermediate nodes securely forward messages.

## 🚧 Roadmap / Next-Level Moves

- ✅ Complete File Sharing  
- 🔊 Voice & Video Messaging over mesh  
- 🤝 Smart Contracts (scheduled messages, on-chain triggers)  
- 💼 Wallet Integration (crypto inside chat)  
- 🌙 Dark Mode, search, backup/restore  

## 🚀 Getting Started

### Prerequisites
- Python 3.x  
- BLE-capable hardware  
- Wallet identity system (e.g., wallet address for identity)  
- Optional: local test blockchain if integrating on-chain logic

## 🤝 Contributing  
This is open source and hype-ready — collabs welcome.  

1. **Fork** the repo  
2. **Create** a feature branch: `feature/your-idea`  
3. **Code**, **test**, **commit**  
4. **Open** a PR with what you added/fixed  
5. We’ll review and merge — let’s build something decentralized and dope 🚀  

### 💡 Cool Contribution Ideas  
- Add encrypted media/image transfer (IPFS hybrid)  
- ENS/DID identity overlays  
- Group threads, offline sync resilience  
- UI polish or mobile-friendly port  

---

## 📦 Example Features You Can Add  
- Message encryption layers (e.g., hybrid symmetric/asymmetric)  
- QR-based trust bootstrap UI  
- Local chain explorers for debugging message history  
- Offline-first UI state persistence  

---

## 👥 Community & Support  
Open an issue, drop a feature request, or submit a PR. This is a growth playground — if you’ve got ideas, we’re here for it.  

---

## 🧰 Maintainer  
**Priyanshu Kumar** (_virusinlinux_) — builder, security enthusiast, and blockchain tinkerer.  

---

## 📜 License  
MIT License — do your thing, just keep it open source.  


### Quickstart (example)
```bash
# Clone
git clone https://github.com/virusinlinux/Blockchain-Chat.git
cd Blockchain-Chat

# Install deps (adjust to actual requirements file)
pip install -r requirements.txt

# Run locally (assumes Bluetooth and environment configured)
python main.py


