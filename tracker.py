import requests
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import os
import time
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv


# Initialize the config scanner
load_dotenv()

# Pull variables out of the hidden environment
sender = os.getenv("SENDER_EMAIL")
password = os.getenv("EMAIL_PASSWORD")
receiver = "your_hotmail_account@hotmail.com"  # Hardcode or pull from os.getenv("RECEIVER_EMAIL")

print(f"Environment Loaded! Script configured to send from: {sender}")

# --- Configuration Settings ---
ALERT_THRESHOLD = 75000.0  # Trigger an email alert if Bitcoin drops below this price
FETCH_INTERVAL = 300       # Time to wait between checks (300 seconds = 5 minutes)

# --- State Flag Tracker ---
# Tracks whether the user has already been emailed about a price drop
alert_already_sent = False

def send_email_alert(current_price):
    """Handles the secure connection and delivery of SMTP text emails."""
    msg = MIMEText(f"Alert! Bitcoin has dropped to ${current_price:.2f}, falling below your threshold of ${ALERT_THRESHOLD:.2f}.")
    msg['Subject'] = f"CRITICAL: Bitcoin Price Dip Alert (${current_price:.2f})"
    msg['From'] = sender
    msg['To'] = receiver

    try:
        # Standard Gmail SMTP secure configuration on port 587
        with smtplib.SMTP("://gmail.com", 587) as server:
            server.starttls()  # Upgrade connection to secure TLS encryption
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print(f"✈️ Email alert successfully dispatched to {receiver}!")
    except Exception as e:
        print(f"❌ Failed to deliver email alert. Error: {e}")


# ==========================================
# MAIN AUTOMATION CORE ENGINE
# ==========================================
print("\n🚀 Commencing automated tracker engine...")

while True:
    url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

    # Senior Dev Tip: Adding headers makes our script look like a genuine application
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Pinging API...")

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            price_str = data['data']['amount']
            price_float = float(price_str)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"🟢 Extracted Price: ${price_float:.2f}")
        
            # 1. Append data packet to local CSV spreadsheet
            with open("bitcoin_history.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, price_str])
            
            # 2. Smart Email Alert Logic Matrix
            if price_float < ALERT_THRESHOLD and not alert_already_sent:
                print("⚠️ Price drop detected below threshold! Commencing email dispatch...")
                send_email_alert(price_float)
                alert_already_sent = True  # Lock the gate so it doesn't spam you next loop
                
            elif price_float >= ALERT_THRESHOLD and alert_already_sent:
                print("🔄 Price recovered above threshold. Resetting alert gate triggers.")
                alert_already_sent = False  # Unlock the gate for future price drops


            # 3. Read history and draw the compiled chart
            timestamps = []
            prices = []

            with open("bitcoin_history.csv", mode="r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:
                        timestamps.append(row[0])
                        prices.append(float(row[1]))


            # Slice down to rolling 24 entry window
            recent_timestamps = timestamps[-24:]
            recent_prices = prices[-24:]

            plt.figure(figsize=(10, 5))
            plt.plot(recent_timestamps, recent_prices, marker='o', color='b', linestyle='-')
            plt.title("Bitcoin Price Trend (USD) - Last 24 Entries")
            plt.xlabel("Timestamp")
            plt.ylabel("Price ($)")
            plt.xticks(rotation=45) # Tilt the dates so they don't overlap
            plt.tight_layout()

            graph_filename = "bitcoin_trend.png"
            plt.savefig(graph_filename)
            plt.close()  # Vital step: clear memory buffer after saving static image
            print("📊 Trend visualization updated successfully.")
        else:
            print(f"🔴 API Warning: Server returned status code {response.status_code}")

    except Exception as e:
        print(f"❌ Main Loop Error Event: {e}")

    # Enter loop hibernation cycle
    print(f"💤 Sleeping for {FETCH_INTERVAL} seconds...")
    time.sleep(FETCH_INTERVAL)
