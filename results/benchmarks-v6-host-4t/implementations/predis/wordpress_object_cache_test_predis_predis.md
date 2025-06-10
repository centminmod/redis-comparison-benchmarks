# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 11:02:16 UTC
**PHP Version:** 8.4.8
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 8
**Thread Variant:** 4

## Predis Configuration

- **Connection Timeout:** 5s
- **Read/Write Timeout:** 5s
- **TCP Keepalive:** Enabled
- **Persistent Connections:** Disabled
- **Connection Retry Attempts:** 3

## Statistical Methodology

- **Iterations per Test:** 5
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
| Redis | Non-TLS | Predis | 9,614 | ±443 | 4.6% | 🟡 good | 0.104 | ±0.005 | 0.177 | 0.222 | 9,065-10,163 | 5 |
| Redis | TLS | Predis | 7,276 | ±340 | 4.7% | 🟡 good | 0.137 | ±0.007 | 0.235 | 0.293 | 6,854-7,698 | 5 |
| KeyDB | Non-TLS | Predis | 11,732 | ±594 | 5.1% | 🟠 fair | 0.085 | ±0.005 | 0.147 | 0.187 | 10,994-12,469 | 5 |
| KeyDB | TLS | Predis | 8,947 | ±423 | 4.7% | 🟡 good | 0.111 | ±0.006 | 0.190 | 0.244 | 8,422-9,472 | 5 |
| Dragonfly | Non-TLS | Predis | 10,051 | ±435 | 4.3% | 🟡 good | 0.099 | ±0.004 | 0.165 | 0.221 | 9,511-10,590 | 5 |
| Dragonfly | TLS | Predis | 7,016 | ±263 | 3.7% | 🟡 good | 0.142 | ±0.005 | 0.235 | 0.301 | 6,689-7,342 | 5 |
| Valkey | Non-TLS | Predis | 13,850 | ±605 | 4.4% | 🟡 good | 0.072 | ±0.003 | 0.125 | 0.166 | 13,098-14,601 | 5 |
| Valkey | TLS | Predis | 9,941 | ±433 | 4.4% | 🟡 good | 0.100 | ±0.005 | 0.171 | 0.232 | 9,404-10,479 | 5 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 13,850 ops/sec
- **Average Performance:** 9,803 ops/sec
- **Average Measurement Precision:** 4.5% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
