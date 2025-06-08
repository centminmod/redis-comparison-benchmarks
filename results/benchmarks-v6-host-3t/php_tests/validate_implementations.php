<?php
/**
 * Redis Implementation Validation Script
 * 
 * This script validates both phpredis and Predis implementations to ensure
 * feature parity and identify any differences in behavior.
 */

// Include both implementations
require_once 'RedisTestBase.php';
require_once 'RedisTestBase-predis.php';

class RedisImplementationValidator {
    private $test_host = '127.0.0.1';
    private $test_port = 6379;
    private $test_tls_port = 6390;
    private $debug = true;
    
    public function __construct($debug = true) {
        $this->debug = $debug;
    }
    
    public function validateImplementations() {
        echo "Redis Implementation Validation\n";
        echo "================================\n\n";
        
        $results = [
            'phpredis' => [],
            'predis' => [],
            'comparison' => []
        ];
        
        // Test phpredis availability
        echo "1. Testing phpredis availability...\n";
        $results['phpredis'] = $this->testPhpRedis();
        
        // Test Predis availability
        echo "\n2. Testing Predis availability...\n";
        $results['predis'] = $this->testPredis();
        
        // Connection tests
        echo "\n3. Testing connections...\n";
        $this->testConnections($results);
        
        // Feature parity tests
        echo "\n4. Testing feature parity...\n";
        $this->testFeatureParity($results);
        
        // TLS reliability comparison
        echo "\n5. Testing TLS reliability...\n";
        $this->testTlsReliability($results);
        
        // Performance comparison
        echo "\n6. Quick performance comparison...\n";
        $this->testPerformanceComparison($results);
        
        // Generate report
        echo "\n7. Generating validation report...\n";
        $this->generateReport($results);
        
        return $results;
    }
    
    private function testPhpRedis() {
        $result = [
            'available' => false,
            'version' => 'unknown',
            'connection_test' => false,
            'tls_support' => false,
            'errors' => []
        ];
        
        try {
            if (!extension_loaded('redis')) {
                $result['errors'][] = 'phpredis extension not loaded';
                echo "  ❌ phpredis extension not available\n";
                return $result;
            }
            
            $result['available'] = true;
            
            // Get version
            try {
                $reflection = new ReflectionExtension('redis');
                $result['version'] = $reflection->getVersion();
                echo "  ✅ phpredis extension available (version: {$result['version']})\n";
            } catch (Exception $e) {
                $result['version'] = 'unknown';
                echo "  ⚠️ phpredis available but version unknown\n";
            }
            
            // Test basic connection
            try {
                $redis = new Redis();
                $connected = $redis->connect($this->test_host, $this->test_port, 2.0);
                if ($connected) {
                    $ping = $redis->ping();
                    if (in_array($ping, ['+PONG', 'PONG', true, 1], true)) {
                        $result['connection_test'] = true;
                        echo "  ✅ phpredis basic connection successful\n";
                    } else {
                        $result['errors'][] = "PING failed: " . var_export($ping, true);
                        echo "  ❌ phpredis PING failed\n";
                    }
                    $redis->close();
                } else {
                    $result['errors'][] = 'Connection failed';
                    echo "  ❌ phpredis connection failed\n";
                }
            } catch (Exception $e) {
                $result['errors'][] = 'Connection exception: ' . $e->getMessage();
                echo "  ❌ phpredis connection exception: " . $e->getMessage() . "\n";
            }
            
            // Test TLS support
            try {
                $redis = new Redis();
                $ssl_context = [
                    'verify_peer' => false,
                    'verify_peer_name' => false,
                    'allow_self_signed' => true
                ];
                
                $connected = @$redis->connect($this->test_host, $this->test_tls_port, 2.0, null, 0, 0, $ssl_context);
                if ($connected) {
                    $result['tls_support'] = true;
                    echo "  ✅ phpredis TLS connection possible\n";
                    $redis->close();
                } else {
                    echo "  ⚠️ phpredis TLS connection failed (expected if no TLS server)\n";
                }
            } catch (Exception $e) {
                echo "  ⚠️ phpredis TLS test exception: " . $e->getMessage() . "\n";
            }
            
        } catch (Exception $e) {
            $result['errors'][] = 'General exception: ' . $e->getMessage();
            echo "  ❌ phpredis test failed: " . $e->getMessage() . "\n";
        }
        
        return $result;
    }
    
