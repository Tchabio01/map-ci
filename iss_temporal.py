"""iss_temporal.py - Passages par periode"""
from datetime import datetime, timezone, timedelta


def _load_alarm():
    import json
    from pathlib import Path
    p = Path.home() / ".mapci_alarm.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return {}


def passages_periode(periode="jour"):
    """periode : 'jour', 'demain', 'semaine'"""
    cfg = _load_alarm()
    lat = cfg.get("lat")
    lon = cfg.get("lon")
    if lat is None:
        return None, "Position non configurée"

    try:
        from iss_pass import get_next_passes
        hours = {"jour": 24, "demain": 48, "semaine": 168}.get(periode, 24)
        passes = get_next_passes(lat, lon, hours=hours, min_elevation=0, verbose=False)
    except Exception as e:
        return None, str(e)

    now = datetime.now(timezone.utc)
    filtered = []
    for p in passes:
        delta_h = (p["risetime"] - now).total_seconds() / 3600
        if periode == "jour" and 0 <= delta_h < 24:
            filtered.append(p)
        elif periode == "demain" and 24 <= delta_h < 48:
            filtered.append(p)
        elif periode == "semaine" and 0 <= delta_h < 168:
            filtered.append(p)
    return filtered, None


def texte_periode(periode="jour"):
    passes, err = passages_periode(periode)
    if err:
        return f"❌ {err}"
    if not passes:
        return f"Aucun passage prévu ({periode})."

    titres = {
        "jour": "🛰️ *Passages aujourd'hui*",
        "demain": "🛰️ *Passages demain*",
        "semaine": "🛰️ *Passages cette semaine*",
    }
    txt = [titres.get(periode, "Passages"), ""]

    # Grouper par jour
    from collections import defaultdict
    par_jour = defaultdict(list)
    for p in passes:
        jour = p["risetime"].strftime("%A %d/%m")
        par_jour[jour].append(p)

    for jour, plist in par_jour.items():
        txt.append(f"*{jour}*")
        for p in plist:
            emoji = "🟢" if p["max_elevation"] > 60 else "🟡" if p["max_elevation"] > 20 else "⚪"
            txt.append(
                f"  {emoji} {p['risetime']:%H:%M} UTC — "
                f"max {p['max_elevation']:.0f}° — "
                f"{p.get('cardinal_rise', '?')}→{p.get('cardinal_set', '?')}"
            )
        txt.append("")

    txt.append(f"_Total : {len(passes)} passage(s)_")
    return "\n".join(txt)


if __name__ == "__main__":
    print(texte_periode("jour"))
