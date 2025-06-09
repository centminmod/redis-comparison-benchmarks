# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 15:31:04 UTC
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
| Redis | Non-TLS | Predis | 15,068 | ±374 | 2.5% | 🟡 good | 0.066 | ±0.002 | 0.106 | 0.123 | 14,861-15,275 | 13 |
| Redis | TLS | Predis | 10,860 | ±313 | 2.9% | 🟡 good | 0.092 | ±0.003 | 0.139 | 0.165 | 10,686-11,033 | 13 |
| KeyDB | Non-TLS | Predis | 12,919 | ±338 | 2.6% | 🟡 good | 0.077 | ±0.002 | 0.119 | 0.138 | 12,732-13,107 | 13 |
| KeyDB | TLS | Predis | 9,837 | ±285 | 2.9% | 🟡 good | 0.101 | ±0.003 | 0.148 | 0.176 | 9,679-9,996 | 13 |
| Dragonfly | Non-TLS | Predis | 10,659 | ±327 | 3.1% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.167 | 10,477-10,840 | 13 |
| Valkey | Non-TLS | Predis | 15,086 | ±386 | 2.6% | 🟡 good | 0.066 | ±0.002 | 0.106 | 0.122 | 14,872-15,300 | 13 |
| Valkey | TLS | Predis | 10,842 | ±339 | 3.1% | 🟡 good | 0.092 | ±0.003 | 0.140 | 0.165 | 10,654-11,030 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 7
- **Reliable Measurements:** 7/7
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 15,086 ops/sec
- **Average Performance:** 12,182 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 3/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
