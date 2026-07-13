const API_URL = window.location.origin + "/api";

const map = L.map("map").setView([35.2271, -80.8431], 11);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors"
}).addTo(map);

let allPotholes = [];
let markers = [];

function getColor(confidence) {
    if (confidence >= 0.7) return "red";
    if (confidence >= 0.5) return "orange";
    return "gold";
}

function applyFilters() {
    const confidenceFilter = document.getElementById("confidence-filter").value;
    const timeFilter = document.getElementById("time-filter").value;
    const now = new Date();

    const filtered = allPotholes.filter(p => {
        if (confidenceFilter === "high" && p.confidence < 0.7) return false;
        if (confidenceFilter === "medium" && (p.confidence < 0.5 || p.confidence >= 0.7)) return false;
        if (confidenceFilter === "low" && p.confidence >= 0.5) return false;

        let ts = p.timestamp;
        if (!ts.endsWith("Z") && !ts.includes("+")) ts += "Z";
        const timestamp = new Date(ts);
        const diffHours = (now - timestamp) / (1000 * 60 * 60);

        if (timeFilter === "day" && diffHours > 24) return false;
        if (timeFilter === "week" && diffHours > 168) return false;
        if (timeFilter === "month" && diffHours > 720) return false;

        return true;
    });

    renderMarkers(filtered);
}

function renderMarkers(potholes) {
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    potholes.forEach(pothole => {
        const color = getColor(pothole.confidence);
        const marker = L.circleMarker(
            [pothole.latitude, pothole.longitude],
            { radius: 7, color: color, fillColor: color, fillOpacity: 0.75, weight: 1 }
        ).addTo(map);

        let ts = pothole.timestamp;
        if (!ts.endsWith("Z") && !ts.includes("+")) ts += "Z";

        marker.bindPopup(`
            <b>Pothole #${pothole.id}</b><br>
            Confidence: ${(pothole.confidence * 100).toFixed(1)}%<br>
            Lat: ${pothole.latitude.toFixed(6)}<br>
            Lng: ${pothole.longitude.toFixed(6)}<br>
            Time: ${new Date(ts).toLocaleString('en-US', {timeZone: 'America/New_York'})}
        `);

        markers.push(marker);
    });

    document.getElementById("stats").textContent =
        `${potholes.length} of ${allPotholes.length} pothole${potholes.length !== 1 ? "s" : ""} shown`;
}

function resetFilters() {
    document.getElementById("confidence-filter").value = "all";
    document.getElementById("time-filter").value = "all";
    applyFilters();
}

async function loadPotholes() {
    document.getElementById("stats").textContent = "Loading...";
    try {
        const response = await fetch(`${API_URL}/potholes`);
        allPotholes = await response.json();
        applyFilters();
    } catch (error) {
        document.getElementById("stats").textContent = "Error connecting to API";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("apply-filters").addEventListener("click", applyFilters);
    document.getElementById("reset-filters").addEventListener("click", resetFilters);
    document.getElementById("refresh").addEventListener("click", loadPotholes);

    loadPotholes();
    setInterval(loadPotholes, 30000);
});