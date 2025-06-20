<?php
return [
    'duration' => 10,
    'implementation' => 'predis',
    'test_iterations' => 5,
    'iteration_pause_ms' => 500,
    'save_raw_results' => true,
    'output_dir' => './benchmarklogs-2t',
    'test_tls' => true,
    'flush_before_test' => true,
    'debug' => false,
    'thread_variant' => '2',
    'thread_config' => [
        'redis_io_threads' => 2,
        'keydb_server_threads' => 2,
        'dragonfly_proactor_threads' => 2,
        'valkey_io_threads' => 2
    ],
    'databases' => [
        'Redis' => ['host' => '127.0.0.1', 'port' => 6379, 'tls_port' => 6390, 'io_threads' => 2],
        'KeyDB' => ['host' => '127.0.0.1', 'port' => 6380, 'tls_port' => 6391, 'server_threads' => 2],
        'Dragonfly' => ['host' => '127.0.0.1', 'port' => 6381, 'tls_port' => 6392, 'proactor_threads' => 2],
        'Valkey' => ['host' => '127.0.0.1', 'port' => 6382, 'tls_port' => 6393, 'io_threads' => 2]
    ],
    'connection_timeout' => 5.0,
    'read_write_timeout' => 5.0,
    'tcp_keepalive' => true,
    'persistent_connections' => false,
    'connection_retry_attempts' => 3,
    'connection_retry_delay' => 1000
];
