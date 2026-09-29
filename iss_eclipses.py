"""iss_eclipses.py — Éclipses solaires et lunaires (calcul approximatif)"""
from datetime import datetime, timedelta

# Éclipses connues (2025-2030)
ECLIPSES = [
    ("2025-03-14", "Lunaire totale", "Amériques, Europe"),
    ("2025-03-29", "Solaire partielle", "Europe, Afrique du Nord"),
    ("2025-09-07", "Lunaire totale", "Europe, Afrique, Asie"),
    ("2025-09-21", "Solaire partielle", "Pacifique, Antarctique"),
    ("2026-02-17", "Solaire annulaire", "Antarctique"),
    ("2026-03-03", "Lunaire totale", "Asie, Amériques"),
    ("2026-08-12", "Solaire totale", "Arctique, Groenland, Islande, Espagne"),
    ("2026-08-28", "Lunaire partielle", "Amériques, Europe, Afrique"),
    ("2027-02-06", "Solaire annulaire", "Amérique du Sud, Afrique"),
    ("2027-02-20", "Lunaire partielle", "Amériques, Europe, Afrique"),
    ("2027-07-22", "Lunaire partielle", "Asie, Australie, Pacifique"),
    ("2027-08-02", "Solaire totale", "Espagne, Afrique du Nord, Égypte"),
    ("2027-08-17", "Lunaire partielle", "Pacifique, Amériques"),
    ("2028-01-12", "Lunaire partielle", "Amériques, Europe, Afrique"),
    ("2028-01-26", "Solaire annulaire", "Amériques, Europe"),
    ("2028-07-06", "Solaire partielle", "Europe, Asie"),
    ("2028-07-22", "Lunaire partielle", "Asie, Australie"),
    ("2029-01-14", "Solaire partielle", "Amériques"),
    ("2029-06-12", "Solaire partielle", "Arctique, Scandinavie"),
    ("2029-12-05", "Solaire partielle", "Antarctique"),
    ("2030-06-01", "Solaire annulaire", "Europe, Asie, Afrique"),
]

def prochaines_eclipses(n=5):
    now = datetime.now()
    out = []
    for date_str, type_ecl, region in ECLIPSES:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        if d > now:
            jours = (d - now).days
            out.append({"date": d, "type": type_ecl, "region": region, "jours": jours})
    return out[:n]

if __name__ == "__main__":
    print("Test iss_eclipses.py\n")
    print("🌑 Prochaines éclipses :\n")
    for e in prochaines_eclipses(10):
        emoji = "🌑" if "Lunaire" in e["type"] else "☀️"
        print(f"  {emoji} {e['date']:%d/%m/%Y}  {e['type']:<20}  "
              f"dans {e['jours']:>4}j  |  {e['region']}")
