"""iss_aurora.py — Alertes aurores boréales (NOAA Kp index)"""
import requests

def get_kp_forecast():
    """Retourne les 8 prochains Kp (3h chacun)."""
    try:
        r = requests.get("https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json", timeout=10)
        data = r.json()
        # Skip header
        out = []
        for row in data[1:12]:
            out.append({"time": row[0], "kp": float(row[1]), "status": row[2]})
        return out
    except Exception as e:
        return None

def get_current_kp():
    try:
        r = requests.get("https://services.swpc.noaa.gov/json/planetary_k_index_1m.json", timeout=10)
        data = r.json()
        if data:
            return float(data[-1].get("kp_index", 0))
    except Exception:
        pass
    return None

def aurora_level(kp):
    """Niveau d'aurore selon Kp."""
    if kp is None: return "?", "Inconnu", "⚪"
    if kp < 3: return "Calme", "Pas d'aurore significative", "🟢"
    if kp < 5: return "Actif", "Aurores possibles hautes latitudes", "🟡"
    if kp < 6: return "Orage G1", "Aurores visibles nord", "🟠"
    if kp < 7: return "Orage G2", "Belles aurores nord", "🔴"
    if kp < 8: return "Orage G3", "Aurores étendues", "🟣"
    return "Orage G4+", "Aurores jusqu'en Europe centrale !", "⚫"

def check_alert(threshold=5):
    """Retourne True si Kp >= threshold (aurores)."""
    kp = get_current_kp()
    return kp is not None and kp >= threshold

if __name__ == "__main__":
    print("Test iss_aurora.py\n")
    kp = get_current_kp()
    level, desc, emoji = aurora_level(kp)
    print(f"Kp actuel : {kp} {emoji} {level}")
    print(f"→ {desc}\n")
    print("Prévisions :")
    fc = get_kp_forecast()
    if fc:
        for f in fc[:8]:
            print(f"  {f['time']}  Kp {f['kp']}")
