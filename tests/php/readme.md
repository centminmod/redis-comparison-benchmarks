# WordPress Redis Protocol PHP Benchmark Suite

A comprehensive PHP-based testing suite for evaluating Redis protocol databases (Redis, KeyDB, Dragonfly, Valkey) with realistic WordPress workload patterns. This suite complements memtier_benchmark with application-specific tests that simulate actual WordPress Redis object caching scenarios.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Test Suite Description](#test-suite-description)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [Configuration](#configuration)
- [Output Formats](#output-formats)
- [Visualization and Charts](#visualization-and-charts)
- [Integration with Existing Benchmarks](#integration-with-existing-benchmarks)
- [Troubleshooting](#troubleshooting)
- [Performance Tuning](#performance-tuning)
- [Examples](#examples)

## Overview

This PHP benchmark suite provides five specialized tests that simulate typical WordPress Redis object caching patterns:

1. **Object Cache Test** - General WordPress object caching with typical read/write ratios
2. **Transient API Test** - WordPress transient operations with expiration handling  
3. **Session Storage Test** - User session management with frequent updates
4. **Cache Invalidation Test** - Complex invalidation patterns and cache tagging
5. **High-Frequency Operations Test** - Rapid small operations (counters, flags, queues, locks)

### Key Features

- **Realistic Workloads**: Based on actual WordPress Redis usage patterns
- **Dual Mode Testing**: Automatic testing of both non-TLS and TLS connections
- **Multiple Output Formats**: CSV, JSON, and Markdown results
- **Comprehensive Metrics**: Ops/sec, latency percentiles, cache hit rates, error rates
- **Advanced Visualization**: Python-based charting and reporting
- **Docker Integration**: Works with your existing Docker-based Redis setup

## Prerequisites

### System Requirements

- **PHP 8.0+** with CLI support
- **Redis PHP Extension** (`php-redis`)
- **Python 3.8+** with pip
- **Docker** (for database containers)
- **Git** (for cloning)

### PHP Extensions Required

```bash
# Ubuntu/Debian
sudo apt-get install php-cli php-redis php-json

# CentOS/RHEL
sudo yum install php-cli php-redis php-json

# macOS with Homebrew
brew install php redis
pecl install redis
```

### Python Dependencies

```bash
pip install pandas matplotlib seaborn numpy pathlib
```

## Installation

### 1. Clone the Repository

```bash
# Clone the redis-comparison-benchmarks repository
git clone https://github.com/centminmod/redis-comparison-benchmarks.git
cd redis-comparison-benchmarks

# Navigate to the PHP tests directory
cd tests/php
```

### 2. Verify Repository Structure

The PHP test files should be located at:

```
redis-comparison-benchmarks/
├── tests/
│   └── php/
│       ├── RedisTestBase.php
│       ├── wp_object_cache_test.php
│       ├── wp_transient_test.php
│       ├── wp_session_test.php
│       ├── wp_invalidation_test.php
│       ├── wp_high_frequency_test.php
│       ├── php_redis_charts.py
│       ├── run_all_php_tests.sh
│       └── README.md
└── ... (other benchmark files)
```

### 3. Set Permissions

```bash
# From the tests/php directory
chmod +x run_all_php_tests.sh
chmod +x *.php
```

### 4. Verify PHP Redis Extension

```bash
php -m | grep redis
# Should output: redis
```

### 5. Test Basic Connectivity

```bash
# Test if Redis is accessible (ensure your Redis containers are running first)
php -r "
try {
    \$redis = new Redis();
    \$redis->connect('127.0.0.1', 6379);
    echo 'Redis connection: OK\n';
} catch (Exception \$e) {
    echo 'Redis connection failed: ' . \$e->getMessage() . '\n';
}
"
```

### 6. Set up TLS Certificates (if testing TLS)

Ensure TLS certificates are available in the repository root or copy them to the php tests directory:

```bash
# If certificates are in repository root
cp ../../*.crt ../../*.key . 2>/dev/null || echo "TLS certificates not found - TLS tests will be skipped"

# Or create symlinks
ln -sf ../../test.crt ../../test.key ../../ca.crt . 2>/dev/null || true
```

## Test Suite Description

### 1. WordPress Object Cache Test (`wp_object_cache_test.php`)

**Purpose**: Simulates general WordPress object caching patterns

**Operations**:
- 70% read operations (GET commands)
- 30% write operations (SETEX commands with TTL)
- Typical WordPress cache groups: posts, terms, users, options, comments
- Object types: post_meta, user_meta, term_meta, transients
- TTL range: 1-24 hours

**Key Metrics**:
- Operations per second
- Average/P95/P99 latency
- Error rate

### 2. WordPress Transient API Test (`wp_transient_test.php`)

**Purpose**: Tests WordPress transient operations with expiration handling

**Operations**:
- 60% transient reads
- 25% transient writes  
- 10% transient deletions
- 5% cleanup operations
- Simulates feed cache, remote API calls, query cache, theme cache

**Key Metrics**:
- Cache hit/miss rates
- Operations per second
- Latency measurements
- Cleanup efficiency

### 3. WordPress Session Storage Test (`wp_session_test.php`)

**Purpose**: Simulates user session management with frequent updates

**Operations**:
- 40% session reads
- 30% session updates
- 20% session creation
- 10% session destruction
- Session data includes user_id, cart_items, preferences, metadata

**Key Metrics**:
- Session operation breakdown
- Active session count
- Update frequency
- Session lifecycle performance

### 4. WordPress Cache Invalidation Test (`wp_invalidation_test.php`)

**Purpose**: Tests complex cache invalidation patterns

**Operations**:
- 50% cache reads
- 20% cache writes
- 15% single key invalidation
- 10% group invalidation
- 5% tag-based invalidation

**Key Metrics**:
- Invalidation efficiency
- Cache consistency
- Bulk operation performance
- Tag system overhead

### 5. WordPress High-Frequency Operations Test (`wp_high_frequency_test.php`)

**Purpose**: Tests rapid small operations typical in high-traffic WordPress sites

**Operations**:
- 30% counter updates (INCR operations)
- 20% flag operations (boolean cache values)
- 20% queue operations (LPUSH/RPOP)
- 20% lock acquisition/release
- 10% statistics updates (HASH operations)

**Key Metrics**:
- High-frequency operation throughput
- Lock contention
- Queue processing efficiency
- Statistical aggregation performance

## Quick Start

### 1. Start Your Redis Containers

Ensure your Redis containers are running using the repository's Docker setup:

```bash
# From repository root directory
cd ../../
docker-compose up -d redis keydb dragonfly valkey redis-tls keydb-tls dragonfly-tls valkey-tls

# Return to PHP tests directory
cd tests/php
```

### 2. Run All Tests

```bash
# Run complete test suite
./run_all_php_tests.sh
```

### 3. View Results

```bash
# Check results directory
ls -la php_benchmark_results/

# View charts
ls -la php_benchmark_charts/

# Read summary report
cat php_benchmark_charts/php_redis_benchmark_summary.md
```

## Detailed Usage

### Running Individual Tests

```bash
# Run specific test
php wp_object_cache_test.php

# Run with custom configuration
php -d memory_limit=512M wp_transient_test.php
```

### Custom Test Configuration

Create a configuration file `test_config.php`:

```php
<?php
return [
    'duration' => 60,              // Test duration in seconds
    'output_dir' => 'custom_results',  // Custom output directory
    'test_tls' => true,            // Enable TLS testing
    'databases' => [               // Custom database configuration
        'Redis' => ['host' => '127.0.0.1', 'port' => 6379, 'tls_port' => 6390],
        'KeyDB' => ['host' => '127.0.0.1', 'port' => 6380, 'tls_port' => 6391],
        // Add only databases you want to test
    ]
];
```

Then modify test files to load this configuration:

```php
// At the top of any test file
$config = include 'test_config.php';
$test = new WordPressObjectCacheTest($config);
```

### Running with Different Parameters

```bash
# Longer test duration (modify in test file)
sed -i 's/test_duration = 30/test_duration = 120/' wp_object_cache_test.php

# Custom output directory
mkdir my_custom_results
# Edit test files to change output_dir in constructor
```

## Configuration

### Database Connection Settings

Modify `RedisTestBase.php` to adjust connection settings:

```php
protected $databases = [
    'Redis' => [
        'host' => '127.0.0.1', 
        'port' => 6379, 
        'tls_port' => 6390,
        'timeout' => 2.0,      // Connection timeout
        'auth' => null         // Password if required
    ],
    // ... other databases
];
```

### TLS Configuration

TLS certificates should be available in the current directory or repository root:
- `test.crt` - Client certificate
- `test.key` - Client private key  
- `ca.crt` - CA certificate

These should match your existing memtier_benchmark TLS setup from the repository.

### Test Parameters

Each test class has configurable parameters:

```php
class WordPressObjectCacheTest extends RedisTestBase {
    private $test_duration = 30;     // Test duration in seconds
    private $key_prefix = 'wp_obj_'; // Key prefix for this test
    
    // Modify constructor to accept custom parameters
    public function __construct($config) {
        parent::__construct($config);
        $this->test_duration = $config['duration'] ?? 30;
    }
}
```

## Output Formats

### 1. CSV Format

```csv
database,tls,port,operations,errors,duration,ops_per_sec,avg_latency,p95_latency,p99_latency,error_rate
Redis,false,6379,15420,0,30.05,513.14,1.95,3.20,5.80,0.00
Redis,true,6390,14250,2,30.12,473.21,2.11,4.10,7.20,0.01
```

### 2. JSON Format

```json
{
  "test_name": "WordPress Object Cache Test",
  "timestamp": "2024-01-15T10:30:00+00:00",
  "results": [
    {
      "database": "Redis",
      "tls": false,
      "port": 6379,
      "operations": 15420,
      "errors": 0,
      "duration": 30.05,
      "ops_per_sec": 513.14,
      "avg_latency": 1.95,
      "p95_latency": 3.20,
      "p99_latency": 5.80,
      "error_rate": 0.00
    }
  ]
}
```

### 3. Markdown Format

```markdown
# WordPress Object Cache Test

**Test Date:** 2024-01-15 10:30:00

| database | tls | port | operations | errors | duration | ops_per_sec | avg_latency | p95_latency | p99_latency | error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Redis | false | 6379 | 15420 | 0 | 30.05 | 513.14 | 1.95 | 3.20 | 5.80 | 0.00 |
| Redis | true | 6390 | 14250 | 2 | 30.12 | 473.21 | 2.11 | 4.10 | 7.20 | 0.01 |
```

## Visualization and Charts

### Generated Charts

The `php_redis_charts.py` script generates:

1. **Performance Comparison Chart** (`php_redis_performance_comparison.png`)
   - Ops/sec comparison across all tests and databases
   - Separate bars for TLS vs non-TLS

2. **Latency Comparison Chart** (`php_redis_latency_comparison.png`)
   - Average and P99 latency comparison
   - Database and TLS mode breakdown

3. **Test-Specific Detailed Charts** (e.g., `wp_object_cache_test_detailed.png`)
   - Individual charts for each test type
   - 2x2 subplot layout with ops/sec, latency, error rate, and custom metrics

4. **Summary Report** (`php_redis_benchmark_summary.md`)
   - Markdown report with performance tables
   - Top performers by throughput and latency

### Running Chart Generation

```bash
# Generate charts from results
python3 php_redis_charts.py --results-dir php_benchmark_results --output-dir php_benchmark_charts

# Custom directories
python3 php_redis_charts.py --results-dir my_results --output-dir my_charts
```

### Chart Customization

Modify `php_redis_charts.py` to customize:

```python
# Change chart colors
colors = plt.cm.Set2(np.linspace(0, 1, len(databases)))  # Use Set2 colormap

# Adjust figure sizes
fig, axes = plt.subplots(2, 3, figsize=(24, 14))  # Larger charts

# Add custom styling
plt.style.use('seaborn-v0_8')  # Use seaborn style
```

## Integration with Existing Benchmarks

### Running with GitHub Actions

Add to your existing workflow in the repository:

```yaml
- name: Run PHP WordPress Redis Tests
  run: |
    cd tests/php
    ./run_all_php_tests.sh
    
- name: Generate PHP Test Charts
  run: |
    cd tests/php
    python3 php_redis_charts.py

- name: Upload PHP Test Results
  uses: actions/upload-artifact@v4
  with:
    name: php_wordpress_test_results
    path: |
      tests/php/php_benchmark_results/**
      tests/php/php_benchmark_charts/**
```

### Combining with Memtier Results

Create a combined analysis script in the repository:

```python
#!/usr/bin/env python3
"""
Combined Memtier + PHP WordPress Test Analysis
Located at: tests/php/combined_analysis.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Add paths to load existing benchmark results
sys.path.append('../../scripts')  # For existing benchmark scripts
sys.path.append('../../')         # For repository root

def load_memtier_results():
    # Load your existing memtier markdown results from repository
    memtier_files = ['../../combined_all_results.md', '../../combined_all_results_tls.md']
    # Implementation here
    pass

def load_php_results():
    # Load PHP test JSON results
    import glob
    results = {}
    for json_file in glob.glob('php_benchmark_results/*.json'):
        # Implementation here
        pass
    return results

def create_combined_report():
    # Generate combined performance analysis
    pass

if __name__ == "__main__":
    create_combined_report()
```

### Data Correlation

Compare PHP test results with memtier_benchmark results from the repository:

```bash
# Example correlation analysis script
cat > correlation_analysis.sh << 'EOF'
#!/bin/bash
# Compare PHP WordPress tests with existing memtier results

echo "Database,Memtier_Ops_Sec,PHP_Ops_Sec,Correlation" > correlation.csv

# Extract memtier results from repository markdown files
if [ -f "../../combined_all_results.md" ]; then
    echo "Found memtier results, analyzing..."
    # Add correlation logic here
fi

# Extract PHP results
if [ -d "php_benchmark_results" ]; then
    echo "Found PHP results, analyzing..."
    # Add PHP results processing here
fi
EOF

chmod +x correlation_analysis.sh
```

## Troubleshooting

### Common Issues

#### 1. Redis Connection Failed

```bash
# Check if Redis is running (from repository root)
cd ../../
docker ps | grep redis

# Test connectivity
telnet 127.0.0.1 6379

# Check Redis logs
docker logs redis

# Return to PHP tests directory
cd tests/php
```

#### 2. PHP Redis Extension Missing

```bash
# Install on Ubuntu/Debian
sudo apt-get install php-redis

# Install on CentOS/RHEL  
sudo yum install php-redis

# Verify installation
php -m | grep redis
```

#### 3. TLS Connection Issues

```bash
# Verify certificates exist (check repository root and current directory)
ls -la ../../*.crt ../../*.key  # Repository root
ls -la *.crt *.key              # Current directory

# Copy certificates if needed
cp ../../test.crt ../../test.key ../../ca.crt .

# Test TLS connection manually
openssl s_client -connect 127.0.0.1:6390 -cert test.crt -key test.key -CAfile ca.crt
```

#### 4. Repository Structure Issues

```bash
# Verify you're in the correct directory
pwd
# Should show: /path/to/redis-comparison-benchmarks/tests/php

# Check file availability
ls -la *.php *.py *.sh

# If files are missing, re-clone the repository
cd ../../../
git clone https://github.com/centminmod/redis-comparison-benchmarks.git
cd redis-comparison-benchmarks/tests/php
```

#### 5. Memory Issues

```bash
# Increase PHP memory limit
php -d memory_limit=1G wp_object_cache_test.php

# Check current memory usage
php -r "echo 'Memory limit: ' . ini_get('memory_limit') . \"\n\";"
```

#### 6. Permission Issues

```bash
# Fix script permissions
chmod +x *.php *.sh

# Create results directory with proper permissions
mkdir -p php_benchmark_results
chmod 755 php_benchmark_results
```

### Debug Mode

Enable debug output in tests:

```php
// Add at the top of any test file
define('DEBUG_MODE', true);

// Add debug output in RedisTestBase
if (defined('DEBUG_MODE') && DEBUG_MODE) {
    echo "Connecting to {$host}:{$port} (TLS: " . ($tls ? 'yes' : 'no') . ")\n";
}
```

### Performance Issues

If tests are running slowly:

1. **Reduce test duration**:
   ```php
   private $test_duration = 10; // Reduce to 10 seconds
   ```

2. **Skip TLS tests**:
   ```php
   $config = ['test_tls' => false];
   ```

3. **Test fewer databases**:
   ```php
   $this->databases = [
       'Redis' => ['host' => '127.0.0.1', 'port' => 6379, 'tls_port' => 6390]
       // Remove other databases
   ];
   ```

## Performance Tuning

### Optimize for High Performance

1. **Increase PHP memory limit**:
   ```bash
   php -d memory_limit=2G wp_object_cache_test.php
   ```

2. **Adjust Redis connection timeouts**:
   ```php
   $redis->connect($host, $port, 0.1); // 100ms timeout
   ```

3. **Use Redis pipelining** (advanced):
   ```php
   $redis->multi(Redis::PIPELINE);
   // Queue multiple operations
   $redis->exec();
   ```

4. **Optimize test patterns**:
   ```php
   // Reduce random ranges for better cache locality
   $id = mt_rand(1, 1000); // Instead of mt_rand(1, 10000)
   ```

### Resource Monitoring

Monitor system resources during tests:

```bash
# Monitor in separate terminal
watch -n 1 'docker stats --no-stream'

# Monitor PHP memory usage
php -d memory_limit=1G -r "
echo 'Peak memory: ' . memory_get_peak_usage(true) / 1024 / 1024 . ' MB\n';
"
```

## Examples

### Example 1: Quick Performance Check

```bash
# Quick 10-second test of all databases
sed -i 's/test_duration = 30/test_duration = 10/' *.php
./run_all_php_tests.sh
```

### Example 2: Repository Integration Test

```bash
# Test with repository's existing Docker setup
cd ../../
docker-compose up -d

cd tests/php
./run_all_php_tests.sh

# Compare with existing memtier results
python3 combined_analysis.py
```

### Example 3: Single Database Focus

```bash
# Test only Redis
php -r "
\$config = [
    'duration' => 60,
    'databases' => [
        'Redis' => ['host' => '127.0.0.1', 'port' => 6379, 'tls_port' => 6390]
    ]
];
include 'wp_object_cache_test.php';
\$test = new WordPressObjectCacheTest(\$config);
\$test->run();
"
```

### Example 4: Custom Workload

Create a custom test based on your specific WordPress usage:

```php
<?php
// custom_wp_test.php
require_once 'RedisTestBase.php';

class CustomWordPressTest extends RedisTestBase {
    public function __construct($config) {
        parent::__construct($config);
        $this->test_name = "Custom WordPress Test";
    }
    
    protected function runTest($redis, $db_name) {
        // Your custom test logic here
        // Based on your actual WordPress Redis usage patterns
        return [
            'operations' => 1000,
            'errors' => 0,
            'duration' => 30.0,
            'ops_per_sec' => 33.33,
            'avg_latency' => 1.5,
            'error_rate' => 0.0
        ];
    }
}

if (php_sapi_name() === 'cli') {
    $config = ['duration' => 30, 'output_dir' => 'php_benchmark_results'];
    $test = new CustomWordPressTest($config);
    $test->run();
}
?>
```

### Example 5: Automated Comparison with Repository Results

```bash
#!/bin/bash
# compare_with_baseline.sh
# Compare current PHP results with repository baseline

echo "Running PHP WordPress tests..."
./run_all_php_tests.sh

echo "Comparing with repository memtier results..."
if [ -f "../../combined_all_results.md" ]; then
    echo "Found memtier baseline results"
    # Add comparison logic
    python3 php_redis_charts.py --results-dir php_benchmark_results --output-dir php_benchmark_charts
    echo "Charts generated with comparison data"
else
    echo "No memtier baseline found, generating PHP-only charts"
    python3 php_redis_charts.py --results-dir php_benchmark_results --output-dir php_benchmark_charts
fi

echo "Results available in:"
echo "  - php_benchmark_results/ (raw data)"
echo "  - php_benchmark_charts/ (visualizations)"
```

## Advanced Usage

### Extending Tests

Add custom metrics to any test:

```php
protected function runTest($redis, $db_name) {
    // ... existing test code ...
    
    return array_merge($base_results, [
        'custom_metric' => $my_custom_value,
        'cache_efficiency' => $cache_hits / $total_operations,
        'write_ratio' => $writes / $total_operations
    ]);
}
```

### Integration with Repository CI/CD

Create a workflow that integrates with the repository's existing benchmarks:

```yaml
# .github/workflows/php-wordpress-tests.yml
name: PHP WordPress Redis Tests

on:
  workflow_dispatch:
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Mondays

jobs:
  php-tests:
    runs-on: ubuntu-24.04
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up PHP
      uses: shivammathur/setup-php@v2
      with:
        php-version: '8.2'
        extensions: redis
        
    - name: Start Redis containers
      run: docker-compose up -d
      
    - name: Run PHP WordPress tests
      run: |
        cd tests/php
        ./run_all_php_tests.sh
        
    - name: Generate charts
      run: |
        cd tests/php
        pip install pandas matplotlib seaborn numpy
        python3 php_redis_charts.py
        
    - name: Upload results
      uses: actions/upload-artifact@v4
      with:
        name: php-wordpress-test-results
        path: |
          tests/php/php_benchmark_results/
          tests/php/php_benchmark_charts/
```

### Integration with Monitoring

Send results to monitoring systems:

```php
// Add to RedisTestBase
protected function sendToMonitoring($results) {
    $payload = json_encode([
        'timestamp' => time(),
        'test' => $this->test_name,
        'repository' => 'centminmod/redis-comparison-benchmarks',
        'branch' => trim(`git rev-parse --abbrev-ref HEAD`),
        'commit' => trim(`git rev-parse HEAD`),
        'results' => $results
    ]);
    
    // Send to your monitoring system
    // curl, webhooks, InfluxDB, etc.
}
```