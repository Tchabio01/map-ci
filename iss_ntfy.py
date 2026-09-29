"""iss_ntfy.py — Notifications push via ntfy.sh (gratuit, sans compte)"""
import requests
from pathlib import Path

NTFY_CONFIG = Path.home() / ".mapci_ntfy.txt"

def get_topic():
    if NTFY_CONFIG.exists():
        return NTFY_CONFIG.read_text().strip()
    return None

def set_topic(topic):
    NTFY_CONFIG.write_text(topic.strip())

def envoyer(message, titre="MAP-CI ISS", priorite="high"):
    """Envoie une notification via ntfy.sh."""
    topic = get_topic()
    if not topic:
        return False
    try:
        r = requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers={
                "Title": titre,
                "Priority": priorite,
                "Tags": "satellite",
            },
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False

if __name__ == "__main__":
    print("Test iss_ntfy.py\n")
    print("Pour utiliser ntfy.sh :")
    print("1. Installe l'app 'ntfy' sur ton téléphone (Play Store / F-Droid)")
    print("2. Abonne-toi à un topic (ex: mapci-tchabio-123)")
    print("3. Configure le topic ici")
    print()
    if get_topic():
        print(f"Topic actuel : {get_topic()}")
        if input("Envoyer test ? (o/N) : ").strip().lower() == "o":
            if envoyer("Test MAP-CI V9"):
                print("✅ Envoyé !")
    else:
        t = input("Topic ntfy (ex: mapci-tchabio-123) : ").strip()
        if t:
            set_topic(t)
            print(f"✅ Topic configuré : {t}")
            print("   → Abonne-toi dans l'app ntfy sur ton téléphone")
            print(f"   → Test : envoie un message à https://ntfy.sh/{t}")
