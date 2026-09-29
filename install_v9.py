#!/usr/bin/env python3
"""install_v9.py — Installe automatiquement le Pack V9 (12 fichiers)"""
from pathlib import Path
import textwrap

ROOT = Path.home() / "map-ci"
(ROOT / "templates").mkdir(exist_ok=True)
(ROOT / "static").mkdir(exist_ok=True)

FILES = {}

# ============================================================
# 1. web_app.py — Interface Web Flask + API
# ============================================================
FILES["web_app.py"] = r'''
"""web_app.py — Interface Web MAP-CI V9 (Flask + Leaflet)"""
from flask import Flask, jsonify, render_template, request
import json
from pathlib import Path
from datetime import datetime, timezone

app = Flask(__name__)
ALARM = Path.home() / ".mapci_alarm.json"

def _load_alarm():
    if ALARM.exists():
        try:
            return json.loads(ALARM.read_text())
        except Exception:
            pass
    return {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def api_status():
    cfg = _load_alarm()
    return jsonify({
        "alarme": cfg.get("enabled", False),
        "lieu": cfg.get("lieu"),
        "coords": [cfg.get("lat"), cfg.get("lon")],
        "seuil_min": cfg.get("seuil_minutes"),
    })

@app.route("/api/iss-now")
def api_iss_now():
    import requests
    try:
        d = requests.get("http://api.open-notify.org/iss-now.json", timeout=10).json()
        return jsonify({
            "lat": float(d["iss_position"]["latitude"]),
            "lon": float(d["iss_position"]["longitude"]),
            "ts": d["timestamp"],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/passes")
def api_passes():
    cfg = _load_alarm()
    try:
        lat = float(request.args.get("lat", cfg.get("lat") or 5.3599517))
        lon = float(request.args.get("lon", cfg.get("lon") or -4.0082563))
        hours = int(request.args.get("hours", 48))
    except ValueError:
        return jsonify({"error": "Paramètres invalides"}), 400
    from iss_pass import get_next_passes
    passes = get_next_passes(lat, lon, hours=hours, min_elevation=0, verbose=False)
    return jsonify([{
        "risetime": p["risetime"].isoformat(),
        "settime": p["settime"].isoformat(),
        "duration_s": int(p["duration_s"]),
        "max_elevation": round(p["max_elevation"], 1),
        "cardinal_rise": p.get("cardinal_rise"),
        "cardinal_set": p.get("cardinal_set"),
        "az_rise": round(p.get("az_rise", 0), 1),
        "az_set": round(p.get("az_set", 0), 1),
        "distance_km": round(p.get("distance_km", 0), 1),
    } for p in passes])

@app.route("/api/iss-path")
def api_iss_path():
    """Retourne la trajectoire ISS sur les prochaines 90 minutes."""
    import requests
    from datetime import timedelta
    try:
        path = []
        # Position actuelle + interpolation simple
        d = requests.get("http://api.open-notify.org/iss-now.json", timeout=10).json()
        lat0 = float(d["iss_position"]["latitude"])
        lon0 = float(d["iss_position"]["longitude"])
        path.append({"lat": lat0, "lon": lon0, "t": "now"})
        # Position prévue (TLE via Skyfield si possible)
        try:
            from iss_pass import get_iss_tle, TS
            from skyfield.api import EarthSatellite, wgs84
            tle = get_iss_tle(verbose=False)
            if tle:
                sat = EarthSatellite(tle[0], tle[1], "ISS", TS)
                for min_ahead in range(10, 91, 10):
                    t = TS.now().utc_datetime() + timedelta(minutes=min_ahead)
                    tt = TS.from_datetime(t)
                    geo = sat.at(tt).subpoint()
                    path.append({
                        "lat": geo.latitude.degrees,
                        "lon": geo.longitude.degrees,
                        "t": f"+{min_ahead}min",
                    })
        except Exception:
            pass
        return jsonify(path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🌐 Interface Web MAP-CI V9")
    print("   http://127.0.0.1:8080/")
    print("   Depuis un autre appareil : http://<IP-TEL>:8080/")
    app.run(host="0.0.0.0", port=8080, debug=False)
'''

