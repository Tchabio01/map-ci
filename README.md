# 🗺️ MAP-CI V8

> Station de suivi spatial et d'observation ISS pour Termux / Linux / macOS / Windows

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Termux](https://img.shields.io/badge/Termux-ready-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

## 🎯 Fonctionnalités

- 🛰️ **Calcul local des passages ISS** (Skyfield + TLE Celestrak)
- 🚨 **Alarme automatique** avant chaque passage (Android + Telegram + Discord + SMS)
- 🧭 **Azimut et direction** (N→SE, O→NE...)
- 🔭 **Magnitude estimée** (brillance du satellite)
- 🌦️ **Météo des passages** (visibilité nuageuse)
- 🌌 **Carte ASCII** de la trajectoire
- 📱 **Notifications Android natives** (Termux:API) + vibration + voix
- 📅 **Export iCal** (calendrier Google/Outlook)
- 🌐 **API REST** locale (Flask)
- 🛰️ **Multi-satellites** : ISS, Hubble, Tiangong, NOAA, Starlink...
- 📍 **Multi-positions** : surveille plusieurs villes
- 📝 **Historique d'observations** (vu/raté + notes)
- 🎮 **Jeux géographiques** (quiz capitales, chasse au trésor)
- 📊 **Dashboard temps réel**

## 📦 Installation

### Termux (Android)

```bash
pkg update && pkg upgrade -y
pkg install python python-numpy termux-api -y
pip install -r requirements.txt

git clone https://github.com/Tcabio01/map-ci.git
cd map-ci
python mapci.py
```

### Linux / macOS / Windows

```bash
git clone https://github.com/Tcabio01/map-ci.git
cd map-ci
pip install -r requirements.txt
python mapci.py
```

## 🚀 Utilisation rapide

1. **Configurer l'alarme** : Option `27` → entre `abidjan` (ou `M` pour manuel) → seuil `40` min
2. **Voir les passages** : Option `P`
3. **Tester l'alerte** : Option `29`
4. **Config Telegram** : Option `30`

## 📁 Structure

```
map-ci/
├── mapci.py              # Menu principal (42 options)
├── iss_pass.py           # Calcul Skyfield (ISS, passages)
├── iss_alerts.py         # Notifications Android + SMS + TTS
├── iss_visibility.py     # Météo, magnitude, carte ASCII
├── iss_notify.py         # Telegram, Discord, iCal, widget
├── iss_multisat.py       # Suivi multi-satellites
├── iss_observe.py        # Historique d'observations
├── iss_multipos.py       # Multi-positions
├── iss_api.py            # API REST Flask
├── watch_iss.py          # Mode veille autonome
└── daily_report.py       # Rapport journalier
```

## 🔑 APIs utilisées

| Service | Usage |
|---|---|
| **Celestrak** | TLE des satellites |
| **Open-Meteo** | Météo + qualité de l'air |
| **Photon (komoot)** | Géocodage |
| **ip-api.com** | Position IP |
| **USGS** | Séismes |
| **Open Notify** | Position ISS actuelle |
| **The Space Devs** | Lancements spatiaux |

## 📱 Termux:API

Pour les notifications Android, installe l'app **Termux:API** depuis [F-Droid](https://f-droid.org/packages/com.termux.api/).

## 📄 Licence

MIT — voir [LICENSE](LICENSE)

## 🙏 Crédits

- [Skyfield](https://rhodesmill.org/skyfield/) — calculs orbitaux
- [Celestrak](https://celestrak.org/) — TLE
- [Photon](https://photon.komoot.io/) — géocodage
- [Open-Meteo](https://open-meteo.com/) — météo

---

🛰️ **Bon ciel !**
