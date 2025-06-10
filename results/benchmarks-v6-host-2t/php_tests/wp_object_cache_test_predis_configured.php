<?php
/**
 * Configured WordPress Object Cache Test Runner for Predis
 * 
 * This script runs the WordPress object cache tests using the Predis Redis client
 * with configuration loaded from a PHP config file.
 * 
 * Usage:
 *   php wp_object_cache_test_predis_configured.php [config_file]
 * 
 * If no config file is provided, it will look for test_config_predis.php
 */

require_once 'wp_object_cache_test_predis.php';

function main() {
    global $argv;
    
    echo "WordPress Object Cache Test with Predis - Configured Runner\n";
    echo "============================================================\n";
    echo "Implementation: Predis (Pure PHP Redis Client)\n";
    echo "Enhanced TLS Support: Yes\n";
    echo "Statistical Analysis: 5 iterations with confidence intervals\n\n";
    
    // Determine config file
    $config_file = isset($argv[1]) ? $argv[1] : 'test_config_predis.php';
    
    if (!file_exists($config_file)) {
        echo "❌ Configuration file not found: {$config_file}\n";
        echo "\nUsage: php wp_object_cache_test_predis_configured.php [config_file]\n";
        echo "\nExpected config file format:\n";
        echo "<?php\n";
        echo "return [\n";
        echo "    'duration' => 10,\n";
        echo "    'test_iterations' => 5,\n";
        echo "    'output_dir' => './results',\n";
        echo "    'implementation' => 'predis',\n";
        echo "    // ... other configuration options\n";
        echo "];\n";
        exit(1);
    }
    
    echo "📋 Loading configuration from: {$config_file}\n";
    
    try {
        $config = require $config_file;
        
        if (!is_array($config)) {
            throw new Exception("Configuration file must return an array");
        }
        
        // Ensure we're using Predis implementation
        $config['implementation'] = 'predis';
        
        // Validate required configuration
        $required_keys = ['duration', 'output_dir'];
        foreach ($required_keys as $key) {
            if (!isset($config[$key])) {
                throw new Exception("Missing required configuration key: {$key}");
            }
        }
        
        echo "✅ Configuration loaded successfully\n\n";
        
        // Display key configuration parameters
        echo "📊 Test Configuration:\n";
        echo "  Implementation: Predis (Pure PHP)\n";
        echo "  Duration per iteration: {$config['duration']}s\n";
        echo "  Test iterations: " . ($config['test_iterations'] ?? 5) . "\n";
        echo "  Output directory: {$config['output_dir']}\n";
        echo "  TLS testing: " . (($config['test_tls'] ?? true) ? 'Enabled' : 'Disabled') . "\n";
        echo "  Flush before test: " . (($config['flush_before_test'] ?? false) ? 'Yes' : 'No') . "\n";
        echo "  Thread variant: " . ($config['thread_variant'] ?? 'unknown') . "\n";
        
        // Predis-specific configuration
        echo "  Connection timeout: " . ($config['connection_timeout'] ?? 5.0) . "s\n";
        echo "  Read/write timeout: " . ($config['read_write_timeout'] ?? 5.0) . "s\n";
        echo "  Connection retries: " . ($config['connection_retry_attempts'] ?? 3) . "\n";
        echo "  Persistent connections: " . (($config['persistent_connections'] ?? false) ? 'Yes' : 'No') . "\n";
        
        if (!empty($config['thread_config'])) {
            echo "  Thread configuration:\n";
            foreach ($config['thread_config'] as $db => $threads) {
                echo "    {$db}: {$threads} threads\n";
            }
        }
        
        if (!empty($config['databases'])) {
            echo "  Database configurations:\n";
            foreach ($config['databases'] as $db_name => $db_config) {
                $thread_info = [];
                if (isset($db_config['io_threads'])) $thread_info[] = "IO threads: {$db_config['io_threads']}";
                if (isset($db_config['server_threads'])) $thread_info[] = "Server threads: {$db_config['server_threads']}";
                if (isset($db_config['proactor_threads'])) $thread_info[] = "Proactor threads: {$db_config['proactor_threads']}";
                
                $thread_str = !empty($thread_info) ? ' (' . implode(', ', $thread_info) . ')' : '';
                echo "    {$db_name}: {$db_config['host']}:{$db_config['port']}" . 
                     (isset($db_config['tls_port']) ? " (TLS: {$db_config['tls_port']})" : "") . 
                     $thread_str . "\n";
            }
        }
        
        echo "\n" . str_repeat("=", 70) . "\n\n";
        
        // Verify Predis availability
        echo "🔍 Checking Predis availability...\n";
        if (!class_exists('Predis\Client')) {
            echo "❌ Predis library not found!\n";
            echo "Install with: composer require predis/predis\n";
            echo "Current working directory: " . getcwd() . "\n";
            echo "Composer autoload path: " . __DIR__ . '/vendor/autoload.php' . "\n";
            exit(1);
        }
        echo "✅ Predis library available\n\n";
        
        // Initialize and run the test
        echo "🚀 Starting Predis WordPress Object Cache Test...\n\n";
        
        $test = new WordPressObjectCacheTestPredis($config);
        $test->run();
        
        echo "\n" . str_repeat("=", 70) . "\n";
        echo "✅ Predis WordPress Object Cache test completed successfully!\n";
        echo "📁 Results saved to: {$config['output_dir']}\n";
        echo "📊 Implementation: Predis (Pure PHP Redis Client)\n";
        echo "🔒 TLS Support: Enhanced reliability compared to phpredis\n";
        
        // Display result files
        if (is_dir($config['output_dir'])) {
            echo "\n📄 Generated files:\n";
            $files = glob($config['output_dir'] . '/*predis*');
            foreach ($files as $file) {
                $size = filesize($file);
                $size_str = $size > 1024 ? round($size/1024, 1) . 'KB' : $size . 'B';
                echo "  " . basename($file) . " ({$size_str})\n";
            }
        }
        
    } catch (Exception $e) {
        echo "\n❌ Test failed: " . $e->getMessage() . "\n";
        
        // Enhanced error information for debugging
        echo "\n🔍 Debug Information:\n";
        echo "  PHP Version: " . PHP_VERSION . "\n";
        echo "  Working Directory: " . getcwd() . "\n";
        echo "  Config File: " . realpath($config_file) . "\n";
        echo "  Predis Available: " . (class_exists('Predis\Client') ? 'Yes' : 'No') . "\n";
        
        if (isset($config)) {
            echo "  Output Directory: " . ($config['output_dir'] ?? 'not set') . "\n";
            echo "  Output Dir Exists: " . (isset($config['output_dir']) && is_dir($config['output_dir']) ? 'Yes' : 'No') . "\n";
            echo "  Output Dir Writable: " . (isset($config['output_dir']) && is_writable(dirname($config['output_dir'])) ? 'Yes' : 'No') . "\n";
        }
        
        echo "\n📋 Stack Trace:\n";
        echo $e->getTraceAsString() . "\n";
        
        exit(1);
    }
}

