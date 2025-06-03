
---

🚀 Bitcoin Check Address Bot

A high-performance tool for random Bitcoin private key scanning, automatically matching generated addresses against a target list (add.txt).
On a match, the bot instantly sends the private key and address to your Telegram channel!


---

🛠 Features

🔑 Generates Bitcoin addresses (Legacy - P2PKH & SegWit - Bech32) from random private keys

🎯 Checks generated addresses against a target list (add.txt)

📲 Sends instant notifications to your Telegram channel upon a match

📊 Sends periodic 10-minute reports with stats: keys scanned, uptime, CPU & RAM usage

🌐 Provides a simple web interface on port 1000 (optimized for deployment on Render.com)



---

🚀 Getting Started

Prerequisites

Python 3.8 or higher

Telegram Bot Token and Channel ID


Installation

1. Clone the repository or download the files:

git clone https://github.com/im-mcm/bitcoin-check-address-bot.git
cd bitcoin-check-address-bot


2. Install dependencies:

pip install -r requirements.txt


3. Set up environment variables (recommended via .env file or your deployment platform settings):

export BOT_TOKEN="your_bot_token_here"
export CHANNEL_ID="@yourchannelusername"
export PORT=1000


4. Add your target Bitcoin addresses (one per line) to add.txt


5. Run the bot:

python bot.py




---

📁 Project Structure

project/
│
├── add.txt              # List of target Bitcoin addresses
├── main.py              # Main bot script
├── requirements.txt     # Python dependencies
├── static/
│   └── index.html       # Simple web interface
└── README.md            # This documentation file


---

💡 Notes

This tool prioritizes speed over security — do NOT use for real wallets!

Keep the target address list size moderate to avoid high memory usage.

Reports are automatically updated and sent every 10 minutes on Telegram.



---

🤝 Support & Donate

If you find this project useful, please consider supporting it! 🙏

BTC: bc1qxyzxyzxyzxyzxyzxyzxyzxyzxyzxyzxyz

ETH: 0x1234567890abcdef1234567890abcdef12345678


Thank you for your kindness! ❤️


---

📜 License

MIT License © 2025


---

Made with ❤️ by 𝕚𝕞_𝕒𝕓𝕚🌙


--
