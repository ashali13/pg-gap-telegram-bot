import requests
import os
import re

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://publicgold.com.my/index.php/liveprice.php"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# Fetch the live price page
html = requests.get(URL, timeout=20).text

# Regex to find GAP 1g sell price (RMxxx = 1.0000 gram)
pattern = r"(RM\s?\d+)\s?=\s?1\.0000\s?gram"
match = re.search(pattern, html, re.IGNORECASE)

if not match:
    print("Price not found on page.")
    exit()

current_price_str = match.group(1)  # e.g., RM648
current_price = float(current_price_str.replace("RM", "").strip())

# Read last price from file
try:
    with open("last_price.txt", "r") as f:
        last_price_str = f.read().strip()
        last_price = float(last_price_str.replace("RM", "").strip())
except FileNotFoundError:
    last_price = None

# If first run, just save price
if last_price is None:
    with open("last_price.txt", "w") as f:
        f.write(current_price_str)
    print(f"First run: last_price.txt created with {current_price_str}")
    exit()

# Calculate difference
difference = round(current_price - last_price, 2)

if difference == 0:
    print("No change in price.")
    exit()

change_amount = f"{abs(difference):.0f}"

# Build Telegram message
if difference > 0:
    message = (
        f"‼️‼️‼️PRICE UPDATED‼️‼️‼️\n\n"
        f"Harga emas GAP baru sahaja naik sebanyak RM{change_amount} "
        f"daripada RM{last_price:.0f} kepada {current_price_str}"
    )
else:
    message = (
        f"‼️‼️‼️PRICE UPDATED‼️‼️‼️\n\n"
        f"Harga emas GAP baru sahaja turun sebanyak RM{change_amount} "
        f"daripada RM{last_price:.0f} kepada {current_price_str}"
    )

send_telegram(message)

# Save the current price for next run
with open("last_price.txt", "w") as f:
    f.write(current_price_str)

print("Telegram message sent successfully.")
