"""iss_i18n.py - Internationalisation (fr/en/es/ar)"""
import json
from pathlib import Path

LANG_FILE = Path.home() / ".mapci_lang.json"

STRINGS = {
    "fr": {
        "menu_title": "🛰️ MAP-CI Tchabio",
        "menu_intro": "👋 Que veux-tu faire aujourd'hui ?",
        "iss_pos": "Position ISS",
        "passes": "Passages",
        "countdown": "Compte à rebours",
        "status": "Statut alarme",
        "today": "Aujourd'hui",
        "tomorrow": "Demain",
        "weather": "Météo spatiale",
        "moon": "Phase Lune",
        "radio": "Radio ISS",
        "contact": "Contact ISS",
        "satellites": "Multi-satellites",
        "track": "Trajectoire",
        "charts": "Graphiques",
        "report": "Rapport",
        "live": "Lives NASA",
        "earth": "Vue Terre",
        "quiz": "Quiz",
        "stats": "Mes stats",
        "achievements": "Achievements",
        "eclipses": "Éclipses",
        "meteors": "Météores",
        "planets": "Planètes",
        "kids": "Mode enfants",
        "ai": "IA conversationnelle",
        "prefs": "Préférences",
        "terminal": "Menu terminal",
        "todo": "Todo",
        "web": "Interface Web",
        "loading": "Chargement...",
        "no_pass": "Aucun passage",
        "min": "min",
        "max": "max",
    },
    "en": {
        "menu_title": "🛰️ MAP-CI Tchabio",
        "menu_intro": "👋 What would you like to do?",
        "iss_pos": "ISS Position",
        "passes": "Passes",
        "countdown": "Countdown",
        "status": "Alarm Status",
        "today": "Today",
        "tomorrow": "Tomorrow",
        "weather": "Space Weather",
        "moon": "Moon Phase",
        "radio": "ISS Radio",
        "contact": "Contact ISS",
        "satellites": "Multi-Satellites",
        "track": "Ground Track",
        "charts": "Charts",
        "report": "Report",
        "live": "NASA Live",
        "earth": "Earth View",
        "quiz": "Quiz",
        "stats": "My Stats",
        "achievements": "Achievements",
        "eclipses": "Eclipses",
        "meteors": "Meteors",
        "planets": "Planets",
        "kids": "Kids Mode",
        "ai": "AI Chat",
        "prefs": "Settings",
        "terminal": "Terminal Menu",
        "todo": "Todo",
        "web": "Web Interface",
        "loading": "Loading...",
        "no_pass": "No passes",
        "min": "min",
        "max": "max",
    },
    "es": {
        "menu_title": "🛰️ MAP-CI Tchabio",
        "menu_intro": "👋 ¿Qué quieres hacer?",
        "iss_pos": "Posición ISS",
        "passes": "Pasos",
        "countdown": "Cuenta atrás",
        "status": "Estado alarma",
        "today": "Hoy",
        "tomorrow": "Mañana",
        "weather": "Clima espacial",
        "moon": "Fase Lunar",
        "radio": "Radio ISS",
        "contact": "Contacto ISS",
        "satellites": "Multi-satélites",
        "track": "Trayectoria",
        "charts": "Gráficos",
        "report": "Informe",
        "live": "NASA en vivo",
        "earth": "Vista Tierra",
        "quiz": "Quiz",
        "stats": "Mis stats",
        "achievements": "Logros",
        "eclipses": "Eclipses",
        "meteors": "Meteoros",
        "planets": "Planetas",
        "kids": "Modo niños",
        "ai": "IA chat",
        "prefs": "Ajustes",
        "terminal": "Menu terminal",
        "todo": "Tareas",
        "web": "Interfaz web",
        "loading": "Cargando...",
        "no_pass": "Sin pasos",
        "min": "min",
        "max": "max",
    },
    "ar": {
        "menu_title": "🛰️ MAP-CI Tchabio",
        "menu_intro": "👋 ماذا تريد أن تفعل؟",
        "iss_pos": "موقع المحطة",
        "passes": "المرور",
        "countdown": "العد التنازلي",
        "status": "حالة التنبيه",
        "today": "اليوم",
        "tomorrow": "غدا",
        "weather": "الطقس الفضائي",
        "moon": "طور القمر",
        "radio": "راديو المحطة",
        "contact": "اتصال بالمحطة",
        "satellites": "أقمار متعددة",
        "track": "المسار",
        "charts": "رسوم بيانية",
        "report": "تقرير",
        "live": "ناسا مباشر",
        "earth": "رؤية الأرض",
        "quiz": "اختبار",
        "stats": "إحصائياتي",
        "achievements": "الإنجازات",
        "eclipses": "الكسوف",
        "meteors": "الشهب",
        "planets": "الكواكب",
        "kids": "وضع الأطفال",
        "ai": "ذكاء اصطناعي",
        "prefs": "الإعدادات",
        "terminal": "قائمة الطرفية",
        "todo": "المهام",
        "web": "واجهة الويب",
        "loading": "جار التحميل...",
        "no_pass": "لا مرور",
        "min": "دقيقة",
        "max": "أقصى",
    },
}


def get_lang():
    if LANG_FILE.exists():
        try:
            return json.loads(LANG_FILE.read_text()).get("lang", "fr")
        except Exception:
            pass
    return "fr"


def set_lang(lang):
    if lang not in STRINGS:
        return False
    LANG_FILE.write_text(json.dumps({"lang": lang}))
    return True


def t(key, lang=None):
    """Traduit une cle dans la langue courante."""
    lang = lang or get_lang()
    return STRINGS.get(lang, STRINGS["fr"]).get(key, key)


def afficher_menu_i18n():
    """Retourne les libelles des boutons traduits."""
    return {
        "iss": t("iss_pos"),
        "passes": t("passes"),
        "countdown": t("countdown"),
        "status": t("status"),
        "aujourdhui": t("today"),
        "demain": t("tomorrow"),
        "solar": t("weather"),
        "lune": t("moon"),
        "radio": t("radio"),
        "contact": t("contact"),
        "multisat": t("satellites"),
        "track": t("track"),
        "charts": t("charts"),
        "report": t("report"),
        "live": t("live"),
        "earth": t("earth"),
        "quiz": t("quiz"),
        "stats": t("stats"),
        "achievements": t("achievements"),
        "eclipses": t("eclipses"),
        "meteors": t("meteors"),
        "planetes": t("planets"),
        "kids": t("kids"),
        "ai_help": t("ai"),
        "prefs": t("prefs"),
        "term_page_0": t("terminal"),
    }


if __name__ == "__main__":
    print("Test iss_i18n.py\n")
    for lang in ["fr", "en", "es", "ar"]:
        set_lang(lang)
        print(f"[{lang}] {t('menu_title')} - {t('menu_intro')}")
        print(f"     ISS: {t('iss_pos')} | Passes: {t('passes')}")
    set_lang("fr")
    print("\nLangue remise en francais.")
