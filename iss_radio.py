"""iss_radio.py - Radio ISS et contacts ARISS"""
from datetime import datetime, timezone

# Frequences standards
FREQUENCES = {
    "voix": "145.800 MHz FM-N",
    "voix_alt": "145.200 MHz (régions 2-3)",
    "sstv": "145.800 MHz (événements spéciaux)",
    "aprs": "145.825 MHz (packets)",
    "data": "437.550 MHz (downlink)",
}

# Contacts ARISS connus (à mettre à jour selon agenda)
CONTACTS_ARISS = [
    # (date ISO, école, pays)
    ("2026-10-15", "École primaire Paris", "France"),
    ("2026-11-02", "Lycée Dakar", "Sénégal"),
]


def prochains_contacts(n=3):
    now = datetime.now(timezone.utc)
    out = []
    for date_str, ecole, pays in CONTACTS_ARISS:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if d > now:
                jours = (d - now).days
                out.append({"date": d, "ecole": ecole, "pays": pays, "jours": jours})
        except Exception:
            continue
    out.sort(key=lambda x: x["jours"])
    return out[:n]


def infos_radio(lieu="?"):
    txt = f"""📻 *Radio ISS — Infos*

📍 Lieu : {lieu}

*Fréquences principales :*
• 🎙️ Voix : `{FREQUENCES["voix"]}`
• 🎙️ Voix (alt) : `{FREQUENCES["voix_alt"]}`
• 📺 SSTV : `{FREQUENCES["sstv"]}`
• 📡 APRS : `{FREQUENCES["aprs"]}`
• 💾 Data : `{FREQUENCES["data"]}`

*Quand écouter ?*
• Pendant les passages > 10° d'élévation
• Contrôler les prévisions (option P du menu)

*Astuce :*
Utilise une radio VHF ou un scanner avec antenne
orientée vers la direction du passage.

Plus d'infos : https://www.ariss.org/"""

    contacts = prochains_contacts(3)
    if contacts:
        txt += "\n\n*📅 Prochains contacts ARISS :*\n"
        for c in contacts:
            txt += f"• {c['date']:%d/%m/%Y} — {c['ecole']} ({c['pays']}) dans {c['jours']}j\n"
    return txt


if __name__ == "__main__":
    print(infos_radio("Abidjan"))