    private function testPredis() {
        $result = [
            'available' => false,
            'version' => 'unknown',
            'connection_test' => false,
            'tls_support' => false,
            'errors' => []
        ];
        
        try {
            if (!class_exists('Predis\Client')) {
                $result['errors'][] = 'Predis library not available';
                echo "  ❌ Predis library not available\n";
                echo "  💡 Install with: composer require predis/predis\n";
                return $result;
            }
            
            $result['available'] = true;
            
            // Get version (attempt to read from composer)
            try {
                $reflection = new ReflectionClass('Predis\Client');
                $composer_file = dirname($reflection->getFileName()) . '/../composer.json';
                if (file_exists($composer_file)) {
                    $composer_data = json_decode(file_get_contents($composer_file), true);
                    $result['version'] = $composer_data['version'] ?? 'unknown';
                }
                echo "  ✅ Predis library available (version: {$result['version']})\n";
            } catch (Exception $e) {
                $result['version'] = 'unknown';
                echo "  ✅ Predis library available (version unknown)\n";
            }
            
            // Test basic connection
            try {
                $redis = new Predis\Client([
                    'scheme' => 'tcp',
                    'host' => $this->test_host,
                    'port' => $this->test_port,
                    'timeout' => 2.0
                ]);
                
                $ping = $redis->ping();
                if ($ping === 'PONG' || $ping === '+PONG' || $ping === true) {
                    $result['connection_test'] = true;
                    echo "  ✅ Predis basic connection successful\n";
                } else {
                    $result['errors'][] = "PING failed: " . var_export($ping, true);
                    echo "  ❌ Predis PING failed\n";
                }
            } catch (Exception $e) {
                $result['errors'][] = 'Connection exception: ' . $e->getMessage();
                echo "  ❌ Predis connection exception: " . $e->getMessage() . "\n";
            }
            
            // Test TLS support
            try {
                $redis = new Predis\Client([
                    'scheme' => 'tls',
                    'host' => $this->test_host,
                    'port' => $this->test_tls_port,
                    'timeout' => 2.0,
                    'ssl' => [
                        'verify_peer' => false,
                        'verify_peer_name' => false,
                        'allow_self_signed' => true
                    ]
                ]);
                
                $ping = $redis->ping();
                if ($ping === 'PONG' || $ping === '+PONG' || $ping === true) {
                    $result['tls_support'] = true;
                    echo "  ✅ Predis TLS connection successful\n";
                } else {
                    echo "  ⚠️ Predis TLS connection failed (expected if no TLS server)\n";
                }
            } catch (Exception $e) {
                echo "  ⚠️ Predis TLS test exception: " . $e->getMessage() . "\n";
            }
            
        } catch (Exception $e) {
            $result['errors'][] = 'General exception: ' . $e->getMessage();
            echo "  ❌ Predis test failed: " . $e->getMessage() . "\n";
        }
        
        return $result;
    }
    
    private function testConnections(&$results) {
        if (!$results['phpredis']['available'] && !$results['predis']['available']) {
            echo "  ❌ Neither implementation available for connection testing\n";
            return;
        }
        
        echo "  Testing concurrent connections...\n";
        
        // Test multiple connections
        $connection_tests = [
            'simultaneous' => 'Multiple simultaneous connections',
            'sequential' => 'Sequential connection/disconnection',
            'rapid' => 'Rapid connection cycling'
        ];
        
        foreach ($connection_tests as $test_type => $description) {
            echo "    {$description}:\n";
            
            if ($results['phpredis']['available']) {
                $phpredis_result = $this->testConnectionPattern($test_type, 'phpredis');
                echo "      phpredis: " . ($phpredis_result ? '✅' : '❌') . "\n";
            }
            
            if ($results['predis']['available']) {
                $predis_result = $this->testConnectionPattern($test_type, 'predis');
                echo "      Predis: " . ($predis_result ? '✅' : '❌') . "\n";
            }
        }
    }
    
