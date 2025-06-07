<?php
/**
 * WordPress Object Cache Test - Configured Runner
 * 
 * This file loads configuration from test_config.php and runs the enhanced
 * WordPress Object Cache Test with 5-run statistical analysis.
 * 
 * Features:
 * - Loads configuration from external file or uses defaults
 * - Runs enhanced multi-iteration testing
 * - Provides detailed configuration validation
 * - Enhanced error handling and reporting
 */

// Ensure we're running from command line
if (php_sapi_name() !== 'cli') {
    die("This script must be run from the command line.\n");
}

// Include required classes
require_once __DIR__ . '/RedisTestBase.php';
require_once __DIR__ . '/wp_object_cache_test.php';

/**
 * Enhanced configuration loader with validation and defaults
 */
function loadTestConfiguration() {
    $config_file = __DIR__ . '/test_config.php';
    
    // Default configuration
    $default_config = [
        'duration' => 30,
        'test_iterations' => 5,
        'iteration_pause_ms' => 500,
        'save_raw_results' => true,
        'output_dir' => './php_benchmark_results',
        'test_tls' => true,
        'flush_before_test' => true,
        'debug' => false,
        'operations' => 100000,
        'read_write_ratio' => 70,
        'thread_variant' => 'unknown',
        'thread_config' => [],
        'databases' => [
            'Redis' => ['host' => '127.0.0.1', 'port' => 6379, 'tls_port' => 6390],
            'KeyDB' => ['host' => '127.0.0.1', 'port' => 6380, 'tls_port' => 6391],
            'Dragonfly' => ['host' => '127.0.0.1', 'port' => 6381, 'tls_port' => 6392],
            'Valkey' => ['host' => '127.0.0.1', 'port' => 6382, 'tls_port' => 6393]
        ]
    ];
    
    // Load configuration from file if it exists
    if (file_exists($config_file)) {
        echo "Loading configuration from test_config.php...\n";
        try {
            $loaded_config = include $config_file;
            
            if (!is_array($loaded_config)) {
                throw new Exception("Configuration file must return an array");
            }
            
            // Merge with defaults (loaded config takes precedence)
            $config = array_merge($default_config, $loaded_config);
            echo "✅ Configuration loaded successfully from file\n";
            
        } catch (Exception $e) {
            echo "⚠️  Error loading configuration file: " . $e->getMessage() . "\n";
            echo "Using default configuration...\n";
            $config = $default_config;
        }
    } else {
        echo "Configuration file not found, using defaults...\n";
        $config = $default_config;
    }
    
    return $config;
}

/**
 * Validate configuration parameters
 */
function validateConfiguration($config) {
    $errors = [];
    
    // Validate required parameters
    if (!is_numeric($config['duration']) || $config['duration'] <= 0) {
        $errors[] = "Duration must be a positive number";
    }
    
    if (!is_numeric($config['test_iterations']) || $config['test_iterations'] < 1) {
        $errors[] = "Test iterations must be >= 1";
    }
    
    if (!is_numeric($config['operations']) || $config['operations'] <= 0) {
        $errors[] = "Operations must be a positive number";
    }
    
    if (!is_numeric($config['read_write_ratio']) || $config['read_write_ratio'] < 0 || $config['read_write_ratio'] > 100) {
        $errors[] = "Read/write ratio must be between 0 and 100";
    }
    
    if (empty($config['output_dir'])) {
        $errors[] = "Output directory cannot be empty";
    }
    
    if (!is_array($config['databases']) || empty($config['databases'])) {
        $errors[] = "Databases configuration must be a non-empty array";
    }
    
    // Validate database configurations
    foreach ($config['databases'] as $db_name => $db_config) {
        if (!isset($db_config['host']) || !isset($db_config['port'])) {
            $errors[] = "Database {$db_name} must have host and port configured";
        }
        
        if ($config['test_tls'] && !isset($db_config['tls_port'])) {
            $errors[] = "Database {$db_name} must have tls_port configured when TLS testing is enabled";
        }
    }
    
    if (!empty($errors)) {
        throw new Exception("Configuration validation failed:\n- " . implode("\n- ", $errors));
    }
    
    return true;
}

/**
 * Display configuration summary
 */
