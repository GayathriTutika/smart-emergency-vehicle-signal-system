const stateUrl = "/api/state";
const updateUrl = "/api/update-location";

const systemMode = document.getElementById("systemMode");
const statusMessage = document.getElementById("statusMessage");
const vehicleId = document.getElementById("vehicleId");
const vehicleType = document.getElementById("vehicleType");
const vehicleLocation = document.getElementById("vehicleLocation");
const vehicleSpeed = document.getElementById("vehicleSpeed");
const vehicleTimestamp = document.getElementById("vehicleTimestamp");
const lastUpdate = document.getElementById("lastUpdate");
const priorityBadge = document.getElementById("priorityBadge");
const targetSignal = document.getElementById("targetSignal");
const targetDistance = document.getElementById("targetDistance");
const targetLane = document.getElementById("targetLane");
const targetCommand = document.getElementById("targetCommand");
const hardwareStatus = document.getElementById("hardwareStatus");
const signalList = document.getElementById("signalList");
const simulateButton = document.getElementById("simulateButton");

const demoPath = [
    { vehicle_id: "AMB-108", vehicle_type: "ambulance", lat: 17.4015, lon: 78.4680, speed_kmph: 58 },
    { vehicle_id: "AMB-108", vehicle_type: "ambulance", lat: 17.3978, lon: 78.4716, speed_kmph: 55 },
    { vehicle_id: "AMB-108", vehicle_type: "ambulance", lat: 17.3949, lon: 78.4738, speed_kmph: 52 },
    { vehicle_id: "AMB-108", vehicle_type: "ambulance", lat: 17.3928, lon: 78.4749, speed_kmph: 47 },
    { vehicle_id: "AMB-108", vehicle_type: "ambulance", lat: 17.3922, lon: 78.4753, speed_kmph: 34 },
];

function renderSignalList(signals, activeSignalId) {
    signalList.innerHTML = "";

    signals.forEach((signal) => {
        const card = document.createElement("article");
        const activeClass = signal.id === activeSignalId ? " active" : "";
        card.className = `signal-card${activeClass}`;

        card.innerHTML = `
            <p class="signal-id">${signal.id}</p>
            <h4>${signal.name}</h4>
            <p class="signal-distance">${signal.distance_m} m away</p>
        `;

        signalList.appendChild(card);
    });
}

function renderState(data) {
    const decision = data.decision || {};
    const vehicle = data.vehicle || {};
    const priorityActive = Boolean(decision.priority_active);

    systemMode.textContent =
        data.system_mode === "priority_active" ? "Priority Active" : "Monitoring";
    statusMessage.textContent = data.message || "Waiting for emergency vehicle GPS updates.";

    vehicleId.textContent = vehicle.id || "--";
    vehicleType.textContent = vehicle.type ? vehicle.type.toUpperCase() : "--";
    vehicleLocation.textContent =
        vehicle.lat !== null && vehicle.lon !== null ? `${vehicle.lat}, ${vehicle.lon}` : "--";
    vehicleSpeed.textContent =
        vehicle.speed_kmph !== null && vehicle.speed_kmph !== undefined
            ? `${vehicle.speed_kmph} km/h`
            : "--";
    vehicleTimestamp.textContent = vehicle.timestamp || "--";
    lastUpdate.textContent = data.last_update || "--";

    priorityBadge.textContent = priorityActive ? "Priority Ready" : "No Priority";
    priorityBadge.className = `decision-badge ${priorityActive ? "active" : ""}`;

    targetSignal.textContent = decision.target_signal_name || "--";
    targetDistance.textContent =
        decision.distance_m !== null && decision.distance_m !== undefined
            ? `${decision.distance_m} m`
            : "--";
    targetLane.textContent = decision.lane ? decision.lane.toUpperCase() : "--";
    targetCommand.textContent = decision.command || "NO_ACTION";
    hardwareStatus.textContent = decision.hardware_status || "--";

    renderSignalList(data.signals || [], decision.target_signal_id);
}

async function fetchState() {
    const response = await fetch(stateUrl);
    const data = await response.json();
    renderState(data);
}

async function sendLocation(location) {
    const payload = {
        ...location,
        timestamp: new Date().toISOString(),
    };

    const response = await fetch(updateUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    const data = await response.json();
    renderState(data);
}

async function runSimulation() {
    simulateButton.disabled = true;
    simulateButton.textContent = "Simulation Running...";

    for (const location of demoPath) {
        await sendLocation(location);
        await new Promise((resolve) => setTimeout(resolve, 5000));
    }

    simulateButton.disabled = false;
    simulateButton.textContent = "Start GPS Simulation";
}

simulateButton.addEventListener("click", runSimulation);
fetchState();
