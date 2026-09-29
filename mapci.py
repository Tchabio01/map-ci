#!/data/data/com.termux/files/usr/bin/python
# ============================================================
#   MAP-CI V6 ULTIMATE - Cartographie GPS EXIF Live
#   Toutes fonctions : voyage, meteo, photo, espace, jeux
# ============================================================

import os, sys, json, subprocess, math, random, time, shutil
import socket, select, tty, termios
from pathlib import Path
from datetime import datetime, date

try:
    import requests
except ImportError:
    print("pip install requests"); sys.exit(1)

try:
    from rich.console import Console
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    class Console:
        def print(self, *a, **k): print(*a)
    console = Console()

# --- Chemins ---
HOME = Path.home()
DIR = HOME / ".mapci"
DIR.mkdir(exist_ok=True)
FAV = DIR / "favoris.txt"; FAV.touch(exist_ok=True)
LOG = DIR / "history.log"; LOG.touch(exist_ok=True)
CFG = DIR / "config.json"
if not CFG.exists():
    CFG.write_text('{"units":"metric","lang":"fr"}')

def load_cfg():
    try: return json.loads(CFG.read_text())
    except: return {"units":"metric","lang":"fr"}
def save_cfg(c): CFG.write_text(json.dumps(c, indent=2))
def log(msg):
    try:
        with LOG.open("a") as f:
            f.write(f"[{datetime.now():%F %T}] {msg}\n")
    except: pass

# --- Banniere ---
BANNER = (
    "╔══════════════════════════════════════╗\n"
    "║        🗺️  M A P - C I   V 6          ║\n"
    "║   ────────────────────────────────    ║\n"
    "║   Cartographie • GPS • EXIF • Live    ║\n"
    "╚══════════════════════════════════════╝"
)

def clear_screen():
    print("\033[2J\033[H", end="")

def banner():
    clear_screen()
    if HAS_RICH:
        console.print(BANNER, style="bold cyan")
    else:
        print(BANNER)

def pause():
    try: input("\n⏎  Appuyez sur Entrée...")
    except: pass

def ask(p):
    try: return input(p).strip()
    except: return ""

# --- Reseau ---
UA = {"User-Agent": "MapCI/6.0 (Termux)"}

def safe_get(url, params=None, timeout=10, headers=None):
    try:
        r = requests.get(url, params=params, headers=headers or UA, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return None

# --- Ocean ---
def ocean_name(lat, lon):
    try:
        lat = float(lat); lon = float(lon)
    except: return "Zone inconnue"
    if lat <= -60: return "Ocean Austral"
    if lat >= 60:  return "Ocean Arctique"
    if -70 < lon < 20:   return "Ocean Atlantique"
    if 20 < lon < 100:   return "Ocean Indien"
    if 100 < lon < 180:  return "Ocean Pacifique"
    if -180 < lon < -70: return "Ocean Pacifique"
    return "Zone maritime"

def reverse_info(lat, lon):
    d = safe_get("https://nominatim.openstreetmap.org/reverse",
                 params={"lat": lat, "lon": lon, "format": "json",
                         "zoom": 10, "accept-language": "fr"})
    if d and d.get("display_name"):
        name = d["display_name"]
        print("  🌍 " + name[:60])
        return name
    print(f"  🌊 {ocean_name(lat, lon)} (pas d'adresse)")
    print(f"  📍 {lat} , {lon}")
    return None

# ============================================================
#   CARTE (choix navigateur / Google / MapSCII)
# ============================================================
def mapterra(lat=None, lon=None):
    if lat is None: lat = ask("Latitude : ")
    if lon is None: lon = ask("Longitude : ")
    if not lat or not lon: return

    clear_screen()
    print(f"🗺️  Carte : {lat} , {lon}\n")
    print("  1  Navigateur (OSM)")
    print("  2  Google Maps")
    print("  3  MapSCII (ASCII)")
    print("  4  Copier coords")
    print("  Entree Retour")
    a = ask("  Choix : ")

    if a == "1":
        url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=13/{lat}/{lon}"
        try:
            subprocess.run(["termux-open-url", url], timeout=10)
            print("\n✔ Ouvert dans le navigateur")
        except Exception as e:
            print(f"\n⚠  {e}\n  URL : {url}")
    elif a == "2":
        url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        try:
            subprocess.run(["termux-open-url", url], timeout=10)
            print("\n✔ Ouvert dans Google Maps")
        except Exception as e:
            print(f"\n⚠  {e}\n  URL : {url}")
    elif a == "3":
        mapterra_terminal(lat, lon); return
    elif a == "4":
        print(f"\n  📋 {lat},{lon}")
    else:
        return
    pause()

def mapterra_terminal(lat, lon):
    clear_screen()
    print(f"🗺️  MapSCII → {lat},{lon}")
    print("   Fleches=bouger | a/z=zoom | q=quitter")
    time.sleep(2)

    IAC, DONT, DO, WONT, WILL = 255, 254, 253, 252, 251
    SB, SE, NAWS = 250, 240, 31

    try:
        s = socket.create_connection(("mapscii.me", 23), timeout=15)
    except Exception as e:
        print("❌ Connexion :", e); pause(); return

    def strip_iac(data):
        out = bytearray(); i = 0; n = len(data)
        while i < n:
            b = data[i]
            if b == IAC:
                if i+1 >= n: break
                cmd = data[i+1]
                if cmd in (DO, DONT, WILL, WONT):
                    if i+2 >= n: break
                    opt = data[i+2]
                    if cmd == DO:
                        try: s.sendall(bytes([IAC, WONT, opt]))
                        except: pass
                    elif cmd == WILL:
                        try: s.sendall(bytes([IAC, DONT, opt]))
                        except: pass
                    i += 3
                elif cmd == SB:
                    j = i + 2
                    while j < n-1:
                        if data[j] == IAC and data[j+1] == SE: break
                        j += 1
                    i = j + 2
                elif cmd == IAC:
                    out.append(IAC); i += 2
                else: i += 2
            else:
                out.append(b); i += 1
        return bytes(out)

    cols, rows = 80, 24
    naws = bytes([IAC, SB, NAWS,
                  (cols>>8)&0xFF, cols&0xFF,
                  (rows>>8)&0xFF, rows&0xFF, IAC, SE])
    try: s.sendall(naws)
    except: pass
    try: s.sendall(f"g {lat} {lon}\n".encode())
    except: pass

    try: old_term = termios.tcgetattr(sys.stdin)
    except: old_term = None
    try: tty.setraw(sys.stdin.fileno())
    except: pass
    s.settimeout(None)

    try:
        while True:
            r, _, _ = select.select([s, sys.stdin], [], [])
            if s in r:
                data = s.recv(65536)
                if not data: break
                clean = strip_iac(data)
                if clean:
                    try:
                        sys.stdout.buffer.write(clean)
                        sys.stdout.buffer.flush()
                    except: pass
            if sys.stdin in r:
                ch = sys.stdin.read(1)
                if ch in ("q", "\x03", "\x04"): break
                try: s.sendall(ch.encode())
                except: break
    except KeyboardInterrupt: pass
    except Exception as e: print("\n⚠ ", e)
    finally:
        if old_term:
            try: termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_term)
            except: pass
        try: s.close()
        except: pass
    clear_screen(); pause()