# ============================================================
# 2. templates/index.html — Page Web
# ============================================================
FILES["templates/index.html"] = r'''
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MAP-CI V9 — Suivi ISS</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<link rel="stylesheet" href="/static/style.css" />
</head>
<body>
<div id="header">
  <h1>🛰️ MAP-CI V9</h1>
  <div id="status">Chargement...</div>
</div>

<div id="map"></div>

<div id="panels">
  <div class="panel">
    <h3>🌍 Position ISS</h3>
    <div id="iss-pos">Chargement...</div>
  </div>

  <div class="panel">
    <h3>🚀 Prochains passages</h3>
    <div id="passes">Chargement...</div>
  </div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="/static/app.js"></script>
</body>
</html>
'''

# ============================================================
# 3. static/style.css
# ============================================================
FILES["static/style.css"] = r'''
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, system-ui, sans-serif; background: #0a0e27; color: #e0e0e0; }
#header { padding: 15px 20px; background: #151b3d; border-bottom: 2px solid #2a3a6b; }
#header h1 { font-size: 1.4em; color: #4fc3f7; }
#status { font-size: 0.9em; margin-top: 5px; color: #a0a0a0; }
#map { height: 60vh; width: 100%; }
#panels { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 15px; }
.panel { background: #151b3d; border-radius: 10px; padding: 15px; border: 1px solid #2a3a6b; }
.panel h3 { color: #4fc3f7; margin-bottom: 10px; font-size: 1.1em; }
#iss-pos, #passes { font-size: 0.9em; line-height: 1.6; }
.pass-item { padding: 8px; margin: 5px 0; background: #0f1533; border-radius: 5px; border-left: 3px solid #4fc3f7; }
.pass-item.highlight { border-left-color: #ffd54f; }
.pass-item.best { border-left-color: #66bb6a; }
@media (max-width: 768px) { #panels { grid-template-columns: 1fr; } }
'''

# ============================================================
# 4. static/app.js
# ============================================================
FILES["static/app.js"] = r'''
const map = L.map('map').setView([5.36, -4.01], 3);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap'
}).addTo(map);

const issIcon = L.divIcon({
  html: '<div style="font-size:24px">🛰️</div>',
  iconSize: [30, 30], iconAnchor: [15, 15]
});

let issMarker = L.marker([0, 0], { icon: issIcon }).addTo(map);
let pathLine = L.polyline([], { color: '#4fc3f7', weight: 2, dashArray: '5,5' }).addTo(map);
let passLines = [];

async function updateStatus() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    document.getElementById('status').textContent =
      `📍 ${d.lieu || '?'} | 🚨 Alarme: ${d.alarme ? 'ON' : 'OFF'} | Seuil: ${d.seuil_min || '?'}min`;
  } catch(e) { console.error(e); }
}

async function updateIssNow() {
  try {
    const r = await fetch('/api/iss-now');
    const d = await r.json();
    if (d.error) return;
    issMarker.setLatLng([d.lat, d.lon]);
    const dt = new Date(d.ts * 1000).toLocaleTimeString();
    document.getElementById('iss-pos').innerHTML =
      `📡 Latitude: <b>${d.lat.toFixed(4)}°</b><br>
       📡 Longitude: <b>${d.lon.toFixed(4)}°</b><br>
       ⏰ ${dt}`;
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
    // Efface les anciennes trajectoires
    passLines.forEach(l => map.removeLayer(l));
    passLines = [];

    let html = '';
    passes.slice(0, 5).forEach((p, i) => {
      const rt = new Date(p.risetime);
      const delta = (rt - new Date()) / 1000 / 60;
      const mins = Math.round(delta);
      const cls = p.max_elevation > 60 ? 'best' : p.max_elevation > 20 ? 'highlight' : '';
      html += `<div class="pass-item ${cls}">
        <b>${i+1}.</b> ${rt.toLocaleString('fr-FR')}<br>
        <span style="color:#4fc3f7">max ${p.max_elevation}°</span> |
        ${p.cardinal_rise}→${p.cardinal_set} | ${p.duration_s}s |
        <b>dans ${mins} min</b>
      </div>`;
    });
    document.getElementById('passes').innerHTML = html;
  } catch(e) { console.error(e); }
}

updateStatus();
updateIssNow();
updateIssPath();
updatePasses();
setInterval(updateIssNow, 5000);
setInterval(updateIssPath, 30000);
setInterval(updatePasses, 60000);
setInterval(updateStatus, 30000);
'''

