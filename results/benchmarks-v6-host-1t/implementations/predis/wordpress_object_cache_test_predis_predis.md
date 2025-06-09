# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 04:19:51 UTC
**PHP Version:** 8.4.7
**Predis Version:** unknown
**Redis Implementation:** Predis (Pure PHP)
**Results Count:** 8
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
| Redis | Non-TLS | Predis | 14,724 | ±368 | 2.5% | 🟡 good | 0.067 | ±0.002 | 0.109 | 0.128 | 14,520-14,928 | 13 |
| Redis | TLS | Predis | 10,739 | ±310 | 2.9% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.170 | 10,567-10,911 | 13 |
| KeyDB | Non-TLS | Predis | 12,539 | ±343 | 2.7% | 🟡 good | 0.079 | ±0.002 | 0.123 | 0.145 | 12,349-12,729 | 13 |
| KeyDB | TLS | Predis | 9,638 | ±265 | 2.8% | 🟡 good | 0.103 | ±0.003 | 0.152 | 0.183 | 9,491-9,785 | 13 |
| Dragonfly | Non-TLS | Predis | 10,427 | ±268 | 2.6% | 🟡 good | 0.095 | ±0.003 | 0.141 | 0.170 | 10,278-10,575 | 13 |
| Dragonfly | TLS | Predis | 8,662 | ±233 | 2.7% | 🟡 good | 0.115 | ±0.003 | 0.167 | 0.206 | 8,532-8,791 | 13 |
| Valkey | Non-TLS | Predis | 14,830 | ±446 | 3.0% | 🟡 good | 0.067 | ±0.002 | 0.108 | 0.127 | 14,582-15,077 | 13 |
| Valkey | TLS | Predis | 10,737 | ±293 | 2.7% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.169 | 10,574-10,899 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,830 ops/sec
- **Average Performance:** 11,537 ops/sec
- **Average Measurement Precision:** 2.7% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