# ============================================================
#   1. RECHERCHE VILLE
# ============================================================
def search_city():
    banner()
    q = ask("🔎 Nom de la ville : ")
    if not q: return
    log(f"SEARCH:{q}")
    print("⏳ Recherche...")
    data = safe_get("https://nominatim.openstreetmap.org/search",
                    params={"q": q, "format": "json", "limit": 5})
    if not data:
        pause(); return
    for i, r in enumerate(data, 1):
        print(f"  [{i}] {r['display_name'][:48]}")
        print(f"      📍 {r['lat'][:8]} , {r['lon'][:8]}")
    print("\n  o) 🗺️  Carte   m) 🌦️  Meteo   M) 📅 7j")
    print("  g) 📸 Golden  f) 📌 Favori   t) 🌐 Fuseau")
    a = ask("  Action : ").lower()
    if a in ("o","m","m","g","f","t"):
        try:
            idx = int(ask("  Numero : ")) - 1
            r = data[idx]
        except: return
        city_name = r["display_name"].split(",")[0]
        if a == "o": mapterra(r["lat"], r["lon"])
        elif a == "m": meteo(city_name)
        elif a == "g": golden(r["lat"], r["lon"])
        elif a == "t": fuseaux(city_name)
        elif a == "f":
            with FAV.open("a") as f:
                f.write(f"{r['display_name']}|{r['lat']}|{r['lon']}\n")
            print("✔ Ajoute aux favoris")
    pause()

