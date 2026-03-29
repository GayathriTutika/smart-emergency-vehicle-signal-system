import time
from datetime import datetime

import requests

API_URL = "http://127.0.0.1:5000/api/update-location"

demo_locations = [
    {"lat": 17.4015, "lon": 78.4680, "speed_kmph": 58},
    {"lat": 17.3978, "lon": 78.4716, "speed_kmph": 55},
    {"lat": 17.3949, "lon": 78.4738, "speed_kmph": 52},
    {"lat": 17.3928, "lon": 78.4749, "speed_kmph": 47},
    {"lat": 17.3922, "lon": 78.4753, "speed_kmph": 34},
]

print("Sending emergency vehicle GPS updates to cloud server every 5 seconds...")

for location in demo_locations:
    payload = {
        "vehicle_id": "AMB-108",
        "vehicle_type": "ambulance",
        "lat": location["lat"],
        "lon": location["lon"],
        "speed_kmph": location["speed_kmph"],
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

    response = requests.post(API_URL, json=payload, timeout=10)
    data = response.json()

    print("-" * 60)
    print(f"Vehicle: {payload['vehicle_type']} {payload['vehicle_id']}")
    print(f"Location sent: {payload['lat']}, {payload['lon']}")
    print(f"Nearest signal: {data['decision']['target_signal_name']}")
    print(f"Distance: {data['decision']['distance_m']} meters")
    print(f"Command: {data['decision']['command']}")
    print(f"Hardware status: {data['decision']['hardware_status']}")

    time.sleep(5)
