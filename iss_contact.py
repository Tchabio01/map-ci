"""iss_contact.py - Contact radio avec l'ISS (APRS + ARISS + guide)"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

CONTACT_FILE = Path.home() / ".mapci_contact.json"


# ============================================================
# 1. APRS - Envoyer un message via l'ISS (le plus accessible)
# ============================================================
def guide_aprs():
    return """📨 *Contact APRS via l'ISS*

L'ISS embarque un *digipeater APRS* (indicatif RS0ISS-3).
Tu peux envoyer des messages **packet radio** qui seront relayés
par l'ISS quand elle passe au-dessus de ta station.

*Ce qu'il te faut :*
• 📻 Radio VHF 2m (144-146 MHz) avec mode packet
• 🖥️ TNC ou interface son (SignaLink, Mobilinkd)
• 🎫 Licence radioamateur (obligatoire pour émettre)
• 🖥️ Logiciel : *APRSIS32*, *Xastir* ou *Direwolf*

*Procédure :*
1. Connecte ta station à APRS-IS (serveur principal)
2. Configure le path : `ARISS,SGATE,WIDE1-1,WIDE2-1`
3. Adresse ton message à `RS0ISS` (la station ISS)
4. Envoie quand l'ISS passe (> 30° d'élévation)
5. Tu recevras une confirmation automatique

*Fréquence :* 145.825 MHz
*Vitesse :* 1200 bauds AFSK
*Doppler :* Compenser manuellement (±3 kHz)

*Astuce :*
Depuis un smartphone + app **APRSdroid** + un petit TNC
Bluetooth (Mobilinkd TNC3) = solution portable complète.

*Limitations :*
• L'astronaute ne lit PAS les messages APRS
• C'est un relais automatique pour position/météo
• Le "contact" est technique, pas humain"""


# ============================================================
# 2. ARISS - Contact vocal programmé (écoles)
# ============================================================
def guide_ariss():
    return """🎓 *Contact ARISS programmé*

C'est LE SEUL moyen d'avoir un vrai échange vocal avec un
astronaute. Mais c'est un processus long, réservé aux groupes.

*Qui peut candidater ?*
• Écoles primaires et secondaires
• Universités
• Musées / clubs scientifiques
• Associations jeunesse

*Délai :* 8 à 12 mois entre candidature et contact
*Durée :* environ 10 minutes
*Format :* 10-15 questions d'élèves à l'astronaute

*Procédure :*
1. 📝 Candidater sur https://www.ariss.org/apply.html
2. ⏳ Attente de sélection (plusieurs mois)
3. 📡 ARISS Europe/Amérique/Asie te contacte
4. 🛠️ Mise en place d'une station sol (matériel fourni/assisté)
5. 🛰️ Le jour J : contact de 10 min pendant un passage ISS

*Matériel utilisé par ARISS :*
• 2 stations de radio amateur (une principale, une backup)
• Antennes directionnelles (Yagi) avec rotor
• Ordinateur pour le tracking
• Modem pour la commutation automatique

*Ce qu'il te faut pour candidater :*
• Un projet pédagogique structuré
• Un coordinateur radioamateur
• Un lieu avec accès ciel dégagé
• Du temps (préparation ~6 mois)

*Lien candidature :*
https://www.ariss.org/apply.html"""


# ============================================================
# 3. Guide matériel complet
# ============================================================
def guide_materiel():
    return """🛠️ *Matériel radio ISS*

*Pour écouter seulement (le plus simple) :*
• 📱 Appli smartphone + WebSDR gratuit (aucun matériel)
• 📻 Radio scanner VHF (~50 000 FCFA)
• 📡 Antenne fouet 2m (~15 000 FCFA)

*Pour émettre (APRS) :*
• 🎫 Licence radioamateur (obligatoire, ~50 000 FCFA + examen)
• 📻 Émetteur VHF 2m 5-25W (~150 000 FCFA d'occasion)
• 📡 Antenne Yagi directive (~100 000 FCFA)
• 🖥️ TNC Mobilinkd ou SignaLink (~80 000 FCFA)
• 🔌 Alimentation 12V, câbles, connecteurs

*Pour SDR (numérique) :*
• 🔌 Dongle RTL-SDR (~15 000 FCFA)
• 📡 Antenne QFH ou Yagi (~30 000 FCFA)
• 🧑‍💻 Logiciel : SDR#, GQRX, SDRangel (gratuit)

*Budget minimum pour écouter :* 0 FCFA (WebSDR)
*Budget pour émettre APRS :* ~500 000 FCFA
*Budget pour candidater ARISS :* variable (aide ARISS possible)

*Marques fiables :*
• Yaesu FT-2980R (145 MHz, 80W)
• Icom IC-2730 (dual band)
• Baofeng UV-5R (débutant, mais limité pour satellite)
• RTL-SDR Blog V3 (dongle)
• Arrow Antenna 146/437 (portable satellite)

*Sites d'achat :*
• https://www.radioamateurs-france.fr/
• https://www.dxengineering.com/
• AliExpress (SDR, antennes)"""


# ============================================================
# 4. Préparation d'un contact
# ============================================================
def load_contacts():
    if CONTACT_FILE.exists():
        try:
            return json.loads(CONTACT_FILE.read_text())
        except Exception:
            pass
    return []


def save_contacts(data):
    CONTACT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def ajouter_projet(titre, type_contact, ecole, date_prevue, notes=""):
    contacts = load_contacts()
    contacts.append({
        "id": len(contacts) + 1,
        "titre": titre,
        "type": type_contact,
        "ecole": ecole,
        "date": date_prevue,
        "notes": notes,
        "cree": datetime.now(timezone.utc).isoformat(),
    })
    save_contacts(contacts)
    return contacts[-1]


def afficher_projets():
    contacts = load_contacts()
    if not contacts:
        return "📋 Aucun projet de contact enregistré."
    txt = "📋 *Projets de contact*\n\n"
    for c in contacts:
        txt += f"*{c['id']}. {c['titre']}*\n"
        txt += f"   Type : {c['type']}\n"
        txt += f"   École : {c['ecole']}\n"
        txt += f"   Date prévue : {c['date']}\n"
        if c.get("notes"):
            txt += f"   _{c['notes']}_\n"
        txt += "\n"
    return txt


# ============================================================
# 5. Checklist de préparation
# ============================================================
CHECKLIST = [
    "Projet pédagogique rédigé (objectifs, questions)",
    "Coordonnateur radioamateur identifié",
    "Lieu avec accès ciel dégagé (horizon > 10°)",
    "Autorisation de l'établissement obtenue",
    "Financement prévu (matériel + déplacement)",
    "Candidature envoyée sur ariss.org",
    "Contact régional ARISS établi",
    "Équipe radio formée (2-3 personnes)",
    "Antennes et émetteurs testés",
    "Répétition générale effectuée",
    "Questions des élèves préparées (10-15)",
    "Communication médiatique prévue",
]


def texte_checklist():
    txt = "✅ *Checklist contact ARISS*\n\n"
    for i, item in enumerate(CHECKLIST, 1):
        txt += f"☐ {item}\n"
    txt += "\n_Coche au fur et à mesure !_"
    return txt


if __name__ == "__main__":
    print("=== Test iss_contact.py ===\n")
    print(guide_aprs())
    print("\n" + "=" * 50 + "\n")
    print(guide_ariss())
    print("\n" + "=" * 50 + "\n")
    print(texte_checklist())