# ============================================================
#   3. IMAGE GPS EXIF (avec carte de toutes les photos)
# ============================================================
def exif_img():
    banner()
    if not shutil.which("exiftool"):
        print("⚠  pkg install exiftool"); pause(); return
    p = Path(ask("📷 Image ou dossier : ")).expanduser()
    if not p.exists():
        print("Introuvable :", p); pause(); return

    if p.is_dir():
        # Scanner toutes les images
        imgs = []
        for ext in ("*.jpg","*.jpeg","*.png","*.heic","*.tif","*.webp"):
            imgs.extend(p.rglob(ext))
        if not imgs:
            print("Aucune image."); pause(); return

        # Recupere les coordonnees de chaque image
        geo = []
        print(f"⏳ Analyse de {len(imgs)} images...\n")
        for im in imgs:
            lat = subprocess.run(["exiftool","-c","%.6f","-GPSLatitude","-s3",str(im)],
                                 capture_output=True, text=True).stdout.strip()
            lon = subprocess.run(["exiftool","-c","%.6f","-GPSLongitude","-s3",str(im)],
                                 capture_output=True, text=True).stdout.strip()
            latr = subprocess.run(["exiftool","-GPSLatitudeRef","-s3",str(im)],
                                  capture_output=True, text=True).stdout.strip()
            lonr = subprocess.run(["exiftool","-GPSLongitudeRef","-s3",str(im)],
                                  capture_output=True, text=True).stdout.strip()
            if lat and lon:
                if latr == "S": lat = "-" + lat.lstrip("-")
                if lonr == "W": lon = "-" + lon.lstrip("-")
                geo.append({"file": im, "lat": lat, "lon": lon})

        if not geo:
            print("Aucune image avec donnees GPS."); pause(); return

        print(f"📍 {len(geo)}/{len(imgs)} photo(s) geolocalisee(s) :\n")
        for i, g in enumerate(geo, 1):
            print(f"  [{i}] {g['file'].name[:35]}")
            print(f"      {g['lat']} , {g['lon']}")

        print("\n  v) Voir photo sur carte")
        print("  a) Afficher TOUTES sur une carte")
        print("  c) Copier toutes les coords")
        print("  e) Export GPX")
        print("  Entree) Retour")
        a = ask("  Action : ").lower()

        if a == "v":
            try:
                n = int(ask("  Numero : ")) - 1
                mapterra(geo[n]["lat"], geo[n]["lon"])
            except: pause()
        elif a == "a":
            # Genere un lien OSM avec tous les marqueurs (via umap ou bbox)
            lats = [float(g["lat"]) for g in geo]
            lons = [float(g["lon"]) for g in geo]
            lat_min, lat_max = min(lats), max(lats)
            lon_min, lon_max = min(lons), max(lons)
            url = (f"https://www.openstreetmap.org/"
                   f"?bbox={lon_min},{lat_min},{lon_max},{lat_max}")
            print(f"\n  🌍 BBox : {lat_min:.3f},{lon_min:.3f} → {lat_max:.3f},{lon_max:.3f}")
            print(f"  📋 {len(geo)} points")
            print(f"  URL : {url}")
            if ask("  Ouvrir ? (o/n) : ").lower() == "o":
                try: subprocess.run(["termux-open-url", url], timeout=10)
                except: pass
            # Genere aussi un fichier KML
            kml = DIR / "photos.kml"
            with kml.open("w") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n')
                for g in geo:
                    f.write(f'<Placemark><name>{g["file"].name}</name>\n')
                    f.write(f'<Point><coordinates>{g["lon"]},{g["lat"]},0</coordinates></Point>\n')
                    f.write('</Placemark>\n')
                f.write('</Document></kml>\n')
            print(f"  ✔ KML sauvegarde : {kml}")
            pause()
        elif a == "c":
            print()
            for g in geo:
                print(f"  {g['file'].name[:30]} : {g['lat']},{g['lon']}")
            pause()
        elif a == "e":
            gpx = DIR / "photos.gpx"
            with gpx.open("w") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<gpx version="1.1" creator="MapCI">\n')
                for g in geo:
                    f.write(f'<wpt lat="{g["lat"]}" lon="{g["lon"]}">\n')
                    f.write(f'<name>{g["file"].name}</name>\n</wpt>\n')
                f.write('</gpx>\n')
            print(f"\n  ✔ GPX sauvegarde : {gpx}")
            print(f"  → Importable dans Google Earth, GPS, etc.")
            pause()
        return

    # Image unique
    out = subprocess.run(["exiftool", str(p)], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if any(k in line for k in ("GPS","Date","Model","Make","ISO","Exposure","Focal")):
            print("  " + line[:60])
    lat = subprocess.run(["exiftool","-c","%.6f","-GPSLatitude","-s3",str(p)],
                         capture_output=True, text=True).stdout.strip()
    lon = subprocess.run(["exiftool","-c","%.6f","-GPSLongitude","-s3",str(p)],
                         capture_output=True, text=True).stdout.strip()
    latr = subprocess.run(["exiftool","-GPSLatitudeRef","-s3",str(p)],
                          capture_output=True, text=True).stdout.strip()
    lonr = subprocess.run(["exiftool","-GPSLongitudeRef","-s3",str(p)],
                          capture_output=True, text=True).stdout.strip()
    if lat and lon:
        if latr == "S": lat = "-" + lat.lstrip("-")
        if lonr == "W": lon = "-" + lon.lstrip("-")
        print(f"\n📍 {lat} , {lon}")
        print("  o) 🗺️  Carte   m) 🌦️  Meteo")
        print("  g) 📸 Golden  d) 🔢 DMS")
        print("  i) ℹ️  Info    h) 🏔️  Altitude")
        print("  r) 🛣️  Itineraire ici")
        print("  x) 🗑️  Suppr EXIF")
        a = ask("  Action : ").lower()
        if a == "o": mapterra(lat, lon)
        elif a == "m": meteo(f"{lat},{lon}")
        elif a == "g": golden(lat, lon)
        elif a == "d":
            try: to_dms(float(lat), float(lon))
            except: pass
        elif a == "i": reverse_info(lat, lon); pause()
        elif a == "h": altitude(lat, lon)
        elif a == "r": itineraire(lat, lon)
        elif a == "x":
            subprocess.run(["exiftool","-all=","-overwrite_original",str(p)])
            print("✔ EXIF supprimes")
    else:
        print("⚠  Pas de donnees GPS.")
    pause()

def to_dms(lat, lon):
    def fmt(v, pos, neg):
        d = int(abs(v)); m = (abs(v)-d)*60; mi = int(m); s = (m-mi)*60
        return f"{d}°{mi}'{s:.2f}\" {pos if v>=0 else neg}"
    print(f"  Lat : {fmt(lat,'N','S')}")
    print(f"  Lon : {fmt(lon,'E','W')}")

# ============================================================
#   4. METEO (actuelle + 7 jours + AQI)
# ============================================================
def meteo(city=None):
    if not city:
        city = ask("🌦️  Ville : ")
    if not city: return
    banner()
    try:
        subprocess.run(["curl","-s",
                        "-H","Accept-Language: fr",
                        "-A","curl/7.88.1",
                        f"https://wttr.in/{city}?lang=fr&format=v2"])
    except Exception as e:
        print("Erreur :", e)
    pause()

def meteo_7j(city=None):
    if not city:
        city = ask("📅 Ville (7 jours) : ")
    if not city: return
    banner()
    try:
        subprocess.run(["curl","-s",
                        "-H","Accept-Language: fr",
                        "-A","curl/7.88.1",
                        f"https://wttr.in/{city}?lang=fr&format=v2&compact=0"])
    except Exception as e:
        print("Erreur :", e)
    pause()

def air_quality(city=None):
    if not city:
        city = ask("💨 Ville : ")
    if not city: return
    banner()
    coords = safe_get("https://nominatim.openstreetmap.org/search",
                      params={"q": city, "format": "json", "limit": 1})
    if not coords:
        print("Ville introuvable"); pause(); return
    lat, lon = coords[0]["lat"], coords[0]["lon"]
    d = safe_get("https://air-quality-api.open-meteo.com/v1/air-quality",
                 params={"latitude": lat, "longitude": lon,
                         "current": "pm10,pm2_5,european_aqi,us_aqi"})
    if not d:
        print("Erreur API"); pause(); return
    c = d.get("current", {})
    aqi = c.get("european_aqi", 0)
    if aqi <= 20: note = "🟢 Excellent"
    elif aqi <= 40: note = "🟡 Bon"
    elif aqi <= 60: note = "🟠 Moyen"
    elif aqi <= 80: note = "🔴 Mauvais"
    else: note = "🟣 Tres mauvais"
    print(f"  💨 Qualite de l'air : {city}\n")
    print(f"  AQI Europeen : {aqi}  {note}")
    print(f"  AQI US       : {c.get('us_aqi')}")
    print(f"  PM2.5        : {c.get('pm2_5')} µg/m³")
    print(f"  PM10         : {c.get('pm10')} µg/m³")
    pause()

# ============================================================
#   5. IP
# ============================================================
def my_ip():
    banner()
    d = safe_get("https://ipinfo.io/json")
    if not d: pause(); return
    for k, v in [("🌍 Ville", d.get("city")), ("🏳️  Region", d.get("region")),
                 ("🗺️  Pays", d.get("country")), ("📍 Coords", d.get("loc")),
                 ("📡 FAI", d.get("org")), ("🕒 TZ", d.get("timezone"))]:
        print(f"  {k:12}: {v}")
    print("\n  o) 🗺️  Carte   m) 🌦️  Meteo   f) 📌 Favori")
    a = ask("  Action : ").lower()
    loc = d.get("loc", "0,0")
    lat, lon = (loc.split(",") + ["0"])[:2]
    if a == "o": mapterra(lat, lon)
    elif a == "m": meteo(d.get("city"))
    elif a == "f":
        with FAV.open("a") as f:
            f.write(f"{d.get('city')}, {d.get('country')}|{lat}|{lon}\n")
        print("✔ Ajoute")
    pause()

# ============================================================
#   6. DISTANCE + ITINERAIRE
# ============================================================
def haversine(la1, lo1, la2, lo2):
    R = 6371
    r1, r2 = math.radians(la1), math.radians(la2)
    dr = math.radians(la2-la1); dl = math.radians(lo2-lo1)
    a = math.sin(dr/2)**2 + math.cos(r1)*math.cos(r2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def get_coords(inp):
    inp = inp.strip()
    if "," in inp:
        try:
            a, b = inp.split(","); return float(a), float(b)
        except: pass
    d = safe_get("https://nominatim.openstreetmap.org/search",
                 params={"q": inp, "format": "json", "limit": 1})
    if d:
        return float(d[0]["lat"]), float(d[0]["lon"])
    return None, None

def distance():
    banner()
    a = ask("🧭 Lieu 1 : ")
    b = ask("🧭 Lieu 2 : ")
    la1, lo1 = get_coords(a); la2, lo2 = get_coords(b)
    if None in (la1, lo1, la2, lo2):
        print("❌ Introuvables"); pause(); return
    d = haversine(la1, lo1, la2, lo2)
    # Cap (direction)
    dlon = math.radians(lo2 - lo1)
    y = math.sin(dlon) * math.cos(math.radians(la2))
    x = (math.cos(math.radians(la1)) * math.sin(math.radians(la2)) -
         math.sin(math.radians(la1)) * math.cos(math.radians(la2)) * math.cos(dlon))
    brg = (math.degrees(math.atan2(y, x)) + 360) % 360
    dirs = ["N","NE","E","SE","S","SO","O","NO","N"]
    direction = dirs[int((brg+22.5) % 360 // 45)]

    print(f"\n📍 {a} → {b}")
    print(f"   📏 Distance : {d:.2f} km")
    print(f"   ✈️  Vol ~ {d/800:.1f} h")
    print(f"   🧭 Direction : {direction} ({brg:.0f}°)")
    print("  o) Carte   r) Itineraire voiture")
    c = ask("  Action : ").lower()
    if c == "o": mapterra(str((la1+la2)/2), str((lo1+lo2)/2))
    elif c == "r": osrm_route(la1, lo1, la2, lo2)
    pause()

def osrm_route(la1, lo1, la2, lo2):
    print("\n⏳ Calcul itineraire...")
    d = safe_get(f"https://router.project-osrm.org/route/v1/driving/"
                 f"{lo1},{la1};{lo2},{la2}",
                 params={"overview": "false"})
    if not d or d.get("code") != "Ok":
        print("❌ Erreur itineraire"); pause(); return
    r = d["routes"][0]
    km = r["distance"] / 1000
    h = r["duration"] / 3600
    print(f"  🛣️  Itineraire voiture")
    print(f"  📏 Distance : {km:.1f} km")
    print(f"  ⏱️  Duree    : {int(h)}h {int((h%1)*60)}min")
    pause()

def itineraire(lat=None, lon=None):
    if lat is None:
        lat = ask("Latitude arrivee : ")
        lon = ask("Longitude arrivee : ")
    if not lat or not lon: return
    print("\n📍 Point de depart :")
    d = safe_get("https://ipinfo.io/json")
    if d:
        loc = d.get("loc","0,0")
        slat, slon = (loc.split(",")+["0"])[:2]
        print(f"  {d.get('city')} ({slat},{slon})")
        osrm_route(float(slat), float(slon), float(lat), float(lon))
    else:
        print("Position introuvable"); pause()

# ============================================================
#   7. ISS
# ============================================================
def iss():
    banner()
    d = safe_get("http://api.open-notify.org/iss-now.json")
    if not d: pause(); return
    lat = d["iss_position"]["latitude"]; lon = d["iss_position"]["longitude"]
    print(f"  🛰️  Position de l'ISS\n")
    print(f"  🌍 Lat : {lat}")
    print(f"  🌍 Lon : {lon}")
    print(f"  🕒 {datetime.now():%c}\n")
    print("  o  Carte  i  Info  r  Suivi 1min")
    print("  p  Passages visibles 1h")
    a = ask("  Action : ").lower()
    if a == "o": mapterra(lat, lon)
    elif a == "i":
        print("\n  ⏳ Recherche...")
        reverse_info(lat, lon); pause()
    elif a == "r":
        for i in range(12):
            clear_screen()
            print(f"🛰️  ISS — {i+1}/12 ({5*(i+1)}s)\n")
            d = safe_get("http://api.open-notify.org/iss-now.json")
            if d:
                print(f"  Lat : {d['iss_position']['latitude']}")
                print(f"  Lon : {d['iss_position']['longitude']}")
            time.sleep(5)
        pause()
    elif a == "p":
        passe_iss()
    else:
        pause()

def passe_iss():
    banner()
    print("  🛰️  Passages visibles de l'ISS\n")
    # Utilise ta position (via IP)
    d = safe_get("https://ipinfo.io/json")
    if not d:
        print("Position introuvable"); pause(); return
    loc = d.get("loc","0,0")
    lat, lon = (loc.split(",")+["0"])[:2]
    print(f"  Position : {d.get('city')} ({lat},{lon})\n")
    # API N2YO a besoin d'une cle API, on informe l'utilisateur
    print("  ℹ️  Pour les passages visibles précis :")
    print("  → https://www.n2yo.com/passes/?s=25544")
    print("  (site web, entre tes coordonnees)")
    print()
    print(f"  Ou : https://spotthestation.nasa.gov/")
    pause()

# ============================================================
#   8. FAVORIS
# ============================================================
def favoris():
    banner()
    lines = FAV.read_text().strip().splitlines()
    if not lines:
        print("  📌 (vide)"); pause(); return
    print("  📌 Mes favoris :\n")
    for i, l in enumerate(lines, 1):
        print(f"  [{i}] {l.split('|')[0][:48]}")
    print("\n  s) Suppr  v) Voir carte  d) Distance a un favori")
    print("  r) Itineraire vers favori  Entree) Retour")
    a = ask("  Choix : ").lower()
    if a == "s":
        try:
            n = int(ask("  Numero : ")) - 1
            lines.pop(n); FAV.write_text("\n".join(lines)+"\n")
            print("✔ Supprime")
        except: pass
    elif a == "v":
        try:
            n = int(ask("  Numero : ")) - 1
            _, lat, lon = lines[n].split("|")
            mapterra(lat, lon)
        except: pass
    elif a == "r":
        try:
            n = int(ask("  Numero : ")) - 1
            _, lat, lon = lines[n].split("|")
            itineraire(lat, lon)
        except: pass
    elif a == "d":
        try:
            n = int(ask("  Numero : ")) - 1
            _, lat, lon = lines[n].split("|")
            d = safe_get("https://ipinfo.io/json")
            if d:
                mloc = d.get("loc","0,0")
                mlat, mlon = (mloc.split(",")+["0"])[:2]
                dist = haversine(float(mlat), float(mlon), float(lat), float(lon))
                print(f"\n  📏 Distance : {dist:.2f} km")
                pause()
        except: pass
    else: pause()
    if a not in ("s","v","d","r"): pass
    elif a != "v" and a != "r" and a != "d":
        pause()

# ============================================================
#   9. GOLDEN HOUR
# ============================================================
def golden(lat=None, lon=None):
    if lat is None: lat = ask("Latitude : ")
    if lon is None: lon = ask("Longitude : ")
    if not lat or not lon: return
    banner()
    d = safe_get("https://api.sunrise-sunset.org/json",
                 params={"lat": lat, "lng": lon, "formatted": 0})
    if not d or d.get("status") != "OK":
        print("Erreur API"); pause(); return
    r = d["results"]
    def conv(iso):
        try:
            return datetime.fromisoformat(iso.replace("Z","+00:00")).astimezone().strftime("%H:%M")
        except: return iso
    print("  📸 Golden / Blue hour\n")
    print("  🌅 Aube        :", conv(r["civil_twilight_begin"]))
    print("  🌄 Lever       :", conv(r["sunrise"]))
    print("  ☀️  Midi        :", conv(r["solar_noon"]))
    print("  🌇 Coucher     :", conv(r["sunset"]))
    print("  🌆 Crepuscule  :", conv(r["civil_twilight_end"]))
    print("  📏 Duree jour  :", r["day_length"], "s")
    pause()

# ============================================================
#   10. SEISMES
# ============================================================
def seismes():
    banner()
    print("  🚨 Seismes dernieres 24h (M>2.5)\n")
    d = safe_get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson")
    if not d: pause(); return
    for f in d["features"][:20]:
        p = f["properties"]
        t = datetime.fromtimestamp(p["time"]/1000).strftime("%H:%M")
        print(f"  M{p['mag']} {p['place'][:38]} [{t}]")
    pause()

# ============================================================
#   11. COORDS ALEATOIRES
# ============================================================
def random_coords():
    banner()
    lat = random.uniform(-60, 60); lon = random.uniform(-170, 170)
    print(f"  🎲 {lat:.4f} , {lon:.4f}")
    info = safe_get("https://nominatim.openstreetmap.org/reverse",
                    params={"lat": lat, "lon": lon, "format": "json"})
    if info and info.get("display_name"):
        print("  🌍 " + info["display_name"][:50])
    else:
        print("  🌊 " + ocean_name(lat, lon))
    if ask("  o) Carte : ").lower() == "o":
        mapterra(str(lat), str(lon))
    pause()

# ============================================================
#   12. JEU DEVINE VILLE
# ============================================================
def jeu():
    banner()
    lat = random.uniform(-60, 60); lon = random.uniform(-170, 170)
    print("  🎮 Devine la ville !\n")
    print(f"  🎲 Coordonnees : {lat:.4f} , {lon:.4f}")
    ask("  Ta reponse : ")
    info = safe_get("https://nominatim.openstreetmap.org/reverse",
                    params={"lat": lat, "lon": lon, "format": "json"})
    if info and info.get("display_name"):
        rep = info["display_name"][:50]
    else:
        rep = ocean_name(lat, lon)
    print("  ✔ Reponse : " + rep)
    pause()

# ============================================================
#   13. HISTORIQUE
# ============================================================
def history_menu():
    banner()
    print("  📝 Historique (30 dernieres)\n")
    for l in LOG.read_text().splitlines()[-30:]:
        print("  " + l[:50])
    pause()

# ============================================================
#   14. PARAMETRES
# ============================================================
def config():
    banner()
    c = load_cfg()
    print("  ⚙️  Parametres\n")
    print("  Config :", c)
    print()
    print("  1) Units  2) Vider historique")
    print("  3) Vider favoris  4) Retour")
    a = ask("  Choix : ")
    if a == "1":
        c["units"] = ask("metric/imperial : ")
        save_cfg(c); print("✔ Enregistre")
    elif a == "2": LOG.write_text(""); print("✔ Historique vide")
    elif a == "3": FAV.write_text(""); print("✔ Favoris vides")
    pause()

# ============================================================
#   15. FUSEAUX HORAIRES
# ============================================================
def fuseaux(ville=None):
    banner()
    if not ville:
        ville = ask("🌐 Ville : ")
    if not ville: return
    coords = safe_get("https://nominatim.openstreetmap.org/search",
                      params={"q": ville, "format": "json", "limit": 1})
    if not coords:
        print("Ville introuvable"); pause(); return
    lat, lon = coords[0]["lat"], coords[0]["lon"]
    tz = safe_get("https://timeapi.io/api/TimeZone/coordinate",
                  params={"latitude": lat, "longitude": lon})
    if tz:
        print(f"\n  🌐 Fuseau : {ville}")
        print(f"  📍 {tz.get('timeZone', '?')}")
        local = tz.get("currentLocalTime", "")
        if local:
            print(f"  🕒 Heure locale : {local[:19]}")
        # Heure locale de l'utilisateur
        print(f"  🕒 Chez toi     : {datetime.now():%H:%M}")
    pause()

# ============================================================
#   16. ALTITUDE
# ============================================================
def altitude(lat=None, lon=None):
    if lat is None:
        lat = ask("Latitude : ")
        lon = ask("Longitude : ")
    if not lat or not lon: return
    banner()
    print("⏳ Recherche altitude...")
    d = safe_get("https://api.open-elevation.com/api/v1/lookup",
                 params={"locations": f"{lat},{lon}"})
    if d and d.get("results"):
        alt = d["results"][0]["elevation"]
        print(f"\n  🏔️  Altitude : {alt} m")
        if alt < 0: note = "🌊 Sous le niveau de la mer"
        elif alt < 200: note = "🏖️  Plaine côtière"
        elif alt < 800: note = "🌾 Collines / plateau"
        elif alt < 2000: note = "⛰️  Montagne"
        elif alt < 4000: note = "🏔️  Haute montagne"
        else: note = "🗻 Everest niveau !"
        print(f"  {note}")
    else:
        print("❌ Erreur API")
    pause()

# ============================================================
#   17. POINTS D'INTERET PROCHES
# ============================================================
def poi_proches(lat=None, lon=None):
    if lat is None:
        d = safe_get("https://ipinfo.io/json")
        if not d:
            lat = ask("Latitude : "); lon = ask("Longitude : ")
        else:
            loc = d.get("loc","0,0")
            lat, lon = (loc.split(",")+["0"])[:2]
            print(f"  Position : {d.get('city')}")
    banner()
    print("  🏛️  Points d'interet proches\n")
    print("  1 Restaurants  2 Bars  3 Pharmacies")
    print("  4 Hopitaux     5 Banques  6 Supermarches")
    c = ask("  Choix : ")
    tags = {
        "1": 'amenity=restaurant', "2": 'amenity=bar',
        "3": 'amenity=pharmacy',   "4": 'amenity=hospital',
        "5": 'amenity=bank',       "6": 'shop=supermarket',
    }
    if c not in tags:
        return
    query = f"""[out:json][timeout:25];
    node[{tags[c]}](around:2000,{lat},{lon});
    out body 20;"""
    try:
        r = requests.post("https://overpass-api.de/api/interpreter",
                          data=query, timeout=30)
        d = r.json()
    except Exception as e:
        print("Erreur :", e); pause(); return
    elems = d.get("elements", [])
    if not elems:
        print("  Aucun resultat dans un rayon de 2 km.")
    else:
        print(f"  {len(elems)} resultat(s) :\n")
        for e in elems[:15]:
            name = e.get("tags", {}).get("name", "(sans nom)")
            print(f"  • {name[:50]}")
    pause()

# ============================================================
#   18. PHASE DE LA LUNE
# ============================================================
def lune():
    banner()
    now = date.today()
    y, m, d = now.year, now.month, now.day
    if m < 3:
        y -= 1; m += 12
    a = y // 100
    b = a // 4
    c = 2 - a + b
    e = int(365.25 * (y + 4716))
    f = int(30.6001 * (m + 1))
    jd = c + d + e + f - 1524.5
    days = jd - 2451550.1
    phase = (days / 29.530588853) % 1
    if phase < 0: phase += 1

    if phase < 0.03 or phase > 0.97: nom = "🌑 Nouvelle lune"
    elif phase < 0.22: nom = "🌒 Premier croissant"
    elif phase < 0.28: nom = "🌓 Premier quartier"
    elif phase < 0.47: nom = "🌔 Gibbeuse croissante"
    elif phase < 0.53: nom = "🌕 Pleine lune"
    elif phase < 0.72: nom = "🌖 Gibbeuse decroissante"
    elif phase < 0.78: nom = "🌗 Dernier quartier"
    else: nom = "🌘 Dernier croissant"
    print(f"  🌕 Phase de la Lune\n")
    print(f"  {nom}")
    print(f"  Cycle : {phase*100:.1f}%")
    # Barre de progression
    n = int(phase * 30)
    print(f"  [{'█'*n}{'░'*(30-n)}]")
    pause()

# ============================================================
#   19. LANCEMENTS SPATIAUX
# ============================================================
def lancements():
    banner()
    print("  🚀 Prochains lancements spatiaux\n")
    d = safe_get("https://ll.thespacedevs.com/2.2.0/launch/upcoming/",
                 params={"limit": 10, "format": "json"})
    if not d:
        print("Erreur API"); pause(); return
    for l in d.get("results", [])[:10]:
        name = l.get("name", "?")[:45]
        net = l.get("net", "")[:16]
        stat = l.get("status", {}).get("abbrev", "?")
        print(f"  🚀 {name}")
        print(f"     🕒 {net}  [{stat}]")
    pause()

# ============================================================
#   20. QR CODE POSITION
# ============================================================
def qr_code(lat=None, lon=None):
    if lat is None:
        lat = ask("Latitude : ")
        lon = ask("Longitude : ")
    if not lat or not lon: return
    if not shutil.which("qrencode"):
        print("⚠  pkg install qrencode"); pause(); return
    banner()
    url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}"
    print(f"  📋 QR code pour : {lat},{lon}\n")
    subprocess.run(["qrencode", "-t", "ANSIUTF8", url])
    pause()

# ============================================================
#   21. EXPORT GPX (point unique)
# ============================================================
def export_gpx(lat=None, lon=None, name="point"):
    if lat is None:
        lat = ask("Latitude : ")
        lon = ask("Longitude : ")
    if not lat or not lon: return
    gpx = DIR / f"{name}.gpx"
    with gpx.open("w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<gpx version="1.1" creator="MapCI">\n')
        f.write(f'<wpt lat="{lat}" lon="{lon}">\n')
        f.write(f'<name>{name}</name>\n</wpt>\n</gpx>\n')
    print(f"\n  ✔ GPX sauvegarde : {gpx}")
    pause()

# ============================================================
#   22. DASHBOARD (vue synthese)
# ============================================================
def dashboard():
    banner()
    print("  📊 Tableau de bord\n")
    # Position
    d = safe_get("https://ipinfo.io/json")
    if d:
        print(f"  📍 {d.get('city')}, {d.get('country')}")
        loc = d.get("loc","0,0")
        lat, lon = (loc.split(",")+["0"])[:2]
    else:
        lat, lon = "0", "0"
    # Meteo
    try:
        r = subprocess.run(["curl","-s","-A","curl/7.88.1",
                            f"https://wttr.in/{lat},{lon}?format=%C+%t"],
                           capture_output=True, text=True, timeout=10)
        print(f"  🌦️  Meteo : {r.stdout.strip()}")
    except: pass
    # ISS
    iss_d = safe_get("http://api.open-notify.org/iss-now.json")
    if iss_d:
        print(f"  🛰️  ISS : {iss_d['iss_position']['latitude']} , "
              f"{iss_d['iss_position']['longitude']}")
    # Seismes recents (dernier)
    eq = safe_get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson")
    if eq and eq.get("features"):
        p = eq["features"][0]["properties"]
        print(f"  🚨 Dernier seisme M4.5+ : {p['place'][:40]}")
    # Lune
    print(f"  🌕 Lune :", end=" ")
    now = date.today()
    y, m, dd = now.year, now.month, now.day
    if m < 3: y -= 1; m += 12
    aa = y // 100; bb = aa // 4; cc = 2 - aa + bb
    ee = int(365.25 * (y + 4716)); ff = int(30.6001 * (m + 1))
    jd = cc + dd + ee + ff - 1524.5
    ph = ((jd - 2451550.1) / 29.530588853) % 1
    if ph < 0.03 or ph > 0.97: print("🌑 Nouvelle")
    elif ph < 0.25: print("🌒 Croissant")
    elif ph < 0.53: print("🌕 Pleine proche")
    elif ph < 0.75: print("🌖 Gibbeuse")
    else: print("🌘 Decroissante")
    pause()

# ============================================================
#   23. QUIZ CAPITALES
# ============================================================
def quiz_capitales():
    banner()
    pays = [
        ("France", "Paris"), ("Japon", "Tokyo"), ("Bresil", "Brasilia"),
        ("Australie", "Canberra"), ("Canada", "Ottawa"),
        ("Egypte", "Le Caire"), ("Inde", "New Delhi"),
        ("Cote d'Ivoire", "Yamoussoukro"), ("Senegal", "Dakar"),
        ("Maroc", "Rabat"), ("Espagne", "Madrid"),
        ("Italie", "Rome"), ("Allemagne", "Berlin"),
        ("Russie", "Moscou"), ("Chine", "Pekin"),
        ("Mexique", "Mexico"), ("Argentine", "Buenos Aires"),
        ("Turquie", "Ankara"), ("Nigeria", "Abuja"),
        ("Kenya", "Nairobi"),
    ]
    score = 0
    random.shuffle(pays)
    for i, (p, cap) in enumerate(pays[:5], 1):
        print(f"\n  Question {i}/5 : Capitale de {p} ?")
        rep = ask("  Reponse : ").strip().lower()
        if rep == cap.lower():
            print("  ✔ Correct !"); score += 1
        else:
            print(f"  ✗ Mauvaise. Reponse : {cap}")
    print(f"\n  🏆 Score : {score}/5")
    pause()

# ============================================================
#   24. CHASSE AU TRESOR
# ============================================================
def chasse_tresor():
    banner()
    print("  🏴‍☠️  Chasse au tresor\n")
    print("  Je vais te donner 5 indices pour trouver un lieu.\n")
    lat = random.uniform(-60, 60); lon = random.uniform(-170, 170)
    d = safe_get("https://nominatim.openstreetmap.org/reverse",
                 params={"lat": lat, "lon": lon, "format": "json"})
    if d and d.get("address"):
        a = d["address"]
        country = a.get("country", "?")
        print(f"  Indice 1 : Pays → {country}")
        print(f"  Indice 2 : Latitude → {lat:.1f}")
        print(f"  Indice 3 : Longitude → {lon:.1f}")
        ask("\n  Devine le lieu : ")
        print(f"\n  ✔ Reponse : {d.get('display_name', '?')[:60]}")
        if ask("  Voir sur carte ? (o/n) : ").lower() == "o":
            mapterra(str(lat), str(lon))
            return
    else:
        print("  Point en pleine mer, essaie encore !")
    pause()

# ============================================================
#   MENU PRINCIPAL
# ============================================================
MENU = [
    ("1",  "🔎 Rechercher ville"),
    ("2",  "🗺️  Carte (OSM/Google/MapSCII)"),
    ("3",  "📷 Image GPS EXIF"),
    ("4",  "🌦️  Meteo actuelle"),
    ("5",  "📅 Meteo 7 jours"),
    ("6",  "💨 Qualite de l'air"),
    ("7",  "📍 Ma position (IP)"),
    ("8",  "🧭 Distance + itineraire"),
    ("9",  "🛰️  Position ISS"),
    ("10", "🌐 Fuseaux horaires"),
    ("11", "🏔️  Altitude d'un lieu"),
    ("12", "🏛️  Points d'interet"),
    ("13", "🌕 Phase de la Lune"),
    ("14", "🚀 Lancements spatiaux"),
    ("15", "📋 QR code position"),
    ("16", "📤 Export GPX"),
    ("17", "📊 Tableau de bord"),
    ("18", "📌 Favoris"),
    ("19", "📸 Golden hour"),
    ("20", "🚨 Seismes recents"),
    ("21", "🎲 Coords aleatoires"),
    ("22", "🎮 Quiz capitales"),
    ("23", "🏴‍☠️  Chasse au tresor"),
    ("24", "🎯 Jeu devine ville"),
    ("25", "📝 Historique"),
    ("26", "⚙️  Parametres"),
    ("0",  "❌ Quitter"),
]

ACTIONS = {
    "1": search_city, "2": lambda: mapterra(), "3": exif_img,
    "4": lambda: meteo(), "5": lambda: meteo_7j(),
    "6": lambda: air_quality(),
    "7": my_ip, "8": distance, "9": iss,
    "10": lambda: fuseaux(), "11": lambda: altitude(),
    "12": lambda: poi_proches(),
    "13": lune, "14": lancements, "15": lambda: qr_code(),
    "16": lambda: export_gpx(), "17": dashboard,
    "18": favoris, "19": lambda: golden(), "20": seismes,
    "21": random_coords, "22": quiz_capitales,
    "23": chasse_tresor, "24": jeu,
    "25": history_menu, "26": config,
}

def main_menu():
    while True:
        banner()
        for k, label in MENU:
            print(f"  {k:>2}. {label}")
        print("  " + "─"*30)
        c = ask("👉 Choix : ")
        if c == "0":
            print("👋 Bye !"); sys.exit(0)
        fn = ACTIONS.get(c)
        if fn:
            try: fn()
            except KeyboardInterrupt:
                print("\n(interrompu)")
            except Exception as e:
                print(f"❌ Erreur : {e}"); pause()
        else:
            print("Choix invalide"); time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n👋 Bye !")
