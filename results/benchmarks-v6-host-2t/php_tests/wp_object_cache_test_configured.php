<?php
require_once 'RedisTestBase.php';
require_once 'wp_object_cache_test.php';

if (php_sapi_name() === 'cli') {
    $config = include 'test_config.php';
    $test = new WordPressObjectCacheTest($config);
    $test->run();
}