    private function testConnectionPattern($pattern, $implementation) {
        try {
            switch ($pattern) {
                case 'simultaneous':
                    return $this->testSimultaneousConnections($implementation);
                case 'sequential':
                    return $this->testSequentialConnections($implementation);
                case 'rapid':
                    return $this->testRapidConnections($implementation);
                default:
                    return false;
            }
        } catch (Exception $e) {
            if ($this->debug) {
                echo "        Exception: " . $e->getMessage() . "\n";
            }
            return false;
        }
    }
    
    private function testSimultaneousConnections($implementation) {
        $connections = [];
        $success_count = 0;
        
        // Create 5 simultaneous connections
        for ($i = 0; $i < 5; $i++) {
            if ($implementation === 'phpredis') {
                $redis = new Redis();
                if ($redis->connect($this->test_host, $this->test_port, 1.0)) {
                    $connections[] = $redis;
                    $success_count++;
                }
            } else {
                $redis = new Predis\Client([
                    'scheme' => 'tcp',
                    'host' => $this->test_host,
                    'port' => $this->test_port,
                    'timeout' => 1.0
                ]);
                $redis->ping(); // Test connection
                $connections[] = $redis;
                $success_count++;
            }
        }
        
        // Close connections
        if ($implementation === 'phpredis') {
            foreach ($connections as $redis) {
                $redis->close();
            }
        }
        
        return $success_count >= 4; // Allow for 1 failure
    }
    
    private function testSequentialConnections($implementation) {
        $success_count = 0;
        
        for ($i = 0; $i < 10; $i++) {
            if ($implementation === 'phpredis') {
                $redis = new Redis();
                if ($redis->connect($this->test_host, $this->test_port, 1.0)) {
                    $redis->ping();
                    $redis->close();
                    $success_count++;
                }
            } else {
                $redis = new Predis\Client([
                    'scheme' => 'tcp',
                    'host' => $this->test_host,
                    'port' => $this->test_port,
                    'timeout' => 1.0
                ]);
                $redis->ping();
                $success_count++;
            }
        }
        
        return $success_count >= 8; // Allow for 2 failures
    }
    
    private function testRapidConnections($implementation) {
        $start_time = microtime(true);
        $success_count = 0;
        $target_time = 2.0; // 2 seconds
        
        while ((microtime(true) - $start_time) < $target_time) {
            try {
                if ($implementation === 'phpredis') {
                    $redis = new Redis();
                    if ($redis->connect($this->test_host, $this->test_port, 0.5)) {
                        $redis->ping();
                        $redis->close();
                        $success_count++;
                    }
                } else {
                    $redis = new Predis\Client([
                        'scheme' => 'tcp',
                        'host' => $this->test_host,
                        'port' => $this->test_port,
                        'timeout' => 0.5
                    ]);
                    $redis->ping();
                    $success_count++;
                }
            } catch (Exception $e) {
                // Ignore rapid connection failures
            }
        }
        
        return $success_count > 10; // Minimum connections in 2 seconds
    }
    
    private function testFeatureParity(&$results) {
        $features = [
            'basic_operations' => 'SET/GET/DEL operations',
            'expiration' => 'SETEX/TTL operations',
            'hash_operations' => 'HSET/HGET operations',
            'list_operations' => 'LPUSH/LPOP operations',
            'pipeline' => 'Pipeline operations'
        ];
        
        foreach ($features as $feature => $description) {
            echo "    {$description}:\n";
            
            if ($results['phpredis']['available'] && $results['phpredis']['connection_test']) {
                $phpredis_result = $this->testFeature($feature, 'phpredis');
                echo "      phpredis: " . ($phpredis_result ? '✅' : '❌') . "\n";
            }
            
            if ($results['predis']['available'] && $results['predis']['connection_test']) {
                $predis_result = $this->testFeature($feature, 'predis');
                echo "      Predis: " . ($predis_result ? '✅' : '❌') . "\n";
            }
        }
    }
    
