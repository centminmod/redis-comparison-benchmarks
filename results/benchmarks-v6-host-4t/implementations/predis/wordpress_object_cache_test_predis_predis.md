# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 15:33:28 UTC
**PHP Version:** 8.4.7
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 7
**Thread Variant:** 4

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

- **redis_io_threads:** 4
- **keydb_server_threads:** 4
- **dragonfly_proactor_threads:** 4
- **valkey_io_threads:** 4

## Results with Statistical Analysis (Predis)

| Database | Mode | Implementation | Ops/sec | ±StdDev | CV% | Quality | Latency(ms) | ±StdDev | P95 Lat | P99 Lat | 95% CI | Iterations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | 
| Redis | Non-TLS | Predis | 10,639 | ±334 | 3.1% | 🟡 good | 0.094 | ±0.003 | 0.135 | 0.162 | 10,453-10,824 | 13 |
| Redis | TLS | Predis | 8,102 | ±252 | 3.1% | 🟡 good | 0.123 | ±0.004 | 0.172 | 0.211 | 7,963-8,242 | 13 |
| KeyDB | Non-TLS | Predis | 13,065 | ±381 | 2.9% | 🟡 good | 0.076 | ±0.002 | 0.120 | 0.140 | 12,854-13,276 | 13 |
| KeyDB | TLS | Predis | 9,869 | ±297 | 3.0% | 🟡 good | 0.101 | ±0.003 | 0.149 | 0.177 | 9,704-10,034 | 13 |
| Dragonfly | Non-TLS | Predis | 10,990 | ±329 | 3.0% | 🟡 good | 0.091 | ±0.003 | 0.135 | 0.161 | 10,807-11,172 | 13 |
| Valkey | Non-TLS | Predis | 15,171 | ±388 | 2.6% | 🟡 good | 0.065 | ±0.002 | 0.106 | 0.124 | 14,956-15,386 | 13 |
| Valkey | TLS | Predis | 10,776 | ±294 | 2.7% | 🟡 good | 0.092 | ±0.003 | 0.142 | 0.168 | 10,613-10,939 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 7
- **Reliable Measurements:** 7/7
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 15,171 ops/sec
- **Average Performance:** 11,230 ops/sec
- **Average Measurement Precision:** 2.9% CV
- **TLS Connection Success:** 3/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
