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
