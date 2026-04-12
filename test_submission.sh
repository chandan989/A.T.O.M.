#!/bin/zsh

# test_submission.sh
# ------------------
# Local trial script to verify A.T.O.M. compliance with the Meta PyTorch validator.
# This script simulates the Phase 2 validator environment.

# 1. Configuration
export API_BASE_URL="http://localhost:5050/v1"
export API_KEY="local-trial-api-key-123"
export MODEL_NAME="mock-chemistry-model"
export ATOM_SERVER_URL="http://localhost:8000"

echo "🚀 Starting Local Validator Trial..."
echo "--------------------------------------"
echo "Env Vars Set:"
echo "  API_BASE_URL: $API_BASE_URL"
echo "  API_KEY:      $API_KEY"
echo "  MODEL_NAME:   $MODEL_NAME"
echo "--------------------------------------"

# 2. Cleanup function
cleanup() {
    echo "\n🛑 Cleaning up background processes..."
    # Kill the background jobs started by this script
    kill $(jobs -p) 2>/dev/null
    echo "✅ Cleanup complete."
}
trap cleanup EXIT

# Ensure local python bin is on path for uvicorn etc.
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

# 3. Start ATOM Environment Server (the backend)
echo "📦 Starting ATOM Server on port 8000..."
# We run it via uvicorn to match the Docker deployment
PYTHONPATH=. python3 -m uvicorn server.app:app --host 0.0.0.0 --port 8000 --log-level warning > atom_server.log 2>&1 &
SERVER_PID=$!

# 4. Start Mock Proxy (the simulated validator proxy)
echo "🛰️  Starting Mock Proxy on port 5050..."
python3 mock_proxy.py > mock_proxy.log 2>&1 &
PROXY_PID=$!

sleep 4 # Wait for servers to boot

# Tail the mock proxy log in the background so you can see requests in real-time
tail -f mock_proxy.log &
TAIL_PID=$!

# 5. Run inference.py (the agent)
echo "🧠 Running inference.py... (Limited to Task 1 for trial)"
export ATOM_TASKS="1" # Speed up the test
python3 inference.py

# Give a moment to see the final logs
sleep 2

echo "\n--------------------------------------"
echo "Trial Complete."
echo "VERIFICATION CHECK:"
echo "If you saw '[MOCK PROXY] RECEIVED REQUEST' above, your code is CORRECTLY using the proxy."
echo "If you see 'No API calls made', something is wrong with the code logic."
