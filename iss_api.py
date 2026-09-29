# iss_api.py — API REST locale (Flask)
# Installation : pip install flask
# Lancement    : python iss_api.py
# Accès        : http://127.0.0.1:5000/
import json
from pathlib import Path

try:
    from flask import Flask, jsonify, request
except ImportError:
    print("❌ pip install flask")
    raise SystemExit(1)

ALARM_CONFIG = Path.home() / ".mapci_alarm.json"

app = Flask(__name__)


def _load_alarm():
    if ALARM_CONFIG.exists():
        try:
            return json.loads(ALARM_CONFIG.read_text())
        except Exception:
            pass
    return {}


@app.route("/")
def index():
    return jsonify({
        "name": "MAP-CI API",
        "version": "8.0",
        "endpoints": [
            "/status",
            "/passes?lat=&lon=&hours=48",
            "/iss-now",
            "/position",
        ],
    })


@app.route("/status")
def status():
    cfg = _load_alarm()
    return jsonify({
        "alarme_active": cfg.get("enabled", False),
        "lieu": cfg.get("lieu"),
        "coords": [cfg.get("lat"), cfg.get("lon")],
        "seuil_min": cfg.get("seuil_minutes"),
    })


@app.route("/passes")
def passes_route():
    try:
        lat = float(request.args.get("lat", 5.3599517))
        lon = float(request.args.get("lon", -4.0082563))
        hours = int(request.args.get("hours", 48))
    except ValueError:
        return jsonify({"error": "Paramètres invalides"}), 400

    from iss_pass import get_next_passes
    passes = get_next_passes(lat, lon, hours=hours, min_elevation=0, verbose=False)

    result = []
    for p in passes:
        result.append({
            "risetime": p["risetime"].isoformat(),
            "settime": p["settime"].isoformat(),
            "duration_s": int(p["duration_s"]),
            "max_elevation": round(p["max_elevation"], 1),
            "cardinal_rise": p.get("cardinal_rise"),
            "cardinal_set": p.get("cardinal_set"),
            "distance_km": round(p.get("distance_km", 0), 1),
        })
    return jsonify({"count": len(result), "passes": result})


@app.route("/iss-now")
def iss_now():
    import requests
    try:
        d = requests.get("http://api.open-notify.org/iss-now.json", timeout=10).json()
        return jsonify(d)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/position")
def position():
    import requests
    try:
        d = requests.get("http://ip-api.com/json/", timeout=10).json()
        return jsonify(d)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🌐 MAP-CI API démarrage sur http://127.0.0.1:5000/")
    print("   Endpoints :")
    print("     GET /status")
    print("     GET /passes?lat=5.36&lon=-4.01&hours=48")
    print("     GET /iss-now")
    print("     GET /position")
    print()
    print("⚠️  Ctrl+C pour arrêter")
    print()
    app.run(host="127.0.0.1", port=5000, debug=False)
