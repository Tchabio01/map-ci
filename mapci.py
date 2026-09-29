#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAP-CI V6.2 — Cartographie • GPS • EXIF • Live
Alarme ISS + Géocodeur Photon-only + Cache local
"""

import os
import sys
import json
import math
import time
import random
import shutil
import threading
try:
    import iss_alerts
except Exception:
    iss_alerts = None
try:
    import iss_visibility
except Exception:
    iss_visibility = None
try:
    import iss_notify
except Exception:
    iss_notify = None
try:
    import iss_multisat
except Exception:
    iss_multisat = None
try:
    import iss_observe
except Exception:
    iss_observe = None
try:
    import iss_multipos
except Exception:
    iss_multipos = None
try:
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
from datetime import datetime
from pathlib import Path

# ============================================================
# DÉPENDANCES
# ============================================================
try:
    import requests
except ImportError:
    print("❌ pip install requests")
    sys.exit(1)

try:
    from geopy.distance import geodesic
    GEOPY_OK = True
except ImportError:
    GEOPY_OK = False

try:
    from PIL import Image
    from PIL.ExifTags import GPSTAGS
    PIL_OK = True
except ImportError:
    PIL_OK = False

try:
    import qrcode
    QRCODE_OK = True
except ImportError:
    QRCODE_OK = False

# ============================================================
# CONFIGURATION
# ============================================================
APP_NAME = "MAP-CI"
APP_VERSION = "6.2"
USER_AGENT = f"MAP-CI/{APP_VERSION} (+https://github.com/mapci)"

FAVORIS_FILE      = Path.home() / ".mapci_favoris.json"
HISTORIQUE_FILE   = Path.home() / ".mapci_historique.json"
ALARM_CONFIG_FILE = Path.home() / ".mapci_alarm.json"
ALARM_LOG_FILE    = Path.home() / ".mapci_alarm_log.json"
GEO_CACHE_FILE    = Path.home() / ".mapci_geo_cache.json"

# ============================================================
# MINI-DICTIONNAIRE LOCAL (zéro réseau)
# ============================================================
VILLES_LOCALES = {
    "abidjan":        (5.3599517, -4.0082563, "Abidjan, Côte d'Ivoire"),
    "yamoussoukro":   (6.8276228, -5.2893433, "Yamoussoukro, Côte d'Ivoire"),
    "bouake":         (7.6906,    -5.0301,    "Bouaké, Côte d'Ivoire"),
    "dakar":          (14.6928,   -17.4467,   "Dakar, Sénégal"),
    "bamako":         (12.6392,   -8.0029,    "Bamako, Mali"),
    "ouagadougou":    (12.3714,   -1.5197,    "Ouagadougou, Burkina Faso"),
    "lome":           (6.1375,    1.2123,     "Lomé, Togo"),
    "cotonou":        (6.3654,    2.4183,     "Cotonou, Bénin"),
    "accra":          (5.6037,    -0.1870,    "Accra, Ghana"),
    "lagos":          (6.5244,    3.3792,     "Lagos, Nigeria"),
    "paris":          (48.8566,   2.3522,     "Paris, France"),
    "marseille":      (43.2965,   5.3698,     "Marseille, France"),
    "lyon":           (45.7640,   4.8357,     "Lyon, France"),
    "londres":        (51.5074,   -0.1278,    "Londres, Royaume-Uni"),
    "london":         (51.5074,   -0.1278,    "Londres, Royaume-Uni"),
    "bruxelles":      (50.8503,   4.3517,     "Bruxelles, Belgique"),
    "berlin":         (52.5200,   13.4050,    "Berlin, Allemagne"),
    "madrid":         (40.4168,   -3.7038,    "Madrid, Espagne"),
    "rome":           (41.9028,   12.4964,    "Rome, Italie"),
    "lisbonne":       (38.7223,   -9.1393,    "Lisbonne, Portugal"),
    "new york":       (40.7128,   -74.0060,   "New York, USA"),
    "los angeles":    (34.0522,   -118.2437,  "Los Angeles, USA"),
    "montreal":       (45.5017,   -73.5673,   "Montréal, Canada"),
    "tokyo":          (35.6762,   139.6503,   "Tokyo, Japon"),
    "pekin":          (39.9042,   116.4074,   "Pékin, Chine"),
    "beijing":        (39.9042,   116.4074,   "Pékin, Chine"),
    "shanghai":       (31.2304,   121.4737,   "Shanghai, Chine"),
    "dubai":          (25.2048,   55.2708,    "Dubaï, EAU"),
    "le caire":       (30.0444,   31.2357,    "Le Caire, Égypte"),
    "cairo":          (30.0444,   31.2357,    "Le Caire, Égypte"),
    "marrakech":      (31.6295,   -7.9811,    "Marrakech, Maroc"),
    "casablanca":     (33.5731,   -7.5898,    "Casablanca, Maroc"),
    "tunis":          (36.8065,   10.1815,    "Tunis, Tunisie"),
    "alger":          (36.7538,   3.0588,     "Alger, Algérie"),
    "kinshasa":       (-4.4419,   15.2663,    "Kinshasa, RDC"),
    "brazzaville":    (-4.2634,   15.2429,    "Brazzaville, Congo"),
    "libreville":     (0.4162,    9.4673,     "Libreville, Gabon"),
    "douala":         (4.0511,    9.7679,     "Douala, Cameroun"),
    "yaounde":        (3.8480,    11.5021,    "Yaoundé, Cameroun"),
    "nairobi":        (-1.2864,   36.8172,    "Nairobi, Kenya"),
    "johannesburg":   (-26.2041,  28.0473,    "Johannesburg, Afrique du Sud"),
    "le cap":         (-33.9249,  18.4241,    "Le Cap, Afrique du Sud"),
    "sydney":         (-33.8688,  151.2093,   "Sydney, Australie"),
    "melbourne":      (-37.8136,  144.9631,   "Melbourne, Australie"),
    "rio de janeiro": (-22.9068,  -43.1729,   "Rio de Janeiro, Brésil"),
    "sao paulo":      (-23.5505,  -46.6333,   "São Paulo, Brésil"),
    "buenos aires":   (-34.6037,  -58.3816,   "Buenos Aires, Argentine"),
    "mexico":         (19.4326,   -99.1332,   "Mexico, Mexique"),
}

# ============================================================
# UTILITAIRES
# ============================================================
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def wcswidth(s):
    return sum(2 if ord(ch) > 0x1F000 else 1 for ch in s)

def pad_center(s, width):
    w = wcswidth(s)
    if w >= width:
        return s
    left = (width - w) // 2
    right = width - w - left
    return " " * left + s + " " * right

def box_line(title, width=46):
    inner = width - 2
    return [
        "╔" + "═" * inner + "╗",
        "║" + pad_center(title, inner) + "║",
        "║" + "─" * inner + "║",
    ]

def print_header():
    for line in box_line(f"🗺️  M A P - C I   V {APP_VERSION}", 46):
        print(line)
    print("║" + pad_center("Cartographie • GPS • EXIF • Live • ISS", 44) + "║")
    print("╚" + "═" * 44 + "╝")

def pause():
    input("\n⏎ Entrée pour revenir au menu...")

def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def ajouter_historique(action, details=""):
    hist = load_json(HISTORIQUE_FILE, [])
    hist.append({"date": datetime.now().isoformat(), "action": action, "details": details})
    save_json(HISTORIQUE_FILE, hist[-300:])

def beep():
    print("\a", end="", flush=True)
    if os.name == "nt":
        try:
            import winsound
            winsound.Beep(1200, 500)
            winsound.Beep(1500, 500)
        except Exception:
            pass

# ============================================================
# 🌍 GÉOCODEUR PHOTON-ONLY + CACHE LOCAL
# ============================================================
_GEO_CACHE = load_json(GEO_CACHE_FILE, {})

def _photon_geocode(nom):
    """Géocodeur principal : Photon (komoot). Aucun 403 connu."""
    try:
        r = requests.get(
            "https://photon.komoot.io/api/",
            params={"q": nom, "limit": 1},
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        if r.status_code != 200:
            return None
        feats = r.json().get("features", [])
        if not feats:
            return None
        f = feats[0]
        lon, lat = f["geometry"]["coordinates"]
        p = f.get("properties", {})
        addr = ", ".join(filter(None, [
            p.get("name"), p.get("city"), p.get("state"), p.get("country")
        ])) or nom
        return (lat, lon, addr)
    except Exception:
        return None

def geocoder_robuste(nom):
    """
    Ordre : cache JSON → dictionnaire local → Photon API.
    Retourne (lat, lon, adresse) ou None.
    """
    if not nom:
        return None
    key = nom.strip().lower()

    # 1) Cache JSON
    if key in _GEO_CACHE:
        c = _GEO_CACHE[key]
        return (c["lat"], c["lon"], c["addr"])

    # 2) Dictionnaire local (zéro réseau)
    if key in VILLES_LOCALES:
        lat, lon, addr = VILLES_LOCALES[key]
        _GEO_CACHE[key] = {"lat": lat, "lon": lon, "addr": addr}
        save_json(GEO_CACHE_FILE, _GEO_CACHE)
        return (lat, lon, addr)

    # 3) Photon
    res = _photon_geocode(nom)
    if res:
        _GEO_CACHE[key] = {"lat": res[0], "lon": res[1], "addr": res[2]}
        save_json(GEO_CACHE_FILE, _GEO_CACHE)
    return res

def _geocode(nom):
    return geocoder_robuste(nom)

def _saisie_manuelle_coords(prompt_nom="Nom du lieu : "):
    """Demande lat/lon à l'utilisateur. Retourne (lat, lon, nom) ou None."""
    try:
        lat = float(input("Latitude  : ").strip())
        lon = float(input("Longitude : ").strip())
        nom = input(prompt_nom).strip() or f"{lat},{lon}"
        return (lat, lon, nom)
    except ValueError:
        print("❌ Coordonnées invalides.")
        return None

