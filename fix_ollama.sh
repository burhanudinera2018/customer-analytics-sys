#!/bin/bash
# Script untuk fix Ollama port issue

echo "🔧 FIXING OLLAMA PORT ISSUE"
echo "==========================="

# Cek proses yang menggunakan port 11434
PID=$(lsof -ti :11434)

if [ -n "$PID" ]; then
    echo "📋 Port 11434 digunakan oleh PID: $PID"
    echo "🛑 Menghentikan proses..."
    
    # Kill proses
    kill -9 $PID
    sleep 3
    
    # Verifikasi
    if lsof -ti :11434 > /dev/null; then
        echo "❌ Gagal menghentikan proses"
        exit 1
    else
        echo "✅ Port 11434 freed"
    fi
else
    echo "✅ Port 11434 sudah free"
fi

# Kill semua proses Ollama yang mungkin tersisa
echo "📋 Membersihkan proses Ollama..."
pkill ollama 2>/dev/null
sleep 2

# Set environment variables
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_KEEP_ALIVE=0

# Start Ollama
echo "🚀 Starting Ollama..."
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!

echo "⏳ Menunggu Ollama siap..."
sleep 5

# Test connection
if curl -s http://127.0.0.1:11434/api/tags > /dev/null; then
    echo "✅ Ollama running (PID: $OLLAMA_PID)"
    
    # Test model
    echo "🔥 Testing tinylama..."
    curl -X POST http://127.0.0.1:11434/api/generate \
        -H "Content-Type: application/json" \
        -d '{"model": "tinylama", "prompt": "Hello", "stream": false}' \
        > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Model tinylama siap"
    else
        echo "⚠️ Model tinylama perlu diinstall: ollama pull tinylama"
    fi
else
    echo "❌ Ollama gagal start"
    echo "📝 Log: tail -f /tmp/ollama.log"
fi

echo ""
echo "🚀 Jalankan aplikasi: streamlit run app/main.py"