#!/usr/bin/env php
<?php
/**
 * WordPress Session Storage Simulation Test
 * Simulates session handling with frequent updates
 */

require_once 'RedisTestBase.php';

class WordPressSessionTest extends RedisTestBase {
    private $test_duration = 30;
    private $key_prefix = 'wp_session_';
    private $active_sessions = [];
    
    public function __construct($config) {
        parent::__construct($config);
        $this->test_name = "WordPress Session Storage Test";
    }
    
    protected function runTest($redis, $db_name) {
        $start_time = microtime(true);
        $end_time = $start_time + $this->test_duration;
        $operations = 0;
        $errors = 0;
        $latencies = [];
        $session_creates = 0;
        $session_updates = 0;
        $session_reads = 0;
        $session_destroys = 0;
        
        // Initialize some sessions
        $this->initializeSessions($redis);
        
        while (microtime(true) < $end_time) {
            $op_start = microtime(true);
            
            try {
                $operation = $this->getSessionOperation();
                
                switch ($operation) {
                    case 'create':
                        $this->createSession($redis);
                        $session_creates++;
                        break;
                        
                    case 'read':
                        $this->readSession($redis);
                        $session_reads++;
                        break;
                        
                    case 'update':
                        $this->updateSession($redis);
                        $session_updates++;
                        break;
                        
                    case 'destroy':
                        $this->destroySession($redis);
                        $session_destroys++;
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
            'session_creates' => $session_creates,
            'session_reads' => $session_reads,
            'session_updates' => $session_updates,
            'session_destroys' => $session_destroys,
            'active_sessions' => count($this->active_sessions),
            'error_rate' => ($errors / ($operations + $errors)) * 100
        ];
    }
    
    private function getSessionOperation() {
        $rand = mt_rand(1, 100);
        if ($rand <= 40) return 'read';      // 40% reads
        if ($rand <= 70) return 'update';    // 30% updates
        if ($rand <= 90) return 'create';    // 20% creates
        return 'destroy';                    // 10% destroys
    }
    
    private function initializeSessions($redis) {
        for ($i = 0; $i < 100; $i++) {
            $session_id = $this->generateSessionId();
            $this->active_sessions[] = $session_id;
            
            $session_data = [
                'user_id' => mt_rand(1, 10000),
                'login_time' => time() - mt_rand(0, 3600),
                'last_activity' => time(),
                'cart_items' => mt_rand(0, 10),
                'preferences' => ['theme' => 'dark', 'lang' => 'en'],
                'meta' => str_repeat('session_meta_', mt_rand(5, 15))
            ];
            
            $redis->setex($this->key_prefix . $session_id, 3600, json_encode($session_data));
        }
    }
    
    private function createSession($redis) {
        $session_id = $this->generateSessionId();
        $this->active_sessions[] = $session_id;
        
        $session_data = [
            'user_id' => mt_rand(1, 10000),
            'login_time' => time(),
            'last_activity' => time(),
            'cart_items' => 0,
            'preferences' => ['theme' => 'light', 'lang' => 'en'],
            'ip_address' => $this->generateRandomIP(),
            'user_agent' => 'WordPress/Test'
        ];
        
        return $redis->setex($this->key_prefix . $session_id, 3600, json_encode($session_data));
    }
    
    private function readSession($redis) {
        if (empty($this->active_sessions)) return false;
        
        $session_id = $this->active_sessions[array_rand($this->active_sessions)];
        return $redis->get($this->key_prefix . $session_id);
    }
    
    private function updateSession($redis) {
        if (empty($this->active_sessions)) return false;
        
        $session_id = $this->active_sessions[array_rand($this->active_sessions)];
        $key = $this->key_prefix . $session_id;
        
        $existing = $redis->get($key);
        if ($existing) {
            $data = json_decode($existing, true);
            $data['last_activity'] = time();
            $data['cart_items'] = mt_rand(0, 15);
            $data['page_views'] = ($data['page_views'] ?? 0) + 1;
            
            return $redis->setex($key, 3600, json_encode($data));
        }
        return false;
    }
    
    private function destroySession($redis) {
        if (empty($this->active_sessions)) return false;
        
        $index = array_rand($this->active_sessions);
        $session_id = $this->active_sessions[$index];
        unset($this->active_sessions[$index]);
        $this->active_sessions = array_values($this->active_sessions);
        
        return $redis->del($this->key_prefix . $session_id);
    }
    
    private function generateSessionId() {
        return 'sess_' . bin2hex(random_bytes(16));
    }
    
    private function generateRandomIP() {
        return mt_rand(1, 254) . '.' . mt_rand(1, 254) . '.' . mt_rand(1, 254) . '.' . mt_rand(1, 254);
    }
}

if (php_sapi_name() === 'cli') {
    $config = ['duration' => 30, 'output_dir' => 'php_benchmark_results'];
    $test = new WordPressSessionTest($config);
    $test->run();
}
?>