# ============================================================
# 🚨 ALARME ISS (THREAD)
# ============================================================
class ISSAlarm:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = None
        self.config = load_json(ALARM_CONFIG_FILE, {
            "enabled": False,
            "lat": None, "lon": None, "lieu": "",
            "seuil_minutes": 60,
            "check_interval": 300,
            "duree_min": 60,
            "notified": [],
        })
        self.notified = set(self.config.get("notified", []))

    def _fetch_passes(self, lat, lon, n=10):
        from iss_pass import get_next_passes
        passes_raw = get_next_passes(lat, lon, hours=48, min_elevation=0, verbose=False)
        result = []
        for p in passes_raw[:n]:
            result.append({
                "risetime": int(p['risetime'].timestamp()),
                "duration": int(p['duration_s']),
                "max_elevation": round(p['max_elevation']),
            })
        return result
    def _loop(self):
        while not self.stop_event.is_set():
            try:
                cfg = self.config
                if cfg["enabled"] and cfg["lat"] is not None:
                    passes = self._fetch_passes(cfg["lat"], cfg["lon"], n=5)
                    now = time.time()
                    seuil = cfg["seuil_minutes"] * 60
                    for p in passes:
                        rt = p["risetime"]
                        delta = rt - now
                        if p.get("duration", 0) < cfg["duree_min"]:
                            continue
                        if 0 < delta <= seuil and rt not in self.notified:
                            self._trigger(p, delta)
                            self.notified.add(rt)
                            self.config["notified"] = list(self.notified)[-50:]
                            save_json(ALARM_CONFIG_FILE, self.config)
            except Exception:
                pass
            self.stop_event.wait(self.config.get("check_interval", 300))

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def _trigger(self, p, delta_sec):
        rt = datetime.fromtimestamp(p["risetime"])
        mins = int(delta_sec // 60)
        secs = int(delta_sec % 60)
        duration = p.get("duration", 0)
        max_elev = p.get("max_elevation", "?")

        print("\n" + "=" * 52)
        print("🚨  A L E R T E   I S S  🚨".center(52))
        print("=" * 52)
        print(f"🛰️  Passage dans {mins} min {secs:02d} s")
        print(f"⏰ Risetime  : {rt:%d/%m/%Y %H:%M:%S}")
        print(f"⏱️  Durée     : {duration} sec")
        if max_elev != "?":
            print(f"📐 Élévation : {max_elev}°")
        print(f"📍 Lieu      : {self.config.get('lieu', '?')}")
        print("=" * 52)
        beep()

        if iss_alerts is not None:
            try:
                titre = f"ISS dans {mins} min"
                msg = f"Risetime {rt:%H:%M:%S} - duree {duration}s - {self.config.get('lieu','?')}"
                iss_alerts.notifier_android(titre, msg)
                iss_alerts.vibrer(800)
                iss_alerts.parler(f"Attention, I S S dans {mins} minutes")
                iss_alerts.envoyer_sms(f"[MAP-CI] {titre} - {msg}")
            except Exception:
                pass

        # Telegram + Discord
        try:
            from iss_notify import send_telegram, send_discord
            telegram_msg = (f"🛰️ *ISS dans {mins} min*\n"
                            f"Risetime {rt:%H:%M:%S} UTC\n"
                            f"Duree {duration}s | Max {max_elev if max_elev != '?' else '?'}°\n"
                            f"Lieu : {self.config.get('lieu','?')}")
            send_telegram(telegram_msg)
            send_discord(telegram_msg)
        except Exception:
            pass

        log = load_json(ALARM_LOG_FILE, [])
        log.append({
            "date": datetime.now().isoformat(),
            "risetime": rt.isoformat(),
            "dans_secondes": int(delta_sec),
            "duree": duration,
            "lieu": self.config.get("lieu", ""),
        })
        save_json(ALARM_LOG_FILE, log[-100:])
        ajouter_historique("🚨 Alarme ISS", f"{rt:%H:%M:%S} dans {mins} min")

    def configurer(self):
        print("\n⚙️  Configuration de l'alarme ISS")
        print("─" * 44)
        print("🌍 Tape une ville connue, ou 'M' pour saisir les coordonnées manuellement.")
        print("   (Entrée seule = garder la position actuelle)\n")

        saisie = input("🌍 Ville [M/manuelle] : ").strip()

        # --- Mode manuel ---
        if saisie.lower() == "m":
            coords = _saisie_manuelle_coords()
            if not coords:
                return
            lat, lon, nom = coords
            self.config["lat"] = lat
            self.config["lon"] = lon
            self.config["lieu"] = nom
            print(f"✅ Position enregistrée : {nom} ({lat}, {lon})")

        # --- Ville saisie ---
        elif saisie:
            print("⏳ Recherche...")
            res = geocoder_robuste(saisie)
            if res:
                lat, lon, addr = res
                self.config["lat"] = lat
                self.config["lon"] = lon
                self.config["lieu"] = saisie
                print(f"✅ {addr}")
                print(f"   Lat/Lon : {lat:.5f}, {lon:.5f}")
            else:
                print("❌ Ville introuvable (Photon n'a rien trouvé).")
                if input("🔧 Saisir les coordonnées à la main ? (o/N) : ").strip().lower() == "o":
                    coords = _saisie_manuelle_coords()
                    if not coords:
                        return
                    lat, lon, nom = coords
                    self.config["lat"] = lat
                    self.config["lon"] = lon
                    self.config["lieu"] = nom
                    print("✅ Enregistré.")
                else:
                    return

        # --- Seuil ---
        try:
            seuil = input(f"⏱️  Seuil d'alerte en minutes [{self.config['seuil_minutes']}] : ").strip()
            if seuil:
                self.config["seuil_minutes"] = max(1, int(seuil))
        except ValueError:
            pass

        # --- Durée mini ---
        try:
            dur = input(f"⏳ Durée mini passage (s) [{self.config['duree_min']}] : ").strip()
            if dur:
                self.config["duree_min"] = max(0, int(dur))
        except ValueError:
            pass

        act = input("🔔 Activer l'alarme ? (o/N) : ").strip().lower()
        self.config["enabled"] = (act == "o")

        save_json(ALARM_CONFIG_FILE, self.config)

        if self.config["enabled"]:
            if self.config["lat"] is None:
                print("⚠️  Aucune position définie — l'alarme ne se déclenchera pas.")
                print("💡 Relance l'option 27 avec 'M' pour saisir les coordonnées.")
            else:
                self.start()
                print("✅ Alarme ACTIVÉE en arrière-plan.")
                print(f"   Surveillance : {self.config['lieu']} ({self.config['lat']}, {self.config['lon']})")
        else:
            self.stop()
            print("🔕 Alarme DÉSACTIVÉE.")

    def statut(self):
        print("\n🛰️  Statut de l'alarme ISS")
        print("─" * 44)
        print(f"État      : {'✅ ACTIVÉE' if self.config['enabled'] else '🔕 Désactivée'}")
        print(f"Lieu      : {self.config.get('lieu') or '(non défini)'}")
        print(f"Coords    : {self.config.get('lat')}, {self.config.get('lon')}")
        print(f"Seuil     : {self.config.get('seuil_minutes')} min")
        print(f"Durée mini: {self.config.get('duree_min')} s")
        print(f"Vérif     : toutes les {self.config.get('check_interval')} s")

        if self.config["enabled"] and self.config["lat"] is None:
            print("\n⚠️  ATTENTION : alarme activée mais AUCUNE position définie.")
            print("   → Option 27 puis 'M' pour saisir les coordonnées.")

        log = load_json(ALARM_LOG_FILE, [])
        print(f"Dernières alertes : {len(log)}")
        for e in log[-5:]:
            print(f"  • {e['date'][:19]} — {e['lieu']} (dans {e['dans_secondes']//60} min)")

    def tester(self):
        print("\n🔔 Test de l'alarme...")
        fake = {"risetime": time.time() + 3600, "duration": 480, "max_elevation": 72}
        self._trigger(fake, 3600)
        print("\n✅ Si vous avez entendu un bip, l'alarme fonctionne.")

iss_alarm = ISSAlarm()

# ============================================================
# OPTION 1 — RECHERCHER VILLE
# ============================================================
def rechercher_ville():
    q = input("🔎 Ville / lieu : ").strip()
    if not q:
        return
    print("⏳ Recherche...")
    res = geocoder_robuste(q)
    if res:
        lat, lon, addr = res
        print(f"\n✅ {addr}")
        print(f"📍 Lat : {lat}")
        print(f"📍 Lon : {lon}")
        ajouter_historique("Recherche ville", q)
    else:
        print("❌ Aucun résultat.")
        if input("🔧 Saisir les coordonnées à la main ? (o/N) : ").strip().lower() == "o":
            coords = _saisie_manuelle_coords()
            if coords:
                print(f"✅ {coords[2]} : {coords[0]}, {coords[1]}")

# ============================================================
# OPTION 2 — CARTE
# ============================================================
def afficher_carte():
    try:
        lat = float(input("Latitude  : ").strip())
        lon = float(input("Longitude : ").strip())
    except ValueError:
        print("❌ Invalide.")
        return
    print(f"\n🌐 OSM    : https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}")
    print(f"🗺️  Google : https://www.google.com/maps/@{lat},{lon},15z")
    ajouter_historique("Carte", f"{lat},{lon}")

# ============================================================
# OPTION 3 — EXIF GPS
# ============================================================
def _to_deg(coord, ref):
    if coord is None or ref is None:
        return None
    d, m, s = coord
    return d + m / 60.0 + s / 3600.0

def extraire_gps_exif():
    if not PIL_OK:
        print("❌ Pillow requis.")
        return
    chemin = input("📷 Chemin image : ").strip()
    if not chemin or not Path(chemin).exists():
        print("❌ Introuvable.")
        return
    try:
        img = Image.open(chemin)
        exif = img.getexif()
        gps_ifd = exif.get_ifd(0x8825)
        if not gps_ifd:
            print("❌ Pas de GPS.")
            return
        gps = {GPSTAGS.get(k, k): v for k, v in gps_ifd.items()}
        lat = _to_deg(gps.get("GPSLatitude"), gps.get("GPSLatitudeRef"))
        lon = _to_deg(gps.get("GPSLongitude"), gps.get("GPSLongitudeRef"))
        if gps.get("GPSLatitudeRef") == "S":
            lat = -lat
        if gps.get("GPSLongitudeRef") == "W":
            lon = -lon
        print(f"\n✅ Lat : {lat:.6f}\n✅ Lon : {lon:.6f}")
        if gps.get("GPSAltitude"):
            print(f"🏔️  Alt : {gps['GPSAltitude']:.1f} m")
        print(f"🌐 https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}")
        ajouter_historique("EXIF GPS", f"{lat},{lon}")
    except Exception as e:
        print(f"❌ {e}")

# ============================================================
# OPTIONS 4-5 — MÉTÉO
# ============================================================
WEATHER_CODES = {
    0:"☀️  Ciel dégagé",1:"🌤️  Peu nuageux",2:"⛅ Partiellement nuageux",3:"☁️  Couvert",
    45:"🌫️  Brouillard",48:"🌫️  Brouillard givrant",51:"🌦️  Bruine légère",53:"🌦️  Bruine modérée",
    55:"🌧️  Bruine dense",61:"🌧️  Pluie légère",63:"🌧️  Pluie modérée",65:"🌧️  Pluie forte",
    71:"❄️  Neige légère",73:"❄️  Neige modérée",75:"❄️  Neige forte",80:"🌦️  Averses légères",
    81:"🌧️  Averses modérées",82:"🌧️  Averses violentes",95:"⛈️  Orage",
    96:"⛈️  Orage grêle",99:"⛈️  Orage violent",
}

def meteo_actuelle():
    ville = input("🌦️  Ville : ").strip()
    c = _geocode(ville)
    if not c:
        print("❌ Introuvable.")
        return
    lat, lon, addr = c
    try:
        r = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&timezone=auto",
            timeout=10
        ).json()
        cur = r["current"]
        print(f"\n📍 {addr}")
        print(f"🌡️  {cur['temperature_2m']}°C")
        print(f"💧 {cur['relative_humidity_2m']}%")
        print(f"💨 {cur['wind_speed_10m']} km/h")
        print(f"☁️  {WEATHER_CODES.get(cur['weather_code'], '?')}")
        ajouter_historique("Météo", ville)
    except Exception as e:
        print(f"❌ {e}")

