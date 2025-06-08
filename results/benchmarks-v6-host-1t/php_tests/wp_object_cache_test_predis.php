<?php
/**
 * Enhanced WordPress Object Cache Test with Predis Implementation
 * 
 * Features:
 * - Multiple test iterations for statistical reliability
 * - Standard deviation, coefficient of variation calculations
 * - Confidence intervals and measurement quality assessment
 * - Raw data logging for detailed analysis
 * - Enhanced reporting with statistical measures
 * - Thread-aware configuration and reporting
 * - Predis-based Redis client for better TLS support
 */

require_once 'RedisTestBase-predis.php';

class WordPressObjectCacheTestPredis extends RedisTestBasePredis {
    private $operations = 100000;  // Operations per iteration
    private $test_duration = 30;   // Duration per iteration in seconds
    private $read_write_ratio = 70; // 70% reads, 30% writes
    
    // WordPress-like cache groups
    private $cache_groups = [
        'posts', 'terms', 'users', 'options', 'comments', 
        'themes', 'plugins', 'transients', 'site-options'
    ];
    
    public function __construct($config = []) {
        $this->test_name = "WordPress Object Cache Test (Predis)";
        
        // Override default iterations if specified
        if (isset($config['test_iterations'])) {
            $this->test_iterations = $config['test_iterations'];
        }
        
        // Test-specific configuration
        $this->operations = $config['operations'] ?? 100000;
        $this->test_duration = $config['duration'] ?? 30;
        $this->read_write_ratio = $config['read_write_ratio'] ?? 70;
        
        parent::__construct($config);
        
        $this->debugLog("WordPress Object Cache Test (Predis) initialized");
        $this->debugLog("Operations per iteration: {$this->operations}");
        $this->debugLog("Duration per iteration: {$this->test_duration}s");
        $this->debugLog("Read/Write ratio: {$this->read_write_ratio}%/" . (100 - $this->read_write_ratio) . "%");
    }
    
    /**
     * Override: Run a single test iteration with WordPress-like cache operations using Predis
     */
    protected function runSingleIteration($redis, $test_label, $iteration) {
        $start_time = microtime(true);
        $operations_completed = 0;
        $errors = 0;
        $latencies = [];
        
        $this->debugLog("Starting WordPress cache simulation iteration {$iteration} with Predis");
        
        // Time-based execution for consistent duration
        $end_time = $start_time + $this->test_duration;
        
        while (microtime(true) < $end_time) {
            $operation_start = microtime(true);
            
            try {
                // Determine operation type based on read/write ratio
                $is_read = (rand(1, 100) <= $this->read_write_ratio);
                
                if ($is_read) {
                    // READ operation - simulate WordPress cache lookup
                    $cache_key = $this->generateWordPressCacheKey();
                    
                    // Predis GET operation
                    $result = $redis->get($cache_key);
                    
                    // If key doesn't exist, simulate cache miss - add the data
                    if ($result === null) {
                        $cache_data = $this->generateWordPressCacheData();
                        $ttl = $this->generateWordPressTTL();
                        
                        // Predis SETEX operation (set with expiration)
                        $redis->setex($cache_key, $ttl, $cache_data);
                    }
                } else {
                    // WRITE operation - simulate WordPress cache update
                    $cache_key = $this->generateWordPressCacheKey();
                    $cache_data = $this->generateWordPressCacheData();
                    $ttl = $this->generateWordPressTTL();
                    
                    // Predis SETEX operation
                    $redis->setex($cache_key, $ttl, $cache_data);
                }
                
                $operations_completed++;
                
            } catch (Exception $e) {
                $errors++;
                $this->debugLog("Operation error in iteration {$iteration}: " . $e->getMessage());
            }
            
            $operation_end = microtime(true);
            $latencies[] = ($operation_end - $operation_start) * 1000; // Convert to milliseconds
            
            // Small delay to prevent overwhelming the server
            if ($operations_completed % 1000 == 0) {
                usleep(100); // 0.1ms pause every 1000 operations
            }
        }
        
        $total_duration = microtime(true) - $start_time;
        
        // Calculate statistics
        $ops_per_sec = $operations_completed / $total_duration;
        $avg_latency = count($latencies) > 0 ? array_sum($latencies) / count($latencies) : 0;
        $error_rate = ($errors / max($operations_completed, 1)) * 100;
        
        // Calculate percentile latencies
        sort($latencies);
        $p95_latency = $this->calculatePercentileFromArray($latencies, 95);
        $p99_latency = $this->calculatePercentileFromArray($latencies, 99);
        
        $this->debugLog("Iteration {$iteration} completed: {$operations_completed} ops in {$total_duration}s");
        
        return [
            'operations' => $operations_completed,
            'errors' => $errors,
            'duration' => $total_duration,
            'ops_per_sec' => $ops_per_sec,
            'avg_latency' => $avg_latency,
            'p95_latency' => $p95_latency,
            'p99_latency' => $p99_latency,
            'error_rate' => $error_rate,
            'read_write_ratio' => $this->read_write_ratio,
            'test_duration_target' => $this->test_duration,
            'test_duration_actual' => $total_duration,
            'latency_samples' => count($latencies),
            'predis_implementation' => true
        ];
    }
    
