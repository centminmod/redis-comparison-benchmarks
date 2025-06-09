# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 18:54:59 UTC
**PHP Version:** 8.4.8
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
| Redis | Non-TLS | Predis | 10,522 | ±302 | 2.9% | 🟡 good | 0.095 | ±0.003 | 0.138 | 0.165 | 10,354-10,689 | 13 |
| Redis | TLS | Predis | 8,032 | ±266 | 3.3% | 🟡 good | 0.124 | ±0.004 | 0.174 | 0.213 | 7,885-8,180 | 13 |
| KeyDB | Non-TLS | Predis | 12,928 | ±351 | 2.7% | 🟡 good | 0.077 | ±0.002 | 0.121 | 0.141 | 12,734-13,122 | 13 |
| KeyDB | TLS | Predis | 9,776 | ±255 | 2.6% | 🟡 good | 0.102 | ±0.003 | 0.151 | 0.180 | 9,635-9,918 | 13 |
| Dragonfly | Non-TLS | Predis | 10,940 | ±292 | 2.7% | 🟡 good | 0.091 | ±0.003 | 0.136 | 0.161 | 10,778-11,102 | 13 |
| Valkey | Non-TLS | Predis | 15,064 | ±387 | 2.6% | 🟡 good | 0.066 | ±0.002 | 0.107 | 0.125 | 14,849-15,279 | 13 |
| Valkey | TLS | Predis | 10,734 | ±306 | 2.9% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.168 | 10,564-10,904 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 7
- **Reliable Measurements:** 7/7
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 15,064 ops/sec
- **Average Performance:** 11,142 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 3/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