function displayConfigurationSummary($config) {
    echo "\n" . str_repeat("=", 60) . "\n";
    echo "ENHANCED WORDPRESS OBJECT CACHE TEST CONFIGURATION\n";
    echo str_repeat("=", 60) . "\n";
    
    echo "Test Parameters:\n";
    echo "  Duration per iteration: {$config['duration']} seconds\n";
    echo "  Test iterations: {$config['test_iterations']}\n";
    echo "  Iteration pause: {$config['iteration_pause_ms']}ms\n";
    echo "  Operations per iteration: " . number_format($config['operations']) . "\n";
    echo "  Read/Write ratio: {$config['read_write_ratio']}% / " . (100 - $config['read_write_ratio']) . "%\n";
    
    echo "\nStatistical Analysis:\n";
    echo "  Multi-run testing: Enabled\n";
    echo "  Raw data logging: " . ($config['save_raw_results'] ? 'Enabled' : 'Disabled') . "\n";
    echo "  Quality assessment: Enabled (CV-based)\n";
    echo "  Confidence intervals: 95%\n";
    
    echo "\nThread Configuration:\n";
    echo "  Thread variant: {$config['thread_variant']}\n";
    if (!empty($config['thread_config'])) {
        foreach ($config['thread_config'] as $db => $threads) {
            echo "  {$db}: {$threads} threads\n";
        }
    }
    
    echo "\nDatabase Configuration:\n";
    foreach ($config['databases'] as $db_name => $db_config) {
        echo "  {$db_name}: {$db_config['host']}:{$db_config['port']}";
        if ($config['test_tls'] && isset($db_config['tls_port'])) {
            echo " (TLS: {$db_config['tls_port']})";
        }
        
        // Show thread-specific config
        $thread_info = [];
        if (isset($db_config['io_threads'])) {
            $thread_info[] = "IO: {$db_config['io_threads']}";
        }
        if (isset($db_config['server_threads'])) {
            $thread_info[] = "Server: {$db_config['server_threads']}";
        }
        if (isset($db_config['proactor_threads'])) {
            $thread_info[] = "Proactor: {$db_config['proactor_threads']}";
        }
        
        if (!empty($thread_info)) {
            echo " [" . implode(", ", $thread_info) . "]";
        }
        echo "\n";
    }
    
    echo "\nTest Environment:\n";
    echo "  PHP version: " . PHP_VERSION . "\n";
    echo "  Redis extension: " . (extension_loaded('redis') ? 'Loaded' : 'NOT LOADED') . "\n";
    if (extension_loaded('redis')) {
        $reflection = new ReflectionExtension('redis');
        echo "  Redis extension version: " . $reflection->getVersion() . "\n";
    }
    echo "  Output directory: {$config['output_dir']}\n";
    echo "  TLS testing: " . ($config['test_tls'] ? 'Enabled' : 'Disabled') . "\n";
    echo "  Database flush: " . ($config['flush_before_test'] ? 'Enabled' : 'Disabled') . "\n";
    echo "  Debug mode: " . ($config['debug'] ? 'Enabled' : 'Disabled') . "\n";
    
    echo str_repeat("=", 60) . "\n\n";
}

/**
 * Check system requirements
 */
function checkSystemRequirements() {
    $requirements_met = true;
    
    echo "Checking system requirements...\n";
    
    // Check PHP version
    if (version_compare(PHP_VERSION, '7.4.0', '<')) {
        echo "❌ PHP 7.4+ required, found: " . PHP_VERSION . "\n";
        $requirements_met = false;
    } else {
        echo "✅ PHP version: " . PHP_VERSION . "\n";
    }
    
    // Check Redis extension
    if (!extension_loaded('redis')) {
        echo "❌ Redis PHP extension not loaded\n";
        echo "   Install with: pecl install redis\n";
        $requirements_met = false;
    } else {
        $reflection = new ReflectionExtension('redis');
        echo "✅ Redis extension version: " . $reflection->getVersion() . "\n";
    }
    
    // Check required functions
    $required_functions = ['json_encode', 'json_decode', 'serialize', 'unserialize'];
    foreach ($required_functions as $func) {
        if (!function_exists($func)) {
            echo "❌ Required function missing: {$func}\n";
            $requirements_met = false;
        }
    }
    
    if ($requirements_met) {
        echo "✅ All system requirements met\n\n";
    } else {
        echo "\n❌ System requirements not met. Please install missing components.\n";
        exit(1);
    }
    
    return true;
}

/**
 * Main execution function
 */
function main() {
    try {
        echo "Enhanced WordPress Object Cache Test - Statistical Analysis\n";
        echo "=========================================================\n\n";
        
        // Check system requirements
        checkSystemRequirements();
        
        // Load and validate configuration
        $config = loadTestConfiguration();
        validateConfiguration($config);
        
        // Display configuration summary
        displayConfigurationSummary($config);
        
        // Verify Redis extension is available
        if (!RedisTestBase::checkRedisExtension()['loaded']) {
            throw new Exception("Redis extension check failed");
        }
        
        // Create and run the test
        echo "Initializing WordPress Object Cache Test...\n\n";
        $test = new WordPressObjectCacheTest($config);
        
        // Run the enhanced test suite
        $start_time = microtime(true);
        $test->run();
        $total_time = microtime(true) - $start_time;
        
        // Final summary
        echo "\n" . str_repeat("=", 60) . "\n";
        echo "TEST SUITE COMPLETED SUCCESSFULLY!\n";
        echo str_repeat("=", 60) . "\n";
        echo "Total execution time: " . number_format($total_time, 2) . " seconds\n";
        echo "Statistical iterations per database: {$config['test_iterations']}\n";
        echo "Results saved to: {$config['output_dir']}\n";
        
        // Show generated files
        $output_dir = $config['output_dir'];
        if (is_dir($output_dir)) {
            $json_files = glob("{$output_dir}/*.json");
            $csv_files = glob("{$output_dir}/*.csv");
            $md_files = glob("{$output_dir}/*.md");
            
            echo "\nGenerated files:\n";
            echo "  JSON results: " . count($json_files) . " files\n";
            echo "  CSV exports: " . count($csv_files) . " files\n";
            echo "  Markdown reports: " . count($md_files) . " files\n";
            
            if (!empty($json_files)) {
                echo "  📊 Raw data: " . (file_exists("{$output_dir}/wordpress_object_cache_test_raw.json") ? "Available" : "Not saved") . "\n";
            }
        }
        
        echo "\n🎉 Enhanced benchmarking with statistical analysis complete!\n";
        echo "📈 Results include confidence intervals and measurement quality indicators\n";
        echo "📊 Use the enhanced chart generator to visualize statistical analysis\n\n";
        
    } catch (Exception $e) {
        echo "\n❌ ERROR: " . $e->getMessage() . "\n";
        echo "\nStack trace:\n";
        echo $e->getTraceAsString() . "\n";
        exit(1);
    }
}

// Run the main function
if (__FILE__ === realpath($_SERVER['SCRIPT_FILENAME'])) {
    main();
}
?>