    private function testFeature($feature, $implementation) {
        try {
            if ($implementation === 'phpredis') {
                $redis = new Redis();
                $redis->connect($this->test_host, $this->test_port, 2.0);
            } else {
                $redis = new Predis\Client([
                    'scheme' => 'tcp',
                    'host' => $this->test_host,
                    'port' => $this->test_port,
                    'timeout' => 2.0
                ]);
            }
            
            $test_key = "test_{$feature}_" . uniqid();
            $success = false;
            
            switch ($feature) {
                case 'basic_operations':
                    $redis->set($test_key, 'test_value');
                    $result = $redis->get($test_key);
                    $redis->del($test_key);
                    $success = ($result === 'test_value');
                    break;
                    
                case 'expiration':
                    $redis->setex($test_key, 1, 'expiring_value');
                    $ttl = $redis->ttl($test_key);
                    $redis->del($test_key);
                    $success = ($ttl > 0);
                    break;
                    
                case 'hash_operations':
                    $redis->hset($test_key, 'field1', 'value1');
                    $result = $redis->hget($test_key, 'field1');
                    $redis->del($test_key);
                    $success = ($result === 'value1');
                    break;
                    
                case 'list_operations':
                    $redis->lpush($test_key, 'item1');
                    $result = $redis->lpop($test_key);
                    $success = ($result === 'item1');
                    break;
                    
                case 'pipeline':
                    if ($implementation === 'phpredis') {
                        $pipe = $redis->pipeline();
                        $pipe->set($test_key . '_1', 'value1');
                        $pipe->set($test_key . '_2', 'value2');
                        $results = $pipe->exec();
                        $redis->del([$test_key . '_1', $test_key . '_2']);
                        $success = (count($results) === 2);
                    } else {
                        $pipe = $redis->pipeline();
                        $pipe->set($test_key . '_1', 'value1');
                        $pipe->set($test_key . '_2', 'value2');
                        $results = $pipe->execute();
                        $redis->del([$test_key . '_1', $test_key . '_2']);
                        $success = (count($results) === 2);
                    }
                    break;
            }
            
            if ($implementation === 'phpredis') {
                $redis->close();
            }
            
            return $success;
            
        } catch (Exception $e) {
            if ($this->debug) {
                echo "        Exception: " . $e->getMessage() . "\n";
            }
            return false;
        }
    }
    
    private function testTlsReliability(&$results) {
        echo "    TLS connection reliability test:\n";
        
        $tls_tests = [
            'connection_success' => 'TLS connection establishment',
            'command_execution' => 'Command execution over TLS',
            'connection_stability' => 'TLS connection stability'
        ];
        
        foreach ($tls_tests as $test => $description) {
            echo "      {$description}:\n";
            
            if ($results['phpredis']['available']) {
                $result = $this->testTlsFeature($test, 'phpredis');
                echo "        phpredis: " . $this->formatTlsResult($result) . "\n";
            }
            
            if ($results['predis']['available']) {
                $result = $this->testTlsFeature($test, 'predis');
                echo "        Predis: " . $this->formatTlsResult($result) . "\n";
            }
        }
    }
    
