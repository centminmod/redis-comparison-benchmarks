<?php
/**
 * Base class for WordPress Redis Tests
 * Handles Redis connections, TLS setup, result formatting, and database management
 * 
 * Features:
 * - Non-TLS and TLS connection support with version compatibility
 * - Enhanced TLS error handling and diagnostics
 * - TLS port connectivity pre-checks
 * - Performance comparison between TLS and non-TLS
 * - FLUSHALL database cleanup before tests
 * - Multiple output formats (CSV, JSON, Markdown)
 * - Comprehensive error handling
 * - Debug output and verification
 * - Repository root path handling
 */

class RedisTestBase {
    protected $databases = [
        'Redis' => ['host' => '127.0.0.1', 'port' => 6379, 'tls_port' => 6390],
        'KeyDB' => ['host' => '127.0.0.1', 'port' => 6380, 'tls_port' => 6391],
        'Dragonfly' => ['host' => '127.0.0.1', 'port' => 6381, 'tls_port' => 6392],
        'Valkey' => ['host' => '127.0.0.1', 'port' => 6382, 'tls_port' => 6393]
    ];
    
    protected $test_name = "WordPress Redis Test";
    protected $output_dir = 'php_benchmark_results';
    protected $test_both_tls = true;
    protected $flush_before_test = false;
    protected $debug_mode = false;
    protected $tls_skip_verify = true;
    
    public function __construct($config = []) {
        $this->output_dir = $config['output_dir'] ?? 'php_benchmark_results';
        $this->test_both_tls = $config['test_tls'] ?? true;
        $this->flush_before_test = $config['flush_before_test'] ?? false;
        $this->debug_mode = $config['debug'] ?? false;
        $this->tls_skip_verify = $config['tls_skip_verify'] ?? true;
        
        // Override database configurations if provided
        if (isset($config['databases'])) {
            $this->databases = array_merge($this->databases, $config['databases']);
        }
        
        if (!extension_loaded('redis')) {
            throw new Exception('Redis PHP extension is required');
        }
        
        // Handle relative paths from repository root
        if (!is_dir($this->output_dir)) {
            if (!mkdir($this->output_dir, 0755, true)) {
                throw new Exception("Could not create output directory: {$this->output_dir}");
            }
        }
        
        $this->debugLog("RedisTestBase initialized");
        $this->debugLog("Output directory: {$this->output_dir}");
        $this->debugLog("TLS testing: " . ($this->test_both_tls ? 'enabled' : 'disabled'));
        $this->debugLog("Flush before test: " . ($this->flush_before_test ? 'enabled' : 'disabled'));
        $this->debugLog("Redis extension version: " . $this->getRedisExtensionVersion());
        $this->debugLog("TLS skip verify: " . ($this->tls_skip_verify ? 'enabled' : 'disabled'));
    }
    
    /**
     * Get Redis extension version for compatibility checks
     */
    private function getRedisExtensionVersion() {
        try {
            $reflection = new ReflectionExtension('redis');
            return $reflection->getVersion();
        } catch (Exception $e) {
            return 'unknown';
        }
    }
    
    /**
     * Check if TLS certificates exist and are readable
     */
    private function validateTlsCertificates() {
        $cert_files = [
            'local_cert' => './client_cert.pem',
            'local_pk'   => './client_priv.pem',
            'cafile'     => './ca.crt'
        ];
        
        $missing_certs = [];
        $cert_info = [];
        
        foreach ($cert_files as $key => $file) {
            if (!file_exists($file)) {
                $missing_certs[] = $file;
            } else {
                $cert_info[$key] = [
                    'file' => $file,
                    'size' => filesize($file),
                    'readable' => is_readable($file),
                    'modified' => date('Y-m-d H:i:s', filemtime($file))
                ];
            }
        }
        
        return [
            'valid' => empty($missing_certs),
            'missing' => $missing_certs,
            'info' => $cert_info
        ];
    }
    
