
---

# 🚀 Bitcoin check address Bot

A high-performance tool for **random Bitcoin private key scanning** with automatic matching against a target address list (`add.txt`).  
If a match is found, the bot instantly sends the **private key** and **address** to your Telegram channel!

---

## 🛠 Features

- 🔑 Generates Bitcoin addresses (Legacy - P2PKH and SegWit - Bech32) from random private keys  
- 🎯 Checks generated addresses against a target list (`add.txt`)  
- 📲 Sends instant notifications to your Telegram channel upon match  
- 📊 Sends periodic 10-minute reports on keys scanned, uptime, CPU & RAM usage  
- 🌐 Serves a simple web interface on port 1000 (optimized for Render.com deployment)  

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+  
- Telegram Bot Token and Channel ID  

### Installation

1. Clone this repo or download the files  
2. Install dependencies:

```bash
pip install -r requirements.txt

3. Setup environment variables (recommended using .env or platform env settings):



export BOT_TOKEN="your_bot_token_here"
export CHANNEL_ID="@yourchannelusername"
export PORT=1000

4. Add your target Bitcoin addresses (one per line) to add.txt


5. Run the bot:



python main.py


---

📁 Project Structure

project/
│
├── add.txt              # Target Bitcoin addresses
├── main.py              # Main bot script
├── requirements.txt     # Python dependencies
├── static/
│   └── index.html       # Simple web interface
└── README.md            # This file


---

💡 Notes

This tool prioritizes speed over security — do NOT use this for real wallets!

Keep the target address list size moderate to avoid high RAM usage.

The bot automatically updates reports every 10 minutes in Telegram.



---

🤝 Support & Donate

If you find this project useful, consider supporting it! 🙏

BTC: bc1qxyzxyzxyzxyzxyzxyzxyzxyzxyzxyzxyz

ETH: 0x1234567890abcdef1234567890abcdef12345678


Thank you for your kindness! ❤️


---

📜 License

MIT License © 2025


---

Made with ❤️ by 𝕚𝕞_𝕒𝕓𝕚🌙

--
