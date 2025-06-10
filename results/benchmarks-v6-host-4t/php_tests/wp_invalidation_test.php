#!/usr/bin/env php
<?php
/**
 * WordPress Cache Invalidation Pattern Test
 * Tests cache invalidation scenarios typical in WordPress
 */

require_once 'RedisTestBase.php';

class WordPressCacheInvalidationTest extends RedisTestBase {
    private $test_duration = 10;
    private $key_prefix = 'wp_cache_';
    private $tag_prefix = 'wp_tag_';
    
    public function __construct($config) {
        parent::__construct($config);
        $this->test_name = "WordPress Cache Invalidation Test";
    }
    
    protected function runTest($redis, $db_name) {
        $start_time = microtime(true);
        $end_time = $start_time + $this->test_duration;
        $operations = 0;
        $errors = 0;
        $latencies = [];
        $cache_sets = 0;
        $cache_gets = 0;
        $invalidations = 0;
        $bulk_invalidations = 0;
        
        // Pre-populate cache
        $this->populateCache($redis);
        
        while (microtime(true) < $end_time) {
            $op_start = microtime(true);
            
            try {
                $operation = $this->getInvalidationOperation();
                
                switch ($operation) {
                    case 'get':
                        $this->getCachedContent($redis);
                        $cache_gets++;
                        break;
                        
                    case 'set':
                        $this->setCachedContent($redis);
                        $cache_sets++;
                        break;
                        
                    case 'invalidate_single':
                        $this->invalidateSingle($redis);
                        $invalidations++;
                        break;
                        
                    case 'invalidate_group':
                        $this->invalidateGroup($redis);
                        $bulk_invalidations++;
                        break;
                        
                    case 'invalidate_tags':
                        $this->invalidateByTags($redis);
                        $bulk_invalidations++;
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
            'cache_sets' => $cache_sets,
            'cache_gets' => $cache_gets,
            'single_invalidations' => $invalidations,
            'bulk_invalidations' => $bulk_invalidations,
            'error_rate' => ($errors / ($operations + $errors)) * 100
        ];
    }
    
    private function getInvalidationOperation() {
        $rand = mt_rand(1, 100);
        if ($rand <= 50) return 'get';                // 50% reads
        if ($rand <= 70) return 'set';                // 20% writes
        if ($rand <= 85) return 'invalidate_single';  // 15% single invalidations
        if ($rand <= 95) return 'invalidate_group';   // 10% group invalidations
        return 'invalidate_tags';                     // 5% tag invalidations
    }
    
    private function populateCache($redis) {
        $content_types = ['post', 'page', 'category', 'tag', 'user', 'comment'];
        $cache_groups = ['query', 'object', 'transient', 'fragment'];
        
        for ($i = 0; $i < 1000; $i++) {
            $content_type = $content_types[array_rand($content_types)];
            $cache_group = $cache_groups[array_rand($cache_groups)];
            $id = mt_rand(1, 5000);
            
            $key = "{$this->key_prefix}{$cache_group}_{$content_type}_{$id}";
            $tags = [$content_type, $cache_group, "id_{$id}"];
            
            $data = [
                'content' => str_repeat("Cached {$content_type} content ", mt_rand(10, 50)),
                'type' => $content_type,
                'group' => $cache_group,
                'id' => $id,
                'tags' => $tags,
                'created' => time(),
                'dependencies' => array_map(function($i) { return "dep_$i"; }, range(1, mt_rand(2, 8)))
            ];
            
            $redis->setex($key, mt_rand(1800, 7200), json_encode($data));
            
            // Store tag associations
            foreach ($tags as $tag) {
                $redis->sadd($this->tag_prefix . $tag, $key);
            }
        }
    }
    
    private function getCachedContent($redis) {
        $content_types = ['post', 'page', 'category', 'tag', 'user', 'comment'];
        $cache_groups = ['query', 'object', 'transient', 'fragment'];
        
        $content_type = $content_types[array_rand($content_types)];
        $cache_group = $cache_groups[array_rand($cache_groups)];
        $id = mt_rand(1, 5000);
        
        $key = "{$this->key_prefix}{$cache_group}_{$content_type}_{$id}";
        return $redis->get($key);
    }
    
    private function setCachedContent($redis) {
        $content_types = ['post', 'page', 'category', 'tag', 'user', 'comment'];
        $cache_groups = ['query', 'object', 'transient', 'fragment'];
        
        $content_type = $content_types[array_rand($content_types)];
        $cache_group = $cache_groups[array_rand($cache_groups)];
        $id = mt_rand(1, 5000);
        
        $key = "{$this->key_prefix}{$cache_group}_{$content_type}_{$id}";
        $tags = [$content_type, $cache_group, "id_{$id}"];
        
        $data = [
            'content' => str_repeat("Updated {$content_type} content ", mt_rand(10, 50)),
            'type' => $content_type,
            'group' => $cache_group,
            'id' => $id,
            'tags' => $tags,
            'updated' => time()
        ];
        
        $result = $redis->setex($key, mt_rand(1800, 7200), json_encode($data));
        
        // Update tag associations
        foreach ($tags as $tag) {
            $redis->sadd($this->tag_prefix . $tag, $key);
        }
        
        return $result;
    }
    
    private function invalidateSingle($redis) {
        $content_types = ['post', 'page', 'category', 'tag', 'user', 'comment'];
        $cache_groups = ['query', 'object', 'transient', 'fragment'];
        
        $content_type = $content_types[array_rand($content_types)];
        $cache_group = $cache_groups[array_rand($cache_groups)];
        $id = mt_rand(1, 5000);
        
        $key = "{$this->key_prefix}{$cache_group}_{$content_type}_{$id}";
        return $redis->del($key);
    }
    
    private function invalidateGroup($redis) {
        $cache_groups = ['query', 'object', 'transient', 'fragment'];
        $content_types = ['post', 'page', 'category', 'tag', 'user', 'comment'];
        
        $cache_group = $cache_groups[array_rand($cache_groups)];
        $content_type = $content_types[array_rand($content_types)];
        
        $pattern = "{$this->key_prefix}{$cache_group}_{$content_type}_*";
        $keys = $redis->keys($pattern);
        
        if (!empty($keys)) {
            return $redis->del($keys);
        }
        return 0;
    }
    
    private function invalidateByTags($redis) {
        $tags = ['post', 'page', 'category', 'tag', 'user', 'comment', 'query', 'object'];
        $tag = $tags[array_rand($tags)];
        
        $tag_key = $this->tag_prefix . $tag;
        $keys = $redis->smembers($tag_key);
        
        if (!empty($keys)) {
            $redis->del($keys);
            $redis->del($tag_key);
            return count($keys);
        }
        return 0;
    }
}

if (php_sapi_name() === 'cli') {
    $config = ['duration' => 30, 'output_dir' => 'php_benchmark_results'];
    $test = new WordPressCacheInvalidationTest($config);
    $test->run();
}
?>