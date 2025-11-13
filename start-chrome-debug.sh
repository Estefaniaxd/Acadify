#!/bin/bash
# Script para iniciar Chrome/Chromium/Brave con remote debugging habilitado

# Buscar ejecutable de Chrome/Chromium/Brave
if command -v google-chrome &> /dev/null; then
    CHROME_BIN="google-chrome"
elif command -v chromium &> /dev/null; then
    CHROME_BIN="chromium"
elif command -v chromium-browser &> /dev/null; then
    CHROME_BIN="chromium-browser"
elif command -v brave &> /dev/null; then
    CHROME_BIN="brave"
elif command -v brave-browser &> /dev/null; then
    CHROME_BIN="brave-browser"
else
    echo "❌ No se encontró Chrome/Chromium/Brave instalado"
    exit 1
fi

echo "🚀 Iniciando Chrome con remote debugging en puerto 9222..."
echo "📍 URL de debugging: http://localhost:9222"
echo ""
echo "⚠️  IMPORTANTE: Deja esta terminal abierta mientras usas el debugging"
echo ""

# Iniciar Chrome con debugging habilitado
$CHROME_BIN \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug-profile \
  --no-first-run \
  --no-default-browser-check \
  http://localhost:5173/avatar &

CHROME_PID=$!
echo "✅ Chrome iniciado (PID: $CHROME_PID)"
echo ""
echo "Para detener Chrome con debugging, presiona Ctrl+C o ejecuta:"
echo "  kill $CHROME_PID"
echo ""

# Esperar a que Chrome se cierre
wait $CHROME_PID