    /**
     * Test if TLS port is accessible before attempting Redis connection
     */
    private function testTlsPortConnectivity($host, $port, $timeout = 2) {
        $this->debugLog("Testing TLS port connectivity to {$host}:{$port}");
        
        $context = stream_context_create([
            'ssl' => [
                'verify_peer' => false,
                'verify_peer_name' => false,
                'allow_self_signed' => true
            ]
        ]);
        
        $socket = @stream_socket_client(
            "ssl://{$host}:{$port}",
            $errno,
            $errstr,
            $timeout,
            STREAM_CLIENT_CONNECT,
            $context
        );
        
        if ($socket) {
            fclose($socket);
            $this->debugLog("TLS port {$host}:{$port} is accessible");
            return true;
        } else {
            $this->debugLog("TLS port {$host}:{$port} is not accessible: {$errstr} ({$errno})");
            return false;
        }
    }
    
    public function run() {
        echo "Starting {$this->test_name}...\n";
        echo "Timestamp: " . date('Y-m-d H:i:s') . " UTC\n";
        echo "Redis Extension Version: " . $this->getRedisExtensionVersion() . "\n";
        
        // Validate TLS certificates if TLS testing is enabled
        $tls_ready_databases = [];
        if ($this->test_both_tls) {
            $cert_validation = $this->validateTlsCertificates();
            if (!$cert_validation['valid']) {
                echo "TLS Certificate Warning: Missing files - " . implode(', ', $cert_validation['missing']) . "\n";
            } else {
                echo "TLS Certificates: Found and validated\n";
                foreach ($cert_validation['info'] as $type => $info) {
                    $this->debugLog("Certificate {$type}: {$info['file']} ({$info['size']} bytes, modified: {$info['modified']})");
                }
            }
            
            // Check TLS port accessibility
            echo "\nChecking TLS readiness...\n";
            foreach ($this->databases as $db_name => $config) {
                if ($this->testTlsPortConnectivity($config['host'], $config['tls_port'], 3)) {
                    $tls_ready_databases[] = $db_name;
                    echo "  {$db_name}: TLS port accessible ✓\n";
                } else {
                    echo "  {$db_name}: TLS port not accessible ✗\n";
                }
            }
            
            if (empty($tls_ready_databases)) {
                echo "\nNo databases have accessible TLS ports. Running non-TLS tests only.\n";
                $this->test_both_tls = false;
            } else {
                echo "\nTLS testing will be attempted for: " . implode(', ', $tls_ready_databases) . "\n";
            }
        }
        
        echo str_repeat("=", 60) . "\n";
        
        $all_results = [];
        $test_start_time = microtime(true);
        
        foreach ($this->databases as $db_name => $config) {
            echo "Testing {$db_name}...\n";
            
            // Test non-TLS
            $redis = $this->connectRedis($config['host'], $config['port'], false);
            if ($redis) {
                $result = $this->runSingleTest($redis, $db_name, false, $config['port']);
                if ($result) {
                    $all_results[] = $result;
                }
                $redis->close();
            }
            
            // Test TLS only for databases with accessible TLS ports
            if ($this->test_both_tls && in_array($db_name, $tls_ready_databases)) {
                $redis_tls = $this->connectRedis($config['host'], $config['tls_port'], true);
                if ($redis_tls) {
                    $result = $this->runSingleTest($redis_tls, $db_name, true, $config['tls_port']);
                    if ($result) {
                        $all_results[] = $result;
                    }
                    $redis_tls->close();
                }
            } elseif ($this->test_both_tls) {
                echo "  Skipping TLS test for {$db_name} (port not accessible)\n";
            }
            
            echo "\n";
        }
        
        $total_test_time = microtime(true) - $test_start_time;
        
        // Save results in multiple formats
        $this->saveResults($all_results);
        
        echo str_repeat("=", 60) . "\n";
        echo "Test suite completed!\n";
        echo "Total execution time: " . number_format($total_test_time, 2) . " seconds\n";
        echo "Total tests run: " . count($all_results) . "\n";
        echo "Results saved to {$this->output_dir}/\n";
        
        // Print summaries
        $this->printResultsSummary($all_results);
        $this->printTlsPerformanceComparison($all_results);
    }
    
