<?php
return [
    'duration' => 30,
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
    ]
];
