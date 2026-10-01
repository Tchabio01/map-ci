"""iss_voice.py - Commandes vocales via Termux:API + Telegram voice"""
import os
import shutil
import subprocess
from pathlib import Path


def has_stt():
    return shutil.which("termux-speech-to-text") is not None


def has_tts():
    return shutil.which("termux-tts-speak") is not None


def ecouter(timeout=10):
    """Ecoute une commande vocale via le micro."""
    if not has_stt():
        return None, "Termux:API requis (pkg install termux-api + app Termux:API)"
    try:
        r = subprocess.run(
            ["termux-speech-to-text"],
            capture_output=True, text=True, timeout=timeout,
        )
        if r.returncode == 0:
            return r.stdout.strip(), None
        return None, "Erreur reconnaissance vocale"
    except subprocess.TimeoutExpired:
        return None, "Timeout - pas de voix detectee"
    except Exception as e:
        return None, str(e)


def parler(texte, langue="fra"):
    """Synthese vocale."""
    if not has_tts():
        return False
    try:
        subprocess.run(
            ["termux-tts-speak", "-l", langue, texte],
            timeout=30, check=False,
        )
        return True
    except Exception:
        return False


def vibrer(duree=200):
    if not shutil.which("termux-vibrate"):
        return False
    try:
        subprocess.run(["termux-vibrate", "-d", str(duree)], check=False, timeout=3)
        return True
    except Exception:
        return False


# Traduction vocal -> commande texte (mots cles)
MOTS_CLES = {
    "iss": ["iss", "station", "satellite", "espace"],
    "prochain": ["prochain", "prochaine", "quand", "passe"],
    "passes": ["passages", "liste", "planning"],
    "countdown": ["compte", "rebours", "combien", "reste"],
    "meteo": ["meteo", "temps", "climat", "nuages"],
    "radio": ["radio", "frequence", "ecoute"],
    "photo": ["photo", "terre", "image", "vue"],
    "stats": ["stat", "combien", "observations"],
    "lune": ["lune", "phase"],
    "solaire": ["solaire", "aurore", "kp", "orage"],
    "contact": ["contact", "parler", "astronaute"],
    "aide": ["aide", "help", "peux tu", "commandes"],
    "stop": ["stop", "arrete", "quitte", "silence"],
}


def interpreter(texte):
    """Convertit une phrase vocale en intention."""
    if not texte:
        return "inconnu"
    t = texte.lower()
    # Verifie chaque categorie
    for intent, mots in MOTS_CLES.items():
        for mot in mots:
            if mot in t:
                return intent
    return "inconnu"


if __name__ == "__main__":
    print("Test iss_voice.py\n")
    print("STT (reconnaissance) :", has_stt())
    print("TTS (voix)           :", has_tts())
    print("Vibrate              :", shutil.which("termux-vibrate") is not None)
    print()
    print("Test interpretation :")
    for phrase in ["Où est l'ISS", "Quand passe la station", "Montre-moi la Terre",
                   "Quel est le compte à rebours", "Arrête"]:
        intent = interpreter(phrase)
        print(f"  '{phrase}' -> {intent}")