    protected function runSingleTest($redis, $db_name, $is_tls, $port) {
        $test_label = $db_name . ($is_tls ? ' (TLS)' : ' (non-TLS)');
        echo "  Running {$test_label}...\n";
        
        try {
            // Get initial database state
            $initial_keys = $redis->dbSize();
            echo "  Initial keys in database: {$initial_keys}\n";
            
            // Flush database before test if configured
            if ($this->flush_before_test) {
                echo "  Flushing database before test...\n";
                $flush_start = microtime(true);
                $redis->flushAll();
                $flush_time = microtime(true) - $flush_start;
                $key_count_after_flush = $redis->dbSize();
                echo "  Database flushed in " . number_format($flush_time * 1000, 2) . "ms. Keys remaining: {$key_count_after_flush}\n";
            }
            
            // Run the actual test
            $result = $this->runTest($redis, $test_label);
            
            // Add metadata to result
            $result['database'] = $db_name;
            $result['tls'] = $is_tls;
            $result['port'] = $port;
            $result['flushed_before_test'] = $this->flush_before_test;
            $result['initial_key_count'] = $initial_keys;
            $result['test_timestamp'] = date('c');
            $result['php_version'] = PHP_VERSION;
            $result['redis_extension_version'] = $this->getRedisExtensionVersion();
            
            // Get final database state
            $final_keys = $redis->dbSize();
            $result['final_key_count'] = $final_keys;
            
            echo sprintf(
                "  %s: %.2f ops/sec, %.2fms avg latency, %.2f%% errors\n",
                $test_label,
                $result['ops_per_sec'],
                $result['avg_latency'],
                $result['error_rate']
            );
            echo "  Final keys in database: {$final_keys}\n";
            
            return $result;
            
        } catch (Exception $e) {
            echo "  ERROR: Test failed for {$test_label}: " . $e->getMessage() . "\n";
            return null;
        }
    }
    
    protected function connectRedis($host, $port, $tls = false) {
        $connection_label = $tls ? "TLS" : "non-TLS";
        $this->debugLog("Attempting {$connection_label} connection to {$host}:{$port}");
        
        try {
            $redis = new Redis();
            
            if ($tls) {
                // TLS connection with improved error handling
                $cert_files = [
                    'local_cert' => './client_cert.pem',
                    'local_pk'   => './client_priv.pem', 
                    'cafile'     => './ca.crt'
                ];
                
                // Check if certificates exist
                $missing_certs = [];
                foreach ($cert_files as $key => $file) {
                    if (!file_exists($file)) {
                        $missing_certs[] = $file;
                    }
                }
                
                if (!empty($missing_certs)) {
                    echo "  TLS certificates not found: " . implode(', ', $missing_certs) . "\n";
                    echo "  Skipping TLS test for {$host}:{$port}\n";
                    return false;
                }
                
                $this->debugLog("TLS certificates found, attempting connection");
                
                // Method 1: Direct TLS connection using tls:// scheme
                try {
                    $this->debugLog("Attempt 1: Using tls:// scheme");
                    $connected = $redis->connect("tls://{$host}", $port, 5.0);
                    if ($connected) {
                        $this->debugLog("TLS connection successful with tls:// scheme");
                    } else {
                        throw new Exception("Connection failed with tls:// scheme");
                    }
                } catch (Exception $e) {
                    $this->debugLog("tls:// scheme failed: " . $e->getMessage());
                    
                    // Method 2: Try with SSL context array
                    try {
                        $this->debugLog("Attempt 2: Using SSL context array");
                        $ssl_context = [
                            'verify_peer' => false,
                            'verify_peer_name' => false,
                            'allow_self_signed' => true,
                            'local_cert' => $cert_files['local_cert'],
                            'local_pk' => $cert_files['local_pk'],
                            'cafile' => $cert_files['cafile'],
                            'capture_peer_cert' => true,
                            'disable_compression' => true,
                            'SNI_enabled' => false
                        ];
                        
                        $connected = $redis->connect($host, $port, 5.0, null, 0, 0, $ssl_context);
                        if (!$connected) {
                            throw new Exception("SSL context connection failed");
                        }
                        $this->debugLog("TLS connection successful with SSL context");
                    } catch (Exception $e2) {
                        $this->debugLog("SSL context failed: " . $e2->getMessage());
                        
                        // Method 3: Try minimal TLS connection
                        try {
                            $this->debugLog("Attempt 3: Minimal TLS connection");
                            $minimal_context = ['verify_peer' => false, 'verify_peer_name' => false];
                            $connected = $redis->connect($host, $port, 5.0, null, 0, 0, $minimal_context);
                            if (!$connected) {
                                throw new Exception("Minimal TLS connection failed");
                            }
                            $this->debugLog("TLS connection successful with minimal context");
                        } catch (Exception $e3) {
                            throw new Exception("All TLS connection methods failed. Last: " . $e3->getMessage());
                        }
                    }
                }
            } else {
                // Non-TLS connection with improved timeout handling
                $redis->connect($host, $port, 2.0);
            }
            
            // Set read timeout to prevent socket errors
            $redis->setOption(Redis::OPT_READ_TIMEOUT, 5.0);
            
            // Test connection - use simpler test for TLS
            $this->debugLog("Testing connection");
            if ($tls) {
                // For TLS, try a simple command instead of PING
                try {
                    $test_key = 'connection_test_' . uniqid();
                    $redis->set($test_key, 'test', 1);
                    $result = $redis->get($test_key);
                    $redis->del($test_key);
                    if ($result !== 'test') {
                        throw new Exception("TLS connection test failed");
                    }
                    $this->debugLog("TLS connection verified with SET/GET test");
                } catch (Exception $e) {
                    throw new Exception("TLS connection verification failed: " . $e->getMessage());
                }
            } else {
                $ping_result = $redis->ping();
                $valid_responses = ['+PONG', 'PONG', true, 1];
                if (!in_array($ping_result, $valid_responses, true)) {
                    throw new Exception("PING failed: " . var_export($ping_result, true));
                }
                $this->debugLog("Non-TLS connection verified with PING");
            }
            
            $this->debugLog("Successfully connected to {$host}:{$port} ({$connection_label})");
            return $redis;
            
        } catch (Exception $e) {
            $error_msg = $e->getMessage();
            echo "  Connection failed to {$host}:{$port} ({$connection_label}): {$error_msg}\n";
            
            if ($tls) {
                echo "  → TLS connection troubleshooting:\n";
                echo "    - Check if TLS port {$port} is accessible\n";
                echo "    - Verify TLS certificates are valid\n";
                echo "    - Ensure server has TLS properly configured\n";
            }
            
            return false;
        }
    }
    
