"""iss_search.py - Recherche globale dans les donnees MAP-CI"""
import json
from pathlib import Path

DATA_FILES = {
    "historique": Path.home() / ".mapci_historique.json",
    "favoris": Path.home() / ".mapci_favoris.json",
    "observations": Path.home() / ".mapci_observations.json",
    "todos": Path.home() / ".mapci_todos.json",
    "positions": Path.home() / ".mapci_positions.json",
}

EMOJIS = {"historique": "📝", "favoris": "📌",
          "observations": "👁️", "todos": "📋", "positions": "📍"}
LABELS = {"historique": "Historique", "favoris": "Favori",
          "observations": "Observation", "todos": "Todo", "positions": "Position"}


def load_json(p, default=None):
    if not p.exists():
        return default if default is not None else []
    try:
        return json.loads(p.read_text())
    except Exception:
        return []


def chercher(query, max_results=20):
    q = query.lower().strip()
    if not q:
        return []
    results = []
    for cat_key, path in DATA_FILES.items():
        for item in load_json(path):
            blob = json.dumps(item, ensure_ascii=False).lower()
            if q in blob:
                results.append((EMOJIS[cat_key] + " " + LABELS[cat_key], item))
    return results[:max_results]


def format_resultats(results, query):
    if not results:
        return "🔍 Aucun résultat pour _" + query + "_\n\n_Essaie : abidjan, ISS, observé..._"
    txt = "🔍 *" + str(len(results)) + " résultat(s)* pour _" + query + "_\n\n"
    for cat, item in results[:15]:
        txt += cat + "\n"
        for k in ["action", "nom", "texte", "lieu", "details", "note"]:
            if k in item:
                txt += "  " + str(item[k])[:80] + "\n"
                break
        if "date" in item:
            txt += "  _" + str(item["date"])[:19] + "_\n"
        elif "risetime" in item:
            txt += "  _" + str(item["risetime"])[:19] + "_\n"
        txt += "\n"
    return txt


if __name__ == "__main__":
    print("Test iss_search.py\n")
    r = chercher("abidjan")
    print("Resultats 'abidjan' :", len(r))
    for cat, it in r[:3]:
        print("  " + cat + " : " + str(it)[:100])
