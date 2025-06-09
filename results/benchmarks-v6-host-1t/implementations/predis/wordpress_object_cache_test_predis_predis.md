# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 00:11:18 UTC
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
| Redis | Non-TLS | Predis | 14,720 | ±434 | 2.9% | 🟡 good | 0.067 | ±0.002 | 0.109 | 0.127 | 14,479-14,961 | 13 |
| Redis | TLS | Predis | 10,723 | ±283 | 2.6% | 🟡 good | 0.093 | ±0.003 | 0.142 | 0.168 | 10,566-10,880 | 13 |
| KeyDB | Non-TLS | Predis | 12,525 | ±345 | 2.8% | 🟡 good | 0.079 | ±0.002 | 0.123 | 0.143 | 12,333-12,716 | 13 |
| KeyDB | TLS | Predis | 9,625 | ±278 | 2.9% | 🟡 good | 0.103 | ±0.003 | 0.152 | 0.180 | 9,471-9,779 | 13 |
| Dragonfly | Non-TLS | Predis | 11,145 | ±304 | 2.7% | 🟡 good | 0.089 | ±0.003 | 0.137 | 0.163 | 10,976-11,314 | 13 |
| Dragonfly | TLS | Predis | 8,287 | ±241 | 2.9% | 🟡 good | 0.120 | ±0.004 | 0.173 | 0.209 | 8,153-8,420 | 13 |
| Valkey | Non-TLS | Predis | 14,753 | ±375 | 2.5% | 🟡 good | 0.067 | ±0.002 | 0.108 | 0.126 | 14,545-14,961 | 13 |
| Valkey | TLS | Predis | 10,758 | ±306 | 2.8% | 🟡 good | 0.092 | ±0.003 | 0.141 | 0.167 | 10,588-10,928 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,753 ops/sec
- **Average Performance:** 11,567 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