    /**
     * Compare TLS vs non-TLS performance
     */
    protected function printTlsPerformanceComparison($results) {
        $tls_results = array_filter($results, function($r) { return $r['tls']; });
        $non_tls_results = array_filter($results, function($r) { return !$r['tls']; });
        
        if (empty($tls_results)) {
            echo "\n" . str_repeat("=", 60) . "\n";
            echo "TLS PERFORMANCE COMPARISON\n";
            echo str_repeat("=", 60) . "\n";
            echo "No successful TLS connections for performance comparison.\n";
            echo "All databases tested with non-TLS only.\n";
            echo str_repeat("=", 60) . "\n";
            return;
        }
        
        echo "\n" . str_repeat("=", 60) . "\n";
        echo "TLS vs NON-TLS PERFORMANCE COMPARISON\n";
        echo str_repeat("=", 60) . "\n";
        
        foreach ($this->databases as $db_name => $config) {
            $non_tls = array_filter($non_tls_results, function($r) use ($db_name) { 
                return $r['database'] === $db_name; 
            });
            $tls = array_filter($tls_results, function($r) use ($db_name) { 
                return $r['database'] === $db_name; 
            });
            
            if (!empty($non_tls) && !empty($tls)) {
                $non_tls_ops = reset($non_tls)['ops_per_sec'];
                $tls_ops = reset($tls)['ops_per_sec'];
                $performance_impact = (($non_tls_ops - $tls_ops) / $non_tls_ops) * 100;
                
                echo sprintf("%-10s | Non-TLS: %8.0f ops/sec | TLS: %8.0f ops/sec | Impact: %+5.1f%%\n",
                    $db_name,
                    $non_tls_ops,
                    $tls_ops,
                    $performance_impact
                );
            } elseif (!empty($non_tls)) {
                echo sprintf("%-10s | Non-TLS: %8.0f ops/sec | TLS: %8s | Impact: %s\n",
                    $db_name,
                    reset($non_tls)['ops_per_sec'],
                    'FAILED',
                    'N/A'
                );
            }
        }
        echo str_repeat("=", 60) . "\n";
    }
    
