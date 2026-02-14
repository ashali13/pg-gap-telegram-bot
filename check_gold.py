import requests
import os
import re
import time

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
URL = "https://publicgold.com.my/index.php/liveprice.php"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        })
    except Exception as e:
        print(f"Failed to send Telegram: {e}")

def check_price():
    # Fetch the live price page
    try:
        html = requests.get(URL, timeout=20).text
    except Exception as e:
        print(f"Network error: {e}")
        return

    # Regex to find GAP 1g sell price
    pattern = r"(RM\s?\d+)\s?=\s?1\.0000\s?gram"
    match = re.search(pattern, html, re.IGNORECASE)

    if not match:
        print("Price not found on page.")
        return

    current_price_str = match.group(1).replace(" ", "")
    current_price = float(current_price_str.replace("RM", "").strip())

    # Read last price from file
    try:
        with open("last_price.txt", "r") as f:
            last_price_str = f.read().strip()
            last_price = float(last_price_str.replace("RM", "").strip())
    except FileNotFoundError:
        last_price = None

    # First run logic
    if last_price is None:
        with open("last_price.txt", "w") as f:
            f.write(current_price_str)
        print(f"Initialized last_price.txt with {current_price_str}")
        return

    # Calculate difference
    difference = round(current_price - last_price, 2)

    if difference == 0:
        print(f"Checked at {time.strftime('%H:%M:%S')}: No change (RM{current_price:.0f})")
        return

    change_amount = f"{abs(difference):.0f}"

    # Build Message
    status = "*NAIK*" if difference > 0 else "*TURUN*"
    message = (
        f"‼️‼️‼️PRICE UPDATED‼️‼️‼️\n\n"
        f"Harga emas GAP baru sahaja dikemaskini {status} sebanyak *RM{change_amount}* "
        f"daripada *RM{last_price:.0f}* kepada *{current_price_str}*"
    )

    send_telegram(message)

    # Save the current price for next run
    with open("last_price.txt", "w") as f:
        f.write(current_price_str)
    print(f"Price updated to {current_price_str}. Notification sent.")

# Main Loop
print("Starting price monitor (20s intervals)...")
while True:
    check_price()
    time.sleep(20)  #
