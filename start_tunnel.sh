#!/data/data/com.termux/files/usr/bin/bash
pkill -f cloudflared 2>/dev/null
sleep 1

if ! pgrep -f "python web_app.py" > /dev/null; then
    echo "Demarrage de web_app.py..."
    cd ~/map-ci
    nohup python web_app.py > ~/.mapci_web.log 2>&1 &
    sleep 3
fi

echo "Creation du tunnel Cloudflare..."
echo "Copie l'URL https://xxx.trycloudflare.com"
echo ""
cloudflared tunnel --url http://127.0.0.1:8080