# ============================================================
# 5. iss_aurora.py — Aurores boréales (Kp index)
# ============================================================
FILES["iss_aurora.py"] = r'''
"""iss_aurora.py — Alertes aurores boréales (NOAA Kp index)"""
import requests

def get_kp_forecast():
    """Retourne les 8 prochains Kp (3h chacun)."""
    try:
        r = requests.get("https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json", timeout=10)
        data = r.json()
        # Skip header
        out = []
        for row in data[1:12]:
            out.append({"time": row[0], "kp": float(row[1]), "status": row[2]})
        return out
    except Exception as e:
        return None

def get_current_kp():
    try:
        r = requests.get("https://services.swpc.noaa.gov/json/planetary_k_index_1m.json", timeout=10)
        data = r.json()
        if data:
            return float(data[-1].get("kp_index", 0))
    except Exception:
        pass
    return None

def aurora_level(kp):
    """Niveau d'aurore selon Kp."""
    if kp is None: return "?", "Inconnu", "⚪"
    if kp < 3: return "Calme", "Pas d'aurore significative", "🟢"
    if kp < 5: return "Actif", "Aurores possibles hautes latitudes", "🟡"
    if kp < 6: return "Orage G1", "Aurores visibles nord", "🟠"
    if kp < 7: return "Orage G2", "Belles aurores nord", "🔴"
    if kp < 8: return "Orage G3", "Aurores étendues", "🟣"
    return "Orage G4+", "Aurores jusqu'en Europe centrale !", "⚫"

def check_alert(threshold=5):
    """Retourne True si Kp >= threshold (aurores)."""
    kp = get_current_kp()
    return kp is not None and kp >= threshold

if __name__ == "__main__":
    print("Test iss_aurora.py\n")
    kp = get_current_kp()
    level, desc, emoji = aurora_level(kp)
    print(f"Kp actuel : {kp} {emoji} {level}")
    print(f"→ {desc}\n")
    print("Prévisions :")
    fc = get_kp_forecast()
    if fc:
        for f in fc[:8]:
            print(f"  {f['time']}  Kp {f['kp']}")
'''

# ============================================================
# 6. iss_meteors.py — Pluies d'étoiles filantes
# ============================================================
FILES["iss_meteors.py"] = r'''
"""iss_meteors.py — Pluies de météores (Perséides, Géminides...)"""
from datetime import datetime

# (nom, mois pic, jour pic, ZHR max, radiant)
METEORS = [
    ("Quadrantides", 1, 3, 110, "Bouvier"),
    ("Lyrides", 4, 22, 18, "Lyre"),
    ("Êta Aquariides", 5, 6, 60, "Verseau"),
    ("Delta Aquariides", 7, 30, 25, "Verseau"),
    ("Perséides", 8, 12, 100, "Persée"),
    ("Draconides", 10, 8, 10, "Dragon"),
    ("Orionides", 10, 21, 20, "Orion"),
    ("Léonides", 11, 17, 15, "Lion"),
    ("Géminides", 12, 14, 150, "Gémeaux"),
    ("Ursides", 12, 22, 10, "Petite Ourse"),
]

def prochains_meteors(n=5):
    """Retourne les n prochaines pluies."""
    now = datetime.now()
    out = []
    for m in METEORS:
        nom, mois, jour, zhr, radiant = m
        annee = now.year
        pic = datetime(annee, mois, jour)
        if pic < now:
            pic = datetime(annee + 1, mois, jour)
        jours = (pic - now).days
        out.append({
            "nom": nom, "date": pic, "jours": jours,
            "zhr": zhr, "radiant": radiant,
        })
    out.sort(key=lambda x: x["jours"])
    return out[:n]

if __name__ == "__main__":
    print("Test iss_meteors.py\n")
    print("🌠 Prochaines pluies d'étoiles filantes :\n")
    for m in prochains_meteors(10):
        emoji = "🔥" if m["zhr"] > 80 else "⭐" if m["zhr"] > 30 else "·"
        print(f"  {emoji} {m['nom']:<20} {m['date']:%d/%m/%Y}  "
              f"dans {m['jours']:>3}j  ZHR {m['zhr']:>3}  ({m['radiant']})")
'''