    private function testTlsFeature($test, $implementation) {
        try {
            if ($implementation === 'phpredis') {
                $redis = new Redis();
                $ssl_context = [
                    'verify_peer' => false,
                    'verify_peer_name' => false,
                    'allow_self_signed' => true
                ];
                $connected = @$redis->connect($this->test_host, $this->test_tls_port, 2.0, null, 0, 0, $ssl_context);
            } else {
                $redis = new Predis\Client([
                    'scheme' => 'tls',
                    'host' => $this->test_host,
                    'port' => $this->test_tls_port,
                    'timeout' => 2.0,
                    'ssl' => [
                        'verify_peer' => false,
                        'verify_peer_name' => false,
                        'allow_self_signed' => true
                    ]
                ]);
                $connected = true; // Predis throws exception if connection fails
            }
            
            if (!$connected) {
                return 'connection_failed';
            }
            
            switch ($test) {
                case 'connection_success':
                    return 'success';
                    
                case 'command_execution':
                    try {
                        $test_key = 'tls_test_' . uniqid();
                        $redis->set($test_key, 'test_value');
                        $result = $redis->get($test_key);
                        $redis->del($test_key);
                        return ($result === 'test_value') ? 'success' : 'command_failed';
                    } catch (Exception $e) {
                        return 'command_exception';
                    }
                    
                case 'connection_stability':
                    try {
                        for ($i = 0; $i < 10; $i++) {
                            $redis->ping();
                            usleep(100000); // 100ms
                        }
                        return 'success';
                    } catch (Exception $e) {
                        return 'stability_failed';
                    }
            }
            
        } catch (Exception $e) {
            return 'exception';
        }
        
        return 'unknown';
    }
    
    private function formatTlsResult($result) {
        $icons = [
            'success' => '✅ Success',
            'connection_failed' => '❌ Connection failed',
            'command_failed' => '⚠️ Commands failed',
            'command_exception' => '❌ Command exception',
            'stability_failed' => '⚠️ Stability issues',
            'exception' => '❌ Exception',
            'unknown' => '❓ Unknown'
        ];
        
        return $icons[$result] ?? "❓ {$result}";
    }
    
    private function testPerformanceComparison(&$results) {
        if (!$results['phpredis']['connection_test'] && !$results['predis']['connection_test']) {
            echo "    ❌ No available implementations for performance testing\n";
            return;
        }
        
        $operations = 1000;
        echo "    Quick performance test ({$operations} operations):\n";
        
        if ($results['phpredis']['connection_test']) {
            $phpredis_time = $this->benchmarkImplementation('phpredis', $operations);
            echo "      phpredis: " . number_format($phpredis_time * 1000, 2) . "ms\n";
        }
        
        if ($results['predis']['connection_test']) {
            $predis_time = $this->benchmarkImplementation('predis', $operations);
            echo "      Predis: " . number_format($predis_time * 1000, 2) . "ms\n";
        }
        
        if ($results['phpredis']['connection_test'] && $results['predis']['connection_test']) {
            $phpredis_time = $this->benchmarkImplementation('phpredis', $operations);
            $predis_time = $this->benchmarkImplementation('predis', $operations);
            
            if ($phpredis_time > 0 && $predis_time > 0) {
                $ratio = $predis_time / $phpredis_time;
                echo "      Performance ratio (Predis/phpredis): " . number_format($ratio, 2) . "x\n";
                
                if ($ratio < 2.0) {
                    echo "      📊 Predis performance is competitive\n";
                } elseif ($ratio < 5.0) {
                    echo "      📊 Predis has moderate overhead\n";
                } else {
                    echo "      📊 Predis has significant overhead\n";
                }
            }
        }
    }
    
