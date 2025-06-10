# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 07:42:35 UTC
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
| Redis | Non-TLS | Predis | 10,335 | ±305 | 2.9% | 🟡 good | 0.096 | ±0.003 | 0.140 | 0.169 | 10,166-10,504 | 13 |
| Redis | TLS | Predis | 7,835 | ±252 | 3.2% | 🟡 good | 0.127 | ±0.004 | 0.178 | 0.221 | 7,695-7,975 | 13 |
| KeyDB | Non-TLS | Predis | 12,496 | ±343 | 2.7% | 🟡 good | 0.080 | ±0.002 | 0.124 | 0.146 | 12,305-12,686 | 13 |
| KeyDB | TLS | Predis | 9,554 | ±302 | 3.2% | 🟡 good | 0.104 | ±0.004 | 0.154 | 0.185 | 9,387-9,722 | 13 |
| Dragonfly | Non-TLS | Predis | 11,138 | ±344 | 3.1% | 🟡 good | 0.089 | ±0.003 | 0.138 | 0.167 | 10,947-11,329 | 13 |
| Dragonfly | TLS | Predis | 7,594 | ±205 | 2.7% | 🟡 good | 0.131 | ±0.004 | 0.181 | 0.222 | 7,480-7,708 | 13 |
| Valkey | Non-TLS | Predis | 14,773 | ±389 | 2.6% | 🟡 good | 0.067 | ±0.002 | 0.109 | 0.128 | 14,557-14,989 | 13 |
| Valkey | TLS | Predis | 10,683 | ±300 | 2.8% | 🟡 good | 0.093 | ±0.003 | 0.143 | 0.170 | 10,517-10,849 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,773 ops/sec
- **Average Performance:** 10,551 ops/sec
- **Average Measurement Precision:** 2.9% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
