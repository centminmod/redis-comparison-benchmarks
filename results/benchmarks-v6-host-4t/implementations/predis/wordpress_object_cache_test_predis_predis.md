# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-09 07:45:22 UTC
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
| Redis | Non-TLS | Predis | 10,486 | ±320 | 3.0% | 🟡 good | 0.095 | ±0.003 | 0.137 | 0.163 | 10,308-10,663 | 13 |
| Redis | TLS | Predis | 8,129 | ±237 | 2.9% | 🟡 good | 0.123 | ±0.004 | 0.172 | 0.209 | 7,997-8,260 | 13 |
| KeyDB | Non-TLS | Predis | 12,943 | ±325 | 2.5% | 🟡 good | 0.077 | ±0.002 | 0.120 | 0.141 | 12,763-13,123 | 13 |
| KeyDB | TLS | Predis | 9,766 | ±273 | 2.8% | 🟡 good | 0.102 | ±0.003 | 0.150 | 0.179 | 9,615-9,918 | 13 |
| Dragonfly | Non-TLS | Predis | 10,669 | ±248 | 2.3% | 🟡 good | 0.093 | ±0.002 | 0.138 | 0.165 | 10,532-10,807 | 13 |
| Dragonfly | TLS | Predis | 8,849 | ±275 | 3.1% | 🟡 good | 0.113 | ±0.004 | 0.163 | 0.202 | 8,696-9,001 | 13 |
| Valkey | Non-TLS | Predis | 15,166 | ±416 | 2.7% | 🟡 good | 0.065 | ±0.002 | 0.106 | 0.124 | 14,935-15,397 | 13 |
| Valkey | TLS | Predis | 10,826 | ±330 | 3.0% | 🟡 good | 0.092 | ±0.003 | 0.140 | 0.167 | 10,643-11,009 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 15,166 ops/sec
- **Average Performance:** 10,854 ops/sec
- **Average Measurement Precision:** 2.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
