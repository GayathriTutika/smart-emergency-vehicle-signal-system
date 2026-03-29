from datetime import datetime
import math

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

PRIORITY_RADIUS_METERS = 1000

TRAFFIC_SIGNALS = [
    {
        "id": "SIG-101",
        "name": "City Hospital Junction",
        "lat": 17.3855,
        "lon": 78.4870,
    },
    {
        "id": "SIG-102",
        "name": "Tank Bund Signal",
        "lat": 17.3921,
        "lon": 78.4754,
    },
    {
        "id": "SIG-103",
        "name": "Panjagutta Main Signal",
        "lat": 17.4308,
        "lon": 78.4501,
    },
    {
        "id": "SIG-104",
        "name": "Ameerpet Metro Junction",
        "lat": 17.4374,
        "lon": 78.4482,
    },
]

dashboard_state = {
    "system_mode": "monitoring",
    "last_update": None,
    "message": "Waiting for emergency vehicle GPS updates.",
    "vehicle": {
        "id": "AMB-01",
        "type": "ambulance",
        "lat": None,
        "lon": None,
        "speed_kmph": None,
        "timestamp": None,
    },
    "decision": {
        "priority_active": False,
        "target_signal_id": None,
        "target_signal_name": None,
        "distance_m": None,
        "lane": None,
        "command": "NO_ACTION",
        "hardware_status": "Awaiting GPS updates",
    },
    "signals": [],
}


def haversine_distance(lat1, lon1, lat2, lon2):
    radius = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def detect_lane(vehicle_lat, vehicle_lon, signal):
    lat_gap = vehicle_lat - signal["lat"]
    lon_gap = vehicle_lon - signal["lon"]

    if abs(lat_gap) >= abs(lon_gap):
        return "north" if lat_gap > 0 else "south"
    return "east" if lon_gap > 0 else "west"


def calculate_signal_distances(vehicle_lat, vehicle_lon):
    signal_distances = []

    for signal in TRAFFIC_SIGNALS:
        distance = haversine_distance(
            vehicle_lat,
            vehicle_lon,
            signal["lat"],
            signal["lon"],
        )
        signal_distances.append(
            {
                "id": signal["id"],
                "name": signal["name"],
                "lat": signal["lat"],
                "lon": signal["lon"],
                "distance_m": round(distance, 2),
            }
        )

    return sorted(signal_distances, key=lambda item: item["distance_m"])


def build_decision(vehicle_lat, vehicle_lon, signal_distances):
    nearest_signal = signal_distances[0]

    if nearest_signal["distance_m"] <= PRIORITY_RADIUS_METERS:
        signal = next(
            item for item in TRAFFIC_SIGNALS if item["id"] == nearest_signal["id"]
        )
        lane = detect_lane(vehicle_lat, vehicle_lon, signal)
        return {
            "priority_active": True,
            "target_signal_id": nearest_signal["id"],
            "target_signal_name": nearest_signal["name"],
            "distance_m": nearest_signal["distance_m"],
            "lane": lane,
            "command": f"SET_PRIORITY:{nearest_signal['id']}:{lane.upper()}",
            "hardware_status": "Command ready for controller box execution",
        }

    return {
        "priority_active": False,
        "target_signal_id": nearest_signal["id"],
        "target_signal_name": nearest_signal["name"],
        "distance_m": nearest_signal["distance_m"],
        "lane": None,
        "command": "NO_ACTION",
        "hardware_status": "Vehicle not within 1 km priority radius",
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/state", methods=["GET"])
def get_state():
    return jsonify(dashboard_state)


@app.route("/api/signals", methods=["GET"])
def get_signals():
    return jsonify({"signals": TRAFFIC_SIGNALS})


@app.route("/api/update-location", methods=["POST"])
def update_location():
    data = request.get_json(silent=True) or {}
    vehicle_id = data.get("vehicle_id", "AMB-01")
    vehicle_type = data.get("vehicle_type", "ambulance")
    vehicle_lat = data.get("lat")
    vehicle_lon = data.get("lon")
    speed_kmph = data.get("speed_kmph", 45)
    timestamp = data.get("timestamp") or datetime.now().isoformat(timespec="seconds")

    if vehicle_lat is None or vehicle_lon is None:
        return jsonify({"error": "lat and lon are required"}), 400

    signal_distances = calculate_signal_distances(vehicle_lat, vehicle_lon)
    decision = build_decision(vehicle_lat, vehicle_lon, signal_distances)
    system_mode = "priority_active" if decision["priority_active"] else "monitoring"
    last_update = datetime.now().strftime("%d %b %Y, %I:%M:%S %p")

    if decision["priority_active"]:
        message = (
            f"{vehicle_type.title()} {vehicle_id} is within 1 km of "
            f"{decision['target_signal_name']}. Priority command generated."
        )
    else:
        message = (
            f"{vehicle_type.title()} {vehicle_id} is being tracked. "
            f"Nearest signal is {decision['target_signal_name']}."
        )

    dashboard_state.update(
        {
            "system_mode": system_mode,
            "last_update": last_update,
            "message": message,
            "vehicle": {
                "id": vehicle_id,
                "type": vehicle_type,
                "lat": vehicle_lat,
                "lon": vehicle_lon,
                "speed_kmph": speed_kmph,
                "timestamp": timestamp,
            },
            "decision": decision,
            "signals": signal_distances,
        }
    )

    return jsonify(dashboard_state)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
