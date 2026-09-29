"""patch_v9.py — Ajoute les modules V9 dans mapci.py"""
import ast
import shutil
from pathlib import Path

MAPCI = Path.home() / "map-ci" / "mapci.py"
BACKUP = Path.home() / "map-ci" / "mapci.py.bak9"
shutil.copy(MAPCI, BACKUP)
print(f"Backup : {BACKUP}")

src = MAPCI.read_text(encoding="utf-8")

IMPORTS = """try:
    import iss_aurora
except Exception:
    iss_aurora = None
try:
    import iss_meteors
except Exception:
    iss_meteors = None
try:
    import iss_eclipses
except Exception:
    iss_eclipses = None
try:
    import iss_planets
except Exception:
    iss_planets = None
try:
    import iss_achievements
except Exception:
    iss_achievements = None
try:
    import iss_stats
except Exception:
    iss_stats = None
try:
    import iss_ntfy
except Exception:
    iss_ntfy = None
"""

if "import iss_aurora" not in src:
    anchor = "except Exception:\n    iss_multipos = None\n"
    if anchor in src:
        src = src.replace(anchor, anchor + IMPORTS, 1)
        print("+ imports V9")
else:
    print("= imports deja presents")

FUNCS = '''

# ============================================================
# OPTIONS 43-50 - Pack V9
# ============================================================
def menu_aurores():
    if iss_aurora is None:
        print("iss_aurora non disponible")
        return
    kp = iss_aurora.get_current_kp()
    level, desc, emoji = iss_aurora.aurora_level(kp)
    print(f"\\n{emoji}  Aurores boreales")
    print("-" * 44)
    print(f"Kp actuel : {kp} - {level}")
    print(f"-> {desc}")
    print()
    print("Previsions (3h / ligne) :")
    fc = iss_aurora.get_kp_forecast()
    if fc:
        for f in fc[:8]:
            bar = "#" * int(f["kp"] * 3)
            print(f"  {f['time'][:16]:<17} Kp {f['kp']:.1f}  {bar}")


def menu_meteors():
    if iss_meteors is None:
        print("iss_meteors non disponible")
        return
    print("\\nProchaines pluies d'etoiles filantes :\\n")
    for m in iss_meteors.prochains_meteors(10):
        emoji = "***" if m["zhr"] > 80 else "**" if m["zhr"] > 30 else "-"
        print(f"  {emoji} {m['nom']:<20} {m['date']:%d/%m/%Y}  "
              f"dans {m['jours']:>3}j  ZHR {m['zhr']:>3}  ({m['radiant']})")


def menu_eclipses():
    if iss_eclipses is None:
        print("iss_eclipses non disponible")
        return
    print("\\nProchaines eclipses :\\n")
    for e in iss_eclipses.prochaines_eclipses(10):
        emoji = "LUNE" if "Lunaire" in e["type"] else "SOLEIL"
        print(f"  [{emoji}] {e['date']:%d/%m/%Y}  {e['type']:<20}  "
              f"dans {e['jours']:>4}j  |  {e['region']}")


def menu_planetes():
    if iss_planets is None:
        print("iss_planets non disponible")
        return
    lat = iss_alarm.config.get("lat")
    lon = iss_alarm.config.get("lon")
    if lat is None:
        print("Position requise")
        return
    print("\\nPlanetes visibles maintenant :\\n")
    ps = iss_planets.visibles_ce_soir(lat, lon)
    if not ps:
        print("  Aucune planete au-dessus de l'horizon")
        return
    for p in ps:
        print(f"  {p['nom']:<10}  alt {p['altitude']:>5.1f}deg  "
              f"{p['cardinal']:<3}  dist {p['distance_ua']} UA")


def menu_achievements():
    if iss_achievements is None:
        print("iss_achievements non disponible")
        return
    nouveaux = iss_achievements.check_achievements()
    if nouveaux:
        print(f"\\n{len(nouveaux)} nouveau(x) badge(s) !")
        for _, nom in nouveaux:
            print(f"   {nom}")
    iss_achievements.afficher()


def menu_stats():
    if iss_stats is None:
        print("iss_stats non disponible")
        return
    iss_stats.afficher()


def menu_ntfy():
    if iss_ntfy is None:
        print("iss_ntfy non disponible")
        return
    print("\\nNotifications ntfy.sh")
    print("-" * 44)
    topic = iss_ntfy.get_topic()
    if topic:
        print(f"Topic actuel : {topic}")
        if input("Tester envoi ? (o/N) : ").strip().lower() == "o":
            if iss_ntfy.envoyer("Test MAP-CI V9"):
                print("Envoye !")
    else:
        t = input("Topic ntfy (ex: mapci-tchabio-123) : ").strip()
        if t:
            iss_ntfy.set_topic(t)
            print(f"Configure : {t}")
            print(f"   Abonne-toi a https://ntfy.sh/{t} dans l'app ntfy")


def menu_web_app():
    print("\\nInterface Web MAP-CI V9")
    print("-" * 44)
    print("Lance dans un terminal separe :")
    print("  cd ~/map-ci")
    print("  python web_app.py")
    print()
    print("Puis ouvre dans un navigateur :")
    print("  Sur le telephone : http://127.0.0.1:8080/")
    print("  Depuis un autre appareil : http://<IP-TEL>:8080/")
    print()
    print("Pour trouver ton IP locale :")
    print("  ifconfig 2>/dev/null | grep inet | grep -v 127.0.0.1")

'''

if "def menu_aurores" not in src:
    marker = "# ============================================================\n# MENU\n"
    if marker in src:
        src = src.replace(marker, FUNCS + "\n" + marker, 1)
        print("+ fonctions V9")
else:
    print("= fonctions deja presentes")

OLD = '    ("42", "Widget permanent",             menu_widget),\n    ("0",  "Quitter",                      None),'
NEW = '''    ("42", "Widget permanent",             menu_widget),
    ("43", "Aurores boreales (Kp)",        menu_aurores),
    ("44", "Pluies etoiles filantes",      menu_meteors),
    ("45", "Eclipses",                     menu_eclipses),
    ("46", "Planetes visibles",            menu_planets),
    ("47", "Achievements",                 menu_achievements),
    ("48", "Mes statistiques",             menu_stats),
    ("49", "Notifications ntfy.sh",        menu_ntfy),
    ("50", "Interface Web (info)",         menu_web_app),
    ("0",  "Quitter",                      None),'''

if '"43"' not in src:
    if OLD in src:
        src = src.replace(OLD, NEW, 1)
        print("+ menu 43-50")
    else:
        print("! Bloc menu 42 introuvable")
else:
    print("= menu 43-50 deja present")

try:
    ast.parse(src)
    print("Syntaxe OK")
except SyntaxError as e:
    print(f"Erreur : {e}")
    raise SystemExit(1)

MAPCI.write_text(src, encoding="utf-8")
print("mapci.py mis a jour !")
