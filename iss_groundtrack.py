"""iss_groundtrack.py - Trace au sol de l'ISS sur 90 min"""
from datetime import datetime, timezone, timedelta


def trajectoire_sol(minutes=90, pas=2):
    """Retourne une liste de points (lat, lon, t) pour la trajectoire."""
    from iss_pass import get_iss_tle, TS
    from skyfield.api import EarthSatellite

    tle = get_iss_tle(verbose=False)
    if not tle:
        return None

    sat = EarthSatellite(tle[0], tle[1], "ISS", TS)
    now = datetime.now(timezone.utc)
    points = []
    for m in range(0, minutes + 1, pas):
        t = now + timedelta(minutes=m)
        tt = TS.from_datetime(t)
        geo = sat.at(tt).subpoint()
        points.append({
            "t": t,
            "lat": geo.latitude.degrees,
            "lon": geo.longitude.degrees,
            "min": m,
        })
    return points


def villes_traversees(points):
    """Détecte les villes proches de la trajectoire (approximation)."""
    # Villes de référence (lat, lon, nom)
    VILLES = [
        (48.85, 2.35, "Paris"), (51.50, -0.12, "Londres"),
        (40.71, -74.00, "New York"), (35.67, 139.65, "Tokyo"),
        (5.36, -4.01, "Abidjan"), (14.69, -17.44, "Dakar"),
        (-33.86, 151.20, "Sydney"), (-23.55, -46.63, "Sao Paulo"),
        (19.43, -99.13, "Mexico"), (30.04, 31.23, "Le Caire"),
        (1.35, 103.81, "Singapour"), (25.20, 55.27, "Dubai"),
        (-1.28, 36.81, "Nairobi"), (-26.20, 28.04, "Johannesburg"),
    ]
    trouvees = []
    for v_lat, v_lon, nom in VILLES:
        for p in points:
            d_lat = abs(p["lat"] - v_lat)
            d_lon = abs(p["lon"] - v_lon)
            if d_lat < 3 and d_lon < 3:
                trouvees.append((nom, p["min"]))
                break
    return trouvees


def texte_trajectoire(minutes=90):
    points = trajectoire_sol(minutes=minutes)
    if not points:
        return "Erreur : impossible de recuperer les TLE"

    txt = ["🗺️ *Trajectoire ISS au sol*", ""]
    txt.append(f"📍 *{len(points)} points* sur {minutes} min\n")

    villes = villes_traversees(points)
    if villes:
        txt.append("🏙️ *Villes survolees :*")
        for nom, m in villes:
            txt.append(f"   • {nom} (dans ~{m} min)")
        txt.append("")

    # Echantillons
    txt.append("*Position prévue :*")
    for p in points[::max(1, len(points)//6)][:7]:
        lat_dir = "N" if p["lat"] > 0 else "S"
        lon_dir = "E" if p["lon"] > 0 else "O"
        txt.append(f"   +{p['min']:>2} min : {abs(p['lat']):.1f}°{lat_dir}, {abs(p['lon']):.1f}°{lon_dir}")

    return "\n".join(txt)


if __name__ == "__main__":
    print(texte_trajectoire(90))
