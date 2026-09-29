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
