#!/usr/bin/env python3
# watch_iss.py — Mode veille autonome (widget + Telegram + Discord + SMS)
# v1.0
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ALARM_CONFIG = Path.home() / ".mapci_alarm.json"
CHECK_INTERVAL = 300      # 5 min
WIDGET_REFRESH = 900      # 15 min

_last_widget = 0
_notified = set()


def load_config():
    if not ALARM_CONFIG.exists():
        return None
    try:
        return json.loads(ALARM_CONFIG.read_text())
    except Exception:
        return None


def beep():
    print("\a", end="", flush=True)


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def notifier(titre, msg):
    """Notifie via tous les canaux disponibles."""
    try:
        from iss_alerts import notifier_android, vibrer, parler, envoyer_sms
        notifier_android(titre, msg)
        vibrer(800)
        parler("Attention, I S S dans quelques minutes")
        envoyer_sms(f"[MAP-CI] {titre}")
    except Exception:
        pass

    try:
        from iss_notify import send_telegram, send_discord
        send_telegram(f"🛰️ *{titre}*\n{msg}")
        send_discord(f"🛰️ **{titre}**\n{msg}")
    except Exception:
        pass


def main():
    global _last_widget
    log("🚀 MAP-CI Watch V8 démarré")
    log(f"   Config : {ALARM_CONFIG}")
    log(f"   Vérif toutes les {CHECK_INTERVAL} s")
    log("")

    while True:
        cfg = load_config()
        if not cfg or not cfg.get("enabled") or cfg.get("lat") is None:
            log("⏸️  Alarme désactivée ou position manquante")
            time.sleep(CHECK_INTERVAL)
            continue

        try:
            from iss_pass import get_next_passes
            lat = cfg["lat"]
            lon = cfg["lon"]
            lieu = cfg.get("lieu", "?")
            seuil = cfg.get("seuil_minutes", 60) * 60
            duree_min = cfg.get("duree_min", 0)

            log(f"🔍 Vérif passages pour {lieu}...")
            passes = get_next_passes(lat, lon, hours=24, min_elevation=0, verbose=False)
            if not passes:
                log("   Aucun passage")
                time.sleep(CHECK_INTERVAL)
                continue

            now = datetime.now(passes[0]["risetime"].tzinfo)
            next_p = passes[0]
            delta_next = (next_p["risetime"] - now).total_seconds()
            mins_next = int(delta_next // 60)
            log(f"   Prochain : dans {mins_next} min ({next_p['max_elevation']:.0f}°)")

            # Rafraîchit le widget
            if time.time() - _last_widget > WIDGET_REFRESH:
                try:
                    from iss_notify import update_widget
                    update_widget(
                        f"Prochain ISS dans {mins_next} min — {lieu} "
                        f"(max {next_p['max_elevation']:.0f}°)"
                    )
                    _last_widget = time.time()
                except Exception:
                    pass

            # Cherche un passage dans la fenêtre seuil
            for p in passes:
                delta = (p["risetime"] - now).total_seconds()
                key = p["risetime"].isoformat()

                if p["duration_s"] < duree_min:
                    continue

                if 0 < delta <= seuil and key not in _notified:
                    mins = int(delta // 60)
                    titre = f"ISS dans {mins} min"
                    msg = (
                        f"Risetime {p['risetime']:%H:%M:%S} UTC\n"
                        f"Duree {p['duration_s']:.0f}s | Max {p['max_elevation']:.0f}°\n"
                        f"Direction {p.get('cardinal_rise', '?')} → "
                        f"{p.get('cardinal_set', '?')}\n"
                        f"Lieu : {lieu}"
                    )
                    log(f"🚨 ALERTE : {titre}")
                    print()
                    print("=" * 52)
                    print("🚨  A L E R T E   I S S  🚨".center(52))
                    print("=" * 52)
                    print(msg)
                    print("=" * 52)
                    print()
                    beep()
                    notifier(titre, msg)
                    _notified.add(key)
                    if len(_notified) > 50:
                        _notified = set(list(_notified)[-30:])

        except Exception as e:
            log(f"❌ Erreur : {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Watch arrêté.")
