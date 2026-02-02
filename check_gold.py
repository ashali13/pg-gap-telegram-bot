import requests
import os
import re

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://www.publicgold.com.my/"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

html = requests.get(URL, timeout=20).text

# Find GAP 1g sell price
pattern = r"(RM\s?\d+)\s?=\s?1\.0000\s?gram"
match = re.search(pattern, html, re.IGNORECASE)

if not match:
    exit()

current_price_str = match.group(1)  # e.g. RM648
current_price = float(current_price_str.replace("RM", "").strip())

# Read last price
try:
    with open("last_price.txt", "r") as f:
        last_price_str = f.read().strip()
        last_price = float(last_price_str.replace("RM", "").strip())
except:
    last_price = None

# First run (no previous price)
if last_price is None:
    send_telegram(f"Harga emas GAP 1g kini {current_price_str}")
    with open("last_price.txt", "w") as f:
        f.write(current_price_str)
    exit()

# Calculate change
difference = round(current_price - last_price, 2)

if difference == 0:
    exit()

change_amount = f"RM{abs(difference):.0f}"

# 📈 Increase
if difference > 0:
    message = (
        f"‼️‼️‼️PRICE UPDATED‼️‼️‼️
        
        Harga emas GAP baru sahaja naik sebanyak RM{change_amount} "
        f"daripada RM{last_price:.0f} kepada RM{current_price:.0f}"
    )

# 📉 Decrease
else:
    message = (
        f"‼️‼️‼️PRICE UPDATED‼️‼️‼️
        
        Harga emas GAP baru sahaja turun sebanyak RM{change_amount} "
        f"daripada RM{last_price:.0f} kepada RM{current_price:.0f}"
    )

send_telegram(message)

with open("last_price.txt", "w") as f:
    f.write(current_price_str)
