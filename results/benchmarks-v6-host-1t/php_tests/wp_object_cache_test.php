<?php
/**
 * WordPress Object Cache Simulation Test
 * Simulates typical WordPress object caching patterns
 */

require_once 'RedisTestBase.php';

class WordPressObjectCacheTest extends RedisTestBase {
    private $test_duration = 30; // seconds
    private $key_prefix = 'wp_obj_';
    
    public function __construct($config) {
        parent::__construct($config);
        $this->test_name = "WordPress Object Cache Test";
    }
    
    protected function runTest($redis, $db_name) {
        echo "  Starting test with database containing " . $redis->dbSize() . " keys\n";
        
        $start_time = microtime(true);
        $end_time = $start_time + $this->test_duration;
        $operations = 0;
        $errors = 0;
        $latencies = [];
        
        // Typical WordPress cache keys and data
        $cache_groups = ['posts', 'terms', 'users', 'options', 'comments'];
        $object_types = ['post_meta', 'user_meta', 'term_meta', 'transient'];
        
        while (microtime(true) < $end_time) {
            $op_start = microtime(true);
            
            try {
                // 70% reads, 30% writes (typical WordPress ratio)
                if (mt_rand(1, 100) <= 70) {
                    // Read operation
                    $group = $cache_groups[array_rand($cache_groups)];
                    $id = mt_rand(1, 10000);
                    $key = "{$this->key_prefix}{$group}_{$id}";
                    $redis->get($key);
                } else {
                    // Write operation with WordPress-like data
                    $group = $cache_groups[array_rand($cache_groups)];
                    $type = $object_types[array_rand($object_types)];
                    $id = mt_rand(1, 10000);
                    $key = "{$this->key_prefix}{$group}_{$type}_{$id}";
                    
                    $data = json_encode([
                        'id' => $id,
                        'type' => $type,
                        'content' => str_repeat('WordPress cache data ', mt_rand(10, 50)),
                        'meta' => ['created' => time(), 'version' => '1.0'],
                        'tags' => ['wp', 'cache', $group]
                    ]);
                    
                    // Set with typical WordPress TTL (1 hour to 24 hours)
                    $ttl = mt_rand(3600, 86400);
                    $redis->setex($key, $ttl, $data);
                }
                
                $operations++;
                $latencies[] = (microtime(true) - $op_start) * 1000;
                
            } catch (Exception $e) {
                $errors++;
            }
        }
        
        $total_time = microtime(true) - $start_time;
        $final_keys = $redis->dbSize();
        echo "  Test completed with {$final_keys} keys in database\n";
        
        return [
            'operations' => $operations,
            'errors' => $errors,
            'duration' => $total_time,
            'ops_per_sec' => $operations / $total_time,
            'avg_latency' => array_sum($latencies) / count($latencies),
            'p95_latency' => $this->percentile($latencies, 95),
            'p99_latency' => $this->percentile($latencies, 99),
            'error_rate' => ($errors / ($operations + $errors)) * 100,
            'final_key_count' => $final_keys
        ];
    }
    
    protected function percentile($array, $percentile) {
        if (empty($array)) return 0;
        
        sort($array);
        $index = ceil($percentile / 100 * count($array)) - 1;
        return $array[max(0, $index)];
    }
}

// Run the test
if (php_sapi_name() === 'cli') {
    $config = [
        'duration' => 30,
        'output_dir' => 'php_benchmark_results'
    ];
    
    $test = new WordPressObjectCacheTest($config);
    $test->run();
}
?>