    /**
     * Calculate percentile from array of values
     */
    private function calculatePercentileFromArray($values, $percentile) {
        if (empty($values)) return 0;
        
        $index = ($percentile / 100) * (count($values) - 1);
        
        if (floor($index) == $index) {
            return $values[$index];
        } else {
            $lower = $values[floor($index)];
            $upper = $values[ceil($index)];
            return $lower + (($index - floor($index)) * ($upper - $lower));
        }
    }
    
    /**
     * Generate WordPress-like cache keys with realistic patterns
     */
    private function generateWordPressCacheKey() {
        $group = $this->cache_groups[array_rand($this->cache_groups)];
        
        switch ($group) {
            case 'posts':
                $post_id = rand(1, 10000);
                return "wp:{$group}:post_{$post_id}";
            
            case 'terms':
                $term_id = rand(1, 500);
                return "wp:{$group}:term_{$term_id}";
            
            case 'users':
                $user_id = rand(1, 1000);
                return "wp:{$group}:user_{$user_id}";
            
            case 'options':
                $options = ['site_url', 'home_url', 'theme_options', 'active_plugins', 'site_title'];
                $option = $options[array_rand($options)];
                return "wp:{$group}:{$option}";
            
            case 'comments':
                $comment_id = rand(1, 50000);
                return "wp:{$group}:comment_{$comment_id}";
            
            case 'themes':
                $themes = ['twentytwentyfour', 'twentytwentythree', 'custom-theme'];
                $theme = $themes[array_rand($themes)];
                return "wp:{$group}:{$theme}_stylesheet";
            
            case 'plugins':
                $plugins = ['woocommerce', 'yoast', 'jetpack', 'elementor'];
                $plugin = $plugins[array_rand($plugins)];
                return "wp:{$group}:{$plugin}_options";
            
            case 'transients':
                $transients = ['feed_cache', 'update_core', 'update_plugins', 'site_health'];
                $transient = $transients[array_rand($transients)];
                return "wp:{$group}:_transient_{$transient}";
            
            case 'site-options':
                $site_options = ['network_settings', 'multisite_options', 'global_config'];
                $option = $site_options[array_rand($site_options)];
                return "wp:{$group}:{$option}";
            
            default:
                return "wp:{$group}:key_" . rand(1, 1000);
        }
    }
    
    /**
     * Generate WordPress-like cache data with realistic sizes
     */
    private function generateWordPressCacheData() {
        // Simulate different types of WordPress cache data
        $data_types = [
            'post_content' => $this->generatePostContent(),
            'user_data' => $this->generateUserData(),
            'options' => $this->generateOptionsData(),
            'query_results' => $this->generateQueryResults(),
            'theme_data' => $this->generateThemeData()
        ];
        
        $type = array_rand($data_types);
        return serialize($data_types[$type]);
    }
    
    /**
     * Generate simulated WordPress post content
     */
    private function generatePostContent() {
        return [
            'ID' => rand(1, 10000),
            'post_title' => 'Sample WordPress Post Title ' . rand(1, 1000),
            'post_content' => str_repeat('Lorem ipsum dolor sit amet, consectetur adipiscing elit. ', rand(10, 50)),
            'post_excerpt' => 'Sample excerpt for the post',
            'post_status' => 'publish',
            'post_type' => 'post',
            'post_author' => rand(1, 100),
            'post_date' => date('Y-m-d H:i:s'),
            'meta_data' => [
                '_edit_lock' => time() . ':' . rand(1, 100),
                '_edit_last' => rand(1, 100),
                'custom_field_' . rand(1, 10) => 'custom_value_' . rand(1, 1000)
            ]
        ];
    }
    
    /**
     * Generate simulated WordPress user data
     */
    private function generateUserData() {
        return [
            'ID' => rand(1, 1000),
            'user_login' => 'user_' . rand(1, 1000),
            'user_email' => 'user' . rand(1, 1000) . '@example.com',
            'user_registered' => date('Y-m-d H:i:s'),
            'display_name' => 'User ' . rand(1, 1000),
            'capabilities' => ['subscriber' => true],
            'user_meta' => [
                'nickname' => 'nickname_' . rand(1, 1000),
                'description' => 'User description text here',
                'locale' => 'en_US'
            ]
        ];
    }
    
    /**
     * Generate simulated WordPress options data
     */
    private function generateOptionsData() {
        $options = [
            ['option_name' => 'site_title', 'option_value' => 'My WordPress Site'],
            ['option_name' => 'active_plugins', 'option_value' => ['plugin1/plugin1.php', 'plugin2/plugin2.php']],
            ['option_name' => 'theme_options', 'option_value' => ['color' => '#ffffff', 'layout' => 'full-width']],
            ['option_name' => 'widget_settings', 'option_value' => array_fill(0, rand(5, 15), 'widget_data')]
        ];
        
        return $options[array_rand($options)];
    }
    
