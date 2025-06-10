#!/usr/bin/env php
<?php
/**
 * WordPress Transient API Simulation Test
 * Tests expiration handling and transient-like operations
 */

require_once 'RedisTestBase.php';

class WordPressTransientTest extends RedisTestBase {
    private $test_duration = 10;
    private $key_prefix = 'wp_transient_';
    
    public function __construct($config) {
        parent::__construct($config);
        $this->test_name = "WordPress Transient API Test";
    }
    
    protected function runTest($redis, $db_name) {
        $start_time = microtime(true);
        $end_time = $start_time + $this->test_duration;
        $operations = 0;
        $errors = 0;
        $latencies = [];
        $expired_hits = 0;
        $cache_hits = 0;
        $cache_misses = 0;
        
        // Pre-populate with some transients
        $this->populateTransients($redis);
        
        while (microtime(true) < $end_time) {
            $op_start = microtime(true);
            
            try {
                $operation = $this->getWeightedOperation();
                
                switch ($operation) {
                    case 'get':
                        $result = $this->getTransient($redis);
                        if ($result === false) $cache_misses++;
                        else $cache_hits++;
                        break;
                        
                    case 'set':
                        $this->setTransient($redis);
                        break;
                        
                    case 'delete':
                        $this->deleteTransient($redis);
                        break;
                        
                    case 'cleanup':
                        $this->cleanupExpired($redis);
                        break;
                }
                
                $operations++;
                $latencies[] = (microtime(true) - $op_start) * 1000;
                
            } catch (Exception $e) {
                $errors++;
            }
        }
        
        $total_time = microtime(true) - $start_time;
        $hit_rate = $cache_hits / ($cache_hits + $cache_misses) * 100;
        
        return [
            'operations' => $operations,
            'errors' => $errors,
            'duration' => $total_time,
            'ops_per_sec' => $operations / $total_time,
            'avg_latency' => array_sum($latencies) / count($latencies),
            'p95_latency' => $this->percentile($latencies, 95),
            'p99_latency' => $this->percentile($latencies, 99),
            'cache_hit_rate' => $hit_rate,
            'cache_hits' => $cache_hits,
            'cache_misses' => $cache_misses,
            'error_rate' => ($errors / ($operations + $errors)) * 100
        ];
    }
    
    private function getWeightedOperation() {
        $rand = mt_rand(1, 100);
        if ($rand <= 60) return 'get';      // 60% reads
        if ($rand <= 85) return 'set';      // 25% writes  
        if ($rand <= 95) return 'delete';   // 10% deletes
        return 'cleanup';                   // 5% cleanup
    }
    
    private function populateTransients($redis) {
        $transient_types = ['feed_cache', 'remote_get', 'query_cache', 'theme_cache'];
        
        for ($i = 0; $i < 1000; $i++) {
            $type = $transient_types[array_rand($transient_types)];
            $key = "{$this->key_prefix}{$type}_" . mt_rand(1, 5000);
            $ttl = mt_rand(300, 3600); // 5 minutes to 1 hour
            
            $data = json_encode([
                'type' => $type,
                'data' => str_repeat('Transient data ', mt_rand(5, 20)),
                'created' => time(),
                'expires' => time() + $ttl
            ]);
            
            $redis->setex($key, $ttl, $data);
        }
    }
    
    private function getTransient($redis) {
        $types = ['feed_cache', 'remote_get', 'query_cache', 'theme_cache'];
        $type = $types[array_rand($types)];
        $id = mt_rand(1, 5000);
        $key = "{$this->key_prefix}{$type}_{$id}";
        
        return $redis->get($key);
    }
    
    private function setTransient($redis) {
        $types = ['feed_cache', 'remote_get', 'query_cache', 'theme_cache'];
        $type = $types[array_rand($types)];
        $id = mt_rand(1, 5000);
        $key = "{$this->key_prefix}{$type}_{$id}";
        $ttl = mt_rand(300, 3600);
        
        $data = json_encode([
            'type' => $type,
            'data' => str_repeat('New transient data ', mt_rand(5, 20)),
            'created' => time(),
            'expires' => time() + $ttl
        ]);
        
        return $redis->setex($key, $ttl, $data);
    }
    
    private function deleteTransient($redis) {
        $types = ['feed_cache', 'remote_get', 'query_cache', 'theme_cache'];
        $type = $types[array_rand($types)];
        $id = mt_rand(1, 5000);
        $key = "{$this->key_prefix}{$type}_{$id}";
        
        return $redis->del($key);
    }
    
    private function cleanupExpired($redis) {
        // Simulate cleanup of expired transients
        $pattern = $this->key_prefix . '*';
        $keys = $redis->keys($pattern);
        
        if (!empty($keys)) {
            // Delete a few random keys to simulate cleanup
            $to_delete = array_slice($keys, 0, mt_rand(1, min(10, count($keys))));
            if (!empty($to_delete)) {
                return $redis->del($to_delete);
            }
        }
        return 0;
    }
}

if (php_sapi_name() === 'cli') {
    $config = ['duration' => 30, 'output_dir' => 'php_benchmark_results'];
    $test = new WordPressTransientTest($config);
    $test->run();
}
?>