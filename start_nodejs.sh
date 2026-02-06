#!/bin/bash
# Script para iniciar backend e frontend simultaneamente

echo "🚀 Iniciando aplicação Node.js/React..."

# Verificar se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não está instalado. Por favor, instale Node.js primeiro."
    exit 1
fi

# Iniciar backend em background
echo "📦 Iniciando backend..."
cd backend
npm install 2>/dev/null || true
npm start &
BACKEND_PID=$!
cd ..

# Aguardar backend iniciar
sleep 3

# Iniciar frontend
echo "⚛️  Iniciando frontend..."
cd frontend
npm install 2>/dev/null || true
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Aplicação iniciada!"
echo "   Backend: http://localhost:3000"
echo "   Frontend: http://localhost:5173"
echo ""
echo "Pressione Ctrl+C para encerrar ambos os serviços"

# Aguardar Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
