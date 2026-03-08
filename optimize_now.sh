#!/bin/bash
# Auto-optimasi untuk Ollama

echo "🚀 OPTIMIZING OLLAMA FOR FAST RESPONSE"
echo "======================================"

# 1. Stop Ollama
echo -e "\n1. Stopping Ollama..."
pkill ollama
sleep 3

# 2. Set optimal environment
echo -e "\n2. Setting optimal environment..."
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_KEEP_ALIVE=10m
export OLLAMA_HOST=127.0.0.1

# 3. Pull ultra-fast model
echo -e "\n3. Pulling ultra-fast model..."
ollama pull qwen2:0.5b

# 4. Start Ollama
echo -e "\n4. Starting Ollama..."
ollama serve > /tmp/ollama.log 2>&1 &
sleep 5

# 5. Preload model
echo -e "\n5. Preloading model for fast response..."
curl -X POST http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen2:0.5b", "prompt": "test", "stream": false}' \
  > /dev/null 2>&1

# 6. Update .env
echo -e "\n6. Updating .env..."
cat > .env << EOF
OLLAMA_MODEL=qwen2:0.5b
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_TIMEOUT=60
DATABASE_URL=postgresql://kudos_user:kudos_password@localhost:5432/kudos_db
EOF

# 7. Test response time
echo -e "\n7. Testing response time..."
start=$(date +%s%N)
response=$(curl -s -X POST http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen2:0.5b", "prompt": "Hello", "stream": false}')
end=$(date +%s%N)
elapsed=$(( ($end - $start) / 1000000 ))

if echo "$response" | grep -q "response"; then
    echo "✅ Response time: ${elapsed}ms"
else
    echo "❌ Test failed"
fi

echo -e "\n✅ OPTIMIZATION COMPLETE!"
echo "🚀 Run: streamlit run app/main.py"