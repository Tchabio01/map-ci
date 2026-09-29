# iss_alerts.py — Notifications Android (Termux) + SMS + countdown
import os
import json
import shutil
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

SMS_CONFIG = Path.home() / ".mapci_sms.json"
_CACHE = {"ts": 0, "info": None, "key": ""}

# ---------- Utilitaires Termux ----------
def _has(cmd):
    return shutil.which(cmd) is not None

def notifier_android(titre, message, vibrate=True):
    """Envoie une notification Android via termux-notification."""
    if not _has("termux-notification"):
        return False
    try:
        args = [
            "termux-notification",
            "--title", titre,
            "--content", message,
            "--priority", "high",
            "--id", "mapci_iss",
        ]
        if vibrate:
            args += ["--vibrate", "500,200,500,200,500"]
        subprocess.run(args, check=False, timeout=5)
        return True
    except Exception:
        return False

def parler(texte):
    """Synthèse vocale via termux-tts-speak."""
    if not _has("termux-tts-speak"):
        return False
    try:
        subprocess.run(
            ["termux-tts-speak", "-l", "fra", texte],
            check=False, timeout=10,
        )
        return True
    except Exception:
        return False

def vibrer(duree_ms=800):
    if not _has("termux-vibrate"):
        return False
    try:
        subprocess.run(["termux-vibrate", "-d", str(duree_ms)], check=False, timeout=3)
        return True
    except Exception:
        return False

# ---------- SMS via Twilio ----------
def envoyer_sms(message):
    """Envoie un SMS via Twilio (config dans ~/.mapci_sms.json)."""
    if not SMS_CONFIG.exists():
        return False
    try:
        cfg = json.loads(SMS_CONFIG.read_text())
        sid = cfg.get("sid")
        token = cfg.get("token")
        from_num = cfg.get("from")
        to_num = cfg.get("to")
        if not all([sid, token, from_num, to_num]):
            return False
        import requests
        r = requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
            data={"From": from_num, "To": to_num, "Body": message[:1600]},
            auth=(sid, token),
            timeout=15,
        )
        return r.status_code in (200, 201)
    except Exception:
        return False

# ---------- Compte à rebours prochain passage ----------
def next_pass_summary(lat, lon, seuil_min=0):
    """
    Retourne une chaîne de compte à rebours du prochain passage.
    Cache 5 min pour ne pas ralentir le menu.
    Utilise iss_pass.get_next_passes.
    """
    if lat is None or lon is None:
        return None

    key = f"{lat:.4f},{lon:.4f}"
    now = time.time()
    if (_CACHE["info"] is not None
            and now - _CACHE["ts"] < 300
            and _CACHE["key"] == key):
        return _CACHE["info"]

    try:
        from iss_pass import get_next_passes, az_to_cardinal
    except Exception:
        return None

    try:
        passes = get_next_passes(lat, lon, hours=24, min_elevation=0, verbose=False)
    except Exception:
        return None

    if not passes:
        _CACHE.update({"ts": now, "info": "Aucun passage dans 24h", "key": key})
        return _CACHE["info"]

    p = passes[0]
    now_utc = datetime.now(p['risetime'].tzinfo) if p['risetime'].tzinfo else datetime.utcnow()
    delta = (p['risetime'] - now_utc).total_seconds()
    if delta < 0:
        delta = 0
    h = int(delta // 3600)
    m = int((delta % 3600) // 60)

    quand = f"{h}h{m:02d}" if h else f"{m} min"
    info = (f"🛰️  Prochain ISS : dans {quand} "
            f"({p['risetime']:%H:%M} UTC, "
            f"max {p['max_elevation']:.0f}°, "
            f"{p['cardinal_rise']}→{p['cardinal_set']})")

    _CACHE.update({"ts": now, "info": info, "key": key})
    return info

def reset_cache():
    _CACHE["ts"] = 0
    _CACHE["info"] = None
    _CACHE["key"] = ""

# ---------- Test ----------
if __name__ == "__main__":
    print("Test iss_alerts.py\n")
    print("termux-notification :", _has("termux-notification"))
    print("termux-tts-speak    :", _has("termux-tts-speak"))
    print("termux-vibrate      :", _has("termux-vibrate"))
    print("SMS config          :", SMS_CONFIG.exists())
    print("\nTest notification...")
    ok = notifier_android("MAP-CI", "Test de notification ISS 🛰️")
    print("  Envoi :", "OK" if ok else "Non disponible")
    print("\nCompte à rebours prochain passage :")
    info = next_pass_summary(5.3599517, -4.0082563)
    print("  " + (info or "indisponible"))
