#!/bin/bash
# Run all PHP WordPress Redis tests

set -e

echo "Starting WordPress Redis Protocol Tests..."
echo "========================================"

# Create results directory
mkdir -p php_benchmark_results
mkdir -p php_benchmark_charts

# Run all PHP tests
echo "Running WordPress Object Cache Test..."
php wp_object_cache_test.php

echo "Running WordPress Transient API Test..."
php wp_transient_test.php

echo "Running WordPress Session Storage Test..."
php wp_session_test.php

echo "Running WordPress Cache Invalidation Test..."
php wp_invalidation_test.php

echo "Running WordPress High-Frequency Operations Test..."
php wp_high_frequency_test.php

echo "Generating charts and reports..."
python3 php_redis_charts.py --results-dir php_benchmark_results --output-dir php_benchmark_charts

echo "========================================"
echo "All tests completed!"
echo "Results: php_benchmark_results/"
echo "Charts: php_benchmark_charts/"
echo "Summary: php_benchmark_charts/php_redis_benchmark_summary.md"