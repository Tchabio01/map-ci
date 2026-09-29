const map = L.map('map', {
  worldCopyJump: false,
  maxBounds: [[-90, -180], [90, 180]],
  maxBoundsViscosity: 1.0
}).setView([5.36, -4.01], 4);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: 'OpenStreetMap',
  noWrap: true
}).addTo(map);

const issIcon = L.divIcon({
  html: '<div style="font-size:28px;filter:drop-shadow(0 0 8px #4fc3f7)">🛰️</div>',
  iconSize: [34, 34], iconAnchor: [17, 17]
});

const userIcon = L.divIcon({
  html: '<div style="font-size:22px">📍</div>',
  iconSize: [24, 24], iconAnchor: [12, 24]
});

let issMarker = L.marker([0, 0], { icon: issIcon }).addTo(map);
let pathLine = L.polyline([], { color: '#4fc3f7', weight: 2, dashArray: '6,6' }).addTo(map);
let userMarker = null;
let passLines = [];
let firstCenter = true;

async function updateStatus() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    document.getElementById('status').textContent =
      '📍 ' + (d.lieu || '?') + ' | Alarme: ' + (d.alarme ? 'ON' : 'OFF') + ' | Seuil: ' + (d.seuil_min || '?') + 'min';

    if (d.coords && d.coords[0] && !userMarker) {
      userMarker = L.marker(d.coords, { icon: userIcon })
        .bindPopup('📍 ' + (d.lieu || 'Ma position'))
        .addTo(map);
    }
  } catch(e) { console.error(e); }
}

async function updateIssNow() {
  try {
    const r = await fetch('/api/iss-now');
    const d = await r.json();
    if (d.error) return;
    issMarker.setLatLng([d.lat, d.lon]);

    if (firstCenter) {
      map.setView([d.lat, d.lon], 4);
      firstCenter = false;
    }

    const dt = new Date(d.ts * 1000).toLocaleTimeString();
    document.getElementById('iss-pos').innerHTML =
      '📡 Latitude: <b>' + d.lat.toFixed(4) + '°</b><br>' +
      '📡 Longitude: <b>' + d.lon.toFixed(4) + '°</b><br>' +
      '⏰ ' + dt;
  } catch(e) { console.error(e); }
}

async function updateIssPath() {
  try {
    const r = await fetch('/api/iss-path');
    const d = await r.json();
    if (d.error) return;
    const coords = d.map(p => [p.lat, p.lon]);
    pathLine.setLatLngs(coords);
  } catch(e) { console.error(e); }
}

async function updatePasses() {
  try {
    const r = await fetch('/api/passes?hours=48');
    const passes = await r.json();
    if (!passes.length) {
      document.getElementById('passes').innerHTML = 'Aucun passage dans les 48h';
      return;
    }
    passLines.forEach(l => map.removeLayer(l));
    passLines = [];

    let html = '';
    passes.slice(0, 5).forEach((p, i) => {
      const rt = new Date(p.risetime);
      const delta = (rt - new Date()) / 1000 / 60;
      const mins = Math.round(delta);
      const cls = p.max_elevation > 60 ? 'best' : p.max_elevation > 20 ? 'highlight' : '';
      html += '<div class="pass-item ' + cls + '">' +
        '<b>' + (i+1) + '.</b> ' + rt.toLocaleString('fr-FR') + '<br>' +
        '<span style="color:#4fc3f7">max ' + p.max_elevation + '°</span> | ' +
        p.cardinal_rise + '→' + p.cardinal_set + ' | ' + p.duration_s + 's | ' +
        '<b>dans ' + mins + ' min</b>' +
        '</div>';
    });
    document.getElementById('passes').innerHTML = html;
  } catch(e) { console.error(e); }
}

const centerBtn = L.control({ position: 'topright' });
centerBtn.onAdd = function() {
  const div = L.DomUtil.create('div', 'center-btn');
  div.innerHTML = '🛰️';
  div.title = 'Recentrer sur ISS';
  div.style.cssText = 'background:#4fc3f7;width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:22px;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.3)';
  div.onclick = () => {
    const pos = issMarker.getLatLng();
    map.setView(pos, 4);
  };
  return div;
};
centerBtn.addTo(map);

updateStatus();
updateIssNow();
updateIssPath();
updatePasses();
setInterval(updateIssNow, 5000);
setInterval(updateIssPath, 30000);
setInterval(updatePasses, 60000);
setInterval(updateStatus, 30000);
