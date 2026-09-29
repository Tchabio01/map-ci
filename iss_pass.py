# iss_pass.py — Calcul local des passages ISS via Skyfield
# v3.0 — Azimut (direction) + distance
import os
from datetime import datetime, timedelta
from pathlib import Path
from skyfield.api import load, wgs84, EarthSatellite

TLE_CACHE = Path.home() / '.mapci_tle.txt'
TS = load.timescale()
EPHEMERIS = load('de421.bsp')

TLE_SOURCES = [
    "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle",
    "https://retlector.eu/tle/active.txt",
]

CARDINALS = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']

def az_to_cardinal(az):
    idx = int((az + 22.5) / 45) % 8
    return CARDINALS[idx]

def _extract_iss_tle(text):
    if not text:
        return None
    lines = [l.rstrip() for l in text.strip().split('\n') if l.strip()]
    for i, line in enumerate(lines):
        if line.startswith('1 ') and i+1 < len(lines) and lines[i+1].startswith('2 '):
            nom = lines[i-1] if i > 0 else ""
            if 'ISS' in nom.upper() or '25544' in line:
                return [line, lines[i+1]]
    return None

def get_iss_tle(verbose=True):
    if TLE_CACHE.exists():
        age = datetime.now() - datetime.fromtimestamp(TLE_CACHE.stat().st_mtime)
        if age < timedelta(hours=6):
            tle = _extract_iss_tle(TLE_CACHE.read_text())
            if tle:
                if verbose: print("  TLE depuis cache")
                return tle
    try:
        import requests
    except ImportError:
        print("  pip install requests")
        return None
    for url in TLE_SOURCES:
        try:
            if verbose: print(f"  -> {url[:40]}...", end=" ", flush=True)
            r = requests.get(url, timeout=15, headers={'User-Agent': 'MAP-CI'})
            r.raise_for_status()
            tle = _extract_iss_tle(r.text)
            if tle:
                TLE_CACHE.write_text(r.text)
                if verbose: print("OK")
                return tle
            if verbose: print("ISS absente")
        except Exception as e:
            if verbose: print(f"echec ({type(e).__name__})")
    if TLE_CACHE.exists():
        if verbose: print("  Cache expire utilise")
        return _extract_iss_tle(TLE_CACHE.read_text())
    return None

def get_next_passes(lat, lon, hours=48, min_elevation=0, verbose=True):
    tle = get_iss_tle(verbose=verbose)
    if not tle:
        print("  Impossible de recuperer les TLE.")
        return []
    iss = EarthSatellite(tle[0], tle[1], 'ISS', TS)
    station = wgs84.latlon(lat, lon, elevation_m=0)
    t0 = TS.now()
    t1 = TS.from_datetime(t0.utc_datetime() + timedelta(hours=hours))
    times, events = iss.find_events(station, t0, t1, altitude_degrees=min_elevation)
    passes = []
    for i in range(0, len(events), 3):
        if i+2 >= len(events): break
        rt, ct, st = times[i], times[i+1], times[i+2]
        diff = iss - station
        alt_r, az_r, dist_r = diff.at(rt).altaz()
        alt_c, az_c, dist_c = diff.at(ct).altaz()
        alt_s, az_s, dist_s = diff.at(st).altaz()
        passes.append({
            'risetime': rt.utc_datetime(),
            'culmination': ct.utc_datetime(),
            'settime': st.utc_datetime(),
            'duration_s': (st.utc_datetime() - rt.utc_datetime()).total_seconds(),
            'max_elevation': alt_c.degrees,
            'az_rise': az_r.degrees,
            'az_culm': az_c.degrees,
            'az_set': az_s.degrees,
            'cardinal_rise': az_to_cardinal(az_r.degrees),
            'cardinal_set': az_to_cardinal(az_s.degrees),
            'distance_km': dist_c.km,
        })
    return passes

def format_pass(p, offset_h=0, show_azimuth=True):
    rt = p['risetime'] + timedelta(hours=offset_h)
    ct = p['culmination'] + timedelta(hours=offset_h)
    st = p['settime'] + timedelta(hours=offset_h)
    base = (f"  ISS {rt:%d/%m %H:%M:%S} -> {st:%H:%M:%S}  "
            f"| {p['duration_s']:>3.0f}s "
            f"| max {p['max_elevation']:>4.1f}deg "
            f"| pic {ct:%H:%M:%S}")
    if show_azimuth:
        base += f" | {p['cardinal_rise']}->{p['cardinal_set']}"
    return base

if __name__ == "__main__":
    print("Test iss_pass.py v3.0")
    passes = get_next_passes(5.3599517, -4.0082563, verbose=True)
    print(f"\n{len(passes)} passage(s) dans les 48h :\n")
    for p in passes:
        print(format_pass(p))   
