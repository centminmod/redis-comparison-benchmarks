<?php
return [
    'duration' => 30,
    'output_dir' => './benchmarklogs-2t',
    'test_tls' => true,
    'flush_before_test' => true,
    'databases' => [
        'Redis' => ['host' => '127.0.0.1', 'port' => 6379, 'tls_port' => 6390],
        'KeyDB' => ['host' => '127.0.0.1', 'port' => 6380, 'tls_port' => 6391],
        'Dragonfly' => ['host' => '127.0.0.1', 'port' => 6381, 'tls_port' => 6392],
        'Valkey' => ['host' => '127.0.0.1', 'port' => 6382, 'tls_port' => 6393]
    ]
];
