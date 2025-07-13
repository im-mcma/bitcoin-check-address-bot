import threading
from bit import Key
import requests
import time
import datetime
import os
import psutil
from flask import Flask, send_from_directory, jsonify
import signal
import sys
import queue

# --- Settings ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PORT = int(os.getenv("PORT", 10000))
START_TIME = time.time()

# Counters for stats
stats = {
    "scans_done": 0,
    "successes": 0,
    "errors": 0,
}
stats_lock = threading.Lock()

# --- Flask app ---
app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/stats')
def api_stats():
    with stats_lock:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        uptime_sec = int(time.time() - START_TIME)
        uptime_str = str(datetime.timedelta(seconds=uptime_sec))
        data = {
            "scans_done": stats["scans_done"],
            "successes": stats["successes"],
            "errors": stats["errors"],
            "cpu": cpu,
            "ram": ram,
            "uptime": uptime_str,
        }
    return jsonify(data)

def flask_thread():
    app.run(host='0.0.0.0', port=PORT)

# --- Telegram messaging with retry ---
def send_telegram_message(bot_token, chat_id, message, retries=5):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    for i in range(retries):
        try:
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code == 200:
                return True
            else:
                print(f"[!] Telegram Send failed {res.status_code}: {res.text} - Message: {message}")
        except Exception as e:
            print(f"[!] Telegram Send Exception: {e}")
        time.sleep(2 ** i)
    return False

# --- Load target addresses ---
def load_target_addresses(filename):
    with open(filename, 'r') as f:
        return set(line.strip() for line in f if line.strip())

# --- Generate only 1 and bc1 addresses ---
def generate_addresses(key):
    addresses = [key.address, key.segwit_address]
    return [addr for addr in addresses if addr.startswith('1') or addr.startswith('bc1')]

# --- Format Match Found message ---
def format_match_message(address, private_key):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return (
        f"🚨 *MATCH FOUND!* 🚨\n\n"
        f"🔑 *Address:*  \n`{address}`\n\n"
        f"🔐 *Private Key (WIF):*  \n`{private_key}`\n\n"
        f"⚠️ **لطفاً کلید خصوصی را با دقت نگهداری کنید و آن را به کسی ندهید!**\n\n"
        f"---\n\n"
        f"⏰ _زمان یافتن:_ {now}\n\n"
        f"🔗 [بررسی تراکنش‌ها](https://www.blockchain.com/btc/address/{address})"
    )

# --- Format 6-hour report message ---
def format_report_message(count, uptime, cpu, ram):
    thread_count = threading.active_count()
    return (
        f"🕒 *6-hour Report*\n\n"
        f"🔢 *Addresses Checked:* `{count}`\n"
        f"⏱ *Uptime:* `{uptime}`\n"
        f"🖥 *CPU Usage:* `{cpu}%`\n"
        f"💾 *RAM Usage:* `{ram}%`\n"
        f"🔄 *Active Threads:* `{thread_count}`"
    )

# --- Worker thread to check keys ---
def worker_thread(targets, queue):
    while True:
        key = Key()
        addrs = generate_addresses(key)
        with stats_lock:
            stats["scans_done"] += 1
        found_match = False
        for addr in addrs:
            if addr in targets:
                found_match = True
                print(f"[MATCH] {addr}")
                queue.put(format_match_message(addr, key.to_wif()))
        if found_match:
            with stats_lock:
                stats["successes"] += 1

# --- Listener thread for matches ---
def listener_thread(queue, token, channel):
    while True:
        try:
            msg = queue.get()
            if msg == 'STOP':
                break
            success = send_telegram_message(token, channel, msg)
            if not success:
                with stats_lock:
                    stats["errors"] += 1
        except Exception as e:
            print(f"[Listener Exception] {e}")
            with stats_lock:
                stats["errors"] += 1

# --- Periodic report to Telegram ---
def reporter_thread(counter, token, channel):
    while True:
        time.sleep(21600)  # 6 ساعت
        with stats_lock:
            count = stats["scans_done"]
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
        msg = format_report_message(count, uptime, cpu, ram)
        send_telegram_message(token, channel, msg)

# --- Signal handler ---
def signal_handler(sig, frame):
    print("[!] Signal received, shutting down...")
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if not BOT_TOKEN or not CHANNEL_ID:
        print("[!] BOT_TOKEN or CHANNEL_ID is not set.")
        sys.exit(1)

    send_telegram_message(BOT_TOKEN, CHANNEL_ID, "🚀 Bot is starting...")

    threading.Thread(target=flask_thread, daemon=True).start()

    targets = load_target_addresses('add.txt')
    print(f"[+] Loaded {len(targets)} target addresses.")

    q = queue.Queue()

    threading.Thread(target=listener_thread, args=(q, BOT_TOKEN, CHANNEL_ID), daemon=True).start()
    threading.Thread(target=reporter_thread, args=(None, BOT_TOKEN, CHANNEL_ID), daemon=True).start()

    num_workers = max(1, os.cpu_count() - 1)
    for _ in range(num_workers):
        threading.Thread(target=worker_thread, args=(targets, q), daemon=True).start()

    while True:
        time.sleep(60)
