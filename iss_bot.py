#!/usr/bin/env python3
"""iss_bot.py — Bot Telegram interactif pour MAP-CI"""
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timezone

TG_CONFIG = Path.home() / ".mapci_telegram.json"
ALARM_CONFIG = Path.home() / ".mapci_alarm.json"


def load_config():
    if not TG_CONFIG.exists():
        return None
    try:
        return json.loads(TG_CONFIG.read_text())
    except Exception:
        return None


def load_alarm():
    if ALARM_CONFIG.exists():
        try:
            return json.loads(ALARM_CONFIG.read_text())
        except Exception:
            pass
    return {}


def send_message(token, chat_id, text, markdown=True):
    try:
        data = {"chat_id": chat_id, "text": text}
        if markdown:
            data["parse_mode"] = "Markdown"
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data, timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


def get_updates(token, offset=None):
    try:
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset
        r = requests.get(
            f"https://api.telegram.org/bot{token}/getUpdates",
            params=params, timeout=35,
        )
        return r.json().get("result", [])
    except Exception:
        return []


# ---------- COMMANDES ----------
def cmd_help():
    return (
        "🛰️ *MAP-CI Tchabio* — Commandes disponibles :\n\n"
        "/status — État de l'alarme\n"
        "/passes — Prochains passages ISS (48h)\n"
        "/iss — Position actuelle de l'ISS\n"
        "/aujourdhui — Résumé du jour\n"
        "/help — Cette aide"
    )


def cmd_status():
    cfg = load_alarm()
    if not cfg.get("enabled"):
        return "🔕 *Alarme ISS désactivée*\n\nLance option 27 dans MAP-CI."
    return (
        f"🚨 *Alarme ISS active*\n\n"
        f"📍 Lieu : {cfg.get('lieu', '?')}\n"
        f"📡 Coords : {cfg.get('lat')}, {cfg.get('lon')}\n"
        f"⏱️ Seuil : {cfg.get('seuil_minutes')} min\n"
        f"⏳ Durée mini : {cfg.get('duree_min')} s"
    )


def cmd_passes():
    cfg = load_alarm()
    lat = cfg.get("lat")
    lon = cfg.get("lon")
    if lat is None:
        return "❌ Position non configurée"
    try:
        from iss_pass import get_next_passes
        passes = get_next_passes(lat, lon, hours=48, min_elevation=0, verbose=False)
        if not passes:
            return "❌ Aucun passage dans les 48h"
        lines = [f"🛰️ *{len(passes)} prochains passages ISS*\n"]
        for i, p in enumerate(passes[:5], 1):
            rt = p["risetime"]
            lines.append(
                f"*{i}.* {rt:%d/%m %H:%M} UTC\n"
                f"   max {p['max_elevation']:.0f}° | "
                f"{p.get('cardinal_rise', '?')}→{p.get('cardinal_set', '?')} | "
                f"{p['duration_s']:.0f}s"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Erreur : {e}"


def cmd_iss():
    try:
        d = requests.get("http://api.open-notify.org/iss-now.json", timeout=10).json()
        p = d["iss_position"]
        ts = datetime.fromtimestamp(d["timestamp"], tz=timezone.utc)
        return (
            f"🛰️ *Position ISS*\n\n"
            f"📡 Lat : {p['latitude']}°\n"
            f"📡 Lon : {p['longitude']}°\n"
            f"⏰ {ts:%H:%M:%S} UTC\n\n"
            f"[Voir sur OSM](https://www.openstreetmap.org/?mlat={p['latitude']}&mlon={p['longitude']}#map=3/{p['latitude']}/{p['longitude']})"
        )
    except Exception as e:
        return f"❌ Erreur : {e}"


def cmd_aujourdhui():
    try:
        from daily_report import build_report
        return build_report()
    except Exception as e:
        return f"❌ Erreur : {e}"


def traiter_commande(text):
    cmd = text.strip().lower().split()[0] if text.strip() else ""
    if cmd in ("/start", "/help", "/aide"):
        return cmd_help()
    if cmd == "/status":
        return cmd_status()
    if cmd == "/passes":
        return cmd_passes()
    if cmd == "/iss":
        return cmd_iss()
    if cmd in ("/aujourdhui", "/jour"):
        return cmd_aujourdhui()
    return "❓ Commande inconnue. Envoie /help pour la liste."


# ---------- BOUCLE PRINCIPALE ----------
def main():
    cfg = load_config()
    if not cfg:
        print("❌ Configuration Telegram manquante")
        print("   Lance d'abord l'option 30 dans MAP-CI")
        return
    token = cfg.get("token")
    chat_id = cfg.get("chat_id")
    if not token or not chat_id:
        print("❌ Token ou chat_id manquant")
        return

    print(f"🤖 Bot MAP-CI démarré (chat_id : ...{str(chat_id)[-4:]})")
    print("   Envoie /help sur Telegram pour tester")
    print("   Ctrl+C pour arrêter\n")

    last_update_id = None
    while True:
        try:
            updates = get_updates(token, offset=last_update_id)
            for u in updates:
                last_update_id = u["update_id"] + 1
                msg = u.get("message")
                if not msg:
                    continue
                text = msg.get("text", "")
                from_chat = msg.get("chat", {}).get("id")
                if not text:
                    continue
                # Sécurité : ne répond qu'à ton chat
                if str(from_chat) != str(chat_id):
                    continue
                print(f"[{datetime.now():%H:%M:%S}] Reçu : {text}")
                reponse = traiter_commande(text)
                send_message(token, chat_id, reponse)
        except KeyboardInterrupt:
            print("\n👋 Bot arrêté.")
            break
        except Exception as e:
            print(f"⚠️  Erreur : {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