# ============================================================
# 7. iss_eclipses.py — Éclipses solaires/lunaires
# ============================================================
FILES["iss_eclipses.py"] = r'''
"""iss_eclipses.py — Éclipses solaires et lunaires (calcul approximatif)"""
from datetime import datetime, timedelta

# Éclipses connues (2025-2030)
ECLIPSES = [
    ("2025-03-14", "Lunaire totale", "Amériques, Europe"),
    ("2025-03-29", "Solaire partielle", "Europe, Afrique du Nord"),
    ("2025-09-07", "Lunaire totale", "Europe, Afrique, Asie"),
    ("2025-09-21", "Solaire partielle", "Pacifique, Antarctique"),
    ("2026-02-17", "Solaire annulaire", "Antarctique"),
    ("2026-03-03", "Lunaire totale", "Asie, Amériques"),
    ("2026-08-12", "Solaire totale", "Arctique, Groenland, Islande, Espagne"),
    ("2026-08-28", "Lunaire partielle", "Amériques, Europe, Afrique"),
    ("2027-02-06", "Solaire annulaire", "Amérique du Sud, Afrique"),
    ("2027-02-20", "Lunaire partielle", "Amériques, Europe, Afrique"),
    ("2027-07-22", "Lunaire partielle", "Asie, Australie, Pacifique"),
    ("2027-08-02", "Solaire totale", "Espagne, Afrique du Nord, Égypte"),
    ("2027-08-17", "Lunaire partielle", "Pacifique, Amériques"),
    ("2028-01-12", "Lunaire partielle", "Amériques, Europe, Afrique"),
    ("2028-01-26", "Solaire annulaire", "Amériques, Europe"),
    ("2028-07-06", "Solaire partielle", "Europe, Asie"),
    ("2028-07-22", "Lunaire partielle", "Asie, Australie"),
    ("2029-01-14", "Solaire partielle", "Amériques"),
    ("2029-06-12", "Solaire partielle", "Arctique, Scandinavie"),
    ("2029-12-05", "Solaire partielle", "Antarctique"),
    ("2030-06-01", "Solaire annulaire", "Europe, Asie, Afrique"),
]

def prochaines_eclipses(n=5):
    now = datetime.now()
    out = []
    for date_str, type_ecl, region in ECLIPSES:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        if d > now:
            jours = (d - now).days
            out.append({"date": d, "type": type_ecl, "region": region, "jours": jours})
    return out[:n]

if __name__ == "__main__":
    print("Test iss_eclipses.py\n")
    print("🌑 Prochaines éclipses :\n")
    for e in prochaines_eclipses(10):
        emoji = "🌑" if "Lunaire" in e["type"] else "☀️"
        print(f"  {emoji} {e['date']:%d/%m/%Y}  {e['type']:<20}  "
              f"dans {e['jours']:>4}j  |  {e['region']}")
'''

# ============================================================
# 8. iss_planets.py — Planètes visibles
# ============================================================
FILES["iss_planets.py"] = r'''
"""iss_planets.py — Planètes visibles ce soir"""
from datetime import datetime
from skyfield.api import load, wgs84
from pathlib import Path

EPH = load('de421.bsp')
TS = load.timescale()

PLANETS = [
    ("Mercure", "mercury barycenter"),
    ("Vénus", "venus barycenter"),
    ("Mars", "mars barycenter"),
    ("Jupiter", "jupiter barycenter"),
    ("Saturne", "saturn barycenter"),
    ("Uranus", "uranus barycenter"),
    ("Neptune", "neptune barycenter"),
]

def visibles_ce_soir(lat, lon):
    """Retourne les planètes au-dessus de l'horizon maintenant."""
    observer = wgs84.latlon(lat, lon)
    t = TS.now()
    results = []
    for nom, key in PLANETS:
        try:
            body = EPH[key]
            alt, az, dist = (body - observer).at(t).altaz()
            if alt.degrees > 0:
                card = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
                idx = int((az.degrees + 22.5) / 45) % 8
                results.append({
                    "nom": nom,
                    "altitude": round(alt.degrees, 1),
                    "azimut": round(az.degrees, 1),
                    "cardinal": card[idx],
                    "distance_ua": round(dist.au, 3),
                })
        except Exception:
            continue
    results.sort(key=lambda x: -x["altitude"])
    return results

if __name__ == "__main__":
    print("Test iss_planets.py\n")
    print("🪐 Planètes visibles ce soir (Abidjan) :\n")
    for p in visibles_ce_soir(5.3599517, -4.0082563):
        print(f"  {p['nom']:<10}  alt {p['altitude']:>5.1f}°  {p['cardinal']:<3} "
              f"(az {p['azimut']:>5.1f}°)  dist {p['distance_ua']} UA")
'''