// Helper function to create a sample config file
function createSampleConfig($filename = 'test_config_predis_sample.php') {
    $sample_config = '<?php
/**
 * Sample Predis Configuration for WordPress Object Cache Test
 */
return [
    // Test execution parameters
    \'duration\' => 30,                    // Duration per iteration in seconds
    \'test_iterations\' => 5,             // Number of iterations for statistical analysis
    \'iteration_pause_ms\' => 500,         // Pause between iterations
    \'save_raw_results\' => true,          // Save detailed iteration data
    
    // Output configuration
    \'output_dir\' => \'./predis_benchmark_results\',
    
    // Redis implementation
    \'implementation\' => \'predis\',
    
    // TLS configuration
    \'test_tls\' => true,                  // Test both TLS and non-TLS
    \'tls_skip_verify\' => true,           // Skip certificate verification for self-signed certs
    
    // Test behavior
    \'flush_before_test\' => true,         // Clear database before testing
    \'debug\' => false,                    // Enable debug output
    
    // WordPress test specific
    \'operations\' => 100000,              // Target operations per iteration
    \'read_write_ratio\' => 70,            // 70% reads, 30% writes
    
    // Thread configuration (example)
    \'thread_variant\' => \'4t\',
    \'thread_config\' => [
        \'redis_io_threads\' => 4,
        \'keydb_server_threads\' => 4,
        \'dragonfly_proactor_threads\' => 4,
        \'valkey_io_threads\' => 4
    ],
    
    // Predis-specific configuration
    \'connection_timeout\' => 5.0,         // Connection timeout in seconds
    \'read_write_timeout\' => 5.0,         // Read/write timeout in seconds
    \'tcp_keepalive\' => true,             // Enable TCP keepalive
    \'persistent_connections\' => false,   // Use persistent connections
    \'connection_retry_attempts\' => 3,    // Number of connection retry attempts
    \'connection_retry_delay\' => 1000,    // Delay between retries in milliseconds
    
    // Database configurations
    \'databases\' => [
        \'Redis\' => [
            \'host\' => \'127.0.0.1\',
            \'port\' => 6379,
            \'tls_port\' => 6390,
            \'io_threads\' => 4
        ],
        \'KeyDB\' => [
            \'host\' => \'127.0.0.1\',
            \'port\' => 6380,
            \'tls_port\' => 6391,
            \'server_threads\' => 4
        ],
        \'Dragonfly\' => [
            \'host\' => \'127.0.0.1\',
            \'port\' => 6381,
            \'tls_port\' => 6392,
            \'proactor_threads\' => 4
        ],
        \'Valkey\' => [
            \'host\' => \'127.0.0.1\',
            \'port\' => 6382,
            \'tls_port\' => 6393,
            \'io_threads\' => 4
        ]
    ]
];
';
    
    if (file_put_contents($filename, $sample_config)) {
        echo "📄 Sample configuration created: {$filename}\n";
        return true;
    } else {
        echo "❌ Failed to create sample configuration file\n";
        return false;
    }
}

// Command line argument handling
if (isset($argv[1]) && $argv[1] === '--create-sample') {
    echo "Creating sample Predis configuration file...\n";
    createSampleConfig();
    exit(0);
}

if (isset($argv[1]) && in_array($argv[1], ['--help', '-h'])) {
    echo "WordPress Object Cache Test with Predis - Help\n";
    echo "==============================================\n\n";
    echo "Usage:\n";
    echo "  php wp_object_cache_test_predis_configured.php [config_file]\n";
    echo "  php wp_object_cache_test_predis_configured.php --create-sample\n";
    echo "  php wp_object_cache_test_predis_configured.php --help\n\n";
    echo "Options:\n";
    echo "  config_file       Path to PHP configuration file (default: test_config_predis.php)\n";
    echo "  --create-sample   Create a sample configuration file\n";
    echo "  --help, -h        Show this help message\n\n";
    echo "Features:\n";
    echo "  - Enhanced TLS support with Predis\n";
    echo "  - Statistical analysis with 5 iterations\n";
    echo "  - WordPress-realistic cache operations\n";
    echo "  - Connection retry logic and error recovery\n";
    echo "  - Comprehensive performance reporting\n\n";
    echo "Requirements:\n";
    echo "  - PHP 8.1+\n";
    echo "  - Predis library (composer require predis/predis)\n";
    echo "  - Redis/KeyDB/Dragonfly/Valkey servers running\n";
    exit(0);
}

// Run the main function
main();
?>