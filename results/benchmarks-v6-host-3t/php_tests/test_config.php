<?php
return [
    'duration' => 30,
    'output_dir' => './benchmarklogs-3t',
    'test_tls' => true,
    'flush_before_test' => true,
    'thread_variant' => '3',
    'thread_config' => [
        'redis_io_threads' => 3,
        'keydb_server_threads' => 3,
        'dragonfly_proactor_threads' => 3,
        'valkey_io_threads' => 3
    ],
    'databases' => [
        'Redis' => ['host' => '127.0.0.1', 'port' => 6379, 'tls_port' => 6390, 'io_threads' => 3],
        'KeyDB' => ['host' => '127.0.0.1', 'port' => 6380, 'tls_port' => 6391, 'server_threads' => 3],
        'Dragonfly' => ['host' => '127.0.0.1', 'port' => 6381, 'tls_port' => 6392, 'proactor_threads' => 3],
        'Valkey' => ['host' => '127.0.0.1', 'port' => 6382, 'tls_port' => 6393, 'io_threads' => 3]
    ]
];
