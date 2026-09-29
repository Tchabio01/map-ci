# iss_observe.py — Historique d'observations (vu/raté + notes)
# v1.0
import json
from datetime import datetime, timezone
from pathlib import Path

OBS_FILE = Path.home() / ".mapci_observations.json"


def load_obs():
    if OBS_FILE.exists():
        try:
            return json.loads(OBS_FILE.read_text())
        except Exception:
            pass
    return []


def save_obs(obs):
    OBS_FILE.write_text(json.dumps(obs, indent=2, ensure_ascii=False))


def ajouter_observation(risetime, lieu, statut, note="", mag=None, elev=None):
    """statut : 'vu', 'rate', 'annule'"""
    obs = load_obs()
    obs.append({
        "risetime": risetime if isinstance(risetime, str) else risetime.isoformat(),
        "lieu": lieu,
        "statut": statut,
        "note": note,
        "magnitude": mag,
        "elevation": elev,
        "enregistre": datetime.now(timezone.utc).isoformat(),
    })
    save_obs(obs)


def stats():
    obs = load_obs()
    vus = sum(1 for o in obs if o["statut"] == "vu")
    rates = sum(1 for o in obs if o["statut"] == "rate")
    total = len(obs)
    taux = round(vus / max(1, vus + rates) * 100, 1)
    return {"total": total, "vus": vus, "rates": rates, "taux": taux}


def afficher(limit=20):
    obs = load_obs()
    if not obs:
        print("📭 Aucune observation enregistrée.")
        return
    st = stats()
    print(f"\n📊 Observations ({st['total']} au total)")
    print(f"   ✅ Vus : {st['vus']}  |  ❌ Ratés : {st['rates']}  |  Taux : {st['taux']}%")
    print()
    for o in obs[-limit:][::-1]:
        emoji = {"vu": "✅", "rate": "❌", "annule": "⏸️"}.get(o["statut"], "?")
        mag = f" mag {o['magnitude']}" if o.get("magnitude") else ""
        elev = f" elev {o['elevation']}°" if o.get("elevation") else ""
        print(f"  {emoji} {o['risetime'][:16]} @ {o['lieu']}{mag}{elev}")
        if o.get("note"):
            print(f"     📝 {o['note']}")


def marquer_interactif(lieu="Abidjan"):
    """Mode interactif pour saisir une observation."""
    print("\n📝 Nouvelle observation")
    print("─" * 44)
    rs = input("Date/heure UTC (YYYY-MM-DDTHH:MM) : ").strip()
    if not rs:
        return
    print("Statut : 1=Vu  2=Rate  3=Annule")
    choix = input("Choix [1] : ").strip() or "1"
    statut = {"1": "vu", "2": "rate", "3": "annule"}.get(choix, "vu")
    note = input("Note (optionnel) : ").strip()
    try:
        mag_str = input("Magnitude observée (Entrée=skip) : ").strip()
        mag = float(mag_str) if mag_str else None
    except ValueError:
        mag = None
    try:
        elev_str = input("Élévation max ° (Entrée=skip) : ").strip()
        elev = int(elev_str) if elev_str else None
    except ValueError:
        elev = None
    ajouter_observation(rs, lieu, statut, note, mag, elev)
    print("✅ Enregistré")


def supprimer_derniere():
    obs = load_obs()
    if not obs:
        print("📭 Rien à supprimer.")
        return
    obs.pop()
    save_obs(obs)
    print("✅ Dernière observation supprimée")


def reset():
    if input("⚠️  Tout effacer ? (o/N) : ").strip().lower() == "o":
        save_obs([])
        print("✅ Historique vidé")


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("Test iss_observe.py\n")

    # Ajoute 2 observations de test si vide
    if not load_obs():
        ajouter_observation(
            "2026-09-29T20:18:58", "Abidjan", "vu",
            "Superbe, très brillant", -2.5, 30,
        )
        ajouter_observation(
            "2026-09-29T21:56:44", "Abidjan", "rate",
            "Nuages", None, 8,
        )
        print("2 observations de test ajoutées.\n")

    afficher()