    private function benchmarkImplementation($implementation, $operations) {
        try {
            $start_time = microtime(true);
            
            if ($implementation === 'phpredis') {
                $redis = new Redis();
                $redis->connect($this->test_host, $this->test_port, 2.0);
                
                for ($i = 0; $i < $operations; $i++) {
                    $redis->set("bench_key_{$i}", "value_{$i}");
                    $redis->get("bench_key_{$i}");
                }
                
                // Cleanup
                for ($i = 0; $i < $operations; $i++) {
                    $redis->del("bench_key_{$i}");
                }
                
                $redis->close();
            } else {
                $redis = new Predis\Client([
                    'scheme' => 'tcp',
                    'host' => $this->test_host,
                    'port' => $this->test_port,
                    'timeout' => 2.0
                ]);
                
                for ($i = 0; $i < $operations; $i++) {
                    $redis->set("bench_key_{$i}", "value_{$i}");
                    $redis->get("bench_key_{$i}");
                }
                
                // Cleanup
                for ($i = 0; $i < $operations; $i++) {
                    $redis->del("bench_key_{$i}");
                }
            }
            
            return microtime(true) - $start_time;
            
        } catch (Exception $e) {
            if ($this->debug) {
                echo "        Benchmark exception: " . $e->getMessage() . "\n";
            }
            return 0;
        }
    }
    
    private function generateReport($results) {
        $report_file = 'redis_implementation_validation_report.md';
        
        $content = "# Redis Implementation Validation Report\n\n";
        $content .= "**Generated:** " . date('Y-m-d H:i:s') . " UTC\n";
        $content .= "**PHP Version:** " . PHP_VERSION . "\n\n";
        
        $content .= "## Implementation Availability\n\n";
        $content .= "| Implementation | Available | Version | Connection | TLS Support |\n";
        $content .= "|---|---|---|---|---|\n";
        
        foreach (['phpredis', 'predis'] as $impl) {
            $data = $results[$impl];
            $available = $data['available'] ? '✅' : '❌';
            $connection = $data['connection_test'] ? '✅' : '❌';
            $tls = $data['tls_support'] ? '✅' : '❌';
            $content .= "| {$impl} | {$available} | {$data['version']} | {$connection} | {$tls} |\n";
        }
        
        $content .= "\n## Recommendations\n\n";
        
        if ($results['phpredis']['available'] && $results['predis']['available']) {
            $content .= "### Both Implementations Available\n";
            $content .= "- **phpredis**: Use for maximum performance in non-TLS scenarios\n";
            $content .= "- **Predis**: Use for better TLS reliability and cross-platform compatibility\n";
            $content .= "- **Recommendation**: Test both implementations in your specific environment\n\n";
        } elseif ($results['phpredis']['available']) {
            $content .= "### Only phpredis Available\n";
            $content .= "- Install Predis for enhanced TLS support: `composer require predis/predis`\n\n";
        } elseif ($results['predis']['available']) {
            $content .= "### Only Predis Available\n";
            $content .= "- Install phpredis for better performance: `pecl install redis`\n\n";
        } else {
            $content .= "### No Implementations Available\n";
            $content .= "- Install phpredis: `pecl install redis`\n";
            $content .= "- Install Predis: `composer require predis/predis`\n\n";
        }
        
        $content .= "## Error Summary\n\n";
        foreach (['phpredis', 'predis'] as $impl) {
            if (!empty($results[$impl]['errors'])) {
                $content .= "### {$impl} Errors\n";
                foreach ($results[$impl]['errors'] as $error) {
                    $content .= "- {$error}\n";
                }
                $content .= "\n";
            }
        }
        
        if (file_put_contents($report_file, $content)) {
            echo "  ✅ Validation report saved to: {$report_file}\n";
        } else {
            echo "  ❌ Failed to save validation report\n";
        }
    }
}

// Run validation if called directly
if (basename(__FILE__) == basename($_SERVER['PHP_SELF'])) {
    $validator = new RedisImplementationValidator(true);
    $results = $validator->validateImplementations();
    
    echo "\n" . str_repeat("=", 50) . "\n";
    echo "Validation completed!\n";
    
    if ($results['phpredis']['available'] && $results['predis']['available']) {
        echo "✅ Both implementations are available for testing\n";
    } elseif ($results['phpredis']['available'] || $results['predis']['available']) {
        echo "⚠️ Only one implementation available - install the other for comparison\n";
    } else {
        echo "❌ No Redis implementations available - install phpredis and/or Predis\n";
    }
}
?>