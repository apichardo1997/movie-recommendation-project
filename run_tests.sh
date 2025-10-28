#!/bin/bash
# Newman CLI Test Runner
# Run Postman tests from command line (CI/CD ready)

echo "🚀 Running Movie Recommendation API Tests..."
echo ""

# Check if Newman is installed
if ! command -v newman &> /dev/null; then
    echo "❌ Newman is not installed!"
    echo "Install with: npm install -g newman"
    echo "Or: brew install newman (on Mac)"
    exit 1
fi

# Run the collection
newman run "Dont Share/Movie_Recommendation_API_Enhanced.postman_collection.json" \
    --environment "Dont Share/Movie_Recommendation_API.postman_environment.json" \
    --reporters cli,json,html \
    --reporter-html-export "test-results.html" \
    --reporter-json-export "test-results.json" \
    --color on \
    --delay-request 100 \
    --timeout-request 10000

echo ""
echo "✅ Tests complete! Check test-results.html for detailed report"
