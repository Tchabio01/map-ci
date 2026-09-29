# iss_visibility.py — Illumination, magnitude, ASCII, météo
import math
from datetime import timedelta

try:
    import requests
except ImportError:
    requests = None

WEATHER_CODES = {
    0:"Clair",1:"Peu nuageux",2:"Partiel",3:"Couvert",
    45:"Brouillard",48:"Brouillard givrant",
    51:"Bruine legere",53:"Bruine",55:"Bruine dense",
    61:"Pluie legere",63:"Pluie",65:"Pluie forte",
    71:"Neige legere",73:"Neige",75:"Neige forte",
    80:"Averses",81:"Averses",82:"Averses violentes",
    95:"Orage",96:"Orage grele",99:"Orage violent",
}

# ---------- Météo ----------
def get_weather(lat, lon, when=None):
    """Retourne (code, nuages_pct, precip_mm, temp_c) pour l'heure du passage."""
    if requests is None:
        return None
    try:
        r = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&hourly=cloudcover,precipitation,temperature_2m,weather_code"
            "&forecast_days=3&timezone=auto",
            timeout=10,
        ).json()
        h = r.get("hourly", {})
        times = h.get("time", [])
        clouds = h.get("cloudcover", [])
        precips = h.get("precipitation", [])
        temps = h.get("temperature_2m", [])
        codes = h.get("weather_code", [])

        if when is None:
            idx = 0
        else:
            key = when.strftime("%Y-%m-%dT%H:00")
            try:
                idx = times.index(key)
            except ValueError:
                idx = 0
        return {
            "code": codes[idx] if idx < len(codes) else None,
            "clouds": clouds[idx] if idx < len(clouds) else None,
            "precip": precips[idx] if idx < len(precips) else None,
            "temp": temps[idx] if idx < len(temps) else None,
        }
    except Exception:
        return None

def meteo_verdict(weather):
    """Retourne (note, message) sur la visibilité météo."""
    if not weather or weather.get("clouds") is None:
        return ("?", "Meteo indisponible")
    clouds = weather["clouds"]
    precip = weather.get("precip", 0) or 0
    if precip > 0.5:
        return ("❌", f"Pluie ({precip:.1f} mm)")
    if clouds < 20:
        return ("✅", f"Ciel degage ({clouds:.0f}%)")
    if clouds < 50:
        return ("👍", f"Partiel ({clouds:.0f}%)")
    if clouds < 80:
        return ("⚠️", f"Nuageux ({clouds:.0f}%)")
    return ("❌", f"Couvert ({clouds:.0f}%)")

# ---------- Illumination ----------
def is_visible_from_observer(sun_alt_deg):
    """Vrai si l'observateur est dans l'obscurité (soleil < -6°)."""
    return sun_alt_deg < -6

def sun_altitude(eph, lat, lon, t):
    """Altitude du soleil pour un observateur à lat/lon à l'instant t."""
    from skyfield.api import wgs84
    observer = wgs84.latlon(lat, lon)
    sun = eph['sun']
    alt, az, _ = (sun - observer).at(t).altaz()
    return alt.degrees

# ---------- Magnitude ----------
def compute_magnitude(distance_km, sunlit=True, sun_alt_deg=-20):
    """Estimation magnitude ISS. Typique : -3.5 (très brillant) à +2 (faible)."""
    if distance_km <= 0:
        return None
    mag = -1.8 + 5 * math.log10(distance_km / 1000.0)
    if not sunlit:
        mag += 3
    if sun_alt_deg > -10:
        mag += 1.5
    return round(mag, 1)

def magnitude_label(mag):
    if mag is None: return "?"
    if mag < -3: return "⭐⭐⭐ Eclatante"
    if mag < -1: return "⭐⭐ Tres brillante"
    if mag < 0: return "⭐ Brillante"
    if mag < 2: return "· Visible"
    return "· Faible"

# ---------- Carte ASCII ----------
def sky_chart(p, width=41, height=15):
    """Carte ASCII : N en haut, S en bas, O à gauche, E à droite."""
    chart = [[' '] * width for _ in range(height)]
    for x in range(width):
        chart[0][x] = '·'
        chart[height-1][x] = '·'
    cx = width // 2
    chart[0][cx] = 'N'
    chart[height-1][cx] = 'S'
    chart[height//2][0] = 'O'
    chart[height//2][width-1] = 'E'

    def plot(az, el, sym):
        x = int((az / 360.0) * (width - 1))
        y = int((1 - el / 90.0) * (height - 1))
        x = max(1, min(width - 2, x))
        y = max(1, min(height - 2, y))
        chart[y][x] = sym

    plot(p.get('az_rise', 0), 0, 'R')
    plot(p.get('az_culm', 180), p.get('max_elevation', 45), '*')
    plot(p.get('az_set', 180), 0, 'S')

    # Trace approximative R → * → S
    return '\n'.join(''.join(r) for r in chart)

# ---------- Test ----------
if __name__ == "__main__":
    print("Test iss_visibility.py\n")
    fake = {'az_rise': 10, 'az_culm': 135, 'az_set': 200, 'max_elevation': 45}
    print(sky_chart(fake))
    print()
    for d in [400, 800, 1500]:
        m = compute_magnitude(d)
        print(f"  {d} km → mag {m:>4}  {magnitude_label(m)}")
    print("\nTest meteo Abidjan :")
    w = get_weather(5.3599517, -4.0082563)
    if w:
        note, msg = meteo_verdict(w)
        print(f"  {note} {msg}  | temp {w['temp']}°C")
    else:
        print("  Meteo indisponible")
