#!/data/data/com.termux/files/usr/bin/bash
echo "🛰️ Installation MAP-CI"
echo "========================"

pkg update && pkg upgrade -y
pkg install python python-numpy termux-api git -y
pip install -r requirements.txt

echo ""
echo "✅ Installation terminée !"
echo ""
echo "Pour lancer :"
echo "  python mapci.py"
echo "  python web_app.py"
echo "  python iss_bot.py"
