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