    protected function saveResults($results) {
        if (empty($results)) {
            echo "No results to save.\n";
            return;
        }
        
        $timestamp = date('Y-m-d_H-i-s');
        $test_slug = strtolower(str_replace([' ', '-'], '_', $this->test_name));
        $test_slug = preg_replace('/[^a-z0-9_]/', '', $test_slug);
        
        $base_filename = "{$test_slug}_{$timestamp}";
        
        // Save in multiple formats
        $csv_file = $this->saveCSV($results, "{$this->output_dir}/{$base_filename}.csv");
        $json_file = $this->saveJSON($results, "{$this->output_dir}/{$base_filename}.json");
        $md_file = $this->saveMarkdown($results, "{$this->output_dir}/{$base_filename}.md");
        
        echo "Results saved:\n";
        echo "  CSV: {$csv_file}\n";
        echo "  JSON: {$json_file}\n";
        echo "  Markdown: {$md_file}\n";
    }
    
    protected function saveCSV($results, $filename) {
        $fp = fopen($filename, 'w');
        if (!$fp) {
            throw new Exception("Could not open file for writing: {$filename}");
        }
        
        if (!empty($results)) {
            // Header
            fputcsv($fp, array_keys($results[0]));
            
            // Data
            foreach ($results as $row) {
                fputcsv($fp, $row);
            }
        }
        
        fclose($fp);
        return $filename;
    }
    
    protected function saveJSON($results, $filename) {
        $data = [
            'test_name' => $this->test_name,
            'timestamp' => date('c'),
            'php_version' => PHP_VERSION,
            'redis_extension_version' => $this->getRedisExtensionVersion(),
            'test_configuration' => [
                'flush_before_test' => $this->flush_before_test,
                'test_tls' => $this->test_both_tls,
                'tls_skip_verify' => $this->tls_skip_verify,
                'output_dir' => $this->output_dir
            ],
            'results_count' => count($results),
            'results' => $results
        ];
        
        $json_content = json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        if ($json_content === false) {
            throw new Exception("Failed to encode results as JSON");
        }
        
        if (file_put_contents($filename, $json_content) === false) {
            throw new Exception("Could not write JSON file: {$filename}");
        }
        
        return $filename;
    }
    
    protected function saveMarkdown($results, $filename) {
        $content = "# {$this->test_name}\n\n";
        $content .= "**Test Date:** " . date('Y-m-d H:i:s') . " UTC\n";
        $content .= "**PHP Version:** " . PHP_VERSION . "\n";
        $content .= "**Redis Extension Version:** " . $this->getRedisExtensionVersion() . "\n";
        $content .= "**Results Count:** " . count($results) . "\n\n";
        
        $content .= "## Test Configuration\n\n";
        $content .= "- **Flush Before Test:** " . ($this->flush_before_test ? 'Yes' : 'No') . "\n";
        $content .= "- **TLS Testing:** " . ($this->test_both_tls ? 'Enabled' : 'Disabled') . "\n";
        $content .= "- **TLS Skip Verify:** " . ($this->tls_skip_verify ? 'Yes' : 'No') . "\n";
        $content .= "- **Output Directory:** {$this->output_dir}\n\n";
        
        if (!empty($results)) {
            $content .= "## Results\n\n";
            
            $headers = array_keys($results[0]);
            
            // Table header
            $content .= "| " . implode(" | ", $headers) . " |\n";
            $content .= "| " . str_repeat("--- | ", count($headers)) . "\n";
            
            // Table rows
            foreach ($results as $row) {
                $formatted_row = array_map(function($val) {
                    if (is_numeric($val)) {
                        return is_float($val) ? number_format($val, 3) : $val;
                    } elseif (is_bool($val)) {
                        return $val ? 'true' : 'false';
                    } else {
                        return $val;
                    }
                }, $row);
                $content .= "| " . implode(" | ", $formatted_row) . " |\n";
            }
        }
        
        $content .= "\n## Summary Statistics\n\n";
        if (!empty($results)) {
            $ops_per_sec = array_column($results, 'ops_per_sec');
            $avg_latencies = array_column($results, 'avg_latency');
            $error_rates = array_column($results, 'error_rate');
            
            $content .= "- **Average Ops/Sec:** " . number_format(array_sum($ops_per_sec) / count($ops_per_sec), 2) . "\n";
            $content .= "- **Max Ops/Sec:** " . number_format(max($ops_per_sec), 2) . "\n";
            $content .= "- **Average Latency:** " . number_format(array_sum($avg_latencies) / count($avg_latencies), 3) . "ms\n";
            $content .= "- **Average Error Rate:** " . number_format(array_sum($error_rates) / count($error_rates), 3) . "%\n";
        }
        
        if (file_put_contents($filename, $content) === false) {
            throw new Exception("Could not write Markdown file: {$filename}");
        }
        
        return $filename;
    }
    