def meteo_7_jours():
    ville = input("📅 Ville : ").strip()
    c = _geocode(ville)
    if not c:
        print("❌ Introuvable.")
        return
    lat, lon, addr = c
    try:
        r = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&daily=temperature_2m_max,temperature_2m_min,weather_code&timezone=auto&forecast_days=7",
            timeout=10
        ).json()
        d = r["daily"]
        print(f"\n📍 {addr}\n")
        print(f"{'Date':<12}{'Min':>6}{'Max':>6}  Condition")
        print("─" * 52)
        for i, day in enumerate(d["time"]):
            desc = WEATHER_CODES.get(d["weather_code"][i], "?")
            print(f"{day:<12}{d['temperature_2m_min'][i]:>5}°{d['temperature_2m_max'][i]:>5}°  {desc}")
        ajouter_historique("Météo 7j", ville)
    except Exception as e:
        print(f"❌ {e}")

# ============================================================
# OPTION 6 — QUALITÉ DE L'AIR
# ============================================================
def qualite_air():
    ville = input("💨 Ville : ").strip()
    c = _geocode(ville)
    if not c:
        print("❌ Introuvable.")
        return
    lat, lon, addr = c
    try:
        r = requests.get(
            f"https://air-quality-api.open-meteo.com/v1/air-quality?"
            f"latitude={lat}&longitude={lon}"
            f"&current=pm10,pm2_5,ozone,nitrogen_dioxide,european_aqi&timezone=auto",
            timeout=10
        ).json()
        cur = r["current"]
        aqi = cur.get("european_aqi", 0)
        niveau = ("🟢 Excellent" if aqi <= 20 else
                  "🟡 Bon" if aqi <= 40 else
                  "🟠 Moyen" if aqi <= 60 else
                  "🔴 Mauvais" if aqi <= 80 else
                  "🟣 Très mauvais" if aqi <= 100 else
                  "⚫ Extrêmement mauvais")
        print(f"\n📍 {addr}")
        print(f"💨 AQI européen : {aqi} — {niveau}")
        print(f"  PM10  : {cur.get('pm10')} µg/m³")
        print(f"  PM2.5 : {cur.get('pm2_5')} µg/m³")
        print(f"  O₃    : {cur.get('ozone')} µg/m³")
        print(f"  NO₂   : {cur.get('nitrogen_dioxide')} µg/m³")
        ajouter_historique("Qualité air", ville)
    except Exception as e:
        print(f"❌ {e}")

