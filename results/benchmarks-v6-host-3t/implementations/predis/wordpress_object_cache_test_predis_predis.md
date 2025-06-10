# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 18:55:20 UTC
**PHP Version:** 8.4.8
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 7
**Thread Variant:** 3

## Predis Configuration

- **Connection Timeout:** 5s
- **Read/Write Timeout:** 5s
- **TCP Keepalive:** Enabled
- **Persistent Connections:** Disabled
- **Connection Retry Attempts:** 3

## Statistical Methodology

- **Iterations per Test:** 13
- **Iteration Pause:** 500ms
- **Statistical Measures:** Standard deviation, coefficient of variation, 95% confidence intervals
- **Quality Thresholds:** Excellent (<2% CV), Good (<5% CV), Fair (<10% CV), Poor (≥10% CV)

## Thread Configuration

- **redis_io_threads:** 3
- **keydb_server_threads:** 3
- **dragonfly_proactor_threads:** 3
- **valkey_io_threads:** 3

## Results with Statistical Analysis (Predis)

| Database | Mode | Implementation | Ops/sec | ±StdDev | CV% | Quality | Latency(ms) | ±StdDev | P95 Lat | P99 Lat | 95% CI | Iterations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | 
| Redis | Non-TLS | Predis | 9,378 | ±331 | 3.5% | 🟡 good | 0.106 | ±0.004 | 0.151 | 0.218 | 9,195-9,562 | 13 |
| Redis | TLS | Predis | 7,208 | ±588 | 8.2% | 🟠 fair | 0.139 | ±0.012 | 0.197 | 0.294 | 6,882-7,534 | 13 |
| KeyDB | Non-TLS | Predis | 12,421 | ±322 | 2.6% | 🟡 good | 0.080 | ±0.002 | 0.125 | 0.148 | 12,243-12,600 | 13 |
| KeyDB | TLS | Predis | 9,002 | ±314 | 3.5% | 🟡 good | 0.111 | ±0.004 | 0.160 | 0.227 | 8,828-9,177 | 13 |
| Dragonfly | Non-TLS | Predis | 10,525 | ±332 | 3.2% | 🟡 good | 0.095 | ±0.003 | 0.146 | 0.176 | 10,340-10,709 | 13 |
| Valkey | Non-TLS | Predis | 14,883 | ±481 | 3.2% | 🟡 good | 0.067 | ±0.002 | 0.109 | 0.128 | 14,616-15,150 | 13 |
| Valkey | TLS | Predis | 10,513 | ±330 | 3.1% | 🟡 good | 0.095 | ±0.003 | 0.144 | 0.173 | 10,330-10,696 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 7
- **Reliable Measurements:** 7/7
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,883 ops/sec
- **Average Performance:** 10,561 ops/sec
- **Average Measurement Precision:** 3.9% CV
- **TLS Connection Success:** 3/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
