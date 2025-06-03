import multiprocessing
from bit import Key
import requests
import time
import datetime
import os
import psutil
from flask import Flask, send_from_directory
import threading

# --- Settings ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PORT = int(os.getenv("PORT", 1000))
START_TIME = time.time()

# --- Flask app for port 1000 and index.html ---
app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

def flask_thread():
    app.run(host='0.0.0.0', port=PORT)

# --- Send Telegram Message ---
def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[!] Telegram Send Error: {e}")

def edit_telegram_message(bot_token, chat_id, message_id, new_text):
    url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": new_text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[!] Telegram Edit Error: {e}")

# --- Load target addresses ---
def load_target_addresses(filename):
    with open(filename, 'r') as f:
        return set(line.strip() for line in f if line.strip())

# --- Generate different Bitcoin addresses ---
def generate_addresses(key):
    return [key.address, key.segwit_address]

# --- Worker to check keys ---
def worker(targets, queue, counter):
    while True:
        key = Key()
        for addr in generate_addresses(key):
            if addr in targets:
                queue.put(f"🎯 *Match Found!*\n\nAddress: `{addr}`\nKey: `{key.to_wif()}`")
        with counter.get_lock():
            counter.value += 1

# --- Listener for successful messages ---
def listener(queue, token, channel):
    while True:
        msg = queue.get()
        if msg == 'STOP':
            break
        send_telegram_message(token, channel, msg)

# --- Periodic report ---
def reporter(counter, token, channel):
    message_id = None
    first_time = True
    while True:
        time.sleep(600)
        count = counter.value
        uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        msg = f"🕒 *10-minute report*\n\n🔢 Addresses checked: `{count}`\n⏱ Uptime: `{uptime}`\n🖥 CPU: `{cpu}%`, RAM: `{ram}%`"
        if first_time:
            res = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": channel, "text": msg, "parse_mode": "Markdown"}
            )
            if res.ok:
                message_id = res.json().get("result", {}).get("message_id")
                first_time = False
        else:
            if message_id:
                edit_telegram_message(token, channel, message_id, msg)

# --- Start the program ---
if __name__ == '__main__':
    if not BOT_TOKEN or not CHANNEL_ID:
        print("[!] BOT_TOKEN or CHANNEL_ID is not set.")
        exit(1)

    send_telegram_message(BOT_TOKEN, CHANNEL_ID, "🚀 Bot is starting...")

    # Run Flask
    threading.Thread(target=flask_thread, daemon=True).start()

    # Load addresses
    targets = load_target_addresses('add.txt')
    queue = multiprocessing.Queue()
    counter = multiprocessing.Value('i', 0)

    # Start processes
    multiprocessing.Process(target=listener, args=(queue, BOT_TOKEN, CHANNEL_ID)).start()
    multiprocessing.Process(target=reporter, args=(counter, BOT_TOKEN, CHANNEL_ID)).start()

    for _ in range(multiprocessing.cpu_count() - 1):
        multiprocessing.Process(target=worker, args=(targets, queue, counter)).start()