# ============================================================
# 9. iss_achievements.py — Badges et achievements
# ============================================================
FILES["iss_achievements.py"] = r'''
"""iss_achievements.py — Achievements / Badges d'observation"""
import json
from pathlib import Path

ACH_FILE = Path.home() / ".mapci_achievements.json"
OBS_FILE = Path.home() / ".mapci_observations.json"

BADGES = [
    ("first", "🥉 Premier pas", "Première observation réussie", 1),
    ("ten", "🥈 Observateur", "10 passages observés", 10),
    ("fifty", "🥇 Expert ISS", "50 passages observés", 50),
    ("hundred", "💎 Maître ISS", "100 passages observés", 100),
    ("zenith", "🌟 Zénith", "Passage à plus de 85° d'élévation", None),
    ("night", "🌙 Nocturne", "Observation entre minuit et 5h", None),
    ("multi_city", "🌍 Voyageur", "3 villes d'observation différentes", None),
]

def load_badges():
    if ACH_FILE.exists():
        try:
            return json.loads(ACH_FILE.read_text())
        except Exception:
            pass
    return {}

def save_badges(b):
    ACH_FILE.write_text(json.dumps(b, indent=2))

def check_achievements():
    """Vérifie et débloque les nouveaux badges."""
    if not OBS_FILE.exists():
        return []
    try:
        obs = json.loads(OBS_FILE.read_text())
    except Exception:
        return []

    unlocked = load_badges()
    nouveaux = []

    vus = [o for o in obs if o.get("statut") == "vu"]
    nb_vus = len(vus)

    # Compteurs
    if nb_vus >= 1 and "first" not in unlocked:
        unlocked["first"] = True
        nouveaux.append(("first", "🥉 Premier pas"))

    if nb_vus >= 10 and "ten" not in unlocked:
        unlocked["ten"] = True
        nouveaux.append(("ten", "🥈 Observateur"))

    if nb_vus >= 50 and "fifty" not in unlocked:
        unlocked["fifty"] = True
        nouveaux.append(("fifty", "🥇 Expert ISS"))

    if nb_vus >= 100 and "hundred" not in unlocked:
        unlocked["hundred"] = True
        nouveaux.append(("hundred", "💎 Maître ISS"))

    # Zenith (élévation > 85)
    if any((o.get("elevation") or 0) > 85 for o in vus) and "zenith" not in unlocked:
        unlocked["zenith"] = True
        nouveaux.append(("zenith", "🌟 Zénith"))

    # Nocturne (00h-05h)
    if any(o["risetime"][11:13] in ("00","01","02","03","04") for o in vus) and "night" not in unlocked:
        unlocked["night"] = True
        nouveaux.append(("night", "🌙 Nocturne"))

    # Multi-villes
    villes = set(o.get("lieu", "") for o in vus)
    if len(villes) >= 3 and "multi_city" not in unlocked:
        unlocked["multi_city"] = True
        nouveaux.append(("multi_city", "🌍 Voyageur"))

    save_badges(unlocked)
    return nouveaux

def afficher():
    unlocked = load_badges()
    print(f"\n🏆 Achievements ({len(unlocked)}/{len(BADGES)} débloqués)\n")
    for key, emoji_nom, desc, _ in BADGES:
        fait = "✅" if key in unlocked else "🔒"
        print(f"  {fait} {emoji_nom:<20} — {desc}")

if __name__ == "__main__":
    print("Test iss_achievements.py")
    nouveaux = check_achievements()
    if nouveaux:
        print(f"\n🎉 {len(nouveaux)} nouveau(x) badge(s) débloqué(s) !")
        for _, nom in nouveaux:
            print(f"   {nom}")
    afficher()
'''

