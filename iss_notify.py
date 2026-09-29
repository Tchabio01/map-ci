# iss_notify.py — Telegram, Discord, iCal, widget permanent
# v1.1 — Corrigé pour Termux (timezone-aware, chemins)
import json
import subprocess
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

TG_CONFIG = Path.home() / ".mapci_telegram.json"
DC_CONFIG = Path.home() / ".mapci_discord.json"
ICAL_FILE = Path.home() / "mapci_passes.ics"

try:
    import requests
except ImportError:
    requests = None


# ============================================================
# TELEGRAM
# ============================================================
def send_telegram(message, markdown=True):
    if not TG_CONFIG.exists() or requests is None:
        return False
    try:
        cfg = json.loads(TG_CONFIG.read_text())
        token = cfg.get("token")
        chat_id = cfg.get("chat_id")
        if not token or not chat_id:
            return False
        data = {"chat_id": chat_id, "text": message}
        if markdown:
            data["parse_mode"] = "Markdown"
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data, timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


def configurer_telegram():
    print("\n📱 Configuration Telegram")
    print("─" * 44)
    print("1. Ouvre Telegram, cherche @BotFather")
    print("2. Envoie /newbot et suis les instructions")
    print("3. Récupère le token (ex: 123456:ABC...)")
    print("4. Envoie /start à ton bot")
    print("5. Ouvre https://api.telegram.org/bot<TOKEN>/getUpdates")
    print('   → cherche "chat":{"id":...}')
    print()
    token = input("Token bot : ").strip()
    if not token:
        print("❌ Annulé")
        return
    chat_id = input("Chat ID   : ").strip()
    if not chat_id:
        print("❌ Annulé")
        return
    TG_CONFIG.write_text(
        json.dumps({"token": token, "chat_id": chat_id}, indent=2)
    )
    print("✅ Config sauvegardée")
    if send_telegram("✅ *MAP-CI V8* : Telegram configuré !"):
        print("📤 Message test envoyé")
    else:
        print("❌ Échec envoi test (vérifie token/chat_id)")


# ============================================================
# DISCORD
# ============================================================
def send_discord(message):
    if not DC_CONFIG.exists() or requests is None:
        return False
    try:
        cfg = json.loads(DC_CONFIG.read_text())
        url = cfg.get("webhook_url")
        if not url:
            return False
        r = requests.post(url, json={"content": message}, timeout=10)
        return r.status_code in (200, 204)
    except Exception:
        return False


def configurer_discord():
    print("\n💬 Configuration Discord")
    print("─" * 44)
    print("Salon → Paramètres → Intégrations → Webhooks → Nouveau")
    print()
    url = input("URL Webhook : ").strip()
    if not url:
        print("❌ Annulé")
        return
    DC_CONFIG.write_text(json.dumps({"webhook_url": url}, indent=2))
    print("✅ Config sauvegardée")
    if send_discord("✅ **MAP-CI V8** : Discord configuré !"):
        print("📤 Message test envoyé")
    else:
        print("❌ Échec envoi test")


# ============================================================
# iCAL
# ============================================================
def _to_ical_utc(dt):
    """Convertit un datetime (naif ou aware) en string iCal UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def export_ical(passes, lieu="Position", filename=None):
    """Exporte les passages au format .ics (importable calendrier)."""
    filename = filename or str(ICAL_FILE)
    now_stamp = _to_ical_utc(datetime.now(timezone.utc))

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//MAP-CI//ISS Passes//FR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for p in passes:
        rt = p["risetime"]
        st = p["settime"]
        uid = f"{int(rt.timestamp())}@mapci"
        summary = f"ISS - max {p['max_elevation']:.0f}deg - {lieu}"
        desc = (
            f"Duree {p['duration_s']:.0f}s | "
            f"{p.get('cardinal_rise', '?')}->{p.get('cardinal_set', '?')} | "
            f"{p.get('distance_km', 0):.0f} km"
        )
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_stamp}",
            f"DTSTART:{_to_ical_utc(rt)}",
            f"DTEND:{_to_ical_utc(st)}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{desc}",
            "BEGIN:VALARM",
            "TRIGGER:-PT40M",
            "ACTION:DISPLAY",
            "DESCRIPTION:Rappel passage ISS",
            "END:VALARM",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    Path(filename).write_text("\r\n".join(lines), encoding="utf-8")
    return filename


# ============================================================
# WIDGET PERMANENT (notification Android)
# ============================================================
def update_widget(message, title="MAP-CI ISS"):
    """Met à jour la notification permanente Android."""
    if not shutil.which("termux-notification"):
        return False
    try:
        subprocess.run(
            [
                "termux-notification",
                "--id", "mapci_widget",
                "--title", title,
                "--content", message,
                "--priority", "low",
                "--ongoing",
            ],
            check=False, timeout=5,
        )
        return True
    except Exception:
        return False


def remove_widget():
    if not shutil.which("termux-notification-remove"):
        return False
    try:
        subprocess.run(
            ["termux-notification-remove", "mapci_widget"],
            check=False, timeout=5,
        )
        return True
    except Exception:
        return False


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("Test iss_notify.py\n")
    print("Telegram config :", TG_CONFIG.exists())
    print("Discord config  :", DC_CONFIG.exists())
    print("Widget Termux   :", shutil.which("termux-notification") is not None)
    print()

    # Test iCal avec données fictives
    fake = [
        {
            "risetime": datetime.now(timezone.utc) + timedelta(hours=2),
            "settime": datetime.now(timezone.utc) + timedelta(hours=2, minutes=10),
            "max_elevation": 30,
            "duration_s": 600,
            "az_rise": 10,
            "az_set": 200,
            "cardinal_rise": "N",
            "cardinal_set": "SO",
            "distance_km": 500,
        }
    ]
    test_path = str(Path.home() / "test.ics")
    f = export_ical(fake, lieu="Abidjan", filename=test_path)
    print(f"📅 iCal exporté : {f}")

    if Path(f).exists():
        content = Path(f).read_text()
        print(f"   Taille : {len(content)} octets")
        print(f"   Contient BEGIN:VEVENT : {'BEGIN:VEVENT' in content}")

    # Test widget
    if update_widget("Test widget — prochain ISS dans 2h"):
        print("🔔 Widget mis à jour (regarde la barre de notifications)")
    else:
        print("⚠️  termux-notification indisponible (installe Termux:API)")