# ============================================================
# OPTION 7 — POSITION IP
# ============================================================
def ma_position_ip():
    try:
        d = requests.get(
            "http://ip-api.com/json/?fields=status,country,city,zip,lat,lon,timezone,isp,query",
            timeout=10
        ).json()
        if d.get("status") != "success":
            print("❌ Échec.")
            return
        print(f"\n🌍 {d['country']} — {d['city']} ({d['zip']})")
        print(f"📍 {d['lat']}, {d['lon']}")
        print(f"🕐 {d['timezone']}")
        print(f"📡 {d['isp']}  |  IP : {d['query']}")
        ajouter_historique("Position IP", d["query"])
    except Exception as e:
        print(f"❌ {e}")

# ============================================================
# OPTION 8 — DISTANCE + ITINÉRAIRE
# ============================================================
def distance_itineraire():
    if not GEOPY_OK:
        print("❌ geopy requis.")
        return
    try:
        la1 = float(input("Lat A : ")); lo1 = float(input("Lon A : "))
        la2 = float(input("Lat B : ")); lo2 = float(input("Lon B : "))
    except ValueError:
        print("❌ Invalide.")
        return
    d = geodesic((la1, lo1), (la2, lo2)).km
    print(f"\n📏 Distance : {d:.2f} km")
    print(f"🌐 https://www.openstreetmap.org/directions?from={la1},{lo1}&to={la2},{lo2}")
    ajouter_historique("Distance", f"{d:.1f} km")

# ============================================================
# OPTION 9 — POSITION ISS
# ============================================================
def position_iss():
    try:
        d = requests.get("http://api.open-notify.org/iss-now.json", timeout=10).json()
        p = d["iss_position"]
        ts = datetime.fromtimestamp(d["timestamp"])
        print(f"\n🛰️  ISS à {ts:%d/%m/%Y %H:%M:%S} UTC")
        print(f"📍 Lat : {p['latitude']}")
        print(f"📍 Lon : {p['longitude']}")
        print(f"🌐 https://www.openstreetmap.org/?mlat={p['latitude']}&mlon={p['longitude']}#map=3/{p['latitude']}/{p['longitude']}")
        ajouter_historique("ISS", f"{p['latitude']},{p['longitude']}")
    except Exception as e:
        print(f"❌ {e}")

# ============================================================
# OPTION P — PROCHAINS PASSAGES ISS
# ============================================================
def passages_iss():
    from iss_pass import get_next_passes, format_pass
    ville = input("Ville (Entree = config alarme) : ").strip()
    if ville:
        c = _geocode(ville)
        if not c:
            print("Introuvable.")
            return
        lat, lon, addr = c
    else:
        lat = iss_alarm.config.get("lat")
        lon = iss_alarm.config.get("lon")
        addr = iss_alarm.config.get("lieu") or "?"
    if lat is None:
        print("Aucune position definie.")
        return

    print(f"Calcul des passages ISS pour {addr}...")
    passes = get_next_passes(lat, lon, hours=48, min_elevation=0, verbose=True)
    if not passes:
        print("Aucun passage prevu dans les 48 prochaines heures.")
        return

    print(f"{len(passes)} passage(s) prevu(s) dans les 48h :")
    print("  " + "-" * 52)
    for p in passes:
        print(format_pass(p, offset_h=0))
    print("  " + "-" * 52)
    ajouter_historique("Passages ISS (Skyfield)", addr)

def fuseaux_horaires():
    ville = input("🌐 Ville : ").strip()
    c = _geocode(ville)
    if not c:
        print("❌ Introuvable.")
        return
    lat, lon, addr = c
    try:
        d = requests.get(
            f"https://timeapi.io/api/Time/current/coordinate?latitude={lat}&longitude={lon}",
            timeout=10
        ).json()
        print(f"\n📍 {addr}")
        print(f"🕐 Heure locale : {d.get('dateTime', '?')}")
        print(f"🌍 Fuseau      : {d.get('timeZone', '?')}")
        print(f"📅 Jour        : {d.get('dayOfWeek', '?')}")
        ajouter_historique("Fuseau horaire", ville)
    except Exception as e:
        print(f"❌ {e}")

# ============================================================
# OPTION 11 — ALTITUDE
# ============================================================
def altitude_lieu():
    ville = input("🏔️  Ville : ").strip()
    c = _geocode(ville)
    if not c:
        print("❌ Introuvable.")
        return
    lat, lon, addr = c
    try:
        d = requests.get(
            f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}",
            timeout=10
        ).json()
        elev = d["results"][0]["elevation"]
        print(f"\n📍 {addr}")
        print(f"🏔️  Altitude : {elev} m")
        ajouter_historique("Altitude", f"{ville} = {elev} m")
    except Exception as e:
        print(f"❌ {e}")

