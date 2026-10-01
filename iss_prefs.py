"""iss_prefs.py - Preferences utilisateur"""
import json
from pathlib import Path

PREFS_FILE = Path.home() / ".mapci_prefs.json"

DEFAULTS = {
    "langue": "fr",
    "unites": "metric",
    "notif_avant": 40,
    "notif_telegram": True,
    "notif_android": True,
    "notif_vocal": True,
    "elevation_min": 10,
    "compact": False,
}


def load():
    if PREFS_FILE.exists():
        try:
            data = json.loads(PREFS_FILE.read_text())
            # Merge avec defaults
            return {**DEFAULTS, **data}
        except Exception:
            pass
    return DEFAULTS.copy()


def save(prefs):
    PREFS_FILE.write_text(json.dumps(prefs, indent=2))


def set_pref(key, value):
    prefs = load()
    prefs[key] = value
    save(prefs)
    return prefs


def get(key, default=None):
    prefs = load()
    return prefs.get(key, default if default is not None else DEFAULTS.get(key))


def reset():
    save(DEFAULTS.copy())
    return DEFAULTS.copy()


def afficher():
    p = load()
    txt = ["⚙️ *Préférences*", ""]
    txt.append(f"🌐 Langue : `{p['langue']}`")
    txt.append(f"📏 Unités : `{p['unites']}`")
    txt.append(f"🔔 Notif avant : `{p['notif_avant']} min`")
    txt.append(f"📍 Élévation mini : `{p['elevation_min']}°`")
    txt.append(f"📱 Telegram : {'✅' if p['notif_telegram'] else '❌'}")
    txt.append(f"📳 Android : {'✅' if p['notif_android'] else '❌'}")
    txt.append(f"🔊 Vocal : {'✅' if p['notif_vocal'] else '❌'}")
    txt.append(f"📦 Compact : {'✅' if p['compact'] else '❌'}")
    return "\n".join(txt)


if __name__ == "__main__":
    print(afficher())
