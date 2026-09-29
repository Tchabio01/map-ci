# iss_multipos.py — Gestion de plusieurs positions à surveiller
# v1.0
import json
from pathlib import Path

POS_FILE = Path.home() / ".mapci_positions.json"


def load_positions():
    if POS_FILE.exists():
        try:
            return json.loads(POS_FILE.read_text())
        except Exception:
            pass
    return []


def save_positions(pos):
    POS_FILE.write_text(json.dumps(pos, indent=2, ensure_ascii=False))


def ajouter(nom, lat, lon):
    pos = load_positions()
    pos = [p for p in pos if p["nom"].lower() != nom.lower()]
    pos.append({"nom": nom, "lat": lat, "lon": lon})
    save_positions(pos)


def supprimer(nom):
    pos = load_positions()
    pos = [p for p in pos if p["nom"].lower() != nom.lower()]
    save_positions(pos)


def get(nom):
    for p in load_positions():
        if p["nom"].lower() == nom.lower():
            return p
    return None


def passages_toutes_positions(hours=48, min_elev=0):
    """Calcule les passages pour toutes les positions enregistrées."""
    from iss_pass import get_next_passes
    resultats = {}
    for p in load_positions():
        try:
            passes = get_next_passes(
                p["lat"], p["lon"], hours=hours,
                min_elevation=min_elev, verbose=False,
            )
            resultats[p["nom"]] = passes
        except Exception as e:
            resultats[p["nom"]] = []
    return resultats


def afficher():
    pos = load_positions()
    if not pos:
        print("📭 Aucune position enregistrée.")
        return
    print(f"\n📍 {len(pos)} position(s) surveillée(s) :")
    for p in pos:
        print(f"  • {p['nom']:<20} {p['lat']:>9.4f}, {p['lon']:>9.4f}")


def menu_interactif():
    while True:
        afficher()
        print("\n  A. Ajouter  |  S. Supprimer  |  P. Passages  |  Entrée. Retour")
        c = input("👉 ").strip().upper()
        if c == "A":
            nom = input("Nom : ").strip()
            if not nom:
                continue
            try:
                lat = float(input("Latitude  : ").strip())
                lon = float(input("Longitude : ").strip())
                ajouter(nom, lat, lon)
                print(f"✅ {nom} ajouté")
            except ValueError:
                print("❌ Coordonnées invalides")
        elif c == "S":
            nom = input("Nom à supprimer : ").strip()
            supprimer(nom)
            print(f"✅ {nom} supprimé")
        elif c == "P":
            pos = load_positions()
            if not pos:
                print("❌ Aucune position")
                continue
            print(f"\n⏳ Calcul des passages pour {len(pos)} position(s)...")
            res = passages_toutes_positions()
            for nom, passes in res.items():
                print(f"\n🛰️  {nom} — {len(passes)} passage(s)")
                for p in passes[:3]:
                    print(f"  {p['risetime']:%d/%m %H:%M} UTC | "
                          f"max {p['max_elevation']:>4.0f}° | "
                          f"{p.get('cardinal_rise','?')}->{p.get('cardinal_set','?')}")
        else:
            break


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("Test iss_multipos.py\n")

    # Ajoute 3 villes de test
    ajouter("Abidjan", 5.3599517, -4.0082563)
    ajouter("Dakar", 14.6928, -17.4467)
    ajouter("Paris", 48.8566, 2.3522)

    afficher()

    print("\nTest passages toutes positions (24h)...")
    res = passages_toutes_positions(hours=24)
    for nom, passes in res.items():
        print(f"\n🛰️  {nom} — {len(passes)} passage(s) dans 24h")
        for p in passes[:2]:
            print(f"  {p['risetime']:%d/%m %H:%M} UTC | "
                  f"max {p['max_elevation']:>4.0f}°")
