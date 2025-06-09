# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 11:41:22 UTC
**PHP Version:** 8.4.7
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 7
**Thread Variant:** 1

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

- **redis_io_threads:** 1
- **keydb_server_threads:** 1
- **dragonfly_proactor_threads:** 1
- **valkey_io_threads:** 1

## Results with Statistical Analysis (Predis)

| Database | Mode | Implementation | Ops/sec | ±StdDev | CV% | Quality | Latency(ms) | ±StdDev | P95 Lat | P99 Lat | 95% CI | Iterations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | 
| Redis | Non-TLS | Predis | 15,198 | ±383 | 2.5% | 🟡 good | 0.065 | ±0.002 | 0.106 | 0.123 | 14,986-15,411 | 13 |
| Redis | TLS | Predis | 10,781 | ±303 | 2.8% | 🟡 good | 0.092 | ±0.003 | 0.141 | 0.166 | 10,613-10,949 | 13 |
| KeyDB | Non-TLS | Predis | 12,825 | ±369 | 2.9% | 🟡 good | 0.078 | ±0.002 | 0.121 | 0.141 | 12,621-13,029 | 13 |
| KeyDB | TLS | Predis | 9,728 | ±291 | 3.0% | 🟡 good | 0.102 | ±0.003 | 0.150 | 0.177 | 9,567-9,890 | 13 |
| Dragonfly | Non-TLS | Predis | 11,374 | ±275 | 2.4% | 🟡 good | 0.087 | ±0.002 | 0.135 | 0.162 | 11,222-11,526 | 13 |
| Valkey | Non-TLS | Predis | 15,239 | ±410 | 2.7% | 🟡 good | 0.065 | ±0.002 | 0.106 | 0.122 | 15,012-15,466 | 13 |
| Valkey | TLS | Predis | 10,897 | ±332 | 3.0% | 🟡 good | 0.091 | ±0.003 | 0.140 | 0.165 | 10,713-11,081 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 7
- **Reliable Measurements:** 7/7
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 15,239 ops/sec
- **Average Performance:** 12,292 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 3/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
