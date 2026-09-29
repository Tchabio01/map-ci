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