    protected function printResultsSummary($results) {
        if (empty($results)) {
            return;
        }
        
        echo "\n" . str_repeat("=", 60) . "\n";
        echo "PERFORMANCE SUMMARY\n";
        echo str_repeat("=", 60) . "\n";
        
        // Group results by database and TLS status
        $grouped = [];
        foreach ($results as $result) {
            $key = $result['database'] . ($result['tls'] ? ' (TLS)' : '');
            $grouped[$key] = $result;
        }
        
        // Sort by ops_per_sec descending
        uasort($grouped, function($a, $b) {
            $a_ops = isset($a['ops_per_sec']) ? (float)$a['ops_per_sec'] : 0;
            $b_ops = isset($b['ops_per_sec']) ? (float)$b['ops_per_sec'] : 0;
            
            if ($a_ops == $b_ops) {
                return 0;
            }
            return ($a_ops < $b_ops) ? 1 : -1;
        });
        
        $rank = 1;
        foreach ($grouped as $key => $result) {
            echo sprintf("#%d %-20s %8.2f ops/sec  %6.2fms latency  %5.2f%% errors\n",
                $rank++,
                $key,
                $result['ops_per_sec'],
                $result['avg_latency'],
                $result['error_rate']
            );
        }
        
        echo str_repeat("=", 60) . "\n";
    }
    
    protected function percentile($array, $percentile) {
        if (empty($array)) {
            return 0;
        }
        
        sort($array);
        $index = ceil($percentile / 100 * count($array)) - 1;
        return $array[max(0, $index)];
    }
    
    protected function debugLog($message) {
        if ($this->debug_mode) {
            echo "[DEBUG] " . date('H:i:s') . " - {$message}\n";
        }
    }
    
    // Override this method in child classes
    protected function runTest($redis, $db_name) {
        // Default implementation - should be overridden
        sleep(1);
        
        return [
            'operations' => 1000,
            'errors' => 0,
            'duration' => 1.0,
            'ops_per_sec' => 1000.0,
            'avg_latency' => 1.0,
            'p95_latency' => 1.5,
            'p99_latency' => 2.0,
            'error_rate' => 0.0
        ];
    }
    
    // Static helper method for configuration validation
    public static function validateConfig($config) {
        $required_keys = ['duration', 'output_dir'];
        $missing_keys = [];
        
        foreach ($required_keys as $key) {
            if (!isset($config[$key])) {
                $missing_keys[] = $key;
            }
        }
        
        if (!empty($missing_keys)) {
            throw new Exception("Missing required configuration keys: " . implode(', ', $missing_keys));
        }
        
        // Validate duration
        if (!is_numeric($config['duration']) || $config['duration'] <= 0) {
            throw new Exception("Duration must be a positive number");
        }
        
        // Validate output directory path
        if (empty($config['output_dir']) || !is_string($config['output_dir'])) {
            throw new Exception("Output directory must be a non-empty string");
        }
        
        return true;
    }
    
    // Static helper method to check Redis extension
    public static function checkRedisExtension() {
        if (!extension_loaded('redis')) {
            throw new Exception('Redis PHP extension is not loaded. Install with: pecl install redis');
        }
        
        $reflection = new ReflectionExtension('redis');
        return [
            'loaded' => true,
            'version' => $reflection->getVersion(),
            'methods' => get_class_methods('Redis')
        ];
    }
    
    // Static helper method to test basic connectivity
    public static function testConnection($host = '127.0.0.1', $port = 6379, $timeout = 2.0) {
        try {
            $redis = new Redis();
            $redis->connect($host, $port, $timeout);
            $result = $redis->ping();
            $redis->close();
            
            return [
                'success' => true,
                'host' => $host,
                'port' => $port,
                'ping_result' => $result
            ];
        } catch (Exception $e) {
            return [
                'success' => false,
                'host' => $host,
                'port' => $port,
                'error' => $e->getMessage()
            ];
        }
    }
}
?>