# ============================================================
# OPTION 12 — POINTS D'INTÉRÊT
# ============================================================
def points_interet():
    ville = input("🏛️  Ville : ").strip()
    c = _geocode(ville)
    if not c:
        print("❌ Introuvable.")
        return
    lat, lon, addr = c
    cat = input("Catégorie (restaurant/museum/hotel/cafe) [restaurant] : ").strip() or "restaurant"
    tag = "tourism" if cat == "museum" else "amenity"
    val = cat if cat in ("restaurant", "museum", "hotel", "cafe") else "restaurant"
    query = f"""
    [out:json][timeout:15];
    node["{tag}"="{val}"](around:3000,{lat},{lon});
    out body 15;
    """
    try:
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query}, timeout=20
        ).json()
        elems = r.get("elements", [])
        print(f"\n🏛️  {len(elems)} résultat(s) autour de {addr}\n")
        for e in elems[:10]:
            name = e.get("tags", {}).get("name", "(sans nom)")
            d_lat, d_lon = e["lat"], e["lon"]
            dist = geodesic((lat, lon), (d_lat, d_lon)).km if GEOPY_OK else 0
            print(f"  • {name} — {dist:.2f} km ({d_lat:.4f},{d_lon:.4f})")
        ajouter_historique("POI", f"{cat} @ {ville}")
    except Exception as e:
        print(f"❌ {e}")

# ============================================================
# OPTION 13 — PHASE DE LA LUNE
# ============================================================
def phase_lune():
    now = datetime.utcnow()
    ref = datetime(2000, 1, 6, 18, 14)
    days = (now - ref).total_seconds() / 86400
    syn = 29.530588853
    age = days % syn
    if age < 1.84566: nom, emoji = "Nouvelle Lune", "🌑"
    elif age < 5.53699: nom, emoji = "Premier Croissant", "🌒"
    elif age < 9.22831: nom, emoji = "Premier Quartier", "🌓"
    elif age < 12.91963: nom, emoji = "Gibbeuse Croissante", "🌔"
    elif age < 16.61096: nom, emoji = "Pleine Lune", "🌕"
    elif age < 20.30228: nom, emoji = "Gibbeuse Décroissante", "🌖"
    elif age < 23.99361: nom, emoji = "Dernier Quartier", "🌗"
    elif age < 27.68493: nom, emoji = "Dernier Croissant", "🌘"
    else: nom, emoji = "Nouvelle Lune", "🌑"
    ill = (1 - math.cos(2 * math.pi * age / syn)) / 2 * 100
    print(f"\n{emoji}  {nom}")
    print(f"📊 Âge : {age:.2f} jours")
    print(f"💡 Illumination : {ill:.1f}%")
    ajouter_historique("Phase lune", nom)

# ============================================================
# OPTION 14 — LANCEMENTS SPATIAUX
# ============================================================
def lancements_spatiaux():
    try:
        r = requests.get(
            "https://ll.thespacedevs.com/2.2.0/launch/upcoming/?limit=10",
            timeout=15
        ).json()
        results = r.get("results", [])
        if not results:
            print("❌ Aucun lancement prévu.")
            return
        print("\n🚀 Prochains lancements spatiaux :\n")
        for l in results:
            nom = l.get("name", "?")
            net = l.get("net", "")[:16].replace("T", " ")
            pad = l.get("pad", {}).get("location", {}).get("name", "?")
            status = l.get("status", {}).get("abbrev", "?")
            print(f"  🚀 {nom}")
            print(f"     ⏰ {net}  |  📍 {pad}  |  [{status}]")
        ajouter_historique("Lancements", f"{len(results)} résultats")
    except Exception as e:
        print(f"❌ {e}")

# ============================================================
# OPTION 15 — QR CODE
# ============================================================
def qr_code_position():
    if not QRCODE_OK:
        print("❌ pip install qrcode[pil]")
        return
    try:
        lat = float(input("Latitude : "))
        lon = float(input("Longitude : "))
    except ValueError:
        print("❌ Invalide.")
        return
    txt = f"geo:{lat},{lon}"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(txt); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    f = Path.cwd() / f"qr_{lat}_{lon}.png"
    img.save(f)
    print(f"\n✅ {f}")

