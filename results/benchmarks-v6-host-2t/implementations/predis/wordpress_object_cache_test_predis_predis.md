# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 00:14:37 UTC
**PHP Version:** 8.4.7
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 8
**Thread Variant:** 2

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

- **redis_io_threads:** 2
- **keydb_server_threads:** 2
- **dragonfly_proactor_threads:** 2
- **valkey_io_threads:** 2

## Results with Statistical Analysis (Predis)

| Database | Mode | Implementation | Ops/sec | ±StdDev | CV% | Quality | Latency(ms) | ±StdDev | P95 Lat | P99 Lat | 95% CI | Iterations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | 
| Redis | Non-TLS | Predis | 10,609 | ±302 | 2.8% | 🟡 good | 0.094 | ±0.003 | 0.135 | 0.160 | 10,441-10,776 | 13 |
| Redis | TLS | Predis | 8,149 | ±239 | 2.9% | 🟡 good | 0.122 | ±0.004 | 0.171 | 0.207 | 8,017-8,282 | 13 |
| KeyDB | Non-TLS | Predis | 13,019 | ±340 | 2.6% | 🟡 good | 0.076 | ±0.002 | 0.119 | 0.138 | 12,831-13,208 | 13 |
| KeyDB | TLS | Predis | 9,840 | ±290 | 3.0% | 🟡 good | 0.101 | ±0.003 | 0.148 | 0.176 | 9,679-10,001 | 13 |
| Dragonfly | Non-TLS | Predis | 11,353 | ±316 | 2.8% | 🟡 good | 0.088 | ±0.003 | 0.135 | 0.162 | 11,177-11,528 | 13 |
| Dragonfly | TLS | Predis | 8,150 | ±211 | 2.6% | 🟡 good | 0.122 | ±0.003 | 0.168 | 0.203 | 8,033-8,267 | 13 |
| Valkey | Non-TLS | Predis | 15,293 | ±398 | 2.6% | 🟡 good | 0.065 | ±0.002 | 0.105 | 0.121 | 15,073-15,514 | 13 |
| Valkey | TLS | Predis | 10,987 | ±275 | 2.5% | 🟡 good | 0.091 | ±0.002 | 0.139 | 0.163 | 10,835-11,140 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 15,293 ops/sec
- **Average Performance:** 10,925 ops/sec
- **Average Measurement Precision:** 2.7% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
