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
