# iss_multisat.py — Suivi multi-satellites (ISS, Hubble, Tiangong, Starlink...)
# v1.0
from datetime import datetime, timedelta, timezone
from pathlib import Path
from skyfield.api import load, wgs84, EarthSatellite

TLE_CACHE = Path.home() / ".mapci_tle_multi.txt"
TS = load.timescale()

# Sources TLE (chaque groupe contient des satellites différents)
SOURCES = [
    ("https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle", "stations"),
    ("https://celestrak.org/NORAD/elements/gp.php?GROUP=science&FORMAT=tle", "science"),
    ("https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=tle", "weather"),
]

# Mot-clés de recherche dans les TLE
TARGETS = {
    "iss":      "ZARYA",
    "hubble":   "HST",
    "hst":      "HST",
    "tiangong": "TIANHE",
    "css":      "TIANHE",
    "starlink": "STARLINK",
    "terra":    "TERRA",
    "aqua":     "AQUA",
    "noaa":     "NOAA",
    "landsat":  "LANDSAT",
    "sentinel": "SENTINEL",
}


def _download_tles(verbose=False):
    """Télécharge et met en cache les TLE de plusieurs groupes."""
    if TLE_CACHE.exists():
        age = datetime.now() - datetime.fromtimestamp(TLE_CACHE.stat().st_mtime)
        if age < timedelta(hours=6):
            if verbose:
                print("  TLE depuis cache multi")
            return TLE_CACHE.read_text()

    try:
        import requests
    except ImportError:
        return TLE_CACHE.read_text() if TLE_CACHE.exists() else ""

    chunks = []
    for url, name in SOURCES:
        try:
            if verbose:
                print(f"  -> {name}...", end=" ", flush=True)
            r = requests.get(url, timeout=15, headers={"User-Agent": "MAP-CI/8"})
            r.raise_for_status()
            chunks.append(r.text)
            if verbose:
                print("OK")
        except Exception as e:
            if verbose:
                print(f"echec ({type(e).__name__})")
            continue

    if chunks:
        TLE_CACHE.write_text("\n".join(chunks))
        return "\n".join(chunks)
    if TLE_CACHE.exists():
        if verbose:
            print("  Cache expire utilise")
        return TLE_CACHE.read_text()
    return ""


def _find_satellite(keyword, tle_text):
    """Cherche un satellite par mot-clé. Retourne (nom, l1, l2) ou None."""
    lines = [l.rstrip() for l in tle_text.split("\n") if l.strip()]
    kw = keyword.upper()
    for i, l in enumerate(lines):
        if kw in l.upper() and i + 2 < len(lines):
            if lines[i + 1].startswith("1 ") and lines[i + 2].startswith("2 "):
                return (l, lines[i + 1], lines[i + 2])
    return None


def get_satellite_passes(target, lat, lon, hours=48, min_elev=0, verbose=False):
    """Calcule les passages d'un satellite nommé.
    Retourne (passes, info) où info est le nom ou un message d'erreur.
    """
    keyword = TARGETS.get(target.lower(), target.upper())
    tle_text = _download_tles(verbose=verbose)
    sat_data = _find_satellite(keyword, tle_text)
    if not sat_data:
        return None, f"Satellite '{target}' non trouve"

    name, l1, l2 = sat_data
    sat = EarthSatellite(l1, l2, name, TS)
    station = wgs84.latlon(lat, lon, elevation_m=0)

    t0 = TS.now()
    t1 = TS.from_datetime(t0.utc_datetime() + timedelta(hours=hours))
    times, events = sat.find_events(station, t0, t1, altitude_degrees=min_elev)

    passes = []
    for i in range(0, len(events), 3):
        if i + 2 >= len(events):
            break
        rt, ct, st = times[i], times[i + 1], times[i + 2]
        diff = sat - station
        alt_c, az_c, dist_c = diff.at(ct).altaz()
        alt_r, az_r, _ = diff.at(rt).altaz()
        alt_s, az_s, _ = diff.at(st).altaz()
        passes.append({
            "satellite": name,
            "risetime": rt.utc_datetime(),
            "culmination": ct.utc_datetime(),
            "settime": st.utc_datetime(),
            "duration_s": (st.utc_datetime() - rt.utc_datetime()).total_seconds(),
            "max_elevation": alt_c.degrees,
            "az_rise": az_r.degrees,
            "az_culm": az_c.degrees,
            "az_set": az_s.degrees,
            "distance_km": dist_c.km,
        })
    return passes, name


def list_available():
    """Liste les satellites disponibles dans le cache."""
    text = _download_tles()
    lines = [l.rstrip() for l in text.split("\n") if l.strip()]
    names = []
    for i, l in enumerate(lines):
        if (not l.startswith(" ") and not l.startswith("1 ")
                and not l.startswith("2 ")):
            if i + 2 < len(lines) and lines[i + 1].startswith("1 "):
                names.append(l)
    return names


def az_to_cardinal(az):
    """Convertit un azimut en point cardinal."""
    CARDINALS = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    idx = int((az + 22.5) / 45) % 8
    return CARDINALS[idx]


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("Test iss_multisat.py\n")

    print("Satellites disponibles (extrait) :")
    names = list_available()
    for n in names[:15]:
        print(f"  - {n}")
    print(f"  ... {len(names)} au total\n")

    lat, lon = 5.3599517, -4.0082563  # Abidjan
    print(f"Recherche de passages au-dessus d'Abidjan ({lat}, {lon})...\n")

    for target in ["iss", "hubble", "tiangong", "noaa"]:
        print(f"=== {target} ===")
        try:
            passes, info = get_satellite_passes(target, lat, lon, hours=24, verbose=True)
            if passes:
                print(f"✅ {info} : {len(passes)} passage(s) dans 24h")
                for p in passes[:3]:
                    rise_c = az_to_cardinal(p["az_rise"])
                    set_c = az_to_cardinal(p["az_set"])
                    print(f"   {p['risetime']:%d/%m %H:%M} UTC | "
                          f"max {p['max_elevation']:>4.0f}° | "
                          f"{rise_c}->{set_c} | "
                          f"{p['duration_s']:.0f}s")
            else:
                print(f"❌ {info}")
        except Exception as e:
            print(f"❌ Erreur {target} : {e}")
        print()