# ============================================================
# 10. iss_stats.py — Statistiques personnelles
# ============================================================
FILES["iss_stats.py"] = r'''
"""iss_stats.py — Statistiques personnelles d'observation"""
import json
from pathlib import Path
from collections import Counter

OBS_FILE = Path.home() / ".mapci_observations.json"

def load_obs():
    if OBS_FILE.exists():
        try:
            return json.loads(OBS_FILE.read_text())
        except Exception:
            pass
    return []

def stats_completes():
    obs = load_obs()
    vus = [o for o in obs if o.get("statut") == "vu"]
    rates = [o for o in obs if o.get("statut") == "rate"]

    if not vus:
        return {"message": "Aucune observation"}

    villes = Counter(o.get("lieu", "?") for o in vus)
    meilleur = max(vus, key=lambda o: o.get("elevation", 0))
    plus_brillant = min(
        (o for o in vus if o.get("magnitude") is not None),
        key=lambda o: o.get("magnitude", 999),
        default=None,
    )

    # Estimation distance cumulée (moyenne 1500 km par observation)
    distance_totale = len(vus) * 1500

    return {
        "total_observations": len(obs),
        "vus": len(vus),
        "rates": len(rates),
        "taux_reussite": round(len(vus) / max(1, len(obs)) * 100, 1),
        "villes_observees": dict(villes),
        "ville_favorite": villes.most_common(1)[0] if villes else ("?", 0),
        "meilleur_passage": {
            "date": meilleur.get("risetime", "?"),
            "elevation": meilleur.get("elevation"),
            "lieu": meilleur.get("lieu"),
        },
        "plus_brillant": {
            "date": plus_brillant.get("risetime", "?") if plus_brillant else None,
            "magnitude": plus_brillant.get("magnitude") if plus_brillant else None,
        },
        "distance_cumulee_km": distance_totale,
    }

def afficher():
    s = stats_completes()
    if "message" in s:
        print(f"📊 {s['message']}")
        return
    print("\n📊 VOS STATISTIQUES\n" + "─" * 44)
    print(f"👁️  Observations : {s['total_observations']} total")
    print(f"   ✅ Vus      : {s['vus']}")
    print(f"   ❌ Ratés    : {s['rates']}")
    print(f"   🎯 Taux     : {s['taux_reussite']}%")
    print()
    print(f"🌍 Villes observées : {len(s['villes_observees'])}")
    for ville, n in sorted(s['villes_observees'].items(), key=lambda x: -x[1]):
        print(f"   • {ville:<15} {n} observation(s)")
    print()
    print(f"🏔️  Meilleur passage : {s['meilleur_passage']['elevation']}° à "
          f"{s['meilleur_passage']['lieu']}")
    if s['plus_brillant']['magnitude']:
        print(f"⭐ Plus brillant  : mag {s['plus_brillant']['magnitude']}")
    print(f"🚀 Distance cumulée : {s['distance_cumulee_km']:,} km")
    print(f"   (l'ISS a parcouru ~{s['distance_cumulee_km']/40000:.1f} fois le tour de la Terre)")

if __name__ == "__main__":
    afficher()
'''