    /**
     * Generate simulated WordPress database query results
     */
    private function generateQueryResults() {
        $query_count = rand(5, 20);
        $results = [];
        
        for ($i = 0; $i < $query_count; $i++) {
            $results[] = [
                'ID' => rand(1, 10000),
                'post_title' => 'Query Result ' . $i,
                'post_date' => date('Y-m-d H:i:s', strtotime('-' . rand(0, 365) . ' days')),
                'post_status' => 'publish'
            ];
        }
        
        return [
            'query' => 'SELECT * FROM wp_posts WHERE post_status = "publish"',
            'results' => $results,
            'found_posts' => $query_count,
            'cache_time' => time()
        ];
    }
    
    /**
     * Generate simulated WordPress theme data
     */
    private function generateThemeData() {
        return [
            'theme_name' => 'Custom Theme',
            'stylesheet' => str_repeat('.class { property: value; }', rand(20, 100)),
            'template_cache' => [
                'header.php' => 'header template content',
                'footer.php' => 'footer template content',
                'index.php' => 'index template content'
            ],
            'customizer_settings' => [
                'background_color' => '#ffffff',
                'text_color' => '#000000',
                'custom_logo' => rand(1, 1000)
            ]
        ];
    }
    
    /**
     * Generate realistic WordPress cache TTL values
     */
    private function generateWordPressTTL() {
        // WordPress typical cache durations
        $ttl_options = [
            300,    // 5 minutes - transient data
            900,    // 15 minutes - user sessions
            1800,   // 30 minutes - theme data
            3600,   // 1 hour - post content
            7200,   // 2 hours - menu data
            21600,  // 6 hours - widget data
            43200,  // 12 hours - options
            86400   // 24 hours - rarely changing data
        ];
        
        return $ttl_options[array_rand($ttl_options)];
    }
    
    /**
     * Enhanced error handling for Predis-specific exceptions
     */
    protected function handlePredisException($e, $operation, $iteration) {
        $error_type = get_class($e);
        $error_message = $e->getMessage();
        
        $this->debugLog("Predis {$error_type} during {$operation} in iteration {$iteration}: {$error_message}");
        
        // Specific handling for different Predis exception types
        if (strpos($error_type, 'ConnectionException') !== false) {
            echo "  ⚠️ Predis connection issue during {$operation}: {$error_message}\n";
        } elseif (strpos($error_type, 'ServerException') !== false) {
            echo "  ⚠️ Redis server error during {$operation}: {$error_message}\n";
        } else {
            echo "  ⚠️ Predis error during {$operation}: {$error_message}\n";
        }
        
        return false;
    }
    
    /**
     * Get Predis-specific performance insights
     */
    public function getPredisPerformanceInsights($results) {
        if (empty($results)) {
            return [];
        }
        
        $insights = [];
        
        // Analyze Predis-specific metrics
        foreach ($results as $result) {
            if (!isset($result['predis_implementation']) || !$result['predis_implementation']) {
                continue;
            }
            
            $db_name = $result['database'];
            $is_tls = $result['tls'];
            
            $insights[] = [
                'database' => $db_name,
                'tls' => $is_tls,
                'ops_per_sec' => $result['ops_per_sec'],
                'avg_latency' => $result['avg_latency'],
                'measurement_quality' => $result['measurement_quality'] ?? 'unknown',
                'predis_connection_config' => $result['predis_config'] ?? [],
                'connection_success_rate' => 100, // Predis succeeded if we have results
                'tls_reliability' => $is_tls ? 'successful' : 'n/a'
            ];
        }
        
        return $insights;
    }
}

// Allow direct execution for testing
if (basename(__FILE__) == basename($_SERVER['PHP_SELF'])) {
    echo "WordPress Object Cache Test with Predis - Direct Execution\n";
    echo "=========================================================\n";
    
    try {
        // Default configuration for direct testing
        $config = [
            'duration' => 30,
            'operations' => 50000,
            'test_iterations' => 5,
            'output_dir' => './predis_test_results',
            'test_tls' => true,
            'flush_before_test' => true,
            'debug' => true,
            'read_write_ratio' => 70,
            'thread_variant' => 'direct-test',
            'save_raw_results' => true,
            'connection_timeout' => 5.0,
            'read_write_timeout' => 5.0,
            'connection_retry_attempts' => 3
        ];
        
        echo "Initializing Predis WordPress test with configuration:\n";
        foreach ($config as $key => $value) {
            echo "  {$key}: " . (is_bool($value) ? ($value ? 'true' : 'false') : $value) . "\n";
        }
        echo "\n";
        
        $test = new WordPressObjectCacheTestPredis($config);
        $test->run();
        
        echo "\n✅ Predis WordPress Object Cache test completed successfully!\n";
        
    } catch (Exception $e) {
        echo "\n❌ Test failed: " . $e->getMessage() . "\n";
        echo "Stack trace:\n" . $e->getTraceAsString() . "\n";
        exit(1);
    }
}
?>