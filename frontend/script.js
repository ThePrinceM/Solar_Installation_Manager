let map;
let marker;
let chart;
let selectedLat = null, selectedLng = null;

window.onload = () => {
    map = L.map('map').setView([22.9734, 78.6569], 5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
    }).addTo(map);

    map.on('click', function (e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        if (marker) map.removeLayer(marker);
        marker = L.marker([lat, lng]).addTo(map);

        selectedLat = lat;
        selectedLng = lng;

        console.log("Selected:", lat, lng);

        document.getElementById("locationDisplay").innerText =
            `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
    });
};


function showDebug(msg) {
    document.getElementById("debugOutput").innerHTML = "<pre>" + msg + "</pre>";
    console.log(msg);
}

function testBackend() {
    fetch("/api/debug")
        .then(res => res.json())
        .then(data => showDebug(JSON.stringify(data)))
        .catch(err => showDebug("Backend error: " + err));
}

function testIrradiance() {
    if (!selectedLat) {
        showDebug("Select a location on map first.");
        return;
    }

    fetch("/api/calculate-location", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lat: selectedLat, lng: selectedLng, roof_area: 1 })
    })
        .then(res => res.json())
        .then(data => showDebug(JSON.stringify(data)))
        .catch(err => showDebug("API error: " + err));
}

function calculateSolar() {
    const roofArea = document.getElementById("roofArea").value;

    if (!selectedLat || !roofArea) {
        alert("Select location and enter roof area");
        return;
    }

    fetch("/api/calculate-location", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            lat: selectedLat,
            lng: selectedLng,
            roof_area: roofArea
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                showDebug("Calc error: " + JSON.stringify(data));
                return;
            }

            document.getElementById("result").innerHTML =
                `Irradiance: ${data.irradiance.toFixed(2)} kWh/m²/day<br>
                 Annual Energy: ${data.annual_energy_kwh} kWh<br>
                 Savings: ${data.annual_savings_inr} Rupees<br>
                 Payback: ${data.payback_years} years<br>
                 Lifetime Savings: ${data.lifetime_savings_inr} Rupees`;

            drawChart(roofArea, data.annual_energy_kwh);
        })
        .catch(err => showDebug("Fetch error: " + err));
}

function drawChart(roofArea, energy) {
    const ctx = document.getElementById("energyChart").getContext("2d");

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [0, roofArea / 2, roofArea],
            datasets: [{
                label: 'Energy Output (kWh)',
                data: [0, energy / 2, energy]
            }]
        }
    });
}
