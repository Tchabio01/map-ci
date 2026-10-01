"""iss_charts.py - Graphiques ASCII pour stats et passages"""

def bar_chart(data, width=30, title=""):
    """Bar chart horizontal. data = [(label, value), ...]"""
    if not data:
        return "Aucune donnee"
    max_val = max(v for _, v in data) or 1
    lines = []
    if title:
        lines.append(f"📊 {title}")
        lines.append("")
    for label, value in data:
        bar_len = int((value / max_val) * width)
        bar = "█" * bar_len + "░" * (width - bar_len)
        lines.append(f"  {label:<14} {bar} {value}")
    return "\n".join(lines)


def elevation_chart(passes):
    """Graphique d'élévation des prochains passages."""
    if not passes:
        return "Aucun passage"
    data = []
    for i, p in enumerate(passes[:8], 1):
        elev = int(p["max_elevation"])
        emoji = "🟢" if elev > 60 else "🟡" if elev > 30 else "⚪"
        data.append((f"#{i} {p['risetime']:%d/%m}", elev))
    return bar_chart(data, width=25, title="Élévation max (degrés)")


def duration_chart(passes):
    """Durée des passages."""
    if not passes:
        return "Aucun passage"
    data = []
    for i, p in enumerate(passes[:8], 1):
        dur = int(p["duration_s"])
        data.append((f"#{i}", dur))
    return bar_chart(data, width=25, title="Durée (secondes)")


def week_heatmap(passes):
    """Heatmap des 7 prochains jours."""
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    days = {}
    for p in passes:
        delta_days = (p["risetime"] - now).days
        if 0 <= delta_days < 7:
            days.setdefault(delta_days, []).append(p["max_elevation"])

    lines = ["🗓️ *Visibilité cette semaine*", ""]
    for d in range(7):
        date = now + timedelta(days=d)
        elevs = days.get(d, [])
        if not elevs:
            bar = "·" * 20
            txt = "aucun"
        else:
            best = max(elevs)
            n = len(elevs)
            # Intensité selon la meilleure élévation
            if best > 60:
                bar = "🟩" * n + "⬜" * (7 - min(7, n))
            elif best > 30:
                bar = "🟨" * n + "⬜" * (7 - min(7, n))
            else:
                bar = "⬜" * n + "⬜" * (7 - min(7, n))
            txt = f"{n} passage(s) — max {best:.0f}°"
        jour = date.strftime("%a %d/%m")
        lines.append(f"  {jour:<12} {bar} {txt}")
    lines.append("")
    lines.append("🟩 Excellent (>60°) · 🟨 Bon (>30°) · ⬜ Faible")
    return "\n".join(lines)


def stats_summary(stats):
    """Résumé graphique des statistiques."""
    lines = ["📈 *Statistiques visuelles*", ""]
    total = stats.get("total", 0)
    vus = stats.get("vus", 0)
    rates = stats.get("rates", 0)
    if vus + rates > 0:
        pct = vus / (vus + rates) * 100
        filled = int(pct / 100 * 20)
        bar = "█" * filled + "░" * (20 - filled)
        lines.append(f"  Taux de réussite :")
        lines.append(f"  [{bar}] {pct:.0f}%")
        lines.append("")
    lines.append(f"  ✅ Vus      : {vus}")
    lines.append(f"  ❌ Ratés    : {rates}")
    lines.append(f"  📊 Total    : {total}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Test
    data = [("Paris", 12), ("Abidjan", 8), ("Dakar", 5), ("Tokyo", 15)]
    print(bar_chart(data, title="Test villes"))
