# WordPress Object Cache Test (Predis)

**Test Date:** 2025-06-10 11:06:24 UTC
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

- **Iterations per Test:** 5
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
| Redis | Non-TLS | Predis | 9,614 | ±499 | 5.2% | 🟠 fair | 0.104 | ±0.006 | 0.176 | 0.222 | 8,994-10,233 | 5 |
| Redis | TLS | Predis | 7,290 | ±311 | 4.3% | 🟡 good | 0.137 | ±0.006 | 0.234 | 0.295 | 6,904-7,677 | 5 |
| KeyDB | Non-TLS | Predis | 11,833 | ±577 | 4.9% | 🟡 good | 0.084 | ±0.004 | 0.144 | 0.184 | 11,117-12,550 | 5 |
| KeyDB | TLS | Predis | 8,960 | ±432 | 4.8% | 🟡 good | 0.111 | ±0.006 | 0.188 | 0.241 | 8,423-9,496 | 5 |
| Dragonfly | Non-TLS | Predis | 10,639 | ±503 | 4.7% | 🟡 good | 0.094 | ±0.005 | 0.161 | 0.216 | 10,014-11,263 | 5 |
| Dragonfly | TLS | Predis | 7,899 | ±313 | 4.0% | 🟡 good | 0.126 | ±0.005 | 0.207 | 0.287 | 7,510-8,288 | 5 |
| Valkey | Non-TLS | Predis | 13,766 | ±823 | 6.0% | 🟠 fair | 0.072 | ±0.005 | 0.126 | 0.163 | 12,744-14,788 | 5 |
| Valkey | TLS | Predis | 9,763 | ±451 | 4.6% | 🟡 good | 0.102 | ±0.005 | 0.173 | 0.233 | 9,203-10,322 | 5 |

## Implementation Summary (Predis)

- **Total Tests:** 8
- **Reliable Measurements:** 8/8
- **Implementation:** Predis (Pure PHP Redis Client)
- **Best Performance:** 13,766 ops/sec
- **Average Performance:** 9,970 ops/sec
- **Average Measurement Precision:** 4.8% CV
- **TLS Connection Success:** 4/4 databases
- **TLS Reliability:** ✅ Enhanced with Predis

## Predis Advantages

- **Enhanced TLS Support:** Better SSL context handling than phpredis
- **Connection Reliability:** Built-in retry logic and error recovery
- **Cross-Platform Consistency:** Pure PHP implementation
- **No Extension Dependencies:** Works without Redis PHP extension
- **Trade-off:** Higher latency compared to C-based phpredis extension
