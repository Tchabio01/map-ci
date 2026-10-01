"""iss_radio_live.py - Ecoute radio ISS via WebSDR"""
from datetime import datetime, timezone


# WebSDR publics accessibles depuis un navigateur mobile
WEBSDRS = [
    {
        "nom": "Twente (Pays-Bas)",
        "url": "http://websdr.ewi.utwente.nl:8901/",
        "portee": "Europe, Afrique du Nord",
        "note": "Le plus fiable, souvent utilise pour ARISS",
    },
    {
        "nom": "KFS (Californie)",
        "url": "http://sdr.kfs.fm:8901/",
        "portee": "Amerique du Nord, Pacifique",
        "note": "Bon pour les USA",
    },
    {
        "nom": "Farnham (UK)",
        "url": "http://websdr.serversfm.com:8901/",
        "portee": "Europe, Atlantique Nord",
        "note": "Alternative Europe",
    },
    {
        "nom": "SDR.hu Directory",
        "url": "http://sdr.hu/",
        "portee": "Monde entier",
        "note": "Annuaire de tous les WebSDR",
    },
    {
        "nom": "SATNOGS Network",
        "url": "https://network.satnogs.org/observations/",
        "portee": "Monde entier",
        "note": "Reseau de stations satellite amateurs",
    },
]

# Frequences par type d'activite
FREQS = {
    "voix": {
        "freq": "145.800 MHz",
        "mode": "FM-N (bande etroite)",
        "usage": "Contacts ARISS avec les ecoles",
    },
    "voix_alt": {
        "freq": "145.200 MHz",
        "mode": "FM-N",
        "usage": "Regions 2 et 3 (Ameriques, Asie)",
    },
    "sstv": {
        "freq": "145.800 MHz",
        "mode": "FM-N / SSTV PD120",
        "usage": "Images SSTV (evenements speciaux)",
    },
    "aprs": {
        "freq": "145.825 MHz",
        "mode": "AFSK 1200 bauds",
        "usage": "Paquets APRS automatiques",
    },
    "data": {
        "freq": "437.550 MHz",
        "mode": "UHF",
        "usage": "Telemetrie data (moins courant)",
    },
}


def texte_websdrs():
    """Message avec liens WebSDR cliquables."""
    txt = ("📻 *Ecouter la radio ISS*\n\n"
           "Aucun materiel necessaire : utilise un *WebSDR*\n"
           "(recepteur radio en ligne, gratuit).\n\n"
           "*WebSDR disponibles :*\n")
    for w in WEBSDRS:
        txt += "• *" + w["nom"] + "*\n"
        txt += "  Portee : " + w["portee"] + "\n"
        txt += "  " + w["note"] + "\n"
    txt += "\n_Frequence a regler : 145.800 MHz FM_"
    return txt


def kb_websdrs():
    """Clavier inline avec les liens WebSDR."""
    rows = []
    for w in WEBSDRS:
        rows.append([{"text": "Ecouter " + w["nom"], "url": w["url"]}])
    rows.append([{"text": "Guide complet", "callback_data": "radio_guide"}])
    rows.append([{"text": "Menu", "callback_data": "menu"}])
    return {"inline_keyboard": rows}


def texte_guide():
    """Guide pour ecouter l'ISS."""
    txt = ("📻 *Guide d'ecoute radio ISS*\n\n"
           "*1. Verifie un passage imminent*\n"
           "   Utilise /countdown ou le bouton Countdown\n"
           "   Il faut un passage > 10 deg d'elevation\n\n"
           "*2. Ouvre un WebSDR*\n"
           "   Choisis le plus proche de toi pour de meilleurs resultats\n"
           "   (Twente pour l'Afrique/Europe)\n\n"
           "*3. Regle la frequence*\n"
           "   Voix : *145.800 MHz* (bande etroite FM)\n"
           "   SSTV : *145.800 MHz*\n"
           "   APRS : *145.825 MHz*\n\n"
           "*4. Active le mode Doppler*\n"
           "   L'ISS bouge tres vite, la frequence derive.\n"
           "   Twente WebSDR a un bouton *Doppler* a activer.\n\n"
           "*5. Ecoute pendant le passage*\n"
           "   Le signal est faible mais audible.\n"
           "   La plupart du temps c'est silencieux.\n"
           "   Les contacts ARISS sont annonces a l'avance.\n\n"
           "*A savoir :*\n"
           "• L'ISS n'emet pas en permanence\n"
           "• Les astronautes dorment 8h/jour (silence nocturne)\n"
           "• Les meilleurs moments : contacts ARISS programmes\n"
           "• Voir https://www.ariss.org/ pour l'agenda\n\n"
           "*Astuce Pro :*\n"
           "Sur le WebSDR de Twente, tu peux activer le mode\n"
           "*autotrack* pour suivre l'ISS automatiquement !")
    return txt


def texte_frequences():
    """Detail de toutes les frequences."""
    txt = "📻 *Frequences ISS*\n\n"
    for key, f in FREQS.items():
        txt += "*" + f["freq"] + "* _(" + f["mode"] + ")_\n"
        txt += "  " + f["usage"] + "\n\n"
    return txt


def texte_ariss():
    """Infos contacts ARISS."""
    txt = ("📡 *Contacts ARISS*\n\n"
           "ARISS = Amateur Radio on the ISS\n"
           "Des astronautes contactent des ecoles du monde entier.\n\n"
           "*Comment savoir quand ?*\n"
           "• Site officiel : https://www.ariss.org/\n"
           "• Ces contacts sont annonces 2-4 semaines avant\n"
           "• Ils durent environ 10 minutes\n"
           "• Frequence : 145.800 MHz FM\n\n"
           "*Ecouter depuis chez toi :*\n"
           "1. Ouvre un WebSDR (Twente en priorite)\n"
           "2. Regle 145.800 MHz FM-N\n"
           "3. Active le Doppler tracking\n"
           "4. Attends le passage de l'ISS\n\n"
           "*SSTV (images)* :\n"
           "Occasionnellement, l'ISS envoie des images SSTV.\n"
           "Frequence : 145.800 MHz\n"
           "Tu peux decoder avec un telephone + appli SSTV\n"
           "(ex: Robot36 sur Android).")
    return txt


if __name__ == "__main__":
    print(texte_websdrs())
    print()
    print(texte_guide())
