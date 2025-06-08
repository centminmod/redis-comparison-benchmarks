<?php
/**
 * Enhanced WordPress Object Cache Test with 5-Run Statistical Analysis
 * 
 * Features:
 * - Multiple iterations per database test
 * - Statistical reliability measurement
 * - Enhanced error handling and reporting
 * - Raw data logging for analysis
 */

require_once 'RedisTestBase.php';

class WordPressObjectCacheTest extends RedisTestBase {
    private $operations = 100000;  // Operations per iteration
    private $test_duration = 30;   // Duration per iteration in seconds
    private $read_write_ratio = 70; // 70% reads, 30% writes
    
    // WordPress-like cache groups
    private $cache_groups = [
        'posts', 'terms', 'users', 'options', 'comments', 
        'themes', 'plugins', 'transients', 'site-options'
    ];
    
    public function __construct($config = []) {
        $this->test_name = "WordPress Object Cache Test";
        
        // Override default iterations if specified
        if (isset($config['test_iterations'])) {
            $this->test_iterations = $config['test_iterations'];
        }
        
        // Test-specific configuration
        $this->operations = $config['operations'] ?? 100000;
        $this->test_duration = $config['duration'] ?? 30;
        $this->read_write_ratio = $config['read_write_ratio'] ?? 70;
        
        parent::__construct($config);
        
        $this->debugLog("WordPress Object Cache Test initialized");
        $this->debugLog("Operations per iteration: {$this->operations}");
        $this->debugLog("Duration per iteration: {$this->test_duration}s");
        $this->debugLog("Read/Write ratio: {$this->read_write_ratio}%/{100-$this->read_write_ratio}%");
    }
    
    /**
     * Override: Run a single test iteration with WordPress-like cache operations
     */
    protected function runSingleIteration($redis, $test_label, $iteration) {
        $start_time = microtime(true);
        $end_time = $start_time + $this->test_duration;
        
        $operations = 0;
        $errors = 0;
        $latencies = [];
        
        // Warm up the cache with some initial data
        $this->warmUpCache($redis);
        
        $this->debugLog("Starting iteration {$iteration} for {$test_label}");
        
        while (microtime(true) < $end_time && $operations < $this->operations) {
            $operation_start = microtime(true);
            
            try {
                if (rand(1, 100) <= $this->read_write_ratio) {
                    // READ operation (GET)
                    $key = $this->generateWordPressKey();
                    $result = $redis->get($key);
                    
                    // Simulate cache miss handling (WordPress behavior)
                    if ($result === false && rand(1, 100) <= 20) {
                        // 20% chance to populate missing key
                        $value = $this->generateWordPressValue();
                        $ttl = rand(3600, 86400); // 1-24 hours TTL
                        $redis->setex($key, $ttl, $value);
                    }
                } else {
                    // WRITE operation (SETEX with TTL)
                    $key = $this->generateWordPressKey();
                    $value = $this->generateWordPressValue();
                    $ttl = rand(300, 86400); // 5 minutes to 24 hours
                    $redis->setex($key, $ttl, $value);
                }
                
                $operations++;
                
            } catch (Exception $e) {
                $errors++;
                $this->debugLog("Error in iteration {$iteration}: " . $e->getMessage());
            }
            
            // Record latency for statistical analysis
            $operation_latency = (microtime(true) - $operation_start) * 1000; // Convert to ms
            $latencies[] = $operation_latency;
            
            // Occasional brief pause to simulate real-world usage
            if ($operations % 1000 == 0) {
                usleep(100); // 0.1ms pause every 1000 operations
            }
        }
        
        $actual_duration = microtime(true) - $start_time;
        $ops_per_sec = $operations / $actual_duration;
        
        // Calculate latency statistics
        $avg_latency = array_sum($latencies) / count($latencies);
        sort($latencies);
        $p95_latency = $this->calculatePercentile($latencies, 95);
        $p99_latency = $this->calculatePercentile($latencies, 99);
        
        $this->debugLog("Iteration {$iteration} completed: {$operations} ops in {$actual_duration}s");
        
        return [
            'iteration' => $iteration,
            'operations' => $operations,
            'errors' => $errors,
            'duration' => $actual_duration,
            'ops_per_sec' => $ops_per_sec,
            'avg_latency' => $avg_latency,
            'p95_latency' => $p95_latency,
            'p99_latency' => $p99_latency,
            'error_rate' => ($errors / max($operations, 1)) * 100,
            'latency_samples' => count($latencies),
            'read_write_ratio_actual' => $this->read_write_ratio, // Could calculate actual ratio
        ];
    }
    
    /**
     * Warm up cache with initial WordPress-like data
     */
    private function warmUpCache($redis) {
        $warmup_keys = 100;
        
        for ($i = 0; $i < $warmup_keys; $i++) {
            $key = $this->generateWordPressKey();
            $value = $this->generateWordPressValue();
            $ttl = rand(3600, 43200); // 1-12 hours for warmup data
            
            try {
                $redis->setex($key, $ttl, $value);
            } catch (Exception $e) {
                // Ignore warmup errors
            }
        }
    }
    
