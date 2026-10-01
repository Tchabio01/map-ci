"""iss_nlp.py - Assistant conversationnel (NLP par mots-clés)"""
import re

def analyser(texte):
    """Retourne (intention, parametres) depuis un texte naturel."""
    t = texte.lower()

    # Salutations
    if re.search(r"\b(salut|bonjour|hello|hi|yo|slt|coucou)\b", t):
        return "salut", {}

    # Position ISS
    if any(w in t for w in ["ou est", "où est", "position", "localis", "trouve l iss"]):
        return "iss", {}

    # Prochain passage
    if any(w in t for w in ["quand", "prochain", "prochaine", "passe", "passage", "arrive"]):
        return "prochain", {}

    # Tous les passages
    if any(w in t for w in ["tous les passages", "liste", "planning", "agenda", "48h"]):
        return "passes", {}

    # Meteo
    if any(w in t for w in ["meteo", "météo", "temps", "il fait", "climat"]):
        return "meteo", {}

    # Photo Terre
    if any(w in t for w in ["photo", "terre", "image", "epic", "dscovr"]):
        return "earth", {}

    # Quiz
    if any(w in t for w in ["quiz", "joue", "jeu", "question", "apprend"]):
        return "quiz", {}

    # Stats
    if any(w in t for w in ["stat", "combien", "observ", "vu"]):
        return "stats", {}

    # Radio
    if any(w in t for w in ["radio", "frequence", "fréquence", "ecoute", "ariss"]):
        return "radio", {}

    # Aurores
    if any(w in t for w in ["aurore", "kp", "boreale", "boréale", "orage"]):
        return "aurores", {}

    # Aide
    if any(w in t for w in ["aide", "help", "peux tu", "peux-tu", "commandes"]):
        return "aide", {}

    # Vive / Bravo
    if any(w in t for w in ["bravo", "genial", "génial", "super", "cool", "merci"]):
        return "bravo", {}

    return "inconnu", {}


if __name__ == "__main__":
    tests = [
        "Salut ca va ?",
        "Ou est l ISS ?",
        "Quand passe l ISS ce soir ?",
        "Photo de la Terre",
        "Joue au quiz",
        "Mes stats d observation",
        "Frequence radio ISS",
        "Aurores boreales ce soir ?",
        "Merci beaucoup",
        "Comment marche le bot ?",
    ]
    for t in tests:
        intent, _ = analyser(t)
        print(f"  {t:40s} -> {intent}")
