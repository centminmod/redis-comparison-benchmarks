# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 07:40:13 UTC
**PHP Version:** 8.4.8
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
| Redis | Non-TLS | Predis | 14,555 | ±342 | 2.3% | 🟡 good | 0.068 | ±0.002 | 0.110 | 0.128 | 14,365-14,744 | 13 |
| Redis | TLS | Predis | 10,511 | ±254 | 2.4% | 🟡 good | 0.095 | ±0.002 | 0.144 | 0.171 | 10,370-10,651 | 13 |
| KeyDB | Non-TLS | Predis | 12,498 | ±377 | 3.0% | 🟡 good | 0.080 | ±0.003 | 0.123 | 0.144 | 12,289-12,707 | 13 |
| KeyDB | TLS | Predis | 9,490 | ±285 | 3.0% | 🟡 good | 0.105 | ±0.003 | 0.154 | 0.185 | 9,332-9,648 | 13 |
| Dragonfly | Non-TLS | Predis | 10,520 | ±223 | 2.1% | 🟡 good | 0.095 | ±0.002 | 0.140 | 0.166 | 10,396-10,644 | 13 |
| Dragonfly | TLS | Predis | 10,527 | ±292 | 2.8% | 🟡 good | 0.095 | ±0.003 | 0.141 | 0.168 | 10,365-10,689 | 13 |
| Valkey | Non-TLS | Predis | 14,648 | ±363 | 2.5% | 🟡 good | 0.068 | ±0.002 | 0.109 | 0.127 | 14,447-14,850 | 13 |
| Valkey | TLS | Predis | 10,423 | ±254 | 2.4% | 🟡 good | 0.095 | ±0.002 | 0.145 | 0.172 | 10,282-10,564 | 13 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 14,648 ops/sec
- **Average Performance:** 11,647 ops/sec
- **Average Measurement Precision:** 2.6% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
