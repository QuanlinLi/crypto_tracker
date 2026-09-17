import requests
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv


# Initialize the config scanner
load_dotenv()

# Pull variables out of the hidden environment
sender = os.getenv("SENDER_EMAIL")
password = os.getenv("EMAIL_PASSWORD")

print(f"Environment Loaded! Script configured to send from: {sender}")



url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

# Senior Dev Tip: Adding headers makes our script look like a genuine application
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json"
}

print("Sending request with professional headers...")
response = requests.get(url, headers=headers)

print(f"Server responded with Status Code: {response.status_code}")

# Let's inspect exactly what text the server is feeding us
print(f"Raw snippet from server: {response.text[:100]}")



try:
    data = response.json()
    print("\n--- Success! Data Parsed Perfectly ---")
    
    # 1. Drill down into the dictionary to grab just the price string
    price = data['data']['amount']
    
    # 2. Generate a clean timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Extracted Price: ${price} at {timestamp}")
    
    # 3. Append this data to a local spreadsheet file
    # 'a' means append (add to the end without deleting old data)
    # newline='' prevents blank rows on certain operating systems
    with open("bitcoin_history.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        
        # Write our data packet as a row: [Time, Price]
        writer.writerow([timestamp, price])
        
    print("Successfully saved data packet to bitcoin_history.csv!")

except Exception as e:
    print(f"\n--- Could not parse or save data. Error: {e} ---")



print("\n--- Generating Price Report ---")

timestamps = []
prices = []

# Step A: Read the historical spreadsheet
try:
    with open("bitcoin_history.csv", mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row: # Skip empty rows if any
                timestamps.append(row[0])
                # Senior Dev Hint: CSV data reads as text/strings. 
                # We must convert the price into a decimal (float) so the math engine can graph it!
                prices.append(float(row[1]))

    print(f"Loaded {len(prices)} data entries from file.")

    # Step B: Let Matplotlib draw a line graph
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, prices, marker='o', color='b', linestyle='-')
    plt.title("Bitcoin Price Trend (USD)")
    plt.xlabel("Timestamp")
    plt.ylabel("Price ($)")
    plt.xticks(rotation=45) # Tilt the dates so they don't overlap
    plt.tight_layout()

    # Step C: Save the graph as an image asset
    graph_filename = "bitcoin_trend.png"
    plt.savefig(graph_filename)
    print(f"Graph image successfully compiled and saved as: {graph_filename}")

except Exception as e:
    print(f"Failed to generate visualization. Error: {e}")
