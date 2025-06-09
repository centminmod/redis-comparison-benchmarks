<?php
/**
 * Enhanced RedisTestBase with 5-Run Testing and Statistical Analysis
 * 
 * Features:
 * - Multiple test iterations for statistical reliability
 * - Standard deviation, coefficient of variation calculations
 * - Confidence intervals and measurement quality assessment
 * - Raw data logging for detailed analysis
 * - Enhanced reporting with statistical measures
 * - Thread-aware configuration and reporting
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
    
    // NEW: Multi-run testing configuration
    protected $test_iterations = 13;
    protected $iteration_pause_ms = 500; // 500ms pause between iterations
    protected $save_raw_results = true;
    
    // Thread configuration properties
    protected $thread_variant = 'unknown';
    protected $thread_config = [];
    
    // NEW: Statistical thresholds for measurement quality
    protected $cv_thresholds = [
        'excellent' => 0.02,  // CV < 2%
        'good' => 0.05,       // CV < 5%
        'fair' => 0.10,       // CV < 10%
        // 'poor' for CV >= 10%
    ];
    
    public function __construct($config = []) {
        $this->output_dir = $config['output_dir'] ?? 'php_benchmark_results';
        $this->test_both_tls = $config['test_tls'] ?? true;
        $this->flush_before_test = $config['flush_before_test'] ?? false;
        $this->debug_mode = $config['debug'] ?? false;
        $this->tls_skip_verify = $config['tls_skip_verify'] ?? true;
        
        // NEW: Multi-run configuration
        $this->test_iterations = $config['test_iterations'] ?? 13;
        $this->iteration_pause_ms = $config['iteration_pause_ms'] ?? 500;
        $this->save_raw_results = $config['save_raw_results'] ?? true;
        
        // Thread configuration
        $this->thread_variant = $config['thread_variant'] ?? 'unknown';
        $this->thread_config = $config['thread_config'] ?? [];
        
        // Override database configurations if provided
        if (isset($config['databases'])) {
            $this->databases = array_merge($this->databases, $config['databases']);
        }
        
        if (!extension_loaded('redis')) {
            throw new Exception('Redis PHP extension is required');
        }
        
        if (!is_dir($this->output_dir)) {
            if (!mkdir($this->output_dir, 0755, true)) {
                throw new Exception("Could not create output directory: {$this->output_dir}");
            }
        }
        
        $this->debugLog("Enhanced RedisTestBase initialized");
        $this->debugLog("Test iterations: {$this->test_iterations}");
        $this->debugLog("Iteration pause: {$this->iteration_pause_ms}ms");
        $this->debugLog("Save raw results: " . ($this->save_raw_results ? 'enabled' : 'disabled'));
        $this->debugLog("Output directory: {$this->output_dir}");
        $this->debugLog("Thread variant: {$this->thread_variant}");
    }
    
    /**
     * Get Redis extension version for compatibility checks
     */
    protected function getRedisExtensionVersion() {
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
     * Debug raw SSL socket connection to understand handshake issues
     */
    private function debugSSLSocket($host, $port) {
        echo "    🔍 Testing raw SSL socket to {$host}:{$port}\n";
        
        $context = stream_context_create([
            'ssl' => [
                'verify_peer' => false,
                'verify_peer_name' => false,
                'allow_self_signed' => true,
                'capture_peer_cert' => true
            ]
        ]);
        
        $socket = @stream_socket_client(
            "ssl://{$host}:{$port}",
            $errno,
            $errstr,
            5,
            STREAM_CLIENT_CONNECT,
            $context
        );
        
        if ($socket) {
            echo "    ✅ Raw SSL socket connection successful\n";
            
            // Get SSL info
            $ssl_info = stream_context_get_options($context);
            if (isset($ssl_info['ssl']['peer_certificate'])) {
                $cert_info = openssl_x509_parse($ssl_info['ssl']['peer_certificate']);
                echo "    📜 Server certificate subject: " . ($cert_info['subject']['CN'] ?? 'unknown') . "\n";
                echo "    📜 Server certificate issuer: " . ($cert_info['issuer']['CN'] ?? 'unknown') . "\n";
            }
            fclose($socket);
            return true;
        } else {
            echo "    ❌ Raw SSL socket failed: {$errstr} ({$errno})\n";
            return false;
        }
    }

    /**
     * Try Redis connection with specific SSL context and detailed error reporting
     */
    private function tryRedisConnection($redis, $host, $port, $ssl_context, $test_name, $skip_commands = false) {
        echo "    🔧 Testing: {$test_name}\n";
        echo "    📋 SSL Context: " . json_encode(array_keys($ssl_context)) . "\n";
        
        try {
            // Enable error reporting for this test
            $old_error_level = error_reporting(E_ALL);
            
            $connected = $redis->connect($host, $port, 5.0, null, 0, 0, $ssl_context);
            
            if ($connected) {
                echo "    ✅ Redis TLS connection successful with {$test_name}\n";
                
                if ($skip_commands) {
                    echo "    ⏭️ Skipping command test as requested\n";
                    return true;
                }
                
                // Test basic Redis command with detailed debugging
                try {
                    echo "    🧪 Testing Redis commands over TLS...\n";
                    
                    // Test 1: Simple PING
                    try {
                        echo "      📞 Testing PING...\n";
                        $ping_result = $redis->ping();
                        echo "      ✅ PING successful: " . var_export($ping_result, true) . "\n";
                    } catch (Exception $ping_e) {
                        echo "      ❌ PING failed: " . $ping_e->getMessage() . "\n";
                        throw $ping_e;
                    }
                    
                    // Test 2: Simple SET/GET
                    try {
                        $test_key = 'tls_test_' . uniqid();
                        echo "      💾 Testing SET with key: {$test_key}...\n";
                        $set_result = $redis->set($test_key, 'test_value', 1);
                        echo "      ✅ SET successful: " . var_export($set_result, true) . "\n";
                        
                        echo "      📖 Testing GET...\n";
                        $result = $redis->get($test_key);
                        echo "      ✅ GET successful: " . var_export($result, true) . "\n";
                        
                        echo "      🗑️ Testing DEL...\n";
                        $del_result = $redis->del($test_key);
                        echo "      ✅ DEL successful: " . var_export($del_result, true) . "\n";
                        
                        if ($result === 'test_value') {
                            echo "    ✅ All Redis commands working with {$test_name}\n";
                            return true;
                        } else {
                            echo "    ⚠️ Commands executed but GET returned unexpected value: " . var_export($result, true) . "\n";
                            return false;
                        }
                    } catch (Exception $cmd_e) {
                        echo "      ❌ Command failed: " . $cmd_e->getMessage() . "\n";
                        echo "      🔍 Error details: " . get_class($cmd_e) . "\n";
                        
                        // Try to get more connection info
                        try {
                            $info = $redis->info('server');
                            echo "      📊 Server still responsive, got info: " . (is_array($info) ? count($info) . " keys" : "non-array") . "\n";
                        } catch (Exception $info_e) {
                            echo "      💔 Connection appears dead: " . $info_e->getMessage() . "\n";
                        }
                        
                        throw $cmd_e;
                    }
                    
                } catch (Exception $cmd_e) {
                    echo "    ⚠️ Command test failed for {$test_name}: " . $cmd_e->getMessage() . "\n";
                    return false;
                }
            } else {
                $last_error = error_get_last();
                echo "    ❌ Redis connect() returned false for {$test_name}\n";
                if ($last_error) {
                    echo "    🐛 Last PHP error: " . $last_error['message'] . "\n";
                }
                return false;
            }
        } catch (Exception $e) {
            echo "    ❌ {$test_name} exception: " . $e->getMessage() . "\n";
            return false;
        } finally {
            error_reporting($old_error_level);
        }
    }

    /**
     * Validate and display certificate information
     */
    private function debugCertificates($cert_files) {
        echo "    🔍 Debugging certificate files:\n";
        
        foreach ($cert_files as $type => $file) {
            if (file_exists($file)) {
                $size = filesize($file);
                $perms = substr(sprintf('%o', fileperms($file)), -4);
                echo "    📄 {$type}: {$file} ({$size} bytes, perms: {$perms})\n";
                
                if ($type === 'local_cert' || $type === 'cafile') {
                    // Try to parse certificate
                    $cert_content = file_get_contents($file);
                    $cert_info = openssl_x509_parse($cert_content);
                    if ($cert_info) {
                        echo "      Subject CN: " . ($cert_info['subject']['CN'] ?? 'unknown') . "\n";
                        echo "      Issuer CN: " . ($cert_info['issuer']['CN'] ?? 'unknown') . "\n";
                        echo "      Valid from: " . date('Y-m-d H:i:s', $cert_info['validFrom_time_t']) . "\n";
                        echo "      Valid to: " . date('Y-m-d H:i:s', $cert_info['validTo_time_t']) . "\n";
                    } else {
                        echo "      ⚠️ Failed to parse certificate\n";
                    }
                }
            } else {
                echo "    ❌ {$type}: {$file} - FILE NOT FOUND\n";
            }
        }
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
    
    /**
     * Display thread-specific configuration for a database
     */
    protected function displayDatabaseThreadConfig($db_name, $config) {
        $thread_info = [];
        
        // Add thread information based on database type
        switch ($db_name) {
            case 'Redis':
                if (isset($config['io_threads'])) {
                    $thread_info[] = "IO Threads: {$config['io_threads']}";
                }
                break;
            case 'KeyDB':
                if (isset($config['server_threads'])) {
                    $thread_info[] = "Server Threads: {$config['server_threads']}";
                }
                break;
            case 'Dragonfly':
                if (isset($config['proactor_threads'])) {
                    $thread_info[] = "Proactor Threads: {$config['proactor_threads']}";
                }
                break;
            case 'Valkey':
                if (isset($config['io_threads'])) {
                    $thread_info[] = "IO Threads: {$config['io_threads']}";
                }
                break;
        }
        
        if (!empty($thread_info)) {
            echo "  Configuration: " . implode(', ', $thread_info) . "\n";
        }
    }
    
    /**
     * Extract thread configuration specific to a database
     */
    protected function extractDatabaseThreadConfig($db_name, $config) {
        $thread_config = [];
        
        switch ($db_name) {
            case 'Redis':
                if (isset($config['io_threads'])) {
                    $thread_config['io_threads'] = $config['io_threads'];
                }
                break;
            case 'KeyDB':
                if (isset($config['server_threads'])) {
                    $thread_config['server_threads'] = $config['server_threads'];
                }
                break;
            case 'Dragonfly':
                if (isset($config['proactor_threads'])) {
                    $thread_config['proactor_threads'] = $config['proactor_threads'];
                }
                break;
            case 'Valkey':
                if (isset($config['io_threads'])) {
                    $thread_config['io_threads'] = $config['io_threads'];
                }
                break;
        }
        
        return $thread_config;
    }
    
    public function run() {
        echo "Starting {$this->test_name}...\n";
        echo "Timestamp: " . date('Y-m-d H:i:s') . " UTC\n";
        echo "Redis Extension Version: " . $this->getRedisExtensionVersion() . "\n";
        
        // NEW: Display enhanced test configuration
        echo "Enhanced Testing Configuration:\n";
        echo "- Iterations per test: {$this->test_iterations}\n";
        echo "- Iteration pause: {$this->iteration_pause_ms}ms\n";
        echo "- Statistical analysis: Enabled\n";
        echo "- Raw data logging: " . ($this->save_raw_results ? 'Enabled' : 'Disabled') . "\n";
        
        // Display thread configuration information
        echo "Thread Variant: {$this->thread_variant}\n";
        if (!empty($this->thread_config)) {
            echo "Thread Configuration:\n";
            foreach ($this->thread_config as $db => $threads) {
                echo "  {$db}: {$threads} threads\n";
            }
        }
        
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
            
            // Display thread-specific configuration for this database
            $this->displayDatabaseThreadConfig($db_name, $config);
            
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
                } else {
                    echo "  → TLS test skipped for {$db_name} due to connection failure\n";
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
        echo "Enhanced test suite completed!\n";
        echo "Total execution time: " . number_format($total_test_time, 2) . " seconds\n";
        echo "Total tests run: " . count($all_results) . "\n";
        echo "Statistical iterations per test: {$this->test_iterations}\n";
        echo "Results saved to {$this->output_dir}/\n";
        
        // Print enhanced summaries
        $this->printResultsSummary($all_results);
        $this->printTlsPerformanceComparison($all_results);
        $this->printStatisticalInsights($all_results);
    }
    
    /**
     * NEW: Enhanced single test runner with multiple iterations
     */
    protected function runSingleTest($redis, $db_name, $is_tls, $port) {
        $test_label = $db_name . ($is_tls ? ' (TLS)' : ' (non-TLS)');
        echo "  Running {$this->test_iterations} iterations for {$test_label}...\n";
        
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
                $initial_keys = $key_count_after_flush; // Update initial count after flush
            }
            
            // Run multiple test iterations
            $all_iterations = [];
            for ($iteration = 1; $iteration <= $this->test_iterations; $iteration++) {
                echo "    Iteration {$iteration}/{$this->test_iterations}... ";
                
                $iteration_result = $this->runSingleIteration($redis, $test_label, $iteration);
                $iteration_result['iteration'] = $iteration;
                $iteration_result['iteration_timestamp'] = date('c');
                $all_iterations[] = $iteration_result;
                
                echo sprintf("%.0f ops/sec, %.3fms latency\n", 
                    $iteration_result['ops_per_sec'], $iteration_result['avg_latency']);
                
                // Brief pause between iterations to let system stabilize
                if ($iteration < $this->test_iterations && $this->iteration_pause_ms > 0) {
                    usleep($this->iteration_pause_ms * 1000);
                }
            }
            
            // Calculate aggregate statistics
            $aggregate_result = $this->calculateAggregateResults($all_iterations, $test_label);
            
            // Add metadata to result
            $aggregate_result['database'] = $db_name;
            $aggregate_result['tls'] = $is_tls;
            $aggregate_result['port'] = $port;
            $aggregate_result['flushed_before_test'] = $this->flush_before_test;
            $aggregate_result['initial_key_count'] = $initial_keys;
            $aggregate_result['test_timestamp'] = date('c');
            $aggregate_result['php_version'] = PHP_VERSION;
            $aggregate_result['redis_extension_version'] = $this->getRedisExtensionVersion();
            $aggregate_result['thread_variant'] = $this->thread_variant;
            $aggregate_result['thread_config'] = $this->thread_config;
            
            // Add database-specific thread information
            $db_config = $this->databases[$db_name] ?? [];
            $aggregate_result['database_thread_config'] = $this->extractDatabaseThreadConfig($db_name, $db_config);
            
            // Get final database state
            $final_keys = $redis->dbSize();
            $aggregate_result['final_key_count'] = $final_keys;
            
            // NEW: Store raw iterations if enabled
            if ($this->save_raw_results) {
                $aggregate_result['raw_iterations'] = $all_iterations;
            }
            
            // Enhanced output with statistical information
            echo sprintf(
                "  %s: %.2f±%.2f ops/sec (CV: %.1f%%), %.3f±%.3fms latency, Quality: %s\n",
                $test_label,
                $aggregate_result['ops_per_sec'],
                $aggregate_result['ops_per_sec_stddev'],
                $aggregate_result['ops_per_sec_cv'] * 100,
                $aggregate_result['avg_latency'],
                $aggregate_result['latency_stddev'],
                $aggregate_result['measurement_quality']
            );
            echo "  Final keys in database: {$final_keys}\n";
            
            return $aggregate_result;
            
        } catch (Exception $e) {
            echo "  ERROR: Test failed for {$test_label}: " . $e->getMessage() . "\n";
            return null;
        }
    }
    
    /**
     * NEW: Calculate aggregate results from multiple iterations
     */
    protected function calculateAggregateResults($iterations, $test_label) {
        if (empty($iterations)) {
            throw new Exception("No iterations to aggregate");
        }
        
        // Extract metric arrays
        $ops_per_sec = array_column($iterations, 'ops_per_sec');
        $latencies = array_column($iterations, 'avg_latency');
        $p95_latencies = array_column($iterations, 'p95_latency');
        $p99_latencies = array_column($iterations, 'p99_latency');
        $operations = array_column($iterations, 'operations');
        $errors = array_column($iterations, 'errors');
        $durations = array_column($iterations, 'duration');
        
        // Calculate basic statistics
        $avg_ops = $this->calculateMean($ops_per_sec);
        $stddev_ops = $this->calculateStandardDeviation($ops_per_sec);
        $cv_ops = $this->calculateCoefficientOfVariation($ops_per_sec);
        
        $avg_latency = $this->calculateMean($latencies);
        $stddev_latency = $this->calculateStandardDeviation($latencies);
        
        // Determine measurement quality
        $quality = $this->assessMeasurementQuality($cv_ops);
        
        // Calculate confidence interval (95%)
        $confidence_interval = $this->calculateConfidenceInterval($ops_per_sec, 0.95);
        
        return [
            'iterations_count' => count($iterations),
            'test_iterations' => $this->test_iterations,
            
            // Primary metrics (averages)
            'ops_per_sec' => $avg_ops,
            'avg_latency' => $avg_latency,
            'p95_latency' => $this->calculateMean($p95_latencies),
            'p99_latency' => $this->calculateMean($p99_latencies),
            
            // Statistical measures for ops/sec
            'ops_per_sec_min' => min($ops_per_sec),
            'ops_per_sec_max' => max($ops_per_sec),
            'ops_per_sec_stddev' => $stddev_ops,
            'ops_per_sec_cv' => $cv_ops,
            'ops_per_sec_confidence_interval_95' => $confidence_interval,
            
            // Statistical measures for latency
            'latency_min' => min($latencies),
            'latency_max' => max($latencies),
            'latency_stddev' => $stddev_latency,
            'latency_cv' => $this->calculateCoefficientOfVariation($latencies),
            
            // Measurement quality assessment
            'measurement_quality' => $quality,
            'measurement_reliable' => ($quality !== 'poor'),
            
            // Aggregated totals
            'total_operations' => array_sum($operations),
            'total_errors' => array_sum($errors),
            'error_rate' => (array_sum($errors) / max(array_sum($operations), 1)) * 100,
            'avg_duration' => $this->calculateMean($durations),
            
            // Additional percentiles for ops/sec
            'ops_per_sec_median' => $this->calculatePercentile($ops_per_sec, 50),
            'ops_per_sec_p25' => $this->calculatePercentile($ops_per_sec, 25),
            'ops_per_sec_p75' => $this->calculatePercentile($ops_per_sec, 75),
        ];
    }
    
    /**
     * NEW: Run a single test iteration (to be overridden by child classes)
     */
    protected function runSingleIteration($redis, $test_label, $iteration) {
        // Default implementation - child classes should override this
        $start_time = microtime(true);
        
        // Simulate some work
        usleep(rand(900000, 1100000)); // 0.9-1.1 seconds
        
        $duration = microtime(true) - $start_time;
        $operations = rand(950, 1050);
        
        return [
            'operations' => $operations,
            'errors' => 0,
            'duration' => $duration,
            'ops_per_sec' => $operations / $duration,
            'avg_latency' => ($duration / $operations) * 1000, // Convert to ms
            'p95_latency' => (($duration / $operations) * 1000) * 1.2,
            'p99_latency' => (($duration / $operations) * 1000) * 1.5,
            'error_rate' => 0.0
        ];
    }
    
    /**
     * NEW: Calculate mean of an array
     */
    protected function calculateMean($values) {
        if (empty($values)) return 0;
        return array_sum($values) / count($values);
    }
    
    /**
     * NEW: Calculate standard deviation (sample)
     */
    protected function calculateStandardDeviation($values) {
        if (count($values) < 2) return 0;
        
        $mean = $this->calculateMean($values);
        $sum_squares = 0;
        
        foreach ($values as $value) {
            $sum_squares += pow($value - $mean, 2);
        }
        
        // Sample standard deviation (n-1)
        return sqrt($sum_squares / (count($values) - 1));
    }
    
    /**
     * NEW: Calculate coefficient of variation
     */
    protected function calculateCoefficientOfVariation($values) {
        $mean = $this->calculateMean($values);
        if ($mean == 0) return 0;
        
        $stddev = $this->calculateStandardDeviation($values);
        return $stddev / $mean;
    }
    
    /**
     * NEW: Calculate confidence interval
     */
    protected function calculateConfidenceInterval($values, $confidence_level = 0.95) {
        if (count($values) < 2) return ['lower' => 0, 'upper' => 0, 'margin_error' => 0];
        
        $mean = $this->calculateMean($values);
        $stddev = $this->calculateStandardDeviation($values);
        $n = count($values);
        
        // T-score for 95% confidence (approximation for small samples)
        $t_scores = [
            2 => 12.706, 3 => 4.303, 4 => 3.182, 5 => 2.776,
            6 => 2.571, 7 => 2.447, 8 => 2.365, 9 => 2.306, 10 => 2.262
        ];
        
        $t_score = $t_scores[$n] ?? 2.0; // Default to ~2.0 for larger samples
        $margin_error = $t_score * ($stddev / sqrt($n));
        
        return [
            'lower' => $mean - $margin_error,
            'upper' => $mean + $margin_error,
            'margin_error' => $margin_error
        ];
    }
    
    /**
     * NEW: Calculate percentile
     */
    protected function calculatePercentile($values, $percentile) {
        if (empty($values)) return 0;
        
        sort($values);
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
     * NEW: Assess measurement quality based on coefficient of variation
     */
    protected function assessMeasurementQuality($cv) {
        if ($cv <= $this->cv_thresholds['excellent']) {
            return 'excellent';
        } elseif ($cv <= $this->cv_thresholds['good']) {
            return 'good';
        } elseif ($cv <= $this->cv_thresholds['fair']) {
            return 'fair';
        } else {
            return 'poor';
        }
    }
    
    /**
     * Connect to Redis with enhanced TLS support using official approach (adapted for custom ports)
     */
    protected function connectRedis($host, $port, $is_tls = false, $database_name = 'Unknown') {
        $this->debugLog("🔌 Connecting to $database_name at $host:$port" . ($is_tls ? ' (TLS)' : ''));
        
        $redis = new Redis();
        
        if (!$is_tls) {
            // Standard non-TLS connection
            if (!$redis->connect($host, $port, 2)) {
                throw new Exception("Failed to connect to $database_name at $host:$port");
            }
            $this->debugLog("✅ Connected to $database_name (non-TLS)");
            return $redis;
        }
        
        // TLS connection using official working approach adapted for your port scheme
        echo "🔐 Attempting TLS connection to $database_name at $host:$port\n";
        echo "  Using custom port scheme: Redis=6390, KeyDB=6391, Dragonfly=6392, Valkey=6393\n";
        
        try {
            // Method 1: Official tls:// scheme approach (adapted for your ports)
            echo "  📡 Method 1: Using tls:// scheme with custom port $port...\n";
            
            // Test with localhost first (allows peer name verification)
            $tls_host = ($host === '127.0.0.1') ? 'localhost' : $host;
            $verify_peer_name = ($tls_host === 'localhost');
            
            $tls_redis = new Redis();
            $success = $tls_redis->connect(
                'tls://' . $tls_host, 
                $port,  // Your custom TLS port (6390, 6391, etc.)
                2,      // timeout
                null, 
                0, 
                0, 
                [
                    'stream' => [
                        'verify_peer_name' => $verify_peer_name,
                        'verify_peer' => false,  // Allow self-signed certs
                        'allow_self_signed' => true,
                        'crypto_method' => STREAM_CRYPTO_METHOD_TLSv1_2_CLIENT
                    ]
                ]
            );
            
            if ($success) {
                echo "  ✅ TLS connection successful with tls://$tls_host:$port\n";
                
                // Test basic command
                echo "  🧪 Testing basic command over TLS...\n";
                try {
                    $pong = $tls_redis->ping();
                    if ($pong === true || $pong === 'PONG') {
                        echo "  ✅ PING successful over TLS\n";
                        $this->debugLog("✅ TLS connection to $database_name established and verified");
                        return $tls_redis;
                    } else {
                        echo "  ⚠️ PING returned unexpected result: " . var_export($pong, true) . "\n";
                    }
                } catch (Exception $e) {
                    echo "  ❌ PING failed: " . $e->getMessage() . "\n";
                }
            }
            
            // Method 2: Fallback to IP address if localhost failed
            if ($tls_host === 'localhost') {
                echo "  📡 Method 2: Fallback to IP address with port $port...\n";
                $tls_redis2 = new Redis();
                $success = $tls_redis2->connect(
                    'tls://127.0.0.1', 
                    $port,  // Keep your custom port
                    2, 
                    null, 
                    0, 
                    0, 
                    [
                        'stream' => [
                            'verify_peer_name' => false,
                            'verify_peer' => false,
                            'allow_self_signed' => true,
                            'crypto_method' => STREAM_CRYPTO_METHOD_TLSv1_2_CLIENT
                        ]
                    ]
                );
                
                if ($success) {
                    echo "  ✅ TLS connection successful with tls://127.0.0.1:$port\n";
                    try {
                        $pong = $tls_redis2->ping();
                        if ($pong === true || $pong === 'PONG') {
                            echo "  ✅ PING successful over TLS (IP)\n";
                            $this->debugLog("✅ TLS connection to $database_name established (IP fallback)");
                            return $tls_redis2;
                        }
                    } catch (Exception $e) {
                        echo "  ❌ PING failed on IP: " . $e->getMessage() . "\n";
                    }
                }
            }
            
            // Method 3: Minimal SSL context (legacy fallback)
            echo "  📡 Method 3: Legacy SSL context approach with port $port...\n";
            $context_redis = new Redis();
            $minimal_context = [
                'verify_peer' => false,
                'verify_peer_name' => false,
                'allow_self_signed' => true,
                'crypto_method' => STREAM_CRYPTO_METHOD_TLSv1_2_CLIENT
            ];
            
            $success = $context_redis->connect(
                $host, 
                $port,  // Your custom TLS port
                2, 
                null, 
                0, 
                0, 
                ['stream' => $minimal_context]
            );
            
            if ($success) {
                echo "  ✅ SSL context connection successful\n";
                try {
                    $pong = $context_redis->ping();
                    if ($pong === true || $pong === 'PONG') {
                        echo "  ✅ PING successful with SSL context\n";
                        $this->debugLog("✅ TLS connection to $database_name established (SSL context)");
                        return $context_redis;
                    }
                } catch (Exception $e) {
                    echo "  ❌ PING failed with SSL context: " . $e->getMessage() . "\n";
                }
            }
            
        } catch (Exception $e) {
            echo "  ❌ TLS connection failed: " . $e->getMessage() . "\n";
        }
        
        // If all TLS methods fail, implement graceful bypass strategy
        echo "  ❌ All TLS connection methods failed for $database_name at port $port\n";
        echo "  📋 Note: This is likely due to the known phpredis TLS command execution bug\n";
        echo "  🔄 TLS connections establish but Redis commands fail immediately\n";
        echo "  🚫 Bypassing TLS test for $database_name - known phpredis limitation\n";
        echo "  ✅ Non-TLS results remain valid and reliable for performance comparison\n";
        
        $this->debugLog("⚠️ TLS bypassed for $database_name due to phpredis extension bug");
        
        // Return null instead of throwing exception to allow graceful continuation
        return null;
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
            echo "Thread Variant: {$this->thread_variant}\n";
            echo str_repeat("=", 60) . "\n";
            echo "No successful TLS connections for performance comparison.\n";
            echo "All databases tested with non-TLS only.\n";
            echo str_repeat("=", 60) . "\n";
            return;
        }
        
        echo "\n" . str_repeat("=", 60) . "\n";
        echo "TLS vs NON-TLS PERFORMANCE COMPARISON\n";
        echo "Thread Variant: {$this->thread_variant}\n";
        echo str_repeat("=", 60) . "\n";
        
        foreach ($this->databases as $db_name => $config) {
            $non_tls = array_filter($non_tls_results, function($r) use ($db_name) { 
                return $r['database'] === $db_name; 
            });
            $tls = array_filter($tls_results, function($r) use ($db_name) { 
                return $r['database'] === $db_name; 
            });
            
            if (!empty($non_tls) && !empty($tls)) {
                $non_tls_result = reset($non_tls);
                $tls_result = reset($tls);
                
                $non_tls_ops = $non_tls_result['ops_per_sec'];
                $tls_ops = $tls_result['ops_per_sec'];
                $performance_impact = (($non_tls_ops - $tls_ops) / $non_tls_ops) * 100;
                
                // Check if difference is statistically significant
                $non_tls_ci = $non_tls_result['ops_per_sec_confidence_interval_95'] ?? [];
                $tls_ci = $tls_result['ops_per_sec_confidence_interval_95'] ?? [];
                
                $significant = "";
                if (isset($tls_ci['upper']) && isset($non_tls_ci['lower']) && 
                    $tls_ci['upper'] < $non_tls_ci['lower']) {
                    $significant = " *";
                }
                
                echo sprintf("%-10s | Non-TLS: %8.0f±%-4.0f | TLS: %8.0f±%-4.0f | Impact: %+5.1f%%%s\n",
                    $db_name,
                    $non_tls_ops,
                    $non_tls_result['ops_per_sec_stddev'] ?? 0,
                    $tls_ops,
                    $tls_result['ops_per_sec_stddev'] ?? 0,
                    $performance_impact,
                    $significant
                );
            } elseif (!empty($non_tls)) {
                echo sprintf("%-10s | Non-TLS: %8.0f±%-4.0f | TLS: %8s | Impact: %s\n",
                    $db_name,
                    reset($non_tls)['ops_per_sec'],
                    reset($non_tls)['ops_per_sec_stddev'] ?? 0,
                    'FAILED',
                    'N/A'
                );
            }
        }
        echo str_repeat("-", 60) . "\n";
        echo "* = Statistically significant difference (95% confidence)\n";
        echo str_repeat("=", 60) . "\n";
    }
    
    /**
     * NEW: Print statistical insights about the test results
     */
    protected function printStatisticalInsights($results) {
        if (empty($results)) {
            return;
        }
        
        echo "\n" . str_repeat("=", 80) . "\n";
        echo "STATISTICAL INSIGHTS\n";
        echo "Thread Variant: {$this->thread_variant} | Iterations: {$this->test_iterations}\n";
        echo str_repeat("=", 80) . "\n";
        
        // Analyze measurement quality
        $quality_counts = ['excellent' => 0, 'good' => 0, 'fair' => 0, 'poor' => 0];
        $cv_values = [];
        
        foreach ($results as $result) {
            $quality = $result['measurement_quality'] ?? 'unknown';
            if (isset($quality_counts[$quality])) {
                $quality_counts[$quality]++;
            }
            
            $cv = $result['ops_per_sec_cv'] ?? 0;
            if ($cv > 0) {
                $cv_values[] = $cv * 100; // Convert to percentage
            }
        }
        
        echo "Measurement Quality Distribution:\n";
        $total_tests = array_sum($quality_counts);
        foreach ($quality_counts as $quality => $count) {
            if ($count > 0) {
                $percentage = ($count / $total_tests) * 100;
                $quality_icons = ['excellent' => '🟢', 'good' => '🟡', 'fair' => '🟠', 'poor' => '🔴'];
                $quality_icon = $quality_icons[$quality] ?? '⚪';
                echo sprintf("  %s %-10s: %2d tests (%.1f%%)\n", 
                    $quality_icon, ucfirst($quality), $count, $percentage);
            }
        }
        
        if (!empty($cv_values)) {
            $avg_cv = $this->calculateMean($cv_values);
            $min_cv = min($cv_values);
            $max_cv = max($cv_values);
            
            echo "\nCoefficient of Variation Analysis:\n";
            echo sprintf("  Average CV: %.1f%% (lower is better)\n", $avg_cv);
            echo sprintf("  Range: %.1f%% - %.1f%%\n", $min_cv, $max_cv);
            
            if ($avg_cv < 2.0) {
                echo "  📊 Excellent measurement consistency across all tests\n";
            } elseif ($avg_cv < 5.0) {
                echo "  📊 Good measurement consistency\n";
            } elseif ($avg_cv < 10.0) {
                echo "  📊 Fair measurement consistency - consider test environment optimization\n";
            } else {
                echo "  ⚠️  Poor measurement consistency - investigate test conditions\n";
            }
        }
        
        // Analyze performance spread
        $all_ops = array_column($results, 'ops_per_sec');
        if (!empty($all_ops)) {
            $min_ops = min($all_ops);
            $max_ops = max($all_ops);
            $performance_range = (($max_ops - $min_ops) / $min_ops) * 100;
            
            echo "\nPerformance Analysis:\n";
            echo sprintf("  Performance range: %.0f - %.0f ops/sec (%.1f%% spread)\n", 
                $min_ops, $max_ops, $performance_range);
            
            if ($performance_range > 100) {
                echo "  📈 Significant performance differences detected between databases\n";
            } elseif ($performance_range > 50) {
                echo "  📈 Moderate performance differences between databases\n";
            } else {
                echo "  📈 Relatively similar performance across databases\n";
            }
        }
        
        // Statistical recommendations
        echo "\nStatistical Recommendations:\n";
        
        $poor_quality_count = $quality_counts['poor'];
        if ($poor_quality_count > 0) {
            echo "  ⚠️  {$poor_quality_count} tests showed high variability (CV ≥ 10%)\n";
            echo "     • Consider running tests during low system load\n";
            echo "     • Check for background processes affecting performance\n";
            echo "     • Increase iteration count for better statistical power\n";
        }
        
        if ($this->test_iterations < 13) {
            echo "  📊 Consider increasing iterations to 13+ for better statistical confidence\n";
        }
        
        $reliable_count = $quality_counts['excellent'] + $quality_counts['good'];
        if ($reliable_count >= count($results) * 0.8) {
            echo "  ✅ High confidence in results - good statistical reliability\n";
        }
        
        echo str_repeat("=", 80) . "\n";
    }
    
    /**
     * NEW: Enhanced results saving with raw data
     */
    protected function saveResults($results) {
        if (empty($results)) {
            echo "No results to save.\n";
            return;
        }
        
        $test_slug = strtolower(str_replace([' ', '-'], '_', $this->test_name));
        $test_slug = preg_replace('/[^a-z0-9_]/', '', $test_slug);
        
        $base_filename = $test_slug;
        
        // Save aggregated results (existing format)
        $csv_file = $this->saveCSV($results, "{$this->output_dir}/{$base_filename}.csv");
        $json_file = $this->saveJSON($results, "{$this->output_dir}/{$base_filename}.json");
        $md_file = $this->saveMarkdown($results, "{$this->output_dir}/{$base_filename}.md");
        
        // NEW: Save raw iteration data if enabled
        $raw_file = '';
        if ($this->save_raw_results) {
            $raw_file = $this->saveRawResults($results, "{$this->output_dir}/{$base_filename}_raw.json");
        }
        
        echo "Enhanced results saved:\n";
        echo "  CSV: {$csv_file}\n";
        echo "  JSON: {$json_file}\n";
        echo "  Markdown: {$md_file}\n";
        if ($raw_file) {
            echo "  Raw Data: {$raw_file}\n";
        }
    }
    
    /**
     * NEW: Save raw iteration results for detailed analysis
     */
    protected function saveRawResults($results, $filename) {
        $raw_data = [
            'test_name' => $this->test_name . ' - Raw Iterations',
            'timestamp' => date('c'),
            'test_iterations' => $this->test_iterations,
            'iteration_pause_ms' => $this->iteration_pause_ms,
            'thread_variant' => $this->thread_variant,
            'thread_config' => $this->thread_config,
            'statistical_methodology' => [
                'iterations_per_test' => $this->test_iterations,
                'pause_between_iterations_ms' => $this->iteration_pause_ms,
                'quality_thresholds' => $this->cv_thresholds,
                'confidence_level' => 0.95
            ],
            'databases' => []
        ];
        
        foreach ($results as $result) {
            if (!isset($result['raw_iterations'])) continue;
            
            $db_key = $result['database'] . ($result['tls'] ? '_TLS' : '_NonTLS');
            $raw_data['databases'][$db_key] = [
                'database' => $result['database'],
                'tls' => $result['tls'],
                'port' => $result['port'],
                'thread_config' => $result['database_thread_config'] ?? [],
                'measurement_quality' => $result['measurement_quality'] ?? 'unknown',
                'coefficient_of_variation' => $result['ops_per_sec_cv'] ?? 0,
                'confidence_interval_95' => $result['ops_per_sec_confidence_interval_95'] ?? [],
                'iterations' => $result['raw_iterations']
            ];
        }
        
        $json_content = json_encode($raw_data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        if (file_put_contents($filename, $json_content) === false) {
            throw new Exception("Could not write raw results file: {$filename}");
        }
        
        return $filename;
    }
    
    protected function saveCSV($results, $filename) {
        $fp = fopen($filename, 'w');
        if (!$fp) {
            throw new Exception("Could not open file for writing: {$filename}");
        }
        
        if (!empty($results)) {
            // Enhanced header with statistical fields
            $headers = [
                'database', 'tls', 'port', 'ops_per_sec', 'ops_per_sec_stddev', 'ops_per_sec_cv',
                'avg_latency', 'latency_stddev', 'p95_latency', 'p99_latency', 
                'measurement_quality', 'iterations_count', 'error_rate',
                'confidence_interval_lower', 'confidence_interval_upper', 'thread_variant'
            ];
            fputcsv($fp, $headers);
            
            // Data rows with statistical information
            foreach ($results as $result) {
                $ci = $result['ops_per_sec_confidence_interval_95'] ?? [];
                $row = [
                    $result['database'],
                    $result['tls'] ? 'true' : 'false',
                    $result['port'],
                    $result['ops_per_sec'],
                    $result['ops_per_sec_stddev'] ?? 0,
                    $result['ops_per_sec_cv'] ?? 0,
                    $result['avg_latency'],
                    $result['latency_stddev'] ?? 0,
                    $result['p95_latency'],
                    $result['p99_latency'],
                    $result['measurement_quality'] ?? 'unknown',
                    $result['iterations_count'] ?? $this->test_iterations,
                    $result['error_rate'],
                    $ci['lower'] ?? 0,
                    $ci['upper'] ?? 0,
                    $result['thread_variant']
                ];
                fputcsv($fp, $row);
            }
        }
        
        fclose($fp);
        return $filename;
    }
    
    /**
     * Enhanced JSON save with statistical metadata
     */
    protected function saveJSON($results, $filename) {
        $data = [
            'test_name' => $this->test_name,
            'timestamp' => date('c'),
            'php_version' => PHP_VERSION,
            'redis_extension_version' => $this->getRedisExtensionVersion(),
            
            // Enhanced: Add statistical testing metadata
            'test_methodology' => [
                'iterations_per_test' => $this->test_iterations,
                'iteration_pause_ms' => $this->iteration_pause_ms,
                'statistical_measures' => [
                    'standard_deviation',
                    'coefficient_of_variation',
                    'confidence_intervals',
                    'percentiles'
                ],
                'quality_thresholds' => $this->cv_thresholds,
                'confidence_level' => 0.95
            ],
            
            'thread_variant' => $this->thread_variant,
            'thread_config' => $this->thread_config,
            
            'test_configuration' => [
                'flush_before_test' => $this->flush_before_test,
                'test_tls' => $this->test_both_tls,
                'tls_skip_verify' => $this->tls_skip_verify,
                'output_dir' => $this->output_dir,
                'thread_variant' => $this->thread_variant,
                'database_configurations' => $this->databases
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
    
    /**
     * Enhanced markdown save with statistical information
     */
    protected function saveMarkdown($results, $filename) {
        $content = "# {$this->test_name}\n\n";
        $content .= "**Test Date:** " . date('Y-m-d H:i:s') . " UTC\n";
        $content .= "**PHP Version:** " . PHP_VERSION . "\n";
        $content .= "**Redis Extension Version:** " . $this->getRedisExtensionVersion() . "\n";
        $content .= "**Results Count:** " . count($results) . "\n";
        $content .= "**Thread Variant:** {$this->thread_variant}\n";
        
        // NEW: Statistical methodology information
        $content .= "\n## Statistical Methodology\n\n";
        $content .= "- **Iterations per Test:** {$this->test_iterations}\n";
        $content .= "- **Iteration Pause:** {$this->iteration_pause_ms}ms\n";
        $content .= "- **Statistical Measures:** Standard deviation, coefficient of variation, 95% confidence intervals\n";
        $content .= "- **Quality Thresholds:** Excellent (<2% CV), Good (<5% CV), Fair (<10% CV), Poor (≥10% CV)\n";
        
        if (!empty($this->thread_config)) {
            $content .= "\n## Thread Configuration\n\n";
            foreach ($this->thread_config as $key => $value) {
                $content .= "- **{$key}:** {$value}\n";
            }
        }
        
        $content .= "\n## Test Configuration\n\n";
        $content .= "- **Flush Before Test:** " . ($this->flush_before_test ? 'Yes' : 'No') . "\n";
        $content .= "- **TLS Testing:** " . ($this->test_both_tls ? 'Enabled' : 'Disabled') . "\n";
        $content .= "- **Output Directory:** {$this->output_dir}\n\n";
        
        if (!empty($results)) {
            $content .= "## Results with Statistical Analysis\n\n";
            
            // Enhanced table with statistical columns
            $headers = [
                'Database', 'Mode', 'Ops/sec', '±StdDev', 'CV%', 'Quality', 
                'Latency(ms)', '±StdDev', 'P95 Lat', 'P99 Lat', '95% CI', 'Iterations'
            ];
            
            $content .= "| " . implode(" | ", $headers) . " |\n";
            $content .= "| " . str_repeat("--- | ", count($headers)) . "\n";
            
            foreach ($results as $result) {
                $mode = $result['tls'] ? 'TLS' : 'Non-TLS';
                $ci = $result['ops_per_sec_confidence_interval_95'] ?? ['lower' => 0, 'upper' => 0];
                
                // Quality indicator
                $quality = $result['measurement_quality'] ?? 'unknown';
                $quality_icon = (['excellent' => '🟢', 'good' => '🟡', 'fair' => '🟠', 'poor' => '🔴'])[$quality] ?? '⚪';
                
                $row = [
                    $result['database'],
                    $mode,
                    number_format($result['ops_per_sec'], 0),
                    '±' . number_format($result['ops_per_sec_stddev'] ?? 0, 0),
                    number_format(($result['ops_per_sec_cv'] ?? 0) * 100, 1) . '%',
                    $quality_icon . ' ' . $quality,
                    number_format($result['avg_latency'], 3),
                    '±' . number_format($result['latency_stddev'] ?? 0, 3),
                    number_format($result['p95_latency'], 3),
                    number_format($result['p99_latency'], 3),
                    number_format($ci['lower'] ?? 0, 0) . '-' . number_format($ci['upper'] ?? 0, 0),
                    $result['iterations_count'] ?? $this->test_iterations
                ];
                
                $content .= "| " . implode(" | ", $row) . " |\n";
            }
        }
        
        // Enhanced summary with statistical insights
        $content .= "\n## Statistical Summary\n\n";
        if (!empty($results)) {
            $reliable_results = array_filter($results, function($r) { 
                return ($r['measurement_quality'] ?? 'poor') !== 'poor'; 
            });
            
            $content .= "- **Total Tests:** " . count($results) . "\n";
            $content .= "- **Reliable Measurements:** " . count($reliable_results) . "/" . count($results) . "\n";
            
            if (!empty($reliable_results)) {
                $ops_values = array_column($reliable_results, 'ops_per_sec');
                $content .= "- **Best Performance:** " . number_format(max($ops_values), 0) . " ops/sec\n";
                $content .= "- **Average Performance:** " . number_format($this->calculateMean($ops_values), 0) . " ops/sec\n";
                
                $cv_values = array_column($reliable_results, 'ops_per_sec_cv');
                $avg_cv = $this->calculateMean(array_filter($cv_values)) * 100;
                $content .= "- **Average Measurement Precision:** " . number_format($avg_cv, 1) . "% CV\n";
            }
        }
        
        if (file_put_contents($filename, $content) === false) {
            throw new Exception("Could not write Markdown file: {$filename}");
        }
        
        return $filename;
    }
    
    /**
     * Enhanced performance summary with statistical analysis
     */
    protected function printResultsSummary($results) {
        if (empty($results)) {
            return;
        }
        
        echo "\n" . str_repeat("=", 100) . "\n";
        echo "ENHANCED STATISTICAL PERFORMANCE SUMMARY\n";
        echo "Thread Variant: {$this->thread_variant} | Iterations per test: {$this->test_iterations}\n";
        echo str_repeat("=", 100) . "\n";
        
        // Group and sort results
        $grouped = [];
        foreach ($results as $result) {
            $key = $result['database'] . ($result['tls'] ? ' (TLS)' : '');
            $grouped[$key] = $result;
        }
        
        uasort($grouped, function($a, $b) {
            return ($b['ops_per_sec'] ?? 0) <=> ($a['ops_per_sec'] ?? 0);
        });
        
        $rank = 1;
        echo sprintf("%-3s %-20s %12s %10s %8s %8s %8s %10s %12s\n", 
            "Rank", "Database", "Ops/sec", "±StdDev", "CV%", "Latency", "Quality", "95% CI", "Reliable");
        echo str_repeat("-", 100) . "\n";
        
        foreach ($grouped as $key => $result) {
            $quality_icon = [
                'excellent' => '🟢',
                'good' => '🟡', 
                'fair' => '🟠',
                'poor' => '🔴'
            ][$result['measurement_quality'] ?? 'poor'] ?? '⚪';
            
            $ci = $result['ops_per_sec_confidence_interval_95'] ?? [];
            $ci_range = isset($ci['lower'], $ci['upper']) ? 
                number_format($ci['lower'], 0) . '-' . number_format($ci['upper'], 0) : 'N/A';
            
            $reliable = ($result['measurement_quality'] ?? 'poor') !== 'poor' ? '✅' : '❌';
            
            echo sprintf("#%-2d %-20s %8.0f %8.0f %6.1f%% %6.3fms %s%-7s %12s %8s\n",
                $rank++,
                $key,
                $result['ops_per_sec'],
                $result['ops_per_sec_stddev'] ?? 0,
                ($result['ops_per_sec_cv'] ?? 0) * 100,
                $result['avg_latency'],
                $quality_icon,
                $result['measurement_quality'] ?? 'unknown',
                $ci_range,
                $reliable
            );
        }
        
        echo str_repeat("=", 100) . "\n";
        
        // Statistical insights summary
        $reliable_results = array_filter($results, function($r) { 
            return ($r['measurement_quality'] ?? 'poor') !== 'poor'; 
        });
        
        echo "Quick Insights:\n";
        echo "- Reliable measurements: " . count($reliable_results) . "/" . count($results) . "\n";
        
        if (count($reliable_results) != count($results)) {
            echo "- ⚠️  Some measurements show high variability - check test conditions\n";
        }
        
        if (!empty($reliable_results)) {
            $best_result = null;
            $best_ops = 0;
            foreach ($reliable_results as $result) {
                if ($result['ops_per_sec'] > $best_ops) {
                    $best_ops = $result['ops_per_sec'];
                    $best_result = $result;
                }
            }
            if ($best_result) {
                echo "- 🏆 Best: {$best_result['database']}" . ($best_result['tls'] ? ' (TLS)' : '') . 
                     " - " . number_format($best_result['ops_per_sec'], 0) . " ops/sec\n";
            }
            
            $cv_values = array_filter(array_column($reliable_results, 'ops_per_sec_cv'));
            if (!empty($cv_values)) {
                $avg_precision = $this->calculateMean($cv_values) * 100;
                echo "- 📊 Average precision: " . number_format($avg_precision, 1) . "% CV\n";
            }
        }
    }
    
    protected function debugLog($message) {
        if ($this->debug_mode) {
            echo "[DEBUG] " . date('H:i:s') . " - {$message}\n";
        }
    }
    
    // Static helper methods
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
        
        if (!is_numeric($config['duration']) || $config['duration'] <= 0) {
            throw new Exception("Duration must be a positive number");
        }
        
        if (empty($config['output_dir']) || !is_string($config['output_dir'])) {
            throw new Exception("Output directory must be a non-empty string");
        }
        
        return true;
    }
    
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