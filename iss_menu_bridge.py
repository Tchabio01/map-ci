"""iss_menu_bridge.py - Pont entre le menu terminal et le bot Telegram"""
import io
import sys
import json
from contextlib import redirect_stdout
from pathlib import Path


def _import_mapci():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mapci",
        str(Path.home() / "map-ci" / "mapci.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    import builtins
    original_input = builtins.input
    builtins.input = lambda prompt="": "0"
    try:
        spec.loader.exec_module(mod)
    finally:
        builtins.input = original_input
    return mod


_MAPCI = None


def get_mapci():
    global _MAPCI
    if _MAPCI is None:
        _MAPCI = _import_mapci()
    return _MAPCI


COMMANDES = [
    ("1", "Rechercher ville", "rechercher_ville", True, "Ville en texte"),
    ("2", "Carte OSM/Google", "afficher_carte", True, "Lat,Lon"),
    ("3", "Image GPS EXIF", "extraire_gps_exif", True, "Chemin image"),
    ("4", "Meteo actuelle", "meteo_actuelle", True, "Ville"),
    ("5", "Meteo 7 jours", "meteo_7_jours", True, "Ville"),
    ("6", "Qualite air", "qualite_air", True, "Ville"),
    ("7", "Ma position IP", "ma_position_ip", False, ""),
    ("8", "Distance itineraire", "distance_itineraire", True, "Lat1,Lon1,Lat2,Lon2"),
    ("9", "Position ISS", "position_iss", False, ""),
    ("10", "Fuseaux horaires", "fuseaux_horaires", True, "Ville"),
    ("11", "Altitude lieu", "altitude_lieu", True, "Ville"),
    ("12", "Points d interet", "points_interet", True, "Ville,Categorie"),
    ("13", "Phase de la Lune", "phase_lune", False, ""),
    ("14", "Lancements spatiaux", "lancements_spatiaux", False, ""),
    ("15", "QR code position", "qr_code_position", True, "Lat,Lon"),
    ("16", "Export GPX", "export_gpx", True, "Lat,Lon,Nom"),
    ("17", "Tableau de bord", "tableau_de_bord", False, ""),
    ("19", "Golden hour", "golden_hour", True, "Lat"),
    ("20", "Seismes recents", "seismes_recents", False, ""),
    ("21", "Coords aleatoires", "coords_aleatoires", False, ""),
    ("25", "Historique", "afficher_historique", False, ""),
    ("26", "Parametres", "parametres", False, ""),
    ("43", "Aurores boreales", "menu_aurores", False, ""),
    ("44", "Pluies etoiles", "menu_meteors", False, ""),
    ("45", "Eclipses", "menu_eclipses", False, ""),
    ("46", "Planetes visibles", "menu_planetes", False, ""),
    ("47", "Achievements", "menu_achievements", False, ""),
    ("48", "Mes statistiques", "menu_stats", False, ""),
    ("49", "Notifications ntfy", "menu_ntfy", True, "Topic"),
    ("50", "Interface Web", "menu_web_app", False, ""),
]


def get_commandes():
    return COMMANDES


def find_commande(code):
    for c in COMMANDES:
        if c[0] == code:
            return c
    return None


def executer(code, params=None):
    cmd = find_commande(code)
    if not cmd:
        return False, "Commande " + code + " inconnue"

    num, label, fname, needs_input, desc = cmd
    mapci = get_mapci()

    if not hasattr(mapci, fname):
        return False, "Fonction " + fname + " non trouvee"

    func = getattr(mapci, fname)

    import builtins
    original_input = builtins.input
    params_iter = iter(params or [])

    def fake_input(prompt=""):
        try:
            return next(params_iter)
        except StopIteration:
            return ""

    builtins.input = fake_input

    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            func()
        ok = True
    except Exception as e:
        buf.write("\n[ERREUR] " + str(e))
        ok = False
    finally:
        builtins.input = original_input

    output = buf.getvalue().strip()
    if not output:
        output = "(pas de sortie)"
    return ok, output


def liste_pour_bot(page=0, per_page=10):
    total = len(COMMANDES)
    start = page * per_page
    end = min(start + per_page, total)
    chunk = COMMANDES[start:end]

    txt = "🖥️ *Menu terminal* (" + str(start+1) + "-" + str(end) + "/" + str(total) + ")\n\n"
    for num, label, fname, needs_input, desc in chunk:
        marker = " 📝" if needs_input else ""
        txt += "*" + num + ".* " + label + marker + "\n"
        if desc:
            txt += "   _" + desc + "_\n"
    txt += "\n_📝 = necessite des parametres_"
    return txt


def keyboard_pour_bot(page=0, per_page=10):
    total = len(COMMANDES)
    start = page * per_page
    end = min(start + per_page, total)
    chunk = COMMANDES[start:end]

    rows = []
    for i in range(0, len(chunk), 2):
        row = []
        for j in range(2):
            if i + j < len(chunk):
                num, label, _, needs_input, _ = chunk[i + j]
                short = label[:18]
                row.append({"text": num + ". " + short, "callback_data": "term_" + num})
        rows.append(row)

    nav = []
    if page > 0:
        nav.append({"text": "◀️ Prec.", "callback_data": "term_page_" + str(page-1)})
    if end < total:
        nav.append({"text": "Suiv. ▶️", "callback_data": "term_page_" + str(page+1)})
    if nav:
        rows.append(nav)

    rows.append([{"text": "◀️ Menu principal", "callback_data": "menu"}])
    return {"inline_keyboard": rows}


if __name__ == "__main__":
    print("Test iss_menu_bridge.py\n")
    print(str(len(COMMANDES)) + " commandes disponibles\n")

    print("Test 1 - Position ISS...")
    ok, out = executer("9")
    print("  OK=" + str(ok))
    print("  " + out[:200])

    print("\nTest 2 - Recherche ville (abidjan)...")
    ok, out = executer("1", ["abidjan"])
    print("  OK=" + str(ok))
    print("  " + out[:200])
