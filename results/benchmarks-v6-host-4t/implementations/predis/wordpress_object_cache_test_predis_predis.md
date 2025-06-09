# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 00:09:43 UTC
**PHP Version:** 8.4.7
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
| Redis | Non-TLS | Predis | 10,478 | ±288 | 2.7% | 🟡 good | 0.095 | ±0.003 | 0.136 | 0.162 | 10,318-10,638 | 13 |
| Redis | TLS | Predis | 8,084 | ±243 | 3.0% | 🟡 good | 0.123 | ±0.004 | 0.171 | 0.208 | 7,950-8,219 | 13 |
| KeyDB | Non-TLS | Predis | 12,823 | ±347 | 2.7% | 🟡 good | 0.077 | ±0.002 | 0.120 | 0.140 | 12,631-13,015 | 13 |
| KeyDB | TLS | Predis | 9,817 | ±280 | 2.9% | 🟡 good | 0.101 | ±0.003 | 0.148 | 0.176 | 9,662-9,973 | 13 |
| Dragonfly | Non-TLS | Predis | 11,267 | ±328 | 2.9% | 🟡 good | 0.088 | ±0.003 | 0.135 | 0.163 | 11,085-11,449 | 13 |
| Dragonfly | TLS | Predis | 8,867 | ±253 | 2.8% | 🟡 good | 0.112 | ±0.003 | 0.162 | 0.198 | 8,727-9,008 | 13 |
| Valkey | Non-TLS | Predis | 14,853 | ±383 | 2.6% | 🟡 good | 0.067 | ±0.002 | 0.107 | 0.124 | 14,641-15,065 | 13 |
| Valkey | TLS | Predis | 10,769 | ±317 | 2.9% | 🟡 good | 0.092 | ±0.003 | 0.140 | 0.165 | 10,593-10,944 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,853 ops/sec
- **Average Performance:** 10,870 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