# ============================================================
# OPTION 16 — EXPORT GPX
# ============================================================
def export_gpx():
    try:
        lat = float(input("Latitude : "))
        lon = float(input("Longitude : "))
    except ValueError:
        print("❌ Invalide.")
        return
    nom = input("Nom : ").strip() or "Point MAP-CI"
    gpx = f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="MAP-CI V6" xmlns="http://www.topografix.com/GPX/1/1">
  <wpt lat="{lat}" lon="{lon}"><name>{nom}</name>
  <time>{datetime.utcnow().isoformat()}Z</time></wpt></gpx>"""
    f = Path.cwd() / "point.gpx"
    f.write_text(gpx, encoding="utf-8")
    print(f"✅ {f}")

# ============================================================
# OPTION 17 — TABLEAU DE BORD
# ============================================================
def tableau_de_bord():
    print("\n📊 TABLEAU DE BORD MAP-CI\n" + "─" * 46)
    try:
        d = requests.get("http://ip-api.com/json/?fields=city,country,timezone", timeout=8).json()
        print(f"📍 Position : {d.get('city')}, {d.get('country')}")
        print(f"🕐 Fuseau   : {d.get('timezone')}")
    except Exception:
        print("📍 Position : (indisponible)")
    try:
        d = requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35"
            "&current=temperature_2m,weather_code", timeout=8
        ).json()
        cur = d["current"]
        print(f"🌡️  Paris    : {cur['temperature_2m']}°C — {WEATHER_CODES.get(cur['weather_code'], '?')}")
    except Exception:
        pass
    try:
        d = requests.get("http://api.open-notify.org/iss-now.json", timeout=8).json()["iss_position"]
        print(f"🛰️  ISS      : {d['latitude']}, {d['longitude']}")
    except Exception:
        pass
    now = datetime.utcnow()
    ref = datetime(2000, 1, 6, 18, 14)
    age = ((now - ref).total_seconds() / 86400) % 29.530588853
    ill = (1 - math.cos(2 * math.pi * age / 29.530588853)) / 2 * 100
    print(f"🌕 Lune     : {ill:.0f}% illuminée")
    st = "✅ ON" if iss_alarm.config["enabled"] else "🔕 OFF"
    print(f"🚨 Alarme   : {st}")
    ajouter_historique("Dashboard")

# ============================================================
# OPTION 18 — FAVORIS
# ============================================================
def gerer_favoris():
    fav = load_json(FAVORIS_FILE, [])
    print("\n📌 FAVORIS")
    print("─" * 46)
    if not fav:
        print("(vide)")
    for i, f in enumerate(fav, 1):
        print(f"  {i}. {f['nom']} — {f['lat']}, {f['lon']}")
    print("\n  A. Ajouter  |  S. Supprimer  |  Entrée. Retour")
    c = input("👉 ").strip().upper()
    if c == "A":
        try:
            nom = input("Nom : ").strip()
            lat = float(input("Latitude : "))
            lon = float(input("Longitude : "))
            fav.append({"nom": nom, "lat": lat, "lon": lon})
            save_json(FAVORIS_FILE, fav)
            print("✅ Ajouté.")
        except ValueError:
            print("❌ Invalide.")
    elif c == "S":
        try:
            i = int(input("Numéro : ")) - 1
            if 0 <= i < len(fav):
                fav.pop(i); save_json(FAVORIS_FILE, fav)
                print("✅ Supprimé.")
        except ValueError:
            pass

# ============================================================
# OPTION 19 — GOLDEN HOUR
# ============================================================
def golden_hour():
    try:
        lat = float(input("Latitude : "))
    except ValueError:
        print("❌ Invalide.")
        return
    if abs(lat) < 23.5: lever, coucher = ("06:00", "06:30"), ("18:00", "18:30")
    elif abs(lat) < 45: lever, coucher = ("06:30", "07:00"), ("17:30", "18:00")
    else: lever, coucher = ("07:30", "08:00"), ("16:30", "17:00")
    print(f"\n📸 Golden Hour (lat {lat}°)")
    print(f"🌅 Matin : {lever[0]} – {lever[1]}")
    print(f"🌇 Soir  : {coucher[0]} – {coucher[1]}")

# ============================================================
# OPTION 20 — SÉISMES
# ============================================================
def seismes_recents():
    try:
        d = requests.get(
            "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson",
            timeout=10
        ).json()
        feats = d.get("features", [])
        print(f"\n🚨 {len(feats)} séismes (M≥2.5) / 24h\n")
        for f in feats[:15]:
            p = f["properties"]
            t = datetime.fromtimestamp(p["time"] / 1000)
            print(f"  M{p['mag']:.1f} — {p.get('place','?')} ({t:%d/%m %H:%M})")
    except Exception as e:
        print(f"❌ {e}")

# ============================================================
# OPTION 21 — COORDS ALÉATOIRES
# ============================================================
def coords_aleatoires():
    lat = random.uniform(-90, 90); lon = random.uniform(-180, 180)
    print(f"\n🎲 {lat:.6f}, {lon:.6f}")
    print(f"🌐 https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=5/{lat}/{lon}")

# ============================================================
# OPTION 22 — QUIZ CAPITALES
# ============================================================
CAPITALES = {
    "France": "Paris", "Japon": "Tokyo", "Brésil": "Brasilia",
    "Côte d'Ivoire": "Yamoussoukro", "Canada": "Ottawa",
    "Australie": "Canberra", "Égypte": "Le Caire", "Maroc": "Rabat",
    "Sénégal": "Dakar", "Mali": "Bamako", "Espagne": "Madrid",
    "Italie": "Rome", "Allemagne": "Berlin", "Portugal": "Lisbonne",
    "Chine": "Pékin", "Inde": "New Delhi", "Russie": "Moscou",
}

def quiz_capitales():
    score = 0
    questions = random.sample(list(CAPITALES.items()), 5)
    for i, (pays, cap) in enumerate(questions, 1):
        r = input(f"{i}/5 — Capitale de {pays} ? ").strip()
        if r.lower() == cap.lower():
            print("✅"); score += 1
        else:
            print(f"❌ C'était {cap}")
    print(f"\n🎯 Score : {score}/5")
    ajouter_historique("Quiz capitales", f"{score}/5")

# ============================================================
# OPTION 23 — CHASSE AU TRÉSOR
# ============================================================
def chasse_tresor():
    print("\n🏴‍☠️  CHASSE AU TRÉSOR — trouvez le point caché !")
    print("La grille va de 0 à 100 (x = longitude, y = latitude)\n")
    tx, ty = random.randint(0, 100), random.randint(0, 100)
    essais = 0
    while True:
        try:
            x = int(input("X : ")); y = int(input("Y : "))
        except ValueError:
            continue
        essais += 1
        dx, dy = x - tx, y - ty
        dist = math.hypot(dx, dy)
        if dist < 5:
            print(f"\n🎉 TROUVÉ en {essais} essais !")
            break
        dirs = []
        if abs(dx) > 5: dirs.append("Est" if dx < 0 else "Ouest")
        if abs(dy) > 5: dirs.append("Nord" if dy < 0 else "Sud")
        print(f"❄️  {dist:.0f} unités — " + (", ".join(dirs) if dirs else "presque !"))
    ajouter_historique("Chasse trésor", f"{essais} essais")

# ============================================================
# OPTION 24 — DEVINE LA VILLE
# ============================================================
VILLES_INDICES = {
    "Paris": ["Tour Eiffel", "France", "Seine"],
    "Tokyo": ["Japon", "Shibuya", "Sakura"],
    "New York": ["Statue de la Liberté", "USA", "Manhattan"],
    "Londres": ["Big Ben", "Tamise", "UK"],
    "Le Caire": ["Pyramides", "Nil", "Égypte"],
    "Rio": ["Christ Rédempteur", "Brésil", "Carnaval"],
    "Dakar": ["Sénégal", "Pointe des Almadies", "Téranga"],
    "Abidjan": ["Côte d'Ivoire", "Cocody", "Lagune Ébrié"],
}

def devine_ville():
    ville, indices = random.choice(list(VILLES_INDICES.items()))
    print("\n🎯 DEVINE LA VILLE\n")
    for i, ind in enumerate(indices, 1):
        print(f"  Indice {i} : {ind}")
        r = input("  Votre réponse : ").strip()
        if r.lower() == ville.lower():
            print(f"✅ Bravo ! C'était {ville} (indice {i}/3)")
            ajouter_historique("Devine ville", f"{ville} - {i}/3")
            return
    print(f"\n❌ C'était {ville}")

# ============================================================
# OPTION 25 — HISTORIQUE
# ============================================================
def afficher_historique():
    hist = load_json(HISTORIQUE_FILE, [])
    if not hist:
        print("📭 Vide.")
        return
    print(f"\n📝 Historique ({len(hist)})\n")
    for e in hist[-20:]:
        print(f"  [{e['date'][:19]}] {e['action']} — {e.get('details', '')}")

# ============================================================
# OPTION 26 — PARAMÈTRES
# ============================================================
def parametres():
    print("\n⚙️  Paramètres")
    print("─" * 44)
    print(f"Version    : {APP_VERSION}")
    print(f"geopy      : {'✅' if GEOPY_OK else '❌'}")
    print(f"Pillow     : {'✅' if PIL_OK else '❌'}")
    print(f"qrcode     : {'✅' if QRCODE_OK else '❌'}")
    print(f"Cache géo  : {len(_GEO_CACHE)} entrées")
    print(f"Villes locales : {len(VILLES_LOCALES)}")
    print(f"Favoris    : {FAVORIS_FILE}")
    print(f"Historique : {HISTORIQUE_FILE}")
    print(f"Alarme cfg : {ALARM_CONFIG_FILE}")
    choix = input("\n🗑️  Vider l'historique ? (o/N) : ").strip().lower()
    if choix == "o":
        save_json(HISTORIQUE_FILE, [])
        print("✅ Vidé.")
    choix2 = input("🗑️  Vider le cache géocodeur ? (o/N) : ").strip().lower()
    if choix2 == "o":
        _GEO_CACHE.clear()
        save_json(GEO_CACHE_FILE, {})
        print("✅ Cache vidé.")



# ============================================================
# OPTION 30-42 — Modules V8
# ============================================================
def config_telegram():
    if iss_notify is None:
        print("iss_notify non disponible")
        return
    iss_notify.configurer_telegram()


def config_discord():
    if iss_notify is None:
        print("iss_notify non disponible")
        return
    iss_notify.configurer_discord()


def export_ical_menu():
    if iss_notify is None:
        print("iss_notify non disponible")
        return
    ville = input("Ville (Entree = config) : ").strip() or iss_alarm.config.get("lieu", "Abidjan")
    c = _geocode(ville)
    if c:
        lat, lon, _ = c
    else:
        lat = iss_alarm.config.get("lat")
        lon = iss_alarm.config.get("lon")
    if lat is None:
        print("Position requise")
        return
    from iss_pass import get_next_passes
    print("Calcul des passages (7 jours)...")
    passes = get_next_passes(lat, lon, hours=168, min_elevation=0, verbose=False)
    if not passes:
        print("Aucun passage")
        return
    f = iss_notify.export_ical(passes, lieu=ville)
    print(f"{len(passes)} passages exportes : {f}")
    print("   -> Importe ce .ics dans ton calendrier (Google/Outlook)")


def carte_ciel():
    if iss_visibility is None:
        print("iss_visibility non disponible")
        return
    ville = input("Ville (Entree = config) : ").strip() or iss_alarm.config.get("lieu", "Abidjan")
    c = _geocode(ville)
    if c:
        lat, lon, _ = c
    else:
        lat = iss_alarm.config.get("lat")
        lon = iss_alarm.config.get("lon")
    if lat is None:
        print("Position requise")
        return
    from iss_pass import get_next_passes
    print("Calcul des passages...")
    passes = get_next_passes(lat, lon, hours=48, min_elevation=0, verbose=False)
    if not passes:
        print("Aucun passage")
        return
    print("\n" + str(len(passes)) + " passages :\n")
    for i, p in enumerate(passes[:5], 1):
        print(f"  Passage #{i} - {p['risetime']:%d/%m %H:%M} UTC, max {p['max_elevation']:.0f} deg")
        print(iss_visibility.sky_chart(p))
        print()
    ajouter_historique("Carte ciel", ville)


def magnitude_passages():
    if iss_visibility is None:
        print("iss_visibility non disponible")
        return
    lat = iss_alarm.config.get("lat")
    lon = iss_alarm.config.get("lon")
    if lat is None:
        print("Aucune position")
        return
    from iss_pass import get_next_passes
    print("Calcul des passages...")
    passes = get_next_passes(lat, lon, hours=48, min_elevation=0, verbose=False)
    if not passes:
        print("Aucun passage")
        return
    print("\nMagnitude estimee :\n")
    print(f"{'Date':<14}{'Heure':<10}{'Elev':>6}{'Dist km':>10}{'Mag':>8}")
    print("-" * 55)
    for p in passes[:10]:
        mag = iss_visibility.compute_magnitude(p.get("distance_km", 500))
        mag_str = f"{mag:>6.1f}" if mag is not None else "   N/A"
        print(f"{p['risetime']:%d/%m %Y}  {p['risetime']:%H:%M}    "
              f"{p['max_elevation']:>4.0f}  "
              f"{p.get('distance_km', 0):>8.0f}  "
              f"{mag_str}  {iss_visibility.magnitude_label(mag)}")


def mode_veille():
    print("\nMode veille autonome (watch_iss.py)")
    print("-" * 48)
    print()
    print("Lance en arriere-plan :")
    print("  termux-wake-lock")
    print("  nohup python ~/map-ci/watch_iss.py > ~/.mapci_watch.log 2>&1 &")
    print()
    print("Consulter le log :")
    print("  tail -f ~/.mapci_watch.log")
    print()
    print("Arreter :")
    print("  pkill -f watch_iss.py")
    print("  termux-wake-unlock")


def menu_multi_satellites():
    if iss_multisat is None:
        print("iss_multisat non disponible")
        return
    print("\nSatellites disponibles (extrait) :")
    names = iss_multisat.list_available()
    for n in names[:15]:
        print(f"  - {n}")
    print(f"  ... {len(names)} au total\n")
    target = input("Satellite (iss/hubble/tiangong/noaa/starlink) : ").strip().lower()
    if not target:
        return
    lat = iss_alarm.config.get("lat")
    lon = iss_alarm.config.get("lon")
    if lat is None:
        print("Position non configuree")
        return
    print(f"Calcul des passages pour {target}...")
    passes, info = iss_multisat.get_satellite_passes(target, lat, lon, hours=48)
    if not passes:
        print(f"Erreur : {info}")
        return
    print(f"\n{info} : {len(passes)} passage(s)\n")
    for p in passes[:10]:
        rise_c = iss_multisat.az_to_cardinal(p["az_rise"])
        set_c = iss_multisat.az_to_cardinal(p["az_set"])
        print(f"  {p['risetime']:%d/%m %H:%M} -> {p['settime']:%H:%M}  "
              f"| {p['duration_s']:.0f}s | max {p['max_elevation']:.0f} deg | {rise_c}->{set_c}")


def menu_observations():
    if iss_observe is None:
        print("iss_observe non disponible")
        return
    iss_observe.afficher()
    print()
    print("  A. Ajouter | S. Supprimer derniere | R. Reset | Entree. Retour")
    c = input("Choix : ").strip().upper()
    if c == "A":
        iss_observe.marquer_interactif(iss_alarm.config.get("lieu", "Abidjan"))
    elif c == "S":
        iss_observe.supprimer_derniere()
    elif c == "R":
        iss_observe.reset()


def menu_multi_positions():
    if iss_multipos is None:
        print("iss_multipos non disponible")
        return
    iss_multipos.menu_interactif()


def menu_meteo_passage():
    if iss_visibility is None:
        print("iss_visibility non disponible")
        return
    lat = iss_alarm.config.get("lat")
    lon = iss_alarm.config.get("lon")
    if lat is None:
        print("Aucune position")
        return
    from iss_pass import get_next_passes
    print("Calcul des passages + meteo...")
    passes = get_next_passes(lat, lon, hours=24, min_elevation=0, verbose=False)
    if not passes:
        print("Aucun passage")
        return
    print("\nMeteo + visibilite pour les prochains passages :\n")
    for p in passes[:5]:
        w = iss_visibility.get_weather(lat, lon, p["risetime"])
        if w:
            note, msg = iss_visibility.meteo_verdict(w)
            print(f"  {p['risetime']:%d/%m %H:%M}  {note}  {msg}")
        else:
            print(f"  {p['risetime']:%d/%m %H:%M}  ? Meteo indispo")


def menu_rapport_journalier():
    try:
        from daily_report import build_report, send_report
        print(build_report())
        print()
        c = input("Envoyer sur Telegram/Discord ? (o/N) : ").strip().lower()
        if c == "o":
            send_report()
    except Exception as e:
        print(f"Erreur : {e}")


def menu_api_rest():
    print("\nAPI REST locale")
    print("-" * 44)
    print("Lance l'API dans un terminal separe :")
    print("  cd ~/map-ci")
    print("  python iss_api.py")
    print()
    print("Puis teste depuis un autre terminal :")
    print("  curl http://127.0.0.1:5000/status")
    print('  curl "http://127.0.0.1:5000/passes?hours=24"')


def menu_widget():
    if iss_notify is None:
        print("iss_notify non disponible")
        return
    lat = iss_alarm.config.get("lat")
    lon = iss_alarm.config.get("lon")
    if lat is None:
        print("Position requise")
        return
    from iss_pass import get_next_passes
    from datetime import datetime
    passes = get_next_passes(lat, lon, hours=24, min_elevation=0, verbose=False)
    if not passes:
        print("Aucun passage")
        return
    p = passes[0]
    now = datetime.now(p["risetime"].tzinfo)
    delta = (p["risetime"] - now).total_seconds()
    mins = int(delta // 60)
    msg = f"Prochain ISS dans {mins} min - {iss_alarm.config.get('lieu', '?')} (max {p['max_elevation']:.0f} deg)"
    if iss_notify.update_widget(msg):
        print(f"Widget mis a jour : {msg}")
    else:
        print("Termux:API non disponible")





# ============================================================
# OPTIONS 43-50 - Pack V9
# ============================================================
def menu_aurores():
    if iss_aurora is None:
        print("iss_aurora non disponible")
        return
    kp = iss_aurora.get_current_kp()
    level, desc, emoji = iss_aurora.aurora_level(kp)
    print(f"\n{emoji}  Aurores boreales")
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
    print("\nProchaines pluies d'etoiles filantes :\n")
    for m in iss_meteors.prochains_meteors(10):
        emoji = "***" if m["zhr"] > 80 else "**" if m["zhr"] > 30 else "-"
        print(f"  {emoji} {m['nom']:<20} {m['date']:%d/%m/%Y}  "
              f"dans {m['jours']:>3}j  ZHR {m['zhr']:>3}  ({m['radiant']})")


def menu_eclipses():
    if iss_eclipses is None:
        print("iss_eclipses non disponible")
        return
    print("\nProchaines eclipses :\n")
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
    print("\nPlanetes visibles maintenant :\n")
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
        print(f"\n{len(nouveaux)} nouveau(x) badge(s) !")
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
    print("\nNotifications ntfy.sh")
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
    print("\nInterface Web MAP-CI V9")
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


# ============================================================
# MENU
# ============================================================
MENU = [
    ("1",  "🔎 Rechercher ville",           rechercher_ville),
    ("2",  "🗺️  Carte (OSM/Google)",         afficher_carte),
    ("3",  "📷 Image GPS EXIF",             extraire_gps_exif),
    ("4",  "🌦️  Meteo actuelle",             meteo_actuelle),
    ("5",  "📅 Meteo 7 jours",              meteo_7_jours),
    ("6",  "💨 Qualite de l'air",           qualite_air),
    ("7",  "📍 Ma position (IP)",           ma_position_ip),
    ("8",  "🧭 Distance + itineraire",      distance_itineraire),
    ("9",  "🛰️  Position ISS",               position_iss),
    ("P",  "🛰️  Prochains passages ISS",     passages_iss),
    ("10", "🌐 Fuseaux horaires",           fuseaux_horaires),
    ("11", "🏔️  Altitude d'un lieu",         altitude_lieu),
    ("12", "🏛️  Points d'interet",           points_interet),
    ("13", "🌕 Phase de la Lune",           phase_lune),
    ("14", "🚀 Lancements spatiaux",        lancements_spatiaux),
    ("15", "📋 QR code position",           qr_code_position),
    ("16", "📤 Export GPX",                 export_gpx),
    ("17", "📊 Tableau de bord",            tableau_de_bord),
    ("18", "📌 Favoris",                    gerer_favoris),
    ("19", "📸 Golden hour",                golden_hour),
    ("20", "🚨 Seismes recents",            seismes_recents),
    ("21", "🎲 Coords aleatoires",          coords_aleatoires),
    ("22", "🎮 Quiz capitales",             quiz_capitales),
    ("23", "🏴‍☠️  Chasse au tresor",          chasse_tresor),
    ("24", "🎯 Jeu devine ville",           devine_ville),
    ("25", "📝 Historique",                 afficher_historique),
    ("26", "⚙️  Parametres",                 parametres),
    ("27", "🚨 Alarme ISS (config)",        iss_alarm.configurer),
    ("28", "🔔 Statut alarme ISS",          iss_alarm.statut),
    ("29", "🧪 Tester l'alarme",            iss_alarm.tester),
    ("30", "Config Telegram",              config_telegram),
    ("31", "Config Discord",               config_discord),
    ("32", "Export iCal (7 jours)",        export_ical_menu),
    ("33", "Carte ASCII du ciel",          carte_ciel),
    ("34", "Magnitude estimee",            magnitude_passages),
    ("35", "Mode veille",                  mode_veille),
    ("36", "Multi-satellites",             menu_multi_satellites),
    ("37", "Mes observations",             menu_observations),
    ("38", "Multi-positions",              menu_multi_positions),
    ("39", "Meteo des passages",           menu_meteo_passage),
    ("40", "Rapport journalier",           menu_rapport_journalier),
    ("41", "API REST (info)",              menu_api_rest),
    ("42", "Widget permanent",             menu_widget),
    ("43", "Aurores boreales (Kp)",        menu_aurores),
    ("44", "Pluies etoiles filantes",      menu_meteors),
    ("45", "Eclipses",                     menu_eclipses),
    ("46", "Planetes visibles",            menu_planetes),
    ("47", "Achievements",                 menu_achievements),
    ("48", "Mes statistiques",             menu_stats),
    ("49", "Notifications ntfy.sh",        menu_ntfy),
    ("50", "Interface Web (info)",         menu_web_app),
    ("0",  "Quitter",                      None),
]

def show_menu():
    clear()
    w = shutil.get_terminal_size((80, 30)).columns
    width = min(54, max(44, w - 2))

    print_header()
    if iss_alarm.config["enabled"]:
        if iss_alarm.config.get("lat") is not None:
            st = f"🚨 ISS ALARME ON — {iss_alarm.config.get('lieu','?')}"
        else:
            st = "⚠️  ISS alarme ON mais SANS POSITION (option 27)"
    else:
        st = "🔕 ISS alarme OFF"
    print(f"  {st}".ljust(width))

    if (iss_alarm.config.get("enabled")
            and iss_alarm.config.get("lat") is not None
            and iss_alerts is not None):
        try:
            info = iss_alerts.next_pass_summary(
                iss_alarm.config["lat"], iss_alarm.config["lon"]
            )
            if info:
                print(f"  {info}".ljust(width))
        except Exception:
            pass
    print()

    for key, label, _ in MENU:
        print(f"  {key:>2}. {label}")

    print("  " + "─" * (width - 4))
    return input("👉 Choix : ").strip().upper()

def main():
    if iss_alarm.config.get("enabled"):
        if iss_alarm.config.get("lat") is None:
            print("\n⚠️  L'alarme ISS est activée mais sans position.")
            print("   → Fais l'option 27 avec 'M' pour saisir les coordonnées.\n")
            time.sleep(2)
        else:
            iss_alarm.start()

    while True:
        try:
            choice = show_menu()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Au revoir !")
            break

        if choice == "0":
            iss_alarm.stop()
            print("👋 Au revoir !")
            break

        action = next((f for k, _, f in MENU if k == choice), None)
        if action is None:
            print("\n❌ Choix invalide.")
            pause()
            continue

        try:
            print()
            action()
        except Exception as e:
            print(f"\n❌ Erreur : {e}")
        pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        iss_alarm.stop()
        print("\n👋 Interrompu.")
