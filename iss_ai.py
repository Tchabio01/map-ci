"""iss_ai.py - IA conversationnelle via Groq (gratuit, rapide)"""
import json
from pathlib import Path

import requests

AI_CONFIG = Path.home() / ".mapci_ai.json"

SYSTEM_PROMPT = """Tu es MAP-CI, un assistant spatial francophone integre a un bot Telegram dedie au suivi de l'ISS et de l'espace.

Tu as acces a ces outils internes (le bot les gere separement) :
- Position ISS en temps reel
- Prochains passages ISS
- Meteo spatiale (Kp index)
- Radio ISS (frequences)
- Contacts ARISS
- Photos NASA EPIC (Terre vue de l'espace)
- Multi-satellites (Hubble, Tiangong, NOAA)

Quand l'utilisateur demande une donnee que le bot peut fournir (position, passage, etc),
reponds brievement et indique-lui la commande exacte (ex: /iss, /passes).

Sinon, reponds en tant qu'expert spatial : precis, concis, amical.
Reponses limitees a 3-4 phrases maximum.

Ne jamais inventer de donnees. Si tu ne sais pas, dis-le IMPORTANT - contexte actuel :
- Nous sommes en 2026
- Il y a environ 12 000 satellites actifs en orbite
- Starlink : ~7 000 satellites
- ISS : altitude ~408 km, vitesse 27600 km/h
- Tiangong (station chinoise) : altitude ~390 km."""

MODEL = "openai/gpt-oss-120b"


def load_config():
    if AI_CONFIG.exists():
        try:
            return json.loads(AI_CONFIG.read_text())
        except Exception:
            pass
    return {}


def set_api_key(key):
    cfg = load_config()
    cfg["groq_api_key"] = key.strip()
    AI_CONFIG.write_text(json.dumps(cfg, indent=2))


def has_key():
    return bool(load_config().get("groq_api_key"))


def demander(question, historique=None):
    """Pose une question a Llama 3.3 via Groq."""
    key = load_config().get("groq_api_key")
    if not key:
        return None, "Cle API Groq manquante (option 51 dans le menu)"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if historique:
        for h in historique[-6:]:
            messages.append(h)
    messages.append({"role": "user", "content": question})

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": "Bearer " + key,
                     "Content-Type": "application/json"},
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": 0.6,
                "max_tokens": 400,
            },
            timeout=20,
        )
        data = r.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"], None
        if "error" in data:
            return None, data["error"].get("message", "Erreur Groq")
        return None, "Reponse inattendue"
    except Exception as e:
        return None, str(e)


def test():
    if not has_key():
        return "❌ Cle API manquante"
    r, err = demander("Dis bonjour en 3 mots")
    if err:
        return "❌ " + err
    return "✅ Groq OK : " + r


if __name__ == "__main__":
    print("Test iss_ai.py\n")
    print("Cle API presente :", has_key())
    if has_key():
        print(test())
    else:
        print("Ajoute ta cle avec :")
        print("  python3 -c \"import iss_ai; iss_ai.set_api_key('gsk_...')\"")