# ============================================================
# 11. iss_ntfy.py — Notifications push via ntfy.sh
# ============================================================
FILES["iss_ntfy.py"] = r'''
"""iss_ntfy.py — Notifications push via ntfy.sh (gratuit, sans compte)"""
import requests
from pathlib import Path

NTFY_CONFIG = Path.home() / ".mapci_ntfy.txt"

def get_topic():
    if NTFY_CONFIG.exists():
        return NTFY_CONFIG.read_text().strip()
    return None

def set_topic(topic):
    NTFY_CONFIG.write_text(topic.strip())

def envoyer(message, titre="MAP-CI ISS", priorite="high"):
    """Envoie une notification via ntfy.sh."""
    topic = get_topic()
    if not topic:
        return False
    try:
        r = requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers={
                "Title": titre,
                "Priority": priorite,
                "Tags": "satellite",
            },
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False

if __name__ == "__main__":
    print("Test iss_ntfy.py\n")
    print("Pour utiliser ntfy.sh :")
    print("1. Installe l'app 'ntfy' sur ton téléphone (Play Store / F-Droid)")
    print("2. Abonne-toi à un topic (ex: mapci-tchabio-123)")
    print("3. Configure le topic ici")
    print()
    if get_topic():
        print(f"Topic actuel : {get_topic()}")
        if input("Envoyer test ? (o/N) : ").strip().lower() == "o":
            if envoyer("Test MAP-CI V9"):
                print("✅ Envoyé !")
    else:
        t = input("Topic ntfy (ex: mapci-tchabio-123) : ").strip()
        if t:
            set_topic(t)
            print(f"✅ Topic configuré : {t}")
            print("   → Abonne-toi dans l'app ntfy sur ton téléphone")
            print(f"   → Test : envoie un message à https://ntfy.sh/{t}")
'''

# ============================================================
# 12. patch_v9.py — Intégration dans mapci.py
# ============================================================
FILES["patch_v9.py"] = r'''
"""patch_v9.py — Ajoute les modules V9 dans mapci.py"""
import ast, shutil
from pathlib import Path

MAPCI = Path.home() / "map-ci" / "mapci.py"
BACKUP = Path.home() / "map-ci" / "mapci.py.bak9"
shutil.copy(MAPCI, BACKUP)
print(f"Backup : {BACKUP}")

src = MAPCI.read_text(encoding="utf-8")

# Imports
imports = '''try:
    import iss_aurora
except Exception:
    iss_aurora = None
try:
    import iss_meteors
except Exception:
    iss_meteors = None
try:
    import iss_eclipses
except Exception:
    iss_eclipses = None
try:
    import iss_planets
except Exception:
    iss_planets = None
try:
    import iss_achievements
except Exception:
    iss_achievements = None
try:
    import iss_stats
except Exception:
    iss_stats = None
try:
    import iss_ntfy
except Exception:
    iss_ntfy = None
'''

if "import iss_aurora" not in src:
    anchor = "except Exception:\n    iss_multipos = None\n"
    if anchor in src:
        src = src.replace(anchor, anchor + imports, 1)
        print("+ imports V9")

# Fonctions
new_funcs = '''

# ============================================================
# OPTIONS 43-50 — Pack V9
# ============================================================
def menu_aurores():
    if iss_aurora is None:
        print("iss_aurora non disponible")
        return
    kp = iss_aurora.get_current_kp()
    level, desc, emoji = iss_aurora.aurora_level(kp)
    print(f"\\n{emoji}  Aurores boréales")
    print("-" * 44)
    print(f"Kp actuel : {kp} - {level}")
    print(f"-> {desc}")
    print()
    print("Prévisions (3h / ligne) :")
    fc = iss_aurora.get_kp_forecast()
    if fc:
        for f in fc[:8]:
            bar = "#" * int(f["kp"] * 3)
            print(f"  {f['time'][:16]:<17} Kp {f['kp']:.1f}  {bar}")


def menu_meteors():
    if iss_meteors is None:
        print("iss_meteors non disponible")
        return
    print("\\n🌠 Prochaines pluies d'étoiles filantes :\\n")
    for m in iss_meteors.prochains_meteors(10):
        emoji = "🔥" if m["zhr"] > 80 else "⭐" if m["zhr"] > 30 else "·"
        print(f"  {emoji} {m['nom']:<20} {m['date']:%d/%m/%Y}  "
              f"dans {m['jours']:>3}j  ZHR {m['zhr']:>3}  ({m['radiant']})")


def menu_eclipses():
    if iss_eclipses is None:
        print("iss_eclipses non disponible")
        return
    print("\\n🌑 Prochaines éclipses :\\n")
    for e in iss_eclipses.prochaines_eclipses(10):
        emoji = "🌑" if "Lunaire" in e["type"] else "☀️"
        print(f"  {emoji} {e['date']:%d/%m/%Y}  {e['type']:<20}  "
              f"dans {e['jours']:>4}j  |  {e['region']}")


