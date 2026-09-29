#!/usr/bin/env python3
# daily_report.py — Rapport journalier (à lancer via cron au lever)
# v1.0
import json
from datetime import datetime, timezone
from pathlib import Path

ALARM = Path.home() / ".mapci_alarm.json"


def get_config():
    if ALARM.exists():
        try:
            return json.loads(ALARM.read_text())
        except Exception:
            pass
    return {}


def build_report():
    cfg = get_config()
    lat = cfg.get("lat")
    lon = cfg.get("lon")
    lieu = cfg.get("lieu", "?")
    if lat is None:
        return "⚠️ Aucune position configurée."

    from iss_pass import get_next_passes
    from iss_visibility import (
        compute_magnitude, magnitude_label,
        get_weather, meteo_verdict,
    )

    passes = get_next_passes(lat, lon, hours=24, min_elevation=0, verbose=False)

    now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y")
    lines = [
        f"🛰️ *Rapport ISS — {now_str}*",
        f"📍 {lieu}",
        "",
    ]

    if not passes:
        lines.append("Aucun passage dans les 24h.")
    else:
        lines.append(f"*{len(passes)} passage(s)* aujourd'hui :")
        lines.append("")
        for i, p in enumerate(passes[:5], 1):
            mag = compute_magnitude(p.get("distance_km", 500))
            w = get_weather(lat, lon, p["risetime"])
            if w:
                note, _ = meteo_verdict(w)
            else:
                note = "❓"
            rise = p.get("cardinal_rise", "?")
            setc = p.get("cardinal_set", "?")
            lines.append(
                f"{i}. `{p['risetime']:%H:%M}` → `{p['settime']:%H:%M}` UTC"
            )
            lines.append(
                f"   max *{p['max_elevation']:.0f}°* | {rise}→{setc} | "
                f"{note} météo | mag {mag} ({magnitude_label(mag)})"
            )
            lines.append("")

    return "\n".join(lines)


def send_report():
    text = build_report()
    print(text)
    print()
    try:
        from iss_notify import send_telegram, send_discord
        ok_tg = send_telegram(text)
        ok_dc = send_discord(text)
        if ok_tg:
            print("📤 Envoyé sur Telegram")
        if ok_dc:
            print("📤 Envoyé sur Discord")
        if not ok_tg and not ok_dc:
            print("💡 Configure Telegram (option 30) ou Discord (option 31) "
                  "pour recevoir ce rapport automatiquement.")
    except Exception as e:
        print(f"⚠️  {e}")


if __name__ == "__main__":
    send_report()
