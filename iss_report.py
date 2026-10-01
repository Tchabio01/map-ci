"""iss_report.py - Génère un rapport PDF mensuel"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

OBS_FILE = Path.home() / ".mapci_observations.json"
ALARM_FILE = Path.home() / ".mapci_alarm.json"
PDF_DIR = Path.home() / "mapci_rapports"


def _load(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return default


def collecter_stats():
    obs = _load(OBS_FILE, [])
    cfg = _load(ALARM_FILE, {})
    vus = [o for o in obs if o.get("statut") == "vu"]
    rates = [o for o in obs if o.get("statut") == "rate"]

    # Observations des 30 derniers jours
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    recents = [o for o in vus if o.get("risetime", "") >= cutoff]

    villes = {}
    for o in vus:
        v = o.get("lieu", "?")
        villes[v] = villes.get(v, 0) + 1

    meilleur = max(vus, key=lambda o: o.get("elevation", 0)) if vus else None

    return {
        "total": len(obs),
        "vus": len(vus),
        "rates": len(rates),
        "recents": len(recents),
        "villes": villes,
        "meilleur": meilleur,
        "lieu_principal": cfg.get("lieu", "?"),
    }


def generer_texte():
    s = collecter_stats()
    now = datetime.now(timezone.utc)
    txt = []
    txt.append("=" * 56)
    txt.append("RAPPORT MAP-CI".center(56))
    txt.append("=" * 56)
    txt.append(f"Genere le {now:%d/%m/%Y a %H:%M} UTC")
    txt.append("")
    txt.append(f"Position principale : {s['lieu_principal']}")
    txt.append("")
    txt.append("-" * 56)
    txt.append("STATISTIQUES GLOBALES")
    txt.append("-" * 56)
    txt.append(f"  Total observations     : {s['total']}")
    txt.append(f"  Passages vus           : {s['vus']}")
    txt.append(f"  Passages rates         : {s['rates']}")
    txt.append(f"  Ces 30 derniers jours  : {s['recents']}")
    if s['vus'] > 0:
        taux = round(s['vus'] / max(1, s['vus'] + s['rates']) * 100, 1)
        txt.append(f"  Taux de reussite       : {taux}%")
    txt.append("")
    if s['villes']:
        txt.append("-" * 56)
        txt.append("VILLES OBSERVEES")
        txt.append("-" * 56)
        for v, n in sorted(s['villes'].items(), key=lambda x: -x[1]):
            bar = "#" * min(40, n)
            txt.append(f"  {v:<15} {n:>3}  {bar}")
        txt.append("")
    if s['meilleur']:
        m = s['meilleur']
        txt.append("-" * 56)
        txt.append("MEILLEUR PASSAGE")
        txt.append("-" * 56)
        txt.append(f"  Date       : {m.get('risetime', '?')[:16]}")
        txt.append(f"  Lieu       : {m.get('lieu', '?')}")
        txt.append(f"  Elevation  : {m.get('elevation', '?')} deg")
        if m.get('magnitude'):
            txt.append(f"  Magnitude  : {m['magnitude']}")
        txt.append("")
    txt.append("=" * 56)
    txt.append("Bon ciel et bons passages !")
    txt.append("=" * 56)
    return "\n".join(txt)


def generer_pdf():
    """Genere un PDF si fpdf2 est installe, sinon TXT."""
    PDF_DIR.mkdir(exist_ok=True)
    txt_content = generer_texte()
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m")

    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Courier", size=10)
        for line in txt_content.split("\n"):
            pdf.cell(0, 5, txt=line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        path = PDF_DIR / f"rapport_{date_str}.pdf"
        pdf.output(str(path))
        return str(path)
    except ImportError:
        path = PDF_DIR / f"rapport_{date_str}.txt"
        path.write_text(txt_content, encoding="utf-8")
        return str(path)


if __name__ == "__main__":
    print(generer_texte())
    print()
    f = generer_pdf()
    print(f"Fichier : {f}")
