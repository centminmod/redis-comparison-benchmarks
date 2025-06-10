# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 10:15:20 UTC
**PHP Version:** 8.4.8
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
| Redis | Non-TLS | Predis | 10,332 | ±290 | 2.8% | 🟡 good | 0.096 | ±0.003 | 0.140 | 0.167 | 10,171-10,493 | 13 |
| Redis | TLS | Predis | 8,012 | ±254 | 3.2% | 🟡 good | 0.124 | ±0.004 | 0.175 | 0.212 | 7,871-8,152 | 13 |
| KeyDB | Non-TLS | Predis | 12,569 | ±310 | 2.5% | 🟡 good | 0.079 | ±0.002 | 0.123 | 0.142 | 12,398-12,741 | 13 |
| KeyDB | TLS | Predis | 9,698 | ±311 | 3.2% | 🟡 good | 0.103 | ±0.004 | 0.151 | 0.179 | 9,526-9,871 | 13 |
| Dragonfly | Non-TLS | Predis | 11,540 | ±333 | 2.9% | 🟡 good | 0.086 | ±0.003 | 0.133 | 0.160 | 11,356-11,725 | 13 |
| Dragonfly | TLS | Predis | 8,572 | ±269 | 3.1% | 🟡 good | 0.116 | ±0.004 | 0.172 | 0.205 | 8,423-8,722 | 13 |
| Valkey | Non-TLS | Predis | 14,688 | ±372 | 2.5% | 🟡 good | 0.068 | ±0.002 | 0.109 | 0.125 | 14,481-14,894 | 13 |
| Valkey | TLS | Predis | 10,567 | ±291 | 2.8% | 🟡 good | 0.094 | ±0.003 | 0.143 | 0.167 | 10,406-10,729 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,688 ops/sec
- **Average Performance:** 10,747 ops/sec
- **Average Measurement Precision:** 2.9% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
