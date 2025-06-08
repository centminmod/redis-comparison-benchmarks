#!/usr/bin/env php
<?php
/**
 * WordPress High-Frequency Operations Test
 * Simulates rapid small operations typical in high-traffic WordPress sites
 */

require_once 'RedisTestBase.php';

class WordPressHighFrequencyTest extends RedisTestBase {
    private $test_duration = 30;
    private $key_prefix = 'wp_hf_';
    
    public function __construct($config) {
        parent::__construct($config);
        $this->test_name = "WordPress High-Frequency Operations Test";
    }
    
    protected function runTest($redis, $db_name) {
        $start_time = microtime(true);
        $end_time = $start_time + $this->test_duration;
        $operations = 0;
        $errors = 0;
        $latencies = [];
        $counters = 0;
        $flags = 0;
        $queues = 0;
        $locks = 0;
        $stats = 0;
        
        while (microtime(true) < $end_time) {
            $op_start = microtime(true);
            
            try {
                $operation = $this->getHighFrequencyOperation();
                
                switch ($operation) {
                    case 'counter':
                        $this->updateCounter($redis);
                        $counters++;
                        break;
                        
                    case 'flag':
                        $this->setFlag($redis);
                        $flags++;
                        break;
                        
                    case 'queue':
                        $this->queueOperation($redis);
                        $queues++;
                        break;
                        
                    case 'lock':
                        $this->acquireLock($redis);
                        $locks++;
                        break;
                        
                    case 'stats':
                        $this->updateStats($redis);
                        $stats++;
                        break;
                }
                
                $operations++;
                $latencies[] = (microtime(true) - $op_start) * 1000;
                
            } catch (Exception $e) {
                $errors++;
            }
        }
        
        $total_time = microtime(true) - $start_time;
        
        return [
            'operations' => $operations,
            'errors' => $errors,
            'duration' => $total_time,
            'ops_per_sec' => $operations / $total_time,
            'avg_latency' => array_sum($latencies) / count($latencies),
            'p95_latency' => $this->percentile($latencies, 95),
            'p99_latency' => $this->percentile($latencies, 99),
            'counter_ops' => $counters,
            'flag_ops' => $flags,
            'queue_ops' => $queues,
            'lock_ops' => $locks,
            'stats_ops' => $stats,
            'error_rate' => ($errors / ($operations + $errors)) * 100
        ];
    }
    
    private function getHighFrequencyOperation() {
        $rand = mt_rand(1, 100);
        if ($rand <= 30) return 'counter';   // 30% counter updates
        if ($rand <= 50) return 'flag';      // 20% flag operations
        if ($rand <= 70) return 'queue';     // 20% queue operations
        if ($rand <= 90) return 'lock';      // 20% lock operations
        return 'stats';                      // 10% stats updates
    }
    
    private function updateCounter($redis) {
        $counters = ['page_views', 'post_views', 'user_sessions', 'cache_hits', 'login_attempts'];
        $counter = $counters[array_rand($counters)];
        $key = $this->key_prefix . "counter_{$counter}";
        
        // Use Redis atomic operations
        $redis->incr($key);
        $redis->expire($key, 86400); // 24 hour TTL
        
        return true;
    }
    
    private function setFlag($redis) {
        $flags = ['maintenance_mode', 'cache_enabled', 'debug_mode', 'uploads_disabled', 'comments_open'];
        $flag = $flags[array_rand($flags)];
        $key = $this->key_prefix . "flag_{$flag}";
        $value = mt_rand(0, 1) ? 'true' : 'false';
        
        return $redis->setex($key, 3600, $value);
    }
    
    private function queueOperation($redis) {
        $queues = ['email_queue', 'image_resize', 'backup_tasks', 'cleanup_tasks', 'notification_queue'];
        $queue = $queues[array_rand($queues)];
        $queue_key = $this->key_prefix . "queue_{$queue}";
        
        $operation = mt_rand(1, 100) <= 70 ? 'push' : 'pop';
        
        if ($operation === 'push') {
            $task = json_encode([
                'id' => uniqid(),
                'type' => $queue,
                'priority' => mt_rand(1, 10),
                'created' => time(),
                'data' => str_repeat('task_data_', mt_rand(2, 8))
            ]);
            return $redis->lpush($queue_key, $task);
        } else {
            return $redis->rpop($queue_key);
        }
    }
    
    private function acquireLock($redis) {
        $resources = ['user_update', 'post_save', 'cache_clear', 'backup_run', 'cron_job'];
        $resource = $resources[array_rand($resources)];
        $lock_key = $this->key_prefix . "lock_{$resource}";
        $lock_value = uniqid();
        
        // Try to acquire lock with 30 second timeout
        $result = $redis->set($lock_key, $lock_value, ['nx', 'ex' => 30]);
        
        if ($result) {
            // Simulate some work then release
            usleep(mt_rand(1000, 5000)); // 1-5ms work
            return $redis->eval(
                "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end",
                [$lock_key, $lock_value], 1
            );
        }
        
        return false;
    }
    
    private function updateStats($redis) {
        $stats_types = ['hourly', 'daily', 'weekly', 'monthly'];
        $metrics = ['visitors', 'pageviews', 'comments', 'searches', 'downloads'];
        
        $stat_type = $stats_types[array_rand($stats_types)];
        $metric = $metrics[array_rand($metrics)];
        $timestamp = $this->getStatTimestamp($stat_type);
        
        $key = $this->key_prefix . "stats_{$stat_type}_{$metric}_{$timestamp}";
        
        // Use hash to store multiple metrics
        $redis->hincrby($key, 'count', 1);
        $redis->hincrby($key, 'total', mt_rand(1, 100));
        $redis->expire($key, $this->getStatTTL($stat_type));
        
        return true;
    }
    
    private function getStatTimestamp($type) {
        $now = time();
        switch ($type) {
            case 'hourly':
                return date('Y-m-d-H', $now);
            case 'daily':
                return date('Y-m-d', $now);
            case 'weekly':
                return date('Y-W', $now);
            case 'monthly':
                return date('Y-m', $now);
            default:
                return date('Y-m-d', $now);
        }
    }
    
    private function getStatTTL($type) {
        switch ($type) {
            case 'hourly':
                return 86400;    // 1 day
            case 'daily':
                return 2592000;  // 30 days
            case 'weekly':
                return 7776000;  // 90 days
            case 'monthly':
                return 31536000; // 1 year
            default:
                return 86400;
        }
    }
}

if (php_sapi_name() === 'cli') {
    $config = ['duration' => 30, 'output_dir' => 'php_benchmark_results'];
    $test = new WordPressHighFrequencyTest($config);
    $test->run();
}
?>