def menu_planetes():
    if iss_planets is None:
        print("iss_planets non disponible")
        return
    lat = iss_alarm.config.get("lat")
    lon = iss_alarm.config.get("lon")
    if lat is None:
        print("Position requise")
        return
    print("\\n🪐 Planètes visibles maintenant :\\n")
    ps = iss_planets.visibles_ce_soir(lat, lon)
    if not ps:
        print("  Aucune planète au-dessus de l'horizon")
        return
    for p in ps:
        print(f"  {p['nom']:<10}  alt {p['altitude']:>5.1f}°  "
              f"{p['cardinal']:<3}  dist {p['distance_ua']} UA")


def menu_achievements():
    if iss_achievements is None:
        print("iss_achievements non disponible")
        return
    nouveaux = iss_achievements.check_achievements()
    if nouveaux:
        print(f"\\n🎉 {len(nouveaux)} nouveau(x) badge(s) !")
        for _, nom in nouveaux:
            print(f"   {nom}")
    iss_achievements.afficher()


def menu_stats():
    if iss_stats is None:
        print("iss_stats non disponible")
        return
    iss_stats.afficher()


def menu_ntfy():
    if iss_ntfy is None:
        print("iss_ntfy non disponible")
        return
    print("\\n📲 Notifications ntfy.sh")
    print("-" * 44)
    topic = iss_ntfy.get_topic()
    if topic:
        print(f"Topic actuel : {topic}")
        if input("Tester envoi ? (o/N) : ").strip().lower() == "o":
            if iss_ntfy.envoyer("Test MAP-CI V9"):
                print("✅ Envoyé !")
    else:
        t = input("Topic ntfy (ex: mapci-tchabio-123) : ").strip()
        if t:
            iss_ntfy.set_topic(t)
            print(f"✅ Configuré : {t}")
            print(f"   Abonne-toi à https://ntfy.sh/{t} dans l'app ntfy")


def menu_web_app():
    print("\\n🌐 Interface Web MAP-CI V9")
    print("-" * 44)
    print("Lance dans un terminal séparé :")
    print("  cd ~/map-ci")
    print("  python web_app.py")
    print()
    print("Puis ouvre dans un navigateur :")
    print("  Sur le téléphone : http://127.0.0.1:8080/")
    print("  Depuis un autre appareil du réseau : http://<IP-TEL>:8080/")
    print()
    print("Pour trouver ton IP locale :")
    print("  ifconfig 2>/dev/null | grep inet | grep -v 127.0.0.1")

'''

if "def menu_aurores" not in src:
    marker = "# ============================================================\n# MENU\n"
    if marker in src:
        src = src.replace(marker, new_funcs + "\n" + marker, 1)
        print("+ fonctions V9")

# Menu
old = '''    ("42", "Widget permanent",             menu_widget),
    ("0",  "Quitter",                      None),'''
new = '''    ("42", "Widget permanent",             menu_widget),
    ("43", "Aurores boreales (Kp)",        menu_aurores),
    ("44", "Pluies d'etoiles filantes",    menu_meteors),
    ("45", "Eclipses",                     menu_eclipses),
    ("46", "Planetes visibles",            menu_planets),
    ("47", "Achievements",                 menu_achievements),
    ("48", "Mes statistiques",             menu_stats),
    ("49", "Notifications ntfy.sh",        menu_ntfy),
    ("50", "Interface Web (info)",         menu_web_app),
    ("0",  "Quitter",                      None),'''

if '"43"' not in src:
    if old in src:
        src = src.replace(old, new, 1)
        print("+ menu 43-50")

try:
    ast.parse(src)
    print("Syntaxe OK")
except SyntaxError as e:
    print(f"Erreur : {e}")
    raise SystemExit(1)

MAPCI.write_text(src, encoding="utf-8")
print("mapci.py mis a jour !")
'''

# ============================================================
# ÉCRITURE DES FICHIERS
# ============================================================
print(f"Installation dans : {ROOT}\n")
for name, content in FILES.items():
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    lines = len(content.split("\n"))
    print(f"  + {name:<30} ({lines} lignes)")

print(f"\nOK - {len(FILES)} fichiers installes !")
print("\nProchaines etapes :")
print("  1. pip install flask")
print("  2. python patch_v9.py")
print("  3. python mapci.py")
print("  4. python web_app.py    (dans un autre onglet)")
