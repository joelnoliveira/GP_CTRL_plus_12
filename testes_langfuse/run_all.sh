#!/bin/bash
# Run all Langfuse tests

echo "🚀 Running all Langfuse tests..."
echo ""

for script in 0{1..6}_*.py; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Running: $script"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python "$script"
    echo ""
    sleep 2
done

echo "✅ All tests completed!"
echo "📊 Check Langfuse UI at http://localhost:3000"