    /**
     * Generate WordPress-like cache keys
     */
    private function generateWordPressKey() {
        $group = $this->cache_groups[array_rand($this->cache_groups)];
        $id = rand(1, 10000);
        
        // Generate keys that mimic WordPress cache patterns
        $patterns = [
            "wp_cache_{$group}_{$id}",
            "{$group}_meta_{$id}",
            "wp_option_{$group}_{$id}",
            "query_{$group}_" . md5("query_{$id}"),
            "transient_{$group}_{$id}",
            "user_meta_{$id}_{$group}",
            "post_meta_{$id}_{$group}",
            "taxonomy_{$group}_{$id}",
        ];
        
        return $patterns[array_rand($patterns)];
    }
    
    /**
     * Generate WordPress-like cache values
     */
    private function generateWordPressValue() {
        $value_types = [
            // Simple values
            'simple_string' => 'WordPress cached value ' . rand(1000, 9999),
            'simple_number' => rand(1, 1000000),
            'simple_boolean' => rand(0, 1) ? 'true' : 'false',
            
            // Serialized PHP data (common in WordPress)
            'serialized_array' => serialize([
                'id' => rand(1, 1000),
                'title' => 'Sample Post Title ' . rand(1, 100),
                'content' => str_repeat('Lorem ipsum dolor sit amet. ', rand(5, 20)),
                'meta' => [
                    'author' => 'user_' . rand(1, 100),
                    'date' => date('Y-m-d H:i:s'),
                    'category' => 'category_' . rand(1, 20)
                ]
            ]),
            
            // JSON data
            'json_data' => json_encode([
                'type' => 'wordpress_cache',
                'data' => str_repeat('x', rand(100, 1000)),
                'timestamp' => time(),
                'random' => rand(1, 100000)
            ]),
            
            // Larger content (simulating page cache)
            'large_content' => str_repeat('WordPress page content. ', rand(50, 200))
        ];
        
        $type = array_rand($value_types);
        return $value_types[$type];
    }
    
    /**
     * Override: Enhanced results summary for WordPress context
     */
    protected function printResultsSummary($results) {
        parent::printResultsSummary($results);
        
        // WordPress-specific analysis
        echo "\n" . str_repeat("=", 80) . "\n";
        echo "WORDPRESS PERFORMANCE ANALYSIS\n";
        echo str_repeat("=", 80) . "\n";
        
        foreach ($results as $result) {
            $db_name = $result['database'] . ($result['tls'] ? ' (TLS)' : '');
            $ops_per_sec = $result['ops_per_sec'];
            
            // Estimate WordPress page loads per second
            // Assuming 10-50 cache operations per page load
            $light_pages_per_sec = $ops_per_sec / 10;  // Light pages (10 cache ops)
            $heavy_pages_per_sec = $ops_per_sec / 50;  // Heavy pages (50 cache ops)
            
            echo sprintf("%-20s | Light pages: %6.0f/sec | Heavy pages: %6.0f/sec\n",
                $db_name, $light_pages_per_sec, $heavy_pages_per_sec);
        }
        
        echo "\nWordPress Cache Recommendations:\n";
        
        // Find best performer
        $best_result = null;
        $best_ops = 0;
        foreach ($results as $result) {
            if (($result['measurement_quality'] ?? 'poor') !== 'poor' && $result['ops_per_sec'] > $best_ops) {
                $best_ops = $result['ops_per_sec'];
                $best_result = $result;
            }
        }
        
        if ($best_result) {
            $best_name = $best_result['database'] . ($best_result['tls'] ? ' with TLS' : '');
            echo "- 🏆 Best performer: {$best_name}\n";
            echo "- 📊 Estimated capacity: " . number_format($best_ops / 30, 0) . " concurrent users (30 cache ops/user/sec)\n";
        }
        
        // Reliability analysis
        $reliable_count = count(array_filter($results, function($r) { 
            return ($r['measurement_quality'] ?? 'poor') !== 'poor'; 
        }));
        
        if ($reliable_count < count($results)) {
            echo "- ⚠️  Consider running tests during low system load for better measurement reliability\n";
        }
        
        echo "- 💡 For production WordPress, consider read/write ratios: 90/10 for cached sites, 70/30 for dynamic sites\n";
        echo str_repeat("=", 80) . "\n";
    }
}

// Enhanced configuration support
if (php_sapi_name() === 'cli') {
    // Load configuration if available
    $config_file = __DIR__ . '/test_config.php';
    if (file_exists($config_file)) {
        $config = include $config_file;
        echo "Loaded configuration from test_config.php\n";
    } else {
        // Default configuration
        $config = [
            'duration' => 30,
            'test_iterations' => 13,
            'output_dir' => './php_benchmark_results',
            'test_tls' => true,
            'flush_before_test' => true,
            'debug' => false,
            'operations' => 100000,
            'read_write_ratio' => 70
        ];
        echo "Using default configuration\n";
    }
    
    echo "Configuration: " . json_encode($config, JSON_PRETTY_PRINT) . "\n\n";
    
    $test = new WordPressObjectCacheTest($config);
    $test->run();
}
?>