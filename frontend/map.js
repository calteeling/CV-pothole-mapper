const API_URL = "http://localhost:8000/api";

const map = L.map("map").setView([35.2271, -80.8431], 12);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors"
}).addTo(map);

const markers = [];

async function loadPotholes() {
    try {
        const response = await fetch(`${API_URL}/potholes`);
        const potholes = await response.json();

        markers.forEach(m => map.removeLayer(m));
        markers.length = 0;

        potholes.forEach(pothole => {
            const color = pothole.confidence > 0.7 ? "red" : "orange";
            const marker = L.circleMarker(
                [pothole.latitude, pothole.longitude],
                { radius: 8, color: color, fillColor: color, fillOpacity: 0.7 }
            ).addTo(map);

            marker.bindPopup(`
                <b>Pothole #${pothole.id}</b><br>
                Confidence: ${(pothole.confidence * 100).toFixed(1)}%<br>
                Lat: ${pothole.latitude.toFixed(6)}<br>
                Lng: ${pothole.longitude.toFixed(6)}<br>
                Time: ${new Date(pothole.timestamp).toLocaleString()}
            `);

            markers.push(marker);
        });

        document.getElementById("stats").textContent =
            `${potholes.length} pothole${potholes.length !== 1 ? "s" : ""} detected`;

    } catch (error) {
        document.getElementById("stats").textContent = "Error connecting to API";
    }
}

loadPotholes();
setInterval(loadPotholes, 5000);