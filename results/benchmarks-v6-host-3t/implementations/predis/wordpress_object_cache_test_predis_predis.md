# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 04:14:21 UTC
**PHP Version:** 8.4.7
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 8
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
| Redis | Non-TLS | Predis | 10,585 | ±312 | 2.9% | 🟡 good | 0.094 | ±0.003 | 0.136 | 0.162 | 10,412-10,758 | 13 |
| Redis | TLS | Predis | 8,171 | ±243 | 3.0% | 🟡 good | 0.122 | ±0.004 | 0.172 | 0.209 | 8,036-8,306 | 13 |
| KeyDB | Non-TLS | Predis | 12,963 | ±352 | 2.7% | 🟡 good | 0.077 | ±0.002 | 0.120 | 0.140 | 12,767-13,158 | 13 |
| KeyDB | TLS | Predis | 9,818 | ±254 | 2.6% | 🟡 good | 0.101 | ±0.003 | 0.149 | 0.178 | 9,677-9,958 | 13 |
| Dragonfly | Non-TLS | Predis | 11,278 | ±332 | 2.9% | 🟡 good | 0.088 | ±0.003 | 0.137 | 0.165 | 11,094-11,462 | 13 |
| Dragonfly | TLS | Predis | 8,345 | ±276 | 3.3% | 🟡 good | 0.119 | ±0.004 | 0.173 | 0.211 | 8,191-8,498 | 13 |
| Valkey | Non-TLS | Predis | 15,156 | ±364 | 2.4% | 🟡 good | 0.066 | ±0.002 | 0.106 | 0.123 | 14,954-15,358 | 13 |
| Valkey | TLS | Predis | 10,885 | ±287 | 2.6% | 🟡 good | 0.091 | ±0.003 | 0.140 | 0.166 | 10,726-11,044 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 15,156 ops/sec
- **Average Performance:** 10,900 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
