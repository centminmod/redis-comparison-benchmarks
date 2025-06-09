# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 15:37:24 UTC
**PHP Version:** 8.4.7
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 7
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
| Redis | Non-TLS | Predis | 10,490 | ±310 | 3.0% | 🟡 good | 0.095 | ±0.003 | 0.136 | 0.165 | 10,318-10,662 | 13 |
| Redis | TLS | Predis | 8,155 | ±257 | 3.1% | 🟡 good | 0.122 | ±0.004 | 0.171 | 0.209 | 8,013-8,298 | 13 |
| KeyDB | Non-TLS | Predis | 12,868 | ±324 | 2.5% | 🟡 good | 0.077 | ±0.002 | 0.120 | 0.140 | 12,688-13,047 | 13 |
| KeyDB | TLS | Predis | 9,779 | ±316 | 3.2% | 🟡 good | 0.102 | ±0.004 | 0.150 | 0.180 | 9,604-9,955 | 13 |
| Dragonfly | Non-TLS | Predis | 10,961 | ±325 | 3.0% | 🟡 good | 0.091 | ±0.003 | 0.135 | 0.161 | 10,781-11,141 | 13 |
| Valkey | Non-TLS | Predis | 15,022 | ±438 | 2.9% | 🟡 good | 0.066 | ±0.002 | 0.106 | 0.124 | 14,779-15,265 | 13 |
| Valkey | TLS | Predis | 10,902 | ±306 | 2.8% | 🟡 good | 0.091 | ±0.003 | 0.139 | 0.165 | 10,733-11,072 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 7
- **Reliable Measurements:** 7/7
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 15,022 ops/sec
- **Average Performance:** 11,168 ops/sec
- **Average Measurement Precision:** 2.9% CV
- **TLS Connection Success:** 3/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
