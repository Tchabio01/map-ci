"""iss_live.py - Lives NASA TV + Cameras ISS"""
from datetime import datetime, timezone

LIVES = [
    ("NASA TV Public", "https://www.nasa.gov/multimedia/nasatv/#public",
     "Chaine principale NASA 24/7"),
    ("ISS Live HD", "https://www.youtube.com/watch?v=P9C25Un7xoE",
     "Vue directe depuis l'ISS (camera externe)"),
    ("NASA TV Media", "https://www.nasa.gov/multimedia/nasatv/#media",
     "Conferences de presse et evenements"),
    ("Live HDEV", "https://eol.jsc.nasa.gov/ESRS/HDEV/",
     "Camera HDEV (vue de la Terre)"),
    ("Live ISS Tracker", "https://www.astroviewer.net/iss/en/",
     "Suivi 3D en direct de l'ISS"),
]


def liste_lives():
    return LIVES


def texte_lives():
    txt = ["🎬 *Lives NASA / ISS*", ""]
    for nom, url, desc in LIVES:
        txt.append(f"• *{nom}*")
        txt.append(f"  _{desc}_")
        txt.append(f"  [Ouvrir]({url})")
        txt.append("")
    return "\n".join(txt)


if __name__ == "__main__":
    print(texte_lives())
